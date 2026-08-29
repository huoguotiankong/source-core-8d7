import json,re,base64,gzip
from pathlib import Path
p=Path('sources/novel/qidian-next/qidian-next-beta.json')
d=json.loads(p.read_text(encoding='utf-8')); s=d[0] if isinstance(d,list) else d
js=s['jsLib']; m=re.search(r'(\\?"role\\?"\s*:\s*\\?"gz:)([A-Za-z0-9+/=]+)',js); assert m
b=m.group(2); b+='='*((4-len(b)%4)%4); role=gzip.decompress(base64.b64decode(b)).decode('utf-8')
old='if(i<lim&&r.id){var rel=qfRoleRelationshipB26(ctx,bid,r.id);if(qfRoleRelValidB26(rel))r.star=rel;}'
new='if(i<lim&&r.id){var rel=qfRoleRelationshipB26(ctx,bid,r.id);if(rel&&(qfRoleRelValidB26(rel)||rel._diag))r.star=rel;}'
assert old in role,'enrich anchor not found'; role=role.replace(old,new,1)
role=role.replace('角色档案 · 起点官方数据 · B27','角色档案 · 起点官方数据 · B28',1)
assert 'rel._diag' in role and 'Relationship诊断' in role
packed=base64.b64encode(gzip.compress(role.encode(),9)).decode(); js=js[:m.start(2)]+packed+js[m.end(2):]; s['jsLib']=js
s['bookSourceComment']='v1.1.0-beta28：修复 beta27 诊断信息被 enrich 层丢弃的问题。Relationship 请求失败时也保留 _diag 到角色 star 模型，因此星耀守护页必定能显示页面/脚本/API候选/尝试数诊断；数据获取逻辑仍沿用 beta27 多官方入口发现链，不伪造星耀数据。其它域冻结。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
