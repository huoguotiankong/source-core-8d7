import json, re, base64, gzip, pathlib
p=pathlib.Path('sources/novel/qidian-next/qidian-next-beta.json')
doc=json.loads(p.read_text(encoding='utf-8'))
s=doc[0]['jsLib']
m=re.search(r'var QF_MOD38_B64=(\{.*?\});\nvar QF_MOD38_EXPORTS=',s,re.S)
assert m,'QF_MOD38_B64 not found'
mods=json.loads(m.group(1))
raw=mods['circle']
assert raw.startswith('gz:')
code=gzip.decompress(base64.b64decode(raw[3:])).decode('utf-8')
out=pathlib.Path('.staging/qidian-circle-beta15/circle.js')
out.write_text(code,encoding='utf-8')
print('circle chars',len(code))
print('functions',code.count('function '))