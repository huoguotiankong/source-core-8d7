import json,re,base64,gzip
from pathlib import Path

PATH=Path('sources/novel/qidian-next/qidian-next-beta.json')
data=json.loads(PATH.read_text(encoding='utf-8'))
src=data[0] if isinstance(data,list) else data
js=src['jsLib']
m=re.search(r'(\\?"role\\?"\s*:\s*\\?"gz:)([A-Za-z0-9+/=]+)',js)
assert m,'role payload not found'
b=m.group(2); b+='='*((4-len(b)%4)%4)
role=gzip.decompress(base64.b64decode(b)).decode('utf-8')

anchor='function qfRoleFetchOfficial2940(ctx,bid){'
assert anchor in role
helper=r'''
/* beta26：官方 Relationship 星耀守护数据链。
 * lookfor 继续负责角色基础资料；星耀数据按 BookId + RoleId 从官方 relationship 前端
 * 动态发现 Argus 路径，命中后会话缓存路径与角色结果，避免硬编码易变接口。 */
var QF_ROLE_REL_ROUTE_B26="",QF_ROLE_REL_MEM_B26={};
function qfRoleRelEmptyB26(){return {rank:"",value:"",level:"",guardians:"",current:0,next:0,percent:-1};}
function qfRoleRelValidB26(s){return !!(s&&(s.rank||s.value||s.level||s.guardians||Number(s.current)>0||Number(s.next)>0));}
function qfRoleRelNumB26(v){var m=String(v==null?"":v).replace(/,/g,"").match(/\d+(?:\.\d+)?/);return m?(Number(m[0])||0):0;}
function qfRoleRelParseB26(raw){
    raw=String(raw==null?"":raw);var out=qfRoleRelEmptyB26(),obj=null;
    try{obj=JSON.parse(raw.replace(/^\uFEFF/,"").trim());}catch(_e){}
    if(obj){try{var mm=qfRoleMetaB22(obj);if(mm&&mm.star)out=mm.star;}catch(_e2){}}
    function text(re){var m=raw.match(re);return m&&m[1]?String(m[1]).trim():"";}
    function numberKey(names){var re=new RegExp('"(?:'+names.join('|')+')"\\s*:\\s*"?([\\d,.]+)"?','i'),m=raw.match(re);return m?qfRoleRelNumB26(m[1]):0;}
    if(!out.value){var n=numberKey(['StarScore','starScore','StarValue','starValue','StarLightValue','starLightValue','GloryValue','gloryValue','RelationshipValue','relationshipValue','RelationValue','relationValue']);if(n)out.value=String(n);}
    if(!out.guardians){var g=numberKey(['GuardianCount','guardianCount','GuardCount','guardCount','GuardUserCount','guardUserCount','GuardianUserCount','guardianUserCount','StarUserCount','starUserCount','SupporterCount','supporterCount']);if(g)out.guardians=String(g);}
    if(!out.rank){var r=numberKey(['GuardianRank','guardianRank','GuardRank','guardRank','RankNo','rankNo','Ranking','ranking','SupportRank','supportRank']);if(r)out.rank=String(r);}
    if(!out.level)out.level=text(/"(?:StarLevelName|starLevelName|StarRankName|starRankName|GuardianLevelName|guardianLevelName|RelationshipLevelName|relationshipLevelName|RelationLevelName|relationLevelName)"\s*:\s*"([^"]+)"/i);
    if(!out.level)out.level=text(/([一二三四五六七八九十]+等星)/);
    if(!out.guardians){var mg=raw.match(/([\d,]+)\s*位守护者/);if(mg)out.guardians=String(qfRoleRelNumB26(mg[1]));}
    if(!out.value){var ms=raw.match(/([\d.]+)\s*(万|亿)?\s*星耀值/);if(ms){var sc=qfRoleRelNumB26(ms[1]);if(ms[2]==="万")sc*=10000;else if(ms[2]==="亿")sc*=100000000;out.value=String(sc);}}
    if(Number(out.current)>0&&Number(out.next)>Number(out.current))out.percent=Math.max(0,Math.min(100,Math.round(Number(out.current)*100/Number(out.next))));
    return out;
}
function qfRoleRelHttpB26(ctx,url){
    try{var j=ctx&&ctx.java?ctx.java:(typeof java!=="undefined"?java:null);if(!j||!j.ajax)return "";return String(j.ajax(String(url))||"");}catch(_e){return "";}
}
function qfRoleRelAbsB26(base,u){
    u=String(u||"").replace(/&amp;/g,"&").replace(/\\\//g,"/").trim();if(!u)return "";
    if(/^https?:\/\//i.test(u))return u;if(/^\/\//.test(u))return "https:"+u;
    var m=String(base||"").match(/^(https?:\/\/[^\/]+)/i);if(/^\//.test(u))return (m?m[1]:"")+u;
    var p=String(base||"").replace(/[?#].*$/,"").replace(/\/[^\/]*$/,"/");return p+u;
}
function qfRoleRelCandidatesB26(text){
    text=String(text||"").replace(/\\\//g,"/");var out=[],seen={};
    function add(x){x=String(x||"").replace(/^https?:\/\/[^\/]+\//i,"").replace(/^\//,"").replace(/^argus\/api\//i,"").split(/[?#]/)[0];if(!/^v\d+\//i.test(x)||seen[x])return;if(!/(role|star|guard|guardian|glory|relationship|relation)/i.test(x))return;seen[x]=1;out.push(x);}
    var r,m;r=/(?:https?:\/\/[^"'`\s<>{}]+\/)?(?:argus\/api\/)?(v\d+\/[A-Za-z0-9_\-\/]*(?:role|star|guard|guardian|glory|relationship|relation)[A-Za-z0-9_\-\/]*)/gi;while((m=r.exec(text))&&out.length<60)add(m[1]);
    r=/(v\d+\/[A-Za-z0-9_\-\/]*bookrole\/[A-Za-z0-9_\-\/]+)/gi;while((m=r.exec(text))&&out.length<60)add(m[1]);
    return out;
}
function qfRoleRelTryPathB26(ctx,path,bid,rid){
    var packs=[
        {bookId:String(bid),roleId:String(rid)},
        {roleId:String(rid),bookId:String(bid)},
        {bookId:String(bid),roleId:String(rid),pg:"1",pz:"20"},
        {bookId:String(bid),roleId:String(rid),pageIndex:"1",pageSize:"20"},
        {bookId:String(bid),id:String(rid)},
        {roleID:String(rid),bookID:String(bid)}
    ];
    for(var i=0;i<packs.length;i++){
        try{var raw=qfArgusOuterRequest2931(ctx,path,packs[i]);if(!raw)continue;var st=qfRoleRelParseB26(raw);if(qfRoleRelValidB26(st))return {ok:true,star:st,path:path};}catch(_e){}
    }
    return {ok:false,star:qfRoleRelEmptyB26(),path:path};
}
function qfRoleRelDiscoverB26(ctx,bid,rid){
    var page="https://h5.if.qidian.com/h5/relationship?roleId="+encodeURIComponent(String(rid))+"&bookId="+encodeURIComponent(String(bid));
    var html=qfRoleRelHttpB26(ctx,page),st=qfRoleRelParseB26(html);if(qfRoleRelValidB26(st))return {ok:true,star:st,path:"@relationship-html"};
    var cand=qfRoleRelCandidatesB26(html),scripts=[],m,re=/<script\b[^>]*\bsrc=["']([^"']+)["'][^>]*>/gi;
    while((m=re.exec(html))&&scripts.length<10){var su=qfRoleRelAbsB26(page,m[1]);if(su&&scripts.indexOf(su)<0)scripts.push(su);}
    scripts.sort(function(a,b){function score(u){var n=0;if(/relationship|role|relation/i.test(u))n-=40;if(/app|index|main/i.test(u))n-=10;if(/vendor|polyfill|chunk-vendors/i.test(u))n+=30;return n;}return score(a)-score(b);});
    for(var si=0;si<scripts.length&&si<6;si++){
        var body=qfRoleRelHttpB26(ctx,scripts[si]),sx=qfRoleRelParseB26(body);if(qfRoleRelValidB26(sx))return {ok:true,star:sx,path:"@relationship-js"};
        var cc=qfRoleRelCandidatesB26(body);for(var ci=0;ci<cc.length;ci++)if(cand.indexOf(cc[ci])<0)cand.push(cc[ci]);
    }
    for(var ai=0;ai<cand.length&&ai<24;ai++){var hit=qfRoleRelTryPathB26(ctx,cand[ai],bid,rid);if(hit.ok){QF_ROLE_REL_ROUTE_B26=hit.path;return hit;}}
    return {ok:false,star:qfRoleRelEmptyB26(),path:""};
}
function qfRoleRelationshipB26(ctx,bid,rid){
    bid=String(bid||"");rid=String(rid||"");if(!bid||!rid)return qfRoleRelEmptyB26();var key=bid+"|"+rid,c=QF_ROLE_REL_MEM_B26[key];
    if(c&&Date.now()-Number(c.ts||0)<5*60*1000)return c.star||qfRoleRelEmptyB26();
    var hit=null;if(QF_ROLE_REL_ROUTE_B26)hit=qfRoleRelTryPathB26(ctx,QF_ROLE_REL_ROUTE_B26,bid,rid);if(!hit||!hit.ok)hit=qfRoleRelDiscoverB26(ctx,bid,rid);
    var star=hit&&hit.ok?hit.star:qfRoleRelEmptyB26();QF_ROLE_REL_MEM_B26[key]={ts:Date.now(),star:star};return star;
}
function qfRoleEnrichStarsB26(ctx,bid,roles){
    roles=Array.isArray(roles)?roles:[];var lim=Math.min(roles.length,10);
    for(var i=0;i<roles.length;i++){
        var r=roles[i]||{},base=qfRoleMetaB22(r.raw||{});r.profile=base.profile||{};r.star=base.star||qfRoleRelEmptyB26();
        if(i<lim&&r.id){var rel=qfRoleRelationshipB26(ctx,bid,r.id);if(qfRoleRelValidB26(rel))r.star=rel;}
    }
    return roles;
}

'''
role=role.replace(anchor,helper+anchor,1)

old='var roles=[];\n            try{roles=qfRoleNormalize2940(root,bid)||[];}catch(_nr){roles=[];}\n            if(roles.length){\n                return qfRoleCachePutB6(bid,{ok:true,root:root,raw:lastRaw,attempt:i,cached:false,roles:roles});\n            }'
new='var roles=[];\n            try{roles=qfRoleNormalize2940(root,bid)||[];}catch(_nr){roles=[];}\n            if(roles.length){\n                try{roles=qfRoleEnrichStarsB26(ctx,bid,roles)||roles;}catch(_se){}\n                return qfRoleCachePutB6(bid,{ok:true,root:root,raw:lastRaw,attempt:i,cached:false,roles:roles});\n            }'
assert old in role,'fetch success block not found'
role=role.replace(old,new,1)

old2="for(var i=0;i<src.length;i++){var r=src[i]||{};var rm=qfRoleMetaB22(r.raw||{});canonical.push({id:String(r.id||''),name:String(r.name||''),position:String(r.position||''),desc:String(r.description!==undefined?r.description:(r.desc||'')),likes:Number(r.likes||0)||0,image:String(r.image||''),tags:Array.isArray(r.tags)?r.tags:[],profile:rm.profile,star:rm.star});}"
new2="for(var i=0;i<src.length;i++){var r=src[i]||{};var rm=(r.profile||r.star)?{profile:r.profile||{},star:r.star||{}}:qfRoleMetaB22(r.raw||{});canonical.push({id:String(r.id||''),name:String(r.name||''),position:String(r.position||''),desc:String(r.description!==undefined?r.description:(r.desc||'')),likes:Number(r.likes||0)||0,image:String(r.image||''),tags:Array.isArray(r.tags)?r.tags:[],profile:rm.profile,star:rm.star});}"
assert old2 in role,'canonical block not found'
role=role.replace(old2,new2,1)

role=role.replace('角色档案 · 起点官方数据 · B25','角色档案 · 起点官方数据 · B26',1)
assert 'https://h5.if.qidian.com/h5/relationship?roleId=' in role
assert 'qfRoleEnrichStarsB26(ctx,bid,roles)' in role
assert 'interactive=!!(e.target&&e.target.closest&&e.target.closest(".tabs"))' in role

packed=base64.b64encode(gzip.compress(role.encode('utf-8'),9)).decode('ascii')
js=js[:m.start(2)]+packed+js[m.end(2):]
src['jsLib']=js
src['bookSourceComment']='v1.1.0-beta26：角色卡官方星耀守护链测试版。保留 beta25 已真机确认的页签触摸修复与角色档案默认页；角色基础资料仍走 v3/bookdetail/lookfor，新增按 BookId+RoleId 访问官方 /h5/relationship，并从其前端动态发现 Relationship/Role/Star/Guard Argus 路径，复用现有签名请求器获取真实星耀值、守护人数、等级/排名后按 RoleId 合并。接口/角色结果会话缓存，最多 enrich 前10个角色；失败仅保留暂无，不影响角色档案。其它域冻结。'
PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('patched beta26 role bytes',len(role.encode('utf-8')))
