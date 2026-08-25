import json, pathlib, hashlib
from datetime import datetime, timezone, timedelta

ROOT=pathlib.Path('.')
sp=ROOT/'sources/novel/qidian-next/qidian-next.json'
data=json.loads(sp.read_text(encoding='utf-8'))
assert isinstance(data,list) and len(data)==1
src=data[0]
assert src.get('bookSourceUrl')=='https://m.qidian.com/?qf_source=qidian_next_8d7'
login=str(src.get('loginUrl') or '')
assert 'qfMultiAccountsV423' in login and 'qfMultiDiagV423' in login

patch=r'''
/* qidian-next v0.1.1-beta2 · Multi-level settings compatibility fixes */
function qfMIdV011(key){
    var s=String(key==null?'':key),o='qf';
    for(var i=0;i<s.length;i++)o+='_'+s.charCodeAt(i).toString(16);
    return o;
}
qfMSelect423=function(label,key,opts,def,desc){
    var cur=qfMGet423(key,def),id=qfMIdV011(key),h='<div class="row"><div class="lab"><b>'+qfMEsc423(label)+'</b><small>'+qfMEsc423(desc||'')+'</small></div><select id="'+id+'">';
    for(var i=0;i<opts.length;i++)h+='<option value="'+qfMEsc423(opts[i])+'"'+(String(opts[i])===cur?' selected':'')+'>'+qfMEsc423(opts[i])+'</option>';
    return h+'</select></div>';
};
qfMToggle423=function(label,key,def,desc){
    var cur=qfMGet423(key,def)==='✅',id=qfMIdV011(key);
    return '<div class="row"><div class="lab"><b>'+qfMEsc423(label)+'</b><small>'+qfMEsc423(desc||'')+'</small></div><label class="sw"><input id="'+id+'" type="checkbox" '+(cur?'checked':'')+'><span class="track"></span></label></div>';
};
qfMInput423=function(label,key,type,def,desc){
    var id=qfMIdV011(key),cur=qfMGet423(key,def||'');
    return '<div class="row"><div class="lab"><b>'+qfMEsc423(label)+'</b><small>'+qfMEsc423(desc||'')+'</small></div><input id="'+id+'" type="'+(type||'text')+'" value="'+qfMEsc423(cur)+'"></div>';
};
qfMScript423=function(selectKeys,toggleKeys,inputKeys){
    var js='function fid(k){var s=String(k==null?"":k),o="qf";for(var z=0;z<s.length;z++)o+="_"+s.charCodeAt(z).toString(16);return o;}function sync(){';
    for(var i=0;i<selectKeys.length;i++)js+='document.getElementById("v_'+i+'").textContent=document.getElementById("'+qfMIdV011(selectKeys[i])+'").value;';
    var base=selectKeys.length;
    for(var j=0;j<toggleKeys.length;j++)js+='document.getElementById("v_'+(base+j)+'").textContent=document.getElementById("'+qfMIdV011(toggleKeys[j])+'").checked?"✅":"🔳";';
    base+=toggleKeys.length;
    for(var n=0;n<inputKeys.length;n++)js+='document.getElementById("v_'+(base+n)+'").textContent=document.getElementById("'+qfMIdV011(inputKeys[n])+'").value;';
    js+='}document.addEventListener("change",sync);document.addEventListener("input",sync);sync();';
    return js;
};
function qfNextTakeActionV011(){
    var a='';try{a=String(source.get('qf_next_action_v011')||'');source.remove('qf_next_action_v011');}catch(_e){}
    return a;
}
function qfNextAccountRunV011(a){
    try{
        if(a==='qw-login')return qfQwNativeLoginV52();
        if(a==='qw-check')return qfQwNativeCheckV317();
        if(a==='qw-web')return qfQwNativeWebLoginV52();
        if(a==='qw-logout')return qfQwNativeLogoutV317();
        if(a==='sm-login')return qfSmLoginV30();
        if(a==='sm-check')return qfSmCheckV30();
        if(a==='sm-backend')return qfSmOpenBackendV30();
        if(a==='sm-logout')return qfSmLogoutV30();
        if(a==='qt-login')return qfQtLoginV328();
        if(a==='qt-check')return qfQtCheckV328();
        if(a==='qt-backend')return qfQtOpenBackendV328();
        if(a==='qt-logout')return qfQtLogoutV328();
        if(a==='tr-check')return qfTrCheckV102();
        if(a==='tr-console')return qfTrOpenConsoleV102();
        if(a==='save-only'){try{java.toast('账号设置已保存');}catch(_t){}return true;}
    }catch(e){try{java.longToast('账号操作失败：'+String(e));}catch(_e){}}
}
qfMultiAccountsV423=function(){
    try{source.remove('qf_next_action_v011');}catch(_e){}
    var ik=['email','password','情无接口地址','神魔账号或邮箱','神魔密码','晴天密钥','晴天口令','晴天接口地址'];
    var inner=
      '<div class="card"><div class="lab"><b>🌙 情无</b><small>填写后点动作按钮；看到提示后点右上角 ✓ 返回执行。</small></div>'+qfMInput423('邮箱','email','text','','QQ邮箱')+qfMInput423('密码','password','password','','情无密码')+qfMInput423('接口地址','情无接口地址','text','http://103.236.85.8:7878/qd','可自定义')+'<div class="grid"><button class="act primary" onclick="fire(\'qw-login\')">登录</button><button class="act" onclick="fire(\'qw-check\')">检测</button><button class="act" onclick="fire(\'qw-web\')">网页登录</button><button class="act" onclick="fire(\'qw-logout\')">退出</button></div></div>'+ 
      '<div class="card"><div class="lab"><b>⚔️ 神魔</b></div>'+qfMInput423('账号或邮箱','神魔账号或邮箱','text','','')+qfMInput423('密码','神魔密码','password','','')+'<div class="grid"><button class="act primary" onclick="fire(\'sm-login\')">登录</button><button class="act" onclick="fire(\'sm-check\')">检测</button><button class="act" onclick="fire(\'sm-backend\')">后台</button><button class="act" onclick="fire(\'sm-logout\')">退出</button></div></div>'+ 
      '<div class="card"><div class="lab"><b>☀️ 晴天</b></div>'+qfMInput423('密钥','晴天密钥','password','','')+qfMInput423('口令','晴天口令','password','','')+qfMInput423('接口地址','晴天接口地址','text','https://sb.shazi.tk','')+'<div class="grid"><button class="act primary" onclick="fire(\'qt-login\')">登录</button><button class="act" onclick="fire(\'qt-check\')">检测</button><button class="act" onclick="fire(\'qt-backend\')">后台</button><button class="act" onclick="fire(\'qt-logout\')">退出</button></div></div>'+ 
      '<div class="card"><div class="lab"><b>🍋 同人</b></div><div class="grid"><button class="act primary" onclick="fire(\'tr-check\')">检测共享Token</button><button class="act" onclick="fire(\'tr-console\')">打开后台</button></div></div>'+ 
      '<div class="card"><button class="act primary" style="width:100%" onclick="fire(\'save-only\')">💾 只保存账号设置</button><div class="tip">动作会先把当前输入写入阅读登录信息，再在返回后执行。</div></div>';
    var js=qfMScript423([],[],ik)+'function fire(a){sync();var q=[],ks='+JSON.stringify(ik)+';for(var i=0;i<ks.length;i++){var el=document.getElementById(fid(ks[i]));if(el)q.push(encodeURIComponent(ks[i])+"="+encodeURIComponent(el.value||""));}document.title="已选择："+a+"；请点右上角✓";location.href="qfnext://account?action="+encodeURIComponent(a)+"&"+q.join("&");}';
    qfMOpen423('🔐 Provider 账号',inner,js);
    var a=qfNextTakeActionV011();if(a)qfNextAccountRunV011(a);
};
qfMultiDiagV423=function(){
    try{source.remove('qf_next_action_v011');}catch(_e){}
    var inner='<div class="card"><div class="grid"><button class="act primary" onclick="fire(\'overview\')">Runtime 概览</button><button class="act" onclick="fire(\'performance\')">性能摘要</button><button class="act" onclick="fire(\'performance-deep\')">深度追踪</button><button class="act" onclick="fire(\'copy\')">复制脱敏诊断</button><button class="act" onclick="fire(\'reset\')">清空诊断</button></div><div class="tip">点击动作后看到提示，再点右上角 ✓ 返回执行。</div></div>';
    qfMOpen423('🩺 诊断工具',inner,'function fire(a){document.title="已选择："+a+"；请点右上角✓";location.href="qfnext://diag?action="+encodeURIComponent(a);}');
    var a=qfNextTakeActionV011();
    try{if(a==='copy')qfRuntimeDiagCopy();else if(a==='reset')qfRuntimeDiagReset();else if(a)qfRuntimeDiagShow(a);}catch(e){try{java.longToast('诊断操作失败：'+String(e));}catch(_e){}}
};
'''
if 'qidian-next v0.1.1-beta2' not in login:
    src['loginUrl']=login.rstrip()+'\n\n'+patch.strip()+'\n'

old_override=str(src.get('shouldOverrideUrlLoading') or '').strip()
assert not old_override or 'qfnext://' in old_override
src['shouldOverrideUrlLoading']=r'''var u=String(url||'');
if(/^qfnext:\/\//i.test(u)){
  try{
    function pv(k){var m=u.match(new RegExp('[?&]'+k+'=([^&]*)'));return m?decodeURIComponent(String(m[1]||'').replace(/\+/g,' ')):'';}
    var a=pv('action');
    var keys=['email','password','情无接口地址','神魔账号或邮箱','神魔密码','晴天密钥','晴天口令','晴天接口地址'];
    var hm=new Packages.java.util.HashMap();
    for(var i=0;i<keys.length;i++){var v=pv(encodeURIComponent(keys[i]));hm.put(keys[i],v);}
    try{java.upLoginData(hm);}catch(_u){}
    try{source.put('qf_next_action_v011',a);}catch(_s){}
    try{java.toast('已选择：'+a+'；点右上角✓返回执行');}catch(_t){}
  }catch(e){try{java.longToast('动作桥接失败：'+String(e));}catch(_e){}}
  true;
}else{
  false;
}'''

src['bookSourceComment']='v0.1.1-beta2：修复新架构登录设置中的账号管理与诊断工具；HTML 中文字段改为 Unicode 唯一 ID，解决账号/设置字段 ID 冲突；账号和诊断动作改用 qfnext:// WebView 原生拦截桥接，不再依赖 DOM action 回传。其它搜索/详情/目录/正文/评论与 Provider 业务保持 beta1。'
src['lastUpdateTime']=int(datetime.now(timezone(timedelta(hours=8))).timestamp()*1000)
raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')
sp.write_bytes(raw)
sha=hashlib.sha256(raw).hexdigest()

bp=ROOT/'bundles/all-beta.json'; bundle=json.loads(bp.read_text(encoding='utf-8'))
found=False
for i,x in enumerate(bundle):
    if x.get('bookSourceUrl')==src.get('bookSourceUrl'):
        bundle[i]=src;found=True
assert found
bp.write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

now_dt=datetime.now(timezone(timedelta(hours=8))); now=now_dt.isoformat(timespec='seconds'); day=now_dt.date().isoformat()
changes=['修复账号管理与诊断工具动作回传失效','中文设置字段使用 Unicode 唯一控件 ID，消除同长度中文键碰撞','账号/诊断动作改用 qfnext:// WebView 拦截桥接','保持 beta1 搜索、目录、正文、评论和 Provider 业务不变']
subp=ROOT/'subscription/beta.json'; sub=json.loads(subp.read_text(encoding='utf-8')); sub['updatedAt']=now
for x in sub.get('items',[]):
    if x.get('id')=='qidian-next':
        x['version']='0.1.1-beta2'; x['updatedAt']=day; x['changelog']=changes
subp.write_text(json.dumps(sub,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

mp=ROOT/'manifest.json'; manifest=json.loads(mp.read_text(encoding='utf-8')); manifest['updatedAt']=now
for x in manifest.get('sources',[]):
    if x.get('id')=='qidian-next':
        x['version']='0.1.1-beta2'; x['versionCode']=1102; x['updatedAt']=now; x['changelog']=changes; x['sha256']=sha
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/qidian-next.json'; detail=json.loads(dp.read_text(encoding='utf-8')); detail['badges']=['Beta','0.1.1-beta2','小说','新架构']
if not any(s.get('title')=='Beta2 修复' for s in detail.get('sections',[])):
    detail['sections'].insert(1,{'title':'Beta2 修复','text':'账号管理与诊断工具改为 WebView 自定义 URL 动作桥接；同时修复中文设置字段 DOM ID 冲突。'})
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; h=hp.read_text(encoding='utf-8')
h=h.replace('- Current version: `0.1.0-beta1`','- Current version: `0.1.1-beta2`')
import re
h=re.sub(r'- SHA256: `[0-9a-f]{64}`','- SHA256: `'+sha+'`',h,count=1)
note='''\n## Beta2 account/diagnostic fix\n\nReal-device testing of Beta1 was broadly normal, but Account Management and Diagnostics were faulty. Root causes identified in the login HTML layer:\n\n- Chinese setting keys were converted to underscore-only DOM ids, so same-length Chinese keys collided.\n- account/diagnostic actions relied on returning mutated DOM state from `startBrowserAwait`, which is not reliable in the current Legado WebView path.\n\nBeta2 uses Unicode-derived unique DOM ids and a `qfnext://` custom-URL bridge intercepted by `shouldOverrideUrlLoading`. Business reading modules are unchanged.\n'''
if '## Beta2 account/diagnostic fix' not in h:h=h.rstrip()+note+'\n'
hp.write_text(h,encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'; log=rp.read_text(encoding='utf-8'); marker='## 2026-08-25 — Qidian Next v0.1.1-beta2'
if marker not in log:
    block=marker+'\n\nStatus: Beta/Test; account/diagnostic compatibility fix awaiting user real-device confirmation.\n\nChanges:\n\n- Fixed duplicate DOM ids generated from Chinese setting keys.\n- Reworked Account Management and Diagnostics actions to use `qfnext://` WebView interception instead of mutated-DOM action return.\n- Kept search/detail/catalog/content/review/Provider business logic unchanged from Beta1.\n- SHA256: `'+sha+'`.\n\n'
    lines=log.splitlines(True); log=(lines[0]+'\n'+block+''.join(lines[1:])) if lines and lines[0].startswith('# RELEASE LOG') else block+log
    rp.write_text(log,encoding='utf-8')
print('qidian-next beta2',len(raw),sha)
