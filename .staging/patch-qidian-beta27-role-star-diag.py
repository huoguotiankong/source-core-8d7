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

start=role.index('function qfRoleRelDiscoverB26(ctx,bid,rid){')
end=role.index('function qfRoleRelationshipB26(ctx,bid,rid){',start)
new_discover=r'''function qfRoleRelDiscoverB26(ctx,bid,rid){
    var pages=[
        "https://h5.if.qidian.com/h5/relationship?roleId="+encodeURIComponent(String(rid))+"&bookId="+encodeURIComponent(String(bid)),
        "https://h5.if.qidian.com/new/role/share/?roleId="+encodeURIComponent(String(rid))+"&bookId="+encodeURIComponent(String(bid)),
        "https://h5v6.if.qidian.com/new/role/share/?roleId="+encodeURIComponent(String(rid))+"&bookId="+encodeURIComponent(String(bid)),
        "https://h5v6.if.qidian.com/h5/relationship?roleId="+encodeURIComponent(String(rid))+"&bookId="+encodeURIComponent(String(bid))
    ];
    var cand=[],seenCand={},scripts=[],seenScript={},pageBytes=0,pageHits=0,scriptBytes=0,scriptHits=0,attempts=0;
    function addCand(arr){arr=arr||[];for(var ai=0;ai<arr.length;ai++){var x=String(arr[ai]||"");if(x&&!seenCand[x]){seenCand[x]=1;cand.push(x);}}}
    function addScripts(base,html){var mm,re=/<script\b[^>]*\bsrc=["']([^"']+)["'][^>]*>/gi;while((mm=re.exec(String(html||"")))&&scripts.length<18){var su=qfRoleRelAbsB26(base,mm[1]);if(su&&!seenScript[su]){seenScript[su]=1;scripts.push(su);}}}
    for(var pi=0;pi<pages.length;pi++){
        var html=qfRoleRelHttpB26(ctx,pages[pi]);if(html){pageHits++;pageBytes+=html.length;}
        var st=qfRoleRelParseB26(html);if(qfRoleRelValidB26(st)){st._diag="B27 · 页面直出 · P"+pageHits+"/"+pages.length+" · "+pageBytes+"B";return {ok:true,star:st,path:"@relationship-html"};}
        addCand(qfRoleRelCandidatesB26(html));addScripts(pages[pi],html);
    }
    scripts.sort(function(a,b){function score(u){var n=0;if(/relationship|role|relation|star|guard/i.test(u))n-=50;if(/app|index|main/i.test(u))n-=10;if(/vendor|polyfill|chunk-vendors/i.test(u))n+=30;return n;}return score(a)-score(b);});
    for(var si=0;si<scripts.length&&si<10;si++){
        var body=qfRoleRelHttpB26(ctx,scripts[si]);if(body){scriptHits++;scriptBytes+=body.length;}
        var sx=qfRoleRelParseB26(body);if(qfRoleRelValidB26(sx)){sx._diag="B27 · JS直出 · P"+pageHits+" · S"+scriptHits+" · "+scriptBytes+"B";return {ok:true,star:sx,path:"@relationship-js"};}
        addCand(qfRoleRelCandidatesB26(body));
    }
    for(var ci=0;ci<cand.length&&ci<36;ci++){attempts++;var hit=qfRoleRelTryPathB26(ctx,cand[ci],bid,rid);if(hit.ok){hit.star._diag="B27 · API命中 · "+cand[ci]+" · P"+pageHits+" S"+scriptHits+" C"+cand.length+" A"+attempts;QF_ROLE_REL_ROUTE_B26=hit.path;return hit;}}
    var empty=qfRoleRelEmptyB26();empty._diag="B27 · 未命中 · 页面"+pageHits+"/"+pages.length+"("+pageBytes+"B) · 脚本"+scriptHits+"/"+scripts.length+"("+scriptBytes+"B) · API候选"+cand.length+" · 已试"+attempts;
    return {ok:false,star:empty,path:""};
}
'''
role=role[:start]+new_discover+role[end:]

old='var star=hit&&hit.ok?hit.star:qfRoleRelEmptyB26();QF_ROLE_REL_MEM_B26[key]={ts:Date.now(),star:star};return star;'
new='var star=hit&&hit.star?hit.star:qfRoleRelEmptyB26();QF_ROLE_REL_MEM_B26[key]={ts:Date.now(),star:star};return star;'
assert old in role
role=role.replace(old,new,1)

old_ui="+(!hasStar?'<div class=\"officialEmpty\">官方暂未返回该角色的星耀守护数据</div>':'')+'<div class=\"ruleTitle\">星耀互动</div>"
new_ui="+(!hasStar?'<div class=\"officialEmpty\">官方暂未返回该角色的星耀守护数据</div>':'')+(s._diag?'<div class=\"officialEmpty\" style=\"font-size:10px;line-height:1.6;text-align:left;word-break:break-all;color:rgba(214,182,107,.72)\">Relationship诊断 · '+v(s._diag)+'</div>':'')+'<div class=\"ruleTitle\">星耀互动</div>"
assert old_ui in role,'star UI anchor not found'
role=role.replace(old_ui,new_ui,1)
role=role.replace('角色档案 · 起点官方数据 · B26','角色档案 · 起点官方数据 · B27',1)

assert 'Relationship诊断' in role
assert 'h5v6.if.qidian.com/new/role/share/' in role
assert 'B27 · 未命中' in role
packed=base64.b64encode(gzip.compress(role.encode('utf-8'),9)).decode('ascii')
js=js[:m.start(2)]+packed+js[m.end(2):]
src['jsLib']=js
src['bookSourceComment']='v1.1.0-beta27：角色卡 Relationship 可观测/多入口发现版。保留 beta26 角色档案与星耀页签；星耀数据发现从单一 /h5/relationship 扩展为 h5/h5v6 的 relationship 与 new/role/share 四个官方入口，并扫描最多10个关联脚本、36个 Role/Star/Guard/Relationship Argus 候选。星耀页底部新增临时 Relationship 诊断，显示页面/脚本/候选API/尝试数或命中路径，用于真机定位数据链。失败仍不伪造数据，其它域冻结。'
PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('patched beta27 role bytes',len(role.encode('utf-8')))
