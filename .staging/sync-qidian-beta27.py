import json,hashlib
from pathlib import Path
ROOT=Path('.')
sp=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
raw=sp.read_bytes(); sd=json.loads(raw.decode('utf-8')); so=sd[0] if isinstance(sd,list) else sd
sha=hashlib.sha256(raw).hexdigest(); version='1.1.0-beta27'; code=11027; ts='2026-08-29T11:32:00+08:00'; day='2026-08-29'
summary='角色卡 beta27：Relationship 多入口发现 + 真机诊断，定位星耀守护数据链最终失败层。'
tags=['起点','测试版','角色卡','星耀守护','Relationship','h5v6','接口诊断','RoleId']
changes=['保留 beta26 角色档案、页签切换与触摸逻辑','星耀发现扩展到 h5/h5v6 的 relationship 与 new/role/share 四个官方入口','最多扫描10个关联脚本与36个 Role/Star/Guard/Relationship Argus 候选','星耀页新增临时 Relationship 诊断：页面字节、脚本数、候选API数、尝试数或命中路径','仍只展示官方真实返回数据，失败不伪造数值','书友圈、正文、目录、评论、Provider 与其它域冻结']

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

p=ROOT/'docs/RELEASE_LOG.md'; old=p.read_text(encoding='utf-8'); entry='''## 2026-08-29 · 🌈 起点增强 1.1.0-beta27\n\n- 通道：Beta / 测试版，等待真机确认；Stable 1.1.0 不变。\n- 角色卡：保留 beta26 已确认运行的 B26 页面、角色档案与星耀页签交互。\n- Relationship：从单一 `h5.if.qidian.com/h5/relationship` 扩展到 h5/h5v6 的 relationship 与 new/role/share 四个官方入口。\n- 动态发现：最多扫描10个关联脚本、36个 Role/Star/Guard/Relationship Argus 候选，继续复用现有签名请求器。\n- 可观测性：星耀页临时显示 Relationship 诊断，包括页面命中/字节数、脚本数、候选 API 数、已尝试数或实际命中路径。\n- 数据原则：没有官方真实返回仍显示暂无，不使用点赞数等替代。\n- 冻结：书友圈、正文、目录、评论、Provider 与其它域均不改。\n\n'''
assert version not in old
pos=old.find('\n')+1 if old.startswith('# ') else 0
p.write_text(old[:pos]+'\n'+entry+old[pos:].lstrip('\n') if pos else entry+old,encoding='utf-8')
print('synced',version,'bundle hits',hits,'sha',sha)
