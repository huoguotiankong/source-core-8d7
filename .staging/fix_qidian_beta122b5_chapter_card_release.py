import base64
import gzip
import hashlib
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = "huoguotiankong/source-core-8d7"
SRC = Path("sources/novel/qidian-next/qidian-next-beta.json")
STABLE = Path("sources/novel/qidian-next/qidian-next.json")
VERSION = "1.2.2-beta5"
CODE = 12025
PREV_VERSION = "1.2.1-beta8"
BETA4_COMMIT = "05af8feb180ca2c8260a0311e4eb0960f910003b"


def unpack_module(value):
    s = str(value)
    if not s.startswith("gz:"):
        return s
    b = s[3:].strip().replace("-", "+").replace("_", "/")
    b += "=" * ((4 - len(b) % 4) % 4)
    return gzip.decompress(base64.b64decode(b)).decode("utf-8")


def module_pack(js):
    m = re.search(r"var\s+QF_MOD38_PACK\s*=\s*(\{.*?\});\s*var\s+QF_MOD38_EXPORTS", js, re.S)
    if not m:
        raise SystemExit("QF_MOD38_PACK missing")
    return json.loads(m.group(1))


def chapter_fn(text):
    start = text.find("function qdChapterTalkCardV20(")
    if start < 0:
        raise SystemExit("qdChapterTalkCardV20 missing")
    nxt = re.search(r"\nfunction\s+[A-Za-z0-9_$]+\s*\(", text[start + 10:])
    end = start + 10 + nxt.start() if nxt else len(text)
    return text[start:end], text[:start] + "__QF_CHAPTER_CARD__" + text[end:]


def main():
    stable_before = hashlib.sha256(STABLE.read_bytes()).hexdigest()
    arr = json.loads(SRC.read_text(encoding="utf-8"))
    src = arr[0] if isinstance(arr, list) else arr

    if PREV_VERSION not in str(src.get("bookSourceComment", "")):
        raise SystemExit("unexpected beta source baseline; expected beta8 visual build")

    # Verify current beta is Beta4 functionality + only the chapter-card visual change.
    import subprocess
    old_raw = subprocess.check_output([
        "git", "show", f"{BETA4_COMMIT}:sources/novel/qidian-next/qidian-next-beta.json"
    ])
    old_arr = json.loads(old_raw.decode("utf-8"))
    old_src = old_arr[0] if isinstance(old_arr, list) else old_arr
    if (src.get("ruleContent") or {}).get("content") != (old_src.get("ruleContent") or {}).get("content"):
        raise SystemExit("ruleContent differs from beta4 baseline")
    cur_js = str(src.get("jsLib") or "")
    old_js = str(old_src.get("jsLib") or "")
    cur_pack = module_pack(cur_js)
    old_pack = module_pack(old_js)
    if set(cur_pack) != set(old_pack):
        raise SystemExit("lazy module names differ from beta4")
    changed = [k for k in old_pack if old_pack[k] != cur_pack[k]]
    if changed != ["review"]:
        raise SystemExit("unexpected modules changed vs beta4: " + repr(changed))
    old_review = unpack_module(old_pack["review"])
    cur_review = unpack_module(cur_pack["review"])
    old_fn, old_rest = chapter_fn(old_review)
    cur_fn, cur_rest = chapter_fn(cur_review)
    if old_rest != cur_rest:
        raise SystemExit("review module changed outside qdChapterTalkCardV20")
    for marker in ["#FFF0ED", "#E65A4F", "#FCFCFD", "chapter-b8"]:
        if marker not in cur_fn:
            raise SystemExit("chapter-card visual marker missing: " + marker)
    for contract in ["showCmtV20('", "'-1','0','zp'"]:
        if contract not in cur_fn:
            raise SystemExit("chapter-card click contract missing: " + contract)

    # Keep visual/runtime code untouched; correct the version line and publication metadata only.
    src["bookSourceComment"] = (
        "v1.2.2-beta5：基于 1.2.2-beta4 仅优化起点本地段评章末‘本章说’卡片视觉。"
        "卡片改为近白浅灰底、浅灰边框与评论页同系珊瑚红标签，昵称/正文/点赞/回复统一中性灰阶；"
        "评论总数、两条真实评论预览、点赞/回复统计和点击进入本章说逻辑保持不变。"
        "情无/小雨服务器段评本轮冻结；正文、目录、搜索、账号、ruleContent、Rhino 加载器及其它 lazy module 不改。"
        "Stable 1.2.1 不变。"
    )
    for k in ("version", "sourceVersion"):
        if k in src:
            src[k] = VERSION
    for k in ("versionCode", "sourceVersionCode"):
        if k in src:
            src[k] = CODE
    SRC.write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding="utf-8")

    # Code must be byte-identical apart from source metadata JSON serialization fields above.
    arr_check = json.loads(SRC.read_text(encoding="utf-8"))
    src_check = arr_check[0] if isinstance(arr_check, list) else arr_check
    if src_check.get("jsLib") != cur_js:
        raise SystemExit("jsLib changed during release correction")
    if (src_check.get("ruleContent") or {}).get("content") != (src.get("ruleContent") or {}).get("content"):
        raise SystemExit("ruleContent changed during release correction")

    sha = hashlib.sha256(SRC.read_bytes()).hexdigest()
    now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    day = now[:10]
    raw_url = f"https://raw.githubusercontent.com/{REPO}/main/{SRC}?v={CODE}"
    cdn_url = f"https://cdn.jsdelivr.net/gh/{REPO}@main/{SRC}?v={CODE}"
    import_url = "legado://import/importonline?src=" + raw_url
    summary = "本地本章说卡片视觉统一：近白浅灰卡片 + 珊瑚红强调；沿用 1.2.2-beta4 功能链，评论数据与点击逻辑不变。"
    changes = [
        "本章说标签改为浅珊瑚红底 + 珊瑚红字，统一评论页面强调色",
        "卡片背景/边框改为近白浅灰，昵称、正文、点赞与回复统一中性灰阶",
        "评论总数、两条真实评论预览、点赞/回复统计及点击进入本章说逻辑保持不变",
        "沿用 1.2.2-beta4 的 Argus 段评快通道与服务器评论兼容代码，本轮不再修改情无/小雨链",
        "正文、目录、搜索、账号、ruleContent、Rhino loader 及其它 lazy module 不变；Stable 1.2.1 不变",
    ]

    def patch_item(v):
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
        tags = [x for x in list(v.get("tags") or []) if x not in ["绿色", "米黄"]]
        for tag in ["起点", "测试版", "本地段评", "本章说", "评论页", "UI统一", "珊瑚红", "正文冻结"]:
            if tag not in tags:
                tags.append(tag)
        v["tags"] = tags

    for fp in ["subscription/beta.json", "subscription/novel.json", "manifest.json"]:
        p = Path(fp)
        d = json.loads(p.read_text(encoding="utf-8"))
        hits = []
        def walk(x):
            if isinstance(x, list):
                for y in x: walk(y)
            elif isinstance(x, dict):
                if x.get("id") == "qidian-next-beta": hits.append(x)
                for y in x.values(): walk(y)
        walk(d)
        if len(hits) != 1:
            raise SystemExit(f"{fp}: qidian-next-beta count={len(hits)}")
        patch_item(hits[0])
        if isinstance(d, dict):
            if "updatedAt" in d: d["updatedAt"] = now
            if "generatedAt" in d: d["generatedAt"] = now
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    bp = Path("bundles/all-beta.json")
    bd = json.loads(bp.read_text(encoding="utf-8"))
    hits = [0]
    def replace_bundle(x):
        if isinstance(x, list):
            for i, y in enumerate(x):
                if isinstance(y, dict) and y.get("bookSourceUrl") == src.get("bookSourceUrl") and "Beta" in str(y.get("bookSourceName", "")):
                    x[i] = json.loads(json.dumps(src, ensure_ascii=False)); hits[0] += 1
                else: replace_bundle(y)
        elif isinstance(x, dict):
            for y in x.values(): replace_bundle(y)
    replace_bundle(bd)
    if hits[0] != 1:
        raise SystemExit("bundle beta target count=" + str(hits[0]))
    bp.write_text(json.dumps(bd, ensure_ascii=False, indent=2), encoding="utf-8")

    detail = {
        "kind": "source",
        "title": "🌈 起点增强 · Beta",
        "summary": "Beta 1.2.2-beta5：先完成本地段评章末‘本章说’卡片主题统一；服务器段评本轮冻结。",
        "badges": ["Beta", VERSION, "本地段评", "本章说", "UI统一"],
        "sourceUrl": raw_url,
        "backupUrl": cdn_url,
        "importUrl": import_url,
        "sections": [
            {"title": "卡片主题", "text": "绿色/米黄视觉改为近白浅灰卡片，使用评论页同系珊瑚红标签；正文、昵称、点赞与回复统一中性灰阶。"},
            {"title": "功能保持", "text": "评论总数、两条真实评论预览、点赞/回复统计及点击进入本章说均保持原逻辑。"},
            {"title": "严格隔离", "text": "沿用 1.2.2-beta4 功能链；本轮不修改情无/小雨服务器段评，不修改正文、目录、搜索、账号和评论请求链。"},
            {"title": "版本策略", "text": "Stable 1.2.1 保持不变。本版只进入 Beta，等待真机截图确认。"},
        ],
        "links": [
            {"label": "导入 Beta", "url": import_url},
            {"label": "Raw", "url": raw_url},
            {"label": "CDN", "url": cdn_url},
        ],
        "updatedAt": now,
    }
    Path("rss/data/details/beta/qidian-next.json").write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")

    entry = f"""## {day} · qidian-next {VERSION} — 本地本章说卡片主题统一\n- 延续 1.2.2-beta4 功能链，仅保留已完成的 `qdChapterTalkCardV20` 视觉改造；上一轮误写成 1.2.1-beta8 的版本序列在本版纠正为 1.2.2-beta5。\n- 卡片由绿色/米黄改为近白浅灰底、浅灰边框和评论页同系珊瑚红标签；昵称、正文、点赞与回复统一中性灰阶。\n- 评论总数、两条真实评论预览、点赞/回复统计及点击进入本章说逻辑不变。\n- 情无/小雨服务器段评本轮冻结；正文、目录、搜索、账号、`ruleContent`、Rhino loader 与其它 lazy module 均不改。\n- 修复 Beta 详情页发布元数据：恢复顶层 `sourceUrl` / `backupUrl` / `importUrl`，同时保留 links。\n- Stable 1.2.1 不变，仅发布 Beta 等待真机确认。\n\n"""
    for fp in ["docs/RELEASE_LOG.md", "docs/sources/qidian-next/PROJECT_HANDOFF.md"]:
        p = Path(fp)
        t = p.read_text(encoding="utf-8")
        if f"qidian-next {VERSION}" not in t:
            p.write_text(entry + t, encoding="utf-8")

    if hashlib.sha256(STABLE.read_bytes()).hexdigest() != stable_before:
        raise SystemExit("Stable source changed")
    print("BETA5_RELEASE_FIX_OK")
    print("version", VERSION, "code", CODE)
    print("sha256", sha)
    print("stable_sha256", stable_before)
    print("raw", raw_url)


if __name__ == "__main__":
    main()
