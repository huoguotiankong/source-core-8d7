import json,hashlib
from pathlib import Path
ROOT=Path('.')
sp=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
raw=sp.read_bytes(); sd=json.loads(raw.decode('utf-8')); so=sd[0] if isinstance(sd,list) else sd
sha=hashlib.sha256(raw).hexdigest(); version='1.1.0-beta24'; code=11024; ts='2026-08-29T09:55:00+08:00'; day='2026-08-29'
summary='角色卡 beta24：默认角色档案，页签改为纯 HTML/CSS 原生切换，修复真机点击星耀守护不响应。'
tags=['起点','测试版','角色卡','角色档案','星耀守护','纯CSS页签','高清立绘','官方数据']
changes=['角色卡默认显示角色档案','角色档案/星耀守护改为 radio + label + CSS 切换，完全移除 onclick 依赖','星耀守护无数据仍作为独立数据问题保留，不伪造数值','保留高清立绘、左右切换、原图查看和 88% BottomSheet','书友圈、正文、目录、评论、Provider 与其它域冻结']

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

p=ROOT/'docs/RELEASE_LOG.md'; old=p.read_text(encoding='utf-8'); entry='''## 2026-08-29 · 🌈 起点增强 1.1.0-beta24\n\n- 通道：Beta / 测试版，等待真机确认；Stable 1.1.0 不变。\n- 角色卡：默认显示“角色档案”。\n- 页签：将“角色档案 / 星耀守护”从 JavaScript onclick 切换改为 radio + label + CSS 原生状态切换，规避阅读 WebView 点击事件不执行的问题。\n- 数据：星耀守护暂无数据仍作为独立数据链问题保留，本版不伪造、不映射其它统计值。\n- 冻结：高清立绘、多角色切换、原图查看、88% BottomSheet、书友圈、正文、目录、评论、Provider 与其它域均不改。\n\n'''
assert version not in old
pos=old.find('\n')+1 if old.startswith('# ') else 0
p.write_text(old[:pos]+'\n'+entry+old[pos:].lstrip('\n') if pos else entry+old,encoding='utf-8')
print('synced',version,'bundle hits',hits,'sha',sha)
