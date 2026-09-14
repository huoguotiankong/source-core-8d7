import json, hashlib
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
OUT=ROOT/'sources/novel/qidian-next/qidian-next-toc-phase-diag.json'
REPORT=ROOT/'.staging/qidian-toc-phase-diag-report.json'

arr=json.loads(STABLE.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
stable=json.loads(json.dumps(s,ensure_ascii=False))

helper=r'''
/* qidian toc phase diagnostic: exact minimal-source Argus v1 signing, isolated names */
var QF_PD_KEY1='{1dYgqE)h9,R)hKqEcv4]k[h';
var QF_PD_IV1='01234567';
var QF_PD_KEY2='0821CAAD409B84020821CAAD';
var QF_PD_IV2='\0\0\0\0\0\0\0\0';
var QF_PD_BRANDS=['realme','OPPO','Xiaomi','vivo','HUAWEI','samsung','Google','HONOR'];
var QF_PD_MODELS=['RMX3366','PHY120','24030PN60C','V2324A','ALN-AL10','SM-S9280','Pixel 4 XL','MAA-AN10'];
var QF_PD_RND=Math.floor(Math.random()*8),QF_PD_BRAND=QF_PD_BRANDS[QF_PD_RND],QF_PD_MODEL=QF_PD_MODELS[QF_PD_RND];
function qfPdPadKey24(k){while(k.length<24)k+='\0';return k}
function qfPdPad3(n){n=String(n);while(n.length<3)n='0'+n;return n}
function qfPdRandomHex(n){var s='';for(var i=0;i<n;i++)s+=Math.floor(Math.random()*16).toString(16);return s}
function qfPdDes3(dataStr,key,iv){var cipher=this.java.createSymmetricCrypto('DESede/CBC/PKCS5Padding',key,iv);return cipher.encryptBase64(dataStr)}
function qfPdSignToc(which,bookId){
  var ts=new Date().getTime(),now=new Date(ts+8*3600*1000);
  var ymdhm=now.getUTCFullYear()+qfPdPad3(now.getUTCMonth()+1)+qfPdPad3(now.getUTCDate())+qfPdPad3(now.getUTCHours())+qfPdPad3(now.getUTCMinutes());
  var qimei=ymdhm+qfPdPad3(ts%1000)+qfPdRandomHex(12),params={'bookid':String(bookId||'')},ks=Object.keys(params).sort(),ps=[];
  for(var i=0;i<ks.length;i++)ps.push(ks[i]+'='+params[ks[i]]);
  var md5p=this.java.md5Encode(ps.join('&').toLowerCase());
  if(which==='QDSign')return qfPdDes3.call(this,'Rv1rPTnczce|'+ts+'|0|'+qimei+'||||'+md5p+'|f189adc92b816b3e9da29ea304d4a7e4',qfPdPadKey24(QF_PD_KEY1),QF_PD_IV1);
  if(which==='QDInfo')return qfPdDes3.call(this,qimei+'|7.9.378|1080|1184|1000009|10|1|'+QF_PD_MODEL+'|1436|1000009|4|0|'+ts+'|1|'+qimei+'|||||0',qfPdPadKey24(QF_PD_KEY2),QF_PD_IV2);
  if(which==='tstamp')return ts;
  if(which==='UA')return 'Mozilla/mobile QDReaderAndroid/7.9.378/1436/1000009/'+QF_PD_BRAND;
  return '';
}
function qfPdTocUrl(bookId){
  var bid=String(bookId||'');if(!bid)throw new Error('QF phase diag: missing bookId');
  var url='https://druidv6.if.qidian.com/argus/api/v1/chapterlist/chapterlist?bookId='+bid;
  var opt={'headers':{'QDSign':qfPdSignToc.call(this,'QDSign',bid),'QDInfo':qfPdSignToc.call(this,'QDInfo',bid),'tstamp':String(qfPdSignToc.call(this,'tstamp',bid)),'User-Agent':qfPdSignToc.call(this,'UA',bid),'Content-Type':'application/json','Accept':'application/json'}};
  return url+','+JSON.stringify(opt);
}
'''
assert 'qfPdTocUrl' not in s['jsLib']
s['jsLib']=s['jsLib']+'\n'+helper

init=s['ruleBookInfo']['init']
needle='JSON.stringify(info);'
assert init.count(needle)==1, f'final JSON stringify count={init.count(needle)}'
init=init.replace(needle,"try{info.qfDiagBid=String(bid||'');}catch(_qfDiagBid){info.qfDiagBid='';}\n"+needle,1)
s['ruleBookInfo']=dict(s['ruleBookInfo'])
s['ruleBookInfo']['init']=init
s['ruleBookInfo']['tocUrl']="""@js:\n(function(){\n var bid='';\n try{var o=JSON.parse(String(result||'{}'));bid=String(o.qfDiagBid||o.bookId||o.BookId||'');}catch(e){}\n if(!bid)try{bid=String(java.get('bookId')||'');}catch(e2){}\n if(!bid){var m=String(baseUrl||'').match(/[?&]bookId=(\\d+)/i);if(m)bid=m[1];}\n if(!bid)throw new Error('QF phase diag: tocUrl phase missing bid');\n return qfPdTocUrl.call(this,bid);\n})()"""

s['ruleToc']={
  'chapterList':"""@js:\nvar root=JSON.parse(String(result||'{}'));\nvar chapters=root&&root.Data&&Array.isArray(root.Data.Chapters)?root.Data.Chapters:[];\nif(!chapters.length)throw new Error('QF phase diag: Data.Chapters empty');\nvar bm=String(baseUrl||'').match(/[?&]bookId=(\\d+)/i),bid=bm?bm[1]:'';\nif(!bid)try{bid=String(root.Data.BookId||'');}catch(_b){}\nvar out=[];\nfor(var i=0;i<chapters.length;i++){var item=chapters[i]||{},title=String(item.N||'').trim();if(!title||title.indexOf('版权信息')!==-1)continue;var cid=String(item.C||'').trim();if(!cid)continue;var sj='';if(item.T&&item.W)sj=java.timeFormat(item.T)+' '+String(item.W)+'字';out.push({title:title,url:'https://www.qidian.com/chapter/'+bid+'/'+cid,sj:sj,vip:item.V||0});}\nout""",
  'chapterName':'title','chapterUrl':'url','isPay':'vip','isVip':'vip','isVolume':'','nextTocUrl':'','updateTime':'sj'
}

s['bookSourceName']='🧪 起点增强 · 目录阶段诊断'
s['bookSourceGroup']='﹅🧪 目录诊断'
s['bookSourceUrl']='https://m.qidian.com/?qf_source=qidian_next_toc_phase_diag_1248'
s['bookSourceComment']='目录阶段诊断：完整保留 Stable 1.2.2 业务代码，仅在 ruleBookInfo.init 末尾保存 bid；真正的 Argus v1 QDSign/QDInfo 请求延迟到 ruleBookInfo.tocUrl 阶段生成，尽量复刻已真机通过的最小目录源执行时机。活动 Beta/Stable 均不修改。'

# hard isolation
for k,v in stable.items():
    if k in ('jsLib','ruleBookInfo','ruleToc','bookSourceName','bookSourceGroup','bookSourceUrl','bookSourceComment'):continue
    assert s.get(k)==v, 'unexpected changed field '+k
for k,v in stable['ruleBookInfo'].items():
    if k in ('init','tocUrl'):continue
    assert s['ruleBookInfo'].get(k)==v, 'unexpected bookInfo field '+k
assert s['ruleContent']==stable['ruleContent']

OUT.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
REPORT.write_text(json.dumps({'stableSha256':hashlib.sha256(STABLE.read_bytes()).hexdigest(),'diagSha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'identity':s['bookSourceUrl'],'changedTopFields':['jsLib','ruleBookInfo.init','ruleBookInfo.tocUrl','ruleToc','display identity'],'ruleContentFrozen':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('built',OUT)
