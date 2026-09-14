import json, hashlib
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
PHASE=ROOT/'sources/novel/qidian-next/qidian-next-toc-phase-diag.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.4-beta8'; VC=12048; TS='2026-09-14T20:50:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8'))
stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(PHASE.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr

# Keep the user-confirmed working phase-diag request lifecycle exactly.
assert 'qfPdTocUrl' in s.get('jsLib','')
assert 'qfDiagBid' in s['ruleBookInfo']['init']
assert 'qfPdTocUrl.call(this,bid)' in s['ruleBookInfo']['tocUrl']
assert s['ruleContent']==stable['ruleContent']

# Restore the mature Stable row schema (copyright row, volume rows, VIP flags, chapter URL shape),
# but keep the proven direct Argus response and merge direct T/W back into chapter rows.
rule_toc=dict(stable['ruleToc'])
rule_toc['chapterList']="""@js:\nvar root=JSON.parse(String(result||'{}'));\nvar d=(root&&root.Data)?root.Data:{};\nvar bm=String(baseUrl||'').match(/[?&]bookId=(\\d+)/i),bid=bm?bm[1]:'';\nif(!bid)try{bid=String(d.BookId||d.bookId||'');}catch(_b){}\nif(!bid)throw new Error('QF beta8: catalog response has no bookId');\nvar bname='',author='';\ntry{bname=String(book&&book.name||'');author=String(book&&book.author||'');}catch(_ba){}\nvar out=qfTocNormalizeAppV70.call(this,root,bid,bname,author);\nif(!Array.isArray(out)||!out.length)throw new Error('QF beta8: normalized catalog empty');\nvar direct=Array.isArray(d.Chapters)?d.Chapters:(Array.isArray(d.chapters)?d.chapters:[]),imap={};\nfor(var i=0;i<direct.length;i++){\n  var x=direct[i]||{},cid=String(x.C||x.ChapterId||x.chapterId||'').trim();\n  if(!cid)continue;\n  var sj='';\n  if(x.T!==undefined&&x.T!==null&&String(x.T)!==''){try{sj=String(java.timeFormat(x.T)||'');}catch(_t){sj=String(x.T);}}\n  if(x.W!==undefined&&x.W!==null&&String(x.W)!=='')sj+=(sj?' ':'')+String(x.W)+'字';\n  if(sj)imap[cid]=sj;\n}\nfor(var j=0;j<out.length;j++){\n  var r=out[j]||{};if(r.Vo||r.N==='版权信息'||!r.C)continue;\n  var m=String(r.C||'').match(/\\/chapter\\/\\d+\\/(\\d+)/i)||String(r.C||'').match(/[?&#](?:chapterId|cid)=(\\d+)/i);\n  var id=m&&m[1]?String(m[1]):'';if(id&&imap[id])r.T=imap[id];\n}\nout"""
s['ruleToc']=rule_toc
s['bookSourceUrl']=IDENTITY
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.4-beta8：基于已真机确认能加载目录的“目录阶段诊断”直接转入 Beta。保持其 ruleBookInfo.init → tocUrl 执行时机和 Argus v1 QDSign/QDInfo 请求完全不变；目录输出层恢复 Stable 1.2.2 的版权信息、分卷行、VIP 标记和章节 URL 结构，并从当前 Argus Data.Chapters 回填 T + W 时间/字数。正文、评论、账号、搜索、详情主体、情无/小雨及其它 Provider 不变。'

# Isolation: request lifecycle is byte-identical to the working phase diagnostic.
phase_arr=json.loads(PHASE.read_text(encoding='utf-8'))
phase=phase_arr[0] if isinstance(phase_arr,list) else phase_arr
assert s['jsLib']==phase['jsLib']
assert s['ruleBookInfo']==phase['ruleBookInfo']
assert s['ruleContent']==phase['ruleContent']==stable['ruleContent']
assert s['ruleToc']['isVolume']=='Vo'
assert 'qfTocNormalizeAppV70.call(this,root,bid,bname,author)' in s['ruleToc']['chapterList']
assert "x.W" in s['ruleToc']['chapterList']

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.4-beta8：沿用真机已通过的目录阶段请求链，恢复版权信息、分卷目录并保留时间+字数。'
tags=['起点','测试版','目录修复','版权信息','分卷目录','章节字数','Argus v1']
changes=[
 '沿用“目录阶段诊断”已真机确认可用的 ruleBookInfo.init → tocUrl 执行时机，目录请求和签名逻辑不改',
 '目录输出改回 Stable 1.2.2 成熟行结构，恢复版权信息行、分卷行、VIP 标记与原章节 URL 结构',
 '若 Argus 响应包含 Volumes/VolumeList/vs，直接恢复真实分卷；若仅有 Chapters，则保守生成正文卷',
 '继续从 Data.Chapters 的 T/W 回填每章更新时间与官方字数，不增加额外字数请求',
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
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'目录恢复','版权信息','分卷'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'真机基线','text':'目录阶段诊断已确认：目录可以加载，时间与字数正常。beta8 保持该请求生命周期不变。'},
 {'title':'本版补齐','text':'只调整目录结果组织：恢复 Stable 的版权信息行、分卷行、VIP 与章节 URL 结构；章节 T/W 继续从同一 Argus 响应回填。'},
 {'title':'分卷策略','text':'优先使用 Argus 返回的 Volumes / VolumeList / vs；若接口当前只返回扁平 Chapters，则保守显示“正文”卷，不额外切回旧 CatalogService。'},
 {'title':'冻结范围','text':'正文、评论、账号、搜索、详情主体、情无/小雨及其它 Provider 不修改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'
release=(f"## 2026-09-14 · qidian-next {VERSION} — 目录结果层恢复\n"
'- 用户真机确认独立“目录阶段诊断”可以正常显示目录，且章节时间、字数均正常；目录请求时机问题已定位。\n'
'- beta8 直接沿用该诊断源的 `ruleBookInfo.init → tocUrl` 生命周期与 Argus v1 签名请求，不再修改请求层。\n'
'- 仅恢复目录结果层：版权信息、分卷行、VIP 标记、Stable 章节 URL 结构；T/W 继续从同一响应回填。\n'
'- 优先读取 Argus 的 `Volumes/VolumeList/vs`；若只返回 `Chapters`，保守生成“正文”卷，避免重新引入旧 CatalogService。\n'
'- Stable 1.2.2 不变，等待真机确认版权信息、分卷及正文衔接。\n\n')
rp.write_text(release+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
hand=(f"## 2026-09-14 · {VERSION} — 当前活动 Beta\n\n"
'- 真机证据：`qidian-next-toc-phase-diag.json` 目录已正常，时间+字数均正常；缺失项只剩版权信息与分卷目录。\n'
'- 当前 Beta 基线直接使用该诊断源请求生命周期；不得再把 Argus 签名提前回 `ruleBookInfo.init`。\n'
'- beta8 仅替换 `ruleToc` 结果组织：调用 Stable `qfTocNormalizeAppV70` 恢复版权/分卷/VIP/章节 URL，再用当前 `Data.Chapters.T/W` 覆盖章节信息。\n'
'- 若真机只显示“正文”卷而非真实卷名，说明当前 Argus v1 响应没有暴露分卷数组；下一步只为分卷结构增加独立 donor，不动已通过的目录主请求。\n'
'- Stable 仍为 1.2.2，未获得用户确认前不得晋升。\n\n')
hp.write_text(hand+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-124b8-report.json'
report.write_text(json.dumps({'version':VERSION,'phaseDiagSha256':hashlib.sha256(PHASE.read_bytes()).hexdigest(),'betaSha256':sha,'requestLifecycleFrozen':True,'ruleContentFrozen':True,'restored':['copyright','volume rows','vip','stable chapter URL','T+W']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
