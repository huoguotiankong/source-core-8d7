import json, hashlib
from pathlib import Path

ROOT=Path('.')
PHASE=ROOT/'sources/novel/qidian-next/qidian-next-toc-phase-diag.json'
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.4-beta9'; VC=12049; TS='2026-09-14T21:00:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

phase_arr=json.loads(PHASE.read_text(encoding='utf-8'))
s=phase_arr[0] if isinstance(phase_arr,list) else phase_arr
stable_arr=json.loads(STABLE.read_text(encoding='utf-8'))
stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
phase=json.loads(json.dumps(s,ensure_ascii=False))

# A/B invariant: business/runtime rules are byte-for-byte the already user-confirmed working phase diagnostic.
# Only source identity/display metadata changes to the normal qidian-next Beta identity.
s['bookSourceUrl']=IDENTITY
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.4-beta9：目录身份 A/B 诊断版。业务运行代码与已真机确认“能加载目录、时间和字数正常”的目录阶段诊断源完全一致；仅把 bookSourceUrl 切回 qidian-next 正常身份。用于确认剩余故障是否来自阅读对该身份的持久化状态/书籍记录，而不是目录代码。版权信息与分卷本版暂不补，避免再次混入结果层变量。'

for k,v in phase.items():
    if k in ('bookSourceUrl','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v, 'runtime field differs from phase diag: '+k
assert s['jsLib']==phase['jsLib']
assert s['ruleBookInfo']==phase['ruleBookInfo']
assert s['ruleToc']==phase['ruleToc']
assert s['ruleContent']==phase['ruleContent']==stable['ruleContent']

BETA.write_text(json.dumps(phase_arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.4-beta9：与真机已通过的目录阶段诊断源业务代码完全一致，仅切回 qidian-next 正常身份做 A/B。'
tags=['起点','测试版','目录诊断','身份A/B','Argus v1','章节字数']
changes=[
 '业务运行代码逐字段等于已真机确认可正常加载目录的“目录阶段诊断”源',
 '仅将 bookSourceUrl 从独立诊断身份切回 qidian-next 正常身份，用于隔离阅读持久化状态/书籍记录影响',
 '本版故意不补版权信息和分卷，避免再次混入目录结果层变化',
 '若 beta9 仍失败而独立目录阶段诊断仍成功，即可确认故障与 qidian-next 正常身份的持久化状态强相关',
 '正文、评论、账号、搜索、详情主体、Provider 等均与目录阶段诊断/Stable 对应业务代码保持不变'
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
    d=json.loads(path.read_text(encoding='utf-8')); d['updatedAt']=TS; d['generatedAt']=TS; ok=False
    for i,e in enumerate(d.get('items',[])):
        if isinstance(e,dict) and e.get('id')=='qidian-next-beta': d['items'][i]=entry(e,typed); ok=True; break
    assert ok, str(path)
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bp=ROOT/'bundles/all-beta.json'; ba=json.loads(bp.read_text(encoding='utf-8')); src=phase_arr[0] if isinstance(phase_arr,list) else phase_arr; ok=False
for i,o in enumerate(ba):
    if isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY: ba[i]=src; ok=True; break
if not ok: ba.insert(0,src)
bp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'身份A/B','目录诊断'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'唯一变量','text':'beta9 与已经真机通过的目录阶段诊断源业务运行代码完全一致；唯一关键变量是 bookSourceUrl 恢复为 qidian-next 正常身份。'},
 {'title':'为什么撤回 beta8','text':'beta8 在工作诊断源基础上调用 Stable 目录结果转换器后再次无法加载，因此先撤销版权/分卷补丁，不继续叠加猜测。'},
 {'title':'判定标准','text':'若 beta9 失败但独立目录阶段诊断继续成功，说明问题来自正常身份下的阅读持久化状态/旧书籍记录；若 beta9 成功，则 beta8 的结果转换层是故障点。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'
release=(f"## 2026-09-14 · qidian-next {VERSION} — 目录身份 A/B\n"
'- 真机：独立“目录阶段诊断”可正常加载目录且时间/字数正常；beta8 恢复版权/分卷后再次无法加载。\n'
'- beta9 撤销 beta8 的结果层补丁，业务代码完整回到已通过的目录阶段诊断源。\n'
'- 唯一关键变量：`bookSourceUrl` 切回 qidian-next 正常身份，验证阅读对该身份的持久化状态/旧书籍记录是否导致失败。\n'
'- 本版不补版权信息和分卷；等身份 A/B 结论明确后再单独处理。\n'
'- Stable 1.2.2 不变。\n\n')
rp.write_text(release+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
hand=(f"## 2026-09-14 · {VERSION} — 当前活动 Beta：身份 A/B\n\n"
'- 已通过对照：独立 `qidian-next-toc-phase-diag.json` 能加载目录并显示时间+字数。\n'
'- beta8 仅补目录结果层后再次失败，因此当前不能假定 `qfTocNormalizeAppV70` 在该执行阶段安全。\n'
'- beta9 业务运行代码与通过版逐字段一致，仅恢复正常 qidian-next `bookSourceUrl`。\n'
'- 若 beta9 失败而独立诊断源仍成功，下一步优先处理 Legado 身份/持久化状态，不再修改目录请求或解析。\n'
'- 版权信息/分卷暂缓。Stable 不变。\n\n')
hp.write_text(hand+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-124b9-report.json'
report.write_text(json.dumps({'version':VERSION,'phaseDiagSha256':hashlib.sha256(PHASE.read_bytes()).hexdigest(),'betaSha256':sha,'runtimeEqualToPhaseDiag':True,'onlyRuntimeIdentityDifference':'bookSourceUrl/name/group/comment','ruleContentFrozen':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
