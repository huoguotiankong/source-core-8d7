import hashlib, json
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.4-beta5'; VC=12045; TS='2026-09-14T19:45:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

arr=json.loads(STABLE.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
assert s.get('bookSourceUrl')==IDENTITY
stable=json.loads(json.dumps(s,ensure_ascii=False))

helper=r'''
/* 1.2.4-beta5: Qidian Argus v1 direct catalog recovery path.
 * Source reference: the currently working direct chapterlist pattern in 妙想天开.
 * Only catalog request/parsing is replaced. Content/review/provider runtime stays Stable 1.2.2.
 */
var QF_DC1245_KEY1='{1dYgqE)h9,R)hKqEcv4]k[h';
var QF_DC1245_IV1='01234567';
var QF_DC1245_KEY2='0821CAAD409B84020821CAAD';
var QF_DC1245_IV2='\0\0\0\0\0\0\0\0';
function qfDc1245Pad24(k){while(k.length<24)k+='\0';return k;}
function qfDc1245Pad3(n){n=String(n);while(n.length<3)n='0'+n;return n;}
function qfDc1245Hex(n){var s='';for(var i=0;i<n;i++)s+=Math.floor(Math.random()*16).toString(16);return s;}
function qfDc1245Des3(data,key,iv){var c=this.java.createSymmetricCrypto('DESede/CBC/PKCS5Padding',key,iv);return c.encryptBase64(data);}
function qfDc1245SignToc(which,bookId){
  var ts=new Date().getTime();
  var now=new Date(ts+8*3600*1000);
  var ymdhm=now.getUTCFullYear()+qfDc1245Pad3(now.getUTCMonth()+1)+qfDc1245Pad3(now.getUTCDate())+qfDc1245Pad3(now.getUTCHours())+qfDc1245Pad3(now.getUTCMinutes());
  var qimei=ymdhm+qfDc1245Pad3(ts%1000)+qfDc1245Hex(12);
  var md5p=this.java.md5Encode(('bookid='+String(bookId||'')).toLowerCase());
  if(which==='QDSign')return qfDc1245Des3.call(this,'Rv1rPTnczce|'+ts+'|0|'+qimei+'||||'+md5p+'|f189adc92b816b3e9da29ea304d4a7e4',qfDc1245Pad24(QF_DC1245_KEY1),QF_DC1245_IV1);
  if(which==='QDInfo')return qfDc1245Des3.call(this,qimei+'|7.9.378|1080|1184|1000009|10|1|RMX3366|1436|1000009|4|0|'+ts+'|1|'+qimei+'|||||0',qfDc1245Pad24(QF_DC1245_KEY2),QF_DC1245_IV2);
  if(which==='tstamp')return ts;
  if(which==='UA')return 'Mozilla/mobile QDReaderAndroid/7.9.378/1436/1000009/realme';
  return '';
}
function qfDc1245BookId(ctx,baseUrl,raw){
  var bid='';
  try{var m=String(baseUrl||'').match(/\/book\/(\d+)/i);if(m)bid=m[1];}catch(e){}
  if(!bid)try{var m2=String(baseUrl||'').match(/[?&]bookId=(\d+)/i);if(m2)bid=m2[1];}catch(e2){}
  if(!bid)try{var b=qfBook(ctx);if(b&&b.getVariable)bid=String(b.getVariable('qf_bid')||'');}catch(e3){}
  if(!bid)try{var o=JSON.parse(String(raw||'{}'));bid=String((o.Data&&o.Data.BookId)||o.bookId||o.BookId||'');}catch(e4){}
  return bid;
}
function qfDc1245CatalogUrl(ctx,baseUrl,raw){
  var bid=qfDc1245BookId(ctx,baseUrl,raw);
  if(!bid)throw new Error('QF direct catalog: missing bookId');
  var u='https://druidv6.if.qidian.com/argus/api/v1/chapterlist/chapterlist?bookId='+encodeURIComponent(bid);
  var h={
    'QDSign':qfDc1245SignToc.call(ctx,'QDSign',bid),
    'QDInfo':qfDc1245SignToc.call(ctx,'QDInfo',bid),
    'tstamp':String(qfDc1245SignToc.call(ctx,'tstamp',bid)),
    'User-Agent':qfDc1245SignToc.call(ctx,'UA',bid),
    'Content-Type':'application/json',
    'Accept':'application/json'
  };
  return u+','+JSON.stringify({headers:h});
}
function qfDc1245CatalogParse(ctx,raw,baseUrl){
  var root=JSON.parse(String(raw||'{}'));
  var src=root&&root.Data&&Array.isArray(root.Data.Chapters)?root.Data.Chapters:[];
  if(!src.length)throw new Error('QF direct catalog: Data.Chapters empty');
  var bid=qfDc1245BookId(ctx,baseUrl,raw);
  if(!bid){try{bid=String(root.Data.BookId||'');}catch(_e){}}
  var out=[];
  for(var i=0;i<src.length;i++){
    var it=src[i]||{};
    var title=String(it.N||it.ChapterName||it.chapterName||'').trim();
    if(!title||title.indexOf('版权信息')>=0)continue;
    var cid=String(it.C||it.ChapterId||it.chapterId||'').trim();
    if(!cid)continue;
    var vip=(String(it.V||'0')==='0'||String(it.V||'').toLowerCase()==='false')?0:1;
    var t='';
    if(it.T!==undefined&&it.T!==null&&String(it.T)!==''){
      try{t=String(ctx.java.timeFormat(it.T)||'');}catch(_t){t=String(it.T);}
    }
    var w=(it.W!==undefined&&it.W!==null&&String(it.W)!=='')?String(it.W):'';
    if(w)t=(t?t+' ':'')+w+'字';
    var cu='https://www.qidian.com/chapter/'+encodeURIComponent(bid)+'/'+encodeURIComponent(cid)+'?qfVip='+vip+'&qfTitle='+encodeURIComponent(title);
    out.push({N:title,C:cu,V:vip,Vo:0,T:t});
  }
  if(!out.length)throw new Error('QF direct catalog: no valid chapters');
  return out;
}
'''
s['jsLib']=s['jsLib']+'\n'+helper

s.setdefault('ruleBookInfo',{})['tocUrl']="@js:\nqfDc1245CatalogUrl.call(this,this,baseUrl,result);"
s['ruleToc']=dict(s.get('ruleToc') or {})
s['ruleToc']['chapterList']="<js>\nqfDc1245CatalogParse.call(this,this,result,baseUrl);\n</js>"
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceComment']='v1.2.4-beta5：目录主链恢复版。独立身份诊断源复用 Stable 1.2.2 仍无法加载目录，确认问题不在阅读旧缓存/覆盖。目录改为直接使用当前参考源已验证的起点 Argus v1 chapterlist，并在本地解析 N/C/V/T/W；章节 URL 重新接回 qidian-next 既有正文入口，正文、评论、账号、搜索、详情、情无/小雨及所有 Provider 继续沿用 Stable 1.2.2。目录时间同时附带官方 W 字数。'

# Isolation checks.
for k,v in stable.items():
    if k in ('jsLib','ruleBookInfo','ruleToc','bookSourceName','bookSourceComment'): continue
    assert s.get(k)==v, 'unexpected changed field: '+k
for k,v in stable['ruleBookInfo'].items():
    if k=='tocUrl': continue
    assert s['ruleBookInfo'].get(k)==v, 'unexpected ruleBookInfo change: '+k
for k,v in stable['ruleToc'].items():
    if k=='chapterList': continue
    assert s['ruleToc'].get(k)==v, 'unexpected ruleToc change: '+k
assert 'qfDc1245CatalogUrl' in s['jsLib'] and 'qfDc1245CatalogParse' in s['jsLib']
assert 'argus/api/v1/chapterlist/chapterlist' in s['jsLib']

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.4-beta5：目录改走起点 Argus v1 chapterlist 直接链，恢复章节并带时间+字数。'
tags=['起点','测试版','目录恢复','Argus v1','章节字数','直连目录']
changes=[
 '独立身份 Stable 1.2.2 诊断源仍目录空白，排除阅读旧书源身份/目录缓存为主因',
 '目录请求切换到 druidv6 Argus v1 chapterlist 直连链，复用当前参考源已验证的 QDSign/QDInfo 生成方式',
 '直接解析官方 N/C/V/T/W，目录显示更新时间 + W 字数，不增加第二次字数请求',
 '章节 URL 重新映射到 qidian-next 既有 /chapter/{bookId}/{chapterId} 正文入口，正文 Provider 不改',
 '评论、账号、搜索、详情、情无/小雨、本章说和其它 Provider 全部保持 Stable 1.2.2'
]

def entry(old, typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json'})
    if typed:e['type']='novel'
    return e

mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
found=False
for i,e in enumerate(m.get('sources',[])):
    if isinstance(e,dict) and e.get('id')=='qidian-next-beta':
        ne=entry(e); ne['category']='novel'; ne['artifactType']='bookSource'; ne['bookSourceUrl']=IDENTITY; m['sources'][i]=ne; found=True; break
assert found
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

for path,typed in [(ROOT/'subscription/beta.json',False),(ROOT/'subscription/novel.json',True)]:
    d=json.loads(path.read_text(encoding='utf-8')); d['updatedAt']=TS; d['generatedAt']=TS
    ok=False
    for i,e in enumerate(d.get('items',[])):
        if e.get('id')=='qidian-next-beta': d['items'][i]=entry(e,typed); ok=True; break
    assert ok, str(path)
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bp=ROOT/'bundles/all-beta.json'; ba=json.loads(bp.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr
ok=False
for i,o in enumerate(ba):
    if isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY: ba[i]=src;ok=True;break
if not ok: ba.insert(0,src)
bp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'目录恢复','Argus v1'], 'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[{'title':'根因收敛','text':'Stable 1.2.2 的独立身份诊断源重新搜索新书后目录仍为空，说明旧身份/旧书籍缓存不是主因，当前成熟目录链本身已失效。'},{'title':'本版目录','text':'改用起点 Argus v1 chapterlist 直接请求，解析 N/C/V/T/W；更新时间后直接附带官方章节字数。'},{'title':'正文兼容','text':'目录只更换获取与解析，章节链接重新接入 qidian-next 原有正文入口，正文 Provider、评论和账号等运行时不改。'},{'title':'测试重点','text':'确认目录能否恢复、章节数量是否完整、时间+字数是否显示，以及免费/VIP章节能否继续打开正文。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

release=(f"## 2026-09-14 · qidian-next {VERSION} — Argus v1 目录主链恢复\n"+
'- 独立身份、全量复用 Stable 1.2.2 的目录诊断源仍真机失败，排除 Legado 旧身份/旧目录缓存为主要原因。\n'+
'- 目录主链改为 `druidv6.if.qidian.com/argus/api/v1/chapterlist/chapterlist`，参考当前 `妙想天开` 已工作的直接目录方案。\n'+
'- 本地解析 `N/C/V/T/W`；`T + W字` 直接作为目录更新时间展示，不增加额外字数请求。\n'+
'- 章节 URL 映射回 qidian-next 既有 `/chapter/{bookId}/{chapterId}` 正文入口；正文、评论、账号、搜索、详情、情无/小雨和其它 Provider 不改。\n'+
'- Stable 1.2.2 保持不变，等待真机确认目录与正文衔接。\n\n')
rp=ROOT/'docs/RELEASE_LOG.md'; rp.write_text(release+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
hand=(f"## 2026-09-14 · {VERSION} — 当前目录恢复测试\n"+
'- 真机结论：beta4 与独立身份 Stable 1.2.2 诊断源都无法加载目录，因此不要继续把问题归因于旧 Beta 缓存或 review_local_ui。\n'+
'- 当前 Beta 仅替换 Catalog：使用 Argus v1 chapterlist 直连并解析 N/C/V/T/W；正文及其它模块保持 Stable 1.2.2。\n'+
'- 真机下一步：先确认目录恢复与章节完整度，再确认免费/VIP正文衔接；未确认前不得晋升 Stable。\n\n')
hp.write_text(hand+hp.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps({'version':VERSION,'sha256':sha,'chaptersParser':'N/C/V/T/W','url':RAW},ensure_ascii=False))
