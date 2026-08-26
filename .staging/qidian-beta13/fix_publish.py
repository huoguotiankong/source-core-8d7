from pathlib import Path
p=Path('.staging/qidian-beta13/publish.py')
s=p.read_text(encoding='utf-8')
a="s, n = re.subn(pat, new, s, count=1, flags=re.S)"
b="s, n = re.subn(pat, lambda _m: new, s, count=1, flags=re.S)"
assert s.count(a)==1, s.count(a)
s=s.replace(a,b,1)
a2="s, n = re.subn(pat_rows, new_rows, s, count=1, flags=re.S)"
b2="s, n = re.subn(pat_rows, lambda _m: new_rows, s, count=1, flags=re.S)"
assert s.count(a2)==1, s.count(a2)
s=s.replace(a2,b2,1)
p.write_text(s,encoding='utf-8')
print('publish.py regex replacement escaping fixed')
