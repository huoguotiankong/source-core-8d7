import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta3'; VC=12073; TS='2026-09-14T22:35:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8')); stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
js=str(s.get('jsLib',''))
mark='var QF_MOD38_PACK='; p=js.find(mark); assert p>=0
start=js.find('{',p+len(mark)); depth=0; quote=''; esc=False; end=-1
for i in range(start,len(js)):
    ch=js[i]
    if quote:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch==quote: quote=''
        continue
    if ch in ('"',"'"): quote=ch; continue
    if ch=='{': depth+=1
    elif ch=='}':
        depth-=1
        if depth==0: end=i+1; break
assert end>start
pack=json.loads(js[start:end]); raw=pack['review_local_ui']; assert raw.startswith('gz:')
b64=raw[3:]+'='*(-len(raw[3:])%4)
code=gzip.decompress(base64.b64decode(b64)).decode('utf-8'); old_code=code

# beta2 regression: inline onerror text used two backslashes before a single quote inside a
# single-quoted JavaScript HTML string. That terminates the string at parse time, so the
# entire comment script never starts (count stays 0, quote stays '加载原文…', spinner forever).
# Remove all such quote-sensitive inline handlers. Avatar fallback remains behind the image;
# failed images are hidden by a capture-phase error listener instead.
mal=r"\\'none\\'"
mal_count=code.count(mal)
assert mal_count>=2, f'expected malformed beta2 inline handlers, got {mal_count}'
code=code.replace(mal,'&quot;none&quot;')

# Add a syntax-safe global image error fallback. It covers avatar/badge/frame/media images
# without putting nested quote syntax inside generated HTML strings.
anchor="document.getElementById('lightbox').onclick=function(){this.classList.add('hidden')};"
assert anchor in code
safe="""document.addEventListener('error',function(ev){try{var el=ev&&ev.target;if(el&&el.tagName==='IMG'){if(el.classList&&el.classList.contains('zoom'))return;el.style.display='none';}}catch(_e){}},true);\n"""
code=code.replace(anchor,safe+anchor,1)

# Preserve beta1/beta2 intended behavior.
assert 'qfOfficialBadge' in code and 'qfEmojiHtmlV1272' in code and 'avatarFallback' in code
assert 'autoLoadBudget=0' in code and 'h-y-v<600' in code and '已加载全部回复' in code
assert mal not in code
assert code!=old_code

# Emit unpacked module for CI syntax validation.
check=ROOT/'.staging/qidian-127b3-review-check.js'; check.write_text(code,encoding='utf-8')

pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta3：修复 beta2 评论页一直“加载中”的脚本解析回归。保留官方 TitleImage 标签、[fn] 表情映射、头像字段扩展和首字兜底；移除会破坏 JavaScript 字符串的内联 onerror 引号写法，改为统一图片错误监听。继承 beta1 首屏10条、600px近底翻页和楼中楼完成态；评论请求链及目录/正文/版权/账号/Provider 不变。'

for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta2 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.7-beta3：修复 beta2 评论页脚本解析失败导致一直加载；保留官方标签、表情和头像优化。'
tags=['起点','测试版','评论优化','回归修复','官方标签','TitleImage','Emoji','头像兜底','10条首屏','滚动分页','Stable 1.2.6基线']
changes=[
 '修复 beta2 内联图片 onerror 引号转义错误导致 review_local_ui 整段 JavaScript 无法解析的问题',
 '图片失败处理改为 capture error 统一监听，避免再次把嵌套引号写入 HTML 字符串',
 '保留官方 TitleImage 标签、[fn=N] 表情映射、Emoji 字体兜底、头像字段扩展与用户名首字兜底',
 '保留首屏10条、取消后台预取、600px近底翻页和楼中楼完成态',
 '评论请求/解析数据链、目录、版权、正文、账号、Provider 全部冻结'
]

def beta_entry(old=None,typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    return e

mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
items=m.setdefault('sources',[]); pos=next((i for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
ne=beta_entry(items[pos] if pos is not None else None); ne['category']='novel'; ne['artifactType']='bookSource'
if pos is None:
    ins=next((i+1 for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next'),len(items)); items.insert(ins,ne)
else:items[pos]=ne
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bp=ROOT/'subscription/beta.json'; bd=json.loads(bp.read_text(encoding='utf-8')); bd['updatedAt']=TS; bd['generatedAt']=TS
bi=bd.setdefault('items',[]); pos=next((i for i,e in enumerate(bi) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
if pos is None:bi.insert(0,beta_entry())
else:bi[pos]=beta_entry(bi[pos])
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

np=ROOT/'subscription/novel.json'; nd=json.loads(np.read_text(encoding='utf-8')); nd['updatedAt']=TS; nd['generatedAt']=TS
ni=[e for e in nd.get('items',[]) if not (isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'))]
ni.insert(0,beta_entry(typed=True)); nd['items']=ni
np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bunp=ROOT/'bundles/all-beta.json'; ba=json.loads(bunp.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr
ba=[o for o in ba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)]; ba.insert(0,src)
bunp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'评论回归修复'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'本版修复','text':'beta2 的图片 onerror 内联字符串存在错误的引号转义，导致整个评论脚本无法解析，所以页面停在“加载原文…/加载中…”。beta3 已改为统一图片错误监听。'},
 {'title':'保留优化','text':'官方 TitleImage 标签、[fn] 表情映射、Emoji 字体、头像多字段兼容和首字兜底全部保留。'},
 {'title':'分页','text':'继续保持首屏10条、无后台预取、距离底部600px再加载下一页。'},
 {'title':'冻结项','text':'评论请求/解析数据链、目录、版权、正文、账号和 Provider 均未修改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'; rp.write_text((f"## 2026-09-14 · qidian-next {VERSION}\n- 修复 beta2 评论页一直加载：根因为内联图片 `onerror` 的引号转义破坏了 `review_local_ui` JavaScript 解析。\n- 图片失败处理改为统一 capture error 监听，避免生成 HTML 字符串中的嵌套引号风险。\n- 官方 TitleImage 标签、表情、头像优化与 beta1 按需分页全部保留。\n- 评论请求链、目录、版权、正文、账号、Provider 全部冻结。\n- 新增 Node `--check` 语法门禁；未经真机确认不得晋升 Stable。\n\n")+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hp.write_text((f"## 2026-09-14 · {VERSION} — 评论加载回归修复\n\n- beta2 的 `review_local_ui` 因内联 `onerror` 引号转义错误导致 JS parse failure，真机表现为评论数量0、原文和列表永久加载中。\n- beta3 仅修正该运行时解析问题，并增加 Node `--check` 构建门禁。\n- beta2 的官方标签、表情、头像优化继续保留；其它业务域冻结。\n\n")+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-127b3-report.json'; report.write_text(json.dumps({'version':VERSION,'versionCode':VC,'betaSha256':sha,'baseline':'1.2.7-beta2 / Stable 1.2.6','rootCause':'malformed inline onerror quote escaping caused review_local_ui JavaScript parse failure','malformedHandlersFixed':mal_count,'syntaxGate':'node --check','officialTitleImagePreserved':True,'emojiPreserved':True,'avatarFallbackPreserved':True,'firstPageStrict10Preserved':True,'backgroundPrefetchPages':0,'scrollThresholdPx':600,'ruleTocFrozen':True,'ruleBookInfoFrozen':True,'ruleContentFrozen':True,'bookSourceUrlFrozen':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha,'fixed',mal_count)
