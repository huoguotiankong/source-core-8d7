import json, pathlib, hashlib
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
SP = ROOT / 'sources/novel/qidian-next/qidian-next.json'
data = json.loads(SP.read_text(encoding='utf-8'))
assert isinstance(data, list) and len(data) == 1
src = data[0]
assert src.get('bookSourceUrl') == 'https://m.qidian.com/?qf_source=qidian_next_8d7'
login = str(src.get('loginUrl') or '')
assert 'qfSmLoginV30' in login and 'qfNextAccountExecV013' in login

PATCH = r'''
/* qidian-next v0.1.4-beta5 · restore Shenmo account dependencies */
function qfSmCtxV30(){return {source:source,java:java,cookie:cookie,cache:(typeof cache!=="undefined"?cache:null)};}
function qfSmInputV30(name){
    var v="";
    try{if(typeof result!=="undefined"&&result&&result[name]!=null)v=String(result[name]);}catch(e0){}
    if(v)return v;
    try{v=String(Map(name)||"");}catch(e1){}
    if(v)return v;
    try{
        var m=source.getLoginInfoMap?source.getLoginInfoMap():null;
        var x=m&&(m.get?m.get(name):m[name]);
        if(x!=null)v=String(x);
    }catch(e2){}
    if(v)return v;
    try{
        var j=JSON.parse(String(source.getLoginInfo()||"{}"))||{};
        if(j[name]!=null)v=String(j[name]);
    }catch(e3){}
    return v;
}
function qfSmTrimV30(v){return String(v==null?"":v).replace(/^[\s\u3000]+|[\s\u3000]+$/g,"");}
function qfSmSaveCredsV30(acc,pw){
    try{
        var m=new Packages.java.util.HashMap();
        if(acc!=null)m.put("神魔账号或邮箱",String(acc));
        if(pw!=null)m.put("神魔密码",String(pw));
        java.upLoginData(m);
    }catch(e0){}
}
function qfNextActionsV014(provider){
    provider=String(provider||'情无');
    if(provider==='情无')return ['不执行','登录','检测','网页登录','退出'];
    if(provider==='神魔')return ['不执行','登录','检测','后台','退出'];
    if(provider==='晴天')return ['不执行','登录','检测','后台','退出'];
    if(provider==='同人')return ['不执行','检测','后台'];
    return ['不执行'];
}
qfMultiAccountsV423=function(){
    var sk=['账号管理Provider','账号管理动作'];
    var ik=['email','password','情无接口地址','神魔账号或邮箱','神魔密码','晴天密钥','晴天口令','晴天接口地址'];
    var provider=qfMGet423('账号管理Provider','情无');
    if(['情无','神魔','晴天','同人'].indexOf(provider)<0)provider='情无';
    var actions=qfNextActionsV014(provider);
    var savedAction=qfMGet423('账号管理动作','不执行');
    if(actions.indexOf(savedAction)<0)savedAction='不执行';
    var inner='<div class="card">'+
      qfMSelect423('Provider','账号管理Provider',['情无','神魔','晴天','同人'],provider,'一次只管理一个 Provider；切换后只显示对应账号字段。')+
      qfMSelect423('执行动作','账号管理动作',actions,savedAction,'选好动作后点右上角 ✓ 返回执行；只保存账号时保持“不执行”。')+
      '</div>'+
      '<div class="card" id="qf_card_qw"><div class="lab"><b>🌙 情无</b><small>邮箱 / 密码 / 接口地址</small></div>'+qfMInput423('邮箱','email','text','','QQ邮箱')+qfMInput423('密码','password','password','','情无密码')+qfMInput423('接口地址','情无接口地址','text','http://103.236.85.8:7878/qd','可自定义')+'</div>'+
      '<div class="card" id="qf_card_sm"><div class="lab"><b>⚔️ 神魔</b><small>账号或邮箱 / 密码</small></div>'+qfMInput423('账号或邮箱','神魔账号或邮箱','text','','')+qfMInput423('密码','神魔密码','password','','')+'</div>'+
      '<div class="card" id="qf_card_qt"><div class="lab"><b>☀️ 晴天</b><small>密钥 / 口令 / 接口地址</small></div>'+qfMInput423('密钥','晴天密钥','password','','')+qfMInput423('口令','晴天口令','password','','')+qfMInput423('接口地址','晴天接口地址','text','https://sb.shazi.tk','')+'</div>'+
      '<div class="card" id="qf_card_tr"><div class="lab"><b>🍋 同人</b><small>使用共享 Token；无需填写账号字段。</small></div></div>';
    var all=sk.concat(ik);
    for(var i=0;i<all.length;i++)inner+=qfMSpan423('v_'+i,qfMGet423(all[i],all[i]==='账号管理Provider'?provider:(all[i]==='账号管理动作'?'不执行':'')));
    var pId=qfMIdV011('账号管理Provider'),aId=qfMIdV011('账号管理动作');
    var js=qfMScript423(sk,[],ik)+
      'var __pid='+JSON.stringify(pId)+',__aid='+JSON.stringify(aId)+';'+
      'var __am={"情无":["不执行","登录","检测","网页登录","退出"],"神魔":["不执行","登录","检测","后台","退出"],"晴天":["不执行","登录","检测","后台","退出"],"同人":["不执行","检测","后台"]};'+
      'function __refresh(reset){var p=document.getElementById(__pid).value||"情无";var ids={"情无":"qf_card_qw","神魔":"qf_card_sm","晴天":"qf_card_qt","同人":"qf_card_tr"};for(var k in ids){var c=document.getElementById(ids[k]);if(c)c.style.display=(k===p?"block":"none");}var a=document.getElementById(__aid),old=a.value,arr=__am[p]||["不执行"];a.innerHTML="";for(var i=0;i<arr.length;i++){var o=document.createElement("option");o.value=arr[i];o.textContent=arr[i];a.appendChild(o);}a.value=(!reset&&arr.indexOf(old)>=0)?old:"不执行";sync();}'+
      'document.getElementById(__pid).addEventListener("change",function(){__refresh(true);});__refresh(false);';
    var body=qfMOpen423('🔐 Provider 账号',inner,js);
    if(!body)return;
    qfMSave423(body,all);
    provider=qfMRead423(body,'v_0')||'情无';
    var action=qfMRead423(body,'v_1')||'不执行';
    qfMSet423('账号管理Provider',provider,true);
    qfMSet423('账号管理动作','不执行',true);
    if(action!=='不执行')qfNextAccountExecV013(provider,action);
};
'''

if 'qidian-next v0.1.4-beta5' not in login:
    src['loginUrl'] = login.rstrip() + '\n\n' + PATCH.strip() + '\n'

# Keep the static first-level UI, but update its stale header text.
try:
    ui = json.loads(src.get('loginUi') or '[]')
    if isinstance(ui, list) and ui:
        ui[0]['name'] = '🌈 起点助手 · v0.1.4-beta5'
        src['loginUi'] = json.dumps(ui, ensure_ascii=False, separators=(',', ':'))
except Exception:
    pass

src['bookSourceComment'] = ('v0.1.4-beta5：修复神魔账号链历史依赖缺失。恢复 qfSmCtxV30 / qfSmInputV30 / '
                            'qfSmTrimV30 / qfSmSaveCredsV30 四个成熟辅助函数；账号动作列表改为随 Provider 动态变化，'
                            '神魔仅显示登录/检测/后台/退出，不再出现不支持的网页登录。其它搜索/详情/目录/正文/评论/Provider 业务不变。')
now_dt = datetime.now(timezone(timedelta(hours=8)))
now = now_dt.isoformat(timespec='seconds')
day = now_dt.date().isoformat()
src['lastUpdateTime'] = int(now_dt.timestamp() * 1000)

raw = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
SP.write_bytes(raw)
sha = hashlib.sha256(raw).hexdigest()

# Beta bundle: replace only qidian-next; preserve every other Beta source.
bp = ROOT / 'bundles/all-beta.json'
bundle = json.loads(bp.read_text(encoding='utf-8'))
replaced = False
for i, item in enumerate(bundle):
    if item.get('bookSourceUrl') == src.get('bookSourceUrl') or item.get('bookSourceName') == '🌈 起点助手·新架构':
        bundle[i] = src
        replaced = True
if not replaced:
    bundle.append(src)
bp.write_text(json.dumps(bundle, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

changes = [
    '修复神魔登录 ReferenceError：恢复历史误删的 qfSmCtxV30 / qfSmInputV30 / qfSmTrimV30 / qfSmSaveCredsV30',
    '账号动作列表真正随 Provider 动态变化',
    '神魔只显示登录 / 检测 / 后台 / 退出，不再出现不支持的网页登录',
    '更新一级登录页版本标题；其它阅读业务模块保持不变'
]

subp = ROOT / 'subscription/beta.json'
sub = json.loads(subp.read_text(encoding='utf-8'))
sub['updatedAt'] = now
for item in sub.get('items', []):
    if item.get('id') == 'qidian-next':
        item['version'] = '0.1.4-beta5'
        item['updatedAt'] = day
        item['changelog'] = changes
subp.write_text(json.dumps(sub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

mp = ROOT / 'manifest.json'
manifest = json.loads(mp.read_text(encoding='utf-8'))
manifest['updatedAt'] = now
for item in manifest.get('sources', []):
    if item.get('id') == 'qidian-next':
        item['version'] = '0.1.4-beta5'
        item['versionCode'] = 1405
        item['updatedAt'] = now
        item['changelog'] = changes
        item['sha256'] = sha
mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

dp = ROOT / 'rss/data/details/qidian-next.json'
detail = json.loads(dp.read_text(encoding='utf-8'))
detail['badges'] = ['Beta', '0.1.4-beta5', '小说', '新架构']
sections = detail.setdefault('sections', [])
sections.insert(1, {
    'title': 'Beta5 神魔账号修复',
    'text': '恢复神魔账号链历史误删的四个上下文/输入辅助函数；账号动作列表随 Provider 动态变化，神魔只保留登录、检测、后台、退出。'
})
dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

hp = ROOT / 'docs/sources/qidian-next/PROJECT_HANDOFF.md'
h = hp.read_text(encoding='utf-8')
h = h.replace('- Current version: `0.1.3-beta4`', '- Current version: `0.1.4-beta5`')
h = h.replace('- SHA256: `9c8b63ce4c000456d47bfd3d2284416680292ee66dfbc3d358395eedff28b896`', '- SHA256: `' + sha + '`')
note = '''\n## Beta5 Shenmo account dependency repair\n\nReal-device Beta4 exposed `ReferenceError: qfSmCtxV30 未定义` when executing Shenmo login. Historical working Qidian versions contained four account helper functions (`qfSmCtxV30`, `qfSmInputV30`, `qfSmTrimV30`, `qfSmSaveCredsV30`), while later source cleanup retained `qfSmLoginV30` / check / backend / logout callers but removed those dependencies. Beta5 restores the mature helpers unchanged.\n\nThe account action selector now follows the active Provider. Shenmo exposes only login/check/backend/logout; unsupported web-login is no longer shown. Reading business modules are unchanged.\n'''
if '## Beta5 Shenmo account dependency repair' not in h:
    h = h.rstrip() + '\n' + note
hp.write_text(h, encoding='utf-8')

rp = ROOT / 'docs/RELEASE_LOG.md'
r = rp.read_text(encoding='utf-8')
block = f'''## {day} — Qidian Next v0.1.4-beta5\n\nStatus: Beta/Test; Shenmo account dependency repair awaiting user real-device confirmation.\n\nChanges:\n\n- Restored `qfSmCtxV30`, `qfSmInputV30`, `qfSmTrimV30`, and `qfSmSaveCredsV30` from the mature historical Shenmo account implementation.\n- Fixed the real-device `ReferenceError: qfSmCtxV30 未定义` path.\n- Made account actions Provider-specific; Shenmo no longer exposes unsupported web-login.\n- Search/detail/catalog/content/review/Provider reading logic remains unchanged.\n- SHA256: `{sha}`.\n\n'''
if 'Qidian Next v0.1.4-beta5' not in r:
    r = r.replace('# RELEASE LOG\n', '# RELEASE LOG\n\n' + block, 1)
rp.write_text(r, encoding='utf-8')

kp = ROOT / 'docs/KNOWN_ISSUES.md'
k = kp.read_text(encoding='utf-8')
issue = '''\n## 15. Shenmo account helpers removed while callers remained — fixed in qidian-next Beta5\n\nObserved on real device in `0.1.3-beta4`: Shenmo login failed with `ReferenceError: qfSmCtxV30 未定义`. Historical working versions showed that four helper functions had been removed during later cleanup while `qfSmLoginV30`, check, backend and logout still called them.\n\nFix: restore the mature `qfSmCtxV30 / qfSmInputV30 / qfSmTrimV30 / qfSmSaveCredsV30` implementations and keep Provider-specific account actions. Status: Beta fix pending real-device confirmation.\n'''
if '## 15. Shenmo account helpers removed' not in k:
    k = k.rstrip() + '\n' + issue
kp.write_text(k, encoding='utf-8')

print('qidian-next beta5 prepared', 'sha256', sha, 'bytes', len(raw))
