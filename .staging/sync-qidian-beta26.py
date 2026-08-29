import json,hashlib
from pathlib import Path
ROOT=Path('.')
sp=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
raw=sp.read_bytes(); sd=json.loads(raw.decode('utf-8')); so=sd[0] if isinstance(sd,list) else sd
sha=hashlib.sha256(raw).hexdigest(); version='1.1.0-beta26'; code=11026; ts='2026-08-29T10:20:00+08:00'; day='2026-08-29'
summary='角色卡 beta26：接入官方 Relationship 星耀守护数据链，按 BookId+RoleId 动态发现并签名请求真实星耀数据。'
tags=['起点','测试版','角色卡','角色档案','星耀守护','Relationship','官方数据','RoleId']
changes=['保留 beta25 已真机确认的角色档案/星耀守护页签切换与触摸修复','角色基础资料继续使用官方 v3/bookdetail/lookfor','新增官方 /h5/relationship 星耀链：按 BookId+RoleId 动态发现 Role/Star/Guard Relationship Argus 接口并复用现有签名请求器','真实星耀值、守护人数、等级/排名按 RoleId 合并；接口失败仍显示暂无，不伪造数据','星耀接口路径与角色结果使用会话缓存，最多处理前10个角色','书友圈、正文、目录、评论、Provider 与其它域冻结']

p=ROOT/'manifest.json'; d=json.loads(p.read_text(encoding='utf-8')); d['updatedAt']=ts
for x in d.get('sources',[]):
    if x.get('id')=='qidian-next-beta': x.update({'version':version,'versionCode':code,'updatedAt':ts,'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','summary':summary,'tags':tags,'changelog':changes,'sha256':sha})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=ROOT/'subscription/beta.json'; d=json.loads(p.read_text(encoding='utf-8')); d['updatedAt']=ts; d['generatedAt']=ts
for x in d.get('items',[]):
    if x.get('id')=='qidian-next-beta': x.update({'summary':summary,'version':version,'updatedAt':day,'tags':tags,'changelog':changes,'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','backupUrl':f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','importUrl':f'legado://import/importonline?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}'})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=ROOT/'bundles/all-beta.json'; d=json.loads(p.read_text(encoding='utf-8')); hits=0
def walk(v):
    global hits
    if isinstance(v,list):
        for i,x in enumerate(v):
            if isinstance(x,dict) and ('起点增强' in str(x.get('bookSourceName','')) and 'Beta' in str(x.get('bookSourceName',''))): v[i]=so; hits+=1
            else: walk(x)
    elif isinstance(v,dict):
        for k,x in list(v.items()):
            if isinstance(x,dict) and ('起点增强' in str(x.get('bookSourceName','')) and 'Beta' in str(x.get('bookSourceName',''))): v[k]=so; hits+=1
            else: walk(x)
walk(d); assert hits>=1
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=ROOT/'docs/RELEASE_LOG.md'; old=p.read_text(encoding='utf-8'); entry='''## 2026-08-29 · 🌈 起点增强 1.1.0-beta26\n\n- 通道：Beta / 测试版，等待真机确认；Stable 1.1.0 不变。\n- 角色卡：保留 beta25 已真机确认的页签触摸根因修复，默认“角色档案”。\n- 星耀守护：角色基础资料继续使用 `v3/bookdetail/lookfor`；新增官方 `https://h5.if.qidian.com/h5/relationship?roleId=<RoleId>&bookId=<BookId>` 数据链。\n- 接口发现：从 Relationship HTML 与少量关联脚本动态提取 Role/Star/Guard/Relationship Argus 路径，复用现有 `qfArgusOuterRequest2931` 签名请求器，避免硬编码易变路径。\n- 数据合并：真实星耀值、守护人数、等级/排名按 RoleId 合并；接口失败保持“暂无”，不拿点赞数等其它数据冒充。\n- 性能：接口路径和角色结果使用会话缓存，单本最多 enrich 前10个角色。\n- 冻结：书友圈、正文、目录、评论、Provider 与其它域均不改。\n\n'''
assert version not in old
pos=old.find('\n')+1 if old.startswith('# ') else 0
p.write_text(old[:pos]+'\n'+entry+old[pos:].lstrip('\n') if pos else entry+old,encoding='utf-8')
print('synced',version,'bundle hits',hits,'sha',sha)
