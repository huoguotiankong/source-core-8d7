import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path('.')
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
VERSION = '1.2.3-beta1'
VC = 12031
DATE = '2026-09-13'
TS = '2026-09-13T10:45:00+08:00'
RAW = f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP = f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT = 'legado://import/importonline?src=' + RAW
DETAIL = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'
IDENTITY = 'https://m.qidian.com/?qf_source=qidian_next_8d7'

stable_bytes = STABLE.read_bytes()
stable_hash = hashlib.sha256(stable_bytes).hexdigest()
stable_arr = json.loads(stable_bytes.decode('utf-8'))
arr = json.loads(json.dumps(stable_arr, ensure_ascii=False))
s = arr[0] if isinstance(arr, list) else arr
stable_s = stable_arr[0] if isinstance(stable_arr, list) else stable_arr
assert s.get('bookSourceUrl') == IDENTITY, s.get('bookSourceUrl')

lib = s['jsLib']
mk = 'var QF_MOD38_PACK='
a = lib.index(mk) + len(mk)
try:
    b = lib.index(';\nvar QF_MOD38_EXPORTS=', a)
    export_prefix = ';\nvar QF_MOD38_EXPORTS='
except ValueError:
    b = lib.index(';var QF_MOD38_EXPORTS=', a)
    export_prefix = ';var QF_MOD38_EXPORTS='
pack = json.loads(lib[a:b])
assert 'review_local_ui' in pack
pack_before = dict(pack)

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
assert '.metaLine{' in code, 'root meta-line layout missing'
assert '.like{' in code and '.like svg{' in code, 'root like CSS missing'
assert 'class="metaLine"' in code, 'root meta-line template missing'

# Append declarations inside an existing selector rule. Later declarations win,
# so the patch remains narrowly scoped and does not rewrite unrelated CSS.
def patch_rule(src, selector, props, required=True):
    pat = re.compile(re.escape(selector) + r'\{([^{}]*)\}')
    matches = list(pat.finditer(src))
    if not matches:
        if required:
            raise AssertionError('missing CSS selector: ' + selector)
        return src
    if len(matches) != 1:
        raise AssertionError('ambiguous CSS selector %s: %d matches' % (selector, len(matches)))
    m = matches[0]
    body = m.group(1).rstrip(';')
    extra = ';'.join(k + ':' + v for k, v in props.items())
    new_rule = selector + '{' + body + (';' if body else '') + extra + '}'
    return src[:m.start()] + new_rule + src[m.end():]

# 1) Root-comment like becomes metadata, not a visual focal point.
code = patch_rule(code, '.like', {
    'gap': '1px',
    'font-size': '10px',
    'line-height': '13px',
    'color': 'var(--muted)'
})
code = patch_rule(code, '.like svg', {
    'width': '13px',
    'height': '13px',
    'stroke-width': '1.45'
})
code = patch_rule(code, '.metaLine', {
    'gap': '4px',
    'width': '100%'
})

# 2) Reclaim the unused right-side column for actual comment text.
# Keep avatar/reply indentation unchanged; only release right-side constraints.
code = patch_rule(code, '.comment', {
    'padding-right': '7px'
})
code = patch_rule(code, '.mainRow', {
    'width': '100%',
    'min-width': '0'
}, required=False)
code = patch_rule(code, '.body', {
    'flex': '1 1 auto',
    'min-width': '0',
    'width': 'auto',
    'max-width': 'none',
    'padding-right': '0',
    'margin-right': '0'
}, required=False)
code = patch_rule(code, '.content', {
    'width': 'auto',
    'max-width': 'none',
    'padding-right': '0',
    'margin-right': '0',
    'overflow-wrap': 'anywhere'
})
code = patch_rule(code, '.meta', {
    'padding-right': '0',
    'max-width': 'none'
})

assert code != code_before
assert 'font-size:10px' in code
assert 'width:13px' in code
assert 'padding-right:7px' in code
assert 'overflow-wrap:anywhere' in code
# Nested replies remain their prior hierarchy (12px like icon from Beta37 line).
assert '.rLike{' in code and '.rLike svg{' in code

pack['review_local_ui'] = enc(code)
for k, v in pack_before.items():
    if k != 'review_local_ui':
        assert pack.get(k) == v, 'non-target lazy module changed: ' + k

s['jsLib'] = lib[:a] + json.dumps(pack, ensure_ascii=False, separators=(',', ':')) + lib[b:]
s['bookSourceName'] = '🌈 起点增强 · Beta'
s['bookSourceComment'] = (
    'v1.2.3-beta1：仅继续优化段评/评论页面视觉。楼主点赞图标与数字降为元信息层级，'
    '与楼号、时间更协调；压缩点赞与元信息间距，释放评论正文右侧无效留白，让文字获得更多横向空间。'
    '楼中楼结构与请求逻辑保持不变；情无/小雨评论桥接、Argus 段评计数、正文、目录、搜索、账号、'
    'ruleContent、Rhino loader、本章说卡片及其它 Provider 全部冻结。Stable 1.2.2 不变。'
)
assert s.get('bookSourceUrl') == stable_s.get('bookSourceUrl') == IDENTITY

BETA.write_text(json.dumps(arr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
source_sha = hashlib.sha256(BETA.read_bytes()).hexdigest()

summary = 'Beta 1.2.3-beta1：缩小楼主点赞并回收评论右侧无效留白，让楼号/时间/点赞层级更统一、正文获得更多横向空间。'
tags = ['起点', '测试版', '段评', '评论页', 'UI优化', '点赞', '信息密度', '正文宽度', 'Stable1.2.2基线']
changes = [
    '楼主点赞图标缩至 13px、数字缩至 10px，改为与楼号/时间同级的弱化元信息',
    '根评论元信息行间距继续收紧，点赞不再形成醒目的右侧视觉块',
    '释放 comment/mainRow/body/content 右侧约束并将评论卡右内边距收紧到 7px，正文可使用更多横向空间',
    '楼中楼结构、点赞层级和回复加载逻辑保持不变',
    '仅修改 review_local_ui；情无/小雨桥接、Argus、正文、目录、搜索、账号、ruleContent、Rhino loader、本章说卡片及其它 Provider 全部冻结',
    'Stable 1.2.2 保持不变，等待真机确认'
]

def beta_entry(base=None, include_type=False):
    e = dict(base or {})
    e.update({
        'id': 'qidian-next-beta',
        'name': '🌈 起点增强 · Beta',
        'summary': summary,
        'icon': e.get('icon', ''),
        'channel': 'beta',
        'version': VERSION,
        'updatedAt': TS,
        'tags': tags,
        'changelog': changes,
        'sourceUrl': RAW,
        'backupUrl': BACKUP,
        'importUrl': IMPORT,
        'detailUrl': DETAIL,
        'versionCode': VC,
        'sha256': source_sha,
        'sourcePath': 'sources/novel/qidian-next/qidian-next-beta.json'
    })
    if include_type:
        e['type'] = 'novel'
    return e

# Manifest: upsert Beta alongside Stable, never replace the Stable entry.
mp = ROOT / 'manifest.json'
m = json.loads(mp.read_text(encoding='utf-8'))
m['updatedAt'] = TS
sources = m.setdefault('sources', [])
manifest_beta = {
    'id': 'qidian-next-beta',
    'name': '🌈 起点增强 · Beta',
    'category': 'novel',
    'artifactType': 'bookSource',
    'channel': 'beta',
    'version': VERSION,
    'versionCode': VC,
    'updatedAt': TS,
    'sourcePath': 'sources/novel/qidian-next/qidian-next-beta.json',
    'sourceUrl': RAW,
    'backupUrl': BACKUP,
    'importUrl': IMPORT,
    'detailUrl': DETAIL,
    'bookSourceUrl': IDENTITY,
    'summary': summary,
    'tags': tags,
    'changelog': changes,
    'sha256': source_sha
}
hit = False
for i, e in enumerate(sources):
    if isinstance(e, dict) and e.get('id') == 'qidian-next-beta':
        ne = dict(e); ne.update(manifest_beta); sources[i] = ne; hit = True; break
if not hit:
    stable_idx = next((i for i,e in enumerate(sources) if isinstance(e,dict) and e.get('id') == 'qidian-next'), 0)
    sources.insert(stable_idx + 1, manifest_beta)
mp.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Beta channel: upsert the active Beta.
bp = ROOT / 'subscription/beta.json'
bj = json.loads(bp.read_text(encoding='utf-8'))
bj['updatedAt'] = TS
bj['generatedAt'] = TS
items = bj.setdefault('items', [])
be = beta_entry()
for i, e in enumerate(items):
    if isinstance(e, dict) and e.get('id') == 'qidian-next-beta':
        items[i] = be; break
else:
    items.insert(0, be)
bp.write_text(json.dumps(bj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Novel type catalog: one logical qidian-next entry only; Beta becomes the current active entry.
np = ROOT / 'subscription/novel.json'
nj = json.loads(np.read_text(encoding='utf-8'))
nj['updatedAt'] = TS
nj['generatedAt'] = TS
nitems = nj.setdefault('items', [])
positions = [i for i,e in enumerate(nitems) if isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta')]
insert_at = min(positions) if positions else 0
nitems[:] = [e for e in nitems if not (isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'))]
nitems.insert(min(insert_at, len(nitems)), beta_entry(include_type=True))
np.write_text(json.dumps(nj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Beta bundle: upsert by stable Legado identity.
bund = ROOT / 'bundles/all-beta.json'
ba = json.loads(bund.read_text(encoding='utf-8'))
if not isinstance(ba, list):
    ba = []
src_obj = arr[0] if isinstance(arr, list) else arr
replaced = False
for i, o in enumerate(ba):
    if isinstance(o, dict) and o.get('bookSourceUrl') == IDENTITY:
        ba[i] = src_obj; replaced = True; break
if not replaced:
    ba.insert(0, src_obj)
# Defensive de-duplication by source identity.
out = []
seen = set()
for o in ba:
    if not isinstance(o, dict):
        continue
    k = str(o.get('bookSourceUrl') or o.get('bookSourceName') or len(out))
    if k in seen:
        continue
    seen.add(k); out.append(o)
bund.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Beta RSS detail.
dp = ROOT / 'rss/data/details/beta/qidian-next.json'
detail = {
    'kind': 'source',
    'title': '🌈 起点增强 · Beta',
    'summary': summary,
    'badges': ['Beta', VERSION, '段评UI', '更宽正文'],
    'sourceUrl': RAW,
    'backupUrl': BACKUP,
    'importUrl': IMPORT,
    'sections': [
        {'title': '点赞层级', 'text': '楼主点赞图标缩至 13px、数字缩至 10px，并继续贴合楼号/时间所在的元信息行，避免点赞喧宾夺主。'},
        {'title': '文字空间', 'text': '压缩评论卡右内边距与元信息间距，解除正文容器的右侧宽度约束，让长评论尽量使用卡片的有效宽度，减少无意义换行。'},
        {'title': '严格隔离', 'text': '本版只改 review_local_ui 视觉层。楼中楼请求、情无/小雨 java.ajax 桥接、Argus 段评计数、正文、目录、搜索、账号、本章说卡片等全部保持 Stable 1.2.2 行为。'},
        {'title': '版本状态', 'text': 'Beta / 测试通道，等待真机确认点赞尺寸、右侧留白和正文换行效果。'}
    ]
}
dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

release = (
    '## 2026-09-13 · qidian-next 1.2.3-beta1 — 段评页面点赞与正文宽度优化\n'
    '- 从用户已确认的 Stable 1.2.2 重新建立 Beta 基线，仅修改 `review_local_ui`。\n'
    '- 楼主点赞图标缩至 13px、数字缩至 10px，视觉层级与楼号/时间对齐；元信息行间距同步收紧。\n'
    '- 评论卡右内边距收紧，并解除 `mainRow/body/content` 的右侧宽度约束，使正文获得更多横向空间、减少过早换行。\n'
    '- 楼中楼结构与回复加载保持不变；情无/小雨评论桥接、Argus 段评计数、正文、目录、搜索、账号、`ruleContent`、Rhino loader、本章说卡片及其它 Provider 全部冻结。\n'
    '- Stable 1.2.2 不变，仅发布 Beta 等待真机确认。\n\n'
)
for p in [ROOT/'docs/RELEASE_LOG.md', ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md']:
    old = p.read_text(encoding='utf-8')
    if not old.startswith('## 2026-09-13 · qidian-next 1.2.3-beta1'):
        p.write_text(release + old, encoding='utf-8')

# Gates: Stable byte-for-byte untouched; Beta identity preserved; every packed module decodes;
# only review_local_ui changed inside the lazy pack.
assert hashlib.sha256(STABLE.read_bytes()).hexdigest() == stable_hash, 'Stable changed'
beta_check = json.loads(BETA.read_text(encoding='utf-8'))
bs = beta_check[0] if isinstance(beta_check, list) else beta_check
assert bs['bookSourceUrl'] == IDENTITY
newlib = bs['jsLib']
na = newlib.index(mk) + len(mk)
try:
    nb = newlib.index(';\nvar QF_MOD38_EXPORTS=', na)
except ValueError:
    nb = newlib.index(';var QF_MOD38_EXPORTS=', na)
newpack = json.loads(newlib[na:nb])
for k, v in newpack.items():
    if isinstance(v, str) and v.startswith('gz:'):
        dec(v)
for k, v in pack_before.items():
    if k != 'review_local_ui':
        assert newpack.get(k) == v, 'gate: non-target module drift: ' + k
assert newpack['review_local_ui'] != pack_before['review_local_ui']

# Catalog gates.
for p in [mp, bp, np, bund, dp]:
    json.loads(p.read_text(encoding='utf-8'))
novel = json.loads(np.read_text(encoding='utf-8'))['items']
assert sum(1 for e in novel if e.get('id') in ('qidian-next','qidian-next-beta')) == 1
assert any(e.get('id') == 'qidian-next-beta' and e.get('version') == VERSION for e in novel)
assert any(e.get('id') == 'qidian-next-beta' and e.get('version') == VERSION for e in json.loads(bp.read_text(encoding='utf-8'))['items'])
print('PASS', VERSION, source_sha, 'stable', stable_hash)
