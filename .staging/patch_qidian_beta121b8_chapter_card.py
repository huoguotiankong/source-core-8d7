import base64
import gzip
import hashlib
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = "huoguotiankong/source-core-8d7"
SRC = Path("sources/novel/qidian-next/qidian-next-beta.json")
STABLE = Path("sources/novel/qidian-next/qidian-next.json")
VERSION = "1.2.1-beta8"
CODE = 12018


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


def unpack_module(value):
    s = str(value)
    if not s.startswith("gz:"):
        return s
    b = s[3:].strip().replace("-", "+").replace("_", "/")
    b += "=" * ((4 - len(b) % 4) % 4)
    return gzip.decompress(base64.b64decode(b)).decode("utf-8")


def pack_module(text):
    raw = gzip.compress(text.encode("utf-8"), compresslevel=9, mtime=0)
    return "gz:" + base64.b64encode(raw).decode("ascii")


def main():
    stable_before = hashlib.sha256(STABLE.read_bytes()).hexdigest()
    arr = json.loads(SRC.read_text(encoding="utf-8"))
    src = arr[0] if isinstance(arr, list) else arr

    old_rule = str((src.get("ruleContent") or {}).get("content") or "")
    old_js = str(src.get("jsLib") or "")
    if "Packages.java.util.Scanner" not in old_js or "java.lang.reflect.Array.newInstance" in old_js:
        raise SystemExit("Beta7 Rhino-compatible loader gate failed")
    if old_rule.count("@js:") != 1 or "\\n@js:" in old_rule or "@js:\\n" in old_rule:
        raise SystemExit("Beta7 single ruleContent JS gate failed")

    pack_re = re.compile(r"var\s+QF_MOD38_PACK\s*=\s*(\{.*?\});\s*var\s+QF_MOD38_EXPORTS", re.S)
    exp_re = re.compile(r"var\s+QF_MOD38_EXPORTS\s*=\s*(\{.*?\});", re.S)
    m = pack_re.search(old_js)
    exm = exp_re.search(old_js)
    if not m or not exm:
        raise SystemExit("module pack/exports not found")
    old_pack = json.loads(m.group(1))
    exports = json.loads(exm.group(1))
    if len(old_pack) != 32 or "review" not in old_pack:
        raise SystemExit(f"unexpected module pack: total={len(old_pack)} review={'review' in old_pack}")

    review = unpack_module(old_pack["review"])
    start = review.find("function qdChapterTalkCardV20(")
    if start < 0:
        raise SystemExit("qdChapterTalkCardV20 not found")
    nxt = re.search(r"\nfunction\s+[A-Za-z0-9_$]+\s*\(", review[start + 10:])
    end = (start + 10 + nxt.start()) if nxt else len(review)
    fn = review[start:end]

    required_old = [
        "qdCardVisGetV500('chapter',visualSig)",
        'fill="#5E9A76"',
        'fill="#fff" font-weight="700" text-anchor="middle">本章说</text>',
        'fill="#7D8D84"',
        'stroke="#E7ECE9"',
        'fill="#4F5B54" font-weight="700"',
        'fill="#9AA39E"',
        'fill="#222"',
        'rx="44" fill="rgba(250,253,251,0.38)" stroke="#D9E4DD" stroke-width="1"',
        "qdCardVisPutV500(j,'chapter',visualSig,final)",
        "showCmtV20('",
    ]
    for needle in required_old:
        if needle not in fn:
            raise SystemExit("chapter-card baseline mismatch: " + needle)

    replacements = [
        ("qdCardVisGetV500('chapter',visualSig)", "qdCardVisGetV500('chapter-b8',visualSig)"),
        ('<rect x="34" y="28" width="178" height="58" rx="29" fill="#5E9A76"/>', '<rect x="34" y="28" width="178" height="58" rx="29" fill="#FFF0ED" stroke="#FFD8D1" stroke-width="1"/>'),
        ('fill="#fff" font-weight="700" text-anchor="middle">本章说</text>', 'fill="#E65A4F" font-weight="700" text-anchor="middle">本章说</text>'),
        ('font-size="29" text-anchor="end" font-family="'+"'+font+'"+'" fill="#7D8D84"', 'font-size="27" text-anchor="end" font-family="'+"'+font+'"+'" fill="#9A9CA2"'),
        ('stroke="#E7ECE9" stroke-width="1"', 'stroke="#F0F1F3" stroke-width="1"'),
        ('font-size="34" font-family="'+"'+font+'"+'" fill="#4F5B54" font-weight="700"', 'font-size="32" font-family="'+"'+font+'"+'" fill="#56585D" font-weight="600"'),
        ('font-size="27" text-anchor="end" font-family="'+"'+font+'"+'" fill="#9AA39E"', 'font-size="25" text-anchor="end" font-family="'+"'+font+'"+'" fill="#A3A5AB"'),
        ('font-size="38" font-family="'+"'+font+'"+'" fill="#222"', 'font-size="38" font-family="'+"'+font+'"+'" fill="#303238"'),
        ('rx="44" fill="rgba(250,253,251,0.38)" stroke="#D9E4DD" stroke-width="1"', 'rx="44" fill="#FCFCFD" stroke="#ECEDEF" stroke-width="1.2"'),
        ("qdCardVisPutV500(j,'chapter',visualSig,final)", "qdCardVisPutV500(j,'chapter-b8',visualSig,final)"),
    ]
    new_fn = fn
    for old, new in replacements:
        count = new_fn.count(old)
        if count != 1:
            raise SystemExit(f"chapter-card replacement count {count}: {old}")
        new_fn = new_fn.replace(old, new, 1)
    if new_fn == fn:
        raise SystemExit("chapter-card function unchanged")
    if "showCmtV20('" not in new_fn or "'-1','0','zp'" not in new_fn:
        raise SystemExit("chapter-card click contract changed")
    review_new = review[:start] + new_fn + review[end:]
    new_review_value = pack_module(review_new)

    pack_json = m.group(1)
    key_re = re.compile(r'("review"\s*:\s*)"([^"\\]*(?:\\.[^"\\]*)*)"')
    km = key_re.search(pack_json)
    if not km:
        raise SystemExit("review pack entry not found textually")
    if json.loads('"' + km.group(2) + '"') != old_pack["review"]:
        raise SystemExit("review textual entry mismatch")
    replacement_value = json.dumps(new_review_value, ensure_ascii=False)
    new_pack_json = pack_json[:km.start(2)-1] + replacement_value + pack_json[km.end(2)+1:]
    new_js = old_js[:m.start(1)] + new_pack_json + old_js[m.end(1):]

    m2 = pack_re.search(new_js)
    exm2 = exp_re.search(new_js)
    if not m2 or not exm2:
        raise SystemExit("updated module pack/exports missing")
    new_pack = json.loads(m2.group(1))
    if set(new_pack) != set(old_pack):
        raise SystemExit("module names changed")
    changed = [name for name in old_pack if old_pack[name] != new_pack[name]]
    if changed != ["review"]:
        raise SystemExit("unexpected lazy module changes: " + repr(changed))
    if new_js[:m2.start(1)] != old_js[:m.start(1)] or new_js[m2.end(1):] != old_js[m.end(1):]:
        raise SystemExit("jsLib changed outside QF_MOD38_PACK")
    if exm2.group(1) != exm.group(1):
        raise SystemExit("module exports changed")

    pairs = []
    for name in exports.get("review", []):
        pairs.append(json.dumps(name, ensure_ascii=False) + ":(typeof " + name + "==='function'?" + name + ":null)")
    wrapped = "(function(){\n" + review_new + "\n;return {" + ",".join(pairs) + "};\n})"
    js_check("review module beta8", wrapped)
    js_check("jsLib beta8", new_js)

    # Runtime / body gates: this release is UI-only.
    if str((src.get("ruleContent") or {}).get("content") or "") != old_rule:
        raise SystemExit("ruleContent changed before write")
    src["jsLib"] = new_js
    if str((src.get("ruleContent") or {}).get("content") or "") != old_rule:
        raise SystemExit("ruleContent changed")
    if "Packages.java.util.Scanner" not in new_js or "java.lang.reflect.Array.newInstance" in new_js:
        raise SystemExit("Rhino loader regression")

    src["bookSourceComment"] = (
        "v1.2.1-beta8：仅优化起点本地评论的章末“本章说”卡片视觉。"
        "移除原绿色/米黄视觉，改为评论页同系的近白浅灰卡片、珊瑚红强调标签与统一灰阶文字；"
        "保留评论总数、两条真实评论预览、点赞/回复统计及点击进入本章说逻辑。"
        "正文规则、Rhino懒模块加载器、评论请求链和其它31个lazy module均不改。Stable 1.2.0不变。"
    )
    for k in ("version", "sourceVersion"):
        if k in src:
            src[k] = VERSION
    for k in ("versionCode", "sourceVersionCode"):
        if k in src:
            src[k] = CODE

    SRC.write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding="utf-8")
    stable_after = hashlib.sha256(STABLE.read_bytes()).hexdigest()
    if stable_after != stable_before:
        raise SystemExit("Stable source changed")

    sha = hashlib.sha256(SRC.read_bytes()).hexdigest()
    now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    day = now[:10]
    summary = "本地本章说卡片视觉统一：近白浅灰卡片 + 珊瑚红强调；评论数据与点击逻辑不变。"
    changes = [
        "本章说标签由绿色改为浅珊瑚红底+珊瑚红字，统一评论页强调色",
        "卡片背景/边框改为近白+浅灰，昵称、正文、回复与点赞统一中性灰阶",
        "保留评论总数、两条真实评论预览、点赞/回复统计和点击进入本章说",
        "仅替换 review lazy module 视觉层；ruleContent、Rhino loader 与其它31个模块保持不变",
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
        for tag in ["起点", "测试版", "本地段评", "本章说", "评论页", "UI统一", "珊瑚红"]:
            if tag not in tags:
                tags.append(tag)
        v["tags"] = tags

    for fp in ["subscription/beta.json", "subscription/novel.json", "manifest.json"]:
        p = Path(fp)
        d = json.loads(p.read_text(encoding="utf-8"))
        hit = [0]
        def walk(x):
            if isinstance(x, list):
                for v in x:
                    walk(v)
            elif isinstance(x, dict):
                if x.get("id") == "qidian-next-beta":
                    update_item(x)
                    hit[0] += 1
                else:
                    for v in x.values():
                        walk(v)
        walk(d)
        if hit[0] != 1:
            raise SystemExit(f"{fp}: expected 1 qidian-next-beta item, got {hit[0]}")
        if isinstance(d, dict):
            if "updatedAt" in d:
                d["updatedAt"] = now
            if "generatedAt" in d:
                d["generatedAt"] = now
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    bp = Path("bundles/all-beta.json")
    bd = json.loads(bp.read_text(encoding="utf-8"))
    hit = [0]
    def replace_beta(x):
        if isinstance(x, list):
            for i, v in enumerate(x):
                if isinstance(v, dict) and v.get("bookSourceUrl") == src.get("bookSourceUrl") and "Beta" in str(v.get("bookSourceName", "")):
                    x[i] = json.loads(json.dumps(src, ensure_ascii=False))
                    hit[0] += 1
                else:
                    replace_beta(v)
        elif isinstance(x, dict):
            for v in x.values():
                replace_beta(v)
    replace_beta(bd)
    if hit[0] != 1:
        raise SystemExit(f"bundle beta source target count={hit[0]}")
    bp.write_text(json.dumps(bd, ensure_ascii=False, indent=2), encoding="utf-8")

    dp = Path("rss/data/details/beta/qidian-next.json")
    detail = {
        "kind": "source",
        "title": "🌈 起点增强 · Beta",
        "summary": "Beta 1.2.1-beta8：统一本地本章说章末卡片与评论页视觉主题。",
        "badges": ["Beta", VERSION, "本地段评", "本章说", "UI统一"],
        "sections": [
            {"title": "视觉", "text": "章末本章说由绿色主题改为近白浅灰卡片，标签使用评论页同系浅珊瑚红底与珊瑚红文字；边框、分隔线及正文信息改为统一中性灰阶。"},
            {"title": "功能", "text": "评论总数、两条真实评论预览、点赞/回复统计以及点击进入本章说全部保留。"},
            {"title": "隔离", "text": "只修改 review lazy module 的 qdChapterTalkCardV20 视觉层；正文 ruleContent、Beta7 Rhino Scanner/GZIP 加载器及其余31个 lazy module 均保持不变。"},
            {"title": "发布", "text": "Stable 1.2.0 保持不变，Beta8 等待真机截图确认后再决定后续处理。"},
        ],
        "links": [
            {"label": "导入 Beta", "url": import_url},
            {"label": "Raw", "url": raw_url},
            {"label": "CDN", "url": cdn_url},
        ],
        "updatedAt": now,
    }
    dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")

    entry = f"""## {day} · qidian-next {VERSION}\n- 本轮按真机反馈先冻结情无服务器段评，只处理本地段评章末“本章说”卡片。\n- 视觉统一：绿色实心标签改为浅珊瑚红底 + 珊瑚红字；卡片改为近白背景、浅灰边框/分隔线，昵称、正文、回复与点赞统一中性灰阶。\n- 功能保持：评论总数、两条真实评论预览、点赞/回复统计与点击进入本章说逻辑全部不变。\n- 隔离门禁：仅 `review` lazy module 发生变化；`ruleContent`、Beta7 Rhino `Scanner + GZIPInputStream` 加载器及其它31个 lazy module 不变。\n- Stable 1.2.0 不变，仅发布 Beta 等待真机确认。\n\n"""
    for fp in ["docs/RELEASE_LOG.md", "docs/sources/qidian-next/PROJECT_HANDOFF.md"]:
        p = Path(fp)
        t = p.read_text(encoding="utf-8")
        if f"qidian-next {VERSION}" not in t:
            p.write_text(entry + t, encoding="utf-8")

    # Final integrity gates after all writes.
    arr2 = json.loads(SRC.read_text(encoding="utf-8"))
    src2 = arr2[0] if isinstance(arr2, list) else arr2
    if str((src2.get("ruleContent") or {}).get("content") or "") != old_rule:
        raise SystemExit("final ruleContent changed")
    js2 = str(src2.get("jsLib") or "")
    mm = pack_re.search(js2)
    if not mm:
        raise SystemExit("final module pack missing")
    p2 = json.loads(mm.group(1))
    changed2 = [name for name in old_pack if old_pack[name] != p2[name]]
    if changed2 != ["review"]:
        raise SystemExit("final module isolation failed: " + repr(changed2))
    if stable_before != hashlib.sha256(STABLE.read_bytes()).hexdigest():
        raise SystemExit("final Stable SHA changed")

    print("BETA8_OK")
    print("version", VERSION, "code", CODE)
    print("source_sha256", sha)
    print("changed_modules", changed2)
    print("stable_sha256", stable_before)
    print("raw", raw_url)


if __name__ == "__main__":
    main()
