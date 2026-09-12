import json,re,gzip,base64,hashlib
from pathlib import Path

ROOT=Path('.')
SRC=Path('sources/novel/qidian-next/qidian-next-beta.json')
arr=json.loads(SRC.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
js=s['jsLib']
m=re.search(r'var\s+QF_MOD38_PACK\s*=\s*(\{.*?\});\s*var\s+QF_MOD38_EXPORTS',js,re.S)
if not m: raise SystemExit('QF_MOD38_PACK not found')
pack=json.loads(m.group(1))

def dec(v):
    raw=v.split(':',1)[1] if ':' in v[:12] else v
    raw += '='*((4-len(raw)%4)%4)
    b=base64.urlsafe_b64decode(raw)
    try:return gzip.decompress(b).decode('utf-8')
    except Exception:return b.decode('utf-8')

def enc(t):
    return 'gz:'+base64.urlsafe_b64encode(gzip.compress(t.encode('utf-8'),9)).decode().rstrip('=')

def replace_fn(text,name,new_code):
    p=text.find('function '+name)
    if p<0: raise SystemExit('function missing: '+name)
    b=text.find('{',p)
    dep=0; ins=None; esc=False
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
            if dep==0:return text[:p]+new_code+text[i+1:]
    raise SystemExit('unterminated function: '+name)

core=dec(pack['review_server_core'])

QW_CAND=r'''function qfQwCommentCandidatesV321(){
    /* 1.2.1-beta4：情无评论已迁移到小雨当前后端，不再探测旧 103.236.* /comments.php。 */
    return ["https://full.hnxianxin.cn/qd/"];
}'''

QW_API=r'''function qfQwCommentApiV315(action,params){
    params=params||{};
    var root="https://full.hnxianxin.cn/qd/",a=String(action||"");
    if(a==="paragraph_summary")a="summary";
    else if(a==="paragraph_comments")a="paragraph";
    else if(a==="comment_replies")a="replies";
    var bid=params.bookId||params.book_id||params.bid||"",cid=params.chapterId||params.chapter_id||params.cid||"";
    var page=Number(params.page||1)||1,url="";
    if(a==="summary"){
        url=root+"review.php?bookId="+encodeURIComponent(String(bid))+"&chapterId="+encodeURIComponent(String(cid));
    }else if(a==="replies"){
        var rid=params.reviewId||params.review_id||params.commentId||params.comment_id||"";
        var rpid=params.paragraphId!==undefined?params.paragraphId:params.paragraph_id;
        url=root+"reply.php?bookId="+encodeURIComponent(String(bid))+"&chapterId="+encodeURIComponent(String(cid))+"&reviewId="+encodeURIComponent(String(rid))+"&paragraphId="+encodeURIComponent(rpid==null?"":String(rpid))+"&page="+page;
    }else{
        var pid=params.paragraphId!==undefined?params.paragraphId:params.paragraph_id;
        url=root+"list.php?bookId="+encodeURIComponent(String(bid))+"&chapterId="+encodeURIComponent(String(cid));
        if(pid!==undefined&&pid!==null&&String(pid)!==""&&params.chapter!==true){url+="&paragraphId="+encodeURIComponent(String(pid))+"&type=all";}
        url+="&page="+page;
    }
    try{
        var raw=String(qfRuntimeJavaV13(this).ajax(url)||"");
        var obj=qfServerJsonV315(raw)||{};
        try{this.source.put("qf_qw_comment_base",root);}catch(_s){}
        return obj;
    }catch(e){return {code:-1,message:String(e),data:{},Data:{}};}
}'''

NORM=r'''function qfServerNormV315(x,defaultQuote){
    x=x||{};var raw=(x.raw&&typeof x.raw==="object")?x.raw:x;var n={};
    try{n=qdNormalizeCommentV13(x,defaultQuote)||{};}catch(e0){n={};}
    var ui=x.user_info||raw.user_info||{};
    if(!n.id)n.id=String(x.reviewId||x.comment_id||x.review_id||raw.reviewId||raw.comment_id||raw.review_id||"");
    if(!n.name||n.name==="书友")n.name=String(x.nickname||x.user_name||ui.user_name||raw.nickname||raw.user_name||"书友");
    if(!n.avatar)n.avatar=String(x.avatarUrl||x.user_avatar||ui.user_avatar||raw.avatarUrl||raw.user_avatar||"");
    if(!n.content)n.content=qfEmojiV13(String(x.content||x.text||raw.content||raw.text||""));
    if(!n.quote)n.quote=String(x.quoteNickname||x.reffer_content||raw.quoteNickname||raw.reffer_content||defaultQuote||"");
    if(!n.like)n.like=Number(x.likeCount||x.digg_count||x.like_count||raw.likeCount||raw.digg_count||0)||0;
    if(!n.reply)n.reply=Number(x.replyCount||x.reply_count||raw.replyCount||raw.reply_count||0)||((n.replies&&n.replies.length)||0);
    if(!n.time)n.time=x.createTime||x.create_timestamp||x.create_time||raw.createTime||raw.create_timestamp||raw.create_time||"";
    if(!n.timeValue)n.timeValue=qfTimeValueV13(n.time);
    if(!n.ip)n.ip=String(x.ipAddress||x.ip_address||x.ip_location||raw.ipAddress||raw.ip_address||raw.ip_location||"");
    if(!Array.isArray(n.images))n.images=[];
    var im=x.imageUrl||x.image_url||raw.imageUrl||raw.image_url||"";if(im&&n.images.indexOf(String(im))<0)n.images.push(String(im));
    if(!n.audio)n.audio=String(x.audioUrl||x.audio_url||raw.audioUrl||raw.audio_url||"");
    n.isGod=!!(x.isGod||raw.isGod);n.raw=raw;
    return n;
}'''

SUMMARY=r'''function qfQwSummaryV315(bid,cid){
    /* beta4：选择“情无”时，正文段评数量以小雨 review.php 为准；只对章名评论做起点本地兜底。 */
    var key="qf-qw-summary-v121b4-"+bid+"-"+cid;
    var old=qfServerCacheGetV315(this,key,90000);if(old&&old.items&&old.items.length)return old;
    var root={};try{root=qfQwCommentApiV315.call(this,"summary",{bookId:bid,chapterId:cid})||{};}catch(_e0){root={};}
    var d=root.Data||root.data||{},box=d.Getparagraphscommentcounts||d.getparagraphscommentcounts||d.GetParagraphsCommentCounts||{};
    var list=qfServerArrayV319(box.DataList||box.dataList||box.List||box.list),out=[],hasTitle=false;
    for(var i=0;i<list.length;i++){
        var x=list[i]||{},rp=x.ParagraphId!==undefined?x.ParagraphId:x.paragraphId,p=Number(rp);
        var cnt=Number(x.CommentCount!==undefined?x.CommentCount:(x.commentCount!==undefined?x.commentCount:(x.TextCount||x.textCount||0)))||0;
        if(isNaN(p)||cnt<=0)continue;
        if(p<0)hasTitle=true;
        out.push({paragraphId:p<0?-1:p,segmentId:p>0?p:0,serverParaId:p>0?p:0,count:cnt,reviewId:String(x.ReviewId||x.reviewId||""),hot:Number(x.HasHotComment||x.hasHotComment||0)!==0,quote:String(x.QuoteContent||x.quoteContent||x.ParagraphContent||x.paragraphContent||""),raw:x,countSource:"情无·小雨服务器"});
    }
    var local=[];try{local=qdReviewSummaryV22.call(this,bid,cid,true)||[];}catch(_e1){local=[];}
    if(!hasTitle){
        var title=null;for(var j=0;j<local.length;j++){var z=local[j]||{};if(Number(z.paragraphId)<0||Number(z.segmentId)===0){if(Number(z.count||0)>0&&(!title||Number(z.count)>Number(title.count||0)))title=z;}}
        if(title)out.unshift({paragraphId:-1,segmentId:0,serverParaId:-1,count:Number(title.count||0),reviewId:String(title.reviewId||""),hot:!!title.hot,quote:String(title.quote||""),raw:title.raw||title,countSource:"起点本地章名兜底"});
    }
    if(!out.length&&local.length){
        for(var k=0;k<local.length;k++){var l=local[k]||{},lp=Number(l.paragraphId),ls=Number(l.segmentId),lc=Number(l.count||0);if(lc<=0)continue;out.push({paragraphId:lp<0?-1:(lp>0?lp:ls),segmentId:ls>0?ls:(lp>0?lp:0),serverParaId:lp,count:lc,reviewId:String(l.reviewId||""),hot:!!l.hot,quote:String(l.quote||""),raw:l.raw||l,countSource:"情无服务器不可用·起点本地全量兜底"});}
    }
    out.sort(function(a,b){if(Number(a.paragraphId)<0)return -1;if(Number(b.paragraphId)<0)return 1;return Number(a.segmentId||a.paragraphId)-Number(b.segmentId||b.paragraphId);});
    var pack={items:out,hot:{},raw:root,indexSource:out.length?"情无·小雨服务器":""};if(out.length)qfServerCachePutV315(this,key,pack);return pack;
}'''

PACK=r'''function qfQwCommentPackV315(bid,cid,pid,page,size,chapter){
    page=Number(page||1)||1;size=Number(size||20)||20;
    var p={bookId:bid,chapterId:cid,page:page,page_size:size,chapter:!!chapter};
    if(!chapter)p.paragraphId=pid;
    var r=qfQwCommentApiV315.call(this,chapter?"chapter":"paragraph",p),root=(r&&typeof r==="object")?r:{},d=root.data||root.Data||{};
    var a=qfServerArrayV319(d.comments||d.Comments||d.DataList||d.dataList||d.list||d.List),rows=[];
    for(var i=0;i<a.length;i++){var n=qfServerNormV315(a[i],"");if(n&&n.content)rows.push(n);}
    var total=Number(d.total||d.Total||d.totalCount||d.TotalCount||d.count||d.Count||root.total||root.totalCount||rows.length)||rows.length;
    /* 章名评论：服务器 review.php 有 -1 计数但 list.php(-1) 可能无详情，此时仅详情回退现有起点本地段评。 */
    if(!chapter&&Number(pid)<0&&!rows.length){
        var lp=null;
        try{if(typeof qdFetchParagraphCommentsV22==="function")lp=qdFetchParagraphCommentsV22.call(this,bid,cid,-1,page,size);}catch(_l0){lp=null;}
        try{if(!lp&&typeof qdFetchParagraphCommentsV20==="function")lp=qdFetchParagraphCommentsV20.call(this,bid,cid,-1,page,size);}catch(_l1){lp=null;}
        if(lp){var lr=lp.rows||lp.items||lp.comments||[];if(Array.isArray(lr)&&lr.length)return {rows:lr,rawRows:lr,total:Number(lp.total||lr.length)||lr.length,hasMore:!!lp.hasMore,raw:lp,source:"起点本地章名兜底"};}
    }
    return {rows:rows,rawRows:a,total:total,hasMore:rows.length>0&&((page*size)<total||rows.length>=size),raw:root,source:"情无·小雨服务器"};
}'''

CHAPTER=r'''function qfServerChapterPackV315(provider,bid,cid){
    if(provider==='晴天')return qfServerEmptyPackV334('晴天服务器原生页面');
    if(provider==='神魔')return qfSmChapterSayPackV319.call(this,bid,cid);
    if(provider==='情无')return qfQwCommentPackV315.call(this,bid,cid,0,1,20,true);
    return qfServerEmptyPackV334('');
}'''

for name,code in [
    ('qfQwCommentCandidatesV321',QW_CAND),('qfQwCommentApiV315',QW_API),('qfServerNormV315',NORM),
    ('qfQwSummaryV315',SUMMARY),('qfQwCommentPackV315',PACK),('qfServerChapterPackV315',CHAPTER)]:
    core=replace_fn(core,name,code)

# Base used by showBrowser: use current Xiaoyu origin, never old 103.236 host.
core=core.replace('return "http://103.236.85.8:7878/qd";','return "https://full.hnxianxin.cn/qd/";')
core=core.replace("return 'http://103.236.85.8:7878/qd';","return 'https://full.hnxianxin.cn/qd/';")
pack['review_server_core']=enc(core)
newpack=json.dumps(pack,ensure_ascii=False,separators=(',',':'))
js=js[:m.start(1)]+newpack+js[m.end(1):]
s['jsLib']=js
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceComment']='v1.2.1-beta4：情无段评适配当前“小雨的世界”服务器：review.php 提供段评计数，list.php 提供段评/本章说详情，reply.php 提供楼中楼；章名评论服务器优先、无详情时仅章名回退起点本地；本章说服务器详情已接通。Stable 与其它域冻结。'
SRC.write_text(json.dumps(arr,ensure_ascii=False,indent=2),encoding='utf-8')

VERSION='1.2.1-beta4'; VC=12014
SOURCE_URL=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
sha=hashlib.sha256(SRC.read_bytes()).hexdigest()

def walk(obj):
    if isinstance(obj,dict):
        isq=(obj.get('id') in ('qidian-next','qidian-next-beta') or '起点增强' in str(obj.get('name','')))
        if isq and (obj.get('channel')=='beta' or obj.get('id')=='qidian-next-beta' or 'Beta' in str(obj.get('name',''))):
            obj['version']=VERSION;obj['versionCode']=VC;obj['updatedAt']='2026-09-12T16:15:00+08:00';obj['sourcePath']='sources/novel/qidian-next/qidian-next-beta.json';obj['sourceUrl']=SOURCE_URL;obj['sha256']=sha
            obj['summary']='情无段评接入当前小雨服务器；章名评论服务器优先/本地兜底；本章说服务器详情接通。'
            obj['changelog']=['情无段评计数改走当前小雨 review.php','段评详情/本章说改走 list.php，楼中楼走 reply.php','章名评论服务器有则服务器，无详情时只回退起点本地','Stable 1.2.0 与其它域冻结']
        for v in obj.values(): walk(v)
    elif isinstance(obj,list):
        for v in obj: walk(v)

for fp in ['manifest.json','subscription/beta.json','subscription/novel.json']:
    p=Path(fp)
    if p.exists():
        d=json.loads(p.read_text(encoding='utf-8'));walk(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Rebuild/replace qidian-next Beta object inside bundle while preserving unrelated sources.
bp=Path('bundles/all-beta.json')
if bp.exists():
    bd=json.loads(bp.read_text(encoding='utf-8'))
    beta_obj=arr[0]
    def repl(lst):
        if not isinstance(lst,list):return False
        for i,x in enumerate(lst):
            if isinstance(x,dict) and (x.get('bookSourceUrl')==beta_obj.get('bookSourceUrl') or '起点增强' in str(x.get('bookSourceName',''))):lst[i]=beta_obj;return True
        return False
    if isinstance(bd,list):
        if not repl(bd):bd.append(beta_obj)
    elif isinstance(bd,dict):
        done=False
        for k,v in bd.items():
            if isinstance(v,list) and repl(v):done=True;break
        if not done:
            for k,v in bd.items():
                if isinstance(v,list):v.append(beta_obj);done=True;break
    bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Update current beta detail if it exists.
for fp in ['rss/data/details/beta/qidian-next.json']:
    p=Path(fp)
    if p.exists():
        try:
            d=json.loads(p.read_text(encoding='utf-8'));walk(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        except Exception: pass

rl=Path('docs/RELEASE_LOG.md');old=rl.read_text(encoding='utf-8')
entry='''\n## 2026-09-12 · qidian-next 1.2.1-beta4 — 情无/小雨评论服务器适配\n- 情无段评选择项接入当前小雨服务器：`review.php` 获取段评计数，`list.php` 获取段评与本章说详情，`reply.php` 获取楼中楼。\n- 章名评论优先尝试情无服务器；服务器无具体章名评论时，仅章名详情回退起点本地评论。\n- 情无本章说服务器详情链已经接通，可供正文章末两条预览/完整评论页使用。\n- Stable 1.2.0、正文 Provider、账号、角色卡、书友圈及其它评论 Provider 冻结。\n'''
if 'qidian-next 1.2.1-beta4' not in old:rl.write_text(entry+old,encoding='utf-8')
print('patched review_server_core',len(core),'sha',sha)
