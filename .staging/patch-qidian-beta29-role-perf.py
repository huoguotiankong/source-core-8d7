import json,re,hashlib
from pathlib import Path

CUR=Path('sources/novel/qidian-next/qidian-next-beta.json')
OLD=Path('/tmp/qidian-beta25.json')
cur=json.loads(CUR.read_text(encoding='utf-8'))
old=json.loads(OLD.read_text(encoding='utf-8'))
cs=cur[0] if isinstance(cur,list) else cur
os=old[0] if isinstance(old,list) else old

pat=re.compile(r'(\\?"role\\?"\s*:\s*\\?"gz:)([A-Za-z0-9+/=]+)')
cm=pat.search(cs['jsLib']); om=pat.search(os['jsLib'])
assert cm and om,'role payload missing'
old_payload=om.group(2)
js=cs['jsLib']
js=js[:cm.start(2)]+old_payload+js[cm.end(2):]
cs['jsLib']=js
cs['bookSourceComment']='v1.1.0-beta29：角色卡性能回退版。完整恢复 beta25 已真机确认的角色模块：保留新版角色档案默认页、角色档案/星耀守护页签切换、触摸让行、高清立绘、多角色滑动、原图查看与 88% BottomSheet；彻底移除 beta26-beta28 Relationship H5 页面/脚本/API 扫描及诊断，恢复首次打开速度。星耀守护数据暂不主动联网探测，待确认稳定官方接口后再单独接入。其它域保持 beta28 当前状态不变。'
CUR.write_text(json.dumps(cur,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('restored exact beta25 role payload',len(old_payload),'sha256',hashlib.sha256(old_payload.encode()).hexdigest())
