import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.5-beta3'; VC=12053; TS='2026-09-14T21:55:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

arr=json.loads(BETA.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
stable_arr=json.loads(STABLE.read_text(encoding='utf-8'))
stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr

# Beta2 is the input baseline: keep its copyright data model (intro/tags) and replace renderer only.
assert '1.2.5-beta2' in str(s.get('bookSourceComment',''))
assert s['ruleToc']==stable['ruleToc']
assert s['ruleBookInfo']==stable['ruleBookInfo']
assert s['ruleContent']==stable['ruleContent']
assert s['bookSourceUrl']==stable['bookSourceUrl']==IDENTITY

js=str(s.get('jsLib',''))
mark='var QF_MOD38_PACK='
p=js.find(mark); assert p>=0
start=js.find('{',p+len(mark)); assert start>=0
depth=0; quote=''; esc=False; end=-1
for i in range(start,len(js)):
    ch=js[i]
    if quote:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch==quote: quote=''
        continue
    if ch in ('"',"'"):
        quote=ch; continue
    if ch=='{': depth+=1
    elif ch=='}':
        depth-=1
        if depth==0:
            end=i+1; break
assert end>start
pack=json.loads(js[start:end])
raw=pack['copyright']; assert raw.startswith('gz:')
b64=raw[3:] + '=' * (-len(raw[3:])%4)
code=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
old_code=code
assert "intro:t(intro||'')" in code and 'tags:Array.isArray(tags)?tags:[]' in code

fn_start=code.index('function qfCopyrightRender(model){')
fn_end=code.index('function qdCopyrightV2929',fn_start)
new_render=r'''function qfCopyrightRender(model){
    model=model&&typeof model==='object'?model:{};
    var bid=String(model.bookId||''),author=String(model.author||''),kind=String(model.category||'作品'),status=String(model.status||'连载'),date=String(model.publishDate||'—'),dateLabel=String(model.publishLabel||'上架'),num=String(model.wordCountWan||'—'),rawWords=String(model.wordCountRaw||''),cover=String(model.coverUrl||''),intro=String(model.intro||''),tags=Array.isArray(model.tags)?model.tags:[];
    function e(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');}
    function t(v){return qfText(String(v==null?'':v)).replace(/\s+/g,' ').trim();}
    function wm(){var z=t(rawWords),m=z.match(/(\d+(?:\.\d+)?)\s*万/);if(m)return m[1];var n=Number(z.replace(/[^0-9.]/g,''));if(isFinite(n)&&n>0)return n>=10000?String(Math.round(n/100)/10000):String(Math.round(n));return (num&&num!=='—')?num:'—';}
    function wrap(v,n,max){v=t(v);var a=[];while(v&&a.length<max){if(v.length<=n){a.push(v);v='';break;}var cut=n,seg=v.slice(0,cut),p=Math.max(seg.lastIndexOf('。'),seg.lastIndexOf('，'),seg.lastIndexOf('；'),seg.lastIndexOf('、'),seg.lastIndexOf(' '));if(p>Math.floor(n*.55))cut=p+1;a.push(v.slice(0,cut));v=v.slice(cut).trim();}if(v&&a.length){a[a.length-1]=a[a.length-1].replace(/[，、；\s]*$/,'')+'…';}return a;}
    function tx(x,y,s,fs,w,a,o){return '<text x="'+x+'" y="'+y+'" font-size="'+fs+'" fill="#202020"'+(w?' font-weight="'+w+'"':'')+(a?' text-anchor="'+a+'"':'')+(o!=null?' opacity="'+o+'"':'')+'>'+e(s)+'</text>';}
    function lines(x,y,arr,fs,lh,w){var z='';for(var i=0;i<arr.length;i++)z+=tx(x,y+i*lh,arr[i],fs,w,'start',.92);return z;}
    var word=wm(),coverData='';
    if(cover){try{coverData=qfCopyrightImageData2929(this,cover,bid?'https://www.qidian.com/book/'+encodeURIComponent(bid)+'/':'https://www.qidian.com/',2*1024*1024)||'';}catch(_cv){}}
    var introLines=wrap(intro,18,4),cleanTags=[];for(var i=0;i<tags.length&&cleanTags.length<9;i++){var q=t(tags[i]);if(q&&cleanTags.indexOf(q)<0)cleanTags.push(q);}var tagLines=wrap(cleanTags.join('   '),24,2);
    var H=760,svg='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="720" height="'+H+'" viewBox="0 0 720 '+H+'">'+
      '<rect width="720" height="'+H+'" fill="transparent"/>'+
      tx(360,90,'版权信息',54,'600','middle',1)+
      tx(120,205,kind||'作品',31,'600','middle',1)+tx(120,242,'类型',18,'400','middle',.52)+
      tx(360,205,date||'—',31,'650','middle',1)+tx(360,242,dateLabel||'上架',18,'400','middle',.52)+
      tx(600,205,word,31,'600','middle',1)+tx(600,242,'万字/'+(status||'连载'),18,'400','middle',.52)+
      '<line x1="90" y1="286" x2="630" y2="286" stroke="#777" stroke-opacity=".20" stroke-width="1"/>'+
      tx(82,338,'支持原创文学，支持正版阅读！',28,'500','start',1)+
      (author?tx(630,382,'— '+author,24,'500','end',.92):'')+
      '<line x1="90" y1="412" x2="630" y2="412" stroke="#777" stroke-opacity=".17" stroke-width="1"/>'+
      (coverData?'<defs><clipPath id="qf125b3"><rect x="548" y="442" width="104" height="138" rx="2"/></clipPath></defs><image href="'+e(coverData)+'" xlink:href="'+e(coverData)+'" x="548" y="442" width="104" height="138" preserveAspectRatio="xMidYMid slice" clip-path="url(#qf125b3)"/>':'')+
      (introLines.length?lines(72,458,introLines,26,44,'400'):'')+
      (tagLines.length?lines(72,introLines.length?635:505,tagLines,23,38,'400'):'')+
      tx(360,710,'— 本作品由起点中文网进行电子制作与发行 —',17,'400','middle',.48)+
      tx(360,740,'版权所有 · 侵权必究',17,'400','middle',.48)+
      '</svg>';
    try{var j=qfJava(this);if(j&&j.base64Encode)return '<img src="data:image/svg+xml;base64,'+j.base64Encode(svg)+'" style="display:block;width:96%;height:auto;margin:0 auto;padding:0;">';}catch(_b){}
    return '<div>'+svg+'</div>';
}
'''
code=code[:fn_start]+new_render+'\n'+code[fn_end:]
assert code!=old_code
assert 'var H=760' in code
assert 'width:96%' in code
assert 'float:right' not in new_render
assert 'table style=' not in new_render
assert 'Book ID' not in new_render

packed='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
pack['copyright']=packed
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.5-beta3：针对 beta2 真机排版错乱修复。阅读会重写普通 HTML 的字体/表格/浮动布局，因此版权页改为高度受控的紧凑 SVG 版式（760/720），锁定三列核心信息、正版声明、作者署名、可选简介/标签与右侧小封面；不再使用表格、float 或大封面。Stable 1.2.4 的目录、时间/字数/分卷、正文、评论、账号与 Provider 全部冻结。'

# Runtime isolation gates against Stable 1.2.4.
for k,v in stable.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v, 'unexpected stable field changed: '+k
assert s['ruleToc']==stable['ruleToc']
assert s['ruleBookInfo']==stable['ruleBookInfo']
assert s['ruleContent']==stable['ruleContent']
assert s['bookSourceUrl']==stable['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.5-beta3：修复版权信息页在阅读中表格/浮动失效导致的竖排和大封面分页，改为紧凑固定版式。'
tags=['起点','测试版','版权信息','排版修复','紧凑SVG','Stable 1.2.4基线']
changes=[
 '根据真机截图确认：阅读正文排版会重写普通 HTML 的表格、字号和 float，beta2 三列信息被拆成纵向文字，封面被单独推到第二页',
 '版权页改为 720×760 紧凑 SVG，只作为一个低高度内容块参与分页，避免 beta1 的整页高图与 beta2 的 HTML 重排问题',
 '固定恢复参考图结构：大标题、三列类型/日期/字数状态、正版声明、作者署名、简介/标签和右侧小封面',
 '继续复用 beta2 已有官方详情数据与 intro/tags 模型，不新增任何网络请求',
 'Stable 1.2.4 的目录时间/字数/真实分卷、正文、评论、账号、Provider 全部冻结'
]

def beta_entry(old=None,typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    return e

mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
items=m.setdefault('sources',[]); pos=next((i for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
ne=beta_entry(items[pos] if pos is not None else None); ne['category']='novel'; ne['artifactType']='bookSource'
if pos is None:
    ins=next((i+1 for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next'),len(items)); items.insert(ins,ne)
else: items[pos]=ne
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bp=ROOT/'subscription/beta.json'; bd=json.loads(bp.read_text(encoding='utf-8')); bd['updatedAt']=TS; bd['generatedAt']=TS
bi=bd.setdefault('items',[]); pos=next((i for i,e in enumerate(bi) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
if pos is None: bi.insert(0,beta_entry())
else: bi[pos]=beta_entry(bi[pos])
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

np=ROOT/'subscription/novel.json'; nd=json.loads(np.read_text(encoding='utf-8')); nd['updatedAt']=TS; nd['generatedAt']=TS
ni=nd.setdefault('items',[]); ni[:]=[e for e in ni if not (isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'))]; ni.insert(0,beta_entry(typed=True))
np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bunp=ROOT/'bundles/all-beta.json'; ba=json.loads(bunp.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr
ba=[o for o in ba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)]; ba.insert(0,src)
bunp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'版权页排版修复'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'真机问题','text':'beta2 使用普通 HTML 表格/float 后，被阅读正文排版重写：三列信息拆成纵向文字，小封面被放大并推到第二页。'},
 {'title':'beta3 方案','text':'改为 720×760 的紧凑 SVG 内容块，所有位置/字号/封面尺寸固定，整体高度显著低于 beta1 大图，目标是在章节标题后直接显示在同一页。'},
 {'title':'冻结范围','text':'目录、章节时间/字数、真实分卷、正文、评论、账号及正文 Provider 不修改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'; old=rp.read_text(encoding='utf-8')
entry=f"## 2026-09-14 · qidian-next {VERSION} — 版权信息页真机排版修复\n- beta2 真机截图确认阅读会重写普通 HTML 表格、字号与 float：三列信息被拆成纵向，封面被放大并单独分页。\n- beta3 将版权页改为 720×760 紧凑 SVG，固定大标题、三列信息、正版声明、作者署名、简介/标签及右侧小封面。\n- 与 beta1 不同，本版 SVG 高度显著压缩，避免高图在章节标题后无法容纳而整体推到下一页。\n- 目录、正文、评论、账号及 Provider 全部冻结，Stable 1.2.4 不变。\n\n"
if entry not in old: rp.write_text(entry+old,encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; old=hp.read_text(encoding='utf-8')
entry=f"## 2026-09-14 · {VERSION} 版权页紧凑固定版式\n- 真机证明普通 HTML 表格/float 不适合版权页：阅读正文 CSS 会重排。\n- 当前 Beta 仅把 copyright renderer 改为 720×760 紧凑 SVG；保留 beta2 intro/tags 数据模型，不新增请求。\n- Stable 1.2.4 目录主链严格冻结。未获真机确认不得晋升 Stable。\n\n"
if entry not in old: hp.write_text(entry+old,encoding='utf-8')

report={'version':VERSION,'versionCode':VC,'betaSha256':sha,'stableRuleTocFrozen':s['ruleToc']==stable['ruleToc'],'stableRuleBookInfoFrozen':s['ruleBookInfo']==stable['ruleBookInfo'],'stableRuleContentFrozen':s['ruleContent']==stable['ruleContent'],'bookSourceUrlFrozen':s['bookSourceUrl']==stable['bookSourceUrl'],'copyrightModuleOnly':True,'compactSvg':'720x760','keepsBeta2IntroTags':True,'noExtraNetworkRequest':True}
(ROOT/'.staging/qidian-125b3-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
