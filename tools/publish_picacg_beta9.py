import json
import hashlib
import pathlib
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
VERSION = '1.0.0-beta9'
VERSION_CODE = 10009
DISPLAY_NAME = '◈ 哔咔漫画'
SOURCE_ID = 'https://sc8d7.invalid/legado/picacg-8d7'
ICON_URL = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/assets/source-core-source-icon.svg'
DATE = '2026-08-26'
NOW = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
SUMMARY = 'Beta9：相关推荐按真实页码只加载首批并增加标题级强去重；详情顶部定制按钮改走 startBrowser 独立评论页，绕开 BottomWebViewDialog 线程链。'
CHANGELOG = [
    '真机确认 Beta8 仍会在推荐超过约 10 部后出现重复；Beta9 不再依赖 session 状态，直接以阅读传入的真实 page 为准，推荐 page>1 硬返回空列表',
    '推荐首批去重从“ID + 标题/封面/作者组合签名”升级为 ID、规范化标题、规范化封面路径三层独立去重；同标题作品即使 API 返回不同 ID/作者/封面 host 也不会重复显示',
    '真机确认 Beta8 详情顶部定制按钮仍无法打开评论；Beta9 删除 Rhino function -> Activity.runOnUiThread -> SourceLoginJsExtensions.showBrowser 链',
    '详情顶部定制按钮直接调用阅读官方 java.startBrowser(url,title,html)，打开独立 WebViewActivity 评论中心；本地 HTML 自动接入 WebViewActivity 注入的 run() 桥，继续复用现有评论/楼中楼/点赞/回复模块',
    '顶部按钮改为直接从当前 book.bookUrl 提取漫画 ID，不再依赖额外详情请求；详情内原“查看评论”按钮及账号、目录、漫画正文、APP/Web 双线路保持不变'
]
TAGS = ['哔咔', '漫画', 'APP API', '网页线路', '评论', '相关推荐', '强去重', '定制按钮', 'startBrowser', '双线路']


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def dump_json(path, data):
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


source_path = ROOT / 'sources/comic/picacg/picacg-beta.json'
sources = json.loads(source_path.read_text(encoding='utf-8'))
assert isinstance(sources, list) and len(sources) == 1
src = sources[0]
assert src.get('bookSourceUrl') == SOURCE_ID
assert 'v1.0.0-beta8' in src.get('bookSourceComment', ''), 'Beta8 baseline required'
src['bookSourceName'] = DISPLAY_NAME
src['bookSourceComment'] = (
    '【v1.0.0-beta9 · 2026-08-26】\n'
    '哔咔漫画推荐终止 / 详情顶部评论入口专项修复测试版。\n\n'
    'Beta8 真机结果：\n'
    '• 相关推荐超过约 10 部后仍会出现一部重复作品，说明组合签名去重仍受作者/封面字段差异影响。\n'
    '• 详情页顶部定制按钮仍无法进入评论页，说明 Rhino runOnUiThread + SourceLoginJsExtensions.showBrowser 链在当前阅读环境仍不可靠。\n\n'
    'Beta9：\n'
    '• 相关推荐不再使用 session 状态；直接读取阅读发现页真实 page，page > 1 立即返回空列表，所以推荐接口只会取首批一次。\n'
    '• 首批推荐同时按漫画 ID、规范化标题、规范化封面路径独立去重；相同标题即使 ID/作者/封面域名不同也只保留第一项。\n'
    '• 顶部定制按钮完全绕开 BottomWebViewDialog：直接用 java.startBrowser(url,title,html) 打开独立评论页。\n'
    '• WebViewActivity 对本地 HTML 会自动注入 run() 桥；评论页面将该桥接到 picaRun，继续支持评论分页、楼中楼、点赞和回复。\n'
    '• 顶部按钮直接从当前 book.bookUrl 提取漫画 ID，不再先请求详情数据，减少失败点并加快打开速度。\n'
    '• 详情内原“查看评论”按钮、账号、目录、漫画图片正文和 APP/Web 双线路核心链冻结。\n\n'
    '本版仍为 Beta，等待真机确认。'
)

# 1) Recommendation helper: independent dedupe keys. Exact title duplicates are always dropped.
js = src['jsLib']
old_dedupe = '''function picaDedupeComicsStrong(list){
    list=list||[];var seenId={},seenSig={},out=[];
    function norm(v){return picaStr(v).toLowerCase().replace(/\\s+/g," ").trim();}
    function cleanUrl(v){v=picaStr(v);return v.split("?")[0].replace(/\\/+$/," ").trim().replace(/\\s+$/," ").trim();}
    for(var i=0;i<list.length;i++){
        var e=list[i]||{},id=picaStr(e._id||e.id||e.comicId),title=norm(e.title),author=norm(e.author||e.chineseTeam),cover="";
        try{cover=cleanUrl(picaMediaUrl(e.thumb||e.cover||{}));}catch(_c){}
        var sig=title+"|"+cover+"|"+author;
        if(id&&seenId[id])continue;
        if((title||cover)&&seenSig[sig])continue;
        if(id)seenId[id]=1;
        if(title||cover)seenSig[sig]=1;
        out.push(e);
    }
    return out;
}'''
# Beta8's cleanUrl is simpler; use an exact fallback if the defensive spelling above is not present.
old_dedupe_real = '''function picaDedupeComicsStrong(list){
    list=list||[];var seenId={},seenSig={},out=[];
    function norm(v){return picaStr(v).toLowerCase().replace(/\\s+/g," ").trim();}
    function cleanUrl(v){v=picaStr(v);return v.split("?")[0].replace(/\\/+$/ ,"");}
    for(var i=0;i<list.length;i++){
        var e=list[i]||{},id=picaStr(e._id||e.id||e.comicId),title=norm(e.title),author=norm(e.author||e.chineseTeam),cover="";
        try{cover=cleanUrl(picaMediaUrl(e.thumb||e.cover||{}));}catch(_c){}
        var sig=title+"|"+cover+"|"+author;
        if(id&&seenId[id])continue;
        if((title||cover)&&seenSig[sig])continue;
        if(id)seenId[id]=1;
        if(title||cover)seenSig[sig]=1;
        out.push(e);
    }
    return out;
}'''
# Normalize whitespace in the exact text replacement target by locating function boundaries instead of nested-brace regex.
start = js.find('function picaDedupeComicsStrong(list){')
assert start >= 0, 'picaDedupeComicsStrong start missing'
end_marker = '\n}\n'
end = js.find(end_marker, start)
assert end >= 0, 'picaDedupeComicsStrong end missing'
end += len(end_marker)
new_dedupe = '''function picaDedupeComicsStrong(list){
    list=list||[];var seenId={},seenTitle={},seenCover={},out=[];
    function norm(v){return picaStr(v).toLowerCase().replace(/[\\s\\u3000]+/g," ").trim();}
    function coverKey(v){
        v=picaStr(v).split("?")[0].replace(/\\/+$/,"").toLowerCase();
        return v.replace(/^https?:\\/\\/[^\\/]+/i,"");
    }
    for(var i=0;i<list.length;i++){
        var e=list[i]||{},id=norm(e._id||e.id||e.comicId),title=norm(e.title),cover="";
        try{cover=coverKey(picaMediaUrl(e.thumb||e.cover||{}));}catch(_c){}
        if(id&&seenId[id])continue;
        if(title&&seenTitle[title])continue;
        if(cover&&seenCover[cover])continue;
        if(id)seenId[id]=1;
        if(title)seenTitle[title]=1;
        if(cover)seenCover[cover]=1;
        out.push(e);
    }
    return out;
}
'''
js = js[:start] + new_dedupe + js[end:]

old_recommend_fn = '''function picaBookInfoRecommend(){var j=picaCtxJava(this),id=picaBookIdFromContext(this);if(!id){if(j)j.toast("无法识别当前漫画 ID");return true;}try{var sid=String(Date.now())+"_"+String(Math.floor(Math.random()*1000000));picaPutSetting(this,"pica_rec_loaded_session","");if(j&&j.open)j.open("explore",PICA_ROUTE_BASE+"/?legado=picacg_explore&type=recommendation&id="+encodeURIComponent(id)+"&sid="+encodeURIComponent(sid)+"&page={{page}}","相关推荐");}catch(e){if(j)j.longToast("打开相关推荐失败："+String(e&&e.message||e));}return true;}'''
new_recommend_fn = '''function picaBookInfoRecommend(){var j=picaCtxJava(this),id=picaBookIdFromContext(this);if(!id){if(j)j.toast("无法识别当前漫画 ID");return true;}try{if(j&&j.open)j.open("explore",PICA_ROUTE_BASE+"/?legado=picacg_explore&type=recommendation&id="+encodeURIComponent(id)+"&page={{page}}","相关推荐");}catch(e){if(j)j.longToast("打开相关推荐失败："+String(e&&e.message||e));}return true;}'''
assert old_recommend_fn in js, 'Beta8 picaBookInfoRecommend missing'
js = js.replace(old_recommend_fn, new_recommend_fn, 1)
src['jsLib'] = js

# 2) Recommendation Explore branch: trust Legado's actual page placeholder and hard-stop after page 1.
book_list = src['ruleExplore']['bookList']
start = book_list.find('else if(type==="recommendation"){')
assert start >= 0, 'recommendation branch start missing'
end = book_list.find('\n    else if(type==="category")', start)
assert end >= 0, 'recommendation branch end missing'
new_branch = '''else if(type==="recommendation"){
      if(p>1)return new Packages.java.util.ArrayList();
      var id=(u.match(/[?&]id=([^&]+)/)||[])[1]||"";
      try{id=decodeURIComponent(id);}catch(_ri){}
      if(id){var j=picaRequest(this,"comics/"+encodeURIComponent(id)+"/recommendation","GET");list=picaDedupeComicsStrong((j.data||{}).comics||[]);}
    }'''
book_list = book_list[:start] + new_branch + book_list[end:]
src['ruleExplore']['bookList'] = book_list

# 3) Detail top custom button: use startBrowser local-HTML path, which is explicitly designed for source JS on a background thread.
src['ruleContent']['callBackJs'] = r'''(function(){
  if(String(event||"")!=="clickCustomButton") return 0;
  try{
    var rawUrl="";
    try{rawUrl=String(book&&book.bookUrl||"");}catch(_u){}
    var m=rawUrl.match(/\/comic\/([^?#\/]+)/i),id=m&&m[1]?decodeURIComponent(m[1]):"";
    if(!id){try{java.longToast("无法从当前书籍地址识别漫画 ID，请刷新详情后重试");}catch(_id){}return true;}
    var title="哔咔评论",cover="";
    try{title=String(book&&book.name||title);cover=String(book&&book.coverUrl||"");}catch(_b){}
    var html=picaCommunityHtml(id,title,cover,0);
    html=String(html).replace("<script>","<script>try{if(!window.picaRun&&typeof run==='function')window.picaRun=run;}catch(_picaBridge){}");
    var url="https://picaapi.picacomic.com/comics/"+encodeURIComponent(id)+"/comments";
    try{java.log("[PICA-CUSTOM] startBrowser comments id="+id);}catch(_l){}
    java.startBrowser(url,"💬 "+title+" · 评论",html);
    return true;
  }catch(e){
    try{java.longToast("打开哔咔评论失败："+String(e&&e.message||e));}catch(_e){}
    return true;
  }
})()'''

source_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()

# 4) Static gates.
json.loads(source_path.read_text(encoding='utf-8'))
assert src['bookSourceName'] == DISPLAY_NAME
assert 'seenTitle' in src['jsLib'] and 'seenCover' in src['jsLib']
assert 'pica_rec_loaded_session' not in src['ruleExplore']['bookList']
assert 'if(p>1)return new Packages.java.util.ArrayList();' in src['ruleExplore']['bookList']
assert 'java.startBrowser(' in src['ruleContent']['callBackJs']
assert 'runOnUiThread' not in src['ruleContent']['callBackJs']
assert 'showBrowser(' not in src['ruleContent']['callBackJs']
for label, code in [('jsLib', src['jsLib']), ('explore', src['ruleExplore']['bookList']), ('callback', src['ruleContent']['callBackJs'])]:
    if code.startswith('<js>'):
        code = code[4:code.rfind('</js>')]
    with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as f:
        f.write(code)
        temp = f.name
    proc = subprocess.run(['node', '--check', temp], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode:
        raise RuntimeError(f'{label} syntax failed:\n{proc.stderr}')

# 5) Manifest + subscription metadata.
manifest = load_json('manifest.json')
entry = next(x for x in manifest['sources'] if x.get('id') == 'picacg')
entry.update({
    'name': DISPLAY_NAME,
    'channel': 'beta',
    'version': VERSION,
    'versionCode': VERSION_CODE,
    'updatedAt': NOW,
    'summary': SUMMARY,
    'tags': TAGS,
    'changelog': CHANGELOG,
    'sha256': sha256,
    'icon': ICON_URL,
})
manifest['updatedAt'] = NOW
dump_json('manifest.json', manifest)

for catalog_path in ['subscription/beta.json', 'subscription/comic.json']:
    catalog = load_json(catalog_path)
    item = next(x for x in catalog['items'] if x.get('id') == 'picacg')
    detail_url = item.get('detailUrl')
    item.update({
        'name': DISPLAY_NAME,
        'summary': SUMMARY,
        'icon': ICON_URL,
        'channel': 'beta',
        'version': VERSION,
        'updatedAt': DATE,
        'tags': TAGS,
        'changelog': CHANGELOG,
        'sourceUrl': f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
        'backupUrl': f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
        'importUrl': f'legado://import/bookSource?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
    })
    if detail_url is not None:
        item['detailUrl'] = detail_url
    catalog['updatedAt'] = NOW
    dump_json(catalog_path, catalog)

# 6) Current-state RSS detail (stable article identity retained).
detail_path = 'rss/data/details/beta/picacg.json'
detail = load_json(detail_path)
detail.update({
    'kind': 'source',
    'title': DISPLAY_NAME,
    'summary': SUMMARY,
    'badges': ['BETA', VERSION, '漫画源', '评论入口专项修复'],
    'sections': [
        {'title': 'Beta8 真机结论', 'text': '相关推荐超过约 10 部后仍会出现重复；详情页顶部定制按钮仍无法进入评论。两个问题均未判定为已解决。'},
        {'title': '推荐修复', 'text': 'Beta9 直接使用阅读发现页真实 page：相关推荐只允许 page=1 请求接口，page>1 立即返回空。首批再按漫画 ID、规范化标题、规范化封面路径三层独立去重。'},
        {'title': '顶部评论入口', 'text': '不再使用 runOnUiThread + SourceLoginJsExtensions.showBrowser。顶部定制按钮直接调用 java.startBrowser 打开独立评论 WebViewActivity，本地 HTML 自动接入阅读注入的 run() 桥。'},
        {'title': '评论能力', 'text': '评论中心继续复用现有哔咔评论模块：评论分页、最新/热门、楼中楼、点赞、回复与发表能力保持。详情内原“查看评论”按钮不改。'},
        {'title': '核心保护', 'text': '账号、签到、收藏、作品点赞、目录、漫画图片正文以及 APP/Web 双线路核心链保持 Beta8 基线。'},
        {'title': '发布状态', 'text': 'Beta / 测试版；等待真机确认“推荐不再重复”和“顶部按钮直开评论”。'},
        {'title': '唯一身份', 'text': SOURCE_ID},
    ],
    'sourceUrl': f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
    'backupUrl': f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
})
dump_json(detail_path, detail)

# 7) Replace only Picacg in Beta bundle.
bundle_path = ROOT / 'bundles/all-beta.json'
bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
replaced = 0

def replace_source(node):
    global replaced
    if isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, dict) and v.get('bookSourceUrl') == SOURCE_ID:
                node[i] = json.loads(json.dumps(src, ensure_ascii=False))
                replaced += 1
            else:
                replace_source(v)
    elif isinstance(node, dict):
        for k, v in list(node.items()):
            if isinstance(v, dict) and v.get('bookSourceUrl') == SOURCE_ID:
                node[k] = json.loads(json.dumps(src, ensure_ascii=False))
                replaced += 1
            else:
                replace_source(v)

replace_source(bundle)
assert replaced >= 1, 'Picacg not found in beta bundle'
bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# 8) Release log.
release_path = ROOT / 'docs/RELEASE_LOG.md'
release = release_path.read_text(encoding='utf-8')
release_entry = f'''## 2026-08-26 — Picacg {VERSION} recommendation hard-stop + startBrowser comment entry

Status: Beta/Test; awaiting user real-device confirmation.

Real-device finding from Beta8:

- 相关推荐超过约 10 部后仍会出现一部重复作品。
- 详情页顶部 customButton 仍无法进入评论页。

Changes:

- 推荐接口改为严格单页集合：直接使用阅读实际 page，`page > 1` 返回空，不再依赖 session 状态。
- 首批推荐按 ID、规范化标题、规范化封面路径三层独立去重；标题相同即视为重复，不再让作者/封面字段差异绕过去重。
- 顶部 customButton 删除 Rhino `runOnUiThread(function)` + `SourceLoginJsExtensions.showBrowser` 路径。
- 顶部按钮直接 `java.startBrowser(url,title,html)` 打开独立评论页；利用 WebViewActivity 本地 HTML 的官方 `run()` 注入桥继续运行评论/楼中楼/点赞/回复逻辑。
- 顶部按钮直接从 `book.bookUrl` 提取漫画 ID，不再为开评论先请求作品详情。
- 其它核心链冻结。
- Published SHA256: `{sha256}`.


'''
assert release.startswith('# RELEASE LOG\n')
release = '# RELEASE LOG\n\n' + release_entry + release[len('# RELEASE LOG\n\n'):]
release_path.write_text(release, encoding='utf-8')

# 9) Known issue update: record Beta8 failure so future work does not repeat the same thread workaround.
known_path = ROOT / 'docs/KNOWN_ISSUES.md'
known = known_path.read_text(encoding='utf-8')
issue_marker = '## Picacg — recommendation duplicate / detail custom button path (Beta8 incomplete)'
if issue_marker not in known:
    known += f'''\n\n{issue_marker}\n\nReal-device result on 2026-08-26:\n\n- Beta8 recommendation session de-dup still allowed a repeated work after roughly ten recommendations.\n- Beta8 detail customButton using `Activity.runOnUiThread(function)` + `SourceLoginJsExtensions.showBrowser` still did not open the comment page.\n\nEngineering conclusion for Beta9:\n\n- Treat `/comics/<id>/recommendation` as a fixed one-page recommendation set in Legado: use the actual `page` parameter and return empty for `page > 1`.\n- De-duplicate the first set by independent semantic keys, especially normalized title, instead of one composite signature.\n- Do not retry the Rhino-function-to-`runOnUiThread` BottomWebViewDialog path for this button. Use `java.startBrowser(url,title,html)` so WebViewActivity owns UI-thread creation and injects the official local-HTML `run()` bridge.\n\nStatus: Beta9 published for real-device verification.\n'''
    known_path.write_text(known, encoding='utf-8')

# Final metadata parse gates.
for p in ['manifest.json', 'subscription/beta.json', 'subscription/comic.json', 'bundles/all-beta.json', detail_path]:
    json.loads((ROOT / p).read_text(encoding='utf-8'))

print(json.dumps({
    'version': VERSION,
    'name': DISPLAY_NAME,
    'sha256': sha256,
    'bundle_replacements': replaced,
    'updatedAt': NOW,
}, ensure_ascii=False, indent=2))
