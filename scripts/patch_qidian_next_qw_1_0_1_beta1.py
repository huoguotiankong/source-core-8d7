import json, pathlib, hashlib, gzip, base64
from datetime import datetime, timezone, timedelta
from copy import deepcopy

ROOT = pathlib.Path('.')
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
IDENTITY = 'https://m.qidian.com/?qf_source=qidian_next_8d7'
VERSION = '1.0.1-beta1'
VERSION_CODE = 10101

stable_bytes = STABLE.read_bytes()
stable_sha = hashlib.sha256(stable_bytes).hexdigest()
data = json.loads(stable_bytes)
assert isinstance(data, list) and len(data) == 1
src = deepcopy(data[0])
assert src.get('bookSourceUrl') == IDENTITY
assert src.get('bookSourceName') == '🌈 起点增强'

def replace1(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'{label}: expected 1 exact match, got {n}')
    return text.replace(old, new, 1)

js = str(src.get('jsLib') or '')
marker = 'var QF_MOD38_PACK='
s = js.index(marker) + len(marker)
e = js.index(';\nvar QF_MOD38_EXPORTS', s)
pack = json.loads(js[s:e])
packed = str(pack['limited_qw'])
assert packed.startswith('gz:')
mod = gzip.decompress(base64.b64decode(packed[3:])).decode('utf-8')

mod = replace1(mod,
    'function qfQwStaticHeadersV51(){return {"Accept":"application/json"};}',
    '''function qfQwStaticHeadersV51(){\n    var b=qfQwBaseV44.call(this);\n    return {\n        "User-Agent":"Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36",\n        "Accept":"application/json,text/plain,*/*",\n        "Referer":b+"/ranking.html"\n    };\n}''',
    'restore 情无 content UA/referer')

mod = replace1(mod,
    'var h={"Content-Type":"application/json","Accept":"application/json"},res=null,data=null;',
    'var h=qfQwStaticHeadersV51.call(this);h["Content-Type"]="application/json";var res=null,data=null;',
    'password relog headers')

mod = replace1(mod,
    'var hd={Accept:"application/json"};if(ck)hd.Cookie=ck;if(token)hd["X-Content-Token"]=token;',
    'var hd=qfQwStaticHeadersV51.call(this);if(ck)hd.Cookie=ck;if(token)hd["X-Content-Token"]=token;',
    'password relog me headers')

anchor = 'function qfQwAuthLikeV317(obj,raw){\n'
helper = '''function qfQwMarkVipVerifiedV101(token){\n    var s=qfQwSrcV318(this),base=qfQwBaseV44.call(this);\n    token=String(token||"");\n    if(!s||!s.put||!token)return;\n    try{s.put("qf_qw_vip_verified_v101",base+"|"+token+"|"+String(Date.now()));}catch(e0){}\n}\n'''
if helper not in mod:
    mod = replace1(mod, anchor, helper + anchor, 'insert VIP verification marker')

old = 'if(r.val){qfLimSetErrV30.call(this,"情无","");return r.val.replace(/\\\\r\\\\n/g,"\\n").replace(/\\\\n/g,"\\n").replace(/\\r\\n/g,"\\n").replace(/\\r/g,"\\n");}'
new = 'if(r.val){if(isPaid)qfQwMarkVipVerifiedV101.call(this,String(hd["X-Content-Token"]||""));qfLimSetErrV30.call(this,"情无","");return r.val.replace(/\\\\r\\\\n/g,"\\n").replace(/\\\\n/g,"\\n").replace(/\\r\\n/g,"\\n").replace(/\\r/g,"\\n");}'
mod = replace1(mod, old, new, 'mark first VIP success')

old = 'if(r2.val){qfLimSetErrV30.call(this,"情无","");return r2.val.replace(/\\\\r\\\\n/g,"\\n").replace(/\\\\n/g,"\\n").replace(/\\r\\n/g,"\\n").replace(/\\r/g,"\\n");}'
new = 'if(r2.val){if(isPaid)qfQwMarkVipVerifiedV101.call(this,String(hd2["X-Content-Token"]||""));qfLimSetErrV30.call(this,"情无","");return r2.val.replace(/\\\\r\\\\n/g,"\\n").replace(/\\\\n/g,"\\n").replace(/\\r\\n/g,"\\n").replace(/\\r/g,"\\n");}'
mod = replace1(mod, old, new, 'mark retry VIP success')

old = '''        /* 只在正文第一次失败时续签一次。VIP 的旧 token/cookie 失效时可自动恢复；\n         * 不循环重试，避免拖慢全源智能切换。 */\n        if(isPaid||qfQwAuthLikeV317(r.obj,r.raw)){\n'''
new = '''        /* 只在明确认证错误时续签一次。服务端业务/共享凭据失败不再盲目重登。 */\n        if(qfQwAuthLikeV317(r.obj,r.raw)){\n'''
mod = replace1(mod, old, new, 'auth-only retry')

old = '''        var ds=qfQwDedicatedV317.call(this);\n        if(isPaid&&Number(ds.keys)===0)msg+="（账号已登录，但共享凭据为 0）";\n        else if(isPaid)msg+="（VIP 章节请检查情无登录/共享凭据）";\n        qfLimSetErrV30.call(this,"情无",msg);return null;\n    }catch(e1){qfLimSetErrV30.call(this,"情无","正文请求失败："+String(e1)+(isPaid?"（VIP 章节请检查情无登录/共享凭据）":""));return null;}\n'''
new = '''        var ds=qfQwDedicatedV317.call(this),authLike=qfQwAuthLikeV317(r.obj,r.raw);\n        if(isPaid&&Number(ds.keys)===0)msg+="（账号会话已建立，但共享凭据为 0；VIP 正文尚不可用）";\n        else if(isPaid&&authLike)msg+="（情无会话/阅读令牌被正文接口拒绝，请重新登录后再试）";\n        else if(isPaid)msg+="（账号会话已建立"+(Number(ds.keys)>0?" · 共享凭据 "+String(Number(ds.keys))+" 个":"")+"，但 VIP 正文服务拒绝本次请求；请保留 Reference 供后续排查）";\n        qfLimSetErrV30.call(this,"情无",msg);return null;\n    }catch(e1){qfLimSetErrV30.call(this,"情无","正文请求失败："+String(e1)+(isPaid?"（账号会话与 VIP 正文可用性是两层状态）":""));return null;}\n'''
mod = replace1(mod, old, new, 'truthful VIP error')

pack['limited_qw'] = 'gz:' + base64.b64encode(gzip.compress(mod.encode('utf-8'), mtime=0)).decode('ascii')
src['jsLib'] = js[:s] + json.dumps(pack, ensure_ascii=False, separators=(',', ':')) + js[e:]

login = str(src.get('loginUrl') or '')
anchor = 'function qfQwNativeLoginV52(){'
helper = '''function qfQwNativeVipVerifiedV101(token){\n    var mark="",base=qfQwNativeBaseV52();token=String(token||"");\n    try{mark=String(source.get("qf_qw_vip_verified_v101")||"");}catch(e0){}\n    return !!token&&mark.indexOf(base+"|"+token+"|")===0;\n}\nfunction qfQwNativeSessionLabelV101(n,token,prefix){\n    var x=String(prefix||"情无账号会话已建立"),tk=String(token||"");\n    if(n>=0)x+=" · 共享凭据 "+String(n)+" 个";\n    if(!tk)return x+" · VIP正文未获取令牌";\n    if(Number(n)===0)return x+" · VIP正文不可用";\n    return x+(qfQwNativeVipVerifiedV101(tk)?" · VIP正文已验证":" · VIP正文待首次验证");\n}\n'''
if 'function qfQwNativeVipVerifiedV101' not in login:
    login = replace1(login, anchor, helper + anchor, 'insert native VIP status helper')

login = replace1(login,
    'qfQwNativeMsgV52("情无登录成功"+(n>=0?" · 共享凭据 "+n+" 个":"")+(token?" · 阅读令牌已获取":""));',
    'qfQwNativeMsgV52(qfQwNativeSessionLabelV101(n,token,"情无账号会话已建立"));',
    'login status wording')
login = replace1(login,
    'qfQwNativeMsgV52("网页登录成功"+(n>=0?" · 共享凭据 "+n+" 个":""));',
    'qfQwNativeMsgV52(qfQwNativeSessionLabelV101(n,token,"情无网页登录会话已建立"));',
    'web login status wording')
login = replace1(login,
    'qfQwNativeMsgV52("情无会话有效"+(n>=0?" · 共享凭据 "+n+" 个":"")+(tk?" · 阅读令牌正常":""));',
    'qfQwNativeMsgV52(qfQwNativeSessionLabelV101(n,tk,"情无账号会话有效"));',
    'check status wording')
login = replace1(login,
    'qfQwNativeMsgV52("情无已改为独立会话：登录方式与附件书源一致。可直接点“登录情无”或右上角 ✓；VIP 正文会在令牌失效时自动续签一次。情无 Cookie/Token 独立保存，不参与其它正文源登录。");',
    'qfQwNativeMsgV52("情无账号登录与 VIP 正文可用性是两层状态：登录/检测成功只代表账号会话和 request_token 有效；只有实际成功获取一次 VIP 正文后才标记为“VIP正文已验证”。情无正文会显式使用独立 UA/Referer/Cookie/Token；仅遇到明确认证错误时自动续签一次。");',
    'help wording')

for old, new, label in [
    ('try{source.remove("qf_qw_comment_base");source.remove("qf_qw_cookie_v317");source.remove("qf_qw_token_v317");source.remove("qf_qw_keys_v317");}catch(e3){}', 'try{source.remove("qf_qw_comment_base");source.remove("qf_qw_cookie_v317");source.remove("qf_qw_token_v317");source.remove("qf_qw_keys_v317");source.remove("qf_qw_vip_verified_v101");}catch(e3){}', 'save base marker cleanup'),
    ('try{source.remove("qf_qw_comment_base");source.remove("qf_qw_cookie_v317");source.remove("qf_qw_token_v317");source.remove("qf_qw_keys_v317");}catch(e1){}', 'try{source.remove("qf_qw_comment_base");source.remove("qf_qw_cookie_v317");source.remove("qf_qw_token_v317");source.remove("qf_qw_keys_v317");source.remove("qf_qw_vip_verified_v101");}catch(e1){}', 'reset base marker cleanup'),
    ('try{source.remove("qf_qw_cookie_v317");source.remove("qf_qw_token_v317");source.remove("qf_qw_keys_v317");}catch(e0){}', 'try{source.remove("qf_qw_cookie_v317");source.remove("qf_qw_token_v317");source.remove("qf_qw_keys_v317");source.remove("qf_qw_vip_verified_v101");}catch(e0){}', 'logout marker cleanup'),
]:
    login = replace1(login, old, new, label)

src['loginUrl'] = login
src['bookSourceName'] = '🌈 起点增强 · Beta'
src['bookSourceGroup'] = '﹅♚2、测试源'
src['bookSourceComment'] = 'v1.0.1-beta1：情无账号/VIP正文专项修复。恢复情无 content.php 专属 User-Agent + Referer + Accept；仅明确认证错误自动续签，服务端业务失败不再盲目重登；登录/检测状态区分“账号会话有效”和“VIP正文已验证”。其它搜索/详情/目录/评论/Provider 不改。'
if isinstance(src.get('loginUi'), str):
    src['loginUi'] = src['loginUi'].replace('v1.0.0', 'v1.0.1-beta1')

raw = json.dumps([src], ensure_ascii=False, separators=(',', ':')).encode('utf-8')
beta_sha = hashlib.sha256(raw).hexdigest()
BETA.parent.mkdir(parents=True, exist_ok=True)
BETA.write_bytes(raw)

now_dt = datetime.now(timezone(timedelta(hours=8)))
now = now_dt.isoformat(timespec='seconds')
day = now_dt.date().isoformat()
raw_url = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v=10101'
backup_url = 'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v=10101'
detail_url = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?v=10101'
summary = '起点增强测试版：本版只修情无账号会话与 VIP 正文认证/请求头链路。'
changes = [
    '恢复情无 content.php 专属 User-Agent / Referer / Accept，避免继承起点全局请求环境',
    '账号登录/检测不再等同于 VIP 正文可用；首次真实 VIP 正文成功后才标记已验证',
    '仅明确认证错误自动续签一次；Service request failed 等业务失败保留 Reference，不再盲目重登',
    'Stable 1.0.0 与其它搜索/目录/评论/Provider 逻辑保持不变',
]

bundle_path = ROOT / 'bundles/all-beta.json'
bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
assert isinstance(bundle, list)
bundle = [x for x in bundle if x.get('bookSourceUrl') != IDENTITY]
bundle.append(src)
bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

sub_path = ROOT / 'subscription/beta.json'
sub = json.loads(sub_path.read_text(encoding='utf-8'))
items = [x for x in sub.get('items', []) if x.get('id') != 'qidian-next-beta']
items.append({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'icon':'','channel':'beta','version':VERSION,'updatedAt':day,'tags':['起点','测试版','情无','VIP正文','认证修复','多正文 Provider'],'changelog':changes[:2],'sourceUrl':raw_url,'backupUrl':backup_url,'importUrl':'legado://import/importonline?src='+raw_url,'detailUrl':detail_url})
sub['updatedAt'] = now
sub['items'] = items
sub_path.write_text(json.dumps(sub, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

detail_path = ROOT / 'rss/data/details/beta/qidian-next.json'
detail_path.parent.mkdir(parents=True, exist_ok=True)
detail = {'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'情无专项'],'sections':[{'title':'本次测试','text':'恢复情无正文请求的独立 UA/Referer/Accept；登录成功只表示账号会话有效，实际 VIP 正文成功后才视为正文链验证通过。'},{'title':'测试重点','text':'固定情无打开同一 VIP 章节；若仍失败，请保留 Service request failed 后面的 Reference。'}],'sourceUrl':raw_url,'backupUrl':backup_url}
detail_path.write_text(json.dumps(detail, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

mp = ROOT / 'manifest.json'
manifest = json.loads(mp.read_text(encoding='utf-8'))
manifest['updatedAt'] = now
arr = [x for x in manifest.get('sources', []) if x.get('id') != 'qidian-next-beta']
arr.append({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','category':'novel','channel':'beta','version':VERSION,'versionCode':VERSION_CODE,'updatedAt':now,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','sourceUrl':raw_url,'bookSourceUrl':IDENTITY,'summary':summary,'tags':['起点','测试版','情无','VIP正文','认证修复'],'changelog':changes,'sha256':beta_sha})
manifest['sources'] = arr
mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

rp = ROOT / 'docs/RELEASE_LOG.md'
release = rp.read_text(encoding='utf-8')
block = f'''## {day} — 起点增强 {VERSION}\n\nStatus: Beta/Test; 情无账号/VIP正文专项修复，等待真机确认。\n\nChanges:\n\n- 恢复情无 `/qd/content.php` 的独立 User-Agent / Referer / Accept 请求头。\n- 登录/检测只表示账号会话有效；真实 VIP 正文成功后才记录“VIP正文已验证”。\n- 仅明确认证错误触发一次自动续签；普通 `Service request failed. Reference: ...` 不再盲目重登。\n- Stable `1.0.0` 文件与正式通道保持不变。\n- Beta SHA256: `{beta_sha}`.\n\n'''
if f'## {day} — 起点增强 {VERSION}' not in release:
    lines = release.splitlines(True)
    release = (lines[0]+'\n'+block+''.join(lines[1:])) if lines and lines[0].startswith('# RELEASE LOG') else block+release
    rp.write_text(release, encoding='utf-8')

kp = ROOT / 'docs/KNOWN_ISSUES.md'
known = kp.read_text(encoding='utf-8')
issue = '''## 17. 情无账号会话有效但 VIP 正文被服务端拒绝 — 1.0.1-beta1 修复中\n\n真机现象：账号管理显示情无登录/检测成功，但固定情无读取 VIP 章节仍返回 `Service request failed. Reference: ...`。\n\n定位：登录层使用情无自己的 UA/Referer，但 lazy `limited_qw` 正文模块退化成仅发送 `Accept: application/json`；历史已验证版本要求 `/qd/content.php` 显式使用情无 UA + `Referer: <base>/ranking.html`。当前代码还会对所有 VIP 失败无条件续签，导致服务业务失败也被误判为登录问题。\n\nBeta 修复：恢复情无正文专属 UA/Referer/Accept；只对明确认证错误续签；将“账号会话有效”和“VIP正文已验证”拆成两层状态；保留服务端 Reference 供后续排查。\n\nStatus: `🌈 起点增强 1.0.1-beta1` 待真机验证；Stable 1.0.0 未修改。\n'''
if '## 17. 情无账号会话有效但 VIP 正文被服务端拒绝' not in known:
    kp.write_text(known.rstrip()+'\n\n'+issue+'\n', encoding='utf-8')

hp = ROOT / 'docs/sources/qidian-next/PROJECT_HANDOFF.md'
handoff = hp.read_text(encoding='utf-8')
section = f'''## Active Beta {VERSION} — 情无 VIP 认证修复\n\nStable remains `1.0.0` at `sources/novel/qidian-next/qidian-next.json`. Beta path: `sources/novel/qidian-next/qidian-next-beta.json`.\n\nReal-device trigger: 情无账号登录/检测成功，但固定情无读取 VIP 章节返回 `Service request failed. Reference: ...`. Historical working builds required an explicit 情无 User-Agent + Referer for `/qd/content.php`; the current lazy module had regressed to Accept-only headers. `/auth.php?action=me` validates the account session but does not prove that VIP content is accepted.\n\nBeta changes: restore 情无-specific content headers; retry only authentication-like failures; mark VIP verification only after real paid content succeeds; keep service Reference visible on non-auth failures; keep Stable and all unrelated reading domains unchanged.\n'''
if f'## Active Beta {VERSION}' not in handoff:
    hp.write_text(handoff.rstrip()+'\n\n'+section+'\n', encoding='utf-8')

assert hashlib.sha256(STABLE.read_bytes()).hexdigest() == stable_sha
print('stable_sha', stable_sha)
print('beta_sha', beta_sha)
print('beta_bytes', len(raw))
