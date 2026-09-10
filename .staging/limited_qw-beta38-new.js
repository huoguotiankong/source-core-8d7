function qfLimSetErrV30(name,msg){
    try{qfRuntimeCacheV13(this).putMemory("qf_lim_err_"+String(name||""),String(msg||""));}catch(e0){}
}
function qfLimGetErrV30(name){
    try{return String(qfRuntimeCacheV13(this).getFromMemory("qf_lim_err_"+String(name||""))||"");}catch(e0){return "";}
}

/* 情无 Provider · beta38
 * 来源替换为用户附件「小雨的世界」的起点正文链：
 *   https://full.hnxianxin.cn/qd/catalog.php
 *   https://full.hnxianxin.cn/qd/content.php
 * 对外名称仍保持“情无”。
 * 不接管搜索/详情/评论，只作为起点增强限免正文 Provider。
 */
function qfQwSrcV38(ctx){try{return qfSource(ctx);}catch(e){return null;}}
function qfQwJavaV38(ctx){try{return qfJava(ctx);}catch(e){return null;}}
function qfQwNormBaseV44(v){return "https://full.hnxianxin.cn/qd";}
function qfQwBaseV44(){return "https://full.hnxianxin.cn/qd";}
function qfQwRootsV44(){return [qfQwBaseV44.call(this)];}
function qfQwCredV38(){
    var s=qfQwSrcV38(this),m=null,out={ywkey:"",ywguid:""};
    try{m=s&&s.getLoginInfoMap?s.getLoginInfoMap():null;}catch(_e0){}
    function g(k){try{return m&&(m.get?m.get(k):m[k]);}catch(_e1){return null;}}
    try{out.ywkey=String((s&&s.get?s.get("qf_qw_ywkey"):"")||g("情无Ywkey")||g("ywkey")||"").trim();}catch(_e2){}
    try{out.ywguid=String((s&&s.get?s.get("qf_qw_ywguid"):"")||g("情无Ywguid")||g("ywguid")||"").trim();}catch(_e3){}
    return out;
}
function qfQwHeadersV44(){
    var h={"Accept":"application/json,text/plain,*/*","User-Agent":"Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36","Referer":qfQwBaseV44.call(this)+"/"};
    var c=qfQwCredV38.call(this);if(c.ywkey&&c.ywguid){h.Ywkey=c.ywkey;h.Ywguid=c.ywguid;}
    return h;
}
function qfQwAcquireTokenV44(force){return "small-rain-free";}
function qfQwNormB64V38(v){var x=String(v||"").replace(/\s+/g,"").replace(/-/g,"+").replace(/_/g,"/");while(x.length%4)x+="=";return x;}
function qfQwDecodePayloadV38(v){
    var j=qfQwJavaV38(this),txt=String(v||"");if(!txt)return null;
    try{if(j&&j.hexDecodeToString&&/^[0-9a-f]+$/i.test(txt)&&txt.length%2===0)txt=String(j.hexDecodeToString(txt)||txt);}catch(_h){}
    try{txt=decodeURIComponent(txt);}catch(_u){}
    try{if(txt.charAt(0)==="{")return JSON.parse(txt);}catch(_j0){}
    var m=txt.match(/base64,([A-Za-z0-9+\/_=%-]+)/i),z=m?m[1]:txt;
    var comma=z.indexOf(",");if(comma>=0)z=z.substring(0,comma);
    try{if(j&&j.base64Decode){var raw=String(j.base64Decode(qfQwNormB64V38(z))||"");if(raw&&raw.charAt(0)==="{")return JSON.parse(raw);}}catch(_b){}
    return null;
}
function qfQwCatalogMapV38(bid){
    bid=String(bid||"");var key="qf_qw_xy_cat_"+bid,cache=null;
    try{cache=qfRuntimeCacheV13(this).getFromMemory(key);if(cache&&typeof cache==="object")return cache;}catch(_c0){}
    var out={},j=qfQwJavaV38(this);if(!j)return out;
    try{
        var url=qfQwBaseV44.call(this)+"/catalog.php?bookId="+encodeURIComponent(bid);
        var res=j.get(String(url),qfQwHeadersV44.call(this),12000),obj=JSON.parse(String(res.body()||"{}"));
        var list=obj.data||obj.Data||[];if(list&&list.DataList)list=list.DataList;if(!Array.isArray(list))list=[];
        for(var i=0;i<list.length;i++){
            var it=list[i]||{},p=qfQwDecodePayloadV38.call(this,it.C!==undefined?it.C:(it.c!==undefined?it.c:it.chapterUrl));
            var cid=String((p&&(p.chapterId!==undefined?p.chapterId:p.ChapterId))||(it.chapterId!==undefined?it.chapterId:(it.ChapterId!==undefined?it.ChapterId:""))||"");
            if(!cid)continue;
            out[cid]={
                time:String((p&&(p.time!==undefined?p.time:p.t))||(it.T!==undefined?it.T:(it.time!==undefined?it.time:""))||""),
                epub:Number((p&&p.epub)||it.epub||0)?1:0,
                vip:Number((p&&(p.v!==undefined?p.v:p.vip))||(it.V!==undefined?it.V:it.vip)||0)?1:0
            };
        }
        try{qfRuntimeCacheV13(this).putMemory(key,out);}catch(_c1){}
    }catch(e){qfLimSetErrV30.call(this,"情无","目录映射失败："+String(e));}
    return out;
}
function qfQwPickContentV38(obj,raw){
    if(obj){
        if(obj.error)throw new Error(String(obj.error));
        if(obj.detail)throw new Error(String(obj.detail));
        if(obj.code!==undefined&&Number(obj.code)!==0&&obj.msg)throw new Error(String(obj.msg));
        if(obj.content!==undefined)return String(obj.content||"");
        if(obj.Content!==undefined)return String(obj.Content||"");
        if(obj.Data){if(obj.Data.Content!==undefined)return String(obj.Data.Content||"");if(obj.Data.content!==undefined)return String(obj.Data.content||"");}
    }
    return String(raw||"");
}
function qfQwStripFooterV38(text){
    var s=String(text||"").replace(/\\r\\n/g,"\n").replace(/\\n/g,"\n").replace(/\r\n?/g,"\n");
    s=s.replace(/\s*所有接口算法来自于\s*(?:\[?https?:\/\/m\.tb\.cn\/h\.8pvBZxh\?tk=R4fMTSqAOiS\]?(?:\([^\n)]*\))?)?\s*/gi,"\n");
    s=s.replace(/\s*免费看七天请求无限制[，,]?\s*喜欢就来闲鱼支持一下吧\s*/g,"\n");
    s=s.replace(/\n[ \t]+/g,"\n").replace(/\n{3,}/g,"\n\n").replace(/^\s+|\s+$/g,"");
    return s;
}
function qfQwContentV44(meta){
    meta=meta||{};var bid=String(meta.bookId||""),cid=String(meta.chapterId||""),isPaid=String(meta.vip||"0")==="1";
    if(!bid||!cid){qfLimSetErrV30.call(this,"情无","章节参数错误：BookId="+bid+"，ChapterId="+cid);return null;}
    var map=qfQwCatalogMapV38.call(this,bid),it=map[cid]||null;
    if(!it||!String(it.time||"")){qfLimSetErrV30.call(this,"情无","未从新来源目录解析到章节时间戳，请刷新目录/章节后重试");return null;}
    var v=isPaid?1:Number(it.vip||0)?1:0;
    var api=qfQwBaseV44.call(this)+"/content.php?bookId="+encodeURIComponent(bid)+"&chapterId="+encodeURIComponent(cid)+"&t="+encodeURIComponent(String(it.time))+"&epub="+(Number(it.epub||0)?1:0)+"&v="+v;
    var j=qfQwJavaV38(this);if(!j){qfLimSetErrV30.call(this,"情无","java context unavailable");return null;}
    try{
        var res=j.get(String(api),qfQwHeadersV44.call(this),12000),raw=String(res.body()||""),obj=null;
        try{obj=JSON.parse(raw);}catch(_j){}
        var txt=qfQwPickContentV38(obj,raw);txt=qfQwStripFooterV38(txt);
        if(!txt){qfLimSetErrV30.call(this,"情无","新来源正文为空");return null;}
        qfLimSetErrV30.call(this,"情无","");return txt;
    }catch(e){qfLimSetErrV30.call(this,"情无","新来源正文请求失败："+String(e));return null;}
}
