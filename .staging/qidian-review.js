/* v4.0.0-alpha19：正文性能⑪——热评/作者说/本章说视觉层短 LRU。缓存纯 SVG Base64，点击 metadata 仍按章节动态生成；命中时跳过 SVG 字符串构建、Java 获取和 base64Encode。评论数据/TitleInfoList/楼中楼链不改。 */
/* v4.0.0-alpha18：正文性能⑩——评论装饰对象池 + 点击参数延迟构建。Decoration Plan 改用可复用紧凑行对象；quote 的 URI/JS escape 只在真正生成可点击气泡/热评时计算一次；同章 click context 复用；lineExtra 去除小数组对象。TitleInfoList/标签解析链不改。 */
/* v4.0.0-alpha17：正文性能⑨——最终输出单次组装。正文行不再反复 += 气泡/热评；作者说/本章说不再对已 join 的整章正文继续 +=；只显示尾卡时跳过 textIdx/媒体索引构建；热评单开时非 hot 段不进入 decoration plan。 */
/* alpha16：纯文字媒体检测快路径；无媒体正文跳过 Markdown/img replace，lines 无媒体时不逐行跑 img regex。 */
/* v4.0.0-alpha15：正文性能⑦——正文行/文本索引一次建模；评论 item 单次规划后复用给热评预取与装饰；气泡 SVG Base64 进入共享 LRU；标题 quote 仅有章名气泡时写缓存。 */
/* alpha81 shared import */
var __qfRc81=QF_MOD38_CACHE["review_common"]||qfModuleEnsureV38.call(this,"review_common");
var qdBubbleDataV20=__qfRc81.qdBubbleDataV20;
var qdQtAuthorSayCardV332=__qfRc81.qdQtAuthorSayCardV332;

/* ============================================================
 * v4.0.0-alpha11 · Chapter Review Decoration Snapshot
 *
 * 这是“最终装饰结果”的短期内存快照，不替代任何官方数据缓存：
 * - 本地评论 120s；服务器评论 60s；
 * - 只保留最近 5 个 chapter/mode 组合；
 * - key 绑定正文轻签名、正文 Provider、评论路由、四个显示开关、智能对齐开关；
 * - 命中后恢复 chapter title bubble 副作用，再直接返回已经生成好的 body。
 *
 * 目的：返回上一章/重复打开同章时，不再重复执行 summary、章末预览、热评、
 * paragraph map、SVG/base64 构建和作者说/本章说拼接。
 * ============================================================ */
var QF_REVIEW_SNAP460={},QF_REVIEW_SNAP460_ORDER=[],QF_REVIEW_SNAP460_MAX=5;
function qdReviewSnapSigV460(s){
    s=String(s||'');var n=s.length,h=2166136261>>>0;
    function mixAt(a,b){for(var i=a;i<b&&i<n;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}}
    mixAt(0,96);
    if(n>192){var m=Math.max(96,Math.floor(n/2)-48);mixAt(m,m+96);}
    if(n>96)mixAt(Math.max(0,n-96),n);
    return n.toString(36)+'-'+h.toString(36);
}
function qdReviewSnapKeyV460(bid,cid,isPaid,provider,serverProvider,flags,smart,content){
    flags=flags||{};
    return [String(bid),String(cid),isPaid?'1':'0',String(provider||''),String(serverProvider||''),
        flags.bubble?'1':'0',flags.hot?'1':'0',flags.talk?'1':'0',flags.author?'1':'0',smart?'1':'0',qdReviewSnapSigV460(content)].join('|');
}
function qdReviewSnapGetV460(key,serverMode){
    var o=QF_REVIEW_SNAP460[String(key||'')],ttl=serverMode?60000:120000;
    if(!o)return null;
    if(Date.now()-Number(o.ts||0)>ttl){delete QF_REVIEW_SNAP460[key];var ix=QF_REVIEW_SNAP460_ORDER.indexOf(key);if(ix>=0)QF_REVIEW_SNAP460_ORDER.splice(ix,1);return null;}
    var i=QF_REVIEW_SNAP460_ORDER.indexOf(key);if(i>=0){QF_REVIEW_SNAP460_ORDER.splice(i,1);QF_REVIEW_SNAP460_ORDER.push(key);}
    return o;
}
function qdReviewSnapPutV460(key,body,titleCount,titleHot){
    body=String(body==null?'':body);if(!key||!body||body.length>420000)return;
    QF_REVIEW_SNAP460[key]={ts:Date.now(),body:body,titleCount:Number(titleCount||0)||0,titleHot:!!titleHot};
    var i=QF_REVIEW_SNAP460_ORDER.indexOf(key);if(i>=0)QF_REVIEW_SNAP460_ORDER.splice(i,1);QF_REVIEW_SNAP460_ORDER.push(key);
    while(QF_REVIEW_SNAP460_ORDER.length>QF_REVIEW_SNAP460_MAX){var old=QF_REVIEW_SNAP460_ORDER.shift();delete QF_REVIEW_SNAP460[old];}
}
function qdReviewSnapRestoreTitleV460(bid,cid,showBubble,snap){
    try{
        var ch=qfChapter(this);if(!ch||!ch.putImgUrl)return;
        if(showBubble&&snap&&Number(snap.titleCount||0)>0){
            ch.putImgUrl(qdBubbleDataV20.call(this,Number(snap.titleCount||0),bid,cid,-1,0,!!snap.titleHot));
        }else ch.putImgUrl(null);
    }catch(_e){}
}

/* alpha80：继续将仅属于本模块的 helper 收回 lazy module，未进入功能时不建立全局函数。 */
function qdV20List(v){
    if(!v)return [];
    if(Array.isArray(v))return v;
    try{if(v.size&&v.get){var a=[];for(var i=0;i<v.size();i++)a.push(v.get(i));return a;}}catch(e){}
    return [];
}
function qdV20CommentText(c){
    c=c||{};
    var t=c.text||c.ReviewContent||c.reviewContent||c.Content||c.content||
        c.Body||c.Subject||c.CommentContent||
        (c.raw&&(c.raw.text||c.raw.ReviewContent||c.raw.Content||c.raw.content))||"";
    if(typeof t==="object")t=t.Text||t.text||t.Content||t.content||"";
    return qfEmojiV13(String(t||""));
}
function qdV20CleanCommentText(s){
    return qfEmojiV13(String(s||""))
        .replace(/https?:\/\/[^\s]+/g,"")
        .replace(/qdd\.gg\/[^\s]+/g,"")
        .replace(/<[^>]+>/g,"")
        .trim();
}
function qdV20CommentUser(c){
    c=c||{};
    var u=c.user_info||c.UserInfo||c.User||c.user||c.raw||{};
    return {
        name:String(u.user_name||u.UserName||u.NickName||u.nickname||c.nickname||c.UserName||c.userName||"书友"),
        avatar:String(u.user_avatar||u.UserHeadIcon||u.Avatar||u.avatar||c.avatar||c.UserHeadIcon||"")
    };
}
function qdV20CommentLike(c){
    c=c||{};
    return Number(c.digg_count||c.like_count||c.LikeCount||c.likeCount||c.DiggCount||
        c.AgreeAmount||c.Likes||(c.raw&&(c.raw.LikeCount||c.raw.DiggCount||c.raw.AgreeAmount))||0)||0;
}
function qdV20CommentReply(c){
    c=c||{};
    return Number(c.reply_count||c.ReplyCount||c.replyCount||c.CommentCount||c.commentCount||
        (c.raw&&(c.raw.ReplyCount||c.raw.CommentCount))||0)||0;
}
/* alpha18：Decoration Plan 行对象池。
 * 一章完成后立即归还；仅复用段落位置/quote 等瞬时装饰数据，不缓存评论实体。
 * tuple: 0=item,1=pid,2=count,3=seg,4=lineIndex,5=quote,6=uriEncoded,7=jsEscaped,8=hot */
var QF_DECOR_ROW490_POOL=[],QF_DECOR_ROW490_MAX=128;
function qdDecorRowAllocV490(it,pid,cnt,seg,ix,quote,hot){
    var r=QF_DECOR_ROW490_POOL.length?QF_DECOR_ROW490_POOL.pop():new Array(9);
    r[0]=it;r[1]=pid;r[2]=cnt;r[3]=seg;r[4]=ix;r[5]=quote;r[6]=null;r[7]=null;r[8]=hot?1:0;return r;
}
function qdDecorRowQuoteV490(r){
    if(r[6]===null){var q='';try{q=encodeURIComponent(String(r[5]||''));}catch(_qe490){q='';}r[6]=q;r[7]=qfEscJsV13(q);}return String(r[6]||'');
}
function qdDecorRowQuoteJsV490(r){if(r[7]===null)qdDecorRowQuoteV490(r);return String(r[7]||'');}
function qdDecorRowsReleaseV490(plan){
    if(!plan||!plan.length)return;
    for(var i=0;i<plan.length&&QF_DECOR_ROW490_POOL.length<QF_DECOR_ROW490_MAX;i++){
        var r=plan[i];if(!r)continue;for(var k=0;k<9;k++)r[k]=null;QF_DECOR_ROW490_POOL.push(r);
    }
}

/* alpha19：低频正文卡片只缓存“视觉层”，绝不缓存 click / ReviewId / 评论实体。
 * 同一作者说/本章说/热评在返回章节或快照失效后可直接复用 Base64，减少 SVG 拼接与 Java Bridge。
 * 36 项 LRU 仅常驻很小的 data URI；业务内容变化会自然产生不同 key。 */
var QF_CARD_VIS500={},QF_CARD_VIS500_ORDER=[],QF_CARD_VIS500_MAX=36;
function qdCardVisKeyV500(kind,sig){return String(kind||'')+'\u001f'+String(sig||'');}
function qdCardVisGetV500(kind,sig){
    var key=qdCardVisKeyV500(kind,sig),v=QF_CARD_VIS500[key];if(!v)return '';
    var i=QF_CARD_VIS500_ORDER.indexOf(key);if(i>=0){QF_CARD_VIS500_ORDER.splice(i,1);QF_CARD_VIS500_ORDER.push(key);}return v;
}
function qdCardVisPutV500(j,kind,sig,svg){
    if(!j||!svg)return '';
    var key=qdCardVisKeyV500(kind,sig),base='';try{base='data:image/svg+xml;base64,'+j.base64Encode(svg);}catch(_e){return '';}
    if(!base)return '';
    QF_CARD_VIS500[key]=base;var i=QF_CARD_VIS500_ORDER.indexOf(key);if(i>=0)QF_CARD_VIS500_ORDER.splice(i,1);QF_CARD_VIS500_ORDER.push(key);
    while(QF_CARD_VIS500_ORDER.length>QF_CARD_VIS500_MAX){var old=QF_CARD_VIS500_ORDER.shift();delete QF_CARD_VIS500[old];}
    return base;
}

function qdHotHtmlV20(c,bid,cid,pid,seg,quote,quoteEncoded,quoteJsEncoded){
    if(!c||!c.content)return "";
    var t=String(c.content||"").replace(/\s+/g," ").trim();if(t.length>22)t=t.substring(0,22)+"…";
    var like=Number(c.like||0)||0,meta=like>0?("♡ "+(like>999?"999+":like)):"查看段评 ›";
    var visualSig=t+'\u001f'+meta,base=qdCardVisGetV500('hot',visualSig);
    if(!base){
        var j=qfImageJavaV14(this);if(!j)return "";try{if(typeof j.base64Encode!=="function")return "";}catch(e0){return "";}
        var svg='<svg width="1000" height="122" xmlns="http://www.w3.org/2000/svg">'+
            '<rect x="2" y="5" width="996" height="104" fill="rgba(255,250,248,0.72)" rx="30" stroke="#F0D9D3" stroke-width="1"/>'+
            '<rect x="27" y="28" width="122" height="50" rx="25" fill="#EF5B50"/>'+
            '<text x="88" y="62" font-size="28" fill="#FFF" text-anchor="middle" font-weight="700">热评</text>'+
            '<text x="174" y="63" font-size="33" fill="#252525" font-weight="600">'+qfEscV13(t)+'</text>'+
            '<text x="962" y="63" font-size="25" fill="#9A8B87" text-anchor="end">'+qfEscV13(meta)+'</text></svg>';
        base=qdCardVisPutV500(j,'hot',visualSig,svg);if(!base)return "";
    }
    var qe=quoteEncoded==null?"":String(quoteEncoded),qj=quoteJsEncoded==null?"":String(quoteJsEncoded);
    if(quoteEncoded==null){try{qe=encodeURIComponent(String(quote||""));}catch(_qe){qe="";}}
    if(quoteJsEncoded==null)qj=qfEscJsV13(qe);
    var click="showCmtV20('"+qfEscJsV13(bid)+"','"+qfEscJsV13(cid)+"','"+pid+"','"+seg+"','dp','"+qj+"','"+String(Number(c.total||c.replyCount||0)||0)+"')";
    var d=base+',{"style":"FULL","type":"qd","click":'+JSON.stringify(click)+'}';
    return '<img src="'+d.replace(/"/g,"&quot;")+'">';
}
function qdAuthorSayCardV20(text,bid,cid,provider){
    text=String(text||"").trim();if(!qfAuthorSayRealV327(text))return "";
    provider=String(provider||"");
    var clickable=(provider===""||provider==="晴天");
    var author=qfBookVarV09.call(this,"qf_author","作者"),w=1080,lp=62,rp=62,font="system-ui,Arial,sans-serif";
    /* alpha3.6：旧版固定 slice(27) 没考虑汉字/英文实际宽度，38px 字号下 27 个汉字会超过正文宽度。
       改按视觉宽度估算换行；保留原文换行，同时避免标点单独掉到下一行。 */
    function unit(ch){
        if(/[\u2E80-\u9FFF\uF900-\uFAFF\uFF00-\uFFEF]/.test(ch))return 1;
        if(/[A-Z0-9]/.test(ch))return .68;
        if(/[a-z]/.test(ch))return .56;
        if(/\s/.test(ch))return .32;
        return .52;
    }
    function wrap(src,limit,maxRows){
        var out=[],paras=String(src||'').replace(/\r/g,'').split('\n');
        for(var p=0;p<paras.length&&out.length<maxRows;p++){
            var ss=paras[p],line='',u=0;
            if(!ss){if(out.length&&out[out.length-1]!=='')out.push('');continue;}
            for(var i=0;i<ss.length&&out.length<maxRows;i++){
                var ch=ss.charAt(i),cu=unit(ch);
                if(line&&u+cu>limit){
                    /* 句号/逗号等不要单独成为下一行首字符。 */
                    if(/[，。！？；：、,.!?;:）】》”’]/.test(ch)){line+=ch;out.push(line);line='';u=0;continue;}
                    out.push(line);line=ch;u=cu;
                }else{line+=ch;u+=cu;}
            }
            if(line&&out.length<maxRows)out.push(line);
        }
        if(out.length>maxRows)out=out.slice(0,maxRows);
        var consumed=out.join('').replace(/\s/g,'').length,full=String(src||'').replace(/\s/g,'').length;
        if(out.length&&consumed<full){var last=out.length-1;out[last]=out[last].replace(/[，。！？；：、,.!?;:\s]+$/,'');if(out[last].length>1)out[last]=out[last].slice(0,-1)+'…';else out[last]+='…';}
        return out;
    }
    var rows=wrap(text,29.0,4),right=provider==="晴天"?"晴天 · 查看 ›":(!provider?"起点官方 · 查看 ›":provider+"服务器");
    var visualSig=String(author)+'\u001f'+right+'\u001f'+rows.join('\n'),base=qdCardVisGetV500('author',visualSig),y=96,svg='';
    svg+='<rect x="34" y="25" width="164" height="52" rx="26" fill="#4A74E4"/>'+ 
         '<text x="116" y="60" font-size="28" font-family="'+font+'" fill="#fff" font-weight="700" text-anchor="middle">作者说</text>'+ 
         '<text x="'+(w-rp)+'" y="59" font-size="24" text-anchor="end" font-family="'+font+'" fill="#8992A2">'+qfEscV13(right)+'</text>';
    y+=30;
    svg+='<text x="'+lp+'" y="'+y+'" font-size="28" font-family="'+font+'" fill="#4A5570" font-weight="650">'+qfEscV13(author||"作者")+'</text>';y+=48;
    for(var i=0;i<rows.length;i++){
        if(rows[i]===''){y+=20;continue;}
        svg+='<text x="'+lp+'" y="'+y+'" font-size="31" font-family="'+font+'" fill="#27282B" font-weight="400">'+qfEscV13(rows[i])+'</text>';y+=47;
    }
    y+=25;
    if(!base){
        var j=qfImageJavaV14(this);if(!j)return "";try{if(typeof j.base64Encode!=="function")return "";}catch(e0){return "";}
        var final='<svg width="'+w+'" height="'+y+'" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="'+(w-4)+'" height="'+(y-4)+'" rx="38" fill="rgba(249,250,255,0.34)" stroke="#DDE2ED" stroke-width="1"/>'+svg+'</svg>';
        base=qdCardVisPutV500(j,'author',visualSig,final);if(!base)return "";
    }
    if(!clickable)return '<img src="'+base.replace(/"/g,'&quot;')+'">';
    var openProvider=provider==="晴天"?"晴天":"",payload="",authorPayload="";
    if(!openProvider){try{payload=encodeURIComponent(text);authorPayload=encodeURIComponent(String(author||""));}catch(_ep){payload=String(text||"");authorPayload=String(author||"");}}
    var ob={style:"FULL",type:"qd",click:"qfOpenAuthorSayV314('"+qfEscJsV13(bid)+"','"+qfEscJsV13(cid)+"','"+qfEscJsV13(openProvider)+"','"+qfEscJsV13(payload)+"','"+qfEscJsV13(authorPayload)+"')"};
    return '<img src="'+(base+','+JSON.stringify(ob)).replace(/"/g,'&quot;')+'">';
}

function qdChapterTalkCardV20(rawList,total,bid,cid){
    var src=qdV20List(rawList),list=[];
    for(var i=0;i<src.length&&list.length<2;i++){var c=src[i]||{},txt=qdV20CleanCommentText(qdV20CommentText(c));if(!txt)continue;var u=qdV20CommentUser(c);list.push({name:u.name,content:txt,like:qdV20CommentLike(c),reply:qdV20CommentReply(c)});}
    /* beta22：本章说卡只展示真实评论预览。没有任何可展示评论时不生成提示占位卡。 */
    if(!list.length)return "";
    var totalNum=Number(total);if(!isFinite(totalNum)||totalNum<1)totalNum=list.length;
    var sigParts=[String(totalNum)];for(var si=0;si<list.length;si++){var sc=list[si];sigParts.push(String(sc.name||''),String(sc.content||''),String(sc.like||0),String(sc.reply||0));}
    var visualSig=sigParts.join('\u001f'),base=qdCardVisGetV500('chapter-b8',visualSig);
    var w=1080,lp=58,rp=58,y=104,svg="",font="system-ui,Arial,sans-serif",rightText=totalNum+' 条评论 ›';
    svg+='<rect x="34" y="28" width="178" height="58" rx="29" fill="#FFF0ED" stroke="#FFD8D1" stroke-width="1"/>'+
         '<text x="123" y="67" font-size="31" font-family="'+font+'" fill="#E65A4F" font-weight="700" text-anchor="middle">本章说</text>'+
         '<text x="'+(w-rp)+'" y="67" font-size="27" text-anchor="end" font-family="'+font+'" fill="#9A9CA2">'+qfEscV13(rightText)+'</text>';
    for(var k=0;k<list.length;k++){
        var c2=list[k],tx=c2.content,rows=[],max=24;while(tx){rows.push(tx.slice(0,max));tx=tx.slice(max);}if(rows.length>2){rows=rows.slice(0,2);rows[1]=rows[1].slice(0,max-1)+"…";}
        y+=32;svg+='<line x1="'+lp+'" y1="'+y+'" x2="'+(w-rp)+'" y2="'+y+'" stroke="#F0F1F3" stroke-width="1"/>';y+=54;
        svg+='<text x="'+lp+'" y="'+y+'" font-size="32" font-family="'+font+'" fill="#56585D" font-weight="600">'+qfEscV13(c2.name||"书友")+'</text>';
        var meta=[];if(c2.reply>0)meta.push(c2.reply+"回复");if(c2.like>0)meta.push("♡ "+c2.like);if(meta.length)svg+='<text x="'+(w-rp)+'" y="'+y+'" font-size="25" text-anchor="end" font-family="'+font+'" fill="#A3A5AB">'+meta.join(" · ")+'</text>';
        y+=56;for(var rr=0;rr<rows.length;rr++){svg+='<text x="'+lp+'" y="'+y+'" font-size="38" font-family="'+font+'" fill="#303238">'+qfEscV13(rows[rr])+'</text>';y+=55;}y+=12;
    }
    y+=28;
    if(!base){
        var j=qfImageJavaV14(this);if(!j)return "";try{if(typeof j.base64Encode!=="function")return "";}catch(e0){return "";}
        var final='<svg width="'+w+'" height="'+y+'" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="'+(w-4)+'" height="'+(y-4)+'" rx="44" fill="#FCFCFD" stroke="#ECEDEF" stroke-width="1.2"/>'+svg+'</svg>';
        base=qdCardVisPutV500(j,'chapter-b8',visualSig,final);if(!base)return "";
    }
    var ob={style:"FULL",type:"qd",click:"showCmtV20('"+String(bid)+"','"+String(cid)+"','-1','0','zp','','"+String(totalNum)+"')"};
    return '<img src="'+base+','+JSON.stringify(ob)+'">';
}

/* ---------- 作者说 ---------- */

function qdBubbleImageV20(count,bid,cid,pid,seg,hot,quote,quoteEncoded,quoteJsEncoded){
    var u=qdBubbleDataV20.call(this,count,bid,cid,pid,seg,hot,quote,quoteEncoded,quoteJsEncoded);
    return u?'<img src="'+u.replace(/"/g,"&quot;")+'">':"";
}
/* ---------- 热评 ---------- */

/* alpha15：旧流程先 split/filter 一遍正文，再单独扫描 lines 建 textIdx。
 * 这里把两次 O(n) 遍历合并；lines 的输出语义保持不变。 */
function qdV22BuildLinesV470(content,needTextIdx){
    var src=String(content||"");if(src.indexOf("\r")>=0)src=src.replace(/\r/g,"");
    var raw=src.split("\n"),lines=[],idx=[],needIdx=(needTextIdx!==false),hasMedia=false;
    /* alpha17：只显示作者说/本章说时最终输出仍保持旧版 trim/去空行语义，
       但不再建立完全用不到的 textIdx，也不再执行媒体判定。 */
    if(needIdx)hasMedia=(src.indexOf("data:image/")>=0)||(src.indexOf("<")>=0&&/<\s*img\b/i.test(src));
    for(var i=0;i<raw.length;i++){
        var t=String(raw[i]||"").trim();if(!t)continue;
        var pos=lines.length;lines.push(t);
        if(needIdx&&(!hasMedia||(!/^<\s*img\b/i.test(t)&&t.indexOf("data:image/")<0)))idx.push(pos);
    }
    return {lines:lines,textIdx:idx};
}



/* ============================================================
 * v2.9.4 基础运行时恢复
 * 只恢复被误删的通用 helper，不恢复任何私人服务器。
 * ============================================================ */

function qdFetchCommentsV20(bid,cid,pid,seg,quote){
    return qdFetchOfficialCommentsV20.call(this,bid,cid,pid,seg,quote);
}
/* ---------- 起点源附件同款 官方章评 ---------- */

function qfTextKeepMediaV323(v){
    var src=String(v==null?"":v),hint=0;
    /* alpha16：普通小说正文几乎从不含“<”或“![”，先用 indexOf 过滤掉全局媒体 regex。 */
    if(src.indexOf("<")>=0&&/<img\b/i.test(src))hint|=1;
    if(src.indexOf("![")>=0&&src.indexOf("](")>=0&&/!\[[^\]]*\]\(https?:\/\//i.test(src))hint|=2;
    if(!(hint&3))return qfText(src);
    var imgs=[];
    if(hint&2){
        src=src.replace(/!\[([^\]]*)\]\((https?:\/\/[^\s)]+)\)/gi,function(_m,alt,url){
            return '<img src="'+String(url||'').replace(/"/g,'&quot;')+'" alt="'+String(alt||'').replace(/"/g,'&quot;')+'">';
        });
        hint|=1;
    }
    if(hint&1){
        src=src.replace(/<img\b[^>]*>/gi,function(tag){
            var t=String(tag||'');
            t=t.replace(/(\bsrc\s*=\s*["'])\/\//i,'$1https://');
            imgs.push(t);
            return "\nQFIMGV323_"+(imgs.length-1)+"_END\n";
        });
    }
    var out=qfText(src);
    if(imgs.length){
        out=out.replace(/QFIMGV323_(\d+)_END/g,function(_m,n){n=Number(n);return n>=0&&n<imgs.length?imgs[n]:"";});
        out=out.replace(/(^|\n)\s*我的彩蛋章\s*-?\s*\d{8,}\s*-\s*\d+\s*插图\s*(?=\n|$)/g,'$1');
        out=out.replace(/\n{3,}/g,'\n\n').trim();
    }
    return out;
}

/* alpha35：晴天评论轻量路径。
 * 正文只读取 /api/comments 的数量索引来画气泡；不读取 /comments、/chapterComments 详情。
 * 热评排序/列表交给晴天原生页面，不再在正文阶段做任何评论详情请求。
 */

/* beta17.2：情无正文 + 起点本地段评的快速索引。
 * 情无正文服务器本身已经提供 comments.php?action=summary，ParagraphId 与情无正文天然对齐。
 * 本地模式只借它画气泡/判断热段；真正点击段评仍进入起点本地评论页。
 * 这样避免每章正文阶段都串行执行起点 PC+移动 reviewSummary 双兜底。 */
function qfQwLocalFastIndexV3172(bid,cid){
    var cacheObj=qfRuntimeCacheV13(this),key="qf-qw-local-fast-index-v3172-"+String(bid)+"-"+String(cid),now=Date.now();
    try{
        if(cacheObj&&qfCallableV13(cacheObj,"getFromMemory")){
            var old=String(cacheObj.getFromMemory(key)||"");
            if(old){var co=JSON.parse(old);if(co&&co.ts&&now-Number(co.ts)<120000&&Array.isArray(co.items))return co.items;}
        }
    }catch(_c0){}
    var out=[];
    try{
        var fn=qfModuleFnV38.call(this,"review_server_core","qfQwCommentApiV315");
        if(typeof fn!=="function")return out;
        var r=fn.call(this,"summary",{book_id:bid,chapter_id:cid})||{},d=r.Data||r.data||{},box=d.Getparagraphscommentcounts||d.getparagraphscommentcounts||d.GetParagraphsCommentCounts||{},list=box.DataList||box.dataList||box.List||box.list||[];
        if(!Array.isArray(list)){try{list=Java.from(list);}catch(_ja){list=[];}}
        var seen={},title=null;
        for(var i=0;i<list.length;i++){
            var x=list[i]||{},pid=Number(x.ParagraphId!==undefined?x.ParagraphId:(x.paragraphId!==undefined?x.paragraphId:(x.ParagraphsId!==undefined?x.ParagraphsId:x.paragraphsId))),cnt=Number(x.CommentCount!==undefined?x.CommentCount:(x.commentCount!==undefined?x.commentCount:(x.TextCount!==undefined?x.TextCount:(x.textCount!==undefined?x.textCount:(x.ReviewCount!==undefined?x.ReviewCount:x.reviewCount)))))||0;
            if(isNaN(pid)||cnt<=0)continue;
            var it={paragraphId:pid>0?pid:-1,segmentId:pid>0?pid:0,count:cnt,reviewId:String(x.ReviewId||x.reviewId||""),hot:Number(x.HasHotComment||x.hasHotComment||0)!==0,quote:String(x.QuoteContent||x.quoteContent||x.ParagraphContent||x.paragraphContent||""),raw:x};
            if(pid<=0){if(!title||cnt>Number(title.count||0))title=it;continue;}
            var k=String(pid);if(!seen[k]||cnt>Number(seen[k].count||0))seen[k]=it;
        }
        if(title)out.push(title);
        for(var k2 in seen)if(Object.prototype.hasOwnProperty.call(seen,k2))out.push(seen[k2]);
        out.sort(function(a,b){if(Number(a.paragraphId)<0)return -1;if(Number(b.paragraphId)<0)return 1;return Number(a.paragraphId)-Number(b.paragraphId);});
    }catch(_e){}
    try{if(cacheObj&&qfCallableV13(cacheObj,"putMemory"))cacheObj.putMemory(key,JSON.stringify({ts:now,items:out}));}catch(_c1){}
    return out;
}

function qdDecorateContentV26(content,bid,cid,isPaid,provider,hotCtx){
    var _dAll=Date.now(),_dStage=Date.now();
    /* alpha23：保留正文中的彩蛋章/插图 img，普通文本仍沿用 qfText 清洗。 */
    content=qfTextKeepMediaV323(content);
    if(!content||!bid||!cid)return content;
    hotCtx=(hotCtx&&typeof hotCtx==='object')?hotCtx:{};
    var hf=hotCtx.flags&&typeof hotCtx.flags==='object'?hotCtx.flags:null;
    /* alpha9：正文入口已经读取过一次四个显示开关，模块直接复用；旧入口仍兼容独立读取。 */
    var showBubble=hf?!!hf.bubble:qfToggle.call(this,"起点段评",true);
    var showHot=hf?!!hf.hot:qfToggle.call(this,"热评显示",true);
    var showTalk=hf?!!hf.talk:qfToggle.call(this,"本章说",true);
    var showAuthor=hf?!!hf.author:qfToggle.call(this,"作家说",true);

    /* alpha34：功能级懒执行。四项全部关闭时，评论/本章说/作者说模块完全不进入。 */
    if(!showBubble&&!showHot&&!showTalk&&!showAuthor){
        try{var _chOff=qfChapter(this);if(_chOff&&_chOff.putImgUrl)_chOff.putImgUrl(null);}catch(_off){}
        return content;
    }

    /* alpha84：服务器评论是否生效由 Comment Registry 的 bind/mode/capability 决定；
       其它正文源即使选择“服务器”仍保持起点本地评论链。 */
    var serverProvider="";
    if(hotCtx.routeResolved===true)serverProvider=String(hotCtx.serverProvider||"");
    else{try{serverProvider=qfCommentRouteSetV315.call(this,bid,cid,provider);}catch(_route9){serverProvider="";}}
    var actualProvider=String(provider||"");
    /* alpha11：快照 key 需要包含智能对齐开关；这里提前读取一次，后面直接复用。 */
    var smart=!!isPaid&&["猫眼","得奇","69书吧"].indexOf(actualProvider)>=0&&((hf&&hf.smartAlign!==undefined)?!!hf.smartAlign:qfToggle.call(this,"兜底段评智能对齐",true));
    var _snapKey460=qdReviewSnapKeyV460(bid,cid,!!isPaid,actualProvider,serverProvider,{bubble:showBubble,hot:showHot,talk:showTalk,author:showAuthor},smart,content);
    var _snap460=qdReviewSnapGetV460(_snapKey460,!!serverProvider);
    qfChapterSubStage("decorate.setup-snapshot",Date.now()-_dStage,_snap460?"hit":"miss");_dStage=Date.now();
    if(_snap460){
        qdReviewSnapRestoreTitleV460.call(this,bid,cid,showBubble,_snap460);
        return String(_snap460.body||content);
    }
    /* beta17.3：情无 + 本地段评恢复起点官方段落索引。
     * beta17.2 借情无 summary 直接映射起点本地气泡，在部分章节 ParagraphId 口径不一致，
     * 会出现整章无气泡。现在本地气泡重新以起点官方 reviewSummary 为准；
     * 但章末评论详情仍保持懒加载，不在翻章时请求。 */
    var qwLocalMode=(actualProvider==="情无"&&!serverProvider);
    var qwChapterLocal=!!(serverProvider==="情无"&&qfCommentPolicyV83(serverProvider,"chapterLocal",false));
    /* beta17.4：情无本章说恢复真实预览。
     * 不再零详情预取，而是正文阶段只取起点章末接口第一页 2 条，
     * 用于卡片预览；完整列表仍在点击后加载。 */
    var qwPreviewChapter=!!(actualProvider==="情无");
    var serverSummary=null;
    var items=[];
    var summaryForHot=!serverProvider||qfCommentPolicyV83(serverProvider,"summaryForHot",true);

    /* v3.5 beta18：本地评论装饰的两条独立网络请求并发预取。
     * Provider 正文已经成功后才进入这里；预取失败不改变任何数据来源，
     * 后面的 qdReviewSummary / qdFetchChapterComments 会自动按原稳定链重试。 */
    if(!serverProvider){
        try{
            var _wantSummary=!!(showBubble||(showHot&&summaryForHot));
            /* alpha9：热评已有专用 paragraph hot endpoint；关闭“本章说”时不再为了热评
               预取 getchapterendreview。真正命中 hot 段落时再按专用接口获取。 */
            var _wantChapter=!!showTalk;
            var _primeSize=2;
            if(_wantSummary&&_wantChapter)qdPrimeReviewV350.call(this,bid,cid,!!isPaid,true,true,_primeSize);
        }catch(_prime350){}
    }
    qfChapterSubStage("decorate.review-prime",Date.now()-_dStage,(!serverProvider&&showTalk)?"local":"skip");_dStage=Date.now();
    if(showBubble||(showHot&&summaryForHot)){
        try{
            if(serverProvider){serverSummary=qfCommentCallV83.call(this,serverProvider,"summary",[bid,cid]);items=(serverSummary&&serverSummary.items)||[];}
            else if(qwLocalMode){
                /* 情无正文 + 本地段评：优先一次起点 PC/mobile 官方 summary。
                 * 不再使用 beta17.2 的情无 ParagraphId 直映射；只有官方 summary 完全为空时
                 * 才进入旧移动端兜底，避免“有少量气泡也再跑第二套接口”的额外等待。 */
                try{items=qdReviewSummaryV292.call(this,bid,cid)||[];}catch(_qwl0){items=[];}
                if(!items.length){try{items=qdReviewSummaryV11.call(this,bid,cid)||[];}catch(_qwl1){items=[];}}
            }else items=qdReviewSummaryV22.call(this,bid,cid,!!isPaid)||[];
        }catch(e0){items=[];}
    }
    qfChapterSubStage("decorate.summary-read",Date.now()-_dStage,"items="+String(items&&items.length||0));_dStage=Date.now();
    if(!items||!items.length){
        try{qfReviewEdgeTrace({stage:"decorate-summary-empty",source:serverProvider||"local",items:0,total:0,valid:false,detail:"summary items empty before mapping"});}catch(_edgeDS){}
    }

    /* beta21.3：神魔/晴天气泡索引双向容错。
     * - 服务器段评：服务器 summary 无法映射时借起点官方 summary 画气泡；
     * - 本地段评：起点 summary 无法映射时借实际正文服务器 summary 画气泡。
     * 这里只替换 paragraphId/count 索引，不改变点击后的评论数据来源。 */
    if(showBubble&&(actualProvider==="神魔"||actualProvider==="晴天")&&!qfBubbleItemsUsableV353(content,items)){
        var _alt353=[];
        try{
            if(serverProvider){
                _alt353=qdReviewSummaryV22.call(this,bid,cid,!!isPaid)||[];
            }else{
                var _ss353=qfCommentCallV83.call(this,actualProvider,"summary",[bid,cid]);
                _alt353=(_ss353&&Array.isArray(_ss353.items))?_ss353.items:[];
            }
        }catch(_e353){_alt353=[];}
        if(qfBubbleItemsUsableV353(content,_alt353))items=_alt353;
    }

    /* alpha84：需要原生评论装饰的 Provider 由 capability/policy 决定。
       主评论模块不再识别具体服务器源名称。 */
    if(serverProvider&&qfCommentPolicyV83(serverProvider,"nativeDecorate",false)){
        try{
            var nativeBody=qfCommentCallV83.call(this,serverProvider,"decorate",[content,bid,cid,showBubble,showTalk,showAuthor,items]);
            if(nativeBody!==null&&nativeBody!==undefined)return nativeBody;
        }catch(_native){}
    }

    /* beta22：本章说预览与评论详情来源解耦。
     * 所有 Provider 的正文卡统一只取起点官方章末接口前 2 条真实评论；
     * 点击卡片后仍按本地/服务器路由打开对应评论源。这样避免服务器章评接口/原生 SVG
     * 为正文阶段额外增加不一致的网络开销，也保证卡片样式与预览数量统一。 */
    qfChapterSubStage("decorate.alt-native",Date.now()-_dStage,serverProvider?"server":"local");_dStage=Date.now();
    var chapterPack=null,chapterPreviewPack=null,hotPackByPid={};
    if(showTalk){
        try{chapterPreviewPack=qdFetchChapterCommentsV22.call(this,bid,cid,1,2);}catch(_pv22){chapterPreviewPack=null;}
    }
    qfChapterSubStage("decorate.chapter-preview",Date.now()-_dStage,chapterPreviewPack?"hit":"empty");_dStage=Date.now();
    if(showTalk){
        try{
            qfReviewEdgeTrace({
                stage:"decorate-chapter-preview",
                source:String(chapterPreviewPack&&chapterPreviewPack.source||""),
                items:Number(chapterPreviewPack&&chapterPreviewPack.rows&&chapterPreviewPack.rows.length||0),
                total:Number(chapterPreviewPack&&chapterPreviewPack.total||0),
                segments:Number(chapterPreviewPack&&chapterPreviewPack.segments&&chapterPreviewPack.segments.length||0),
                valid:!!chapterPreviewPack,
                detail:chapterPreviewPack?"preview-pack":"preview-empty"
            });
        }catch(_edgeCP){}
    }
    if(showHot){
        /* 本地模式直接复用已经获取的官方预览包；服务器模式优先使用 summary.hot，
         * 只有 summary 没有热评材料时才额外拉服务器 chapter pack。 */
        /* v4.0：本地热评不再为了热评额外拉整章 getchapterendreview。
         * 如果本章说已经拿到 preview，可零成本保留为异常兜底；真正热评优先在命中 hot 段落时调用专用 getparagraphshotcomments。 */
        if(!serverProvider){chapterPack=chapterPreviewPack||null;}
        else{
            var _hasServerHot=false;try{for(var _hk0 in (serverSummary&&serverSummary.hot||{})){if(Object.prototype.hasOwnProperty.call(serverSummary.hot,_hk0)&&serverSummary.hot[_hk0]&&serverSummary.hot[_hk0].length){_hasServerHot=true;break;}}}catch(_h0){}
            if(!_hasServerHot){try{chapterPack=qfCommentCallV83.call(this,serverProvider,"chapter",[bid,cid]);}catch(_cpS){chapterPack=null;}}
        }
    }
    if(showTalk||showHot){
        if(serverProvider&&serverSummary&&serverSummary.hot){
            try{for(var _hk in serverSummary.hot){if(Object.prototype.hasOwnProperty.call(serverSummary.hot,_hk)&&serverSummary.hot[_hk]&&serverSummary.hot[_hk].length)hotPackByPid[String(_hk)]={rows:serverSummary.hot[_hk],total:serverSummary.hot[_hk].length,source:serverProvider+"服务器"};}}catch(_hs){}
        }
        if(showHot&&chapterPack&&Array.isArray(chapterPack.segments)){
            try{
                for(var _si=0;_si<chapterPack.segments.length;_si++){
                    var _sg=chapterPack.segments[_si]||{};
                    var _sp=Number(_sg.ParagraphsId!==undefined?_sg.ParagraphsId:(_sg.paragraphsId!==undefined?_sg.paragraphsId:(_sg.ParagraphId!==undefined?_sg.ParagraphId:(_sg.paragraphId!==undefined?_sg.paragraphId:(_sg.SegmentId!==undefined?_sg.SegmentId:_sg.segmentId)))));
                    var _dl=_sg.DataList||_sg.dataList||_sg.List||_sg.list||[];
                    if(!Array.isArray(_dl)||!(_sp>0)||!_dl.length)continue;
                    var _q=String(_sg.QuoteContent||_sg.quoteContent||_sg.RefferContent||_sg.refferContent||"");
                    var _rows=[];
                    for(var _di=0;_di<_dl.length&&_rows.length<3;_di++){var _nr=serverProvider?qfServerNormV315(_dl[_di],_q):qdNormalizeCommentV13(_dl[_di],_q);if(_nr&&_nr.content)_rows.push(_nr);}
                    if(_rows.length&&!hotPackByPid[String(_sp)])hotPackByPid[String(_sp)]={rows:_rows,total:Number(_sg.ReviewCount||_sg.reviewCount||_rows.length)||_rows.length,source:serverProvider?(serverProvider+"服务器"):"起点官方App"};
                }
            }catch(_cp1){}
        }
    }

    qfChapterSubStage("decorate.hot-pack-map",Date.now()-_dStage,"pack="+String(Object.keys(hotPackByPid||{}).length));_dStage=Date.now();
    /* alpha15：正文行 + textIdx 一次构建；随后 items 只做一次 normalization/planning。
     * decoration plan 同时供热评预取和最终渲染使用，不再重复扫描 items/paraMap。 */
    var _needTextIdx470=!!(showBubble||showHot);
    var _lm470=qdV22BuildLinesV470(content,_needTextIdx470),lines=_lm470.lines,textIdx=_lm470.textIdx;
    /* alpha17：不再直接反复 lines[ix] += ...；每个正文行只记录小型追加片段，
       最终与作者说/本章说尾卡一起一次 join，避免长章节正文字符串被多次复制。 */
    var lineExtra480=[],tail480=[];
    var _renderBubble541=0,_renderHot541=0,_renderAuthor541=0,_renderTalk541=0;
    function pushLineExtra480(ix,v){
        v=String(v||'');if(!v)return;
        /* alpha18：每行最多气泡+热评两个小片段，直接合并小字符串比创建 Array 更轻；
           不触碰正文 lines 本身，因此仍避免大正文重复复制。 */
        lineExtra480[ix]=lineExtra480[ix]?lineExtra480[ix]+v:v;
    }
    var titleItem=null,hotN=0,detailCache={},hotFallbackBudget=0;

    /* 优选源沿用直接 ParagraphId；兜底源启用智能文本锚点对齐。 */
    var smartMap={};
    if(smart&&items.length&&textIdx.length){
        try{
            smartMap=qfModuleFnV38.call(this,"review_align","qdV26BuildAlignMap").call(
                this,bid,cid,provider,items,lines,textIdx
            )||{};
        }catch(e2){smartMap={};}
    }

    var plan470=[],hotPid470=[],hotSeen470={};
    for(var a=0;a<items.length;a++){
        var it=items[a]||{},pid470=Number(it.paragraphId),cnt470=Number(it.count||0);
        if(pid470<0){if(!titleItem||cnt470>Number(titleItem.count||0))titleItem=it;continue;}
        if(!(pid470>0)||!(cnt470>0))continue;
        /* 热评单开时，非 hot 段既不会画气泡也不会生成热评卡，直接不进入 decoration plan。 */
        if(!showBubble&&!(showHot&&it.hot))continue;
        var ix470=(smart&&smartMap[String(pid470)]!==undefined)?Number(smartMap[String(pid470)]):textIdx[pid470-1];
        if(ix470===undefined||ix470<0||ix470>=lines.length)continue;
        var seg470=Number(it.segmentId);if(isNaN(seg470))seg470=pid470;
        var quote470=String(lines[ix470]||"");
        /* alpha18：这里不再提前 encodeURIComponent。只有真正生成气泡，或热评接口确实返回
           可显示热评时，才懒计算 URI encoded + JS escaped quote，并在同一行复用。 */
        var row470=qdDecorRowAllocV490(it,pid470,cnt470,seg470,ix470,quote470,!!it.hot);
        plan470.push(row470);
        if(showHot&&!serverProvider&&row470[8]&&hotPid470.length<2&&!hotSeen470[String(pid470)]){
            var _localHot536=hotPackByPid[String(pid470)]||hotPackByPid[String(seg470)]||null;
            var _localRows536=_localHot536&&Array.isArray(_localHot536.rows)?_localHot536.rows:[];
            if(!_localRows536.length){hotSeen470[String(pid470)]=1;hotPid470.push(pid470);}
            else{try{qfChapterHotTraceV535({stage:"prime-local-skip",pid:String(pid470),profile:String(_localHot536.source||""),transport:"decorate",cache:"local",ok:true,rows:_localRows536.length,ms:0,detail:"reuse"});}catch(_pls536){}}
        }
    }

    /* alpha9.8：先统计本章 hot 候选中已有多少 PID 能直接复用 chapter-preview/App rows。
     * 本地可直接满足 2 张热评卡时进入 LOCAL-FULL：
     * - 不 prime；
     * - 不调用专用 getparagraphshotcomments；
     * - 仍按原 plan470 顺序渲染前两张本地可用热评。
     * 本地不足 2 张时完全保留 alpha9.7 HYBRID 行为。 */
    var _cand538=[],_localReady538=[],_localSeen538={};
    try{
        for(var _ci538=0;_ci538<plan470.length;_ci538++){
            var _cr538=plan470[_ci538];
            if(!_cr538||!_cr538[8])continue;
            var _pid538=String(_cr538[1]||""),_seg538=String(_cr538[3]||"");
            if(_cand538.length<16)_cand538.push(_pid538);
            var _lp538=hotPackByPid[_pid538]||hotPackByPid[_seg538]||null;
            var _lr538=_lp538&&Array.isArray(_lp538.rows)?_lp538.rows:[];
            if(_lr538.length&&!_localSeen538[_pid538]){
                _localSeen538[_pid538]=1;
                if(_localReady538.length<8)_localReady538.push(_pid538);
            }
        }
    }catch(_lc538){}
    var _localFull538=showHot&&!serverProvider&&_localReady538.length>=2;
    if(_localFull538)hotPid470=[];
    try{
        qfChapterHotPlanV536({
            candidates:_cand538,
            prime:hotPid470,
            localReady:_localReady538,
            mode:_localFull538?"LOCAL-FULL":"HYBRID",
            showHot:showHot,
            server:!!serverProvider
        });
    }catch(_hp538){}
    /* HYBRID 仍保留 alpha10/alpha9.7 prime；LOCAL-FULL 则 hotPid470 已清空。 */
    if(showHot&&!serverProvider&&hotPid470.length>1){try{qdPrimeParagraphHotV450.call(this,bid,cid,hotPid470,1,3);}catch(_ph450){}}

    qfChapterSubStage("decorate.build-plan",Date.now()-_dStage,"plan="+String(plan470.length));_dStage=Date.now();
    try{
        if((items&&items.length)&&plan470.length<Math.min(3,items.length)){
            qfReviewEdgeTrace({
                stage:"mapping-gap",
                source:serverProvider||"local",
                items:Number(items.length||0),
                total:Number(plan470.length||0),
                valid:plan470.length>0,
                detail:"summary-to-textIdx sparse"
            });
        }
    }catch(_edgeMG){}
    for(var b=0;b<plan470.length;b++){
        var pp470=plan470[b],x=pp470[0],pid=pp470[1],cnt2=pp470[2],seg=pp470[3],ix=pp470[4],localQuote=pp470[5];

        if(showBubble){
            var localQuoteEncoded=qdDecorRowQuoteV490(pp470),localQuoteJsEncoded=qdDecorRowQuoteJsV490(pp470);
            var _bubbleHtml541=qdBubbleImageV20.call(
                this,cnt2,bid,cid,pid,seg,!!pp470[8],localQuote,localQuoteEncoded,localQuoteJsEncoded
            );
            if(_bubbleHtml541){_renderBubble541++;pushLineExtra480(ix,_bubbleHtml541);}
        }

        if(showHot&&x.hot&&hotN<2){
            var dk=String(pid)+"|"+String(seg),pack=detailCache[dk];
            if(!pack){
                /* alpha9.7：热路径先复用本章说/章末已存在的同 PID 评论。
                 * 只有本地无可用 rows 时才调用专用 getparagraphshotcomments。
                 * 数据源优先级变化仅用于减少重复网络，不改变最终热评卡选择逻辑。 */
                var _reuse537=hotPackByPid[String(pid)]||hotPackByPid[String(seg)]||null;
                var _reuseRows537=_reuse537&&Array.isArray(_reuse537.rows)?_reuse537.rows:[];
                if(_reuseRows537.length){
                    pack=_reuse537;
                    try{qfChapterHotTraceV535({stage:"local-reuse",pid:String(pid),profile:String(pack.source||""),transport:"decorate",cache:"local",ok:true,rows:_reuseRows537.length,ms:0,detail:_localFull538?"local-full":"reuse-first"});}catch(_lr537){}
                }else if(_localFull538){
                    pack=null;
                    try{qfChapterHotTraceV535({stage:"local-full-skip",pid:String(pid),profile:"",transport:"decorate",cache:"local",ok:true,rows:0,ms:0,detail:"dedicated-api-skipped"});}catch(_lfs538){}
                }else if(!serverProvider){
                    try{pack=qdFetchParagraphHotV402.call(this,bid,cid,pid,1,3);}catch(_hot402){pack=null;}
                    if(!pack||!pack.rows||!pack.rows.length)pack=_reuse537||pack;
                }else{
                    pack=_reuse537||null;
                }
                if(!pack&&hotFallbackBudget>0){
                    hotFallbackBudget--;
                    pack=serverProvider?qfServerCommentPackV315.call(this,serverProvider,bid,cid,Number(x.serverParaId||pid),1,10,false):null;
                }
                detailCache[dk]=pack;
            }
            var arr=(pack&&pack.rows)||[];
            try{
                qfChapterHotTraceV535({
                    stage:"candidate-result",pid:String(pid||""),profile:String(pack&&pack.source||""),
                    transport:"decorate",cache:"",ok:!!(pack&&pack.ok),rows:arr.length,ms:0,
                    detail:arr.length?"rows":"empty"
                });
            }catch(_hr536){}
            if(arr.length){
                /* alpha15：这里只需要点赞最高的一条，不再为了最多 3 条数据原地 sort 并修改共享缓存顺序。 */
                var _hotRow=null,_hotLike=-1;for(var _hr470=0;_hr470<arr.length;_hr470++){var _hc470=arr[_hr470];if(!_hc470||!_hc470.content)continue;var _hl470=Number(_hc470.like||0)||0;if(_hotRow===null||_hl470>_hotLike){_hotRow=_hc470;_hotLike=_hl470;}}
                if(_hotRow&&_hotRow.content){
                    /* alpha10：热评卡本身携带段落引用，不再依赖正文阶段逐段写 Java memory。 */
                    try{_hotRow.total=Number(pack&&pack.total||0)||0;}catch(_ht){}
                    /* 热评单开且接口最终无评论时，整章不会为这些段落生成 quote 点击参数。 */
                    var _hq490=qdDecorRowQuoteV490(pp470),_hjs490=qdDecorRowQuoteJsV490(pp470);
                    var hh=qdHotHtmlV20.call(
                        this,_hotRow,bid,cid,pid,seg,localQuote,_hq490,_hjs490
                    );
                    if(hh){pushLineExtra480(ix,"\n"+hh);hotN++;_renderHot541++;try{qfChapterHotRenderedV536(pid,arr.length,_hotLike);}catch(_rend536){}}
                }
            }
        }
    }

    qfChapterSubStage("decorate.bubble-hot-render",Date.now()-_dStage,"hot="+String(hotN));_dStage=Date.now();
    var _snapTitleCount460=(showBubble&&titleItem&&Number(titleItem.count||0)>0)?Number(titleItem.count||0):0;
    var _snapTitleHot460=!!(titleItem&&titleItem.hot);
    /* alpha15：章名 quote 只有存在章名气泡时才会在点击详情时读取；普通章节不再无条件写 Java memory。 */
    if(_snapTitleCount460>0){
        try{var _tc470=qfRuntimeCacheV13(this),_ch470=qfChapter(this),_tt470="";if(_ch470){_tt470=String(_ch470.title||"");if(!_tt470&&typeof _ch470.getTitle==="function")_tt470=String(_ch470.getTitle()||"");}if(_tt470&&_tc470&&qfCallableV13(_tc470,"putMemory"))_tc470.putMemory("qfv20-"+bid+"-"+cid+"-chapter-title",_tt470);}catch(_t470){}
    }
    try{
        var ch2=qfChapter(this);
        if(ch2&&ch2.putImgUrl){
            if(_snapTitleCount460>0){
                ch2.putImgUrl(
                    qdBubbleDataV20.call(
                        this,
                        _snapTitleCount460,
                        bid,cid,-1,0,_snapTitleHot460
                    )
                );
            }else{
                ch2.putImgUrl(null);
            }
        }
    }catch(e3){}

    qfChapterSubStage("decorate.title-meta",Date.now()-_dStage,"title="+String(_snapTitleCount460));_dStage=Date.now();
    if(showAuthor){
        /* beta14：作者说与“段评来源”解耦。正文实际来自晴天/情无/神魔时，
           即使段评选择本地，也先读取该正文 Provider 的作者说；没有再退起点官方。 */
        var as="",authorProvider="";
        if(qfCommentIsServerV83(actualProvider)&&!(qwLocalMode&&actualProvider==="情无")){
            try{as=qfCommentCallV83.call(this,actualProvider,"author",[bid,cid])||"";if(as)authorProvider=actualProvider;}catch(e4){as="";}
        }
        if(!as&&serverProvider&&serverProvider!==actualProvider){
            try{as=qfCommentCallV83.call(this,serverProvider,"author",[bid,cid])||"";if(as)authorProvider=serverProvider;}catch(_as2){as="";}
        }
        if(!as){
            /* alpha9：只有 Provider/服务器作者说都为空，才解析原始起点章节并准备官方作者说缓存。 */
            try{if(hotCtx.authorRaw)qfPrimeAuthorSayV38.call(this,hotCtx.authorRaw,bid,cid);}catch(_primeA9){}
            try{as=qdAuthorSayV20.call(this,bid,cid)||"";authorProvider="";}catch(_qa){as="";}
        }
        if(as){var _ac480=qdAuthorSayCardV20.call(this,as,bid,cid,authorProvider);if(_ac480){tail480.push(_ac480);_renderAuthor541++;}}
    }

    qfChapterSubStage("decorate.author-say",Date.now()-_dStage,showAuthor?"on":"off");_dStage=Date.now();
    if(showTalk){
        var cpv=chapterPreviewPack||{rows:[],total:0},pr=(cpv&&cpv.rows)||[],pt=Number(cpv&&cpv.total||0);
        /* 起点章末接口至少有一条真实评论时才生成卡片；最多显示前两条。
         * 不再用“章末讨论/点击后加载”占位图。 */
        if(pr.length){
            if(!(pt>0)&&titleItem&&Number(titleItem.count||0)>0)pt=Number(titleItem.count||0);
            var _card22=qdChapterTalkCardV20.call(this,pr,pt>0?pt:pr.length,bid,cid);
            if(_card22){tail480.push(_card22);_renderTalk541++;}
        }
    }

    qfChapterSubStage("decorate.chapter-talk",Date.now()-_dStage,showTalk?"on":"off");_dStage=Date.now();
    /* alpha17：最终正文只组装一次。
       旧实现先 lines.join，再为作者说/本章说执行 body += 大字符串；
       现在正文行、气泡/热评片段、尾卡统一进入 parts 后一次 join。 */
    var parts480=[];
    for(var _li480=0;_li480<lines.length;_li480++){
        if(_li480>0)parts480.push("\n");
        parts480.push(lines[_li480]);
        var _le480=lineExtra480[_li480];
        if(_le480)parts480.push(_le480);
    }
    for(var _ti480=0;_ti480<tail480.length;_ti480++){parts480.push("\n");parts480.push(tail480[_ti480]);}
    var body=parts480.join("");
    try{
        qfReviewEdgeTrace({
            stage:"renderer-final",
            source:serverProvider||"local",
            items:_renderBubble541,
            total:_renderHot541,
            segments:_renderTalk541,
            rawLen:body.length,
            valid:!!body,
            detail:"bubble="+String(_renderBubble541)+
                ",hot="+String(_renderHot541)+
                ",talk="+String(_renderTalk541)+
                ",author="+String(_renderAuthor541)+
                ",plan="+String(plan470.length)+
                ",tail="+String(tail480.length)
        });
    }catch(_edgeRF){}
    /* plan 已经全部消费，立即归还瞬时行对象。最终 body/快照不持有这些引用。 */
    qdDecorRowsReleaseV490(plan470);

    /* alpha11：只缓存已经完整生成的最终装饰结果；网络异常导致的空卡不会额外制造长期状态，
       TTL 远短于原 summary/chapter 业务缓存，且设置/Provider/正文变化都会生成不同 key。 */
    try{qdReviewSnapPutV460(_snapKey460,body,_snapTitleCount460,_snapTitleHot460);}catch(_snapPut460){}
    qfChapterSubStage("decorate.final-join-cache",Date.now()-_dStage,"len="+String(body.length));
    qfChapterSubStage("decorate.total",Date.now()-_dAll,"done");
    return body;
}
