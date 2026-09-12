import json,re,gzip,base64,hashlib
from pathlib import Path
P=Path('sources/novel/qidian-next/qidian-next-beta.json')
arr=json.loads(P.read_text(encoding='utf-8')); s=arr[0]; js=s['jsLib']
pos=js.find('QF_MOD38_PACK='); st=js.find('{',pos); pack,used=json.JSONDecoder().raw_decode(js[st:])

def dec(v):
    raw=v.split(':',1)[1] if v.startswith('gz:') else v
    raw += '='*((4-len(raw)%4)%4)
    return gzip.decompress(base64.urlsafe_b64decode(raw)).decode('utf-8')
def enc(t):
    return 'gz:'+base64.urlsafe_b64encode(gzip.compress(t.encode('utf-8'),9)).decode().rstrip('=')
mods={k:dec(v) for k,v in pack.items()}
review_name=next(k for k,v in mods.items() if 'function qfReviewV410' in v)
review=mods[review_name]

HELPER=r'''
/* beta4: 情无/小雨评论服务器适配 */
function qfQwReviewRootV121b4(){return "https://full.hnxianxin.cn/qd/";}
function qfQwJsonV121b4(ctx,url){try{return JSON.parse(String(ctx.java.ajax(url)||"{}"));}catch(e){try{ctx.java.log("情无评论请求失败: "+e);}catch(_e){}return {};}}
function qfQwCountV121b4(x){var n=Number((x&&x.CommentCount)!=null?x.CommentCount:(x&&x.TextCount));return isFinite(n)&&n>0?n:0;}
function qfQwLocalChapterNameV121b4(ctx,bid,cid){
  try{
    var u="https://m.qidian.com/argus/api/v1/chapter/getparagraphscommentcount?bookId="+encodeURIComponent(String(bid))+"&chapterId="+encodeURIComponent(String(cid));
    var j=JSON.parse(String(ctx.java.ajax(u)||"{}")); var d=j&&(j.Data||j.data)||{}; var box=d.Getparagraphscommentcounts||d.getparagraphscommentcounts||d; var a=box.DataList||box.dataList||[];
    for(var i=0;i<a.length;i++){var x=a[i]||{};if(Number(x.ParagraphId)==-1){var c=qfQwCountV121b4(x);if(c>0)return {count:c,hot:Number(x.HasHotComment||0)==1};}}
  }catch(e){} return null;
}
function qfReviewQingWuV121b4(ctx,bid,cid,paragraphCount){
  var out={map:{},chapterName:null,provider:"情无"};
  var u=qfQwReviewRootV121b4()+"review.php?bookId="+encodeURIComponent(String(bid))+"&chapterId="+encodeURIComponent(String(cid));
  var j=qfQwJsonV121b4(ctx,u), root=(j&&(j.data||j.Data))||{}; var box=root.Getparagraphscommentcounts||root.getparagraphscommentcounts||{}; var a=box.DataList||box.dataList||[];
  for(var i=0;i<a.length;i++){
    var x=a[i]||{}, p=Number(x.ParagraphId), c=qfQwCountV121b4(x); if(c<=0)continue;
    var hot=Number(x.HasHotComment||x.hasHotComment||0)==1;
    if(p===-1){out.chapterName={count:c,hot:hot};continue;}
    if(p>=0){var idx=p;if(idx===0)idx=1;if(idx>0&&(!paragraphCount||idx<=paragraphCount+2))out.map[String(idx)]={count:c,hot:hot};}
  }
  /* 服务器没有章名评论时，仅章名气泡回退本地官方段评；正文段评仍保持情无 */
  if(!out.chapterName)out.chapterName=qfQwLocalChapterNameV121b4(ctx,bid,cid);
  return out;
}
function qfReviewOpenQingWuV121b4(ctx,bid,cid,pid){
  try{
    var u=qfQwReviewRootV121b4()+"index.html?bookId="+encodeURIComponent(String(bid))+"&chapterId="+encodeURIComponent(String(cid));
    if(pid!==undefined&&pid!==null&&String(pid)!==""&&Number(pid)>0)u+="&paragraphIndex="+encodeURIComponent(String(pid));
    ctx.java.startBrowser(u,Number(pid)>0?"情无 · 段评":"情无 · 本章说"); return;
  }catch(e){try{ctx.java.toast("情无评论页打开失败: "+e);}catch(_e){}}
}
function qfQwEscV121b4(s){return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\"/g,"&quot;");}
function qfQwCleanV121b4(s){return String(s||"").replace(/\[fn=(\d+)\]/g,"").replace(/<[^>]+>/g,"").replace(/^\s+|\s+$/g,"");}
function qfBuildChapterReviewQingWuV121b4(ctx,bid,cid){
  try{
    var u=qfQwReviewRootV121b4()+"list.php?bookId="+encodeURIComponent(String(bid))+"&chapterId="+encodeURIComponent(String(cid))+"&page=1";
    var j=qfQwJsonV121b4(ctx,u), d=(j&&j.data)||{}, a=d.comments||[], total=Number(d.total||a.length)||0;
    if(!a.length)return "";
    var rows=[]; for(var i=0;i<Math.min(2,a.length);i++){var c=a[i]||{};rows.push({name:String(c.nickname||c.NickName||c.UserName||"书友"),text:qfQwCleanV121b4(c.content||c.Content||c.ReviewContent||""),like:Number(c.likeCount||c.AgreeAmount||0)||0});}
    if(!rows.length)return "";
    var w=1080,h=210+rows.length*150,svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+w+'" height="'+h+'"><rect x="18" y="12" width="1044" height="'+(h-24)+'" rx="38" fill="rgba(255,255,255,.24)" stroke="#c8c8c8"/><text x="60" y="78" font-size="42" font-weight="700" fill="#333">本章说</text><text x="1010" y="76" text-anchor="end" font-size="30" fill="#888">'+total+' 条评论 ›</text>';
    var y=145; for(var k=0;k<rows.length;k++){var r=rows[k],t=r.text;if(t.length>34)t=t.slice(0,34)+'…';svg+='<text x="62" y="'+y+'" font-size="30" font-weight="600" fill="#555">'+qfQwEscV121b4(r.name)+'</text><text x="990" y="'+y+'" text-anchor="end" font-size="25" fill="#aaa">♡ '+r.like+'</text><text x="62" y="'+(y+48)+'" font-size="31" fill="#333">'+qfQwEscV121b4(t)+'</text>';y+=150;} svg+='</svg>';
    var opt={style:"FULL",click:"qfReviewOpenQingWuV121b4(this,"+JSON.stringify(String(bid))+","+JSON.stringify(String(cid)) + ",0)",marker:"qfQwChapter:"+bid+":"+cid};
    return '<img src="data:image/svg+xml;base64,'+ctx.java.base64Encode(svg)+','+JSON.stringify(opt)+'">';
  }catch(e){try{ctx.java.log("情无本章说预览失败: "+e);}catch(_e){}return "";}
}
'''
if 'function qfQwReviewRootV121b4' not in review:
    review=review.replace('function qfReviewV410(ctx,bid,cid,paragraphCount){',HELPER+'\nfunction qfReviewV410(ctx,bid,cid,paragraphCount){',1)
# provider dispatch
needle='provider=qfReviewProviderNormalizeV410(provider);'
if 'qfReviewQingWuV121b4(ctx,bid,cid,paragraphCount)' not in review:
    review=review.replace(needle,needle+'\n    if(provider==="情无")return qfReviewQingWuV121b4(ctx,bid,cid,paragraphCount);',1)
# settings option
review=review.replace('["review_local","xianren","review_server"]','["review_local","xianren","review_server","情无"]')
# qfReviewOpen early dispatch: add after function declaration
open_decl='function qfReviewOpenV410(ctx,bid,cid,pid){'
if 'qfReviewOpenQingWuV121b4(ctx,bid,cid,pid);return;' not in review:
    review=review.replace(open_decl,open_decl+'\n    try{var _qs=qfStateGetV410(ctx),_qp=qfReviewProviderNormalizeV410(_qs.reviewProvider||"review_local");if(_qp==="情无"){qfReviewOpenQingWuV121b4(ctx,bid,cid,pid);return;}}catch(_qe){}',1)
# chapter preview dispatch
chap_decl='function qfBuildChapterReviewV41(ctx,bid,cid){'
if 'qfBuildChapterReviewQingWuV121b4(ctx,bid,cid)' not in review:
    review=review.replace(chap_decl,chap_decl+'\n    try{var _qs2=qfStateGetV410(ctx),_qp2=qfReviewProviderNormalizeV410(_qs2.reviewProvider||"review_local");if(_qp2==="情无"){var _qw=qfBuildChapterReviewQingWuV121b4(ctx,bid,cid);if(_qw)return _qw;/* 服务器无章评则回退原本地预览 */}}catch(_qe2){}',1)
mods[review_name]=review
pack[review_name]=enc(review)
newpack=json.dumps(pack,ensure_ascii=False,separators=(',',':'))
js=js[:st]+newpack+js[st+used:]
s['jsLib']=js
s['bookSourceComment']='v1.2.1-beta4：段评数据源新增“情无”，段评计数走小雨/情无 review.php；点击进入情无评论页；章名评论优先情无，服务器无数据时仅章名回退本地官方；本章说优先读取情无 list.php 并显示前2条具体评论，服务器无章评时回退原本地预览。其它域冻结。'
P.write_text(json.dumps(arr,ensure_ascii=False,indent=2),encoding='utf-8')
# metadata
mp=Path('sources/novel/qidian-next/manifest.json'); m=json.loads(mp.read_text(encoding='utf-8')); m['beta']['version']='1.2.1-beta4';m['beta']['versionCode']=12104;m['beta']['source']='qidian-next-beta.json?v=12104';m['beta']['summary']='段评新增情无服务器；章名评论情无优先/本地回退；本章说显示情无前2条具体评论。';mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for fp in ['subscription/beta.json','bundles/all-beta.json']:
 p=Path(fp); data=json.loads(p.read_text(encoding='utf-8')); txt=json.dumps(data,ensure_ascii=False); txt=txt.replace('1.2.1-beta3','1.2.1-beta4').replace('12103','12104').replace('qidian-next-beta.json?v=12103','qidian-next-beta.json?v=12104'); p.write_text(json.dumps(json.loads(txt),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rl=Path('docs/RELEASE_LOG.md'); old=rl.read_text(encoding='utf-8'); entry='''\n## 2026-09-12 · qidian-next `1.2.1-beta4`\n- 段评数据源新增 `情无`，段评计数接入小雨/情无 `review.php`。\n- 情无章名评论：服务器有则使用服务器；无则只对章名评论回退本地官方段评。\n- 情无本章说：接入 `list.php`，章末卡片显示前 2 条具体评论；服务器无章评时回退原本地预览。\n- Stable 不变，其它功能域冻结。\n'''; rl.write_text(entry+old,encoding='utf-8')
print('patched module',review_name,'review len',len(review))
print('beta4 sha256',hashlib.sha256(P.read_bytes()).hexdigest())
