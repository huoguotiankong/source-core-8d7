import json
import pathlib
import hashlib
import datetime
import copy

root = pathlib.Path('.')
beta_path = root / 'sources/novel/qidian-next/qidian-next-beta.json'
stable_path = root / 'sources/novel/qidian-next/qidian-next.json'
manifest_path = root / 'manifest.json'
sub_path = root / 'subscription/stable.json'
bundle_path = root / 'bundles/all-stable.json'
rss_path = root / 'rss/data/details/stable/qidian-next.json'
log_path = root / 'docs/RELEASE_LOG.md'

beta_bytes_before = beta_path.read_bytes()
beta_sha_before = hashlib.sha256(beta_bytes_before).hexdigest()

beta_doc = json.loads(beta_bytes_before.decode('utf-8'))
stable_old_doc = json.loads(stable_path.read_text(encoding='utf-8'))
assert isinstance(beta_doc, list) and len(beta_doc) == 1
assert isinstance(stable_old_doc, list) and len(stable_old_doc) == 1
beta = beta_doc[0]
stable_old = stable_old_doc[0]
assert beta.get('bookSourceName') == '🌈 起点增强 · Beta'
assert beta.get('bookSourceUrl') == stable_old.get('bookSourceUrl') == 'https://m.qidian.com/?qf_source=qidian_next_8d7'
assert 'v1.1.0-beta14' in str(beta.get('bookSourceComment',''))

now_cn = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
now_iso = now_cn.isoformat(timespec='seconds')
day = now_cn.strftime('%Y-%m-%d')
now_ms = int(now_cn.timestamp() * 1000)

# Promote the exact Beta14 business baseline. Only release/display metadata is changed.
stable = copy.deepcopy(beta)
stable['bookSourceName'] = '🌈 起点增强'
stable['bookSourceGroup'] = stable_old.get('bookSourceGroup', stable.get('bookSourceGroup',''))
stable['bookSourceUrl'] = stable_old['bookSourceUrl']
stable['bookSourceComment'] = (
    'v1.1.0 Stable：由 1.1.0-beta14 真机确认基线原样晋升。保留详情富数据、'
    '最近更新时间、作品数据固定双列、紧凑快捷入口与正文设置直达；搜索、目录、'
    '正文 Provider、评论、角色卡、书友圈、账号链不新增业务逻辑。'
)
stable['lastUpdateTime'] = now_ms
# Static settings header is release metadata, not business logic.
if isinstance(stable.get('loginUi'), str):
    stable['loginUi'] = stable['loginUi'].replace('🌈 起点增强 · v1.0.1-beta1', '🌈 起点增强 · v1.1.0')
    stable['loginUi'] = stable['loginUi'].replace('🌈 起点增强 · v1.1.0-beta14', '🌈 起点增强 · v1.1.0')

stable_doc = [stable]
stable_path.write_text(json.dumps(stable_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
stable_sha = hashlib.sha256(stable_path.read_bytes()).hexdigest()

# Stable bundle: replace only qidian-next, keep every unrelated source.
bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
assert isinstance(bundle, list)
hits = [i for i,x in enumerate(bundle) if isinstance(x,dict) and x.get('bookSourceUrl') == stable['bookSourceUrl']]
assert len(hits) == 1, ('stable bundle qidian-next hits', hits)
bundle[hits[0]] = stable
bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

summary = '正式版 1.1.0：由 Beta14 真机确认基线晋升；详情富数据、最近更新时间、固定双列与正文设置直达均保留。'
tags = ['起点','正式版','详情富数据','最近更新','固定双列','正文设置','多正文 Provider','评论']
changes = [
    '由 1.1.0-beta14 真机确认基线原样晋升 Stable，不新增业务逻辑',
    '详情页保留完整富数据与内容简介，只显示最近更新时间，不显示首发时间',
    '作品数据固定分栏：月票/收藏/粉丝在左列，其余可用指标在右列',
    '快捷入口保持紧凑三按钮，正文设置可从详情页直接打开',
    '搜索、目录、正文 Provider、评论、角色卡、书友圈、账号链保持 Beta14 基线',
]
raw = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next.json?v=11000'
cdn = 'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next.json?v=11000'
imp = 'legado://import/importonline?src=' + raw

# Stable subscription.
sub = json.loads(sub_path.read_text(encoding='utf-8'))
item = next(x for x in sub['items'] if x.get('id') == 'qidian-next')
item.update({
    'name':'🌈 起点增强','summary':summary,'channel':'stable','version':'1.1.0',
    'updatedAt':day,'tags':tags,'changelog':changes,'sourceUrl':raw,'backupUrl':cdn,'importUrl':imp,
    'detailUrl':'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/stable/qidian-next.json'
})
sub['updatedAt'] = now_iso
sub['generatedAt'] = now_iso
sub_path.write_text(json.dumps(sub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Manifest stable entry only; Beta entry remains Beta14.
man = json.loads(manifest_path.read_text(encoding='utf-8'))
mi = next(x for x in man['sources'] if x.get('id') == 'qidian-next')
mi.update({
    'name':'🌈 起点增强','category':'novel','channel':'stable','version':'1.1.0','versionCode':11000,
    'updatedAt':now_iso,'sourcePath':'sources/novel/qidian-next/qidian-next.json','sourceUrl':raw,
    'bookSourceUrl':stable['bookSourceUrl'],'summary':summary,'tags':tags,'changelog':changes,'sha256':stable_sha
})
man['updatedAt'] = now_iso
manifest_path.write_text(json.dumps(man, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Stable RSS detail current-state card.
rss = {
  'kind':'source','title':'🌈 起点增强','summary':summary,
  'badges':['Stable','1.1.0','Beta14 真机确认'],
  'sections':[
    {'title':'详情页','text':'保留作品富数据、标签/荣誉与内容简介；作品资料只显示最近更新时间。'},
    {'title':'作品数据','text':'固定双列：月票、收藏、粉丝在左列；总推荐、盟主、首订、在看、评分、投资等可用指标在右列。'},
    {'title':'快捷入口','text':'书友圈、角色卡、正文设置保持紧凑布局；正文设置可从详情直接打开。'},
    {'title':'稳定基线','text':'本正式版由 1.1.0-beta14 原样晋升；搜索、目录、正文 Provider、评论、角色卡、书友圈和账号链没有新增改动。'}
  ],
  'sourceUrl':raw,'backupUrl':cdn,'importUrl':imp
}
rss_path.write_text(json.dumps(rss, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Release log.
log = log_path.read_text(encoding='utf-8')
entry = f'''## {day} — Qidian Next 1.1.0 Stable\n\nStatus: Stable; user explicitly requested promotion after Beta14 real-device confirmation.\n\nChanges:\n\n- Promoted the exact `1.1.0-beta14` functional baseline to Stable; no new business behavior added.\n- Retained rich detail metadata and synopsis, with only the latest-update time shown.\n- Retained fixed two-column metrics: month-ticket / collection / fans on the left, remaining available metrics on the right.\n- Retained compact shortcuts and direct detail-page content settings entry.\n- Search, catalog, content Providers, reviews, role card, book circle and account domains remain on the Beta14 baseline.\n- Published Stable SHA256: `{stable_sha}`.\n\n\n'''
log_path.write_text(entry + log, encoding='utf-8')

# Static release gates.
parsed_stable = json.loads(stable_path.read_text(encoding='utf-8'))[0]
parsed_beta = json.loads(beta_path.read_text(encoding='utf-8'))[0]
assert parsed_stable['bookSourceName'] == '🌈 起点增强'
assert parsed_stable['bookSourceUrl'] == parsed_beta['bookSourceUrl']
assert 'v1.1.0 Stable' in parsed_stable['bookSourceComment']
assert 'qfBookInfoOpenContentSettingsV1114.call(this)' in json.dumps(parsed_stable.get('ruleBookInfo',{}), ensure_ascii=False)
assert "['','月票',mt],['','收藏',col],['','粉丝',fans]" in json.dumps(parsed_stable.get('ruleBookInfo',{}), ensure_ascii=False)
assert hashlib.sha256(beta_path.read_bytes()).hexdigest() == beta_sha_before, 'Beta14 source changed during Stable promotion'
check_sub = json.loads(sub_path.read_text(encoding='utf-8'))
assert next(x for x in check_sub['items'] if x.get('id')=='qidian-next')['version'] == '1.1.0'
check_man = json.loads(manifest_path.read_text(encoding='utf-8'))
assert next(x for x in check_man['sources'] if x.get('id')=='qidian-next')['versionCode'] == 11000
assert next(x for x in check_man['sources'] if x.get('id')=='qidian-next-beta')['version'] == '1.1.0-beta14'
assert json.loads(bundle_path.read_text(encoding='utf-8'))
assert json.loads(rss_path.read_text(encoding='utf-8'))['badges'][0] == 'Stable'

print('STABLE_VERSION 1.1.0')
print('STABLE_SHA256', stable_sha)
print('BETA14_SHA256_UNCHANGED', beta_sha_before)
print('VALIDATION OK')
