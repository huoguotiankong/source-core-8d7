function qfLimSetErrV30(name,msg){
    try{qfRuntimeCacheV13(this).putMemory("qf_lim_err_"+String(name||""),String(msg||""));}catch(e0){}
}
function qfLimGetErrV30(name){
    try{return String(qfRuntimeCacheV13(this).getFromMemory("qf_lim_err_"+String(name||""))||"");}catch(e0){return "";}
}

/* 情无 Provider · beta17
 * 登录/正文严格对齐附件「📖起点中文」：
 * - POST 根目录 /auth.php?action=login
 * - /qd/auth.php?action=me 验证/刷新 request_token
 * - /qd/content.php 获取正文
 * 集成源额外只做两件事：
 * 1) 情无 Cookie/Token 使用 qf_qw_* 独立镜像，避免与其它源设置互相覆盖；
 * 2) VIP 首次失败时只自动续签一次，再重试正文一次。
 */
/* beta17.1：lazy module 不再依赖全局 source/java/cookie。
 * Provider 由 Registry 以 fn.apply(ctx) 调用，必须始终从 this 取当前书源运行上下文。
 * 登录页的 source 是全局对象，而 lazy Provider 的自由变量 source 在部分阅读执行线程中可能不存在，
 * 这正是“登录页显示令牌正常，但正文模块读不到 request_token”的根因。 */
function qfQwSrcV318(ctx){try{return qfSource(ctx);}catch(e){return null;}}
function qfQwJavaV318(ctx){try{return qfJava(ctx);}catch(e){return null;}}
function qfQwLoginMapV318(ctx){
    var s=qfQwSrcV318(ctx),m=null;
    try{m=s&&s.getLoginInfoMap?s.getLoginInfoMap():null;}catch(e0){}
    function g(k){try{return m&&(m.get?m.get(k):m[k]);}catch(e1){return null;}}
    return {cookie:String(g("情无会话Cookie")||""),token:String(g("情无会话令牌")||""),keys:String(g("情无共享凭据")||"")};
}
function qfQwCookieObjV318(ctx){
    try{if(ctx&&ctx.cookie)return ctx.cookie;}catch(e0){}
    try{if(typeof cookie!=="undefined")return cookie;}catch(e1){}
    return null;
}
function qfQwNormBaseV44(v){
    var s=String(v||"").trim();
    if(!s)return "";
    if(!/^https?:\/\//i.test(s))s="http://"+s;
    s=s.replace(/[?#].*$/g,"").replace(/\/+$/g,"");
    var m=s.match(/^(https?:\/\/[^\/]+)(\/.*)?$/i);
    if(!m)return s;
    var host=m[1],path=String(m[2]||"");
    var q=path.match(/^(.*?\/qd)(?:\/.*)?$/i);
    if(q)return host+q[1];
    if(!path||path==="/")return host+"/qd";
    return s;
}
function qfQwBaseV44(){
    var d="http://103.236.85.8:7878/qd",x="",s=qfQwSrcV318(this);
    try{
        var m=s&&s.getLoginInfoMap?s.getLoginInfoMap():null;
        var v=m&&(m.get?m.get("情无接口地址"):m["情无接口地址"]);
        if(v!=null&&String(v).trim())x=qfQwNormBaseV44(v);
    }catch(e0){}
    if(!x){try{x=qfQwNormBaseV44(s&&s.get?s.get("qf_qw_base")||"":"");}catch(e1){}}
    return x||d;
}
function qfQwRootsV44(){return [qfQwBaseV44.call(this)];}
function qfQwStaticHeadersV51(){
    var b=qfQwBaseV44.call(this);
    return {
        "User-Agent":"Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36",
        "Accept":"application/json,text/plain,*/*",
        "Referer":b+"/ranking.html"
    };
}
function qfQwReadLoginInfoV51(){
    var s=qfQwSrcV318(this);
    try{return JSON.parse(String(s&&s.getLoginInfo?s.getLoginInfo():"")||"{}")||{};}catch(e0){return {};}
}
function qfQwReadLoginHeaderV51(){
    var s=qfQwSrcV318(this);
    try{return JSON.parse(String(s&&s.getLoginHeader?s.getLoginHeader():"")||"{}")||{};}catch(e0){return {};}
}
function qfQwDedicatedV317(){
    var out={cookie:"",token:"",keys:-1},s=qfQwSrcV318(this),lm=qfQwLoginMapV318(this);
    try{out.cookie=String((s&&s.get?s.get("qf_qw_cookie_v317"):"")||lm.cookie||"");}catch(e0){out.cookie=String(lm.cookie||"");}
    try{out.token=String((s&&s.get?s.get("qf_qw_token_v317"):"")||lm.token||"");}catch(e1){out.token=String(lm.token||"");}
    try{var k=(s&&s.get?s.get("qf_qw_keys_v317"):null);if(k===null||k===undefined||String(k)==="")k=lm.keys;if(k!==null&&k!==undefined&&String(k)!=="")out.keys=Number(k);}catch(e2){}
    return out;
}
function qfQwCookieJarV317(){
    var base=qfQwBaseV44.call(this),root=/\/qd$/i.test(base)?base.replace(/\/qd$/i,""):base,ck="",cj=qfQwCookieObjV318(this);
    if(!cj)return "";
    try{ck=String(cj.getCookie(base+"/")||"");}catch(e0){}
    if(!ck)try{ck=String(cj.getCookie(root+"/")||"");}catch(e1){}
    return ck;
}
function qfQwSaveSessionV317(ck,token,keys){
    ck=String(ck||"");token=String(token||"");var s=qfQwSrcV318(this);
    if(!s)return;
    try{if(ck&&s.put)s.put("qf_qw_cookie_v317",ck);}catch(e0){}
    try{if(token&&s.put)s.put("qf_qw_token_v317",token);}catch(e1){}
    try{if(keys!==undefined&&keys!==null&&!isNaN(Number(keys))&&s.put)s.put("qf_qw_keys_v317",String(Number(keys)));}catch(e2){}
    try{
        var lh=qfQwReadLoginHeaderV51.call(this);lh.Accept="application/json";
        if(ck)lh.Cookie=ck;if(token)lh["X-Content-Token"]=token;
        if(s.putLoginHeader)s.putLoginHeader(JSON.stringify(lh));
    }catch(e3){}
    try{
        var li=qfQwReadLoginInfoV51.call(this);if(token)li.request_token=token;
        if(s.putLoginInfo)s.putLoginInfo(JSON.stringify(li));
    }catch(e4){}
}
function qfQwHeadersV44(){
    var hd=qfQwStaticHeadersV51.call(this),ds=qfQwDedicatedV317.call(this),lh=qfQwReadLoginHeaderV51.call(this),li=qfQwReadLoginInfoV51.call(this);
    var ck=String(ds.cookie||lh.Cookie||qfQwCookieJarV317.call(this)||"");
    var tk=String(ds.token||lh["X-Content-Token"]||li.request_token||"");
    if(ck)hd.Cookie=ck;if(tk)hd["X-Content-Token"]=tk;
    if((ck&&!ds.cookie)||(tk&&!ds.token))qfQwSaveSessionV317.call(this,ck,tk,ds.keys);
    return hd;
}
function qfQwCollectCookieV317(res){
    var parts=[];
    try{
        var all=res.headers(new Packages.java.lang.String("Set-Cookie"));
        if(all)for(var i=0;i<all.size();i++){var first=String(all.get(i)).split(";")[0];if(first)parts.push(first);}
    }catch(e0){}
    return parts.join("; ");
}
function qfQwKeyCountV317(user){
    try{
        if(!user)return -1;var k=user.keys;
        if(k&&typeof k.length==="number")return Number(k.length);
        if(k&&typeof k.size==="function")return Number(k.size());
    }catch(e0){}
    return -1;
}
function qfQwMeV317(hd){
    var base=qfQwBaseV44.call(this),obj=null,j=qfQwJavaV318(this);if(!j)return null;
    try{var me=j.get(base+"/auth.php?action=me",hd||qfQwHeadersV44.call(this),12000);obj=JSON.parse(String(me.body()||"{}"));}catch(e0){return null;}
    var token=String(obj&&obj.request_token||""),keys=qfQwKeyCountV317(obj&&obj.user),ck=String((hd&&hd.Cookie)||qfQwDedicatedV317.call(this).cookie||"");
    if(token||obj&&obj.user)qfQwSaveSessionV317.call(this,ck,token,keys);
    return obj;
}
function qfQwPasswordLoginV317(){
    var li=qfQwReadLoginInfoV51.call(this),email=String(li.email||"").trim(),pw=String(li.password||""),j=qfQwJavaV318(this);
    if(!email||!pw||!j)return false;
    var base=qfQwBaseV44.call(this),root=/\/qd$/i.test(base)?base.replace(/\/qd$/i,""):base;
    var body=new Packages.java.lang.String(JSON.stringify({email:email,password:pw}));
    var h=qfQwStaticHeadersV51.call(this);h["Content-Type"]="application/json";var res=null,data=null;
    try{res=j.post(new Packages.java.lang.String(root+"/auth.php?action=login"),body,h,15000);}catch(e0){return false;}
    try{data=JSON.parse(String(res.body()||"{}"));}catch(e1){return false;}
    if(!data||!data.user)return false;
    var ck=qfQwCollectCookieV317(res),token=String(data.request_token||""),keys=qfQwKeyCountV317(data.user);
    if(!ck)try{ck=qfQwCookieJarV317.call(this);}catch(_ck){}
    qfQwSaveSessionV317.call(this,ck,token,keys);
    var hd=qfQwStaticHeadersV51.call(this);if(ck)hd.Cookie=ck;if(token)hd["X-Content-Token"]=token;
    var me=qfQwMeV317.call(this,hd);if(me&&me.request_token)token=String(me.request_token);
    return !!(token||(me&&me.user));
}
function qfQwRefreshSessionV317(allowPassword){
    var hd=qfQwHeadersV44.call(this),me=qfQwMeV317.call(this,hd);
    if(me&&(me.user||me.request_token))return qfQwHeadersV44.call(this);
    if(allowPassword&&qfQwPasswordLoginV317.call(this))return qfQwHeadersV44.call(this);
    return hd;
}
function qfQwAcquireTokenV44(force){
    var hd=force?qfQwRefreshSessionV317.call(this,true):qfQwHeadersV44.call(this);
    var token=String(hd["X-Content-Token"]||"");
    if(!token&&force){hd=qfQwRefreshSessionV317.call(this,true);token=String(hd["X-Content-Token"]||"");}
    return token;
}
function qfQwPickContentV51(obj,raw){
    function pick(x){
        if(!x)return "";if(typeof x==="string")return x;
        if(x.Content!==undefined)return x.Content;if(x.content!==undefined)return x.content;
        if(x.Data){if(x.Data.Content!==undefined)return x.Data.Content;if(x.Data.content!==undefined)return x.Data.content;}
        return "";
    }
    var val=obj?pick(obj):raw;
    for(var deep=0;deep<3;deep++){
        var t=String(val||"").trim();if(!(t.charAt(0)==="{"||t.charAt(0)==="["))break;
        try{var inner=JSON.parse(t),next=pick(inner);if(next===undefined||next===null||String(next)===String(val))break;val=next;}catch(e){break;}
    }
    return String(val||"");
}
function qfQwRequestContentV317(api,hd){
    var raw="",j=qfQwJavaV318(this);if(!j)return "";
    try{
        var arr=j.ajaxAll([api+","+JSON.stringify({headers:hd,timeout:12000})]);
        if(arr&&arr.length)try{raw=String(arr[0].body()||"");}catch(_b){}
    }catch(e0){}
    if(!raw)try{raw=String(j.get(String(api),hd,10000).body()||"");}catch(e1){}
    return raw;
}
function qfQwMarkVipVerifiedV101(token){
    var s=qfQwSrcV318(this),base=qfQwBaseV44.call(this);
    token=String(token||"");
    if(!s||!s.put||!token)return;
    try{s.put("qf_qw_vip_verified_v101",base+"|"+token+"|"+String(Date.now()));}catch(e0){}
}
function qfQwAuthLikeV317(obj,raw){
    var msg="";try{msg=String((obj&&(obj.detail||obj.Message||obj.message||obj.error))||raw||"");}catch(e0){}
    return /未登录|登录|token|令牌|凭据|unauthor|expired|过期|失效|401|403/i.test(msg);
}
function qfQwContentV44(meta){
    meta=meta||{};var bid=String(meta.bookId||""),cid=String(meta.chapterId||""),isPaid=String(meta.vip||"0")==="1";
    if(!bid||!cid){qfLimSetErrV30.call(this,"情无","章节参数错误：BookId="+bid+"，ChapterId="+cid);return null;}
    var base=qfQwBaseV44.call(this),api=base+"/content.php?book_id="+encodeURIComponent(bid)+"&chapter_id="+encodeURIComponent(cid)+(isPaid?"&vip=1":"");
    var hd=qfQwHeadersV44.call(this);
    if(isPaid&&!hd["X-Content-Token"]){hd=qfQwRefreshSessionV317.call(this,true);}
    if(isPaid&&!hd["X-Content-Token"]){qfLimSetErrV30.call(this,"情无","正文线程未读取到情无 request_token；请重新进入登录设置 → 情无 → 检测会话后刷新本章");return null;}

    function decode(raw){var obj=null;try{obj=JSON.parse(String(raw||""));}catch(_j){}return {raw:String(raw||""),obj:obj,val:qfQwPickContentV51(obj,String(raw||""))};}
    try{
        var r=decode(qfQwRequestContentV317.call(this,api,hd));
        if(r.val){if(isPaid)qfQwMarkVipVerifiedV101.call(this,String(hd["X-Content-Token"]||""));qfLimSetErrV30.call(this,"情无","");return r.val.replace(/\\r\\n/g,"\n").replace(/\\n/g,"\n").replace(/\r\n/g,"\n").replace(/\r/g,"\n");}

        /* 只在明确认证错误时续签一次。服务端业务/共享凭据失败不再盲目重登。 */
        if(qfQwAuthLikeV317(r.obj,r.raw)){
            var hd2=qfQwRefreshSessionV317.call(this,true);
            if(hd2&&hd2["X-Content-Token"]){
                var r2=decode(qfQwRequestContentV317.call(this,api,hd2));
                if(r2.val){if(isPaid)qfQwMarkVipVerifiedV101.call(this,String(hd2["X-Content-Token"]||""));qfLimSetErrV30.call(this,"情无","");return r2.val.replace(/\\r\\n/g,"\n").replace(/\\n/g,"\n").replace(/\r\n/g,"\n").replace(/\r/g,"\n");}
                r=r2;
            }
        }
        var msg="";
        if(r.obj&&r.obj.detail)msg=String(r.obj.detail);else if(r.obj&&r.obj.Message)msg=String(r.obj.Message);else if(r.obj&&r.obj.message)msg=String(r.obj.message);else msg="正文为空";
        var ds=qfQwDedicatedV317.call(this),authLike=qfQwAuthLikeV317(r.obj,r.raw);
        if(isPaid&&Number(ds.keys)===0)msg+="（账号会话已建立，但共享凭据为 0；VIP 正文尚不可用）";
        else if(isPaid&&authLike)msg+="（情无会话/阅读令牌被正文接口拒绝，请重新登录后再试）";
        else if(isPaid)msg+="（账号会话已建立"+(Number(ds.keys)>0?" · 共享凭据 "+String(Number(ds.keys))+" 个":"")+"，但 VIP 正文服务拒绝本次请求；请保留 Reference 供后续排查）";
        qfLimSetErrV30.call(this,"情无",msg);return null;
    }catch(e1){qfLimSetErrV30.call(this,"情无","正文请求失败："+String(e1)+(isPaid?"（账号会话与 VIP 正文可用性是两层状态）":""));return null;}
}
