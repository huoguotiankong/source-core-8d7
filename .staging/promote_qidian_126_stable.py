import json, hashlib
from pathlib import Path
from datetime import datetime

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.6'; VC=12060; TS='2026-09-14T21:55:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/stable/qidian-next.json'

old_arr=json.loads(STABLE.read_text(encoding='utf-8'))
old=old_arr[0] if isinstance(old_arr,list) else old_arr
beta_arr=json.loads(BETA.read_text(encoding='utf-8'))
beta=beta_arr[0] if isinstance(beta_arr,list) else beta_arr

# User-confirmed 1.2.6-beta1 -> Stable. Runtime is copied exactly; only stable display metadata changes.
new=json.loads(json.dumps(beta,ensure_ascii=False))
new['bookSourceName']=old.get('bookSourceName','🌈 起点增强')
new['bookSourceGroup']=old.get('bookSourceGroup',new.get('bookSourceGroup',''))
new['bookSourceUrl']=IDENTITY
new['bookSourceComment']='v1.2.6 Stable：由用户真机确认的 1.2.6-beta1 直接晋升。保留 Stable 1.2.4 已确认的 Argus v1 目录主链、章节时间/字数/真实分卷和版权信息；版权页沿用 1.2.5-beta3 紧凑固定版式；评论页参考妙想天开，首屏 10 条、后续分页，并在官方 v2 结构明确时启用快速组织，同时保留 TitleInfoList 身份称号、头像、时间/IP、点赞、配图、配音、楼中楼和回复分页。正文、账号、搜索、情无/小雨及其它 Provider 保持既有稳定链。'
try:new['lastUpdateTime']=int(datetime.fromisoformat(TS).timestamp()*1000)
except Exception:pass

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
sha=hashlib.sha256(STABLE.read_bytes()).hexdigest(); beta_sha=hashlib.sha256(BETA.read_bytes()).hexdigest()

summary='正式版 1.2.6：真机确认评论功能正常；合并紧凑版权页与妙想天开参考评论优化。'
tags=['起点','正式版','目录','章节字数','分卷','版权信息','段评','本章说','楼中楼','10条分页','TitleInfoList','配图','配音','情无','小雨用户系统']
changes=[
 '由用户真机确认的 1.2.6-beta1 直接晋升 Stable，不新增业务逻辑',
 '目录继续使用已确认的 Argus v1 + QDSign/QDInfo 与轻量 N/C/P/V/Vo/T 输出，支持时间、字数、真实分卷和版权信息',
 '版权页沿用 1.2.5-beta3 紧凑固定版式',
 '评论页参考妙想天开：首屏 10 条、后续分页；官方 v2 结构明确时走快速组织，否则保留成熟 Web/mobile 骨架链',
 '保留真实 TitleInfoList 身份标签、头像、时间/IP、点赞、配图、配音、楼中楼与回复分页；正文/账号/Provider 不变'
]

def stable_entry(old_entry=None,typed=False):
    e=dict(old_entry or {})
    e.update({'id':'qidian-next','name':'🌈 起点增强','summary':summary,'channel':'stable','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    e.pop('artifactType',None)
    return e

mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
new_sources=[]; found=False
for e in m.get('sources',[]):
    if not isinstance(e,dict): new_sources.append(e); continue
    if e.get('id')=='qidian-next-beta': continue
    if e.get('id')=='qidian-next':
        ne=stable_entry(e); ne['category']='novel'; ne['artifactType']='bookSource'; new_sources.append(ne); found=True
    else:new_sources.append(e)
if not found:
    ne=stable_entry(); ne['category']='novel'; ne['artifactType']='bookSource'; new_sources.insert(0,ne)
m['sources']=new_sources; mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

sp=ROOT/'subscription/stable.json'; sd=json.loads(sp.read_text(encoding='utf-8')); sd['updatedAt']=TS; sd['generatedAt']=TS
found=False
for i,e in enumerate(sd.get('items',[])):
    if isinstance(e,dict) and e.get('id')=='qidian-next': sd['items'][i]=stable_entry(e); found=True; break
if not found:sd.setdefault('items',[]).insert(0,stable_entry())
sp.write_text(json.dumps(sd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bp=ROOT/'subscription/beta.json'; bd=json.loads(bp.read_text(encoding='utf-8')); bd['updatedAt']=TS; bd['generatedAt']=TS
bd['items']=[e for e in bd.get('items',[]) if not (isinstance(e,dict) and e.get('id')=='qidian-next-beta')]
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

np=ROOT/'subscription/novel.json'; nd=json.loads(np.read_text(encoding='utf-8')); nd['updatedAt']=TS; nd['generatedAt']=TS
items=[]; inserted=False
for e in nd.get('items',[]):
    if isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'):
        if not inserted:items.append(stable_entry(e,True)); inserted=True
        continue
    items.append(e)
if not inserted:items.insert(0,stable_entry(None,True))
nd['items']=items; np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

sbp=ROOT/'bundles/all-stable.json'; sba=json.loads(sbp.read_text(encoding='utf-8')); replaced=False
for i,o in enumerate(sba):
    if isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY:sba[i]=new;replaced=True;break
if not replaced:sba.insert(0,new)
sbp.write_text(json.dumps(sba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bbp=ROOT/'bundles/all-beta.json'; bba=json.loads(bbp.read_text(encoding='utf-8'))
bba=[o for o in bba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)]
bbp.write_text(json.dumps(bba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/stable/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强','summary':summary,'badges':['Stable',VERSION,'目录','版权信息','评论优化'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'当前正式版','text':'1.2.6 由用户真机确认的 1.2.6-beta1 原业务逻辑直接晋升。'},
 {'title':'目录与版权','text':'继续使用已确认的 Argus v1 目录主链，支持章节时间、字数、真实分卷和版权信息；版权页采用紧凑固定版式。'},
 {'title':'评论','text':'参考妙想天开：首屏10条、后续分页；官方 v2 结构明确时快速组织主评论/楼中楼，保留 TitleInfoList、头像、时间/IP、点赞、配图、配音与回复分页。'},
 {'title':'其它功能','text':'正文、账号、搜索、情无/小雨及其它 Provider 沿用既有稳定功能链。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'
release=(f"## 2026-09-14 · qidian-next Stable {VERSION}\n"
'- 用户真机确认 `1.2.6-beta1` 功能均正常，并明确要求先晋升正式版后继续优化。\n'
'- Stable 直接沿用该 Beta 运行代码，不新增业务逻辑。\n'
'- 目录继续冻结在 1.2.4 已确认基线：Argus v1 + QDSign/QDInfo，自包含 `N/C/P/V/Vo/T`，支持时间、字数、真实分卷与版权信息。\n'
'- 版权页沿用 1.2.5-beta3 紧凑固定版式。\n'
'- 评论页参考妙想天开：首屏 10 条 + 后续分页；官方 v2 结构明确时走快速组织，保留 TitleInfoList、头像、时间/IP、点赞、配图、配音、楼中楼与回复分页。\n'
'- 发布同步完成 Stable Source / Manifest / Stable Subscription / Novel Catalog / Stable Bundle / Stable Detail；活动 Beta 条目与 Beta Bundle 中的同逻辑源移除，Beta 物理文件保留作下一轮开发基线。\n\n')
rp.write_text(release+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
hand=(f"## 2026-09-14 · Stable {VERSION} — 当前正式基线\n\n"
'- 用户真机确认 `1.2.6-beta1` 功能均正常并要求晋升正式版。\n'
'- 目录：保持 Stable 1.2.4 的 Argus v1 + QDSign/QDInfo 与轻量 `N/C/P/V/Vo/T` 输出，不得重新接回旧大型目录主链。\n'
'- 版权：采用 1.2.5-beta3 紧凑固定版式。\n'
'- 评论：参考妙想天开，首屏10条、后续分页；结构明确时快通道，保留完整身份/媒体/楼中楼能力。\n'
'- Stable 1.2.6 为后续新 Beta 的唯一开发基线。\n\n')
hp.write_text(hand+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-126-stable-report.json'
report.write_text(json.dumps({'version':VERSION,'versionCode':VC,'promotedFrom':'1.2.6-beta1','betaSha256':beta_sha,'stableSha256':sha,'runtimeEqualToBeta':True,'stableIdentity':IDENTITY,'betaCatalogRemoved':True,'betaBundleRemoved':True,'stableCatalogUpdated':True,'novelCatalogUpdated':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
