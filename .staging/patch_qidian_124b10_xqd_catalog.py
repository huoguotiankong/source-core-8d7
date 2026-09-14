import json, hashlib
from pathlib import Path

ROOT=Path('.')
PHASE=ROOT/'sources/novel/qidian-next/qidian-next-toc-phase-diag.json'
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.4-beta10'; VC=120410; TS='2026-09-14T20:44:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

arr=json.loads(PHASE.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
phase=json.loads(json.dumps(s,ensure_ascii=False))
stable_arr=json.loads(STABLE.read_text(encoding='utf-8'))
stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr

# Keep the user-confirmed working request lifecycle exactly.
assert 'qfPdTocUrl' in s.get('jsLib','')
assert 'qfDiagBid' in s['ruleBookInfo']['init']
assert 'qfPdTocUrl.call(this,bid)' in s['ruleBookInfo']['tocUrl']
assert s['ruleContent']==stable['ruleContent']

# X-QD lesson: ruleToc should consume/produce a flat N/C/P/V/Vo/T row list directly.
# Do not call qfTocNormalizeAppV70 or any lazy catalog module from this execution phase.
s['ruleToc']={
  'chapterList':'''@js:\nvar root=JSON.parse(String(result||'{}'));\nvar d=(root&&root.Data)?root.Data:{};\nvar bm=String(baseUrl||'').match(/[?&]bookId=(\\d+)/i),bid=bm?bm[1]:'';\nif(!bid)try{bid=String(d.BookId||d.bookId||'');}catch(_bid){}\nif(!bid)throw new Error('QF beta10: catalog response has no bookId');\nvar bname='',author='';\ntry{bname=String(book&&book.name||'');author=String(book&&book.author||'');}catch(_book){}\nfunction A(v){return Array.isArray(v)?v:[];}\nfunction V(o,ks,def){o=o||{};for(var i=0;i<ks.length;i++){var k=ks[i];if(o[k]!==undefined&&o[k]!==null&&String(o[k])!=='')return o[k];}return def;}\nfunction E(v){return encodeURIComponent(String(v==null?'':v));}\nfunction FT(v){if(v===undefined||v===null||String(v)==='')return '';try{return String(java.timeFormat(v)||'');}catch(e){return String(v);}}\nfunction FI(c){var tm=FT(V(c,['T','t','uT','UT','time','Time','PublishTime','publishTime','UpdateTime','updateTime'],'')||'');var w=V(c,['W','w','cnt','Cnt','CNT','cW','CW','wC','WC','wordCount','WordCount','chapterWordCount','ChapterWordCount'],'');var z='';if(tm)z=tm;if(w!==undefined&&w!==null&&String(w)!=='')z+=(z?' ':'')+String(w)+'字';return z;}\nfunction VIP(c){var x=V(c,['V','v','vip','Vip','isVip','IsVip','P','p','isPay','IsPay'],0);return (x===true||String(x)==='1'||String(x).toLowerCase()==='true');}\nfunction CU(cid,title,vip,idx){return 'https://www.qidian.com/chapter/'+E(bid)+'/'+E(cid)+'/?qfVip='+(vip?'1':'0')+'&qfTitle='+E(title)+'&qfBook='+E(bname)+'&qfAuthor='+E(author)+'&qfTocSrc=xqd-flat& qfIndex='+String(idx);}\nfunction CR(){return 'https://m.qidian.com/book/'+E(bid)+'/?qfType=copyright&qfBook='+E(bname)+'&qfAuthor='+E(author)+'&qfCv=3101';}\nvar out=[{N:'版权信息',C:CR(),P:false,V:false,Vo:false,T:''}],idx=0,lastVol='';\nvar vols=A(d.Volumes||d.volumes||d.VolumeList||d.volumeList||d.vs),flat=A(d.Chapters||d.chapters||d.ChapterList||d.chapterList);\nvar vmap={},vranges=[],sum=0;\nfor(var vi=0;vi<vols.length;vi++){var vo=vols[vi]||{},code=String(V(vo,['VolumeCode','volumeCode','VCode','vCode','Code','code','Id','id'],'')||''),name=String(V(vo,['VolumeName','volumeName','VName','vN','VN','Name','name'],'')||'').trim(),cnt=Number(V(vo,['ChapterCount','chapterCount','cCnt','CCnt','Count','count'],0)||0);if(code&&name)vmap[code]=name;if(name&&cnt>0){vranges.push({name:name,start:sum,end:sum+cnt});sum+=cnt;}}\nfunction ADDVOL(name){name=String(name||'').trim();if(name&&name!==lastVol){out.push({N:name,C:'',P:false,V:false,Vo:true,T:''});lastVol=name;}}\nfunction ADDCH(c,forcedVol){c=c||{};var cid=String(V(c,['C','c','ChapterId','chapterId','chapterID','id','Id','cId','cid'],'')||'').trim(),title=String(V(c,['N','n','ChapterName','chapterName','cN','CN','name','Name','title','Title'],'')||'').trim();if(!cid||!title||title.indexOf('版权信息')!==-1)return;var vc=String(V(c,['Vc','VC','VolumeCode','volumeCode','VCode','vCode','VolumeId','volumeId'],'')||''),vn=String(forcedVol||vmap[vc]||V(c,['VolumeName','volumeName','VName','vN','VN'],'')||'').trim();if(!vn&&vranges.length){for(var r=0;r<vranges.length;r++){if(idx>=vranges[r].start&&idx<vranges[r].end){vn=vranges[r].name;break;}}}ADDVOL(vn);var vip=VIP(c);out.push({N:title,C:CU(cid,title,vip,idx),P:vip,V:vip,Vo:false,T:FI(c)});idx++;}\nif(flat.length){for(var ci=0;ci<flat.length;ci++)ADDCH(flat[ci],'');}\nelse if(vols.length){for(var vi2=0;vi2<vols.length;vi2++){var vo2=vols[vi2]||{},vn2=String(V(vo2,['VolumeName','volumeName','VName','vN','VN','Name','name'],'')||'').trim(),cs=A(vo2.Chapters||vo2.chapters||vo2.ChapterList||vo2.chapterList||vo2.cs||vo2.Cs);for(var cj=0;cj<cs.length;cj++)ADDCH(cs[cj],vn2);}}\nif(idx===0)throw new Error('QF beta10: no chapter rows');\nout''',
  'chapterName':'N','chapterUrl':'C','isPay':'P','isVip':'V','isVolume':'Vo','nextTocUrl':'','updateTime':'T'
}

# Fix an accidental whitespace in qfIndex parameter without involving any helper module.
s['ruleToc']['chapterList']=s['ruleToc']['chapterList'].replace("+'&qfTocSrc=xqd-flat& qfIndex='+", "+'&qfTocSrc=xqd-flat&qfIndex='+")

s['bookSourceUrl']=IDENTITY
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.4-beta10：参考“起点X-QD”的目录设计重写结果层。保留已真机通过的目录阶段 Argus v1 请求时机与 QDSign/QDInfo，不再调用 qfTocNormalizeAppV70 / 旧 CatalogService；ruleToc 自己直接产出 X-QD 风格 N/C/P/V/Vo/T 扁平行。章节时间+字数来自 T/W；分卷优先使用 Data.Volumes + Chapter.Vc；版权信息使用 qidian-next 原有版权入口。正文、评论、账号、搜索、详情与 Provider 不变。'

# Isolation gates: only ruleToc and display identity differ from the proven phase diagnostic.
for k,v in phase.items():
    if k in ('ruleToc','bookSourceUrl','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v, 'unexpected runtime difference from phase diag: '+k
assert s['jsLib']==phase['jsLib']
assert s['ruleBookInfo']==phase['ruleBookInfo']
assert s['ruleContent']==phase['ruleContent']==stable['ruleContent']
assert 'qfTocNormalizeAppV70' not in s['ruleToc']['chapterList']
assert "N:'版权信息'" in s['ruleToc']['chapterList']
assert "Vo:true" in s['ruleToc']['chapterList']
assert "['W','w','cnt'" in s['ruleToc']['chapterList']
assert s['ruleToc']['isVolume']=='Vo' and s['ruleToc']['updateTime']=='T'

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.4-beta10：参考起点X-QD，目录改为自包含 N/C/P/V/Vo/T 扁平行，恢复时间字数/分卷/版权信息且不调用旧目录模块。'
tags=['起点','测试版','目录修复','X-QD参考','分卷目录','版权信息','章节字数','Argus v1']
changes=[
 '参考起点X-QD：目录规则只消费当前响应并直接输出 N/C/P/V/Vo/T 行，不在 ruleToc 中调用大型旧目录转换模块',
 '保留已经真机通过的目录阶段 Argus v1 请求时机与 QDSign/QDInfo 签名链，jsLib/ruleBookInfo 不改',
 '章节信息直接用 T + W；分卷优先按 Data.Volumes.VolumeCode 与 Chapter.Vc 对应，兼容嵌套 Volumes 结构',
 '首行恢复版权信息，沿用 qidian-next 已有 qfType=copyright 内容入口，不引入第三方正文/目录服务器',
 '正文、评论、账号、搜索、详情主体、情无/小雨与其它 Provider 全部冻结'
]

def entry(old,typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json'})
    if typed:e['type']='novel'
    return e

mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS; ok=False
for i,e in enumerate(m.get('sources',[])):
    if isinstance(e,dict) and e.get('id')=='qidian-next-beta':
        ne=entry(e); ne['category']='novel'; ne['artifactType']='bookSource'; ne['bookSourceUrl']=IDENTITY; m['sources'][i]=ne; ok=True; break
assert ok
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

for path,typed in [(ROOT/'subscription/beta.json',False),(ROOT/'subscription/novel.json',True)]:
    d0=json.loads(path.read_text(encoding='utf-8')); d0['updatedAt']=TS; d0['generatedAt']=TS; ok=False
    for i,e in enumerate(d0.get('items',[])):
        if isinstance(e,dict) and e.get('id')=='qidian-next-beta': d0['items'][i]=entry(e,typed); ok=True; break
    assert ok, str(path)
    path.write_text(json.dumps(d0,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bp=ROOT/'bundles/all-beta.json'; ba=json.loads(bp.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr; ok=False
for i,o in enumerate(ba):
    if isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY: ba[i]=src; ok=True; break
if not ok:ba.insert(0,src)
bp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'X-QD目录结构','分卷/版权'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'参考结论','text':'起点X-QD 的 ruleToc 很薄：catalog.php 已返回 N/C/P/V/Vo/T 完整行，阅读只按字段消费。beta10 按这个思路把 qidian-next 的目录结果层改成自包含扁平行。'},
 {'title':'为什么不同于 beta8','text':'beta8 在 ruleToc 阶段调用 qfTocNormalizeAppV70，可能依赖未在该阶段加载的 lazy 目录模块。beta10 完全不调用这些函数，只用当前 Argus JSON 和原生 JS。'},
 {'title':'版权与分卷','text':'版权信息首行直接构造 qidian-next 原 qfType=copyright 入口；分卷优先使用 Data.Volumes 与章节 Vc/VolumeCode 映射，时间字数继续用 T/W。'},
 {'title':'冻结范围','text':'正文、评论、账号、搜索、详情主体及所有正文 Provider 不修改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'
release=(f"## 2026-09-14 · qidian-next {VERSION} — X-QD 风格自包含目录结果层\n"
'- 用户提供 `起点X-QD` 作为参考：其目录规则直接消费服务端已整理好的 `N/C/P/V/Vo/T` 行，分卷与版权信息都作为普通目录行返回。\n'
'- beta10 保留已真机通过的“目录阶段诊断” Argus v1 请求生命周期与签名链；不再调用 `qfTocNormalizeAppV70` 或旧 CatalogService。\n'
'- `ruleToc` 自包含构造版权信息、分卷、章节行；章节 T/W 直接形成时间+字数，分卷优先按 `Data.Volumes.VolumeCode` ↔ `Chapter.Vc` 映射。\n'
'- 版权信息沿用 qidian-next 原 `qfType=copyright` 内容入口；不依赖 X-QD 的服务器。\n'
'- Stable 1.2.2 不变，等待真机确认目录、分卷、版权信息与正文衔接。\n\n')
rp.write_text(release+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
hand=(f"## 2026-09-14 · {VERSION} — 当前活动 Beta：X-QD 风格目录\n\n"
'- 新参考源 `起点X-QD` 的关键不是复杂 Legado 目录解析，而是把目录先整理成 `N/C/P/V/Vo/T` 扁平行再交给阅读。\n'
'- beta10 从已真机通过的 `qidian-next-toc-phase-diag.json` 出发，只重写 `ruleToc`；`jsLib`、`ruleBookInfo`、`ruleContent` 与通过版保持一致。\n'
'- 禁止在该路径重新调用 `qfTocNormalizeAppV70`/旧 CatalogService；它们在 beta8 的当前执行阶段导致目录再次失败。\n'
'- 分卷：优先 `Data.Volumes.VolumeCode` ↔ `Chapter.Vc`，兼容嵌套 volume.chapters；版权：首行手工构造旧 qfType=copyright URL；章节：T/W 直接输出时间+字数。\n'
'- 未经真机确认不得晋升 Stable。\n\n')
hp.write_text(hand+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-124b10-report.json'
report.write_text(json.dumps({'version':VERSION,'phaseDiagSha256':hashlib.sha256(PHASE.read_bytes()).hexdigest(),'betaSha256':sha,'requestLifecycleFrozen':True,'ruleContentFrozen':True,'ruleTocSelfContained':True,'usesLegacyNormalizer':False,'rowSchema':['N','C','P','V','Vo','T'],'features':['copyright','volumes','time','wordCount']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
