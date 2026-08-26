import hashlib
import json
import pathlib
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_ID = "https://sc8d7.invalid/legado/picacg-8d7"
VERSION = "1.0.0"
VERSION_CODE = 10000
NOW = datetime.now(ZoneInfo("Asia/Shanghai"))
NOW_ISO = NOW.isoformat(timespec="seconds")
DATE = NOW.strftime("%Y-%m-%d")

STABLE_PATH = ROOT / "sources/comic/picacg/picacg.json"
MANIFEST_PATH = ROOT / "manifest.json"
STABLE_SUB_PATH = ROOT / "subscription/stable.json"
BETA_SUB_PATH = ROOT / "subscription/beta.json"
COMIC_SUB_PATH = ROOT / "subscription/comic.json"
STABLE_BUNDLE_PATH = ROOT / "bundles/all-stable.json"
BETA_BUNDLE_PATH = ROOT / "bundles/all-beta.json"
DETAIL_PATH = ROOT / "rss/data/details/stable/picacg.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_list(path):
    data = load_json(path)
    return data if isinstance(data, list) else [data]


stable_source = load_json(STABLE_PATH)
assert isinstance(stable_source, list) and len(stable_source) == 1
src = stable_source[0]
assert src.get("bookSourceUrl") == SOURCE_ID
assert src.get("bookSourceName") == "◈ 哔咔漫画"
assert src.get("customButton") is True and src.get("eventListener") is True
assert "java.startBrowser" in src.get("ruleContent", {}).get("callBackJs", "")
sha256 = hashlib.sha256(STABLE_PATH.read_bytes()).hexdigest()

manifest = load_json(MANIFEST_PATH)
manifest["updatedAt"] = NOW_ISO
manifest_by_id = {x.get("id"): x for x in manifest.get("sources", [])}
pica_meta = manifest_by_id.get("picacg")
assert pica_meta and pica_meta.get("channel") == "stable"
pica_meta["updatedAt"] = NOW_ISO
pica_meta["sha256"] = sha256
dump_json(MANIFEST_PATH, manifest)

raw = f"https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg.json?v={VERSION_CODE}"
cdn = f"https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg.json?v={VERSION_CODE}"
detail_url = f"https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/stable/picacg.json?v={VERSION_CODE}"

stable_item = {
    "id": "picacg",
    "name": "◈ 哔咔漫画",
    "summary": "正式版：Beta9 真机确认后原样晋升；详情顶部定制按钮恢复，相关推荐保持首批一次性返回与强去重。",
    "icon": "https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/assets/source-core-source-icon.svg",
    "channel": "stable",
    "version": VERSION,
    "updatedAt": DATE,
    "tags": ["哔咔", "漫画", "正式版", "APP API", "网页线路", "评论", "楼中楼", "定制按钮", "双线路"],
    "changelog": [
        "由 1.0.0-beta9 真机确认基线原样晋升 Stable，不新增业务逻辑",
        "详情页顶部定制按钮已真机确认恢复，可直接进入独立哔咔评论中心",
        "相关推荐保留 page>1 硬终止和漫画 ID/标题/封面路径三层独立去重",
        "保留登录、账户中心、签到、点赞收藏、评论/楼中楼、标签、目录、漫画图片正文及 APP/Web 双线路"
    ],
    "sourceUrl": raw,
    "backupUrl": cdn,
    "importUrl": f"legado://import/bookSource?src={raw}",
    "detailUrl": detail_url
}

stable_sub = load_json(STABLE_SUB_PATH)
stable_sub["updatedAt"] = NOW_ISO
stable_sub["generatedAt"] = NOW_ISO
stable_sub["items"] = [x for x in stable_sub.get("items", []) if x.get("id") != "picacg"]
stable_sub["items"].append(stable_item)
stable_sub.pop("sources", None)
dump_json(STABLE_SUB_PATH, stable_sub)

beta_sub = load_json(BETA_SUB_PATH)
beta_sub["updatedAt"] = NOW_ISO
beta_sub["generatedAt"] = NOW_ISO
beta_sub["items"] = [x for x in beta_sub.get("items", []) if x.get("id") != "picacg"]
beta_sub.pop("sources", None)
dump_json(BETA_SUB_PATH, beta_sub)

comic_sub = load_json(COMIC_SUB_PATH)
comic_sub["updatedAt"] = NOW_ISO
comic_sub["generatedAt"] = NOW_ISO
comic_item = dict(stable_item)
comic_item["type"] = "comic"
comic_sub["items"] = [x for x in comic_sub.get("items", []) if x.get("id") != "picacg"]
comic_sub["items"].append(comic_item)
comic_sub.pop("sources", None)
dump_json(COMIC_SUB_PATH, comic_sub)

detail = load_json(DETAIL_PATH)
detail.update({
    "version": VERSION,
    "channel": "stable",
    "status": "Stable / 正式",
    "updatedAt": NOW_ISO,
    "sourceUrl": raw,
    "backupUrl": cdn
})
dump_json(DETAIL_PATH, detail)

manifest_by_id = {x.get("id"): x for x in manifest.get("sources", [])}

def rebuild_bundle(catalog, out_path):
    out = []
    for item in catalog.get("items", []):
        sid = item.get("id")
        meta = manifest_by_id.get(sid)
        assert meta and meta.get("sourcePath"), f"Missing manifest sourcePath: {sid}"
        path = ROOT / meta["sourcePath"]
        assert path.exists(), f"Missing source file: {path}"
        out.extend(source_list(path))
    dump_json(out_path, out)
    return len(out)

stable_count = rebuild_bundle(stable_sub, STABLE_BUNDLE_PATH)
beta_count = rebuild_bundle(beta_sub, BETA_BUNDLE_PATH)
assert stable_count == len(stable_sub.get("items", []))
assert beta_count == len(beta_sub.get("items", []))
assert any(x.get("bookSourceUrl") == SOURCE_ID for x in load_json(STABLE_BUNDLE_PATH))
assert not any(x.get("bookSourceUrl") == SOURCE_ID for x in load_json(BETA_BUNDLE_PATH))

print(json.dumps({
    "version": VERSION,
    "name": src["bookSourceName"],
    "sha256": sha256,
    "stable_catalog_items": len(stable_sub.get("items", [])),
    "stable_bundle_sources": stable_count,
    "beta_catalog_items": len(beta_sub.get("items", [])),
    "beta_bundle_sources": beta_count,
    "updatedAt": NOW_ISO
}, ensure_ascii=False, indent=2))
