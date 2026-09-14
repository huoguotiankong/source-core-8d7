import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta11'; VC=12081; TS='2026-09-15T01:18:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8')); stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
assert '1.2.7-beta10' in str(s.get('bookSourceComment','')), 'beta10 baseline expected'

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
code=gzip.decompress(base64.b64decode(raw[3:]+'='*(-len(raw[3:])%4))).decode('utf-8'); old_code=code
assert '1.2.7-beta10' in code or 'qfEmojiHtmlV1280' in code
assert "safe=safe.replace(/[\\u2612\\uFFFD\\uE000-\\uF8FF]/g,function(ch){" in code

helper=r'''
/* 1.2.7-beta11：恢复被截断成 BMP 私用区字符的 supplementary-plane Emoji。
 * 真机 beta10 直接暴露 U+F60D；它恰好等于 U+1F60D(😍) 的低 16 位。
 * 这说明至少一条评论链把非 BMP Emoji 误当成 16-bit char，丢掉了最高的 0x10000。
 * 只对 U+F000..U+F8FF 私用区做 +0x10000 恢复；其它未知字符继续保留诊断，不猜映射。 */
function qfEmojiFromCodePointV1281(cp){
    cp=Number(cp)||0;
    if(cp<=0xFFFF)return String.fromCharCode(cp);
    cp-=0x10000;
    return String.fromCharCode(0xD800+(cp>>10),0xDC00+(cp&0x3FF));
}
function qfTruncatedPuaEmojiHtmlV1281(ch){
    try{
        var low=String(ch||'').charCodeAt(0);
        if(low>=0xF000&&low<=0xF8FF){
            var full=low+0x10000;
            return '<span class="qfEmoji">'+esc(qfEmojiFromCodePointV1281(full))+'</span>';
        }
    }catch(_e){}
    return '';
}
'''
anchor='function qfEmojiCodeV1280(ch){'
pos=code.find(anchor); assert pos>=0
code=code[:pos]+helper+'\n'+code[pos:]

old='''    safe=safe.replace(/[\\u2612\\uFFFD\\uE000-\\uF8FF]/g,function(ch){
        var rep='';while(hi<hs.length&&!rep){rep=qfEmojiHintHtmlV1280(hs[hi++])}
        if(rep)return rep;
        var cp=qfEmojiCodeV1280(ch);
        return '<span class="qfEmojiUnknown">'+esc(ch)+'<span class="qfEmojiCode">'+esc(cp)+'</span></span>';
    });'''
new='''    safe=safe.replace(/[\\u2612\\uFFFD\\uE000-\\uF8FF]/g,function(ch){
        var pua=qfTruncatedPuaEmojiHtmlV1281(ch);
        if(pua)return pua;
        var rep='';while(hi<hs.length&&!rep){rep=qfEmojiHintHtmlV1280(hs[hi++])}
        if(rep)return rep;
        var cp=qfEmojiCodeV1280(ch);
        return '<span class="qfEmojiUnknown">'+esc(ch)+'<span class="qfEmojiCode">'+esc(cp)+'</span></span>';
    });'''
assert old in code, 'beta10 fmt diagnostic block not found'
code=code.replace(old,new,1)
assert 'qfTruncatedPuaEmojiHtmlV1281' in code
assert 'low>=0xF000&&low<=0xF8FF' in code
assert code!=old_code

check=ROOT/'.staging/qidian-127b11-review-check.js'; check.write_text(code,encoding='utf-8')
pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta11：beta10 真机诊断得到 U+F60D，确认存在 supplementary-plane Emoji 被截断成低16位私用区字符的问题；U+F60D + 0x10000 = U+1F60D（😍）。本版在评论最终渲染前仅对 U+F000..U+F8FF 做 +0x10000 恢复并重新组成 UTF-16 surrogate pair；其它未知字符继续显示码点诊断，不再改评论请求、签名或分页。目录/正文/版权/账号/Provider 全部冻结。'

for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta10 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY
BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()

summary='Beta 1.2.7-beta11：按真机暴露的 U+F60D 修复 Emoji 低16位截断，恢复 U+1Fxxx supplementary-plane 表情。'
tags=['起点','测试版','评论优化','表情修复','U+F60D','PUA恢复','UTF-16','Emoji码点','Stable 1.2.6基线']
changes=[
 'beta10 真机直接显示 U+F60D，证明至少部分乱码不是缺少 fn 表，而是非 BMP Emoji 被截断为低16位',
 'U+F60D 恰好恢复为 U+1F60D（😍）；新增 U+F000..U+F8FF -> U+1F000..U+1F8FF 的受限恢复',
 '使用手工 surrogate pair 生成字符，避免旧 WebView 对 String.fromCodePoint 的兼容差异',
 'U+2612/FFFD/其它未知 PUA 不猜测，继续保留码点诊断，便于下一轮按真机证据补齐',
 '评论请求/签名/分页、目录、正文、版权、账号、Provider 全部冻结'
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
ni=[e for e in nd.get('items',[]) if not (isinstance(e,dict) and e.get('id')=='qidian-next-beta')]
ni.insert(0,beta_entry(typed=True)); nd['items']=ni
np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bunp=ROOT/'bundles/all-beta.json'; ba=json.loads(bunp.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr
ba=[o for o in ba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)]; ba.insert(0,src)
bunp.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'PUA Emoji恢复'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'真机证据','text':'beta10 将未知字符显示为码点后，真机明确暴露 U+F60D。U+F60D 是 U+1F60D（😍）丢失最高 0x10000 后的低16位。'},
 {'title':'本版修复','text':'评论最终渲染前，U+F000..U+F8FF 私用区字符按 +0x10000 恢复 supplementary-plane 码点，并用 UTF-16 surrogate pair 输出。'},
 {'title':'仍保留诊断','text':'不能由该规则确定的 U+2612、FFFD 或其它未知字符继续显示码点，不做猜测式替换。'},
 {'title':'冻结','text':'评论请求/签名/分页及目录、正文、版权、账号、Provider 均未修改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

logp=ROOT/'docs/RELEASE_LOG.md'; log=logp.read_text(encoding='utf-8')
entry='''## 2026-09-15 · qidian-next 1.2.7-beta11\n- beta10 真机码点诊断抓到 `U+F60D`；这是 `U+1F60D`（😍）截掉最高 `0x10000` 后的低16位。\n- 新增受限 PUA 恢复：`U+F000..U+F8FF -> U+1F000..U+1F8FF`，用 surrogate pair 输出，修复 supplementary-plane Emoji 的 16-bit 截断。\n- 其它未知字符继续显示码点，不猜映射；评论请求链及其它业务域冻结。\n\n'''
if entry.splitlines()[0] not in log: logp.write_text(entry+log,encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hand=hp.read_text(encoding='utf-8')
block='''\n\n## 2026-09-15 · 1.2.7-beta11 评论 Emoji 低16位截断修复\n- beta10 真机明确暴露 `U+F60D`，由此确认至少一类乱码来自 supplementary-plane Emoji 的 16-bit 截断，而不是 fn=1..64 映射缺失。\n- `U+F60D + 0x10000 = U+1F60D`（😍）。beta11 仅在最终评论渲染层将 `U+F000..U+F8FF` 恢复到 `U+1F000..U+1F8FF`。\n- 不能确定的 `U+2612`/FFFD/其它未知码点仍保留诊断，不做盲替换。\n- Stable 1.2.6 不变；未真机确认前不得晋升。\n'''
if '1.2.7-beta11 评论 Emoji 低16位截断修复' not in hand: hp.write_text(hand+block,encoding='utf-8')

report={'version':VERSION,'versionCode':VC,'sha256':sha,'baseline':'1.2.7-beta10','evidence':'U+F60D -> U+1F60D -> 😍','mappingRange':'U+F000..U+F8FF + 0x10000','stableBusinessFrozen':True}
(ROOT/'.staging/qidian-127b11-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
