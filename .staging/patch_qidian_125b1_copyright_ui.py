import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.5-beta1'; VC=12051; TS='2026-09-14T21:24:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

arr=json.loads(STABLE.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
stable=json.loads(json.dumps(s,ensure_ascii=False))

# Parse QF_MOD38_PACK with a brace/string aware scanner because some raw module strings contain "};".
js=str(s.get('jsLib',''))
mark='var QF_MOD38_PACK='
p=js.find(mark)
assert p>=0, 'QF_MOD38_PACK not found'
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
assert end>start, 'QF_MOD38_PACK end not found'
pack=json.loads(js[start:end])
raw=pack['copyright']
assert raw.startswith('gz:'), 'copyright module is expected to be gzip packed'
b64=raw[3:] + '=' * (-len(raw[3:])%4)
code=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
old_code=code

fn_start=code.index('function qfCopyrightRender(model){')
fn_end=code.index('function qdCopyrightV2929',fn_start)
new_render=r'''function qfCopyrightRender(model){
    model=model&&typeof model==='object'?model:{};
    var bid=String(model.bookId||''),name=String(model.title||'本书'),author=String(model.author||''),kind=String(model.category||'作品'),status=String(model.status||'连载'),date=String(model.publishDate||'—'),dateLabel=String(model.publishLabel||'上架'),num=String(model.wordCountWan||'—'),rawWords=String(model.wordCountRaw||''),cover=String(model.coverUrl||'');
    function e(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');}
    function t(v){return qfText(String(v==null?'':v)).replace(/\s+/g,' ').trim();}
    function words(){
        var z=t(rawWords),n=Number(z.replace(/[^0-9.]/g,''));
        if(/万/.test(z))return z.replace(/\s+/g,'');
        if(isFinite(n)&&n>0){if(n>=10000){var w=(n/10000).toFixed(n>=1000000?0:1).replace(/\.0$/,'');return w+'万字';}return Math.round(n)+'字';}
        return (num&&num!=='—')?num+'万字':'—';
    }
    var coverData='';
    if(cover){try{coverData=qfCopyrightImageData2929(this,cover,bid?'https://www.qidian.com/book/'+encodeURIComponent(bid)+'/':'https://www.qidian.com/',4*1024*1024)||'';}catch(_cv){}}
    function tx(X,Y,S,F,C,W,A,O){return '<text x="'+X+'" y="'+Y+'" font-size="'+F+'" fill="'+(C||'#252525')+'"'+(W?' font-weight="'+W+'"':'')+(A?' text-anchor="'+A+'"':'')+(O!=null?' opacity="'+O+'"':'')+'>'+e(S)+'</text>';}
    function rect(x,y,w,h,r,fill,stroke){return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="'+r+'" fill="'+fill+'"'+(stroke?' stroke="'+stroke+'"':'')+'/>';}
    function titleText(z){z=t(z)||'本书';var fs=z.length<=8?42:(z.length<=12?37:(z.length<=18?31:27)),max=580;return '<text x="360" y="505" text-anchor="middle" font-size="'+fs+'" font-weight="700" fill="#1f1f1f"'+(z.length>20?' textLength="'+max+'" lengthAdjust="spacingAndGlyphs"':'')+'>'+e(z)+'</text>';}
    function infoCard(x,y,label,value){return rect(x,y,276,104,18,'#ffffff','#ebe7df')+tx(x+20,y+34,label,18,'#9a9184','500','start')+tx(x+20,y+76,value,29,'#2c2925','650','start');}
    var H=1210,W=720;
    var svg='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'">'+
      '<rect width="720" height="1210" fill="#f7f5f1"/>'+
      tx(360,48,'作品版权信息',18,'#9f9486','600','middle',1)+
      '<line x1="292" y1="64" x2="428" y2="64" stroke="#d8d1c7" stroke-width="1"/>'+
      '<defs><filter id="qfshadow" x="-30%" y="-30%" width="160%" height="180%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000000" flood-opacity=".15"/></filter><clipPath id="qfcv125"><rect x="218" y="92" width="284" height="370" rx="10"/></clipPath></defs>'+
      rect(210,84,300,386,14,'#e9e4dc','')+
      (coverData?'<image href="'+e(coverData)+'" xlink:href="'+e(coverData)+'" x="218" y="92" width="284" height="370" preserveAspectRatio="xMidYMid slice" clip-path="url(#qfcv125)" filter="url(#qfshadow)"/>':rect(218,92,284,370,10,'#ebe7e0','')+tx(360,290,'暂无封面',24,'#aaa196','500','middle'))+
      titleText(name)+
      tx(360,544,author?('作者 · '+author):'作者信息暂缺',22,'#70685f','500','middle')+
      infoCard(72,592,'作品类型',kind||'作品')+
      infoCard(372,592,'作品状态',status||'—')+
      infoCard(72,714,dateLabel||'上架',date||'—')+
      infoCard(372,714,'作品字数',words())+
      rect(72,852,576,226,22,'#ffffff','#e8e2d9')+
      tx(100,900,'正版版权声明',22,'#3b3732','700','start')+
      tx(100,946,'支持原创文字，支持正版阅读。',25,'#2d2925','600','start')+
      tx(100,989,'本作品由起点中文网进行电子制作与发行。',19,'#746c63','400','start')+
      tx(100,1025,'版权所有 · 侵权必究',19,'#746c63','400','start')+
      (author?tx(620,1060,'— '+author,19,'#746c63','500','end'):'')+
      (bid?tx(360,1147,'Book ID · '+bid,15,'#aaa096','400','middle'):tx(360,1147,'Qidian Original',15,'#aaa096','400','middle'))+
      '</svg>';
    try{var j=qfJava(this);if(j&&j.base64Encode)return '<img src="data:image/svg+xml;base64,'+j.base64Encode(svg)+'" style="display:block;width:100%;height:auto;margin:0;padding:0;">';}catch(_b){}
    return '<div>'+svg+'</div>';
}
'''
code=code[:fn_start]+new_render+'\n'+code[fn_end:]
assert code!=old_code
assert 'function qfCopyrightData(baseUrl)' in code
assert 'function qfCopyrightRender(model)' in code
assert '作品版权信息' in code and '正版版权声明' in code

packed='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
pack['copyright']=packed
pack_text=json.dumps(pack,ensure_ascii=False,separators=(',',':'))
new_js=js[:start]+pack_text+js[end:]
s['jsLib']=new_js
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.5-beta1：仅优化版权信息页。保留 Stable 1.2.4 已真机确认的目录、时间/字数/分卷、正文、评论、账号与 Provider 全部不变；版权页继续使用官方数据模型，重排为全宽大封面 + 作品信息卡 + 正版版权声明，提升长书名、字数和上架信息的可读性。'

# Isolation gates: only display metadata + copyright lazy module payload may differ from Stable 1.2.4.
for k,v in stable.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v, 'unexpected stable field changed: '+k
assert s['ruleToc']==stable['ruleToc']
assert s['ruleBookInfo']==stable['ruleBookInfo']
assert s['ruleContent']==stable['ruleContent']
assert s['bookSourceUrl']==stable['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.5-beta1：仅重做版权信息页视觉，Stable 1.2.4 目录与其它业务链全部冻结。'
tags=['起点','测试版','版权信息','UI优化','大封面','Stable 1.2.4基线']
changes=[
 '仅修改 copyright 懒模块中的渲染器，不修改目录主链、ruleToc、ruleBookInfo 或 ruleContent',
 '版权页改为全宽固定版式：大封面、书名/作者、类型/状态/上架日期/作品字数四块信息卡',
 '增加独立正版版权声明卡，保留起点电子制作发行与侵权必究文案',
 '封面仍在版权模块内部转 data:image，避免阅读正文里依赖外链图片加载',
 'Stable 1.2.4 已确认的时间/字数/真实分卷/正文/评论/账号/Provider 全部冻结'
]

def beta_entry(old=None,typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    return e

# manifest: upsert active beta next to stable line.
mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
items=m.setdefault('sources',[]); pos=None
for i,e in enumerate(items):
    if isinstance(e,dict) and e.get('id')=='qidian-next-beta': pos=i; break
ne=beta_entry(items[pos] if pos is not None else None); ne['category']='novel'; ne['artifactType']='bookSource'
if pos is None:
    ins=next((i+1 for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next'),len(items)); items.insert(ins,ne)
else: items[pos]=ne
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# beta catalog upsert
bp=ROOT/'subscription/beta.json'; bd=json.loads(bp.read_text(encoding='utf-8')); bd['updatedAt']=TS; bd['generatedAt']=TS
bi=bd.setdefault('items',[]); pos=next((i for i,e in enumerate(bi) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
if pos is None: bi.insert(0,beta_entry())
else: bi[pos]=beta_entry(bi[pos])
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# novel type catalog uses current active channel entry for qidian-next logical source.
np=ROOT/'subscription/novel.json'; nd=json.loads(np.read_text(encoding='utf-8')); nd['updatedAt']=TS; nd['generatedAt']=TS
ni=nd.setdefault('items',[])
ni[:]=[e for e in ni if not (isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'))]
ni.insert(0,beta_entry(typed=True))
np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# beta bundle upsert source identity.
bunp=ROOT/'bundles/all-beta.json'; ba=json.loads(bunp.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr
ba=[o for o in ba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)]
ba.insert(0,src)
bunp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# detail current-state page
dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'版权信息UI'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'本版范围','text':'只优化版权信息页；Stable 1.2.4 的目录请求、时间/字数/分卷、正文与评论链全部冻结。'},
 {'title':'新版版权页','text':'大封面置顶，书名与作者居中；类型、状态、上架/首发日期、作品字数使用四块信息卡；下方独立显示正版版权声明。'},
 {'title':'兼容策略','text':'继续复用 qf.copyright/1 官方数据模型与本地封面转 data:image 逻辑，只替换 renderer，不增加新的业务依赖。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'
release=(f"## 2026-09-14 · qidian-next {VERSION} — 版权信息页视觉优化\n"
'- 基于已真机确认的 Stable 1.2.4，仅修改 `copyright` lazy module 的 renderer。\n'
'- 新版版权页使用全宽大封面、居中书名/作者、类型/状态/日期/字数信息卡和独立正版版权声明。\n'
'- 数据 Provider 与 `qf.copyright/1` 模型保持不变；目录、正文、评论、账号、Provider 全部冻结。\n'
'- 新版继续在模块内将封面转为 `data:image`，避免正文页外链封面加载不稳定。\n'
'- 未经真机确认不得晋升 Stable。\n\n')
rp.write_text(release+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
hand=(f"## 2026-09-14 · {VERSION} — 当前活动 Beta：版权信息页\n\n"
'- Stable 基线仍为 1.2.4；目录主链不得修改。\n'
'- 本版只替换 `copyright` lazy module 的 `qfCopyrightRender`，官方数据获取逻辑保持原样。\n'
'- UI：大封面 + 书名/作者 + 四块作品信息 + 正版版权声明；图片继续内嵌 data URI。\n'
'- `ruleToc` / `ruleBookInfo` / `ruleContent` 与 Stable 1.2.4 精确相等。\n'
'- 等用户真机确认视觉与字段显示后再决定晋升。\n\n')
hp.write_text(hand+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-125b1-report.json'
report.write_text(json.dumps({'version':VERSION,'versionCode':VC,'betaSha256':sha,'stableRuleTocFrozen':s['ruleToc']==stable['ruleToc'],'stableRuleBookInfoFrozen':s['ruleBookInfo']==stable['ruleBookInfo'],'stableRuleContentFrozen':s['ruleContent']==stable['ruleContent'],'bookSourceUrlFrozen':s['bookSourceUrl']==stable['bookSourceUrl'],'copyrightModuleOnly':True,'renderMarkers':['作品版权信息','正版版权声明','作品类型','作品状态','作品字数']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
