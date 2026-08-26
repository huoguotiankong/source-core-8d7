import json
import pathlib
import hashlib
import datetime

root = pathlib.Path('.')
source_path = root / 'sources/novel/qidian-next/qidian-next-beta.json'
stable_path = root / 'sources/novel/qidian-next/qidian-next.json'
stable_before = hashlib.sha256(stable_path.read_bytes()).hexdigest()

def find_rule_field(rule, token, label):
    hits = [(k, v) for k, v in rule.items() if isinstance(v, str) and token in v]
    assert len(hits) == 1, f'{label}: hits={[k for k,_ in hits]}'
    return hits[0]

def replace_once(text, old, new, label):
    n = text.count(old)
    assert n == 1, f'{label}: expected 1, got {n}'
    return text.replace(old, new, 1)

doc = json.loads(source_path.read_text(encoding='utf-8'))
assert isinstance(doc, list) and len(doc) == 1
src = doc[0]
assert src.get('bookSourceName') == '🌈 起点增强 · Beta'
assert 'v1.1.0-beta13' in src.get('bookSourceComment',''), 'Beta13 baseline required'
rule = src.get('ruleBookInfo')
assert isinstance(rule, dict)
render_key, rs = find_rule_field(rule, 'function dataRows(items)', 'render field')

# 1) 作品数据：月票 / 收藏 / 粉丝固定左列；其余指标固定右列。
assert 'function dataColumnsV1114(' not in rs
insert_marker = 'function chips(v,limit,color){'
assert insert_marker in rs
column_helper = r'''function qfMetricPadV1114(label,value){
  var w=qfDispWidthV1112(qfMetricTextV1112(label,value)),h='';
  while(w<16){h+='　';w+=2;}
  return h;
}
function dataColumnsV1114(left,right){
  var l=[],r=[],i;
  for(i=0;i<left.length;i++)if(left[i][2])l.push(left[i]);
  for(i=0;i<right.length;i++)if(right[i][2])r.push(right[i]);
  var rows=Math.max(l.length,r.length),h='';
  for(i=0;i<rows;i++){
    h+='<br>';
    if(l[i])h+=qfMetricHtmlV1112(l[i][1],l[i][2])+qfMetricPadV1114(l[i][1],l[i][2]);
    else h+='　　　　　　　　';
    if(r[i])h+=qfMetricHtmlV1112(r[i][1],r[i][2]);
  }
  return h;
}
'''
rs = rs.replace(insert_marker, column_helper + insert_marker, 1)

data_start = rs.find('var data=[')
assert data_start >= 0, 'old data array missing'
data_end_marker = 'var dr=dataRows(data);'
data_end = rs.find(data_end_marker, data_start)
assert data_end >= 0, 'old dataRows call missing'
new_data = r'''var leftData=[
 ['','月票',mt],['','收藏',col],['','粉丝',fans]
];
var rightData=[
 ['','总推荐',rec],['','盟主',leader],['','首订',first],
 ['',clean(x.readingMetricLabel)||'在看',watch],['','评分',sc?(sc+(clean(x.ratingCount)?' / '+num(x.ratingCount)+'人':'')):'' ],['','投资',invest]
];
var dr=dataColumnsV1114(leftData,rightData);'''
# Replace through the old dataRows invocation.
old_end = data_end + len(data_end_marker)
rs = rs[:data_start] + new_data + rs[old_end:]

# 2) 快捷入口：三枚短按钮紧凑排列，正文入口改为直达设置。
quick_start = rs.find("body+=section('快捷入口','#149c95');")
assert quick_start >= 0, 'quick entry section missing'
quick_end = rs.find('var tg=chips(', quick_start)
assert quick_end >= 0, 'quick entry end missing'
quick_block = r'''body+=section('快捷入口','#149c95');
body+='<br><button>💬 书友圈@onclick:qfBookInfoOpenCircleV373.call(this)</button> <button>🎭 角色卡@onclick:qfBookInfoOpenRoleV373.call(this)</button> <button>⚡ 正文设置@onclick:qfBookInfoOpenContentSettingsV1114.call(this)</button>';

'''
rs = rs[:quick_start] + quick_block + rs[quick_end:]
rule[render_key] = rs
src['ruleBookInfo'] = rule

# 3) 在 jsLib 增加详情页可见的自包含正文设置入口。
jslib = src.get('jsLib','')
assert isinstance(jslib, str)
assert 'function qfBookInfoOpenContentSettingsV1114' not in jslib
helper = r'''

/* Qidian Next 1.1.0-beta14: 详情页直达正文设置。 */
function qfBookInfoSettingsEscV1114(v){
    return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
function qfBookInfoSettingsGetV1114(s,key,def){
    var v='';
    try{var m=s.getLoginInfoMap?s.getLoginInfoMap():null;v=String(m&&(m.get?m.get(key):m[key])||'');}catch(_e0){}
    if(!v)try{var o=JSON.parse(String(s.getLoginInfo?s.getLoginInfo():'{}'))||{};v=String(o[key]||'');}catch(_e1){}
    return v||String(def==null?'':def);
}
function qfBookInfoSettingsSaveV1114(s,j,vals){
    var old={};try{old=JSON.parse(String(s.getLoginInfo?s.getLoginInfo():'{}'))||{};}catch(_e0){old={};}
    var hm=null;try{hm=new Packages.java.util.HashMap();}catch(_e1){}
    for(var k in vals)if(vals.hasOwnProperty(k)){
        var v=String(vals[k]==null?'':vals[k]);old[String(k)]=v;
        if(hm)try{hm.put(String(k),v);}catch(_e2){}
    }
    try{if(hm&&j&&j.upLoginData)j.upLoginData(hm);}catch(_e3){}
    try{s.putLoginInfo(JSON.stringify(old));}catch(_e4){}
    return true;
}
function qfBookInfoSettingsDecodeV1114(v){
    return String(v||'').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
}
function qfBookInfoSettingsReadV1114(body,id){
    try{var r=new RegExp('id=["\\\']'+id+'["\\\'][^>]*>([^<]*)<\\/span>','i'),m=String(body||'').match(r);return m?qfBookInfoSettingsDecodeV1114(m[1]):null;}catch(_e){return null;}
}
function qfBookInfoOpenContentSettingsV1114(){
    var j=qfJava(this),s=qfSource(this);if(!j||!s)return false;
    var tier=qfBookInfoSettingsGetV1114(s,'正文源类别','限免源');
    var tiers=['限免源','优选源','兜底源','STV源','全源智能'];
    if(tiers.indexOf(tier)<0)tier='限免源';
    var vals={
      '限免源':qfBookInfoSettingsGetV1114(s,'限免源选择','自动'),
      '优选源':qfBookInfoSettingsGetV1114(s,'优选源选择','自动'),
      '兜底源':qfBookInfoSettingsGetV1114(s,'兜底源选择','自动'),
      'STV源':qfBookInfoSettingsGetV1114(s,'STV源选择','STV·自动'),
      '全源智能':qfBookInfoSettingsGetV1114(s,'全源智能选择','自动')
    };
    var stvKey=qfBookInfoSettingsGetV1114(s,'STV API密钥','');
    var state=JSON.stringify({tier:tier,vals:vals,stvKey:stvKey});
    var css='*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}:root{color-scheme:light dark;--bg:#f5f6fa;--card:#fff;--text:#202532;--muted:#7e8798;--line:#e7eaf0;--pri:#3599f5;--soft:#eaf5ff;--ok:#149c95}@media(prefers-color-scheme:dark){:root{--bg:#101319;--card:#191e27;--text:#edf1f6;--muted:#9ca6b8;--line:#2b3340;--soft:#1c3448}}html,body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}.wrap{padding:18px}.hero,.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px;margin-bottom:14px}.hero h1{margin:0 0 6px;font-size:22px}.hero p,.note{margin:0;color:var(--muted);font-size:13px;line-height:1.6}.label{font-weight:700;margin-bottom:10px}.route{font-size:14px;color:var(--ok);margin-top:10px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}.grid button{border:1px solid var(--line);border-radius:12px;padding:10px 4px;background:var(--card);color:var(--text);font-size:14px}.grid button.on{background:var(--soft);border-color:var(--pri);color:var(--pri);font-weight:700}.field input{width:100%;border:1px solid var(--line);border-radius:12px;padding:12px;background:var(--card);color:var(--text);font-size:14px}.hide{display:none}.out{display:none}';
    var html='<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><style>'+css+'</style></head><body><div class="wrap">'+
      '<div class="hero"><h1>⚡ 正文设置</h1><p>详情页直达正文路由中心。修改后点击右上角 ✓ 返回，设置自动保存。</p><div id="route" class="route"></div></div>'+
      '<div class="card"><div class="label">正文源类别</div><div id="tierBox" class="grid"></div></div>'+
      '<div class="card"><div class="label">Provider</div><div id="providerBox" class="grid"></div></div>'+
      '<div id="stvCard" class="card field"><div class="label">STV API 密钥</div><input id="stvKey" type="text" value="'+qfBookInfoSettingsEscV1114(stvKey)+'" placeholder="仅 STV 源需要"></div>'+
      '<div class="card note">固定源只使用当前选中的 Provider；自动模式按对应类别策略运行。STV 不进入限免 / 优选 / 兜底 / 全源智能自动池。</div>'+
      '<span id="ux_tier" class="out"></span><span id="ux_limited" class="out"></span><span id="ux_preferred" class="out"></span><span id="ux_fallback" class="out"></span><span id="ux_stv" class="out"></span><span id="ux_all" class="out"></span><span id="ux_stvkey" class="out"></span>'+
      '<script>var S='+state+';var tiers=["限免源","优选源","兜底源","STV源","全源智能"],pmap={"限免源":["自动","情无","神魔","晴天","同人"],"优选源":["自动","七猫","书旗","QQ浏览器","得间","酷我"],"兜底源":["自动","猫眼","得奇","69书吧","速读谷","万相"],"STV源":["STV·自动","STV·qidian"],"全源智能":["自动"]};function set(id,v){document.getElementById(id).textContent=v||""}function sync(){set("ux_tier",S.tier);set("ux_limited",S.vals["限免源"]||"自动");set("ux_preferred",S.vals["优选源"]||"自动");set("ux_fallback",S.vals["兜底源"]||"自动");set("ux_stv",S.vals["STV源"]||"STV·自动");set("ux_all",S.vals["全源智能"]||"自动");set("ux_stvkey",document.getElementById("stvKey").value);document.getElementById("route").textContent="当前路线："+S.tier+" · "+(S.vals[S.tier]||"自动");document.getElementById("stvCard").className=S.tier==="STV源"?"card field":"card field hide"}function renderTiers(){var b=document.getElementById("tierBox");b.innerHTML="";tiers.forEach(function(t){var x=document.createElement("button");x.type="button";x.textContent=t;x.className=t===S.tier?"on":"";x.onclick=function(){S.tier=t;renderTiers();renderProviders();sync()};b.appendChild(x)})}function renderProviders(){var b=document.getElementById("providerBox"),arr=pmap[S.tier]||["自动"];b.innerHTML="";if(arr.indexOf(S.vals[S.tier])<0)S.vals[S.tier]=arr[0];arr.forEach(function(v){var x=document.createElement("button");x.type="button";x.textContent=v;x.className=v===S.vals[S.tier]?"on":"";x.onclick=function(){S.vals[S.tier]=v;renderProviders();sync()};b.appendChild(x)})}document.getElementById("stvKey").addEventListener("input",sync);renderTiers();renderProviders();sync();</script></div></body></html>';
    var body='';
    try{body=String(j.startBrowserAwait('data:text/html;base64,'+j.base64Encode(html),'正文设置',false).body()||'');}
    catch(e){try{j.longToast('打开正文设置失败：'+String(e));}catch(_e0){}return false;}
    if(!body)return true;
    var map={
      '正文源类别':'ux_tier','限免源选择':'ux_limited','优选源选择':'ux_preferred','兜底源选择':'ux_fallback',
      'STV源选择':'ux_stv','全源智能选择':'ux_all','STV API密钥':'ux_stvkey'
    },out={},k;
    for(k in map)if(map.hasOwnProperty(k)){
        var v=qfBookInfoSettingsReadV1114(body,map[k]);if(v!==null)out[k]=v;
    }
    qfBookInfoSettingsSaveV1114(s,j,out);
    return true;
}
'''
src['jsLib'] = jslib + helper

src['bookSourceComment'] = 'v1.1.0-beta14：详情页作品数据按固定左右列重排：月票/收藏/粉丝固定左列，其余可用指标固定右列；快捷入口缩短为三枚紧凑按钮；正文入口由状态提示改为详情页直达正文设置，并使用 jsLib 自包含设置页避免 loginUrl 作用域问题。搜索、目录、正文 Provider 实际解析、评论、角色卡、书友圈、账号链冻结。'
src['lastUpdateTime'] = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
source_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()

# Bundle 只替换当前 Beta 对象。
bundle_path = root / 'bundles/all-beta.json'
bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
assert isinstance(bundle, list)
hits = [i for i,x in enumerate(bundle) if isinstance(x,dict) and x.get('bookSourceName') == '🌈 起点增强 · Beta']
assert len(hits) == 1, ('bundle hits', hits)
bundle[hits[0]] = src
bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

now_cn = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
now_iso = now_cn.isoformat(timespec='seconds')
day = now_cn.strftime('%Y-%m-%d')
summary = '详情 beta14：作品数据固定左右列；快捷入口紧凑化；正文按钮直达正文设置。'
tags = ['起点','测试版','详情页','作品数据','固定双列','快捷入口','正文设置','直达设置']
changes = [
    '作品数据固定分栏：月票、收藏、粉丝只进入左列；总推荐、盟主、首订、在看、评分、投资等只进入右列',
    '双列继续使用真实 HTML 换行与全角空格补位，不回退到真机兼容性较差的 table/pre/CSS 固定列宽',
    '快捷入口压缩为书友圈、角色卡、正文设置三枚短按钮，减少第三枚按钮单独换行的情况',
    '正文入口不再只弹“正文源状态”，改为 jsLib 全局自包含正文设置页，直接编辑正文源类别、各 Provider 与 STV API 密钥',
    '避免再次跨作用域调用 loginUrl 内 qfMultiContentV423；设置保存继续写回阅读登录信息映射',
    '搜索、目录、正文 Provider 实际取正文逻辑、评论、角色卡、书友圈和账号链冻结'
]
raw = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v=11014'
cdn = 'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v=11014'
imp = 'legado://import/importonline?src=' + raw

sub_path = root / 'subscription/beta.json'
sub = json.loads(sub_path.read_text(encoding='utf-8'))
item = next(x for x in sub['items'] if x.get('id') == 'qidian-next-beta')
item.update({'summary':summary,'version':'1.1.0-beta14','updatedAt':day,'tags':tags,'changelog':changes,'sourceUrl':raw,'backupUrl':cdn,'importUrl':imp})
sub['updatedAt'] = now_iso
sub_path.write_text(json.dumps(sub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

man_path = root / 'manifest.json'
man = json.loads(man_path.read_text(encoding='utf-8'))
mi = next(x for x in man['sources'] if x.get('id') == 'qidian-next-beta')
mi.update({'version':'1.1.0-beta14','versionCode':11014,'updatedAt':now_iso,'sourceUrl':raw,'summary':summary,'tags':tags,'changelog':changes,'sha256':source_sha})
man['updatedAt'] = now_iso
man_path.write_text(json.dumps(man, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

rss_path = root / 'rss/data/details/beta/qidian-next.json'
rss = {
  'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,
  'badges':['Beta','1.1.0-beta14','固定双列 / 快捷入口 / 正文设置'],
  'sections':[
    {'title':'作品数据','text':'固定左右列：月票、收藏、粉丝只在左侧；总推荐、盟主、首订、在看、评分、投资等其余可用指标只在右侧。'},
    {'title':'快捷入口','text':'书友圈、角色卡、正文设置三枚短按钮紧凑排列，降低第三枚按钮被单独挤到下一行的概率。'},
    {'title':'正文设置直达','text':'详情按钮直接打开自包含正文设置页，可修改正文源类别、各类 Provider 以及 STV API 密钥；不再跨作用域调用 loginUrl 内函数。'},
    {'title':'冻结范围','text':'搜索、目录、正文 Provider 实际解析、评论、角色卡、书友圈、账号和情无 VIP 链不改。'}
  ],
  'sourceUrl':raw,'backupUrl':cdn,'importUrl':imp
}
rss_path.write_text(json.dumps(rss, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

log_path = root / 'docs/RELEASE_LOG.md'
log = log_path.read_text(encoding='utf-8')
entry = f'''## {day} — Qidian Next 1.1.0-beta14 fixed metric columns + direct content settings

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 详情作品数据改为固定左右列：月票 / 收藏 / 粉丝固定左列，其余可用指标固定右列。
- 继续使用真实 HTML 换行和全角空格补位，不使用已在真机失败过的 table / pre / CSS 固定列宽方案。
- 快捷入口缩短为书友圈 / 角色卡 / 正文设置三枚紧凑按钮，减少不均匀换行。
- 原“正文源状态”入口改为详情页直达正文设置；新增 jsLib 全局自包含设置页，避免 loginUrl 作用域导致 qfMultiContentV423 未定义。
- 正文设置页可直接修改正文源类别、各类别 Provider 和 STV API 密钥，并写回原登录信息映射。
- 搜索、目录、正文 Provider 实际解析、评论、角色卡、书友圈和账号链冻结。
- Published SHA256: `{source_sha}`.


'''
log_path.write_text(entry + log, encoding='utf-8')

# Static validation
parsed = json.loads(source_path.read_text(encoding='utf-8'))[0]
prs = parsed['ruleBookInfo'][render_key]
assert "['','月票',mt],['','收藏',col],['','粉丝',fans]" in prs
assert "['','总推荐',rec],['','盟主',leader],['','首订',first]" in prs
assert 'var dr=dataColumnsV1114(leftData,rightData);' in prs
assert '正文源状态@onclick' not in prs
assert '⚡ 正文设置@onclick:qfBookInfoOpenContentSettingsV1114.call(this)' in prs
assert 'function qfBookInfoOpenContentSettingsV1114' in parsed['jsLib']
assert 'qfMultiContentV423.call(this)' not in prs
assert json.loads(sub_path.read_text(encoding='utf-8'))['items']
assert json.loads(man_path.read_text(encoding='utf-8'))
assert json.loads(bundle_path.read_text(encoding='utf-8'))
assert hashlib.sha256(stable_path.read_bytes()).hexdigest() == stable_before, 'stable source changed'

print('RENDER_FIELD', render_key)
print('SOURCE_SHA256', source_sha)
print('VERSION', '1.1.0-beta14')
print('VALIDATION', 'OK')
