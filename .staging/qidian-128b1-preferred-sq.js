/* alpha81 shared import */
var __qfPc81=QF_MOD38_CACHE["provider_common"]||qfModuleEnsureV38.call(this,"provider_common");
var qfChapterHintTryV56=__qfPc81.qfChapterHintTryV56;
var qfChapterHintPutV56=__qfPc81.qfChapterHintPutV56;
var qfChapterWindowTryV310=__qfPc81.qfChapterWindowTryV310;
var qfChapterWindowPutV310=__qfPc81.qfChapterWindowPutV310;
var qfNameVariantsV10=__qfPc81.qfNameVariantsV10;

/* =========================
 * 书旗 Provider · alpha49 Token隔离修复
 * API 搜索仍为主链；若旧搜索接口只返回同名衍生书，追加书旗官网 SSR 搜索兜底。
 * 官网结果直接提取 /book/{bookId}.html，并用书名+作者二次确认；只在首次绑定时运行。
 * ========================= */
function qfSqSortedV44(str){var obj={},arr=String(str||"").split("&");for(var i=0;i<arr.length;i++){var p=arr[i].indexOf("=");if(p<0)continue;obj[arr[i].slice(0,p)]=arr[i].slice(p+1);}var keys=Object.keys(obj).sort();if(/platform=0/.test(str))return keys.map(function(k){return k+"="+obj[k];}).join("&");return keys.map(function(k){return obj[k];}).join("");}
function qfSqUserIdV45(){try{var v=String(source.getVariable()||""),o=JSON.parse(v||"[]"),u=o&&o[0]&&o[0].uid&&o[0].uid[0]&&o[0].uid[0].userId;if(/^\d+$/.test(String(u||"")))return String(u);}catch(e0){}return "12345678";}
function qfSqTokenCleanV47(v){return String(v||"").replace(/^[\s"'{}[\]]+|[\s"'{}[\]]+$/g,"").trim();}
function qfSqTokenV47(force){
    var now=Date.now(),cached="",ts=0;
    if(!force)try{
        cached=qfSqTokenCleanV47(source.get("qf_sq_token_v47")||"");
        ts=Number(source.get("qf_sq_token_ts_v47")||0)||0;
    }catch(e0){}
    if(cached&&now-ts<600000)return cached;

    var j=qfJava(this),token="",resp=null,rawCookie="",old="";
    function pick(v){
        var s=String(v||""),m=s.match(/shuqi_token=([^,;\s]+)/);
        if(m&&m[1])return qfSqTokenCleanV47(m[1]);
        return "";
    }

    /* alpha49：聚合源最大的差异是 source.loginHeader 可能正在保存情无/其它源认证头。
       独立书旗源取 token 时 loginHeader 为空，因此取 token 的短窗口先清空，完成后立即恢复。 */
    try{old=qfSqOldLoginHeaderV47.call(this);}catch(_o){old="";}
    try{
        try{source.putLoginHeader("");}catch(_c0){}

        /* 先复用 t.shuqi.com 自己已经存在的 cookie。 */
        if(!force)try{
            rawCookie=String(cookie.getCookie("https://t.shuqi.com/")||cookie.getCookie("https://t.shuqi.com")||"");
            token=pick(rawCookie);
        }catch(_ck0){}

        /* 强制刷新时先清掉旧 token cookie，行为更接近独立源首次访问。 */
        if(force)try{cookie.removeCookie("https://t.shuqi.com");}catch(_rm){}

        if(!token){
            try{
                resp=j.get("https://t.shuqi.com",qfSqBaseHeadersV47());
                try{
                    rawCookie=String(resp.cookies().toString()||"");
                    token=pick(rawCookie);
                }catch(_r1){}
                if(!token)try{
                    var hs=resp.headers("Set-Cookie");
                    if(hs)for(var i=0;i<hs.size();i++){
                        token=pick(String(hs.get(i)||""));
                        if(token)break;
                    }
                }catch(_r2){}
            }catch(_g){}
        }

        /* 某些轻阅读/WebView 版本普通 HTTP 不回传 shuqi_token。
           仅 token 缺失时启动一次隐藏 WebView，让书旗页面自行写 cookie；正常翻章不会进入。 */
        if(!token)try{
            var dc=String(j.webView(null,"https://t.shuqi.com/","document.cookie")||"");
            token=pick(dc);
            if(!token){
                rawCookie=String(cookie.getCookie("https://t.shuqi.com/")||cookie.getCookie("https://t.shuqi.com")||"");
                token=pick(rawCookie);
            }
        }catch(_wv){}
    }finally{
        try{qfSqRestoreLoginHeaderV47(old);}catch(_rs){}
    }

    if(token){
        try{
            source.put("qf_sq_token_v47",token);
            source.put("qf_sq_token_ts_v47",String(now));
            source.put("qf_sq_token_diag_v48","ok-v49");
        }catch(e6){}
    }else{
        try{source.put("qf_sq_token_diag_v48","v49 cookie="+String(rawCookie||"").slice(0,180));}catch(_dg){}
    }
    return token;
}
function qfSqBearerV44(){var t=qfSqTokenV47.call(this,false);return t?"Bearer "+t:"";}
function qfSqBaseHeadersV47(){
    return {"accept":"application/json, text/plain, */*","user-agent":"Mozilla/5.0 (Linux; Android 9; Pixel 4 Build/PQ3A.190801.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.117 Mobile Safari/537.36","content-type":"application/x-www-form-urlencoded","origin":"https://t.shuqi.com","x-requested-with":"mark.via.gp","sec-fetch-site":"cross-site","sec-fetch-mode":"cors","sec-fetch-dest":"empty","accept-language":"zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7","Referer":"https://t.shuqi.com/"};
}
function qfSqBuildV47(path,params,host){
    var j=qfJava(this),userId=qfSqUserIdV45.call(this),now=Math.floor(Date.now()/1000),body="",sign="";
    host=host||"https://ocean.shuqireader.com";
    var p0="sqSv=1.0",p1="user_id="+userId+"&timestamp="+now;
    if(/info/.test(path)){
        var p=p1+"&"+params;
        sign=j.md5Encode(qfSqSortedV44(p)+"37e81a9d8f02596e1b895d07c171d5c9");
        body=p+"&platform=0&needFreeStack=1&sign="+sign;
    }else{
        var q=p0+"&"+p1+"&platform=0&"+params;
        sign=j.md5Encode(qfSqSortedV44(q)+"&skey=eefc4798f28ea41622487ad80ef7e81c");
        body=q+"&key=sq_h5_gateway&sign="+sign;
    }
    return {url:host+path,body:body};
}
function qfSqOldLoginHeaderV47(){try{return String(source.getLoginHeader?source.getLoginHeader():""||"");}catch(e0){return "";}}
function qfSqRestoreLoginHeaderV47(old){try{source.putLoginHeader(String(old||""));}catch(e0){}}
function qfSqGatewayBadV47(raw){return /Api\s*Gateway\s*Auth\s*ERROR|auth(?:entication)?\s*(?:error|fail)|unauthorized/i.test(String(raw||""));}
function qfSqApiV47(path,params,host){
    var j=qfJava(this),last="",authMode="";
    for(var attempt=0;attempt<2;attempt++){
        var token=qfSqTokenV47.call(this,attempt>0);
        if(!token){
            var dg="";try{dg=String(source.get("qf_sq_token_diag_v48")||"");}catch(_d){}
            last="shuqi_token 获取失败"+(dg?"｜"+dg:"");
            continue;
        }
        var req=qfSqBuildV47.call(this,path,params,host),bearer="Bearer "+token,old=qfSqOldLoginHeaderV47.call(this),raw="";
        /* 第一条：完全按独立书旗源 GetUrl() 的关键行为。
           LoginHeader 负责 authorization，URL options 只给 body/method。 */
        try{
            source.putLoginHeader(JSON.stringify({authorization:bearer}));
            raw=String(j.ajax(req.url+","+JSON.stringify({body:req.body,method:"POST"}))||"");
            authMode="native";
        }catch(e0){last=String(e0&&e0.message||e0);}
        finally{qfSqRestoreLoginHeaderV47(old);}
        if(raw&&!qfSqGatewayBadV47(raw))return {raw:raw,mode:authMode,token:token};
        if(raw)last=raw;

        /* 第二条：聚合源全局 Header 与书旗独立源不同，显式补齐原书旗 Header + authorization。 */
        try{
            var headers=qfSqBaseHeadersV47();
            headers.authorization=bearer;
            var r=j.post(req.url,req.body,headers,18000);
            raw=String(r&&r.body?r.body():"");
            authMode="direct";
        }catch(e1){
            try{
                var h2=qfSqBaseHeadersV47();h2.authorization=bearer;
                raw=String(j.ajax(req.url+","+JSON.stringify({method:"POST",body:req.body,headers:h2,timeout:18000}))||"");
                authMode="ajaxHeader";
            }catch(e2){last=String(e2&&e2.message||e2);}
        }
        if(raw&&!qfSqGatewayBadV47(raw))return {raw:raw,mode:authMode,token:token};
        if(raw)last=raw;
        try{
            source.put("qf_sq_token_v47","");
            source.put("qf_sq_token_ts_v47","0");
        }catch(_c){}
    }
    return {raw:String(last||""),mode:authMode,token:""};
}
function qfSqSignedUrlV44(path,params,host){
    var req=qfSqBuildV47.call(this,path,params,host),h=qfSqBaseHeadersV47(),b=qfSqBearerV44.call(this);if(b)h.authorization=b;
    return req.url+","+JSON.stringify({body:req.body,method:"POST",headers:h});
}
function qfSqDecodeV44(enc){function p(e){return String(e||"").split("").map(function(ch){if(!/[A-Za-z]/.test(ch))return ch;var c=Math.floor(ch.charCodeAt(0)/97),k=(ch.toLowerCase().charCodeAt(0)-83)%26||26;return String.fromCharCode(k+(c===0?64:96));}).join("");}try{return String(qfJava(this).base64Decode(p(enc))||"");}catch(e0){return "";}}
function qfSqBookIdV44(x){return String(x&&(x.bookId||x.bid||x.book_id)||"");}
function qfSqBookNameV44(x){return qfText(x&&(x.bookName||x.book_name||x.title||x.name||x.resourceName)||"");}
function qfSqBookAuthorV44(x){return qfText(x&&(x.authorName||x.author_name||x.author||x.writerName||x.writer)||"");}
function qfSqSearchHeadersV46(){return {"accept":"application/json, text/plain, */*","user-agent":"Mozilla/5.0 (Linux; Android 9; Pixel 4 Build/PQ3A.190801.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.117 Mobile Safari/537.36","content-type":"application/x-www-form-urlencoded","origin":"https://t.shuqi.com","x-requested-with":"mark.via.gp","accept-language":"zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7","Referer":"https://t.shuqi.com/"};}
function qfSqSearchOneV44(name,page,size){var j=qfJava(this),u="https://read.xiaoshuo1-sm.com/novel/i.php?do=is_search&isNewBind=0&platform=3&user_id=8000000&q="+encodeURIComponent(name)+"&page="+Number(page||1)+"&size="+Number(size||10)+"&uid=8000000&filterMigu=1&ver=&p=3&timestamp="+Math.floor(Date.now()/1000),root=[];try{root=qfJson(j.ajax(u+","+JSON.stringify({headers:qfSqSearchHeadersV46(),timeout:7000})),[]);}catch(e0){return [];}if(Array.isArray(root))return root;if(root&&Array.isArray(root.data))return root.data;if(root&&root.data&&Array.isArray(root.data.books))return root.data.books;if(root&&Array.isArray(root.books))return root.books;return [];}
function qfSqWebSearchV46(name,author){var j=qfJava(this),queries=[],out=[],seen={};function aq(v){v=qfText(v);if(v&&queries.indexOf(v)<0)queries.push(v);}aq(name);if(author){aq(name+" "+author);aq(author);}for(var qi=0;qi<queries.length;qi++){var url="https://www.shuqi.com/search?keyword="+encodeURIComponent(queries[qi])+"&page=1",raw="";try{raw=String(j.ajax(url+","+JSON.stringify({headers:{"User-Agent":"Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/124 Mobile Safari/537.36","Referer":"https://www.shuqi.com/"},timeout:7000}))||"");}catch(e0){continue;}var doc=null;try{doc=Packages.org.jsoup.Jsoup.parse(raw,url);}catch(e1){continue;}var as=doc.select('a[href*="/book/"]');for(var i=0;i<as.size();i++){var a=as.get(i),href=String(a.attr("href")||""),m=href.match(/\/book\/(\d+)(?:\.html)?/i);if(!m)continue;var id=String(m[1]),title=qfText(a.text()||"");if(!title)continue;var block=a,txt="";try{for(var up=0;up<5&&block;up++){txt=qfText(block.text()||"");if((author&&txt.indexOf(author)>=0)||txt.length>title.length+8)break;block=block.parent();}}catch(_p){}var au="";if(author&&txt.indexOf(author)>=0)au=author;else{var mm=txt.match(/作者[：:]?\s*([^\s|丨·]{2,20})/);if(mm)au=mm[1];}if(!seen[id]){seen[id]=1;out.push({bookId:id,bookName:title,authorName:au,_web:1});}}if(out.length)break;}return out;}
function qfSqSearchV44(name,author){
    var vars=qfNameVariantsV10(name),out=[],seen={};
    function add(arr){arr=qdList(arr);for(var i=0;i<arr.length;i++){var x=arr[i]||{},id=qfSqBookIdV44(x);if(!id||seen[id])continue;seen[id]=1;out.push(x);}}
    for(var v=0;v<vars.length;v++){
        for(var p=1;p<=5;p++){
            try{add(qfSqSearchOneV44.call(this,vars[v],p,20));}catch(e0){}
            if(qfSqPickBookV44(out,name,author))return out;
        }
    }
    try{add(qfSqWebSearchV46.call(this,name,author));}catch(e1){}
    return out;
}
function qfSqNormAuthorV44(s){return qfNorm(s).replace(/^(?:作者|作家|原著|作者名)/g,"").replace(/(?:作者|著|所著|作品)$/g,"").trim();}
function qfSqTitleVariantsV48(name){
    var arr=[],seen={};
    function add(v){v=qfNorm(v);if(v&&!seen[v]){seen[v]=1;arr.push(v);}}
    add(name);
    try{var vs=qfNameVariantsV10(name)||[];for(var i=0;i<vs.length;i++)add(vs[i]);}catch(_e){}
    return arr;
}
function qfSqTitleExactV48(candidate,target){
    var c=qfNorm(candidate),vs=qfSqTitleVariantsV48(target);
    if(!c||!vs.length)return false;
    for(var i=0;i<vs.length;i++)if(c===vs[i])return true;
    return false;
}
function qfSqAuthorExactV48(candidate,target){
    var c=qfSqNormAuthorV44(candidate),t=qfSqNormAuthorV44(target);
    return !!(c&&t&&c===t);
}
function qfSqBookStrictV48(x,name,author){
    return !!(x&&qfSqBookIdV44(x)&&qfSqTitleExactV48(qfSqBookNameV44(x),name)&&qfSqAuthorExactV48(qfSqBookAuthorV44(x),author));
}
function qfSqBindValidV48(bind,meta){
    meta=meta||{};bind=bind||{};
    return !!(bind.id&&qfSqTitleExactV48(bind.name,meta.bookName)&&qfSqAuthorExactV48(bind.author,meta.author));
}
function qfSqPickBookV44(items,name,author){
    items=qdList(items);
    var best=null,bestScore=-1,target=qfNorm(name);
    for(var i=0;i<items.length;i++){
        var v=items[i]||{};
        if(!qfSqBookStrictV48(v,name,author))continue;
        var score=(qfNorm(qfSqBookNameV44(v))===target?200:120)+(v._web?5:0);
        if(score>bestScore){bestScore=score;best=v;}
    }
    return best;
}
function qfSqChapterBodyV44(title){var s=qfText(title).replace(/^\s*\[?\d+\]?\s*[.、:：\-]?\s*/,"").replace(/\s+/g," ").trim();s=s.replace(/^第\s*[0-9零〇○一二两三四五六七八九十百千万]+\s*[章节回卷]\s*/i,"").replace(/^chapter\s*\d+\s*[:：.\-—]?\s*/i,"").replace(/^[\s:：、.\-—]+/,"");return qfNormChapter(s);}
function qfSqChapterCompatibleV48(x,meta){
    if(!x)return false;meta=meta||{};
    var title=String(x.chapterName||""),target=String(meta.title||""),n=qfNormChapter(title),tn=qfNormChapter(target),b=qfSqChapterBodyV44(title),tb=qfSqChapterBodyV44(target),no=qfChapterNoV10(title),tno=qfChapterNoV10(target);
    if(tno>=0&&no>=0&&no!==tno)return false;
    if(n&&tn&&n===tn)return true;
    if(b&&tb&&b===tb)return true;
    if(b&&tb&&Math.min(b.length,tb.length)>=6&&(b.indexOf(tb)>=0||tb.indexOf(b)>=0))return true;
    return false;
}
function qfSqPickChapterV44(list,meta,bindId){
    list=qdList(list);if(!list.length)return null;meta=meta||{};
    var tag="书旗#"+String(bindId||"strict-v48"),fast=qfChapterHintTryV56(tag,meta,list,"chapterName",true);
    if(fast&&qfSqChapterCompatibleV48(fast,meta))return fast;
    var target=String(meta.title||""),tn=qfNormChapter(target),tb=qfSqChapterBodyV44(target),tno=qfChapterNoV10(target),idx=Number(meta.index),best=null,bestScore=-99999;
    for(var i=0;i<list.length;i++){
        var x=list[i]||{},title=String(x.chapterName||""),n=qfNormChapter(title),b=qfSqChapterBodyV44(title),no=qfChapterNoV10(title),score=-99999;
        if(tno>=0&&no>=0&&no!==tno)continue;
        if(n&&tn&&n===tn)score=2500;
        else if(b&&tb&&b===tb)score=2250;
        else if(b&&tb&&Math.min(b.length,tb.length)>=6&&(b.indexOf(tb)>=0||tb.indexOf(b)>=0))score=1550;
        if(score<0)continue;
        if(tno>=0&&no>=0&&no===tno)score+=520;
        if(idx>=0){var d=Math.abs(i-idx);if(d===0)score+=100;else if(d<=4)score+=50-d*8;}
        if(score>bestScore){bestScore=score;best=x;}
    }
    if(bestScore>=1500){qfChapterHintPutV56(tag,meta,list,best);return best;}
    return null;
}
function qfSqDiagV45(root,raw,bookId){var a=[];try{if(root&&root.code!==undefined)a.push("code="+root.code);if(root&&root.message)a.push(String(root.message));else if(root&&root.msg)a.push(String(root.msg));var d=root&&root.data;if(d&&typeof d==="object"&&!Array.isArray(d))a.push("data="+Object.keys(d).slice(0,8).join(","));}catch(e0){}if(!a.length&&raw)a.push("响应="+String(raw).replace(/\s+/g," ").slice(0,120));return "bookId="+String(bookId||"")+(a.length?"｜"+a.join("｜"):"");}
function qfSqCatalogV44(bookId,force){
    var key="qf_v47_toc_sq_"+String(bookId),cached=!force?qfCacheGet.call(this,key):null;
    if(cached&&cached.ts&&Date.now()-Number(cached.ts)<21600000&&Array.isArray(cached.list)&&cached.list.length)return cached;
    var ap=qfSqApiV47.call(this,"/webapi/bcspub/openapi/book/chapterlist","bookId="+encodeURIComponent(bookId),"https://ocean.shuqireader.com");
    var raw=String(ap.raw||""),toc=qfJson(raw,{}),d=(toc&&toc.data)||{},vols=Array.isArray(d.chapterList)?d.chapterList:[],flat=[];
    for(var i=0;i<vols.length;i++){var vl=vols[i]&&vols[i].volumeList||[];for(var k=0;k<vl.length;k++)flat.push(vl[k]);}
    var diag=qfSqDiagV45(toc,raw,bookId);
    if(ap.mode)diag+="｜auth="+ap.mode;
    if(!ap.token&&qfSqGatewayBadV47(raw))diag+="｜shuqi_token无效/未注入";
    var pack={ts:Date.now(),list:flat,free:String(d.freeContUrlPrefix||""),charge:String(d.chargeContUrlPrefix||""),short:String(d.shortContUrlPrefix||""),diag:diag};
    if(flat.length)qfCachePut.call(this,key,pack);
    return pack;
}
function qfShuqiContentV44(meta){
    meta=meta||{};
    if(!qfText(meta.bookName)||!qfText(meta.author))throw new Error("书旗严格匹配需要完整书名和作者信息");
    var bkey="qf_v48_bind_sq_"+meta.bookId,bind=qfCacheGet.call(this,bkey);
    if(!qfSqBindValidV48(bind,meta))bind=null;
    if(!bind||!bind.id){
        var books=qfSqSearchV44.call(this,meta.bookName,meta.author),hit=qfSqPickBookV44(books,meta.bookName,meta.author);
        if(!hit){
            var web=[];try{web=qfSqWebSearchV46.call(this,meta.bookName,meta.author)||[];}catch(_w){}
            if(web.length){for(var wi=0;wi<web.length;wi++)books.push(web[wi]);hit=qfSqPickBookV44(books,meta.bookName,meta.author);}
        }
        if(!hit){
            var sample=[];
            for(var si=0;si<Math.min(10,books.length);si++)sample.push(qfSqBookNameV44(books[si])+"/"+qfSqBookAuthorV44(books[si])+"#"+qfSqBookIdV44(books[si]));
            throw new Error("书旗未匹配到书名+作者均一致的书籍｜目标["+meta.bookName+"/"+meta.author+"]｜搜索"+books.length+"项"+(sample.length?"："+sample.join(" / "):""));
        }
        bind={id:qfSqBookIdV44(hit),name:qfSqBookNameV44(hit),author:qfSqBookAuthorV44(hit),strictV:48};
        if(!qfSqBindValidV48(bind,meta))throw new Error("书旗候选二次校验失败：["+bind.name+"/"+bind.author+"#"+bind.id+"]");
        qfCachePut.call(this,bkey,bind);
    }
    var providerTag="书旗#"+String(bind.id),wh=qfChapterWindowTryV310.call(this,providerTag,meta,"chapterName",true),cat=null,ch=null;
    if(wh&&wh.chapter&&qfSqChapterCompatibleV48(wh.chapter,meta)){
        var ex=wh.extra||{};ch=wh.chapter;cat={free:String(ex.free||""),charge:String(ex.charge||""),short:String(ex.short||""),list:[],diag:"章节窗口直达/严格校验"};
    }else{
        cat=qfSqCatalogV44.call(this,bind.id,false);ch=qfSqPickChapterV44(cat.list,meta,bind.id);
        if(!ch){cat=qfSqCatalogV44.call(this,bind.id,true);ch=qfSqPickChapterV44(cat.list,meta,bind.id);}
        if(ch)qfChapterWindowPutV310.call(this,providerTag,meta,cat.list,ch,"chapterName",{free:cat.free,charge:cat.charge,short:cat.short});
    }
    if(!ch)throw new Error("书旗已严格匹配本书["+bind.name+"/"+bind.author+"#"+bind.id+"]，但未匹配章节："+meta.title+"｜书旗目录"+((cat&&cat.list&&cat.list.length)||0)+"章｜"+((cat&&cat.diag)||"无目录诊断"));
    var suffix=String(ch.contUrlSuffix||""),free=(ch.isFreeRead===true||String(ch.isFreeRead)==="1"||Number(ch.isFreeRead)===1),prefix=free?cat.free:cat.charge,real=String(prefix||"")+suffix;if(real)real=real.replace(/0$/,"1");var shortUrl=String(cat.short||"")+String(ch.shortContUrlSuffix||""),urls=[],last="";function add(u){u=String(u||"");if(u&&urls.indexOf(u)<0)urls.push(u);}add(real);add(shortUrl);if(/1$/.test(real))add(real.replace(/1$/,"0"));for(var u=0;u<urls.length;u++)try{var r=qfJson(qfJava(this).ajax(urls[u]+","+JSON.stringify({headers:qfSqSearchHeadersV46()})),{}),enc=r&&(r.ChapterContent||r.chapterContent)||"";if(enc){var text=qfSqDecodeV44.call(this,enc);if(qfValidContentV10(text))return text;}last=String(r.message||r.msg||"正文为空");}catch(e0){last=String(e0&&e0.message||e0);}throw new Error("书旗正文获取失败："+(last||"正文为空"));
}
