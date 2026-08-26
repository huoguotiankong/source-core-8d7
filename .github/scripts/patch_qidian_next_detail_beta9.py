import copy
import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
SRC_PATH = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
TRIGGER = ROOT / '.staging/qidian-next-detail-beta9.trigger'


def dump_json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + '\n'


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


data = json.loads(SRC_PATH.read_text(encoding='utf-8'))
assert isinstance(data, list) and len(data) == 1
src = data[0]
assert src.get('bookSourceName') == '🌈 起点增强 · Beta'
old_comment = str(src.get('bookSourceComment') or '')
assert ('v1.1.0-beta8' in old_comment) or ('v1.1.0-beta9' in old_comment), old_comment[:100]

frozen_keys = [
    'jsLib', 'ruleSearch', 'ruleExplore', 'ruleToc', 'ruleContent',
    'searchUrl', 'exploreUrl', 'loginUrl', 'shouldOverrideUrlLoading'
]
frozen = {k: copy.deepcopy(src.get(k)) for k in frozen_keys}

if 'v1.1.0-beta9' not in old_comment:
    src['bookSourceComment'] = (
        'v1.1.0-beta9：详情富数据多层回归版。Beta8 真机仍只有月票/作者等级等少数字段，证明单独依赖官方 APP bookDetailInfo 在部分阅读环境并不可靠。'
        '本版保留当前响应/搜索参数/书籍缓存快速路径，先尝试官方 APP；仍稀疏时按需恢复旧版已使用的起点图富数据链，补收藏、真实粉丝、总推荐、盟主、评分、首订、上架、作者等级、标签、状态、荣誉等；'
        '作品简介/在看/总推荐仍缺时，再用起点官方移动搜索页按 bookId 精确锚定补全。起点图正缓存12小时、官方搜索正缓存6小时，失败仅短缓存10分钟；不再出现“请求失败也锁30分钟”的情况。'
        '不引入推书君第三请求，优先控制冷启动开销。搜索、目录、正文 Provider、段评/本章说、角色卡、书友圈及情无 VIP 认证链不改。'
    )

    bi = src.setdefault('ruleBookInfo', {})
    init = str(bi.get('init') or '')

    pattern = re.compile(
        r"function qfDetailOfficialEnrichV1108\(\)\{[\s\S]*?"
        r"qfNormalizeDetailV1104\(\);\s*"
        r"qfDetailOfficialEnrichV1108\.call\(this\);\s*"
        r"qfNormalizeDetailV1104\(\);"
    )

    replacement = r'''function qfCacheGetV1109(k){try{return (typeof cache!=='undefined'&&cache.get)?String(cache.get(k)||''):'';}catch(_e){return '';}}
function qfCachePutV1109(k,v,sec){try{if(typeof cache!=='undefined'&&cache.put)cache.put(k,String(v||''),sec);}catch(_e){}}
function qfAjaxV1109(url,timeout,referer){
  try{
    var j=qfJava(this);if(!j||typeof j.ajax!=='function')return '';
    var op={method:'GET',timeout:timeout||3800,headers:{
      'User-Agent':'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36',
      'Referer':referer||'https://www.qidian.com/','Accept':'text/html,application/json,text/plain,*/*','Accept-Language':'zh-CN,zh;q=0.9'
    }};
    return String(j.ajax(String(url)+','+JSON.stringify(op))||'');
  }catch(_e){return '';}
}
function qfAbsNumV1109(v){
  var s=String(v==null?'':v).replace(/,/g,'').trim();if(!s)return '';
  var m=s.match(/^([0-9]+(?:\.[0-9]+)?)\s*(亿|百万|万|千|w|W|k|K)?$/);if(!m)return '';
  var n=Number(m[1]);if(!isFinite(n)||n<=0)return '';
  var u=m[2]||'';if(u==='亿')n*=1e8;else if(u==='百万')n*=1e6;else if(u==='万'||u==='w'||u==='W')n*=1e4;else if(u==='千'||u==='k'||u==='K')n*=1e3;
  return String(Math.round(n));
}
function qfPlainV1109(html){
  return String(html||'').replace(/<script[\s\S]*?<\/script>/gi,' ').replace(/<style[\s\S]*?<\/style>/gi,' ').replace(/<br\s*\/?>/gi,'\n').replace(/<\/p>/gi,'\n').replace(/<[^>]+>/g,' ').replace(/&nbsp;/gi,' ').replace(/&amp;/gi,'&').replace(/&#39;/gi,"'").replace(/&quot;/gi,'"').replace(/[ \t]+/g,' ').replace(/\n\s+/g,'\n');
}
function qfPickMetricV1109(text,label){
  text=String(text||'');var e=String(label).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  var m=text.match(new RegExp(e+'\\s*[:：]?\\s*([0-9]+(?:\\.[0-9]+)?\\s*(?:亿|百万|万|千|[wWkK])?)','i'));
  if(!m)m=text.match(new RegExp('([0-9]+(?:\\.[0-9]+)?\\s*(?:亿|百万|万|千|[wWkK])?)\\s*'+e,'i'));
  return m&&m[1]?qfAbsNumV1109(m[1]):'';
}
function qfMergeListV1109(a,b){
  var out=[],seen={};function add(v){String(v||'').split(/[·,，|\/]/).forEach(function(x){x=String(x||'').trim();if(x&&x.length<=30&&!seen[x]){seen[x]=1;out.push(x);}});}
  if(Array.isArray(a))for(var i=0;i<a.length;i++)add(a[i]);else add(a);
  if(Array.isArray(b))for(var j=0;j<b.length;j++)add(b[j]);else add(b);
  return out;
}
function qfDetailAppEnrichV1109(){
  if(!bid||!qfDetailSparseV1104())return false;
  var now=Date.now(),neg=Number(bv('qf_appDetailNegAtV1109')||0);if(neg>0&&now-neg<5*60*1000)return false;
  var appInfo=null;try{appInfo=qfOfficialCallV400.call(this,'bookDetailInfo',[String(bid)]);}catch(_app){appInfo=null;}
  if(!appInfo||!appInfo.ok){try{qfPutBookVarV09.call(this,'qf_appDetailNegAtV1109',String(now));}catch(_n){}return false;}
  function ap(k,prefer){var v=appInfo[k];if(v===undefined||v===null||String(v).trim()==='')return;if(prefer||blank(info[k]))info[k]=v;}
  ap('intro',true);ap('recommendCount',true);ap('readingCount',true);ap('collectionCount',true);ap('fansCount',true);ap('monthTicket',true);
  ap('ratingScore',false);ap('ratingCount',false);ap('leaderCount',false);ap('investCount',false);ap('firstSubscribe',false);
  ap('authorLevel',false);ap('authorDesc',false);ap('authorWorksCount',false);ap('authorTags',false);ap('wordCount',false);
  ap('publishDate',false);ap('listingDate',false);ap('honors',false);ap('isVip',false);ap('kind',false);ap('subKind',false);ap('status',false);ap('updateTime',false);
  if((!info.tags||!info.tags.length)&&appInfo.bookTags)info.tags=appInfo.bookTags;
  if(!blank(info.readingCount))info.readingMetricLabel='在看';
  info.detailSource=(info.detailSource?info.detailSource+'+':'')+'app-bookdetail-v1109';
  return true;
}
function qfApplyQidianTuV1109(q){
  if(!q||!q.ok)return;
  if(q.collection)info.collectionCount=q.collection;
  if(q.fans)info.fansCount=q.fans;
  if(!info.recommendCount&&q.recommend)info.recommendCount=q.recommend;
  if(!info.readingCount&&q.reading){info.readingCount=q.reading;info.readingMetricLabel='在看';}
  if(!info.monthTicket&&q.monthTicket)info.monthTicket=q.monthTicket;
  if(!info.leaderCount&&q.leader)info.leaderCount=q.leader;
  if((!info.ratingScore||Number(info.ratingScore)<=0)&&q.score)info.ratingScore=q.score;
  if(!info.firstSubscribe&&q.firstSubscribe)info.firstSubscribe=q.firstSubscribe;
  if(!info.authorLevel&&q.authorLevel)info.authorLevel=q.authorLevel;
  if(!info.status&&q.status)info.status=q.status;
  if(!info.listingDate&&q.listingDate)info.listingDate=q.listingDate;
  if(q.isVip)info.isVip=true;
  info.tags=qfMergeListV1109(info.tags,q.tags||'');
  info.honors=qfMergeListV1109(info.honors,q.honors||[]);
  info.detailSource=(info.detailSource?info.detailSource+'+':'')+'qidiantu-v1109';
}
function qfDetailQidianTuV1109(){
  if(!bid||!qfDetailSparseV1104())return;
  var ck='qf_qidiantu_stat_v1109_'+String(bid),cv=qfCacheGetV1109(ck),q={};
  if(cv&&cv.charAt(0)==='{'){try{q=JSON.parse(cv)||{};}catch(_c){q={};}}
  if(q.ok){qfApplyQidianTuV1109(q);return;}
  if(q.checked&&!q.ok)return;
  var h=qfAjaxV1109.call(this,'https://www.qidiantu.com/info/'+encodeURIComponent(String(bid)),4200,'https://www.qidiantu.com/');
  q={checked:1,ok:false};
  if(h&&h.length>300){
    var t=qfPlainV1109(h),m='';
    q.collection=qfPickMetricV1109(t,'总收藏')||qfPickMetricV1109(t,'收藏');
    q.fans=qfPickMetricV1109(t,'真实粉丝数')||qfPickMetricV1109(t,'真实粉丝')||qfPickMetricV1109(t,'粉丝');
    q.recommend=qfPickMetricV1109(t,'总推荐');
    q.reading=qfPickMetricV1109(t,'在看')||qfPickMetricV1109(t,'人在看')||qfPickMetricV1109(t,'阅读人数');
    q.monthTicket=qfPickMetricV1109(t,'月票');
    q.leader=qfPickMetricV1109(t,'盟主数')||qfPickMetricV1109(t,'盟主');
    m=t.match(/评分\s*[:：]?\s*([0-9]+(?:\.[0-9]+)?)/);if(m&&m[1]&&Number(m[1])>0&&Number(m[1])<=10)q.score=m[1];
    m=t.match(/首订\s*[:：]?\s*([0-9]+)/);if(m&&m[1]&&Number(m[1])>0)q.firstSubscribe=m[1];
    m=t.match(/首订\s*[:：]?\s*[0-9]+[\s\S]{0,45}?[（(](\d{4}-\d{1,2}-\d{1,2})上架[）)]/);if(m&&m[1])q.listingDate=m[1];
    m=t.match(/作者\s*[:：]\s*[^\n（(]{1,50}[（(]([^）)]{1,24})[）)]/);if(m&&m[1])q.authorLevel=String(m[1]).trim();
    m=t.match(/标签\s*[:：]?\s*([^\n]{2,140}?)\s*状态\s*[:：]?/);if(m&&m[1])q.tags=String(m[1]).trim().replace(/\s+/g,' · ');
    m=t.match(/状态\s*[:：]?\s*([^\s\n]{1,12})/);if(m&&m[1])q.status=String(m[1]).trim();
    q.isVip=/\(VIP\)|（VIP）|\bVIP\b/i.test(t.slice(0,1200));
    q.honors=[];
    try{
      var d=org.jsoup.Jsoup.parse(h),tabs=d.select('table');
      for(var ti=0;ti<tabs.size()&&q.honors.length<10;ti++){
        var tb=tabs.get(ti),tt=String(tb.text()||'');if(tt.indexOf('徽章名称')<0||tt.indexOf('获得时间')<0)continue;
        var rows=tb.select('tr');for(var ri=0;ri<rows.size()&&q.honors.length<10;ri++){
          var cs=rows.get(ri).select('th,td');if(cs.size()<1)continue;var hn=String(cs.get(0).text()||'').trim();if(!hn||/徽章名称/.test(hn))continue;if(q.honors.indexOf(hn)<0)q.honors.push(hn);
        }
      }
    }catch(_hon){}
    q.ok=!!(q.collection||q.fans||q.recommend||q.reading||q.monthTicket||q.leader||q.score||q.firstSubscribe||q.authorLevel||q.tags||q.status||q.honors.length);
  }
  qfCachePutV1109(ck,JSON.stringify(q),q.ok?12*60*60:10*60);
  if(q.ok)qfApplyQidianTuV1109(q);
}
function qfApplySearchV1109(o){
  if(!o||!o.ok)return;
  if(blank(info.intro)&&o.intro)info.intro=o.intro;
  if(blank(info.readingCount)&&o.reading){info.readingCount=o.reading;info.readingMetricLabel=o.readingLabel||'在看';}
  if(blank(info.recommendCount)&&o.recommend)info.recommendCount=o.recommend;
  info.detailSource=(info.detailSource?info.detailSource+'+':'')+'qidian-search-v1109';
}
function qfDetailOfficialSearchV1109(){
  if(!bid)return;
  var needIntro=blank(info.intro),needRead=blank(info.readingCount),needRec=blank(info.recommendCount);if(!needIntro&&!needRead&&!needRec)return;
  var ck='qf_qidian_search_detail_v1109_'+String(bid),cv=qfCacheGetV1109(ck),o={};
  if(cv&&cv.charAt(0)==='{'){try{o=JSON.parse(cv)||{};}catch(_c){o={};}}
  if(o.ok){qfApplySearchV1109(o);return;}if(o.checked&&!o.ok)return;
  var name=String(info.name||searchName||'').trim();if(!name)return;
  var url='https://m.qidian.com/search?kw='+encodeURIComponent(name),h=qfAjaxV1109.call(this,url,4200,'https://m.qidian.com/');
  o={checked:1,ok:false};
  if(h&&h.length>300){
    var block='',row=null;
    try{
      var d=org.jsoup.Jsoup.parse(h);row=d.select('[data-bid="'+String(bid)+'"]').first();
      if(row){
        block=String(row.text()||'');var de=row.select('[class*=searchBookDesc]').first();if(de){var it=String(de.text()||'').trim();if(it.length>=10) o.intro=it;}
      }
    }catch(_d){}
    if(!block){
      var marks=['data-bid="'+String(bid)+'"',"data-bid='"+String(bid)+"'",'/book/'+String(bid)+'/'];var ix=-1;
      for(var mi=0;mi<marks.length;mi++){ix=h.indexOf(marks[mi]);if(ix>=0)break;}
      if(ix>=0){var sl=h.slice(Math.max(0,ix-1200),Math.min(h.length,ix+9000));block=qfPlainV1109(sl);if(!o.intro){var mm=sl.match(/class=["'][^"']*searchBookDesc[^"']*["'][^>]*>([\s\S]*?)<\//i);if(mm&&mm[1]){var it2=qfPlainV1109(mm[1]).trim();if(it2.length>=10)o.intro=it2;}}}
    }
    if(block){
      o.recommend=qfPickMetricV1109(block,'总推荐');
      var labs=['人在追','人在看','在追','在看'];for(var li=0;li<labs.length&&!o.reading;li++){var rv=qfPickMetricV1109(block,labs[li]);if(rv){o.reading=rv;o.readingLabel=labs[li];}}
    }
    o.ok=!!(o.intro||o.recommend||o.reading);
  }
  qfCachePutV1109(ck,JSON.stringify(o),o.ok?6*60*60:10*60);if(o.ok)qfApplySearchV1109(o);
}
qfNormalizeDetailV1104();
qfDetailAppEnrichV1109.call(this);
qfNormalizeDetailV1104();
qfDetailQidianTuV1109.call(this);
qfNormalizeDetailV1104();
qfDetailOfficialSearchV1109.call(this);
qfNormalizeDetailV1104();'''

    init2, n = pattern.subn(replacement, init, count=1)
    assert n == 1, f'Beta8 enrichment block match count={n}'
    assert 'qfDetailOfficialEnrichV1108' not in init2
    assert 'qfDetailAppEnrichV1109' in init2
    assert 'qfDetailQidianTuV1109' in init2
    assert 'qfDetailOfficialSearchV1109' in init2
    assert '/ttsbook/' not in init2
    bi['init'] = init2

for k, v in frozen.items():
    assert src.get(k) == v, f'frozen field changed: {k}'

raw = dump_json(data).encode('utf-8')
SRC_PATH.write_bytes(raw)
source_sha = sha256_bytes(raw)

now_dt = datetime.now(timezone(timedelta(hours=8)))
now = now_dt.isoformat(timespec='seconds')
day = now_dt.date().isoformat()
version = '1.1.0-beta9'
version_code = 11009
source_url = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v=11009'
backup_url = 'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v=11009'
summary = '详情 beta9：APP 后仍稀疏则按需恢复起点图富数据，并以起点官方搜索页按 bookId 补简介/在看/总推荐。'
tags = ['起点','测试版','详情页','完整数据','起点图','官方搜索','按需补全','缓存']
changes = [
    'APP bookDetailInfo 仍保留为第一层快速补全，但失败不再阻断后续富数据链',
    '稀疏详情按需恢复起点图：收藏、真实粉丝、总推荐、盟主、评分、首订、上架、作者等级、标签、状态、荣誉等',
    '简介/在看/总推荐仍为空时，用起点官方移动搜索页按 bookId 精确锚定补全',
    '起点图正缓存12小时、官方搜索正缓存6小时，失败只短缓存10分钟',
    '不增加推书君第三请求；搜索、目录、正文、评论及账号链保持不变'
]

manifest_path = ROOT / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['updatedAt'] = now
found = False
for ent in manifest.get('sources', []):
    if ent.get('id') == 'qidian-next-beta':
        ent.update({
            'version': version, 'versionCode': version_code, 'updatedAt': now,
            'sourceUrl': source_url, 'summary': summary, 'tags': tags,
            'changelog': changes, 'sha256': source_sha
        })
        found = True
assert found
manifest_path.write_text(dump_json(manifest), encoding='utf-8')

sub_path = ROOT / 'subscription/beta.json'
sub = json.loads(sub_path.read_text(encoding='utf-8'))
sub['updatedAt'] = now
found = False
for ent in sub.get('items', []):
    if ent.get('id') == 'qidian-next-beta':
        ent.update({
            'summary': summary, 'version': version, 'updatedAt': day,
            'tags': tags, 'changelog': changes,
            'sourceUrl': source_url, 'backupUrl': backup_url,
            'importUrl': 'legado://import/importonline?src=' + source_url,
            'detailUrl': 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'
        })
        found = True
assert found
sub_path.write_text(dump_json(sub), encoding='utf-8')

detail_path = ROOT / 'rss/data/details/beta/qidian-next.json'
detail = {
    'kind': 'source',
    'title': '🌈 起点增强 · Beta',
    'summary': summary,
    'badges': ['Beta', version, '详情富数据'],
    'sections': [
        {'title': 'Beta8 真机结论', 'text': '单独恢复官方 APP bookDetailInfo 后，真机仍只出现月票、作者等级、分类等少数字段；因此不能把它作为唯一详情补全链。'},
        {'title': '多层回归', 'text': '当前页面/缓存优先；稀疏时先尝试官方 APP，再按需恢复旧版已使用的起点图富数据。'},
        {'title': '简介与在看', 'text': '若起点图后简介、在看或总推荐仍缺失，再请求一次起点官方移动搜索页，并按当前 bookId 精确锚定结果，避免串书。'},
        {'title': '性能控制', 'text': '起点图成功缓存12小时，官方搜索成功缓存6小时；失败仅短缓存10分钟。不引入推书君第三请求。'},
        {'title': '冻结范围', 'text': '搜索、发现、目录、正文 Provider、段评/本章说、角色卡、书友圈与情无 VIP 认证链不变。'}
    ],
    'sourceUrl': source_url,
    'backupUrl': backup_url,
    'importUrl': 'legado://import/importonline?src=' + source_url
}
detail_path.parent.mkdir(parents=True, exist_ok=True)
detail_path.write_text(dump_json(detail), encoding='utf-8')

# Rebuild Beta bundle from every manifest entry currently marked beta.
bundle = []
for ent in manifest.get('sources', []):
    if ent.get('channel') != 'beta':
        continue
    p = ROOT / str(ent.get('sourcePath') or '')
    if not p.exists():
        continue
    obj = json.loads(p.read_text(encoding='utf-8'))
    if isinstance(obj, list):
        bundle.extend(obj)
    elif isinstance(obj, dict):
        bundle.append(obj)
(ROOT / 'bundles').mkdir(parents=True, exist_ok=True)
(ROOT / 'bundles/all-beta.json').write_text(dump_json(bundle), encoding='utf-8')

release_path = ROOT / 'docs/RELEASE_LOG.md'
old = release_path.read_text(encoding='utf-8')
marker = f'## {day} — Qidian Next {version} detail rich fallback'
if marker not in old:
    block = (
        marker + '\n\n'
        'Status: Beta/Test; awaiting user real-device confirmation.\n\n'
        'Real-device finding:\n\n'
        '- Beta8 still rendered only a small subset of detail metrics, proving APP `bookDetailInfo` is not a reliable sole enrichment path in the user environment.\n\n'
        'Changes:\n\n'
        '- Kept current-response/book-cache fast path and APP enrichment as the first layer.\n'
        '- Restored cached qidiantu rich-detail fallback only when the detail remains sparse.\n'
        '- Added exact-bookId Qidian mobile-search fallback for synopsis / reading / recommendation.\n'
        '- Removed the Beta8 30-minute failure suppression behavior; negative caches are short-lived.\n'
        '- Kept search/catalog/content/review/account domains frozen.\n'
        f'- Published SHA256: `{source_sha}`.\n\n'
    )
    lines = old.splitlines(True)
    if lines and lines[0].startswith('# RELEASE LOG'):
        old = lines[0] + '\n' + block + ''.join(lines[1:])
    else:
        old = block + old
    release_path.write_text(old, encoding='utf-8')

# Final gates.
check = json.loads(SRC_PATH.read_text(encoding='utf-8'))
assert check[0]['bookSourceName'] == '🌈 起点增强 · Beta'
assert 'v1.1.0-beta9' in check[0]['bookSourceComment']
ci = check[0]['ruleBookInfo']['init']
assert 'qfDetailAppEnrichV1109' in ci and 'qfDetailQidianTuV1109' in ci and 'qfDetailOfficialSearchV1109' in ci
assert '/ttsbook/' not in ci
assert json.loads(manifest_path.read_text(encoding='utf-8'))
assert json.loads(sub_path.read_text(encoding='utf-8'))
assert json.loads(detail_path.read_text(encoding='utf-8'))
assert json.loads((ROOT / 'bundles/all-beta.json').read_text(encoding='utf-8'))

if TRIGGER.exists():
    TRIGGER.unlink()

print('published', version, 'sha256', source_sha, 'bundle_items', len(bundle))
