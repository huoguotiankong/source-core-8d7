import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path('.')
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
VERSION = '1.2.3-beta3'
VC = 12033
TS = '2026-09-13T14:41:00+08:00'
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
assert '1.2.3-beta2' in s.get('bookSourceComment', ''), 'expected beta2 baseline'

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
assert '.metaLine{' in code and 'class="metaLine"' in code
assert '.like{' in code and '.like svg{' in code
assert '</style>' in code

# Beta3: follow the user's reference layout more closely.
# 1) Let the root comment body flex-fill all remaining width beside the avatar.
# 2) Take the root like block out of normal meta flex distribution and anchor it
#    at the meta row's bottom-right, so it neither floats upward nor steals width.
# Keep beta1/beta2 sizes and all non-UI logic untouched.
scoped = (
    '/* qidian-next 1.2.3-beta3 review-layout-refine */'
    '.comment{padding-right:5px!important;}'
    '.comment>.mainRow{display:flex!important;align-items:flex-start!important;gap:8px!important;'
    'width:100%!important;min-width:0!important;max-width:none!important;box-sizing:border-box!important;}'
    '.comment>.mainRow>.body{flex:1 1 0!important;width:0!important;min-width:0!important;max-width:none!important;'
    'padding-right:0!important;margin-right:0!important;box-sizing:border-box!important;}'
    '.comment>.mainRow>.body>.content{display:block!important;width:100%!important;min-width:0!important;max-width:none!important;'
    'padding-right:2px!important;margin-right:0!important;box-sizing:border-box!important;}'
    '.comment>.mainRow>.body>.metaLine{position:relative!important;display:flex!important;align-items:baseline!important;'
    'gap:4px!important;width:100%!important;min-width:0!important;min-height:18px!important;line-height:18px!important;'
    'padding-right:48px!important;box-sizing:border-box!important;}'
    '.comment>.mainRow>.body>.metaLine>.like{position:absolute!important;right:2px!important;bottom:-1px!important;'
    'margin:0!important;display:inline-flex!important;align-items:flex-end!important;align-self:auto!important;gap:2px!important;'
    'height:16px!important;line-height:16px!important;font-size:10px!important;color:#9ca3af!important;'
    'transform:none!important;vertical-align:baseline!important;}'
    '.comment>.mainRow>.body>.metaLine>.like svg{width:13px!important;height:13px!important;display:block!important;'
    'flex:0 0 13px!important;align-self:flex-end!important;margin:0!important;vertical-align:baseline!important;}'
    # Fallback for variants where body is a direct child of the root comment.
    '.comment>.body{flex:1 1 0!important;min-width:0!important;max-width:none!important;padding-right:0!important;margin-right:0!important;}'
    '.comment>.body>.content{width:100%!important;min-width:0!important;max-width:none!important;padding-right:2px!important;margin-right:0!important;box-sizing:border-box!important;}'
    '.comment>.body>.metaLine{position:relative!important;align-items:baseline!important;width:100%!important;min-width:0!important;'
    'min-height:18px!important;line-height:18px!important;padding-right:48px!important;box-sizing:border-box!important;}'
    '.comment>.body>.metaLine>.like{position:absolute!important;right:2px!important;bottom:-1px!important;margin:0!important;'
    'align-items:flex-end!important;align-self:auto!important;height:16px!important;line-height:16px!important;transform:none!important;}'
)
code = code.replace('</style>', scoped + '</style>', 1)
assert code != code_before
assert '1.2.3-beta3 review-layout-refine' in code
assert 'position:absolute!important;right:2px!important;bottom:-1px!important' in code
assert 'flex:1 1 0!important;width:0!important' in code

pack['review_local_ui'] = enc(code)
for k, v in pack_before.items():
    if k != 'review_local_ui':
        assert pack.get(k) == v, 'non-target lazy module changed: ' + k

s['jsLib'] = lib[:a] + json.dumps(pack, ensure_ascii=False, separators=(',', ':')) + lib[b:]
s['bookSourceName'] = '🌈 起点增强 · Beta'
s['bookSourceComment'] = (
    'v1.2.3-beta3：参考真机目标样式继续收口段评主评论布局。点赞从元信息 flex 流中独立出来，'
    '固定锚定元信息行右下角，保持 13px 图标/10px 数字并与楼号、时间、地点底线对齐；'
    '主评论正文列改为 flex 填满头像右侧剩余空间，进一步收紧主行间距和右内边距，使评论文字获得更多有效宽度。'
    '仅修改 review_local_ui；楼中楼结构与回复加载、情无/小雨桥接、Argus、正文、目录、搜索、账号、'
    'ruleContent、Rhino loader、本章说及其它 Provider 全部冻结。Stable 1.2.2 不变。'
)
BETA.write_text(json.dumps(arr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
source_sha = hashlib.sha256(BETA.read_bytes()).hexdigest()

summary = 'Beta 1.2.3-beta3：参考真机目标样式，点赞锚定元信息右下角，正文列真正填满头像右侧剩余宽度。'
tags = ['起点','测试版','段评','评论页','UI优化','点赞','正文宽度','参考布局','Stable1.2.2基线']
changes = [
    '点赞脱离元信息 flex 分布，改为右下角独立锚定，避免视觉上浮和挤占元信息宽度',
    '保持 13px 点赞图标 / 10px 数字，并按楼号、时间、地点底线对齐',
    '主评论正文列改为 flex:1 + min-width:0，主行 gap 收紧到 8px、评论右内边距收紧到 5px',
    '正文 content 明确占满主评论 body 可用宽度，减少参考图中不存在的右侧无效留白',
    '仅修改 review_local_ui；楼中楼与其它业务模块全部冻结，Stable 1.2.2 不变'
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

# manifest
mp = ROOT/'manifest.json'
m = json.loads(mp.read_text(encoding='utf-8'))
m['updatedAt'] = TS
for i,e in enumerate(m.get('sources', [])):
    if isinstance(e, dict) and e.get('id') == 'qidian-next-beta':
        ne = dict(e)
        ne.update(patch_entry(e))
        ne['category'] = 'novel'; ne['artifactType'] = 'bookSource'; ne['bookSourceUrl'] = IDENTITY
        m['sources'][i] = ne
        break
else:
    raise AssertionError('manifest beta entry missing')
mp.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# beta subscription
bp = ROOT/'subscription/beta.json'
bj = json.loads(bp.read_text(encoding='utf-8'))
bj['updatedAt'] = TS; bj['generatedAt'] = TS
for i,e in enumerate(bj.get('items', [])):
    if e.get('id') == 'qidian-next-beta':
        bj['items'][i] = patch_entry(e)
        break
else:
    raise AssertionError('beta subscription entry missing')
bp.write_text(json.dumps(bj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# novel type subscription
np = ROOT/'subscription/novel.json'
nj = json.loads(np.read_text(encoding='utf-8'))
nj['updatedAt'] = TS; nj['generatedAt'] = TS
for i,e in enumerate(nj.get('items', [])):
    if e.get('id') == 'qidian-next-beta':
        nj['items'][i] = patch_entry(e, include_type=True)
        break
else:
    raise AssertionError('novel beta entry missing')
np.write_text(json.dumps(nj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# beta bundle
bund = ROOT/'bundles/all-beta.json'
ba = json.loads(bund.read_text(encoding='utf-8'))
for i,o in enumerate(ba):
    if isinstance(o, dict) and o.get('bookSourceUrl') == IDENTITY:
        ba[i] = arr[0] if isinstance(arr, list) else arr
        break
else:
    ba.insert(0, arr[0] if isinstance(arr, list) else arr)
bund.write_text(json.dumps(ba, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# beta detail
dp = ROOT/'rss/data/details/beta/qidian-next.json'
detail = {
    'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,
    'badges':['Beta',VERSION,'段评UI','参考布局','正文宽度'],
    'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,
    'sections':[
        {'title':'点赞位置','text':'点赞脱离普通 flex 分布，固定在主评论元信息行右下角，并以底线方式和楼号、时间、地点对齐。'},
        {'title':'正文宽度','text':'主评论 body 改为 flex 填满头像右侧剩余区域，content 明确占满 body 可用宽度，减少右侧无效留白。'},
        {'title':'尺寸保持','text':'继续保持 13px 点赞图标与 10px 数字，不重新放大点赞视觉层级。'},
        {'title':'严格隔离','text':'仅修改 review_local_ui 样式；楼中楼、回复加载和其它业务模块全部冻结。'}
    ]
}
dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

release = (
    '## 2026-09-13 · qidian-next 1.2.3-beta3 — 段评点赞锚定与正文宽度继续收口\n'
    '- 根据用户真机截图，并参考目标页面布局，基于 `1.2.3-beta2` 继续微调，仅修改 `review_local_ui`。\n'
    '- 点赞从元信息 flex 流中独立，固定锚定主评论元信息行右下角；保持 13px 图标 / 10px 数字，并按楼号、时间、地点底线对齐。\n'
    '- 主评论 body 改为 `flex:1 + min-width:0`，主行 gap 收紧到 8px，评论右内边距收紧到 5px；content 明确占满 body 可用宽度。\n'
    '- 目标是进一步减少右侧无效留白与过早换行，让文字占用区域更接近用户提供的参考图。\n'
    '- 楼中楼结构与回复加载、情无/小雨桥接、Argus、正文、目录、搜索、账号、`ruleContent`、Rhino loader、本章说及其它 Provider 全部冻结。\n'
    '- Stable 1.2.2 保持不变，继续等待真机确认。\n\n'
)
for p in [ROOT/'docs/RELEASE_LOG.md', ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md']:
    old = p.read_text(encoding='utf-8')
    if not old.startswith('## 2026-09-13 · qidian-next 1.2.3-beta3'):
        p.write_text(release + old, encoding='utf-8')

# gates
assert hashlib.sha256(STABLE.read_bytes()).hexdigest() == STABLE_EXPECTED, 'Stable changed'
new_arr = json.loads(BETA.read_text(encoding='utf-8'))
bs = new_arr[0] if isinstance(new_arr, list) else new_arr
assert bs['bookSourceUrl'] == IDENTITY and '1.2.3-beta3' in bs['bookSourceComment']
newlib = bs['jsLib']; na = newlib.index(mk) + len(mk)
try:
    nb = newlib.index(';\nvar QF_MOD38_EXPORTS=', na)
except ValueError:
    nb = newlib.index(';var QF_MOD38_EXPORTS=', na)
newpack = json.loads(newlib[na:nb])
new_review = dec(newpack['review_local_ui'])
assert new_review != code_before
assert '1.2.3-beta3 review-layout-refine' in new_review
for k,v in pack_before.items():
    if k != 'review_local_ui':
        assert newpack.get(k) == v, 'gate: non-target module drift: ' + k
for p in [mp,bp,np,bund,dp]:
    json.loads(p.read_text(encoding='utf-8'))
assert any(e.get('id')=='qidian-next-beta' and e.get('version')==VERSION and e.get('versionCode')==VC for e in json.loads(bp.read_text(encoding='utf-8'))['items'])
assert any(e.get('id')=='qidian-next-beta' and e.get('version')==VERSION for e in json.loads(np.read_text(encoding='utf-8'))['items'])
print('PASS', VERSION, source_sha, 'stable', hashlib.sha256(STABLE.read_bytes()).hexdigest())
