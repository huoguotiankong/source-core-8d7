import json,hashlib
from pathlib import Path

ROOT=Path('.')
source_path=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
raw=source_path.read_bytes()
source_data=json.loads(raw.decode('utf-8'))
source_obj=source_data[0] if isinstance(source_data,list) else source_data
sha=hashlib.sha256(raw).hexdigest()
version='1.1.0-beta22'; code=11022
ts='2026-08-29T09:30:00+08:00'; day='2026-08-29'
summary='角色卡 beta22：官方高清立绘 + 星耀守护/角色档案双页签，基础资料与星耀字段仅展示官方实值。'
tags=['起点','测试版','角色卡','星耀守护','角色档案','高清立绘','官方数据','多角色切换']
changes=[
 '角色卡重构为“星耀守护 / 角色档案”双页签，减少立绘独占首屏空间',
 '保留官方高清立绘、左右角色切换、页码提示、点击立绘查看原图及 88% BottomSheet',
 '档案页新增性别、生日、星座、年龄、身份、阵营等官方字段的按需展示，并保留官方角色简介与标签',
 '星耀页新增守护排名、星耀值、等级、守护人数与官方进度字段；接口无数据时明确显示暂无，不猜造数值',
 '书友圈第二页、正文、目录、评论、Provider 与其它域冻结'
]

# manifest
p=ROOT/'manifest.json'; d=json.loads(p.read_text(encoding='utf-8')); d['updatedAt']=ts
hit=0
for x in d.get('sources',[]):
    if x.get('id')=='qidian-next-beta':
        x.update({'version':version,'versionCode':code,'updatedAt':ts,'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','summary':summary,'tags':tags,'changelog':changes,'sha256':sha});hit+=1
assert hit==1
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# beta subscription
p=ROOT/'subscription/beta.json'; d=json.loads(p.read_text(encoding='utf-8'));d['updatedAt']=ts;d['generatedAt']=ts
hit=0
for x in d.get('items',[]):
    if x.get('id')=='qidian-next-beta':
        x.update({'summary':summary,'version':version,'updatedAt':day,'tags':tags,'changelog':changes,'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','backupUrl':f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={code}','importUrl':f'legado://import/importonline?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}'});hit+=1
assert hit==1
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# all-beta bundle: replace only beta21 qidian-next source object.
p=ROOT/'bundles/all-beta.json'; d=json.loads(p.read_text(encoding='utf-8'));hits=0
def walk(v):
    global hits
    if isinstance(v,list):
        for i,x in enumerate(v):
            if isinstance(x,dict) and ('v1.1.0-beta21' in str(x.get('bookSourceComment','')) or (str(x.get('bookSourceName','')).find('起点增强')>=0 and 'Beta' in str(x.get('bookSourceName','')))):
                v[i]=source_obj;hits+=1
            else: walk(x)
    elif isinstance(v,dict):
        for k,x in list(v.items()):
            if isinstance(x,dict) and ('v1.1.0-beta21' in str(x.get('bookSourceComment','')) or (str(x.get('bookSourceName','')).find('起点增强')>=0 and 'Beta' in str(x.get('bookSourceName','')))):
                v[k]=source_obj;hits+=1
            else: walk(x)
walk(d)
assert hits>=1, f'bundle qidian beta not found: {hits}'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# release log prepend, preserving history.
p=ROOT/'docs/RELEASE_LOG.md'; old=p.read_text(encoding='utf-8')
entry='''## 2026-08-29 · 🌈 起点增强 1.1.0-beta22\n\n- 通道：Beta / 测试版，等待真机确认；Stable 1.1.0 不变。\n- 单域：角色卡。重构为“星耀守护 / 角色档案”双页签，保留官方高清立绘、左右切换、页码、原图查看和 88% 半屏。\n- 角色档案：性别、生日、星座、年龄、身份、阵营等字段仅在官方响应真实存在时展示；角色简介缺失不再生成虚构文案。\n- 星耀守护：展示官方响应中可识别的守护排名、星耀值、等级、守护人数及进度字段；没有官方数据时显示暂无，不推断、不伪造。\n- 冻结：书友圈第二页已按当前用户决定暂缓；正文、目录、评论、Provider、账号及其它域均未修改。\n\n'''
assert '1.1.0-beta22' not in old
if old.startswith('# '):
    pos=old.find('\n')+1
    new=old[:pos]+'\n'+entry+old[pos:].lstrip('\n')
else:new=entry+old
p.write_text(new,encoding='utf-8')
print('synced',version,'sha256',sha,'bundle hits',hits)
