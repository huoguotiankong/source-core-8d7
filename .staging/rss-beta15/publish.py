import json
import pathlib
from datetime import datetime, timezone, timedelta

root = pathlib.Path('.')
cn = timezone(timedelta(hours=8))
now = datetime.now(cn)
now_iso = now.isoformat(timespec='seconds')
day = now.strftime('%Y-%m-%d')

# RSS source: enable Legado's native stale-article cleanup without a real next page.
rss_path = root / 'rss/reader-source-repository-beta.json'
rss_doc = json.loads(rss_path.read_text(encoding='utf-8'))
assert isinstance(rss_doc, list) and len(rss_doc) == 1
src = rss_doc[0]
src['sourceName'] = '🌈 阅读书源仓库'
src['sourceComment'] = '唯一当前仓库订阅入口。UI Beta15：按阅读原生 RSS 数据库机制清理历史文章；分类和详情 URL 从此保持固定，不再通过改 URL 规避缓存。'
src['ruleNextPage'] = "@js:''"
src['sortUrl'] = src['sortUrl'].replace('?reset=1', '')
src['ruleContent'] = src['ruleContent'].replace('UI Beta 14', 'UI Beta 15')
src['lastUpdateTime'] = int(now.timestamp() * 1000)
rss_path.write_text(json.dumps(rss_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Unique repository catalog entry.
sub_path = root / 'subscription/rss.json'
sub = json.loads(sub_path.read_text(encoding='utf-8'))
assert len(sub.get('items', [])) == 1
item = sub['items'][0]
item['version'] = '0.4.1-beta15'
item['summary'] = '唯一当前仓库订阅入口；Beta15 启用阅读原生旧文章清理机制，刷新分类时删除历史残留。'
item['updatedAt'] = day
item['tags'] = ['订阅源', '仓库', '唯一入口', '旧文章清理']
sub['updatedAt'] = now_iso
sub_path.write_text(json.dumps(sub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Current repository detail.
detail_path = root / 'rss/data/details/rss/repository-current.json'
detail = {
  'kind': 'rss',
  'title': '🌈 阅读书源仓库',
  'summary': '当前唯一仓库订阅入口。Beta15 使用阅读自身的 RSS 数据库清理逻辑替换旧文章，而不是继续修改分类 URL。',
  'badges': ['订阅源', '唯一入口', 'UI Beta15'],
  'sections': [
    {'title': '当前策略', 'text': '仓库订阅只保留一个活动入口；书源本身仍按 Stable / Beta 分通道。'},
    {'title': '历史文章清理', 'text': '阅读只有在 ruleNextPage 非空时才会在刷新后执行 clearOld。Beta15 提供一个非空但返回空值的下一页规则，因此没有真实第二页，同时会删除当前分类中旧版本残留文章。'},
    {'title': '固定身份', 'text': '首页、漫画、仓库订阅、正式版、测试版、批量和帮助分类 URL 从本版起固定；不再添加 ?reset 或 UI 版本参数。'}
  ],
  'rssUrl': 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/reader-source-repository-beta.json'
}
detail_path.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Picacg Stable RSS detail: migrate old manifest-shaped payload to the current UI schema.
pica_detail_path = root / 'rss/data/details/stable/picacg.json'
pica_detail = {
  'kind': 'source',
  'title': '◈ 哔咔漫画',
  'summary': '哔咔漫画 1.0.0 正式版。APP/API + 网页双线路，支持登录、账号、评论/楼中楼、点赞收藏、标签、目录和漫画图片正文。',
  'badges': ['Stable', '1.0.0', '漫画', '双线路'],
  'sections': [
    {'title': '互动与账户', 'text': '支持登录、账户中心、签到、点赞、收藏、评论、楼中楼、回复与评论点赞。详情页顶部定制按钮已真机确认可进入评论中心。'},
    {'title': '浏览与阅读', 'text': '支持发现分类、标签跳转、相关推荐、分页目录和漫画图片正文；相关推荐采用一次性集合与强去重。'},
    {'title': '线路', 'text': '保留 APP/API 与网页双线路；线路和版本信息不再堆进书源名称。'}
  ],
  'sourceUrl': 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg.json?v=10000',
  'backupUrl': 'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg.json?v=10000'
}
pica_detail_path.write_text(json.dumps(pica_detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Manifest timestamp only; book-source release data stays unchanged.
man_path = root / 'manifest.json'
man = json.loads(man_path.read_text(encoding='utf-8'))
man['updatedAt'] = now_iso
man_path.write_text(json.dumps(man, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Long-term rules and diagnosis.
rules_path = root / 'docs/DEVELOPMENT_RULES.md'
rules = rules_path.read_text(encoding='utf-8')
rule_note = '''\n## 19. RSS stale-article cleanup invariant\n\nLegado persists RSS articles and only calls `rssArticleDao.clearOld(origin, sort, order)` after a refresh when the RSS source's `ruleNextPage` field is non-blank.\n\nFor repository-style RSS sources whose remote JSON represents the complete current list:\n\n- keep `ruleNextPage` non-blank even when there is no real pagination; use an empty-result rule such as `@js:''`;\n- this enables Legado to delete older rows after inserting the current result while still producing no second-page URL;\n- do not use category-name churn, `?ui=N`, `?reset=N`, or versioned detail URLs as a routine cache-clearing mechanism;\n- category URLs and article detail URLs remain long-lived identities.\n'''
if '## 19. RSS stale-article cleanup invariant' not in rules:
    rules = rules.rstrip() + '\n' + rule_note
rules_path.write_text(rules.rstrip() + '\n', encoding='utf-8')

known_path = root / 'docs/KNOWN_ISSUES.md'
known = known_path.read_text(encoding='utf-8')
known_note = '''\n## 30. RSS historical cards persisted despite clean remote catalogs — root cause fixed in Beta15\n\nReal-device result after Beta14: Home, Stable and Beta still contained Beta3/Beta10/Beta11-era cards even though the current remote catalogs contained only the latest items.\n\nRoot cause confirmed from Legado source: RSS articles are persisted by `origin + link + sort`; `RssArticlesViewModel` calls `rssArticleDao.clearOld(...)` only when `rssSource.ruleNextPage` is non-blank. The repository RSS source had always used an empty `ruleNextPage`, so refresh inserted/replaced current rows but never deleted older rows.\n\nBeta15 fix: set `ruleNextPage` to the non-blank empty-result rule `@js:''`. It triggers Legado's native `clearOld` branch after current articles are inserted while yielding no actual next-page URL. Beta14 `?reset=1` category parameters are removed and category/detail identities are frozen.\n\nAlso fixed the Picacg Stable RSS detail payload, which still used the old manifest-shaped schema and therefore rendered the fallback repository title instead of `◈ 哔咔漫画`.\n\nStatus: Beta15 published for real-device confirmation.\n'''
if '## 30. RSS historical cards persisted despite clean remote catalogs' not in known:
    known = known.rstrip() + '\n' + known_note
known_path.write_text(known.rstrip() + '\n', encoding='utf-8')

plan_path = root / 'docs/PROJECT_PLAN.md'
plan = plan_path.read_text(encoding='utf-8')
plan_note = '''\n## 14. RSS current-list replacement model\n\nFrom UI Beta15 onward the repository RSS source uses Legado's own stale-row cleanup path: `ruleNextPage` stays non-blank but evaluates to an empty result. Current remote catalogs are therefore authoritative complete lists, and refreshing a category can remove older persisted rows instead of accumulating them. Category/detail URLs remain fixed.\n'''
if '## 14. RSS current-list replacement model' not in plan:
    plan = plan.rstrip() + '\n' + plan_note
plan_path.write_text(plan.rstrip() + '\n', encoding='utf-8')

log_path = root / 'docs/RELEASE_LOG.md'
log = log_path.read_text(encoding='utf-8')
entry = f'''## {day} — RSS UI 0.4.1-beta15 native stale-article cleanup\n\nStatus: Beta/Test; awaiting real-device confirmation.\n\nChanges:\n\n- Root cause confirmed from Legado source: old RSS rows are deleted by `clearOld` only when `ruleNextPage` is non-blank.\n- Repository `ruleNextPage` changed from empty to `@js:''`: no real second page, but refresh now enters Legado's native old-row cleanup branch.\n- Removed Beta14 `?reset=1` category URL churn; category and detail identities are fixed from this version onward.\n- `subscription/rss.json` continues to expose exactly one repository entry.\n- Rebuilt Picacg Stable RSS detail into the current `kind/title/badges/sections` schema so its detail page shows `◈ 哔咔漫画` instead of the repository fallback title.\n- Picacg Stable book-source JSON and all Qidian book-source business logic are unchanged.\n\n\n'''
if 'RSS UI 0.4.1-beta15 native stale-article cleanup' not in log:
    log = entry + log
log_path.write_text(log, encoding='utf-8')

# Static gates.
check = json.loads(rss_path.read_text(encoding='utf-8'))[0]
assert check['ruleNextPage'].strip() == "@js:''"
assert '?reset=' not in check['sortUrl']
assert 'UI Beta 15' in check['ruleContent']
assert len(json.loads(sub_path.read_text(encoding='utf-8'))['items']) == 1
assert json.loads(pica_detail_path.read_text(encoding='utf-8'))['title'] == '◈ 哔咔漫画'
for p in [rss_path, sub_path, detail_path, pica_detail_path, man_path]:
    json.loads(p.read_text(encoding='utf-8'))
print(json.dumps({'rss_ui':'0.4.1-beta15','ruleNextPage':check['ruleNextPage'],'reset_params':False,'rss_entries':1,'picacg_detail_schema':'source','updatedAt':now_iso}, ensure_ascii=False, indent=2))
