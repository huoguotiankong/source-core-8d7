import json, pathlib, time
from datetime import datetime, timezone, timedelta

ROOT=pathlib.Path('.')
REPO='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/'
CDN='https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/'
NOW=datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
DATE=NOW[:10]

# 1) Beta RSS definition: keep identity, bump cache rev, fix RSS self-update scheme.
p=ROOT/'rss/reader-source-repository-beta.json'
a=json.loads(p.read_text(encoding='utf-8'))
assert isinstance(a,list) and len(a)==1
s=a[0]
assert s['sourceUrl'].endswith('/rss/reader-source-repository-beta.json')
s['sourceComment']='UI Beta 10：修复订阅源自更新；Stable/Beta 详情和导入路径严格分流；分类缓存版本升级到 v10。'
s['sortUrl']='\n'.join([
  '🏠 首页::'+REPO+'rss/data/home-beta.json?v=10',
  '⭐ 正式版::'+REPO+'subscription/stable.json?v=10',
  '🧪 测试版::'+REPO+'subscription/beta.json?v=10',
  '📦 批量导入::'+REPO+'rss/data/bundle.json?v=10',
  '📖 使用说明::'+REPO+'rss/data/help.json?v=10',
])
rc=s['ruleContent']
old="if(kind==='rss'&&d.rssUrl){buttons=btn('重新导入 / 更新仓库订阅源','legado://import/importonline?src='+d.rssUrl,false)}"
new="if(kind==='rss'&&d.rssUrl){buttons=btn('重新导入 / 更新仓库订阅源','legado://import/rssSource?src='+d.rssUrl,false)}"
assert old in rc
rc=rc.replace(old,new)
rc=rc.replace('🌈 阅读书源仓库 · 0.2.8-beta9','🌈 阅读书源仓库 · 0.3.0-beta10')
s['ruleContent']=rc
s['lastUpdateTime']=int(time.time()*1000)
p.write_text(json.dumps(a,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(ROOT/'rss/reader-source-repository-beta10.json').write_text(json.dumps(a,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

# 2) Beta home gets its own self-update detail. No stale UI version history.
home={
  'type':'home','name':'首页','updatedAt':NOW,'items':[
    {'name':'🌈 阅读书源仓库','summary':'统一浏览正式版、测试版与批量导入；两个发布通道严格分离。','updatedAt':'仓库入口','icon':CDN+'assets/reader-repo-icon.png','detailUrl':REPO+'rss/data/details/overview.json?v=10'},
    {'name':'📡 仓库线路','summary':'GitHub Raw 主线路，jsDelivr 备用线路。','updatedAt':'双线路','detailUrl':REPO+'rss/data/details/line.json?v=10'},
    {'name':'⭐ Stable / 🧪 Beta','summary':'正式版只导入 Stable；测试版只导入当前 Beta。','updatedAt':'严格分流','detailUrl':REPO+'rss/data/details/policy.json?v=10'},
    {'name':'🔄 更新仓库订阅源','summary':'重新导入当前最新版仓库 Beta 订阅源定义。','updatedAt':'Beta 10','detailUrl':REPO+'rss/data/details/update-beta.json?v=10'},
  ]
}
(ROOT/'rss/data/home-beta.json').write_text(json.dumps(home,ensure_ascii=False,indent=2),encoding='utf-8')
update_beta={
  'kind':'rss','title':'🔄 更新仓库订阅源','summary':'重新导入最新版仓库 Beta 订阅源定义；内部 sourceUrl 身份保持不变，会更新现有仓库订阅源。',
  'badges':['RSS','Beta 10','自更新'],
  'sections':[{'title':'说明','text':'Beta9 及更早版本误用了书源在线导入协议。本版已改为 RSS 专用 legado://import/rssSource 导入协议。'}],
  'rssUrl':REPO+'rss/reader-source-repository-beta.json'
}
(ROOT/'rss/data/details/update-beta.json').write_text(json.dumps(update_beta,ensure_ascii=False,indent=2),encoding='utf-8')

# 3) Version-neutral repository overview; do not accumulate per-release intro.
overview={
  'kind':'info','title':'🌈 阅读书源仓库','summary':'统一浏览、测试和导入本项目发布的阅读书源。',
  'badges':['Repository','Stable/Beta 分流'],
  'sections':[
    {'title':'仓库原则','text':'正式版和测试版使用独立列表、独立详情、独立下载文件。详情页只展示当前状态，不累计每一版历史。'},
    {'title':'更新原则','text':'完整历史统一记录在 Release Log；仓库详情只保留当前版本、核心能力和必要的导入说明。'}
  ]
}
(ROOT/'rss/data/details/overview.json').write_text(json.dumps(overview,ensure_ascii=False,indent=2),encoding='utf-8')

# 4) Stable source detail gets a NEW physical path to break the old Beta-detail cache.
stable_detail={
  'kind':'source','title':'🌈 起点增强',
  'summary':'起点增强型完整书源：官方搜索/详情/目录/评论体系 + 多正文 Provider；设置采用静态双列首页与卡片化多级页面。',
  'badges':['Stable','1.0.0','小说','增强版'],
  'sections':[
    {'title':'核心能力','text':'官方搜索、书籍详情、目录、段评、本章说、作者说等数据链保持起点体系；正文支持多 Provider、STV 与既有切源策略。'},
    {'title':'设置架构','text':'一级页使用静态双列宫格；二级设置使用卡片化多级页面。'},
    {'title':'当前版本','text':'1.0.0 Stable。后续这里只替换当前状态，不累计 Beta3/Beta4/Beta5 等历史介绍。'}
  ],
  'sourceUrl':REPO+'sources/novel/qidian-next/qidian-next.json',
  'backupUrl':CDN+'sources/novel/qidian-next/qidian-next.json'
}
sp=ROOT/'rss/data/details/stable/qidian-next.json'
sp.parent.mkdir(parents=True,exist_ok=True)
sp.write_text(json.dumps(stable_detail,ensure_ascii=False,indent=2),encoding='utf-8')

# 5) Stable list points only to stable physical source/detail. Beta list must not expose qidian-next unless a real beta file exists.
stp=ROOT/'subscription/stable.json'
st=json.loads(stp.read_text(encoding='utf-8'))
for x in st.get('items',[]):
  if x.get('id')=='qidian-next':
    x['name']='🌈 起点增强'
    x['channel']='stable'; x['version']='1.0.0'; x['updatedAt']=DATE
    x['sourceUrl']=REPO+'sources/novel/qidian-next/qidian-next.json'
    x['backupUrl']=CDN+'sources/novel/qidian-next/qidian-next.json'
    x['importUrl']='legado://import/importonline?src='+x['sourceUrl']
    x['detailUrl']=REPO+'rss/data/details/stable/qidian-next.json?v=100'
    x['changelog']=['当前正式版：1.0.0','完整版本历史请查看 Release Log']
st['updatedAt']=NOW
stp.write_text(json.dumps(st,ensure_ascii=False,indent=2),encoding='utf-8')

bp=ROOT/'subscription/beta.json'
beta=json.loads(bp.read_text(encoding='utf-8'))
assert not any(x.get('id')=='qidian-next' for x in beta.get('items',[])), 'qidian-next must not exist in beta until a separate beta source file is published'
beta['updatedAt']=NOW
bp.write_text(json.dumps(beta,ensure_ascii=False,indent=2),encoding='utf-8')

# 6) Docs: hard rule for physical Stable/Beta separation and cache revision.
devp=ROOT/'docs/DEVELOPMENT_RULES.md'
dev=devp.read_text(encoding='utf-8')
rule='''\n## 14. Stable/Beta physical distribution separation\n\nFor a source that has entered Stable, Stable and Beta may share the same Legado `bookSourceUrl` identity, but MUST NOT share the same downloadable JSON path or RSS detail path.\n\nFor `qidian-next` / `🌈 起点增强`:\n\n- Stable source: `sources/novel/qidian-next/qidian-next.json`\n- Future Beta source: `sources/novel/qidian-next/qidian-next-beta.json`\n- Stable detail: `rss/data/details/stable/qidian-next.json`\n- Future Beta detail: `rss/data/details/beta/qidian-next.json`\n\nA Beta catalog entry must point only to the Beta source/detail paths. A Stable catalog entry must point only to the Stable paths. Never let an old Beta detail URL start importing the current Stable file after promotion.\n\nWhen repository channel/detail payloads change in a way that may be cached by Legado/Raw, bump the query revision in the RSS definition (`?v=N`) or move to a new channel-specific detail path.\n'''
if '## 14. Stable/Beta physical distribution separation' not in dev:
  dev=dev.rstrip()+rule+'\n'
devp.write_text(dev,encoding='utf-8')

kp=ROOT/'docs/KNOWN_ISSUES.md'
known=kp.read_text(encoding='utf-8')
issue='''\n## 16. Repository self-update and Stable/Beta route collision — fixed in RSS UI Beta10\n\nObserved on real device after `🌈 起点增强 1.0.0` promotion:\n\n- repository subscription update page did not import/update the RSS definition;\n- old qidian-next detail still showed accumulated Beta3-Beta6 sections;\n- an old cached Beta page could import the newly promoted Stable file.\n\nRoot causes:\n\n- Beta9 used `legado://import/importonline` for RSS self-update instead of `legado://import/rssSource`;\n- update metadata still pointed to an obsolete Beta3 definition;\n- Stable reused the same qidian-next detail/source URLs that old Beta entries had referenced, so cached Beta entries could resolve to Stable after promotion;\n- RSS category query revision remained `v=9`, allowing stale channel payloads to persist.\n\nFix in Beta10:\n\n- RSS self-update uses the RSS-specific import URI;\n- Beta home/update metadata points to the stable Beta identity file `reader-source-repository-beta.json`;\n- category cache revision bumped to `v=10`;\n- Stable qidian-next detail moved to a new Stable-only physical path;\n- future qidian-next Beta releases must use separate Beta source/detail paths.\n\nStatus: published to RSS UI Beta10; awaiting user real-device confirmation.\n'''
if '## 16. Repository self-update and Stable/Beta route collision' not in known:
  known=known.rstrip()+issue+'\n'
kp.write_text(known,encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'
rel=rp.read_text(encoding='utf-8')
entry=f'''## {DATE} — RSS repository UI 0.3.0-beta10\n\nStatus: Beta/Test; repository self-update/channel-isolation fix awaiting real-device confirmation.\n\nChanges:\n\n- Fixed RSS self-update URI to `legado://import/rssSource?src=...`.\n- Added Beta-specific home/update payload and pointed update to the stable Beta RSS identity file.\n- Bumped repository category cache revision from v9 to v10.\n- Moved `🌈 起点增强` Stable detail to a new Stable-only path so stale Beta detail cache cannot import Stable.\n- Codified separate Stable/Beta source and detail paths for future qidian-next releases.\n- Source detail pages remain current-state only; version history stays in Release Log.\n\n'''
if 'RSS repository UI 0.3.0-beta10' not in rel:
  rel='# RELEASE LOG\n\n'+entry+rel.split('# RELEASE LOG',1)[1].lstrip('\n') if rel.startswith('# RELEASE LOG') else entry+rel
rp.write_text(rel,encoding='utf-8')

print('beta10 patch prepared')
