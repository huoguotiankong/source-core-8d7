import json
import pathlib
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOW = datetime.now(ZoneInfo('Asia/Shanghai'))
NOW_ISO = NOW.isoformat(timespec='seconds')
DATE = NOW.strftime('%Y-%m-%d')
NOW_MS = int(NOW.timestamp() * 1000)
RAW = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/'
CDN = 'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/'
CANONICAL_RSS_PATH = 'rss/reader-source-repository-beta.json'
CANONICAL_RSS_URL = RAW + CANONICAL_RSS_PATH


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def dump(path, obj):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def upsert_doc_append(path, marker, text):
    p = ROOT / path
    s = p.read_text(encoding='utf-8')
    if marker not in s:
        if not s.endswith('\n'):
            s += '\n'
        s += '\n' + text.strip() + '\n'
        p.write_text(s, encoding='utf-8')


def prepend_release(marker, text):
    p = ROOT / 'docs/RELEASE_LOG.md'
    s = p.read_text(encoding='utf-8')
    if marker not in s:
        p.write_text(text.strip() + '\n\n\n' + s, encoding='utf-8')

# 1) Canonical active RSS source: keep the already-imported Beta identity so users update in place.
rss = load(CANONICAL_RSS_PATH)
assert isinstance(rss, list) and len(rss) == 1
src = rss[0]
assert src.get('sourceUrl') == CANONICAL_RSS_URL
src['sourceName'] = '🌈 阅读书源仓库'
src['sourceGroup'] = '书源仓库'
src['sourceComment'] = '唯一当前仓库订阅入口。UI Beta14：一次性清理旧 RSS 文章缓存；漫画、仓库订阅、正式版、测试版分类从本版起固定身份。'
src['sortUrl'] = '\n'.join([
    f'🏠 首页::{RAW}rss/data/home-beta.json',
    f'🖼 漫画::{RAW}subscription/comic.json?reset=1',
    f'📰 仓库订阅::{RAW}subscription/rss.json?reset=1',
    f'⭐ 正式版::{RAW}subscription/stable.json?reset=1',
    f'🧪 测试版::{RAW}subscription/beta.json?reset=1',
    f'📦 批量::{RAW}rss/data/bundle.json',
    f'📖 帮助::{RAW}rss/data/help.json',
])
rule_content = src.get('ruleContent', '')
rule_content = rule_content.replace('🌈 阅读书源仓库 · UI Beta 13', '🌈 阅读书源仓库 · UI Beta 14')
src['ruleContent'] = rule_content
src['lastUpdateTime'] = NOW_MS
dump(CANONICAL_RSS_PATH, rss)

# 2) RSS type catalog: one logical repository source, not Stable+Beta duplicates.
rss_catalog = {
    'schemaVersion': 1,
    'type': 'rss',
    'name': '仓库订阅',
    'updatedAt': NOW_ISO,
    'items': [{
        'id': 'reader-repository',
        'name': '🌈 阅读书源仓库',
        'summary': '唯一当前仓库订阅入口；沿用现有最新订阅身份原位更新，不再同时展示 Stable/Beta 两个重复仓库源。',
        'icon': CDN + 'assets/reader-repo-icon.png',
        'channel': 'current',
        'meta': '当前',
        'version': '0.4.0-beta14',
        'updatedAt': DATE,
        'tags': ['订阅源', '仓库', '当前入口', '去重'],
        'sourceUrl': CANONICAL_RSS_URL,
        'importUrl': 'legado://import/rssSource?src=' + CANONICAL_RSS_URL,
        'detailUrl': RAW + 'rss/data/details/rss/repository-current.json'
    }]
}
dump('subscription/rss.json', rss_catalog)

dump('rss/data/details/rss/repository-current.json', {
    'kind': 'rss',
    'title': '🌈 阅读书源仓库',
    'summary': '当前唯一仓库订阅入口。更新会覆盖现有最新仓库订阅，不再额外创建 Stable/Beta 重复入口。',
    'badges': ['订阅源', '唯一入口', 'UI Beta14'],
    'sections': [
        {'title': '当前策略', 'text': '仓库订阅只保留一个活动入口；书源本身仍按 Stable / Beta 分通道。'},
        {'title': '缓存迁移', 'text': '本版对漫画、仓库订阅、正式版、测试版分类做一次性身份重置，用于摆脱阅读持久化的旧文章。之后这些分类身份固定，不再随 UI 版本变化。'}
    ],
    'rssUrl': CANONICAL_RSS_URL
})

# 3) Ensure Picacg is Stable-only in active catalogs and freeze its RSS article detail identity.
for catalog_path in ['subscription/stable.json', 'subscription/comic.json']:
    c = load(catalog_path)
    items = c.get('items', [])
    found = [x for x in items if x.get('id') == 'picacg']
    assert len(found) == 1, f'Expected exactly one Picacg in {catalog_path}'
    p = found[0]
    assert p.get('channel') == 'stable' and p.get('version') == '1.0.0'
    p['name'] = '◈ 哔咔漫画'
    p['detailUrl'] = RAW + 'rss/data/details/stable/picacg.json'
    c['updatedAt'] = NOW_ISO
    c['generatedAt'] = NOW_ISO
    dump(catalog_path, c)

beta = load('subscription/beta.json')
assert not any(x.get('id') == 'picacg' for x in beta.get('items', [])), 'Picacg must not remain in active Beta catalog'

# 4) Repository manifest points to the one active/current RSS entry.
manifest = load('manifest.json')
manifest['updatedAt'] = NOW_ISO
manifest['rssSource'] = CANONICAL_RSS_URL
for e in manifest.get('sources', []):
    if e.get('id') == 'picacg':
        assert e.get('channel') == 'stable' and e.get('version') == '1.0.0'
        assert e.get('sourcePath') == 'sources/comic/picacg/picacg.json'
dump('manifest.json', manifest)

# 5) Long-term project rules/docs.
upsert_doc_append(
    'docs/DEVELOPMENT_RULES.md',
    '## 18. Single active RSS repository entry and logical-source de-duplication',
    '''## 18. Single active RSS repository entry and logical-source de-duplication

The repository itself is one logical RSS source. Do not publish separate Stable/Beta repository RSS entries as simultaneously active choices when they expose the same repository.

- `subscription/rss.json` lists exactly one current repository entry.
- Preserve the current released RSS `sourceUrl` identity for in-place updates; UI status/version belongs in metadata, not in extra duplicate RSS sources.
- Type catalogs such as `subscription/comic.json` list only the latest active channel entry for a logical source. A source promoted to Stable is removed from the active Beta/type duplicate listing.
- Historical JSON/detail files may remain for compatibility/history, but they are not active catalog entries.
- RSS item `detailUrl` is a long-lived article identity and must not receive routine version query parameters.
- When persisted old RSS articles make clean replacement impossible, one deliberate category identity reset is allowed. After that migration, freeze the new category names/URLs; do not repeat the reset per release.
'''
)

upsert_doc_append(
    'docs/KNOWN_ISSUES.md',
    '## RSS historical duplicate articles and duplicate repository entries — Beta14 migration',
    '''## RSS historical duplicate articles and duplicate repository entries — Beta14 migration

Real-device symptom on 2026-08-26:

- 漫画分类同时显示当前 Stable 哔咔、旧 Beta 哔咔和更早的长名称 Beta 条目，尽管当前 `subscription/comic.json` 已只有一个 Stable 项。
- 仓库订阅分类同时显示 Stable/Beta 两个名称不同但逻辑相同的仓库 RSS 源。
- 正式版通道未可靠反映刚晋升的 Picacg Stable，表现符合旧分类文章缓存仍在参与展示。

Cause:

- Legado persists RSS articles from older category/article identities; deleting an item from current channel JSON does not delete historical stored articles.
- Earlier repository design also intentionally advertised two repository RSS definitions, which is unnecessary for a single logical repository source.
- Picacg Stable detail URL had a version query, which would create future article identities if incremented.

Beta14 migration:

- keep the already-imported latest RSS source identity and update it in place;
- make `subscription/rss.json` contain exactly one current repository entry;
- perform one deliberate category identity reset for 漫画 / 仓库订阅 / 正式版 / 测试版, then freeze those identities permanently;
- keep only Picacg Stable 1.0.0 in the active comic catalog and remove version query from its RSS detail identity;
- Stable/Beta book-source channels remain separate; only the duplicate repository-RSS entry is collapsed.

Status: published as UI Beta14 for real-device confirmation.
'''
)

upsert_doc_append(
    'docs/PROJECT_PLAN.md',
    '## 13. Single current repository RSS entry',
    '''## 13. Single current repository RSS entry

From RSS UI Beta14 onward, the repository itself has one active subscription entry. Stable/Beta remain release channels for book sources, not duplicate active RSS repository definitions. The latest already-imported RSS identity is preserved for in-place updates, while legacy repository JSON files may remain only as compatibility artifacts and are not listed in the active RSS catalog.
'''
)

prepend_release(
    'RSS UI 0.4.0-beta14 single-entry cleanup',
    f'''## {DATE} — RSS UI 0.4.0-beta14 single-entry cleanup

Status: Beta/Test; user requested repository/subscription de-duplication after real-device screenshots showed historical RSS entries still visible.

Changes:

- The repository RSS catalog now exposes one current `🌈 阅读书源仓库` entry instead of separate Stable/Beta duplicates.
- The already-imported latest RSS `sourceUrl` identity is preserved so Beta13 updates in place rather than creating another subscription source.
- One deliberate cache migration resets the category identity for 漫画 / 仓库订阅 / 正式版 / 测试版; these identities are frozen after Beta14.
- `subscription/comic.json` remains one active Picacg entry only: `◈ 哔咔漫画 1.0.0 Stable`.
- Picacg Stable is confirmed present in `subscription/stable.json`; its RSS detail article identity is now the permanent non-versioned Stable detail URL.
- Historical Beta/detail/source files remain only for compatibility/history and are not active catalog entries.
'''
)

# Final gates.
rss2 = load(CANONICAL_RSS_PATH)[0]
assert rss2['sourceName'] == '🌈 阅读书源仓库'
assert '?reset=1' in rss2['sortUrl'] and 'UI Beta 14' in rss2['ruleContent']
assert len(load('subscription/rss.json').get('items', [])) == 1
comic_items = load('subscription/comic.json').get('items', [])
assert len(comic_items) == 1 and comic_items[0].get('id') == 'picacg' and comic_items[0].get('channel') == 'stable'
stable_items = load('subscription/stable.json').get('items', [])
assert any(x.get('id') == 'picacg' and x.get('channel') == 'stable' for x in stable_items)
assert all('?v=' not in x.get('detailUrl', '') for x in comic_items if x.get('id') == 'picacg')
assert manifest['rssSource'] == CANONICAL_RSS_URL

print(json.dumps({
    'rss_ui': '0.4.0-beta14',
    'rss_entries': 1,
    'comic_entries': len(comic_items),
    'picacg_stable_visible': True,
    'canonical_rss': CANONICAL_RSS_URL,
    'updatedAt': NOW_ISO
}, ensure_ascii=False, indent=2))
