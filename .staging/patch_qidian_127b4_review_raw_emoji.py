import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta4'; VC=12074; TS='2026-09-14T22:50:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8')); stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
assert '1.2.7-beta3' in str(s.get('bookSourceComment','')), 'beta baseline is not 1.2.7-beta3'

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

# 妙想天开实际做法：先取起点官方原始 Content，再对字面 [fn=N] 做 emoji 映射。
# beta2/3 的 canonical payload 反而优先 item.text/item.content；这些字段有机会已经被
# 上游 normalizer 转换成私有字形/缺字方框，导致 fmt 再也看不到 [fn=N]。
old_payload='''        content:String(\n            textOf(\n                item.text||item.content||\n                raw.Content||raw.content||\n                raw.ReviewContent||raw.reviewContent||\n                raw.Body||raw.PostBody||raw.PostContent||\n                raw.Subject||raw.Title\n            )||""\n        ),'''
assert old_payload in code, 'canonical content block not found'
new_payload='''        content:String(\n            textOf(\n                raw.Content||raw.content||\n                raw.ReviewContent||raw.reviewContent||\n                raw.Body||raw.PostBody||raw.PostContent||\n                raw.Subject||raw.Title||\n                item.text||item.content\n            )||""\n        ),'''
code=code.replace(old_payload,new_payload,1)

# 表情处理也收敛到参考源的简单语义：HTML 转义之后，仅把官方原始 [fn=N] 逐项替换。
old_fmt='''function qfEmojiHtmlV1272(n){var v=EM[Number(n)];return v?'<span class="qfEmoji">'+esc(v)+'</span>':'💬'}\nfunction fmt(s){\n    var raw=String(s==null?'':s);\n    var safe=esc(raw);\n    /* 妙想天开同款 [fn=N]；同时兼容接口偶发带反斜杠/实体括号的形式。 */\n    safe=safe.replace(/\\\\?\\[fn=(\\d+)\\]\\\\?/gi,function(m,n){return qfEmojiHtmlV1272(n)});\n    safe=safe.replace(/&#91;fn=(\\d+)&#93;/gi,function(m,n){return qfEmojiHtmlV1272(n)});\n    return safe.replace(/\\r\\n|\\r|\\n/g,'<br>');\n}'''
assert old_fmt in code, 'beta3 fmt block not found'
new_fmt='''function qfEmojiHtmlV1272(n){var v=EM[Number(n)];return v?'<span class="qfEmoji">'+esc(v)+'</span>':'[fn='+String(n)+']'}\nfunction fmt(s){\n    var safe=esc(String(s==null?'':s));\n    safe=safe.replace(/\\[fn=(\\d+)\\]/g,function(m,n){return qfEmojiHtmlV1272(n)});\n    return safe.replace(/\\r\\n|\\r|\\n/g,'<br>');\n}'''
code=code.replace(old_fmt,new_fmt,1)

# Hard gates: official raw content must now win before normalized item content.
payload_pos=code.index('function qfReviewUiPayloadBase')
raw_pos=code.index('raw.Content||raw.content',payload_pos)
item_pos=code.index('item.text||item.content',payload_pos)
assert payload_pos>=0 and raw_pos>payload_pos and item_pos>raw_pos, 'raw Content is not preferred'
assert "safe=safe.replace(/\\[fn=(\\d+)\\]/g" in code
assert "26:'🤪'" in code and "19:'😂'" in code and "64:'🐲'" in code

# Preserve beta3 visual and paging fixes.
assert 'qfOfficialBadge' in code and 'avatarFallback' in code
assert 'autoLoadBudget=0' in code and 'h-y-v<600' in code and '已加载全部回复' in code
assert code!=old_code

# Emit unpacked module so CI validates the actual browser script, not only JSON/Python syntax.
check=ROOT/'.staging/qidian-127b4-review-check.js'; check.write_text(code,encoding='utf-8')

pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta4：按妙想天开明文评论实现修复起点自定义表情。canonical 内容改为优先使用官方 raw.Content/ReviewContent，再执行字面 [fn=N]→Emoji 映射，避免上游 item.content 已被转换成缺字方框后再映射失效。保留官方 TitleImage 标签、头像多字段与首字兜底，以及首屏10条、无后台预取、600px近底翻页和楼中楼完成态；评论请求链及目录/正文/版权/账号/Provider 不变。'

# Only review_local_ui/display metadata may differ from beta3; core stable domains stay frozen.
for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta3 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.7-beta4：按妙想天开明文实现，评论优先读取官方 raw Content 后再替换 [fn=N] 表情。'
tags=['起点','测试版','评论优化','妙想天开参考','原始Content','Emoji','官方标签','头像兜底','10条首屏','滚动分页','Stable 1.2.6基线']
changes=[
 '对照妙想天开明文评论代码：官方评论先读取 c.Content/r.Content，再执行 replaceEmoji([fn=N])',
 '修正我们的 canonical 优先级：raw.Content/ReviewContent/Body/PostContent 优先，item.text/item.content 仅作为末级兜底，避免表情 token 在 normalizer 阶段被提前损坏',
 '表情渲染收敛为字面 [fn=N] 映射，保留 HTML 转义与 Emoji 字体兼容；映射 1-64 与参考源一致',
 '保留 beta3 官方 TitleImage 标签、头像字段扩展/首字兜底及图片错误监听',
 '保留首屏10条、取消后台预取、600px近底翻页、楼中楼完成态；评论请求链和其它业务全部冻结'
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
else: items[pos]=ne
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bp=ROOT/'subscription/beta.json'; bd=json.loads(bp.read_text(encoding='utf-8')); bd['updatedAt']=TS; bd['generatedAt']=TS
bi=bd.setdefault('items',[]); pos=next((i for i,e in enumerate(bi) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
if pos is None: bi.insert(0,beta_entry())
else: bi[pos]=beta_entry(bi[pos])
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

np=ROOT/'subscription/novel.json'; nd=json.loads(np.read_text(encoding='utf-8')); nd['updatedAt']=TS; nd['generatedAt']=TS
ni=[e for e in nd.get('items',[]) if not (isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'))]
ni.insert(0,beta_entry(typed=True)); nd['items']=ni
np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bunp=ROOT/'bundles/all-beta.json'; ba=json.loads(bunp.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr
ba=[o for o in ba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)]; ba.insert(0,src)
bunp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'原始Content表情'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'根因','text':'妙想天开直接使用起点官方 Content 后再替换 [fn=N]。我们此前优先使用 item.text/item.content，表情 token 可能在前置 normalizer 中已变成缺字方框，因此后续映射无法命中。'},
 {'title':'本版修复','text':'评论正文与楼中楼统一优先读取 raw.Content/ReviewContent 等官方原始字段，再执行 1-64 的 [fn=N] Emoji 映射；item.text/item.content 仅末级兜底。'},
 {'title':'保留优化','text':'官方 TitleImage 标签、头像多字段兼容/首字兜底、首屏10条、无后台预取、600px近底翻页、楼中楼完成态全部保留。'},
 {'title':'冻结项','text':'评论请求/签名/分页接口、目录、版权、正文、账号和 Provider 均未修改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'; rp.write_text((f"## 2026-09-14 · qidian-next {VERSION}\n- 对照妙想天开明文评论实现，确认其直接使用官方 `Content` 后执行 `[fn=N]` 表情替换。\n- 修正评论 canonical 内容优先级：`raw.Content/ReviewContent/...` 优先，`item.text/item.content` 降为末级兜底，避免表情 token 在前置 normalizer 阶段损坏。\n- 表情映射收敛为官方原始 `[fn=N]` 字面替换；官方 TitleImage、头像优化和 beta1 分页策略全部保留。\n- 评论请求链、目录、版权、正文、账号、Provider 全部冻结。\n- 继续执行解包后 `node --check` 语法门禁；未经真机确认不得晋升 Stable。\n\n")+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hp.write_text((f"## 2026-09-14 · {VERSION} — 评论原始 Content 表情修复\n\n- 参考妙想天开明文实现：评论/回复直接使用官方 `Content`，随后 `[fn=N]` 映射 Emoji。\n- beta3 的 canonical 曾优先 `item.text/item.content`，可能已在前置 normalizer 丢失 `[fn]` token；beta4 改为 raw official Content 优先。\n- TitleImage 标签、头像兜底、首屏10条/600px分页继续保留；其它业务域冻结。\n\n")+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-127b4-report.json'; report.write_text(json.dumps({
 'version':VERSION,'versionCode':VC,'betaSha256':sha,'baseline':'1.2.7-beta3 / Stable 1.2.6',
 'reference':'妙想天开 plaintext comment renderer','rawOfficialContentFirst':True,'literalFnEmojiMap':True,
 'emojiMapReferenceRange':'1-64','officialTitleImagePreserved':True,'avatarFallbackPreserved':True,
 'firstPageStrict10Preserved':True,'backgroundPrefetchPages':0,'scrollThresholdPx':600,
 'syntaxGate':'node --check','ruleTocFrozen':True,'ruleBookInfoFrozen':True,'ruleContentFrozen':True,'bookSourceUrlFrozen':True
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha,'raw-first',raw_pos<item_pos)
