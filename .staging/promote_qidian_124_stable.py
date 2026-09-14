import json, hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.4'; VC=12040; TS='2026-09-14T21:00:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/stable/qidian-next.json'

old_arr=json.loads(STABLE.read_text(encoding='utf-8'))
old=old_arr[0] if isinstance(old_arr,list) else old_arr
beta_arr=json.loads(BETA.read_text(encoding='utf-8'))
beta=beta_arr[0] if isinstance(beta_arr,list) else beta_arr

# Promote the user-confirmed beta10 runtime exactly. Only stable display metadata is rewritten.
new=json.loads(json.dumps(beta,ensure_ascii=False))
new['bookSourceName']=old.get('bookSourceName','🌈 起点增强')
new['bookSourceGroup']=old.get('bookSourceGroup',new.get('bookSourceGroup',''))
new['bookSourceUrl']=IDENTITY
new['bookSourceComment']='v1.2.4 Stable：由用户真机确认的 1.2.4-beta10 直接晋升。目录参考起点X-QD，采用自包含 N/C/P/V/Vo/T 扁平目录结构；已确认目录可加载，并恢复章节时间、字数、真实分卷和版权信息。目录请求继续沿用已验证的 Argus v1 + QDSign/QDInfo 执行时机；正文、评论、账号、搜索、详情主体、情无/小雨及其它 Provider 保持原稳定功能链。'
try:
    new['lastUpdateTime']=int(datetime.fromisoformat(TS).timestamp()*1000)
except Exception:
    pass

# Runtime gate: no business rule may differ from beta10.
for k,v in beta.items():
    if k in ('bookSourceName','bookSourceGroup','bookSourceComment','lastUpdateTime'): continue
    assert new.get(k)==v, 'runtime changed during promotion: '+k
assert new['jsLib']==beta['jsLib']
assert new['ruleBookInfo']==beta['ruleBookInfo']
assert new['ruleToc']==beta['ruleToc']
assert new['ruleContent']==beta['ruleContent']
assert new['bookSourceUrl']==beta['bookSourceUrl']==IDENTITY

out_arr=[new] if isinstance(beta_arr,list) else new
STABLE.write_text(json.dumps(out_arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(STABLE.read_bytes()).hexdigest()
beta_sha=hashlib.sha256(BETA.read_bytes()).hexdigest()

summary='正式版 1.2.4：由真机确认的 1.2.4-beta10 直接晋升；目录恢复并支持时间、字数、分卷和版权信息。'
tags=['起点','正式版','目录修复','X-QD参考','分卷目录','版权信息','章节字数','Argus v1','限免源','情无','小雨用户系统','评论页','段评','书友圈','本章说']
changes=[
 '由用户真机确认的 1.2.4-beta10 直接晋升 Stable，不新增业务逻辑',
 '目录采用自包含 N/C/P/V/Vo/T 扁平行，不再在 ruleToc 中调用旧大型目录转换模块',
 '保留已验证的 Argus v1 + QDSign/QDInfo 目录请求时机，章节显示更新时间 + 官方字数',
 '恢复真实分卷与版权信息目录项',
 '正文、评论、账号、搜索、详情主体、情无/小雨及其它 Provider 保持原功能链'
]

def stable_entry(old_entry=None, typed=False):
    e=dict(old_entry or {})
    e.update({'id':'qidian-next','name':'🌈 起点增强','summary':summary,'channel':'stable','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    e.pop('artifactType',None)
    return e

# manifest: replace stable item, remove active beta duplicate.
mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
new_sources=[]; found=False
for e in m.get('sources',[]):
    if not isinstance(e,dict):
        new_sources.append(e); continue
    if e.get('id')=='qidian-next-beta':
        continue
    if e.get('id')=='qidian-next':
        ne=stable_entry(e); ne['category']='novel'; ne['artifactType']='bookSource'; new_sources.append(ne); found=True
    else:
        new_sources.append(e)
if not found:
    ne=stable_entry(); ne['category']='novel'; ne['artifactType']='bookSource'; new_sources.insert(0,ne)
m['sources']=new_sources
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# stable catalog upsert.
sp=ROOT/'subscription/stable.json'; sd=json.loads(sp.read_text(encoding='utf-8')); sd['updatedAt']=TS; sd['generatedAt']=TS
found=False
for i,e in enumerate(sd.get('items',[])):
    if isinstance(e,dict) and e.get('id')=='qidian-next': sd['items'][i]=stable_entry(e); found=True; break
if not found: sd.setdefault('items',[]).insert(0,stable_entry())
sp.write_text(json.dumps(sd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# beta catalog: promoted source is no longer active beta.
bp=ROOT/'subscription/beta.json'; bd=json.loads(bp.read_text(encoding='utf-8')); bd['updatedAt']=TS; bd['generatedAt']=TS
bd['items']=[e for e in bd.get('items',[]) if not (isinstance(e,dict) and e.get('id')=='qidian-next-beta')]
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# novel type catalog: one active logical source, now stable.
np=ROOT/'subscription/novel.json'; nd=json.loads(np.read_text(encoding='utf-8')); nd['updatedAt']=TS; nd['generatedAt']=TS
items=[]; inserted=False
for e in nd.get('items',[]):
    if isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'):
        if not inserted:
            items.append(stable_entry(e,True)); inserted=True
        continue
    items.append(e)
if not inserted: items.insert(0,stable_entry(None,True))
nd['items']=items
np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# stable bundle replace same identity; beta bundle remove promoted logical source.
sbp=ROOT/'bundles/all-stable.json'; sba=json.loads(sbp.read_text(encoding='utf-8')); replaced=False
for i,o in enumerate(sba):
    if isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY:
        sba[i]=new; replaced=True; break
if not replaced:sba.insert(0,new)
sbp.write_text(json.dumps(sba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bbp=ROOT/'bundles/all-beta.json'; bba=json.loads(bbp.read_text(encoding='utf-8'))
bba=[o for o in bba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)]
bbp.write_text(json.dumps(bba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Stable current-state detail.
dp=ROOT/'rss/data/details/stable/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强','summary':summary,'badges':['Stable',VERSION,'目录恢复','分卷','版权信息','章节字数'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'当前正式版','text':'1.2.4 由用户真机确认的 1.2.4-beta10 原业务逻辑晋升，不新增功能改动。'},
 {'title':'目录','text':'目录采用参考起点X-QD的轻量扁平结构 N/C/P/V/Vo/T；保留已验证 Argus v1 + QDSign/QDInfo 请求时机，支持章节时间、字数、真实分卷与版权信息。'},
 {'title':'其它功能','text':'正文、评论、账号、搜索、详情主体、情无/小雨和其它 Provider 沿用既有稳定功能链。'},
 {'title':'发布状态','text':'已完成真机确认并晋升 Stable；活动 Beta 条目已从测试目录和 Beta Bundle 移除，Beta 物理文件保留作历史开发基线。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'
release=(f"## 2026-09-14 · qidian-next Stable {VERSION}\n"
'- 用户真机确认 `1.2.4-beta10` 目录已恢复正常，并明确要求晋升正式版。\n'
'- Stable 直接沿用 beta10 业务运行代码：参考起点X-QD，以自包含 `N/C/P/V/Vo/T` 扁平结构输出目录，不再调用旧大型目录转换模块。\n'
'- 已确认支持章节时间、字数、真实分卷和版权信息；保留已通过的 Argus v1 + QDSign/QDInfo 目录请求时机。\n'
'- 正文、评论、账号、搜索、详情主体、情无/小雨及其它 Provider 不新增改动。\n'
'- 发布同步完成 Stable Source / Manifest / Stable Subscription / Novel Catalog / Stable Bundle / Stable Detail；活动 Beta 条目与 Beta Bundle 中的同逻辑源已移除，Beta 物理文件保留作历史基线。\n\n')
rp.write_text(release+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
hand=(f"## 2026-09-14 · Stable {VERSION} — 当前正式基线\n\n"
'- 用户真机确认 `1.2.4-beta10` 可正常加载目录，并明确要求晋升正式版。\n'
'- 当前目录基线：Argus v1 + QDSign/QDInfo 请求时机沿用已通过的目录阶段方案；ruleToc 自包含输出 `N/C/P/V/Vo/T`，支持时间、字数、分卷和版权信息。\n'
'- 禁止重新接回 `qfTocNormalizeAppV70` 或旧 `CatalogService` 作为目录主链，除非后续有新的真机证据。\n'
'- Stable 1.2.4 为后续开发基线；新的未确认改动重新进入独立 Beta 文件。\n\n')
hp.write_text(hand+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-124-stable-report.json'
report.write_text(json.dumps({'version':VERSION,'versionCode':VC,'promotedFrom':'1.2.4-beta10','betaSha256':beta_sha,'stableSha256':sha,'runtimeEqualToBeta10':True,'stableIdentity':IDENTITY,'betaCatalogRemoved':True,'betaBundleRemoved':True,'stableCatalogUpdated':True,'novelCatalogUpdated':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
