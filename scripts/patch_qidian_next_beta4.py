import json, pathlib, hashlib
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
sp = ROOT / 'sources/novel/qidian-next/qidian-next.json'
data = json.loads(sp.read_text(encoding='utf-8'))
assert isinstance(data, list) and len(data) == 1
src = data[0]
assert src.get('bookSourceUrl') == 'https://m.qidian.com/?qf_source=qidian_next_8d7'
login = str(src.get('loginUrl') or '')
assert 'qfMIdV011' in login and 'qfMultiAccountsV423' in login and 'qfMultiDiagV423' in login

patch = r'''
/* qidian-next v0.1.3-beta4 · compact account/diagnostics UI */
function qfNextAccountExecV013(provider,action){
    provider=String(provider||'');action=String(action||'');
    if(!action || action==='不执行')return;
    try{
        if(provider==='情无'){
            if(action==='登录')return qfQwNativeLoginV52();
            if(action==='检测')return qfQwNativeCheckV317();
            if(action==='网页登录')return qfQwNativeWebLoginV52();
            if(action==='退出')return qfQwNativeLogoutV317();
        }
        if(provider==='神魔'){
            if(action==='登录')return qfSmLoginV30();
            if(action==='检测')return qfSmCheckV30();
            if(action==='后台')return qfSmOpenBackendV30();
            if(action==='退出')return qfSmLogoutV30();
        }
        if(provider==='晴天'){
            if(action==='登录')return qfQtLoginV328();
            if(action==='检测')return qfQtCheckV328();
            if(action==='后台')return qfQtOpenBackendV328();
            if(action==='退出')return qfQtLogoutV328();
        }
        if(provider==='同人'){
            if(action==='检测')return qfTrCheckV102();
            if(action==='后台')return qfTrOpenConsoleV102();
        }
        try{java.toast(provider+' 不支持「'+action+'」');}catch(_t){}
    }catch(e){try{java.longToast('账号操作失败：'+String(e));}catch(_e){}}
}
qfMultiAccountsV423=function(){
    var sk=['账号管理Provider','账号管理动作'];
    var ik=['email','password','情无接口地址','神魔账号或邮箱','神魔密码','晴天密钥','晴天口令','晴天接口地址'];
    var provider=qfMGet423('账号管理Provider','情无');
    var inner='<div class="card">'+
      qfMSelect423('Provider','账号管理Provider',['情无','神魔','晴天','同人'],provider,'一次只管理一个 Provider，页面会自动切换对应账号字段。')+
      '</div>'+
      '<div id="pv_qw" class="card"><div class="lab"><b>🌙 情无</b><small>邮箱 / 密码 / 接口地址</small></div>'+qfMInput423('邮箱','email','text','','QQ邮箱')+qfMInput423('密码','password','password','','情无密码')+qfMInput423('接口地址','情无接口地址','text','http://103.236.85.8:7878/qd','可自定义')+'</div>'+
      '<div id="pv_sm" class="card"><div class="lab"><b>⚔️ 神魔</b><small>账号或邮箱 / 密码</small></div>'+qfMInput423('账号或邮箱','神魔账号或邮箱','text','','')+qfMInput423('密码','神魔密码','password','','')+'</div>'+
      '<div id="pv_qt" class="card"><div class="lab"><b>☀️ 晴天</b><small>密钥 / 口令 / 接口地址</small></div>'+qfMInput423('密钥','晴天密钥','password','','')+qfMInput423('口令','晴天口令','password','','')+qfMInput423('接口地址','晴天接口地址','text','https://sb.shazi.tk','')+'</div>'+
      '<div id="pv_tr" class="card"><div class="lab"><b>🍋 同人</b><small>共享 Token 由书源内部维护，无需填写账号。</small></div><div class="tip">可执行：检测、后台。</div></div>'+
      '<div class="card">'+qfMSelect423('执行动作','账号管理动作',['不执行','登录','检测','网页登录','后台','退出'],'不执行','选好动作后点击阅读右上角 ✓；返回后立即执行。单纯保存账号时保持“不执行”。')+'</div>';
    var all=sk.concat(ik);
    for(var i=0;i<all.length;i++)inner+=qfMSpan423('v_'+i,qfMGet423(all[i],all[i]==='账号管理Provider'?provider:(all[i]==='账号管理动作'?'不执行':'')));
    var pid=qfMIdV011('账号管理Provider');
    var js=qfMScript423(sk,[],ik)+
      'function showPv(){var p=document.getElementById("'+pid+'").value;var map={"情无":"pv_qw","神魔":"pv_sm","晴天":"pv_qt","同人":"pv_tr"};["pv_qw","pv_sm","pv_qt","pv_tr"].forEach(function(x){document.getElementById(x).style.display=(x===map[p]?"block":"none");});sync();}document.getElementById("'+pid+'").addEventListener("change",showPv);showPv();';
    var body=qfMOpen423('🔐 Provider 账号',inner,js);
    if(!body)return;
    qfMSave423(body,all);
    var p=qfMRead423(body,'v_0')||provider;
    var a=qfMRead423(body,'v_1')||'不执行';
    qfMSet423('账号管理Provider',p,true);
    qfMSet423('账号管理动作','不执行',true);
    if(a!=='不执行')qfNextAccountExecV013(p,a);
};
qfMultiDiagV423=function(){
    var key='诊断动作';
    var inner='<div class="card">'+qfMSelect423('诊断动作',key,['不执行','Runtime 概览','性能摘要','深度追踪','复制脱敏诊断','清空诊断'],'不执行','选择后点击阅读右上角 ✓，返回后立即执行。')+'</div>'+
      '<div class="card"><div class="tip">常规排查优先使用 Runtime 概览；性能问题再用性能摘要/深度追踪。</div></div>'+qfMSpan423('v_0','不执行');
    var body=qfMOpen423('🩺 诊断工具',inner,qfMScript423([key],[],[]));
    if(!body)return;
    var a=qfMRead423(body,'v_0')||'不执行';
    qfMSet423(key,'不执行',true);
    try{
        if(a==='Runtime 概览')qfRuntimeDiagShow('overview');
        else if(a==='性能摘要')qfRuntimeDiagShow('performance');
        else if(a==='深度追踪')qfRuntimeDiagShow('performance-deep');
        else if(a==='复制脱敏诊断')qfRuntimeDiagCopy();
        else if(a==='清空诊断')qfRuntimeDiagReset();
    }catch(e){try{java.longToast('诊断操作失败：'+String(e));}catch(_e){}}
};
'''
if 'qidian-next v0.1.3-beta4' not in login:
    src['loginUrl'] = login.rstrip() + '\n\n' + patch.strip() + '\n'

src['bookSourceComment'] = 'v0.1.3-beta4：优化账号管理和诊断工具交互。账号管理不再把 Provider×动作组合成超长列表，改为独立 Provider 选择 + 6 项动作选择，并只显示当前 Provider 的账号字段；诊断工具改为紧凑单选。动作执行后自动恢复“不执行”。保留 Unicode 唯一控件 ID；搜索/详情/目录/正文/评论/Provider 业务不变。'
src['lastUpdateTime'] = int(datetime.now(timezone(timedelta(hours=8))).timestamp() * 1000)
raw = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
sp.write_bytes(raw)
sha = hashlib.sha256(raw).hexdigest()

bp = ROOT / 'bundles/all-beta.json'
bundle = json.loads(bp.read_text(encoding='utf-8'))
bundle = [src if x.get('bookSourceUrl') == src.get('bookSourceUrl') else x for x in bundle]
bp.write_text(json.dumps(bundle, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

now_dt = datetime.now(timezone(timedelta(hours=8)))
now = now_dt.isoformat(timespec='seconds')
day = now_dt.date().isoformat()
changes = [
    '账号管理拆分为 Provider 选择 + 动作选择，取消超长组合列表',
    '账号页只显示当前 Provider 对应字段，减少页面长度',
    '动作执行后自动恢复“不执行”，避免重复触发',
    '诊断工具改为紧凑单选流程',
    '搜索、目录、正文、评论和 Provider 业务保持不变'
]
subp = ROOT / 'subscription/beta.json'
sub = json.loads(subp.read_text(encoding='utf-8'))
sub['updatedAt'] = now
for x in sub.get('items', []):
    if x.get('id') == 'qidian-next':
        x['version'] = '0.1.3-beta4'; x['updatedAt'] = day; x['changelog'] = changes
subp.write_text(json.dumps(sub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

mp = ROOT / 'manifest.json'
manifest = json.loads(mp.read_text(encoding='utf-8'))
manifest['updatedAt'] = now
for x in manifest.get('sources', []):
    if x.get('id') == 'qidian-next':
        x['version'] = '0.1.3-beta4'; x['versionCode'] = 1304; x['updatedAt'] = now; x['changelog'] = changes; x['sha256'] = sha
mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

dp = ROOT / 'rss/data/details/qidian-next.json'
detail = json.loads(dp.read_text(encoding='utf-8'))
detail['badges'] = ['Beta', '0.1.3-beta4', '小说', '新架构']
detail['sections'].insert(1, {'title':'Beta4 交互优化','text':'账号管理改为 Provider + 动作双选择并只显示当前 Provider 字段；诊断工具改为紧凑动作选择。'})
dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

hp = ROOT / 'docs/sources/qidian-next/PROJECT_HANDOFF.md'
h = hp.read_text(encoding='utf-8')
h = h.replace('- Current version: `0.1.2-beta3`', '- Current version: `0.1.3-beta4`')
import re
h = re.sub(r'- SHA256: `[0-9a-f]{64}`', '- SHA256: `'+sha+'`', h, count=1)
note = '\n## Beta4 account UX\n\nBeta3 removed the incompatible custom scheme but exposed an oversized Provider×action selector. Beta4 keeps the proven return-and-execute mechanism while splitting the UI into a short Provider selector and short action selector; only the active Provider card is shown. Diagnostics use the same compact return-and-execute pattern.\n'
if '## Beta4 account UX' not in h: h += note
hp.write_text(h, encoding='utf-8')

rp = ROOT / 'docs/RELEASE_LOG.md'
r = rp.read_text(encoding='utf-8')
entry = f'''# RELEASE LOG\n\n## {day} — Qidian Next v0.1.3-beta4\n\nStatus: Beta/Test; compact account/diagnostic UX awaiting user real-device confirmation.\n\nChanges:\n\n- Split Account Management into Provider selection and short action selection instead of one oversized combined list.\n- Show only the active Provider account card.\n- Reset the selected action after execution to prevent accidental repeat operations.\n- Simplified Diagnostics to the same compact return-and-execute flow.\n- Reading business modules remain unchanged.\n- SHA256: `{sha}`.\n\n'''
if 'Qidian Next v0.1.3-beta4' not in r:
    if r.startswith('# RELEASE LOG\n'):
        r = entry + r[len('# RELEASE LOG\n'):].lstrip('\n')
    else:
        r = entry + r
rp.write_text(r, encoding='utf-8')

print('beta4 sha256', sha)
