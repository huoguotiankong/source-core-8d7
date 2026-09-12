import json,hashlib
from pathlib import Path

ROOT=Path('.')
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
EXPECTED_BETA='faeba9977dc50810456aedee8382d83e358aa666799cc89bb5c6d9774760d93e'
EXPECTED_STABLE='1ee474c209b48d069344ffa4409379a0d39012cbaf2acecbd5ffcaba5404ab7e'
VERSION='1.2.2-beta2'; VC=12022; TODAY='2026-09-12'; NOW='2026-09-12T19:50:00+08:00'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/bookSource?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'

if hashlib.sha256(STABLE.read_bytes()).hexdigest()!=EXPECTED_STABLE: raise SystemExit('Stable changed')
if hashlib.sha256(BETA.read_bytes()).hexdigest()!=EXPECTED_BETA: raise SystemExit('Beta1 baseline changed')
arr=json.loads(BETA.read_text()); s=arr[0] if isinstance(arr,list) else arr; js=s['jsLib']

def replace_fn(text,name,new):
 p=text.find('function '+name)
 if p<0: raise SystemExit('missing '+name)
 b=text.find('{',p); dep=0; ins=None; esc=False
 for i in range(b,len(text)):
  c=text[i]
  if ins:
   if esc: esc=False
   elif c=='\\': esc=True
   elif c==ins: ins=None
   continue
  if c in "'\"`": ins=c; continue
  if c=='{': dep+=1
  elif c=='}':
   dep-=1
   if dep==0: return text[:p]+new+text[i+1:]
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
      var tc=Number(x.TextCount!==undefined?x.TextCount:(x.textCount!==undefined?x.textCount:0))||0;
      var cc=Number(x.CommentCount!==undefined?x.CommentCount:(x.commentCount!==undefined?x.commentCount:0))||0;
      var cnt=tc>0?tc:cc;
      if(pid===-1&&cnt>0)out.title=x;
      if(pid>0&&cnt>0){x.__qfCount=cnt;out.list.push(x);}
    }
    out.ok=d.length>0; out.chapter=out.title?(Number(out.title.TextCount||out.title.textCount||out.title.CommentCount||out.title.commentCount||0)||0):0;
    try{ctx.java.log('[QW-RV] rows='+d.length+' para='+out.list.length+' title='+(out.title?1:0)+' bid='+bid+' cid='+cid)}catch(_2){}
  }catch(e){try{ctx.java.log('[QW-RV] parse_fail '+e+' bid='+bid+' cid='+cid)}catch(_3){}}
  return out;
}'''

js=replace_fn(js,'qfQwReviewCountsV1214',COUNTS)
old="var cnt=Number(x.__qfCount||(x.CommentCount!==undefined?x.CommentCount:(x.commentCount!==undefined?x.commentCount:(x.TextCount||x.textCount||0))))||0;"
new="var cnt=Number(x.__qfCount||x.TextCount||x.textCount||x.CommentCount||x.commentCount||0)||0;"
if old not in js: raise SystemExit('Beta1 decorate count expression missing')
js=js.replace(old,new,1)
s['jsLib']=js
s['bookSourceComment']='v1.2.2-beta2：修复 Beta1 情无/小雨服务器段评气泡全部消失。根因是 Beta1 优先读取 CommentCount，服务器返回 CommentCount=0 时遮蔽了有效 TextCount，导致所有段评行被过滤。Beta2 恢复已验证的 TextCount 优先语义，保留 Beta1 的 ParagraphId-1+图片补偿映射；Stable 1.2.1 与正文链冻结。'
BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()

entry={'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','category':'novel','artifactType':'bookSource','channel':'beta','version':VERSION,'versionCode':VC,'updatedAt':TODAY,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'summary':'Beta2：修复情无/小雨服务器段评气泡全部消失；恢复 TextCount 优先计数语义，保留 ParagraphId 图片补偿映射。Stable 1.2.1 与正文冻结。','tags':['起点','测试版','情无','小雨服务器','段评','TextCount','ParagraphId','正文冻结'],'changelog':['修复 Beta1 回归：CommentCount=0 不再遮蔽有效 TextCount','服务器段评筛选恢复 Stable/Beta7 已验证的 TextCount 优先语义','保留 ParagraphId-1+图片补偿与原始 ParagraphId 点击参数','Stable 1.2.1、正文链、目录、搜索、账号及其它 Provider 不变'],'sha256':sha}

def isbeta(x): return isinstance(x,dict) and x.get('id')=='qidian-next-beta'
def replace_entry(path, extra=None):
 data=json.loads(path.read_text()); items=data.get('items',[]); done=False
 for i,x in enumerate(items):
  if isbeta(x):
   v=dict(entry)
   if extra: v.update(extra)
   items[i]=v; done=True; break
 if not done: items.insert(1,dict(entry,**(extra or {})))
 data['updatedAt']=NOW
 if 'generatedAt' in data: data['generatedAt']=NOW
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

replace_entry(ROOT/'subscription/beta.json',{'detailUrl':DETAIL})
novel_extra={'detailUrl':DETAIL,'type':'novel'}; replace_entry(ROOT/'subscription/novel.json',novel_extra)
mp=ROOT/'manifest.json'; m=json.loads(mp.read_text());
for i,x in enumerate(m.get('sources',[])):
 if isbeta(x): m['sources'][i]=dict(entry); break
m['updatedAt']=NOW; mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')

bp=ROOT/'bundles/all-beta.json'; bd=json.loads(bp.read_text()); qobj=arr[0] if isinstance(arr,list) else arr
for i,x in enumerate(bd):
 if isinstance(x,dict) and x.get('bookSourceUrl')==qobj.get('bookSourceUrl'):
  bd[i]=qobj; break
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n')

detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':'1.2.2-beta2：修复情无/小雨服务器段评气泡全部消失；正文继续沿用已真机确认正常的 Stable 1.2.1。','badges':['Beta','1.2.2-beta2','段评气泡回归修复','正文冻结'],'sections':[{'title':'Beta1 回归根因','text':'Beta1 优先读取 CommentCount；服务器行存在 CommentCount=0 时会遮蔽有效 TextCount，导致段评列表全部被过滤，所以正文中一个服务器段评气泡都没有。'},{'title':'Beta2 修复','text':'恢复 Stable/Beta7 已验证的 TextCount 优先计数语义：TextCount>0 时直接使用，否则才回退 CommentCount。'},{'title':'映射保持','text':'继续保留 ParagraphId - 1 + 正文图片补偿；点击气泡仍传服务器原始 ParagraphId。'},{'title':'冻结范围','text':'Stable 1.2.1、正文链、目录、搜索、账号、书友圈及其它 Provider 不改。'}],'sourceUrl':RAW,'backupUrl':BACKUP}
(ROOT/'rss/data/details/beta/qidian-next.json').write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n')

block='## 2026-09-12 · qidian-next 1.2.2-beta2 — 情无/小雨段评气泡回归修复\n- 真机确认 Beta1 选择情无服务器后连段评气泡都没有。\n- 根因：Beta1 将 `CommentCount` 放在 `TextCount` 前；服务器行存在 `CommentCount=0` 时遮蔽有效 `TextCount`，从而把全部段评行过滤掉。\n- Beta2 恢复 Stable/Beta7 已验证的 `TextCount` 优先语义，仅当 TextCount 无有效值时回退 CommentCount。\n- 保留 Beta1 的 `ParagraphId - 1 + 图片补偿` 定位与原始 ParagraphId 点击参数；正文与 Stable 1.2.1 冻结。\n- 状态：Beta，等待真机确认气泡恢复后再继续评论列表/楼中楼。\n\n'
for path in [ROOT/'docs/RELEASE_LOG.md',ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md']:
 old=path.read_text()
 if '1.2.2-beta2 — 情无/小雨段评气泡回归修复' not in old: path.write_text(block+old.lstrip('\n'))

assert hashlib.sha256(STABLE.read_bytes()).hexdigest()==EXPECTED_STABLE
print('built',VERSION,sha)
