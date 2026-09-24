from pathlib import Path
p=Path('.staging/patch_qidian_128b1_sq_match.py')
s=p.read_text(encoding='utf-8')
old="'- 重点真机复测：《惊悚乐园》作者“三天两觉”，第079章《校园七不思议（八）》；不得再绑定“傀儡先生#8880120”。\\n'- 未经用户真机确认不得晋升 Stable。\\n\\n')"
new="'- 重点真机复测：《惊悚乐园》作者“三天两觉”，第079章《校园七不思议（八）》；不得再绑定“傀儡先生#8880120”。\\n'\n'- 未经用户真机确认不得晋升 Stable。\\n\\n')"
if old not in s:
    raise SystemExit('expected syntax-fix target not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
exec(compile(s,str(p),'exec'),globals(),globals())
