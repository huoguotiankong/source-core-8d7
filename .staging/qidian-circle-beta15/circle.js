/* v3.1.0-beta5.6：书友圈加载速度 + 原生化美观专项优化。
 * - 分类规则完全沿用 beta5.5，不再改动动态/精华/同人候选与交叉逻辑；
 * - 首开取消“为了追求长讨论 JsId”而额外补拉一次 getcircledetail：beta5.4 后短 PostCategoryId=2 已有稳定兜底，减少一次串行网络请求；
 * - 书友圈 Boot 内存缓存延长到 5 分钟；WebView 分类页请求缓存支持空结果短缓存，避免同一失败参数在切分类/翻页时重复请求；
 * - 帖子详情首屏增加 2 分钟会话缓存，重复打开同帖直接复用；
 * - 图片统一 lazy + async decode + low priority，降低首屏图片解码阻塞；
 * - 顶部、卡片、分类条、详情和回复区做紧凑原生化重排；筛选加载改为轻量骨架屏。
 */
/* alpha80：继续将仅属于本模块的 helper 收回 lazy module，未进入功能时不建立全局函数。 */
function qfStripVideoMetaV13(text){
    var s=String(text==null?"":text);
    if(!/(?:VideoCover|VideoUrl|VideoId|VideoStatus|VideoHeight|VideoWidth)/i.test(s))return s;
    var keys=['"VideoCover"',"'VideoCover'",'VideoCover:', '"VideoUrl"',"'VideoUrl'",'VideoUrl:','"VideoId"',"'VideoId'",'VideoId:'];
    var p=-1;
    for(var i=0;i<keys.length;i++){var x=s.indexOf(keys[i]);if(x>=0&&(p<0||x<p))p=x;}
    if(p<0)return s;
    var st=p,b1=s.lastIndexOf('{',p),b2=s.lastIndexOf('(',p),b3=s.lastIndexOf('[',p);
    if(b1>=0&&p-b1<6)st=b1;else if(b2>=0&&p-b2<6)st=b2;else if(b3>=0&&p-b3<6)st=b3;
    return s.slice(0,st).replace(/[({\[\s]+$/g,'').trim();
}

/* alpha79：本模块私有依赖内聚。未进入该功能时，不在全局运行时建立这些 helper。 */
function qfCircleFaceTextV310(text){
    var s=String(text==null?"":text);
    /* beta5.1：先修复 beta5 第二层正则误伤 &nbsp; 形成的历史污染文本。 */
    s=s.replace(/&\[fn=\$1\]b\[fn=\$1\]p;/ig," ").replace(/\[fn=\$1\]/g,"");
    s=s.replace(/&#91;/ig,"[").replace(/&#93;/ig,"]");
    try{
        s=s.replace(/\[(?:fn|em|face|emoji)[ ]*[=:][ ]*([0-9]{1,3})\]/ig,function(_,n){
            var map={1:"👏",2:"🌹",3:"🤝",4:"😁",5:"😄",6:"🥺",7:"🙂",8:"😏",9:"😙",10:"👆🏻🐽",11:"🙄",12:"😭",13:"😵",14:"😥",15:"🖕🏻",16:"🥵",17:"😓",18:"🤫",19:"😂",20:"😢",21:"😍",22:"🤕🔨",23:"😑",24:"😫",25:"🤗",26:"🤪",27:"🙏",28:"😣",29:"💪",30:"💀",31:"😳",32:"😎",33:"🤭",34:"😄👏",35:"👍🏻",36:"🤓",37:"😡",38:"🙁",39:"😄❓",40:"😞",41:"😧",42:"💋",43:"☺️",44:"🤬",45:"😴",46:"🤠🚬",47:"😱",48:"🐷",49:"😪",50:"🤐",51:"🥴",52:"🌙",53:"❤️",54:"🔪",55:"🎁",56:"💔",57:"👊🏻",58:"😒",59:"✌🏻️",60:"😮",61:"🤨",62:"😴",63:"👏🏻",64:"🐲",65:"⭐",66:"🌧️",67:"🍉",68:"🍵",69:"🔥",70:"💯"};
            return map[Number(n)]||"";
        });
    }catch(e){}
    return s;
}

function qfRoleBookIdV12(bookObj){
    var vals=[];
    try{vals.push(String(bookObj&&bookObj.bookUrl||""));}catch(e0){}
    try{vals.push(String(bookObj&&bookObj.tocUrl||""));}catch(e1){}
    try{vals.push(String(bookObj&&bookObj.origin||""));}catch(e2){}
    try{vals.push(String(bookObj&&bookObj.bookId||""));}catch(e3){}
    try{
        if(bookObj&&bookObj.getVariable){
            vals.push("bookId="+String(bookObj.getVariable("qf_bid")||""));
        }
    }catch(e4){}

    for(var i=0;i<vals.length;i++){
        var x=vals[i];
        if(/^\d{5,}$/.test(x))return x;
        var m=x.match(/(?:book_id=|bookId=|\/book\/|qdbimg\/349573\/)(\d+)/i);
        if(m&&m[1])return String(m[1]);
    }
    return "";
}

function qfCircleCleanResult2964(v){
    var s=String(v==null?"":v).trim();
    if(!s||s==="null"||s==="undefined")return "";
    if(s.charAt(0)==='"'&&s.charAt(s.length-1)==='"'){
        try{return String(JSON.parse(s)||"");}catch(e0){}
    }
    return s;
}

function qfCircleExtractScript2965(){
    return "(function(){"
        +"function n(s){return String(s||'').replace(/[\\t\\r ]+/g,' ').replace(/\\n{3,}/g,'\\n\\n').trim();}"
        +"function bad(t){return !t||/^(书友圈|动态|热门|最新|精华|同人创作|全部|作家说|讨论|书评|登录|立即登录|打开起点读书|下载起点读书|发帖|查看全部帖子)/.test(t);}"
        +"function hrefOf(el){if(!el)return'';var as=[];if(el.matches&&el.matches('a[href]'))as=[el];else as=el.querySelectorAll('a[href]');for(var i=0;i<as.length;i++){var h=String(as[i].href||as[i].getAttribute('href')||'');if(h&&!/javascript:/i.test(h))return h;}return'';}"
        +"function imgOf(el){if(!el)return'';var is=el.querySelectorAll('img');for(var i=0;i<is.length;i++){var im=is[i],u=im.getAttribute('data-src')||im.getAttribute('data-original')||im.currentSrc||im.src||'';if(!u)continue;var p=im,cls='';for(var d=0;d<4&&p;d++,p=p.parentElement)cls+=' '+String(p.className||'');if(/avatar|head|user|author|logo|icon|qrcode|sprite|loading/i.test(cls+' '+u))continue;var w=Number(im.naturalWidth||im.width||im.getAttribute('width')||0),h=Number(im.naturalHeight||im.height||im.getAttribute('height')||0);if(w&&h&&w<=180&&h<=180)continue;return String(u);}return'';}"
        +"function avatarOf(el){if(!el)return'';var is=el.querySelectorAll('img');for(var i=0;i<is.length;i++){var im=is[i],u=im.getAttribute('data-src')||im.getAttribute('data-original')||im.currentSrc||im.src||'';if(!u)continue;var p=im,cls='';for(var d=0;d<3&&p;d++,p=p.parentElement)cls+=' '+String(p.className||'');var w=Number(im.naturalWidth||im.width||im.getAttribute('width')||0),h=Number(im.naturalHeight||im.height||im.getAttribute('height')||0);if(/avatar|head|user|author/i.test(cls+' '+u)||(w&&h&&w<=120&&h<=120))return String(u);}return'';}"
        +"var out=[],seen={};"
        +"function add(el){if(!el||out.length>=36)return;var raw=String(el.innerText||el.textContent||'');var t=n(raw);if(!t||t.length<8||t.length>1400)return;if(/登录后获得更多|新人.*免费读|下载起点读书|打开起点读书/.test(t))return;"
            +"var lines=raw.split(/\\n+/).map(n).filter(function(x){return x&&!bad(x)&&x.length<240;});if(!lines.length)return;"
            +"var user='',title='',body='';"
            +"if(lines.length>=2&&lines[0].length<=20&&!/[，。！？：]/.test(lines[0]))user=lines.shift();"
            +"if(lines.length)title=lines.shift();"
            +"if(lines.length)body=lines.slice(0,7).join('\\n');"
            +"if(!title&&user){title=user;user='';}"
            +"var meaningful=(title?title.length:0)+(body?body.length:0);if(meaningful<8)return;if(!body&&title.length<10&&!imgOf(el))return;"
            +"var h=hrefOf(el),im=imgOf(el),av=avatarOf(el);"
            +"var k=n((user+'|'+title+'|'+body).substring(0,320));if(seen[k])return;seen[k]=1;"
            +"out.push({user:user,title:title,body:body,url:h,img:im,avatar:av});"
        +"}"
        +"var sels=['article','li','[class*=thread-item]','[class*=topic-item]','[class*=post-item]','[class*=feed-item]','[class*=comment-item]','[class*=card]','[class*=post]','[class*=thread]','[class*=feed]','[class*=topic]'];"
        +"for(var s=0;s<sels.length;s++){var es=document.querySelectorAll(sels[s]);for(var i=0;i<es.length;i++)add(es[i]);if(out.length>=12)break;}"
        +"if(!out.length){var as=document.querySelectorAll('a[href]');for(var j=0;j<as.length;j++){var h=String(as[j].href||'');if(/forum|circle|comment|review|discuss|topic|thread|post/i.test(h))add(as[j].parentElement||as[j]);}}"
        +"var text=n(document.body?document.body.innerText:'');var mm=text.match(/(\\d+)\\s*讨论帖/);"
        +"var allTxt='',allUrl='';var ae=document.querySelectorAll('a,button,[role=button],div,span');for(var q=0;q<ae.length;q++){var z=n(ae[q].innerText||ae[q].textContent||'');if(/^查看全部帖子/.test(z)){allTxt=z;var aa=(ae[q].matches&&ae[q].matches('a[href]'))?ae[q]:(ae[q].closest?ae[q].closest('a[href]'):null);if(aa)allUrl=String(aa.href||aa.getAttribute('href')||'');break;}}"
        +"return JSON.stringify({url:location.href,title:document.title||'',count:mm?mm[1]:'',all:{text:allTxt,url:allUrl},items:out,body:text.slice(0,1200),cand:document.querySelectorAll('article,li,[class*=post],[class*=thread],[class*=feed],[class*=topic],[class*=card]').length});"
    +"})()";
}

function qfCircleExtract2965(j,url){
    var pack={url:String(url||""),count:"",all:{text:"",url:""},items:[],title:"",body:"",cand:0};
    if(!j||typeof j.webView!=="function"||!url)return pack;
    try{
        var raw=qfCircleCleanResult2964(j.webView(null,String(url),qfCircleExtractScript2965()));
        if(!raw)return pack;
        var x=JSON.parse(raw);
        if(x&&typeof x==="object"){
            pack.url=String(x.url||url);
            pack.count=String(x.count||"");
            pack.all=x.all||pack.all;
            pack.items=Array.isArray(x.items)?x.items:[];
            pack.title=String(x.title||"");
            pack.body=String(x.body||"");
            pack.cand=Number(x.cand||0)||0;
        }
    }catch(e){}
    return pack;
}

function qfCircleFindRealUrl2965(j,bid){
    var bookUrls=[
        "https://www.qidian.com/book/"+encodeURIComponent(String(bid))+"/",
        "https://book.qidian.com/info/"+encodeURIComponent(String(bid))+"/"
    ];
    var script="(function(){"
        +"function n(s){return String(s||'').replace(/\\s+/g,'').trim();}"
        +"var a=document.querySelectorAll('a[href],button,[role=button],[onclick]'),best='',bs=0;"
        +"for(var i=0;i<a.length;i++){var t=n(a[i].innerText||a[i].textContent||a[i].getAttribute('title')||''),h=String(a[i].href||a[i].getAttribute('href')||''),s=0;"
        +"if(/书友圈/.test(t))s+=150;if(/书友互动/.test(t))s+=100;if(/书评区|书评/.test(t))s+=80;if(/forum|circle|comment|review|discuss|topic|thread/i.test(h))s+=55;"
        +"if(s>bs&&h&&h.indexOf('javascript:')!==0){bs=s;best=h;}}return best;})()";
    for(var i=0;i<bookUrls.length;i++){
        try{
            var raw=qfCircleCleanResult2964(j.webView(null,bookUrls[i],script));
            if(/^https?:\/\//i.test(raw))return raw;
        }catch(e){}
    }
    return "";
}

function qfCircleEsc2964(v){
    return String(v==null?"":v)
        .replace(/&/g,"&amp;")
        .replace(/</g,"&lt;")
        .replace(/>/g,"&gt;")
        .replace(/"/g,"&quot;")
        .replace(/'/g,"&#39;");
}

function qfCircleBookName2964(b){
    var n="";
    try{n=String(b&&b.getVariable?b.getVariable("qf_name"):"").trim();}catch(e0){}
    try{if(!n)n=String(b&&(b.name||b.bookName||b.title)||"").trim();}catch(e1){}
    return n;
}

function qfCircleHtml2964(bookName,bid,pack,officialUrl){
    pack=pack||{};
    var rawItems=Array.isArray(pack.items)?pack.items:[];
    var items=[],seenTitle={};

    function qfCircleKey2968(s){
        s=String(s||"")
            .replace(/[\s·•，。！？、：；（）()【】《》<>\[\]_-]+/g,"")
            .replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g,"")
            .toLowerCase();
        return s;
    }

    function qfCircleRich2968(x){
        var v=0;
        try{if(x.body)v+=Math.min(260,String(x.body).length);}catch(e0){}
        try{if(x.img)v+=100;}catch(e1){}
        try{if(x.avatar)v+=25;}catch(e2){}
        try{if(x.user)v+=18;}catch(e3){}
        try{if(x.url)v+=45;}catch(e4){}
        return v;
    }

    for(var di=0;di<rawItems.length;di++){
        var it0=rawItems[di]||{};
        var dk=qfCircleKey2968(it0.title||"");
        if(!dk)dk=qfCircleKey2968(String(it0.body||"").slice(0,100));
        if(!dk)continue;

        if(seenTitle[dk]!==undefined){
            var oi=seenTitle[dk];
            var oldIt=items[oi]||{};
            if(qfCircleRich2968(it0)>qfCircleRich2968(oldIt)){
                if(!it0.body&&oldIt.body)it0.body=oldIt.body;
                if(!it0.user&&oldIt.user)it0.user=oldIt.user;
                if(!it0.avatar&&oldIt.avatar)it0.avatar=oldIt.avatar;
                if(!it0.img&&oldIt.img)it0.img=oldIt.img;
                if(!it0.url&&oldIt.url)it0.url=oldIt.url;
                items[oi]=it0;
            }else{
                if(!oldIt.body&&it0.body)oldIt.body=it0.body;
                if(!oldIt.user&&it0.user)oldIt.user=it0.user;
                if(!oldIt.avatar&&it0.avatar)oldIt.avatar=it0.avatar;
                if(!oldIt.img&&it0.img)oldIt.img=it0.img;
                if(!oldIt.url&&it0.url)oldIt.url=it0.url;
            }
            continue;
        }

        seenTitle[dk]=items.length;
        items.push(it0);
    }

    var count=String(pack.count||"");
    var all=pack.all||{};
    var html=[];
    html.push("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'>");
    html.push("<title>起点书友圈</title><style>");
    html.push(":root{color-scheme:light dark;--bg:#f4f5f7;--card:#fff;--text:#202226;--sub:#8a8e96;--line:#eceef1;--red:#ef4553;--chip:#f1f2f4}");
    html.push("*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}");
    html.push("body{padding:0 0 26px}.head{position:sticky;top:0;z-index:8;background:rgba(255,255,255,.97);border-bottom:1px solid var(--line);padding:14px 16px 11px;backdrop-filter:blur(12px)}");
    html.push(".topline{display:flex;align-items:center;gap:10px}.ttl{font-size:19px;font-weight:760;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.count{font-size:12px;color:var(--sub);margin-top:4px}");
    html.push(".official{margin-left:auto;color:#777;text-decoration:none;font-size:12px;border:1px solid #ddd;padding:6px 10px;border-radius:999px;white-space:nowrap}");
    html.push(".tabs{display:flex;gap:18px;margin-top:12px;font-size:14px}.tab{font-weight:700;color:#222;position:relative;padding-bottom:6px}.tab:after{content:'';position:absolute;left:0;right:0;bottom:0;height:3px;border-radius:99px;background:var(--red)}.future{color:#aaa}");
    html.push(".feed{padding:8px 0}.card{background:var(--card);padding:14px 16px;margin:0 0 9px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}");
    html.push(".user{display:flex;align-items:center;gap:9px;color:var(--sub);font-size:12px;margin-bottom:8px}.avatar{width:30px;height:30px;border-radius:50%;object-fit:cover;background:#eee}.avatarFallback{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#eee;color:#999}");
    html.push(".ct{font-size:16px;font-weight:720;line-height:1.45;margin-bottom:6px}.cb{font-size:14px;line-height:1.65;color:#555;white-space:pre-wrap;display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden}.pic{display:block;margin-top:10px;max-width:48%;max-height:180px;border-radius:9px;object-fit:cover}");
    html.push(".actions{margin-top:11px;display:flex;align-items:center;justify-content:space-between}.go{color:#d64651;text-decoration:none;font-size:13px;font-weight:680}.hint{color:var(--sub);font-size:11px}");
    html.push(".empty{margin:14px;background:var(--card);border-radius:14px;padding:28px 18px;text-align:center;color:var(--sub)}.empty b{display:block;color:var(--text);font-size:16px;margin-bottom:8px}.diag{margin-top:12px;font-size:11px;line-height:1.55;word-break:break-all;text-align:left;background:var(--chip);padding:10px;border-radius:9px}");
    html.push(".foot{text-align:center;color:#a2a5ab;font-size:11px;padding:14px}");
    html.push("@media(prefers-color-scheme:dark){:root{--bg:#101115;--card:#181a20;--text:#eef0f3;--sub:#9297a2;--line:#292c34;--chip:#22252d}.head{background:rgba(24,26,32,.97)}.tab{color:#eee}.official{border-color:#3b3e47;color:#bbb}.cb{color:#c0c4ca}.avatarFallback{background:#2c2f37}.empty b{color:#eee}}");
    html.push("</style></head><body>");

    html.push("<header class='head'><div class='topline'><div><div class='ttl'>💬 "+qfCircleEsc2964((bookName||("BookId "+bid))+"书友圈")+"</div>");
    html.push("<div class='count'>"+(count?qfCircleEsc2964(count)+" 讨论帖 · ":"")+"数据来自起点官方页面，本地整理</div></div>");
    html.push("<a class='official' href='"+qfCircleEsc2964(officialUrl)+"'>官方页</a></div>");
    html.push("<div class='tabs'><span class='tab'>动态</span><span class='future'>精华</span><span class='future'>同人创作</span></div></header>");

    if(items.length){
        html.push("<main class='feed'>");
        for(var i=0;i<items.length&&i<30;i++){
            var it=items[i]||{};
            html.push("<article class='card'>");
            if(it.user||it.avatar){
                html.push("<div class='user'>");
                if(it.avatar)html.push("<img class='avatar' src='"+qfCircleEsc2964(it.avatar)+"' referrerpolicy='no-referrer'>");
                else html.push("<span class='avatarFallback'>书</span>");
                html.push("<span>"+qfCircleEsc2964(it.user||"书友")+"</span></div>");
            }
            if(it.title)html.push("<div class='ct'>"+qfCircleEsc2964(it.title)+"</div>");
            if(it.body)html.push("<div class='cb'>"+qfCircleEsc2964(it.body)+"</div>");
            if(it.img&&/^https?:\/\//i.test(String(it.img)))html.push("<img class='pic' src='"+qfCircleEsc2964(it.img)+"' referrerpolicy='no-referrer'>");
            html.push("<div class='actions'>");
            if(it.url&&/^https?:\/\//i.test(String(it.url)))html.push("<a class='go' href='"+qfCircleEsc2964(it.url)+"'>查看帖子 ›</a>");
            else html.push("<span class='hint'>预览帖</span>");
            html.push("</div></article>");
        }
        html.push("</main>");
    }else{
        html.push("<div class='empty'><b>暂未提取到帖子</b><div>本版已改用旧版曾成功显示帖子卡片的宽松提取规则，并先定位真实书友圈 URL。</div>");
        html.push("<div class='diag'>最终页："+qfCircleEsc2964(String(pack.url||officialUrl))+"<br>页面标题："+qfCircleEsc2964(String(pack.title||""))+"<br>候选容器："+qfCircleEsc2964(String(pack.cand||0))+"<br>“查看全部帖子”："+qfCircleEsc2964(String((all&&all.text)||"未识别"))+"<br>链接："+qfCircleEsc2964(String((all&&all.url)||"未暴露"))+"<br><br>页面正文前1200字：<br>"+qfCircleEsc2964(String(pack.body||""))+"</div>");
        html.push("</div>");
    }
    html.push("<div class='foot'>起点书友圈 · 本地整理测试版 v2.9.68</div>");
    html.push("</body></html>");
    return html.join("");
}


function qfCircleApiJson2970(raw){
    var s=String(raw||"").trim();
    if(!s)return null;

    /*
     * 书友圈 Post/Topic/Circle/User Id 经常超过 JS 安全整数。
     * 真机 getcirclepostlist 已返回 Id / CircleId 等长整数，
     * 先字符串化再 JSON.parse，避免帖子详情链接 ID 被舍入。
     */
    function safe(t){
        return String(t||"").replace(
            /("(?:Id|ID|CircleId|circleId|PostId|postId|TopicId|topicId|UserId|userId|MemberId|memberId|AuthorId|authorId|RoleId|roleId|MasterPostId|masterPostId|PostCategoryId|postCategoryId|CategoryId|categoryId|SubCategoryId|subCategoryId|SubCategory|subCategory|JsId|jsId)"\s*:\s*)(\d{16,})/g,
            '$1"$2"'
        );
    }

    try{return JSON.parse(safe(s));}catch(e0){}
    try{
        if(s.charAt(0)==='"'&&s.charAt(s.length-1)==='"'){
            var x=JSON.parse(s);
            return JSON.parse(safe(String(x||"")));
        }
    }catch(e1){}
    return null;
}

function qfCircleApiKeys2970(o){
    try{
        if(o&&typeof o==="object")return Object.keys(o).slice(0,40).join(",");
    }catch(e){}
    return "";
}

function qfCircleApiCode2970(o){
    if(!o||typeof o!=="object")return "";
    var v="";
    try{
        if(o.Code!==undefined)v=o.Code;
        else if(o.code!==undefined)v=o.code;
        else if(o.Status!==undefined)v=o.Status;
        else if(o.status!==undefined)v=o.status;
    }catch(e){}
    return String(v===undefined||v===null?"":v);
}

function qfCircleApiMsg2970(o){
    if(!o||typeof o!=="object")return "";
    var v="";
    try{
        v=o.Message!==undefined?o.Message:
          (o.message!==undefined?o.message:
          (o.Msg!==undefined?o.Msg:
          (o.msg!==undefined?o.msg:"")));
    }catch(e){}
    return String(v===undefined||v===null?"":v);
}

function qfCircleFindIds2970(root){
    var out={circleId:"",postId:"",topicId:""};
    var seen=[];
    function clean(v){
        if(v===undefined||v===null)return "";
        var s=String(v).trim();
        return /^\d{5,}$/.test(s)?s:"";
    }
    function walk(v,d){
        if(!v||d>9)return;
        if(typeof v!=="object")return;
        if(seen.indexOf(v)>=0)return;
        seen.push(v);
        if(Array.isArray(v)){
            for(var i=0;i<v.length&&i<30;i++)walk(v[i],d+1);
            return;
        }
        var ks=Object.keys(v);
        for(var j=0;j<ks.length;j++){
            var k=ks[j],lk=String(k).toLowerCase(),x=v[k],id="";
            if(!out.circleId&&(
                lk==="circleid"||lk==="bookcircleid"||
                lk==="realcircleid"||lk==="applycircleid"
            )){
                id=clean(x);if(id)out.circleId=id;
            }
            if(!out.postId&&(lk==="postid"||lk==="masterpostid")){
                id=clean(x);if(id)out.postId=id;
            }
            if(!out.topicId&&lk==="topicid"){
                id=clean(x);if(id)out.topicId=id;
            }
            if(x&&typeof x==="object")walk(x,d+1);
        }
    }
    walk(root,0);
    return out;
}

function qfCirclePostText2970(o,keys){
    if(!o||typeof o!=="object")return "";
    for(var i=0;i<keys.length;i++){
        var k=keys[i];
        if(o[k]!==undefined&&o[k]!==null){
            var s=String(o[k]).trim();
            if(s&&s!=="[object Object]")return s;
        }
    }
    return "";
}

function qfCirclePostUser2970(o){
    if(!o||typeof o!=="object")return "";
    var s=qfCirclePostText2970(o,[
        "UserName","userName","NickName","nickName",
        "AuthorName","authorName","UserNickName","userNickName"
    ]);
    if(s)return s;
    var nests=["UserInfo","userInfo","Author","author","User","user"];
    for(var i=0;i<nests.length;i++){
        var x=o[nests[i]];
        if(x&&typeof x==="object"){
            s=qfCirclePostText2970(x,[
                "UserName","userName","NickName","nickName",
                "Name","name","AuthorName","authorName"
            ]);
            if(s)return s;
        }
    }
    return "";
}

function qfCirclePostImagesV310(o){
    var out=[],seen={},deny={},seenObj=[];
    function norm(u){
        u=String(u==null?"":u).trim().replace(/^['"]|['"]$/g,"")
            .replace(/\\u002[fF]/g,"/").replace(/\\u0026/g,"&").replace(/\\u003[dD]/g,"=")
            .replace(/\\\//g,"/").replace(/&amp;/ig,"&");
        if(/^\/\//.test(u))u="https:"+u;
        if(/^http:\/\//i.test(u))u="https://"+u.slice(7);
        return u;
    }
    function denyPath(path){
        return /(?:^|[._\[\]])(?:user|userinfo|useritem|author|profile|avatar|head|headicon|headimage|portrait|level|rank|grade|badge|medal|honou?r|identity|role|vip|titleicon|usertitle|label|tag|frame|pendant|decorate|decoration|icon|logo|qrcode|emoji|face|sprite)(?:$|[._\[\]])/i.test(String(path||""));
    }
    function badUrl(u){
        return /(?:avatar|head(?:icon|img|image)?|user(?:icon|head)?|profile|portrait|level|rank|grade|badge|medal|honou?r|identity|role|vip|title[_-]?icon|label|tag|frame|pendant|decoration|emoji|face|sprite|logo|qrcode)/i.test(String(u||""));
    }
    function isImage(u,path){
        u=norm(u);path=String(path||"");
        if(!/^https?:\/\//i.test(u))return false;
        if(/\.(?:mp4|m4v|mov|webm|m3u8|ts)(?:[?#]|$)/i.test(u))return false;
        if(denyPath(path)||badUrl(u))return false;
        return /\.(?:jpe?g|png|webp|gif|avif|bmp)(?:[?#]|$)/i.test(u)||/(?:image|img|pic|photo|picture|cover|poster|thumb|snapshot|preimage|bitmap)/i.test(path+" "+u);
    }
    function collectUrls(v,path,d,target){
        if(v==null||d>7)return;
        if(typeof v==="string"){
            var s=String(v),m;
            var re=/["'](?:ImageUrl|imageUrl|ImgUrl|imgUrl|OriginUrl|originUrl|OriginalUrl|originalUrl|PictureUrl|pictureUrl|PicUrl|picUrl|PreImage|preImage|BitmapUrl|bitmapUrl|CoverUrl|coverUrl|Poster|poster|PhotoUrl|photoUrl|Src|src)["']\s*:\s*["']([^"']+)["']/ig;
            while((m=re.exec(s))!==null)target(norm(m[1]),path+".embedded");
            var hi=/<img[^>]+(?:src|data-src)=["']([^"']+)["']/ig;
            while((m=hi.exec(s))!==null)target(norm(m[1]),path+".htmlimg");
            return;
        }
        if(typeof v!=="object")return;
        if(seenObj.indexOf(v)>=0)return;seenObj.push(v);
        if(Array.isArray(v)){for(var i=0;i<v.length&&i<80;i++)collectUrls(v[i],path+"["+i+"]",d+1,target);return;}
        var ks=Object.keys(v);
        for(var k=0;k<ks.length;k++){
            var key=String(ks[k]),x=v[key],np=path?path+"."+key:key;
            if(denyPath(np)){collectUrls(x,np,d+1,function(u){if(/^https?:\/\//i.test(u))deny[u]=1;});continue;}
            if(/(?:image|img|pic|photo|picture|attachment|media|cover|poster|thumb|snapshot|preimage|bitmap|bodyrichtext|richtext|postcontent|contenttext|body|content|summary)/i.test(key)){
                if(typeof x==="string"){
                    var u=norm(x);if(/^https?:\/\//i.test(u))target(u,np);
                    collectUrls(x,np,d+1,target);
                }else if(x&&typeof x==="object")collectUrls(x,np,d+1,target);
            }
        }
    }
    /* 正文媒体采用白名单路径；UserInfo/等级/称号等非媒体子树不会被遍历。 */
    seenObj=[];
    function add(v,path){
        var u=norm(v);if(!isImage(u,path)||deny[u]||seen[u])return;
        seen[u]=1;out.push(u);
    }
    /* 官方正文媒体字段优先。 */
    var lists=[
        o&&o.ImgList,o&&o.imgList,o&&o.ImageList,o&&o.imageList,
        o&&o.ImageObjList,o&&o.imageObjList,o&&o.NineImageList,o&&o.nineImageList,
        o&&o.Images,o&&o.images,o&&o.PicList,o&&o.picList,o&&o.PictureList,o&&o.pictureList,
        o&&o.AttachmentList,o&&o.attachmentList,o&&o.MediaList,o&&o.mediaList
    ];
    for(var li=0;li<lists.length;li++)collectUrls(lists[li],"post.mediaList"+li,0,add);
    var rich=[
        o&&o.BodyRichText,o&&o.bodyRichText,o&&o.RichText,o&&o.richText,
        o&&o.PostContent,o&&o.postContent,o&&o.ContentText,o&&o.contentText,
        o&&o.Body,o&&o.body,o&&o.Content,o&&o.content,o&&o.Summary,o&&o.summary
    ];
    for(var ri=0;ri<rich.length;ri++)collectUrls(rich[ri],"post.rich"+ri,0,add);
    var direct=["ImageUrl","imageUrl","ImgUrl","imgUrl","PreImage","preImage","BitmapUrl","bitmapUrl","PicUrl","picUrl","PictureUrl","pictureUrl"];
    for(var di=0;di<direct.length;di++)if(o&&o[direct[di]]!=null)add(o[direct[di]],"post."+direct[di]);
    /* 最后一层只遍历媒体语义字段，不再扫描整个帖子对象。 */
    seenObj=[];collectUrls(o,"post",0,add);
    try{
        var av=qfCirclePostText2970(o,["UserIcon","userIcon","UserHeadIcon","userHeadIcon","Avatar","avatar"]),nav=norm(av);
        if(nav)out=out.filter(function(u){return norm(u)!==nav;});
    }catch(_av){}
    return out.slice(0,9);
}
function qfCirclePostImage2970(o){
    var a=qfCirclePostImagesV310(o);
    return a.length?a[0]:"";
}

function qfCircleVideoInfo2975(o){
    var best={url:"",poster:"",duration:0,score:-999},seen=[];
    function norm(u){
        u=String(u==null?"":u).trim().replace(/^['"]|['"]$/g,"")
          .replace(/\\u002[fF]/g,"/").replace(/\\u0026/g,"&").replace(/\\u003[dD]/g,"=")
          .replace(/\\\//g,"/").replace(/&amp;/ig,"&");
        if(/^\/\//.test(u))u="https:"+u;
        if(/^http:\/\//i.test(u))u="https://"+u.slice(7);
        return u;
    }
    function img(u){u=norm(u);return /^https?:\/\//i.test(u)&&(/\.(?:jpe?g|png|webp|gif|avif)(?:[?#]|$)/i.test(u)||/(?:image|img|pic|cover|poster|thumb)/i.test(u));}
    function take(v,path,key){
        var u=norm(v),p=(String(path||"")+"."+String(key||"")).toLowerCase();
        if(!/^https?:\/\//i.test(u))return;
        var sc=-999;
        if(/\.(?:mp4|m4v|mov|webm|m3u8|ts)(?:[?#]|$)/i.test(u))sc=48;
        if(/(?:video|vod|play|stream|media)/i.test(p))sc=Math.max(sc,58);
        if(/(?:playurl|play_url|videourl|video_url|sourceurl|source_url|streamurl|stream_url|transcode|urlhd|hdurl)/i.test(p))sc+=30;
        if(/(?:cover|poster|thumb|image|img|pic|avatar|head|icon)/i.test(p))sc-=95;
        if(/\.(?:mp4|m4v|mov|webm)(?:[?#]|$)/i.test(u))sc+=35;
        if(/\.m3u8(?:[?#]|$)/i.test(u))sc+=28;
        if(sc>best.score){best.url=u;best.score=sc;}
        if(!best.poster&&img(u)&&/(?:cover|poster|thumb|firstframe|snapshot|image|img|pic)/i.test(p))best.poster=u;
    }
    function scanEmbedded(s,path){
        s=String(s||"");
        var re=/["'](VideoUrl|videoUrl|PlayUrl|playUrl|StreamUrl|streamUrl|VideoCover|videoCover|Poster|poster)["']\s*:\s*["']([^"']+)["']/ig,m;
        while((m=re.exec(s))!==null)take(m[2],path,m[1]);
        var ru=/(https?:\/\/[^\s"'<>]+?\.(?:mp4|m4v|mov|webm|m3u8)(?:\?[^\s"'<>]*)?)/ig;
        while((m=ru.exec(s))!==null)take(m[1],path,"embeddedVideoUrl");
    }
    function walk(v,path,d){
        if(v==null||d>11)return;
        if(typeof v==="string"){
            var s=String(v).trim();
            scanEmbedded(s,path);
            if(/^https?:\/\//i.test(norm(s))||/^\/\//.test(s))take(s,path,"");
            if((s.charAt(0)==="{"&&s.charAt(s.length-1)==="}")||(s.charAt(0)==="["&&s.charAt(s.length-1)==="]")){
                try{walk(JSON.parse(s),path+".json",d+1);}catch(_j){}
            }
            return;
        }
        if(typeof v!=="object")return;
        if(seen.indexOf(v)>=0)return;seen.push(v);
        if(Array.isArray(v)){for(var i=0;i<v.length&&i<100;i++)walk(v[i],path+"["+i+"]",d+1);return;}
        for(var k in v){if(!Object.prototype.hasOwnProperty.call(v,k))continue;var x=v[k],np=path?path+"."+k:k;
            if(typeof x==="string")take(x,path,k);
            else if(typeof x==="number"&&/(duration|videotime|video_time|playtime|play_time|length)/i.test(k)&&!best.duration){var n=Number(x);if(n>100000)n/=1000;if(n>0&&n<86400)best.duration=n;}
            if(x&&typeof x==="object")walk(x,np,d+1);
        }
    }
    walk(o,"",0);if(best.score<20)best.url="";return {url:best.url,poster:best.poster,duration:best.duration};
}

function qfCircleExtractPosts2970(root){
    var out=[],seenObj=[],seenPost={};

    function normKey(s){
        return String(s||"")
            .replace(/[\s·•，。！？、：；（）()【】《》<>\[\]_-]+/g,"")
            .replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g,"")
            .toLowerCase();
    }

    function cleanId(v){
        if(v===undefined||v===null)return "";
        var s=String(v).trim();
        return /^\d{5,}$/.test(s)?s:"";
    }

    function plain(v){
        if(v==null)return "";
        if(typeof v==="number"||typeof v==="boolean")return String(v);

        if(typeof v==="string"){
            var s=String(v).trim();
            if(!s)return "";

            if(
                (s.charAt(0)==="{"&&s.charAt(s.length-1)==="}")||
                (s.charAt(0)==="["&&s.charAt(s.length-1)==="]")
            ){
                try{
                    var jo=JSON.parse(s);
                    var jt=plain(jo);
                    if(jt)return jt;
                }catch(_json){}
            }

            s=qfStripVideoMetaV13(s);
            return qfCircleFaceTextV310(s)
                .replace(/<br\s*\/?>/ig,"\n")
                .replace(/<\/p\s*>/ig,"\n")
                .replace(/<[^>]+>/g," ")
                .replace(/&nbsp;/ig," ")
                .replace(/&amp;/ig,"&")
                .replace(/&lt;/ig,"<")
                .replace(/&gt;/ig,">")
                .replace(/[ \t\r]+/g," ")
                .replace(/\n{3,}/g,"\n\n")
                .trim();
        }

        if(Array.isArray(v)){
            var a=[];
            for(var i=0;i<v.length&&i<120;i++){
                var t=plain(v[i]);
                if(t)a.push(t);
            }
            return a.join("").replace(/\n{3,}/g,"\n\n").trim();
        }

        if(typeof v==="object"){
            var keys=[
                "Text","text","Content","content",
                "BodyRichText","bodyRichText",
                "RichText","richText",
                "Body","body",
                "PostContent","postContent",
                "ContentText","contentText",
                "Value","value",
                "Desc","desc","Summary","summary",
                "Title","title"
            ];

            /*
             * 同一对象有时同时带摘要和完整正文。
             * 不再遇到第一个字段就 return，而是取文本更完整的一项。
             */
            var best="";
            for(var k=0;k<keys.length;k++){
                if(v[keys[k]]!=null){
                    var x=plain(v[keys[k]]);
                    if(x&&x.length>best.length)best=x;
                }
            }
            return best;
        }
        return "";
    }

    function imageOf(o){
        if(!o||typeof o!=="object")return "";

        var direct=[
            "ImageUrl","imageUrl","ImgUrl","imgUrl",
            "Cover","cover","PreImage","preImage",
            "BitmapUrl","bitmapUrl","PicUrl","picUrl",
            "Picture","picture"
        ];

        for(var i=0;i<direct.length;i++){
            var u=o[direct[i]];
            if(typeof u==="string"&&/^\/\//.test(u))u="https:"+u;
            if(typeof u==="string"&&/^https?:\/\//i.test(u))return u;
        }

        /*
         * 真机 TopicDataList 使用 ImgList；
         * APK UGCBaseItem 同时还有 imageList / imageObjList。
         */
        var lists=[
            o.ImgList,o.imgList,
            o.imageList,o.ImageList,
            o.imageObjList,o.ImageObjList,
            o.nineImageList,o.NineImageList,
            o.Images,o.images,
            o.PicList,o.picList
        ];

        for(var j=0;j<lists.length;j++){
            var a=lists[j];
            if(!Array.isArray(a))continue;

            for(var q=0;q<a.length;q++){
                var it=a[q],u2="";

                if(typeof it==="string")u2=it;
                else if(it&&typeof it==="object"){
                    u2=String(
                        it.Url||it.url||
                        it.ImageUrl||it.imageUrl||
                        it.ImgUrl||it.imgUrl||
                        it.OriginUrl||it.originUrl||
                        it.OriginalUrl||it.originalUrl||
                        it.Src||it.src||""
                    );
                }

                if(/^\/\//.test(u2))u2="https:"+u2;
                if(/^https?:\/\//i.test(u2))return u2;
            }
        }
        return "";
    }

    function userOf(o){
        if(!o||typeof o!=="object")return "";

        var u=
            o.UserInfo||o.userInfo||
            o.User||o.user||
            o.userItem||o.UserItem||{};

        return String(
            o.UserName||o.userName||
            o.NickName||o.nickName||
            o.Nickname||o.nickname||
            o.AuthorName||o.authorName||
            u.UserName||u.userName||
            u.NickName||u.nickName||
            u.Nickname||u.nickname||""
        ).trim();
    }

    function avatarOf(o){
        if(!o||typeof o!=="object")return "";

        var u=
            o.UserInfo||o.userInfo||
            o.User||o.user||
            o.userItem||o.UserItem||{};

        var s=String(
            o.UserIcon||o.userIcon||
            o.UserHeadIcon||o.userHeadIcon||
            o.Avatar||o.avatar||
            u.UserIcon||u.userIcon||
            u.UserHeadIcon||u.userHeadIcon||
            u.Avatar||u.avatar||""
        );

        if(/^\/\//.test(s))s="https:"+s;
        return /^https?:\/\//i.test(s)?s:"";
    }

    function timeOf(o){
        var v=
            o.PostDate!=null?o.PostDate:
            o.postDate!=null?o.postDate:
            o.PublishedTime!=null?o.PublishedTime:
            o.publishedTime!=null?o.publishedTime:
            o.EditedTime!=null?o.EditedTime:
            o.editedTime!=null?o.editedTime:"";

        if(v===undefined||v===null||v==="")return "";

        var n=Number(v);
        if(isFinite(n)&&n>1000000000){
            if(n<100000000000)n*=1000;
            try{
                var d=new Date(n);
                function z(x){return x<10?"0"+x:String(x);}
                return d.getFullYear()+"-"+z(d.getMonth()+1)+"-"+z(d.getDate())+
                    " "+z(d.getHours())+":"+z(d.getMinutes());
            }catch(_d){}
        }
        return String(v);
    }

    function add(o,force){
        if(!o||typeof o!=="object")return;

        /*
         * 真机 TopicDataList 的帖子主键就是 Id，
         * 不一定另外提供 PostId。
         */
        var postId=cleanId(
            o.PostId||o.postId||
            o.MasterPostId||o.masterPostId||
            (force?(o.Id||o.id):"")||""
        );

        var topicId=cleanId(
            o.TopicId||o.topicId||
            o.ContentId||o.contentId||""
        );

        var circleId=cleanId(
            o.CircleId||o.circleId||
            o.BookCircleId||o.bookCircleId||""
        );

        var title=plain(
            o.Title!=null?o.Title:
            o.title!=null?o.title:
            o.PostTitle!=null?o.PostTitle:
            o.postTitle!=null?o.postTitle:
            o.TopicTitle!=null?o.TopicTitle:
            o.topicTitle!=null?o.topicTitle:
            o.Subject!=null?o.Subject:
            o.subject!=null?o.subject:
            o.PostName!=null?o.PostName:
            o.postName!=null?o.postName:
            o.TopicName!=null?o.TopicName:
            o.topicName!=null?o.topicName:
            o.ContentTitle!=null?o.ContentTitle:
            o.contentTitle!=null?o.contentTitle:
            o.TitleDetail!=null?o.TitleDetail:
            o.TitleDetailBigBook!=null?o.TitleDetailBigBook:
            o.TitleDetailBigbook!=null?o.TitleDetailBigbook:
            ""
        );

        var body=plain(
            o.BodyRichText!=null?o.BodyRichText:
            o.bodyRichText!=null?o.bodyRichText:
            o.RichText!=null?o.RichText:
            o.richText!=null?o.richText:
            o.PostContent!=null?o.PostContent:
            o.postContent!=null?o.postContent:
            o.ContentText!=null?o.ContentText:
            o.contentText!=null?o.contentText:
            o.Body!=null?o.Body:
            o.body!=null?o.body:
            o.Content!=null?o.Content:
            o.content!=null?o.content:
            o.Summary!=null?o.Summary:
            o.summary!=null?o.summary:
            ""
        );

        if(!body&&o.text!=null)body=plain(o.text);

        var h5=String(
            o.H5Url||o.h5Url||
            o.H5URL||o.h5URL||
            o.Url||o.url||""
        );
        if(/^\/\//.test(h5))h5="https:"+h5;

        var postish=!!(
            force||postId||topicId||circleId||h5||
            o.PostType!=null||o.postType!=null||
            o.Type!=null||o.type!=null||
            o.PostCategoryId!=null||o.postCategoryId!=null||
            o.QDBookId!=null||o.qdBookId!=null||
            o.BookId!=null||o.bookId!=null
        );

        if(!postish)return;
        if(!title&&!body&&!postId&&!topicId&&!h5)return;

        if(!postId)postId=cleanId(o.Id||o.id||"");

        var key=
            postId||topicId||
            normKey(title||body.slice(0,140));

        if(!key||seenPost[key])return;
        seenPost[key]=1;

        var mediaImages=[];
        try{mediaImages=qfCirclePostImagesV310(o)||[];}catch(_images){mediaImages=[];}
        var vinfo={url:"",poster:"",duration:0};
        try{vinfo=qfCircleVideoInfo2975(o)||vinfo;}catch(_video){}

        out.push({
            circleId:circleId,
            postId:postId,
            topicId:topicId,
            user:userOf(o),
            avatar:avatarOf(o),
            title:title,
            body:body,
            image:mediaImages.length?String(mediaImages[0]):"",
            images:mediaImages,
            video:String(vinfo.url||""),
            videoPoster:String(vinfo.poster||(mediaImages.length?mediaImages[0]:"")||""),
            videoDuration:Number(vinfo.duration||0)||0,
            url:/^https?:\/\//i.test(h5)?h5:"",
            reply:String(
                o.CommentCount!=null?o.CommentCount:
                o.commentCount!=null?o.commentCount:
                o.ReviewCount!=null?o.ReviewCount:
                o.reviewCount!=null?o.reviewCount:
                o.PostCount!=null?o.PostCount:
                o.postCount!=null?o.postCount:""
            ),
            like:String(
                o.LikeCount!=null?o.LikeCount:
                o.likeCount!=null?o.likeCount:
                o.AgreeAmount!=null?o.AgreeAmount:
                o.agreeAmount!=null?o.agreeAmount:
                o.StarCount!=null?o.StarCount:
                o.starCount!=null?o.starCount:""
            ),
            time:timeOf(o),
            postCategoryId:String(
                o.PostCategoryId!=null?o.PostCategoryId:
                o.postCategoryId!=null?o.postCategoryId:""
            ),
            categoryId:String(
                o.CategoryId!=null?o.CategoryId:
                o.categoryId!=null?o.categoryId:
                o.PostCategoryId!=null?o.PostCategoryId:
                o.postCategoryId!=null?o.postCategoryId:""
            ),
            subCategoryId:String(
                o.SubCategoryId!=null?o.SubCategoryId:
                o.subCategoryId!=null?o.subCategoryId:
                o.SubCategory!=null?o.SubCategory:
                o.subCategory!=null?o.subCategory:""
            ),
            postType:String(
                o.PostType!=null?o.PostType:
                o.postType!=null?o.postType:
                o.Type!=null?o.Type:
                o.type!=null?o.type:""
            )
        });
    }

    /*
     * 先专门抓官方列表字段。
     * 这是 v2.9.71 真机诊断真正返回数据的位置。
     */
    function direct(v,d){
        if(!v||d>10||typeof v!=="object")return;

        if(Array.isArray(v)){
            for(var i=0;i<v.length&&i<120;i++)direct(v[i],d+1);
            return;
        }

        var names=[
            "TopicDataList","topicDataList",
            "PostList","postList",
            "TopPostList","topPostList",
            "TopPost","topPost",
            "TopPostV2","topPostV2",
            "FansWorkList","fansWorkList"
        ];

        for(var n=0;n<names.length;n++){
            var a=v[names[n]];
            if(Array.isArray(a)){
                for(var j=0;j<a.length&&j<120;j++){
                    if(a[j]&&typeof a[j]==="object")add(a[j],true);
                }
            }
        }

        var ks=Object.keys(v);
        for(var k=0;k<ks.length;k++){
            var x=v[ks[k]];
            if(x&&typeof x==="object")direct(x,d+1);
        }
    }

    direct(root,0);

    /*
     * 再做通用递归兜底，以兼容 getcircledetail / getpostdetail。
     */
    function walk(v,d){
        if(!v||d>10||out.length>=100)return;
        if(typeof v!=="object")return;
        if(seenObj.indexOf(v)>=0)return;
        seenObj.push(v);

        if(Array.isArray(v)){
            for(var i=0;i<v.length&&i<120;i++){
                var it=v[i];
                if(it&&typeof it==="object")add(it,false);
                walk(it,d+1);
            }
            return;
        }

        add(v,false);

        var ks=Object.keys(v);
        for(var j=0;j<ks.length;j++){
            var x=v[ks[j]];
            if(x&&typeof x==="object")walk(x,d+1);
        }
    }

    walk(root,0);
    return out;
}

function qfCircleApiSummary2970(raw){
    var o=qfCircleApiJson2970(raw);
    var s={
        len:String(raw||"").length,
        code:"",
        msg:"",
        topKeys:"",
        dataKeys:"",
        ids:{circleId:"",postId:"",topicId:""},
        posts:[],
        total:0
    };

    if(!o)return s;

    s.code=qfCircleApiCode2970(o);
    s.msg=qfCircleApiMsg2970(o);
    s.topKeys=qfCircleApiKeys2970(o);

    function findTotal(v,d){
        if(!v||d>8||typeof v!=="object")return 0;

        var keys=[
            "TotalCount","totalCount",
            "PostTotalCount","postTotalCount",
            "Count","count"
        ];

        for(var i=0;i<keys.length;i++){
            var n=Number(v[keys[i]]);
            if(isFinite(n)&&n>=0)return n;
        }

        if(Array.isArray(v))return 0;

        var ks=Object.keys(v);
        for(var j=0;j<ks.length;j++){
            var x=v[ks[j]];
            if(x&&typeof x==="object"){
                var z=findTotal(x,d+1);
                if(z>0)return z;
            }
        }
        return 0;
    }

    try{
        var d=
            o.Data!==undefined?o.Data:
            o.data!==undefined?o.data:
            o.Result!==undefined&&typeof o.Result==="object"?o.Result:
            o.result!==undefined&&typeof o.result==="object"?o.result:
            null;

        if(d&&typeof d==="object"){
            if(d.Data&&typeof d.Data==="object")d=d.Data;
            else if(d.data&&typeof d.data==="object")d=d.data;
        }

        s.dataKeys=qfCircleApiKeys2970(d);
    }catch(e){}

    s.ids=qfCircleFindIds2970(o);
    s.posts=qfCircleExtractPosts2970(o);
    s.total=findTotal(o,0);

    if(!s.total&&s.posts.length)s.total=s.posts.length;
    return s;
}


function qfCircleCategoryMeta2984(raw){
    var root=qfCircleApiJson2970(raw);

    /*
     * v2.9.88：动态分类完全按当前书籍 getcircledetail 返回的官方分类表生成。
     * 常规分类的真实请求参数优先使用 PostCategoryId/CategoryId/Id；
     * JsId 只保留为长 ID 兼容值，不再把 JsId 默认塞进 subCategory，
     * 避免“书评/周边/分享全部落到讨论”的问题。
     */
    var commonLabels=["讨论","书评","周边","分享","版务消息"];
    var essenceLabels=[];
    var fanLabels=["全部","同人文","同人图","同人视频","其他同人","精华"];
    var nativeShort={"讨论":"2","书评":"3","周边":"4","分享":"5","版务消息":"6","同人创作":"316"};
    var allowedDynamic={"作家说":1,"作者说":1,"版权信息":1,"讨论":1,"书评":1,"周边":1,"分享":1,"版务消息":1,"同人创作":1,"其他":1};
    var essenceShort={"讨论":"2","书评":"3","周边":"4","分享":"5","版务消息":"6"};

    var out={
        filters:[],
        filterSets:{dongtai:[],jinghua:[],tongren:[]},
        dongtai:{postCategoryId:"0"},
        jinghua:{postCategoryId:"2",domain:"essence"},
        tongren:{postCategoryId:"316",treePostCategoryId:"",subCategoryId:""},
        debugTree:""
    };

    function sid(v){
        if(v===undefined||v===null)return "";
        var s=String(v).trim();
        return /^-?\d{1,22}$/.test(s)?s:"";
    }
    function nameOf(o){
        o=o||{};
        var a=[o.Name,o.name,o.PostCategoryName,o.postCategoryName,o.SubCategoryName,o.subCategoryName,o.CategoryName,o.categoryName,o.Title,o.title,o.Label,o.label];
        for(var i=0;i<a.length;i++)if(a[i]!==undefined&&a[i]!==null&&String(a[i]).trim()!=="")return String(a[i]).trim();
        return "";
    }
    function requestIdOf(o){
        o=o||{};
        var a=[o.PostCategoryId,o.postCategoryId,o.CategoryId,o.categoryId,o.Id,o.id];
        for(var i=0;i<a.length;i++){var s=sid(a[i]);if(s)return s;}
        return "";
    }
    function jsIdOf(o){
        o=o||{};
        return sid(o.JsId!==undefined?o.JsId:o.jsId);
    }
    function legacyIdOf(o){
        var r=requestIdOf(o),j=jsIdOf(o);
        return r||j;
    }
    function listOf(v){
        if(Array.isArray(v))return v;
        if(!v||typeof v!=="object")return [];
        var d=v.Data||v.data||v.Result||v.result||v;
        var pc=d.PostCategoryListV2||d.postCategoryListV2||d.PostCategoryList||d.postCategoryList;
        if(Array.isArray(pc))return pc;
        function find(x,dep){
            if(!x||dep>6||typeof x!=="object")return [];
            if(Array.isArray(x)){
                var hit=0;
                for(var i=0;i<x.length&&i<24;i++)if(x[i]&&typeof x[i]==="object"&&nameOf(x[i]))hit++;
                if(hit)return x;
                for(var j=0;j<x.length&&j<36;j++){var z=find(x[j],dep+1);if(z.length)return z;}
                return [];
            }
            var ks=Object.keys(x);
            for(var k=0;k<ks.length;k++){var y=find(x[ks[k]],dep+1);if(y.length)return y;}
            return [];
        }
        return find(pc||d,0);
    }

    var rows=listOf(root);
    if(rows.length){try{out.debugTree=JSON.stringify(rows).slice(0,5000);}catch(_dbg){}}

    var mainMap={},fanMap={},dynamicLabels=["全部"],seenDynamic={"全部":1};
    for(var c=0;c<commonLabels.length;c++)mainMap[commonLabels[c]]=null;
    for(var f=0;f<fanLabels.length;f++)fanMap[fanLabels[f]]=null;
    fanMap["全部"]={id:"0"};

    for(var i=0;i<rows.length;i++){
        var o=rows[i]||{},nm=nameOf(o),req=requestIdOf(o),jsid=jsIdOf(o),id=legacyIdOf(o);
        if(!nm)continue;

        /* 动态二级栏严格跟随这本书官方返回：作家说/版权信息有就显示，没有就不显示。 */
        if(allowedDynamic[nm]){
            var fallback=String(nativeShort[nm]||"");
            var rid=req||fallback||jsid;
            if(rid){
                mainMap[nm]={id:rid,altId:(jsid&&jsid!==rid)?jsid:"",requestId:req||fallback,jsId:jsid};
                if(!seenDynamic[nm]){seenDynamic[nm]=1;dynamicLabels.push(nm);}
            }
        }

        if(nm==="同人创作"){
            /* v2.9.96：同人子类优先使用 JsId。子项 PostCategoryId 经常继承父级 316，
             * 旧版因此把同人文/同人图/同人视频/其他同人都请求成“全部”。 */
            var parentReq=req||"316",parentJs=jsid||"";
            if(parentJs&&parentJs!=="0"&&parentJs!=="-1"&&parentJs!=="316")out.tongren.treePostCategoryId=parentJs;
            else if(id&&id!=="0"&&id!=="-1"&&id!=="316")out.tongren.treePostCategoryId=id;
            out.tongren.requestPostCategoryId=parentReq;
            out.tongren.jsId=parentJs;
            var subs=o.SubCategoryList||o.subCategoryList||o.ChildCategoryList||o.childCategoryList||o.Children||o.children||[];
            if(!Array.isArray(subs))subs=[];
            for(var s=0;s<subs.length;s++){
                var so=subs[s]||{},sn=nameOf(so),sr=requestIdOf(so),sj=jsIdOf(so),si=sj||sr;
                if(!sn||!fanMap.hasOwnProperty(sn))continue;
                var cleanReq=(sr&&sr!=="316"&&sr!==parentReq)?sr:"";
                if(si)fanMap[sn]={id:String(si),jsId:String(sj||""),requestId:String(cleanReq||""),altId:String(cleanReq||""),parentId:String(parentJs||id||"")};
            }
        }
    }

    /* 分类表没解析出来时才使用固定常规分类兜底；有官方分类表时不伪造书籍不存在的特殊分类。 */
    if(dynamicLabels.length===1){
        for(var fb=0;fb<commonLabels.length;fb++){
            var fn=commonLabels[fb],fid=String(nativeShort[fn]||"");
            if(fid){mainMap[fn]={id:fid,altId:"",requestId:fid,jsId:""};dynamicLabels.push(fn);}
        }
    }

    /*
     * v2.9.94：精华是独立数据域，不再使用 isJinghua/isGodReview 这种会被接口忽略的伪筛选。
     * APK/旧 Argus 语义里精华顶层为 postCategoryId=2；二级分类继续使用本书
     * PostCategoryListV2 的 JsId/请求 ID 作为 subCategory。这样与同人创作
     * postCategoryId=316 + subCategory 的结构一致，也不会把动态讨论误当精华。
     * 精华二级分类跟随当前书籍官方分类表：作家说/版权信息/其他等有则显示。
     */
    essenceLabels=["全部"];
    for(var el=1;el<dynamicLabels.length;el++){
        var enm=String(dynamicLabels[el]||"");
        if(enm&&enm!=="同人创作"&&essenceLabels.indexOf(enm)<0)essenceLabels.push(enm);
    }

    function dynamicCandidates(n,x){
        if(n==="全部")return [{id:"0",mode:"all",source:"official-top"}];
        if(!x||!x.id)return [];
        var rid=String(x.requestId||x.id||""),jid=String(x.jsId||x.altId||"");
        var a=[],seen={};
        function add(id,mode,source,alt){
            id=String(id||"");if(!id)return;
            var k=id+"|"+mode;if(seen[k])return;seen[k]=1;
            a.push({id:id,altId:String(alt||""),mode:mode,source:source});
        }
        /*
         * v2.9.92：讨论继续固定使用已真机验证正确的长 JsId + subCategory 链路。
         * 本版只优化首次加载：外层先预热，WebView 再走单路径阶梯重试；其它动态分类保持冻结。
         */
        if(n==="讨论"){
            var did=jid||rid||"2";
            /* beta5.4：长 JsId 仍优先；部分书籍 getcircledetail 只返回短分类 ID，
             * 此时显式补 postCategoryId=2，不能再让长 ID 缺失把“讨论”直接变空。 */
            add(did,"sub","verified-discussion-JsId-subCategory",rid&&rid!==did?rid:"2");
            add("2","post","official-discussion-PostCategoryId=2",did!=="2"?did:"");
            add("2","sub","compat-discussion-subCategory=2",did!=="2"?did:"");
            if(did!=="2")add(did,"subId","compat-discussion-JsId-subCategoryId",rid&&rid!==did?rid:"2");
            if(rid&&rid!=="2"&&rid!==did)add(rid,"post","compat-discussion-requestId-postCategoryId",did);
        }else{
            add(rid,"post","official-PostCategoryId",jid);
            add(rid,"category","compat-CategoryId",jid);
            add(jid||rid,"sub","compat-JsId-subCategory",rid!==jid?rid:"");
        }
        return a.slice(0,5);
    }

    function essenceCandidates(n,x){
        if(n==="全部")return [{id:"0",altId:"",parentId:"2",mode:"essence-all",source:"official-essence-postCategoryId=2"}];
        if(!x)return [];
        var rid=String(x.requestId||x.id||essenceShort[n]||""),jid=String(x.jsId||x.altId||"");
        var preferred=jid||rid,shortId=String(essenceShort[n]||rid||""),a=[],seen={};
        function add(id,mode,source,alt){
            id=String(id||"");if(!id)return;
            var k=id+"|"+mode;if(seen[k])return;seen[k]=1;
            a.push({id:id,altId:String(alt||""),parentId:"2",mode:mode,source:source});
        }
        /* beta5.4：起点当前不同书籍存在两套精华子分类语义。
         * 先按“具体动态分类 + 精华标记”请求（讨论=2/书评=3/周边=4/分享=5…），
         * 再回退旧版“精华域 postCategoryId=2 + JsId/subCategory”链。 */
        if(shortId){
            add(shortId,"essence-post-god","official-essence+PostCategoryId+isGodReview",preferred);
            add(shortId,"essence-post-jh","verified-essence+PostCategoryId+isJinghua",preferred);
        }
        add(preferred,"essence-sub","official-essence+JsId-subCategory",rid&&rid!==preferred?rid:"");
        add(preferred,"essence-subId","compat-essence+JsId-subCategoryId",rid&&rid!==preferred?rid:"");
        if(rid&&rid!==preferred)add(rid,"essence-sub","compat-essence+requestId-subCategory",preferred);
        return a.slice(0,5);
    }

    function fanCandidates(n,x){
        var parent=String(out.tongren.treePostCategoryId||"");
        if(n==="全部")return [{id:"316",parentId:parent,mode:"fan-all",source:"official-316"}];
        var a=[],seen={};
        function add(id,mode,source,alt){id=String(id||"");if(!id)return;var k=id+"|"+mode;if(seen[k])return;seen[k]=1;a.push({id:id,altId:String(alt||""),parentId:parent,mode:mode,source:source});}
        var jid=String(x&&x.jsId||x&&x.id||""),rid=String(x&&x.requestId||x&&x.altId||"");

        /* v2.9.99：同人“精华”必须先尝试服务端精华标记。
         * v2.9.98 把这两个候选追加在 5~8 个 JsId 兼容候选之后，随后又 slice(0,8)，
         * 部分书籍实际上根本没有把 fan-god / fan-jinghua 带进 WebView，最终只命中 1 条本地帖子。 */
        if(n==="精华"){
            add("1","fan-god","official-isGodReview","");
            add("1","fan-jinghua","compat-isJinghua","");
        }

        if(jid&&jid!=="316"){
            add(jid,"fan-post","official-JsId-postCategoryId",rid);
            add(jid,"fan-sub","compat-316+JsId-subCategory",rid);
            add(jid,"fan-subId","compat-316+JsId-subCategoryId",rid);
            add(jid,"fan-category","compat-316+JsId-categoryId",rid);
            if(parent)add(jid,"fan-parent-sub","compat-treeParent+JsId",rid);
        }
        if(rid&&rid!=="316"){
            add(rid,"fan-sub","compat-316+requestId-subCategory",jid);
            add(rid,"fan-category","compat-316+requestId-categoryId",jid);
            add(rid,"fan-post","compat-child-postCategoryId",jid);
        }
        return a.slice(0,8);
    }

    var dm=[],jm=[],fm=[];
    for(var a=0;a<dynamicLabels.length;a++){
        var dn=dynamicLabels[a],dx=mainMap[dn],dc=dynamicCandidates(dn,dx);
        dm.push({name:dn,tabs:"dongtai",id:dx&&dx.id?String(dx.id):"",mode:dc.length?dc[0].mode:"",resolved:dc.length>0,candidates:dc});
    }
    for(var e=0;e<essenceLabels.length;e++){
        var en=essenceLabels[e],ex=mainMap[en],ec=essenceCandidates(en,ex);
        jm.push({name:en,tabs:"jinghua",id:ec.length?String(ec[0].id):"",mode:ec.length?ec[0].mode:"",resolved:ec.length>0,candidates:ec});
    }
    for(var b=0;b<fanLabels.length;b++){
        var fn2=fanLabels[b],fx=fanMap[fn2],fc=fanCandidates(fn2,fx);
        fm.push({name:fn2,tabs:"tongren",id:fx&&fx.id?String(fx.id):"",mode:fc.length?fc[0].mode:"",resolved:fc.length>0,candidates:fc});
    }

    out.filterSets.dongtai=dm;
    out.filterSets.jinghua=jm;
    out.filterSets.tongren=fm;
    out.filters=[];
    for(var d=0;d<dm.length;d++)out.filters.push(dm[d]);
    for(var j=0;j<jm.length;j++)out.filters.push(jm[j]);
    for(var t=0;t<fm.length;t++)out.filters.push(fm[t]);
    return out;
}

function qfCircleApiCall2970(j,path,params){
    var raw="";
    try{raw=qfArgusOuterRequest2931({java:j},path,params)||"";}catch(e){}
    return {
        path:path,
        params:params,
        raw:String(raw||""),
        sum:qfCircleApiSummary2970(raw)
    };
}

function qfCircleApiHtml2970(bookName,bid,tests,circleId,posts,tabs,totals,categoryMode,categoryMeta){
    var E=qfCircleEsc2964;

    tabs=tabs||{};
    totals=totals||{};
    categoryMode=categoryMode||{};
    categoryMeta=categoryMeta||{filters:[{id:"0",name:"全部"}]};

    var filters=Array.isArray(categoryMeta.filters)?categoryMeta.filters:[{id:"0",name:"全部"}];
    if(!filters.length)filters=[{id:"0",name:"全部"}];

    var groups=[
        {key:"dongtai",name:"动态",rows:tabs.dongtai||posts||[],total:Number(totals.dongtai||0)},
        {key:"jinghua",name:"精华",rows:tabs.jinghua||[],total:Number(totals.jinghua||0)},
        {key:"tongren",name:"同人创作",rows:tabs.tongren||[],total:Number(totals.tongren||0)}
    ];

    var h=[];
    h.push("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'>");
    h.push("<title>起点书友圈</title><style>");

    h.push(":root{--bg:#f5f7fb;--card:#fff;--text:#202633;--sub:#8b94a5;--line:#e9edf3;--accent:#ff5a6b;--accent2:#7b7ff6;--soft:#f1f4f8;--blue:#5b7fa8;--shadow:0 8px 24px rgba(35,45,70,.07)}");
    h.push("*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}html,body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}body{padding:0 0 28px;background:linear-gradient(180deg,#f1f4fb 0,#f7f8fb 170px,var(--bg) 320px)}button,select{font:inherit}.head{position:sticky;top:0;z-index:8;padding:10px 12px 0;background:rgba(245,247,251,.92);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px)}.hero{display:flex;align-items:center;gap:12px;padding:15px 16px;border-radius:19px;background:linear-gradient(135deg,#282f43 0%,#424a67 58%,#5a617d 100%);box-shadow:0 10px 26px rgba(34,42,64,.18);color:#fff;transition:.2s ease}.heroIcon{width:42px;height:42px;border-radius:14px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.12);font-size:22px;flex:none;transition:.2s ease}.heroText{min-width:0;flex:1}.ttl{font-size:19px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px;transition:.2s ease}.sub{font-size:11px;color:rgba(255,255,255,.68);margin-top:5px;transition:.18s ease}.head.compact{padding-top:5px}.head.compact .hero{padding:8px 12px;border-radius:15px;box-shadow:0 5px 16px rgba(34,42,64,.13)}.head.compact .heroIcon{width:31px;height:31px;border-radius:10px;font-size:17px}.head.compact .ttl{font-size:15px}.head.compact .sub{display:none}.head.compact .tabs{margin-top:5px}.head.compact .tab{height:34px}.tabs{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:9px;padding:4px;border-radius:15px;background:rgba(255,255,255,.88);box-shadow:0 4px 16px rgba(40,50,75,.06)}.tab{height:38px;border:0;border-radius:12px;background:transparent;color:#8a93a3;font-size:14px;font-weight:600}.tab.active{color:#272d3a;background:#fff;box-shadow:0 3px 12px rgba(47,56,82,.09);font-weight:800}");
    h.push(".filters{display:none;margin:9px -12px 0;padding:8px 13px 10px;background:rgba(255,255,255,.94);border-bottom:1px solid var(--line);align-items:center;gap:8px;overflow-x:auto;white-space:nowrap;scrollbar-width:none}.filters::-webkit-scrollbar{display:none}.filters.show{display:flex}.chip{height:32px;border:0;border-radius:11px;background:var(--soft);color:#7f8795;padding:0 13px;font-size:12.5px;flex:none}.chip.active{background:#fff0f2;color:#e64d5c;font-weight:800;box-shadow:inset 0 0 0 1px rgba(255,90,107,.09)}.sortSel{margin-left:auto;height:32px;border:0;border-radius:10px;background:#f4f6f9;color:#666f7e;padding:0 8px;font-size:12px;min-width:78px;outline:none;flex:none}");
    h.push(".pane{display:none;padding-top:2px}.pane.active{display:block}.feedList{padding:0 12px}.post{margin:9px 0;background:var(--card);padding:14px 15px 13px;border-radius:18px;box-shadow:var(--shadow);border:1px solid rgba(226,231,239,.72)}.user{display:flex;align-items:center;gap:9px;margin-bottom:10px}.avatar{width:36px;height:36px;border-radius:50%;object-fit:cover;background:#eef1f5}.avatarFb{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#eef1f7,#e1e6ef);color:#768096;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800}.u{font-size:13px;color:#657083;font-weight:650}.t{font-size:17px;font-weight:800;line-height:1.45;color:#222936}.b{font-size:14px;color:#566071;line-height:1.68;margin-top:6px;white-space:pre-wrap;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:6;overflow:hidden}.img{display:block;width:100%;max-height:270px;border-radius:13px;margin-top:11px;object-fit:cover;background:#eef1f5}.postFoot{display:flex;align-items:center;gap:8px;margin-top:11px;padding-top:10px;border-top:1px solid #f0f2f6}.meta{font-size:11px;color:#9aa2af;min-width:0;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.go{display:inline-flex;align-items:center;gap:3px;color:#df5360;font-size:11.5px;font-weight:750;cursor:pointer;flex:none}.kindTag{margin-left:auto;padding:3px 7px;border-radius:999px;background:#fff0f2;color:#e85b69;font-size:10px;font-weight:750;line-height:1.2}.feedLoading,.filterBusy{margin:13px 0;background:rgba(255,255,255,.86);border:1px solid var(--line);border-radius:16px;padding:26px 16px;text-align:center;color:#929aa8;font-size:12px}.empty{margin:14px 0;background:var(--card);border-radius:18px;padding:34px 18px;text-align:center;color:#98a0ad;box-shadow:var(--shadow)}.spinMini{width:22px;height:22px;border:3px solid #e9ecf2;border-top-color:var(--accent);border-radius:50%;margin:0 auto 9px;animation:qfspin .75s linear infinite}");
    h.push(".imgGrid{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;margin-top:11px;border-radius:13px;overflow:hidden}.imgGrid.one{grid-template-columns:1fr}.imgGrid.two{grid-template-columns:repeat(2,1fr)}.imgGrid img{display:block;width:100%;aspect-ratio:1/1;object-fit:cover;background:#eef1f5}.imgGrid.one img{aspect-ratio:auto;max-height:360px;object-fit:contain}.feedAuto{margin:6px 12px 18px;padding:12px;text-align:center;color:#9aa2af;font-size:11.5px}.feedAuto.loading{color:#70798a}.feedAuto.done{opacity:.66}");
    h.push("#detail{display:none;position:fixed;inset:0;z-index:30;background:var(--bg);overflow:auto}.dHead{position:sticky;top:0;z-index:31;background:var(--card);height:54px;display:flex;align-items:center;border-bottom:1px solid var(--line);padding:0 14px}.back{font-size:28px;line-height:1;border:0;background:none;color:var(--text);padding:6px 12px 6px 0}.dTitle{font-size:17px;font-weight:760}.loading{padding:50px 20px;text-align:center;color:var(--sub)}.spin{width:26px;height:26px;border:3px solid #e6e7ea;border-top-color:var(--red);border-radius:50%;margin:0 auto 12px;animation:qfspin .75s linear infinite}@keyframes qfspin{to{transform:rotate(360deg)}}.topic{background:var(--card);padding:16px}.topicUser{display:flex;gap:10px;align-items:center}.topicName{font-size:14px;font-weight:650}.topicTime{font-size:11px;color:var(--sub);margin-top:3px}.topicTitle{font-size:20px;font-weight:800;line-height:1.45;margin-top:14px}.topicBody{font-size:16px;line-height:1.75;margin-top:10px;white-space:pre-wrap}.topicImg{display:block;max-width:88%;max-height:520px;object-fit:contain;border-radius:10px;margin-top:12px;background:#f2f3f5}.topicVideo,.postVideo{display:block;width:100%;max-height:66vh;border-radius:12px;background:#000;object-fit:contain}.postVideo{max-height:48vh}.qfVideoWrap{position:relative;margin-top:12px;border-radius:13px;overflow:hidden;background:#111;min-height:118px}.qfVideoWrap .topicVideo,.qfVideoWrap .postVideo{margin:0}.qfVideoPoster{display:block;width:100%;max-height:66vh;object-fit:cover;background:#111}.postVideoPoster{max-height:48vh}.qfVideoPlayBtn{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:58px;height:58px;border-radius:50%;border:0;background:rgba(17,17,20,.72);color:#fff;font-size:28px;padding-left:5px;box-shadow:0 5px 20px rgba(0,0,0,.28)}.qfVideoStatus{position:absolute;left:50%;bottom:12px;transform:translateX(-50%);max-width:88%;padding:5px 10px;border-radius:999px;background:rgba(0,0,0,.58);color:#fff;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.qfVideoOpen{display:none;width:100%;border:0;padding:10px 12px;background:#202226;color:#fff;font-size:13px}.qfVideoWrap.qfVideoFailed .qfVideoOpen{display:block}.qfVideoWrap.qfVideoLoading .qfVideoPlayBtn{animation:qfspin .8s linear infinite}.qfVideoWrap.qfVideoPlaying .qfVideoPlayBtn,.qfVideoWrap.qfVideoPlaying .qfVideoStatus{display:none}.qfVideoWrap.qfVideoNeedTap .qfVideoStatus{display:block;cursor:pointer;z-index:4}.qfVideoLazy{position:relative;display:inline-block;max-width:100%;cursor:pointer}.qfVideoLazy .img{max-width:100%;margin-top:12px}.qfPlay{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:52px;height:52px;border-radius:50%;background:rgba(20,20,20,.66);color:#fff;display:flex;align-items:center;justify-content:center;font-size:25px;padding-left:3px;box-shadow:0 4px 18px rgba(0,0,0,.2)}.qfPlayText{position:absolute;left:50%;bottom:12px;transform:translateX(-50%);background:rgba(0,0,0,.58);color:#fff;border-radius:999px;padding:5px 10px;font-size:11px;white-space:nowrap}.loadingVideo .qfPlay{animation:qfspin .8s linear infinite}.qfFace{display:inline-block;width:1.35em;height:1.35em;vertical-align:-.28em;object-fit:contain;margin:0 .06em}.topicMeta{font-size:12px;color:var(--sub);margin-top:14px}.reviewTitle{padding:18px 16px 10px;font-size:18px;font-weight:800}.review{background:var(--card);padding:14px 16px;border-bottom:1px solid var(--line)}.reviewTop{display:flex;align-items:center;gap:9px}.reviewName{font-size:13px;font-weight:650}.reviewBody{font-size:15px;line-height:1.65;margin:8px 0 0 41px;white-space:pre-wrap}.reviewMeta{font-size:11px;color:var(--sub);margin:7px 0 0 41px}.subReplies{margin:9px 0 0 41px;background:var(--bg);border-radius:9px;padding:8px 10px}.subReply{font-size:13px;line-height:1.55;padding:3px 0;color:#555}.subName{color:var(--blue);font-weight:650}.replyMore{display:inline-block;margin:5px 0 0 41px;color:var(--blue);font-size:12px;cursor:pointer}.moreBtn{display:block;width:calc(100% - 32px);margin:14px 16px 28px;border:0;border-radius:999px;background:var(--card);color:var(--text);padding:12px;font-size:14px}.err{margin:20px;background:#fff2f3;color:#c7434e;padding:14px;border-radius:12px;font-size:12px;line-height:1.5;word-break:break-all}");

    /* beta5.6：更接近原生社区的紧凑视觉，减少首屏占屏和重阴影。 */
    h.push("body{background:#f6f7f9}.head{padding:7px 10px 0;background:rgba(246,247,249,.96)}.hero{padding:10px 12px;border-radius:15px;gap:10px;box-shadow:0 4px 14px rgba(35,45,70,.12)}.heroIcon{width:34px;height:34px;border-radius:11px;font-size:18px}.ttl{font-size:17px;font-weight:760}.sub{font-size:10.5px;margin-top:2px}.tabs{margin-top:6px;padding:3px;border-radius:13px;box-shadow:none;border:1px solid rgba(230,233,239,.9)}.tab{height:36px;border-radius:10px;font-size:13.5px}.filters{margin:7px -10px 0;padding:7px 11px 8px;gap:7px}.chip{height:30px;border-radius:10px;padding:0 12px;font-size:12px}.sortSel{height:30px;border-radius:9px;font-size:11.5px}.feedList{padding:0 10px}.post{margin:7px 0;padding:13px 14px 11px;border-radius:16px;box-shadow:0 2px 10px rgba(39,48,69,.045);border:1px solid #eceff4}.user{gap:8px;margin-bottom:8px}.avatar,.avatarFb{width:34px;height:34px}.u{font-size:13px;color:#505a6c;font-weight:680}.t{font-size:16.5px;font-weight:720;line-height:1.44}.b{font-size:14px;line-height:1.62;margin-top:5px;color:#5a6372;-webkit-line-clamp:5}.kindTag{padding:2px 7px;background:#fff1f3;color:#e55362}.imgGrid{gap:3px;margin-top:9px;border-radius:12px}.imgGrid.one img{max-height:330px}.postFoot{margin-top:9px;padding-top:8px}.meta{font-size:10.8px}.go{font-size:11.5px;color:#e44f5e}.feedAuto{margin-bottom:12px}.dHead{height:50px;background:rgba(255,255,255,.96);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}.dTitle{font-size:16px}.topic{margin:8px 10px 0;padding:14px;border-radius:16px}.topicTitle{font-size:19px;margin-top:12px}.topicBody{font-size:15.5px;line-height:1.72}.reviewTitle{padding:16px 15px 8px;font-size:17px}.review{padding:13px 15px}.reviewBody{font-size:14.5px;line-height:1.62}.subReplies{background:#f6f7f9;border-radius:10px}.qfSkeleton{position:relative;overflow:hidden;text-align:left;padding:18px 16px}.qfSkeleton:after{content:'';position:absolute;inset:0;transform:translateX(-100%);background:linear-gradient(90deg,transparent,rgba(255,255,255,.58),transparent);animation:qfsh 1.15s infinite}.skHead{width:34px;height:34px;border-radius:50%;background:#e9edf2;margin-bottom:13px}.skLine{height:12px;border-radius:7px;background:#e9edf2;margin:9px 0}.skLine.w1{width:82%}.skLine.w2{width:96%}.skLine.w3{width:58%}.skNote{font-size:10.5px;color:#a3aab5;margin-top:14px}@keyframes qfsh{100%{transform:translateX(100%)}}");
    h.push("@media(prefers-color-scheme:dark){:root{--bg:#111318;--card:#1a1d24;--text:#edf0f5;--sub:#969ead;--line:#2a2e38;--soft:#232730;--shadow:none}body{background:linear-gradient(180deg,#151821 0,#111318 320px)}.head{background:rgba(17,19,24,.92)}.tabs,.filters{background:rgba(26,29,36,.94)}.tab.active{background:#242832;color:#fff}.chip{background:#242832;color:#a9b0bc}.chip.active{background:#38252a;color:#ff7885}.sortSel{background:#242832;color:#b1b7c1}.post{border-color:#272c36}.b{color:#c4cad4}.avatarFb{background:#272c35}.postFoot{border-top-color:#272c35}.topicImg{background:#242832}.subReply{color:#c6cbd3}.topic{background:#1a1d24}.subReplies{background:#15181f}.skHead,.skLine{background:#272c35}.qfSkeleton:after{background:linear-gradient(90deg,transparent,rgba(255,255,255,.035),transparent)}}");
    h.push("</style></head><body>");

    h.push("<header class='head'><div class='hero'><div class='heroIcon'>💬</div><div class='heroText'><div class='ttl'>"+E(bookName||"起点书友圈")+"</div><div class='sub'>书友圈 · 起点官方数据直连</div></div></div><div class='tabs'>");
    for(var gi=0;gi<groups.length;gi++){
        var gc=groups[gi];
        h.push("<button class='tab"+(gi===0?" active":"")+"' data-tab='"+gc.key+"'>"+gc.name+"</button>");
    }
    h.push("</div>");

    /* v2.9.93：二级分类栏放进同一个 sticky header，纵向滚动时与动态/精华/同人创作一起常驻。 */
    h.push("<div class='filters show' id='filterBar'>");
    for(var fi=0;fi<filters.length;fi++){
        var f=filters[fi]||{};
        var ftabs=String(f.tabs||"dongtai,jinghua");
        var fshow=ftabs.indexOf("dongtai")>=0;
        var fcands=Array.isArray(f.candidates)?f.candidates.slice(0):[];
        h.push("<button class='chip"+(fshow&&fi===0?" active":"")+"' "+(fshow?"":"style='display:none' ")+"data-tabs='"+E(ftabs)+"' data-sub='"+E(String(f.id||""))+"' data-mode='"+E(String(f.mode||""))+"' data-name='"+E(String(f.name||"全部"))+"' data-candidates='"+E(JSON.stringify(fcands))+"' data-resolved='"+(fcands.length?"1":"0")+"'>"+E(String(f.name||"全部"))+"</button>");
    }
    h.push("<select class='sortSel' id='sortSel'><option value='6'>最近评论</option><option value='7'>最近发布</option></select></div></header>");

    function renderPane(gr,g){
        var rows=gr.rows||[];
        h.push("<main class='pane"+(g===0?" active":"")+"' id='pane_"+gr.key+"'><div class='feedList'>");
        if(rows.length){
            for(var i=0;i<rows.length&&i<40;i++){
                var p=rows[i]||{},ms=[];
                h.push("<article class='post'>");
                if(p.user||p.avatar){
                    var fb=(p.user||"书友").slice(0,1);
                    h.push("<div class='user'>"+(p.avatar&&/^https?:\/\//i.test(p.avatar)?"<img class='avatar' src='"+E(p.avatar)+"' referrerpolicy='no-referrer' loading='lazy' decoding='async' fetchpriority='low'>":"<span class='avatarFb'>"+E(fb)+"</span>")+"<span class='u'>"+E(p.user||"书友")+"</span></div>");
                }
                if(p.title)h.push("<div class='t'>"+E(p.title)+"</div>");
                if(p.body&&p.body!==p.title)h.push("<div class='b'>"+E(p.body)+"</div>");
                if(p.video&&/^https?:\/\//i.test(p.video)){
                    var vp=String(p.videoPoster||p.image||"");
                    h.push("<video class='postVideo' controls playsinline webkit-playsinline preload='none' "+(vp&&/^https?:\/\//i.test(vp)?"poster='"+E(vp)+"' ":"")+"src='"+E(p.video)+"'></video>");
                }else{
                    var pis=Array.isArray(p.images)?p.images.slice(0,9):[];
                    if(!pis.length&&p.image&&/^https?:\/\//i.test(p.image))pis=[p.image];
                    if(pis.length){
                        var pc=pis.length===1?" one":(pis.length===2?" two":""),ph=["<div class='imgGrid"+pc+"'>"];
                        for(var px=0;px<pis.length;px++)if(/^https?:\/\//i.test(String(pis[px]||"")))ph.push("<img src='"+E(pis[px])+"' referrerpolicy='no-referrer' loading='lazy' decoding='async' fetchpriority='low'>");
                        ph.push("</div>");h.push(ph.join(""));
                    }
                }
                if(p.time)ms.push(p.time);
                if(p.reply!=="")ms.push("💬 "+p.reply);
                if(p.like!=="")ms.push("♡ "+p.like);
                h.push("<div class='postFoot'>"+(ms.length?"<div class='meta'>"+E(ms.join("　"))+"</div>":"<div class='meta'></div>"));
                if((p.circleId||circleId)&&p.postId)h.push("<span class='go qfPostOpen' data-cid='"+E(String(p.circleId||circleId))+"' data-pid='"+E(String(p.postId))+"' data-img='"+E(String(p.image||""))+"'>查看详情 ›</span>");
                h.push("</div></article>");
            }
        }else{
            h.push("<div class='feedLoading'><div class='spinMini'></div>首次进入时按需加载</div>");
        }
        h.push("</div></main>");
    }
    for(var g=0;g<groups.length;g++)renderPane(groups[g],g);

    h.push("<section id='detail'><div class='dHead'><button class='back' id='dBack'>‹</button><div class='dTitle'>帖子详情</div></div><div id='detailBody'><div class='loading'><div class='spin'></div>正在加载帖子详情…</div></div></section>");

    h.push("<script>(function(){");
    h.push("var BOOK_ID="+JSON.stringify(String(bid))+",CIRCLE_ID="+JSON.stringify(String(circleId||""))+";");
    h.push("var SIGN_KEY='{1dYgqE)h9,R)hKqEcv4]k[h',SIGN_IV='01234567',INFO_KEY='0821CAAD409B84020821CAAD',INFO_IV='\\u0000\\u0000\\u0000\\u0000\\u0000\\u0000\\u0000\\u0000';");

    h.push("function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\\"/g,'&quot;').replace(/'/g,'&#39;');}");
    h.push("var QF_FACE={1:'👏',2:'🌹',3:'🤝',4:'😁',5:'😄',6:'🥺',7:'🙂',8:'😏',9:'😙',10:'👆🏻🐽',11:'🙄',12:'😭',13:'😵',14:'😥',15:'🖕🏻',16:'🥵',17:'😓',18:'🤫',19:'😂',20:'😢',21:'😍',22:'🤕🔨',23:'😑',24:'😫',25:'🤗',26:'🤪',27:'🙏',28:'😣',29:'💪',30:'💀',31:'😳',32:'😎',33:'🤭',34:'😄👏',35:'👍🏻',36:'🤓',37:'😡',38:'🙁',39:'😄❓',40:'😞',41:'😧',42:'💋',43:'☺️',44:'🤬',45:'😴',46:'🤠🚬',47:'😱',48:'🐷',49:'😪',50:'🤐',51:'🥴',52:'🌙',53:'❤️',54:'🔪',55:'🎁',56:'💔',57:'👊🏻',58:'😒',59:'✌🏻️',60:'😮',61:'🤨',62:'😴',63:'👏🏻',64:'🐲',65:'⭐',66:'🌧️',67:'🍉',68:'🍵',69:'🔥',70:'💯'};function faceText(s){s=String(s==null?'':s).replace(/&\\[fn=\\$1\\]b\\[fn=\\$1\\]p;/ig,' ').replace(/\\[fn=\\$1\\]/g,'').replace(/&#91;/ig,'[').replace(/&#93;/ig,']');return s.replace(/\\[(?:fn|em|face|emoji)[ ]*[=:][ ]*([0-9]{1,3})\\]/ig,function(_,n){return QF_FACE[Number(n)]||'';});}");
    h.push("function md5(s){if(!window.java||typeof window.java.md5Encode!=='function')throw new Error('缺少 md5Encode');return String(window.java.md5Encode(String(s))||'');}");
    h.push("function des(s,k,iv){if(!window.java||typeof window.java.tripleDESEncodeBase64Str!=='function')throw new Error('缺少 tripleDES');return String(window.java.tripleDESEncodeBase64Str(String(s),String(k),'CBC','PKCS5Padding',String(iv))||'').replace(/[\\r\\n]/g,'');}");
    h.push("function signed(path,p){var ks=Object.keys(p).sort(),a=[];for(var i=0;i<ks.length;i++){var k=ks[i];a.push(k+'='+String(p[k]==null?'':p[k]));}var q=a.join('&'),t=Date.now();var sign=des('Rv1rPTnczce|'+t+'||||||'+md5(q.toLowerCase()),SIGN_KEY,SIGN_IV);var seed=md5('qf-qidian-'+BOOK_ID).replace(/[^0-9a-f]/ig,'').toLowerCase();var did=(seed+'0123456789abcdef').slice(0,16);var info=des(did+'||||||1||999|'+t,INFO_KEY,INFO_IV);return {url:'https://druidv6.if.qidian.com/argus/api/'+path+'?'+q,headers:{QDSign:sign,QDInfo:info,tstamp:String(t)}};}");
    h.push("function ajax(req){if(!window.java||typeof window.java.ajax!=='function')throw new Error('当前阅读 WebView 不支持 java.ajax');var opt={method:'GET',timeout:12000,headers:{'User-Agent':'Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36','Accept':'application/json,text/plain,*/*','Referer':'https://h5.if.qidian.com/','Origin':'https://h5.if.qidian.com'}};for(var k in req.headers)opt.headers[k]=req.headers[k];return String(window.java.ajax(req.url+','+JSON.stringify(opt))||'');}");
    h.push("function parse(raw){var s=String(raw||'').replace(/(\\\"(?:Id|ID|CircleId|circleId|PostId|postId|TopicId|topicId|UserId|userId|RootId|rootId|ReviewId|reviewId|PostCategoryId|postCategoryId|CategoryId|categoryId|SubCategoryId|subCategoryId|SubCategory|subCategory|JsId|jsId)\\\"\\s*:\\s*)(\\d{16,})/g,'$1\\\"$2\\\"');return JSON.parse(s);}");
    h.push("function dataOf(o){return o&&(o.Data||o.data||o.Result||o.result)||o||{};}");
    h.push("function qfNormUrl(s){s=String(s||'').trim().replace(/^['\\\"]|['\\\"]$/g,'').replace(/\\\\u002[fF]/g,'/').replace(/\\\\u0026/g,'&').replace(/\\\\u003[dD]/g,'=').replace(/\\\\\\//g,'/').replace(/&amp;/ig,'&').replace(/&quot;/ig,'\\\"');try{if(/^https?%3A%2F%2F/i.test(s))s=decodeURIComponent(s);}catch(_du){}if(/^\\/\\//.test(s))s='https:'+s;if(/^http:\\/\\/[^/]*\\.file\\.myqcloud\\.com/i.test(s))s='https://'+s.slice(7);return s;}");

    h.push("function qfMetaOnly(o){if(!o||typeof o!=='object'||Array.isArray(o))return false;var ks=Object.keys(o),hasText=false,meta=true;for(var i=0;i<ks.length;i++){var k=String(ks[i]).toLowerCase();if(/text|content|body|title|summary|desc|value/.test(k))hasText=true;if(!/roleid|height|width|size|url|imageurl|imgurl|type|format|md5|key|id/.test(k))meta=false;}return !hasText&&meta;}");
    h.push("function qfStripMetaJson(s){\ns=String(s||'');\nvar keys=['\"VideoCover\"',\"'VideoCover'\",'VideoCover:','\"VideoUrl\"',\"'VideoUrl'\",'VideoUrl:','\"VideoId\"',\"'VideoId'\",'VideoId:'];\nvar vp=-1;\nfor(var i=0;i<keys.length;i++){var x=s.indexOf(keys[i]);if(x>=0&&(vp<0||x<vp))vp=x;}\nif(vp>=0){var st=vp,b1=s.lastIndexOf('{',vp),b2=s.lastIndexOf('(',vp),b3=s.lastIndexOf('[',vp);if(b1>=0&&vp-b1<6)st=b1;else if(b2>=0&&vp-b2<6)st=b2;else if(b3>=0&&vp-b3<6)st=b3;s=s.slice(0,st).trim();}\ns=s.replace(/\\{\\s*\"roleId\"\\s*:\\s*\\d+\\s*\\}/ig,'');\ns=s.replace(/\\{[^{}]{0,1800}\"(?:Url|url|ImageUrl|imageUrl|ImgUrl|imgUrl)\"\\s*:\\s*\"[^\"]+\"[^{}]{0,1800}\\}/g,'');\nreturn s;\n}");
    h.push("function txt(o){if(o==null)return '';if(typeof o==='number'||typeof o==='boolean')return String(o);if(typeof o==='string'){var s=String(o).trim();if(!s)return '';var f=s.charAt(0),l=s.charAt(s.length-1);if((f==='['&&l===']')||(f==='{'&&l==='}')){try{var jo=JSON.parse(s);if(qfMetaOnly(jo))return '';var jt=txt(jo);if(jt)return jt;}catch(_j){}}s=qfStripMetaJson(s);return faceText(s).replace(/<br\\s*\\/?>/ig,'\\n').replace(/<\\/p\\s*>/ig,'\\n').replace(/<[^>]+>/g,' ').replace(/&nbsp;/ig,' ').replace(/&amp;/ig,'&').replace(/&lt;/ig,'<').replace(/&gt;/ig,'>').replace(/[ \\t\\r]+/g,' ').replace(/\\n{3,}/g,'\\n\\n').trim();}if(Array.isArray(o)){var a=[];for(var i=0;i<o.length&&i<200;i++){var x=txt(o[i]);if(x)a.push(x);}return a.join('').replace(/\\n{3,}/g,'\\n\\n').trim();}if(typeof o==='object'){if(qfMetaOnly(o))return '';var ks=['Text','text','Content','content','BodyRichText','bodyRichText','RichText','richText','Body','body','PostContent','postContent','ContentText','contentText','Value','value','Desc','desc','Summary','summary','Title','title'];var best='';for(var k=0;k<ks.length;k++){if(o[ks[k]]!=null){var v=txt(o[ks[k]]);if(v&&v.length>best.length)best=v;}}return best;}return '';}");
    h.push("function titleOf(o){o=o||{};var ks=['Title','title','PostTitle','postTitle','TopicTitle','topicTitle','Subject','subject','PostName','postName','TopicName','topicName','ContentTitle','contentTitle','TitleDetail','titleDetail','TitleDetailBigBook','TitleDetailBigbook'];var best='';for(var i=0;i<ks.length;i++){if(o[ks[i]]!=null){var v=txt(o[ks[i]]);if(v&&v.length>best.length)best=v;}}return best;}");
    h.push("function richOf(o){o=o||{};var ks=['BodyRichText','bodyRichText','RichText','richText','PostContent','postContent','ContentText','contentText','Body','body','Content','content','Summary','summary'];var best='',raw=null;for(var i=0;i<ks.length;i++){if(o[ks[i]]!=null){var v=txt(o[ks[i]]);if(v&&v.length>best.length){best=v;raw=o[ks[i]];}}}return {text:best,raw:raw};}");

    h.push("function avatar(o){o=o||{};var u=o.user_info||o.UserInfo||o.userInfo||o.User||o.user||{};var s=qfNormUrl(o.user_avatar||o.UserIcon||o.userIcon||o.UserHeadIcon||o.userHeadIcon||o.Avatar||o.avatar||u.user_avatar||u.UserIcon||u.userIcon||u.UserHeadIcon||u.userHeadIcon||u.Avatar||u.avatar||'');return /^https?:\\/\\//i.test(s)?s:'';}");
    h.push("function user(o){o=o||{};var u=o.user_info||o.UserInfo||o.userInfo||o.User||o.user||{};return String(o.user_name||o.UserName||o.userName||o.NickName||o.nickName||o.Nickname||o.nickname||u.user_name||u.UserName||u.userName||u.NickName||u.nickName||u.nickname||'').trim();}");

    h.push("function imageUrls(o,rich){var out=[],seen={};function add(s){s=qfNormUrl(s);if(/^https?:\\/\\//i.test(s)&&!seen[s]){seen[s]=1;out.push(s);}}function scanString(s){s=String(s||'');var re=/\\\"(?:Url|url|ImageUrl|imageUrl|ImgUrl|imgUrl|OriginUrl|originUrl|OriginalUrl|originalUrl|Src|src|PreImage|preImage)\\\"\\s*:\\s*\\\"([^\\\"]+)\\\"/g,m;while((m=re.exec(s))!==null&&out.length<20)add(m[1]);}function walk(x,d){if(x==null||d>10||out.length>=20)return;if(typeof x==='string'){scanString(x);var s=String(x).trim();if(/^https?:\\/\\//i.test(qfNormUrl(s)))add(s);if((s.charAt(0)==='['&&s.charAt(s.length-1)===']')||(s.charAt(0)==='{'&&s.charAt(s.length-1)==='}')){try{walk(JSON.parse(s),d+1);}catch(_j){}}return;}if(Array.isArray(x)){for(var i=0;i<x.length;i++)walk(x[i],d+1);return;}if(typeof x==='object'){var ks=['Url','url','ImageUrl','imageUrl','ImgUrl','imgUrl','OriginUrl','originUrl','OriginalUrl','originalUrl','Src','src','PreImage','preImage'];for(var k=0;k<ks.length;k++)if(x[ks[k]]!=null)add(x[ks[k]]);var ls=['ImgList','imgList','ImageList','imageList','imageObjList','ImageObjList','Images','images','ImageDetail','imageDetail','Pictures','pictures'];for(var q=0;q<ls.length;q++)if(x[ls[q]]!=null)walk(x[ls[q]],d+1);}}walk(o,0);walk(rich,0);return out;}");

    h.push("function videoInfo(o,rich){\nvar best={url:'',urls:[],poster:'',duration:0,score:-999},seen=[],pool={};\nfunction isImg(u){u=qfNormUrl(u);return /^https?:\\/\\//i.test(u)&&(/\\.(?:jpe?g|png|webp|gif|avif)(?:[?#]|$)/i.test(u)||/(?:image|img|pic|cover|poster|thumb)/i.test(u));}\nfunction take(v,path,key){var u=qfNormUrl(v),p=(String(path||'')+'.'+String(key||'')).toLowerCase();if(!/^https?:\\/\\//i.test(u))return;var sc=-999;if(/\\.(?:mp4|m4v|mov|webm|m3u8|ts)(?:[?#]|$)/i.test(u))sc=48;if(/(?:video|vod|play|stream|media)/i.test(p))sc=Math.max(sc,58);if(/(?:playurl|play_url|videoplayurl|video_play_url|videourl|video_url|sourceurl|source_url|fileurl|file_url|downloadurl|download_url|hlsurl|hls_url|m3u8url|m3u8_url|mp4url|mp4_url|streamurl|stream_url|src|transcode|urlhd|hdurl|originalurl|originurl)/i.test(p))sc+=30;if(/(?:cover|poster|thumb|image|img|pic|avatar|head|icon)/i.test(p))sc-=95;if(/\\.(?:mp4|m4v|mov|webm)(?:[?#]|$)/i.test(u))sc+=35;if(/\\.m3u8(?:[?#]|$)/i.test(u))sc+=28;if(sc>=20&&(pool[u]===undefined||sc>pool[u]))pool[u]=sc;if(sc>best.score){best.url=u;best.score=sc;}if(!best.poster&&isImg(u)&&/(?:cover|poster|thumb|firstframe|snapshot|image|img|pic)/i.test(p))best.poster=u;}\nfunction scanString(s,path){s=String(s||'');var re=/[\"'](VideoUrl|videoUrl|VideoURL|videoURL|VideoPlayUrl|videoPlayUrl|PlayUrl|playUrl|PlayURL|playURL|StreamUrl|streamUrl|SourceUrl|sourceUrl|FileUrl|fileUrl|DownloadUrl|downloadUrl|HlsUrl|hlsUrl|M3u8Url|m3u8Url|Mp4Url|mp4Url|OriginalUrl|originalUrl|OriginUrl|originUrl|Src|src|VideoCover|videoCover|Poster|poster)[\"']\\s*:\\s*[\"']([^\"']+)[\"']/ig,m;while((m=re.exec(s))!==null)take(m[2],path,m[1]);var ru=/(https?:\\/\\/[^\\s\"'<>]+?\\.(?:mp4|m4v|mov|webm|m3u8)(?:\\?[^\\s\"'<>]*)?)/ig;while((m=ru.exec(s))!==null)take(m[1],path,'embeddedVideoUrl');}\nfunction walk(v,path,d){if(v==null||d>12)return;if(typeof v==='string'){var s=String(v).trim();scanString(s,path);if(/^https?:\\/\\//i.test(qfNormUrl(s))||/^\\/\\//.test(s))take(s,path,'');if((s.charAt(0)==='{'&&s.charAt(s.length-1)==='}')||(s.charAt(0)==='['&&s.charAt(s.length-1)===']')){try{walk(JSON.parse(s),path+'.json',d+1);}catch(_j){}}return;}if(typeof v!=='object')return;if(seen.indexOf(v)>=0)return;seen.push(v);if(Array.isArray(v)){for(var i=0;i<v.length&&i<140;i++)walk(v[i],path+'['+i+']',d+1);return;}var ks=Object.keys(v);for(var i=0;i<ks.length;i++){var k=ks[i],x=v[k],np=path?path+'.'+k:k;if(typeof x==='string')take(x,path,k);else if(typeof x==='number'&&/(duration|videotime|video_time|playtime|play_time|length)/i.test(k)&&!best.duration){var n=Number(x);if(n>100000)n/=1000;if(n>0&&n<86400)best.duration=n;}if(x&&typeof x==='object')walk(x,np,d+1);}}\nwalk(o,'',0);walk(rich,'rich',0);if(best.score<20)best.url='';var us=Object.keys(pool);us.sort(function(a,b){return Number(pool[b]||0)-Number(pool[a]||0);});if(best.url&&us.indexOf(best.url)<0)us.unshift(best.url);best.urls=us.slice(0,8);return best;\n}");
    h.push("function time(o){var v=o&&(o.PostDate!=null?o.PostDate:(o.publishedTime!=null?o.publishedTime:(o.CreateTime!=null?o.CreateTime:o.createTime)));if(v==null||v==='')return '';var n=Number(v);if(isFinite(n)&&n>1000000000){if(n<100000000000)n*=1000;var d=new Date(n),z=function(x){return x<10?'0'+x:x;};return d.getFullYear()+'-'+z(d.getMonth()+1)+'-'+z(d.getDate())+' '+z(d.getHours())+':'+z(d.getMinutes());}return String(v);}");
    h.push("function imgTag(u,cls,style){u=qfNormUrl(u);if(!/^https?:\\/\\//i.test(u))return '';var fb=u+(u.indexOf('?')>=0?'&':'?')+'imageMogr2/thumbnail/1080x';return '<img class=\\\"'+cls+'\\\" '+(style?'style=\\\"'+style+'\\\" ':'')+'src=\\\"'+esc(u)+'\\\" data-fb=\\\"'+esc(fb)+'\\\" referrerpolicy=\\\"no-referrer\\\" loading=\\\"lazy\\\" onerror=\\\"if(this.dataset.fb&&this.src!==this.dataset.fb){this.src=this.dataset.fb;this.dataset.fb=\\x27\\x27;}else{this.style.display=\\x27none\\x27;}\\\">';}");

    h.push("function imageGridTag(ims){ims=Array.isArray(ims)?ims:[];var a=[],seen={};for(var i=0;i<ims.length&&a.length<9;i++){var u=qfNormUrl(ims[i]);if(/^https?:\\/\\//i.test(u)&&!seen[u]){seen[u]=1;a.push(u);}}if(!a.length)return '';var cls=a.length===1?' one':(a.length===2?' two':'');var r='<div class=\\\"imgGrid'+cls+'\\\">';for(var j=0;j<a.length;j++)r+=imgTag(a[j],'','');return r+'</div>';}");
    h.push("function openMediaUrl(u){u=qfNormUrl(u);if(!/^https?:\\/\\//i.test(u))return;try{if(window.java&&typeof window.java.startBrowser==='function'){window.java.startBrowser(u,'视频播放');return;}}catch(_0){}try{if(window.java&&typeof window.java.openUrl==='function'){window.java.openUrl(u);return;}}catch(_1){}try{location.href=u;}catch(_2){}}\nfunction videoTag(v,cls,cid,pid){v=v||{};var u=qfNormUrl(v.url||''),po=qfNormUrl(v.poster||''),cc=String(cid||CIRCLE_ID||''),pp=String(pid||'');if(!/^https?:\\/\\//i.test(u)&&!pp)return '';var pc=(String(cls||'topicVideo').indexOf('postVideo')>=0?' postVideoPoster':'');var poster=po?'<img class=\"qfVideoPoster'+pc+'\" src=\"'+esc(po)+'\" referrerpolicy=\"no-referrer\" loading=\"lazy\">':'<div class=\"qfVideoPoster'+pc+'\" style=\"min-height:180px;background:#141414\"></div>';return '<div class=\"qfVideoWrap qfVideoDeferred\" data-url=\"'+esc(u)+'\" data-cid=\"'+esc(cc)+'\" data-pid=\"'+esc(pp)+'\" data-poster=\"'+esc(po)+'\" data-vclass=\"'+esc(cls||'topicVideo')+'\">'+poster+'<button class=\"qfVideoPlayBtn\" type=\"button\">▶</button><span class=\"qfVideoStatus\">点击播放</span><button class=\"qfVideoOpen\" type=\"button\">用系统播放器打开</button></div>';}\n");
    h.push("function topicHtml(o,root){o=o||{};var av=avatar(o),nm=user(o)||'书友',title=titleOf(o),rr=richOf(o),rich=rr.raw,body=rr.text,ims=imageUrls(o,rich),vd=videoInfo(root||o,rich),tm=time(o);if(state.previewImgs&&state.previewImgs.length){for(var pi=0;pi<state.previewImgs.length;pi++){var pu=qfNormUrl(state.previewImgs[pi]);if(pu&&ims.indexOf(pu)<0)ims.unshift(pu);}}var like=o.StarCount!=null?o.StarCount:(o.LikeCount!=null?o.LikeCount:(o.likeCount!=null?o.likeCount:''));var r='<article class=\\\"topic\\\"><div class=\\\"topicUser\\\">'+(av?imgTag(av,'avatar',''):'<span class=\\\"avatarFb\\\">书</span>')+'<div><div class=\\\"topicName\\\">'+esc(nm)+'</div><div class=\\\"topicTime\\\">'+esc(tm)+'</div></div></div>';if(title)r+='<div class=\\\"topicTitle\\\">'+esc(title)+'</div>';if(body&&body!==title)r+='<div class=\\\"topicBody\\\">'+esc(body)+'</div>';for(var ii=0;ii<ims.length;ii++)r+=imgTag(ims[ii],'topicImg','');if(vd&&vd.url)r+=videoTag(vd,'topicVideo',state.cid,state.pid);if(like!==''||tm)r+='<div class=\\\"topicMeta\\\">'+(like!==''?'赞 '+esc(like):'')+'</div>';return r+'</article>';}");
    h.push("function qfReplyRows(o){o=o||{};var cands=[o.reply_list,o.replyList,o.ReplyList,o.replies,o.Replies,o.review_list,o.ReviewList,o.reviewList,o.reply_data_list,o.ReplyDataList,o.replyDataList,o.SubReviewList,o.subReviewList,o.FirstReplyList,o.firstReplyList,o.FirstReplyComment,o.firstReplyComment];for(var i=0;i<cands.length;i++){var c=cands[i];if(Array.isArray(c)&&c.length)return c;if(c&&typeof c==='object')return [c];}return [];}");
    h.push("function qfReviewId(o){o=o||{};return String(o.comment_id||o.review_id||o.ReviewId||o.reviewId||o.RootReviewId||o.rootReviewId||o.root_review_id||o.Id||o.id||o.CommentId||o.commentId||o.PostId||o.postId||'');}");
    h.push("function qfReplyCount(o){o=o||{};var vals=[o.reply_count,o.root_review_reply_count,o.rootReviewReplyCount,o.RootReviewReplyCount,o.ReplyAmount,o.replyAmount,o.ReplyCount,o.replyCount,o.RepliesCount,o.repliesCount,o.CommentCount,o.commentCount,o.ReviewCount,o.reviewCount];for(var i=0;i<vals.length;i++){if(vals[i]!==undefined&&vals[i]!==null&&String(vals[i])!==''){var n=Number(vals[i]);if(isFinite(n)&&n>=0)return n;}}return 0;}");
    h.push("function subReplyHtml(o){o=o||{};var nm=user(o)||'书友',body=txt(o.Body!=null?o.Body:(o.body!=null?o.body:(o.Content!=null?o.Content:(o.content!=null?o.content:(o.BodyRichText!=null?o.BodyRichText:o.bodyRichText)))));if(!body)body=txt(o.Title!=null?o.Title:o.title);var qn=String(o.ReplyUserName||o.replyUserName||o.QuoteUserName||o.quoteUserName||o.RelatedUser||o.relatedUser||'');return '<div class=\\\"subReply\\\"><span class=\\\"subName\\\">'+esc(nm)+'</span>'+(qn?' 回复 <span class=\\\"subName\\\">'+esc(qn)+'</span>':'')+'：'+esc(body)+'</div>';}");
    h.push("function reviewHtml(o){o=o||{};var av=avatar(o),nm=user(o)||'书友';var rich=o.BodyRichText!=null?o.BodyRichText:(o.bodyRichText!=null?o.bodyRichText:(o.text!=null?o.text:(o.content!=null?o.content:(o.Body!=null?o.Body:(o.body!=null?o.body:(o.Content!=null?o.Content:o.content))))));var body=txt(rich),ims=imageUrls(o,rich),vd=videoInfo(o,rich),tm=time(o);var rp=qfReplyCount(o);var lk=o.digg_count!=null?o.digg_count:(o.StarCount!=null?o.StarCount:(o.LikeCount!=null?o.LikeCount:(o.likeCount!=null?o.likeCount:(o.AgreeAmount!=null?o.AgreeAmount:o.agreeAmount))));if(!body)body=txt(o.Title!=null?o.Title:o.title);var r='<article class=\\\"review\\\"><div class=\\\"reviewTop\\\">'+(av?imgTag(av,'avatar',''):'<span class=\\\"avatarFb\\\">书</span>')+'<div class=\\\"reviewName\\\">'+esc(nm)+'</div></div>';if(body)r+='<div class=\\\"reviewBody\\\">'+esc(body)+'</div>';for(var ii=0;ii<ims.length;ii++)r+=imgTag(ims[ii],'topicImg','margin-left:41px;max-width:72%');if(vd&&vd.url)r+=videoTag(vd,'topicVideo');var subs=qfReplyRows(o);if(subs.length){r+='<div class=\\\"subReplies\\\">';for(var si=0;si<subs.length&&si<5;si++)r+=subReplyHtml(subs[si]);r+='</div>';}var rid=qfReviewId(o);if(rid){var hidden=(rp<=subs.length)?' style=\\\"display:none\\\"':'';var label=rp>subs.length?'查看全部 '+rp+' 条回复 ›':'查看回复 ›';r+='<span class=\\\"replyMore qfReplyMore\\\"'+hidden+' data-rid=\\\"'+esc(rid)+'\\\" data-count=\\\"'+rp+'\\\">'+label+'</span>';}r+='<div class=\\\"reviewMeta\\\">'+esc(tm)+(rp?' · '+esc(rp)+'回复':'')+(lk!=null&&lk!==''?' · '+esc(lk)+'赞':'')+'</div></article>';return r;}");
    h.push("function arrays(d){var a=d.ReviewDataList||d.reviewDataList||[],b=d.AuthorReviewDataList||d.authorReviewDataList||[];if(!Array.isArray(a))a=[];if(!Array.isArray(b))b=[];return b.concat(a);}");

    h.push("function qfFindReplyArray(v,d){if(!v||d>9||typeof v!=='object')return [];var names=['ReplyList','replyList','ReviewList','reviewList','ReplyDataList','replyDataList','ReviewDataList','reviewDataList','SubReviewList','subReviewList'];for(var i=0;i<names.length;i++){var a=v[names[i]];if(Array.isArray(a)&&a.length)return a;}if(Array.isArray(v)){for(var j=0;j<v.length;j++){var z=qfFindReplyArray(v[j],d+1);if(z.length)return z;}return [];}var ks=Object.keys(v);for(var k=0;k<ks.length;k++){var x=v[ks[k]];if(x&&typeof x==='object'){var y=qfFindReplyArray(x,d+1);if(y.length)return y;}}return [];}");
    h.push("function qfReviewDetailRows(root){return qfFindReplyArray(dataOf(root),0);}")
    h.push("function qfObjId(o){o=o||{};return String(o.comment_id||o.review_id||o.ReviewId||o.reviewId||o.CommentId||o.commentId||o.Id||o.id||o.PostId||o.postId||'');}");
    h.push("function qfParentIds(o){o=o||{};var a=[o.reffer_comment_id,o.ref_comment_id,o.reply_review_id,o.reply_to_review_id,o.quote_review_id,o.source_review_id,o.root_review_id,o.parent_review_id,o.parent_id,o.RefferCommentId,o.refferCommentId,o.RefCommentId,o.refCommentId,o.ReplyReviewId,o.replyReviewId,o.ReplyToReviewId,o.replyToReviewId,o.QuoteReviewId,o.quoteReviewId,o.SourceReviewId,o.sourceReviewId,o.RootReviewId,o.rootReviewId,o.ParentReviewId,o.parentReviewId,o.ParentId,o.parentId];var out=[];for(var i=0;i<a.length;i++){if(a[i]!=null&&String(a[i])!=='')out.push(String(a[i]));}return out;}");
    h.push("function qfLooksReview(o){if(!o||typeof o!=='object'||Array.isArray(o))return false;var u=o.user_info||o.UserInfo||o.userInfo||o.User||o.user||{};var hasUser=!!(o.user_name||o.UserName||o.userName||o.NickName||o.nickName||u.user_name||u.UserName||u.userName||u.NickName||u.nickName);var hasBody=!!txt(o.text!=null?o.text:(o.content!=null?o.content:(o.Body!=null?o.Body:(o.body!=null?o.body:(o.Content!=null?o.Content:(o.BodyRichText!=null?o.BodyRichText:o.bodyRichText))))));return hasUser&&hasBody;}");
    h.push("function qfLinkedReplies(root,rid){rid=String(rid||'');var out=[],seen={},seenObj=[];function add(o){if(!qfLooksReview(o))return;var id=qfObjId(o);if(id&&id===rid)return;var ps=qfParentIds(o),ok=false;for(var i=0;i<ps.length;i++)if(ps[i]===rid){ok=true;break;}if(!ok)return;var k=id||user(o)+'|'+txt(o.Body||o.body||o.Content||o.content).slice(0,80);if(k&&seen[k])return;if(k)seen[k]=1;out.push(o);}function walk(v,d){if(!v||d>12||typeof v!=='object')return;if(seenObj.indexOf(v)>=0)return;seenObj.push(v);if(Array.isArray(v)){for(var i=0;i<v.length&&i<300;i++)walk(v[i],d+1);return;}add(v);var ks=Object.keys(v);for(var j=0;j<ks.length;j++){var x=v[ks[j]];if(x&&typeof x==='object')walk(x,d+1);}}walk(root,0);return out;}");
    h.push("function qfLooseReplyRows(root,rid){var linked=qfLinkedReplies(root,rid);if(linked.length)return linked;var all=[],seen={},seenObj=[];function walk(v,d){if(!v||d>11||typeof v!=='object')return;if(seenObj.indexOf(v)>=0)return;seenObj.push(v);if(Array.isArray(v)){for(var i=0;i<v.length&&i<300;i++)walk(v[i],d+1);return;}if(qfLooksReview(v)){var id=qfObjId(v);if(id!==String(rid||'')){var k=id||user(v)+'|'+txt(v.Body||v.body||v.Content||v.content).slice(0,80);if(k&&!seen[k]){seen[k]=1;all.push(v);}}}var ks=Object.keys(v);for(var j=0;j<ks.length;j++){var x=v[ks[j]];if(x&&typeof x==='object')walk(x,d+1);}}walk(dataOf(root),0);return all;}");
;

    h.push("var detail=document.getElementById('detail'),body=document.getElementById('detailBody'),qfDetailPageCache={},state={cid:'',pid:'',pg:1,total:0,loading:false,previewImgs:[],detailRoot:null};document.getElementById('dBack').onclick=function(){detail.style.display='none';document.body.style.overflow='';};");
    h.push("function loadReviewReplies(el,auto){if(!el||el.getAttribute('data-loading')==='1')return;var rid=String(el.getAttribute('data-rid')||'');if(!rid)return;el.setAttribute('data-loading','1');if(!auto){el.style.display='inline-block';el.textContent='正在加载回复…';}var attempts=[{path:'v1/circle/getreviewdetail',p:{circleId:state.cid,postId:state.pid,reviewId:rid,sort:'0'}},{path:'v1/circle/getreviewdetail',p:{circleId:state.cid,postId:state.pid,commentId:rid,sort:'0'}},{path:'v1/circle/getreviewdetail',p:{circleId:state.cid,postId:state.pid,rootReviewId:rid,sort:'0'}},{path:'v1/circle/getreviewdetail',p:{circleId:state.cid,postId:state.pid,reviewId:rid,pageIndex:'1',pageSize:'50',sortType:'0'}},{path:'v1/circle/getreviewdetail',p:{circleId:state.cid,postId:state.pid,commentId:rid,pg:'1',pz:'50',type:'1',sort:'0'}},{path:'v1/circle/getreviewdetail',p:{circleId:state.cid,reviewId:rid,pg:'1',pz:'50',sort:'0'}},{path:'v1/circle/getpostdetail',p:{circleId:state.cid,postId:state.pid,reviewId:rid,pg:'1',pz:'50',sort:'0'}},{path:'v1/circle/getpostdetail',p:{circleId:state.cid,postId:state.pid,rootReviewId:rid,pg:'1',pz:'50',sort:'0'}}],rows=[],lastErr='';if(state.detailRoot)rows=qfLinkedReplies(state.detailRoot,rid);for(var i=0;i<attempts.length&&!rows.length;i++){try{var req=signed(attempts[i].path,attempts[i].p),root=parse(ajax(req));rows=qfLinkedReplies(root,rid);if(!rows.length)rows=qfReviewDetailRows(root);if(!rows.length)rows=qfLooseReplyRows(root,rid);}catch(e){lastErr=String(e&&e.message?e.message:e);}}if(rows.length){var old=el.parentNode.querySelector('.subReplies');if(old)old.parentNode.removeChild(old);var box=document.createElement('div');box.className='subReplies';var hh='';for(var j=0;j<rows.length&&j<50;j++)hh+=subReplyHtml(rows[j]);box.innerHTML=hh;el.parentNode.insertBefore(box,el);el.style.display='none';}else{if(!auto){el.style.display='inline-block';el.textContent='暂未获取到回复'+(lastErr?' · '+lastErr:'');}else{el.style.display='none';}el.setAttribute('data-loading','0');}}");
    h.push("function fetchDetail(reset){if(state.loading)return;state.loading=true;if(reset){state.pg=1;body.innerHTML='<div class=\\\"loading\\\">正在加载起点官方帖子详情…</div>';}try{var dk=state.cid+'|'+state.pid+'|'+state.pg,dc=qfDetailPageCache[dk],root=null;if(dc&&Date.now()-Number(dc.ts||0)<120000){root=dc.root;}else{var req=signed('v1/circle/getpostdetail',{circleId:state.cid,postId:state.pid,pg:String(state.pg),pz:'20',sort:'0'});root=parse(ajax(req));qfDetailPageCache[dk]={ts:Date.now(),root:root};var dks=Object.keys(qfDetailPageCache);if(dks.length>24){dks.sort(function(a,b){return Number((qfDetailPageCache[a]||{}).ts||0)-Number((qfDetailPageCache[b]||{}).ts||0);});while(dks.length>24)delete qfDetailPageCache[dks.shift()];}}state.detailRoot=root;var d=dataOf(root),topic=d.TopicData||d.topicData||{},rows=arrays(d),total=Number(d.TotalCount||d.totalCount||rows.length)||rows.length;state.total=total;if(reset){body.innerHTML=topicHtml(topic,root)+'<div class=\\\"reviewTitle\\\">全部回复'+(total?'（'+total+'）':'')+'</div><div id=\\\"reviewList\\\"></div><button class=\\\"moreBtn\\\" id=\\\"moreBtn\\\">加载更多评论</button>';}bindVideoFallback(body);var list=document.getElementById('reviewList');for(var i=0;i<rows.length;i++)list.insertAdjacentHTML('beforeend',reviewHtml(rows[i]));var arts=list.querySelectorAll('.review');for(var ai=0;ai<arts.length&&ai<rows.length;ai++){var rid=qfReviewId(rows[ai]);if(!rid)continue;var linked=qfLinkedReplies(root,rid);if(linked.length&&!arts[ai].querySelector('.subReplies')){var box=document.createElement('div');box.className='subReplies';var hh='';for(var li=0;li<linked.length&&li<5;li++)hh+=subReplyHtml(linked[li]);box.innerHTML=hh;var meta=arts[ai].querySelector('.reviewMeta');arts[ai].insertBefore(box,meta||null);}}var rms=list.querySelectorAll('.qfReplyMore');for(var ri=0;ri<rms.length;ri++){if(!rms[ri].getAttribute('data-bound')){rms[ri].setAttribute('data-bound','1');rms[ri].onclick=function(){var el=this;el.style.display='inline-block';el.textContent='正在加载回复…';setTimeout(function(){loadReviewReplies(el,false);},30);};}}var btn=document.getElementById('moreBtn');if(btn){if(!rows.length||list.children.length>=total){btn.style.display='none';}else{btn.style.display='block';btn.onclick=function(){state.pg++;fetchDetail(false);};}}}catch(e){body.innerHTML='<div class=\\\"err\\\">帖子详情加载失败：'+esc(e&&e.message?e.message:e)+'</div>';}state.loading=false;}");
    h.push("var qfDetailScrollTimer=0;detail.addEventListener('scroll',function(){if(qfDetailScrollTimer||state.loading)return;qfDetailScrollTimer=setTimeout(function(){qfDetailScrollTimer=0;var btn=document.getElementById('moreBtn');if(!btn||btn.style.display==='none')return;if(detail.scrollTop+detail.clientHeight>=detail.scrollHeight-420){state.pg++;fetchDetail(false);}},100);},{passive:true});");
    h.push("function bindPostOpens(root){root=root||document;var opens=root.querySelectorAll('.qfPostOpen');for(var oi=0;oi<opens.length;oi++){if(opens[oi].getAttribute('data-bound'))continue;opens[oi].setAttribute('data-bound','1');opens[oi].onclick=function(){state.cid=String(this.getAttribute('data-cid')||CIRCLE_ID);state.pid=String(this.getAttribute('data-pid')||'');var pim=qfNormUrl(this.getAttribute('data-img')||'');state.previewImgs=pim?[pim]:[];state.detailRoot=null;detail.style.display='block';detail.scrollTop=0;document.body.style.overflow='hidden';body.innerHTML='<div class=\\\"loading\\\"><div class=\\\"spin\\\"></div>正在加载帖子详情…</div>';setTimeout(function(){fetchDetail(true);},35);};}}bindPostOpens(document);");

    h.push("function qfFreshVideo(cid,pid,poster,fallback){var vd={url:qfNormUrl(fallback||''),urls:[],poster:qfNormUrl(poster||''),pageUrl:''};function add(u){u=qfNormUrl(u);if(/^https?:\\/\\//i.test(u)&&vd.urls.indexOf(u)<0)vd.urls.push(u);}function adopt(fresh){if(!fresh)return;var old=vd.url,page=vd.pageUrl;vd=fresh;if(!Array.isArray(vd.urls))vd.urls=[];if(old&&vd.urls.indexOf(old)<0)vd.urls.push(old);if(!vd.poster)vd.poster=qfNormUrl(poster||'');if(!vd.pageUrl)vd.pageUrl=page||'';}add(vd.url);if(pid){var page='https://h5.if.qidian.com/h5/share/post/topic?circleId='+encodeURIComponent(String(cid||CIRCLE_ID))+'&postId='+encodeURIComponent(String(pid));vd.pageUrl=page;try{var req=signed('v1/circle/getpostdetail',{circleId:String(cid||CIRCLE_ID),postId:String(pid),pg:'1',pz:'1',sort:'0'}),root0=parse(ajax(req)),d=dataOf(root0),topic=d.TopicData||d.topicData||{},fresh=videoInfo(root0,richOf(topic).raw);if(fresh&&fresh.url)adopt(fresh);}catch(_e){}if(!vd.url){try{var opt={method:'GET',timeout:10000,headers:{'User-Agent':'Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36','Accept':'text/html,application/xhtml+xml,*/*','Referer':'https://h5.if.qidian.com/'}},raw=String(window.java.ajax(page+','+JSON.stringify(opt))||''),fresh2=videoInfo(raw,raw);if(fresh2&&fresh2.url)adopt(fresh2);}catch(_p){}}vd.pageUrl=page;}if(!Array.isArray(vd.urls))vd.urls=[];add(vd.url);if(!vd.url&&vd.urls.length)vd.url=vd.urls[0];return vd;}\nfunction qfStartVideoBox(box,external){if(!box||box.getAttribute('data-loading')==='1')return;box.setAttribute('data-loading','1');box.classList.add('qfVideoLoading');var cid=String(box.getAttribute('data-cid')||CIRCLE_ID),pid=String(box.getAttribute('data-pid')||''),poster=qfNormUrl(box.getAttribute('data-poster')||''),fallback=qfNormUrl(box.getAttribute('data-url')||''),status=box.querySelector('.qfVideoStatus');if(status)status.textContent=external?'正在获取最新播放地址…':'正在准备视频…';var vd=qfFreshVideo(cid,pid,poster,fallback),urls=[],u='';function add(u0){u0=qfNormUrl(u0);if(/^https?:\\/\\//i.test(u0)&&urls.indexOf(u0)<0)urls.push(u0);}if(vd&&Array.isArray(vd.urls)){for(var ui=0;ui<vd.urls.length;ui++)add(vd.urls[ui]);}add(vd&&vd.url);add(fallback);u=urls.length?urls[0]:'';box.removeAttribute('data-loading');box.classList.remove('qfVideoLoading');if(!u){if(vd&&vd.pageUrl){box.classList.add('qfVideoFailed');if(status)status.textContent='未拿到直链，正在打开起点官方帖子播放…';openMediaUrl(vd.pageUrl);return;}box.classList.add('qfVideoFailed');if(status)status.textContent='暂未解析到有效播放地址';return;}box.setAttribute('data-url',u);if(vd.poster)box.setAttribute('data-poster',qfNormUrl(vd.poster));if(external){openMediaUrl(u);return;}var oldv=box.querySelector('video');if(oldv){try{oldv.pause();}catch(_ov){}try{oldv.parentNode.removeChild(oldv);}catch(_or){}}var cls=String(box.getAttribute('data-vclass')||'topicVideo'),v=document.createElement('video');v.className=cls;v.controls=true;v.preload='metadata';v.setAttribute('playsinline','');v.setAttribute('webkit-playsinline','');v.setAttribute('x5-playsinline','true');v.setAttribute('x5-video-player-type','h5-page');v.setAttribute('x5-video-player-fullscreen','false');if(vd.poster)v.poster=qfNormUrl(vd.poster);var open=box.querySelector('.qfVideoOpen');box.classList.remove('qfVideoFailed','qfVideoNeedTap');box.classList.add('qfVideoPlaying');var posterEl=box.querySelector('.qfVideoPoster'),playEl=box.querySelector('.qfVideoPlayBtn');if(posterEl)posterEl.style.display='none';if(playEl)playEl.style.display='none';box.insertBefore(v,open||null);var idx=0,dead=false;function hardFail(){if(dead)return;dead=true;box.classList.add('qfVideoFailed');box.classList.remove('qfVideoPlaying','qfVideoNeedTap');if(status){status.style.display='block';status.textContent='内置播放失败，可外部打开';}if(open){open.style.display='block';open.textContent='内置播放失败，点此重新获取地址并外部打开';}}\nfunction playNow(){try{var pr=v.play();if(pr&&typeof pr.then==='function'){pr.then(function(){box.classList.remove('qfVideoNeedTap');if(status)status.style.display='none';}).catch(function(e){var nm=String(e&&e.name||'');if(/NotAllowed|Abort/i.test(nm)||!v.error){box.classList.add('qfVideoNeedTap');if(status){status.style.display='block';status.textContent='视频已加载，点这里或播放键开始播放';status.onclick=function(ev){if(ev&&ev.stopPropagation)ev.stopPropagation();playNow();};}}else{setTimeout(function(){if(v.error)nextSource();else{box.classList.add('qfVideoNeedTap');if(status){status.style.display='block';status.textContent='点这里开始播放';}}},30);}});}}catch(_p){box.classList.add('qfVideoNeedTap');if(status){status.style.display='block';status.textContent='点这里开始播放';status.onclick=function(ev){if(ev&&ev.stopPropagation)ev.stopPropagation();playNow();};}}}\nfunction setSource(n){if(n>=urls.length){hardFail();return;}idx=n;var su=urls[idx];box.setAttribute('data-url',su);try{v.pause();}catch(_p0){}try{v.removeAttribute('src');v.load();}catch(_p1){}v.src=su;try{v.load();}catch(_l){}playNow();}\nfunction nextSource(){if(dead)return;var ni=idx+1;if(ni<urls.length){if(status){status.style.display='block';status.textContent='正在尝试备用播放地址…';}setSource(ni);}else hardFail();}\nv.onerror=function(){nextSource();};v.onloadedmetadata=function(){box.classList.remove('qfVideoFailed');if(open)open.style.display='none';if(status&&!box.classList.contains('qfVideoNeedTap'))status.style.display='none';};v.oncanplay=function(){if(!box.classList.contains('qfVideoNeedTap')&&status)status.style.display='none';};setSource(0);}\nfunction bindVideoFallback(root){root=root||document;var ws=root.querySelectorAll('.qfVideoWrap');for(var i=0;i<ws.length;i++){var w=ws[i];if(w.getAttribute('data-vbound'))continue;w.setAttribute('data-vbound','1');var p=w.querySelector('.qfVideoPlayBtn'),b=w.querySelector('.qfVideoOpen');if(p)p.onclick=(function(box){return function(ev){if(ev&&ev.stopPropagation)ev.stopPropagation();qfStartVideoBox(box,false);};})(w);if(b)b.onclick=(function(box){return function(ev){if(ev&&ev.stopPropagation)ev.stopPropagation();qfStartVideoBox(box,true);};})(w);}}\nfunction bindVideoLazy(root){root=root||document;var xs=root.querySelectorAll('.qfVideoLazy');for(var i=0;i<xs.length;i++){if(xs[i].getAttribute('data-bound'))continue;xs[i].setAttribute('data-bound','1');xs[i].onclick=function(ev){if(ev&&ev.stopPropagation)ev.stopPropagation();var box=this,cid=String(box.getAttribute('data-cid')||CIRCLE_ID),pid=String(box.getAttribute('data-pid')||''),poster=qfNormUrl(box.getAttribute('data-poster')||''),vd=qfFreshVideo(cid,pid,poster,'');if(vd&&vd.url){var holder=document.createElement('div');holder.innerHTML=videoTag(vd,'postVideo',cid,pid);var nw=holder.firstChild;box.parentNode.replaceChild(nw,box);bindVideoFallback(nw.parentNode||document);qfStartVideoBox(nw,false);return;}if(vd&&vd.pageUrl){var tx0=box.querySelector('.qfPlayText');if(tx0)tx0.textContent='正在打开起点官方帖子播放…';openMediaUrl(vd.pageUrl);return;}var tx=box.querySelector('.qfPlayText');if(tx)tx.textContent='暂未解析到播放地址，点“查看详情”再试';};}}bindVideoLazy(document);bindVideoFallback(document);");
    /* 动态分类筛选：使用已真机命中的 getcirclepostlist 字段。 */
    h.push("function feedRows(root){var d=dataOf(root),a=d.TopicDataList||d.topicDataList||d.PostList||d.postList||[];return Array.isArray(a)?a:[];}");
    h.push("function feedCard(o,label){o=o||{};label=String(label||'');var cid=String(o.CircleId||o.circleId||CIRCLE_ID),pid=String(o.PostId||o.postId||o.Id||o.id||''),nm=String(o.user||user(o)||'书友'),av=qfNormUrl(o.avatar||avatar(o)||''),title=String(o.title||titleOf(o)||''),rr=richOf(o),rich=rr.raw,bd=String(o.body||rr.text||''),ims=imageUrls(o,rich),tm=String(o.time||time(o)||''),rp=o.reply!=null?o.reply:(o.PostCount!=null?o.PostCount:(o.CommentCount!=null?o.CommentCount:(o.commentCount!=null?o.commentCount:''))),lk=o.like!=null?o.like:(o.StarCount!=null?o.StarCount:(o.LikeCount!=null?o.LikeCount:o.likeCount));var directImgs=Array.isArray(o.images)?o.images:[];for(var dix=directImgs.length-1;dix>=0;dix--){var diu=qfNormUrl(directImgs[dix]);if(diu&&ims.indexOf(diu)<0)ims.unshift(diu);}var directImg=qfNormUrl(o.image||'');if(directImg&&ims.indexOf(directImg)<0)ims.unshift(directImg);var vd={url:qfNormUrl(o.video||''),poster:qfNormUrl(o.videoPoster||'')};if(!vd.url)vd=videoInfo(o,rich);if(!vd.poster&&ims.length)vd.poster=ims[0];var fb=(nm||'书').slice(0,1);var r='<article class=\"post\"><div class=\"user\">'+(av?imgTag(av,'avatar',''):'<span class=\"avatarFb\">'+esc(fb)+'</span>')+'<span class=\"u\">'+esc(nm)+'</span>'+(label&&label!=='全部'?'<span class=\"kindTag\">'+esc(label)+'</span>':'')+'</div>';if(title)r+='<div class=\"t\">'+esc(title)+'</div>';if(bd&&bd!==title)r+='<div class=\"b\">'+esc(bd)+'</div>';if((vd&&vd.url)||(label==='同人视频'&&pid)){if(!vd)vd={url:'',poster:''};if(!vd.poster&&ims.length)vd.poster=ims[0];r+=videoTag(vd,'postVideo',cid,pid);}else if(ims.length)r+=imageGridTag(ims);var ms=[];if(tm)ms.push(tm);if(rp!==''&&rp!=null)ms.push('💬 '+rp);if(lk!==''&&lk!=null)ms.push('♡ '+lk);r+='<div class=\"postFoot\"><div class=\"meta\">'+esc(ms.join('　'))+'</div>';if(pid)r+='<span class=\"go qfPostOpen\" data-cid=\"'+esc(cid)+'\" data-pid=\"'+esc(pid)+'\" data-img=\"'+esc(ims.length?ims[0]:'')+'\">查看详情 ›</span>';return r+'</div></article>';}");
    h.push("var INITIAL_ROWS="+JSON.stringify({
        dongtai:tabs.dongtai||posts||[],
        jinghua:tabs.jinghua||[],
        tongren:tabs.tongren||[],
        discussion:tabs.discussion||[],
        discussionPreview:tabs.discussionPreview||[]
    })+";");
    h.push("var currentSort='6',currentTab='dongtai';");
    h.push("var TOP_META="+JSON.stringify({
        dongtai:{id:"0"},
        jinghua:{id:"2",essence:true},
        tongren:{id:"316",parentId:String((categoryMeta.tongren&&categoryMeta.tongren.treePostCategoryId)||"")}
    })+";");
    h.push("function feedFingerprint(rows){var a=[];rows=Array.isArray(rows)?rows:[];for(var i=0;i<rows.length&&i<8;i++){var o=rows[i]||{},id=String(o.PostId||o.postId||o.Id||o.id||o.TopicId||o.topicId||'');if(id)a.push(id);else a.push(String(o.Title||o.title||'')+'|'+txt(o.Body||o.body||o.Content||o.content).slice(0,60));}return a.join('||');}");
    h.push("function qfCatValues(o,keys){o=o||{};var out=[],seen={};function add(v){if(v===undefined||v===null||String(v)==='')return;v=String(v);if(!seen[v]){seen[v]=1;out.push(v);}}var bs=[o,o.PostBasicInfo,o.postBasicInfo,o.PostBasicBean,o.postBasicBean,o.BasicInfo,o.basicInfo,o.PostInfo,o.postInfo,o.TopicInfo,o.topicInfo,o.PostCategoryInfo,o.postCategoryInfo,o.CategoryInfo,o.categoryInfo,o.SubCategoryInfo,o.subCategoryInfo,o.ExtInfo,o.extInfo];for(var b=0;b<bs.length;b++){var x=bs[b];if(!x||typeof x!=='object')continue;for(var k=0;k<keys.length;k++)add(x[keys[k]]);}return out;}function qfCatField(o,keys){var a=qfCatValues(o,keys);return a.length?a[0]:'';}function rowCats(o){return qfCatValues(o,['PostCategoryId','postCategoryId','CategoryId','categoryId','PostCategoryJsId','postCategoryJsId','CategoryJsId','categoryJsId']);}function rowSubs(o){return qfCatValues(o,['SubCategoryId','subCategoryId','SubCategory','subCategory','SubCategoryJsId','subCategoryJsId','SubJsId','subJsId','JsCategoryId','jsCategoryId']);}function rowCat(o){var a=rowCats(o);return a.length?a[0]:'';}function rowSub(o){var a=rowSubs(o);return a.length?a[0]:'';}function rowEssence(o){var vs=qfCatValues(o,['IsJinghua','isJinghua','IsJingHua','isJingHua','IsGodReview','isGodReview','IsEssence','isEssence','IsBest','isBest']);for(var i=0;i<vs.length;i++){var v=String(vs[i]).toLowerCase();if(v==='1'||v==='true')return true;}return false;}function idsOf(c){var a=[String(c&&c.id||''),String(c&&c.altId||'')],r=[];for(var i=0;i<a.length;i++)if(a[i]&&r.indexOf(a[i])<0)r.push(a[i]);return r;}function qfAnyEq(vals,ids,ban){for(var i=0;i<vals.length;i++)for(var z=0;z<ids.length;z++)if(vals[i]===ids[z]&&(!ban||ban.indexOf(ids[z])<0))return true;return false;}function localCategoryFilter(rows,c,ignoreEssence){rows=Array.isArray(rows)?rows:[];var ids=idsOf(c),mode=String(c&&c.mode||''),parentId=String(c&&c.parentId||''),out=[];for(var i=0;i<rows.length;i++){var o=rows[i]||{},pcs=rowCats(o),scs=rowSubs(o),cat=qfAnyEq(pcs,ids,[])||qfAnyEq(scs,ids,[]),ok=false;if(mode==='sub'||mode==='subId'||mode==='post'||mode==='category')ok=cat;else if(mode==='fan-sub'||mode==='fan-subId'||mode==='fan-parent-sub'){var ban=['316'];if(parentId)ban.push(parentId);ok=qfAnyEq(scs,ids,ban)||qfAnyEq(pcs,ids,ban);}else if(mode==='fan-post'||mode==='fan-category')ok=qfAnyEq(pcs,ids,['316',parentId])||qfAnyEq(scs,ids,['316',parentId]);else if(mode==='essence-sub'||mode==='essence-subId'||mode==='essence-post-god'||mode==='essence-post-jh')ok=cat;else if(mode==='all'||mode==='fan-all'||mode==='essence-all')ok=true;else if(mode==='fan-god'||mode==='fan-jinghua')ok=rowEssence(o);if(ok)out.push(o);}return out;}");
    h.push("function listRequest(params){var req=signed('v1/circle/getcirclepostlist',params),root=parse(ajax(req));return {root:root,rows:feedRows(root)};}");
    h.push("var qfPageRequestCache={};function qfParamKey(p){p=p||{};var ks=Object.keys(p).sort(),a=[];for(var i=0;i<ks.length;i++)a.push(ks[i]+'='+String(p[ks[i]]==null?'':p[ks[i]]));return a.join('&');}function qfCachedList(p){var k=qfParamKey(p),now=Date.now(),hit=qfPageRequestCache[k];if(hit&&now-Number(hit.ts||0)<45000)return Array.isArray(hit.rows)?hit.rows.slice(0):[];var rows=(listRequest(p).rows||[]);qfPageRequestCache[k]={ts:now,rows:rows.slice(0)};var ks=Object.keys(qfPageRequestCache);if(ks.length>72){ks.sort(function(a,b){return Number((qfPageRequestCache[a]||{}).ts||0)-Number((qfPageRequestCache[b]||{}).ts||0);});while(ks.length>72)delete qfPageRequestCache[ks.shift()];}return rows;}");
    h.push("function rowPostId(o){o=o||{};return String(o.PostId||o.postId||o.Id||o.id||o.TopicId||o.topicId||'');}function mergeFeedRows(a,b){a=Array.isArray(a)?a:[];b=Array.isArray(b)?b:[];var out=[],seen={};function add(o){var id=rowPostId(o),k=id||String(o.title||o.Title||'')+'|'+String(o.body||o.Body||o.Content||'').slice(0,80);if(k&&seen[k])return;if(k)seen[k]=1;out.push(o);}for(var i=0;i<a.length;i++)add(a[i]);for(var j=0;j<b.length;j++)add(b[j]);return out;}");
    h.push("function baseParams(tab,page){var top=TOP_META[tab]||TOP_META.dongtai;return {pageIndex:String(page||1),subCategory:'0',circleId:CIRCLE_ID,sortType:String(currentSort),postCategoryId:String(top.id||'0'),bookId:BOOK_ID,bookType:'1'};}");
    h.push("function topRequest(tab,page,params){var p=params||baseParams(tab,page),rows=qfCachedList(p);if(rows.length)return rows.slice(0);var q={pageIndex:String(page||1),subCategory:String(p.subCategory!=null?p.subCategory:(p.subCategoryId!=null?p.subCategoryId:'0')),circleId:CIRCLE_ID,postSortType:String(currentSort),postCategoryId:String(p.postCategoryId||'0'),qdBookId:BOOK_ID,qdBookType:'1'};if(p.categoryId!=null)q.categoryId=String(p.categoryId);if(p.subCategoryId!=null)q.subCategoryId=String(p.subCategoryId);if(p.isJinghua!=null)q.isJinghua=String(p.isJinghua);if(p.isGodReview!=null)q.isGodReview=String(p.isGodReview);return qfCachedList(q).slice(0);}");
    h.push("function discussionSingle(c,phase){var p=applyCandidate(baseParams('dongtai',1),c||{});if(Number(phase)===1){var q={pageIndex:'1',subCategory:String(p.subCategory!=null?p.subCategory:(p.subCategoryId!=null?p.subCategoryId:'0')),circleId:CIRCLE_ID,postSortType:String(currentSort),postCategoryId:String(p.postCategoryId||'0'),qdBookId:BOOK_ID,qdBookType:'1'};if(p.categoryId!=null)q.categoryId=String(p.categoryId);if(p.subCategoryId!=null)q.subCategoryId=String(p.subCategoryId);return (listRequest(q).rows||[]);}return (listRequest(p).rows||[]);}");
    h.push("function discussionAccept(rows,c){rows=Array.isArray(rows)?rows:[];if(!rows.length)return [];var local=localCategoryFilter(rows,c,true);if(local.length)return local;var all=INITIAL_ROWS.dongtai||[],rf=feedFingerprint(rows),af=feedFingerprint(all);if(!all.length||!af||rf!==af)return rows;return [];}function discussionPreview(c){var key=cacheKey('dongtai','讨论'),p=discussionPreviewCache[key];if(p&&p.length)return p.slice(0);var local=localCategoryFilter(INITIAL_ROWS.dongtai||[],c,true);if(local.length){discussionPreviewCache[key]=local.slice(0);return local;}return [];}function discussionAllPageFallback(c,page){var rows=[];try{rows=topRequest('dongtai',page,baseParams('dongtai',page));}catch(_e){}return localCategoryFilter(rows,c,true);}");
    h.push("var feedCache={},controlCache={},discussionPreviewCache={};if(INITIAL_ROWS.discussion&&INITIAL_ROWS.discussion.length)feedCache['dongtai|6|讨论']=INITIAL_ROWS.discussion.slice(0);if(INITIAL_ROWS.discussionPreview&&INITIAL_ROWS.discussionPreview.length)discussionPreviewCache['dongtai|6|讨论']=INITIAL_ROWS.discussionPreview.slice(0);function paneList(tab){var pane=document.getElementById('pane_'+tab);return pane&&pane.querySelector('.feedList');}function cacheKey(tab,label){return tab+'|'+currentSort+'|'+label;}function renderFiltered(tab,rows,label){var list=paneList(tab);if(!list)return;var hh='';for(var i=0;i<rows.length&&i<200;i++)hh+=feedCard(rows[i],String(label||''));list.innerHTML=hh||'<div class=\"empty\">当前分类暂无帖子</div>';bindPostOpens(list);bindVideoLazy(list);bindVideoFallback(list);}function showFilterBusy(tab,label){var list=paneList(tab);if(list)list.innerHTML='<div class=\"filterBusy qfSkeleton\"><div class=\"skHead\"></div><div class=\"skLine w1\"></div><div class=\"skLine w2\"></div><div class=\"skLine w3\"></div><div class=\"skNote\">正在加载 '+esc(label)+'…</div></div>';}");
    h.push("function parseCandidateAttr(chip){var out=[];try{out=JSON.parse(String(chip.getAttribute('data-candidates')||'[]'));}catch(_e){}if(!Array.isArray(out))out=[];var seen={},r=[];for(var i=0;i<out.length&&r.length<8;i++){var x=out[i]||{},id=String(x.id||''),altId=String(x.altId||''),mode=String(x.mode||'sub'),parentId=String(x.parentId||'');if(!/^-?\\d{1,22}$/.test(id))continue;if(altId&&!/^-?\\d{1,22}$/.test(altId))altId='';if(parentId&&!/^-?\\d{1,22}$/.test(parentId))parentId='';var k=id+'|'+altId+'|'+mode+'|'+parentId;if(seen[k])continue;seen[k]=1;r.push({id:id,altId:altId,mode:mode,parentId:parentId,source:String(x.source||'')});}return r;}");
    h.push("function cloneObj(o){var x={};for(var k in o)x[k]=o[k];return x;}function applyCandidate(base,c){var p=cloneObj(base),id=String(c&&c.id||''),mode=String(c&&c.mode||'all'),parentId=String(c&&c.parentId||'');if(mode==='all'||mode==='fan-all')return p;if(mode==='sub'){p.subCategory=id;delete p.subCategoryId;return p;}if(mode==='subId'){delete p.subCategory;p.subCategoryId=id;return p;}if(mode==='post'){p.postCategoryId=id;p.subCategory='0';delete p.subCategoryId;delete p.categoryId;return p;}if(mode==='category'){p.categoryId=id;p.postCategoryId='0';p.subCategory='0';delete p.subCategoryId;return p;}if(mode==='essence-all'){p.postCategoryId='2';p.subCategory='0';delete p.subCategoryId;delete p.categoryId;delete p.isJinghua;delete p.isGodReview;return p;}if(mode==='essence-sub'){p.postCategoryId='2';p.subCategory=id;delete p.subCategoryId;delete p.categoryId;delete p.isJinghua;delete p.isGodReview;return p;}if(mode==='essence-subId'){p.postCategoryId='2';delete p.subCategory;p.subCategoryId=id;delete p.categoryId;delete p.isJinghua;delete p.isGodReview;return p;}if(mode==='essence-post-god'){p.postCategoryId=id;p.subCategory='0';delete p.subCategoryId;delete p.categoryId;p.isGodReview='true';delete p.isJinghua;return p;}if(mode==='essence-post-jh'){p.postCategoryId=id;p.subCategory='0';delete p.subCategoryId;delete p.categoryId;p.isJinghua='1';delete p.isGodReview;return p;}if(mode==='fan-sub'){p.postCategoryId='316';p.subCategory=id;delete p.subCategoryId;delete p.isGodReview;delete p.isJinghua;return p;}if(mode==='fan-subId'){p.postCategoryId='316';delete p.subCategory;p.subCategoryId=id;delete p.isGodReview;delete p.isJinghua;return p;}if(mode==='fan-parent-sub'){p.postCategoryId=parentId||'316';p.subCategory=id;delete p.subCategoryId;delete p.isGodReview;delete p.isJinghua;return p;}if(mode==='fan-post'){p.postCategoryId=id;p.subCategory='0';delete p.subCategoryId;delete p.isGodReview;delete p.isJinghua;return p;}if(mode==='fan-category'){p.postCategoryId='316';p.subCategory='0';p.categoryId=id;delete p.subCategoryId;delete p.isGodReview;delete p.isJinghua;return p;}if(mode==='fan-god'){p.postCategoryId='316';p.subCategory='0';p.isGodReview='true';delete p.isJinghua;return p;}if(mode==='fan-jinghua'){p.postCategoryId='316';p.subCategory='0';p.isJinghua='1';delete p.isGodReview;return p;}return p;}");
    h.push("function paramVariants(tab,c,page){var b=baseParams(tab,page),p=applyCandidate(b,c||{mode:'all',id:b.postCategoryId}),out=[p];if(tab==='tongren'&&String((TOP_META.tongren||{}).parentId||'')&&String(p.postCategoryId||'')==='316'){var q=cloneObj(p);q.postCategoryId=String(TOP_META.tongren.parentId);out.push(q);}return out;}");
    h.push("function dynamicControl(id){id=String(id||'0');var key=currentSort+'|'+id;if(controlCache[key])return controlCache[key];var p=baseParams('dongtai',1);p.postCategoryId=id;p.subCategory='0';var rows=[];try{rows=topRequest('dongtai',1,p);}catch(_e){}controlCache[key]=rows;return rows;}");
    h.push("function essenceAllControl(){var key=cacheKey('jinghua','全部');if(feedCache[key]&&feedCache[key].length)return feedCache[key];var rows=[];try{rows=topRequest('jinghua',1,baseParams('jinghua',1))||[];}catch(_e){}if(rows.length&&feedFingerprint(rows)!==feedFingerprint(INITIAL_ROWS.dongtai||[])){feedCache[key]=rows.slice(0);return rows;}return [];}function essenceVerified(rows,c,label){rows=Array.isArray(rows)?rows:[];if(!rows.length)return false;var fp=feedFingerprint(rows),dfp=feedFingerprint(INITIAL_ROWS.dongtai||[]);if(dfp&&fp===dfp)return false;if(label==='全部')return true;var all=essenceAllControl();if(all.length&&fp===feedFingerprint(all))return false;for(var k in feedCache){if(k.indexOf('jinghua|'+currentSort+'|')!==0||k===cacheKey('jinghua',label)||k===cacheKey('jinghua','全部'))continue;var rr=feedCache[k];if(rr&&rr.length&&feedFingerprint(rr)===fp)return false;}return true;}function essenceLocalPages(c,maxPages){var out=[];maxPages=Math.max(1,Number(maxPages)||3);for(var pg=1;pg<=maxPages;pg++){var rows=[];try{rows=topRequest('jinghua',pg,baseParams('jinghua',pg))||[];}catch(_e){}if(!rows.length)break;var hit=localCategoryFilter(rows,c,true);if(hit.length)out=mergeFeedRows(out,hit);if(rows.length<20)break;}return out;}");
    h.push("function qfSetOverlap(a,b){a=Array.isArray(a)?a:[];b=Array.isArray(b)?b:[];var s={},n=0,m=0;for(var i=0;i<b.length&&i<30;i++){var id=rowPostId(b[i]);if(id)s[id]=1;}for(var j=0;j<a.length&&j<30;j++){var x=rowPostId(a[j]);if(x){n++;if(s[x])m++;}}return n?m/n:0;}\nfunction qfCandidateTrust(c){var s=String(c&&c.source||'');if(/^verified-/i.test(s))return 3;if(/^official-/i.test(s))return 2;if(/^compat-/i.test(s))return 1;return 0;}\nfunction qfRowsSame(a,b){var af=feedFingerprint(a),bf=feedFingerprint(b);return !!(af&&bf&&af===bf);}\nfunction qfRowsDistinctEnough(rows,control,limit){rows=Array.isArray(rows)?rows:[];control=Array.isArray(control)?control:[];if(!rows.length)return false;if(!control.length)return true;if(qfRowsSame(rows,control))return false;return qfSetOverlap(rows,control)<Number(limit==null?0.92:limit);}\nfunction qfDynamicAccept(rows,c,label){rows=Array.isArray(rows)?rows:[];if(!rows.length)return [];var local=localCategoryFilter(rows,c,true);if(local.length)return local;var trust=qfCandidateTrust(c),all=INITIAL_ROWS.dongtai||[];if(trust<=0)return [];var lim=trust>=2?0.94:0.58;if(!qfRowsDistinctEnough(rows,all,lim))return [];if(String(label||'')!=='讨论'){var dc=dynamicControl('2');if(dc.length&&!qfRowsDistinctEnough(rows,dc,lim))return [];}return rows;}\nfunction qfEssenceAccept(rows,c,label){rows=Array.isArray(rows)?rows:[];if(!rows.length||!essenceVerified(rows,c,label))return [];if(String(label||'')==='全部')return rows;var local=localCategoryFilter(rows,c,true);if(local.length)return local;var trust=qfCandidateTrust(c);if(trust>=2)return rows;var all=essenceAllControl();if(trust===1&&qfRowsDistinctEnough(rows,all,0.55))return rows;return [];}\nfunction qfChipByTabLabel(tab,label){var cs=document.querySelectorAll('.chip');for(var i=0;i<cs.length;i++){var c=cs[i],nm=String(c.getAttribute('data-name')||''),ts=String(c.getAttribute('data-tabs')||'').split(',');if(nm===String(label||'')&&ts.indexOf(String(tab||''))>=0)return c;}return null;}\nfunction qfEssenceDiscussionFallback(){var dchip=qfChipByTabLabel('dongtai','讨论');if(!dchip)return [];var dcands=parseCandidateAttr(dchip),dmain=dcands.length?dcands[0]:null;if(!dmain)return [];var dk=cacheKey('dongtai','讨论'),discussion=(feedCache[dk]&&feedCache[dk].length)?feedCache[dk].slice(0):discussionPreview(dmain);if(!discussion.length){for(var ci=0;ci<dcands.length;ci++){try{var dg=requestCategory('dongtai',dcands[ci],false,'讨论');if(dg.rows&&dg.rows.length){discussion=dg.rows.slice(0);break;}}catch(_d){}}}for(var pg=2;pg<=8;pg++){var more=[];try{more=qfPageRows('dongtai','讨论',dmain,pg)||[];}catch(_p){more=[];}if(!more.length)break;discussion=mergeFeedRows(discussion,more);if(more.length<20)break;}if(!discussion.length)return [];var out=[],seen={};function add(o){var id=rowPostId(o),k=id||feedFingerprint([o]);if(k&&seen[k])return;if(k)seen[k]=1;out.push(o);}for(var i=0;i<discussion.length;i++)if(rowEssence(discussion[i]))add(discussion[i]);var essence=essenceAllControl().slice(0);for(var ep=2;ep<=4;ep++){var er=[];try{er=topRequest('jinghua',ep,baseParams('jinghua',ep))||[];}catch(_e){er=[];}if(!er.length)break;essence=mergeFeedRows(essence,er);if(er.length<20)break;}if(essence.length){var ids={};for(var ei=0;ei<essence.length;ei++){var eid=rowPostId(essence[ei]);if(eid)ids[eid]=1;}for(var di=0;di<discussion.length;di++){var did=rowPostId(discussion[di]);if(did&&ids[did])add(discussion[di]);}}return out;}\nfunction hasVideoHint(o){if(!o||typeof o!=='object')return false;var v=videoInfo(o,richOf(o).raw);if(v&&v.url)return true;var hit=false,seen=[],re=/(video|vod|playurl|play_url|videourl|video_url|videocover|video_cover|stream|media|vid|fileid|mediatype|contenttype|posttype)/i;function w(x,d,k){if(hit||x==null||d>9)return;if(typeof x==='string'){var z=String(x);if(re.test(String(k||''))&&z.length>0&&z!=='0'&&z.toLowerCase()!=='false')hit=true;if(/(?:VideoUrl|videoUrl|VideoCover|videoCover)[\"']?\\s*:/.test(z))hit=true;if(/\\.(?:mp4|m3u8|m4v|mov|webm)(?:[?#]|$)/i.test(z))hit=true;return;}if(typeof x!=='object')return;if(seen.indexOf(x)>=0)return;seen.push(x);if(Array.isArray(x)){for(var i=0;i<x.length&&i<120;i++)w(x[i],d+1,k);return;}var ks=Object.keys(x);for(var i=0;i<ks.length;i++){var kk=String(ks[i]),vv=x[ks[i]];if(re.test(kk)&&vv!=null&&String(vv)!=='0'&&String(vv)!==''&&String(vv).toLowerCase()!=='false')hit=true;w(vv,d+1,kk);if(hit)return;}}w(o,0,'');return hit;}\nfunction hasImageHint(o){var rr=richOf(o),ims=imageUrls(o,rr.raw);return ims.length>0;}\nvar fanPageCache={},fanScanState={};function fanPage(page){page=Math.max(1,Number(page)||1);var k=currentSort+'|'+page;if(fanPageCache[k])return fanPageCache[k].slice(0);var rows=[];try{rows=topRequest('tongren',page,baseParams('tongren',page))||[];}catch(_e){}fanPageCache[k]=rows.slice(0);if(page===1&&rows.length)feedCache[cacheKey('tongren','全部')]=rows.slice(0);return rows;}\nfunction fanOfficialRows(rows,c){if(!c)return [];var mode=String(c.mode||'');if(mode==='fan-god'||mode==='fan-jinghua'){var a=[];for(var i=0;i<rows.length;i++)if(rowEssence(rows[i]))a.push(rows[i]);return a;}return localCategoryFilter(rows,c,true);}\nfunction fanLocalByLabel(rows,c,label){rows=Array.isArray(rows)?rows:[];label=String(label||'');var out=[],seen={};function add(o){var k=rowPostId(o)||feedFingerprint([o]);if(k&&seen[k])return;if(k)seen[k]=1;out.push(o);}var official=fanOfficialRows(rows,c);if(label==='精华'){for(var oi=0;oi<official.length;oi++)add(official[oi]);for(var e=0;e<rows.length;e++)if(rowEssence(rows[e]))add(rows[e]);return out;}if(label==='同人视频'){for(var ov=0;ov<official.length;ov++)add(official[ov]);for(var vi=0;vi<rows.length;vi++)if(hasVideoHint(rows[vi]))add(rows[vi]);return out;}for(var i=0;i<rows.length;i++){var o=rows[i]||{},v=hasVideoHint(o),im=hasImageHint(o),rr=richOf(o),text=(titleOf(o)+' '+rr.text).trim();if(label==='同人图'&&!v&&im)add(o);else if(label==='同人文'&&!v&&!im&&text.length>=2)add(o);else if(label==='其他同人'&&!v&&!im&&text.length<2)add(o);}if((label==='同人图'||label==='同人文'||label==='其他同人')&&official.length){for(var of=0;of<official.length;of++)add(official[of]);}return out;}\nfunction fanAllControl(){var key=cacheKey('tongren','全部');if(feedCache[key]&&feedCache[key].length)return feedCache[key].slice(0);return fanPage(1);}\nfunction fanPreview(c,label){return fanLocalByLabel(fanAllControl(),c,label);}\nfunction fanCollectPages(c,label,maxPages,minWant){var all=[],out=[],seenPage={};maxPages=Math.max(1,Math.min(Number(maxPages)||6,18));minWant=Math.max(1,Number(minWant)||4);for(var pg=1;pg<=maxPages;pg++){var rows=fanPage(pg);if(!rows.length)break;var fp=feedFingerprint(rows);if(fp&&seenPage[fp])break;if(fp)seenPage[fp]=1;all=mergeFeedRows(all,rows);out=fanLocalByLabel(all,c,label);if(out.length>=minWant)break;}return out;}\nfunction fanAccept(rows,c,label){rows=Array.isArray(rows)?rows:[];var local=fanLocalByLabel(rows,c,label);if(local.length)return local;if(!rows.length)return [];var all=fanAllControl(),trust=qfCandidateTrust(c),lim=trust>=2?0.94:0.55;if(trust<=0)return [];if(all.length&&!qfRowsDistinctEnough(rows,all,lim))return [];return rows;}\nfunction fanLocalPages(c,label,maxPages){return fanCollectPages(c,label,maxPages,label==='同人视频'?3:(label==='精华'?6:5));}\nvar fanDirectState={};\nfunction fanDirectFetch(c,label,page){var vs=paramVariants('tongren',c,page),all=fanAllControl();for(var vi=0;vi<vs.length;vi++){try{var rows=topRequest('tongren',page,vs[vi])||[];if(!rows.length)continue;var hit=fanAccept(rows,c,label);if(hit.length)return hit;var fp=feedFingerprint(rows),af=feedFingerprint(all);if(!af||fp!==af)return rows;}catch(_e){}}return [];}\nfunction fanDirectProgressive(chip,label,c,seed,maxPages){var key=cacheKey('tongren',label),token=(fanDirectState[key]&&fanDirectState[key].token||0)+1;var best=Array.isArray(seed)?seed.slice(0):[];fanDirectState[key]={token:token,page:1,done:false,cand:c};maxPages=Math.max(2,Math.min(Number(maxPages)||8,16));var pg=2,seen={},empty=0;var fp0=feedFingerprint(best);if(fp0)seen[fp0]=1;function step(){var st=fanDirectState[key];if(!st||st.token!==token)return;if(currentTab!=='tongren'||!chip||!chip.classList.contains('active'))return;if(pg>maxPages){st.done=true;return;}setTimeout(function(){var st2=fanDirectState[key];if(!st2||st2.token!==token)return;var rows=fanDirectFetch(c,label,pg);st2.page=pg;if(!rows.length){empty++;if(empty>=2||pg>=maxPages){st2.done=true;return;}pg++;step();return;}empty=0;var fp=feedFingerprint(rows);if(fp&&seen[fp]){st2.done=true;return;}if(fp)seen[fp]=1;var merged=mergeFeedRows(best,rows);if(merged.length>best.length){best=merged;feedCache[key]=best.slice(0);if(currentTab==='tongren'&&chip.classList.contains('active'))renderFiltered('tongren',best,label);}pg++;step();},55);}step();}\nfunction fanProgressive(chip,label,c,seed,maxPages,target){var key=cacheKey('tongren',label),token=(fanScanState[key]&&fanScanState[key].token||0)+1;fanScanState[key]={token:token,page:1,done:false};var all=fanAllControl().slice(0),best=Array.isArray(seed)?seed.slice(0):fanLocalByLabel(all,c,label),seenPage={};var fp1=feedFingerprint(fanPage(1));if(fp1)seenPage[fp1]=1;if(best.length){feedCache[key]=best.slice(0);if(currentTab==='tongren'&&chip&&chip.classList.contains('active'))renderFiltered('tongren',best,label);}maxPages=Math.max(2,Math.min(Number(maxPages)||10,18));target=Math.max(2,Number(target)||4);var pg=2;function step(){var st=fanScanState[key];if(!st||st.token!==token)return;if(currentTab!=='tongren'||!chip||!chip.classList.contains('active')){st.page=pg-1;return;}if(pg>maxPages){st.done=true;return;}setTimeout(function(){var st2=fanScanState[key];if(!st2||st2.token!==token)return;var rows=fanPage(pg);st2.page=pg;if(!rows.length){st2.done=true;return;}var fp=feedFingerprint(rows);if(fp&&seenPage[fp]){st2.done=true;return;}if(fp)seenPage[fp]=1;all=mergeFeedRows(all,rows);var next=fanLocalByLabel(all,c,label);if(next.length>best.length){best=next;feedCache[key]=best.slice(0);if(currentTab==='tongren'&&chip.classList.contains('active'))renderFiltered('tongren',best,label);}if(best.length>=target){st2.done=true;return;}pg++;step();},45);}step();}\n");
    h.push("function requestCategory(tab,c,isAll,label){var vs=paramVariants(tab,c,1),last=[];for(var v=0;v<vs.length;v++){try{var rows=topRequest(tab,1,vs[v]);last=rows;if(!rows.length)continue;if(tab==='jinghua'){if(isAll||label==='全部'){if(essenceVerified(rows,c,label))return {rows:rows,via:v};continue;}var ea=qfEssenceAccept(rows,c,label);if(ea.length)return {rows:ea,via:v};continue;}if(tab==='dongtai'){if(isAll)return {rows:rows,via:v};var da=qfDynamicAccept(rows,c,label);if(da.length)return {rows:da,via:v};continue;}if(tab==='tongren'){if(isAll||label==='全部')return {rows:rows,via:v};var fa=fanAccept(rows,c,label);if(fa.length)return {rows:fa,via:v};continue;}if(feedFingerprint(rows)===feedFingerprint(INITIAL_ROWS.dongtai||[]))continue;if(isAll)return {rows:rows,via:v};var hit=localCategoryFilter(rows,c,true);if(hit.length)return {rows:hit,via:v};if(qfCandidateTrust(c)>=2)return {rows:rows,via:v};}catch(_e){}}return {rows:[],via:-1,last:last};}");
    h.push("function performCategory(chip,label,retry){retry=Number(retry||0);var tab=currentTab,key=cacheKey(tab,label);if(tab!=='tongren'&&feedCache[key]){renderFiltered(tab,feedCache[key],label);return;}if(label==='全部'&&currentSort==='6'&&INITIAL_ROWS[tab]&&INITIAL_ROWS[tab].length){feedCache[key]=INITIAL_ROWS[tab].slice(0);renderFiltered(tab,feedCache[key],label);return;}var cands=parseCandidateAttr(chip);if(!cands.length){renderFiltered(tab,[],label);return;}if(tab==='dongtai'&&label==='讨论'){var main=cands[0],preview=discussionPreview(main),rows=[],ok=[];try{rows=discussionSingle(main,0);ok=discussionAccept(rows,main);}catch(_d0){}if(ok.length){feedCache[key]=ok;renderFiltered(tab,ok,label);return;}try{rows=discussionSingle(main,1);ok=discussionAccept(rows,main);}catch(_d1){}if(ok.length){feedCache[key]=ok;renderFiltered(tab,ok,label);return;}if(preview.length<8){try{var p2=discussionAllPageFallback(main,2);if(p2.length)preview=mergeFeedRows(preview,p2);}catch(_p2){}}if(preview.length){feedCache[key]=preview;renderFiltered(tab,preview,label);return;}for(var di=1;di<cands.length;di++){var dg=requestCategory(tab,cands[di],false,label);if(dg.rows.length){feedCache[key]=dg.rows;renderFiltered(tab,dg.rows,label);return;}}renderFiltered(tab,[],label);return;}if(tab==='tongren'&&label!=='全部'){var mainFan=cands[0],seed=fanPreview(mainFan,label);if(seed.length){feedCache[key]=seed.slice(0);renderFiltered(tab,seed,label);}else showFilterBusy(tab,label);var direct=[],directCand=null,bestOne=[],bestOneCand=null;for(var qi=0;qi<cands.length;qi++){var qg=requestCategory(tab,cands[qi],false,label);if(!qg.rows.length)continue;if(qg.rows.length>=2){direct=qg.rows;directCand=cands[qi];break;}if(!bestOne.length){bestOne=qg.rows;bestOneCand=cands[qi];}}if(!direct.length&&bestOne.length){direct=bestOne;directCand=bestOneCand;}if(direct.length){seed=direct.slice(0);feedCache[key]=seed.slice(0);renderFiltered(tab,seed,label);fanDirectProgressive(chip,label,directCand,seed,label==='同人视频'?8:(label==='精华'?10:6));return;}var maxp=label==='同人视频'?10:(label==='精华'?12:7),target=label==='同人视频'?3:(label==='精华'?6:5);fanProgressive(chip,label,mainFan,seed,maxp,target);return;}for(var i=0;i<cands.length;i++){var got=requestCategory(tab,cands[i],label==='全部',label);if(got.rows.length){feedCache[key]=got.rows;renderFiltered(tab,got.rows,label);return;}}if(tab==='jinghua'&&label==='讨论'){var ix=qfEssenceDiscussionFallback();if(ix.length){feedCache[key]=ix;renderFiltered(tab,ix,label);return;}}if(tab==='jinghua'&&label!=='全部'){var fb=essenceLocalPages(cands[0],3);if(fb.length){feedCache[key]=fb;renderFiltered(tab,fb,label);return;}}renderFiltered(tab,[],label);}");
    h.push("function loadCategory(chip){var label=String(chip.getAttribute('data-name')||'全部'),key=cacheKey(currentTab,label);if(feedCache[key]){renderFiltered(currentTab,feedCache[key],label);if(currentTab==='tongren'&&label!=='全部'){var fc0=parseCandidateAttr(chip),fm0=fc0.length?fc0[0]:null,ds0=fanDirectState[key],st=fanScanState[key],resume0=(ds0&&ds0.cand)||fm0;if(resume0&&ds0&&!ds0.done){fanDirectProgressive(chip,label,resume0,feedCache[key],label==='同人视频'?8:(label==='精华'?10:6));}else if(fm0&&(!st||!st.done)){var maxp0=label==='同人视频'?10:(label==='精华'?12:7),target0=label==='同人视频'?3:(label==='精华'?6:5);fanProgressive(chip,label,fm0,feedCache[key],maxp0,target0);}}return;}if(currentTab==='dongtai'&&label==='讨论'){var cands=parseCandidateAttr(chip),main=cands.length?cands[0]:null,preview=main?discussionPreview(main):[];if(preview.length){renderFiltered(currentTab,preview,label);setTimeout(function(){if(currentTab==='dongtai'&&chip.classList.contains('active')&&!feedCache[key])performCategory(chip,label,0);},70);return;}}if(currentTab==='tongren'&&label!=='全部'){var fc=parseCandidateAttr(chip),fm=fc.length?fc[0]:null,fp=fm?fanPreview(fm,label):[];if(fp.length){renderFiltered(currentTab,fp,label);setTimeout(function(){if(currentTab==='tongren'&&chip.classList.contains('active'))performCategory(chip,label,0);},20);return;}}showFilterBusy(currentTab,label);setTimeout(function(){performCategory(chip,label,0);},12);}");
    h.push("var qfFeedPageState={},qfFeedScrollTimer=0;function qfActiveChip(){for(var i=0;i<chips.length;i++)if(chips[i].classList.contains('active')&&chipVisibleFor(chips[i],currentTab))return chips[i];return null;}function qfPageRows(tab,label,c,page){page=Math.max(2,Number(page)||2);var vs=(label==='全部')?[baseParams(tab,page)]:paramVariants(tab,c||{},page);for(var vi=0;vi<vs.length;vi++){var rows=[];try{rows=topRequest(tab,page,vs[vi])||[];}catch(_e){rows=[];}if(!rows.length)continue;if(label==='全部')return rows;if(tab==='tongren'){var fa=fanAccept(rows,c,label);if(fa.length)return fa;continue;}if(tab==='jinghua'){var ea=qfEssenceAccept(rows,c,label);if(ea.length)return ea;continue;}if(tab==='dongtai'){var da=qfDynamicAccept(rows,c,label);if(da.length)return da;continue;}var local=localCategoryFilter(rows,c,true);if(local.length)return local;if(qfCandidateTrust(c)>=2)return rows;}return [];}function qfNextFeed(){if(detail&&detail.style.display==='block')return;var chip=qfActiveChip();if(!chip)return;var label=String(chip.getAttribute('data-name')||'全部'),key=cacheKey(currentTab,label),st=qfFeedPageState[key]||{page:1,loading:false,done:false,empty:0};if(st.loading||st.done)return;var ds=fanDirectState[key],fs=fanScanState[key];if(currentTab==='tongren'&&label!=='全部'){st.page=Math.max(st.page,Number(ds&&ds.page||0),Number(fs&&fs.page||0));if((ds&&!ds.done)||(fs&&!fs.done)){qfFeedPageState[key]=st;return;}}st.loading=true;qfFeedPageState[key]=st;var list=paneList(currentTab),hint=document.createElement('div');hint.className='feedAuto loading';hint.textContent='正在加载下一页…';if(list)list.appendChild(hint);setTimeout(function(){try{var cands=parseCandidateAttr(chip),c=cands.length?cands[0]:{mode:'all',id:String((TOP_META[currentTab]||{}).id||'0')},pg=st.page+1,rows=qfPageRows(currentTab,label,c,pg),base=feedCache[key];if(!base||!base.length){if(label==='全部'&&INITIAL_ROWS[currentTab]&&INITIAL_ROWS[currentTab].length)base=INITIAL_ROWS[currentTab].slice(0);else base=[];}var merged=mergeFeedRows(base,rows);if(rows.length&&merged.length>base.length){st.page=pg;st.empty=0;feedCache[key]=merged.slice(0);renderFiltered(currentTab,merged,label);}else{st.empty++;if(st.empty>=2||!rows.length)st.done=true;}if(st.done&&list){var d=document.createElement('div');d.className='feedAuto done';d.textContent='已经到底了';list.appendChild(d);}}catch(_e){st.empty++;}st.loading=false;qfFeedPageState[key]=st;},30);}function qfNearBottom(){var de=document.documentElement,b=document.body,top=window.pageYOffset||de.scrollTop||b.scrollTop||0,h=window.innerHeight||de.clientHeight||0,sh=Math.max(de.scrollHeight||0,b.scrollHeight||0);return top+h>=sh-520;}function qfHeadCompact(){try{var hd=document.querySelector('.head'),y=window.pageYOffset||document.documentElement.scrollTop||0;if(hd){if(y>86)hd.classList.add('compact');else hd.classList.remove('compact');}}catch(_h){}}window.addEventListener('scroll',function(){qfHeadCompact();if(qfFeedScrollTimer)return;qfFeedScrollTimer=setTimeout(function(){qfFeedScrollTimer=0;if(qfNearBottom())qfNextFeed();},90);},{passive:true});qfHeadCompact();");
    h.push("var chips=document.querySelectorAll('.chip'),sortSel=document.getElementById('sortSel');function chipVisibleFor(chip,tab){var ts=String(chip.getAttribute('data-tabs')||'dongtai,jinghua');return ts.split(',').indexOf(tab)>=0;}function applyChipSet(tab){var first=null;for(var i=0;i<chips.length;i++){var ok=chipVisibleFor(chips[i],tab);chips[i].style.display=ok?'':'none';chips[i].classList.remove('active');if(ok&&!first)first=chips[i];}if(first)first.classList.add('active');}for(var ci=0;ci<chips.length;ci++){chips[ci].onclick=function(){if(!chipVisibleFor(this,currentTab)||this.classList.contains('active'))return;for(var j=0;j<chips.length;j++)chips[j].classList.remove('active');this.classList.add('active');loadCategory(this);};}sortSel.onchange=function(){currentSort=String(this.value||'6');var active=null;for(var i=0;i<chips.length;i++){if(chips[i].classList.contains('active')&&chipVisibleFor(chips[i],currentTab)){active=chips[i];break;}}if(active)loadCategory(active);};");
    h.push("var bs=document.querySelectorAll('.tab'),filterBar=document.getElementById('filterBar');for(var i=0;i<bs.length;i++){bs[i].onclick=function(){var k=this.getAttribute('data-tab');if(k===currentTab)return;currentTab=k;for(var a=0;a<bs.length;a++){if(bs[a]===this)bs[a].classList.add('active');else bs[a].classList.remove('active');}var ps=document.querySelectorAll('.pane');for(var p=0;p<ps.length;p++){if(ps[p].id==='pane_'+k)ps[p].classList.add('active');else ps[p].classList.remove('active');}filterBar.classList.add('show');applyChipSet(k);var first=null;for(var c=0;c<chips.length;c++){if(chips[c].classList.contains('active')&&chipVisibleFor(chips[c],k)){first=chips[c];break;}}if(first)loadCategory(first);};}applyChipSet('dongtai');");

    h.push("})();</script></body></html>");
    return h.join("");
}

var QF_CIRCLE_BOOT_CACHE_V352={};
function qfCircleBootGetV352(bid,maxAge){
    var x=QF_CIRCLE_BOOT_CACHE_V352[String(bid||"")];
    if(!x||!x.ts||Date.now()-Number(x.ts)>Number(maxAge||300000))return null;
    return x.data||null;
}
function qfCircleBootPutV352(bid,data){
    var k=String(bid||"");if(!k||!data)return data;
    QF_CIRCLE_BOOT_CACHE_V352[k]={ts:Date.now(),data:data};
    var ks=Object.keys(QF_CIRCLE_BOOT_CACHE_V352);
    if(ks.length>6){ks.sort(function(a,b){return Number(QF_CIRCLE_BOOT_CACHE_V352[a].ts||0)-Number(QF_CIRCLE_BOOT_CACHE_V352[b].ts||0);});while(ks.length>6)delete QF_CIRCLE_BOOT_CACHE_V352[ks.shift()];}
    return data;
}

function qfCircleApiProbe2970(j,bid){
    var circleId="",posts=[];
    var tabs={dongtai:[],jinghua:[],tongren:[],discussion:[],discussionPreview:[]};
    var totals={dongtai:0,jinghua:0,tongren:0};
    var categoryMode={jinghua:"按需加载",tongren:"按需加载"};
    var categoryMeta=qfCircleCategoryMeta2984("");

    /*
     * v2.9.91：同一本书的 getcircledetail 偶尔会只返回简化分类表，
     * 此时“讨论”只剩短 PostCategoryId=2，而缺少真正可用的长 JsId。
     * 之前因此表现为：同一个讨论分类有时有帖、有时为空。
     * 这里对分类元数据做质量评分，只保留信息更完整的一份；缺长 JsId 时
     * 再用已经拿到的 CircleId 补请求一次详情，不影响其它已正确分类。
     */
    function metaScore(m){
        var score=0,ds=(m&&m.filterSets&&m.filterSets.dongtai)||[];
        score+=ds.length*4;
        for(var i=0;i<ds.length;i++){
            var x=ds[i]||{},nm=String(x.name||"");
            if(nm==="讨论"){
                var cs=Array.isArray(x.candidates)?x.candidates:[];
                for(var c=0;c<cs.length;c++){
                    var z=cs[c]||{},id=String(z.id||"");
                    if((z.mode==="sub"||z.mode==="subId")&&/^\d{8,22}$/.test(id))score+=120;
                    else if(z.mode==="post"&&id==="2")score+=8;
                }
            }
            if(nm==="其他")score+=3;
            if(nm==="作家说"||nm==="作者说"||nm==="版权信息")score+=2;
        }
        return score;
    }
    function hasStableDiscussion(m){
        var ds=(m&&m.filterSets&&m.filterSets.dongtai)||[];
        for(var i=0;i<ds.length;i++){
            var x=ds[i]||{};if(String(x.name||"")!=="讨论")continue;
            var cs=Array.isArray(x.candidates)?x.candidates:[];
            for(var c=0;c<cs.length;c++){
                var z=cs[c]||{},id=String(z.id||"");
                if((z.mode==="sub"||z.mode==="subId")&&/^\d{8,22}$/.test(id))return true;
            }
        }
        return false;
    }
    function absorbMeta(raw){
        try{
            var m=qfCircleCategoryMeta2984(raw);
            if(metaScore(m)>metaScore(categoryMeta))categoryMeta=m;
        }catch(_m){}
    }
    function detailOnce(params){
        var t=qfCircleApiCall2970(j,"v1/circle/getcircledetail",params);
        if(t&&t.sum&&t.sum.ids)circleId=String(t.sum.ids.circleId||circleId||"");
        absorbMeta(t&&t.raw?t.raw:"");
        if(!circleId&&t&&t.sum&&t.sum.posts){
            for(var i=0;i<t.sum.posts.length;i++)if(t.sum.posts[i]&&t.sum.posts[i].circleId){circleId=String(t.sum.posts[i].circleId);break;}
        }
        return t;
    }

    detailOnce({bookId:String(bid),bookType:"1"});
    if(!circleId)detailOnce({circleId:"0",bookId:String(bid),bookType:"1"});
    /* beta5.6：不再为“长讨论 JsId”额外串行补拉详情。
       beta5.4 起动态讨论已经有官方 PostCategoryId=2 短 ID 兜底，
       保留当前首次详情返回的分类表即可，减少首开一次网络往返。 */

    var cid=String(circleId||"0");
    function listVariant(variant){
        var p;
        if(variant===1){
            p={pageIndex:"1",subCategoryId:"0",circleId:cid,sortType:"6",postCategoryId:"0",bookId:String(bid),bookType:"1"};
        }else if(variant===2){
            p={pageIndex:"1",subCategory:"0",circleId:cid,postSortType:"6",postCategoryId:"0",qdBookId:String(bid),qdBookType:"1"};
        }else{
            p={pageIndex:"1",subCategory:"0",circleId:cid,sortType:"6",postCategoryId:"0",bookId:String(bid),bookType:"1"};
        }
        return qfCircleApiCall2970(j,"v1/circle/getcirclepostlist",p);
    }

    var dyn=null;
    for(var v=0;v<3;v++){
        var t=listVariant(v),rows=t&&t.sum&&t.sum.posts?t.sum.posts:[];
        if(rows.length){dyn=t;break;}
    }
    if(dyn){
        tabs.dongtai=dyn.sum.posts||[];
        totals.dongtai=Number(dyn.sum.total||tabs.dongtai.length)||tabs.dongtai.length;
        posts=tabs.dongtai.slice(0);
    }

    /*
     * v2.9.93：讨论不再在打开书友圈前额外发“预热请求”。
     * 之前这次网络请求既拖慢首开，也会碰到起点偶发忽略 subCategory 的情况。
     * 现在直接从已经成功拿到的“动态全部”首屏里，依据帖子自身分类字段筛出
     * 可确认属于“讨论”的帖子作为零网络预览。用户点击讨论时先秒显这批正确帖子，
     * 再由 WebView 只做少量网络刷新；即使服务端本次仍异常，也不会再把页面刷成空白。
     */
    try{
        var discussionIds=[],ds=(categoryMeta&&categoryMeta.filterSets&&categoryMeta.filterSets.dongtai)||[];
        for(var di=0;di<ds.length;di++){
            var df=ds[di]||{};if(String(df.name||"")!=="讨论")continue;
            var dcs=Array.isArray(df.candidates)?df.candidates:[];
            for(var dc=0;dc<dcs.length;dc++){
                var dco=dcs[dc]||{},a=[String(dco.id||""),String(dco.altId||"")];
                for(var ai=0;ai<a.length;ai++)if(a[ai]&&discussionIds.indexOf(a[ai])<0)discussionIds.push(a[ai]);
            }
        }
        if(discussionIds.indexOf("2")<0)discussionIds.push("2");
        var preview=[];
        for(var pi=0;pi<(tabs.dongtai||[]).length;pi++){
            var po=tabs.dongtai[pi]||{};
            var vals=[String(po.postCategoryId||po.PostCategoryId||""),String(po.categoryId||po.CategoryId||""),String(po.subCategoryId||po.SubCategoryId||po.subCategory||po.SubCategory||"")];
            var hit=false;
            for(var vi=0;vi<vals.length&&!hit;vi++)if(vals[vi]&&discussionIds.indexOf(vals[vi])>=0)hit=true;
            if(hit)preview.push(po);
        }
        tabs.discussionPreview=preview;
    }catch(_discussionPreview){}

    return {tests:[],circleId:circleId,posts:posts,tabs:tabs,totals:totals,categoryMode:categoryMode,categoryMeta:categoryMeta};
}

/* ============================================================
 * v4.0.0-alpha7 · Circle Data/Renderer ABI
 * Probe/分类/帖子解析保持原算法；Data 层只负责获得书友圈数据，Renderer 只负责页面。
 * ============================================================ */
function qfCircleData(bookObj){
    var j=null;try{j=this&&this.java?this.java:null;}catch(_j0){}try{if(!j&&typeof java!=='undefined')j=java;}catch(_j1){}
    if(!j)return {ok:false,bookId:'',bookName:'',message:'java unavailable',tests:[],circleId:'',posts:[],tabs:{dongtai:[],jinghua:[],tongren:[]},totals:{dongtai:0,jinghua:0,tongren:0},categoryMode:{},categoryMeta:qfCircleCategoryMeta2984(''),source:'qidian-circle-api',schema:'qf.circle-set/1',contractVersion:1};
    var b=bookObj||null;
    try{if(!b&&typeof book!=='undefined')b=book;}catch(_b0){}
    try{if(!b&&this&&this.book)b=this.book;}catch(_b1){}
    try{if(!b)b=qfBook(this);}catch(_b2){}
    var bid='';try{if(b&&b.getVariable)bid=String(b.getVariable('qf_bid')||'');}catch(_id0){}
    if(!bid){try{bid=String(qfRoleBookIdV12(b)||'');}catch(_id1){}}
    var bookName=qfCircleBookName2964(b);
    if(!bid)return {ok:false,bookId:'',bookName:bookName,message:'未识别到起点 BookId',tests:[],circleId:'',posts:[],tabs:{dongtai:[],jinghua:[],tongren:[]},totals:{dongtai:0,jinghua:0,tongren:0},categoryMode:{},categoryMeta:qfCircleCategoryMeta2984(''),source:'qidian-circle-api',schema:'qf.circle-set/1',contractVersion:1};
    var result={tests:[],circleId:'',posts:[],tabs:{dongtai:[],jinghua:[],tongren:[]},totals:{dongtai:0,jinghua:0,tongren:0},categoryMode:{jinghua:'',tongren:''},categoryMeta:qfCircleCategoryMeta2984('')};
    try{
        var cached=qfCircleBootGetV352(bid,300000);
        if(cached)result=cached;else{result=qfCircleApiProbe2970(j,bid);qfCircleBootPutV352(bid,result);}
    }catch(e){
        result.tests=result.tests||[];result.tests.push({path:'probe-error',params:{bookId:bid},raw:String(e),sum:{len:0,code:'',msg:String(e),topKeys:'',dataKeys:'',ids:{circleId:'',postId:'',topicId:''},posts:[]}});
        result.message=String(e&&e.message||e);
    }
    /* alpha8.1.1：保留 alpha7.1.1 已证明的完整 result ABI。
       不重建 tabs/totals/posts，不删除任何动态子分类或帖子扩展字段；
       Canonical Contract 只做“增量标注 + 缺省补齐”，允许扩展字段继续存在。 */
    result=result&&typeof result==='object'?result:{};
    result.ok=true;
    result.bookId=String(bid);
    result.bookName=String(bookName||'');
    result.source='qidian-circle-api';
    result.schema='qf.circle-set/1';
    result.contractVersion=1;
    result.posts=Array.isArray(result.posts)?result.posts:[];
    result.tests=Array.isArray(result.tests)?result.tests:[];
    result.tabs=result.tabs&&typeof result.tabs==='object'?result.tabs:{};
    if(!Array.isArray(result.tabs.dongtai))result.tabs.dongtai=[];
    if(!Array.isArray(result.tabs.jinghua))result.tabs.jinghua=[];
    if(!Array.isArray(result.tabs.tongren))result.tabs.tongren=[];
    result.totals=result.totals&&typeof result.totals==='object'?result.totals:{};
    if(result.totals.dongtai===undefined)result.totals.dongtai=0;
    if(result.totals.jinghua===undefined)result.totals.jinghua=0;
    if(result.totals.tongren===undefined)result.totals.tongren=0;
    result.categoryMode=result.categoryMode&&typeof result.categoryMode==='object'?result.categoryMode:{};
    result.categoryMeta=result.categoryMeta&&typeof result.categoryMeta==='object'?result.categoryMeta:qfCircleCategoryMeta2984('');
    return result;
}
function qfCircleView(model){
    model=model&&typeof model==='object'?model:{};
    var legacy=model.legacy&&typeof model.legacy==='object'?model.legacy:model;
    var bid=String(model.bookId||legacy.bookId||''),bookName=String(model.bookName||legacy.bookName||'');
    if(!bid)return {ok:false,html:'',target:'',pre:'',config:{},message:'BookId为空'};
    var html=qfCircleApiHtml2970(bookName,bid,legacy.tests||[],String(model.circleId||legacy.circleId||''),legacy.posts||[],legacy.tabs||{},legacy.totals||{},legacy.categoryMode||{},legacy.categoryMeta||{});
    var cfg={heightPercentage:0.94,expandedCornersRadius:22,state:3,skipCollapsed:true,isDraggable:false,isDraggableOnNestedScroll:false,scrollNoDraggable:true,dismissOnTouchOutside:true,shouldDimBackground:true,backgroundDimAmount:0.46,hardwareAccelerated:true,isNestedScrollingEnabled:true,isHideable:true};
    var pre="try{window.java=java;"+
        "function _qfCircleExpand(){try{java.upConfig(JSON.stringify({heightPercentage:0.94,state:3,skipCollapsed:true,isDraggable:false,isDraggableOnNestedScroll:false,scrollNoDraggable:true}));}catch(e){}}"+
        "_qfCircleExpand();setTimeout(_qfCircleExpand,60);setTimeout(_qfCircleExpand,180);setTimeout(_qfCircleExpand,420);setTimeout(_qfCircleExpand,900);"+
        "if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',function(){_qfCircleExpand();setTimeout(_qfCircleExpand,120);setTimeout(_qfCircleExpand,360);});}"+
        "}catch(e){}";
    return {ok:!!html,html:String(html||''),target:'https://local.qidian.circle.api/'+encodeURIComponent(bid),pre:pre,config:cfg,message:html?'':'书友圈页面为空'};
}

function qfOpenQidianCircleV2961(){
    var j=null;
    try{j=this&&this.java?this.java:null;}catch(e0){}
    try{if(!j&&typeof java!=="undefined")j=java;}catch(e1){}
    if(!j)return true;

    var b=null;
    try{if(typeof book!=="undefined")b=book;}catch(e2){}
    try{if(!b&&this&&this.book)b=this.book;}catch(e3){}
    try{if(!b)b=qfBook(this);}catch(e4){}

    var bid="";
    try{if(b&&b.getVariable)bid=String(b.getVariable("qf_bid")||"");}catch(e5){}
    if(!bid){try{bid=String(qfRoleBookIdV12(b)||"");}catch(e6){}}

    if(!bid){
        try{j.longToast("未识别到起点 BookId");}catch(_e){}
        return true;
    }

    var bookName=qfCircleBookName2964(b);
    try{j.toast("正在打开书友圈…");}catch(_t){}

    var result={
        tests:[],
        circleId:"",
        posts:[],
        tabs:{dongtai:[],jinghua:[],tongren:[]},
        totals:{dongtai:0,jinghua:0,tongren:0},
        categoryMode:{jinghua:"",tongren:""},
        categoryMeta:qfCircleCategoryMeta2984("")
    };
    try{
        var cachedBoot=qfCircleBootGetV352(bid,300000);
        if(cachedBoot){
            result=cachedBoot;
        }else{
            result=qfCircleApiProbe2970(j,bid);
            qfCircleBootPutV352(bid,result);
        }
    }catch(e7){
        result.tests.push({
            path:"probe-error",
            params:{bookId:bid},
            raw:String(e7),
            sum:{
                len:0,code:"",msg:String(e7),
                topKeys:"",dataKeys:"",
                ids:{circleId:"",postId:"",topicId:""},
                posts:[]
            }
        });
    }

    var html=qfCircleApiHtml2970(
        bookName,bid,
        result.tests||[],
        result.circleId||"",
        result.posts||[],
        result.tabs||{},
        result.totals||{},
        result.categoryMode||{},
        result.categoryMeta||{}
    );

    var cfg={
        heightPercentage:0.94,
        expandedCornersRadius:22,
        state:3,
        skipCollapsed:true,
        isDraggable:false,
        isDraggableOnNestedScroll:false,
        scrollNoDraggable:true,
        dismissOnTouchOutside:true,
        shouldDimBackground:true,
        backgroundDimAmount:0.46,
        hardwareAccelerated:true,
        isNestedScrollingEnabled:true,
        isHideable:true
    };
    /* beta7.3：首次打开时 WebView 尚未完成布局，部分阅读版本会先按内容高度创建较矮 BottomSheet。
       在 pre/DOMContentLoaded 后重复锚定 94% expanded，缓存与非缓存首开行为保持一致。 */
    var pre=
        "try{window.java=java;"+
        "function _qfCircleExpand(){try{java.upConfig(JSON.stringify({heightPercentage:0.94,state:3,skipCollapsed:true,isDraggable:false,isDraggableOnNestedScroll:false,scrollNoDraggable:true}));}catch(e){}}"+
        "_qfCircleExpand();setTimeout(_qfCircleExpand,60);setTimeout(_qfCircleExpand,180);setTimeout(_qfCircleExpand,420);setTimeout(_qfCircleExpand,900);"+
        "if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',function(){_qfCircleExpand();setTimeout(_qfCircleExpand,120);setTimeout(_qfCircleExpand,360);});}"+
        "}catch(e){}";

    try{
        j.showBrowser(
            "https://local.qidian.circle.api/"+encodeURIComponent(bid),
            html,
            pre,
            JSON.stringify(cfg)
        );
        return true;
    }catch(e8){}

    try{j.longToast("起点书友圈 API 页面打开失败："+String(e8));}catch(e9){}
    return true;
}



function qfCircleDataV430(){return qfCircleData.apply(this,arguments);}

function qfCircleViewV430(){return qfCircleView.apply(this,arguments);}
