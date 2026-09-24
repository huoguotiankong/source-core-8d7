import json, hashlib, base64, gzip
from pathlib import Path
from datetime import datetime

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.8-beta1'; VC=12082; TS='2026-09-24T19:55:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

arr=json.loads(STABLE.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
stable=json.loads(json.dumps(s,ensure_ascii=False))

# Parse QF_MOD38_PACK safely.
js=str(s.get('jsLib',''))
mark='var QF_MOD38_PACK='
p=js.find(mark); assert p>=0, 'QF_MOD38_PACK not found'
start=js.find('{',p+len(mark)); assert start>=0
depth=0; quote=''; esc=False; end=-1
for i in range(start,len(js)):
    ch=js[i]
    if quote:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch==quote: quote=''
        continue
    if ch in ('"',"'"):
        quote=ch; continue
    if ch=='{': depth+=1
    elif ch=='}':
        depth-=1
        if depth==0:
            end=i+1; break
assert end>start
pack=json.loads(js[start:end])
old_pack=dict(pack)
raw=pack['preferred_sq']
assert isinstance(raw,str) and raw.startswith('gz:'), 'preferred_sq must be gzip packed'
b64=raw[3:]+'='*(-len(raw[3:])%4)
code=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
old_code=code

def replace_function(src,name,new_text):
    needle='function '+name+'('
    a=src.find(needle)
    assert a>=0, f'{name} not found'
    brace=src.find('{',a)
    assert brace>=0
    depth=0; quote=''; esc=False; end=-1
    for i in range(brace,len(src)):
        ch=src[i]
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=''
            continue
        if ch in ('"',"'",'`'):
            quote=ch; continue
        if ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:
                end=i+1; break
    assert end>brace, f'{name} end not found'
    return src[:a]+new_text.strip()+src[end:]

# Broaden field aliases only; matching itself is deliberately stricter.
code=replace_function(code,'qfSqBookNameV44',r'''function qfSqBookNameV44(x){return qfText(x&&(x.bookName||x.book_name||x.title||x.name||x.resourceName)||"");}''')
code=replace_function(code,'qfSqBookAuthorV44',r'''function qfSqBookAuthorV44(x){return qfText(x&&(x.authorName||x.author_name||x.author||x.writerName||x.writer)||"");}''')

new_norm=r'''function qfSqNormAuthorV44(s){return qfNorm(s).replace(/^(?:作者|作家|原著|作者名)/g,"").replace(/(?:作者|著|所著|作品)$/g,"").trim();}
function qfSqTitleVariantsV48(name){
    var arr=[],seen={};
    function add(v){v=qfNorm(v);if(v&&!seen[v]){seen[v]=1;arr.push(v);}}
    add(name);
    try{var vs=qfNameVariantsV10(name)||[];for(var i=0;i<vs.length;i++)add(vs[i]);}catch(_e){}
    return arr;
}
function qfSqTitleExactV48(candidate,target){
    var c=qfNorm(candidate),vs=qfSqTitleVariantsV48(target);
    if(!c||!vs.length)return false;
    for(var i=0;i<vs.length;i++)if(c===vs[i])return true;
    return false;
}
function qfSqAuthorExactV48(candidate,target){
    var c=qfSqNormAuthorV44(candidate),t=qfSqNormAuthorV44(target);
    return !!(c&&t&&c===t);
}
function qfSqBookStrictV48(x,name,author){
    return !!(x&&qfSqBookIdV44(x)&&qfSqTitleExactV48(qfSqBookNameV44(x),name)&&qfSqAuthorExactV48(qfSqBookAuthorV44(x),author));
}
function qfSqBindValidV48(bind,meta){
    meta=meta||{};bind=bind||{};
    return !!(bind.id&&qfSqTitleExactV48(bind.name,meta.bookName)&&qfSqAuthorExactV48(bind.author,meta.author));
}'''
code=replace_function(code,'qfSqNormAuthorV44',new_norm)

new_pick_book=r'''function qfSqPickBookV44(items,name,author){
    items=qdList(items);
    var best=null,bestScore=-1,target=qfNorm(name);
    for(var i=0;i<items.length;i++){
        var v=items[i]||{};
        if(!qfSqBookStrictV48(v,name,author))continue;
        var score=(qfNorm(qfSqBookNameV44(v))===target?200:120)+(v._web?5:0);
        if(score>bestScore){bestScore=score;best=v;}
    }
    return best;
}'''
code=replace_function(code,'qfSqPickBookV44',new_pick_book)

new_pick_chapter=r'''function qfSqChapterCompatibleV48(x,meta){
    if(!x)return false;meta=meta||{};
    var title=String(x.chapterName||""),target=String(meta.title||""),n=qfNormChapter(title),tn=qfNormChapter(target),b=qfSqChapterBodyV44(title),tb=qfSqChapterBodyV44(target),no=qfChapterNoV10(title),tno=qfChapterNoV10(target);
    if(tno>=0&&no>=0&&no!==tno)return false;
    if(n&&tn&&n===tn)return true;
    if(b&&tb&&b===tb)return true;
    if(b&&tb&&Math.min(b.length,tb.length)>=6&&(b.indexOf(tb)>=0||tb.indexOf(b)>=0))return true;
    return false;
}
function qfSqPickChapterV44(list,meta,bindId){
    list=qdList(list);if(!list.length)return null;meta=meta||{};
    var tag="书旗#"+String(bindId||"strict-v48"),fast=qfChapterHintTryV56(tag,meta,list,"chapterName",true);
    if(fast&&qfSqChapterCompatibleV48(fast,meta))return fast;
    var target=String(meta.title||""),tn=qfNormChapter(target),tb=qfSqChapterBodyV44(target),tno=qfChapterNoV10(target),idx=Number(meta.index),best=null,bestScore=-99999;
    for(var i=0;i<list.length;i++){
        var x=list[i]||{},title=String(x.chapterName||""),n=qfNormChapter(title),b=qfSqChapterBodyV44(title),no=qfChapterNoV10(title),score=-99999;
        if(tno>=0&&no>=0&&no!==tno)continue;
        if(n&&tn&&n===tn)score=2500;
        else if(b&&tb&&b===tb)score=2250;
        else if(b&&tb&&Math.min(b.length,tb.length)>=6&&(b.indexOf(tb)>=0||tb.indexOf(b)>=0))score=1550;
        if(score<0)continue;
        if(tno>=0&&no>=0&&no===tno)score+=520;
        if(idx>=0){var d=Math.abs(i-idx);if(d===0)score+=100;else if(d<=4)score+=50-d*8;}
        if(score>bestScore){bestScore=score;best=x;}
    }
    if(bestScore>=1500){qfChapterHintPutV56(tag,meta,list,best);return best;}
    return null;
}'''
code=replace_function(code,'qfSqPickChapterV44',new_pick_chapter)

new_content=r'''function qfShuqiContentV44(meta){
    meta=meta||{};
    if(!qfText(meta.bookName)||!qfText(meta.author))throw new Error("书旗严格匹配需要完整书名和作者信息");
    var bkey="qf_v48_bind_sq_"+meta.bookId,bind=qfCacheGet.call(this,bkey);
    if(!qfSqBindValidV48(bind,meta))bind=null;
    if(!bind||!bind.id){
        var books=qfSqSearchV44.call(this,meta.bookName,meta.author),hit=qfSqPickBookV44(books,meta.bookName,meta.author);
        if(!hit){
            var web=[];try{web=qfSqWebSearchV46.call(this,meta.bookName,meta.author)||[];}catch(_w){}
            if(web.length){for(var wi=0;wi<web.length;wi++)books.push(web[wi]);hit=qfSqPickBookV44(books,meta.bookName,meta.author);}
        }
        if(!hit){
            var sample=[];
            for(var si=0;si<Math.min(10,books.length);si++)sample.push(qfSqBookNameV44(books[si])+"/"+qfSqBookAuthorV44(books[si])+"#"+qfSqBookIdV44(books[si]));
            throw new Error("书旗未匹配到书名+作者均一致的书籍｜目标["+meta.bookName+"/"+meta.author+"]｜搜索"+books.length+"项"+(sample.length?"："+sample.join(" / "):""));
        }
        bind={id:qfSqBookIdV44(hit),name:qfSqBookNameV44(hit),author:qfSqBookAuthorV44(hit),strictV:48};
        if(!qfSqBindValidV48(bind,meta))throw new Error("书旗候选二次校验失败：["+bind.name+"/"+bind.author+"#"+bind.id+"]");
        qfCachePut.call(this,bkey,bind);
    }
    var providerTag="书旗#"+String(bind.id),wh=qfChapterWindowTryV310.call(this,providerTag,meta,"chapterName",true),cat=null,ch=null;
    if(wh&&wh.chapter&&qfSqChapterCompatibleV48(wh.chapter,meta)){
        var ex=wh.extra||{};ch=wh.chapter;cat={free:String(ex.free||""),charge:String(ex.charge||""),short:String(ex.short||""),list:[],diag:"章节窗口直达/严格校验"};
    }else{
        cat=qfSqCatalogV44.call(this,bind.id,false);ch=qfSqPickChapterV44(cat.list,meta,bind.id);
        if(!ch){cat=qfSqCatalogV44.call(this,bind.id,true);ch=qfSqPickChapterV44(cat.list,meta,bind.id);}
        if(ch)qfChapterWindowPutV310.call(this,providerTag,meta,cat.list,ch,"chapterName",{free:cat.free,charge:cat.charge,short:cat.short});
    }
    if(!ch)throw new Error("书旗已严格匹配本书["+bind.name+"/"+bind.author+"#"+bind.id+"]，但未匹配章节："+meta.title+"｜书旗目录"+((cat&&cat.list&&cat.list.length)||0)+"章｜"+((cat&&cat.diag)||"无目录诊断"));
    var suffix=String(ch.contUrlSuffix||""),free=(ch.isFreeRead===true||String(ch.isFreeRead)==="1"||Number(ch.isFreeRead)===1),prefix=free?cat.free:cat.charge,real=String(prefix||"")+suffix;if(real)real=real.replace(/0$/,"1");var shortUrl=String(cat.short||"")+String(ch.shortContUrlSuffix||""),urls=[],last="";function add(u){u=String(u||"");if(u&&urls.indexOf(u)<0)urls.push(u);}add(real);add(shortUrl);if(/1$/.test(real))add(real.replace(/1$/,"0"));for(var u=0;u<urls.length;u++)try{var r=qfJson(qfJava(this).ajax(urls[u]+","+JSON.stringify({headers:qfSqSearchHeadersV46()})),{}),enc=r&&(r.ChapterContent||r.chapterContent)||"";if(enc){var text=qfSqDecodeV44.call(this,enc);if(qfValidContentV10(text))return text;}last=String(r.message||r.msg||"正文为空");}catch(e0){last=String(e0&&e0.message||e0);}throw new Error("书旗正文获取失败："+(last||"正文为空"));
}'''
code=replace_function(code,'qfShuqiContentV44',new_content)

assert code!=old_code
for marker in ('qfSqBookStrictV48','qfSqBindValidV48','qfSqChapterCompatibleV48','书旗未匹配到书名+作者均一致的书籍','书旗#'):
    assert marker in code, marker

pack['preferred_sq']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
for k,v in old_pack.items():
    if k!='preferred_sq': assert pack.get(k)==v, 'unexpected lazy module change: '+k
pack_text=json.dumps(pack,ensure_ascii=False,separators=(',',':'))
new_js=js[:start]+pack_text+js[end:]
assert js[:start]==new_js[:start]
assert js[end:]==new_js[start+len(pack_text):]
s['jsLib']=new_js
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.8-beta1：仅优化书旗正文 Provider 的书籍/章节匹配。书籍绑定改为书名与作者同时严格命中，旧错误绑定缓存不再复用；章节匹配增加章节号硬校验与绑定 bookId 隔离缓存，低置信度直接失败并交给后续 Provider，避免串书/串章。Stable 1.2.7 的目录、评论、版权、账号与其它 Provider 保持不变。'
try:s['lastUpdateTime']=int(datetime.fromisoformat(TS).timestamp()*1000)
except Exception:pass

# Isolation gates.
for k,v in stable.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment','lastUpdateTime'): continue
    assert s.get(k)==v, 'unexpected stable field changed: '+k
assert s['ruleToc']==stable['ruleToc']
assert s['ruleBookInfo']==stable['ruleBookInfo']
assert s['ruleContent']==stable['ruleContent']
assert s['bookSourceUrl']==stable['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.8-beta1：书旗改为书名+作者双重严格绑定，并强化章节号校验，避免同名异作者串书和错章。'
tags=['起点','测试版','书旗','正文匹配','作者校验','章节匹配','防串书','防串章']
changes=[
 '书旗候选书必须同时通过书名与作者校验；仅书名相同但作者不一致的候选直接拒绝',
 '书旗绑定缓存升级为 v48，并在每次使用前重新校验书名/作者，旧错误绑定不会继续命中',
 '章节匹配增加章节号硬约束：目标和候选都能解析出章节号时，号码不一致直接淘汰',
 '章节 Hint/Window 缓存加入已绑定书旗 bookId，避免更换正确书籍后复用旧书的章节命中',
 '低置信度不强行返回正文，直接让 Provider Runtime 继续后续优选/兜底源；其它业务域冻结'
]

def beta_entry(old=None,typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    return e

# Manifest: keep Stable and upsert active Beta.
mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
mi=m.setdefault('sources',[]); pos=next((i for i,e in enumerate(mi) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
ne=beta_entry(mi[pos] if pos is not None else None); ne['category']='novel'; ne['artifactType']='bookSource'
if pos is None:
    ins=next((i+1 for i,e in enumerate(mi) if isinstance(e,dict) and e.get('id')=='qidian-next'),len(mi)); mi.insert(ins,ne)
else: mi[pos]=ne
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Beta catalog.
bp=ROOT/'subscription/beta.json'; bd=json.loads(bp.read_text(encoding='utf-8')); bd['updatedAt']=TS; bd['generatedAt']=TS
bi=bd.setdefault('items',[]); pos=next((i for i,e in enumerate(bi) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
if pos is None: bi.insert(0,beta_entry())
else: bi[pos]=beta_entry(bi[pos])
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Novel type catalog: current active channel entry only.
np=ROOT/'subscription/novel.json'; nd=json.loads(np.read_text(encoding='utf-8')); nd['updatedAt']=TS; nd['generatedAt']=TS
ni=nd.setdefault('items',[]); ni[:]=[e for e in ni if not (isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'))]; ni.insert(0,beta_entry(typed=True))
np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Beta bundle.
bunp=ROOT/'bundles/all-beta.json'; ba=json.loads(bunp.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr
ba=[o for o in ba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)]; ba.insert(0,src)
bunp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Current-state beta detail.
dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'书旗严格匹配'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'本版范围','text':'只修改书旗正文 Provider 的书籍绑定和章节匹配；Stable 1.2.7 的目录、评论、版权、账号及其它 Provider 冻结。'},
 {'title':'书籍绑定','text':'书旗候选必须书名和作者同时匹配；同名异作者候选直接拒绝。绑定缓存升级并在使用前二次校验，旧错误绑定不会继续复用。'},
 {'title':'章节匹配','text':'当目标章和候选章都能解析章节号时，号码不一致直接淘汰；标题/正文名匹配只在章节号兼容时参与评分。Hint/Window 缓存按书旗 bookId 隔离。'},
 {'title':'失败策略','text':'匹配置信度不足时不返回错误章节，而是让 Provider Runtime 继续尝试后续优选/兜底源。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'
release=(f"## 2026-09-24 · qidian-next {VERSION} — 书旗严格书籍/章节匹配\n"
'- 真机发现固定书旗把《惊悚乐园》（三天两觉）错误绑定为同名但作者为“傀儡先生”的书，随后目录只有1章/番外，导致第079章无法匹配。\n'
'- 书旗候选改为书名+作者双重严格校验；仅书名相同不再允许绑定。\n'
'- 绑定缓存升级为 v48，并在使用前二次校验书名/作者，避免旧错误绑定继续生效。\n'
'- 章节匹配增加章节号硬约束；可解析章节号不一致时直接淘汰，索引距离只作低权重 tie-break。\n'
'- Hint/Window 缓存加入已绑定书旗 bookId，避免换书后复用旧章节命中。低置信度直接失败并交给后续 Provider。\n'
'- 仅 preferred_sq 懒模块变更；Stable 1.2.7 与目录/评论/版权/账号/其它 Provider 不变。\n\n')
rp.write_text(release+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
hand=(f"## 2026-09-24 · {VERSION} — 书旗匹配测试\n\n"
'- 基线：Stable 1.2.7。用户真机发现书旗固定源可把正确书名绑定到错误作者的同名书，继而章节目录完全不对应。\n'
'- 当前 Beta 只修改 `preferred_sq`：书名+作者必须同时匹配；旧绑定缓存升级并二次校验。\n'
'- 章节匹配加入章节号硬约束，Hint/Window 缓存按绑定的书旗 bookId 隔离；低置信度放弃书旗并继续后续 Provider。\n'
'- 重点真机复测：《惊悚乐园》作者“三天两觉”，第079章《校园七不思议（八）》；不得再绑定“傀儡先生#8880120”。\n'- 未经用户真机确认不得晋升 Stable。\n\n')
hp.write_text(hand+hp.read_text(encoding='utf-8'),encoding='utf-8')

report={'version':VERSION,'versionCode':VC,'stableBaseline':'1.2.7','betaSha256':sha,'bookSourceUrlFrozen':s['bookSourceUrl']==stable['bookSourceUrl'],'ruleTocFrozen':s['ruleToc']==stable['ruleToc'],'ruleBookInfoFrozen':s['ruleBookInfo']==stable['ruleBookInfo'],'ruleContentFrozen':s['ruleContent']==stable['ruleContent'],'onlyLazyModuleChanged':'preferred_sq','strictBookMatch':True,'authorRequired':True,'chapterNumberHardGuard':True,'bindingCache':'qf_v48_bind_sq_','chapterCacheScopedByBoundBookId':True}
(ROOT/'.staging/qidian-128b1-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'.staging/qidian-128b1-preferred-sq.js').write_text(code,encoding='utf-8')
print(VERSION,sha)
