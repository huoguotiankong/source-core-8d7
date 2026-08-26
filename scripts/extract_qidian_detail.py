import json,re
from pathlib import Path

src=Path('sources/novel/qidian-next/qidian-next-beta.json')
obj=json.loads(src.read_text(encoding='utf-8'))[0]
rb=obj.get('ruleBookInfo') or {}
init=rb.get('init','') if isinstance(rb,dict) else str(rb)
Path('.staging').mkdir(exist_ok=True)
Path('.staging/qidian-init-tail.txt').write_text(init[-22000:],encoding='utf-8')
print('tail',len(init),len(init[-22000:]))
