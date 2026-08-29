import json,hashlib
from pathlib import Path
sp=Path('sources/novel/qidian-next/qidian-next-beta.json'); raw=sp.read_bytes(); sd=json.loads(raw); so=sd[0] if isinstance(sd,list) else sd
sha=hashlib.sha256(raw).hexdigest(); version='1.1.0-beta28'; code=11028; ts='2026-08-29T11:50:00+08:00'; day='2026-08-29'
summary='角色卡 beta28：修复 Relationship 失败诊断在角色 enrich 层被丢弃的问题，确保真机显示完整诊断。'
tags=['起点','测试版','角色卡','星耀守护','Relationship','诊断','官方数据']
changes=['修复 beta27 Relationship 请求失败时 _diag 未写回角色 star 模型的问题','星耀守护页现在即使无数据也会显示 Relationship诊断','继续沿用 beta27 relationship/new-role-share 多官方入口发现链','不伪造星耀值、守护排名或等级；其它域冻结']
p=Path('manifest.json'); d=json.loads(p.read_text()); d['updatedAt']=ts
for x in d.get('sources',[]):
 if x.get('id')=='qidian-next-beta': x.update({'version':version,'versionCode':code,'updatedAt':ts,'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','summary':summary,'tags':tags,'changelog':changes,'sha256':sha})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=Path('subscription/beta.json'); d=json.loads(p.read_text()); d['updatedAt']=ts; d['generatedAt']=ts
for x in d.get('items',[]):
 if x.get('id')=='qidian-next-beta': x.update({'summary':summary,'version':version,'updatedAt':day,'tags':tags,'changelog':changes,'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','backupUrl':f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','importUrl':f'legado://import/importonline?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}'})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=Path('bundles/all-beta.json'); d=json.loads(p.read_text()); hits=0
def walk(v):
 global hits
 if isinstance(v,list):
  for i,x in enumerate(v):
   if isinstance(x,dict) and '起点增强' in str(x.get('bookSourceName','')) and 'Beta' in str(x.get('bookSourceName','')): v[i]=so; hits+=1
   else: walk(x)
 elif isinstance(v,dict):
  for k,x in list(v.items()):
   if isinstance(x,dict) and '起点增强' in str(x.get('bookSourceName','')) and 'Beta' in str(x.get('bookSourceName','')): v[k]=so; hits+=1
   else: walk(x)
walk(d); assert hits; p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=Path('docs/RELEASE_LOG.md'); old=p.read_text(); entry='''## 2026-08-29 · 🌈 起点增强 1.1.0-beta28\n\n- 通道：Beta / 测试版；Stable 不变。\n- 角色卡：修复 beta27 的诊断透传错误。Relationship 未命中时 `_diag` 原本在 enrich 层因“无有效星耀值”判断被丢弃，导致真机看不到诊断。\n- 星耀守护：现在失败结果也保留诊断模型，页面会显示 Relationship 页面、脚本、API 候选与尝试数；数据发现逻辑仍沿用 beta27。\n- 冻结：其它域不改。\n\n'''; pos=old.find('\n')+1 if old.startswith('# ') else 0; p.write_text(old[:pos]+'\n'+entry+old[pos:].lstrip('\n') if pos else entry+old)
