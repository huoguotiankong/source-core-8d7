import json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT=Path('.')
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
PERM='https://m.qidian.com/?qf_source=qidian_next_8d7'
VERSION='1.1.0-beta3'
VCODE=11003
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VCODE}'
CDN=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VCODE}'
NOW=datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
DAY=NOW[:10]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

stable_before=sha(STABLE)
data=load(BETA)
assert isinstance(data,list) and len(data)==1
s=data[0]
assert s.get('bookSourceUrl')==PERM
assert 'v1.1.0-beta2' in str(s.get('bookSourceComment',''))
init=s['ruleBookInfo']['init']
intro=s['ruleBookInfo']['intro']
assert '.ajax(' not in init and 'qfOfficialCallV400' not in init and 'qfAtomPost' not in init

# 1) Stop using generic collection/fans fields that can match unrelated nested object counters.
init=init.replace(
"if(blank(info.collectionCount))info.collectionCount=visibleMetric(html,'收藏')||scalar(html,['CollectionCount','collectionCount','CollectCount','collectCount']);",
"var qfCollectionVisibleV1103=visibleMetric(html,'收藏');if(qfCollectionVisibleV1103)info.collectionCount=qfCollectionVisibleV1103;else info.collectionCount='';")
init=init.replace(
"if(blank(info.fansCount))info.fansCount=visibleMetric(html,'粉丝')||scalar(html,['FansCount','fansCount','BookFansCount','bookFansCount']);",
"var qfFansDirectV1103=visibleMetric(html,'粉丝')||scalar(html,['BookFansCount','bookFansCount']);if(qfFansDirectV1103)info.fansCount=qfFansDirectV1103;")

marker="cached('tags','qf_tags',true);cached('rights','qf_rights',true);cached('honors','qf_honors',true);cached('isVip','qf_isVip',false);"
assert marker in init
clean_js=r'''
/* 1.1.0-beta3: semantic cleanup for detail metadata. The mobile Qidian page contains
 * internal state objects beside visible labels. Do not expose object keys, enums, ids,
 * booleans or timestamps as tags/honors. */
function qfMetaListV1103(v,kind){
  var a=Array.isArray(v)?v:String(v||'').split(/\s*[·,，|\/]\s*/),out=[],seen={};
  var bad={sectioncount:1,actionstatus:1,fininshed:1,finished:1,finish:1,intro:1,true:1,false:1,null:1,undefined:1,honortypename:1,honorname:1,tagname:1,name:1,id:1,type:1,count:1,status:1,code:1,value:1,list:1,bookid:1,sectionid:1,action:1};
  var asciiAllow={vip:1,'1v1':1,acg:1,bl:1,gl:1,lol:1,nba:1};
  for(var i=0;i<a.length;i++){
    var t=unesc(String(a[i]||'')).replace(/^[\s\[【{(]+|[\s\]】})]+$/g,'').replace(/^['\"]+|['\"]+$/g,'').replace(/\s+/g,' ').trim();
    if(!t||t.length>28)continue;
    var low=t.toLowerCase();
    if(bad[low])continue;
    if(/^[+-]?\d+(?:\.\d+)?$/.test(t))continue;
    if(/^(?:0x)?[0-9a-f]{8,}$/i.test(t))continue;
    if(/^[\[\]{}():;,!.]+$/.test(t)||/[{}\[\]]/.test(t))continue;
    if(/^[A-Za-z_][A-Za-z0-9_]{2,40}$/.test(t)&&!asciiAllow[low])continue;
    if(kind==='honor'&&!/[\u4e00-\u9fff]/.test(t))continue;
    if(kind==='honor'&&/(?:字段|状态|类型|数量|时间戳|编号)$/.test(t))continue;
    if(!seen[t]){seen[t]=1;out.push(t);if(out.length>=8)break;}
  }
  return out;
}
function qfRightsV1103(v){
  var a=Array.isArray(v)?v:String(v||'').split(/\s*[·,，|\/]\s*/),o=[],seen={};
  for(var i=0;i<a.length;i++){var t=String(a[i]||'').trim();if(!t)continue;if(!/(?:VIP|限免|限时免费|免费|签约|精品|完本|连载)/i.test(t))continue;if(!seen[t]){seen[t]=1;o.push(t);}}
  return o;
}
function qfMetricBaseV1103(v){
  var s=String(v||'').replace(/,/g,'').trim(),m=s.match(/^(\d+(?:\.\d+)?)(万|亿|千)?$/);if(!m)return 0;
  var n=Number(m[1]);if(!isFinite(n)||n<0)return 0;if(m[2]==='千')n*=1000;else if(m[2]==='万')n*=10000;else if(m[2]==='亿')n*=100000000;return n;
}
function qfMetricSafeV1103(v){var n=qfMetricBaseV1103(v);return n>0&&n<10000000000?String(v||'').trim():'';}
info.tags=qfMetaListV1103(info.tags,'tag');
info.honors=qfMetaListV1103(info.honors,'honor');
info.authorTags=qfMetaListV1103(info.authorTags,'author').join(' · ');
info.rights=qfRightsV1103(info.rights);
var qfStV1103=String(info.status||'').trim();
if(/^(?:FININSHED|FINISHED|FINISH|COMPLETED|END)$/i.test(qfStV1103))info.status='完结';
else if(/^(?:SERIAL|SERIALIZATION|ONGOING|UPDATING)$/i.test(qfStV1103))info.status='连载';
var qfLvV1103=String(info.authorLevel||'').trim(),qfLmV1103=qfLvV1103.match(/(?:Lv\.?\s*)?(\d{1,2})/i);if(qfLmV1103)info.authorLevel='Lv.'+qfLmV1103[1];
info.recommendCount=qfMetricSafeV1103(info.recommendCount);info.readingCount=qfMetricSafeV1103(info.readingCount);info.monthTicket=qfMetricSafeV1103(info.monthTicket);
info.collectionCount=qfMetricSafeV1103(info.collectionCount);info.fansCount=qfMetricSafeV1103(info.fansCount);info.leaderCount=qfMetricSafeV1103(info.leaderCount);info.investCount=qfMetricSafeV1103(info.investCount);info.firstSubscribe=qfMetricSafeV1103(info.firstSubscribe);
/* An isolated tiny collection number alongside a very large fan base is usually a nested object count, not the book collection metric. */
var qfCnV1103=qfMetricBaseV1103(info.collectionCount),qfFnV1103=qfMetricBaseV1103(info.fansCount);if(qfCnV1103>0&&qfFnV1103>=10000&&qfCnV1103<50)info.collectionCount='';
if(!info.tags.length){var qfTbV1103=[];if(info.subKind)qfTbV1103.push(info.subKind);else if(info.kind)qfTbV1103.push(info.kind);if(info.status)qfTbV1103.push(info.status);if(info.isVip)qfTbV1103.push('VIP');if(info.isLimitedFree)qfTbV1103.push('限免');info.tags=qfMetaListV1103(qfTbV1103,'tag');}
'''
init=init.replace(marker,marker+'\n'+clean_js,1)

# Renderer-side second defence: old polluted per-book cache must never leak into UI.
new_chips=r'''function chips(v,limit,color){
  var a=arr(v),seen={},o=[],bad=/^(?:sectionCount|actionStatus|FININSHED|FINISHED|intro|true|false|null|undefined|honorTypeName|honorName|tagName|name|id|type|count|status|code|value|list|bookId|sectionId)$/i;
  for(var i=0;i<a.length&&o.length<(limit||8);i++){
    var t=clean(a[i]).replace(/^[\s\[【{(]+|[\s\]】})]+$/g,'');if(!t||seen[t]||t.length>28)continue;
    if(bad.test(t)||/^[+-]?\d+(?:\.\d+)?$/.test(t)||/^(?:0x)?[0-9a-f]{8,}$/i.test(t)||/[{}\[\]]/.test(t))continue;
    if(/^[A-Za-z_][A-Za-z0-9_]{2,40}$/.test(t)&&!/^(?:VIP|1V1|ACG|BL|GL|LOL|NBA)$/i.test(t))continue;
    seen[t]=1;o.push('<font color="'+(color||'#168f89')+'">【'+esc(t)+'】</font>');
  }
  return o.join(' ');
}'''
intro2,n=re.subn(r"function chips\(v,limit,color\)\{[\s\S]*?\}\nfunction date",new_chips+'\nfunction date',intro,count=1)
assert n==1, 'chips renderer not patched'
intro=intro2
intro=intro.replace("var author=clean(x.author),level=clean(x.authorLevel),works=clean(x.authorWorksCount),type=clean(x.subKind)||clean(x.kind),status=clean(x.status);",
"var author=clean(x.author),level=clean(x.authorLevel),works=clean(x.authorWorksCount),type=clean(x.subKind)||clean(x.kind),status=clean(x.status);if(/^\\d{1,2}$/.test(level))level='Lv.'+level;else if(/^Lv\\d+/i.test(level))level=level.replace(/^Lv/i,'Lv.');")
intro=qin=intro.replace("if(tg||hon||at){body+='<br><br><b><font color=\"#9a72c7\">▍标签与荣誉</font></b>';if(tg)body+='<br><br>'+tg;if(at)body+='<br>作者：'+at;if(hon)body+='<br>🏆 '+hon;}",
"if(tg||hon||at){body+='<br><br><b><font color=\"#9a72c7\">'+(hon?'▍标签与荣誉':'▍作品标签')+'</font></b>';if(tg)body+='<br><br>'+tg;if(at)body+='<br>作者：'+at;if(hon)body+='<br>🏆 '+hon;}")

s['ruleBookInfo']['init']=init
s['ruleBookInfo']['intro']=intro
s['bookSourceComment']='v1.1.0-beta3：详情数据清洗专项。保持 beta2 的零额外同步请求快速首屏，修复标签/荣誉把 sectionCount、actionStatus、FININSHED、honorTypeName、ID/时间戳等内部字段当成可见信息的问题；收紧收藏/粉丝等统计可信度并规范作者等级/连载状态显示。保留情无 VIP 正文认证修复及其它搜索/目录/评论/Provider 逻辑。'
s['lastUpdateTime']=int(datetime.now().timestamp()*1000)
s['bookSourceUrl']=PERM
save(BETA,data)

# Distribution metadata
sub=load(ROOT/'subscription/beta.json')
for it in sub.get('items',[]):
    if it.get('id')=='qidian-next-beta':
        it.update({'name':'🌈 起点增强 · Beta','summary':'详情 beta3：清理标签/荣誉内部字段泄漏并收紧统计值可信度；保持首屏零额外同步请求。','channel':'beta','version':VERSION,'updatedAt':DAY,
                   'tags':['起点','测试版','详情页','数据清洗','性能优化','情无','多正文 Provider'],
                   'changelog':['过滤标签/荣誉中的字段名、枚举、ID、布尔值、时间戳等内部数据','收藏/粉丝等统计改用更可信的显示/明确字段并增加合理性校验','作者等级统一为 Lv.x，FINISHED 等状态映射为中文','保持详情首屏零额外同步请求及情无 VIP 正文修复'],
                   'sourceUrl':RAW,'backupUrl':CDN,'importUrl':'legado://import/importonline?src='+RAW,'detailUrl':'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'})
sub['updatedAt']=NOW
save(ROOT/'subscription/beta.json',sub)

bundle=load(ROOT/'bundles/all-beta.json')
arr=bundle if isinstance(bundle,list) else bundle.get('sources',[])
assert isinstance(arr,list)
replaced=False
for i,it in enumerate(arr):
    if isinstance(it,dict) and (it.get('bookSourceUrl')==PERM or str(it.get('bookSourceName','')).startswith('🌈 起点增强')):
        arr[i]=s;replaced=True;break
if not replaced: arr.append(s)
if isinstance(bundle,dict): bundle['sources']=arr
save(ROOT/'bundles/all-beta.json',bundle)

manifest=load(ROOT/'manifest.json')
for it in manifest.get('sources',[]):
    if it.get('id')=='qidian-next-beta':
        it.update({'name':'🌈 起点增强 · Beta','channel':'beta','version':VERSION,'versionCode':VCODE,'updatedAt':NOW,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','sourceUrl':RAW,'bookSourceUrl':PERM,
                   'summary':'详情 beta3：修复标签/荣誉脏数据与统计误识别，保持快速首屏。','tags':['起点','测试版','详情页','数据清洗','性能优化','情无'],
                   'changelog':['清理内部字段/枚举/ID 泄漏','收紧统计可信度','规范作者等级与状态显示','保留零额外请求快速路径']})
manifest['updatedAt']=NOW
save(ROOT/'manifest.json',manifest)

rss=load(ROOT/'rss/data/details/beta/qidian-next.json')
rss.update({'kind':'source','title':'🌈 起点增强 · Beta','summary':'详情 beta3：修复标签/荣誉脏数据和统计误识别，首屏性能路径不回退。','badges':['Beta',VERSION,'详情清洗'],
            'sections':[{'title':'本次修复','text':'过滤 sectionCount、actionStatus、FININSHED、honorTypeName、ID、布尔值、时间戳等起点内部结构字段，避免作为标签/荣誉显示。'},
                        {'title':'统计可信度','text':'收藏优先只接受页面可见值；粉丝优先使用可见值或明确 BookFansCount 字段，并增加极端比例校验。'},
                        {'title':'性能边界','text':'继续保持详情首屏零额外同步网络请求，缺失数据宁可隐藏，也不为补一个数字阻塞详情页。'}],
            'sourceUrl':RAW,'backupUrl':CDN})
save(ROOT/'rss/data/details/beta/qidian-next.json',rss)

beta_sha=sha(BETA)
manifest=load(ROOT/'manifest.json')
for it in manifest.get('sources',[]):
    if it.get('id')=='qidian-next-beta': it['sha256']=beta_sha
save(ROOT/'manifest.json',manifest)

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md';h=hp.read_text(encoding='utf-8')
block='''\n## Detail semantic cleanup Beta 1.1.0-beta3 (2026-08-26)\n\n- Real-device beta2 exposed internal Qidian object keys/enums (`sectionCount`, `actionStatus`, `FININSHED`, `honorTypeName`) and numeric ids/timestamps as visible tags/honors.\n- Add parser-side and renderer-side metadata sanitation; cached polluted values are also blocked at render time.\n- Collection/fan metrics use stricter trust rules; an isolated tiny collection count beside a huge fan base is suppressed as likely nested-object noise.\n- Normalize author level to `Lv.x` and common internal finished/serial states to Chinese display values.\n- Keep the zero-extra-request detail first-paint invariant.\n'''
if '## Detail semantic cleanup Beta 1.1.0-beta3' not in h: hp.write_text(h.rstrip()+block+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md';r=rp.read_text(encoding='utf-8')
rel=f'''## 2026-08-26 — 起点增强 {VERSION}\n\nStatus: Beta/Test; detail metadata sanitation awaiting real-device confirmation.\n\nChanges:\n\n- Block internal object keys/enums/ids/timestamps from tag and honor rendering.\n- Tighten collection/fan metric trust and normalize author-level/status display.\n- Keep zero extra synchronous detail requests and preserve the QW VIP-content fix.\n- Stable 1.0.0 remains unchanged.\n- Beta SHA256: `{beta_sha}`.\n\n'''
if f'## 2026-08-26 — 起点增强 {VERSION}' not in r:
    r='# RELEASE LOG\n\n'+rel+r.split('# RELEASE LOG\n\n',1)[1] if r.startswith('# RELEASE LOG\n\n') else rel+r
    rp.write_text(r,encoding='utf-8')

kp=ROOT/'docs/KNOWN_ISSUES.md';k=kp.read_text(encoding='utf-8')
issue='''\n## 23. Detail beta2 exposed internal Qidian object fields as tags/honors — fixed in 1.1.0-beta3\n\nSymptom: real device displayed tokens such as `sectionCount`, `actionStatus`, `FININSHED`, `honorTypeName`, booleans, ids and timestamps under 标签与荣誉; a generic nested counter could also appear as 收藏.\n\nCause: broad array/string extraction treated object keys and machine values as user-facing labels; ambiguous generic metric fields were accepted without enough context.\n\nBeta fix: parser-side semantic sanitation plus renderer-side defence, stricter collection/fan trust, and status/author-level normalization. No additional first-paint network requests are added.\n\nStatus: Beta 1.1.0-beta3 published for real-device confirmation.\n'''
if '## 23. Detail beta2 exposed internal Qidian object fields' not in k: kp.write_text(k.rstrip()+issue+'\n',encoding='utf-8')

assert sha(STABLE)==stable_before, 'Stable source changed'
final=BETA.read_text(encoding='utf-8')
for marker2 in ['X-Content-Token','VIP正文已验证','qfMetaListV1103','qfMetricBaseV1103']:
    assert marker2 in final, 'regression gate missing: '+marker2
assert '.ajax(' not in init and 'qfOfficialCallV400' not in init and 'qfAtomPost' not in init
print('published',VERSION,beta_sha,'init',len(init),'intro',len(intro),'stable',stable_before)
