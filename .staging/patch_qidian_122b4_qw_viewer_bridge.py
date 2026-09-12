import base64, hashlib, json
from pathlib import Path

ROOT=Path('.')
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
EXPECTED_BETA='b26a99d4ff92c1e93ccb6af8fe4e685b14c6b793e79e17e7c2ccaf2bad16e5f1'
EXPECTED_STABLE='1ee474c209b48d069344ffa4409379a0d39012cbaf2acecbd5ffcaba5404ab7e'
VERSION='1.2.2-beta4'; VC=12024; TODAY='2026-09-12'; NOW='2026-09-12T22:45:00+08:00'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/bookSource?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'

if hashlib.sha256(STABLE.read_bytes()).hexdigest()!=EXPECTED_STABLE: raise SystemExit('Stable changed')
if hashlib.sha256(BETA.read_bytes()).hexdigest()!=EXPECTED_BETA: raise SystemExit('Beta3 baseline changed')
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr; js=s['jsLib']
frozen={}
for k in ['ruleContent','ruleToc','ruleSearch','ruleBookInfo','ruleExplore','loginUrl','loginUi']:
    if k in s: frozen[k]=json.dumps(s[k],ensure_ascii=False,sort_keys=True,separators=(',',':'))

BROWSER_JS=r'''(function(){
'use strict';
var C=window.__QF_QW_CTX__||{};
var BASE='https://full.hnxianxin.cn/qd/';
function txt(v){return v===undefined||v===null?'':String(v)}
function num(v){var n=Number(v||0);return isNaN(n)?0:n}
function safe(raw){raw=txt(raw);try{raw=raw.replace(/([:\\[,]\\s*)(\\d{16,})(?=\\s*[,}\\]])/g,'$1"$2"');return JSON.parse(raw||'{}')}catch(e){throw new Error('评论数据解析失败：'+e)}}
function avatar(v){v=txt(v).trim();if(!v)return '';if(/^\\/\\//.test(v))return 'https:'+v;if(/^http:\\/\\//i.test(v))return 'https://'+v.substring(7);if(/^\\//.test(v))return 'https://full.hnxianxin.cn'+v;if(!/^https?:\\/\\//i.test(v))return BASE+v.replace(/^\\/+/, '');return v}
function ctext(v){return txt(v).replace(/\\[fn=(\\d+)\\]/g,function(_,n){var m={'31':'😳','21':'😍','11':'🙄','32':'😎','12':'😭','43':'☺️','50':'🤐','45':'😴','19':'😂'};return m[n]||_})}
function tval(v){if(!v)return 0;if(typeof v==='number')return v>1000000000000?v:v*1000;var n=Number(v);if(!isNaN(n)&&n>0)return n>1000000000000?n:n*1000;var d=Date.parse(txt(v).replace(/-/g,'/'));return isNaN(d)?0:d}
function item(c,isReply){c=c||{};var rid=c.reviewId||c.ReviewId||c.rootReviewId||c.RootReviewId||c.id||c.Id||'';var nick=c.nickname||c.Nickname||c.NickName||c.userName||c.UserName||c.user_name||'匿名';var av=avatar(c.avatarUrl||c.AvatarUrl||c.userAvatar||c.UserAvatar||c.user_avatar||c.UserHeadIcon||c.userHeadIcon||c.avatar||c.Avatar||'');var body=ctext(c.content||c.Content||c.text||c.Text||c.reviewContent||c.ReviewContent||'');if(isReply&&(c.quoteNickname||c.QuoteNickname))body='回复 @'+txt(c.quoteNickname||c.QuoteNickname)+'：'+body;var out={id:txt(rid),text:body,userInfo:{userName:txt(nick),avatar:av},createTs:tval(c.createTime||c.CreateTime||c.create_timestamp||c.create_time),replyCount:num(c.replyCount||c.ReplyCount||c.rootReviewReplyCount||c.RootReviewReplyCount),diggCount:num(c.likeCount||c.LikeCount||c.agreeCount||c.AgreeAmount||c.digg_count||c.like_count),tags:{isGod:!!(c.isGod||c.IsGod||c.is_hot||c.IsHot)},images:[],audio:null};var img=avatar(c.imageUrl||c.ImageUrl||c.image_url||'');if(!isReply&&img)out.images=[{url:img,width:num(c.imageWidth||c.ImageWidth),height:num(c.imageHeight||c.ImageHeight)}];var au=txt(c.audioUrl||c.AudioUrl||c.audio_url||c.VoiceUrl||'');if(au)out.audio={url:avatar(au),duration:num(c.audioDuration||c.AudioDuration)};return out}
function arr(d){if(!d)return [];var a=d.comments||d.Comments||d.DataList||d.dataList||d.list||d.List||[];return Array.isArray(a)?a:[]}
function endpoint(mode,para,page,review){var u;if(mode==='reply'){u=BASE+'reply.php?bookId='+encodeURIComponent(C.bookId)+'&chapterId='+encodeURIComponent(C.chapterId)+'&reviewId='+encodeURIComponent(review||'')+(para&&String(para)!=='0'?'&paragraphId='+encodeURIComponent(para):'')+'&page='+encodeURIComponent(page||1)}else{u=BASE+'list.php?bookId='+encodeURIComponent(C.bookId)+'&chapterId='+encodeURIComponent(C.chapterId)+(mode==='paragraph'&&para&&String(para)!=='0'?'&paragraphId='+encodeURIComponent(para)+'&type=all':'')+'&page='+encodeURIComponent(page||1)}return u}
function nativeGet(url){if(window.java&&typeof window.java.ajax==='function')return txt(window.java.ajax(url));throw new Error('WebView 不支持 java.ajax')}
var nativeFetch=window.fetch?window.fetch.bind(window):null;
window.fetch=function(input,opt){var u=typeof input==='string'?input:(input&&input.url?input.url:'');if(u.indexOf('__qfqwcmt__?')<0){if(nativeFetch)return nativeFetch(input,opt);return Promise.reject(new Error('fetch unavailable'))}try{var q=u.split('?')[1]||'',sp=new URLSearchParams(q),mode=sp.get('mode')||'paragraph',para=sp.get('para')||'0',page=sp.get('page')||'1',review=sp.get('review')||'',raw=nativeGet(endpoint(mode,para,page,review));return Promise.resolve(new Response(JSON.stringify(safe(raw)),{status:200,headers:{'Content-Type':'application/json'}}))}catch(e){return Promise.reject(e)}};
function register(){if(!window.commentAdapters||typeof window.commentAdapters.replace!=='function'){setTimeout(register,80);return}var ad={buildRequest:function(ctx){var p=(ctx&&ctx.cursor)?ctx.cursor:1;return {url:'__qfqwcmt__?mode='+(C.mode||'paragraph')+'&para='+encodeURIComponent(C.paragraphId||'0')+'&page='+p,method:'GET'}},parseResponse:function(data){var d=(data&&data.data)||(data&&data.Data)||data||{},ls=arr(d),out=[];for(var i=0;i<ls.length;i++)out.push(item(ls[i],false));return {comments:out,nextCursor:ls.length>=20?((Number((C._page||1))+1)):null,totalCount:num(d.totalCount||d.TotalCount||d.count||d.Count)||out.length}},buildReplyRequest:function(ctx){return {url:'__qfqwcmt__?mode=reply&para='+encodeURIComponent(C.paragraphId||'0')+'&page=1&review='+encodeURIComponent(ctx&&ctx.commentId||''),method:'GET'}},parseReplyResponse:function(data){var d=(data&&data.data)||(data&&data.Data)||data||{},ls=arr(d),out=[];for(var i=0;i<ls.length;i++)out.push(item(ls[i],true));return out}};window.commentAdapters.replace('paragraph',ad);window.commentAdapters.replace('chapter',ad);try{var m=document.createElement('meta');m.name='referrer';m.content='no-referrer';document.head.appendChild(m)}catch(_m){}try{document.addEventListener('error',function(e){var im=e.target;if(im&&im.tagName==='IMG'&&im.src&&/^http:\\/\\//i.test(im.src)){im.src='https://'+im.src.substring(7)}},true)}catch(_e){}}
register();
})();'''
B64=base64.b64encode(BROWSER_JS.encode()).decode()

HELPER=r'''var QF_QW_VIEWER_URL_V1224='https://raw.giteeusercontent.com/syiism/legado-source/raw/main/ui/comment-viewer.html';
var QF_QW_VIEWER_JS_B64_V1224='''+repr(B64)+r''';
function qfQwViewerPackV1224(ctx,bid,cid,pid){
  var j=(ctx&&ctx.java)?ctx.java:null,out={html:'',url:'',pre:'',config:''};
  if(!j)return out;
  try{
    var html=String(j.ajax(QF_QW_VIEWER_URL_V1224)||'');
    if(!html||html.indexOf('<')<0)return out;
    var script=String(j.base64Decode(QF_QW_VIEWER_JS_B64_V1224)||'');
    if(!script)return out;
    var tag='<script>'+script.replace(/<\\/script/gi,'<\\\\/script')+'<\\/script>';
    if(/<\\/body>/i.test(html))html=html.replace(/<\\/body>/i,tag+'</body>');else html+=tag;
    var p=Number(pid);if(isNaN(p))p=0;
    var mode=p>0?'paragraph':'chapter';
    var cfg={bookId:String(bid||''),chapterId:String(cid||''),paragraphId:String(p>0?p:0),mode:mode};
    out.html=html;
    out.url=QF_QW_VIEWER_URL_V1224+'?book_id='+encodeURIComponent(String(bid||''))+'&item_id='+encodeURIComponent(String(cid||''))+'&para_id='+encodeURIComponent(String(p>0?p:0))+(mode==='paragraph'?'&paragraph_tog=1':'&chapter_tog=1');
    out.pre='window.java=java;window.__QF_QW_CTX__='+JSON.stringify(cfg).replace(/<\\/script/gi,'<\\\\/script')+';';
    try{out.config=JSON.stringify(qfV18CommentConfig.call(ctx));}catch(_cfg){out.config=JSON.stringify({state:4,isHideable:true,heightPercentage:0.78,radius:22});}
  }catch(e){try{j.log('[QW-V1224] viewer_prepare_fail '+e)}catch(_l){}}
  return out;
}'''

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

anchor='function qfQwOpenV1214'
if js.count(anchor)!=1: raise SystemExit('qfQwOpen anchor count')
if 'QF_QW_VIEWER_JS_B64_V1224' in js: raise SystemExit('beta4 helper already exists')
js=js.replace(anchor,HELPER+'\n'+anchor,1)
OPEN=r'''function qfQwOpenV1214(ctx,bid,cid,pid,title){
  var j=(ctx&&ctx.java)?ctx.java:null;
  if(j){
    try{
      var p=qfQwViewerPackV1224(ctx,bid,cid,pid);
      if(p&&p.html){j.showBrowser(p.url,p.html,p.pre,p.config);return;}
    }catch(e0){try{j.log('[QW-V1224] viewer_open_fail '+e0)}catch(_0){}}
  }
  try{ctx.java.startBrowser(qfQwH5V1214(bid,cid,pid),title||'评论');}catch(e1){try{ctx.java.longToast('情无评论页打开失败：'+e1)}catch(_1){}}
}'''
js=replace_fn(js,'qfQwOpenV1214',OPEN)

assert js.count('QF_QW_VIEWER_JS_B64_V1224')>=2
assert js.count('function qfQwViewerPackV1224')==1
assert js.count('function qfQwOpenV1214')==1
assert 'qfReviewFastSummaryV1223' in js and 'ARGUS-REPAGE' in js
assert 'qfQwH5V1214(bid,cid,pid)' in js
s['jsLib']=js
s['bookSourceComment']='v1.2.2-beta4：真机确认情无/小雨段评气泡与主评论列表已恢复；本版只修评论详情页头像与楼中楼。点击段评改为书源托管评论 Viewer，list.php/reply.php 统一经 java.ajax 跨域桥接，并适配 avatarUrl/reviewId/nickname 等当前服务器字段；Viewer 不可用时保留原 index.html 回退。Beta3 Argus 气泡快通道、正文、目录、搜索、账号及 Stable 1.2.1 全部冻结。'
for k,before in frozen.items():
    after=json.dumps(s[k],ensure_ascii=False,sort_keys=True,separators=(',',':'))
    if after!=before: raise SystemExit('frozen field changed: '+k)
BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()

entry={'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','category':'novel','artifactType':'bookSource','channel':'beta','version':VERSION,'versionCode':VC,'updatedAt':TODAY,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'summary':'Beta4：情无/小雨段评主列表已真机恢复；本版修复头像空白与楼中楼回复加载失败，list.php/reply.php 改走书源 java.ajax 跨域桥接。Stable 1.2.1、正文与目录冻结。','tags':['起点','测试版','情无','小雨服务器','段评','头像','楼中楼','java.ajax','CORS桥接','正文冻结'],'changelog':['真机确认 Beta3 情无段评气泡和主评论列表恢复','评论详情不再直接依赖服务器 H5 的跨域 fetch，优先使用书源托管 Viewer','list.php 与 reply.php 统一通过 java.ajax 请求，规避评论 UI 与接口不同源时的 CORS 拦截','适配 avatarUrl、reviewId、nickname、createTime、replyCount、likeCount、isGod、imageUrl、audioUrl、quoteNickname 当前字段','头像 URL 兼容 //、http:// 与相对路径并使用 no-referrer','Viewer 准备/打开失败保留原 index.html 回退；Beta3 Argus 气泡快通道不改','Stable 1.2.1、正文、目录、搜索、账号及其它 Provider 不变'],'sha256':sha,'detailUrl':DETAIL}

def isbeta(x): return isinstance(x,dict) and x.get('id')=='qidian-next-beta'
def upsert(path,key,extra=None):
    p=ROOT/path; d=json.loads(p.read_text()); a=d[key]; old=next((i for i,x in enumerate(a) if isbeta(x)),None); e=dict(entry); e.update(extra or {})
    if old is None:
        si=next((i+1 for i,x in enumerate(a) if isinstance(x,dict) and x.get('id')=='qidian-next' and x.get('channel')=='stable'),0); a.insert(si,e)
    else: a[old]=e
    d['updatedAt']=NOW
    if 'generatedAt' in d:d['generatedAt']=NOW
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
upsert('manifest.json','sources',{'detailUrl':None});
# remove null manifest-only detail field
mp=ROOT/'manifest.json'; md=json.loads(mp.read_text());
for x in md['sources']:
    if isbeta(x): x.pop('detailUrl',None)
mp.write_text(json.dumps(md,ensure_ascii=False,indent=2)+'\n')
upsert('subscription/beta.json','items')
upsert('subscription/novel.json','items',{'type':'novel'})

bp=ROOT/'bundles/all-beta.json'; bd=json.loads(bp.read_text()); q=arr[0] if isinstance(arr,list) else arr; done=False
for i,x in enumerate(bd):
    if isinstance(x,dict) and x.get('bookSourceUrl')==q.get('bookSourceUrl') and '起点增强' in str(x.get('bookSourceName','')):
        bd[i]=q; done=True; break
if not done: bd.insert(0,q)
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n')

detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':'1.2.2-beta4：情无/小雨段评气泡与主列表已恢复，本版集中修复头像与回复楼中楼。','badges':['Beta','1.2.2-beta4','头像修复','楼中楼修复','CORS桥接','正文冻结'],'sections':[{'title':'真机结果','text':'Beta3 已确认情无/小雨服务器段评气泡和主评论列表可以显示；当前问题收敛为头像空白、回复加载失败。'},{'title':'回复修复','text':'当前小雨接口 list.php/reply.php 与评论 UI 不同源；Beta4 把两者统一改由书源 java.ajax 请求，避免 WebView fetch 被 CORS 拦截。'},{'title':'头像修复','text':'评论适配器新增 avatarUrl 等当前服务器字段，并兼容协议相对、HTTP 和相对路径，图片使用 no-referrer。'},{'title':'冻结范围','text':'Beta3 Argus 段评气泡快通道、正文、目录、搜索、账号和 Stable 1.2.1 均不修改。'}],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'links':{'source':RAW,'backup':BACKUP,'import':IMPORT},'updatedAt':TODAY}
(ROOT/'rss/data/details/beta/qidian-next.json').write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n')

block='''## 2026-09-12 · qidian-next 1.2.2-beta4 — 情无头像 / 楼中楼桥接修复\n- 真机确认 Beta3 已恢复情无/小雨段评气泡和主评论列表；剩余问题为头像空白、楼中楼显示“回复加载失败”。\n- 对照当前“小雨的世界”实现确认：`list.php` / `reply.php` 与评论 UI 不同源且接口无 CORS 头，浏览器直接 `fetch` 会被拦；评论请求应由书源侧 `java.ajax` 代理。\n- Beta4 仅替换情无段评点击后的 Viewer：主列表走 `list.php`、回复走 `reply.php`，均经 `java.ajax`；接口大整数 ID 在 JSON 解析前做字符串保护。\n- 评论字段新增当前服务端 `avatarUrl/reviewId/nickname/createTime/replyCount/likeCount/isGod/imageUrl/audioUrl/quoteNickname` 适配；头像 URL 兼容协议相对/HTTP/相对路径并使用 no-referrer。\n- Viewer 获取或打开失败仍回退原 `index.html`；Beta3 Argus 气泡快通道、正文、目录、搜索、账号和 Stable 1.2.1 冻结。\n- 状态：Beta，等待真机确认头像与楼中楼。\n\n'''
for path in ['docs/RELEASE_LOG.md','docs/sources/qidian-next/PROJECT_HANDOFF.md']:
    p=ROOT/path; old=p.read_text();
    if '## 2026-09-12 · qidian-next 1.2.2-beta4' not in old: p.write_text(block+old.lstrip('\n'))
print('built',VERSION,'sha',sha)
