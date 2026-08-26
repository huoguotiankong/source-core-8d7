import copy
import hashlib
import json
import pathlib
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
SRC_PATH = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'


def dump_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


data = json.loads(SRC_PATH.read_text(encoding='utf-8'))
assert isinstance(data, list) and len(data) == 1, 'qidian-next beta must contain exactly one source'
src = data[0]
assert src.get('bookSourceName') == '🌈 起点增强 · Beta', src.get('bookSourceName')
old_comment = str(src.get('bookSourceComment') or '')
already = 'v1.1.0-beta8' in old_comment
if not already:
    assert 'v1.1.0-beta7' in old_comment, 'unexpected qidian-next beta baseline'

frozen = {
    'jsLib': copy.deepcopy(src.get('jsLib')),
    'ruleSearch': copy.deepcopy(src.get('ruleSearch')),
    'ruleExplore': copy.deepcopy(src.get('ruleExplore')),
    'ruleToc': copy.deepcopy(src.get('ruleToc')),
    'ruleContent': copy.deepcopy(src.get('ruleContent')),
    'searchUrl': copy.deepcopy(src.get('searchUrl')),
    'exploreUrl': copy.deepcopy(src.get('exploreUrl')),
    'loginUrl': copy.deepcopy(src.get('loginUrl')),
    'shouldOverrideUrlLoading': copy.deepcopy(src.get('shouldOverrideUrlLoading')),
}

if not already:
    src['bookSourceComment'] = (
        'v1.1.0-beta8：详情完整数据回归修复版。恢复此前已验证的起点官方 APP bookDetailInfo 富化链，'
        '保留 beta7 当前响应、搜索参数与书籍缓存快速路径；当前详情资料完整时 0 次额外补全，资料稀疏时最多调用 1 次官方 APP 详情并做 30 分钟防重复。'
        '恢复作品简介、总推荐、在看、收藏、粉丝、月票、评分/评分人数、盟主、投资/首订、作者资料、标签/荣誉等详情字段；'
        '移除失败的 TTS 唯一补全请求和临时简介诊断。搜索、目录、正文 Provider、段评/本章说、角色卡、书友圈及情无 VIP 认证链不改。'
    )

    bi = src.setdefault('ruleBookInfo', {})
    init = str(bi.get('init') or '')
    ui = str(bi.get('intro') or '')

    init_lines = init.splitlines(True)
    diag_lines = [x for x in init_lines if 'info.introDiag=' in x]
    assert len(diag_lines) >= 1, f'expected introDiag assignment, got {len(diag_lines)}'
    init = ''.join(x for x in init_lines if 'info.introDiag=' not in x)

    probe_start = init.find('function introProbeV1107(html){')
    cached_start = init.find('function cached(', probe_start)
    assert probe_start >= 0 and cached_start > probe_start, 'introProbeV1107 block not found'
    init = init[:probe_start] + init[cached_start:]

    fn_start = init.find('function qfDetailPcEnrichV1104(){')
    fn_end = init.find('qfNormalizeDetailV1104();', fn_start)
    assert fn_start >= 0 and fn_end > fn_start, 'Beta7 PC enrichment block not found'

    new_fn = '''function qfDetailOfficialEnrichV1108(){
  if(!bid||!qfDetailSparseV1104())return;
  var last=Number(bv('qf_detailOfficialEnrichedAtV1108')||0),now=Date.now();
  if(last>0&&now-last<1800000)return;
  try{qfPutBookVarV09.call(this,'qf_detailOfficialEnrichedAtV1108',String(now));}catch(_ts){}
  var appInfo=null;
  try{appInfo=qfOfficialCallV400.call(this,'bookDetailInfo',[String(bid)]);}catch(_app){appInfo=null;}
  if(!appInfo||!appInfo.ok)return;
  function ap(k,prefer){
    var v=appInfo[k];
    if(v===undefined||v===null||String(v).trim()==='')return;
    if(prefer||blank(info[k]))info[k]=v;
  }
  ap('intro',true);
  ap('recommendCount',true);ap('readingCount',true);ap('collectionCount',true);ap('fansCount',true);ap('monthTicket',true);
  ap('ratingScore',true);ap('ratingCount',true);ap('leaderCount',true);ap('investCount',true);ap('firstSubscribe',true);
  ap('limitStart',true);ap('limitEnd',true);ap('limitFreeType',true);ap('limitFreeText',true);ap('isLimitedFree',true);ap('freshManBlackList',true);
  ap('authorLevel',true);ap('authorDesc',true);ap('authorWorksCount',true);ap('authorTags',true);
  ap('wordCount',false);ap('publishDate',false);ap('listingDate',false);ap('bookTags',false);ap('tags',false);ap('honors',false);ap('rights',false);ap('isVip',true);
  ap('kind',false);ap('subKind',false);ap('status',false);ap('updateTime',false);
  if((!info.tags||!info.tags.length)&&appInfo.bookTags)info.tags=appInfo.bookTags;
  if(!blank(info.readingCount))info.readingMetricLabel='在看';
  info.detailSource=(info.detailSource?info.detailSource+'+':'')+'app-bookdetail-v1108';
}
'''
    init = init[:fn_start] + new_fn + init[fn_end:]
    assert init.count('qfDetailPcEnrichV1104.call(this);') == 1
    init = init.replace('qfDetailPcEnrichV1104.call(this);', 'qfDetailOfficialEnrichV1108.call(this);', 1)

    ui_lines = ui.splitlines(True)
    ui_diag = [x for x in ui_lines if 'x.introDiag' in x]
    assert len(ui_diag) == 1, f'expected one intro diagnostic UI line, got {len(ui_diag)}'
    ui = ''.join(x for x in ui_lines if 'x.introDiag' not in x)

    bi['init'] = init
    bi['intro'] = ui

for key, value in frozen.items():
    assert src.get(key) == value, f'frozen module changed: {key}'

init = str(src['ruleBookInfo']['init'])
ui = str(src['ruleBookInfo']['intro'])
assert "qfOfficialCallV400.call(this,'bookDetailInfo',[String(bid)])" in init
assert 'qfDetailOfficialEnrichV1108.call(this);' in init
assert 'qfDetailSparseV1104' in init
assert '/ttsbook/' not in init
assert 'qfDetailPcEnrichV1104' not in init
assert 'introDiag' not in init
assert 'introDiag' not in ui
for label in ['▍作品资料', '▍作品数据', '总推荐', '月票', '收藏', '粉丝', '盟主', '首订', '▍快捷入口', '▍内容简介']:
    assert label in ui, f'missing UI field: {label}'
assert 'qfContentEntryV38' in str(src.get('ruleContent'))
assert 'qfCatalogLoad.call' in str(src.get('ruleToc'))

out_text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
json.loads(out_text)
SRC_PATH.write_text(out_text, encoding='utf-8')
sha256 = hashlib.sha256(out_text.encode('utf-8')).hexdigest()

now_dt = datetime.now(timezone(timedelta(hours=8)))
now = now_dt.isoformat(timespec='seconds')
day = now_dt.date().isoformat()
version = '1.1.0-beta8'
version_code = 11008
raw_url = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v=11008'
backup_url = 'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v=11008'
import_url = 'legado://import/importonline?src=' + raw_url
detail_url = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'
summary = '详情 beta8：恢复官方 APP bookDetailInfo 完整富化，保留当前页面/缓存快速路径；稀疏页最多一次官方请求。'
tags = ['起点', '测试版', '详情页', '完整数据', '官方APP', '按需补全', '缓存', '单请求']
changes = [
    '恢复官方 APP bookDetailInfo 详情富化，补齐简介、推荐、月票、在看、收藏、粉丝、评分、盟主、作者资料等',
    '当前响应与书籍缓存优先，资料完整时不产生额外详情补全请求',
    '资料稀疏时最多一次官方 APP 详情调用，并做 30 分钟防重复',
    '移除失败的 TTS 唯一补全请求与临时简介诊断',
    '搜索、目录、正文 Provider、评论、角色卡、书友圈及情无认证链保持不变',
]

official_path = ROOT / 'sources/novel/qidian/qidian-official.json'
official = json.loads(official_path.read_text(encoding='utf-8'))
assert isinstance(official, list)
dump_json(ROOT / 'bundles/all-beta.json', official + data)

manifest_path = ROOT / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
found = 0
for item in manifest.get('sources', []):
    if item.get('id') == 'qidian-next-beta':
        found += 1
        item.update({
            'name': '🌈 起点增强 · Beta', 'category': 'novel', 'channel': 'beta',
            'version': version, 'versionCode': version_code, 'updatedAt': now,
            'sourcePath': 'sources/novel/qidian-next/qidian-next-beta.json',
            'sourceUrl': raw_url,
            'bookSourceUrl': 'https://m.qidian.com/?qf_source=qidian_next_8d7',
            'summary': summary, 'tags': tags, 'changelog': changes, 'sha256': sha256,
        })
assert found == 1, f'manifest qidian-next-beta count={found}'
manifest['updatedAt'] = now
dump_json(manifest_path, manifest)

sub_path = ROOT / 'subscription/beta.json'
sub = json.loads(sub_path.read_text(encoding='utf-8'))
found = 0
for item in sub.get('items', []):
    if item.get('id') == 'qidian-next-beta':
        found += 1
        item.update({
            'name': '🌈 起点增强 · Beta', 'summary': summary, 'channel': 'beta',
            'version': version, 'updatedAt': day, 'tags': tags, 'changelog': changes,
            'sourceUrl': raw_url, 'backupUrl': backup_url, 'importUrl': import_url,
            'detailUrl': detail_url,
        })
assert found == 1, f'subscription qidian-next-beta count={found}'
sub['updatedAt'] = now
dump_json(sub_path, sub)

detail = {
    'kind': 'source', 'title': '🌈 起点增强 · Beta', 'summary': summary,
    'badges': ['Beta', version, '详情完整数据回归'],
    'sections': [
        {'title': '回归原因', 'text': 'Beta7 把唯一官方补全请求切到 TTS 页面，真机返回极短无效响应，导致原有完整详情富化链被意外裁掉。'},
        {'title': '本版修复', 'text': '恢复此前验证过的起点官方 APP bookDetailInfo 富化链，补齐简介、推荐/月票/在看、收藏/粉丝、评分/盟主、作者资料、标签/荣誉等。'},
        {'title': '速度策略', 'text': '先解析当前已下载页面并复用书籍缓存；资料已完整时 0 次额外请求，稀疏时最多一次官方 APP 详情调用，30 分钟防重复。'},
        {'title': '冻结范围', 'text': '搜索、目录、正文 Provider、段评/本章说、角色卡、书友圈及情无 VIP 认证链均未修改。'},
        {'title': '发布状态', 'text': 'Beta / 测试通道，等待阅读真机确认后再考虑晋升 Stable。'},
    ],
    'sourceUrl': raw_url, 'backupUrl': backup_url, 'importUrl': import_url,
}
dump_json(ROOT / 'rss/data/details/beta/qidian-next.json', detail)

release_path = ROOT / 'docs/RELEASE_LOG.md'
old = release_path.read_text(encoding='utf-8')
marker = f'## {day} — Qidian Next {version} Beta'
if marker not in old:
    block = (
        marker + '\n\nStatus: Beta/Test; awaiting user real-device confirmation.\n\nChanges:\n\n'
        '- Restored the verified official APP `bookDetailInfo` detail-enrichment chain.\n'
        '- Kept current-response parsing and book-variable caches as the zero-request fast path.\n'
        '- Sparse detail pages make at most one official APP detail call with 30-minute deduplication.\n'
        '- Removed the failed TTS-only enrichment request and temporary synopsis diagnostic UI.\n'
        '- Search, catalog, content Providers, reviews, role cards, book circle, and Qingwu VIP auth remain frozen.\n'
        f'- Published SHA256: `{sha256}`.\n\n'
    )
    if old.startswith('# RELEASE LOG'):
        first, rest = old.split('\n', 1)
        old = first + '\n\n' + block + rest.lstrip('\n')
    else:
        old = block + old
    release_path.write_text(old, encoding='utf-8')

for path in [SRC_PATH, ROOT / 'bundles/all-beta.json', manifest_path, sub_path, ROOT / 'rss/data/details/beta/qidian-next.json']:
    json.loads(path.read_text(encoding='utf-8'))
assert json.loads(SRC_PATH.read_text(encoding='utf-8'))[0]['bookSourceUrl'] == 'https://m.qidian.com/?qf_source=qidian_next_8d7'
print('qidian-next beta8 ready', 'sha256', sha256, 'bytes', SRC_PATH.stat().st_size)
