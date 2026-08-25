import json, pathlib, hashlib
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
SP = ROOT / 'sources/novel/qidian-next/qidian-next.json'
data = json.loads(SP.read_text(encoding='utf-8'))
assert isinstance(data, list) and len(data) == 1
src = data[0]
assert src.get('bookSourceUrl') == 'https://m.qidian.com/?qf_source=qidian_next_8d7'
assert 'v0.1.5-beta6' in src.get('bookSourceComment','')

now_dt = datetime.now(timezone(timedelta(hours=8)))
now = now_dt.isoformat(timespec='seconds')
day = now_dt.date().isoformat()

# Stable display identity. Runtime identity stays unchanged for in-place Legado upgrade.
src['bookSourceName'] = '🌈 起点增强'
src['bookSourceGroup'] = '﹅♚1、正式源'
src['bookSourceComment'] = ('v1.0.0 Stable：第一版正式版。基于 v0.1.5-beta6，保留官方搜索/详情/目录/评论体系与多正文 Provider；'
                            '采用静态双列一级设置页 + startBrowserAwait 多级二级设置架构；正文设置、账号管理、诊断工具已完成第一阶段卡片化重构。'
                            '本次晋升按用户明确要求执行，不改变搜索/详情/目录/正文/评论业务逻辑。')
src['lastUpdateTime'] = int(now_dt.timestamp() * 1000)

# Update the visible first-level header while keeping static loginUi architecture.
try:
    ui = json.loads(src.get('loginUi') or '[]')
    if isinstance(ui, list) and ui:
        ui[0]['name'] = '🌈 起点增强 · v1.0.0'
        src['loginUi'] = json.dumps(ui, ensure_ascii=False, separators=(',', ':'))
except Exception:
    pass

raw = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
SP.write_bytes(raw)
sha = hashlib.sha256(raw).hexdigest()

# Stable bundle owns the current stable copy.
stable_bundle_path = ROOT / 'bundles/all-stable.json'
stable_bundle = json.loads(stable_bundle_path.read_text(encoding='utf-8'))
if not isinstance(stable_bundle, list): stable_bundle = []
new_stable=[]; replaced=False
for item in stable_bundle:
    if item.get('bookSourceUrl') == src['bookSourceUrl']:
        if not replaced:
            new_stable.append(src); replaced=True
    else:
        new_stable.append(item)
if not replaced: new_stable.append(src)
stable_bundle_path.write_text(json.dumps(new_stable, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

# Remove this line from Beta bundle until a future independent beta file is created.
beta_bundle_path = ROOT / 'bundles/all-beta.json'
beta_bundle = json.loads(beta_bundle_path.read_text(encoding='utf-8'))
beta_bundle = [x for x in beta_bundle if x.get('bookSourceUrl') != src['bookSourceUrl']]
beta_bundle_path.write_text(json.dumps(beta_bundle, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

summary = '起点增强型完整书源：官方搜索/详情/目录/评论体系 + 多正文 Provider；设置采用静态双列首页与卡片化多级页面。'
tags = ['起点','正式版','官方目录','段评','本章说','作者说','多正文 Provider','STV','多级设置']
changes = [
    '第一版正式版，基于已使用的 v0.1.5-beta6 主线晋升',
    '正式名称改为「🌈 起点增强」，与「起点助手」明确区分',
    '保留静态双列一级设置页与卡片化多级二级设置架构',
    '搜索/详情/目录/正文/评论业务逻辑不因正式版晋升而改变'
]

stable_sub_path = ROOT / 'subscription/stable.json'
stable_sub = json.loads(stable_sub_path.read_text(encoding='utf-8'))
stable_sub['updatedAt'] = now
items=[x for x in stable_sub.get('items',[]) if x.get('id')!='qidian-next']
items.append({
    'id':'qidian-next','name':'🌈 起点增强','summary':summary,'icon':'','channel':'stable','version':'1.0.0','updatedAt':day,
    'tags':tags,'changelog':changes,
    'sourceUrl':'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next.json',
    'backupUrl':'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next.json',
    'importUrl':'legado://import/importonline?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next.json',
    'detailUrl':'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/qidian-next.json'
})
stable_sub['items']=items
stable_sub_path.write_text(json.dumps(stable_sub, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

beta_sub_path = ROOT / 'subscription/beta.json'
beta_sub = json.loads(beta_sub_path.read_text(encoding='utf-8'))
beta_sub['updatedAt'] = now
beta_sub['items'] = [x for x in beta_sub.get('items',[]) if x.get('id')!='qidian-next']
beta_sub_path.write_text(json.dumps(beta_sub, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

manifest_path = ROOT / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['updatedAt'] = now
for item in manifest.get('sources',[]):
    if item.get('id') == 'qidian-next':
        item.update({
            'name':'🌈 起点增强','channel':'stable','version':'1.0.0','versionCode':10000,'updatedAt':now,
            'sourcePath':'sources/novel/qidian-next/qidian-next.json',
            'sourceUrl':'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next.json',
            'summary':summary,'tags':tags,'changelog':changes,'sha256':sha
        })
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

# Source detail stays compact. Release history belongs in RELEASE_LOG, not this page.
detail_path = ROOT / 'rss/data/details/qidian-next.json'
detail = {
    'kind':'source',
    'title':'🌈 起点增强',
    'summary':summary,
    'badges':['Stable','1.0.0','小说','增强版'],
    'sections':[
        {'title':'定位','text':'独立于旧「起点官方生态」和「起点助手」的增强型起点书源，长期维护官方数据与多正文 Provider 的组合能力。'},
        {'title':'核心能力','text':'官方搜索、书籍详情、目录、段评、本章说、作者说等数据链保持起点体系；正文支持多 Provider、STV 与既有切源策略。'},
        {'title':'设置架构','text':'一级页使用静态双列宫格；二级设置使用卡片化 startBrowserAwait 页面。当前正文设置、账号管理、诊断工具已完成第一阶段重构。'},
        {'title':'当前版本','text':'1.0.0 Stable。由 v0.1.5-beta6 按用户明确要求晋升；本次主要完成正式命名、正式通道发布和仓库结构整理。'},
        {'title':'发布说明','text':'这里以后只展示当前版本与长期能力，不逐版累加历史介绍。完整版本历史统一记录在仓库 Release Log。'},
        {'title':'唯一身份','text':'https://m.qidian.com/?qf_source=qidian_next_8d7'}
    ],
    'sourceUrl':'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next.json',
    'backupUrl':'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next.json'
}
detail_path.write_text(json.dumps(detail, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

# Handoff: freeze current path as Stable; future betas use a separate file path.
handoff_path = ROOT / 'docs/sources/qidian-next/PROJECT_HANDOFF.md'
h = handoff_path.read_text(encoding='utf-8')
h = h.replace('- Display name: `🌈 起点助手·新架构`','- Display name: `🌈 起点增强`')
h = h.replace('- Channel: Beta/Test','- Channel: Stable')
h = h.replace('- Current version: `0.1.5-beta6`','- Current version: `1.0.0`')
import re
h = re.sub(r'- SHA256: `[0-9a-f]+`', '- SHA256: `'+sha+'`', h, count=1)
section = '''\n## Stable 1.0.0 promotion\n\nUser explicitly requested promotion of the Beta6 baseline to the first Stable release. Display name changed to `🌈 起点增强`; permanent `bookSourceUrl` remains unchanged so Legado upgrades in place.\n\nDistribution rule after Stable 1.0.0:\n\n- `sources/novel/qidian-next/qidian-next.json` is the Stable file and must not be overwritten by an unconfirmed Beta.\n- Future test versions must use `sources/novel/qidian-next/qidian-next-beta.json` (or another explicitly beta-only path) while preserving the same `bookSourceUrl`.\n- Stable and Beta subscription entries may therefore point to different files but represent the same Legado source identity.\n- RSS source detail is a current-state introduction, not a per-version history. Replace the current-version section on release; keep historical changes only in `docs/RELEASE_LOG.md`.\n'''
if '## Stable 1.0.0 promotion' not in h:
    h = h.rstrip()+'\n'+section
handoff_path.write_text(h, encoding='utf-8')

# Add repository-wide rule preventing detail-page history accumulation.
rules_path = ROOT / 'docs/DEVELOPMENT_RULES.md'
rules = rules_path.read_text(encoding='utf-8')
rule_section = '''\n## 13. Subscription source-detail maintenance\n\nRSS/source detail pages are current-state introductions, not release-history documents.\n\n- Do not append one new detail section for every Beta/Stable version.\n- Keep long-lived sections such as positioning, core capabilities, setup architecture, current version/status and import identity.\n- On release, replace the current-version/change summary instead of accumulating historical version cards.\n- Full chronological history belongs in `docs/RELEASE_LOG.md`.\n\nThis prevents source detail pages from growing without bound after dozens or hundreds of releases.\n'''
if '## 13. Subscription source-detail maintenance' not in rules:
    rules = rules.rstrip()+'\n'+rule_section
rules_path.write_text(rules, encoding='utf-8')

project_path = ROOT / 'docs/PROJECT_PLAN.md'
project = project_path.read_text(encoding='utf-8')
if 'Qidian Next Stable 1.0.0' not in project:
    project = project.rstrip()+'''\n\n## 12. Qidian Next Stable 1.0.0\n\nOn 2026-08-26 the user explicitly promoted the Beta6 baseline to the first Stable release. The public display name is `🌈 起点增强`; repository id and permanent Legado identity remain `qidian-next` / `https://m.qidian.com/?qf_source=qidian_next_8d7`. Future unconfirmed test versions must use a separate beta file path so the Stable raw URL never silently serves Beta code.\n'''
project_path.write_text(project, encoding='utf-8')

release_path = ROOT / 'docs/RELEASE_LOG.md'
r = release_path.read_text(encoding='utf-8')
block = f'''## {day} — 起点增强 v1.0.0 Stable\n\nStatus: Stable; promoted by explicit user request from the v0.1.5-beta6 baseline.\n\nChanges:\n\n- Renamed the source from `🌈 起点助手·新架构` to `🌈 起点增强` to distinguish it from 起点助手.\n- Promoted the current Beta6 baseline to Stable 1.0.0 without changing reading business logic.\n- Moved the source from Beta catalog/bundle to Stable catalog/bundle.\n- Kept permanent Legado identity `https://m.qidian.com/?qf_source=qidian_next_8d7` for in-place updates.\n- Simplified RSS source detail to current-state information; per-version history is no longer accumulated there.\n- Reserved the Stable raw file; future Beta development must use a separate beta file path.\n- SHA256: `{sha}`.\n\n'''
if '起点增强 v1.0.0 Stable' not in r:
    r = r.replace('# RELEASE LOG\n', '# RELEASE LOG\n\n'+block, 1)
release_path.write_text(r, encoding='utf-8')

print('stable promotion prepared', sha, len(raw))
