import json
import re
import hashlib
import base64
import gzip
import subprocess
import tempfile
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

REPO = "huoguotiankong/source-core-8d7"
SRC = Path("sources/novel/qidian-next/qidian-next-beta.json")
STABLE = Path("sources/novel/qidian-next/qidian-next.json")
BASE_REF = "90c2a479ed7e9fb0c348160de479f3c1b0198598"  # verified Beta4
VERSION = "1.2.1-beta7"
CODE = 12017


def git_show(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], text=True, encoding="utf-8")


def js_check(label, text):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
        tf.write(text)
        p = tf.name
    try:
        cp = subprocess.run(["node", "--check", p], capture_output=True, text=True)
        if cp.returncode != 0:
            raise SystemExit(f"{label} syntax check failed: {cp.stderr[:1800]}")
    finally:
        os.unlink(p)


def main():
    stable_before = hashlib.sha256(STABLE.read_bytes()).hexdigest()

    # Rebuild from the verified Beta4 state. Never patch on top of Beta5/Beta6.
    base_arr = json.loads(git_show(BASE_REF, str(SRC)))
    arr = json.loads(json.dumps(base_arr, ensure_ascii=False))
    src = arr[0] if isinstance(arr, list) else arr
    base_src = base_arr[0] if isinstance(base_arr, list) else base_arr
    base_js = base_src.get("jsLib", "")

    fn = "function qfModuleUnpackV41(v){"
    marker = "/* alpha84：lazy module 首次加载并发保护。"
    start = base_js.find(fn)
    end = base_js.find(marker, start)
    if start < 0 or end < 0:
        raise SystemExit("Beta4 loader/alpha84 boundary not found")
    old_loader = base_js[start:end]
    if "Packages.java.util.Scanner" not in old_loader or 'sc.useDelimiter("\\\\A")' not in old_loader:
        raise SystemExit("verified Beta4 Scanner loader not found")
    if "function qfModuleThreadIdV84" not in base_js or "function qfModuleWaitV84" not in base_js:
        raise SystemExit("verified Beta4 alpha84 runtime functions missing")

    # Keep Beta4's proven Rhino-compatible Scanner/GZIP path. Only normalize Base64URL input.
    loader_lines = [
        'function qfModuleUnpackV41(v){',
        '    var s=String(v||"");',
        '    if(s.indexOf("gz:")!==0)return s;',
        '    try{',
        '        var b64=String(s.substring(3)||"").replace(/\\s+/g,"");',
        '        b64=b64.replace(/-/g,"+").replace(/_/g,"/");',
        '        while(b64.length%4)b64+="=";',
        '        var bytes=null;',
        '        try{bytes=Packages.android.util.Base64.decode(b64,0);}catch(_a){',
        '            bytes=Packages.java.util.Base64.getDecoder().decode(b64);',
        '        }',
        '        var input=new Packages.java.io.ByteArrayInputStream(bytes);',
        '        var gz=new Packages.java.util.zip.GZIPInputStream(input);',
        '        var sc=new Packages.java.util.Scanner(gz,"UTF-8");',
        '        sc.useDelimiter("\\\\A");',
        '        var out=sc.hasNext()?String(sc.next()):"";',
        '        try{sc.close();}catch(_c){}',
        '        return out;',
        '    }catch(e){',
        '        throw new Error("模块解压失败："+String(e&&e.message||e));',
        '    }',
        '}',
        '',
        '',
    ]
    new_loader = "\n".join(loader_lines)
    js = base_js[:start] + new_loader + base_js[end:]
    src["jsLib"] = js

    # Beta4 appended a second @js block as literal "\\n@js:\\n" inside ruleContent.
    # Legado/Rhino receives the backslash itself and throws EvaluatorException at line 1.
    # Merge the exact decorator into ONE real JS block instead of chaining a literal escaped rule.
    rc = src.get("ruleContent")
    if not isinstance(rc, dict) or "content" not in rc:
        raise SystemExit("ruleContent.content missing")
    rc_lines = [
        "@js:",
        "result=qfContentEntryV38.call(this,result,baseUrl);",
        "try{",
        "  var _u=String(baseUrl||url||'');",
        "  var _bm=_u.match(/[?&]bookId=([^&]+)/i),_cm=_u.match(/[?&]chapterId=([^&]+)/i);",
        "  if(_bm&&_cm){",
        "    var _bid=decodeURIComponent(_bm[1]),_cid=decodeURIComponent(_cm[1]);",
        "    var _sel='';",
        "    try{_sel=String(source.get('qf_review_provider')||source.get('段评来源')||'')}catch(e){}",
        "    if(/情无|小雨|qw|xiaoyu/i.test(_sel)){",
        "      var _d=qfQwDecorateV1214(this,String(result||''),_bid,_cid,'');",
        "      result=_d.content;",
        "      if(_d.titleBubble)source.put('qf_qw_title_'+_cid,_d.titleBubble);",
        "    }",
        "  }",
        "}catch(e){try{java.log('QW comment decorate: '+e)}catch(_){}}",
        "result;",
    ]
    rc["content"] = "\n".join(rc_lines)

    src["bookSourceComment"] = (
        "v1.2.1-beta7：按真机报错修复 Beta4-Beta6 两个独立回归。"
        "正文规则不再用字面量\\n串联第二个@js，改为单一真实JS块，修复 EvaluatorException 不允许的字符\\；"
        "懒模块解压恢复 Beta4 已验证的 Scanner/GZIP 实现，仅在解码前做 Base64URL 标准化，"
        "移除 Rhino 不兼容的 java.lang.reflect.Array.newInstance。情无/小雨评论业务逻辑本身不改。Stable 1.2.0 不变。"
    )
    for k in ("version", "sourceVersion"):
        if k in src:
            src[k] = VERSION
    for k in ("versionCode", "sourceVersionCode"):
        if k in src:
            src[k] = CODE

    # Isolation: outside loader, jsLib must still be Beta4 byte-for-byte.
    new_start = js.find(fn)
    new_end = js.find(marker, new_start)
    if base_js[:start] != js[:new_start] or base_js[end:] != js[new_end:]:
        raise SystemExit("unexpected jsLib change outside qfModuleUnpackV41")
    required = [
        "function qfModuleThreadIdV84(){",
        "function qfModuleWaitV84(name,owner){",
        "Packages.java.util.Scanner",
        'sc.useDelimiter("\\\\A")',
        'b64=b64.replace(/-/g,"+").replace(/_/g,"/")',
        'while(b64.length%4)b64+="=";',
    ]
    for needle in required:
        if needle not in js:
            raise SystemExit("runtime assertion failed: " + needle)
    if "java.lang.reflect.Array" in new_loader or "ByteArrayOutputStream" in new_loader:
        raise SystemExit("Beta6 incompatible buffer path still present")
    if js.count(fn) != 1 or js.count("function qfModuleThreadIdV84(){") != 1:
        raise SystemExit("runtime definition count invalid")

    rule_script = rc["content"]
    if rule_script.count("@js:") != 1:
        raise SystemExit("ruleContent must contain exactly one @js block")
    if "\\n@js:" in rule_script or "@js:\\n" in rule_script:
        raise SystemExit("literal escaped @js separator still present")
    if not rule_script.startswith("@js:\n"):
        raise SystemExit("ruleContent does not start with real newline JS block")
    js_check("ruleContent", rule_script[len("@js:\n"):])
    js_check("jsLib", js)

    # Validate ALL 32 lazy modules, including the one uncompressed provider_common module.
    m = re.search(r"var\s+QF_MOD38_PACK\s*=\s*(\{.*?\});\s*var\s+QF_MOD38_EXPORTS", js, re.S)
    exm = re.search(r"var\s+QF_MOD38_EXPORTS\s*=\s*(\{.*?\});", js, re.S)
    if not m or not exm:
        raise SystemExit("module pack/exports not found")
    pack = json.loads(m.group(1))
    exports = json.loads(exm.group(1))
    checked = 0
    compressed = 0
    for name, val in pack.items():
        s = str(val)
        if s.startswith("gz:"):
            b = s[3:].strip().replace("-", "+").replace("_", "/")
            b += "=" * ((4 - len(b) % 4) % 4)
            try:
                text = gzip.decompress(base64.b64decode(b, validate=True)).decode("utf-8")
            except Exception as e:
                raise SystemExit(f"module decode failed {name}: {e}")
            compressed += 1
        else:
            text = s
        if text.startswith("\\n") or text.startswith("\\r"):
            raise SystemExit(f"module {name} starts with literal backslash escape")
        pairs = []
        for n in exports.get(name, []):
            pairs.append(json.dumps(n, ensure_ascii=False) + ":(typeof " + n + "==='function'?" + n + ":null)")
        wrapped = "(function(){\n" + text + "\n;return {" + ",".join(pairs) + "};\n})"
        js_check("module " + name, wrapped)
        checked += 1
    if checked != 32 or compressed != 31:
        raise SystemExit(f"module count mismatch total={checked} compressed={compressed}")

    SRC.write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding="utf-8")
    sha = hashlib.sha256(SRC.read_bytes()).hexdigest()
    now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    summary = "真机回归修复：正文单JS执行，恢复Beta4 Scanner解压并保留Base64URL兼容；移除Rhino不兼容反射数组。"
    changes = [
        "修复正文 EvaluatorException：Beta4 评论补丁的字面量 \\n@js:\\n 改为单一真实 JS 块",
        "懒模块解压恢复 Beta4 已验证 Scanner/GZIP 路径，移除 java.lang.reflect.Array.newInstance",
        "Base64URL 仅做 -/_ 标准化和 = 补位，不改评论业务接口",
        "32 个 lazy module（31 压缩 + provider_common）全部解包/语法校验",
        "Stable 1.2.0 不变，继续仅发布 Beta 等待真机确认",
    ]
    raw_url = f"https://raw.githubusercontent.com/{REPO}/main/{SRC}?v={CODE}"
    cdn_url = f"https://cdn.jsdelivr.net/gh/{REPO}@main/{SRC}?v={CODE}"
    import_url = "legado://import/importonline?src=" + raw_url

    def update_item(v):
        v["name"] = "🌈 起点增强 · Beta"
        v["channel"] = "beta"
        v["version"] = VERSION
        v["versionCode"] = CODE
        v["updatedAt"] = now
        v["summary"] = summary
        v["changelog"] = changes
        v["sourcePath"] = str(SRC)
        v["sourceUrl"] = raw_url
        v["backupUrl"] = cdn_url
        v["importUrl"] = import_url
        v["sha256"] = sha
        tags = list(v.get("tags") or [])
        for tag in ["起点", "测试版", "情无", "小雨用户系统", "评论页", "Base64URL", "Rhino兼容", "正文回归修复"]:
            if tag not in tags:
                tags.append(tag)
        v["tags"] = tags

    for fp in ["subscription/beta.json", "subscription/novel.json", "manifest.json"]:
        p = Path(fp)
        d = json.loads(p.read_text(encoding="utf-8"))
        hit = [0]
        def walk(x):
            if isinstance(x, list):
                for v in x: walk(v)
            elif isinstance(x, dict):
                if x.get("id") == "qidian-next-beta":
                    update_item(x); hit[0] += 1
                else:
                    for v in x.values(): walk(v)
        walk(d)
        if hit[0] != 1:
            raise SystemExit(f"{fp}: expected 1 qidian-next-beta item, got {hit[0]}")
        if isinstance(d, dict):
            if "updatedAt" in d: d["updatedAt"] = now
            if "generatedAt" in d: d["generatedAt"] = now
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    bp = Path("bundles/all-beta.json")
    bd = json.loads(bp.read_text(encoding="utf-8"))
    hit = [0]
    def replace_beta(x):
        if isinstance(x, list):
            for i, v in enumerate(x):
                if isinstance(v, dict) and v.get("bookSourceUrl") == src.get("bookSourceUrl") and "Beta" in str(v.get("bookSourceName", "")):
                    x[i] = json.loads(json.dumps(src, ensure_ascii=False)); hit[0] += 1
                else: replace_beta(v)
        elif isinstance(x, dict):
            for v in x.values(): replace_beta(v)
    replace_beta(bd)
    if hit[0] != 1:
        raise SystemExit(f"bundle beta source target count={hit[0]}")
    bp.write_text(json.dumps(bd, ensure_ascii=False, indent=2), encoding="utf-8")

    dp = Path("rss/data/details/beta/qidian-next.json")
    detail = {
        "kind": "source",
        "title": "🌈 起点增强 · Beta",
        "summary": "Beta 1.2.1-beta7：修复正文反斜杠 EvaluatorException 与 Rhino Scanner/解压兼容问题。",
        "badges": ["Beta", VERSION, "Rhino兼容", "正文回归修复"],
        "sections": [
            {"title": "正文", "text": "Beta4 评论补丁把第二段 @js 以字面量反斜杠+n 拼进 ruleContent；Beta7 合并为一个真实 JS 块，正文主调用仍是 qfContentEntryV38。"},
            {"title": "懒模块", "text": "恢复 Beta4 真机已验证的 Scanner + GZIPInputStream 读取方式；删除 Beta6 在 Rhino 下不可调用的 java.lang.reflect.Array.newInstance。"},
            {"title": "Base64URL", "text": "解码前只做 -→+、_→/ 与缺失 = 补位；不修改情无/小雨评论接口和业务结构。"},
            {"title": "门禁", "text": "32 个 lazy module 全部解包并逐模块语法检查；jsLib 与 ruleContent 单独语法检查；Stable 1.2.0 不变。"},
        ],
        "sourceUrl": raw_url,
        "backupUrl": cdn_url,
        "importUrl": import_url,
    }
    dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")

    entry = f"""
## 2026-09-12 · qidian-next {VERSION}
- 真机确认 Beta6 仍有两类故障：正文 `EvaluatorException: 不允许的字符：\\`；评论页解压时报 `java.lang.reflect.Array.newInstance` 不是函数。
- 根因一：Beta4 评论补丁已把第二个 `@js` 以字面量 `\\n@js:\\n` 拼入 `ruleContent.content`；Beta5/Beta6沿用了该字段。Beta7 改成单一真实 JS 块，正文主链仍调用 `qfContentEntryV38`，随后再执行原情无/小雨装饰逻辑。
- 根因二：Beta6 自行改写 GZIP 读取为反射 byte[]，与当前 Legado Rhino 不兼容。Beta7 恢复 Beta4 已验证的 `Scanner + GZIPInputStream`，只在 Base64 解码前做 URL-safe 标准化。
- 门禁升级：32 个 lazy module（31 压缩 + 1 明文）全部解包并按实际 factory 包装逐个 JS 语法检查；另校验 `jsLib` 与单块 `ruleContent`。
- Stable 1.2.0 不变，仅进入 Beta 真机验证。
"""
    for fp in ["docs/RELEASE_LOG.md", "docs/sources/qidian-next/PROJECT_HANDOFF.md"]:
        p = Path(fp)
        t = p.read_text(encoding="utf-8")
        if f"qidian-next {VERSION}" not in t:
            p.write_text(entry + t, encoding="utf-8")

    if hashlib.sha256(STABLE.read_bytes()).hexdigest() != stable_before:
        raise SystemExit("stable source changed unexpectedly")
    print("Beta7 ready", "modules=", checked, "compressed=", compressed, "sha256=", sha, "time=", now)


if __name__ == "__main__":
    main()
