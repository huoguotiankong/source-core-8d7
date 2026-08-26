import json,re
from pathlib import Path

src=Path('sources/novel/qidian-next/qidian-next-beta.json')
obj=json.loads(src.read_text(encoding='utf-8'))[0]
out=[]
out.append('TOP KEYS\n'+repr(list(obj.keys())))
out.append('\nBOOKSOURCE '+obj.get('bookSourceName','')+' / '+obj.get('bookSourceComment','')[:300])
rb=obj.get('ruleBookInfo')
out.append('\n\n=== ruleBookInfo ===\n'+(json.dumps(rb,ensure_ascii=False,indent=2) if isinstance(rb,(dict,list)) else str(rb)))

# Search all string fields for detail-page visual markers and likely helper/function names.
strings=[]
def walk(x,path='root'):
    if isinstance(x,dict):
        for k,v in x.items(): walk(v,path+'.'+str(k))
    elif isinstance(x,list):
        for i,v in enumerate(x): walk(v,path+f'[{i}]')
    elif isinstance(x,str): strings.append((path,x))
walk(obj)
markers=['互动入口','作品资料','作品数据','标签与荣誉','作品简介','阅读时长','总推荐','月票','粉丝','书友圈','角色卡','查看目录','设置分组','bookInfo','BookInfo','版权信息','最新进度']
for path,s in strings:
    hits=[m for m in markers if m in s]
    if hits:
        out.append('\n\n=== MARKER '+path+' '+','.join(hits)+' ===\n'+s[:24000])

# Gather function identifiers referenced directly in ruleBookInfo.
rbtxt=json.dumps(rb,ensure_ascii=False) if not isinstance(rb,str) else rb
names=sorted(set(re.findall(r'\b(qf[A-Za-z0-9_]+)\s*\(',rbtxt)))
out.append('\n\n=== ruleBookInfo qf refs ===\n'+'\n'.join(names))

# Find definitions for referenced qf funcs and nearby network-call functions in all strings.
for name in names:
    pat=re.compile(r'function\s+'+re.escape(name)+r'\s*\(')
    for path,s in strings:
        m=pat.search(s)
        if m:
            start=max(0,m.start()-300)
            # capture until next top-level function-ish boundary, capped
            nxt=re.search(r'\nfunction\s+qf[A-Za-z0-9_]+\s*\(',s[m.start()+20:])
            end=(m.start()+20+nxt.start()) if nxt else min(len(s),m.start()+14000)
            end=min(end,m.start()+18000)
            out.append(f'\n\n=== DEF {name} in {path} ===\n'+s[start:end])
            break

# Find likely book-info network blocks.
net_tokens=['java.ajax','java.get','java.post','java.request','request(','qfRequest','qfGet','qfAjax','http.get','http.post']
for path,s in strings:
    if any(t in s for t in net_tokens) and any(m in s for m in ['bookInfo','BookInfo','作品资料','书友圈','角色卡','版权','推荐','月票','粉丝']):
        out.append('\n\n=== DETAIL NETWORK CANDIDATE '+path+' ===\n'+s[:30000])

Path('.staging').mkdir(exist_ok=True)
Path('.staging/qidian-detail-extract.txt').write_text('\n'.join(out),encoding='utf-8')
print('wrote extract',len('\n'.join(out)))
