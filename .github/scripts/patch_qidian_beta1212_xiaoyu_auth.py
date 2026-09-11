import json,gzip,base64,time,hashlib
from pathlib import Path

ROOT=Path('.')
stable=ROOT/'sources/novel/qidian-next/qidian-next.json'
beta=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
arr=json.load(open(stable,encoding='utf-8'))
if not isinstance(arr,list) or not arr: raise SystemExit('stable source must be non-empty array')
s=arr[0]

s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceComment']='v1.2.1-beta2：情无/小雨账号系统按最新附件重接：源作者+官方反馈群+临时口令申请游客 Token，或网页注册/登录；正文未登录继续沿用 Stable 1.2.0 已验证免费链。Stable 不变。'
s['lastUpdateTime']=int(time.time()*1000)

auth=r'''

/* ============================================================
 * qf_xy_auth_v1212 · 当前“小雨的世界”用户系统
 * 严格对齐 2026-09-11 用户附件：
 * - user_api.php?action=guest: source_author / feedback_group / temporary_password / android_id
 * - auth.php?mode=legado&android_id=... 网页注册/登录
 * - user_api.php?action=me: X-Sec-Token + X-Android-Id
 * - 不使用旧邮箱/密码、Cookie、X-Content-Token
 * ============================================================ */
var QF_XY_AUTH_ROOT_V1212="https://full.hnxianxin.cn/qd/";
function qfXyGetV1212(k,d){try{var v=source.get(String(k));return v==null?String(d||""):String(v);}catch(e){return String(d||"");}}
function qfXyPutV1212(k,v){try{source.put(String(k),String(v==null?"":v));return true;}catch(e){return false;}}
function qfXyAndroidIdV1212(){
    var v=qfXyGetV1212("qf_xy_android_id_v1212","").replace(/^\s+|\s+$/g,"");
    if(!v)try{if(java.androidId)v=String(java.androidId()||"").replace(/^\s+|\s+$/g,"");}catch(_e0){}
    if(!v){var chars="0123456789abcdef";for(var i=0;i<16;i++)v+=chars.charAt(Math.floor(Math.random()*16));}
    v=v.toUpperCase();qfXyPutV1212("qf_xy_android_id_v1212",v);return v;
}
function qfXyRequestV1212(action,data,headers){
    var h={"Content-Type":"application/json","Accept":"application/json"};
    if(headers)for(var k in headers)if(Object.prototype.hasOwnProperty.call(headers,k))h[k]=String(headers[k]);
    var opt={method:"POST",headers:h,body:JSON.stringify(data||{})};
    var raw=String(java.ajax(QF_XY_AUTH_ROOT_V1212+"user_api.php?action="+encodeURIComponent(String(action||""))+","+JSON.stringify(opt))||"");
    var o=JSON.parse(raw||"{}");if(o&&o.error)throw new Error(String(o.error));return o||{};
}
function qfXySaveAuthV1212(resp,androidId){
    resp=resp||{};var u=resp.user||{};
    qfXyPutV1212("qf_xy_android_id_v1212",androidId||qfXyAndroidIdV1212());
    qfXyPutV1212("qf_xy_user_token_v1212",resp.token||"");
    qfXyPutV1212("qf_xy_user_name_v1212",u.username||"");
    qfXyPutV1212("qf_xy_user_level_v1212",u.level||"guest");
    return u;
}
function qfXyGuestV1212(){
    var author=qfMGet423("情无源作者","").replace(/^\s+|\s+$/g,"");
    var group=qfMGet423("情无官方反馈群","").replace(/^\s+|\s+$/g,"");
    var pass=qfMGet423("情无临时口令","").replace(/^\s+|\s+$/g,"");
    if(!author||!group||!pass){try{java.toast("请填写源作者、官方反馈群和临时口令");}catch(_t){}return false;}
    try{
        var aid=qfXyAndroidIdV1212(),r=qfXyRequestV1212("guest",{source_author:author,feedback_group:group,temporary_password:pass,android_id:aid});
        var u=qfXySaveAuthV1212(r,aid);try{java.toast("游客授权成功："+String(u.privilege||u.username||"已授权"));java.reLoginView();}catch(_t2){}return true;
    }catch(e){try{java.longToast("情无游客授权失败："+String(e));}catch(_e){}return false;}
}
function qfXyWebV1212(){
    var aid=qfXyAndroidIdV1212();
    var preload=[
      "window.xySaveLegadoAuth=function(payload){",
      " try{var u=(payload&&payload.user)||{};source.put('qf_xy_user_token_v1212',String((payload&&payload.token)||''));source.put('qf_xy_android_id_v1212',String((payload&&payload.android_id)||"+JSON.stringify(aid)+"));source.put('qf_xy_user_name_v1212',String(u.username||''));source.put('qf_xy_user_level_v1212',String(u.level||'guest'));return true;}catch(e){return false;}",
      "};"
    ].join("\n");
    try{java.showBrowser(QF_XY_AUTH_ROOT_V1212+"auth.php?mode=legado&android_id="+encodeURIComponent(aid),null,preload);java.toast("请在网页中完成注册/登录，成功后会自动写入 Token");return true;}catch(e){try{java.longToast("打开情无登录页失败："+String(e));}catch(_e){}return false;}
}
function qfXyMeV1212(){
    var tk=qfXyGetV1212("qf_xy_user_token_v1212",""),aid=qfXyAndroidIdV1212();
    if(!tk){try{java.toast("当前未授权：可申请游客 Token 或网页登录");}catch(_t){}return false;}
    try{
        var opt={method:"GET",headers:{"Accept":"application/json","X-Sec-Token":tk,"X-Android-Id":aid}};
        var raw=String(java.ajax(QF_XY_AUTH_ROOT_V1212+"user_api.php?action=me,"+JSON.stringify(opt))||""),r=JSON.parse(raw||"{}");
        if(r.error)throw new Error(String(r.error));var u=r.user||{};
        qfXyPutV1212("qf_xy_user_name_v1212",u.username||qfXyGetV1212("qf_xy_user_name_v1212",""));
        qfXyPutV1212("qf_xy_user_level_v1212",u.level||qfXyGetV1212("qf_xy_user_level_v1212",""));
        try{java.longToast("\n用户："+(u.username||"游客用户")+"\n等级："+(u.level_name||u.level||"--")+"\n权益："+(u.privilege||"--")+"\n今日："+Number(u.today_count||0)+"\n昨日："+Number(u.yesterday_count||0)+"\n累计："+Number(u.total_count||0));}catch(_t2){}return true;
    }catch(e){try{java.longToast("情无用户状态获取失败："+String(e));}catch(_e){}return false;}
}
function qfXyLogoutV1212(){
    try{qfXyRequestV1212("logout",{});}catch(_e0){}
    qfXyPutV1212("qf_xy_user_token_v1212","");qfXyPutV1212("qf_xy_user_name_v1212","");qfXyPutV1212("qf_xy_user_level_v1212","");
    try{java.toast("已退出情无用户系统");java.reLoginView();}catch(_t){}return true;
}
function qfXyAccountExecV1212(provider,action){
    provider=String(provider||"");action=String(action||"不执行");
    if(provider!=="情无")return qfNextAccountExecV013(provider,action);
    if(action==="申请游客Token")return qfXyGuestV1212();
    if(action==="网页登录")return qfXyWebV1212();
    if(action==="查看使用次数")return qfXyMeV1212();
    if(action==="退出")return qfXyLogoutV1212();
    return true;
}
qfMultiAccountsV423=function(){
    var provider=qfMGet423('账号管理Provider','神魔');
    if(['情无','神魔','晴天','同人','X'].indexOf(provider)<0)provider='神魔';
    var xya=qfMGet423('情无源作者',''),xyg=qfMGet423('情无官方反馈群',''),xyp=qfMGet423('情无临时口令','');
    var xyt=qfXyGetV1212('qf_xy_user_token_v1212',''),xyu=qfXyGetV1212('qf_xy_user_name_v1212',''),xyl=qfXyGetV1212('qf_xy_user_level_v1212','');
    var sma=qfMGet423('神魔账号或邮箱',''),smp=qfMGet423('神魔密码','');
    var qtk=qfMGet423('晴天密钥',''),qtp=qfMGet423('晴天口令',''),qtb=qfMGet423('晴天接口地址','https://sb.shazi.tk');
    var xt=qfMGet423('🎬X佬密钥','');
    var inner=''+
      '<div class="section"><div class="sectionHead"><div><h3>Provider</h3><p>切换后只展示当前 Provider 的账号字段和可用动作。</p></div><span class="miniBadge" id="providerBadge">'+qfUxEscV015(provider)+'</span></div><div class="tabs" id="providerTabs"></div></div>'+
      '<div class="section providerCard" data-p="情无"><div class="sectionHead"><div><h3>🌙 情无 / 小雨用户系统</h3><p>当前版本不使用邮箱密码。游客授权填写三项资料；普通账号请使用网页注册/登录。</p></div><span class="miniBadge">'+qfUxEscV015(xyt?(xyu||xyl||'已授权'):'未授权')+'</span></div>'+qfUxFieldV015('xy_author','源作者',xya,'text','手动填写')+qfUxFieldV015('xy_group','官方反馈群',xyg,'text','手动填写')+qfUxFieldV015('xy_pass','临时口令',xyp,'text','手动填写')+'<div class="state">'+(xyt?'Token 已存在；正文会自动携带 X-Sec-Token / X-Android-Id。':'未登录仍可继续使用已验证的免费正文链。')+'</div></div>'+
      '<div class="section providerCard" data-p="神魔"><div class="sectionHead"><div><h3>⚔️ 神魔账号</h3><p>账号/邮箱和密码；支持后台管理。</p></div></div>'+qfUxFieldV015('sm_account','账号或邮箱',sma,'text','神魔后台账号')+qfUxFieldV015('sm_password','密码',smp,'password','神魔密码')+'</div>'+
      '<div class="section providerCard" data-p="晴天"><div class="sectionHead"><div><h3>☀️ 晴天账号</h3><p>密钥、口令和接口地址。</p></div></div>'+qfUxFieldV015('qt_key','密钥',qtk,'password','')+qfUxFieldV015('qt_pass','口令',qtp,'password','')+qfUxFieldV015('qt_base','接口地址',qtb,'text','默认 https://sb.shazi.tk')+'</div>'+
      '<div class="section providerCard" data-p="同人"><div class="sectionHead"><div><h3>🍋 同人</h3><p>使用共享 Token，无需填写账号字段。</p></div><span class="miniBadge">共享</span></div><div class="state">可直接进行 Token 检测或打开后台。</div></div>'+
      '<div class="section providerCard" data-p="X"><div class="sectionHead"><div><h3>❎ X-QD</h3><p>独立 Token，仅用于 X 限免正文。</p></div><span class="miniBadge">X</span></div>'+qfUxFieldV015('x_token','X 密钥',xt,'password','可网页登录自动获取，也可手工填写')+'<div class="state">可执行：网页登录、检测、清除。</div></div>'+
      '<div class="section"><div class="sectionHead"><div><h3>执行动作</h3><p>选择动作后点右上角 ✓ 返回执行。</p></div></div><div class="actionGrid" id="actionGrid"></div><div class="state">当前待执行：<b id="actionText">仅保存</b></div></div>'+
      qfUxSpanV015('ux_provider',provider)+qfUxSpanV015('ux_action','不执行')+qfUxSpanV015('ux_xya',xya)+qfUxSpanV015('ux_xyg',xyg)+qfUxSpanV015('ux_xyp',xyp)+qfUxSpanV015('ux_sma',sma)+qfUxSpanV015('ux_smp',smp)+qfUxSpanV015('ux_qtk',qtk)+qfUxSpanV015('ux_qtp',qtp)+qfUxSpanV015('ux_qtb',qtb)+qfUxSpanV015('ux_xt',xt);
    var js='var provider='+JSON.stringify(provider)+',action="不执行";'+
      'var providers=["情无","神魔","晴天","同人","X"],acts={"情无":["不执行","申请游客Token","网页登录","查看使用次数","退出"],"神魔":["不执行","登录","检测","后台","退出"],"晴天":["不执行","登录","检测","后台","退出"],"同人":["不执行","检测","后台"],"X":["不执行","网页登录","检测","清除"]};'+
      'function sync(){document.getElementById("ux_provider").textContent=provider;document.getElementById("ux_action").textContent=action;document.getElementById("ux_xya").textContent=document.getElementById("xy_author").value;document.getElementById("ux_xyg").textContent=document.getElementById("xy_group").value;document.getElementById("ux_xyp").textContent=document.getElementById("xy_pass").value;document.getElementById("ux_sma").textContent=document.getElementById("sm_account").value;document.getElementById("ux_smp").textContent=document.getElementById("sm_password").value;document.getElementById("ux_qtk").textContent=document.getElementById("qt_key").value;document.getElementById("ux_qtp").textContent=document.getElementById("qt_pass").value;document.getElementById("ux_qtb").textContent=document.getElementById("qt_base").value;document.getElementById("ux_xt").textContent=document.getElementById("x_token").value;document.getElementById("providerBadge").textContent=provider;document.getElementById("actionText").textContent=action==="不执行"?"仅保存":action;}'+
      'function renderProviders(){var b=document.getElementById("providerTabs");b.innerHTML="";providers.forEach(function(p){var x=document.createElement("button");x.type="button";x.textContent=p;x.className=p===provider?"on":"";x.onclick=function(){provider=p;action="不执行";renderProviders();renderCards();renderActions();sync();};b.appendChild(x);});}'+
      'function renderCards(){Array.prototype.forEach.call(document.querySelectorAll(".providerCard"),function(c){c.className=c.getAttribute("data-p")===provider?"section providerCard":"section providerCard hide";});}'+
      'function renderActions(){var b=document.getElementById("actionGrid"),arr=acts[provider]||["不执行"];b.innerHTML="";arr.forEach(function(a){var x=document.createElement("button");x.type="button";x.textContent=a==="不执行"?"仅保存":a;x.className=(a===action?"on ":"")+(a==="退出"?"danger":"");x.onclick=function(){action=a;renderActions();sync();};b.appendChild(x);});}'+
      'Array.prototype.forEach.call(document.querySelectorAll("input"),function(x){x.addEventListener("input",sync);});renderProviders();renderCards();renderActions();sync();';
    var body=qfUxOpenV015('账号管理','🔐','Provider','情无按当前“小雨的世界”用户系统接入；其它 Provider 保持原逻辑。',inner,js);
    if(!body)return;
    var map=[['ux_provider','账号管理Provider'],['ux_xya','情无源作者'],['ux_xyg','情无官方反馈群'],['ux_xyp','情无临时口令'],['ux_sma','神魔账号或邮箱'],['ux_smp','神魔密码'],['ux_qtk','晴天密钥'],['ux_qtp','晴天口令'],['ux_qtb','晴天接口地址'],['ux_xt','🎬X佬密钥']];
    qfUxSaveV015(body,map);provider=qfUxReadV015(body,'ux_provider')||provider;
    var action=qfUxReadV015(body,'ux_action')||'不执行';qfMSet423('账号管理动作','不执行',true);
    if(action!=='不执行')qfXyAccountExecV1212(provider,action);
};
/* end qf_xy_auth_v1212 */
'''
if 'qf_xy_auth_v1212' in s.get('loginUrl',''): raise SystemExit('unexpected auth marker already in stable baseline')
s['loginUrl']=s.get('loginUrl','')+auth

js=s['jsLib']; marker='QF_MOD38_PACK='; pi=js.find(marker)
if pi<0: raise SystemExit('QF_MOD38_PACK missing')
ps=js.find('{',pi); pack,plen=json.JSONDecoder().raw_decode(js[ps:])
v=pack.get('limited_qw')
if not isinstance(v,str): raise SystemExit('limited_qw missing')
enc=v[3:] if v.startswith('gz:') else v
enc=enc.replace('-','+').replace('_','/')+'='*((4-len(enc)%4)%4)
mod=gzip.decompress(base64.b64decode(enc)).decode('utf-8')
old='try{var raw=String(j.ajax(String(api))||""),obj=null;'
new='try{var _tk="",_aid="";try{var _src=qfQwSrcV39(this);if(_src){_tk=String(_src.get("qf_xy_user_token_v1212")||"");_aid=String(_src.get("qf_xy_android_id_v1212")||"");}}catch(_ae){}var _req=String(api);if(_tk&&_aid)_req+=","+JSON.stringify({headers:{"X-Sec-Token":_tk,"X-Android-Id":_aid,"Accept":"application/json"}});var raw=String(j.ajax(_req)||""),obj=null;'
if old not in mod: raise SystemExit('stable qfQwContent request anchor missing')
mod=mod.replace(old,new,1)
raw=gzip.compress(mod.encode('utf-8'),9)
pack['limited_qw']='gz:'+base64.urlsafe_b64encode(raw).decode().rstrip('=')
packed=json.dumps(pack,ensure_ascii=False,separators=(',',':'))
s['jsLib']=js[:ps]+packed+js[ps+plen:]

beta.parent.mkdir(parents=True,exist_ok=True)
json.dump(arr,open(beta,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
open(beta,'a',encoding='utf-8').write('\n')

chk=json.load(open(beta,encoding='utf-8'))[0]
assert '情无源作者' in chk['loginUrl'] and '申请游客Token' in chk['loginUrl']
assert 'qf_xy_user_token_v1212' in chk['loginUrl']
assert chk['bookSourceUrl']=='https://m.qidian.com/?qf_source=qidian_next_8d7'

version='1.2.1-beta2'; code=12012; date='2026-09-11'; now='2026-09-11T23:12:00+08:00'
source_url=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={code}'
backup=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={code}'
imp='legado://import/importonline?src='+source_url
detail='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'
summary='Beta 1.2.1-beta2：按最新“小雨的世界”附件重接情无用户系统；游客 Token/网页登录均使用当前接口，免登录正文保持 Stable 1.2.0 基线。'
changes=['废弃 Beta1 错误的邮箱/密码情无登录，不再调用旧 auth.php?action=login / Cookie / X-Content-Token 体系','情无游客授权改为“源作者 + 官方反馈群 + 临时口令 + AndroidId”，POST user_api.php?action=guest','普通账号改为 auth.php?mode=legado&android_id=... 网页注册/登录，回写当前 X-Sec-Token','用户状态/次数通过 user_api.php?action=me + X-Sec-Token + X-Android-Id 获取','limited_qw 仅在 Token 存在时附加当前认证头；未登录正文请求保持 Stable 1.2.0 已真机确认免费链','Stable 1.2.0、评论、角色卡、书友圈、其它 Provider 全部冻结']
tags=['起点','测试版','限免源','情无','小雨用户系统','游客Token','网页登录','免登录回退','X','评论页']
entry={'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'icon':'','channel':'beta','version':version,'updatedAt':date,'tags':tags,'changelog':changes,'sourceUrl':source_url,'backupUrl':backup,'importUrl':imp,'detailUrl':detail,'versionCode':code}

mp=ROOT/'manifest.json'; man=json.load(open(mp,encoding='utf-8')); man['updatedAt']=now
for x in man.get('sources',[]):
    if x.get('id')=='qidian-next-beta':
        x.update({'name':entry['name'],'category':'novel','channel':'beta','version':version,'versionCode':code,'updatedAt':now,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','sourceUrl':source_url,'bookSourceUrl':'https://m.qidian.com/?qf_source=qidian_next_8d7','summary':summary,'tags':tags,'changelog':changes}); break
else:
    man.setdefault('sources',[]).append({'id':'qidian-next-beta','name':entry['name'],'category':'novel','channel':'beta','version':version,'versionCode':code,'updatedAt':now,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','sourceUrl':source_url,'bookSourceUrl':'https://m.qidian.com/?qf_source=qidian_next_8d7','summary':summary,'tags':tags,'changelog':changes})
json.dump(man,open(mp,'w',encoding='utf-8'),ensure_ascii=False,indent=2);open(mp,'a').write('\n')

sp=ROOT/'subscription/beta.json'; sub=json.load(open(sp,encoding='utf-8')); sub['updatedAt']=now; sub['generatedAt']=now
items=sub.setdefault('items',[])
for i,x in enumerate(items):
    if x.get('id')=='qidian-next-beta': items[i]=entry; break
else: items.append(entry)
json.dump(sub,open(sp,'w',encoding='utf-8'),ensure_ascii=False,indent=2);open(sp,'a').write('\n')

np=ROOT/'subscription/novel.json'; nov=json.load(open(np,encoding='utf-8')); nov['updatedAt']=now; nov['generatedAt']=now
nentry=dict(entry); nentry['type']='novel'
nov['items']=[x for x in nov.get('items',[]) if x.get('id') not in ('qidian-next','qidian-next-beta')]+[nentry]
json.dump(nov,open(np,'w',encoding='utf-8'),ensure_ascii=False,indent=2);open(np,'a').write('\n')

dp=ROOT/'rss/data/details/beta/qidian-next.json'; dp.parent.mkdir(parents=True,exist_ok=True)
det={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',version,'情无当前用户系统'],'sections':[{'title':'本轮测试','text':'按最新“小雨的世界”附件重做情无账号系统，Beta1 邮箱/密码方案已废弃。'},{'title':'情无授权','text':'游客：源作者 + 官方反馈群 + 临时口令；普通账号：网页注册/登录。未登录仍走已验证免费正文链。'},{'title':'冻结范围','text':'Stable 1.2.0、评论、角色卡、书友圈、X/神魔/晴天/同人等其它域不变。'}],'sourceUrl':source_url,'backupUrl':backup,'importUrl':imp}
json.dump(det,open(dp,'w',encoding='utf-8'),ensure_ascii=False,indent=2);open(dp,'a').write('\n')

bp=ROOT/'bundles/all-beta.json'; bun=json.load(open(bp,encoding='utf-8')); obj=json.load(open(beta,encoding='utf-8'))[0]
if isinstance(bun,list):
    out=[]; replaced=False
    for x in bun:
        if isinstance(x,dict) and (x.get('bookSourceUrl')=='https://m.qidian.com/?qf_source=qidian_next_8d7' or str(x.get('bookSourceName','')).startswith('🌈 起点增强')):
            if not replaced: out.append(obj); replaced=True
        else: out.append(x)
    if not replaced: out.append(obj)
    bun=out
elif isinstance(bun,dict) and isinstance(bun.get('items'),list):
    out=[]; replaced=False
    for x in bun['items']:
        if isinstance(x,dict) and (x.get('bookSourceUrl')=='https://m.qidian.com/?qf_source=qidian_next_8d7' or str(x.get('bookSourceName','')).startswith('🌈 起点增强')):
            if not replaced: out.append(obj); replaced=True
        else: out.append(x)
    if not replaced: out.append(obj)
    bun['items']=out; bun['updatedAt']=now
else: raise SystemExit('unknown beta bundle shape')
json.dump(bun,open(bp,'w',encoding='utf-8'),ensure_ascii=False,indent=2);open(bp,'a').write('\n')

rp=ROOT/'docs/RELEASE_LOG.md'; old=rp.read_text(encoding='utf-8')
head='## 2026-09-11 · 起点增强 1.2.1-beta2 — 情无当前“小雨”用户系统\n\n- Stable 1.2.0 保持不变；本版从已确认 Stable 基线重新构建，废弃错误 Beta1。\n- 严格对齐最新附件：游客授权字段为“源作者 / 官方反馈群 / 临时口令”，接口为 `user_api.php?action=guest`，并绑定 AndroidId。\n- 普通账号通过 `auth.php?mode=legado&android_id=...` 网页注册/登录，Token 体系为 `X-Sec-Token + X-Android-Id`；不再使用旧邮箱密码/Cookie/X-Content-Token。\n- 情无正文只有在当前 Token 存在时才附加新认证头；未登录继续保持 Stable 1.2.0 已真机确认的免费正文链。\n- 其它域冻结，等待真机验证。\n\n'
rp.write_text(head+old,encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; h=hp.read_text(encoding='utf-8')
note='## 2026-09-11 · Current Beta 1.2.1-beta2 — Xiaoyu current auth\n\n- Stable remains 1.2.0.\n- Supersedes invalid 1.2.1-beta1 email/password attempt.\n- Current Xiaoyu auth is source-author / feedback-group / temporary-password guest token or web registration/login, using X-Sec-Token + X-Android-Id.\n- No-login content fallback remains the verified Stable behavior.\n\n'
hp.write_text(note+h,encoding='utf-8')

for p in ['sources/novel/qidian-next/qidian-next-beta.json','manifest.json','subscription/beta.json','subscription/novel.json','bundles/all-beta.json','rss/data/details/beta/qidian-next.json']:
    json.load(open(p,encoding='utf-8'))
print('beta sha256',hashlib.sha256(beta.read_bytes()).hexdigest())
