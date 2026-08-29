import json,hashlib
from pathlib import Path
ROOT=Path('.')
source_path=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
raw=source_path.read_bytes(); source_data=json.loads(raw.decode('utf-8')); source_obj=source_data[0] if isinstance(source_data,list) else source_data
sha=hashlib.sha256(raw).hexdigest(); version='1.1.0-beta23'; code=11023; ts='2026-08-29T09:45:00+08:00'; day='2026-08-29'
summary='角色卡 beta23：默认显示角色档案，修复真机页签点击无响应；星耀守护降为次级页。'
tags=['起点','测试版','角色卡','角色档案','页签修复','高清立绘','官方数据','多角色切换']
changes=['角色卡默认页由“星耀守护”改为“角色档案”','页签按钮改为直接点击切换，修复真机点击角色档案无响应','星耀守护保留为次级页；官方没有星耀数据时只显示暂无，不影响角色档案','保留官方高清立绘、左右切换、原图查看和 88% BottomSheet','书友圈、正文、目录、评论、Provider 与其它域冻结']

p=ROOT/'manifest.json'; d=json.loads(p.read_text(encoding='utf-8')); d['updatedAt']=ts
for x in d.get('sources',[]):
    if x.get('id')=='qidian-next-beta': x.update({'version':version,'versionCode':code,'updatedAt':ts,'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','summary':summary,'tags':tags,'changelog':changes,'sha256':sha}); break
else: raise AssertionError('manifest qidian-next-beta missing')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=ROOT/'subscription/beta.json'; d=json.loads(p.read_text(encoding='utf-8')); d['updatedAt']=ts; d['generatedAt']=ts
for x in d.get('items',[]):
    if x.get('id')=='qidian-next-beta':
        x.update({'summary':summary,'version':version,'updatedAt':day,'tags':tags,'changelog':changes,'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','backupUrl':f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','importUrl':f'legado://import/importonline?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}'}); break
else: raise AssertionError('subscription qidian-next-beta missing')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=ROOT/'bundles/all-beta.json'; d=json.loads(p.read_text(encoding='utf-8')); hits=0
def walk(v):
    global hits
    if isinstance(v,list):
        for i,x in enumerate(v):
            if isinstance(x,dict) and (str(x.get('bookSourceName','')).find('起点增强')>=0 and 'Beta' in str(x.get('bookSourceName',''))): v[i]=source_obj; hits+=1
            else: walk(x)
    elif isinstance(v,dict):
        for k,x in list(v.items()):
            if isinstance(x,dict) and (str(x.get('bookSourceName','')).find('起点增强')>=0 and 'Beta' in str(x.get('bookSourceName',''))): v[k]=source_obj; hits+=1
            else: walk(x)
walk(d); assert hits>=1
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=ROOT/'docs/RELEASE_LOG.md'; old=p.read_text(encoding='utf-8')
entry='''## 2026-08-29 · 🌈 起点增强 1.1.0-beta23\n\n- 通道：Beta / 测试版，等待真机确认；Stable 1.1.0 不变。\n- 单域：角色卡交互修复。默认进入“角色档案”，不再让无数据的“星耀守护”占据默认页。\n- 页签：改为直接点击切换，修复 Beta22 真机点击“角色档案”无响应。\n- 星耀：继续保留为次级页；官方未返回可用数据时只显示暂无，不伪造数值。\n- 保留：高清立绘、左右角色切换、页码、点击立绘看原图、88% BottomSheet。\n- 冻结：书友圈、正文、目录、评论、Provider、账号及其它域均未修改。\n\n'''
assert '1.1.0-beta23' not in old
if old.startswith('# '):
    pos=old.find('\n')+1; new=old[:pos]+'\n'+entry+old[pos:].lstrip('\n')
else: new=entry+old
p.write_text(new,encoding='utf-8')
print('synced',version,'sha256',sha,'bundle hits',hits)
