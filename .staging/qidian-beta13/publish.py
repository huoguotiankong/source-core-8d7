import json
import pathlib
import re
import hashlib
import datetime

root = pathlib.Path('.')
source_path = root / 'sources/novel/qidian-next/qidian-next-beta.json'
stable_path = root / 'sources/novel/qidian-next/qidian-next.json'
stable_before = hashlib.sha256(stable_path.read_bytes()).hexdigest()

doc = json.loads(source_path.read_text(encoding='utf-8'))
assert isinstance(doc, list) and len(doc) == 1
src = doc[0]
assert src.get('bookSourceName') == '🌈 起点增强 · Beta', src.get('bookSourceName')
rule = src.get('ruleBookInfo')
assert isinstance(rule, dict) and isinstance(rule.get('intro'), str)
s = rule['intro']

# 1. 最近更新时间：取消“连载超过 60 天”误杀，也不再让首发/上架时间反向干扰更新时间。
pat = r"function qfTimeSuspiciousV1111\(\)\{\n.*?\n\}"
new = """function qfTimeSuspiciousV1111(){
  var raw=String(info.updateTime||'').trim();if(/^(?:刚刚|昨天|前天|\\d+\\s*(?:秒|分钟|小时|天)前)$/.test(raw))return false;
  var u=qfTimeMsV1111(raw),now=Date.now();
  if(!u)return true;if(u>now+2*86400000)return true;return false;
}"""
s, n = re.subn(pat, new, s, count=1, flags=re.S)
assert n == 1, 'qfTimeSuspicious replacement failed'

old = "if(qfTimesV1111.updateTime)info.updateTime=qfTimesV1111.updateTime;else if(qfTimeSuspiciousV1111())info.updateTime='';"
assert s.count(old) == 1, ('initial update guard', s.count(old))
s = s.replace(old, "if(qfTimesV1111.updateTime)info.updateTime=qfTimesV1111.updateTime;", 1)

old_need = "var needIntro=blank(info.intro),needRead=blank(info.readingCount),needRec=blank(info.recommendCount),needUpdate=qfTimeSuspiciousV1111();if(!needIntro&&!needRead&&!needRec&&!needUpdate)return;"
new_need = "var needIntro=blank(info.intro),needRead=blank(info.readingCount),needRec=blank(info.recommendCount),needUpdate=(!qfTimesV1111.updateTime)||qfTimeSuspiciousV1111();if(!needIntro&&!needRead&&!needRec&&!needUpdate)return;"
assert s.count(old_need) == 1, ('search update guard', s.count(old_need))
s = s.replace(old_need, new_need, 1)

assert 'qf_updateTime_v1112' in s
s = s.replace('qf_updateTime_v1112', 'qf_updateTime_v1113')
s = s.replace('qf_qidian_search_detail_v1112_', 'qf_qidian_search_detail_v1113_')
s = s.replace('qidian-search-v1112', 'qidian-search-v1113')

# 2. 作品数据：按两个指标一行真正换行，不依赖 pre / monospace / CSS 列宽。
pat_rows = r"function dataRows\(items\)\{.*?\nfunction chips\(v,limit,color\)\{"
new_rows = """function dataRows(items){
  var a=[];for(var i=0;i<items.length;i++)if(items[i][2])a.push(items[i]);
  var h='';
  for(var j=0;j<a.length;j+=2){
    h+='<br>'+qfMetricHtmlV1112(a[j][1],a[j][2]);
    if(a[j+1])h+='　　'+qfMetricHtmlV1112(a[j+1][1],a[j+1][2]);
  }
  return h;
}
function chips(v,limit,color){"""
s, n = re.subn(pat_rows, new_rows, s, count=1, flags=re.S)
assert n == 1, 'dataRows replacement failed'
assert '<pre style=' not in s, 'pre layout remains'

old_data = """var data=[
 ['','总推荐',rec],['','月票',mt],['',clean(x.readingMetricLabel)||'在看',watch],['','评分',sc?(sc+(clean(x.ratingCount)?' / '+num(x.ratingCount)+'人':'')):'' ],
 ['','收藏',col],['','粉丝',fans],['','盟主',leader],['','投资',invest],['','首订',first]
];"""
new_data = """var data=[
 ['','总推荐',rec],['','月票',mt],['','收藏',col],['','粉丝',fans],['','盟主',leader],['','首订',first],
 ['',clean(x.readingMetricLabel)||'在看',watch],['','评分',sc?(sc+(clean(x.ratingCount)?' / '+num(x.ratingCount)+'人':'')):'' ],['','投资',invest]
];"""
assert s.count(old_data) == 1, ('data order', s.count(old_data))
s = s.replace(old_data, new_data, 1)

# 3. 详情只显示“最近更新”，移除首发时间。
old_time = """if(clean(x.updateTime))body+=row('🕒','更新',date(x.updateTime));
if(clean(x.publishDate)&&date(x.publishDate)!==date(x.updateTime))body+=row('🚀','首发',date(x.publishDate));"""
new_time = "if(clean(x.updateTime))body+=row('🕒','最近更新',date(x.updateTime));"
assert s.count(old_time) == 1, ('visible time block', s.count(old_time))
s = s.replace(old_time, new_time, 1)

# 4. Beta12 的 qfMultiContentV423 位于 loginUrl，详情 onclick 看不到它；回退已验证全局入口避免报错。
old_btn = '<button>⚡ 正文设置@onclick:qfMultiContentV423.call(this)</button>'
new_btn = '<button>⚡ 正文源状态@onclick:qfBookInfoOpenSmartSourceV330.call(this)</button>'
assert s.count(old_btn) == 1, ('broken content settings button', s.count(old_btn))
s = s.replace(old_btn, new_btn, 1)

rule['intro'] = s
src['ruleBookInfo'] = rule
src['bookSourceComment'] = 'v1.1.0-beta13：详情页时间与双列回归修复。作品资料只显示“最近更新”，移除“首发”展示；更新时间不再因“连载超过60天”被清空，仅保留空值/未来时间保护。作品数据按两项一行真实换行，主指标优先固定为总推荐/月票、收藏/粉丝、盟主/首订，其余指标继续两项一行补位。Beta12 跨作用域“正文设置”按钮回退为已验证的“正文源状态”入口，避免 qfMultiContentV423 未定义。搜索、目录、正文 Provider、评论、角色卡、书友圈、账号链冻结。'
src['lastUpdateTime'] = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
source_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()

# 5. Bundle 只替换该 Beta 源。
bundle_path = root / 'bundles/all-beta.json'
bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
assert isinstance(bundle, list)
hits = [i for i, x in enumerate(bundle) if isinstance(x, dict) and x.get('bookSourceName') == '🌈 起点增强 · Beta']
assert len(hits) == 1, ('bundle qidian-next-beta hits', hits)
bundle[hits[0]] = src
bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

now_cn = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
now_iso = now_cn.isoformat(timespec='seconds')
day = now_cn.strftime('%Y-%m-%d')
summary = '详情 beta13：只保留最近更新时间；作品数据按两项一行恢复双列；修复 Beta12 正文设置入口作用域回归。'
tags = ['起点', '测试版', '详情页', '最近更新', '富数据', '双列', '正文源状态', '缓存']
changes = [
    '作品资料只显示“最近更新”，移除“首发”展示，不再混用首发/上架时间',
    '取消“连载超过60天即判异常”的更新时间阈值；旧书的真实最近更新时间不再被误清空',
    '更新时间缓存与官方搜索详情缓存升级到 v1113，避免 Beta12 错误时间继续命中',
    '作品数据放弃 pre/monospace 与 CSS 列宽，改成每两个指标用真实换行；主指标优先为总推荐/月票、收藏/粉丝、盟主/首订',
    'Beta12 会报 qfMultiContentV423 未定义的“正文设置”入口回退为已验证的“正文源状态”全局入口',
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

# RSS detail article
detail_path = root / 'rss/data/details/beta/qidian-next.json'
detail = {
    'kind': 'source',
    'title': '🌈 起点增强 · Beta',
    'summary': summary,
    'badges': ['Beta', '1.1.0-beta13', '最近更新 / 双列 / 正文源'],
    'sections': [
        {'title': '最近更新时间', 'text': '详情页只保留“最近更新”。取消 60 天陈旧阈值，仅过滤空值和明显未来时间；刷新 v1113 时间缓存，避免旧错误继续命中。'},
        {'title': '作品数据', 'text': '不再使用 pre、等宽字体或 CSS 固定列宽。主指标按“总推荐 / 月票、收藏 / 粉丝、盟主 / 首订”成对显示，其余可用指标继续两项一行补位。'},
        {'title': '正文源入口', 'text': 'Beta12 的正文设置按钮跨作用域调用 qfMultiContentV423 会报未定义；本版回退到已验证的“正文源状态”全局入口。'},
        {'title': '冻结范围', 'text': '搜索、目录、正文 Provider 实际解析、评论、角色卡、书友圈、账号和情无 VIP 链不改。'},
    ],
    'sourceUrl': raw,
    'backupUrl': cdn,
    'importUrl': imp,
}
detail_path.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Release Log
log_path = root / 'docs/RELEASE_LOG.md'
log = log_path.read_text(encoding='utf-8')
entry = f"""## {day} — Qidian Next 1.1.0-beta13 latest-update + real two-column recovery

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 详情页作品资料只保留“最近更新”，移除首发时间展示。
- 删除连载书超过 60 天即清空更新时间的错误阈值；只保留空值与明显未来时间保护。
- 时间缓存与起点官方搜索详情缓存升级到 v1113，避免 Beta12 错误时间继续命中。
- 作品数据不再使用 pre/monospace/CSS 列宽；改成每两个指标用真实 HTML 换行显示，主指标优先为总推荐/月票、收藏/粉丝、盟主/首订。
- Beta12 跨作用域“正文设置”回调回退为已验证的“正文源状态”全局入口，消除 qfMultiContentV423 未定义报错。
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
