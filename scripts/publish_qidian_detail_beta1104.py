import json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT=Path('.')
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
PERM='https://m.qidian.com/?qf_source=qidian_next_8d7'
VERSION='1.1.0-beta4'
VCODE=11004
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VCODE}'
CDN=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VCODE}'
NOW=datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
DAY=NOW[:10]
STABLE_SHA='d64937b9dc4e528795d3818834a6ddab1828df1af84bb483b16961a40d8286ec'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

assert sha(STABLE)==STABLE_SHA, 'stable baseline changed before beta4 publish'
data=load(BETA)
assert isinstance(data,list) and len(data)==1
s=data[0]
assert s.get('bookSourceUrl')==PERM
assert 'v1.1.0-beta3' in str(s.get('bookSourceComment',''))
init=s['ruleBookInfo']['init']
intro=s['ruleBookInfo']['intro']
assert 'function qdParseBookInfo' in str(s.get('jsLib',''))
assert 'qfMetaListV1103' in init

# Stop broad array-string extraction for tags/honors. It is the source of fragments such as :true / :50001.
old_tags="if(blank(info.tags)){var ts=listScalar(html,['BookTags','bookTags','TagList','tagList']);if(ts.length)info.tags=ts;}"
old_honors="if(blank(info.honors)){var hs=listScalar(html,['HonorList','honorList','Honors','honors']);if(hs.length)info.honors=hs;}"
assert old_tags in init and old_honors in init
visible_helper=r'''
function qfVisibleTagsV1104(html){
  var out=[],seen={};
  function add(v){
    var t=unesc(String(v||'')).replace(/\s+/g,' ').trim(),low=t.toLowerCase();
    var ascii={vip:1,'1v1':1,acg:1,bl:1,gl:1,lol:1,nba:1};
    if(!t||t.length>20||/[:：{}\[\]]/.test(t))return;
    if(!/[\u4e00-\u9fff]/.test(t)&&!ascii[low])return;
    if(/^(?:连载|连载中|完本|已完结|签约|免费|限免|起点中文网|男生|女生)$/i.test(t))return;
    if(!seen[t]){seen[t]=1;out.push(t);}
  }
  try{
    var d=org.jsoup.Jsoup.parse(String(html||''));
    var es=d.select('.book-info .tag a, p.tag a, [class*=book-info] [class*=tag] a, [class*=bookInfo] [class*=tag] a');
    for(var i=0;i<es.size()&&out.length<8;i++)add(es.get(i).text());
  }catch(e){}
  return out;
}
'''
anchor="if(blank(info.recommendCount))info.recommendCount="
assert anchor in init
init=init.replace(anchor,visible_helper+'\n'+anchor,1)
init=init.replace(old_tags,"if(blank(info.tags)){var ts=qfVisibleTagsV1104(html);if(ts.length)info.tags=ts;}",1)
init=init.replace(old_honors,"if(blank(info.honors))info.honors=[];",1)

# Replace beta3 sanitizer with beta4 strict human-text validation + at-most-one official PC detail enrichment.
start=init.index('/* 1.1.0-beta3: semantic cleanup')
end=init.index('info.serverLimitState=',start)
new_block=r'''
/* 1.1.0-beta4: strict visible-text metadata + one-request official enrichment.
 * Current-response parsing remains first. Only sparse detail pages may make ONE request to
 * https://www.qidian.com/book/<bookId>/ and reuse the mature qdParseBookInfo parser.
 * No APP/Atom/third-party detail fallback is allowed here. */
function qfHumanMetaV1104(v,kind){
  var a=Array.isArray(v)?v:String(v||'').split(/\s*[·,，|\/]\s*/),out=[],seen={};
  var ascii={vip:1,'1v1':1,acg:1,bl:1,gl:1,lol:1,nba:1};
  var bad={sectioncount:1,actionstatus:1,fininshed:1,finished:1,finish:1,intro:1,true:1,false:1,null:1,undefined:1,honortypename:1,honorname:1,tagname:1,name:1,id:1,type:1,count:1,status:1,code:1,value:1,list:1,bookid:1,sectionid:1,action:1};
  for(var i=0;i<a.length;i++){
    var t=unesc(String(a[i]||'')).replace(/^[\s'\"【】()（）]+|[\s'\"【】()（）]+$/g,'').replace(/\s+/g,' ').trim();
    if(!t||t.length<2||t.length>24)continue;
    var low=t.toLowerCase();
    if(bad[low]||/[:：{}\[\]]/.test(t))continue;
    if(/^[+-]?\d+(?:\.\d+)?$/.test(t)||/^(?:0x)?[0-9a-f]{8,}$/i.test(t))continue;
    if(!/[\u4e00-\u9fff]/.test(t)&&!ascii[low])continue;
    if(/^(?:字段|状态|类型|数量|时间戳|编号|名称|简介|动作|章节数)$/i.test(t))continue;
    if(kind==='honor'&&/(?:字段|状态|类型|数量|时间戳|编号|名称)$/.test(t))continue;
    if(!seen[t]){seen[t]=1;out.push(t);if(out.length>=8)break;}
  }
  return out;
}
function qfRightsV1104(v){
  var a=Array.isArray(v)?v:String(v||'').split(/\s*[·,，|\/]\s*/),o=[],seen={};
  for(var i=0;i<a.length;i++){
    var t=String(a[i]||'').trim();if(!t)continue;
    if(!/^(?:VIP|限免|限时免费|免费|签约|精品|完本|已完结|连载)$/i.test(t))continue;
    if(!seen[t]){seen[t]=1;o.push(t);}
  }
  return o;
}
function qfMetricBaseV1104(v){
  var s=String(v||'').replace(/,/g,'').trim(),m=s.match(/^(\d+(?:\.\d+)?)(万|亿|千)?$/);if(!m)return 0;
  var n=Number(m[1]);if(!isFinite(n)||n<0)return 0;
  if(m[2]==='千')n*=1000;else if(m[2]==='万')n*=10000;else if(m[2]==='亿')n*=100000000;
  return n;
}
function qfMetricSafeV1104(v){var n=qfMetricBaseV1104(v);return n>0&&n<10000000000?String(v||'').trim():'';}
function qfNormalizeDetailV1104(){
  info.tags=qfHumanMetaV1104(info.tags,'tag');
  info.honors=qfHumanMetaV1104(info.honors,'honor');
  info.authorTags=qfHumanMetaV1104(info.authorTags,'author').join(' · ');
  info.rights=qfRightsV1104(info.rights);
  var st=String(info.status||'').trim();
  if(/^(?:FININSHED|FINISHED|FINISH|COMPLETED|END|完本|已完结)$/i.test(st))info.status='完结';
  else if(/^(?:SERIAL|SERIALIZATION|ONGOING|UPDATING|连载中)$/i.test(st))info.status='连载';
  var lv=String(info.authorLevel||'').trim(),lm=lv.match(/(?:Lv\.?\s*)?(\d{1,2})/i);if(lm)info.authorLevel='Lv.'+lm[1];
  info.recommendCount=qfMetricSafeV1104(info.recommendCount);info.readingCount=qfMetricSafeV1104(info.readingCount);info.monthTicket=qfMetricSafeV1104(info.monthTicket);
  info.collectionCount=qfMetricSafeV1104(info.collectionCount);info.fansCount=qfMetricSafeV1104(info.fansCount);info.leaderCount=qfMetricSafeV1104(info.leaderCount);info.investCount=qfMetricSafeV1104(info.investCount);info.firstSubscribe=qfMetricSafeV1104(info.firstSubscribe);
  var cn=qfMetricBaseV1104(info.collectionCount),fn=qfMetricBaseV1104(info.fansCount);if(cn>0&&fn>=10000&&cn<50)info.collectionCount='';
}
function qfDetailSparseV1104(){
  var a=[info.recommendCount,info.readingCount,info.monthTicket,info.ratingScore,info.collectionCount,info.fansCount,info.leaderCount],n=0;
  for(var i=0;i<a.length;i++)if(String(a[i]||'').trim())n++;
  return n<3||!info.tags||!info.tags.length||!String(info.status||'').trim();
}
function qfFillV1104(k,v){if(blank(info[k])&&!blank(v))info[k]=v;}
function qfDetailPcEnrichV1104(){
  if(!bid||!qfDetailSparseV1104())return;
  var last=Number(bv('qf_detailPcEnrichedAtV1104')||0),now=Date.now();
  if(last>0&&now-last<1800000)return;
  var pcUrl='https://www.qidian.com/book/'+encodeURIComponent(String(bid))+'/',pcHtml='';
  try{
    pcHtml=String(qfAjaxTextV20(this,pcUrl,{timeout:2600,headers:{'User-Agent':(typeof QF_UA!=='undefined'?QF_UA:'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36'),'Referer':'https://www.qidian.com/','Accept':'text/html,application/xhtml+xml'}})||'');
  }catch(e){pcHtml='';}
  try{qfPutBookVarV09.call(this,'qf_detailPcEnrichedAtV1104',String(now));}catch(_ts){}
  if(!pcHtml||pcHtml.length<500)return;
  var rich={};
  try{rich=JSON.parse(String(qdParseBookInfo.call(this,pcHtml,pcUrl)||'{}'));}catch(_rp){rich={};}
  qfFillV1104('authorLevel',rich.authorLevel);qfFillV1104('authorWorksCount',rich.authorWorksCount);qfFillV1104('status',rich.status);
  qfFillV1104('publishDate',rich.publishDate);qfFillV1104('updateTime',rich.updateTime);qfFillV1104('ratingScore',rich.ratingScore);qfFillV1104('ratingCount',rich.ratingCount);
  qfFillV1104('kind',rich.kind);qfFillV1104('subKind',rich.subKind);qfFillV1104('intro',rich.intro);
  var rec=visibleMetric(pcHtml,'总推荐')||rich.recommendCount;if(rec)info.recommendCount=rec;
  var mt=visibleMetric(pcHtml,'月票')||rich.monthTicket;if(mt)info.monthTicket=mt;
  var col=visibleMetric(pcHtml,'收藏');if(col)info.collectionCount=col;
  var fan=visibleMetric(pcHtml,'粉丝');if(fan)info.fansCount=fan;
  var leader=visibleMetric(pcHtml,'盟主');if(leader)info.leaderCount=leader;
  var rt=qfHumanMetaV1104(rich.tags||[],'tag');if(rt.length)info.tags=rt;
  var rr=qfRightsV1104(rich.rights||[]);if(rr.length)info.rights=rr;
  if(rr.indexOf('VIP')>=0)info.isVip=true;
}
qfNormalizeDetailV1104();
qfDetailPcEnrichV1104.call(this);
qfNormalizeDetailV1104();
if(!info.tags.length){
  var fb=[];if(info.subKind)fb.push(info.subKind);else if(info.kind)fb.push(info.kind);if(info.status)fb.push(info.status);if(info.isVip)fb.push('VIP');if(info.isLimitedFree)fb.push('限免');
  info.tags=qfHumanMetaV1104(fb,'tag');
}
'''
init=init[:start]+new_block+'\n'+init[end:]

# Renderer second defence: reject any JSON/value fragment even if an older cache survived.
cs=intro.index('function chips(v,limit,color){')
ce=intro.index('function date',cs)
new_chips=r'''function chips(v,limit,color){
  var a=arr(v),seen={},o=[],ascii={vip:1,'1v1':1,acg:1,bl:1,gl:1,lol:1,nba:1};
  for(var i=0;i<a.length&&o.length<(limit||8);i++){
    var t=clean(a[i]).replace(/^[\s'\"【】()（）]+|[\s'\"【】()（）]+$/g,'').trim(),low=t.toLowerCase();
    if(!t||t.length<2||t.length>24||seen[t])continue;
    if(/[:：{}\[\]]/.test(t)||/^[+-]?\d+(?:\.\d+)?$/.test(t)||/^(?:0x)?[0-9a-f]{8,}$/i.test(t))continue;
    if(!/[\u4e00-\u9fff]/.test(t)&&!ascii[low])continue;
    if(/^(?:sectionCount|actionStatus|FININSHED|FINISHED|intro|true|false|null|undefined|honorTypeName|honorName|tagName|name|id|type|count|status|code|value|list|bookId|sectionId)$/i.test(t))continue;
    seen[t]=1;o.push('<font color="'+(color||'#168f89')+'">【'+esc(t)+'】</font>');
  }
  return o.join(' ');
}
'''
intro=intro[:cs]+new_chips+intro[ce:]
# Show first-publish date when available and distinct from update time.
needle="if(clean(x.updateTime))body+=row('🕒','更新',date(x.updateTime));"
assert needle in intro
intro=intro.replace(needle,needle+"\nif(clean(x.publishDate)&&date(x.publishDate)!==date(x.updateTime))body+=row('🚀','首发',date(x.publishDate));",1)

s['ruleBookInfo']['init']=init
s['ruleBookInfo']['intro']=intro
s['bookSourceComment']='v1.1.0-beta4：详情信息平衡版。标签只接受可见的人类文本，彻底过滤 :true / :50001 等结构碎片；详情过于稀疏时最多补一次起点 PC 官方书页并复用成熟 qdParseBookInfo 解析器，补全评分/推荐/收藏/粉丝/状态/作者等级/标签等可用字段。无 APP/Atom/第三方详情 fallback，保留情无 VIP 正文认证修复及其它搜索/目录/评论/Provider 逻辑。'
s['lastUpdateTime']=int(datetime.now().timestamp()*1000)
s['bookSourceUrl']=PERM
save(BETA,data)
beta_sha=sha(BETA)

# Beta catalog
sub=load(ROOT/'subscription/beta.json')
for it in sub.get('items',[]):
    if it.get('id')=='qidian-next-beta':
        it.update({'name':'🌈 起点增强 · Beta','summary':'详情 beta4：严格修复标签结构碎片；信息稀疏时最多一次起点官方书页补全，兼顾信息量与速度。','channel':'beta','version':VERSION,'updatedAt':DAY,
                   'tags':['起点','测试版','详情页','官方补全','标签修复','性能优化','情无'],
                   'changelog':['标签只接受可见人类文本，过滤 :true / :50001 等对象碎片','详情过稀时最多一次起点 PC 官方书页请求，2.6 秒超时且无第二 fallback','复用成熟 qdParseBookInfo 补全评分/推荐/收藏/粉丝/状态/作者等级/标签','保留情无 VIP 正文认证修复及其它业务模块'],
                   'sourceUrl':RAW,'backupUrl':CDN,'importUrl':'legado://import/importonline?src='+RAW,'detailUrl':'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'})
sub['updatedAt']=NOW
save(ROOT/'subscription/beta.json',sub)

# Beta bundle
bundle=load(ROOT/'bundles/all-beta.json')
arr=bundle if isinstance(bundle,list) else bundle.get('sources',[])
assert isinstance(arr,list)
found=False
for i,it in enumerate(arr):
    if isinstance(it,dict) and (it.get('bookSourceUrl')==PERM or str(it.get('bookSourceName','')).startswith('🌈 起点增强')):
        arr[i]=s;found=True;break
if not found: arr.append(s)
if isinstance(bundle,dict): bundle['sources']=arr
save(ROOT/'bundles/all-beta.json',bundle)

# Manifest
manifest=load(ROOT/'manifest.json')
for it in manifest.get('sources',[]):
    if it.get('id')=='qidian-next-beta':
        it.update({'name':'🌈 起点增强 · Beta','channel':'beta','version':VERSION,'versionCode':VCODE,'updatedAt':NOW,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','sourceUrl':RAW,'bookSourceUrl':PERM,
                   'summary':'详情 beta4：严格标签清洗 + 稀疏详情最多一次起点官方 PC 书页补全。','tags':['起点','测试版','详情页','官方补全','标签修复','性能优化','情无'],
                   'changelog':['修复 :true / :50001 等标签结构碎片','稀疏详情最多单次官方补全','复用成熟 qdParseBookInfo','保留情无 VIP 正文修复'],'sha256':beta_sha})
manifest['updatedAt']=NOW
save(ROOT/'manifest.json',manifest)

# RSS current-state detail
rss=load(ROOT/'rss/data/details/beta/qidian-next.json')
rss.update({'kind':'source','title':'🌈 起点增强 · Beta','summary':'详情 beta4：标签严格只认可见文本；资料不足时最多一次起点官方补全。','badges':['Beta',VERSION,'详情平衡'],
            'sections':[{'title':'标签修复','text':'不再解析泛化数组字符串；标签只接受起点页面可见文本，:true、:50001、状态键、ID 等结构碎片会被直接拒绝。'},
                        {'title':'信息补全','text':'先解析当前响应和缓存；若作品数据仍明显稀疏，最多请求一次起点 PC 官方书页，并复用现有成熟 qdParseBookInfo 解析器补全可靠字段。'},
                        {'title':'性能边界','text':'官方补全单次超时 2.6 秒，30 分钟内不重复探测；不恢复 APP/Atom/第三方多接口串行详情链。'},
                        {'title':'回归范围','text':'仅修改详情解析/展示。搜索、目录、评论、正文 Provider 与情无 VIP 认证链保持不变。'}],
            'sourceUrl':RAW,'backupUrl':CDN,'importUrl':'legado://import/importonline?src='+RAW})
save(ROOT/'rss/data/details/beta/qidian-next.json',rss)

# Docs
handoff=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
h=handoff.read_text(encoding='utf-8')
h+='\n## Detail balance Beta 1.1.0-beta4 (2026-08-26)\n\n- Real-device beta3 confirmed one title could show correct visible tags, while another still leaked structured fragments such as `:true` and `:50001`; works-data density also remained too low.\n- Generic array-string extraction is no longer used for tags/honors. Tags now require visible human text (Chinese or a short explicit ASCII allowlist) and reject JSON/object punctuation, booleans, ids and internal field names.\n- Current response/cache remains first priority. When reliable detail metrics are sparse, the detail path may issue at most one request to `https://www.qidian.com/book/<bookId>/` with a 2.6s timeout and reuse the existing `qdParseBookInfo(html, baseUrl)` parser.\n- There is no second detail fallback and no APP/Atom/third-party enrichment chain. A per-book 30-minute attempt marker prevents repeated slow probes.\n- Stable 1.0.0 and search/catalog/content/review modules remain unchanged.\n'
handoff.write_text(h,encoding='utf-8')

rel=ROOT/'docs/RELEASE_LOG.md'
r=rel.read_text(encoding='utf-8')
r+='\n### 2026-08-26 — 🌈 起点增强 1.1.0-beta4\n- Detail-only Beta: reject structured tag fragments (`:true`, numeric ids, internal keys) and accept only visible human-readable tags.\n- Sparse detail pages may perform one official Qidian PC book-page enrichment request (2.6s timeout) and reuse `qdParseBookInfo`; no secondary fallback.\n- Adds trustworthy missing detail fields when available while keeping Stable 1.0.0 and non-detail domains untouched.\n'
rel.write_text(r,encoding='utf-8')

known=ROOT/'docs/KNOWN_ISSUES.md'
k=known.read_text(encoding='utf-8')
k+='\n## 24. Detail beta3 still leaked structured tag values and remained sparse — addressed in 1.1.0-beta4\n\nReal-device beta3 showed correct tags on some books, but another book displayed fragments such as `:true`, `:50001`, `:0`, `:50005`; both test books exposed only month-ticket data in the custom works-data block. Root cause: generic array-string extraction could return values from structured objects even after field-name filtering, while the zero-extra-request policy had become too restrictive for information density.\n\nBeta4 removes generic tag/honor array extraction, validates human-visible tag text, and conditionally allows exactly one official Qidian PC book-page request parsed by the mature `qdParseBookInfo` routine. No multi-endpoint fallback is restored. Status: Beta, pending real-device confirmation.\n'
known.write_text(k,encoding='utf-8')

# Final gates
assert sha(STABLE)==STABLE_SHA, 'stable changed during beta4 publish'
assert s['bookSourceUrl']==PERM
assert 'v1.1.0-beta4' in s['bookSourceComment']
assert init.count('qfAjaxTextV20(this,pcUrl')==1, 'detail enrichment must contain exactly one network call site'
assert init.count('qdParseBookInfo.call(this,pcHtml,pcUrl)')==1
assert "listScalar(html,['BookTags'" not in init and "listScalar(html,['HonorList'" not in init
for banned in ['qfAtomPost','QidianTu','TuShuJun']:
    assert banned not in init, 'old multi-probe detail path leaked into beta4 init: '+banned
full=BETA.read_text(encoding='utf-8')
for marker in ['X-Content-Token','VIP正文已验证']:
    assert marker in full, 'QW regression gate missing: '+marker
print('published',VERSION,'sha',beta_sha,'init',len(init),'intro',len(intro),'stable',sha(STABLE))
