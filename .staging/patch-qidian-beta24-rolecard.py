import json,re,base64,gzip
from pathlib import Path

PATH=Path('sources/novel/qidian-next/qidian-next-beta.json')
data=json.loads(PATH.read_text(encoding='utf-8'))
src=data[0] if isinstance(data,list) else data
js=src['jsLib']
m=re.search(r'(\\?"role\\?"\s*:\s*\\?"gz:)([A-Za-z0-9+/=]+)',js)
assert m,'role payload not found'
b=m.group(2); b+='='*((4-len(b)%4)%4)
role=gzip.decompress(base64.b64decode(b)).decode('utf-8')

# Beta23 used inline onclick, but some Legado WebViews still ignore it. Replace the whole tab header
# with radio+label controls so tab switching is handled by native HTML/CSS only.
pat=re.compile(r"'<div class=\"info\"><div class=\"tabs\">.*?</div>'\+",re.S)
hits=len(pat.findall(role))
assert hits==1,f'tab header hits={hits}'
new=("'<div class=\"info\"><input class=\"tabRadio profileRadio\" type=\"radio\" name=\"roleTab'+i+'\" id=\"roleProfile'+i+'\" checked>'"
     "+'<input class=\"tabRadio starRadio\" type=\"radio\" name=\"roleTab'+i+'\" id=\"roleStar'+i+'\">'"
     "+'<div class=\"tabs\"><label class=\"tabBtn profileLabel\" for=\"roleProfile'+i+'\">角色档案</label><label class=\"tabBtn starLabel\" for=\"roleStar'+i+'\">星耀守护</label></div>'+"
)
role=pat.sub(new,role,count=1)

# Neither pane should be permanently forced visible; radio state controls visibility.
role=role.replace('<div class="tabPane profilePane on">','<div class="tabPane profilePane">',1)
role=role.replace('<div class="tabPane starPane on">','<div class="tabPane starPane">',1)

css_old='.tabBtn.on{background:linear-gradient(135deg,#40351e,#282116);color:#f2d38b;box-shadow:inset 0 0 0 1px rgba(231,193,104,.25)}.tabPane{display:none}.tabPane.on{display:block}'
css_new='.tabRadio{position:absolute;opacity:0;width:1px;height:1px;pointer-events:none}.tabBtn{display:flex;align-items:center;justify-content:center;cursor:pointer;user-select:none}.profileRadio:checked~.tabs .profileLabel,.starRadio:checked~.tabs .starLabel{background:linear-gradient(135deg,#40351e,#282116);color:#f2d38b;box-shadow:inset 0 0 0 1px rgba(231,193,104,.25)}.tabPane{display:none}.profileRadio:checked~.profilePane,.starRadio:checked~.starPane{display:block}'
assert css_old in role,'beta23 tab css not found'
role=role.replace(css_old,css_new,1)
role=role.replace('角色档案 · 起点官方数据 · B23','角色档案 · 起点官方数据 · B24',1)

# Ensure no inline tab click dependency remains.
assert 'onclick="event&&event.preventDefault();var box=this.parentNode.parentNode' not in role
assert 'profileRadio:checked~.profilePane' in role and 'starRadio:checked~.starPane' in role
assert 'roleProfile\'+i+\'' in role and 'roleStar\'+i+\'' in role

packed=base64.b64encode(gzip.compress(role.encode('utf-8'),9)).decode('ascii')
js=js[:m.start(2)]+packed+js[m.end(2):]
src['jsLib']=js
src['bookSourceComment']='v1.1.0-beta24：角色卡页签原生切换版。默认角色档案；“角色档案 / 星耀守护”改为 radio + label + CSS 原生状态切换，彻底移除页签对 JavaScript onclick 的依赖，修复真机点击不切换。星耀数据缺失仍作为独立数据问题保留；高清立绘、多角色切换、原图查看、88% BottomSheet 及其它域不变。'
PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('patched beta24 role bytes',len(role.encode('utf-8')))
