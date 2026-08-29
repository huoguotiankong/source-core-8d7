import json,re,base64,gzip,hashlib
from pathlib import Path

PATH=Path('sources/novel/qidian-next/qidian-next-beta.json')
data=json.loads(PATH.read_text(encoding='utf-8'))
src=data[0] if isinstance(data,list) else data
js=src['jsLib']
m=re.search(r'(\\?"role\\?"\s*:\s*\\?"gz:)([A-Za-z0-9+/=]+)',js)
assert m,'role payload not found'
b=m.group(2); b+='='*((4-len(b)%4)%4)
role=gzip.decompress(base64.b64decode(b)).decode('utf-8')

old_tabs='<div class="tabs"><button class="tabBtn on" data-tab="star">星耀守护</button><button class="tabBtn" data-tab="profile">角色档案</button></div>'
profile_handler='event&&event.preventDefault();var box=this.parentNode.parentNode,bs=box.querySelectorAll(&quot;.tabBtn&quot;),ps=box.querySelectorAll(&quot;.tabPane&quot;);for(var j=0;j<bs.length;j++)bs[j].classList.remove(&quot;on&quot;);for(var j=0;j<ps.length;j++)ps[j].classList.remove(&quot;on&quot;);this.classList.add(&quot;on&quot;);var p=box.querySelector(&quot;.profilePane&quot;);if(p)p.classList.add(&quot;on&quot;);return false;'
star_handler='event&&event.preventDefault();var box=this.parentNode.parentNode,bs=box.querySelectorAll(&quot;.tabBtn&quot;),ps=box.querySelectorAll(&quot;.tabPane&quot;);for(var j=0;j<bs.length;j++)bs[j].classList.remove(&quot;on&quot;);for(var j=0;j<ps.length;j++)ps[j].classList.remove(&quot;on&quot;);this.classList.add(&quot;on&quot;);var p=box.querySelector(&quot;.starPane&quot;);if(p)p.classList.add(&quot;on&quot;);return false;'
new_tabs='<div class="tabs"><button class="tabBtn on" data-tab="profile" onclick="'+profile_handler+'">角色档案</button><button class="tabBtn" data-tab="star" onclick="'+star_handler+'">星耀守护</button></div>'
assert old_tabs in role,'beta22 tabs not found'
role=role.replace(old_tabs,new_tabs,1)
old_star='<div class="tabPane starPane on">'
old_profile='<div class="tabPane profilePane">'
assert old_star in role and old_profile in role
role=role.replace(old_star,'<div class="tabPane starPane">',1)
role=role.replace(old_profile,'<div class="tabPane profilePane on">',1)
role=role.replace('该角色当前未返回可用的官方星耀数据','官方暂未返回该角色的星耀守护数据',1)
role=role.replace('角色档案 · 起点官方数据','角色档案 · 起点官方数据 · B23',1)

packed=base64.b64encode(gzip.compress(role.encode('utf-8'),9)).decode('ascii')
js=js[:m.start(2)]+packed+js[m.end(2):]
src['jsLib']=js
src['bookSourceComment']='v1.1.0-beta23：角色卡交互修复版。默认进入“角色档案”，页签改为直接点击切换逻辑，修复真机点击“角色档案”无响应；“星耀守护”降为次级页，官方未返回数据时只显示暂无。保留高清立绘、左右切换、原图查看与 88% BottomSheet；其它域冻结。'
PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('patched beta23 role bytes',len(role.encode('utf-8')))
