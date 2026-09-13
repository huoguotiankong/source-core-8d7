import copy, hashlib, json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path('.')
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
VERSION = '1.2.4-beta4'
VC = 12044
IDENTITY = 'https://m.qidian.com/?qf_source=qidian_next_8d7'
STABLE_EXPECTED = '1eaffa24543b2af58aed1368578368ea326ffb0170338971bde558df725bed87'
TS = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
RAW = f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP = f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT = 'legado://import/importonline?src=' + RAW
DETAIL = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_bytes = STABLE.read_bytes()
stable_sha = hashlib.sha256(stable_bytes).hexdigest()
assert stable_sha == STABLE_EXPECTED, f'unexpected Stable baseline: {stable_sha}'
arr = json.loads(stable_bytes.decode('utf-8'))
assert isinstance(arr, list) and len(arr) == 1
stable_src = arr[0]
assert stable_src.get('bookSourceUrl') == IDENTITY
assert 'v1.2.2 Stable' in stable_src.get('bookSourceComment', '')

# Emergency isolation build: runtime/business source is copied verbatim from the confirmed Stable.
beta_src = copy.deepcopy(stable_src)
beta_src['bookSourceName'] = '🌈 起点增强 · Beta'
beta_src['bookSourceComment'] = (
    'v1.2.4-beta4：目录恢复隔离版。由于 beta2 / beta3 真机仍出现目录整页空白，本版完全撤出 1.2.4 系列目录字数与评论快通道实验，'
    '业务运行代码逐字段复制已真机确认的 Stable 1.2.2。除 bookSourceName / bookSourceComment 外，不允许修改 jsLib、ruleToc、ruleContent、'
    '搜索、详情、账号、评论、正文或任何 Provider。该版只用于确认目录是否恢复，并隔离故障来源。'
)

# Hard gate: every source field except the two display metadata fields must be identical to Stable 1.2.2.
allowed = {'bookSourceName', 'bookSourceComment'}
assert set(beta_src.keys()) == set(stable_src.keys())
for k in stable_src:
    if k not in allowed:
        assert beta_src[k] == stable_src[k], f'runtime field changed: {k}'
assert beta_src['jsLib'] == stable_src['jsLib']
assert beta_src.get('ruleToc') == stable_src.get('ruleToc')
assert beta_src.get('ruleContent') == stable_src.get('ruleContent')

out = [beta_src]
BETA.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
source_sha = hashlib.sha256(BETA.read_bytes()).hexdigest()

summary = 'Beta 1.2.4-beta4：目录恢复隔离版，业务运行代码完整复制已确认 Stable 1.2.2。'
tags = ['起点','测试版','目录恢复','Stable1.2.2基线','隔离验证']
changes = [
    'beta2 / beta3 真机目录仍整页空白，本版停止继续猜测式修补',
    'Beta 业务运行代码从 Stable 1.2.2 重新完整复制，不继承 beta1 的 W 字段改动，也不继承 beta2/beta3 的 review_local_ui 改动',
    '除书源显示名称与版本说明外，jsLib、ruleToc、ruleContent、搜索、详情、账号、评论、正文及所有 Provider 与 Stable 1.2.2 逐字段完全一致',
    '本版只验证目录恢复；确认后再以单模块方式重新引入评论优化和章节字数'
]

def patch_entry(e, typed=False):
    e = dict(e or {})
    e.update({
        'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,
        'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,
        'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,
        'versionCode':VC,'sha256':source_sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json'
    })
    if typed: e['type'] = 'novel'
    return e

mp = ROOT/'manifest.json'
m = json.loads(mp.read_text(encoding='utf-8')); m['updatedAt'] = TS
for i,e in enumerate(m.get('sources', [])):
    if isinstance(e,dict) and e.get('id') == 'qidian-next-beta':
        ne = patch_entry(e); ne['category']='novel'; ne['artifactType']='bookSource'; ne['bookSourceUrl']=IDENTITY
        m['sources'][i] = ne; break
else: raise AssertionError('manifest qidian-next-beta missing')
mp.write_text(json.dumps(m, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

for path, typed in [(ROOT/'subscription/beta.json', False), (ROOT/'subscription/novel.json', True)]:
    d = json.loads(path.read_text(encoding='utf-8')); d['updatedAt']=TS; d['generatedAt']=TS
    for i,e in enumerate(d.get('items', [])):
        if e.get('id') == 'qidian-next-beta': d['items'][i] = patch_entry(e, typed); break
    else: raise AssertionError(f'{path} qidian-next-beta missing')
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

bund = ROOT/'bundles/all-beta.json'
ba = json.loads(bund.read_text(encoding='utf-8'))
for i,o in enumerate(ba):
    if isinstance(o,dict) and o.get('bookSourceUrl') == IDENTITY: ba[i] = beta_src; break
else: ba.insert(0, beta_src)
bund.write_text(json.dumps(ba, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

detail = {
    'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,
    'badges':['Beta',VERSION,'目录恢复','Stable 1.2.2 隔离基线'],
    'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,
    'sections':[
        {'title':'为什么再回退一层','text':'真机确认 beta3 目录仍为空，说明仅撤销 W 字段还不足以恢复。beta3 仍保留了重新打包后的评论模块，因此本版把整个业务运行代码恢复为 Stable 1.2.2。'},
        {'title':'强隔离门禁','text':'除 bookSourceName / bookSourceComment 外，Beta 源每一个字段都必须与 Stable 1.2.2 相同；jsLib、ruleToc、ruleContent 等均做精确相等校验。'},
        {'title':'本版暂时撤出的优化','text':'章节字数 W、评论首屏10条快通道和 beta2/beta3 评论排版实验全部暂时撤出。先恢复目录，再逐个模块重新引入。'},
        {'title':'测试重点','text':'只需确认目录能否恢复正常加载、章节数量和更新时间是否正常。'}
    ]
}
(ROOT/'rss/data/details/beta/qidian-next.json').write_text(json.dumps(detail, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

release = (
    f'## 2026-09-13 · qidian-next {VERSION} — 目录恢复隔离版\n'
    '- 真机确认 `1.2.4-beta3` 目录仍无法加载，因此停止在现有 Beta 上继续猜测式修补。\n'
    '- 从已真机确认的 Stable 1.2.2 重新完整复制业务源；不继承 beta1 的目录 W 字段扩展，也不继承 beta2/beta3 的 `review_local_ui` 重打包。\n'
    '- 强门禁：除 `bookSourceName` / `bookSourceComment` 外，所有书源字段与 Stable 1.2.2 精确相等，包括 `jsLib`、`ruleToc`、`ruleContent`。\n'
    '- 本版只验证目录恢复；章节字数和评论优化全部暂缓，待恢复确认后再逐域重新引入。\n'
    '- Stable 1.2.2 保持不变。\n\n'
)
for p in [ROOT/'docs/RELEASE_LOG.md', ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md']:
    old = p.read_text(encoding='utf-8')
    if not old.startswith(f'## 2026-09-13 · qidian-next {VERSION}'):
        p.write_text(release + old, encoding='utf-8')

# Publication gates.
assert hashlib.sha256(STABLE.read_bytes()).hexdigest() == STABLE_EXPECTED, 'Stable changed'
check = json.loads(BETA.read_text(encoding='utf-8'))[0]
for k in stable_src:
    if k not in allowed: assert check[k] == stable_src[k], f'post-write mismatch: {k}'
for p in [mp, ROOT/'subscription/beta.json', ROOT/'subscription/novel.json', bund, ROOT/'rss/data/details/beta/qidian-next.json']:
    json.loads(p.read_text(encoding='utf-8'))
print('PASS', VERSION, 'source_sha', source_sha, 'stable_sha', stable_sha, 'jsLib_sha', hashlib.sha256(stable_src['jsLib'].encode()).hexdigest())
