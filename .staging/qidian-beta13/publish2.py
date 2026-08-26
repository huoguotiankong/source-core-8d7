import json
import pathlib
import hashlib
import datetime

root = pathlib.Path('.')
source_path = root / 'sources/novel/qidian-next/qidian-next-beta.json'
stable_path = root / 'sources/novel/qidian-next/qidian-next.json'
stable_before = hashlib.sha256(stable_path.read_bytes()).hexdigest()

def between_replace(text, start_marker, end_marker, replacement, label):
    a = text.find(start_marker)
    assert a >= 0, f'{label}: start marker not found'
    b = text.find(end_marker, a + len(start_marker))
    assert b >= 0, f'{label}: end marker not found'
    return text[:a] + replacement + '\n' + text[b:]

def replace_once(text, old, new, label):
    n = text.count(old)
    assert n == 1, f'{label}: expected 1, got {n}'
    return text.replace(old, new, 1)

doc = json.loads(source_path.read_text(encoding='utf-8'))
assert isinstance(doc, list) and len(doc) == 1
src = doc[0]
assert src.get('bookSourceName') == '🌈 起点增强 · Beta'
rule = src.get('ruleBookInfo')
assert isinstance(rule, dict) and isinstance(rule.get('intro'), str)
s = rule['intro']

# 1) 最近更新时间：保留旧书真实更新时间，不再用“连载超过 60 天”误杀。
time_fn = """function qfTimeSuspiciousV1111(){
  var raw=String(info.updateTime||'').trim();if(/^(?:刚刚|昨天|前天|\\d+\\s*(?:秒|分钟|小时|天)前)$/.test(raw))return false;
  var u=qfTimeMsV1111(raw),now=Date.now();
  if(!u)return true;if(u>now+2*86400000)return true;return false;
}"""
s = between_replace(
    s,
    'function qfTimeSuspiciousV1111(){',
    'function qfPublishSuspiciousV1111(){',
    time_fn,
    'time suspicious function'
)

old_guard = "if(qfTimesV1111.updateTime)info.updateTime=qfTimesV1111.updateTime;else if(qfTimeSuspiciousV1111())info.updateTime='';"
if old_guard in s:
    s = replace_once(s, old_guard, "if(qfTimesV1111.updateTime)info.updateTime=qfTimesV1111.updateTime;", 'initial update guard')

# 继续复用当前 bookId 官方搜索做最近更新补充，但不因老书本身年代久远而清空。
old_need = "var needIntro=blank(info.intro),needRead=blank(info.readingCount),needRec=blank(info.recommendCount),needUpdate=qfTimeSuspiciousV1111();if(!needIntro&&!needRead&&!needRec&&!needUpdate)return;"
new_need = "var needIntro=blank(info.intro),needRead=blank(info.readingCount),needRec=blank(info.recommendCount),needUpdate=qfTimeSuspiciousV1111();if(!needIntro&&!needRead&&!needRec&&!needUpdate)return;"
assert old_need in s, 'official-search needUpdate guard not found'
# 语句本体不改，仅确认仍由新的可信判断函数驱动。

assert 'qf_updateTime_v1112' in s, 'v1112 update cache key missing'
s = s.replace('qf_updateTime_v1112', 'qf_updateTime_v1113')
s = s.replace('qf_qidian_search_detail_v1112_', 'qf_qidian_search_detail_v1113_')
s = s.replace('qidian-search-v1112', 'qidian-search-v1113')

# 2) 作品数据：每两个指标一行，用真正 <br>，不依赖 pre / monospace / CSS 列宽。
rows_fn = """function dataRows(items){
  var a=[];for(var i=0;i<items.length;i++)if(items[i][2])a.push(items[i]);
  var h='';
  for(var j=0;j<a.length;j+=2){
    h+='<br>'+qfMetricHtmlV1112(a[j][1],a[j][2]);
    if(a[j+1])h+='　　　　'+qfMetricHtmlV1112(a[j+1][1],a[j+1][2]);
  }
  return h;
}"""
s = between_replace(
    s,
    'function dataRows(items){',
    'function chips(v,limit,color){',
    rows_fn,
    'dataRows function'
)
assert '<pre style=' not in s, 'pre layout remains'

# 主指标固定成对：总推荐/月票、收藏/粉丝、盟主/首订；其它可用指标继续补位。
data_start = s.find('var data=[')
assert data_start >= 0, 'data array start missing'
data_end_marker = 'var dr=dataRows(data);'
data_end = s.find(data_end_marker, data_start)
assert data_end >= 0, 'data array end missing'
new_data = """var data=[
 ['','总推荐',rec],['','月票',mt],['','收藏',col],['','粉丝',fans],['','盟主',leader],['','首订',first],
 ['',clean(x.readingMetricLabel)||'在看',watch],['','评分',sc?(sc+(clean(x.ratingCount)?' / '+num(x.ratingCount)+'人':'')):'' ],['','投资',invest]
];
"""
s = s[:data_start] + new_data + s[data_end:]

# 3) 作品资料只显示“最近更新”，完全移除首发时间展示。
time_row_start = s.find("if(clean(x.updateTime))body+=row(")
assert time_row_start >= 0, 'visible update row missing'
metric_decl = s.find('var sc=score(', time_row_start)
assert metric_decl >= 0, 'metric declaration missing after visible time rows'
s = s[:time_row_start] + "if(clean(x.updateTime))body+=row('🕒','最近更新',date(x.updateTime));\n\n" + s[metric_decl:]

# 4) Beta12 的 qfMultiContentV423 在 loginUrl 作用域；详情 onclick 回退到 jsLib 已验证的全局 ABI。
old_btn = '<button>⚡ 正文设置@onclick:qfMultiContentV423.call(this)</button>'
new_btn = '<button>⚡ 正文源状态@onclick:qfBookInfoOpenSmartSourceV330.call(this)</button>'
s = replace_once(s, old_btn, new_btn, 'content settings button')

rule['intro'] = s
src['ruleBookInfo'] = rule
src['bookSourceComment'] = 'v1.1.0-beta13：详情页只保留最近更新时间并恢复作品数据双列。移除首发时间展示；更新时间取消“连载超过60天”误判，仅过滤空值和明显未来时间，缓存升级 v1113。作品数据按两项一行真实换行，主指标优先总推荐/月票、收藏/粉丝、盟主/首订，其余指标继续补位。Beta12 跨作用域正文设置按钮回退为已验证的正文源状态入口。搜索、目录、正文 Provider、评论、角色卡、书友圈、账号链冻结。'
src['lastUpdateTime'] = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
source_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()

# 5) Beta Bundle：仅替换起点增强 Beta。
bundle_path = root / 'bundles/all-beta.json'
bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
assert isinstance(bundle, list)
hits = [i for i, x in enumerate(bundle) if isinstance(x, dict) and x.get('bookSourceName') == '🌈 起点增强 · Beta']
assert len(hits) == 1, ('bundle hits', hits)
bundle[hits[0]] = src
bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

now_cn = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
now_iso = now_cn.isoformat(timespec='seconds')
day = now_cn.strftime('%Y-%m-%d')
summary = '详情 beta13：只保留最近更新时间；作品数据按两项一行恢复双列；修复 Beta12 正文设置入口作用域回归。'
tags = ['起点', '测试版', '详情页', '最近更新', '富数据', '双列', '正文源状态', '缓存']
changes = [
    '作品资料只显示“最近更新”，彻底移除“首发”展示',
    '取消“连载超过60天即判异常”的更新时间阈值，旧书真实最近更新时间不再被误清空',
    '更新时间缓存与官方搜索详情缓存升级到 v1113，避免 Beta12 错误缓存继续命中',
    '作品数据不再使用 pre/monospace/CSS 列宽，改为每两个指标使用真实 HTML 换行；主指标优先总推荐/月票、收藏/粉丝、盟主/首订',
    'Beta12 会报 qfMultiContentV423 未定义的正文设置入口回退为已验证的正文源状态全局入口',
    '搜索、目录、正文 Provider 实际取正文逻辑、评论、角色卡、书友圈、账号链冻结',
]
raw = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v=11013'
cdn = 'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v=11013'
imp = 'legado://import/importonline?src=' + raw

# Subscription
sub_path = root / 'subscription/beta.json'
sub = json.loads(sub_path.read_text(encoding='utf-8'))
item = next(x for x in sub['items'] if x.get('id') == 'qidian-next-beta')
item.update({
    'summary': summary,
    'version': '1.1.0-beta13',
    'updatedAt': day,
    'tags': tags,
    'changelog': changes,
    'sourceUrl': raw,
    'backupUrl': cdn,
    'importUrl': imp,
})
sub['updatedAt'] = now_iso
sub_path.write_text(json.dumps(sub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Manifest
man_path = root / 'manifest.json'
man = json.loads(man_path.read_text(encoding='utf-8'))
mi = next(x for x in man['sources'] if x.get('id') == 'qidian-next-beta')
mi.update({
    'version': '1.1.0-beta13',
    'versionCode': 11013,
    'updatedAt': now_iso,
    'sourceUrl': raw,
    'summary': summary,
    'tags': tags,
    'changelog': changes,
    'sha256': source_sha,
})
man['updatedAt'] = now_iso
man_path.write_text(json.dumps(man, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# RSS detail
detail_path = root / 'rss/data/details/beta/qidian-next.json'
detail = {
    'kind': 'source',
    'title': '🌈 起点增强 · Beta',
    'summary': summary,
    'badges': ['Beta', '1.1.0-beta13', '最近更新 / 双列 / 正文源'],
    'sections': [
        {'title': '最近更新时间', 'text': '详情页只保留“最近更新”，完全移除首发。取消 60 天陈旧阈值，仅过滤空值和明显未来时间；刷新 v1113 时间缓存。'},
        {'title': '作品数据', 'text': '每两个指标一行真实换行：总推荐 / 月票、收藏 / 粉丝、盟主 / 首订优先成对，其余可用指标继续两项一行补位。'},
        {'title': '正文源入口', 'text': 'Beta12 跨作用域正文设置按钮会报 qfMultiContentV423 未定义，本版回退到已验证的“正文源状态”全局入口。'},
        {'title': '冻结范围', 'text': '搜索、目录、正文 Provider 实际解析、评论、角色卡、书友圈、账号和情无 VIP 链不改。'},
    ],
    'sourceUrl': raw,
    'backupUrl': cdn,
    'importUrl': imp,
}
detail_path.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Release log
log_path = root / 'docs/RELEASE_LOG.md'
log = log_path.read_text(encoding='utf-8')
entry = f"""## {day} — Qidian Next 1.1.0-beta13 latest-update + two-column recovery

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 详情页作品资料只保留“最近更新”，彻底移除首发时间展示。
- 删除连载书超过 60 天即清空更新时间的错误阈值；只保留空值与明显未来时间保护。
- 时间缓存与起点官方搜索详情缓存升级到 v1113，避免 Beta12 错误时间缓存继续命中。
- 作品数据不再使用 pre/monospace/CSS 列宽；改成每两个指标使用真实 HTML 换行，主指标优先总推荐/月票、收藏/粉丝、盟主/首订。
- Beta12 跨作用域正文设置回调回退为已验证的正文源状态全局入口，消除 qfMultiContentV423 未定义报错。
- 搜索、目录、正文 Provider、评论、角色卡、书友圈和账号链冻结。
- Published SHA256: `{source_sha}`.


"""
log_path.write_text(entry + log, encoding='utf-8')

# Static validation
parsed = json.loads(source_path.read_text(encoding='utf-8'))[0]
rr = parsed['ruleBookInfo']['intro']
assert "'🕒','最近更新'" in rr
assert "'🚀','首发'" not in rr
assert '<pre style=' not in rr
assert "h+='<br>'+qfMetricHtmlV1112" in rr
assert 'qfMultiContentV423.call(this)' not in rr
assert 'qfBookInfoOpenSmartSourceV330.call(this)' in rr
assert 'now-u>60*86400000' not in rr
assert 'qf_updateTime_v1113' in rr
assert json.loads(sub_path.read_text(encoding='utf-8'))['items']
assert json.loads(man_path.read_text(encoding='utf-8'))
assert json.loads(bundle_path.read_text(encoding='utf-8'))
assert hashlib.sha256(stable_path.read_bytes()).hexdigest() == stable_before, 'stable source changed'

print('SOURCE_SHA256', source_sha)
print('VERSION', '1.1.0-beta13')
print('VALIDATION', 'OK')
