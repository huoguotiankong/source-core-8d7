import json
from pathlib import Path
P=Path('sources/novel/qidian-next/qidian-next-beta.json')
arr=json.loads(P.read_text(encoding='utf-8'));s=arr[0]
override=r'''
/* 1.2.1-beta2 · 情无/小雨的世界新版用户系统（最终覆盖） */
function qfQwXYGetB2(k,d){try{var v=source.get(String(k));return v==null?String(d||''):String(v);}catch(e){return String(d||'');}}
function qfQwXYPutB2(k,v){try{source.put(String(k),String(v==null?'':v));}catch(e){}}
function qfQwXYAndroidB2(){var v=qfQwXYGetB2('qf_xy_android_id_v1212','');if(v)return v;try{v=String(java.androidId()||'').trim();}catch(e){}if(!v){var c='0123456789abcdef';for(var i=0;i<16;i++)v+=c.charAt(Math.floor(Math.random()*16));}v=String(v).toUpperCase();qfQwXYPutB2('qf_xy_android_id_v1212',v);return v;}
function qfQwXYReqB2(action,data,auth,method){var h={'Accept':'application/json'};if(method!=='GET')h['Content-Type']='application/json';if(auth){var t=qfQwXYGetB2('qf_xy_user_token_v1212',''),a=qfQwXYAndroidB2();if(t)h['X-Sec-Token']=t;if(a)h['X-Android-Id']=a;}var o={method:method||'POST',headers:h};if((method||'POST')!=='GET')o.body=JSON.stringify(data||{});var raw=String(java.ajax('https://full.hnxianxin.cn/qd/user_api.php?action='+encodeURIComponent(action)+','+JSON.stringify(o))||'');var r=JSON.parse(raw||'{}');if(r.error)throw new Error(String(r.error));return r;}
function qfQwXYStoreB2(r,aid){var u=(r&&r.user)||{};qfQwXYPutB2('qf_xy_user_token_v1212',String((r&&r.token)||''));qfQwXYPutB2('qf_xy_android_id_v1212',String(aid||qfQwXYAndroidB2()));qfQwXYPutB2('qf_xy_user_name_v1212',String(u.username||''));qfQwXYPutB2('qf_xy_user_level_v1212',String(u.level||'guest'));return u;}
function qfQwXYGuestB2(){var a=qfMGet423('情无源作者',''),g=qfMGet423('情无官方反馈群',''),p=qfMGet423('情无临时口令','');if(!a||!g||!p){try{java.toast('请填写源作者、官方反馈群和临时口令');}catch(e){}return;}try{var id=qfQwXYAndroidB2(),r=qfQwXYReqB2('guest',{source_author:a,feedback_group:g,temporary_password:p,android_id:id},false,'POST'),u=qfQwXYStoreB2(r,id);java.toast('游客授权成功：'+String(u.privilege||u.level_name||''));}catch(e){java.toast(String(e&&e.message||e));}}
function qfQwXYWebB2(){var id=qfQwXYAndroidB2();var preload=["window.xySaveLegadoAuth=function(payload){","var u=(payload&&payload.user)||{};","source.put('qf_xy_user_token_v1212',String((payload&&payload.token)||''));","source.put('qf_xy_android_id_v1212',String((payload&&payload.android_id)||'"+id+"'));","source.put('qf_xy_user_name_v1212',String(u.username||''));","source.put('qf_xy_user_level_v1212',String(u.level||'guest'));","return true;","};"].join('\n');java.showBrowser('https://full.hnxianxin.cn/qd/auth.php?mode=legado&android_id='+encodeURIComponent(id),null,preload);try{java.toast('请在网页完成注册/登录，成功后会自动写入 Token');}catch(e){}}
function qfQwXYUsageB2(){if(!qfQwXYGetB2('qf_xy_user_token_v1212','')){try{java.toast('请先申请游客 Token 或网页登录');}catch(e){}return;}try{var r=qfQwXYReqB2('me',{},true,'GET'),u=r.user||{};java.longToast('\n用户：'+String(u.username||'游客用户')+'\n等级：'+String(u.level_name||'--')+'\n权益：'+String(u.privilege||'--')+'\n今日：'+Number(u.today_count||0)+'\n昨日：'+Number(u.yesterday_count||0)+'\n累计：'+Number(u.total_count||0));}catch(e){java.toast(String(e&&e.message||e));}}
function qfQwXYLogoutB2(){try{if(qfQwXYGetB2('qf_xy_user_token_v1212',''))qfQwXYReqB2('logout',{},true,'POST');}catch(e){}qfQwXYPutB2('qf_xy_user_token_v1212','');qfQwXYPutB2('qf_xy_user_name_v1212','');qfQwXYPutB2('qf_xy_user_level_v1212','');try{java.toast('已退出情无用户系统');}catch(e){}}
qfMultiAccountsV423=function(){
 var provider=qfMGet423('账号管理Provider','神魔');if(['情无','神魔','晴天','同人','X'].indexOf(provider)<0)provider='情无';
 var qa=qfMGet423('情无源作者',''),qg=qfMGet423('情无官方反馈群',''),qp=qfMGet423('情无临时口令',''),sma=qfMGet423('神魔账号或邮箱',''),smp=qfMGet423('神魔密码',''),qtk=qfMGet423('晴天密钥',''),qtp=qfMGet423('晴天口令',''),qtb=qfMGet423('晴天接口地址','https://sb.shazi.tk'),xt=qfMGet423('🎬X佬密钥','');
 var tok=qfQwXYGetB2('qf_xy_user_token_v1212',''),un=qfQwXYGetB2('qf_xy_user_name_v1212',''),lv=qfQwXYGetB2('qf_xy_user_level_v1212','');
 var inner='<div class="section"><div class="sectionHead"><div><h3>Provider</h3><p>切换后只展示当前 Provider 的账号字段和可用动作。</p></div><span class="miniBadge" id="providerBadge">'+qfUxEscV015(provider)+'</span></div><div class="tabs" id="providerTabs"></div></div>'+
 '<div class="section providerCard" data-p="情无"><div class="sectionHead"><div><h3>🌙 情无账号</h3><p>新版小雨用户系统：游客授权或网页注册/登录，不使用邮箱密码直登。</p></div><span class="miniBadge">'+(tok?'已授权':'未授权')+'</span></div><div class="state">'+(tok?('当前：'+qfUxEscV015(un||lv||'guest')):'未登录；当前免费正文链仍可使用。')+'</div>'+qfUxFieldV015('qw_author','源作者',qa,'text','')+qfUxFieldV015('qw_group','官方反馈群',qg,'text','')+qfUxFieldV015('qw_pass','临时口令',qp,'password','')+'</div>'+
 '<div class="section providerCard" data-p="神魔"><div class="sectionHead"><div><h3>⚔️ 神魔账号</h3></div></div>'+qfUxFieldV015('sm_account','账号或邮箱',sma,'text','')+qfUxFieldV015('sm_password','密码',smp,'password','')+'</div>'+
 '<div class="section providerCard" data-p="晴天"><div class="sectionHead"><div><h3>☀️ 晴天账号</h3></div></div>'+qfUxFieldV015('qt_key','密钥',qtk,'password','')+qfUxFieldV015('qt_pass','口令',qtp,'password','')+qfUxFieldV015('qt_base','接口地址',qtb,'text','')+'</div>'+
 '<div class="section providerCard" data-p="同人"><div class="sectionHead"><div><h3>🍋 同人</h3><p>共享 Token。</p></div></div></div>'+
 '<div class="section providerCard" data-p="X"><div class="sectionHead"><div><h3>❎ X-QD</h3></div></div>'+qfUxFieldV015('x_token','X 密钥',xt,'password','')+'</div>'+
 '<div class="section"><div class="sectionHead"><div><h3>执行动作</h3><p>选择动作后点右上角 ✓ 返回执行。</p></div></div><div class="actionGrid" id="actionGrid"></div><div class="state">当前待执行：<b id="actionText">仅保存</b></div></div>'+qfUxSpanV015('ux_provider',provider)+qfUxSpanV015('ux_action','不执行')+qfUxSpanV015('ux_qa',qa)+qfUxSpanV015('ux_qg',qg)+qfUxSpanV015('ux_qp',qp)+qfUxSpanV015('ux_sma',sma)+qfUxSpanV015('ux_smp',smp)+qfUxSpanV015('ux_qtk',qtk)+qfUxSpanV015('ux_qtp',qtp)+qfUxSpanV015('ux_qtb',qtb)+qfUxSpanV015('ux_xt',xt);
 var ux='var provider='+JSON.stringify(provider)+',action="不执行";var providers=["情无","神魔","晴天","同人","X"],acts={"情无":["不执行","申请游客Token","网页注册/登录","查看使用次数","退出"],"神魔":["不执行","登录","检测","后台","退出"],"晴天":["不执行","登录","检测","后台","退出"],"同人":["不执行","检测","后台"],"X":["不执行","网页登录","检测","清除"]};function sync(){document.getElementById("ux_provider").textContent=provider;document.getElementById("ux_action").textContent=action;var m=[["qw_author","ux_qa"],["qw_group","ux_qg"],["qw_pass","ux_qp"],["sm_account","ux_sma"],["sm_password","ux_smp"],["qt_key","ux_qtk"],["qt_pass","ux_qtp"],["qt_base","ux_qtb"],["x_token","ux_xt"]];m.forEach(function(z){var a=document.getElementById(z[0]),b=document.getElementById(z[1]);if(a&&b)b.textContent=a.value||"";});document.getElementById("providerBadge").textContent=provider;document.getElementById("actionText").textContent=action==="不执行"?"仅保存":action;}function rp(){var b=document.getElementById("providerTabs");b.innerHTML="";providers.forEach(function(p){var x=document.createElement("button");x.type="button";x.textContent=p;x.className=p===provider?"on":"";x.onclick=function(){provider=p;action="不执行";rp();rc();ra();sync();};b.appendChild(x);});}function rc(){Array.prototype.forEach.call(document.querySelectorAll(".providerCard"),function(c){c.className=c.getAttribute("data-p")===provider?"section providerCard":"section providerCard hide";});}function ra(){var b=document.getElementById("actionGrid"),ar=acts[provider]||["不执行"];b.innerHTML="";ar.forEach(function(a){var x=document.createElement("button");x.type="button";x.textContent=a==="不执行"?"仅保存":a;x.className=(a===action?"on ":"")+(a==="退出"?"danger":"");x.onclick=function(){action=a;ra();sync();};b.appendChild(x);});}Array.prototype.forEach.call(document.querySelectorAll("input"),function(x){x.addEventListener("input",sync);});rp();rc();ra();sync();';
 var body=qfUxOpenV015('账号管理','🔐','Provider','一次只管理一个 Provider。情无采用新版小雨用户系统。',inner,ux);if(!body)return;
 qfUxSaveV015(body,[['ux_provider','账号管理Provider'],['ux_qa','情无源作者'],['ux_qg','情无官方反馈群'],['ux_qp','情无临时口令'],['ux_sma','神魔账号或邮箱'],['ux_smp','神魔密码'],['ux_qtk','晴天密钥'],['ux_qtp','晴天口令'],['ux_qtb','晴天接口地址'],['ux_xt','🎬X佬密钥']]);provider=qfUxReadV015(body,'ux_provider')||provider;var action=qfUxReadV015(body,'ux_action')||'不执行';qfMSet423('账号管理动作','不执行',true);if(action==='不执行')return;if(provider==='情无'){if(action==='申请游客Token')qfQwXYGuestB2();else if(action==='网页注册/登录')qfQwXYWebB2();else if(action==='查看使用次数')qfQwXYUsageB2();else if(action==='退出')qfQwXYLogoutB2();}else qfNextAccountExecV013(provider,action);
};
'''
if '1.2.1-beta2 · 情无/小雨的世界新版用户系统（最终覆盖）' not in s['loginUrl']:s['loginUrl']+='\n'+override
s['bookSourceComment']='v1.2.1-beta2：情无账号体系按“小雨的世界”最新实现重做：游客授权需源作者/官方反馈群/临时口令，普通账号走网页注册/登录并自动写入 Token；Token 与正文模块现有 qf_xy_user_token_v1212 / qf_xy_android_id_v1212 键对齐。未登录仍保留已验证免费正文链。撤销 beta1 的旧邮箱/密码直登方案。'
P.write_text(json.dumps(arr,ensure_ascii=False,indent=2),encoding='utf-8')
version='1.2.1-beta2';code=12012;today='2026-09-12';url='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v=12012'
def patch(o):
    if isinstance(o,dict):
        if o.get('id')=='qidian-next' or o.get('sourceId')=='qidian-next':
            if 'version' in o:o['version']=version
            if 'versionCode' in o:o['versionCode']=code
            if 'url' in o:o['url']=url
            if 'sourceUrl' in o:o['sourceUrl']=url
            if 'updatedAt' in o:o['updatedAt']=today
            if 'summary' in o:o['summary']='起点增强 Beta：情无/小雨新版用户系统接入，游客授权 + 网页注册登录；授权 Token 与正文请求链对齐。'
            if 'changelog' in o:o['changelog']=['情无新版游客授权：源作者/官方反馈群/临时口令','普通账号走网页注册/登录并自动回写 Token','Token 与正文现有认证头键完全对齐','未登录免费正文链保持可用','Stable 1.2.0 不变']
        for v in o.values():patch(v)
    elif isinstance(o,list):
        for v in o:patch(v)
for fp in ['manifest.json','subscription/beta.json','bundles/all-beta.json']:
    q=Path(fp)
    if q.exists():
        d=json.loads(q.read_text(encoding='utf-8'));patch(d)
        if isinstance(d,dict) and 'updatedAt' in d:d['updatedAt']='2026-09-12T00:28:00+08:00'
        q.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
r=Path('docs/RELEASE_LOG.md')
if r.exists():
    t=r.read_text(encoding='utf-8');note='\n## 2026-09-12 · qidian-next 1.2.1-beta2\n- 修正 beta1 情无登录误接旧邮箱/密码体系的问题。\n- 按附件“小雨的世界”最新实现接入游客授权（源作者 / 官方反馈群 / 临时口令）和网页注册/登录。\n- 登录 Token 与现有情无正文模块使用的 `qf_xy_user_token_v1212` / `qf_xy_android_id_v1212` 完全对齐；未登录免费正文链保持不变。\n- Stable 1.2.0 不变。\n'
    if 'qidian-next 1.2.1-beta2' not in t:r.write_text(note+t,encoding='utf-8')
