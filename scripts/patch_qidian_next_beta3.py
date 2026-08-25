import json, pathlib, hashlib
from datetime import datetime, timezone, timedelta

ROOT=pathlib.Path('.')
sp=ROOT/'sources/novel/qidian-next/qidian-next.json'
data=json.loads(sp.read_text(encoding='utf-8'))
assert isinstance(data,list) and len(data)==1
src=data[0]
assert src.get('bookSourceUrl')=='https://m.qidian.com/?qf_source=qidian_next_8d7'
login=str(src.get('loginUrl') or '')
assert 'qidian-next v0.1.1-beta2' in login

patch=r'''
/* qidian-next v0.1.2-beta3 · action return without custom scheme */
qfMultiAccountsV423=function(){
    var sk=['账号操作'];
    var ik=['email','password','情无接口地址','神魔账号或邮箱','神魔密码','晴天密钥','晴天口令','晴天接口地址'];
    var actionOpts=['不执行','情无·登录','情无·检测','情无·网页登录','情无·退出','神魔·登录','神魔·检测','神魔·后台','神魔·退出','晴天·登录','晴天·检测','晴天·后台','晴天·退出','同人·检测Token','同人·打开后台'];
    var inner=
      '<div class="card">'+
      qfMSelect423('执行动作','账号操作',actionOpts,'不执行','修改账号后选择一个动作，再点阅读右上角 ✓ 返回；返回后立即执行。')+
      '<div class="tip">兼容当前阅读版本：不再使用网页按钮触发书源 JS，也不会跳转其它应用。</div></div>'+
      '<div class="card"><div class="lab"><b>🌙 情无</b></div>'+qfMInput423('邮箱','email','text','','QQ邮箱')+qfMInput423('密码','password','password','','情无密码')+qfMInput423('接口地址','情无接口地址','text','http://103.236.85.8:7878/qd','可自定义')+'</div>'+
      '<div class="card"><div class="lab"><b>⚔️ 神魔</b></div>'+qfMInput423('账号或邮箱','神魔账号或邮箱','text','','')+qfMInput423('密码','神魔密码','password','','')+'</div>'+
      '<div class="card"><div class="lab"><b>☀️ 晴天</b></div>'+qfMInput423('密钥','晴天密钥','password','','')+qfMInput423('口令','晴天口令','password','','')+qfMInput423('接口地址','晴天接口地址','text','https://sb.shazi.tk','')+'</div>'+
      '<div class="card"><div class="lab"><b>🍋 同人</b><small>共享 Token 仍在“设置源变量”中维护。</small></div></div>';
    var all=sk.concat(ik);
    for(var i=0;i<all.length;i++)inner+=qfMSpan423('v_'+i,qfMGet423(all[i],i===0?'不执行':''));
    var body=qfMOpen423('🔐 Provider 账号',inner,qfMScript423(sk,[],ik));
    if(!body)return;
    qfMSave423(body,all);
    var a=qfMRead423(body,'v_0');
    qfMSet423('账号操作','不执行',true);
    try{
        if(a==='情无·登录')qfQwNativeLoginV52();
        else if(a==='情无·检测')qfQwNativeCheckV317();
        else if(a==='情无·网页登录')qfQwNativeWebLoginV52();
        else if(a==='情无·退出')qfQwNativeLogoutV317();
        else if(a==='神魔·登录')qfSmLoginV30();
        else if(a==='神魔·检测')qfSmCheckV30();
        else if(a==='神魔·后台')qfSmOpenBackendV30();
        else if(a==='神魔·退出')qfSmLogoutV30();
        else if(a==='晴天·登录')qfQtLoginV328();
        else if(a==='晴天·检测')qfQtCheckV328();
        else if(a==='晴天·后台')qfQtOpenBackendV328();
        else if(a==='晴天·退出')qfQtLogoutV328();
        else if(a==='同人·检测Token')qfTrCheckV102();
        else if(a==='同人·打开后台')qfTrOpenConsoleV102();
        else try{java.toast('账号设置已保存');}catch(_t){}
    }catch(e){try{java.longToast('账号操作失败：'+String(e));}catch(_e){}}
};

qfMultiDiagV423=function(){
    var sk=['诊断操作'];
    var opts=['不执行','Runtime 概览','性能摘要','深度追踪','复制脱敏诊断','清空诊断'];
    var inner='<div class="card">'+
      qfMSelect423('执行诊断','诊断操作',opts,'不执行','选择后点阅读右上角 ✓ 返回，返回后立即执行。')+
      '<div class="tip">本页不再使用 qfnext:// 或任何外部应用跳转。</div></div>';
    inner+=qfMSpan423('v_0',qfMGet423('诊断操作','不执行'));
    var body=qfMOpen423('🩺 诊断工具',inner,qfMScript423(sk,[],[]));
    if(!body)return;
    var a=qfMRead423(body,'v_0');
    qfMSet423('诊断操作','不执行',true);
    try{
        if(a==='Runtime 概览')qfRuntimeDiagShow('overview');
        else if(a==='性能摘要')qfRuntimeDiagShow('performance');
        else if(a==='深度追踪')qfRuntimeDiagShow('performance-deep');
        else if(a==='复制脱敏诊断')qfRuntimeDiagCopy();
        else if(a==='清空诊断')qfRuntimeDiagReset();
        else try{java.toast('未选择诊断动作');}catch(_t){}
    }catch(e){try{java.longToast('诊断操作失败：'+String(e));}catch(_e){}}
};
'''
if 'qidian-next v0.1.2-beta3' not in login:
    src['loginUrl']=login.rstrip()+'\n\n'+patch.strip()+'\n'

# Beta2 custom-scheme bridge is invalid inside startBrowserAwait data pages; remove it.
ov=str(src.get('shouldOverrideUrlLoading') or '')
if 'qfnext://' in ov:
    src.pop('shouldOverrideUrlLoading',None)

src['bookSourceComment']='v0.1.2-beta3：账号管理和诊断工具取消 qfnext:// 自定义 Scheme。账号页改为“账号字段 + 执行动作选择”，诊断页改为“诊断动作选择”；统一使用已真机可用的 startBrowserAwait 改值后点右上角 ✓ 返回机制，再由原生 loginUrl 执行真正动作。保留 Beta2 的 Unicode 唯一控件 ID 修复；搜索/详情/目录/正文/评论/Provider 业务不变。'
now_dt=datetime.now(timezone(timedelta(hours=8)))
src['lastUpdateTime']=int(now_dt.timestamp()*1000)
raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')
sp.write_bytes(raw)
sha=hashlib.sha256(raw).hexdigest()
now=now_dt.isoformat(timespec='seconds'); day=now_dt.date().isoformat()
changes=['移除 qfnext:// 自定义 Scheme，解决跳转其它应用/无应用可执行','账号管理改为选择动作后点右上角 ✓ 返回执行','诊断工具改为选择诊断后点右上角 ✓ 返回执行','保留 Unicode 唯一控件 ID 修复','搜索、目录、正文、评论和 Provider 业务保持不变']

bp=ROOT/'bundles/all-beta.json'; bundle=json.loads(bp.read_text(encoding='utf-8'))
bundle=[src if x.get('bookSourceUrl')==src.get('bookSourceUrl') else x for x in bundle]
bp.write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

subp=ROOT/'subscription/beta.json'; sub=json.loads(subp.read_text(encoding='utf-8')); sub['updatedAt']=now
for x in sub.get('items',[]):
    if x.get('id')=='qidian-next':
        x['version']='0.1.2-beta3'; x['updatedAt']=day; x['changelog']=changes
subp.write_text(json.dumps(sub,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

mp=ROOT/'manifest.json'; manifest=json.loads(mp.read_text(encoding='utf-8')); manifest['updatedAt']=now
for x in manifest.get('sources',[]):
    if x.get('id')=='qidian-next':
        x['version']='0.1.2-beta3'; x['versionCode']=1203; x['updatedAt']=now; x['changelog']=changes; x['sha256']=sha
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/qidian-next.json'; detail=json.loads(dp.read_text(encoding='utf-8')); detail['badges']=['Beta','0.1.2-beta3','小说','新架构']
secs=[s for s in detail.get('sections',[]) if s.get('title') not in ('Beta2 修复','Beta3 修复')]
secs.insert(1,{'title':'Beta3 修复','text':'账号/诊断不再从 data: HTML 发起自定义 Scheme。改为选择动作后点右上角 ✓ 返回，再由书源原生 JS 执行。'})
detail['sections']=secs
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; h=hp.read_text(encoding='utf-8')
h=h.replace('- Current version: `0.1.1-beta2`','- Current version: `0.1.2-beta3`')
import re
h=re.sub(r'- SHA256: `[0-9a-f]{64}`','- SHA256: `'+sha+'`',h,count=1)
note='''\n## Beta3 account/diagnostic fix\n\nBeta2 proved that custom `qfnext://` navigation from a `data:` page opened by `startBrowserAwait` is handled as an Android external-app scheme rather than by the book source's `shouldOverrideUrlLoading`. Beta3 removes that bridge completely. Account and diagnostic actions are represented as normal select values inside the already-working HTML settings-return path; after the user taps the browser ✓ button, `loginUrl` reads the returned value and executes the native source action.\n'''
if '## Beta3 account/diagnostic fix' not in h:h=h.rstrip()+note+'\n'
hp.write_text(h,encoding='utf-8')

kp=ROOT/'docs/KNOWN_ISSUES.md'; known=kp.read_text(encoding='utf-8')
marker='## 14. `startBrowserAwait(data:)` custom scheme is treated as external app navigation'
if marker not in known:
    known=known.rstrip()+f'''\n\n{marker}\n\nObserved in qidian-next Beta2 on real device:\n\n- Account HTML buttons did not execute source actions.\n- Diagnostic buttons using `qfnext://...` displayed Android's "open another app" prompt and then "no app can perform this action".\n\nCause: custom-scheme navigation from the `data:` page is not routed through the source's `shouldOverrideUrlLoading` in this Legado/WebView path.\n\nFix in `0.1.2-beta3`: do not use custom schemes for settings actions. Encode the chosen action as ordinary HTML form/select state, return with the browser ✓ button, then execute the corresponding `loginUrl` function.\n\nStatus: Beta fix pending real-device confirmation.\n'''
    kp.write_text(known+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'; r=rp.read_text(encoding='utf-8')
block=f'''## 2026-08-25 — Qidian Next v0.1.2-beta3\n\nStatus: Beta/Test; account/diagnostic action-return fix awaiting user real-device confirmation.\n\nChanges:\n\n- Removed the Beta2 `qfnext://` custom-scheme bridge after real-device confirmation that Android treats it as external-app navigation.\n- Account Management now saves fields and chooses one action inside the HTML page; the action runs only after tapping the browser ✓ button to return.\n- Diagnostics now uses the same proven select-and-return mechanism.\n- Kept the Unicode unique DOM id fix from Beta2.\n- Search/detail/catalog/content/review/Provider business logic is unchanged.\n- SHA256: `{sha}`.\n\n'''
if '## 2026-08-25 — Qidian Next v0.1.2-beta3' not in r:
    lines=r.splitlines(True); r=(lines[0]+'\n'+block+''.join(lines[1:])) if lines and lines[0].startswith('# RELEASE LOG') else block+r
    rp.write_text(r,encoding='utf-8')

print('patched qidian-next beta3',sha)
