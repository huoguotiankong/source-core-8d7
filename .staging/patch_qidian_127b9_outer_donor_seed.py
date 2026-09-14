import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta9'; VC=12079; TS='2026-09-15T00:46:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8')); stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
assert '1.2.7-beta8' in str(s.get('bookSourceComment','')), 'beta8 baseline expected'
js=str(s.get('jsLib','')); old_js=js

# 1) Outer-rule-context donor fetch. This intentionally runs BEFORE showBrowser,
# exactly where 妙想天开 executes qdGetPageWithReplies, rather than inside WebView.
outer=r'''
/* 1.2.7-beta9：妙想天开同执行层评论种子。
 * 关键差异：妙想天开并不是在 WebView 里请求首屏评论，而是在书源规则上下文中先执行
 * qdBuildReq -> java.ajax，再把原始 DataList 注入 showBrowser。前几版虽然复制了参数/签名，
 * 但请求仍发生在 WebView bridge 内。本版把首批/当前段落评论请求搬回规则上下文。
 */
var QF_MIAO_BRANDS_V1279=['realme','OPPO','Xiaomi','vivo','HUAWEI','samsung','Google','HONOR'];
var QF_MIAO_MODELS_V1279=['RMX3366','PHY120','24030PN60C','V2324A','ALN-AL10','SM-S9280','Pixel 4 XL','MAA-AN10'];
var QF_MIAO_RND_V1279=Math.floor(Math.random()*8);
var QF_MIAO_BRAND_V1279=QF_MIAO_BRANDS_V1279[QF_MIAO_RND_V1279];
var QF_MIAO_MODEL_V1279=QF_MIAO_MODELS_V1279[QF_MIAO_RND_V1279];
function qfMiaoPadKeyV1279(k){k=String(k||'');while(k.length<24)k+='\0';return k;}
function qfMiaoPad3V1279(n){n=String(n);while(n.length<3)n='0'+n;return n;}
function qfMiaoHexV1279(n){var s='';for(var i=0;i<n;i++)s+=Math.floor(Math.random()*16).toString(16);return s;}
function qfMiaoDesV1279(data,key,iv){
    var j=this.java;
    if(j&&typeof j.createSymmetricCrypto==='function'){
        var c=j.createSymmetricCrypto('DESede/CBC/PKCS5Padding',String(key),String(iv));
        return String(c.encryptBase64(String(data))||'');
    }
    if(j&&typeof j.tripleDESEncodeBase64Str==='function'){
        return String(j.tripleDESEncodeBase64Str(String(data),String(key),'CBC','PKCS5Padding',String(iv))||'').replace(/[\r\n]/g,'');
    }
    throw new Error('no DESede bridge');
}
function qfMiaoSignByUrlV1279(which,url){
    var qs=String(url||'').split('?')[1]||'',a=qs.split('&').filter(Boolean);a.sort();
    var md5p=String(this.java.md5Encode(a.join('&').toLowerCase())||'');
    var ts=new Date().getTime(),now=new Date(ts+8*3600*1000);
    var ymdhm=now.getUTCFullYear()+qfMiaoPad3V1279(now.getUTCMonth()+1)+qfMiaoPad3V1279(now.getUTCDate())+qfMiaoPad3V1279(now.getUTCHours())+qfMiaoPad3V1279(now.getUTCMinutes());
    var qimei=ymdhm+qfMiaoPad3V1279(ts%1000)+qfMiaoHexV1279(12);
    if(which==='QDSign')return qfMiaoDesV1279.call(this,'Rv1rPTnczce|'+ts+'|0|'+qimei+'||||'+md5p+'|f189adc92b816b3e9da29ea304d4a7e4',qfMiaoPadKeyV1279('{1dYgqE)h9,R)hKqEcv4]k[h'),'01234567');
    if(which==='QDInfo')return qfMiaoDesV1279.call(this,qimei+'|7.9.378|1080|1184|1000009|10|1|'+QF_MIAO_MODEL_V1279+'|1436|1000009|4|0|'+ts+'|1|'+qimei+'|||||0',qfMiaoPadKeyV1279('0821CAAD409B84020821CAAD'),'\0\0\0\0\0\0\0\0');
    if(which==='tstamp')return ts;
    if(which==='UA')return 'Mozilla/mobile QDReaderAndroid/7.9.378/1436/1000009/'+QF_MIAO_BRAND_V1279;
    return '';
}
function qfMiaoBuildReqV1279(url){
    var opt={headers:{
        'QDSign':qfMiaoSignByUrlV1279.call(this,'QDSign',url),
        'QDInfo':qfMiaoSignByUrlV1279.call(this,'QDInfo',url),
        'tstamp':String(qfMiaoSignByUrlV1279.call(this,'tstamp',url)),
        'User-Agent':qfMiaoSignByUrlV1279.call(this,'UA',url),
        'Content-Type':'application/json'
    }};
    return String(url)+','+JSON.stringify(opt);
}
function qfMiaoGroupPageV1279(obj){
    var dl=(obj&&obj.Data&&obj.Data.DataList)||[],main={},subs={},order=[];
    if(!Array.isArray(dl))dl=[];
    for(var i=0;i<dl.length;i++){
        var it=dl[i];if(!it||it.Id==null)continue;
        var id=String(it.Id),rt=Number(it.ReviewType||0),ref=Number(it.RefferCommentId||0),d=it;
        if(ref===0||rt===1||rt===0){if(!main[id])order.push(id);main[id]=d;}
        else if(ref>0&&rt===2){var rk=String(it.RefferCommentId);if(!subs[rk])subs[rk]=[];subs[rk].push(d);}
    }
    for(var k in subs)if(Object.prototype.hasOwnProperty.call(subs,k)&&main[k]){
        main[k].Replies=subs[k];main[k].ReviewCount=Math.max(Number(main[k].ReviewCount||0),subs[k].length);
    }
    var out=[];for(var j=0;j<order.length;j++){var x=main[order[j]];if(!x||!x.UserName||x.UserName==='匿名用户')continue;if(Array.isArray(x.Replies))x.Replies=x.Replies.filter(function(r){return r&&r.UserName&&r.UserName!=='匿名用户';});out.push(x);}
    return out;
}
function qfMiaoOuterSeedV1279(bid,cid,para,expected){
    var total=Math.max(0,Number(expected||0)),want=total>0?Math.ceil(total/10):1,pages=Math.max(1,Math.min(10,want));
    var reqs=[];
    for(var pg=1;pg<=pages;pg++){
        var u='https://druidv6.if.qidian.com/argus/api/v2/chapterreview/getparagraphscomments?anchorId=0&bookId='+bid+'&chapterId='+cid+'&from=0&paragraphId='+para+'&pg='+pg+'&pz=10&type=0';
        reqs.push(qfMiaoBuildReqV1279.call(this,u));
    }
    var texts=[];
    try{
        if(reqs.length>1&&this.java&&typeof this.java.ajaxAll==='function'){
            var rs=this.java.ajaxAll(reqs)||[];
            for(var ri=0;ri<rs.length;ri++){
                var r=rs[ri],t='';try{t=(r&&typeof r.body==='function')?String(r.body()||''):String(r||'');}catch(_rb){}
                texts.push(t);
            }
        }
    }catch(_all){texts=[];}
    if(!texts.length){for(var qi=0;qi<reqs.length;qi++){try{texts.push(String(this.java.ajax(reqs[qi])||''));}catch(_one){texts.push('');}}}
    var list=[],seen={};
    for(var ti=0;ti<texts.length;ti++){
        if(!texts[ti])continue;var d=null;try{d=JSON.parse(texts[ti]);}catch(_j){continue;}
        var a=qfMiaoGroupPageV1279(d);
        for(var ai=0;ai<a.length;ai++){
            var row=a[ai],id=String(row.Id||row.ReviewId||row.CommentId||'');
            var key=id||String(row.UserName||'')+'|'+String(row.Content||'')+'|'+String(row.CreateTime||'');
            if(seen[key])continue;seen[key]=1;list.push(row);
        }
    }
    return {list:list,total:Math.max(total,list.length),pageSize:10,loadedPages:pages,complete:(total>0&&pages>=want),source:'miaoxiang-outer-rule'};
}
'''
anchor='var QF_COMMENT_HTML_CACHE_V2987="";\nfunction qfCommentHtmlV2987(){'
assert anchor in js, 'comment cache anchor missing'
js=js.replace(anchor,'var QF_COMMENT_HTML_CACHE_V2987="";\n'+outer+'\nfunction qfCommentHtmlV2987(){',1)

# Inject outer seed into the comment BottomSheet pre-script. Only real paragraph comments use it.
pre_anchor='''        var pre=\n            "window.java=java;"+\n            "window.__QF_COMMENT_CTX__="+ctxJson+";"+'''
assert pre_anchor in js, 'comment pre anchor missing'
seed_code='''        var qfOuterSeedV1279={list:[],total:0,pageSize:10,loadedPages:0,complete:false,source:''};
        try{
            if(Number(p)>0)qfOuterSeedV1279=qfMiaoOuterSeedV1279.call(this,String(bid),String(cid),String(p),Number(expected||0));
        }catch(_seed1279){}
        var qfOuterSeedJsonV1279='{}';
        try{qfOuterSeedJsonV1279=JSON.stringify(qfOuterSeedV1279).replace(/</g,'\\u003c');}catch(_seedJson1279){qfOuterSeedJsonV1279='{}';}

'''
js=js.replace(pre_anchor,seed_code+'''        var pre=\n            "window.java=java;"+\n            "window.qdOuterSeed="+qfOuterSeedJsonV1279+";"+\n            "window.__QF_COMMENT_CTX__="+ctxJson+";"+''',1)

# 2) Patch lazy review UI: consume outer-rule seed first and use it to repair suspicious reply Content by ID.
mark='var QF_MOD38_PACK='; p=js.find(mark); assert p>=0
start=js.find('{',p+len(mark)); depth=0; quote=''; esc=False; end=-1
for i in range(start,len(js)):
    ch=js[i]
    if quote:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch==quote: quote=''
        continue
    if ch in ('"',"'"): quote=ch; continue
    if ch=='{': depth+=1
    elif ch=='}':
        depth-=1
        if depth==0: end=i+1; break
assert end>start
pack=json.loads(js[start:end]); raw=pack['review_local_ui']; assert raw.startswith('gz:')
code=gzip.decompress(base64.b64decode(raw[3:]+'='*(-len(raw[3:])%4))).decode('utf-8'); old_code=code
assert 'qfReviewCopyReaderContentV1278' in code and '1.2.7-beta8' in code

ctx_anchor="var csrf=String(window.qdCsrf||\"\");\nvar qdCookie=String(window.qdCookie||\"\");"
assert ctx_anchor in code, 'ui context anchor missing'
code=code.replace(ctx_anchor,ctx_anchor+'''\nvar qdOuterSeed=(window.qdOuterSeed&&typeof window.qdOuterSeed==='object')?window.qdOuterSeed:null;
var qdOuterSeedIndex=null;
function qfOuterSeedIndexV1279(){
    if(qdOuterSeedIndex)return qdOuterSeedIndex;
    var map={},seen=[];
    function add(v){
        if(!v||typeof v!=='object')return;
        var ids=[v.Id,v.id,v.ReviewId,v.reviewId,v.CommentId,v.commentId,v.PostId,v.postId];
        for(var i=0;i<ids.length;i++){var k=String(ids[i]==null?'':ids[i]);if(k)map[k]=v;}
        var a=v.Replies||v.replies||v.replyList||v.ReplyList||[];if(Array.isArray(a))for(var j=0;j<a.length;j++)add(a[j]);
    }
    try{var a=qdOuterSeed&&Array.isArray(qdOuterSeed.list)?qdOuterSeed.list:[];for(var i=0;i<a.length;i++)add(a[i]);}catch(_e){}
    qdOuterSeedIndex=map;return map;
}
function qfOuterSeedContentV1279(item,raw){
    try{
        var ids=qfEmojiIdsV1275(item,raw),map=qfOuterSeedIndexV1279();
        for(var i=0;i<ids.length;i++){
            var r=map[ids[i]];if(!r)continue;
            var x=String(textOf(r.Content||r.content||r.ReviewContent||r.reviewContent||r.Body||r.PostBody||r.PostContent||'')||'');
            if(x)return x;
        }
    }catch(_e){}
    return '';
}
function qfOuterSeedPackV1279(p,ps,extra){
    try{
        if(!qdOuterSeed||!Array.isArray(qdOuterSeed.list)||!qdOuterSeed.list.length)return null;
        if(isAuthor||isChapter||currentTab!=='all')return null;
        var pid=Number(extra&&extra.paragraphId!=null?extra.paragraphId:para);if(pid!==Number(para))return null;
        var size=Math.max(1,Number(ps)||10),pg=Math.max(1,Number(p)||1),st=(pg-1)*size,en=st+size;
        var rows=qdOuterSeed.list.slice(st,en),total=Math.max(Number(qdOuterSeed.total||0),qdOuterSeed.list.length);
        if(rows.length)return {data:{},list:rows,total:total,source:'miaoxiang-outer-rule',outerSeed:true};
        if(qdOuterSeed.complete&&st>=qdOuterSeed.list.length)return {data:{},list:[],total:total,source:'miaoxiang-outer-rule',outerSeed:true};
    }catch(_e){}
    return null;
}''',1)

payload_anchor='''    if(qfEmojiSuspiciousV1275(content)){
        var recovered=qfEmojiRecoverContentV1275(item,raw);
        if(recovered)content=recovered;
    }'''
assert payload_anchor in code, 'payload recovery anchor missing'
code=code.replace(payload_anchor,'''    if(qfEmojiSuspiciousV1275(content)){
        var outerRecovered=qfOuterSeedContentV1279(item,raw);
        if(outerRecovered)content=outerRecovered;
    }
    if(qfEmojiSuspiciousV1275(content)){
        var recovered=qfEmojiRecoverContentV1275(item,raw);
        if(recovered)content=recovered;
    }''',1)

fetch_anchor='''function fetchPack(action,p,ps,extra){
    extra=extra||{};
    var richPack=null;'''
assert fetch_anchor in code, 'fetchPack anchor missing'
code=code.replace(fetch_anchor,'''function fetchPack(action,p,ps,extra){
    extra=extra||{};
    var outerPack=qfOuterSeedPackV1279(p,ps,extra);
    if(outerPack)return outerPack;
    var richPack=null;''',1)

assert 'miaoxiang-outer-rule' in js and 'qfMiaoOuterSeedV1279' in js
assert 'qfOuterSeedPackV1279' in code and 'qfOuterSeedContentV1279' in code
assert "safe=safe.replace(/\\[fn=(\\d+)\\]/g" in code
assert code!=old_code
check=ROOT/'.staging/qidian-127b9-review-check.js'; check.write_text(code,encoding='utf-8')
pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]

s['bookSourceName']='🌈 起点增强 · Beta'; s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta9：beta8 真机仍无效后确认架构层差异：妙想天开在 showBrowser 之前、书源规则上下文里执行 qdBuildReq/java.ajax，并把原始 Content 注入页面；我们此前一直在 WebView bridge 内请求。本版精确复制妙想天开的外层签名/加密/请求方式，打开段评前并发预取最多10页当前段落评论作为 qdOuterSeed；评论页优先消费该原始 DataList，并按 ID 用外层 Content 修复楼中楼可疑正文。WebView 原链保留为超出种子/失败兜底。目录、正文、版权、账号、Provider 全部冻结。'

for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta8 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY
BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()

summary='Beta 1.2.7-beta9：把妙想天开的评论请求执行层也复制过来，首批评论在 showBrowser 前由书源规则上下文预取并注入。'
tags=['起点','测试版','评论优化','表情修复','妙想天开外层请求','规则上下文预取','原始Content','官方标签','Stable 1.2.6基线']
changes=[
 'beta8 真机仍有方框，确认继续在 WebView bridge 内复制签名并不等价于妙想天开的实现',
 '妙想天开实际是在 showBrowser 前由书源规则上下文执行 createSymmetricCrypto + qdBuildReq + java.ajax；beta9 精确复制该执行层',
 '当前段落按官方 pz=10 并发预取最多10页，原始 DataList 作为 qdOuterSeed 注入评论页；页面优先消费外层数据',
 '可疑楼中楼按评论 ID 优先从 qdOuterSeed 恢复 Content；超出预取范围或外层失败时仍回退原 WebView 请求链',
 '目录、正文、版权、账号、Provider 与 Stable 业务字段冻结'
]
def beta_entry(old=None,typed=False):
    e=dict(old or {});e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    return e
mp=ROOT/'manifest.json';m=json.loads(mp.read_text(encoding='utf-8'));m['updatedAt']=TS;items=m.setdefault('sources',[]);pos=next((i for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None);ne=beta_entry(items[pos] if pos is not None else None);ne['category']='novel';ne['artifactType']='bookSource';items[pos]=ne if pos is not None else ne
if pos is None: items.insert(0,ne)
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bp=ROOT/'subscription/beta.json';bd=json.loads(bp.read_text(encoding='utf-8'));bd['updatedAt']=TS;bd['generatedAt']=TS;bi=bd.setdefault('items',[]);pos=next((i for i,e in enumerate(bi) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None);(bi.insert(0,beta_entry()) if pos is None else bi.__setitem__(pos,beta_entry(bi[pos])));bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
np=ROOT/'subscription/novel.json';nd=json.loads(np.read_text(encoding='utf-8'));nd['updatedAt']=TS;nd['generatedAt']=TS;ni=[e for e in nd.get('items',[]) if not (isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'))];ni.insert(0,beta_entry(typed=True));nd['items']=ni;np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bunp=ROOT/'bundles/all-beta.json';ba=json.loads(bunp.read_text(encoding='utf-8'));src=arr[0] if isinstance(arr,list) else arr;ba=[o for o in ba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)];ba.insert(0,src);bunp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json';detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'妙想天开外层请求'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[{'title':'根因方向','text':'妙想天开首屏评论请求发生在书源规则上下文，而不是 showBrowser WebView 内。前几版只复制协议参数，没有复制执行层。'},{'title':'本版','text':'showBrowser 前精确使用妙想天开的 createSymmetricCrypto/qdBuildReq/java.ajax 语义预取当前段落原始 DataList，再注入现有评论 UI。'},{'title':'兼容','text':'现有 WebView 评论链保留为外层预取失败或超出预取范围时的兜底。'}]};dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

logp=ROOT/'docs/RELEASE_LOG.md';log=logp.read_text(encoding='utf-8');entry='''## 2026-09-15 · qidian-next 1.2.7-beta9\n- beta8 真机仍有方框，确认妙想天开与当前实现最大的剩余差异是请求执行层：妙想天开在 showBrowser 前的书源规则上下文请求评论。\n- 新增外层 donor seed：精确使用妙想天开的 DESede/createSymmetricCrypto、qdBuildReq 和 java.ajax 语义，pz=10，并发预取当前段落最多10页。\n- 评论页优先消费外层原始 DataList；可疑回复按 ID 优先从 seed 恢复 Content；原 WebView 链仅作兜底。\n- 其它业务域冻结。\n\n''';
if entry.splitlines()[0] not in log: logp.write_text(entry+log,encoding='utf-8')
hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md';hand=hp.read_text(encoding='utf-8');block='''\n\n## 2026-09-15 · 1.2.7-beta9 评论执行层对齐\n- beta8 真机仍无效。重新对照妙想天开确认其 `showQdCmt()` 会先在书源规则上下文执行 `fetchQdCmtData -> qdGetPageWithReplies -> qdBuildReq -> java.ajax`，然后把结果注入 Browser；而 qidian-next 旧架构把首屏请求放在 Browser/WebView 内。\n- beta9 新增 outer donor seed，评论页优先使用该原始 DataList，现有 WebView 链作为兜底。\n- 这是当前表情问题首次对“执行层”而不只是签名字段进行对齐。\n''';
if '1.2.7-beta9 评论执行层对齐' not in hand: hp.write_text(hand.rstrip()+block+'\n',encoding='utf-8')
report={'version':VERSION,'versionCode':VC,'sha256':sha,'baseline':'1.2.7-beta8','rootCauseDirection':'Miaoxiang fetches comments in outer Legado rule context before showBrowser; qidian-next fetched inside WebView','changes':['outer donor exact crypto/sign/request','inject qdOuterSeed','UI prioritizes seed and recovers suspicious reply Content by ID'],'frozen':['ruleToc','ruleBookInfo','ruleContent','bookSourceUrl','copyright','providers']}
(ROOT/'.staging/qidian-127b9-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
