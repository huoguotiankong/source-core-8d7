import json, hashlib
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.4-beta7'; VC=12047; TS='2026-09-14T20:30:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

arr=json.loads(STABLE.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
assert s.get('bookSourceUrl')==IDENTITY
stable=json.loads(json.dumps(s,ensure_ascii=False))

# Exact request/signing behavior proven by the minimal diagnostic source, isolated under qfMin1247* names.
helper=r'''
/* 1.2.4-beta7: catalog lifecycle repair.
 * The minimal diagnostic source proved Argus v1 + QDSign/QDInfo works on-device.
 * Important integration detail: qidian-next has a non-empty ruleBookInfo.init, so the direct
 * toc URL must be generated inside that init while the resolved bid is still available.
 */
var QF_MIN1247_KEY1='{1dYgqE)h9,R)hKqEcv4]k[h';
var QF_MIN1247_IV1='01234567';
var QF_MIN1247_KEY2='0821CAAD409B84020821CAAD';
var QF_MIN1247_IV2='\0\0\0\0\0\0\0\0';
var QF_MIN1247_BRANDS=['realme','OPPO','Xiaomi','vivo','HUAWEI','samsung','Google','HONOR'];
var QF_MIN1247_MODELS=['RMX3366','PHY120','24030PN60C','V2324A','ALN-AL10','SM-S9280','Pixel 4 XL','MAA-AN10'];
var QF_MIN1247_RND=Math.floor(Math.random()*8);
var QF_MIN1247_BRAND=QF_MIN1247_BRANDS[QF_MIN1247_RND];
var QF_MIN1247_MODEL=QF_MIN1247_MODELS[QF_MIN1247_RND];
function qfMin1247PadKey24(k){while(k.length<24)k+='\0';return k;}
function qfMin1247Pad3(n){n=String(n);while(n.length<3)n='0'+n;return n;}
function qfMin1247RandomHex(n){var s='';for(var i=0;i<n;i++)s+=Math.floor(Math.random()*16).toString(16);return s;}
function qfMin1247Des3(dataStr,key,iv){var cipher=this.java.createSymmetricCrypto('DESede/CBC/PKCS5Padding',key,iv);return cipher.encryptBase64(dataStr);}
function qfMin1247SignToc(which,bookId){
    var ts=new Date().getTime();
    var now=new Date(ts+8*3600*1000);
    var ymdhm=now.getUTCFullYear()+qfMin1247Pad3(now.getUTCMonth()+1)+qfMin1247Pad3(now.getUTCDate())+qfMin1247Pad3(now.getUTCHours())+qfMin1247Pad3(now.getUTCMinutes());
    var qimei=ymdhm+qfMin1247Pad3(ts%1000)+qfMin1247RandomHex(12);
    var params={'bookid':String(bookId||'')};
    var ks=Object.keys(params).sort(),ps=[];
    for(var i=0;i<ks.length;i++)ps.push(ks[i]+'='+params[ks[i]]);
    var md5p=this.java.md5Encode(ps.join('&').toLowerCase());
    if(which==='QDSign'){
        var p1='Rv1rPTnczce|'+ts+'|0|'+qimei+'||||'+md5p+'|f189adc92b816b3e9da29ea304d4a7e4';
        return qfMin1247Des3.call(this,p1,qfMin1247PadKey24(QF_MIN1247_KEY1),QF_MIN1247_IV1);
    }
    if(which==='QDInfo'){
        var p2=qimei+'|7.9.378|1080|1184|1000009|10|1|'+QF_MIN1247_MODEL+'|1436|1000009|4|0|'+ts+'|1|'+qimei+'|||||0';
        return qfMin1247Des3.call(this,p2,qfMin1247PadKey24(QF_MIN1247_KEY2),QF_MIN1247_IV2);
    }
    if(which==='tstamp')return ts;
    if(which==='UA')return 'Mozilla/mobile QDReaderAndroid/7.9.378/1436/1000009/'+QF_MIN1247_BRAND;
    return '';
}
function qfMin1247TocUrl(bookId){
    var bid=String(bookId||'');
    if(!bid)throw new Error('QF catalog beta7: missing bookId in bookInfo.init');
    var url='https://druidv6.if.qidian.com/argus/api/v1/chapterlist/chapterlist?bookId='+bid;
    var opt={'headers':{
        'QDSign':qfMin1247SignToc.call(this,'QDSign',bid),
        'QDInfo':qfMin1247SignToc.call(this,'QDInfo',bid),
        'tstamp':String(qfMin1247SignToc.call(this,'tstamp',bid)),
        'User-Agent':qfMin1247SignToc.call(this,'UA',bid),
        'Content-Type':'application/json'
    }};
    return url+','+JSON.stringify(opt);
}
function qfMin1247TocParse(raw,baseUrl){
    var root=JSON.parse(String(raw||'{}'));
    var chapters=root&&root.Data&&Array.isArray(root.Data.Chapters)?root.Data.Chapters:[];
    if(!chapters.length)throw new Error('QF catalog beta7: Data.Chapters empty');
    var bid='';
    try{var m=String(baseUrl||'').match(/[?&]bookId=(\d+)/i);if(m)bid=m[1];}catch(_m){}
    if(!bid)try{bid=String(root.Data.BookId||'');}catch(_b){}
    if(!bid)throw new Error('QF catalog beta7: response has no bookId');
    var out=[];
    for(var i=0;i<chapters.length;i++){
        var item=chapters[i]||{};
        var title=String(item.N||'').trim();
        if(!title||title.indexOf('版权信息')!==-1)continue;
        var cid=String(item.C||'').trim();
        if(!cid)continue;
        var sj='';
        if(item.T!==undefined&&item.T!==null&&String(item.T)!==''){
            try{sj=String(this.java.timeFormat(item.T)||'');}catch(_t){sj=String(item.T);}
        }
        if(item.W!==undefined&&item.W!==null&&String(item.W)!=='')sj+=(sj?' ':'')+String(item.W)+'字';
        var vip=item.V===undefined?0:item.V;
        out.push({
            N:title,
            C:'https://www.qidian.com/chapter/'+bid+'/'+cid,
            V:vip,
            Vo:0,
            T:sj
        });
    }
    if(!out.length)throw new Error('QF catalog beta7: no valid chapters');
    return out;
}
'''
assert 'qfMin1247TocUrl' not in s['jsLib']
s['jsLib']=s['jsLib']+'\n'+helper

# qidian-next's ruleBookInfo.init normalizes the original detail payload into `info`.
# Generate the proven direct catalog URL HERE, while `bid` still exists. This is the key
# difference from failed beta5, which replaced ruleBookInfo.tocUrl after init and could lose bid.
old="""var qfTocLocalV71='';\ntry{var qfj71=qfJava(this);if(bid&&qfj71&&qfj71.base64Encode)qfTocLocalV71='data:;base64,'+qfj71.base64Encode('qf-toc-v71:'+bid)+',{\\\"type\\\":\\\"qfTocV71\\\"}';}catch(_t71){}\ninfo.tocUrl=bid?(qfTocLocalV71||('https://m.qidian.com/book/'+bid+'/catalog/')):String(baseUrl||'');"""
new="""var qfTocLocalV71='';\ntry{if(bid)qfTocLocalV71=qfMin1247TocUrl.call(this,bid);}catch(_t71){qfTocLocalV71='';}\ninfo.tocUrl=bid?qfTocLocalV71:String(baseUrl||'');"""
count=s['ruleBookInfo']['init'].count(old)
assert count==1, f'bookInfo.init toc block match count={count}'
s['ruleBookInfo']['init']=s['ruleBookInfo']['init'].replace(old,new,1)

s['ruleToc']=dict(s['ruleToc'])
s['ruleToc']['chapterList']="<js>\nqfMin1247TocParse.call(this,result,baseUrl);\n</js>"
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceComment']='v1.2.4-beta7：目录生命周期修复。最小诊断源已真机确认 Argus v1 + QDSign/QDInfo 能正常返回目录，因此上游接口与签名可用。此前 beta5 失败的关键差异是 qidian-next 存在 ruleBookInfo.init：beta5 在 init 之后生成 tocUrl，可能已经拿不到原始 Data.BookId；本版改为在 init 内已解析出 bid 时直接生成已验证的 Argus v1 目录请求，再由 ruleToc 只解析 Data.Chapters。正文、评论、账号、搜索、详情主体、Provider 全部保持 Stable 1.2.2。目录同时显示 T + W 字数。'

# Isolation checks: only jsLib, ruleBookInfo.init, ruleToc.chapterList and display fields may change.
for k,v in stable.items():
    if k in ('jsLib','ruleBookInfo','ruleToc','bookSourceName','bookSourceComment'): continue
    assert s.get(k)==v, 'unexpected changed field: '+k
for k,v in stable['ruleBookInfo'].items():
    if k=='init': continue
    assert s['ruleBookInfo'].get(k)==v, 'unexpected ruleBookInfo change: '+k
for k,v in stable['ruleToc'].items():
    if k=='chapterList': continue
    assert s['ruleToc'].get(k)==v, 'unexpected ruleToc change: '+k
assert s['ruleBookInfo']['tocUrl']=='$.tocUrl'
assert 'qfMin1247TocUrl.call(this,bid)' in s['ruleBookInfo']['init']
assert 'qfMin1247TocParse.call(this,result,baseUrl)' in s['ruleToc']['chapterList']
assert 'argus/api/v1/chapterlist/chapterlist' in s['jsLib']
assert s['ruleContent']==stable['ruleContent']

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.4-beta7：按真机通过的最小目录链修复 qidian-next 的 bookInfo.init → tocUrl 生命周期。'
tags=['起点','测试版','目录修复','Argus v1','生命周期','章节字数']
changes=[
 '最小诊断源真机确认能正常显示目录，证明 Argus v1 与 QDSign/QDInfo 在当前阅读环境可用',
 '定位此前 beta5 的集成差异：qidian-next 存在非空 ruleBookInfo.init，init 后再生成 tocUrl 可能丢失原始 Data.BookId',
 '本版在 ruleBookInfo.init 已得到 bid 时直接生成已验证的 Argus v1 tocUrl，保留原 $.tocUrl 取值方式',
 'ruleToc 直接解析 Data.Chapters，并输出 N/C/V/T/W；T 同时显示章节时间与官方字数',
 '正文、评论、账号、搜索、详情主体、情无/小雨及其它 Provider 全部保持 Stable 1.2.2'
]

def entry(old,typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json'})
    if typed:e['type']='novel'
    return e

mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
ok=False
for i,e in enumerate(m.get('sources',[])):
    if isinstance(e,dict) and e.get('id')=='qidian-next-beta':
        ne=entry(e); ne['category']='novel'; ne['artifactType']='bookSource'; ne['bookSourceUrl']=IDENTITY; m['sources'][i]=ne; ok=True; break
assert ok
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

for path,typed in [(ROOT/'subscription/beta.json',False),(ROOT/'subscription/novel.json',True)]:
    d=json.loads(path.read_text(encoding='utf-8')); d['updatedAt']=TS; d['generatedAt']=TS; ok=False
    for i,e in enumerate(d.get('items',[])):
        if isinstance(e,dict) and e.get('id')=='qidian-next-beta': d['items'][i]=entry(e,typed); ok=True; break
    assert ok, str(path)
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bp=ROOT/'bundles/all-beta.json'; ba=json.loads(bp.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr; ok=False
for i,o in enumerate(ba):
    if isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY: ba[i]=src; ok=True; break
if not ok: ba.insert(0,src)
bp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'目录生命周期','Argus v1'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'真机结论','text':'独立最小目录源可以正常显示目录，当前阅读环境中的 Argus v1 与 QDSign/QDInfo 本身可用。'},
 {'title':'根因修正','text':'qidian-next 会先执行 ruleBookInfo.init。此前 beta5 在 init 后再生成 tocUrl，和最小源的生命周期不同；本版改为在 init 已解析出 bookId 时直接生成 tocUrl。'},
 {'title':'目录输出','text':'直接解析 Data.Chapters，保留章节名、章节链接、VIP 标记、更新时间，并将官方 W 字数字段合并到更新时间显示。'},
 {'title':'冻结范围','text':'正文、评论、账号、搜索、详情主体、Provider 与其它运行模块继续沿用 Stable 1.2.2。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'
release=(f"## 2026-09-14 · qidian-next {VERSION} — 目录生命周期修复\n"
'- 用户真机确认独立最小目录源可以正常显示目录，证明 Argus v1 + QDSign/QDInfo 当前可用。\n'
'- 根因进一步收敛到 qidian-next 的 `ruleBookInfo.init → tocUrl` 生命周期；此前 beta5 在 init 后生成直连 tocUrl，和最小源执行上下文不同。\n'
'- 本版在 `ruleBookInfo.init` 已解析出 `bid` 时生成 Argus v1 目录请求，`ruleBookInfo.tocUrl` 仍保持 `$.tocUrl`。\n'
'- `ruleToc` 直接解析 `Data.Chapters` 的 `N/C/V/T/W`，并显示时间 + 官方章节字数。\n'
'- 正文、评论、账号、搜索、详情主体、Provider 全部冻结；Stable 1.2.2 不改。\n\n')
rp.write_text(release+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
hand=(f"## 2026-09-14 · {VERSION} — 当前目录测试\n"
'- 真机证据：最小目录诊断源可正常显示目录。\n'
'- 当前 Beta：在 Stable 1.2.2 上仅集成已验证 Argus v1 目录链，关键是把 tocUrl 生成放入 `ruleBookInfo.init` 内，避免 init 后丢失原始 bookId 上下文。\n'
'- 目录输出：`N/C/V/T/W`；时间 + 字数。\n'
'- 冻结：正文、Review、账号、搜索、详情主体、Provider。\n'
'- 未真机确认前不得晋升 Stable。\n\n')
hp.write_text(hand+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-124b7-report.json'
report.write_text(json.dumps({
 'version':VERSION,'stableSha256':hashlib.sha256(STABLE.read_bytes()).hexdigest(),'betaSha256':sha,
 'integration':'Argus v1 toc URL generated inside ruleBookInfo.init while bid exists',
 'ruleBookInfoTocUrl':s['ruleBookInfo']['tocUrl'],
 'ruleTocChapterList':s['ruleToc']['chapterList'],
 'ruleContentFrozen':s['ruleContent']==stable['ruleContent']
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('built',VERSION,sha)
