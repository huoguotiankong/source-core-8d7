import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path('.')
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
VERSION = '1.2.3-beta4'
VC = 12034
TS = '2026-09-13T14:58:00+08:00'
IDENTITY = 'https://m.qidian.com/?qf_source=qidian_next_8d7'
STABLE_EXPECTED = '1eaffa24543b2af58aed1368578368ea326ffb0170338971bde558df725bed87'
RAW = f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP = f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT = 'legado://import/importonline?src=' + RAW
DETAIL = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'

stable_hash = hashlib.sha256(STABLE.read_bytes()).hexdigest()
assert stable_hash == STABLE_EXPECTED, 'unexpected Stable baseline: ' + stable_hash
arr = json.loads(BETA.read_text(encoding='utf-8'))
s = arr[0] if isinstance(arr, list) else arr
assert s.get('bookSourceUrl') == IDENTITY
assert '1.2.3-beta3' in s.get('bookSourceComment', ''), 'expected beta3 baseline'

lib = s['jsLib']
mk = 'var QF_MOD38_PACK='
a = lib.index(mk) + len(mk)
try:
    b = lib.index(';\nvar QF_MOD38_EXPORTS=', a)
except ValueError:
    b = lib.index(';var QF_MOD38_EXPORTS=', a)
pack = json.loads(lib[a:b])
pack_before = dict(pack)
assert 'review_local_ui' in pack

def dec(v):
    if not isinstance(v, str):
        return ''
    if not v.startswith('gz:'):
        return v
    z = v[3:]
    z += '=' * ((4 - len(z) % 4) % 4)
    return gzip.decompress(base64.b64decode(z)).decode('utf-8')

def enc(code):
    return 'gz:' + base64.b64encode(gzip.compress(code.encode('utf-8'), mtime=0)).decode('ascii').rstrip('=')

code = dec(pack['review_local_ui'])
code_before = code
assert '1.2.3-beta3 review-layout-refine' in code
assert '</style>' in code

# Beta4 corrective patch after real-device regression:
# beta3's absolute-positioned root like counter escaped the metadata row on some cards.
# Keep the body-width improvement, but return like to normal flex flow at the far right.
scoped = (
    '/* qidian-next 1.2.3-beta4 restore-like-flow */'
    '.comment>.mainRow>.body>.metaLine{display:flex!important;align-items:center!important;'
    'gap:4px!important;width:100%!important;min-width:0!important;min-height:18px!important;line-height:18px!important;'
    'padding-right:0!important;box-sizing:border-box!important;}'
    '.comment>.mainRow>.body>.metaLine>.like{position:static!important;right:auto!important;bottom:auto!important;'
    'margin:0 0 0 auto!important;padding:0!important;display:inline-flex!important;align-items:center!important;'
    'align-self:center!important;justify-content:flex-end!important;gap:2px!important;flex:0 0 auto!important;'
    'height:16px!important;line-height:16px!important;font-size:10px!important;color:#9ca3af!important;'
    'transform:none!important;vertical-align:middle!important;white-space:nowrap!important;}'
    '.comment>.mainRow>.body>.metaLine>.like svg{width:13px!important;height:13px!important;display:block!important;'
    'flex:0 0 13px!important;align-self:center!important;margin:0!important;vertical-align:middle!important;}'
    '.comment>.body>.metaLine{display:flex!important;align-items:center!important;width:100%!important;min-width:0!important;'
    'min-height:18px!important;line-height:18px!important;padding-right:0!important;box-sizing:border-box!important;}'
    '.comment>.body>.metaLine>.like{position:static!important;right:auto!important;bottom:auto!important;'
    'margin:0 0 0 auto!important;padding:0!important;display:inline-flex!important;align-items:center!important;'
    'align-self:center!important;justify-content:flex-end!important;gap:2px!important;flex:0 0 auto!important;'
    'height:16px!important;line-height:16px!important;transform:none!important;vertical-align:middle!important;white-space:nowrap!important;}'
    '.comment>.body>.metaLine>.like svg{width:13px!important;height:13px!important;display:block!important;'
    'flex:0 0 13px!important;align-self:center!important;margin:0!important;vertical-align:middle!important;}'
)
code = code.replace('</style>', scoped + '</style>', 1)
assert code != code_before
assert '1.2.3-beta4 restore-like-flow' in code
assert 'position:static!important;right:auto!important;bottom:auto!important' in code

pack['review_local_ui'] = enc(code)
for k, v in pack_before.items():
    if k != 'review_local_ui':
        assert pack.get(k) == v, 'non-target lazy module changed: ' + k

s['jsLib'] = lib[:a] + json.dumps(pack, ensure_ascii=False, separators=(',', ':')) + lib[b:]
s['bookSourceName'] = '🌈 起点增强 · Beta'
s['bookSourceComment'] = (
    'v1.2.3-beta4：根据真机反馈回退 beta3 的点赞绝对定位方案。点赞重新进入楼号/时间/地点元信息行，'
    '使用正常 flex 流并靠右显示，避免点赞跑到回复卡片上方或主评论卡片底部。保留 beta3 已验证的正文列宽度扩展，'
    '点赞尺寸继续保持 13px 图标/10px 数字。仅修改 review_local_ui；楼中楼、回复加载、情无/小雨桥接、Argus、'
    '正文、目录、搜索、账号、ruleContent、Rhino loader、本章说及其它 Provider 全部冻结。Stable 1.2.2 不变。'
)
BETA.write_text(json.dumps(arr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
source_sha = hashlib.sha256(BETA.read_bytes()).hexdigest()

summary = 'Beta 1.2.3-beta4：撤销 beta3 导致点赞脱离评论元信息行的绝对定位，恢复同一行靠右显示。'
tags = ['起点','测试版','段评','评论页','UI修复','点赞','布局回归修复','Stable1.2.2基线']
changes = [
    '根据真机截图确认 beta3 的 absolute 锚定存在布局回归，立即撤销该方案',
    '主评论点赞恢复 normal flex flow，并通过 margin-left:auto 保持在元信息行最右侧',
    '点赞重新和楼号、时间、地点处于同一行，不再落到回复区域或卡片底部',
    '保留 beta3 的正文列宽度扩展，点赞仍为 13px 图标 / 10px 数字',
    '仅修改 review_local_ui；其它业务模块和 Stable 1.2.2 全部冻结'
]

def patch_entry(e, include_type=False):
    e = dict(e or {})
    e.update({
        'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta',
        'version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,
        'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,
        'sha256':source_sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json'
    })
    if include_type:
        e['type'] = 'novel'
    return e

mp = ROOT/'manifest.json'
m = json.loads(mp.read_text(encoding='utf-8'))
m['updatedAt'] = TS
for i,e in enumerate(m.get('sources', [])):
    if isinstance(e, dict) and e.get('id') == 'qidian-next-beta':
        ne = dict(e); ne.update(patch_entry(e)); ne['category']='novel'; ne['artifactType']='bookSource'; ne['bookSourceUrl']=IDENTITY
        m['sources'][i] = ne; break
else:
    raise AssertionError('manifest beta entry missing')
mp.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

bp = ROOT/'subscription/beta.json'
bj = json.loads(bp.read_text(encoding='utf-8')); bj['updatedAt']=TS; bj['generatedAt']=TS
for i,e in enumerate(bj.get('items', [])):
    if e.get('id') == 'qidian-next-beta': bj['items'][i] = patch_entry(e); break
else: raise AssertionError('beta subscription entry missing')
bp.write_text(json.dumps(bj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

np = ROOT/'subscription/novel.json'
nj = json.loads(np.read_text(encoding='utf-8')); nj['updatedAt']=TS; nj['generatedAt']=TS
for i,e in enumerate(nj.get('items', [])):
    if e.get('id') == 'qidian-next-beta': nj['items'][i] = patch_entry(e, include_type=True); break
else: raise AssertionError('novel beta entry missing')
np.write_text(json.dumps(nj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

bund = ROOT/'bundles/all-beta.json'
ba = json.loads(bund.read_text(encoding='utf-8'))
for i,o in enumerate(ba):
    if isinstance(o, dict) and o.get('bookSourceUrl') == IDENTITY: ba[i] = arr[0] if isinstance(arr,list) else arr; break
else: ba.insert(0, arr[0] if isinstance(arr,list) else arr)
bund.write_text(json.dumps(ba, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

dp = ROOT/'rss/data/details/beta/qidian-next.json'
detail = {
    'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,
    'badges':['Beta',VERSION,'段评UI','布局回归修复'],
    'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,
    'sections':[
        {'title':'回归修复','text':'撤销 beta3 的点赞绝对定位；真机已证明该方案会让点赞掉到回复区域或卡片底部。'},
        {'title':'当前布局','text':'点赞恢复为元信息行内普通 flex 元素，并通过 margin-left:auto 靠右；与楼号、时间、地点保持同一行。'},
        {'title':'正文宽度','text':'保留 beta3 对主评论 body/content 的宽度释放，不回退正文有效显示宽度。'},
        {'title':'严格隔离','text':'仅修改 review_local_ui；楼中楼、回复加载及其它业务模块不变。'}
    ]
}
dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

release = (
    '## 2026-09-13 · qidian-next 1.2.3-beta4 — 段评点赞布局回归修复\n'
    '- 用户真机反馈 `1.2.3-beta3` 改得更差；截图确认主评论点赞会脱离元信息行，跑到回复区域上方或评论卡片底部。\n'
    '- 撤销 beta3 的点赞 absolute 锚定方案，恢复正常 flex 流；使用 `margin-left:auto` 将点赞保持在楼号/时间/地点同一行的最右侧。\n'
    '- 继续保持 13px 点赞图标 / 10px 数字；保留 beta3 的正文列宽度扩展，不回退正文有效宽度。\n'
    '- 仅修改 `review_local_ui`；楼中楼、回复加载、情无/小雨桥接、Argus、正文、目录、搜索、账号、`ruleContent`、Rhino loader、本章说及其它 Provider 全部冻结。\n'
    '- Stable 1.2.2 保持不变，等待真机确认。\n\n'
)
for p in [ROOT/'docs/RELEASE_LOG.md', ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md']:
    old = p.read_text(encoding='utf-8')
    if not old.startswith('## 2026-09-13 · qidian-next 1.2.3-beta4'):
        p.write_text(release + old, encoding='utf-8')

assert hashlib.sha256(STABLE.read_bytes()).hexdigest() == STABLE_EXPECTED, 'Stable changed'
new_arr = json.loads(BETA.read_text(encoding='utf-8')); bs = new_arr[0] if isinstance(new_arr,list) else new_arr
assert bs['bookSourceUrl'] == IDENTITY and '1.2.3-beta4' in bs['bookSourceComment']
newlib = bs['jsLib']; na = newlib.index(mk) + len(mk)
try: nb = newlib.index(';\nvar QF_MOD38_EXPORTS=', na)
except ValueError: nb = newlib.index(';var QF_MOD38_EXPORTS=', na)
newpack = json.loads(newlib[na:nb])
newcode = dec(newpack['review_local_ui'])
assert '1.2.3-beta4 restore-like-flow' in newcode
assert 'position:static!important;right:auto!important;bottom:auto!important' in newcode
for k,v in pack_before.items():
    if k != 'review_local_ui': assert newpack.get(k) == v, 'gate: non-target module drift: ' + k
for p in [mp,bp,np,bund,dp]: json.loads(p.read_text(encoding='utf-8'))
assert any(e.get('id')=='qidian-next-beta' and e.get('version')==VERSION for e in json.loads(bp.read_text(encoding='utf-8'))['items'])
assert any(e.get('id')=='qidian-next-beta' and e.get('version')==VERSION for e in json.loads(np.read_text(encoding='utf-8'))['items'])
print('PASS', VERSION, source_sha, 'stable', stable_hash)
