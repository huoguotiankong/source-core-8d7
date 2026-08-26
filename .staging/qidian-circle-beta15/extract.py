import json, base64, gzip, pathlib

p=pathlib.Path('sources/novel/qidian-next/qidian-next-beta.json')
doc=json.loads(p.read_text(encoding='utf-8'))

def walk(v,path='root'):
    if isinstance(v,dict):
        for k,x in v.items(): yield from walk(x,path+'.'+str(k))
    elif isinstance(v,list):
        for i,x in enumerate(v): yield from walk(x,path+f'[{i}]')
    elif isinstance(v,str):
        yield path,v

def extract_object_after(text, token):
    pos=text.find(token)
    assert pos>=0, f'{token} not found'
    start=text.find('{',pos)
    assert start>=0, 'object start not found'
    depth=0; quote=None; esc=False
    for i in range(start,len(text)):
        ch=text[i]
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=None
            continue
        if ch in ('"',"'"):
            quote=ch; continue
        if ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:return text[start:i+1]
    raise AssertionError('object end not found')

hits=[(path,text) for path,text in walk(doc) if 'QF_MOD38_B64' in text]
assert len(hits)==1, f'QF_MOD38_B64 hits={[p for p,_ in hits]}'
path,s=hits[0]
print('MODULE_FIELD',path)
obj=extract_object_after(s,'QF_MOD38_B64')
mods=json.loads(obj)
raw=mods['circle']
assert raw.startswith('gz:')
code=gzip.decompress(base64.b64decode(raw[3:])).decode('utf-8')
out=pathlib.Path('.staging/qidian-circle-beta15/circle.js')
out.write_text(code,encoding='utf-8')
print('circle chars',len(code))
print('functions',code.count('function '))
print('image fn',code.find('function qfCirclePostImage2970'))
print('html fn',code.find('function qfCircleApiHtml2970'))