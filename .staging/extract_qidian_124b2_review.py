import base64,gzip,json
from pathlib import Path
p=Path('sources/novel/qidian-next/qidian-next-beta.json')
a=json.loads(p.read_text(encoding='utf-8'));s=a[0] if isinstance(a,list) else a
lib=s['jsLib'];mk='var QF_MOD38_PACK=';i=lib.index(mk)+len(mk)
try:j=lib.index(';\nvar QF_MOD38_EXPORTS=',i)
except ValueError:j=lib.index(';var QF_MOD38_EXPORTS=',i)
pack=json.loads(lib[i:j])
def dec(v):
    if not isinstance(v,str) or not v.startswith('gz:'):return v if isinstance(v,str) else ''
    z=v[3:];z+='='*((4-len(z)%4)%4);return gzip.decompress(base64.b64decode(z)).decode('utf-8')
for name in ['review_local_ui','review_local_data','review']:
    if name in pack:
        Path('.staging/qidian-124b2-'+name+'.txt').write_text(dec(pack[name]),encoding='utf-8')
print('modules', [x for x in ['review_local_ui','review_local_data','review'] if x in pack])
