from pathlib import Path
import re

src=Path('.staging/patch_qidian_124b7_catalog_lifecycle.py').read_text(encoding='utf-8')
pat=re.compile(r'''old="""var qfTocLocalV71=.*?s\['ruleBookInfo'\]\['init'\]=s\['ruleBookInfo'\]\['init'\]\.replace\(old,new,1\)''',re.S)
replacement=r'''init_src=s['ruleBookInfo']['init']
init_pat=re.compile(r"var qfTocLocalV71='';.*?info\\.tocUrl=bid\\?\\(qfTocLocalV71\\|\\|\\('https://m\\.qidian\\.com/book/'\\+bid\\+'/catalog/'\\)\\):String\\(baseUrl\\|\\|''\\);",re.S)
init_new="var qfTocLocalV71='';try{if(bid)qfTocLocalV71=qfMin1247TocUrl.call(this,bid);}catch(_t71){qfTocLocalV71='';}info.tocUrl=bid?qfTocLocalV71:String(baseUrl||'');"
init_out,n=init_pat.subn(init_new,init_src,count=1)
assert n==1, f'bookInfo.init toc regex match count={n}'
s['ruleBookInfo']['init']=init_out'''
out,n=pat.subn(replacement,src,count=1)
assert n==1, f'patch-script transform count={n}'
exec(compile(out,'.staging/patch_qidian_124b7_catalog_lifecycle.py','exec'),{'__name__':'__main__'})
