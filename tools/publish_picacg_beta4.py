import json, hashlib, pathlib
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
target = ROOT/'sources/comic/picacg/picacg-beta.json'
data = json.loads(target.read_text(encoding='utf-8'))
if not isinstance(data, list) or len(data) != 1:
    raise SystemExit('Picacg source must contain exactly one source object')
src = data[0]
if src.get('bookSourceUrl') != 'https://sc8d7.invalid/legado/picacg-8d7':
    raise SystemExit('Picacg identity mismatch')
if 'v1.0.0-beta3' not in src.get('bookSourceComment',''):
    raise SystemExit('Beta3 baseline not found')

# 1) Runtime self-heal for Archive/Legado reader custom button.
js = src['jsLib']
anchor = '''function picaPutSetting(ctx,key,val){var s=picaCtxSource(ctx);try{if(s&&s.put)s.put(key,String(val));}catch(e){}return val;}\n'''
helper = '''function picaPutSetting(ctx,key,val){var s=picaCtxSource(ctx);try{if(s&&s.put)s.put(key,String(val));}catch(e){}return val;}\nfunction picaEnsureReaderFeatures(ctx){\n    var s=picaCtxSource(ctx);\n    try{if(s){s.customButton=true;s.eventListener=true;}}catch(e){}\n    return true;\n}\n'''
if anchor not in js:
    raise SystemExit('picaPutSetting anchor missing')
src['jsLib'] = js.replace(anchor, helper, 1)

# 2) Enhance quick-link helper.
js = src['jsLib']
old = '''function picaBookInfoOpenTag(label,kind){\n    var j=picaCtxJava(this),t=picaStr(label).trim();if(!t)return true;\n    kind=picaStr(kind||"tag");\n    try{if(j&&j.open)j.open("explore",PICA_ROUTE_BASE+"/?legado=picacg_explore&type=tag&tag="+encodeURIComponent(t)+"&kind="+encodeURIComponent(kind)+"&s=dd&page={{page}}","🏷 "+t);}catch(e){if(j)j.longToast("打开标签失败："+String(e&&e.message||e));}\n    return true;\n}\n'''
new = '''function picaBookInfoOpenTag(label,kind){\n    var j=picaCtxJava(this),t=picaStr(label).trim();if(!t)return true;\n    kind=picaStr(kind||"tag");\n    var icon=kind==="category"?"📂 ":(kind==="author"?"✍️ ":(kind==="team"?"🈶 ":"🏷 "));\n    try{if(j&&j.open)j.open("explore",PICA_ROUTE_BASE+"/?legado=picacg_explore&type=tag&tag="+encodeURIComponent(t)+"&kind="+encodeURIComponent(kind)+"&s=dd&page={{page}}",icon+t);}catch(e){if(j)j.longToast("打开关联页失败："+String(e&&e.message||e));}\n    return true;\n}\n'''
if old not in js:
    raise SystemExit('tag helper baseline missing')
src['jsLib'] = js.replace(old,new,1)

# 3) Detail init.
init = src['ruleBookInfo']['init']
old = '''(function(){\n  var id=picaBookId(String(baseUrl||""));if(!id)return "";\n  try{var c=picaComicInfo(this,id),cover=picaMediaUrl(c.thumb),cats=(c.categories||[]),tags=(c.tags||[]),likes=Number(c.likesCount!==undefined?c.likesCount:c.totalLikes||0),views=Number(c.viewsCount!==undefined?c.viewsCount:c.totalViews||0),comments=Number(c.commentsCount!==undefined?c.commentsCount:c.totalComments||0);'''
new = '''(function(){\n  picaEnsureReaderFeatures(this);\n  var id=picaBookId(String(baseUrl||""));if(!id)return "";\n  try{var c=picaComicInfo(this,id),cover=picaMediaUrl(c.thumb),cats=(c.categories||[]),tags=(c.tags||[]),likes=Number(c.likesCount!==undefined?c.likesCount:c.totalLikes||0),views=Number(c.viewsCount!==undefined?c.viewsCount:c.totalViews||0),comments=Number(c.commentsCount!==undefined?c.commentsCount:c.totalComments||0),creator=c._creator||c.creator||{};'''
if old not in init:
    raise SystemExit('book init opening baseline missing')
init = init.replace(old,new,1)
old2 = 'java.put("pica_kind",cats.concat(tags).join(" · ")+(c.finished?" · 完结":" · 连载"));java.put("pica_categories",JSON.stringify(cats));java.put("pica_tags",JSON.stringify(tags));java.put("pica_team",String(c.chineseTeam||""));java.put("pica_status",c.finished?"已完结":"连载中");java.put("pica_bookid",id);'
new2 = 'java.put("pica_kind",cats.join(" · ")+(c.finished?" · 完结":" · 连载"));java.put("pica_categories",JSON.stringify(cats));java.put("pica_tags",JSON.stringify(tags));java.put("pica_team",String(c.chineseTeam||""));java.put("pica_status",c.finished?"已完结":"连载中");java.put("pica_creator",String(creator.name||creator.username||""));java.put("pica_created",String(c.created_at||c.createdAt||""));java.put("pica_eps",String(Number(c.epsCount||0)));java.put("pica_pages",String(Number(c.pagesCount||0)));java.put("pica_download",c.allowDownload===false?"不允许":"允许");java.put("pica_commentable",c.allowComment===false?"不允许":"允许");java.put("pica_bookid",id);'
if old2 not in init:
    raise SystemExit('book init metadata baseline missing')
src['ruleBookInfo']['init'] = init.replace(old2,new2,1)

# 4) Venera-inspired detail.
src['ruleBookInfo']['intro'] = r'''<js>
var desc=String(java.get("pica_intro")||""),stats=String(java.get("pica_stats")||"");
var cats=picaJson(java.get("pica_categories"),[]),tags=picaJson(java.get("pica_tags"),[]);
var author=String(java.get("pica_author")||""),team=String(java.get("pica_team")||""),status=String(java.get("pica_status")||"");
var creator=String(java.get("pica_creator")||""),created=String(java.get("pica_created")||""),updated=String(java.get("pica_updated")||"");
var eps=String(java.get("pica_eps")||"0"),pages=String(java.get("pica_pages")||"0"),downloadable=String(java.get("pica_download")||""),commentable=String(java.get("pica_commentable")||"");
function dt(v){v=String(v||"");return v?v.replace("T"," ").replace(/\.\d+Z?$/," ").replace(/Z$/," ").trim().slice(0,16):"";}
function chip(t,k,icon){t=String(t||"").trim();if(!t)return "";icon=icon||"";return "<button>"+icon+picaEsc(t)+"@onclick:picaBookInfoOpenTag.call(this,"+JSON.stringify(t)+","+JSON.stringify(k)+")</button> ";}
function row(label,value){value=String(value||"").trim();return value?"<br><b>"+picaEsc(label)+"</b>　"+picaEsc(value):"";}
var html="<button>💬 哔咔评论@onclick:picaBookInfoOpenComments.call(this)</button> "
        +"<button>♥ 点赞@onclick:picaBookInfoLike.call(this)</button> "
        +"<button>⭐ 收藏@onclick:picaBookInfoFavourite.call(this)</button> "
        +"<button>🧭 相关推荐@onclick:picaBookInfoRecommend.call(this)</button>";
html+="<br><br><b>📊 作品数据</b><br>"+picaEsc(stats);
if(status)html+="<br>"+picaEsc(status)+" · "+picaEsc(eps)+"话 / "+picaEsc(pages)+"页";
html+="<br><br><b>📝 描述</b><br>"+(desc?picaEsc(desc).replace(/\r\n|\r|\n/g,"<br>"):"暂无描述");
html+="<br><br><b>ℹ️ 信息</b>";
if(author)html+="<br><b>作者</b>　"+chip(author,"author","✍️ ");
if(team)html+="<br><b>汉化组</b>　"+chip(team,"team","🈶 ");
if(creator)html+=row("上传者",creator);
var cseen={},cc="",i,t;
for(i=0;i<cats.length;i++){t=String(cats[i]||"").trim();if(t&&!cseen[t]){cseen[t]=1;cc+=chip(t,"category","");}}
if(cc)html+="<br><b>分类</b>　"+cc;
var ts="",tseen={};
for(i=0;i<tags.length;i++){t=String(tags[i]||"").trim();if(t&&!tseen[t]){tseen[t]=1;ts+=chip(t,"tag","# ");}}
if(ts)html+="<br><b>标签</b>　"+ts;
html+=row("更新时间",dt(updated));
html+=row("上传时间",dt(created));
html+=row("页数",pages);
html+=row("下载",downloadable);
html+=row("评论",commentable);
"<usehtml>"+html+"</usehtml>";
</js>'''

# 5) Tag route.
exp = src['ruleExplore']['bookList']
old = '''        if(tk==="category"){var jt=picaRequest(this,"comics?page="+p+"&c="+encodeURIComponent(tg)+"&s="+encodeURIComponent(srt),"GET");docs=((jt.data||{}).comics||{}).docs||[];}\n        else{\n          try{var jt=picaRequest(this,"comics?page="+p+"&c="+encodeURIComponent(tg)+"&s="+encodeURIComponent(srt),"GET");docs=((jt.data||{}).comics||{}).docs||[];}catch(_tc){}\n          if(!docs.length){var js=picaRequest(this,"comics/advanced-search?page="+p,"POST",{keyword:tg,sort:srt});docs=((js.data||{}).comics||{}).docs||[];}\n        }'''
new = '''        if(tk==="category"){var jt=picaRequest(this,"comics?page="+p+"&c="+encodeURIComponent(tg)+"&s="+encodeURIComponent(srt),"GET");docs=((jt.data||{}).comics||{}).docs||[];}\n        else if(tk==="author"||tk==="team"){var js=picaRequest(this,"comics/advanced-search?page="+p,"POST",{keyword:tg,sort:srt});docs=((js.data||{}).comics||{}).docs||[];}\n        else{\n          try{var jt=picaRequest(this,"comics?page="+p+"&c="+encodeURIComponent(tg)+"&s="+encodeURIComponent(srt),"GET");docs=((jt.data||{}).comics||{}).docs||[];}catch(_tc){}\n          if(!docs.length){var js=picaRequest(this,"comics/advanced-search?page="+p,"POST",{keyword:tg,sort:srt});docs=((js.data||{}).comics||{}).docs||[];}\n        }'''
if old not in exp:
    raise SystemExit('tag route baseline missing')
src['ruleExplore']['bookList'] = exp.replace(old,new,1)

# 6) Force reader feature flag before catalog/content execution too.
toc = src['ruleToc']['chapterList']
old = '(function(){var id=picaBookId(String(baseUrl||""))||picaBookIdFromContext(this);'
new = '(function(){picaEnsureReaderFeatures(this);var id=picaBookId(String(baseUrl||""))||picaBookIdFromContext(this);'
if old not in toc:
    raise SystemExit('toc baseline missing')
src['ruleToc']['chapterList'] = toc.replace(old,new,1)

content = src['ruleContent']['content']
old = '(function(){var u=String(baseUrl||""),bm=u.match(/[?&]book=([^&]+)/),'
new = '(function(){picaEnsureReaderFeatures(this);var u=String(baseUrl||""),bm=u.match(/[?&]book=([^&]+)/),'
if old not in content:
    raise SystemExit('content baseline missing')
src['ruleContent']['content'] = content.replace(old,new,1)

src['customButton'] = True
src['eventListener'] = True

src['bookSourceComment'] = '''【v1.0.0-beta4 · 2026-08-26】
哔咔漫画 APP/网页双线路增强测试版。

Beta4：
• 正文页定制按钮专项修复：根据阅读/Archive 的 ReadMenu 实现，按钮显示直接取决于当前 BookSource.customButton。除 JSON 顶层继续声明 true 外，在详情、目录、正文运行时再次将 customButton/eventListener 写回当前书源对象，避免已导入书源对象未携带新标志时正文顶部按钮仍隐藏。
• 详情页继续按 Venera 哔咔页面思路增强，改成“作品数据 / 描述 / 信息”分区。
• 信息区新增作者、汉化组、上传者、分类、标签、更新时间、上传时间、页数、下载/评论能力。
• 作者、汉化组、分类、标签均支持点击进入对应列表/搜索页。
• 原生 kind 行只保留主要分类+连载状态，完整标签放到信息区，减少详情顶部过长截断。
• 评论、点赞、收藏、相关推荐、正文图片和 APP/Web 双线路核心链保持不变。

本版仍为 Beta，重点验证正文顶部定制按钮是否出现。'''

src['variableComment'] = '''本源默认不需要设置书籍变量。
线路与清晰度请在“书源登录”页面设置。

正文阅读菜单顶部：定制按钮用于打开当前漫画的哔咔评论中心。
详情页：作者、汉化组、分类、标签均可点击进入对应内容页。'''

assert src['customButton'] is True and src['eventListener'] is True
assert 'picaEnsureReaderFeatures(this)' in src['ruleBookInfo']['init']
assert 'picaEnsureReaderFeatures(this)' in src['ruleToc']['chapterList']
assert 'picaEnsureReaderFeatures(this)' in src['ruleContent']['content']
assert 'type==="tag"' in src['ruleExplore']['bookList']
assert 'pica_creator' in src['ruleBookInfo']['init']

now_dt = datetime.now(timezone(timedelta(hours=8)))
now = now_dt.isoformat(timespec='seconds')
day = now_dt.date().isoformat()
src['lastUpdateTime'] = int(now_dt.timestamp()*1000)
raw = (json.dumps(data, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
json.loads(raw.decode('utf-8'))
target.write_bytes(raw)
sha = hashlib.sha256(raw).hexdigest()

version='1.0.0-beta4'; versionCode=10004
summary='Beta4：正文阅读菜单定制按钮显示专项自愈；详情页按 Venera 思路扩展为作品数据/描述/信息分区，并增强作者、汉化组、分类、标签跳转。'
tags=['哔咔','漫画','APP API','网页线路','正文定制按钮','评论','详情增强','作者','汉化组','标签','上传者','双线路']
changes=[
    '根据 Legado/Archive ReadMenu 机制，详情/目录/正文执行时再次确保当前 BookSource.customButton 与 eventListener 为 true',
    '详情页重构为作品数据、描述、信息三个分区，降低顶部信息拥挤',
    '新增上传者、上传时间、页数、允许下载、允许评论等元数据展示',
    '作者、汉化组、分类、标签新增点击跳转；分类精确过滤，作者/汉化组走高级搜索',
    '原生 kind 只保留主要分类与连载状态，完整 tags 下沉到信息区',
    '评论中心、点赞/收藏、相关推荐、目录、正文图片及 APP/Web 请求核心链冻结'
]
raw_url='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json'
backup='https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg-beta.json'
detail_path='rss/data/details/beta/picacg.json'
detail_url='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/'+detail_path

mp=ROOT/'manifest.json'; manifest=json.loads(mp.read_text(encoding='utf-8')); manifest['updatedAt']=now
for x in manifest.get('sources',[]):
    if x.get('id')=='picacg':
        x.update(version=version,versionCode=versionCode,updatedAt=now,summary=summary,tags=tags,changelog=changes,sha256=sha)
        break
else:
    raise SystemExit('picacg manifest entry missing')
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def update_catalog(path):
    o=json.loads(path.read_text(encoding='utf-8')); o['updatedAt']=now
    for x in o.get('items',[]):
        if x.get('id')=='picacg':
            x.update(name='🍥 哔咔漫画 · APP/网页双线路 Beta',summary=summary,channel='beta',version=version,updatedAt=day,tags=tags,changelog=changes,sourceUrl=raw_url,backupUrl=backup,importUrl='legado://import/bookSource?src='+raw_url,detailUrl=detail_url)
            return o
    raise SystemExit('picacg catalog entry missing: '+str(path))
for rel in ['subscription/beta.json','subscription/comic.json']:
    p=ROOT/rel; p.write_text(json.dumps(update_catalog(p),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

detail={
    'kind':'source','title':'🍥 哔咔漫画 · APP/网页双线路 Beta','summary':summary,
    'badges':['BETA',version,'漫画源','正文按钮/详情增强'],
    'sections':[
        {'title':'正文定制按钮','text':'阅读/Archive 的正文菜单只在当前 BookSource.customButton=true 时显示自定义图标。Beta4 除顶层字段外，还在详情、目录、正文规则运行时对当前书源对象重新确保 customButton/eventListener=true。'},
        {'title':'详情页','text':'参考 Venera 哔咔详情页的信息层级，拆分为作品数据、描述、信息。保留阅读原生详情框架，不另外打开重型网页。'},
        {'title':'可点击信息','text':'作者、汉化组、分类、标签都可以直接进入对应列表；上传者、更新时间、上传时间、页数、下载/评论能力集中放在信息区。'},
        {'title':'冻结域','text':'评论中心、评论楼中楼、点赞/收藏、相关推荐、目录、正文图片及 APP/Web 请求链未重写。'},
        {'title':'发布状态','text':'Beta / 测试版；Stable 未修改。'},
        {'title':'唯一身份','text':'https://sc8d7.invalid/legado/picacg-8d7'}
    ],'sourceUrl':raw_url,'backupUrl':backup
}
dp=ROOT/detail_path; dp.parent.mkdir(parents=True,exist_ok=True); dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

beta=[]
for x in manifest.get('sources',[]):
    if x.get('channel')!='beta': continue
    fp=ROOT/str(x.get('sourcePath') or '')
    if fp.exists():
        obj=json.loads(fp.read_text(encoding='utf-8'))
        if isinstance(obj,list): beta.extend(obj)
(ROOT/'bundles/all-beta.json').write_text(json.dumps(beta,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

log=ROOT/'docs/RELEASE_LOG.md'; oldlog=log.read_text(encoding='utf-8')
marker=f'## {day} — Picacg {version} reader custom-button + Venera-style detail enhancement'
if marker not in oldlog:
    block=(marker+'\n\nStatus: Beta/Test; awaiting real-device confirmation.\n\nChanges:\n\n'+''.join('- '+c+'\n' for c in changes)+f'- Published SHA256: `{sha}`.\n\n')
    lines=oldlog.splitlines(True)
    oldlog=(lines[0]+'\n'+block+''.join(lines[1:])) if lines and lines[0].startswith('# RELEASE LOG') else block+oldlog
    log.write_text(oldlog,encoding='utf-8')

kp=ROOT/'docs/KNOWN_ISSUES.md'; known=kp.read_text(encoding='utf-8')
heading='## Picacg custom button flag present in JSON but hidden in reader — runtime self-heal in 1.0.0-beta4'
if heading not in known:
    known += ('\n\n'+heading+'\n\nReal-device Beta3 showed `customButton: true` and a valid `clickCustomButton` callback in the source JSON, but the manga reader menu still omitted the custom icon. Source review of Legado/Archive `ReadMenu` confirms visibility is decided before callback execution from the current in-memory `BookSource.customButton` flag; therefore improving callback book-id lookup alone cannot make a hidden button appear.\n\nBeta4 keeps the top-level flag and also calls `picaEnsureReaderFeatures(this)` from detail, catalog and content rules to set `customButton/eventListener` on the active source object before the reader menu is opened. Status: awaiting real-device confirmation.\n')
    kp.write_text(known,encoding='utf-8')

pathlib.Path('/tmp/pica-jslib.js').write_text(src['jsLib'],encoding='utf-8')
for key,text in [('intro',src['ruleBookInfo']['intro']),('explore',src['ruleExplore']['bookList']),('content',src['ruleContent']['content']),('toc',src['ruleToc']['chapterList'])]:
    t=text.strip()
    if t.startswith('<js>'): t=t[4:]
    if t.endswith('</js>'): t=t[:-5]
    pathlib.Path('/tmp/pica-'+key+'.js').write_text(t,encoding='utf-8')

for rel in ['hotfix/picacg-beta4/READY','tools/publish_picacg_beta4.py','.github/workflows/publish-picacg-beta4.yml']:
    p=ROOT/rel
    if p.exists(): p.unlink()
try:
    (ROOT/'hotfix/picacg-beta4').rmdir()
except OSError:
    pass

print('published beta4',len(raw),'bytes',sha)
