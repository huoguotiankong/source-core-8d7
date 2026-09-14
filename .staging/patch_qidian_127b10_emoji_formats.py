import json, hashlib, base64, gzip, re
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta10'; VC=12080; TS='2026-09-15T01:05:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8')); stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
assert '1.2.7-beta9' in str(s.get('bookSourceComment','')), 'beta9 baseline expected'
js=str(s.get('jsLib',''))

# unpack QF_MOD38_PACK safely
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
code=gzip.decompress(base64.b64decode(raw[3:]+'='*(-len(raw[3:])%4))).decode('utf-8'); old_code=code
assert '1.2.7-beta8' in code or 'qfReviewCopyReaderContentV1278' in code
assert 'qdOuterSeed' in code, 'beta9 outer seed missing'

# 1) visual support for official image emoji + explicit unknown diagnostics in beta only
css_anchor='.qfEmoji{display:inline;font-size:1.08em;line-height:1;vertical-align:-.04em;font-family:"Noto Color Emoji","Segoe UI Emoji","Apple Color Emoji",sans-serif}'
assert css_anchor in code
code=code.replace(css_anchor,css_anchor+'.qfEmojiImg{display:inline-block;width:1.35em;height:1.35em;object-fit:contain;vertical-align:-.28em;margin:0 .04em}.qfEmojiUnknown{display:inline-flex;align-items:center;gap:2px;color:#d85b50;border-bottom:1px dotted #d85b50}.qfEmojiCode{font-size:.58em;color:#c78378;vertical-align:super;margin-left:1px}',1)

# 2) recursively collect alternate official emoji metadata. We do not assume a single schema.
helper=r'''
/* 1.2.7-beta10：多格式表情线索收集。
 * 妙想天开只公开了 [fn=1..64] 的旧映射；起点新版评论可能把新表情放到 Emoji/Face/
 * Expression/Sticker 等结构字段，或直接给图片 URL。这里递归收集这些字段，供 UI 在正文出现
 * 占位符时按顺序恢复；不扫描普通业务数字，避免把楼层/点赞等误当表情 ID。 */
function qfEmojiHintsV1280(root){
    var out=[],seen={},nodes=0;
    function addId(v,k){var n=Number(v);if(!isFinite(n)||n<=0||n>9999)return;var z='id:'+n;if(seen[z])return;seen[z]=1;out.push({id:n,key:String(k||'')})}
    function addUrl(v,k){var u=String(v||'').trim();if(!/^https?:\/\//i.test(u)&&u.indexOf('//')!==0)return;if(u.indexOf('//')===0)u='https:'+u;var z='url:'+u;if(seen[z])return;seen[z]=1;out.push({url:u,key:String(k||'')})}
    function addText(v,k){var t=String(v||'').trim();if(!t||t.length>24)return;var z='text:'+t;if(seen[z])return;seen[z]=1;out.push({text:t,key:String(k||'')})}
    function walk(v,key,depth){
        if(v==null||depth>6||nodes>300)return;nodes++;
        var keyHit=/(emoji|emot|emotion|expression|face|sticker|smile|emote|fn)/i.test(String(key||''));
        if(typeof v==='string'){
            var m,rx=/\[(?:fn|emoji|face|emot|expression)=(\d+)\]/ig;while((m=rx.exec(v)))addId(m[1],key);
            if(keyHit){
                if(/^\d+$/.test(v.trim()))addId(v,key);
                else if(/^https?:\/\//i.test(v.trim())||v.trim().indexOf('//')===0)addUrl(v,key);
                else if(v.trim().length<=12)addText(v,key);
            }
            return;
        }
        if(typeof v==='number'){if(keyHit)addId(v,key);return;}
        if(typeof v!=='object')return;
        if(Array.isArray(v)){for(var i=0;i<v.length&&i<80;i++)walk(v[i],key,depth+1);return;}
        for(var k in v)if(Object.prototype.hasOwnProperty.call(v,k))walk(v[k],k,depth+1);
    }
    try{walk(root,'',0)}catch(_e){}
    return out.slice(0,24);
}
'''
anchor='function qfReviewUiPayloadBase(item,raw){'
assert anchor in code
code=code.replace(anchor,helper+'\n'+anchor,1)

# 3) carry hints through payload/adapters
ret_anchor='''        content:content,
        image:qfCommentImageV504(raw),'''
assert ret_anchor in code
code=code.replace(ret_anchor,'''        content:content,
        emojiHints:qfEmojiHintsV1280(raw),
        image:qfCommentImageV504(raw),''',1)
# both adaptReply + adapt
count=code.count('content:payload.content,')
assert count>=2, count
code=code.replace('content:payload.content,','content:payload.content,\n        emojiHints:payload.emojiHints||[],',2)

# 4) replace old single-format formatter with a multi-format renderer.
old_fmt=r'''function qfEmojiHtmlV1272(n){var v=EM[Number(n)];return v?'<span class=\"qfEmoji\">'+esc(v)+'</span>':'[fn='+String(n)+']'}
function fmt(s){
    var safe=esc(String(s==null?'':s));
    safe=safe.replace(/\\[fn=(\\d+)\\]/g,function(m,n){return qfEmojiHtmlV1272(n)});
    return safe.replace(/\\r\\
|\\r|\\
/g,'<br>');
}'''
# exact source may contain literal backslash-newline from String.raw, use positional replacement instead
f0=code.find('function qfEmojiHtmlV1272(n){')
f1=code.find('function fmt(s){',f0)
assert f0>=0 and f1>f0
# find end of fmt by next function marker
f2=code.find('\nfunction ',f1+10)
assert f2>f1
new_fmt=r'''function qfEmojiHtmlV1280(n){
    var id=Number(n),v=EM[id];
    return v?'<span class="qfEmoji">'+esc(v)+'</span>':'<span class="qfEmojiUnknown">[fn='+String(n)+']</span>';
}
function qfEmojiHintHtmlV1280(h){
    h=h||{};
    if(h.url)return '<img class="qfEmojiImg" src="'+esc(qfNormAssetUrlV1272(h.url))+'" referrerpolicy="no-referrer" loading="lazy">';
    if(h.id!=null)return qfEmojiHtmlV1280(h.id);
    if(h.text)return '<span class="qfEmoji">'+esc(h.text)+'</span>';
    return '';
}
function qfEmojiCodeV1280(ch){
    try{var cp=String(ch||'').codePointAt(0);return cp==null?'':('U+'+cp.toString(16).toUpperCase())}catch(_e){return''}
}
function fmt(s,hints){
    var raw=String(s==null?'':s),safe=esc(raw),hs=Array.isArray(hints)?hints:[],hi=0;
    safe=safe.replace(/\[(?:fn|emoji|face|emot|expression)=(\d+)\]/gi,function(m,n){return qfEmojiHtmlV1280(n)});
    safe=safe.replace(/\{(?:emoji|face|emot|expression)[:=](\d+)\}/gi,function(m,n){return qfEmojiHtmlV1280(n)});
    safe=safe.replace(/[\u2612\uFFFD\uE000-\uF8FF]/g,function(ch){
        var rep='';while(hi<hs.length&&!rep){rep=qfEmojiHintHtmlV1280(hs[hi++])}
        if(rep)return rep;
        var cp=qfEmojiCodeV1280(ch);
        return '<span class="qfEmojiUnknown">'+esc(ch)+'<span class="qfEmojiCode">'+esc(cp)+'</span></span>';
    });
    return safe.replace(/\r\n|\r|\n/g,'<br>');
}'''
code=code[:f0]+new_fmt+code[f2:]

# 5) every comment/reply/audio renderer passes its structured emoji hints
fmt_count=code.count('fmt(c.content)')
assert fmt_count>=3, fmt_count
code=code.replace('fmt(c.content)','fmt(c.content,c.emojiHints)',fmt_count)

assert 'qfEmojiHintsV1280' in code
assert 'qfEmojiUnknown' in code
assert 'qfEmojiImg' in code
assert 'fmt(c.content,c.emojiHints)' in code
assert code!=old_code
check=ROOT/'.staging/qidian-127b10-review-check.js'; check.write_text(code,encoding='utf-8')

pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta10：根据真机“少数表情正常、部分表情仍为方框”的特征，停止继续改评论请求链，转向表情协议兼容。妙想天开明文表仅覆盖 fn=1..64；当前页在保留既有映射的同时，新增 Emoji/Face/Expression/Sticker 等结构字段递归识别、图片型表情渲染、[emoji=N]/[face=N] 等备用 token 支持。若仍无法恢复，异常字符会显示实际 U+码点，下一轮可直接据此补映射，不再盲猜。Stable 1.2.6 业务域全部冻结。'

for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta9 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY
BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()

summary='Beta 1.2.7-beta10：表情协议兼容层，支持旧 fn 映射之外的 Emoji/Face/Expression/Sticker 元数据与图片表情，并显示未知码点。'
tags=['起点','测试版','评论优化','表情修复','多格式表情','Emoji元数据','图片表情','未知码点诊断','妙想天开参考','Stable 1.2.6基线']
changes=[
 '真机确认不是所有表情都失败：停止继续修改签名/请求链，转向映射与编码协议本身',
 '妙想天开明文映射只覆盖 fn=1..64；当前实现保留原映射并兼容 [emoji=N]/[face=N]/[emot=N]/[expression=N] 等 token',
 '递归读取 Emoji/Emot/Expression/Face/Sticker/Smile 等结构字段；若官方返回表情图片 URL，直接以内联小图渲染',
 '正文仍为占位字符且没有可用元数据时，Beta 页面显示实际 Unicode 码点（如 U+2612/PUA），用于下一轮精确补映射',
 '目录、正文、版权、账号、Provider、评论分页和请求链均冻结'
]
def beta_entry(old=None,typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    return e

mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
items=m.setdefault('sources',[]); pos=next((i for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
ne=beta_entry(items[pos] if pos is not None else None); ne['category']='novel'; ne['artifactType']='bookSource'
if pos is None: items.insert(0,ne)
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
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'Emoji协议兼容'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'判断','text':'真机反馈表现为“少数表情正常、部分表情方框”，因此本轮不再继续改签名与请求层，而是直接扩展表情 token/结构字段兼容。'},
 {'title':'兼容','text':'保留 fn 映射，新增 Emoji/Face/Expression/Sticker 等字段递归识别和图片型表情显示。'},
 {'title':'诊断','text':'如果某个表情仍无法恢复，Beta 会在该占位符旁显示 U+码点；用同一条评论截图即可确定下一步映射。'},
 {'title':'冻结','text':'Stable 1.2.6 的目录、正文、版权、账号、Provider 以及评论请求/分页均不修改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

logp=ROOT/'docs/RELEASE_LOG.md'; log=logp.read_text(encoding='utf-8')
entry='''## 2026-09-15 · qidian-next 1.2.7-beta10\n- 真机表现为少数表情正常、部分表情仍为方框；停止继续修改签名/请求执行层，转向表情协议兼容。\n- 保留旧 `[fn=N]` 映射，并增加 `[emoji=N]` / `[face=N]` / `[emot=N]` / `[expression=N]` token 支持。\n- 递归识别 Emoji/Face/Expression/Sticker 等元数据；有官方图片 URL 时以内联图片渲染。\n- 未识别占位符在 Beta 显示真实 U+码点，便于下一轮按证据补映射。\n- 其它业务域冻结。\n\n'''
if entry.splitlines()[0] not in log: logp.write_text(entry+log,encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hand=hp.read_text(encoding='utf-8')
block='''\n\n## 2026-09-15 · 1.2.7-beta10 表情协议兼容\n- beta9 真机仍有方框，但同时确认部分表情可以正常显示。后续不再优先怀疑 QDSign/请求执行层。\n- 妙想天开公开的 replaceEmoji 仅有 fn=1..64；beta10 新增多格式 token、Emoji/Face/Expression/Sticker 元数据与图片 URL 支持。\n- 对仍无法恢复的占位符显示真实 Unicode U+码点，用于下一轮建立精确映射，不再猜测。\n- Stable 1.2.6 与目录/正文/版权/账号/Provider/评论分页请求链保持冻结。\n'''
if '1.2.7-beta10 表情协议兼容' not in hand: hp.write_text(hand+block,encoding='utf-8')

report={'version':VERSION,'versionCode':VC,'sha256':sha,'baseline':'1.2.7-beta9','focus':'emoji protocol/mapping rather than request chain','features':['multi token formats','structured emoji hints','image emoji','unknown codepoint display'],'stableBusinessFrozen':all(s.get(k)==stable.get(k) for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'))}
(ROOT/'.staging/qidian-127b10-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
