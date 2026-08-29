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

# Beta24 root cause: .info consumed every touchstart/move/end with preventDefault(),
# so label/radio and normal click synthesis could never complete.
start=role.index('function bindInfo(){')
end=role.index('bindInfo();',start)+len('bindInfo();')
fixed='''function bindInfo(){var ins=document.querySelectorAll(".info");for(var n=0;n<ins.length;n++){(function(inf){if(inf.__qfBound)return;inf.__qfBound=1;var sx=0,sy=0,ss0=0,dx=0,dy=0,axis="",interactive=false;inf.addEventListener("touchstart",function(e){lock();interactive=!!(e.target&&e.target.closest&&e.target.closest(".tabs"));if(interactive){e.stopPropagation();return}var t=e.touches[0];sx=t.clientX;sy=t.clientY;ss0=inf.scrollTop;dx=0;dy=0;axis="";if(e.cancelable)e.preventDefault();e.stopPropagation()},{passive:false});inf.addEventListener("touchmove",function(e){if(interactive){e.stopPropagation();return}var t=e.touches[0];dx=t.clientX-sx;dy=t.clientY-sy;var ax=Math.abs(dx),ay=Math.abs(dy);if(!axis&&(ax>6||ay>6))axis=(ax>ay*1.22)?"x":"y";if(axis!=="x"){var max=Math.max(0,inf.scrollHeight-inf.clientHeight),next=ss0-dy;if(next<0)next=0;if(next>max)next=max;inf.scrollTop=next}if(e.cancelable)e.preventDefault();e.stopPropagation()},{passive:false});inf.addEventListener("touchend",function(e){if(interactive){interactive=false;e.stopPropagation();return}if(axis==="x"&&Math.abs(dx)>48&&Math.abs(dx)>Math.abs(dy)*1.22)go(i+(dx<0?1:-1));if(e.cancelable)e.preventDefault();e.stopPropagation();axis=""},{passive:false});inf.addEventListener("touchcancel",function(e){interactive=false;axis="";e.stopPropagation()},{passive:true})})(ins[n])}}bindInfo();'''
role=role[:start]+fixed+role[end:]

# Beta22's JS tab binder is obsolete and conflicts with the radio/label implementation.
bs=role.index('function bindTabs(s){')
be=role.index('function paint(){',bs)
role=role[:bs]+'function bindTabs(s){return}'+role[be:]
role=role.replace('ensureImg(i);bindTabs(ss[i]);','ensureImg(i);',1)

# Explicit native tap zone.
role=role.replace('.tabBtn{display:flex;align-items:center;justify-content:center;cursor:pointer;user-select:none}', '.tabBtn{display:flex;align-items:center;justify-content:center;cursor:pointer;user-select:none;touch-action:manipulation}.tabs{touch-action:manipulation}',1)
role=role.replace('角色档案 · 起点官方数据 · B24','角色档案 · 起点官方数据 · B25',1)

assert 'interactive=!!(e.target&&e.target.closest&&e.target.closest(".tabs"))' in role
assert 'if(interactive){e.stopPropagation();return}' in role
assert 'ensureImg(i);bindTabs(ss[i]);' not in role
assert 'profileRadio:checked~.profilePane' in role and 'starRadio:checked~.starPane' in role
assert '角色档案 · 起点官方数据 · B25' in role

packed=base64.b64encode(gzip.compress(role.encode('utf-8'),9)).decode('ascii')
js=js[:m.start(2)]+packed+js[m.end(2):]
src['jsLib']=js
src['bookSourceComment']='v1.1.0-beta25：角色卡页签触摸根因修复版。定位到档案区自定义 touchstart/touchmove/touchend 对全部触摸执行 preventDefault，导致任何页签方案都无法形成点击；现对 .tabs 触摸完全让行并移除旧 bindTabs 干扰，默认仍为角色档案。星耀数据缺失继续作为独立数据问题保留；其它域冻结。'
PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('patched beta25 role bytes',len(role.encode('utf-8')))
