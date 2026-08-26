import json, pathlib
p=pathlib.Path('sources/novel/qidian-next/qidian-next-beta.json')
doc=json.loads(p.read_text(encoding='utf-8'))
s=doc[0]['jsLib']
for token in ['"circle":"gz:','"circle": "gz:','circle\":\"gz:','qfCircleDataV430']:
    pos=s.find(token)
    print('TOKEN',repr(token),'POS',pos)
    if pos>=0:
        a=max(0,pos-1500);b=min(len(s),pos+500)
        print('CONTEXT',s[a:b].replace('\n','\\n'))
        pathlib.Path('.staging/qidian-circle-beta15/circle_snippets.txt').write_text(s[a:b],encoding='utf-8')
        break