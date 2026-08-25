import json, pathlib, hashlib
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
SP = ROOT / 'sources/novel/qidian-next/qidian-next.json'
data = json.loads(SP.read_text(encoding='utf-8'))
assert isinstance(data, list) and len(data) == 1
src = data[0]
assert src.get('bookSourceUrl') == 'https://m.qidian.com/?qf_source=qidian_next_8d7'
login = str(src.get('loginUrl') or '')
assert 'qidian-next v0.1.4-beta5' in login
assert 'qfSmCtxV30' in login and 'qfNextAccountExecV013' in login

PATCH = r'''
/* qidian-next v0.1.5-beta6 · secondary settings UX phase 1 */
function qfUxEscV015(v){
    return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function qfUxDecodeV015(v){
    return String(v==null?'':v).replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&amp;/g,'&');
}
function qfUxSpanV015(id,val){return '<span id="'+id+'" style="display:none">'+qfUxEscV015(val)+'</span>';}
function qfUxReadV015(body,id){
    try{
        var r=new RegExp('id=["\\\']'+id+'["\\\'][^>]*>([^<]*)<\\/span>','i');
        var m=String(body||'').match(r);
        return m?qfUxDecodeV015(String(m[1]||'')):null;
    }catch(_e){return null;}
}
function qfUxSaveV015(body,map){
    for(var i=0;i<map.length;i++){
        var v=qfUxReadV015(body,map[i][0]);
        if(v!==null)qfMSet423(map[i][1],v,true);
    }
}
function qfUxOpenV015(title,icon,tag,desc,inner,script){
    var css=
      '*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}'+
      ':root{color-scheme:light dark;--bg:#f5f6fa;--card:#ffffff;--card2:#f8f9fc;--text:#1f2430;--muted:#788196;--line:#e7e9f1;--primary:#665cff;--primary2:#8b5cff;--soft:#eeecff;--ok:#25a86b;--warn:#d08a18;--danger:#d84f5f;--shadow:0 8px 28px rgba(38,43,65,.06)}'+
      '@media(prefers-color-scheme:dark){:root{--bg:#0f1218;--card:#181d26;--card2:#202632;--text:#edf1f7;--muted:#99a3b7;--line:#2a3240;--soft:#282443;--shadow:none}}'+
      'html,body{margin:0;min-height:100%;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif}'+
      'body{padding:14px 14px calc(24px + env(safe-area-inset-bottom))}'+
      '.hero{position:relative;overflow:hidden;padding:16px 17px;border-radius:20px;background:linear-gradient(135deg,#5865ff,#8b55f7);color:#fff;box-shadow:var(--shadow);margin-bottom:12px}'+
      '.hero:after{content:"";position:absolute;width:120px;height:120px;border-radius:50%;right:-40px;top:-60px;background:rgba(255,255,255,.12)}'+
      '.heroTop{display:flex;align-items:center;gap:10px}.heroIcon{font-size:25px}.hero h1{margin:0;font-size:20px;letter-spacing:.2px}.heroTag{margin-left:auto;font-size:11px;padding:5px 9px;border-radius:99px;background:rgba(255,255,255,.18)}'+
      '.hero p{margin:8px 0 0;font-size:12px;line-height:1.55;opacity:.92}'+
      '.section{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:14px;margin:0 0 11px;box-shadow:var(--shadow)}'+
      '.sectionHead{display:flex;align-items:flex-start;gap:10px;margin-bottom:11px}.sectionHead h3{margin:0;font-size:15px}.sectionHead p{margin:4px 0 0;color:var(--muted);font-size:11px;line-height:1.45}.miniBadge{margin-left:auto;white-space:nowrap;color:var(--primary);background:var(--soft);padding:5px 9px;border-radius:99px;font-size:11px;font-weight:700}'+
      '.tabs{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}.tabs button,.chips button{border:1px solid var(--line);background:var(--card2);color:var(--text);border-radius:11px;min-height:38px;padding:8px 6px;font-size:13px;font-weight:650}.tabs button.on,.chips button.on{border-color:transparent;background:linear-gradient(135deg,#665cff,#9159f3);color:#fff;box-shadow:0 6px 16px rgba(102,92,255,.18)}'+
      '.chips{display:flex;flex-wrap:wrap;gap:8px}.chips button{min-width:calc(33.333% - 6px);flex:1 0 auto;padding:9px 10px}'+
      '.field{margin:10px 0}.field:first-child{margin-top:0}.field label{display:flex;justify-content:space-between;align-items:center;font-size:13px;font-weight:700;margin-bottom:6px}.field small{font-size:10px;color:var(--muted);font-weight:500}'+
      '.field input{width:100%;border:1px solid var(--line);background:var(--card2);color:var(--text);border-radius:12px;padding:11px 12px;font-size:14px;outline:none}.field input:focus{border-color:var(--primary);box-shadow:0 0 0 3px rgba(102,92,255,.09)}'+
      '.actionGrid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.actionGrid button,.tool{border:1px solid var(--line);background:var(--card2);color:var(--text);border-radius:13px;padding:12px 10px;font-size:13px;font-weight:700}.actionGrid button.on,.tool.on{border-color:transparent;background:linear-gradient(135deg,#665cff,#9159f3);color:#fff}.actionGrid button.danger{color:var(--danger)}.actionGrid button.danger.on{color:#fff;background:linear-gradient(135deg,#d84f5f,#b73f6b)}'+
      '.state{margin-top:10px;padding:10px 12px;border-radius:12px;background:var(--soft);font-size:12px;color:var(--muted)}.state b{color:var(--primary)}'+
      '.route{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.routeStep{padding:7px 10px;border-radius:10px;background:var(--soft);color:var(--primary);font-size:12px;font-weight:750}.arrow{color:var(--muted)}'+
      '.toolGrid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.tool{text-align:left;min-height:76px}.tool b{display:block;font-size:14px}.tool span{display:block;color:var(--muted);font-size:10px;font-weight:500;line-height:1.4;margin-top:5px}.tool.on span{color:rgba(255,255,255,.82)}'+
      'details{border-top:1px solid var(--line);margin-top:11px;padding-top:10px}summary{font-size:12px;color:var(--muted);font-weight:700;cursor:pointer;padding:4px 0 8px}'+
      '.tip{padding:11px 13px;margin-top:4px;border-radius:14px;background:var(--card);border:1px dashed var(--line);color:var(--muted);font-size:11px;line-height:1.55}.tip b{color:var(--text)}'+
      '.hide{display:none!important}';
    var html='<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><style>'+css+'</style></head><body>'+
      '<div class="hero"><div class="heroTop"><span class="heroIcon">'+qfUxEscV015(icon)+'</span><h1>'+qfUxEscV015(title)+'</h1><span class="heroTag">'+qfUxEscV015(tag)+'</span></div><p>'+qfUxEscV015(desc)+'</p></div>'+
      inner+'<div class="tip"><b>保存方式：</b>设置完成后点击阅读页面右上角 ✓ 返回。普通设置会自动保存；若选择了登录/诊断动作，会在返回后执行。</div>'+
      '<script>'+script+'</script></body></html>';
    try{return java.startBrowserAwait('data:text/html;base64,'+java.base64Encode(html),title,false).body();}
    catch(e){try{java.longToast('打开设置页失败：'+String(e));}catch(_e){}return '';}
}
function qfUxFieldV015(id,label,val,type,hint){
    return '<div class="field"><label>'+qfUxEscV015(label)+'<small>'+qfUxEscV015(hint||'')+'</small></label><input id="'+id+'" type="'+(type||'text')+'" value="'+qfUxEscV015(val||'')+'"></div>';
}

qfMultiContentV423=function(){
    var tier=qfMGet423('正文源类别','限免源');
    if(['限免源','优选源','兜底源','STV源','全源智能'].indexOf(tier)<0)tier='限免源';
    var vals={
      '限免源':qfMGet423('限免源选择','自动'),
      '优选源':qfMGet423('优选源选择','自动'),
      '兜底源':qfMGet423('兜底源选择','自动'),
      'STV源':qfMGet423('STV源选择','STV·自动'),
      '全源智能':qfMGet423('全源智能选择','自动')
    };
    var stvKey=qfMGet423('STV API密钥','');
    var inner=''+
      '<div class="section"><div class="sectionHead"><div><h3>正文路线</h3><p>先选择策略类别，再选择该类别下的具体 Provider。</p></div><span class="miniBadge" id="tierBadge">'+qfUxEscV015(tier)+'</span></div><div class="chips" id="tierBox"></div></div>'+
      '<div class="section"><div class="sectionHead"><div><h3>Provider</h3><p>这里只显示当前策略可用的正文来源。</p></div></div><div class="chips" id="providerBox"></div><div class="state"><div class="route"><span class="routeStep" id="routeTier"></span><span class="arrow">→</span><span class="routeStep" id="routeProvider"></span></div></div></div>'+
      '<div class="section" id="stvCard"><div class="sectionHead"><div><h3>STV 专区</h3><p>仅在主动选择 STV 路线时生效，不参与其它自动类别。</p></div><span class="miniBadge">4x</span></div>'+qfUxFieldV015('stv_key','API 密钥',stvKey,'password','可选；没有可留空')+'</div>'+
      qfUxSpanV015('ux_tier',tier)+qfUxSpanV015('ux_limited',vals['限免源'])+qfUxSpanV015('ux_preferred',vals['优选源'])+qfUxSpanV015('ux_fallback',vals['兜底源'])+qfUxSpanV015('ux_stv',vals['STV源'])+qfUxSpanV015('ux_all',vals['全源智能'])+qfUxSpanV015('ux_stvkey',stvKey);
    var js='var tier='+JSON.stringify(tier)+',vals='+JSON.stringify(vals)+';'+
      'var tiers=["限免源","优选源","兜底源","STV源","全源智能"],pmap={"限免源":["自动","情无","神魔","晴天","同人"],"优选源":["自动","七猫","书旗","QQ浏览器","得间","酷我"],"兜底源":["自动","猫眼","得奇","69书吧","速读谷","万相"],"STV源":["STV·自动","STV·qidian"],"全源智能":["自动"]};'+
      'function sync(){document.getElementById("ux_tier").textContent=tier;document.getElementById("ux_limited").textContent=vals["限免源"]||"自动";document.getElementById("ux_preferred").textContent=vals["优选源"]||"自动";document.getElementById("ux_fallback").textContent=vals["兜底源"]||"自动";document.getElementById("ux_stv").textContent=vals["STV源"]||"STV·自动";document.getElementById("ux_all").textContent=vals["全源智能"]||"自动";document.getElementById("ux_stvkey").textContent=document.getElementById("stv_key").value;document.getElementById("tierBadge").textContent=tier;document.getElementById("routeTier").textContent=tier;document.getElementById("routeProvider").textContent=vals[tier]||"自动";}'+
      'function renderTiers(){var b=document.getElementById("tierBox");b.innerHTML="";tiers.forEach(function(t){var x=document.createElement("button");x.type="button";x.textContent=t;x.className=t===tier?"on":"";x.onclick=function(){tier=t;renderTiers();renderProviders();sync();};b.appendChild(x);});}'+
      'function renderProviders(){var b=document.getElementById("providerBox"),arr=pmap[tier]||["自动"];b.innerHTML="";if(arr.indexOf(vals[tier])<0)vals[tier]=arr[0];arr.forEach(function(v){var x=document.createElement("button");x.type="button";x.textContent=v;x.className=v===vals[tier]?"on":"";x.onclick=function(){vals[tier]=v;renderProviders();sync();};b.appendChild(x);});document.getElementById("stvCard").className=tier==="STV源"?"section":"section hide";}'+
      'document.getElementById("stv_key").addEventListener("input",sync);renderTiers();renderProviders();sync();';
    var body=qfUxOpenV015('正文设置','📚','路由中心','把正文策略和 Provider 放在同一个页面里，当前路线会实时显示。',inner,js);
    if(!body)return;
    var map=[['ux_tier','正文源类别'],['ux_limited','限免源选择'],['ux_preferred','优选源选择'],['ux_fallback','兜底源选择'],['ux_stv','STV源选择'],['ux_all','全源智能选择'],['ux_stvkey','STV API密钥']];
    qfUxSaveV015(body,map);
};

qfMultiAccountsV423=function(){
    var provider=qfMGet423('账号管理Provider','情无');
    if(['情无','神魔','晴天','同人'].indexOf(provider)<0)provider='情无';
    var qwe=qfMGet423('email',''),qwp=qfMGet423('password',''),qwb=qfMGet423('情无接口地址','http://103.236.85.8:7878/qd');
    var sma=qfMGet423('神魔账号或邮箱',''),smp=qfMGet423('神魔密码','');
    var qtk=qfMGet423('晴天密钥',''),qtp=qfMGet423('晴天口令',''),qtb=qfMGet423('晴天接口地址','https://sb.shazi.tk');
    var inner=''+
      '<div class="section"><div class="sectionHead"><div><h3>Provider</h3><p>切换后只展示当前 Provider 的账号字段和可用动作。</p></div><span class="miniBadge" id="providerBadge">'+qfUxEscV015(provider)+'</span></div><div class="tabs" id="providerTabs"></div></div>'+
      '<div class="section providerCard" data-p="情无"><div class="sectionHead"><div><h3>🌙 情无账号</h3><p>邮箱、密码和接口地址。</p></div></div>'+qfUxFieldV015('qw_email','邮箱',qwe,'text','QQ 邮箱')+qfUxFieldV015('qw_password','密码',qwp,'password','情无密码')+qfUxFieldV015('qw_base','接口地址',qwb,'text','可自定义')+'</div>'+
      '<div class="section providerCard" data-p="神魔"><div class="sectionHead"><div><h3>⚔️ 神魔账号</h3><p>账号/邮箱和密码；支持后台管理。</p></div></div>'+qfUxFieldV015('sm_account','账号或邮箱',sma,'text','神魔后台账号')+qfUxFieldV015('sm_password','密码',smp,'password','神魔密码')+'</div>'+
      '<div class="section providerCard" data-p="晴天"><div class="sectionHead"><div><h3>☀️ 晴天账号</h3><p>密钥、口令和接口地址。</p></div></div>'+qfUxFieldV015('qt_key','密钥',qtk,'password','')+qfUxFieldV015('qt_pass','口令',qtp,'password','')+qfUxFieldV015('qt_base','接口地址',qtb,'text','默认 https://sb.shazi.tk')+'</div>'+
      '<div class="section providerCard" data-p="同人"><div class="sectionHead"><div><h3>🍋 同人</h3><p>使用共享 Token，无需填写账号字段。</p></div><span class="miniBadge">共享</span></div><div class="state">可直接进行 Token 检测或打开后台。</div></div>'+
      '<div class="section"><div class="sectionHead"><div><h3>执行动作</h3><p>点击只是选择待执行动作；真正执行发生在点右上角 ✓ 返回后。</p></div></div><div class="actionGrid" id="actionGrid"></div><div class="state">当前待执行：<b id="actionText">仅保存</b></div></div>'+
      qfUxSpanV015('ux_provider',provider)+qfUxSpanV015('ux_action','不执行')+qfUxSpanV015('ux_qwe',qwe)+qfUxSpanV015('ux_qwp',qwp)+qfUxSpanV015('ux_qwb',qwb)+qfUxSpanV015('ux_sma',sma)+qfUxSpanV015('ux_smp',smp)+qfUxSpanV015('ux_qtk',qtk)+qfUxSpanV015('ux_qtp',qtp)+qfUxSpanV015('ux_qtb',qtb);
    var js='var provider='+JSON.stringify(provider)+',action="不执行";'+
      'var providers=["情无","神魔","晴天","同人"],acts={"情无":["不执行","登录","检测","网页登录","退出"],"神魔":["不执行","登录","检测","后台","退出"],"晴天":["不执行","登录","检测","后台","退出"],"同人":["不执行","检测","后台"]};'+
      'function sync(){document.getElementById("ux_provider").textContent=provider;document.getElementById("ux_action").textContent=action;document.getElementById("ux_qwe").textContent=document.getElementById("qw_email").value;document.getElementById("ux_qwp").textContent=document.getElementById("qw_password").value;document.getElementById("ux_qwb").textContent=document.getElementById("qw_base").value;document.getElementById("ux_sma").textContent=document.getElementById("sm_account").value;document.getElementById("ux_smp").textContent=document.getElementById("sm_password").value;document.getElementById("ux_qtk").textContent=document.getElementById("qt_key").value;document.getElementById("ux_qtp").textContent=document.getElementById("qt_pass").value;document.getElementById("ux_qtb").textContent=document.getElementById("qt_base").value;document.getElementById("providerBadge").textContent=provider;document.getElementById("actionText").textContent=action==="不执行"?"仅保存":action;}'+
      'function renderProviders(){var b=document.getElementById("providerTabs");b.innerHTML="";providers.forEach(function(p){var x=document.createElement("button");x.type="button";x.textContent=p;x.className=p===provider?"on":"";x.onclick=function(){provider=p;action="不执行";renderProviders();renderCards();renderActions();sync();};b.appendChild(x);});}'+
      'function renderCards(){Array.prototype.forEach.call(document.querySelectorAll(".providerCard"),function(c){c.className=c.getAttribute("data-p")===provider?"section providerCard":"section providerCard hide";});}'+
      'function renderActions(){var b=document.getElementById("actionGrid"),arr=acts[provider]||["不执行"];b.innerHTML="";arr.forEach(function(a){var x=document.createElement("button");x.type="button";x.textContent=a==="不执行"?"仅保存":a;x.className=(a===action?"on ":"")+(a==="退出"?"danger":"");x.onclick=function(){action=a;renderActions();sync();};b.appendChild(x);});}'+
      'Array.prototype.forEach.call(document.querySelectorAll("input"),function(x){x.addEventListener("input",sync);});renderProviders();renderCards();renderActions();sync();';
    var body=qfUxOpenV015('账号管理','🔐','Provider','一次只管理一个 Provider，字段、动作和状态都聚合在同一页。',inner,js);
    if(!body)return;
    var map=[['ux_provider','账号管理Provider'],['ux_qwe','email'],['ux_qwp','password'],['ux_qwb','情无接口地址'],['ux_sma','神魔账号或邮箱'],['ux_smp','神魔密码'],['ux_qtk','晴天密钥'],['ux_qtp','晴天口令'],['ux_qtb','晴天接口地址']];
    qfUxSaveV015(body,map);
    provider=qfUxReadV015(body,'ux_provider')||provider;
    var action=qfUxReadV015(body,'ux_action')||'不执行';
    qfMSet423('账号管理动作','不执行',true);
    if(action!=='不执行')qfNextAccountExecV013(provider,action);
};

qfMultiDiagV423=function(){
    var inner=''+
      '<div class="section"><div class="sectionHead"><div><h3>常用诊断</h3><p>优先用这三项定位大多数问题。</p></div><span class="miniBadge">推荐</span></div><div class="toolGrid">'+
      '<button class="tool" data-a="Runtime 概览"><b>🩺 Runtime 概览</b><span>查看当前运行环境、关键状态和最近摘要。</span></button>'+
      '<button class="tool" data-a="性能摘要"><b>⏱ 性能摘要</b><span>快速查看章节、Provider 与评论相关性能信息。</span></button>'+
      '<button class="tool" data-a="复制脱敏诊断"><b>📋 复制脱敏诊断</b><span>复制可用于反馈的问题信息，不包含敏感凭据。</span></button>'+
      '</div><details><summary>高级诊断 ▾</summary><div class="toolGrid">'+
      '<button class="tool" data-a="深度追踪"><b>🔬 深度追踪</b><span>用于复杂问题，信息更多、开销也更高。</span></button>'+
      '<button class="tool" data-a="清空诊断"><b>🧹 清空诊断</b><span>清理已有运行诊断记录。</span></button>'+
      '</div></details></div>'+
      '<div class="section"><div class="sectionHead"><div><h3>待执行动作</h3><p>选中一个诊断项后，点击右上角 ✓ 返回执行。</p></div></div><div class="state">当前待执行：<b id="diagText">不执行</b></div><div class="actionGrid" style="margin-top:9px"><button id="diagCancel" type="button">取消待执行动作</button></div></div>'+qfUxSpanV015('ux_diag','不执行');
    var js='var action="不执行";'+
      'function sync(){document.getElementById("ux_diag").textContent=action;document.getElementById("diagText").textContent=action;Array.prototype.forEach.call(document.querySelectorAll(".tool"),function(x){x.className=x.getAttribute("data-a")===action?"tool on":"tool";});}'+
      'Array.prototype.forEach.call(document.querySelectorAll(".tool"),function(x){x.onclick=function(){action=x.getAttribute("data-a");sync();};});document.getElementById("diagCancel").onclick=function(){action="不执行";sync();};sync();';
    var body=qfUxOpenV015('诊断工具','🩺','排障','常用诊断优先展示，高级工具默认收起，避免页面像开发面板。',inner,js);
    if(!body)return;
    var a=qfUxReadV015(body,'ux_diag')||'不执行';
    try{
        if(a==='Runtime 概览')qfRuntimeDiagShow('overview');
        else if(a==='性能摘要')qfRuntimeDiagShow('performance');
        else if(a==='深度追踪')qfRuntimeDiagShow('performance-deep');
        else if(a==='复制脱敏诊断')qfRuntimeDiagCopy();
        else if(a==='清空诊断')qfRuntimeDiagReset();
    }catch(e){try{java.longToast('诊断操作失败：'+String(e));}catch(_e){}}
};
'''

if 'qidian-next v0.1.5-beta6' not in login:
    src['loginUrl'] = login.rstrip() + '\n\n' + PATCH.strip() + '\n'

try:
    ui = json.loads(src.get('loginUi') or '[]')
    if isinstance(ui, list) and ui:
        ui[0]['name'] = '🌈 起点助手 · v0.1.5-beta6'
        src['loginUi'] = json.dumps(ui, ensure_ascii=False, separators=(',', ':'))
except Exception:
    pass

src['bookSourceComment'] = ('v0.1.5-beta6：二级设置 UI 重构第一阶段。正文设置改为策略胶囊 + 当前类别 Provider + 实时路线概览；'
                            '账号管理改为 Provider 标签页 + 专属表单 + 动作按钮组；诊断工具改为常用/高级分层卡片。'
                            '继续使用 startBrowserAwait + 右上角 ✓ 返回保存/执行，避免动态 loginUi 和自定义 Scheme 兼容问题。'
                            '搜索/详情/目录/正文获取/评论业务逻辑不变。')

now_dt = datetime.now(timezone(timedelta(hours=8)))
now = now_dt.isoformat(timespec='seconds')
day = now_dt.date().isoformat()
src['lastUpdateTime'] = int(now_dt.timestamp() * 1000)

raw = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
SP.write_bytes(raw)
sha = hashlib.sha256(raw).hexdigest()

bp = ROOT / 'bundles/all-beta.json'
bundle = json.loads(bp.read_text(encoding='utf-8'))
for i, item in enumerate(bundle):
    if item.get('bookSourceUrl') == src.get('bookSourceUrl') or item.get('bookSourceName') == '🌈 起点助手·新架构':
        bundle[i] = src
        break
else:
    bundle.append(src)
bp.write_text(json.dumps(bundle, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

changes = [
    '二级设置 UI 重构第一阶段：统一卡片、轻量渐变头部、暗色模式与操作提示',
    '正文设置：策略胶囊 + 当前类别 Provider + 实时路线概览 + 独立 STV 专区',
    '账号管理：情无/神魔/晴天/同人标签页 + 当前 Provider 专属字段 + 动作按钮组',
    '诊断工具：常用诊断优先，高级诊断折叠；动作仍在点 ✓ 返回后执行',
    '一级双列首页及搜索/详情/目录/正文/评论业务逻辑保持不变'
]

subp = ROOT / 'subscription/beta.json'
sub = json.loads(subp.read_text(encoding='utf-8'))
sub['updatedAt'] = now
for item in sub.get('items', []):
    if item.get('id') == 'qidian-next':
        item['version'] = '0.1.5-beta6'
        item['updatedAt'] = day
        item['changelog'] = changes
subp.write_text(json.dumps(sub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

mp = ROOT / 'manifest.json'
manifest = json.loads(mp.read_text(encoding='utf-8'))
manifest['updatedAt'] = now
for item in manifest.get('sources', []):
    if item.get('id') == 'qidian-next':
        item['version'] = '0.1.5-beta6'
        item['versionCode'] = 1506
        item['updatedAt'] = now
        item['changelog'] = changes
        item['sha256'] = sha
mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

dp = ROOT / 'rss/data/details/qidian-next.json'
detail = json.loads(dp.read_text(encoding='utf-8'))
detail['badges'] = ['Beta', '0.1.5-beta6', '小说', '新架构']
sections = detail.setdefault('sections', [])
sections.insert(1, {
    'title': 'Beta6 二级设置 UI 重构 · 第一阶段',
    'text': '重新设计正文设置、账号管理和诊断工具：统一卡片视觉，Provider/策略用直接点击的标签和按钮选择；诊断按常用/高级分层。继续沿用已验证的 startBrowserAwait + ✓ 返回保存/执行机制。'
})
dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

hp = ROOT / 'docs/sources/qidian-next/PROJECT_HANDOFF.md'
h = hp.read_text(encoding='utf-8')
h = h.replace('- Current version: `0.1.4-beta5`', '- Current version: `0.1.5-beta6`')
h = h.replace('- SHA256: `f694d686980a2c1aa71d86313eb16931ca578e9c23e18dd136a1c175955d8341`', '- SHA256: `' + sha + '`')
plan = '''\n## Secondary settings UI redesign plan\n\nUser approved a staged redesign on 2026-08-25. Keep the confirmed two-column static first-level login page. Secondary pages use one visual system: compact gradient header, grouped cards, direct controls, clear current state, and a unified footer explaining that the browser ✓ returns/saves and executes any chosen native action. Do not return to large dynamic `@js:` loginUi or custom-scheme bridges.\n\nPhases:\n\n1. Beta6: Account Management, Diagnostics, Content/Provider settings.\n2. Next phase: Review/Display settings, Interface/Prompt settings, Book-variable guide and Help.\n3. Final polish: spacing, typography, button states, consistent copy, then remove obsolete UI compatibility blocks after real-device confirmation.\n\n## Beta6 secondary settings UI phase 1\n\n- Content: strategy chips, Provider chips, live route summary, STV card shown only for STV.\n- Accounts: four Provider tabs; only the active Provider card is shown; actions are direct two-column buttons and are executed only after ✓ return.\n- Diagnostics: common tools are visible first; deep trace / reset are under an advanced disclosure; selected action is clearly displayed.\n- Runtime reading modules are untouched.\n'''
if '## Secondary settings UI redesign plan' not in h:
    h = h.rstrip() + '\n' + plan
hp.write_text(h, encoding='utf-8')

rp = ROOT / 'docs/RELEASE_LOG.md'
r = rp.read_text(encoding='utf-8')
block = f'''## {day} — Qidian Next v0.1.5-beta6\n\nStatus: Beta/Test; secondary-settings UX phase 1 awaiting user real-device confirmation.\n\nChanges:\n\n- Redesigned Content, Account Management and Diagnostics secondary pages with one card-based visual system.\n- Content uses strategy/Provider chips, live route summary and a conditional STV card.\n- Accounts use Provider tabs, Provider-specific fields and compact action buttons.\n- Diagnostics prioritize common tools and collapse advanced actions.\n- Preserved the real-device-compatible `startBrowserAwait` + browser ✓ return/save/execute mechanism.\n- First-level login UI and reading business modules remain unchanged.\n- SHA256: `{sha}`.\n\n'''
if 'Qidian Next v0.1.5-beta6' not in r:
    r = r.replace('# RELEASE LOG\n', '# RELEASE LOG\n\n' + block, 1)
rp.write_text(r, encoding='utf-8')

print('qidian-next beta6 prepared', 'sha256', sha, 'bytes', len(raw))
