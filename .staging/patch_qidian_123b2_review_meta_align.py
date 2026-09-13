import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path('.')
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
VERSION = '1.2.3-beta2'
VC = 12032
TS = '2026-09-13T12:08:00+08:00'
IDENTITY = 'https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW = f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP = f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT = 'legado://import/importonline?src=' + RAW
DETAIL = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'

stable_hash = hashlib.sha256(STABLE.read_bytes()).hexdigest()
arr = json.loads(BETA.read_text(encoding='utf-8'))
s = arr[0] if isinstance(arr, list) else arr
assert s.get('bookSourceUrl') == IDENTITY
assert '1.2.3-beta1' in s.get('bookSourceComment', ''), 'expected beta1 baseline'

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

# Beta2: only correct the vertical alignment of the root-comment like block.
# Keep Beta1 sizes (13px icon / 10px number) and width-density changes untouched.
scoped = (
    '.metaLine{align-items:center!important;}'
    '.metaLine .like{display:inline-flex!important;align-items:center!important;align-self:center!important;'
    'height:16px!important;line-height:16px!important;margin-top:0!important;margin-bottom:0!important;'
    'vertical-align:middle!important;}'
    '.metaLine .like svg{display:block!important;align-self:center!important;flex:0 0 auto!important;'
    'margin:0!important;vertical-align:middle!important;}'
)
code = code.replace('</style>', scoped + '</style>', 1)
assert code != code_before
assert '.metaLine .like{display:inline-flex!important;align-items:center!important;align-self:center!important;' in code
assert 'height:16px!important;line-height:16px!important' in code

pack['review_local_ui'] = enc(code)
for k, v in pack_before.items():
    if k != 'review_local_ui':
        assert pack.get(k) == v, 'non-target lazy module changed: ' + k

s['jsLib'] = lib[:a] + json.dumps(pack, ensure_ascii=False, separators=(',', ':')) + lib[b:]
s['bookSourceName'] = '🌈 起点增强 · Beta'
s['bookSourceComment'] = (
    'v1.2.3-beta2：仅修正段评页楼主点赞区域的纵向对齐。保持 beta1 的 13px 点赞图标、10px 数字、'
    '7px 右内边距和正文宽度优化不变；将点赞容器与楼号/时间/地点统一为同一元信息行的垂直居中，'
    '消除点赞整体偏上的视觉问题。楼中楼、评论请求、情无/小雨桥接、Argus、正文、目录、搜索、账号、'
    'ruleContent、Rhino loader、本章说卡片及其它 Provider 全部冻结。Stable 1.2.2 不变。'
)
BETA.write_text(json.dumps(arr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
source_sha = hashlib.sha256(BETA.read_bytes()).hexdigest()

summary = 'Beta 1.2.3-beta2：修正楼主点赞与楼号、时间、地点的纵向基线，让整条元信息真正处于同一水平行。'
tags = ['起点','测试版','段评','评论页','UI优化','点赞','垂直对齐','Stable1.2.2基线']
changes = [
    '保持 beta1 的 13px 点赞图标与 10px 点赞数字不变',
    '将 metaLine 统一为垂直居中，点赞容器使用 inline-flex + center 对齐',
    '点赞容器固定 16px 行高/高度，SVG 改为 block，消除图标基线造成的上浮',
    'beta1 的右侧留白压缩和正文宽度优化保持不变',
    '仅修改 review_local_ui；其它业务模块全部冻结，Stable 1.2.2 不变'
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
    'badges':['Beta',VERSION,'段评UI','点赞对齐'],
    'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,
    'sections':[
        {'title':'本轮修正','text':'楼主点赞区域改为和楼号、时间、地点同一元信息行垂直居中；点赞图标与数字不再整体偏上。'},
        {'title':'尺寸保持','text':'继续沿用 beta1 的 13px 点赞图标、10px 数字，不重新放大点赞。'},
        {'title':'布局保持','text':'beta1 已完成的右侧留白压缩与正文宽度释放继续保留。'},
        {'title':'严格隔离','text':'仅修改 review_local_ui 样式；评论请求、楼中楼、正文、目录、搜索、账号、本章说等逻辑不变。'}
    ]
}
dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

release = (
    '## 2026-09-13 · qidian-next 1.2.3-beta2 — 段评点赞纵向对齐修正\n'
    '- 基于 `1.2.3-beta1` 继续微调，只修改 `review_local_ui`。\n'
    '- 保持 13px 点赞图标、10px 点赞数字及 beta1 的正文宽度优化不变。\n'
    '- `metaLine` 改为统一垂直居中；点赞容器采用 `inline-flex + align-items:center`，固定 16px 行高/高度；SVG 改为 block，消除基线导致的整体上浮。\n'
    '- 目标是让点赞与楼号、时间、地点处于同一视觉水平线。\n'
    '- Stable 1.2.2 与其它业务模块保持不变，继续等待真机确认。\n\n'
)
for p in [ROOT/'docs/RELEASE_LOG.md', ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md']:
    old = p.read_text(encoding='utf-8')
    if not old.startswith('## 2026-09-13 · qidian-next 1.2.3-beta2'):
        p.write_text(release + old, encoding='utf-8')

# gates
assert hashlib.sha256(STABLE.read_bytes()).hexdigest() == stable_hash, 'Stable changed'
new_arr = json.loads(BETA.read_text(encoding='utf-8'))
bs = new_arr[0] if isinstance(new_arr, list) else new_arr
assert bs['bookSourceUrl'] == IDENTITY and '1.2.3-beta2' in bs['bookSourceComment']
newlib = bs['jsLib']; na = newlib.index(mk) + len(mk)
try:
    nb = newlib.index(';\nvar QF_MOD38_EXPORTS=', na)
except ValueError:
    nb = newlib.index(';var QF_MOD38_EXPORTS=', na)
newpack = json.loads(newlib[na:nb])
assert dec(newpack['review_local_ui']) != code_before
for k,v in pack_before.items():
    if k != 'review_local_ui':
        assert newpack.get(k) == v, 'gate: non-target module drift: ' + k
for p in [mp,bp,np,bund,dp]:
    json.loads(p.read_text(encoding='utf-8'))
assert any(e.get('id')=='qidian-next-beta' and e.get('version')==VERSION for e in json.loads(bp.read_text(encoding='utf-8'))['items'])
assert any(e.get('id')=='qidian-next-beta' and e.get('version')==VERSION for e in json.loads(np.read_text(encoding='utf-8'))['items'])
print('PASS', VERSION, source_sha, 'stable', stable_hash)
