import json,hashlib,time,re
from pathlib import Path

ROOT=Path('.')
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
PERM='https://m.qidian.com/?qf_source=qidian_next_8d7'
VERSION='1.1.0-beta1'
VCODE=11001
RAW='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v=11001'
CDN='https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v=11001'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

stable_before=sha(STABLE)
data=load(BETA)
assert isinstance(data,list) and len(data)==1
s=data[0]
assert s.get('bookSourceUrl')==PERM
raw_before=BETA.read_text(encoding='utf-8')
for marker in ['content.php','X-Content-Token','VIP正文已验证','Service request failed']:
    assert marker in raw_before, 'missing QW regression gate: '+marker

FAST_INIT=r'''<js>
var info=qfJson(qdParseBookInfo.call(this,result,baseUrl),{});
var bid=qdBookIdFromUrl(baseUrl);
var b=qfBook(this);
var searchName=qfQueryV09(baseUrl,"qfSearchName");
var searchAuthor=qfQueryV09(baseUrl,"qfSearchAuthor");
var searchIntro=qfQueryV09(baseUrl,"qfSearchIntro");
function bv(k){try{return b&&b.getVariable?String(b.getVariable(k)||""):"";}catch(e){return "";}}
function blank(v){return v===undefined||v===null||String(v).trim()==="";}
function put(k,v){try{if(!blank(v))qfPutBookVarV09.call(this,k,String(v));}catch(e){}}
function unesc(s){return String(s||'').replace(/\\u([0-9a-fA-F]{4})/g,function(_,h){try{return String.fromCharCode(parseInt(h,16));}catch(e){return _;}}).replace(/\\n/g,'\n').replace(/\\r/g,'').replace(/\\\//g,'/').replace(/&nbsp;/gi,' ').replace(/&amp;/gi,'&');}
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
function visibleMetric(html,label){
  var p=plain(html),e=String(label).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  var m=p.match(new RegExp('([0-9][0-9,]*(?:\\.[0-9]+)?)\\s*(万|亿)?\\s*'+e,'i'));
  if(!m)m=p.match(new RegExp(e+'\\s*[:：]?\\s*([0-9][0-9,]*(?:\\.[0-9]+)?)\\s*(万|亿)?','i'));
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

/* 1.1.0-beta1: detail fast path. Only parse the already-downloaded Qidian response here.
 * No APP/Web/Atom/Tu requests are allowed on the first detail render. */
var html=String(result||'');
if(blank(info.intro))info.intro=introFromCurrent(html)||searchIntro||bv('qf_introOfficial');
if(blank(info.recommendCount))info.recommendCount=visibleMetric(html,'总推荐')||scalar(html,['BssRecomTotal','bssRecomTotal','RecommendAll','recommendAll']);
if(blank(info.readingCount)){info.readingCount=scalar(html,['BssReadTotal','bssReadTotal','ReadingCount','readingCount']);if(info.readingCount)info.readingMetricLabel='在看';}
if(blank(info.monthTicket))info.monthTicket=visibleMetric(html,'月票')||scalar(html,['MonthTicketCount','monthTicketCount','MonthTicket','monthTicket']);
if(blank(info.ratingScore))info.ratingScore=scalar(html,['BookScore','bookScore','RatingScore','ratingScore','Score','score']);
if(blank(info.ratingCount))info.ratingCount=scalar(html,['ScoreUserCount','scoreUserCount','RatingCount','ratingCount']);

/* Optional rich data may reuse per-book cache from earlier successful detail loads, but never blocks first paint. */
cached('recommendCount','qf_recommendCount',false);cached('readingCount','qf_readingCount',false);cached('readingMetricLabel','qf_readingMetricLabel',false);
cached('monthTicket','qf_monthTicket',false);cached('ratingScore','qf_ratingScore',false);cached('ratingCount','qf_ratingCount',false);
cached('authorLevel','qf_authorLevel',false);cached('authorWorksCount','qf_authorWorksCount',false);cached('authorDesc','qf_authorDesc',false);cached('authorTags','qf_authorTags',false);
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
put.call(this,'qf_status',info.status);put.call(this,'qf_updateTime',info.updateTime);put.call(this,'qf_recommendCount',info.recommendCount);put.call(this,'qf_readingCount',info.readingCount);
put.call(this,'qf_readingMetricLabel',info.readingMetricLabel||'在看');put.call(this,'qf_monthTicket',info.monthTicket);put.call(this,'qf_ratingScore',info.ratingScore);put.call(this,'qf_ratingCount',info.ratingCount);
put.call(this,'qf_tags',Array.isArray(info.tags)?info.tags.join(' · '):info.tags);put.call(this,'qf_rights',Array.isArray(info.rights)?info.rights.join(' · '):info.rights);
put.call(this,'qf_authorLevel',info.authorLevel);put.call(this,'qf_authorWorksCount',info.authorWorksCount);put.call(this,'qf_authorDesc',info.authorDesc);put.call(this,'qf_authorTags',info.authorTags);
try{qfPutBookVarV09.call(this,'qf_detailCriticalPath','fast-current-response');}catch(_cp){}

var qfTocLocalV71='';
try{var qfj71=qfJava(this);if(bid&&qfj71&&qfj71.base64Encode)qfTocLocalV71='data:;base64,'+qfj71.base64Encode('qf-toc-v71:'+bid)+',{"type":"qfTocV71"}';}catch(_t71){}
info.tocUrl=bid?(qfTocLocalV71||('https://m.qidian.com/book/'+bid+'/catalog/')):String(baseUrl||'');
JSON.stringify(info);
</js>'''

NEW_INTRO=r'''<js>
var x=qfJson(result,{});
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim();}
function num(v){var s=clean(v);if(!s)return '';if(/万$|亿$|千$/.test(s))return s;var n=Number(s.replace(/[^0-9.]/g,''));if(!isFinite(n)||n<=0)return '';if(n>=1e8)return (Math.round(n/1e6)/100)+'亿';if(n>=1e4)return (Math.round(n/1e3)/10)+'万';if(n>=1e3)return (Math.round(n/100)/10)+'千';return String(Math.round(n));}
function score(v){var n=Number(clean(v));return isFinite(n)&&n>0&&n<=10?(Math.round(n*10)/10).toString():'';}
function cell(value,label){return '<td width="33%" align="center" style="padding:9px 4px"><b><font color="#149c95" size="5">'+esc(value)+'</font></b><br><small><font color="#8a949b">'+esc(label)+'</font></small></td>';}
function chips(v){var a=Array.isArray(v)?v:String(v||'').split(/\s*[·,，|\/]\s*/),seen={},o=[];for(var i=0;i<a.length&&o.length<6;i++){var t=clean(a[i]);if(!t||seen[t])continue;seen[t]=1;o.push('<font color="#168f89">【'+esc(t)+'】</font>');}return o.join(' ');}
var desc=String(x.intro||'').trim();if(/创作的.{0,20}(?:小说|作品)《/.test(desc)&&/(?:已更新|最新章节|主要角色)/.test(desc))desc='';
var metrics=[];
var sc=score(x.ratingScore),rec=num(x.recommendCount),watch=num(x.readingCount),mt=num(x.monthTicket),words=num(x.wordCount);
if(sc)metrics.push([sc,'评分']);
if(rec)metrics.push([rec,'总推荐']);
if(watch)metrics.push([watch,clean(x.readingMetricLabel)||'在看']);
if(metrics.length<3&&mt)metrics.push([mt,'月票']);
if(metrics.length<3&&words)metrics.push([words,'字数']);
var body='';
if(metrics.length){body+='<table width="100%" bgcolor="#f3f7f7" style="border-radius:14px;border-collapse:separate;margin:2px 0 12px 0"><tr>';for(var i=0;i<metrics.length&&i<3;i++)body+=cell(metrics[i][0],metrics[i][1]);body+='</tr></table>';}
body+='<br><b><font color="#149c95">▍快捷入口</font></b>';
body+='<br><br><button>💬 书友圈@onclick:qfBookInfoOpenCircleV373.call(this)</button>&nbsp;&nbsp;&nbsp;<button>🎭 角色卡@onclick:qfBookInfoOpenRoleV373.call(this)</button>&nbsp;&nbsp;&nbsp;<button>⚡ 正文源@onclick:qfBookInfoOpenSmartSourceV330.call(this)</button>';
var tg=chips(x.tags||x.bookTags||'');if(tg)body+='<br><br><b><font color="#149c95">▍作品标签</font></b><br><br>'+tg;
if(desc)body+='<br><br><b><font color="#149c95">▍内容简介</font></b><br><br><span style="line-height:1.78">'+esc(desc).replace(/\r\n|\r|\n/g,'<br>')+'</span>';
if(!desc&&!metrics.length)body+='<br><br><small><font color="#9aa1aa">详情基础信息已加载，可直接查看目录或开始阅读。</font></small>';
'<usehtml>'+body+'</usehtml>';
</js>'''

s['ruleBookInfo']['init']=FAST_INIT
s['ruleBookInfo']['intro']=NEW_INTRO
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceComment']='v1.1.0-beta1：详情页 UI / 性能专项。详情首屏改为当前起点响应快速解析，不再同步串行请求 APP/官网/Atom/第三方统计；自定义详情改为轻量核心数据条 + 快捷入口 + 标签 + 简介。保留 1.0.1-beta1 情无 VIP 正文认证修复及其它搜索/目录/评论/Provider 逻辑。'
s['lastUpdateTime']=int(time.time()*1000)
s['bookSourceUrl']=PERM
save(BETA,data)

# Distribution metadata.
now='2026-08-26T10:32:00+08:00'
sub=load(ROOT/'subscription/beta.json')
for it in sub.get('items',[]):
    if it.get('id')=='qidian-next-beta':
        it.update({
          'name':'🌈 起点增强 · Beta','summary':'详情页 UI / 性能专项：首屏只解析当前起点响应，移除同步多接口补全；信息区改为轻量卡片式布局。','channel':'beta','version':VERSION,'updatedAt':'2026-08-26',
          'tags':['起点','测试版','详情页','UI重构','性能优化','情无','多正文 Provider'],
          'changelog':['详情首屏取消 APP/官网/Atom/第三方同步补全请求，优先快速显示基础信息','自定义详情重排为核心数据、快捷入口、标签、内容简介四块','保留 1.0.1-beta1 情无 VIP 正文认证修复'],
          'sourceUrl':RAW,'backupUrl':CDN,'importUrl':'legado://import/importonline?src='+RAW,
          'detailUrl':'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'
        })
sub['updatedAt']=now
save(ROOT/'subscription/beta.json',sub)

bundle=load(ROOT/'bundles/all-beta.json')
if isinstance(bundle,list):
    replaced=False
    for i,it in enumerate(bundle):
        if isinstance(it,dict) and (it.get('bookSourceUrl')==PERM or str(it.get('bookSourceName','')).startswith('🌈 起点增强')):
            bundle[i]=s;replaced=True;break
    if not replaced: bundle.append(s)
elif isinstance(bundle,dict) and isinstance(bundle.get('sources'),list):
    a=bundle['sources'];replaced=False
    for i,it in enumerate(a):
        if isinstance(it,dict) and (it.get('bookSourceUrl')==PERM or str(it.get('bookSourceName','')).startswith('🌈 起点增强')):
            a[i]=s;replaced=True;break
    if not replaced:a.append(s)
else: raise SystemExit('unsupported beta bundle shape')
save(ROOT/'bundles/all-beta.json',bundle)

manifest=load(ROOT/'manifest.json')
for it in manifest.get('sources',[]):
    if it.get('id')=='qidian-next-beta':
        it.update({'name':'🌈 起点增强 · Beta','channel':'beta','version':VERSION,'versionCode':VCODE,'updatedAt':now,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','sourceUrl':RAW,'bookSourceUrl':PERM,'summary':'详情页 UI / 性能专项：首屏只解析当前起点响应，移除同步多接口补全；信息区改为轻量布局。','tags':['起点','测试版','详情页','UI重构','性能优化','情无'],'changelog':['首屏详情改为零额外同步网络请求','详情自定义区域轻量重排','保留情无 VIP 正文认证修复']})
manifest['updatedAt']=now
save(ROOT/'manifest.json',manifest)

rss=load(ROOT/'rss/data/details/beta/qidian-next.json')
rss.update({'kind':'source','title':'🌈 起点增强 · Beta','summary':'详情页 UI / 性能专项：优先快速显示，再按需进入书友圈、角色卡和正文源功能。','badges':['Beta',VERSION,'详情优化'],'sections':[{'title':'本次测试','text':'详情首屏不再为了总推荐、评分、在看等统计同步串行请求多套接口；只解析当前起点响应和已有书籍缓存。'},{'title':'UI 调整','text':'保留阅读原生封面/书名区域，自定义信息区精简为核心数据、快捷入口、作品标签和内容简介，减少重复字段和视觉堆叠。'},{'title':'回归重点','text':'重点检查详情打开速度、简介/标签/快捷按钮，以及搜索、目录、正文、评论和情无 VIP 正文是否保持正常。'}],'sourceUrl':RAW,'backupUrl':CDN})
save(ROOT/'rss/data/details/beta/qidian-next.json',rss)

# Recompute SHA after source write and put into manifest.
beta_sha=sha(BETA)
manifest=load(ROOT/'manifest.json')
for it in manifest.get('sources',[]):
    if it.get('id')=='qidian-next-beta': it['sha256']=beta_sha
save(ROOT/'manifest.json',manifest)

# Docs current-state handoff + release record.
hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
h=hp.read_text(encoding='utf-8')
block='''\n## Detail UI / performance Beta 1.1.0-beta1 (2026-08-26)\n\n- Replaced the 61k-character blocking detail augmentation path with a fast first-paint path based on the already-downloaded Qidian response plus per-book cached values.\n- No APP/Web/Atom/QidianTu/TuShuJun synchronous requests are allowed from the new `ruleBookInfo.init` first-paint path.\n- Native Legado cover/title/author/latest-chapter area remains responsible for primary metadata.\n- Custom detail HTML is reduced to a compact metric strip, on-demand interaction buttons, up to six tags, and synopsis.\n- Book-circle, role-card and smart-source actions remain on-demand buttons and therefore do not block initial detail rendering.\n- The 1.0.1-beta1 QW VIP-content authentication/request-header fix is a hard regression gate for all later Betas.\n'''
if '## Detail UI / performance Beta 1.1.0-beta1' not in h: hp.write_text(h.rstrip()+block+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md';r=rp.read_text(encoding='utf-8')
rel=f'''## 2026-08-26 — 起点增强 {VERSION}\n\nStatus: Beta/Test; detail UI/performance redesign awaiting real-device confirmation.\n\nChanges:\n\n- Replaced blocking multi-provider detail augmentation with a current-response fast path; first render performs no extra synchronous APP/Web/Atom/third-party detail requests.\n- Redesigned custom detail information into compact metrics, on-demand interaction entries, tags and synopsis.\n- Preserved the 1.0.1-beta1 QW VIP-content authentication fix and all search/catalog/content/review Provider logic.\n- Stable 1.0.0 remains unchanged.\n- Beta SHA256: `{beta_sha}`.\n\n'''
if f'## 2026-08-26 — 起点增强 {VERSION}' not in r:
    r='# RELEASE LOG\n\n'+rel+r.split('# RELEASE LOG\n\n',1)[1] if r.startswith('# RELEASE LOG\n\n') else rel+r
    rp.write_text(r,encoding='utf-8')

kp=ROOT/'docs/KNOWN_ISSUES.md';k=kp.read_text(encoding='utf-8')
issue='''\n## 21. Qidian detail page was visually dense and blocked on multiple enrichment requests — redesigned in 1.1.0-beta1\n\nSymptom: the detail page exposed many useful statistics but duplicated native metadata and could wait on several sequential APP/Web/Atom/third-party fallbacks before rendering.\n\nBeta fix: first paint now parses only the current Qidian response and per-book cache; optional interaction features are opened on demand. The custom area is reduced to metrics, shortcuts, tags and synopsis.\n\nStatus: Beta 1.1.0-beta1 published for real-device speed/UI regression testing.\n'''
if '## 21. Qidian detail page was visually dense' not in k: kp.write_text(k.rstrip()+issue+'\n',encoding='utf-8')

# Final gates.
assert sha(STABLE)==stable_before, 'Stable source changed'
final=BETA.read_text(encoding='utf-8')
for marker in ['content.php','X-Content-Token','VIP正文已验证','Service request failed']:
    assert marker in final, 'QW fix regressed: '+marker
assert 'qfOfficialCallV400' not in FAST_INIT and '.ajax(' not in FAST_INIT and 'qfAtomPost' not in FAST_INIT
assert s['bookSourceUrl']==PERM
print('published',VERSION,beta_sha,'stable',stable_before)
