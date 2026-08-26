import json, re, time
from pathlib import Path

ROOT=Path('.')

def load(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))

def save(p,obj):
    (ROOT/p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

def strip_query(url):
    if not isinstance(url,str): return url
    return url.split('?',1)[0]

rss_path=Path('rss/reader-source-repository-beta.json')
rss=load(rss_path)
s=rss[0]
s['sourceComment']='UI Beta 13：一次性重置分类缓存模型；以后分类名、分类URL、详情URL保持永久稳定，不再按UI版本换链接，避免旧文章持续叠加。'
s['ruleArticles']="""<js>
let o={};
try{o=JSON.parse(result)}catch(e){o={items:[]}}
let xs=Array.isArray(o.items)?o.items:[];
let seen={};
xs=xs.filter(function(x){
  let k=String(x.id||x.sourceUrl||x.detailUrl||x.name||'');
  if(!k)return true;
  if(seen[k])return false;
  seen[k]=1;
  return true;
});
xs.map(function(x){
  let ch=String(x.channel||'').toLowerCase();
  let meta=ch==='stable'?'Stable':(ch==='beta'?'Beta':String(x.meta||x.label||''));
  return {n:x.name||'未命名',t:meta,i:x.icon||'',u:x.detailUrl||x.sourceUrl||''};
})
</js>"""
# Keep Beta12 direct-render detail HTML, only update footer label.
s['ruleContent']=s['ruleContent'].replace('UI Beta 12','UI Beta 13')
s['sortUrl']='\n'.join([
 '🏠 首页中心::https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/home-beta.json',
 '⭐ 正式通道::https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/subscription/stable.json',
 '🧪 测试通道::https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/subscription/beta.json',
 '📦 批量中心::https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/bundle.json',
 '📖 帮助中心::https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/help.json',
])
s['lastUpdateTime']=1787706900000
save(rss_path,rss)
save(Path('rss/reader-source-repository-beta13.json'),rss)

# Home: permanent article/detail identities; version info stays inside details, not list identity.
home=load(Path('rss/data/home-beta.json'))
home['name']='首页中心'
home['updatedAt']='2026-08-26T09:15:00+08:00'
meta_map={'repo-overview':'仓库入口','repo-policy':'通道规则','repo-update':'订阅更新'}
for it in home.get('items',[]):
    it['detailUrl']=strip_query(it.get('detailUrl',''))
    it['meta']=meta_map.get(it.get('id',''),'')
    if it.get('id')=='repo-overview': it['updatedAt']='当前仓库'
    elif it.get('id')=='repo-policy': it['updatedAt']='严格分流'
    elif it.get('id')=='repo-update': it['updatedAt']='一键更新'
save(Path('rss/data/home-beta.json'),home)

# Channel lists: detail article identity is permanent; source download URL may still carry its own cache-buster.
for p in [Path('subscription/stable.json'),Path('subscription/beta.json')]:
    o=load(p)
    for it in o.get('items',[]):
        if 'detailUrl' in it: it['detailUrl']=strip_query(it['detailUrl'])
    save(p,o)

# Other repository lists: stabilize detailUrl recursively without changing download/import URLs.
for p in [Path('rss/data/bundle.json'),Path('rss/data/help.json')]:
    if p.exists():
        o=load(p)
        for it in o.get('items',[]):
            if 'detailUrl' in it: it['detailUrl']=strip_query(it['detailUrl'])
        save(p,o)

# Self-update detail.
up=load(Path('rss/data/details/update-beta.json'))
up['summary']='重新导入当前仓库 Beta 定义；Beta13 起分类与详情链接固定，不再用 UI 版本号制造新的文章身份。'
up['badges']=['RSS','UI Beta 13','缓存模型定型']
up['sections']=[
 {'title':'为什么这次需要重新导入','text':'Beta11/Beta12 曾让详情 URL 随 UI 版本变化，阅读会把它们保存成不同文章，因此首页会一版叠一版。Beta13 只做一次分类重置。'},
 {'title':'Beta13 之后','text':'分类名、分类 URL、详情 URL 和条目标题保持稳定；版本信息只更新详情内容。以后正常刷新同一条目，不再通过换链接绕缓存。'}
]
save(Path('rss/data/details/update-beta.json'),up)

# Development rule: lock the model so future versions do not regress.
dev=Path('docs/DEVELOPMENT_RULES.md')
t=dev.read_text(encoding='utf-8')
sec='''\n## 15. RSS article identity stability\n\nLegado persists RSS articles. Changing an item's detail URL or category identity on every UI release can create a new stored article instead of replacing the old one.\n\nRepository UI rule from Beta13 onward:\n\n- top-level category names are stable release-independent identities;\n- category request URLs remain stable and do not carry `?ui=N` release revisions;\n- item `detailUrl` values remain stable and do not carry UI-version query parameters;\n- mutable UI/source version numbers belong inside detail payload content, not in article identity fields;\n- list title/link identity must remain stable across releases;\n- do not solve cache problems by continuously minting new article URLs.\n\nIf a future incompatible RSS migration truly requires a new identity, do it deliberately once with a documented migration plan rather than once per release.\n'''
if '## 15. RSS article identity stability' not in t:
    dev.write_text(t.rstrip()+sec+'\n',encoding='utf-8')

rel=Path('docs/RELEASE_LOG.md')
r=rel.read_text(encoding='utf-8')
block='''## 2026-08-26 — RSS repository UI 0.3.3-beta13\n\nStatus: Beta/Test; one-time RSS cache-model reset awaiting real-device confirmation.\n\nChanges:\n\n- Replaced the Beta11/Beta12 versioned category/detail identity strategy with permanent RSS article identities.\n- Introduced one new set of top-level category names to escape the already polluted old category cache.\n- Removed `?ui=N` from category and item detail URLs; future UI releases must keep them stable.\n- Removed mutable UI version/date metadata from list identity; version stays in detail content only.\n- Kept Beta12 direct-render detail HTML, list de-duplication and Stable/Beta physical source separation.\n- No book-source business JSON was modified.\n\n'''
if '## 2026-08-26 — RSS repository UI 0.3.3-beta13' not in r:
    if r.startswith('# RELEASE LOG\n\n'):
        r='# RELEASE LOG\n\n'+block+r[len('# RELEASE LOG\n\n'):]
    else:r=block+r
    rel.write_text(r,encoding='utf-8')

known=Path('docs/KNOWN_ISSUES.md')
k=known.read_text(encoding='utf-8')
issue='''\n## 20. RSS UI releases accumulated old Home/Stable entries — cache model replaced in Beta13\n\nReal-device symptom: after updating Beta11 -> Beta12, Home displayed the three Beta12 items followed by the same three Beta11 items. The channel JSON itself was not duplicated.\n\nRoot cause: previous mitigation changed category/detail URLs with `?ui=N`. Legado persists RSS articles, so each new detail URL could be treated as a different stored article; in-list de-duplication cannot remove articles already stored by an older RSS definition.\n\nBeta13 strategy: perform one category-name reset, then freeze category names, category URLs and item detail URLs permanently. Mutable version data is shown only inside detail content. Do not mint new article URLs for routine UI releases.\n\nStatus: Beta13 published for real-device confirmation.\n'''
if '## 20. RSS UI releases accumulated old Home/Stable entries' not in k:
    known.write_text(k.rstrip()+issue+'\n',encoding='utf-8')

print('rss beta13 patch complete')
