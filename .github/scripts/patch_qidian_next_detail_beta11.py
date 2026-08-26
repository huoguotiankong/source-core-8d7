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

VERSION = '1.1.0-beta11'
VERSION_CODE = 11011
NOW = '2026-08-26T16:52:00+08:00'
DAY = '2026-08-26'
RAW = f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VERSION_CODE}'
CDN = f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VERSION_CODE}'
IMPORT = f'legado://import/importonline?src={RAW}'
SUMMARY = '详情 beta11：修正更新/首发时间串值；按当前 bookId 锚定时间字段并刷新旧时间缓存，同时把作品数据改成固定宽度双列对齐。'
CHANGELOG = [
    '修复详情更新时间/首发时间可能抓到同页其他对象时间、或两个字段误显示为同一时间的问题',
    '当前响应中的时间仅按当前 bookId/书名邻域提取；不再使用未锚定的全页 UpdateTime/CreateTime 扫描结果',
    '更新时间异常时复用官方移动搜索补全并按当前 bookId 锁定；起点图同时尝试提取明确标注的更新时间/首发时间',
    '旧 qf_updateTime/qf_publishDate 读取缓存升级到 v1111，避免 Beta10 已缓存的错误时间继续污染显示',
    '作品数据改为固定宽度双列 span，右列统一起点；不回退到已在真机失败过的 table 布局',
    'Beta10 富数据、简介、缓存和冷启动顺序保留；搜索、目录、正文 Provider、评论、角色卡、书友圈、账号与情无 VIP 链冻结'
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
assert 'beta10' in str(src.get('bookSourceComment', '')).lower(), 'unexpected source baseline'
old_src = copy.deepcopy(src)

init = src['ruleBookInfo']['init']
intro = src['ruleBookInfo']['intro']

# ---- time semantics: current-book anchoring, no global unscoped UpdateTime/CreateTime scan ----
old_time_scan = """if(blank(info.updateTime))info.updateTime=textScalar(html,['LastUpdateTime','lastUpdateTime','UpdateTime','updateTime'],50);
if(blank(info.publishDate))info.publishDate=textScalar(html,['PublishDate','publishDate','CreateTime','createTime'],50);
if(blank(info.listingDate))info.listingDate=textScalar(html,['ListingDate','listingDate','VipStartTime','vipStartTime'],50);"""
new_time_scan = """var qfTimesV1111=qfCurrentBookTimesV1111(html);
if(qfTimesV1111.updateTime)info.updateTime=qfTimesV1111.updateTime;
if(qfTimesV1111.publishDate)info.publishDate=qfTimesV1111.publishDate;
if(blank(info.listingDate))info.listingDate=textScalar(html,['ListingDate','listingDate','VipStartTime','vipStartTime'],50);
if(!qfTimesV1111.updateTime&&qfTimeSuspiciousV1111())info.updateTime='';
if(!qfTimesV1111.publishDate&&qfPublishSuspiciousV1111())info.publishDate='';"""
init = replace_once(init, old_time_scan, new_time_scan, 'replace unscoped time scan')

anchor = "function qfFillV1104(k,v){if(blank(info[k])&&!blank(v))info[k]=v;}"
helpers = r'''function qfDateCandidateV1111(v){
  var s=unesc(String(v||'')).trim();if(!s)return '';
  if(/^\d{10,13}$/.test(s))return s;
  s=s.replace(/\//g,'-');
  var m=s.match(/(20\d{2}-\d{1,2}-\d{1,2}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?)/);
  if(!m||!m[1])return '';
  var y=Number(m[1].slice(0,4));return y>=2000&&y<=2100?m[1]:'';
}
function qfTimeMsV1111(v){
  var s=qfDateCandidateV1111(v);if(!s)return 0;
  if(/^\d{10,13}$/.test(s)){var n=Number(s);if(s.length===10)n*=1000;return isFinite(n)?n:0;}
  try{var n2=Date.parse(s.replace(' ','T'));return isFinite(n2)?n2:0;}catch(_e){return 0;}
}
function qfTimeSuspiciousV1111(){
  var u=qfTimeMsV1111(info.updateTime),p=qfTimeMsV1111(info.publishDate),l=qfTimeMsV1111(info.listingDate),now=Date.now();
  if(!u)return true;if(u>now+2*86400000)return true;if(l&&u+60000<l)return true;if(p&&Math.abs(u-p)<60000)return true;return false;
}
function qfPublishSuspiciousV1111(){
  var p=qfTimeMsV1111(info.publishDate),u=qfTimeMsV1111(info.updateTime),l=qfTimeMsV1111(info.listingDate),now=Date.now();
  if(!p)return true;if(p>now+2*86400000)return true;if(u&&p>u+86400000)return true;if(l&&p>l+86400000)return true;return false;
}
function qfPickTimeKeyV1111(seg,keys){
  var s=String(seg||'').replace(/\\\"/g,'\"');
  for(var i=0;i<keys.length;i++){
    var k=String(keys[i]).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    var m=s.match(new RegExp('\"'+k+'\"\\s*:\\s*(?:\"([^\"]{4,64})\"|([0-9]{10,13}))','i'));
    var v=qfDateCandidateV1111(m?(m[1]||m[2]||''):'');if(v)return v;
  }
  return '';
}
function qfCurrentBookTimesV1111(h){
  h=String(h||'');var out={updateTime:'',publishDate:''};if(!h||!bid)return out;
  var marks=['\"bookId\":\"'+String(bid)+'\"','\"bookId\":'+String(bid),'\"BookId\":\"'+String(bid)+'\"','\"bid\":\"'+String(bid)+'\"','\"bid\":'+String(bid),'/book/'+String(bid)+'/'];
  var name=String(info&&info.name||searchName||'').trim(),author=String(info&&info.author||searchAuthor||'').trim(),best=-1;
  for(var mi=0;mi<marks.length;mi++){
    var from=0,loops=0,ix=-1;while(loops<12&&(ix=h.indexOf(marks[mi],from))>=0){loops++;from=ix+marks[mi].length;
      var seg=h.slice(Math.max(0,ix-1800),Math.min(h.length,ix+5200)),score=1;if(name&&seg.indexOf(name)>=0)score+=3;if(author&&seg.indexOf(author)>=0)score+=1;
      var u=qfPickTimeKeyV1111(seg,['lastUpdateTime','LastUpdateTime','newChapterTime','NewChapterTime','lastChapterTime','LastChapterTime','updateTime','UpdateTime']);
      var p=qfPickTimeKeyV1111(seg,['publishDate','PublishDate','publishTime','PublishTime','firstPublishTime','FirstPublishTime','bookCreateTime','BookCreateTime','createTime','CreateTime']);
      if((u||p)&&score>=best){if(u)out.updateTime=u;if(p)out.publishDate=p;best=score;if(score>=5&&u&&p)return out;}
    }
  }
  return out;
}
''' + anchor
init = replace_once(init, anchor, helpers, 'insert time helpers')

# Fresh time-cache namespace; Beta10 bad values must not win on import/update.
old_cached = "cached('status','qf_status',false);cached('updateTime','qf_updateTime',false);cached('publishDate','qf_publishDate',false);cached('listingDate','qf_listingDate',false);"
new_cached = "cached('status','qf_status',false);cached('updateTime','qf_updateTime_v1111',false);cached('publishDate','qf_publishDate_v1111',false);cached('listingDate','qf_listingDate',false);"
init = replace_once(init, old_cached, new_cached, 'version time cache reads')

old_put = "put.call(this,'qf_status',info.status);put.call(this,'qf_updateTime',info.updateTime);put.call(this,'qf_publishDate',info.publishDate);put.call(this,'qf_listingDate',info.listingDate);"
new_put = "put.call(this,'qf_status',info.status);put.call(this,'qf_updateTime_v1111',info.updateTime);put.call(this,'qf_publishDate_v1111',info.publishDate);put.call(this,'qf_updateTime',info.updateTime);put.call(this,'qf_publishDate',info.publishDate);put.call(this,'qf_listingDate',info.listingDate);"
init = replace_once(init, old_put, new_put, 'version time cache writes')

# QidianTu refresh cache once so newly-added time parsing is not hidden by beta9/10 payload.
init = init.replace("qf_qidiantu_stat_v1109_", "qf_qidiantu_stat_v1111_")
assert "qf_qidiantu_stat_v1111_" in init

old_apply_q = """if(!info.status&&q.status)info.status=q.status;
  if(!info.listingDate&&q.listingDate)info.listingDate=q.listingDate;
  if(q.isVip)info.isVip=true;"""
new_apply_q = """if(!info.status&&q.status)info.status=q.status;
  if(!info.listingDate&&q.listingDate)info.listingDate=q.listingDate;
  if(q.updateTime&&(blank(info.updateTime)||qfTimeSuspiciousV1111()))info.updateTime=q.updateTime;
  if(q.publishDate&&(blank(info.publishDate)||qfPublishSuspiciousV1111()))info.publishDate=q.publishDate;
  if(q.isVip)info.isVip=true;"""
init = replace_once(init, old_apply_q, new_apply_q, 'apply qidiantu times')

old_q_dates = r"""m=t.match(/首订\s*[:：]?\s*[0-9]+[\s\S]{0,45}?[（(](\d{4}-\d{1,2}-\d{1,2})上架[）)]/);if(m&&m[1])q.listingDate=m[1];"""
new_q_dates = old_q_dates + r"""
    m=t.match(/(?:更新时间|最近更新|最后更新)\s*[:：]?\s*(20\d{2}[-\/]\d{1,2}[-\/]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)/);if(m&&m[1])q.updateTime=qfDateCandidateV1111(m[1]);
    m=t.match(/(?:首发时间|首发日期|发布时间|发布于|创建时间|开书时间)\s*[:：]?\s*(20\d{2}[-\/]\d{1,2}[-\/]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)/);if(m&&m[1])q.publishDate=qfDateCandidateV1111(m[1]);"""
init = replace_once(init, old_q_dates, new_q_dates, 'parse qidiantu dates')

old_q_ok = "q.ok=!!(q.collection||q.fans||q.recommend||q.reading||q.monthTicket||q.leader||q.score||q.firstSubscribe||q.authorLevel||q.tags||q.status||q.honors.length);"
new_q_ok = "q.ok=!!(q.collection||q.fans||q.recommend||q.reading||q.monthTicket||q.leader||q.score||q.firstSubscribe||q.authorLevel||q.tags||q.status||q.updateTime||q.publishDate||q.honors.length);"
init = replace_once(init, old_q_ok, new_q_ok, 'qidiantu ok includes dates')

# If APP is reached for sparse core data, let its explicit time fields replace a suspect current value.
old_app_dates = "ap('publishDate',false);ap('listingDate',false);ap('honors',false);ap('isVip',false);ap('kind',false);ap('subKind',false);ap('status',false);ap('updateTime',false);"
new_app_dates = "ap('publishDate',qfPublishSuspiciousV1111());ap('listingDate',false);ap('honors',false);ap('isVip',false);ap('kind',false);ap('subKind',false);ap('status',false);ap('updateTime',qfTimeSuspiciousV1111());"
init = replace_once(init, old_app_dates, new_app_dates, 'prefer APP explicit times when suspect')

# Official mobile-search cache upgraded; use exact-book row to repair suspicious updateTime without adding a new endpoint.
init = init.replace("qf_qidian_search_detail_v1109_", "qf_qidian_search_detail_v1111_")
assert "qf_qidian_search_detail_v1111_" in init

old_apply_search = """if(blank(info.recommendCount)&&o.recommend)info.recommendCount=o.recommend;
  info.detailSource=(info.detailSource?info.detailSource+'+':'')+'qidian-search-v1109';"""
new_apply_search = """if(blank(info.recommendCount)&&o.recommend)info.recommendCount=o.recommend;
  if(o.updateTime&&(blank(info.updateTime)||qfTimeSuspiciousV1111()))info.updateTime=o.updateTime;
  info.detailSource=(info.detailSource?info.detailSource+'+':'')+'qidian-search-v1111';"""
init = replace_once(init, old_apply_search, new_apply_search, 'apply official search time')

old_search_need = "var needIntro=blank(info.intro),needRead=blank(info.readingCount),needRec=blank(info.recommendCount);if(!needIntro&&!needRead&&!needRec)return;"
new_search_need = "var needIntro=blank(info.intro),needRead=blank(info.readingCount),needRec=blank(info.recommendCount),needUpdate=qfTimeSuspiciousV1111();if(!needIntro&&!needRead&&!needRec&&!needUpdate)return;"
init = replace_once(init, old_search_need, new_search_need, 'official search time need')

old_search_block = """if(block){
      o.recommend=qfPickMetricV1109(block,'总推荐');
      var labs=['人在追','人在看','在追','在看'];for(var li=0;li<labs.length&&!o.reading;li++){var rv=qfPickMetricV1109(block,labs[li]);if(rv){o.reading=rv;o.readingLabel=labs[li];}}
    }
    o.ok=!!(o.intro||o.recommend||o.reading);"""
new_search_block = """if(block){
      o.recommend=qfPickMetricV1109(block,'总推荐');
      var labs=['人在追','人在看','在追','在看'];for(var li=0;li<labs.length&&!o.reading;li++){var rv=qfPickMetricV1109(block,labs[li]);if(rv){o.reading=rv;o.readingLabel=labs[li];}}
      var um=block.match(/(?:更新时间|更新)\\s*[:：]?\\s*(20\\d{2}[-\\/]\\d{1,2}[-\\/]\\d{1,2}(?:\\s+\\d{1,2}:\\d{2}(?::\\d{2})?)?)/);if(um&&um[1])o.updateTime=qfDateCandidateV1111(um[1]);
    }
    o.ok=!!(o.intro||o.recommend||o.reading||o.updateTime);"""
init = replace_once(init, old_search_block, new_search_block, 'official search parse update time')

# ---- UI: fixed-width two-column metrics, no table ----
old_data_rows = "function dataRows(items){var a=[];for(var i=0;i<items.length;i++)if(items[i][2])a.push(items[i]);var h='';for(var j=0;j<a.length;j+=2){h+='<br>'+datum(a[j][0],a[j][1],a[j][2]);if(a[j+1])h+='　<font color=\"#d5d9dc\">｜</font>　'+datum(a[j+1][0],a[j+1][1],a[j+1][2]);}return h;}"
new_data_rows = "function dataCell(v,w){return '<span style=\"display:inline-block;width:'+(w||'49%')+';vertical-align:top;white-space:nowrap\">'+v+'</span>';}function dataRows(items){var a=[];for(var i=0;i<items.length;i++)if(items[i][2])a.push(items[i]);var h='';for(var j=0;j<a.length;j+=2){h+='<br>'+dataCell(datum(a[j][0],a[j][1],a[j][2]),'49%');h+=a[j+1]?dataCell(datum(a[j+1][0],a[j+1][1],a[j+1][2]),'49%'):dataCell('','49%');}return h;}"
intro = replace_once(intro, old_data_rows, new_data_rows, 'fixed two-column metric cells')

src['ruleBookInfo']['init'] = init
src['ruleBookInfo']['intro'] = intro
src['bookSourceComment'] = (
    'v1.1.0-beta11：详情时间与数据对齐修复版。Beta10 真机确认富数据/简介保持正常，但更新与首发时间出现串值：'
    '未锚定的全页 UpdateTime/CreateTime 扫描可能抓到同页其他对象，旧时间缓存又会延续错误。本版废弃这类全页时间扫描，'
    '改为按当前 bookId/书名邻域提取 lastUpdateTime/newChapterTime/publishTime/createTime；异常更新时间复用现有官方移动搜索按 bookId 精确修复，'
    '起点图也只接受明确标注的更新时间/首发时间。时间缓存升级到 v1111，避免 Beta10 错误缓存继续生效。作品数据不使用 table，'
    '改为两个 49% 固定宽度 inline-block 单元格，使月票/粉丝/首订等右列统一起点。Beta10 富数据、简介、缓存及冷启动顺序保留，'
    '搜索、目录、正文 Provider、评论、角色卡、书友圈、账号与情无 VIP 链不改。'
)

# source guard
masked_old = copy.deepcopy(old_src)
masked_new = copy.deepcopy(src)
for obj in (masked_old, masked_new):
    obj['bookSourceComment'] = '<masked>'
    obj['ruleBookInfo']['init'] = '<masked>'
    obj['ruleBookInfo']['intro'] = '<masked>'
assert masked_old == masked_new, 'unexpected qidian source field changed'
assert 'qfCurrentBookTimesV1111' in init
assert 'qf_updateTime_v1111' in init and 'qf_publishDate_v1111' in init
assert 'qf_qidiantu_stat_v1111_' in init and 'qf_qidian_search_detail_v1111_' in init
assert 'display:inline-block;width:' in intro
assert old_time_scan not in init

dump(SOURCE, src_doc)
sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()

manifest = load(MANIFEST)
entry = next(x for x in manifest['sources'] if x.get('id') == 'qidian-next-beta')
entry.update({
    'version': VERSION, 'versionCode': VERSION_CODE, 'updatedAt': NOW, 'sourceUrl': RAW,
    'summary': SUMMARY,
    'tags': ['起点','测试版','详情页','时间修复','富数据','双列对齐','缓存','按需补全'],
    'changelog': CHANGELOG, 'sha256': sha,
})
manifest['updatedAt'] = NOW
dump(MANIFEST, manifest)

sub = load(SUB)
item = next(x for x in sub['items'] if x.get('id') == 'qidian-next-beta')
item.update({
    'summary': SUMMARY, 'version': VERSION, 'updatedAt': DAY,
    'tags': ['起点','测试版','详情页','时间修复','富数据','双列对齐','缓存','按需补全'],
    'changelog': CHANGELOG, 'sourceUrl': RAW, 'backupUrl': CDN, 'importUrl': IMPORT,
})
sub['updatedAt'] = NOW
dump(SUB, sub)

bundle = load(BUNDLE)
replaced = 0

def replace_bundle(node):
    global replaced
    if isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, dict) and v.get('bookSourceName') == '🌈 起点增强 · Beta':
                node[i] = copy.deepcopy(src); replaced += 1
            else:
                replace_bundle(v)
    elif isinstance(node, dict):
        for v in node.values(): replace_bundle(v)

replace_bundle(bundle)
assert replaced == 1, f'bundle replace count={replaced}'
dump(BUNDLE, bundle)

rss = load(DETAIL)
rss.update({
    'summary': SUMMARY,
    'badges': ['Beta', VERSION, '时间 / 对齐'],
    'sections': [
        {'title':'真机结论','text':'Beta10 富数据与简介正常，但更新/首发时间串值，作品数据右列仍因左列文本宽度不同而轻微漂移。'},
        {'title':'时间修复','text':'详情时间只从当前 bookId/书名邻域读取，不再全页扫 UpdateTime/CreateTime；异常更新时间复用现有官方移动搜索按 bookId 精确修复。'},
        {'title':'缓存修复','text':'更新时间和首发时间切换到 v1111 缓存键，Beta10 已缓存的错误值不会继续被优先复用。'},
        {'title':'双列对齐','text':'作品数据使用两个固定 49% inline-block 单元格，右列每行从同一横向位置开始；不使用真机已证明不兼容的 HTML table。'},
        {'title':'冻结范围','text':'Beta10 富数据、简介和冷启动顺序保留；搜索、目录、正文 Provider、评论、角色卡、书友圈、账号与情无 VIP 链不改。'},
    ],
    'sourceUrl': RAW, 'backupUrl': CDN, 'importUrl': IMPORT,
})
dump(DETAIL, rss)

release_text = RELEASE.read_text(encoding='utf-8')
release_text += f'''\n\n### {DAY} — 🌈 起点增强 {VERSION}\n- Beta10 真机确认富数据/简介正常，但更新时间与首发时间出现串值；同页未锚定时间字段不可继续作为可靠来源。\n- 时间改为按当前 bookId/书名邻域提取，并将异常更新时间纳入现有官方移动搜索补全。\n- 时间缓存升级到 v1111，避免旧错误值继续污染。\n- 作品数据由空格推进改为固定宽度双列 inline-block，右列统一对齐。\n- 非详情域保持冻结。\n- SHA256: `{sha}`.\n'''
RELEASE.write_text(release_text, encoding='utf-8')

handoff_text = HANDOFF.read_text(encoding='utf-8')
handoff_text += f'''\n\n## Detail time/alignment {VERSION} ({DAY})\n\n- Beta10 real-device result: rich metrics and synopsis remained correct, but update/publish dates could resolve to the same wrong timestamp.\n- Unscoped full-page `UpdateTime/CreateTime` extraction is removed. Current-book time parsing is anchored to current bookId/title vicinity.\n- Suspect update time may reuse the already-existing exact-book official mobile-search fallback; no new endpoint is introduced.\n- Time book-variable cache keys are versioned to v1111 so old wrong values do not mask the fix.\n- Works-data renderer uses two fixed-width inline-block cells instead of spacing or `<table>`, aligning the right column while preserving the compatibility baseline.\n- Status: Beta, pending real-device confirmation.\n'''
HANDOFF.write_text(handoff_text, encoding='utf-8')

issues_text = ISSUES.read_text(encoding='utf-8')
issues_text += f'''\n\n## Qidian detail time fields could bind to unrelated page objects — addressed in {VERSION}\n\nReal-device Beta10 showed `更新` and `首发` as the same stale timestamp on a currently updating book. The detail fast parser had fallback scans for generic `UpdateTime/CreateTime` across the whole page, which could bind to unrelated nested/recommended objects; old book-variable caches could then preserve the bad values. Beta11 anchors time extraction to the current bookId/title vicinity, versions time cache keys, and lets the existing exact-book official search repair a suspicious update timestamp. Works-data right column also moved from variable spacing to fixed-width inline-block cells.\n'''
ISSUES.write_text(issues_text, encoding='utf-8')

print('published', VERSION, 'sha256', sha, 'bundle_replace', replaced)
