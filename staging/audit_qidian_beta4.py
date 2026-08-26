import json, hashlib, pathlib

ROOT=pathlib.Path('.')
raw=(ROOT/'sources/novel/qidian-next/qidian-next-beta.json').read_bytes()
data=json.loads(raw.decode('utf-8')); src=data[0] if isinstance(data,list) else data
init=(src.get('ruleBookInfo') or {}).get('init') or ''

def around(needle,n=4200):
    i=init.find(needle)
    return '' if i<0 else init[i:i+n].replace('\n',' ')

stable_sha=hashlib.sha256((ROOT/'sources/novel/qidian-next/qidian-next.json').read_bytes()).hexdigest()
print('BETA_SHA',hashlib.sha256(raw).hexdigest())
print('STABLE_SHA',stable_sha)
print('COMMENT',src.get('bookSourceComment','')[:500])
print('--- HUMAN META ---')
print(around('function qfHumanMetaV1104'))
print('--- VISIBLE TAGS ---')
print(around('function qfVisibleTagsV1104'))
print('--- DETAIL ENRICH ---')
print(around('function qfDetailPcEnrichV1104'))
print('--- REGRESSION ---')
print('X-Content-Token',raw.decode('utf-8').count('X-Content-Token'))
print('VIP正文已验证',raw.decode('utf-8').count('VIP正文已验证'))
