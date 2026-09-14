import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta5'; VC=12075; TS='2026-09-14T23:08:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8')); stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
assert '1.2.7-beta4' in str(s.get('bookSourceComment','')), 'beta4 baseline expected'
js=str(s.get('jsLib',''))
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
b64=raw[3:]+'='*(-len(raw[3:])%4)
code=gzip.decompress(base64.b64decode(b64)).decode('utf-8'); old_code=code
assert 'qfEmojiRawCacheV1275' not in code
assert 'qfDirectSignedRequest' in code and 'qfDirectAjax' in code
assert 'getparagraphscomments' in code

helper=r'''
/* 1.2.7-beta5：损坏表情原始 Content 定点恢复。
 * 真机确认部分评论在进入 UI 前，[fn=N] 已被替换为 ☒/�/PUA 字符。
 * 不猜方框对应哪个表情；仅对可疑行按评论 ID 回查官方 Argus v2 原始 DataList，
 * 恢复 Content 后继续交给既有妙想天开同款 [fn=N] 映射。 */
var qfEmojiRawCacheV1275={};
function qfEmojiSuspiciousV1275(s){return /[\u2612\uFFFD\uE000-\uF8FF]/.test(String(s||''))}
function qfEmojiIdsV1275(item,raw){
    var out=[],seen={};
    function take(o){
        if(!o||typeof o!=='object')return;
        var ks=['Id','id','ReviewId','reviewId','CommentId','commentId','SourceId','sourceId','RootReviewId','rootReviewId','PostId','postId'];
        for(var i=0;i<ks.length;i++){
            var v=o[ks[i]];
            if(v!==undefined&&v!==null&&String(v)!==''){
                var k=String(v);if(!seen[k]){seen[k]=1;out.push(k)}
            }
        }
    }
    take(item);take(raw);return out;
}
function qfEmojiRawTextV1275(r){
    if(!r||typeof r!=='object')return '';
    return String(textOf(r.Content||r.content||r.ReviewContent||r.reviewContent||r.Body||r.PostBody||r.PostContent||'')||'');
}
function qfEmojiOfficialPageV1275(){
    var p=String(isAuthor?authorParagraphId:((qfUiContext&&qfUiContext.paragraphId)||para)||'');
    var pg=String(page||1),key=[String(bid),String(cid),p,pg].join('|');
    if(Object.prototype.hasOwnProperty.call(qfEmojiRawCacheV1275,key))return qfEmojiRawCacheV1275[key];
    var map={};
    try{
        var req=qfDirectSignedRequest('v2/chapterreview/getparagraphscomments',{
            anchorId:'0',bookId:String(bid),chapterId:String(cid),from:'0',paragraphId:p,pg:pg,pz:'10',type:'0'
        },false);
        var obj=parse(qfDirectAjax(req,2500)||'');
        var rows=(obj&&obj.Data&&Array.isArray(obj.Data.DataList))?obj.Data.DataList:[];
        if(!rows.length){try{rows=qfDirectCollectRows(obj)||[]}catch(_rows){rows=[]}}
        function indexRow(r){
            if(!r||typeof r!=='object')return;
            var ids=qfEmojiIdsV1275(r,r);
            for(var i=0;i<ids.length;i++)map[ids[i]]=r;
            var nests=[r.Replies,r.replies,r.replyList,r.ReplyList];
            for(var n=0;n<nests.length;n++){
                var a=nests[n];if(!Array.isArray(a))continue;
                for(var j=0;j<a.length;j++)indexRow(a[j]);
            }
        }
        for(var i=0;i<rows.length;i++)indexRow(rows[i]);
    }catch(_e){}
    qfEmojiRawCacheV1275[key]=map;return map;
}
function qfEmojiRecoverContentV1275(item,raw){
    try{
        var ids=qfEmojiIdsV1275(item,raw),map=qfEmojiOfficialPageV1275();
        for(var i=0;i<ids.length;i++){
            var r=map[ids[i]];if(!r)continue;
            var x=qfEmojiRawTextV1275(r);if(!x)continue;
            if(/\[fn=\d+\]/i.test(x))return x;
            if(!qfEmojiSuspiciousV1275(x))return x;
        }
    }catch(_e){}
    return '';
}
'''

fn='function qfReviewUiPayloadBase(item,raw){'
pos=code.find(fn); assert pos>=0
code=code[:pos]+helper+'\n'+code[pos:]
pos=code.find(fn,pos+len(helper))
brace=code.find('{',pos); depth=0; quote=''; esc=False; fend=-1
for i in range(brace,len(code)):
    ch=code[i]
    if quote:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch==quote: quote=''
        continue
    if ch in ('"',"'",'`'): quote=ch; continue
    if ch=='{': depth+=1
    elif ch=='}':
        depth-=1
        if depth==0: fend=i+1; break
assert fend>brace
new_fn=r'''function qfReviewUiPayloadBase(item,raw){
    item=item||{};raw=raw||item;
    var content=String(
        textOf(
            raw.Content||raw.content||
            raw.ReviewContent||raw.reviewContent||
            raw.Body||raw.PostBody||raw.PostContent||
            item.text||item.content||
            raw.Subject||raw.Title
        )||""
    );
    if(qfEmojiSuspiciousV1275(content)){
        var recovered=qfEmojiRecoverContentV1275(item,raw);
        if(recovered)content=recovered;
    }
    return {
        content:content,
        image:qfCommentImageV504(raw),
        audio:String(raw._qfAudioUrl||audioOf(raw)||""),
        audioPage:String(raw._qfAudioPage||""),
        audioDetected:!!raw._qfAudioDetected,
        audioDuration:saneAudioDuration(raw._qfAudioDuration)||audioDurationOf(raw)||0,
        audioPath:String(raw._qfAudioPath||audioPathOf(raw,raw._qfAudioUrl||audioOf(raw))||""),
        audioDiag:String(raw._qfAudioDiag||rawAudioDiag(raw)||"")
    };
}'''
code=code[:pos]+new_fn+code[fend:]

assert code!=old_code
assert 'qfEmojiSuspiciousV1275' in code and 'qfEmojiRecoverContentV1275' in code
assert "'v2/chapterreview/getparagraphscomments'" in code
assert "from:'0'" in code and "pz:'10'" in code and "type:'0'" in code
assert 'autoLoadBudget=0' in code and '600' in code
assert 'qfOfficialBadge' in code and 'qfEmojiHtmlV1272' in code and 'avatarFallback' in code
check=ROOT/'.staging/qidian-127b5-review-check.js'; check.write_text(code,encoding='utf-8')

pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta5：修复评论表情在进入 UI 前已变成方框的问题。检测 ☒/�/PUA 后，仅按评论 ID 通过现有官方 Argus v2 签名链回查原始 Content，再执行妙想天开同款 [fn=N] 映射；不猜方框对应表情。每上下文/页仅回查一次并缓存。目录/正文/版权/账号/Provider 及评论正常行全部冻结。'

for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta4 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY
BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.7-beta5：对已变成方框的评论按 ID 回查起点官方原始 Content，再恢复 [fn=N] 表情。'
tags=['起点','测试版','评论优化','表情修复','Argus原始Content','ID回查','妙想天开参考','官方标签','10条首屏','滚动分页','Stable 1.2.6基线']
changes=[
 '真机确认 beta4 仍有 ☒ 方框：说明 [fn=N] 在进入 UI 前已损坏，单纯 formatter 映射无法恢复',
 '仅当评论含 U+2612/U+FFFD/PUA 可疑字符时，通过现有 Argus v2 签名链回查 getparagraphscomments 原始 DataList',
 '回查结果仅按 Id/ReviewId/CommentId/SourceId/RootReviewId/PostId 精确匹配，不做正文模糊猜测',
 '恢复官方 Content 后继续使用妙想天开同款 [fn=N] 映射；每上下文/页只请求一次并缓存',
 '正常评论不增加请求；目录、正文、版权、账号、Provider 与 Stable 业务字段冻结'
]
def beta_entry(old=None,typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    return e

mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
items=m.setdefault('sources',[]); q=next((i for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
ne=beta_entry(items[q] if q is not None else None); ne['category']='novel'; ne['artifactType']='bookSource'
if q is None: items.insert(next((i+1 for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next'),len(items)),ne)
else: items[q]=ne
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bp=ROOT/'subscription/beta.json'; bd=json.loads(bp.read_text(encoding='utf-8')); bd['updatedAt']=TS; bd['generatedAt']=TS
bi=bd.setdefault('items',[]); q=next((i for i,e in enumerate(bi) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
if q is None: bi.insert(0,beta_entry())
else: bi[q]=beta_entry(bi[q])
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

np=ROOT/'subscription/novel.json'; nd=json.loads(np.read_text(encoding='utf-8')); nd['updatedAt']=TS; nd['generatedAt']=TS
ni=[e for e in nd.get('items',[]) if not (isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'))]
ni.insert(0,beta_entry(typed=True)); nd['items']=ni
np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bunp=ROOT/'bundles/all-beta.json'; ba=json.loads(bunp.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr
ba=[o for o in ba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)]; ba.insert(0,src)
bunp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'表情原始Content恢复'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'根因','text':'beta4 真机仍显示方框，说明部分评论的 [fn=N] 在进入评论 UI 之前已经被替换成占位字符，formatter 已无法知道原表情编号。'},
 {'title':'本版修复','text':'只对含 ☒/�/PUA 的异常评论，按评论 ID 回查起点官方 Argus v2 原始 Content；取回 [fn=N] 后再执行既有 Emoji 映射。'},
 {'title':'请求控制','text':'正常评论零额外请求；异常评论按上下文/页共享一次回查并缓存，不做模糊正文匹配。'},
 {'title':'冻结项','text':'目录、正文、版权、账号、Provider 与其他评论结构保持不变。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'; rp.write_text((f"## 2026-09-14 · qidian-next {VERSION}\n- 真机确认 beta4 仍出现 `☒`：`[fn=N]` 在 UI formatter 前已损坏。\n- beta5 仅对可疑评论按 ID 回查官方 Argus v2 原始 `Content`，再执行 `[fn=N]` 映射；禁止根据方框猜表情。\n- 同上下文/页共享一次回查缓存，正常行不增加网络请求。\n- 目录、正文、版权、账号、Provider 冻结；未经真机确认不得晋升 Stable。\n\n")+rp.read_text(encoding='utf-8'),encoding='utf-8')
hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hp.write_text((f"## 2026-09-14 · {VERSION} — 评论表情原始 Content 定点恢复\n\n- beta4 真机仍有 `☒`，证实不是 Emoji 映射表缺失，而是部分评论在 UI 前已丢失 `[fn=N]`。\n- beta5 对 U+2612/U+FFFD/PUA 异常行，通过现有 Argus 签名链按评论 ID 精确回查 `v2/chapterreview/getparagraphscomments` 原始 DataList。\n- 只恢复 Content；TitleInfoList、头像、楼中楼结构、分页与其它业务域不变。\n\n")+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-127b5-report.json'; report.write_text(json.dumps({
 'version':VERSION,'versionCode':VC,'betaSha256':sha,'baseline':'1.2.7-beta4 / Stable 1.2.6',
 'directRawContentRecovery':True,'endpoint':'v2/chapterreview/getparagraphscomments','requestFrom':'0','pageSize':10,'type':'0',
 'triggerCodepoints':'U+2612/U+FFFD/PUA','matchStrategy':'ID aliases only','cacheStrategy':'one signed request per context/page',
 'reference':'妙想天开 qdGetPageWithReplies + replaceEmoji','normalRowsExtraRequest':False,'fuzzyMatching':False,
 'officialTitleImagePreserved':True,'avatarFallbackPreserved':True,'firstPageStrict10Preserved':True,'backgroundPrefetchPages':0,'scrollThresholdPx':600,
 'syntaxGate':'node --check','ruleTocFrozen':True,'ruleBookInfoFrozen':True,'ruleContentFrozen':True,'bookSourceUrlFrozen':True
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
