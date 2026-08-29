import json,hashlib
from pathlib import Path
ROOT=Path('.')
sp=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
raw=sp.read_bytes(); sd=json.loads(raw.decode('utf-8')); so=sd[0] if isinstance(sd,list) else sd
sha=hashlib.sha256(raw).hexdigest(); version='1.1.0-beta25'; code=11025; ts='2026-08-29T10:05:00+08:00'; day='2026-08-29'
summary='角色卡 beta25：修复档案区 touch preventDefault 吞掉页签点击的根因，页签触摸改为原生让行。'
tags=['起点','测试版','角色卡','角色档案','星耀守护','触摸修复','WebView兼容','官方数据']
changes=['定位并修复 .info 自定义 touchstart/touchmove/touchend 对页签触摸执行 preventDefault 的根因','页签区域触摸完全让行，保留 radio + label + CSS 原生切换','移除旧 bindTabs JavaScript 点击绑定，避免与新页签状态互相干扰','默认仍显示角色档案；星耀数据缺失继续作为独立数据链问题处理','高清立绘、多角色切换、原图查看、88% BottomSheet 及其它域冻结']

p=ROOT/'manifest.json'; d=json.loads(p.read_text(encoding='utf-8')); d['updatedAt']=ts
hit=0
for x in d.get('sources',[]):
    if x.get('id')=='qidian-next-beta': x.update({'version':version,'versionCode':code,'updatedAt':ts,'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','summary':summary,'tags':tags,'changelog':changes,'sha256':sha}); hit+=1
assert hit==1
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=ROOT/'subscription/beta.json'; d=json.loads(p.read_text(encoding='utf-8')); d['updatedAt']=ts; d['generatedAt']=ts
hit=0
for x in d.get('items',[]):
    if x.get('id')=='qidian-next-beta': x.update({'summary':summary,'version':version,'updatedAt':day,'tags':tags,'changelog':changes,'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','backupUrl':f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','importUrl':f'legado://import/importonline?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}'}); hit+=1
assert hit==1
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

p=ROOT/'docs/RELEASE_LOG.md'; old=p.read_text(encoding='utf-8'); entry='''## 2026-08-29 · 🌈 起点增强 1.1.0-beta25\n\n- 通道：Beta / 测试版，等待真机确认；Stable 1.1.0 不变。\n- 根因：角色卡 `.info` 自定义滚动层在 touchstart/touchmove/touchend 全阶段统一 `preventDefault()`，导致页签无论 onclick 还是 label/radio 都无法形成有效点击。\n- 修复：触摸起点属于 `.tabs` 时完全跳过自定义手势接管；普通档案滚动与左右切角色仍沿用原手势逻辑。\n- 清理：移除旧 `bindTabs()` JavaScript 页签绑定，保留 radio + label + CSS 状态切换；默认角色档案。\n- 数据：星耀守护暂无数据仍作为独立数据链问题，本版不处理数据源。\n- 冻结：高清立绘、多角色切换、原图查看、88% BottomSheet、书友圈、正文、目录、评论、Provider 与其它域。\n\n'''
assert version not in old
pos=old.find('\n')+1 if old.startswith('# ') else 0
p.write_text(old[:pos]+'\n'+entry+old[pos:].lstrip('\n') if pos else entry+old,encoding='utf-8')
print('synced',version,'bundle hits',hits,'sha',sha)
