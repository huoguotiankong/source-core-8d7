import copy
import hashlib
import json
from pathlib import Path

ROOT = Path('.')
SOURCE = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
MANIFEST = ROOT / 'manifest.json'
SUB = ROOT / 'subscription/beta.json'
BUNDLE = ROOT / 'bundles/all-beta.json'
DETAIL = ROOT / 'rss/data/details/beta/qidian-next.json'
RELEASE = ROOT / 'docs/RELEASE_LOG.md'
HANDOFF = ROOT / 'docs/sources/qidian-next/PROJECT_HANDOFF.md'
ISSUES = ROOT / 'docs/KNOWN_ISSUES.md'

VERSION = '1.1.0-beta10'
VERSION_CODE = 11010
NOW = '2026-08-26T16:37:00+08:00'
DAY = '2026-08-26'
RAW = f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VERSION_CODE}'
CDN = f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VERSION_CODE}'
IMPORT = f'legado://import/importonline?src={RAW}'
SUMMARY = '详情 beta10：Beta9 富数据真机已恢复；本版优化详情排版与冷启动请求顺序，起点图优先、APP 仅核心数据兜底，并收紧补全超时。'
CHANGELOG = [
    'Beta9 真机确认作品简介与富数据已恢复，详情数据链作为本版稳定基线',
    '详情排版收紧段间距，作品数据增加分隔线，作品标签/作者标签/作品荣誉分层展示，简介增加首行缩进',
    '冷启动先判断核心富数据是否稀疏，仅稀疏时请求起点图；起点图后仍缺核心数据才调用 APP bookDetailInfo',
    '起点图超时由 4.2 秒收紧至 3.2 秒，官方搜索由 4.2 秒收紧至 2.8 秒；缓存策略保持不变',
    '不新增接口；搜索、目录、正文 Provider、评论、角色卡、书友圈、账号与情无 VIP 链全部冻结'
]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def find_source(obj):
    if isinstance(obj, dict):
        if obj.get('bookSourceName') == '🌈 起点增强 · Beta':
            return obj
        for v in obj.values():
            r = find_source(v)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_source(v)
            if r is not None:
                return r
    return None


def replace_once(s, old, new, label):
    n = s.count(old)
    assert n == 1, f'{label}: expected 1 match, got {n}'
    return s.replace(old, new, 1)


src_doc = load(SOURCE)
src = find_source(src_doc)
assert src is not None, 'qidian-next beta source not found'
assert 'beta9' in str(src.get('bookSourceComment', '')).lower(), 'unexpected source baseline'
old_src = copy.deepcopy(src)

init = src['ruleBookInfo']['init']
intro = src['ruleBookInfo']['intro']

# --- performance: distinguish core richness from synopsis-only incompleteness ---
anchor = "function qfFillV1104(k,v){if(blank(info[k])&&!blank(v))info[k]=v;}"
helper = """function qfDetailCoreSparseV1110(){
  var ks=['recommendCount','monthTicket','readingCount','ratingScore','collectionCount','fansCount','leaderCount','investCount','firstSubscribe'],n=0;
  for(var i=0;i<ks.length;i++){var v=info[ks[i]];if(v!==undefined&&v!==null&&String(v).trim()!=='')n++;}
  return n<3||!info.tags||!info.tags.length||!String(info.status||'').trim();
}
""" + anchor
init = replace_once(init, anchor, helper, 'insert core sparse helper')

old_calls = """qfDetailAppEnrichV1109.call(this);
qfNormalizeDetailV1104();
qfDetailQidianTuV1109.call(this);
qfNormalizeDetailV1104();
qfDetailOfficialSearchV1109.call(this);
qfNormalizeDetailV1104();"""
new_calls = """if(qfDetailCoreSparseV1110())qfDetailQidianTuV1109.call(this);
qfNormalizeDetailV1104();
if(qfDetailCoreSparseV1110())qfDetailAppEnrichV1109.call(this);
qfNormalizeDetailV1104();
qfDetailOfficialSearchV1109.call(this);
qfNormalizeDetailV1104();"""
init = replace_once(init, old_calls, new_calls, 'reorder enrichment calls')

init = replace_once(
    init,
    "qfAjaxV1109.call(this,'https://www.qidiantu.com/info/'+encodeURIComponent(String(bid)),4200,'https://www.qidiantu.com/')",
    "qfAjaxV1109.call(this,'https://www.qidiantu.com/info/'+encodeURIComponent(String(bid)),3200,'https://www.qidiantu.com/')",
    'qidiantu timeout'
)
init = replace_once(
    init,
    "qfAjaxV1109.call(this,url,4200,'https://m.qidian.com/')",
    "qfAjaxV1109.call(this,url,2800,'https://m.qidian.com/')",
    'qidian search timeout'
)

# --- UI: keep compatibility-safe HTML, improve hierarchy/spacing ---
old_data_rows = "function dataRows(items){var a=[];for(var i=0;i<items.length;i++)if(items[i][2])a.push(items[i]);var h='';for(var j=0;j<a.length;j+=2){h+='<br>'+datum(a[j][0],a[j][1],a[j][2]);if(a[j+1])h+='　　'+datum(a[j+1][0],a[j+1][1],a[j+1][2]);}return h;}"
new_data_rows = "function dataRows(items){var a=[];for(var i=0;i<items.length;i++)if(items[i][2])a.push(items[i]);var h='';for(var j=0;j<a.length;j+=2){h+='<br>'+datum(a[j][0],a[j][1],a[j][2]);if(a[j+1])h+='　<font color=\"#d5d9dc\">｜</font>　'+datum(a[j+1][0],a[j+1][1],a[j+1][2]);}return h;}"
intro = replace_once(intro, old_data_rows, new_data_rows, 'data rows layout')

start = intro.index("var body='';")
end_marker = "'<usehtml>'+body+'</usehtml>';"
end = intro.index(end_marker)
new_body = r'''var body='';
function section(title,color){return '<br><br><b><font color="'+(color||'#149c95')+'">▍'+title+'</font></b>';}
var author=clean(x.author),level=clean(x.authorLevel),works=clean(x.authorWorksCount),type=clean(x.subKind)||clean(x.kind),status=clean(x.status);if(/^\d{1,2}$/.test(level))level='Lv.'+level;else if(/^Lv\d+/i.test(level))level=level.replace(/^Lv/i,'Lv.');
var rights=arr(x.rights).join(' · ');if(yes(x.isVip)&&rights.indexOf('VIP')<0)rights+=(rights?' · ':'')+'VIP';
var limitState=clean(x.serverLimitState),limitSource=clean(x.serverLimitSource);

body+='<b><font color="#149c95">▍作品资料</font></b>';
body+=row('✍️','作者',author+(level?' · '+level:'')+(works?' · '+works+'本作品':''));
body+=row('📚','分类',type+(status?' · '+status:'')+(rights?' · '+rights:''));
if(limitState&&limitState!=='未知')body+=row('🆓','限免',limitState+(limitSource?' · '+limitSource:''));
if(clean(x.updateTime))body+=row('🕒','更新',date(x.updateTime));
if(clean(x.publishDate)&&date(x.publishDate)!==date(x.updateTime))body+=row('🚀','首发',date(x.publishDate));

var sc=score(x.ratingScore),rec=num(x.recommendCount),watch=num(x.readingCount),mt=num(x.monthTicket),col=num(x.collectionCount),fans=num(x.fansCount),leader=num(x.leaderCount),invest=num(x.investCount),first=num(x.firstSubscribe);
var data=[
 ['🔥','总推荐',rec],['🎟','月票',mt],['👁',clean(x.readingMetricLabel)||'在看',watch],['💯','评分',sc?(sc+(clean(x.ratingCount)?' / '+num(x.ratingCount)+'人':'')):'' ],
 ['⭐','收藏',col],['👥','粉丝',fans],['🏅','盟主',leader],['💎','投资',invest],['📌','首订',first]
];
var dr=dataRows(data);if(dr)body+=section('作品数据','#f08a38')+dr;

body+=section('快捷入口','#149c95');
body+='<br><button>💬 书友圈@onclick:qfBookInfoOpenCircleV373.call(this)</button>　<button>🎭 角色卡@onclick:qfBookInfoOpenRoleV373.call(this)</button>　<button>⚡ 正文源@onclick:qfBookInfoOpenSmartSourceV330.call(this)</button>';

var tg=chips(x.tags||x.bookTags||'',8,'#168f89'),hon=chips(x.honors||'',6,'#b67821'),at=chips(x.authorTags||'',5,'#7162a8');
if(tg||at){body+=section('作品标签','#9a72c7');if(tg)body+='<br>'+tg;if(at)body+='<br><font color="#8a949b">✍ 作者标签</font>　'+at;}
if(hon){body+=section('作品荣誉','#c1842c')+'<br>🏆 '+hon;}
if(desc){var dh=esc(desc).replace(/\r\n|\r|\n/g,'<br>');body+=section('内容简介','#149c95')+'<br><font color="#6f767d">　　'+dh+'</font>';}
'''
intro = intro[:start] + new_body + intro[end:]

src['ruleBookInfo']['init'] = init
src['ruleBookInfo']['intro'] = intro
src['bookSourceComment'] = (
    'v1.1.0-beta10：详情排版与冷启动优化版。Beta9 真机已确认作品简介及总推荐、收藏、粉丝、盟主、首订等富数据恢复，'
    '且速度较旧版明显提升。本版不再改数据字段与解析结果，只优化详情展示和补全顺序：先判断核心富数据是否真的稀疏，稀疏时优先走已验证有效的起点图；'
    '起点图后核心数据仍不足才调用官方 APP bookDetailInfo，避免在当前真机环境中先等待一个经 Beta8 证明命中率偏低的 APP 补全。'
    '起点图超时由4.2秒收紧至3.2秒，官方移动搜索由4.2秒收紧至2.8秒，现有正/负缓存策略不变。'
    'UI 收紧段间距，作品数据加入中线分隔，作品标签/作者标签/作品荣誉拆层，简介增加首行缩进。'
    '搜索、发现、目录、正文 Provider、段评/本章说、角色卡、书友圈、账号与情无 VIP 认证链不改。'
)

# source guard: only intended fields may differ semantically
masked_old = copy.deepcopy(old_src)
masked_new = copy.deepcopy(src)
for obj in (masked_old, masked_new):
    obj['bookSourceComment'] = '<masked>'
    obj['ruleBookInfo']['init'] = '<masked>'
    obj['ruleBookInfo']['intro'] = '<masked>'
assert masked_old == masked_new, 'unexpected qidian source field changed'
assert 'qfDetailCoreSparseV1110' in init
assert '3200' in init and '2800' in init
assert '作品荣誉' in intro and '｜' in intro

dump(SOURCE, src_doc)
sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()

# manifest
manifest = load(MANIFEST)
entry = next(x for x in manifest['sources'] if x.get('id') == 'qidian-next-beta')
entry.update({
    'version': VERSION,
    'versionCode': VERSION_CODE,
    'updatedAt': NOW,
    'sourceUrl': RAW,
    'summary': SUMMARY,
    'tags': ['起点','测试版','详情页','富数据','排版优化','冷启动优化','按需补全','缓存'],
    'changelog': CHANGELOG,
    'sha256': sha,
})
manifest['updatedAt'] = NOW
dump(MANIFEST, manifest)

# beta subscription
sub = load(SUB)
item = next(x for x in sub['items'] if x.get('id') == 'qidian-next-beta')
item.update({
    'summary': SUMMARY,
    'version': VERSION,
    'updatedAt': DAY,
    'tags': ['起点','测试版','详情页','富数据','排版优化','冷启动优化','按需补全','缓存'],
    'changelog': CHANGELOG,
    'sourceUrl': RAW,
    'backupUrl': CDN,
    'importUrl': IMPORT,
})
sub['updatedAt'] = NOW
dump(SUB, sub)

# beta bundle: replace same source identity/name only
bundle = load(BUNDLE)
replaced = 0

def replace_bundle(node):
    global replaced
    if isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, dict) and v.get('bookSourceName') == '🌈 起点增强 · Beta':
                node[i] = copy.deepcopy(src)
                replaced += 1
            else:
                replace_bundle(v)
    elif isinstance(node, dict):
        for v in node.values():
            replace_bundle(v)

replace_bundle(bundle)
assert replaced == 1, f'bundle replace count={replaced}'
dump(BUNDLE, bundle)

# RSS current-state detail
rss = load(DETAIL)
rss.update({
    'summary': SUMMARY,
    'badges': ['Beta', VERSION, '排版 / 冷启动'],
    'sections': [
        {'title':'Beta9 真机结论','text':'作品简介及总推荐、收藏、粉丝、盟主、首订等富数据已经恢复；用户反馈详情速度较旧版明显提升，但首次冷启动仍有可感等待。'},
        {'title':'排版优化','text':'减少标题后的空白；作品数据两列之间增加轻量分隔；作品标签、作者标签、作品荣誉分层；内容简介增加首行缩进，整体更紧凑。'},
        {'title':'冷启动优化','text':'不再固定先请求 APP。只有核心富数据稀疏时才请求起点图；起点图后仍不足才调用 APP bookDetailInfo。这样保留兜底能力，同时跳过当前真机环境中命中率较低的无效等待。'},
        {'title':'超时控制','text':'起点图超时 4.2s→3.2s，起点官方移动搜索 4.2s→2.8s；不新增接口，现有缓存策略保持不变。'},
        {'title':'冻结范围','text':'搜索、发现、目录、正文 Provider、段评/本章说、角色卡、书友圈、账号与情无 VIP 认证链均不修改。'}
    ],
    'sourceUrl': RAW,
    'backupUrl': CDN,
    'importUrl': IMPORT,
})
dump(DETAIL, rss)

# release log / handoff / issue log
release_text = RELEASE.read_text(encoding='utf-8')
release_entry = f'''\n\n### 2026-08-26 — 🌈 起点增强 {VERSION}\n- Beta9 真机确认详情富数据和内容简介恢复，且整体速度较旧版明显提升；本版以 Beta9 为详情数据基线。\n- 详情 UI 收紧段间距，作品数据增加轻量中线分隔，标签/作者标签/荣誉分层，简介首行缩进。\n- 冷启动改为核心数据判定：核心稀疏才请求起点图；起点图后仍不足才调用 APP，避免 Beta8 已证明低命中率的 APP 请求固定占据首段等待。\n- 起点图超时收紧至 3.2 秒，官方移动搜索收紧至 2.8 秒；缓存策略不变，不新增接口。\n- Stable 1.0.0 与所有非详情业务域保持不变。\n- SHA256: `{sha}`.\n'''
if f'🌈 起点增强 {VERSION}' not in release_text:
    RELEASE.write_text(release_text.rstrip() + release_entry, encoding='utf-8')

handoff_text = HANDOFF.read_text(encoding='utf-8')
handoff_entry = f'''\n\n## Detail layout/performance {VERSION} (2026-08-26)\n\n- Beta9 real-device result is positive: synopsis and rich metrics are restored; user reports materially better speed than the older detail chain, though cold load still waits.\n- Beta10 treats Beta9 data extraction as frozen and changes only detail presentation plus enrichment ordering.\n- Core-richness check excludes synopsis-only incompleteness. QidianTu runs only when core metrics/tags/status are sparse; APP bookDetailInfo becomes a second-line fallback rather than the fixed first call.\n- QidianTu timeout: 3.2s. Official mobile search timeout: 2.8s. Existing caches remain unchanged.\n- UI: tighter section spacing, separated metric columns, separate tag/author-tag/honor blocks, indented synopsis.\n- Search/catalog/content/review/community/account/QW-VIP domains remain frozen.\n- Status: Beta pending real-device layout/performance confirmation.\n'''
if f'Detail layout/performance {VERSION}' not in handoff_text:
    HANDOFF.write_text(handoff_text.rstrip() + handoff_entry, encoding='utf-8')

issues_text = ISSUES.read_text(encoding='utf-8')
issue_entry = f'''\n\n## 28. Beta9 rich detail restored, but cold detail load still waits — optimized in {VERSION}\n\nReal-device Beta9 confirmed that synopsis and rich metrics are finally present, and the user reported a clear speed improvement over the old multi-fallback detail chain. Remaining issue: first opening a book can still pause while enrichment requests complete.\n\nBeta10 keeps the proven Beta9 data result but changes request priority: QidianTu is attempted only when core metadata is sparse; APP bookDetailInfo is no longer a mandatory first request and runs only if core data remains insufficient. QidianTu/search timeouts are reduced to 3.2s/2.8s. Detail HTML is also compacted without using the table layout that previously broke on-device.\n\nStatus: Beta published for real-device confirmation.\n'''
if f'optimized in {VERSION}' not in issues_text:
    ISSUES.write_text(issues_text.rstrip() + issue_entry, encoding='utf-8')

print('published', VERSION, 'sha256', sha, 'bundle_replace', replaced)
