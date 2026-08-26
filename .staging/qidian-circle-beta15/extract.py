import json,re,base64,gzip,pathlib
p=pathlib.Path('sources/novel/qidian-next/qidian-next-beta.json')
doc=json.loads(p.read_text(encoding='utf-8'))
s=doc[0]['jsLib']
m=re.search(r'"circle":"gz:([A-Za-z0-9+/=]+)"',s)
assert m,'compressed circle entry not found'
code=gzip.decompress(base64.b64decode(m.group(1))).decode('utf-8')
out=pathlib.Path('.staging/qidian-circle-beta15/circle.js')
out.write_text(code,encoding='utf-8')
print('circle chars',len(code))
print('functions',code.count('function '))
for fn in ['qfCirclePostText2970','qfCirclePostImage2970','qfCircleExtractPosts2970','qfCircleApiHtml2970']:
 print(fn,code.find('function '+fn))