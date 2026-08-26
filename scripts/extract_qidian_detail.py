import json,re
from pathlib import Path

src=Path('sources/novel/qidian-next/qidian-next-beta.json')
obj=json.loads(src.read_text(encoding='utf-8'))[0]
rb=obj.get('ruleBookInfo') or {}
init=rb.get('init','') if isinstance(rb,dict) else str(rb)

out=[]
out.append('BOOKSOURCE: '+obj.get('bookSourceName',''))
out.append('COMMENT: '+obj.get('bookSourceComment','')[:500])
out.append('\nRULEBOOKINFO NON-INIT:\n'+json.dumps({k:v for k,v in rb.items() if k!='init'},ensure_ascii=False,indent=2))
out.append('\nINIT LENGTH: '+str(len(init)))

# Section headings/comments are highly informative in this long legacy init.
comments=re.findall(r'/\*([\s\S]*?)\*/',init)
out.append('\nINIT COMMENT INDEX:')
for i,c in enumerate(comments):
    c=' '.join(c.split())
    if any(x in c for x in ['详情','APP','网页','推荐','评分','简介','书友圈','角色','版权','字数','作者','标签','荣誉','限免']):
        out.append(f'{i}: {c[:500]}')

# All explicit qf calls in execution order, plus counts.
calls=re.findall(r'\b(qf[A-Za-z0-9_]+)\s*\(',init)
out.append('\nQF CALL ORDER:\n'+'\n'.join(f'{i+1}. {n}' for i,n in enumerate(calls)))
out.append('\nQF CALL COUNTS:\n'+json.dumps({n:calls.count(n) for n in sorted(set(calls))},ensure_ascii=False,indent=2))

# Context around likely blocking/secondary augmentation calls.
needles=['qfOfficialCallV400','java.ajax','java.get','java.post','java.request','request(','http://','https://','qfApplyDetailHtml301','qfApplyCurrentOfficial304','qfBookInfo','qfMetric301','qfScore304']
for needle in needles:
    pos=0
    while True:
        i=init.find(needle,pos)
        if i<0: break
        out.append(f'\n--- CONTEXT {needle} @ {i} ---\n'+init[max(0,i-1200):min(len(init),i+3600)])
        pos=i+len(needle)

# Tail often contains displayKind/intro composition and final info serialization.
out.append('\n=== INIT TAIL ===\n'+init[-18000:])

# Extract definitions for qdParseBookInfo/qfOfficialCall and obvious detail helper names from all source strings.
strings=[]
def walk(x,path='root'):
    if isinstance(x,dict):
        for k,v in x.items(): walk(v,path+'.'+str(k))
    elif isinstance(x,list):
        for i,v in enumerate(x): walk(v,path+f'[{i}]')
    elif isinstance(x,str): strings.append((path,x))
walk(obj)
helper_names=['qdParseBookInfo','qfOfficialCallV400','qfBookInfoDisplay','qfBookInfo','qfOfficialBookDetail','qfBookInfoRender']
for hn in helper_names:
    for path,s in strings:
        m=re.search(r'function\s+'+re.escape(hn)+r'\s*\(',s)
        if not m: continue
        nxt=re.search(r'\nfunction\s+[A-Za-z_$][A-Za-z0-9_$]*\s*\(',s[m.start()+20:])
        end=(m.start()+20+nxt.start()) if nxt else min(len(s),m.start()+18000)
        out.append(f'\n=== DEF {hn} in {path} ===\n'+s[max(0,m.start()-200):min(end,m.start()+22000)])
        break

Path('.staging').mkdir(exist_ok=True)
Path('.staging/qidian-detail-compact.txt').write_text('\n'.join(out),encoding='utf-8')
print('wrote compact',len('\n'.join(out)))
