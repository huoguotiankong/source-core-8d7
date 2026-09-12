import json,hashlib
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
EXPECTED='1ee474c209b48d069344ffa4409379a0d39012cbaf2acecbd5ffcaba5404ab7e'
VERSION='1.2.2-beta1';VC=12021;NOW='2026-09-12T18:36:00+08:00';TODAY='2026-09-12'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/bookSource?src='+RAW
raw=STABLE.read_bytes();stable_sha=hashlib.sha256(raw).hexdigest()
if stable_sha!=EXPECTED:raise SystemExit('Stable baseline changed: '+stable_sha)
arr=json.loads(raw.decode());s=arr[0] if isinstance(arr,list) else arr;js=s['jsLib']

def replace_fn(text,name,new):
 p=text.find('function '+name)
 if p<0:raise SystemExit('function missing: '+name)
 b=text.find('{',p);dep=0;ins=None;esc=False
 for i in range(b,len(text)):
  c=text[i]
  if ins:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==ins:ins=None
   continue
  if c in "'\"`":ins=c;continue
  if c=='{':dep+=1
  elif c=='}':
   dep-=1
   if dep==0:return text[:p]+new+text[i+1:]
 raise SystemExit('unterminated '+name)

COUNTS=r'''function qfQwReviewCountsV1214(ctx,bid,cid){
  var out={ok:false,list:[],title:null,chapter:0,rawCount:0};
  var url='https://full.hnxianxin.cn/qd/review.php?bookId='+encodeURIComponent(bid)+'&chapterId='+encodeURIComponent(cid),raw='';
  try{
    raw=qfQwAjaxV1214(ctx,url);
    if(!raw){try{ctx.java.log('[QW-RV] empty_response bid='+bid+' cid='+cid)}catch(_0){}return out;}
    var j=JSON.parse(raw||'{}'),d=[];
    try{
      var a=(j.Data&&j.Data.Getparagraphscommentcounts)||(j.data&&j.data.Getparagraphscommentcounts)||j.Getparagraphscommentcounts||j.getparagraphscommentcounts||{};
      d=a.DataList||a.dataList||a.List||a.list||j.DataList||j.dataList||[];
      if(!Array.isArray(d)&&Array.isArray(a))d=a;
      if(!Array.isArray(d))d=[];
    }catch(_1){d=[];}
    out.rawCount=d.length;
    for(var i=0;i<d.length;i++){
      var x=d[i]||{},rp=(x.ParagraphId!==undefined?x.ParagraphId:x.paragraphId),pid=Number(rp);
      var rc=(x.CommentCount!==undefined?x.CommentCount:(x.commentCount!==undefined?x.commentCount:(x.TextCount!==undefined?x.TextCount:x.textCount)));
      var cnt=Number(rc||0)||0;
      if(pid===-1&&cnt>0)out.title=x;
      if(pid>0&&cnt>0){x.__qfCount=cnt;out.list.push(x);}
    }
    out.ok=d.length>0;out.chapter=0;
    try{ctx.java.log('[QW-RV] rows='+d.length+' para='+out.list.length+' title='+(out.title?1:0)+' bid='+bid+' cid='+cid)}catch(_2){}
  }catch(e){try{ctx.java.log('[QW-RV] parse_fail '+e+' bid='+bid+' cid='+cid)}catch(_3){}}
  return out;
}'''

DECORATE=r'''function qfQwDecorateV1214(ctx,content,bid,cid,localTitleBubble){
  var c=qfQwReviewCountsV1214(ctx,bid,cid);
  if(!c.ok)return {content:content,titleBubble:localTitleBubble||'',server:false};
  var lines=String(content||'').replace(/\\r/g,'').split('\n');
  var list=c.list.slice(0);list.sort(function(a,b){return Number(a.ParagraphId||a.paragraphId)-Number(b.ParagraphId||b.paragraphId);});
  var fix=0,pos=0,mapped=0,miss=[];
  for(var j=0;j<list.length;j++){
    var x=list[j]||{},pid=Number(x.ParagraphId!==undefined?x.ParagraphId:x.paragraphId);
    if(!(pid>0))continue;
    var target=pid-1+fix;
    while(pos<lines.length&&pos<=target){if(String(lines[pos]||'').indexOf('<img')>=0){fix++;target=pid-1+fix;}pos++;}
    if(target>=0&&target<lines.length&&String(lines[target]||'').trim()){
      var cnt=Number(x.__qfCount||(x.CommentCount!==undefined?x.CommentCount:(x.commentCount!==undefined?x.commentCount:(x.TextCount||x.textCount||0))))||0;
      var marker='qfQw:'+bid+':'+cid+':'+pid;
      if(String(lines[target]).indexOf(marker)<0)lines[target]+=qfQwBubbleV1214(ctx,cnt,bid,cid,pid);
      mapped++;
    }else miss.push(pid);
  }
  try{ctx.java.log('[QW-RV] map mapped='+mapped+' miss='+miss.length+(miss.length?' ids='+miss.slice(0,12).join(','):'')+' lines='+lines.length+' bid='+bid+' cid='+cid)}catch(_e){}
  /* ParagraphId=-1 只用于诊断：章名评论继续保留起点本地气泡，不再冒充本章说。 */
  return {content:lines.join('\n'),titleBubble:localTitleBubble||'',server:true};
}'''

js=replace_fn(js,'qfQwReviewCountsV1214',COUNTS);js=replace_fn(js,'qfQwDecorateV1214',DECORATE);s['jsLib']=js
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceComment']='v1.2.2-beta1：仅修复情无/小雨服务器段评映射。按起点X-QD逻辑，ParagraphId 使用“段号-1+图片补偿”定位正文，点击继续携带服务器原始 ParagraphId；ParagraphId=-1 不再覆盖起点本地章名评论，也不再冒充本章说。Stable 1.2.1、正文链及其它功能域冻结。'
BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
entry={'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','category':'novel','artifactType':'bookSource','channel':'beta','version':VERSION,'versionCode':VC,'updatedAt':TODAY,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'summary':'Beta1：仅修复情无/小雨服务器段评气泡映射；章名评论继续保持起点本地。Stable 1.2.1 与正文链冻结。','tags':['起点','测试版','情无','小雨服务器','段评','ParagraphId','章名评论本地','正文冻结'],'changelog':['段评 ParagraphId 改为段号-1并按正文图片数动态补偿','气泡点击继续传服务器原始 ParagraphId','ParagraphId=-1 不再覆盖本地章名评论，也不再作为本章说','增加低开销 QW-RV 计数/映射诊断日志','Stable 1.2.1、正文链、目录、搜索、账号及其它 Provider 不变'],'sha256':sha}
def isbeta(x):return isinstance(x,dict) and (x.get('id')=='qidian-next-beta' or (x.get('id')=='qidian-next' and x.get('channel')=='beta'))
mp=ROOT/'manifest.json';m=json.loads(mp.read_text());src=m.setdefault('sources',[]);src[:]=[x for x in src if not isbeta(x)];idx=next((i+1 for i,x in enumerate(src) if isinstance(x,dict) and x.get('id')=='qidian-next' and x.get('channel')=='stable'),len(src));src.insert(idx,dict(entry));m['updatedAt']=NOW;mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
sp=ROOT/'subscription/beta.json';sub=json.loads(sp.read_text());items=sub.setdefault('items',[]);items[:]=[x for x in items if not isbeta(x)];se=dict(entry);se.pop('category',None);se.pop('artifactType',None);se['detailUrl']='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json';ii=next((i+1 for i,x in enumerate(items) if isinstance(x,dict) and x.get('id')=='qidian-official'),0);items.insert(ii,se);sub['updatedAt']=NOW;sub['generatedAt']=NOW;sp.write_text(json.dumps(sub,ensure_ascii=False,indent=2)+'\n')
bp=ROOT/'bundles/all-beta.json'
try:bd=json.loads(bp.read_text() or '[]')
except:bd=[]
if not isinstance(bd,list):bd=bd.get('items',[]) if isinstance(bd,dict) else []
qobj=arr[0] if isinstance(arr,list) else arr;bd=[x for x in bd if not (isinstance(x,dict) and ('起点增强' in str(x.get('bookSourceName','')) or x.get('bookSourceUrl')==qobj.get('bookSourceUrl')))];bd.insert(0,qobj);bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n')
dp=ROOT/'rss/data/details/beta/qidian-next.json';dp.parent.mkdir(parents=True,exist_ok=True);dp.write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
rl=ROOT/'docs/RELEASE_LOG.md';old=rl.read_text();head='## 2026-09-12 · qidian-next 1.2.2-beta1 — 情无/小雨服务器段评映射修复'
if head not in old:
 block=head+'\n- 从已真机确认正文正常的 Stable 1.2.1 重新构建，仅修改情无/小雨服务器段评域。\n- 对齐起点X-QD现有逻辑：服务器 `ParagraphId` 按“`ParagraphId - 1 + 正文图片补偿`”定位气泡，点击继续传服务器原始 ParagraphId。\n- `ParagraphId=-1` 不再覆盖起点本地章名评论，也不再误作本章说；本地标题气泡原样保留。\n- 增加 `[QW-RV]` 计数解析与映射诊断日志；正文链、目录、搜索、账号、书友圈与其它 Provider 冻结。\n- 状态：Beta，等待真机确认。\n\n';rl.write_text(block+old.lstrip('\n'))
print('built',VERSION,sha,'stable',stable_sha)
