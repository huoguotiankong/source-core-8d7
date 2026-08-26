import copy, datetime, hashlib, json, pathlib, re

ROOT = pathlib.Path('.')
source_path = ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
target_url = 'https://m.qidian.com/?qf_source=qidian_next_8d7'
version = '1.1.0-beta7'
version_code = 11007
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).replace(microsecond=0)
now_iso = now.isoformat()
date = now.date().isoformat()

data = json.loads(source_path.read_text('utf-8'))
assert isinstance(data, list) and len(data) == 1
src = data[0]
before = copy.deepcopy(src)
assert src.get('bookSourceName') == '🌈 起点增强 · Beta'
assert src.get('bookSourceUrl') == target_url
assert src.get('bookSourceComment','').startswith('v1.1.0-beta6')

init = src['ruleBookInfo']['init']
assert 'function introFromCurrent(html){' in init
assert 'function cached(k,vk,asList){' in init
assert 'qf_detailPcEnrichedAtV1106' in init

start = init.index('function introFromCurrent(html){')
end = init.index('function cached(k,vk,asList){', start)
new_intro = r'''function introCleanV1107(v){
  var t=unesc(String(v||''));
  try{t=org.jsoup.Jsoup.parse(t).text();}catch(e){t=t.replace(/<[^>]+>/g,' ');}
  t=t.replace(/\\r\\n|\\n|\\r/g,' ').replace(/\s+/g,' ').trim();
  if(t.length<10||t.length>5000)return '';
  if(/创作的.{0,20}(?:小说|作品)《/.test(t)&&/(?:已更新|最新章节|主要角色)/.test(t))return '';
  if(/^(?:起点中文网|小说在线阅读|最新章节|章节目录)/.test(t)&&t.length<120)return '';
  return t;
}
function introTtsV1107(html){
  html=String(html||'');if(!html)return '';
  var p=plain(html),m=p.match(/作品简介\s*([\s\S]{10,2200}?)(?:音频服务|目录\s|目录$|正文卷|免费试读|加入书架)/);
  if(m&&m[1]){var t=introCleanV1107(m[1]);if(t)return t;}
  return '';
}
function introJsonWalkV1107(node,depth){
  if(node===undefined||node===null||depth>7)return '';
  if(Array.isArray(node)){
    for(var ai=0;ai<node.length&&ai<80;ai++){var av=introJsonWalkV1107(node[ai],depth+1);if(av)return av;}
    return '';
  }
  if(typeof node!=='object')return '';
  var pri=['bookIntro','BookIntro','bookIntroWords','BookIntroWords','contentIntro','ContentIntro','bookDescription','BookDescription','description','Description','intro','Intro','desc','Desc'];
  for(var pi=0;pi<pri.length;pi++){
    var pv=node[pri[pi]];
    if(typeof pv==='string'){var pt=introCleanV1107(pv);if(pt)return pt;}
  }
  var keys=[];try{keys=Object.keys(node);}catch(e){keys=[];}
  for(var ki=0;ki<keys.length&&ki<120;ki++){
    var k=keys[ki],v=node[k];
    if(v&&typeof v==='object'){
      var low=String(k).toLowerCase();
      if(/book|detail|info|data|page|state|novel|author/.test(low)){
        var vv=introJsonWalkV1107(v,depth+1);if(vv)return vv;
      }
    }
  }
  for(var kj=0;kj<keys.length&&kj<120;kj++){
    var v2=node[keys[kj]];
    if(v2&&typeof v2==='object'){var rr=introJsonWalkV1107(v2,depth+1);if(rr)return rr;}
  }
  return '';
}
function introJsonTextV1107(s){
  s=String(s||'').trim();if(!s)return '';
  var tries=[s];
  var a=s.indexOf('{'),z=s.lastIndexOf('}');if(a>=0&&z>a)tries.push(s.slice(a,z+1));
  var aa=s.indexOf('['),zz=s.lastIndexOf(']');if(aa>=0&&zz>aa)tries.push(s.slice(aa,zz+1));
  for(var i=0;i<tries.length;i++){
    try{var obj=JSON.parse(tries[i]);var t=introJsonWalkV1107(obj,0);if(t)return t;}catch(e){}
  }
  return '';
}
function introFromCurrent(html){
  html=String(html||'');if(!html)return '';
  var tt=introTtsV1107(html);if(tt)return tt;
  try{
    var d=org.jsoup.Jsoup.parse(html);
    var sels=['#book-intro-detail','.book-intro-detail','.book-intro','.intro','[id*=book-intro]','[class*=book-intro]','[id*=bookIntro]','[class*=bookIntro]'];
    for(var i=0;i<sels.length;i++){
      var es=d.select(sels[i]);
      for(var ei=0;es&&ei<es.size()&&ei<5;ei++){var t=introCleanV1107(es.get(ei).text());if(t)return t;}
    }
    var metas=d.select('meta[property=og:description],meta[name=description],meta[name=Description]');
    for(var mi=0;mi<metas.size();mi++){var mt=introCleanV1107(metas.get(mi).attr('content'));if(mt)return mt;}
    var lds=d.select('script[type=application/ld+json]');
    for(var li=0;li<lds.size();li++){var lt=introJsonTextV1107(lds.get(li).html());if(lt)return lt;}
    var scripts=d.select('script');
    var nameHint=String(info&&info.name||searchName||'').trim();
    for(var si=0;si<scripts.size()&&si<80;si++){
      var st=String(scripts.get(si).html()||'');
      if(st.length<20||st.length>2000000)continue;
      var related=(bid&&st.indexOf(String(bid))>=0)||(nameHint&&st.indexOf(nameHint)>=0);
      if(!related||!/(?:intro|description|bookInfo|bookIntro|bookDescription)/i.test(st))continue;
      var jt=introJsonTextV1107(st);if(jt)return jt;
    }
  }catch(e){}
  var ks=['BookIntro','bookIntro','BookIntroWords','bookIntroWords','BookDesc','bookDesc','BookDescription','bookDescription','ContentIntro','contentIntro','Description','description','Introduction','introduction'];
  for(var j=0;j<ks.length;j++){
    var k=ks[j].replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    var r=new RegExp("[\\\"']?"+k+"[\\\"']?\\\\s*[:=]\\\\s*[\\\"']([\\\\s\\\\S]{8,3500}?)[\\\"']\\\\s*(?:[,}])",'i');
    var m=html.match(r);if(!m||!m[1])continue;
    var tx=introCleanV1107(m[1]);if(tx)return tx;
  }
  return '';
}
function introProbeV1107(html){
  html=String(html||'');if(!html)return 'len=0';
  var flags=[],sc=0;
  function f(name,re){try{if(re.test(html))flags.push(name);}catch(e){}}
  f('bookInfo',/bookInfo/i);f('bookIntro',/bookIntro/i);f('intro',/\bintro\b/i);f('description',/description/i);f('ldjson',/application\/ld\+json/i);f('next',/__NEXT_DATA__/i);f('作品简介',/作品简介/);
  var title=String(info&&info.name||searchName||'').trim();
  if(title){try{var te=title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');if(new RegExp(te).test(html))flags.push('title');}catch(e){}}
  try{var d=org.jsoup.Jsoup.parse(html);sc=d.select('script').size();}catch(e){}
  return 'len='+html.length+'; flags='+(flags.join(',')||'none')+'; scripts='+sc;
}
'''
init = init[:start] + new_intro + init[end:]

old_fast = "if(blank(info.intro))info.intro=introFromCurrent(html)||searchIntro||bv('qf_introOfficial');"
new_fast = old_fast + "\nif(blank(info.intro))info.introDiag='当前:'+introProbeV1107(html)+'; search='+String(searchIntro?searchIntro.length:0)+'; cache='+String(bv('qf_introOfficial')?bv('qf_introOfficial').length:0);"
assert init.count(old_fast) == 1
init = init.replace(old_fast, new_fast)

assert init.count('qf_detailPcEnrichedAtV1106') == 2
init = init.replace('qf_detailPcEnrichedAtV1106', 'qf_detailPcEnrichedAtV1107')

old_pcurl = "  var pcUrl='https://www.qidian.com/book/'+encodeURIComponent(String(bid))+'/',pcHtml='';"
new_pcurl = "  var needIntro=blank(info.intro);\n  var pcUrl=needIntro?('https://www.qidian.com/ttsbook/'+encodeURIComponent(String(bid))+'/9/'):('https://www.qidian.com/book/'+encodeURIComponent(String(bid))+'/'),pcHtml='';"
assert init.count(old_pcurl) == 1
init = init.replace(old_pcurl, new_pcurl)

old_empty = "  if(!pcHtml||pcHtml.length<500)return;"
new_empty = "  if(!pcHtml||pcHtml.length<500){info.introDiag=String(info.introDiag||'')+'; 官方补全:empty('+String(pcHtml.length||0)+')';return;}\n  info.introDiag=String(info.introDiag||'')+'; 官方补全:'+introProbeV1107(pcHtml);"
assert init.count(old_empty) == 1
init = init.replace(old_empty, new_empty)

old_fill = "qfFillV1104('intro',rich.intro||introFromCurrent(pcHtml));"
new_fill = "qfFillV1104('intro',rich.intro||introFromCurrent(pcHtml));if(!blank(info.intro))info.introDiag=String(info.introDiag||'')+'; hit='+String(info.intro.length);"
assert init.count(old_fill) == 1
init = init.replace(old_fill, new_fill)

src['ruleBookInfo']['init'] = init

intro_rule = src['ruleBookInfo']['intro']
old_tail = "if(desc)body+='<br><br><b><font color=\"#149c95\">▍内容简介</font></b><br><br><span>'+esc(desc).replace(/\\r\\n|\\r|\\n/g,'<br>')+'</span>';"
assert intro_rule.count(old_tail) == 1, 'intro renderer tail not found'
new_tail = old_tail + "\nif(!desc&&clean(x.introDiag))body+='<br><br><b><font color=\"#d78b2f\">▍简介诊断</font></b><br><br><font color=\"#8a949b\">'+esc(clean(x.introDiag))+'</font>';"
intro_rule = intro_rule.replace(old_tail, new_tail)
src['ruleBookInfo']['intro'] = intro_rule

src['bookSourceComment'] = ('v1.1.0-beta7：详情简介官方 TTS 兜底与结构诊断版。Beta6 真机仍无内容简介，证明 bookInfo/BookInfo 不能稳定当成简介字符串。'
                            '本版在不扩大详情网络请求数量的前提下，简介缺失时把原有“最多一次官方补全”的请求槽切换到起点官方 TTS 书页，直接提取其“作品简介”；'
                            '同时增强当前响应/补全响应的 DOM、meta description、JSON-LD 与相关脚本 JSON 结构化解析。若仍为空，详情页临时显示低敏“简介诊断”，只输出响应长度、候选结构与命中长度，不输出正文、Cookie 或账号数据。'
                            '单次超时仍为 2.6 秒，30 分钟防重复；搜索、目录、正文 Provider、段评/本章说、角色卡、书友圈及情无 VIP 认证链不改。')

changed = {k for k in src if src.get(k) != before.get(k)} | {k for k in before if src.get(k) != before.get(k)}
assert changed == {'bookSourceComment','ruleBookInfo'}, changed
rb_changed = {k for k in src['ruleBookInfo'] if src['ruleBookInfo'].get(k) != before['ruleBookInfo'].get(k)} | {k for k in before['ruleBookInfo'] if src['ruleBookInfo'].get(k) != before['ruleBookInfo'].get(k)}
assert rb_changed == {'init','intro'}, rb_changed
assert src['jsLib'] == before['jsLib']
assert src['bookSourceUrl'] == before['bookSourceUrl'] == target_url
assert 'introTtsV1107' in init and 'introJsonWalkV1107' in init and 'introProbeV1107' in init
assert 'https://www.qidian.com/ttsbook/' in init
assert init.count("dr=dj.get(pcUrl,dh,2600)") == 1
assert init.count("dj.ajax(pcUrl+','+JSON.stringify({timeout:2600,headers:dh}))") == 1
assert init.count("qfDetailPcEnrichV1104.call(this)") == 1
assert '▍简介诊断' in intro_rule

source_text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
source_path.write_text(source_text, 'utf-8')
sha = hashlib.sha256(source_text.encode('utf-8')).hexdigest()

import subprocess, tempfile
for rule_name in ('init','intro'):
    code = src['ruleBookInfo'][rule_name]
    if code.startswith('<js>') and code.endswith('</js>'):
        code = code[4:-5]
    with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as tf:
        tf.write(code); js_path = tf.name
    subprocess.run(['node','--check',js_path], check=True)

bundle_path = ROOT/'bundles/all-beta.json'
bundle = json.loads(bundle_path.read_text('utf-8'))
replaced = 0
def replace_source(node):
    global replaced
    if isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, dict) and v.get('bookSourceUrl') == target_url and v.get('bookSourceName') == '🌈 起点增强 · Beta':
                node[i] = copy.deepcopy(src); replaced += 1
            else: replace_source(v)
    elif isinstance(node, dict):
        for k, v in list(node.items()):
            if isinstance(v, dict) and v.get('bookSourceUrl') == target_url and v.get('bookSourceName') == '🌈 起点增强 · Beta':
                node[k] = copy.deepcopy(src); replaced += 1
            else: replace_source(v)
replace_source(bundle)
assert replaced >= 1
bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2)+'\n','utf-8')

sub_path = ROOT/'subscription/beta.json'
sub = json.loads(sub_path.read_text('utf-8'))
sub['updatedAt'] = now_iso
item = next(x for x in sub['items'] if x.get('id') == 'qidian-next-beta')
item.update({
    'summary':'详情 beta7：简介缺失时复用唯一官方补全请求改走起点 TTS 书页，并增加结构化解析/低敏诊断。',
    'version':version,'updatedAt':date,
    'tags':['起点','测试版','详情页','书籍简介','官方TTS','结构化解析','单请求'],
    'changelog':['简介缺失时唯一补全请求改走起点官方 TTS 书页','新增作品简介文本、meta / JSON-LD / 相关脚本 JSON 解析','仍失败时显示低敏简介诊断','维持最多一次请求、2.6 秒超时和 30 分钟防重复'],
    'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}',
    'backupUrl':f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}',
    'importUrl':f'legado://import/importonline?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}'
})
sub_path.write_text(json.dumps(sub, ensure_ascii=False, indent=2)+'\n','utf-8')

man_path = ROOT/'manifest.json'
man = json.loads(man_path.read_text('utf-8'))
man['updatedAt'] = now_iso
found=[]
def walk(node):
    if isinstance(node,dict):
        if node.get('bookSourceUrl') == target_url and (node.get('id')=='qidian-next-beta' or node.get('name')=='🌈 起点增强 · Beta'): found.append(node)
        for v in node.values(): walk(v)
    elif isinstance(node,list):
        for v in node: walk(v)
walk(man); assert found
for m in found:
    m.update({'version':version,'versionCode':version_code,'updatedAt':now_iso,
              'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}',
              'summary':'详情 beta7：用同一个官方补全请求槽获取起点 TTS 作品简介，并加入结构化解析/诊断。',
              'tags':['起点','测试版','详情页','书籍简介','官方TTS','结构化解析','单请求'],
              'changelog':['简介缺失时改用起点官方 TTS 书页补全','增强 DOM/meta/JSON-LD/脚本 JSON 简介解析','失败时输出低敏诊断','其它核心模块保持不变'],
              'sha256':sha})
man_path.write_text(json.dumps(man, ensure_ascii=False, indent=2)+'\n','utf-8')

rss_path = ROOT/'rss/data/details/beta/qidian-next.json'
rss = json.loads(rss_path.read_text('utf-8'))
rss.update({'summary':'详情 beta7：官方 TTS 简介兜底 + 结构化解析 + 失败诊断。','badges':['Beta',version,'简介修复'],
            'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}',
            'backupUrl':f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}',
            'importUrl':f'legado://import/importonline?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}'})
rss['sections']=[
    {'title':'Beta6 结论','text':'真机复测证明 bookInfo/BookInfo 不是可稳定直接读取的简介字符串，继续猜单字段不可取。'},
    {'title':'官方 TTS 兜底','text':'简介为空时不增加第二请求，而是把原有最多一次的官方补全请求改到起点 TTS 书页，从“作品简介”直接提取文本。'},
    {'title':'结构化解析','text':'同时解析当前/补全响应中的简介 DOM、meta description、JSON-LD 和当前书籍相关脚本 JSON。'},
    {'title':'失败诊断','text':'若最终仍为空，详情页临时显示低敏简介诊断，只包含响应长度、候选结构、脚本数和命中长度，不输出正文、Cookie 或账号信息。'}]
rss_path.write_text(json.dumps(rss, ensure_ascii=False, indent=2)+'\n','utf-8')

ki=ROOT/'docs/KNOWN_ISSUES.md'; kt=ki.read_text('utf-8')
if '## 27. Beta6 synopsis repair still blank' not in kt:
    kt += f"\n\n## 27. Beta6 synopsis repair still blank on real device — investigating in {version}\n\nReal-device retest on `同时穿越：继承万界遗产` still showed no 内容简介 while works metadata, month tickets, shortcuts and tags rendered. This disproves the Beta6 assumption that Qidian `bookInfo/BookInfo` can be treated as a scalar synopsis field. Beta7 uses the existing single enrichment request slot for Qidian's official TTS page when synopsis is missing, because that server-rendered page exposes a visible `作品简介`; it also adds DOM/meta/JSON-LD/book-related-script parsing. If no synopsis is found, a low-sensitivity diagnostic line is rendered. No second network request is added. Status: Beta, pending real-device feedback.\n"
ki.write_text(kt,'utf-8')

rl=ROOT/'docs/RELEASE_LOG.md'; rt=rl.read_text('utf-8')
if f'🌈 起点增强 {version}' not in rt:
    rt += f"\n\n### {date} — 🌈 起点增强 {version}\n- Real-device Beta6 still had no synopsis; reopen the synopsis issue rather than marking it fixed.\n- When synopsis is missing, reuse the one official enrichment request slot for Qidian's server-rendered TTS book page and extract its visible 作品简介.\n- Add DOM/meta description/JSON-LD/book-related script JSON parsing and a low-sensitivity fallback diagnostic.\n- Keep the physical one-request ceiling, 2.6s timeout, 30-minute suppression, Stable 1.0.0 and all non-detail modules unchanged.\n"
rl.write_text(rt,'utf-8')

ho=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; ht=ho.read_text('utf-8')
if f'## Synopsis official TTS fallback {version}' not in ht:
    ht += f"\n\n## Synopsis official TTS fallback {version} ({date})\n\n- Beta6 real-device result: synopsis still absent on `同时穿越：继承万界遗产`; other detail blocks remained functional.\n- `bookInfo/BookInfo` must not be assumed to be a scalar synopsis field.\n- Beta7 keeps the one-request network ceiling. If synopsis is blank, the sole enrichment request targets Qidian official `https://www.qidian.com/ttsbook/<bookId>/9/`, whose server-rendered page exposes `作品简介`; otherwise the existing PC detail enrichment URL is retained.\n- Parser also checks intro DOM, meta description, JSON-LD and current-book-related script JSON. If all fail, `introDiag` temporarily shows only response length/structure/script count/hit length.\n- Source guard: only `bookSourceComment` and `ruleBookInfo.init/intro` change; `jsLib`, source identity, search/catalog/content/review/Provider and 情无 logic remain unchanged.\n- Status: Beta pending real-device feedback.\n"
ho.write_text(ht,'utf-8')

for p in [source_path,bundle_path,sub_path,man_path,rss_path]: json.loads(p.read_text('utf-8'))
print('Beta7 source sha256:',sha)
print('Bundle replacements:',replaced)
print('Manifest matches:',len(found))
