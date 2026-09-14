import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.5-beta2'; VC=12052; TS='2026-09-14T21:42:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

arr=json.loads(STABLE.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
stable=json.loads(json.dumps(s,ensure_ascii=False))

# Parse QF_MOD38_PACK with a string-aware brace scanner.
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

# Extend the existing official copyright model without adding a new request.
needle="    var cover=_bound?String(qfBookVarV09.call(this,'qf_cover','')||''):'';\n"
assert needle in code
code=code.replace(needle, needle+"    var intro='',tags=[];\n",1)

needle2="                if(!cover)cover=String(deep(root,['BookCoverUrl','bookCoverUrl','CoverUrl','coverUrl','BookCover','bookCover','Cover','cover'],0)||'');\n"
assert needle2 in code
extra=r'''                if(!rawKind)rawKind=String(deep(root,['CategoryName','categoryName','BookCategoryName','bookCategoryName','SubCategoryName','subCategoryName','Category','category'],0)||'');
                if(!rawStatus)rawStatus=String(deep(root,['BookStatus','bookStatus','StatusName','statusName','BookStatusName','bookStatusName','Status','status'],0)||'');
                if(!intro){
                    var iv=deep(root,['AuthorIntroduction','authorIntroduction','AuthorIntro','authorIntro','AuthorDescription','authorDescription','AuthorDesc','authorDesc','WriterIntro','writerIntro','WriterDescription','writerDescription'],0);
                    if(!iv)iv=deep(root,['BookIntro','bookIntro','Introduction','introduction','Intro','intro','Description','description'],0);
                    intro=t(iv||'');
                }
                if(!tags.length){
                    var tv=deep(root,['TagList','tagList','BookTags','bookTags','Tags','tags','Tag','tag'],0),ta=[];
                    function pushTag(v){v=t(v);if(v&&v!=='[object Object]'&&ta.indexOf(v)<0)ta.push(v);}
                    if(Array.isArray(tv)){
                        for(var ti=0;ti<tv.length;ti++){
                            var it=tv[ti];
                            if(it&&typeof it==='object')pushTag(deep(it,['TagName','tagName','Name','name','Title','title','Tag','tag'],0));
                            else pushTag(it);
                        }
                    }else if(tv&&typeof tv==='object'){
                        for(var tk in tv)if(Object.prototype.hasOwnProperty.call(tv,tk)){
                            var vv=tv[tk];
                            if(vv&&typeof vv==='object')pushTag(deep(vv,['TagName','tagName','Name','name','Title','title','Tag','tag'],0));
                            else pushTag(vv);
                        }
                    }else if(tv){
                        String(tv).split(/[，,、|\/\s]+/).forEach(pushTag);
                    }
                    tags=ta.slice(0,10);
                }
'''
code=code.replace(needle2, needle2+extra,1)

old_ret="        publishLabel:String(dt(pub)?pubLabel:'上架'),publishSource:String(pubSource||'none'),coverUrl:String(cover||''),\n        source:'qidian-official',schema:'qf.copyright/1',contractVersion:1\n"
new_ret="        publishLabel:String(dt(pub)?pubLabel:'上架'),publishSource:String(pubSource||'none'),coverUrl:String(cover||''),\n        intro:t(intro||''),tags:Array.isArray(tags)?tags:[],\n        source:'qidian-official',schema:'qf.copyright/1',contractVersion:1\n"
assert old_ret in code
code=code.replace(old_ret,new_ret,1)

fn_start=code.index('function qfCopyrightRender(model){')
fn_end=code.index('function qdCopyrightV2929',fn_start)
new_render=r'''function qfCopyrightRender(model){
    model=model&&typeof model==='object'?model:{};
    var bid=String(model.bookId||''),author=String(model.author||''),kind=String(model.category||'作品'),status=String(model.status||'连载'),date=String(model.publishDate||'—'),dateLabel=String(model.publishLabel||'上架'),num=String(model.wordCountWan||'—'),rawWords=String(model.wordCountRaw||''),cover=String(model.coverUrl||''),intro=String(model.intro||''),tags=Array.isArray(model.tags)?model.tags:[];
    function e(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
    function t(v){return qfText(String(v==null?'':v)).replace(/\s+/g,' ').trim();}
    function wordMetric(){
        var z=t(rawWords),m=z.match(/(\d+(?:\.\d+)?)\s*万/);if(m)return {v:m[1],u:'万字'};
        var n=Number(z.replace(/[^0-9.]/g,''));
        if(isFinite(n)&&n>0){if(n>=10000){var w=(n/10000).toFixed(n>=1000000?1:2).replace(/0+$/,'').replace(/\.$/,'');return {v:w,u:'万字'};}return {v:String(Math.round(n)),u:'字'};}
        return {v:(num&&num!=='—'?num:'—'),u:'万字'};
    }
    var wm=wordMetric(),coverData='';
    if(cover){try{coverData=qfCopyrightImageData2929(this,cover,bid?'https://www.qidian.com/book/'+encodeURIComponent(bid)+'/':'https://www.qidian.com/',2*1024*1024)||'';}catch(_cv){}}
    intro=t(intro);if(intro.length>240)intro=intro.slice(0,238)+'…';
    var cleanTags=[];for(var i=0;i<tags.length&&cleanTags.length<8;i++){var q=t(tags[i]);if(q&&cleanTags.indexOf(q)<0)cleanTags.push(q);}
    var h='';
    h+='<div style="padding:1.3em .35em .9em;line-height:1.62;color:inherit;background:transparent;">';
    h+='<div style="text-align:center;font-size:2.35em;font-weight:700;line-height:1.2;margin:.45em 0 2.2em;">版权信息</div>';
    h+='<table style="width:100%;border-collapse:collapse;text-align:center;margin:0 0 1.35em;"><tr>';
    h+='<td style="width:33.33%;padding:.2em .1em;"><div style="font-size:1.28em;font-weight:650;">'+e(kind||'作品')+'</div><div style="font-size:.78em;opacity:.58;margin-top:.2em;">类型</div></td>';
    h+='<td style="width:33.33%;padding:.2em .1em;"><div style="font-size:1.28em;font-weight:700;">'+e(date||'—')+'</div><div style="font-size:.78em;opacity:.58;margin-top:.2em;">'+e(dateLabel||'上架')+'</div></td>';
    h+='<td style="width:33.33%;padding:.2em .1em;"><div style="font-size:1.28em;font-weight:650;">'+e(wm.v)+'</div><div style="font-size:.78em;opacity:.58;margin-top:.2em;">'+e(wm.u+'/'+(status||'连载'))+'</div></td>';
    h+='</tr></table>';
    h+='<div style="border-top:1px solid rgba(128,128,128,.22);margin:.7em 1.6em 1.05em;"></div>';
    h+='<div style="font-size:1.16em;font-weight:500;margin:0 .7em .35em;">支持原创文学，支持正版阅读！</div>';
    if(author)h+='<div style="text-align:right;font-size:1.03em;margin:.15em 1.1em .95em;">— '+e(author)+'</div>';
    h+='<div style="border-top:1px solid rgba(128,128,128,.18);margin:.55em 1.6em 1.0em;"></div>';
    if(intro||coverData){
        h+='<div style="margin:.2em .7em .65em;min-height:'+(coverData?'5.7em':'0')+';overflow:hidden;">';
        if(coverData)h+='<img src="'+e(coverData)+'" width="92" style="float:right;width:92px;height:auto;max-height:124px;object-fit:cover;margin:.05em 0 .45em .8em;border-radius:2px;">';
        if(intro)h+='<div style="font-size:1.05em;line-height:1.78;text-align:justify;">'+e(intro)+'</div>';
        h+='</div>';
    }
    if(cleanTags.length){
        h+='<div style="margin:.5em .7em 1.25em;font-size:1.0em;line-height:1.9;">';
        for(var j=0;j<cleanTags.length;j++)h+='<span style="display:inline-block;margin-right:1.0em;white-space:nowrap;">'+e(cleanTags[j])+'</span>';
        h+='</div>';
    }
    h+='<div style="text-align:center;opacity:.54;font-size:.82em;line-height:1.75;margin:2.2em .4em .2em;">— 本作品由起点中文网进行电子制作与发行 —<br>版权所有 · 侵权必究</div>';
    h+='</div>';
    return h;
}
'''
code=code[:fn_start]+new_render+'\n'+code[fn_end:]

assert code!=old_code
assert '版权信息</div>' in code
assert 'float:right' in code
assert '支持原创文学，支持正版阅读！' in code
assert 'Book ID' not in new_render
assert 'data:image/svg+xml' not in new_render
assert "intro:t(intro||'')" in code
assert 'tags:Array.isArray(tags)?tags:[]' in code

packed='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
pack['copyright']=packed
pack_text=json.dumps(pack,ensure_ascii=False,separators=(',',':'))
s['jsLib']=js[:start]+pack_text+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.5-beta2：版权信息页按真机参考图重做为阅读原生单页风格。去掉大白卡和整页 SVG 图片，改为大标题 + 三列核心信息 + 正版声明 + 作者署名 + 可选作者/作品简介、小封面与标签；尽量避免整张大图导致的空白第一页。Stable 1.2.4 的目录、时间/字数/分卷、正文、评论、账号与 Provider 全部冻结。'

# Isolation gates: only display metadata + copyright lazy payload may differ from Stable.
for k,v in stable.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v, 'unexpected stable field changed: '+k
assert s['ruleToc']==stable['ruleToc']
assert s['ruleBookInfo']==stable['ruleBookInfo']
assert s['ruleContent']==stable['ruleContent']
assert s['bookSourceUrl']==stable['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.5-beta2：版权信息页按参考图改为阅读原生单页风格，目录与其它稳定业务全部冻结。'
tags=['起点','测试版','版权信息','单页排版','作者简介','标签','Stable 1.2.4基线']
changes=[
 '版权信息页从整页 SVG 图片改为可分页的原生 HTML 排版，避免大图被阅读整体挪到下一页造成第一页空白',
 '版式按真机参考图重排：顶部大标题、三列类型/日期/字数状态、分隔线、正版声明与作者署名',
 '复用原有官方 bookDetail 请求补充作品分类/状态，并尝试从同一响应提取作者/作品简介与标签，不新增网络请求',
 '简介区域使用右侧小封面，标签以纯文本横向换行展示；不再显示 Book ID，不使用大白卡片',
 'Stable 1.2.4 已确认的目录时间/字数/分卷、正文、评论、账号、Provider 全部冻结'
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
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'版权信息单页'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'本版范围','text':'只优化版权信息页；Stable 1.2.4 的目录请求、时间/字数/分卷、正文与评论链全部冻结。'},
 {'title':'参考图版式','text':'去掉大白卡与整页大封面，改成大标题 + 三列核心数据 + 正版声明 + 作者署名；作者/作品简介存在时在下方展示，并把小封面放在简介右侧。'},
 {'title':'空白第一页修复','text':'beta1 把整个版权页做成不可拆分的大 SVG 图片，阅读分页时可能整体推到第二页。beta2 改为普通 HTML 文本和一个小封面，允许阅读正常分页。'},
 {'title':'数据来源','text':'继续使用原 copyright 官方数据模型；分类、状态、简介、标签都从原 bookDetail 同一次响应里归一化，不增加新请求。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'
release=(f"## 2026-09-14 · qidian-next {VERSION} — 版权信息阅读原生单页版\n"
'- 根据用户真机参考图，将版权信息从“大白卡 + 整页 SVG 大图”改为阅读原生 HTML 排版。\n'
'- 顶部大标题；中部三列显示类型 / 上架或首发日期 / 字数与连载状态；下方为正版声明、作者署名。\n'
'- 作者/作品简介与标签从现有官方 bookDetail 同一次响应提取；简介右侧使用小封面，不新增网络请求。\n'
'- beta1 的空白第一页风险来自不可拆分的大 SVG 图片，本版移除整页 SVG，仅保留小封面。\n'
'- Stable 1.2.4 及目录/正文/评论/账号/Provider 不变，等待真机确认。\n\n')
rp.write_text(release+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
hand=(f"## 2026-09-14 · {VERSION} — 版权信息参考图单页版\n\n"
'- 用户要求版权页参考真机第三张图：大标题、三列数据、正版声明、作者署名、简介+右侧小封面、标签、底部版权文案。\n'
'- beta2 从 Stable 1.2.4 重建，只修改 copyright 懒模块和 Beta 展示元数据；不继承其它未确认运行时改动。\n'
'- 关键修复：取消整页 SVG 大图，改普通 HTML，目标是消除 beta1 的 1/2 空白第一页。\n'
'- 官方数据获取仍为现有 bookDetail；只在同一响应上补分类/状态/简介/标签归一化，不增加请求。\n'
'- 未经真机确认不得晋升 Stable。\n\n')
hp.write_text(hand+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-125b2-report.json'
report.write_text(json.dumps({'version':VERSION,'versionCode':VC,'betaSha256':sha,'stableRuleTocFrozen':True,'stableRuleBookInfoFrozen':True,'stableRuleContentFrozen':True,'bookSourceUrlFrozen':True,'copyrightModuleOnly':True,'wholePageSvgRemoved':True,'htmlSinglePageLayout':True,'noExtraNetworkRequest':True,'features':['large title','3-column metrics','copyright statement','author signature','optional intro','small cover','tags']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
