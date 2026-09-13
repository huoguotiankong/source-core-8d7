import hashlib, json
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.4-beta3'; VC=12043; TS='2026-09-13T23:18:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
STABLE_EXPECTED='1eaffa24543b2af58aed1368578368ea326ffb0170338971bde558df725bed87'
BETA2_EXPECTED='21491f3458ee20a0a7107405690011c41219e3d8312d141e38dd073ae5da9a9b'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'

assert hashlib.sha256(STABLE.read_bytes()).hexdigest()==STABLE_EXPECTED
assert hashlib.sha256(BETA.read_bytes()).hexdigest()==BETA2_EXPECTED
stable_arr=json.loads(STABLE.read_text(encoding='utf-8'))
beta_arr=json.loads(BETA.read_text(encoding='utf-8'))
st=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
bt=beta_arr[0] if isinstance(beta_arr,list) else beta_arr
assert st.get('bookSourceUrl')==IDENTITY and bt.get('bookSourceUrl')==IDENTITY
assert 'v1.2.2 Stable' in st.get('bookSourceComment','')
assert '1.2.4-beta2' in bt.get('bookSourceComment','')

marker='var QF_MOD38_PACK='
def split_pack(lib):
    a=lib.index(marker)+len(marker)
    try:b=lib.index(';\nvar QF_MOD38_EXPORTS=',a)
    except ValueError:b=lib.index(';var QF_MOD38_EXPORTS=',a)
    return a,b,json.loads(lib[a:b])

sa,sb,sp=split_pack(st['jsLib'])
ba,bb,bp=split_pack(bt['jsLib'])
assert 'review_local_ui' in sp and 'review_local_ui' in bp
assert bp['review_local_ui']!=sp['review_local_ui'], 'expected beta2 review module delta'
new_pack=dict(sp)
new_pack['review_local_ui']=bp['review_local_ui']
changed=[k for k in new_pack if new_pack[k]!=sp.get(k)]
assert changed==['review_local_ui'], changed
stable_lib=st['jsLib']
st['jsLib']=stable_lib[:sa]+json.dumps(new_pack,ensure_ascii=False,separators=(',',':'))+stable_lib[sb:]
st['bookSourceName']='🌈 起点增强 · Beta'
st['bookSourceComment']='v1.2.4-beta3：目录回归紧急修复。真机确认 beta2 目录整页空白并显示 null(1/0) 后，立即撤销 beta1 对目录字数字段 W 的底层 jsLib 扩展，目录链完整回到已真机确认的 Stable 1.2.2；仅保留 beta2 的 review_local_ui 评论首屏10条快通道、真实 TitleInfoList 身份标签与排版优化。目录字数功能暂缓，待独立取证后重新实现。正文、搜索、账号、情无/小雨、ruleContent、Rhino loader、本章说及其它 Provider 全部冻结。'
BETA.write_text(json.dumps(stable_arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source_sha=hashlib.sha256(BETA.read_bytes()).hexdigest()

summary='Beta 1.2.4-beta3：紧急恢复 Stable 1.2.2 目录链；保留 beta2 评论首屏加速与身份排版。'
tags=['起点','测试版','目录回归修复','评论','首屏加速','身份标签','楼中楼']
changes=[
 '真机确认 beta2 目录整页空白并显示 null(1/0)，优先恢复目录可用性',
 '撤销 beta1 对目录 W 字段的底层 jsLib 扩展，目录代码完整回到已确认 Stable 1.2.2',
 '仅从 beta2 移植 review_local_ui，保留首屏10条、Reader快通道、真实身份标签和楼中楼排版',
 '章节字数功能暂缓，不再与本次目录恢复捆绑；后续单独取证后实现',
 '正文、搜索、账号、情无/小雨、本章说及其它 Provider 不变'
]

def patch_entry(e,include_type=False):
    e=dict(e or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':source_sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json'})
    if include_type:e['type']='novel'
    return e

mp=ROOT/'manifest.json';m=json.loads(mp.read_text(encoding='utf-8'));m['updatedAt']=TS
for i,e in enumerate(m.get('sources',[])):
    if isinstance(e,dict) and e.get('id')=='qidian-next-beta':
        ne=dict(e);ne.update(patch_entry(e));ne['category']='novel';ne['artifactType']='bookSource';ne['bookSourceUrl']=IDENTITY;m['sources'][i]=ne;break
else:raise AssertionError('manifest beta entry missing')
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

for path,typed in [(ROOT/'subscription/beta.json',False),(ROOT/'subscription/novel.json',True)]:
    d=json.loads(path.read_text(encoding='utf-8'));d['updatedAt']=TS;d['generatedAt']=TS
    for i,e in enumerate(d.get('items',[])):
        if e.get('id')=='qidian-next-beta':d['items'][i]=patch_entry(e,typed);break
    else:raise AssertionError(str(path)+' beta missing')
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bund=ROOT/'bundles/all-beta.json';ba=json.loads(bund.read_text(encoding='utf-8'));src=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
for i,o in enumerate(ba):
    if isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY:ba[i]=src;break
else:ba.insert(0,src)
bund.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'目录回归修复','评论加速'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[{'title':'紧急修复','text':'真机确认 beta2 目录整页空白并显示 null(1/0)。本版首先恢复目录可用性。'},{'title':'目录策略','text':'完全撤销 beta1 的 W 字段底层扩展，目录代码回到已真机确认的 Stable 1.2.2；章节字数暂缓，后续独立实现。'},{'title':'保留优化','text':'仅保留 beta2 的 review_local_ui：评论首屏10条、兼容时一次结构化根评论/回复、真实 TitleInfoList 标签及排版优化。'},{'title':'隔离范围','text':'正文、搜索、账号、情无/小雨、本章说、其它 Provider 全部不改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

release=(
'## 2026-09-13 · qidian-next 1.2.4-beta3 — 目录空白回归紧急修复\n'
'- 用户真机反馈 `1.2.4-beta2` 目录整页空白，底部显示 `null(1/0)`；以真机结果为最高优先级。\n'
'- 立即撤销 beta1 的目录 `W` 字段底层 jsLib 扩展，目录业务代码完整回到已真机确认的 Stable 1.2.2。\n'
'- 仅从 beta2 保留 `review_local_ui`：首屏10条、Reader兼容快通道、真实 `TitleInfoList` 身份标签与评论排版优化。\n'
'- 章节字数功能暂缓，不继续和目录主链捆绑修改；后续先取证真实目录输出结构再单独实现。\n'
'- Stable 1.2.2、正文、搜索、账号、情无/小雨、`ruleContent`、Rhino loader、本章说及其它 Provider 均不变。\n\n'
)
for p in [ROOT/'docs/RELEASE_LOG.md',ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md']:
    old=p.read_text(encoding='utf-8')
    if not old.startswith('## 2026-09-13 · qidian-next 1.2.4-beta3'):
        p.write_text(release+old,encoding='utf-8')

# Gates: Stable unchanged, catalog core restored, only packed review_local_ui differs from Stable.
assert hashlib.sha256(STABLE.read_bytes()).hexdigest()==STABLE_EXPECTED
ck=json.loads(BETA.read_text(encoding='utf-8'));cs=ck[0] if isinstance(ck,list) else ck
assert cs['bookSourceUrl']==IDENTITY and '1.2.4-beta3' in cs['bookSourceComment']
assert cs.get('ruleToc')==st.get('ruleToc')
ca,cb,cp=split_pack(cs['jsLib'])
delta=[k for k in cp if cp[k]!=sp.get(k)]
assert delta==['review_local_ui'], delta
# outside packed module block must exactly equal Stable, proving beta1 W edits are gone
assert cs['jsLib'][:ca]==stable_lib[:sa]
assert cs['jsLib'][cb:]==stable_lib[sb:]
for p in [mp,ROOT/'subscription/beta.json',ROOT/'subscription/novel.json',bund,dp]:json.loads(p.read_text(encoding='utf-8'))
print('PASS',VERSION,source_sha,'stable',STABLE_EXPECTED,'delta',delta)
