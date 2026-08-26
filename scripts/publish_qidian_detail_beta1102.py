import json, hashlib, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path('.')
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
PERM = 'https://m.qidian.com/?qf_source=qidian_next_8d7'
VERSION = '1.1.0-beta2'
VCODE = 11002
RAW = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v=11002'
CDN = 'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v=11002'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text(encoding='utf-8'))

def save(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

stable_before = sha(STABLE)
data = load(BETA)
assert isinstance(data, list) and len(data) == 1
s = data[0]
assert s.get('bookSourceUrl') == PERM
raw_before = BETA.read_text(encoding='utf-8')
for marker in ['X-Content-Token', 'VIP正文已验证']:
    assert marker in raw_before, 'missing QW regression gate: ' + marker

FAST_INIT = r'''<js>
var info=qfJson(qdParseBookInfo.call(this,result,baseUrl),{});
var bid=qdBookIdFromUrl(baseUrl);
var b=qfBook(this);
var searchName=qfQueryV09(baseUrl,"qfSearchName");
var searchAuthor=qfQueryV09(baseUrl,"qfSearchAuthor");
var searchIntro=qfQueryV09(baseUrl,"qfSearchIntro");
function bv(k){try{return b&&b.getVariable?String(b.getVariable(k)||""):"";}catch(e){return "";}}
function blank(v){return v===undefined||v===null||String(v).trim()==="";}
function put(k,v){try{if(!blank(v))qfPutBookVarV09.call(this,k,String(v));}catch(e){}}
function unesc(s){return String(s||'').replace(/\\u([0-9a-fA-F]{4})/g,function(_,h){try{return String.fromCharCode(parseInt(h,16));}catch(e){return _;}}).replace(/\\n/g,'\n').replace(/\\r/g,'').replace(/\\\//g,'/').replace(/\\"/g,'"').replace(/&nbsp;/gi,' ').replace(/&amp;/gi,'&');}
function plain(s){return String(s||'').replace(/<script[\s\S]*?<\/script>/gi,' ').replace(/<style[\s\S]*?<\/style>/gi,' ').replace(/<br\s*\/?>/gi,'\n').replace(/<\/p>/gi,'\n').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();}
function scalar(html,keys){
  html=String(html||'');
  for(var i=0;i<keys.length;i++){
    var k=String(keys[i]).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    var rs=[
      new RegExp('["\\\']?'+k+'["\\\']?\\s*[:=]\\s*["\\\']?([0-9]+(?:\\.[0-9]+)?)','i'),
      new RegExp('\\\\"'+k+'\\\\"\\s*:\\s*\\\\"?([0-9]+(?:\\.[0-9]+)?)','i')
    ];
    for(var j=0;j<rs.length;j++){var m=html.match(rs[j]);if(m&&m[1])return String(m[1]);}
  }
  return '';
}
function textScalar(html,keys,maxLen){
  html=String(html||'');maxLen=maxLen||240;
  for(var i=0;i<keys.length;i++){
    var k=String(keys[i]).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    var rs=[
      new RegExp('["\\\']?'+k+'["\\\']?\\s*[:=]\\s*["\\\']([^"\\\']{1,'+maxLen+'})["\\\']','i'),
      new RegExp('\\\\"'+k+'\\\\"\\s*:\\s*\\\\"([^\\"]{1,'+maxLen+'})\\\\"','i')
    ];
    for(var j=0;j<rs.length;j++){
      var m=html.match(rs[j]);if(!m||!m[1])continue;
      var t=unesc(m[1]).replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
      if(t)return t;
    }
  }
  return '';
}
function listScalar(html,keys){
  html=String(html||'');
  for(var i=0;i<keys.length;i++){
    var k=String(keys[i]).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    var ma=html.match(new RegExp('["\\\']?'+k+'["\\\']?\\s*[:=]\\s*\\[([\\s\\S]{1,1200}?)\\]','i'));
    if(ma&&ma[1]){
      var out=[],seen={},rx=/["']([^"']{1,40})["']/g,m;
      while((m=rx.exec(ma[1]))&&out.length<12){var t=unesc(m[1]).replace(/\s+/g,' ').trim();if(t&&!seen[t]){seen[t]=1;out.push(t);}}
      if(out.length)return out;
    }
    var ts=textScalar(html,[keys[i]],500);
    if(ts){var arr=ts.split(/\s*[·,，|\/]\s*/).filter(Boolean);if(arr.length)return arr.slice(0,12);}
  }
  return [];
}
function visibleMetric(html,label){
  var p=plain(html),e=String(label).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  var m=p.match(new RegExp('([0-9][0-9,]*(?:\\.[0-9]+)?)\\s*(万|亿|千)?\\s*'+e,'i'));
  if(!m)m=p.match(new RegExp(e+'\\s*[:：]?\\s*([0-9][0-9,]*(?:\\.[0-9]+)?)\\s*(万|亿|千)?','i'));
  return m&&m[1]?String(m[1]).replace(/,/g,'')+(m[2]||''):'';
}
function introFromCurrent(html){
  html=String(html||'');if(!html)return '';
  try{
    var d=org.jsoup.Jsoup.parse(html),sels=['#book-intro-detail','.book-intro-detail','.book-intro','.intro'];
    for(var i=0;i<sels.length;i++){
      var es=d.select(sels[i]);
      if(es&&es.size&&es.size()>0){var t=String(es.first().text()||'').trim();if(t.length>=10&&!/创作的.{0,20}(?:小说|作品)《/.test(t))return t;}
    }
  }catch(e){}
  var ks=['BookIntro','bookIntro','BookIntroWords','bookIntroWords','BookDesc','bookDesc','BookDescription','bookDescription','Introduction','introduction'];
  for(var j=0;j<ks.length;j++){
    var k=ks[j].replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    var r=new RegExp('["\\\']?'+k+'["\\\']?\\s*[:=]\\s*["\\\']([\\s\\S]{8,3500}?)["\\\']\\s*(?:[,}])','i');
    var m=html.match(r);if(!m||!m[1])continue;
    var t=unesc(m[1]).replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
    if(t.length>=10&&!/创作的.{0,20}(?:小说|作品)《/.test(t))return t;
  }
  return '';
}
function cached(k,vk,asList){
  if(!blank(info[k]))return;
  var v=bv(vk||('qf_'+k));if(!v)return;
  info[k]=asList?v.split(/\s*[·,，|\/]\s*/).filter(Boolean):v;
}
try{
  if(searchName)info.name=searchName;else if(blank(info.name)&&b)info.name=String(b.name||'');
  if(searchAuthor)info.author=searchAuthor;else if(blank(info.author)&&b)info.author=String(b.author||'');
  if(blank(info.coverUrl)&&b)info.coverUrl=String(b.coverUrl||'');
  if(blank(info.lastChapter)&&b)info.lastChapter=String(b.latestChapterTitle||'');
  if(blank(info.wordCount)&&b)info.wordCount=String(b.wordCount||'');
}catch(_base){}

/* 1.1.0-beta2: rich fast path. Parse only the already-downloaded Qidian response plus book cache. */
var html=String(result||'');
if(blank(info.intro))info.intro=introFromCurrent(html)||searchIntro||bv('qf_introOfficial');
if(blank(info.recommendCount))info.recommendCount=visibleMetric(html,'总推荐')||scalar(html,['BssRecomTotal','bssRecomTotal','RecommendAll','recommendAll','TotalRecommendCount','totalRecommendCount']);
if(blank(info.readingCount)){info.readingCount=scalar(html,['BssReadTotal','bssReadTotal','ReadingCount','readingCount','ReaderCount','readerCount']);if(info.readingCount)info.readingMetricLabel='在看';}
if(blank(info.monthTicket))info.monthTicket=visibleMetric(html,'月票')||scalar(html,['MonthTicketCount','monthTicketCount','MonthTicket','monthTicket']);
if(blank(info.ratingScore))info.ratingScore=scalar(html,['BookScore','bookScore','RatingScore','ratingScore']);
if(blank(info.ratingCount))info.ratingCount=scalar(html,['ScoreUserCount','scoreUserCount','RatingCount','ratingCount','ScoreCount','scoreCount']);
if(blank(info.collectionCount))info.collectionCount=visibleMetric(html,'收藏')||scalar(html,['CollectionCount','collectionCount','CollectCount','collectCount']);
if(blank(info.fansCount))info.fansCount=visibleMetric(html,'粉丝')||scalar(html,['FansCount','fansCount','BookFansCount','bookFansCount']);
if(blank(info.leaderCount))info.leaderCount=visibleMetric(html,'盟主')||scalar(html,['LeagueMasterCount','leagueMasterCount','LeaderCount','leaderCount','RealMasterCount','realMasterCount']);
if(blank(info.investCount))info.investCount=scalar(html,['InvestCount','investCount','InvestmentCount','investmentCount']);
if(blank(info.firstSubscribe))info.firstSubscribe=scalar(html,['FirstSubscribe','firstSubscribe','FirstOrder','firstOrder']);
if(blank(info.authorLevel))info.authorLevel=textScalar(html,['AuthorLevelName','authorLevelName','AuthorLevel','authorLevel'],40);
if(blank(info.authorWorksCount))info.authorWorksCount=scalar(html,['AuthorWorksCount','authorWorksCount','WorksCount','worksCount']);
if(blank(info.authorDesc))info.authorDesc=textScalar(html,['AuthorDesc','authorDesc','AuthorDescription','authorDescription'],300);
if(blank(info.authorTags))info.authorTags=textScalar(html,['AuthorTags','authorTags'],180);
if(blank(info.status))info.status=textScalar(html,['BookStatusName','bookStatusName','StatusName','statusName'],30);
if(blank(info.updateTime))info.updateTime=textScalar(html,['LastUpdateTime','lastUpdateTime','UpdateTime','updateTime'],50);
if(blank(info.publishDate))info.publishDate=textScalar(html,['PublishDate','publishDate','CreateTime','createTime'],50);
if(blank(info.listingDate))info.listingDate=textScalar(html,['ListingDate','listingDate','VipStartTime','vipStartTime'],50);
if(blank(info.tags)){var ts=listScalar(html,['BookTags','bookTags','TagList','tagList']);if(ts.length)info.tags=ts;}
if(blank(info.honors)){var hs=listScalar(html,['HonorList','honorList','Honors','honors']);if(hs.length)info.honors=hs;}
if(blank(info.isVip)){var iv=scalar(html,['IsVip','isVip','VIP','VipStatus','vipStatus']);if(iv)info.isVip=(String(iv)==='1');}

/* Reuse previous successful rich values if present; no request is made to refresh them here. */
cached('recommendCount','qf_recommendCount',false);cached('readingCount','qf_readingCount',false);cached('readingMetricLabel','qf_readingMetricLabel',false);
cached('monthTicket','qf_monthTicket',false);cached('ratingScore','qf_ratingScore',false);cached('ratingCount','qf_ratingCount',false);
cached('collectionCount','qf_collectionCount',false);cached('fansCount','qf_fansCount',false);cached('leaderCount','qf_leaderCount',false);cached('investCount','qf_investCount',false);cached('firstSubscribe','qf_firstSubscribe',false);
cached('authorLevel','qf_authorLevel',false);cached('authorWorksCount','qf_authorWorksCount',false);cached('authorDesc','qf_authorDesc',false);cached('authorTags','qf_authorTags',false);
cached('status','qf_status',false);cached('updateTime','qf_updateTime',false);cached('publishDate','qf_publishDate',false);cached('listingDate','qf_listingDate',false);
cached('tags','qf_tags',true);cached('rights','qf_rights',true);cached('honors','qf_honors',true);cached('isVip','qf_isVip',false);

info.serverLimitState=bv('qf_serverLimitState')||'未知';
info.serverLimitSource=bv('qf_serverLimitSource')||'';
info.serverLimitEvidence=bv('qf_serverLimitEvidence')||'';
if(!blank(info.isVip))info.isVip=(info.isVip===true||String(info.isVip)==='1'||String(info.isVip).toLowerCase()==='true');
var lim=String(info.serverLimitState||'');
info.isLimitedFree=/^(?:限免|限时免费)$/.test(lim);
if(info.isLimitedFree){
  var rr=Array.isArray(info.rights)?info.rights.slice():[];
  if(!/限免|限时免费/.test(rr.join(' ')))rr.push(info.serverLimitSource==='神魔'?'限时免费':'限免');
  info.rights=rr;
}
(function(){
  var out=[],seen={};function add(v){v=String(v||'').trim();if(v&&!seen[v]&&out.length<6){seen[v]=1;out.push(v);}}
  add(info.status||'');if(info.isVip)add('VIP');if(info.isLimitedFree)add(info.serverLimitSource==='神魔'?'限时免费':'限免');
  add(info.kind||'');add(info.subKind||'');
  info.displayKind=out.join(',');
})();
if(bid&&blank(info.coverUrl))info.coverUrl='https://bookcover.yuewen.com/qdbimg/349573/'+bid+'/180';

put.call(this,'qf_bid',bid);put.call(this,'qf_detailBind',String(bid||'')+'|'+String(info.name||searchName||''));
put.call(this,'qf_name',info.name);put.call(this,'qf_author',info.author);put.call(this,'qf_kind',info.kind);put.call(this,'qf_subKind',info.subKind);
put.call(this,'qf_introOfficial',info.intro);put.call(this,'qf_words',info.wordCount);put.call(this,'qf_wordCount',info.wordCount);put.call(this,'qf_lastChapter_v70',info.lastChapter);
put.call(this,'qf_status',info.status);put.call(this,'qf_updateTime',info.updateTime);put.call(this,'qf_publishDate',info.publishDate);put.call(this,'qf_listingDate',info.listingDate);
put.call(this,'qf_recommendCount',info.recommendCount);put.call(this,'qf_readingCount',info.readingCount);put.call(this,'qf_readingMetricLabel',info.readingMetricLabel||'在看');
put.call(this,'qf_monthTicket',info.monthTicket);put.call(this,'qf_ratingScore',info.ratingScore);put.call(this,'qf_ratingCount',info.ratingCount);put.call(this,'qf_collectionCount',info.collectionCount);
put.call(this,'qf_fansCount',info.fansCount);put.call(this,'qf_leaderCount',info.leaderCount);put.call(this,'qf_investCount',info.investCount);put.call(this,'qf_firstSubscribe',info.firstSubscribe);
put.call(this,'qf_tags',Array.isArray(info.tags)?info.tags.join(' · '):info.tags);put.call(this,'qf_rights',Array.isArray(info.rights)?info.rights.join(' · '):info.rights);put.call(this,'qf_honors',Array.isArray(info.honors)?info.honors.join(' · '):info.honors);
put.call(this,'qf_authorLevel',info.authorLevel);put.call(this,'qf_authorWorksCount',info.authorWorksCount);put.call(this,'qf_authorDesc',info.authorDesc);put.call(this,'qf_authorTags',info.authorTags);
if(info.isVip)put.call(this,'qf_isVip','1');
try{qfPutBookVarV09.call(this,'qf_detailCriticalPath','rich-fast-current-response');}catch(_cp){}

var qfTocLocalV71='';
try{var qfj71=qfJava(this);if(bid&&qfj71&&qfj71.base64Encode)qfTocLocalV71='data:;base64,'+qfj71.base64Encode('qf-toc-v71:'+bid)+',{"type":"qfTocV71"}';}catch(_t71){}
info.tocUrl=bid?(qfTocLocalV71||('https://m.qidian.com/book/'+bid+'/catalog/')):String(baseUrl||'');
JSON.stringify(info);
</js>'''

NEW_INTRO = r'''<js>
var x=qfJson(result,{});
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim();}
function num(v){var s=clean(v);if(!s)return '';if(/万$|亿$|千$/.test(s))return s;var n=Number(s.replace(/[^0-9.]/g,''));if(!isFinite(n)||n<=0)return '';if(n>=1e8)return (Math.round(n/1e6)/100)+'亿';if(n>=1e4)return (Math.round(n/1e3)/10)+'万';if(n>=1e3)return (Math.round(n/100)/10)+'千';return String(Math.round(n));}
function score(v){var n=Number(clean(v));return isFinite(n)&&n>0&&n<=10?(Math.round(n*10)/10).toString():'';}
function yes(v){var s=clean(v).toLowerCase();return v===true||s==='1'||s==='true'||s==='yes'||s==='是';}
function arr(v){return Array.isArray(v)?v:String(v||'').split(/\s*[·,，|\/]\s*/).filter(Boolean);}
function row(icon,label,value){value=clean(value);return value?'<br>'+icon+' <font color="#8a949b">'+esc(label)+'</font>　'+esc(value):'';}
function datum(icon,label,value){value=clean(value);return value?icon+' <font color="#8a949b">'+esc(label)+'</font> <b><font color="#149c95">'+esc(value)+'</font></b>':'';}
function dataRows(items){var a=[];for(var i=0;i<items.length;i++)if(items[i][2])a.push(items[i]);var h='';for(var j=0;j<a.length;j+=2){h+='<br>'+datum(a[j][0],a[j][1],a[j][2]);if(a[j+1])h+='　　'+datum(a[j+1][0],a[j+1][1],a[j+1][2]);}return h;}
function chips(v,limit,color){var a=arr(v),seen={},o=[];for(var i=0;i<a.length&&o.length<(limit||8);i++){var t=clean(a[i]);if(!t||seen[t])continue;seen[t]=1;o.push('<font color="'+(color||'#168f89')+'">【'+esc(t)+'】</font>');}return o.join(' ');}
function date(v){var s=clean(v);if(!s)return '';var n=Number(s);if(isFinite(n)&&n>1e9){if(n<1e12)n*=1000;try{return java.timeFormatUTC(n,'yyyy-MM-dd HH:mm',8*36e5);}catch(e){}}return s.replace('T',' ').replace(/\.\d+Z?$/,'').replace(/Z$/,'');}

var desc=String(x.intro||'').trim();if(/创作的.{0,20}(?:小说|作品)《/.test(desc)&&/(?:已更新|最新章节|主要角色)/.test(desc))desc='';
var body='';
var author=clean(x.author),level=clean(x.authorLevel),works=clean(x.authorWorksCount),type=clean(x.subKind)||clean(x.kind),status=clean(x.status);
var rights=arr(x.rights).join(' · ');if(yes(x.isVip)&&rights.indexOf('VIP')<0)rights+=(rights?' · ':'')+'VIP';
var limitState=clean(x.serverLimitState),limitSource=clean(x.serverLimitSource);

body+='<b><font color="#149c95">▍作品资料</font></b>';
body+=row('✍️','作者',author+(level?' · '+level:'')+(works?' · '+works+'本作品':''));
body+=row('📚','分类',type+(status?' · '+status:'')+(rights?' · '+rights:''));
if(limitState&&limitState!=='未知')body+=row('🆓','限免',limitState+(limitSource?' · '+limitSource:''));
if(clean(x.updateTime))body+=row('🕒','更新',date(x.updateTime));
if(clean(x.listingDate))body+=row('📅','上架',date(x.listingDate));
var ad=clean(x.authorDesc);if(ad&&ad.length<=120)body+=row('🪪','作者简介',ad);

var sc=score(x.ratingScore),rec=num(x.recommendCount),watch=num(x.readingCount),mt=num(x.monthTicket),col=num(x.collectionCount),fans=num(x.fansCount),leader=num(x.leaderCount),invest=num(x.investCount),first=num(x.firstSubscribe);
var data=[
 ['🔥','总推荐',rec],['🎟','月票',mt],['👁',clean(x.readingMetricLabel)||'在看',watch],['💯','评分',sc?(sc+(clean(x.ratingCount)?' / '+num(x.ratingCount)+'人':'')):'' ],
 ['⭐','收藏',col],['👥','粉丝',fans],['🏅','盟主',leader],['💎','投资',invest],['📌','首订',first]
];
var dr=dataRows(data);if(dr)body+='<br><br><b><font color="#f08a38">▍作品数据</font></b>'+dr;

body+='<br><br><b><font color="#149c95">▍快捷入口</font></b>';
body+='<br><br><button>💬 书友圈@onclick:qfBookInfoOpenCircleV373.call(this)</button>　<button>🎭 角色卡@onclick:qfBookInfoOpenRoleV373.call(this)</button>　<button>⚡ 正文源@onclick:qfBookInfoOpenSmartSourceV330.call(this)</button>';

var tg=chips(x.tags||x.bookTags||'',8,'#168f89'),hon=chips(x.honors||'',6,'#b67821'),at=chips(x.authorTags||'',5,'#7162a8');
if(tg||hon||at){body+='<br><br><b><font color="#9a72c7">▍标签与荣誉</font></b>';if(tg)body+='<br><br>'+tg;if(at)body+='<br>作者：'+at;if(hon)body+='<br>🏆 '+hon;}
if(desc)body+='<br><br><b><font color="#149c95">▍内容简介</font></b><br><br><span>'+esc(desc).replace(/\r\n|\r|\n/g,'<br>')+'</span>';
'<usehtml>'+body+'</usehtml>';
</js>'''

s['ruleBookInfo']['init'] = FAST_INIT
s['ruleBookInfo']['intro'] = NEW_INTRO
s['bookSourceName'] = '🌈 起点增强 · Beta'
s['bookSourceComment'] = 'v1.1.0-beta2：详情页信息密度回调。保持 beta1 的零额外同步请求快速首屏，同时恢复作品资料、作品数据、标签与荣誉等信息；弃用真机兼容性不稳定的 table 卡片，改用阅读更稳定的普通 HTML 行布局。保留情无 VIP 正文认证修复及其它搜索/目录/评论/Provider 逻辑。'
s['lastUpdateTime'] = int(time.time() * 1000)
s['bookSourceUrl'] = PERM
save(BETA, data)

now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
sub = load(ROOT / 'subscription/beta.json')
for it in sub.get('items', []):
    if it.get('id') == 'qidian-next-beta':
        it.update({
            'name': '🌈 起点增强 · Beta',
            'summary': '详情页 beta2：不增加首屏网络请求，恢复作品资料/数据/标签荣誉，并改用阅读兼容性更好的普通 HTML 行布局。',
            'channel': 'beta', 'version': VERSION, 'updatedAt': '2026-08-26',
            'tags': ['起点','测试版','详情页','信息增强','性能优化','情无','多正文 Provider'],
            'changelog': ['保持详情首屏零额外同步网络请求','恢复作品资料、作品数据、标签与荣誉等信息','移除真机兼容性不稳定的 table 数据卡片，改用普通 HTML 行布局','保留情无 VIP 正文认证修复'],
            'sourceUrl': RAW, 'backupUrl': CDN, 'importUrl': 'legado://import/importonline?src=' + RAW,
            'detailUrl': 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'
        })
sub['updatedAt'] = now
save(ROOT / 'subscription/beta.json', sub)

bundle = load(ROOT / 'bundles/all-beta.json')
if isinstance(bundle, list):
    replaced = False
    for i, it in enumerate(bundle):
        if isinstance(it, dict) and (it.get('bookSourceUrl') == PERM or str(it.get('bookSourceName','')).startswith('🌈 起点增强')):
            bundle[i] = s; replaced = True; break
    if not replaced: bundle.append(s)
elif isinstance(bundle, dict) and isinstance(bundle.get('sources'), list):
    a = bundle['sources']; replaced = False
    for i, it in enumerate(a):
        if isinstance(it, dict) and (it.get('bookSourceUrl') == PERM or str(it.get('bookSourceName','')).startswith('🌈 起点增强')):
            a[i] = s; replaced = True; break
    if not replaced: a.append(s)
else:
    raise SystemExit('unsupported beta bundle shape')
save(ROOT / 'bundles/all-beta.json', bundle)

manifest = load(ROOT / 'manifest.json')
for it in manifest.get('sources', []):
    if it.get('id') == 'qidian-next-beta':
        it.update({
            'name':'🌈 起点增强 · Beta','channel':'beta','version':VERSION,'versionCode':VCODE,'updatedAt':now,
            'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','sourceUrl':RAW,'bookSourceUrl':PERM,
            'summary':'详情页 beta2：首屏继续零额外同步请求，恢复丰富信息并修复 table 真机渲染兼容问题。',
            'tags':['起点','测试版','详情页','信息增强','性能优化','情无'],
            'changelog':['保持首屏快速路径','恢复作品资料/作品数据/标签荣誉','数据区改用普通 HTML 行，避免 table 兼容问题','保留情无 VIP 正文认证修复']
        })
manifest['updatedAt'] = now
save(ROOT / 'manifest.json', manifest)

rss = load(ROOT / 'rss/data/details/beta/qidian-next.json')
rss.update({
    'kind':'source','title':'🌈 起点增强 · Beta','summary':'详情页 beta2：在不牺牲首屏速度的前提下恢复信息密度，并修复数据卡片真机排版。',
    'badges':['Beta',VERSION,'详情增强'],
    'sections':[
        {'title':'本次测试','text':'详情首屏仍然只解析当前起点响应和已有书籍缓存，不恢复 APP/官网/Atom/第三方同步补全请求。'},
        {'title':'信息恢复','text':'重新显示作品资料、总推荐/月票/在看/评分/收藏/粉丝/盟主/投资等作品数据，以及标签与荣誉；无值字段自动隐藏。'},
        {'title':'真机 UI 修复','text':'移除上一版 table 数据卡片，改用普通 HTML 行和自动换行，优先兼容阅读详情页实际渲染。'},
        {'title':'回归重点','text':'重点检查详情信息是否足够、排列是否正常、打开速度是否仍明显快于旧版，以及书友圈/角色卡/正文源按钮是否正常。'}
    ],
    'sourceUrl':RAW,'backupUrl':CDN
})
save(ROOT / 'rss/data/details/beta/qidian-next.json', rss)

beta_sha = sha(BETA)
manifest = load(ROOT / 'manifest.json')
for it in manifest.get('sources', []):
    if it.get('id') == 'qidian-next-beta': it['sha256'] = beta_sha
save(ROOT / 'manifest.json', manifest)

hp = ROOT / 'docs/sources/qidian-next/PROJECT_HANDOFF.md'
h = hp.read_text(encoding='utf-8')
block = '''\n## Detail richness Beta 1.1.0-beta2 (2026-08-26)\n\n- Real-device beta1 showed the metric `<table>` rendering vertically/misaligned and the overall detail information becoming too sparse.\n- beta2 keeps the zero-extra-request first-paint architecture, but expands parsing/cached display for author metadata, status, update time, recommendation/month-ticket/reading/rating/collection/fans/leader/invest/first-subscribe metrics, tags and honors.\n- The metric strip is replaced by plain HTML rows because Legado detail HTML/CSS support is device/version dependent; simple rows are the preferred compatibility baseline.\n- Missing fields are hidden rather than synchronously fetched. Book circle, role card and smart source remain on-demand.\n'''
if '## Detail richness Beta 1.1.0-beta2' not in h:
    hp.write_text(h.rstrip() + block + '\n', encoding='utf-8')

rp = ROOT / 'docs/RELEASE_LOG.md'
r = rp.read_text(encoding='utf-8')
rel = f'''## 2026-08-26 — 起点增强 {VERSION}\n\nStatus: Beta/Test; detail richness/UI compatibility follow-up awaiting real-device confirmation.\n\nChanges:\n\n- Kept the beta1 zero-extra-request detail fast path.\n- Restored richer work metadata, statistics, tags and honors from the current response or existing per-book cache.\n- Replaced the incompatible metric `<table>` with plain HTML rows for Legado real-device compatibility.\n- Missing metrics remain hidden instead of triggering synchronous enrichment requests.\n- Preserved QW VIP-content authentication fix and Stable 1.0.0 unchanged.\n- Beta SHA256: `{beta_sha}`.\n\n'''
if f'## 2026-08-26 — 起点增强 {VERSION}' not in r:
    if r.startswith('# RELEASE LOG\n\n'):
        r = '# RELEASE LOG\n\n' + rel + r.split('# RELEASE LOG\n\n',1)[1]
    else:
        r = rel + r
    rp.write_text(r, encoding='utf-8')

kp = ROOT / 'docs/KNOWN_ISSUES.md'
k = kp.read_text(encoding='utf-8')
issue = '''\n## 22. Detail beta1 became too sparse and its table metrics rendered incorrectly on real devices — adjusted in 1.1.0-beta2\n\nSymptom: the first performance-focused detail redesign rendered only a few metrics on some books, and the HTML table was flattened into misaligned vertical text on the tested Legado build.\n\nBeta fix: restore rich fields from the current response/cache while keeping zero extra first-paint requests; replace table layout with plain HTML rows and hide unavailable fields.\n\nStatus: Beta 1.1.0-beta2 published for real-device UI/information-density testing.\n'''
if '## 22. Detail beta1 became too sparse' not in k:
    kp.write_text(k.rstrip() + issue + '\n', encoding='utf-8')

assert sha(STABLE) == stable_before, 'Stable source changed'
final = BETA.read_text(encoding='utf-8')
for marker in ['X-Content-Token', 'VIP正文已验证']:
    assert marker in final, 'QW fix regressed: ' + marker
assert 'qfOfficialCallV400' not in FAST_INIT and '.ajax(' not in FAST_INIT and 'qfAtomPost' not in FAST_INIT
assert '<table' not in NEW_INTRO.lower()
assert s['bookSourceUrl'] == PERM
print('published', VERSION, beta_sha, 'init', len(FAST_INIT), 'intro', len(NEW_INTRO), 'stable', stable_before)
