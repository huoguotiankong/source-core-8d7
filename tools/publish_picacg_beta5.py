import json, hashlib, pathlib
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path('.')
target = ROOT / 'sources/comic/picacg/picacg-beta.json'
data = json.loads(target.read_text(encoding='utf-8'))
if not isinstance(data, list) or len(data) != 1:
    raise SystemExit('Picacg source must contain exactly one source object')
src = data[0]
if src.get('bookSourceUrl') != 'https://sc8d7.invalid/legado/picacg-8d7':
    raise SystemExit('Picacg identity mismatch')
if src.get('bookSourceType') != 2:
    raise SystemExit('Picacg must remain image/manga source type')

# Beta5: stop trying to emulate the text-reader custom button in source JS.
# Legado image books use ReadMangaActivity/MangaMenu; the current MangaMenu layout/code
# has no tv_custom_btn and no clickCustomButton dispatch. Keep customButton/eventListener
# enabled because BookInfoActivity DOES implement the detail-page custom button.
src['customButton'] = True
src['eventListener'] = True

# Keep the native detail summary short. Full metrics live in our rich intro panel.
init = src['ruleBookInfo']['init']
old_kind = 'java.put("pica_kind",cats.join(" · ")+(c.finished?" · 完结":" · 连载"));'
new_kind = 'var primaryCat=cats.length?String(cats[0]||""):"";java.put("pica_kind",(primaryCat?primaryCat+" · ":"")+(c.finished?"完结":"连载"));'
if old_kind not in init:
    raise SystemExit('beta4 pica_kind baseline not found')
init = init.replace(old_kind, new_kind, 1)
old_stats = 'java.put("pica_stats","👁 "+views+"  ·  ♥ "+likes+"  ·  💬 "+comments+"  ·  "+Number(c.epsCount||0)+"话 / "+Number(c.pagesCount||0)+"页");'
new_stats = 'java.put("pica_views",String(views));java.put("pica_likes",String(likes));java.put("pica_stats","👁 "+views+" · ♥ "+likes+" · 💬 "+comments+" · "+Number(c.epsCount||0)+"话 / "+Number(c.pagesCount||0)+"页");'
if old_stats not in init:
    raise SystemExit('beta4 pica_stats baseline not found')
init = init.replace(old_stats, new_stats, 1)
src['ruleBookInfo']['init'] = init

# Rich detail panel: balanced interaction block + compact data panel + Venera-like metadata hierarchy.
src['ruleBookInfo']['intro'] = r'''<js>
var desc=String(java.get("pica_intro")||"");
var cats=picaJson(java.get("pica_categories"),[]),tags=picaJson(java.get("pica_tags"),[]);
var author=String(java.get("pica_author")||""),team=String(java.get("pica_team")||""),status=String(java.get("pica_status")||"");
var creator=String(java.get("pica_creator")||""),created=String(java.get("pica_created")||""),updated=String(java.get("pica_updated")||"");
var eps=String(java.get("pica_eps")||"0"),pages=String(java.get("pica_pages")||"0"),downloadable=String(java.get("pica_download")||""),commentable=String(java.get("pica_commentable")||"");
var views=String(java.get("pica_views")||"0"),likes=String(java.get("pica_likes")||"0"),comments=String(java.get("pica_comments")||"0");
function dt(v){v=String(v||"");return v?v.replace("T"," ").replace(/\.\d+Z?$/," ").replace(/Z$/," ").trim().slice(0,16):"";}
function sec(t){return "<br><br><b><font color=\"#378fdf\">▍"+picaEsc(t)+"</font></b><br><br>";}
function chip(t,k,icon){t=String(t||"").trim();if(!t)return "";icon=icon||"";return "<button>"+icon+picaEsc(t)+"@onclick:picaBookInfoOpenTag.call(this,"+JSON.stringify(t)+","+JSON.stringify(k)+")</button> ";}
function row(label,value){value=String(value||"").trim();return value?"<br><font color=\"#7f8b99\"><b>"+picaEsc(label)+"</b></font>　"+picaEsc(value):"";}
function dataRow(a,av,b,bv){var s="<b>"+picaEsc(a)+"</b>　"+picaEsc(String(av||"-"));if(b)s+="　　<b>"+picaEsc(b)+"</b>　"+picaEsc(String(bv||"-"));return s+"<br>";}
var html="";
html+=sec("互动与操作");
html+="<button>💬 查看评论@onclick:picaBookInfoOpenComments.call(this)</button> <button>♥ 点赞作品@onclick:picaBookInfoLike.call(this)</button>";
html+="<br><br><button>⭐ 收藏作品@onclick:picaBookInfoFavourite.call(this)</button> <button>🧭 相关推荐@onclick:picaBookInfoRecommend.call(this)</button>";
html+=sec("作品数据");
html+=dataRow("👁 浏览",views,"♥ 点赞",likes);
html+=dataRow("💬 评论",comments,"📚 章节",eps+"话");
html+=dataRow("🖼 页数",pages+"页","● 状态",status||"未知");
html+=sec("描述");
html+=(desc?picaEsc(desc).replace(/\r\n|\r|\n/g,"<br>"):"暂无描述");
html+=sec("作品信息");
if(author)html+="<font color=\"#7f8b99\"><b>作者</b></font>　"+chip(author,"author","✍️ ");
if(team)html+="<br><font color=\"#7f8b99\"><b>汉化组</b></font>　"+chip(team,"team","🈶 ");
if(creator)html+=row("上传者",creator);
if(cats.length){html+="<br><font color=\"#7f8b99\"><b>分类</b></font>　";for(var i=0;i<cats.length;i++)html+=chip(cats[i],"category","📂 ");}
if(tags.length){html+="<br><font color=\"#7f8b99\"><b>标签</b></font>　";for(var j=0;j<tags.length;j++)html+=chip(tags[j],"tag","# ");}
html+=row("更新时间",dt(updated));
html+=row("上传时间",dt(created));
var cap=[];if(downloadable)cap.push("下载 "+downloadable);if(commentable)cap.push("评论 "+commentable);if(cap.length)html+=row("权限",cap.join(" · "));
"<usehtml>"+html+"</usehtml>";
</js>'''

# Remove the duplicated native word-count/stats line; the structured panel is the single source of truth.
src['ruleBookInfo']['wordCount'] = ''

src['bookSourceComment'] = '''【v1.0.0-beta5 · 2026-08-26】
哔咔漫画 APP/网页双线路 UI 优化测试版。

Beta5：
• 正文定制按钮完成根因取证：图片漫画进入 ReadMangaActivity/MangaMenu，而当前阅读漫画菜单自身没有 customButton 控件、判断或 clickCustomButton 回调；这是 App 漫画菜单能力缺口，不是哔咔书源字段失效。详情页定制按钮继续保留并可直达评论。
• 停止继续在书源 JS 内做无效的“强制显示漫画正文定制按钮”修补，保持 bookSourceType=2，避免为了按钮破坏原生漫画连续图片阅读体验。
• 详情页互动区重排为 2×2：查看评论 / 点赞作品 / 收藏作品 / 相关推荐，解决原先 3+1 的不平衡排版。
• 作品数据改为紧凑双列信息面板：浏览、点赞、评论、章节、页数、状态分三行展示。
• 移除详情页原生 wordCount 中重复的一整串统计，顶部只保留简洁主分类/连载状态，完整数据统一下沉到“作品数据”。
• 描述与作品信息继续独立分区；作者、汉化组、分类、标签保持可点击。
• 评论中心、账号、收藏、点赞、目录、漫画图片和 APP/Web 双线路核心链冻结。

本版仍为 Beta，等待真机确认详情 UI。'''
src['variableComment'] = '''本源默认不需要设置书籍变量。
线路与清晰度请在“书源登录”页面设置。

详情页顶部定制按钮：打开当前漫画哔咔评论中心。
说明：阅读 App 的图片漫画模式使用独立 MangaMenu，当前版本的 MangaMenu 本身没有书源 customButton 控件，因此漫画正文菜单无法仅靠书源 JSON 增加该按钮；若后续阅读 App 为 MangaMenu 增加 customButton 支持，本源现有 clickCustomButton 回调可直接复用。
详情页作者、汉化组、分类与标签均可点击进入对应内容页。'''

# Invariants: don't regress the working manga pipeline.
assert src['bookSourceType'] == 2
assert src['customButton'] is True and src['eventListener'] is True
assert src['ruleContent'].get('callBackJs')
assert 'picaBookInfoOpenComments' in src['ruleContent']['callBackJs'] or 'picaOpenCommunityButton' in src['ruleContent']['callBackJs']
for operational in [src.get('loginUrl',''),src.get('exploreUrl',''),src.get('searchUrl',''),src['ruleToc'].get('chapterList','')]:
    assert 'PICA_SOURCE_ID' not in operational

now_dt = datetime.now(timezone(timedelta(hours=8)))
now = now_dt.isoformat(timespec='seconds')
day = now_dt.date().isoformat()
src['lastUpdateTime'] = int(now_dt.timestamp() * 1000)
raw = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
json.loads(raw.decode('utf-8'))
target.write_bytes(raw)
sha = hashlib.sha256(raw).hexdigest()

version = '1.0.0-beta5'
versionCode = 10005
summary = 'Beta5：确认漫画正文定制按钮受 MangaMenu 上游能力限制；详情互动区改为 2×2，作品数据重排并去除顶部重复统计。'
tags = ['哔咔','漫画','APP API','网页线路','评论','详情增强','互动区','作品数据','作者','汉化组','标签','MangaMenu','双线路']
changes = [
    '确认图片漫画正文使用 MangaMenu；当前 MangaMenu 布局/代码没有 customButton 控件与 clickCustomButton 分发，书源侧无法单独补出正文按钮',
    '保留详情页 customButton 与评论回调，不改变 bookSourceType=2，避免退化漫画原生阅读体验',
    '详情互动入口由 3+1 重排为 2×2：查看评论、点赞作品、收藏作品、相关推荐',
    '作品数据改为双列三行：浏览/点赞、评论/章节、页数/状态',
    '清空原生 wordCount 重复统计，顶部摘要仅保留主分类与连载状态',
    '作者、汉化组、分类、标签点击能力及账号/评论/正文/双线路核心链保持不变'
]
raw_base = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/comic/picacg/picacg-beta.json'
raw_url = raw_base + '?v=10005'
backup = 'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/comic/picacg/picacg-beta.json?v=10005'
detail_path = 'rss/data/details/beta/picacg.json'
detail_url = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/' + detail_path + '?v=10005'

mp = ROOT / 'manifest.json'
manifest = json.loads(mp.read_text(encoding='utf-8'))
manifest['updatedAt'] = now
for x in manifest.get('sources', []):
    if x.get('id') == 'picacg':
        x.update(version=version, versionCode=versionCode, updatedAt=now, summary=summary, tags=tags, changelog=changes, sha256=sha)
        break
else:
    raise SystemExit('picacg manifest entry missing')
mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def update_catalog(path):
    obj = json.loads(path.read_text(encoding='utf-8'))
    obj['updatedAt'] = now
    for x in obj.get('items', []):
        if x.get('id') == 'picacg':
            x.update(
                name='🍥 哔咔漫画 · APP/网页双线路 Beta',
                summary=summary,
                channel='beta', version=version, updatedAt=day,
                tags=tags, changelog=changes,
                sourceUrl=raw_url, backupUrl=backup,
                importUrl='legado://import/bookSource?src=' + raw_url,
                detailUrl=detail_url,
            )
            return obj
    raise SystemExit('picacg catalog entry missing: ' + str(path))

for rel in ['subscription/beta.json', 'subscription/comic.json']:
    p = ROOT / rel
    p.write_text(json.dumps(update_catalog(p), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

detail = {
    'kind':'source',
    'title':'🍥 哔咔漫画 · APP/网页双线路 Beta',
    'summary':summary,
    'badges':['BETA',version,'漫画源','详情 UI 优化'],
    'sections':[
        {'title':'本轮真机结论','text':'Beta4 真机再次确认：详情页 customButton 存在，但漫画正文菜单不存在。源码取证表明图片漫画由 ReadMangaActivity/MangaMenu 承载，当前 MangaMenu 没有 customButton 控件和 clickCustomButton 事件分发，因此不能靠书源 JSON 补出该控件。'},
        {'title':'互动区','text':'评论、点赞、收藏、推荐由 3+1 改为 2×2 排列，减少孤立按钮和视觉重心偏移。'},
        {'title':'作品数据','text':'浏览、点赞、评论、章节、页数、状态统一集中到紧凑双列面板；原生 wordCount 的重复长统计已移除。'},
        {'title':'作品信息','text':'描述独立分区；作者、汉化组、上传者、分类、标签、更新时间、上传时间、权限继续展示，其中作者/汉化组/分类/标签可点击。'},
        {'title':'核心保护','text':'账号、签到、收藏、点赞、评论中心、楼中楼、目录、漫画图片正文及 APP/Web 双线路不改。'},
        {'title':'发布状态','text':'Beta / 测试版；Stable 未修改。'},
        {'title':'唯一身份','text':'https://sc8d7.invalid/legado/picacg-8d7'}
    ],
    'sourceUrl':raw_url,
    'backupUrl':backup,
}
dp = ROOT / detail_path
dp.parent.mkdir(parents=True, exist_ok=True)
dp.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Rebuild Beta bundle without dropping unrelated sources.
beta = []
for x in manifest.get('sources', []):
    if x.get('channel') != 'beta':
        continue
    fp = ROOT / str(x.get('sourcePath') or '')
    if fp.exists():
        obj = json.loads(fp.read_text(encoding='utf-8'))
        if isinstance(obj, list):
            beta.extend(obj)
(ROOT / 'bundles/all-beta.json').write_text(json.dumps(beta, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

log = ROOT / 'docs/RELEASE_LOG.md'
oldlog = log.read_text(encoding='utf-8')
marker = f'## {day} — Picacg {version} manga-menu finding and detail UI polish'
if marker not in oldlog:
    block = marker + '\n\nStatus: Beta/Test; core functions retained, detail UI awaits real-device confirmation.\n\nChanges:\n\n' + ''.join('- ' + c + '\n' for c in changes) + f'- Published SHA256: `{sha}`.\n\n'
    lines = oldlog.splitlines(True)
    oldlog = (lines[0] + '\n' + block + ''.join(lines[1:])) if lines and lines[0].startswith('# RELEASE LOG') else block + oldlog
    log.write_text(oldlog, encoding='utf-8')

kp = ROOT / 'docs/KNOWN_ISSUES.md'
known = kp.read_text(encoding='utf-8')
heading = '## Image manga reader customButton gap — confirmed upstream limitation in Picacg 1.0.0-beta5'
if heading not in known:
    known += ('\n\n' + heading + '\n\n'
        'Real-device tests on Picacg beta3/beta4 repeatedly showed the custom button on BookInfoActivity but not in image manga reading. Source audit confirms this is not a BookSource.customButton persistence issue: BookInfoActivity reads the same BookSource.customButton and displays its custom menu item. Image books are launched through ReadMangaActivity and use MangaMenu/ViewMangaMenu; the current MangaMenu implementation has no tv_custom_btn view, no customButton visibility branch, and no SourceCallBack.CLICK_CUSTOM_BUTTON dispatch. Text books such as Qidian use ReadMenu, which does implement all three pieces.\n\n'
        'Rule: do not keep mutating customButton/eventListener inside image-source content rules expecting MangaMenu to render a missing control. Preserve bookSourceType=2 for correct manga UX. Source-side customButton remains useful on the detail page. A true manga-reader custom button requires an app-side MangaMenu implementation change.\n\n'
        'Status: upstream/app capability gap; not fixable by a standalone Legado source JSON without changing image-book reading mode.\n')
    kp.write_text(known, encoding='utf-8')

# Syntax smoke files for node --check.
def unwrap_js(text):
    t = text.strip()
    if t.startswith('<js>'): t = t[4:]
    if t.endswith('</js>'): t = t[:-5]
    return t
pathlib.Path('/tmp/pica-init.js').write_text(unwrap_js(src['ruleBookInfo']['init']), encoding='utf-8')
pathlib.Path('/tmp/pica-intro.js').write_text(unwrap_js(src['ruleBookInfo']['intro']), encoding='utf-8')
pathlib.Path('/tmp/pica-jslib.js').write_text(src['jsLib'], encoding='utf-8')
pathlib.Path('/tmp/pica-callback.js').write_text(src['ruleContent']['callBackJs'], encoding='utf-8')

ready = ROOT / 'hotfix/picacg-beta5/READY'
if ready.exists(): ready.unlink()
try: ready.parent.rmdir()
except OSError: pass
print('published beta5', len(raw), 'bytes', sha)
