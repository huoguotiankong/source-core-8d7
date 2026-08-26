import hashlib
import json
import pathlib
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_ID = "https://sc8d7.invalid/legado/picacg-8d7"
VERSION = "1.0.0"
VERSION_CODE = "100"
MANIFEST_VERSION_CODE = 10000
NOW = datetime.now(ZoneInfo("Asia/Shanghai"))
NOW_ISO = NOW.isoformat(timespec="seconds")
DATE = NOW.strftime("%Y-%m-%d")

BETA_PATH = ROOT / "sources/comic/picacg/picacg-beta.json"
STABLE_PATH = ROOT / "sources/comic/picacg/picacg.json"
MANIFEST_PATH = ROOT / "manifest.json"
STABLE_SUB_PATH = ROOT / "subscription/stable.json"
BETA_SUB_PATH = ROOT / "subscription/beta.json"
COMIC_SUB_PATH = ROOT / "subscription/comic.json"
STABLE_BUNDLE_PATH = ROOT / "bundles/all-stable.json"
BETA_BUNDLE_PATH = ROOT / "bundles/all-beta.json"
DETAIL_PATH = ROOT / "rss/data/details/stable/picacg.json"
RELEASE_PATH = ROOT / "docs/RELEASE_LOG.md"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_list(path):
    data = load_json(path)
    return data if isinstance(data, list) else [data]


def check_js(label, code):
    tmp = ROOT / f".tmp_picacg_{label}.js"
    tmp.write_text("new Function(" + json.dumps(code, ensure_ascii=False) + ");\n", encoding="utf-8")
    try:
        subprocess.run(["node", str(tmp)], check=True)
    finally:
        tmp.unlink(missing_ok=True)


beta_data = load_json(BETA_PATH)
assert isinstance(beta_data, list) and len(beta_data) == 1, "Picacg beta source must contain exactly one source"
src = json.loads(json.dumps(beta_data[0], ensure_ascii=False))
assert src.get("bookSourceUrl") == SOURCE_ID
assert src.get("bookSourceName") == "◈ 哔咔漫画"
assert src.get("customButton") is True and src.get("eventListener") is True
callback = src.get("ruleContent", {}).get("callBackJs", "")
explore = src.get("ruleExplore", {}).get("bookList", "")
assert "clickCustomButton" in callback and "java.startBrowser" in callback
assert "picaDedupeComicsStrong" in src.get("jsLib", "")
assert "if(p>1)return new Packages.java.util.ArrayList()" in explore

src["bookSourceComment"] = (
    f"【v{VERSION} · {DATE}】\n"
    "哔咔漫画正式版。由 v1.0.0-beta9 真机确认基线原样晋升，不改动已验证业务逻辑。\n\n"
    "Stable 1.0.0：\n"
    "• 详情页顶部定制按钮已真机确认恢复，直接进入独立哔咔评论中心。\n"
    "• 相关推荐保持一次性首批集合：后续页硬终止，并按漫画 ID、标题、封面路径独立去重。\n"
    "• 保留 APP/API 与网页双线路、登录、账户中心、签到、收藏、点赞、评论、楼中楼、回复与标签跳转。\n"
    "• 保留漫画目录与原生图片正文阅读链。\n"
    "• 图片漫画正文使用阅读 MangaMenu；当前阅读上游未提供正文 customButton 控件，因此定制按钮入口位于作品详情页。\n"
    "• 后续未经真机确认的新改动继续进入 Beta，不直接覆盖 Stable。"
)
src["bookSourceGroup"] = "漫画"
src["lastUpdateTime"] = int(NOW.timestamp() * 1000)

check_js("jslib", src.get("jsLib", ""))
rule_explore_js = explore
if rule_explore_js.startswith("<js>") and rule_explore_js.endswith("</js>"):
    rule_explore_js = rule_explore_js[4:-5]
check_js("explore", rule_explore_js)
check_js("callback", callback)

dump_json(STABLE_PATH, [src])
sha256 = hashlib.sha256(STABLE_PATH.read_bytes()).hexdigest()

manifest = load_json(MANIFEST_PATH)
manifest["updatedAt"] = NOW_ISO
found = False
for entry in manifest.get("sources", []):
    if entry.get("id") == "picacg":
        entry.clear()
        entry.update({
            "id": "picacg",
            "name": "◈ 哔咔漫画",
            "category": "comic",
            "artifactType": "bookSource",
            "channel": "stable",
            "version": VERSION,
            "versionCode": MANIFEST_VERSION_CODE,
            "updatedAt": NOW_ISO,
            "sourcePath": "sources/comic/picacg/picacg.json",
            "sourceUrl": "https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg.json",
            "bookSourceUrl": SOURCE_ID,
            "summary": "正式版：Beta9 真机确认后原样晋升；详情顶部定制按钮恢复，相关推荐保持首批一次性返回与强去重。",
            "tags": ["哔咔", "漫画", "正式版", "APP API", "网页线路", "评论", "楼中楼", "定制按钮", "双线路"],
            "changelog": [
                "由 1.0.0-beta9 真机确认基线原样晋升 Stable，不新增业务逻辑",
                "详情页顶部定制按钮已真机确认恢复，可直接进入独立哔咔评论中心",
                "相关推荐保留 page>1 硬终止和漫画 ID/标题/封面路径三层独立去重",
                "保留登录、账户中心、签到、点赞收藏、评论/楼中楼、标签、目录、漫画图片正文及 APP/Web 双线路"
            ],
            "sha256": sha256,
            "icon": "https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/assets/source-core-source-icon.svg"
        })
        found = True
        break
assert found, "Picacg manifest entry not found"
dump_json(MANIFEST_PATH, manifest)

stable_entry = {
    "id": "picacg",
    "name": "◈ 哔咔漫画",
    "version": VERSION,
    "sourceUrl": f"https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg.json?v={VERSION_CODE}",
    "backupUrl": f"https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg.json?v={VERSION_CODE}",
    "detailUrl": f"https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/stable/picacg.json?v={VERSION_CODE}",
    "tags": ["漫画源", "Stable", "哔咔", "Picacg", "APP/API", "网页线路", "登录", "账号", "评论"],
    "summary": "哔咔漫画 APP/网页双线路正式源，支持登录、账号、评论/楼中楼、点赞收藏、标签与漫画正文。"
}

stable_sub = load_json(STABLE_SUB_PATH)
stable_sub["generatedAt"] = NOW_ISO
stable_sub["sources"] = [x for x in stable_sub.get("sources", []) if x.get("id") != "picacg"]
stable_sub["sources"].append(stable_entry)
dump_json(STABLE_SUB_PATH, stable_sub)

beta_sub = load_json(BETA_SUB_PATH)
beta_sub["generatedAt"] = NOW_ISO
beta_sub["sources"] = [x for x in beta_sub.get("sources", []) if x.get("id") != "picacg"]
dump_json(BETA_SUB_PATH, beta_sub)

comic_sub = load_json(COMIC_SUB_PATH)
comic_sub["generatedAt"] = NOW_ISO
comic_entry = dict(stable_entry)
comic_entry["channel"] = "stable"
comic_sub["sources"] = [x for x in comic_sub.get("sources", []) if x.get("id") != "picacg"]
comic_sub["sources"].append(comic_entry)
dump_json(COMIC_SUB_PATH, comic_sub)

detail = {
    "id": "picacg",
    "name": "◈ 哔咔漫画",
    "version": VERSION,
    "channel": "stable",
    "type": "漫画",
    "status": "Stable / 正式",
    "summary": "Beta9 真机确认后晋升正式版；详情顶部定制按钮已恢复，相关推荐保留一次性集合与强去重。",
    "tags": ["漫画源", "Stable", "Picacg", "双线路", "登录", "账号", "评论", "楼中楼", "标签", "定制按钮"],
    "updatedAt": NOW_ISO,
    "changelog": [
        "由 1.0.0-beta9 真机确认基线原样晋升 Stable，不改动业务逻辑。",
        "详情页顶部定制按钮已确认可直接打开独立哔咔评论中心。",
        "相关推荐仅返回首批一次，后续页硬终止，并按 ID/标题/封面独立去重。",
        "保留登录、账户中心、签到、评论/楼中楼、点赞收藏与标签跳转。",
        "保留 APP/API + 网页双线路以及漫画目录/图片正文。"
    ],
    "sourceUrl": stable_entry["sourceUrl"],
    "backupUrl": stable_entry["backupUrl"]
}
dump_json(DETAIL_PATH, detail)

manifest_by_id = {x.get("id"): x for x in manifest.get("sources", [])}

def rebuild_bundle(subscription_obj, out_path):
    bundle = []
    for item in subscription_obj.get("sources", []):
        sid = item.get("id")
        meta = manifest_by_id.get(sid)
        assert meta and meta.get("sourcePath"), f"Manifest sourcePath missing for {sid}"
        path = ROOT / meta["sourcePath"]
        assert path.exists(), f"Source file missing for {sid}: {path}"
        bundle.extend(source_list(path))
    dump_json(out_path, bundle)
    return len(bundle)

stable_count = rebuild_bundle(stable_sub, STABLE_BUNDLE_PATH)
beta_count = rebuild_bundle(beta_sub, BETA_BUNDLE_PATH)
assert any(x.get("bookSourceUrl") == SOURCE_ID for x in load_json(STABLE_BUNDLE_PATH)), "Picacg missing from Stable bundle"
assert not any(x.get("bookSourceUrl") == SOURCE_ID for x in load_json(BETA_BUNDLE_PATH)), "Picacg still present in Beta bundle"

release = RELEASE_PATH.read_text(encoding="utf-8")
entry = f"""## {DATE} — Picacg {VERSION} Stable

Status: Stable; user real-device confirmed and explicitly promoted.

Changes:

- Promoted the exact `1.0.0-beta9` functional baseline to Stable; no new business behavior was added during promotion.
- User confirmed the detail-page custom button is restored and opens the Picacg comment center.
- Retained one-shot recommendations (`page > 1` returns empty) plus independent ID/title/cover de-duplication.
- Retained APP/API + Web dual routes, login/account, comments/nested replies, likes/favourites, tags, TOC and manga image content.
- Stable source / Manifest / Stable subscription / Comic subscription / Stable bundle / Beta channel removal / Stable RSS detail were synchronized.
- Published source SHA256: `{sha256}`.


"""
RELEASE_PATH.write_text(entry + release, encoding="utf-8")

print(json.dumps({
    "version": VERSION,
    "name": src["bookSourceName"],
    "sha256": sha256,
    "stable_bundle_sources": stable_count,
    "beta_bundle_sources": beta_count,
    "updatedAt": NOW_ISO
}, ensure_ascii=False, indent=2))
