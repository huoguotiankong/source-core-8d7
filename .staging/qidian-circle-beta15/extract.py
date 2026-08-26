import json, pathlib
p=pathlib.Path('sources/novel/qidian-next/qidian-next-beta.json')
doc=json.loads(p.read_text(encoding='utf-8'))

def walk(v,path='root'):
    if isinstance(v,dict):
        for k,x in v.items(): yield from walk(x,path+'.'+str(k))
    elif isinstance(v,list):
        for i,x in enumerate(v): yield from walk(x,path+f'[{i}]')
    elif isinstance(v,str):
        yield path,v

rows=[]
for path,text in walk(doc):
    for token in ['"circle"','circle','qfCircleData','review_common','gz:H4sI']:
        pos=text.find(token)
        if pos>=0:
            rows.append((path,token,len(text),text[max(0,pos-500):min(len(text),pos+1000)]))
            break
print('CANDIDATES',len(rows))
for i,(path,token,n,snip) in enumerate(rows[:20]):
    print('\n---',i,path,token,n,'---\n',snip.replace('\n','\\n'))
out=pathlib.Path('.staging/qidian-circle-beta15/circle_snippets.txt')
out.write_text('\n\n'.join(f'--- {i} {p} {t} {n} ---\n{s}' for i,(p,t,n,s) in enumerate(rows)),encoding='utf-8')