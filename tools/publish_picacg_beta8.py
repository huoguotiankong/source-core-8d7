import json
import hashlib
import pathlib
import re
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
VERSION = '1.0.0-beta8'
VERSION_CODE = 10008
DISPLAY_NAME = '◈ 哔咔漫画'
SOURCE_ID = 'https://sc8d7.invalid/legado/picacg-8d7'
ICON_URL = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/assets/source-core-source-icon.svg'
DATE = '2026-08-26'
NOW = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
SUMMARY = 'Beta8：修复详情页顶部定制按钮无法打开评论；相关推荐改为单会话单次加载并按 ID/标题封面双重去重；启用阅读源统一品牌标识。'
CHANGELOG = [
    '修复详情页顶部定制按钮：SourceCallBack 在 IO 线程执行，回调改为显式切回 Activity 主线程后再调用 showBrowser 打开评论中心',
    '相关推荐每次打开生成独立 session id；同一 session 只允许推荐接口返回一次，阻止 ExploreShowActivity 自动翻页重复追加同一批结果',
    '推荐结果按漫画 ID 与“标题 + 封面 + 作者”签名双重去重，处理 API 返回不同 ID 但视觉内容相同的重复项',
    '阅读源统一品牌标识启用：书源名改为「◈ 哔咔漫画」，仓库新增专属 source-core 图标资产',
    '详情互动区、作品数据、账号、评论、楼中楼、目录、漫画图片正文和 APP/Web 双线路核心链保持不变'
]
TAGS = ['哔咔', '漫画', 'APP API', '网页线路', '评论', '相关推荐', '去重', '定制按钮', '品牌图标', '双线路']


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def dump_json(path, data):
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


# 0) project source icon: open-book wings + diamond core, designed for small-size readability.
icon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="g" x1="80" y1="60" x2="440" y2="452" gradientUnits="userSpaceOnUse">
      <stop stop-color="#5B7CFA"/>
      <stop offset="1" stop-color="#7C4DFF"/>
    </linearGradient>
  </defs>
  <rect x="24" y="24" width="464" height="464" rx="122" fill="url(#g)"/>
  <path d="M104 164c54-16 102 2 152 47v159c-49-39-97-53-152-34V164Z" fill="#fff" fill-opacity=".96"/>
  <path d="M408 164c-54-16-102 2-152 47v159c49-39 97-53 152-34V164Z" fill="#fff" fill-opacity=".96"/>
  <path d="M256 191 311 246 256 301 201 246 256 191Z" fill="#5F57F5" stroke="#fff" stroke-width="14"/>
  <circle cx="256" cy="246" r="14" fill="#fff"/>
  <path d="M140 193c31-2 58 8 84 30M372 193c-31-2-58 8-84 30" fill="none" stroke="#DCE3FF" stroke-width="13" stroke-linecap="round"/>
</svg>\n'''
asset = ROOT / 'assets/source-core-source-icon.svg'
asset.write_text(icon_svg, encoding='utf-8')

# 1) source JSON
source_path = ROOT / 'sources/comic/picacg/picacg-beta.json'
sources = json.loads(source_path.read_text(encoding='utf-8'))
assert isinstance(sources, list) and len(sources) == 1
src = sources[0]
assert src.get('bookSourceUrl') == SOURCE_ID
src['bookSourceName'] = DISPLAY_NAME
src['bookSourceComment'] = (
    '【v1.0.0-beta8 · 2026-08-26】\n'
    '哔咔漫画定制按钮 / 推荐去重修复测试版。\n\n'
    'Beta8：\n'
    '• 修复详情页顶部定制按钮：阅读 SourceCallBack 会在 IO 线程执行，而 SourceLoginJsExtensions.showBrowser 不会自动切主线程；本版在回调里显式通过当前 Activity.runOnUiThread 后打开评论中心。\n'
    '• 相关推荐改为“单次推荐集合”：每次打开生成独立 session，同一 session 第一次请求返回推荐，后续自动翻页请求直接返回空，防止同一批结果不断追加。\n'
    '• 推荐列表同时按漫画 ID 和“标题 + 封面 + 作者”签名去重，过滤 API 中不同 ID 的重复作品。\n'
    '• 统一阅读源品牌标识：本源名称改为「◈ 哔咔漫画」，◈ 作为 source-core 阅读源的文字标识，仓库同时增加专属图形图标。\n'
    '• 漫画正文原生 MangaMenu 仍不支持 customButton；详情页顶部定制按钮本版专项修复。\n'
    '• 账号、评论、楼中楼、目录、漫画图片正文和 APP/Web 双线路核心链冻结。\n\n'
    '本版仍为 Beta，等待真机确认。'
)

js = src['jsLib']

# Strong recommendation de-dupe helper. Different ids with same visual work are treated as duplicates.
if 'function picaDedupeComicsStrong' not in js:
    anchor = 'function picaListToJava(list){var out=new Packages.java.util.ArrayList();list=list||[];for(var i=0;i<list.length;i++)out.add(picaExploreItem(list[i]));return out;}'
    assert anchor in js, 'picaListToJava anchor missing'
    helper = anchor + '''\nfunction picaDedupeComicsStrong(list){
    list=list||[];var seenId={},seenSig={},out=[];
    function norm(v){return picaStr(v).toLowerCase().replace(/\\s+/g," ").trim();}
    function cleanUrl(v){v=picaStr(v);return v.split("?")[0].replace(/\\/+$/,"");}
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
    js = js.replace(anchor, helper, 1)

# Recommendation launcher: sessionized. Keep {{page}} so Legado can maintain its page state, but backend list is returned once per session.
pat = re.compile(r'function picaBookInfoRecommend\(\)\{.*?return true;\}', re.S)
m = pat.search(js)
assert m, 'picaBookInfoRecommend missing'
new_recommend = '''function picaBookInfoRecommend(){var j=picaCtxJava(this),id=picaBookIdFromContext(this);if(!id){if(j)j.toast("无法识别当前漫画 ID");return true;}try{var sid=String(Date.now())+"_"+String(Math.floor(Math.random()*1000000));picaPutSetting(this,"pica_rec_loaded_session","");if(j&&j.open)j.open("explore",PICA_ROUTE_BASE+"/?legado=picacg_explore&type=recommendation&id="+encodeURIComponent(id)+"&sid="+encodeURIComponent(sid)+"&page={{page}}","相关推荐");}catch(e){if(j)j.longToast("打开相关推荐失败："+String(e&&e.message||e));}return true;}'''
js = js[:m.start()] + new_recommend + js[m.end():]
src['jsLib'] = js

# Recommendation rule: the endpoint is a fixed recommendation set, not a paginated feed.
book_list = src['ruleExplore']['bookList']
old_branch = re.compile(r'else if\(type==="recommendation"\)\{.*?\}\n    else if\(type==="category"\)', re.S)
m = old_branch.search(book_list)
assert m, 'recommendation explore branch missing'
new_branch = '''else if(type==="recommendation"){
      var id=(u.match(/[?&]id=([^&]+)/)||[])[1]||"",sid=(u.match(/[?&]sid=([^&]+)/)||[])[1]||"";
      try{id=decodeURIComponent(id);}catch(_ri){}try{sid=decodeURIComponent(sid);}catch(_rs){}
      if(!sid)sid="legacy_"+id;
      var loaded=picaGetSetting(this,"pica_rec_loaded_session","");
      if(loaded===sid)return new Packages.java.util.ArrayList();
      picaPutSetting(this,"pica_rec_loaded_session",sid);
      if(id){var j=picaRequest(this,"comics/"+encodeURIComponent(id)+"/recommendation","GET");list=picaDedupeComicsStrong((j.data||{}).comics||[]);}
    }
    else if(type==="category")'''
book_list = book_list[:m.start()] + new_branch + book_list[m.end():]
src['ruleExplore']['bookList'] = book_list

# 2) Top BookInfo custom button callback.
# SourceCallBack executes this on Dispatchers.IO and passes SourceLoginJsExtensions as java.
# That class overrides showBrowser without runOnUiThread, so we build/fetch on IO and marshal only the dialog-open call to main.
src['ruleContent']['callBackJs'] = r'''(function(){
  if(String(event||"")!=="clickCustomButton") return 0;
  try{
    var ctx={java:java,source:source,book:book,chapter:chapter};
    var id=picaStr(picaBookIdFromContext(ctx));
    if(!id){try{java.longToast("无法识别当前漫画 ID，请刷新详情后重试");}catch(_id){}return true;}
    var title="",cover="",total=0;
    try{if(book){title=picaStr(book.name||book.title);cover=picaStr(book.coverUrl||book.cover);if(book.getVariable){title=title||picaStr(book.getVariable("pica_title"));cover=cover||picaStr(book.getVariable("pica_cover"));}}}catch(_b){}
    try{var c=picaComicInfo(ctx,id);title=title||picaStr(c.title);cover=cover||picaMediaUrl(c.thumb);total=picaNum(c.commentsCount!==undefined?c.commentsCount:c.totalComments,0);picaRememberBook(ctx,id,title,cover);}catch(_c){}
    var html=picaCommunityHtml(id,title||"哔咔评论",cover,total);
    var url="https://picaapi.picacomic.com/comics/"+encodeURIComponent(id)+"/comments";
    var preload="window.java=java;window.cache=cache;window.source=source;window.picaRun=run;window.picaCommentPage=true;";
    var config=JSON.stringify({state:4,isHideable:true,heightPercentage:0.94,widthPercentage:1.0,dismissOnTouchOutside:true,skipCollapsed:true,expandedCornersRadius:20,isGestureInsetBottomIgnored:true,hardwareAccelerated:true,webViewInitialScale:100});
    var act=null;try{act=java.getActivityRef().get();}catch(_a){}
    if(act){
      act.runOnUiThread(function(){try{java.showBrowser(url,html,preload,config);}catch(e){try{java.longToast("评论页打开失败："+String(e&&e.message||e));}catch(_t){}}});
    }else{
      try{java.showBrowser(url,html,preload,config);}catch(e2){try{java.longToast("评论页打开失败："+String(e2&&e2.message||e2));}catch(_t2){}}
    }
    return true;
  }catch(e){
    try{java.longToast("打开哔咔评论失败："+String(e&&e.message||e));}catch(_e){}
    return true;
  }
})()'''

source_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()

# 3) Static smoke checks.
json.loads(source_path.read_text(encoding='utf-8'))
assert src['bookSourceName'] == DISPLAY_NAME
assert 'picaDedupeComicsStrong' in src['jsLib']
assert 'pica_rec_loaded_session' in src['ruleExplore']['bookList']
assert 'runOnUiThread' in src['ruleContent']['callBackJs']
for label, code in [('jsLib', src['jsLib']), ('explore', src['ruleExplore']['bookList']), ('callback', src['ruleContent']['callBackJs'])]:
    if code.startswith('<js>'):
        code=code[4:code.rfind('</js>')]
    with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as f:
        f.write(code)
        temp=f.name
    subprocess.run(['node','--check',temp],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

# 4) Metadata.
manifest = load_json('manifest.json')
entry = next(x for x in manifest['sources'] if x.get('id') == 'picacg')
entry.update({'name':DISPLAY_NAME,'channel':'beta','version':VERSION,'versionCode':VERSION_CODE,'updatedAt':NOW,'summary':SUMMARY,'tags':TAGS,'changelog':CHANGELOG,'sha256':sha256,'icon':ICON_URL})
manifest['updatedAt']=NOW
dump_json('manifest.json',manifest)

for catalog_path in ['subscription/beta.json','subscription/comic.json']:
    catalog=load_json(catalog_path)
    item=next(x for x in catalog['items'] if x.get('id')=='picacg')
    detail_url=item.get('detailUrl')
    item.update({'name':DISPLAY_NAME,'summary':SUMMARY,'icon':ICON_URL,'channel':'beta','version':VERSION,'updatedAt':DATE,'tags':TAGS,'changelog':CHANGELOG,
        'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
        'backupUrl':f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
        'importUrl':f'legado://import/bookSource?src=https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}'})
    if detail_url is not None:item['detailUrl']=detail_url
    catalog['updatedAt']=NOW
    dump_json(catalog_path,catalog)

# 5) Current-state repository detail.
detail=load_json('rss/data/details/beta/picacg.json')
detail.update({'title':DISPLAY_NAME,'summary':SUMMARY,'icon':ICON_URL,'badges':['BETA',VERSION,'漫画源','评论/推荐修复'],
    'sections':[
        {'title':'详情定制按钮','text':'已定位真实线程差异：BookInfo 顶部 customButton 经 SourceCallBack 在 IO 线程执行，而 SourceLoginJsExtensions.showBrowser 不负责切回主线程。本版先完成评论数据/HTML准备，再通过当前 Activity.runOnUiThread 打开原评论 BottomWebView。'},
        {'title':'相关推荐','text':'哔咔 recommendation 是一次性推荐集合，不按阅读发现页的页码分页。本版每次打开生成独立 session，同一 session 只返回一次；同时按 ID 与标题/封面/作者签名双重去重。'},
        {'title':'品牌标识','text':'source-core 阅读源统一使用「◈」作为文字前缀，并配套独立开卷 + 菱形核心图标。后续新写阅读源默认使用同一品牌标识，版本/线路等信息继续放说明而不塞进名称。'},
        {'title':'核心保护','text':'详情互动区、作品数据、作者/汉化组/标签、账号、签到、收藏、点赞、评论楼中楼、目录、漫画图片正文及 APP/Web 双线路保持原逻辑。'},
        {'title':'发布状态','text':'Beta / 测试版；等待真机确认。'},
        {'title':'唯一身份','text':SOURCE_ID}],
    'sourceUrl':f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}',
    'backupUrl':f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg-beta.json?v={VERSION_CODE}'})
dump_json('rss/data/details/beta/picacg.json',detail)

# 6) Beta bundle replace Picacg only.
bundle_path=ROOT/'bundles/all-beta.json'
bundle=json.loads(bundle_path.read_text(encoding='utf-8'))
replaced=0
def replace_source(node):
    global replaced
    if isinstance(node,list):
        for i,v in enumerate(node):
            if isinstance(v,dict) and v.get('bookSourceUrl')==SOURCE_ID:
                node[i]=json.loads(json.dumps(src,ensure_ascii=False));replaced+=1
            else:replace_source(v)
    elif isinstance(node,dict):
        for k,v in list(node.items()):
            if isinstance(v,dict) and v.get('bookSourceUrl')==SOURCE_ID:
                node[k]=json.loads(json.dumps(src,ensure_ascii=False));replaced+=1
            else:replace_source(v)
replace_source(bundle)
assert replaced>=1,'Picacg not found in beta bundle'
bundle_path.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# 7) Release log.
release_path=ROOT/'docs/RELEASE_LOG.md'
release=release_path.read_text(encoding='utf-8')
assert release.startswith('# RELEASE LOG\n')
entry_text=f'''\n## 2026-08-26 — Picacg {VERSION} custom-button thread fix + recommendation session de-dup\n\nStatus: Beta/Test; awaiting user real-device confirmation.\n\nChanges:\n\n- 详情页顶部 customButton 回调按 SourceCallBack 的 IO 线程模型修复：数据准备在后台完成，showBrowser 显式切回 Activity 主线程\n- 相关推荐每次打开生成 session id，同一 session 仅返回一次推荐集合，阻止阅读发现页自动翻页重复追加\n- 推荐结果同时按漫画 ID 与“标题 + 封面 + 作者”签名去重\n- 书源显示名改为「{DISPLAY_NAME}」，仓库新增 source-core 专属阅读源 SVG 图标\n- 漫画正文 MangaMenu 本身仍没有 customButton；本版只修复详情页顶部已有定制按钮\n- 其它核心链冻结\n- Published SHA256: `{sha256}`.\n\n'''
release_path.write_text('# RELEASE LOG\n'+entry_text+release[len('# RELEASE LOG\n'):],encoding='utf-8')

# 8) Development naming rule: one shared project mark, not per-source emoji roulette.
rules_path=ROOT/'docs/DEVELOPMENT_RULES.md'
rules=rules_path.read_text(encoding='utf-8')
old='''`bookSourceName` / RSS source display names should be short and recognizable. Default format:\n\n`<one distinctive icon> <source/platform name>`\n\nExamples: `🍥 哔咔漫画`, `🌈 起点增强`.'''
new='''`bookSourceName` / RSS source display names should be short and recognizable. New source-core sources use the shared project brand mark by default:\n\n`◈ <source/platform name>`\n\nExample: `◈ 哔咔漫画`. The matching repository artwork is `assets/source-core-source-icon.svg`.'''
if old in rules:rules=rules.replace(old,new,1)
extra='''\n- Do not pick a different decorative emoji for each newly written source. Use the shared `◈` source-core mark unless the user explicitly requests another public identity.\n- Existing mature sources are not bulk-renamed only for branding; adopt the shared mark when they are deliberately renamed or newly rebuilt, so stable user-facing names are not churned unnecessarily.'''
needle='- When renaming an existing source, preserve its stable `bookSourceUrl` identity so updates continue in place.'
if extra.strip() not in rules:
    rules=rules.replace(needle,needle+extra,1)
rules_path.write_text(rules.rstrip()+'\n',encoding='utf-8')

# 9) Known issue: detail callback thread distinction.
issues_path=ROOT/'docs/KNOWN_ISSUES.md'
issues=issues_path.read_text(encoding='utf-8')
section='''\n## Picacg BookInfo customButton used the wrong browser thread path — Beta8 fix\n\nReal-device Beta6/Beta7: the custom button was visible on BookInfoActivity but tapping it did not open the comment UI, while the inline “查看评论” button worked.\n\nRoot cause from current Legado source:\n\n- BookInfoActivity dispatches `CLICK_CUSTOM_BUTTON` through `SourceCallBack.callBackBtn`.\n- `SourceCallBack.callBackBtn` executes `ruleContent.callBackJs` on `Dispatchers.IO` and supplies `SourceLoginJsExtensions` as `java`.\n- generic `JsExtensions.showBrowser` marshals to `runOnUiThread`, but `SourceLoginJsExtensions.showBrowser` overrides it and directly calls `showDialogFragment`.\n- therefore a callback that directly calls `java.showBrowser` can fail from the IO callback path even though the same comment opener works from normal rule/UI execution.\n\nBeta8 rule: prepare comment data in the callback background thread, then call the existing BottomWebView opener through the current Activity's `runOnUiThread`. Do not guess alternate event names; the event is confirmed as `clickCustomButton`.\n\nRecommendation note: Picacg `/recommendation` is treated as a one-shot recommendation set, not a Legado-paginated feed. Each opened recommendation session may load that endpoint once, then must return empty on subsequent Explore pages.\n\n'''
if '## Picacg BookInfo customButton used the wrong browser thread path — Beta8 fix' not in issues:
    issues=issues.rstrip()+'\n'+section
issues_path.write_text(issues.rstrip()+'\n',encoding='utf-8')

# final JSON validation
for p in ['sources/comic/picacg/picacg-beta.json','manifest.json','subscription/beta.json','subscription/comic.json','rss/data/details/beta/picacg.json','bundles/all-beta.json']:
    json.loads((ROOT/p).read_text(encoding='utf-8'))
print(json.dumps({'version':VERSION,'name':DISPLAY_NAME,'sha256':sha256,'bundle_replacements':replaced,'updatedAt':NOW},ensure_ascii=False,indent=2))
