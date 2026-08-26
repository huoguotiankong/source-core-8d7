import json
import hashlib
import pathlib
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
VERSION = '1.0.0-beta6'
VERSION_CODE = 10006
DISPLAY_NAME = '🍥 哔咔漫画'
SOURCE_ID = 'https://sc8d7.invalid/legado/picacg-8d7'
DATE = '2026-08-26'
NOW = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
SUMMARY = 'Beta6：互动区改为评论/推荐同排、点赞/收藏同排；书源显示名精简为「🍥 哔咔漫画」；漫画正文 customButton 已确认受 MangaMenu 上游限制。'
CHANGELOG = [
    '互动与操作重排：第一行查看评论 + 相关推荐，第二行点赞作品 + 收藏作品',
    '书源显示名精简为「🍥 哔咔漫画」，不再把 APP/网页双线路、Beta 等状态塞进 bookSourceName',
    '再次核对阅读当前上游：文本 ReadMenu 有 customButton 控件与 CLICK_CUSTOM_BUTTON 分发，图片 MangaMenu 没有，漫画正文无法仅靠书源 JSON 增加该按钮',
    '详情页定制按钮仍保留并直达评论；作品数据、作者/汉化组/分类/标签点击能力保持不变',
    '账号、评论、楼中楼、目录、漫画图片正文及 APP/Web 双线路核心链冻结'
]
TAGS = ['哔咔', '漫画', 'APP API', '网页线路', '评论', '详情增强', '简洁命名', 'MangaMenu', '双线路']


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def dump_json(path, data):
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


# 1) Source JSON: narrow UI/name-only change.
source_path = ROOT / 'sources/comic/picacg/picacg-beta.json'
sources = json.loads(source_path.read_text(encoding='utf-8'))
assert isinstance(sources, list) and len(sources) == 1
src = sources[0]
assert src.get('bookSourceUrl') == SOURCE_ID
src['bookSourceName'] = DISPLAY_NAME
src['bookSourceComment'] = (
    '【v1.0.0-beta6 · 2026-08-26】\n'
    '哔咔漫画 UI / 命名调整测试版。\n\n'
    'Beta6：\n'
    '• 互动与操作改为两行双按钮：第一行「查看评论 / 相关推荐」，第二行「点赞作品 / 收藏作品」。\n'
    '• 书源显示名精简为「🍥 哔咔漫画」；线路、Beta、版本等信息只放在说明/订阅元数据，不再堆到书源名称。\n'
    '• 再次核对阅读当前上游：文本正文 ReadMenu 有 customButton 控件和 CLICK_CUSTOM_BUTTON 回调；图片漫画正文 MangaMenu 没有对应控件和回调。因此漫画正文定制按钮属于 App 侧能力缺口，无法仅靠书源 JSON 补出。\n'
    '• 详情页定制按钮仍保留并直达哔咔评论。\n'
    '• 作品数据、描述、作品信息及作者/汉化组/分类/标签点击能力不变。\n'
    '• 账号、评论、楼中楼、目录、漫画图片正文和 APP/Web 双线路核心链冻结。\n\n'
    '本版仍为 Beta，等待真机确认互动区与短名称显示。'
)
intro = src['ruleBookInfo']['intro']
old_row1 = '<button>💬 查看评论@onclick:picaBookInfoOpenComments.call(this)</button> <button>♥ 点赞作品@onclick:picaBookInfoLike.call(this)</button>'
old_row2 = '<button>⭐ 收藏作品@onclick:picaBookInfoFavourite.call(this)</button> <button>🧭 相关推荐@onclick:picaBookInfoRecommend.call(this)</button>'
new_row1 = '<button>💬 查看评论@onclick:picaBookInfoOpenComments.call(this)</button> <button>🧭 相关推荐@onclick:picaBookInfoRecommend.call(this)</button>'
new_row2 = '<button>♥ 点赞作品@onclick:picaBookInfoLike.call(this)</button> <button>⭐ 收藏作品@onclick:picaBookInfoFavourite.call(this)</button>'
assert old_row1 in intro, 'beta5 interaction row1 baseline not found'
assert old_row2 in intro, 'beta5 interaction row2 baseline not found'
intro = intro.replace(old_row1, new_row1, 1).replace(old_row2, new_row2, 1)
src['ruleBookInfo']['intro'] = intro
source_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()

# 2) Smoke checks: JSON + important JS syntax.
json.loads(source_path.read_text(encoding='utf-8'))
assert src['bookSourceName'] == DISPLAY_NAME
assert intro.index(new_row1) < intro.index(new_row2)
assert 'APP/网页双线路 Beta' not in src['bookSourceName']
for label, code in [('jsLib', src.get('jsLib', '')), ('bookInfoIntro', intro)]:
    if not code:
        continue
    if label == 'bookInfoIntro':
        code = code.replace('<js>', '', 1)
        if code.rstrip().endswith('</js>'):
            code = code.rstrip()[:-5]
    with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as f:
        f.write(code)
        temp = f.name
    subprocess.run(['node', '--check', temp], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 3) Manifest metadata.
manifest = load_json('manifest.json')
entry = next(x for x in manifest['sources'] if x.get('id') == 'picacg')
entry.update({
    'name': DISPLAY_NAME,
    'channel': 'beta',
    'version': VERSION,
    'versionCode': VERSION_CODE,
    'updatedAt': NOW,
    'summary': SUMMARY,
    'tags': TAGS,
    'changelog': CHANGELOG,
    'sha256': sha256,
})
manifest['updatedAt'] = NOW
dump_json('manifest.json', manifest)

# 4) Beta + comic catalogs. Keep detailUrl untouched to preserve RSS article identity.
for catalog_path in ['subscription/beta.json', 'subscription/comic.json']:
    catalog = load_json(catalog_path)
    item = next(x for x in catalog['items'] if x.get('id') == 'picacg')
    detail_url = item.get('detailUrl')
    item.update({
        'name': DISPLAY_NAME,
        'summary': SUMMARY,
        'channel': 'beta',
        'version': VERSION,
        'updatedAt': DATE,
        'tags': TAGS,
        'changelog': CHANGELOG,
        'sourceUrl': f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
        'backupUrl': f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
        'importUrl': f'legado://import/bookSource?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
    })
    if detail_url is not None:
        item['detailUrl'] = detail_url
    catalog['updatedAt'] = NOW
    dump_json(catalog_path, catalog)

# 5) Current-state detail payload.
detail = load_json('rss/data/details/beta/picacg.json')
detail.update({
    'title': DISPLAY_NAME,
    'summary': SUMMARY,
    'badges': ['BETA', VERSION, '漫画源', '互动区优化'],
    'sections': [
        {
            'title': '正文定制按钮结论',
            'text': '已再次核对阅读当前上游源码：文本正文 ReadMenu 明确包含 tvCustomBtn，会按 BookSource.customButton 显示并分发 CLICK_CUSTOM_BUTTON；图片漫画正文使用 MangaMenu，而 MangaMenu 当前没有对应控件、显示判断和回调。因此原生漫画正文不能仅靠书源 JSON 增加定制按钮。详情页定制按钮不受此限制，继续保留并直达评论。'
        },
        {
            'title': '互动与操作',
            'text': '按使用关系重新排成 2×2：第一行「查看评论 / 相关推荐」，第二行「点赞作品 / 收藏作品」。'
        },
        {
            'title': '显示名称',
            'text': '书源名精简为「🍥 哔咔漫画」。APP/网页双线路、Beta、版本号等信息继续存在于说明和仓库元数据中，不再占用书源列表名称。'
        },
        {
            'title': '作品信息',
            'text': '作品数据、描述、作者、汉化组、上传者、分类、标签、更新时间、上传时间及权限展示保持不变；作者/汉化组/分类/标签继续可点击。'
        },
        {
            'title': '核心保护',
            'text': '账号、签到、收藏、点赞、评论中心、楼中楼、目录、漫画图片正文及 APP/Web 双线路不改。'
        },
        {
            'title': '发布状态',
            'text': 'Beta / 测试版；等待真机确认互动区和短名称显示。'
        },
        {
            'title': '唯一身份',
            'text': SOURCE_ID
        }
    ],
    'sourceUrl': f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
    'backupUrl': f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
})
dump_json('rss/data/details/beta/picacg.json', detail)

# 6) Replace only Picacg source inside Beta bundle.
bundle_path = ROOT / 'bundles/all-beta.json'
bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
replaced = 0

def replace_source(node):
    global replaced
    if isinstance(node, list):
        for i, value in enumerate(node):
            if isinstance(value, dict) and value.get('bookSourceUrl') == SOURCE_ID:
                node[i] = json.loads(json.dumps(src, ensure_ascii=False))
                replaced += 1
            else:
                replace_source(value)
    elif isinstance(node, dict):
        for key, value in list(node.items()):
            if isinstance(value, dict) and value.get('bookSourceUrl') == SOURCE_ID:
                node[key] = json.loads(json.dumps(src, ensure_ascii=False))
                replaced += 1
            else:
                replace_source(value)

replace_source(bundle)
assert replaced >= 1, 'Picacg entry not found in Beta bundle'
bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# 7) Release log.
release_path = ROOT / 'docs/RELEASE_LOG.md'
release = release_path.read_text(encoding='utf-8')
release_entry = f'''\n## 2026-08-26 — Picacg {VERSION} interaction order + concise source naming\n\nStatus: Beta/Test; awaiting user real-device confirmation.\n\nChanges:\n\n- 互动区改为第一行「查看评论 / 相关推荐」，第二行「点赞作品 / 收藏作品」\n- `bookSourceName` 精简为「{DISPLAY_NAME}」，不再追加 APP/网页双线路、Beta、版本等长后缀\n- 再次核对阅读当前上游：文本 `ReadMenu` 有 `tvCustomBtn`、`customButton` 可见性判断和 `CLICK_CUSTOM_BUTTON` 分发；图片 `MangaMenu` 没有，因此漫画正文无法仅靠书源 JSON 增加定制按钮\n- 详情页定制按钮继续保留并直达评论；作品数据与作品信息布局保持 Beta5 基线\n- 账号、评论、楼中楼、目录、漫画图片正文和 APP/Web 双线路核心链冻结\n- Published SHA256: `{sha256}`.\n\n'''
assert release.startswith('# RELEASE LOG\n')
release_path.write_text('# RELEASE LOG\n' + release_entry + release[len('# RELEASE LOG\n'):], encoding='utf-8')

# 8) Project-wide concise naming rule requested by the user.
rules_path = ROOT / 'docs/DEVELOPMENT_RULES.md'
rules = rules_path.read_text(encoding='utf-8')
rules = rules.replace('> Updated: 2026-08-25', '> Updated: 2026-08-26', 1)
section = '''\n## 17. Concise source display naming\n\n`bookSourceName` / RSS source display names should be short and recognizable. Default format:\n\n`<one distinctive icon> <source/platform name>`\n\nExamples: `🍥 哔咔漫画`, `🌈 起点增强`.\n\n- Do not append Beta/Stable, version numbers, APP/Web route descriptions, long capability lists or marketing-style suffixes to the in-app source name.\n- Put channel, version, route architecture and feature descriptions in `bookSourceComment`, Manifest/Subscription metadata, tags and changelog instead.\n- Add a textual suffix only when two independently installable sources would otherwise be genuinely ambiguous, and keep that suffix short.\n- When renaming an existing source, preserve its stable `bookSourceUrl` identity so updates continue in place.\n\n'''
if '## 17. Concise source display naming' not in rules:
    rules = rules.rstrip() + '\n' + section
rules_path.write_text(rules, encoding='utf-8')

# 9) Refresh the already-confirmed known-issue note with latest-upstream recheck.
issues_path = ROOT / 'docs/KNOWN_ISSUES.md'
issues = issues_path.read_text(encoding='utf-8')
issues = issues.replace('> Updated: 2026-08-25', '> Updated: 2026-08-26', 1)
needle = 'Rule: do not keep mutating customButton/eventListener inside image-source content rules expecting MangaMenu to render a missing control.'
recheck = 'Latest upstream master was rechecked on 2026-08-26: ReadMenu still has tvCustomBtn/customButton/CLICK_CUSTOM_BUTTON, while MangaMenu still has none of those pieces.\n\n'
if needle in issues and recheck.strip() not in issues:
    issues = issues.replace(needle, recheck + needle, 1)
issues_path.write_text(issues, encoding='utf-8')

# Final parse/regression checks on all touched JSON.
for p in [
    'sources/comic/picacg/picacg-beta.json',
    'manifest.json',
    'subscription/beta.json',
    'subscription/comic.json',
    'rss/data/details/beta/picacg.json',
    'bundles/all-beta.json',
]:
    json.loads((ROOT / p).read_text(encoding='utf-8'))

print(json.dumps({
    'version': VERSION,
    'name': DISPLAY_NAME,
    'sha256': sha256,
    'bundle_replacements': replaced,
    'updatedAt': NOW,
}, ensure_ascii=False, indent=2))
