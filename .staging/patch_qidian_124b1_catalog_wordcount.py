import hashlib
import json
from pathlib import Path

ROOT = Path('.')
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
VERSION = '1.2.4-beta1'
VC = 12041
TS = '2026-09-13T21:10:00+08:00'
IDENTITY = 'https://m.qidian.com/?qf_source=qidian_next_8d7'
STABLE_EXPECTED = '1eaffa24543b2af58aed1368578368ea326ffb0170338971bde558df725bed87'
RAW = f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP = f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT = 'legado://import/importonline?src=' + RAW
DETAIL = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'

stable_hash = hashlib.sha256(STABLE.read_bytes()).hexdigest()
assert stable_hash == STABLE_EXPECTED, 'unexpected Stable baseline: ' + stable_hash
arr = json.loads(STABLE.read_text(encoding='utf-8'))
s = arr[0] if isinstance(arr, list) else arr
assert s.get('bookSourceUrl') == IDENTITY
assert 'v1.2.2 Stable' in s.get('bookSourceComment', ''), 'expected Stable 1.2.2 baseline'

lib = s['jsLib']
old_schema = 'wordCount:["wordCount","WordCount","words","Words","cnt","Cnt","CNT","cW","CW","wC","WC","chapterWordCount","ChapterWordCount","chapterWords","ChapterWords"]'
new_schema = 'wordCount:["wordCount","WordCount","words","Words","cnt","Cnt","CNT","cW","CW","wC","WC","chapterWordCount","ChapterWordCount","chapterWords","ChapterWords","W"]'
old_direct = "['cnt','Cnt','CNT','cW','CW','wC','WC','wordCount','WordCount','wordsCount','WordsCount','chapterWordCount','ChapterWordCount','chapterWords','ChapterWords']"
new_direct = "['cnt','Cnt','CNT','cW','CW','wC','WC','wordCount','WordCount','wordsCount','WordsCount','chapterWordCount','ChapterWordCount','chapterWords','ChapterWords','W']"
assert old_schema in lib, 'catalog schema word aliases changed'
assert old_direct in lib, 'direct toc word aliases changed'
lib2 = lib.replace(old_schema, new_schema, 1).replace(old_direct, new_direct, 1)
assert lib2 != lib
assert new_schema in lib2 and new_direct in lib2
# Only broaden chapter word-count field aliases; do not alter request routes or fallback ordering.
s['jsLib'] = lib2
s['bookSourceName'] = '🌈 起点增强 · Beta'
s['bookSourceComment'] = (
    'v1.2.4-beta1：目录字数兼容修复。基于已真机确认的 Stable 1.2.2，仅扩展目录章节字数字段识别，'
    '新增起点当前/参考目录结构中的 W 字段，同时保留既有 cnt/cW/wC/wordCount 等别名。目录仍沿用现有 APP v3、'
    'getsimple、pager、Web fallback、多层缓存与完整度诊断，不更换成熟目录链；正文、搜索、账号、评论、'
    '情无/小雨、ruleContent、Rhino loader、角色卡、本章说及其它 Provider 全部冻结。目标是在阅读目录中恢复“更新时间 + 章节字数”显示。'
)
BETA.write_text(json.dumps(arr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
source_sha = hashlib.sha256(BETA.read_bytes()).hexdigest()

summary = 'Beta 1.2.4-beta1：目录章节字数兼容 W 字段，恢复“更新时间 + 字数”显示。'
tags = ['起点','测试版','目录','章节字数','兼容修复','Stable1.2.2基线']
changes = [
    '从已真机确认 Stable 1.2.2 重建 Beta，避免继承未确认的 1.2.3 评论 UI 实验改动',
    '目录章节字数字段新增 W 别名，兼容妙想天开当前目录结构',
    '保留 cnt/cW/wC/wordCount 等既有别名与目录多级 fallback',
    '不新增网络请求，不替换目录接口，只修正字段归一化与显示数据来源',
    '正文、评论、搜索、账号及其它 Provider 全部冻结'
]

def patch_entry(e, include_type=False):
    e = dict(e or {})
    e.update({
        'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta',
        'version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,
        'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,
        'sha256':source_sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json'
    })
    if include_type: e['type'] = 'novel'
    return e

mp = ROOT/'manifest.json'
m = json.loads(mp.read_text(encoding='utf-8')); m['updatedAt'] = TS
for i,e in enumerate(m.get('sources', [])):
    if isinstance(e, dict) and e.get('id') == 'qidian-next-beta':
        ne = dict(e); ne.update(patch_entry(e)); ne['category']='novel'; ne['artifactType']='bookSource'; ne['bookSourceUrl']=IDENTITY
        m['sources'][i] = ne; break
else: raise AssertionError('manifest beta entry missing')
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
ba = json.loads(bund.read_text(encoding='utf-8')); src = arr[0] if isinstance(arr,list) else arr
for i,o in enumerate(ba):
    if isinstance(o, dict) and o.get('bookSourceUrl') == IDENTITY: ba[i] = src; break
else: ba.insert(0, src)
bund.write_text(json.dumps(ba, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

dp = ROOT/'rss/data/details/beta/qidian-next.json'
detail = {
    'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,
    'badges':['Beta',VERSION,'目录','章节字数'],
    'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,
    'sections':[
        {'title':'本轮目标','text':'让目录在更新时间旁恢复显示章节字数，例如 2020-12-13 17:01  3326字。'},
        {'title':'实现方式','text':'仅给现有目录归一化增加 W 字段别名；不新增请求，也不替换 APP/Web 多级目录 fallback。'},
        {'title':'基线','text':'从用户已真机确认的 Stable 1.2.2 重建，未继承 1.2.3 系列未确认评论 UI 调整。'},
        {'title':'隔离范围','text':'正文、评论、搜索、账号、情无/小雨、本章说、角色卡及其它 Provider 全部冻结。'}
    ]
}
dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

release = (
    '## 2026-09-13 · qidian-next 1.2.4-beta1 — 目录章节字数 W 字段兼容\n'
    '- 从用户已真机确认的 Stable 1.2.2 重建 Beta，不继承 1.2.3 系列未确认的评论 UI 实验改动。\n'
    '- 对照当前上传的 `妙想天开` 目录结构，确认章节字数可直接使用 `W` 字段；现有 qidian-next 已有“时间 + 字数”格式化，但字段别名缺少 `W`。\n'
    '- 在目录 Schema 与直接章节解析两处补充 `W` 别名，保留 `cnt/cW/wC/wordCount` 等既有兼容字段。\n'
    '- 不新增网络请求，不替换 APP v3 / getsimple / pager / Web fallback、多层缓存和完整度诊断。\n'
    '- 正文、评论、搜索、账号、情无/小雨、`ruleContent`、Rhino loader、本章说及其它 Provider 全部冻结；Stable 1.2.2 不变。\n\n'
)
for p in [ROOT/'docs/RELEASE_LOG.md', ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md']:
    old = p.read_text(encoding='utf-8')
    if not old.startswith('## 2026-09-13 · qidian-next 1.2.4-beta1'):
        p.write_text(release + old, encoding='utf-8')

# Gates
assert hashlib.sha256(STABLE.read_bytes()).hexdigest() == STABLE_EXPECTED, 'Stable changed'
check = json.loads(BETA.read_text(encoding='utf-8')); bs = check[0] if isinstance(check,list) else check
assert bs['bookSourceUrl'] == IDENTITY and '1.2.4-beta1' in bs['bookSourceComment']
assert new_schema in bs['jsLib'] and new_direct in bs['jsLib']
for p in [mp,bp,np,bund,dp]: json.loads(p.read_text(encoding='utf-8'))
assert any(e.get('id')=='qidian-next-beta' and e.get('version')==VERSION for e in json.loads(bp.read_text(encoding='utf-8'))['items'])
assert any(e.get('id')=='qidian-next-beta' and e.get('version')==VERSION for e in json.loads(np.read_text(encoding='utf-8'))['items'])
print('PASS', VERSION, source_sha, 'stable', stable_hash)
