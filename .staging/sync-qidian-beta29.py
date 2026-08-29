import json,hashlib
from pathlib import Path
ROOT=Path('.')
sp=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
raw=sp.read_bytes(); sd=json.loads(raw.decode('utf-8')); so=sd[0] if isinstance(sd,list) else sd
sha=hashlib.sha256(raw).hexdigest(); version='1.1.0-beta29'; code=11029; ts='2026-08-29T13:50:00+08:00'; day='2026-08-29'
summary='角色卡 beta29：完整回退到 beta25 角色模块，移除 Relationship 扫描，恢复首次打开性能。'
tags=['起点','测试版','角色卡','性能回退','角色档案','页签修复','高清立绘','官方数据']
changes=['角色模块完整恢复 beta25 已真机确认基线','保留角色档案默认页、页签切换、触摸让行、高清立绘、多角色滑动、原图查看和88% BottomSheet','彻底移除 beta26-beta28 Relationship 页面/脚本/API 扫描及诊断，恢复首次打开速度','星耀守护暂不主动联网探测，待找到明确稳定官方接口后再单独接入','书友圈、正文、目录、评论、Provider 与其它域保持当前状态不变']

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

p=ROOT/'docs/RELEASE_LOG.md'; old=p.read_text(encoding='utf-8'); entry='''## 2026-08-29 · 🌈 起点增强 1.1.0-beta29\n\n- 通道：Beta / 测试版，等待真机确认；Stable 1.1.0 不变。\n- 性能回退：角色模块完整恢复 `1.1.0-beta25` 已真机确认版本，不手工裁剪，避免 Relationship 残留逻辑。\n- 保留：角色档案默认页、角色档案/星耀守护页签、`.tabs` 触摸让行修复、高清立绘、多角色滑动、原图查看、88% BottomSheet。\n- 移除：beta26-beta28 新增的 Relationship H5 页面请求、关联脚本扫描、候选 Argus API 探测及诊断。\n- 目标：恢复 beta25 的首次打开速度；星耀守护数据暂不主动联网探测。\n- 冻结：书友圈、正文、目录、评论、Provider 与其它域保持当前状态不变。\n\n'''
pos=old.find('\n')+1 if old.startswith('# ') else 0
p.write_text(old[:pos]+'\n'+entry+old[pos:].lstrip('\n') if pos else entry+old,encoding='utf-8')
print('synced',version,'bundle hits',hits,'sha',sha)
