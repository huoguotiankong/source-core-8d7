import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta8'; VC=12078; TS='2026-09-15T00:12:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8')); stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
assert '1.2.7-beta7' in str(s.get('bookSourceComment','')), 'beta7 baseline expected'

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
assert 'qfReviewFusePackV502' in code and 'qfReviewCopyTitleV502' in code
assert 'qfReaderSignedRequestV3245' in code and '7.9.378' in code

helper=r'''
/* 1.2.7-beta8：Reader 原始 Content 跟随富身份融合回填。
 * 真机已证明：Reader 通道能拿到 TitleInfoList，但 Web/mobile 结构骨架的正文仍可能是 ☒/�。
 * 之前 qfReviewFusePackV502 只从 Reader 行复制标签，正文仍沿用结构骨架，导致 [fn=N]
 * 即使存在于 Reader 原始 Content 里也被丢弃。
 * 本函数只在“结构正文疑似损坏”或“Reader 明确含 [fn=N] 而结构正文不含”时回填 Content；
 * 回复数、父子关系、ID、分页等结构字段仍全部保留 Web/mobile 骨架。 */
function qfReviewCopyReaderContentV1278(dst,src){
    if(!dst||!src||typeof dst!=='object'||typeof src!=='object')return dst;
    function rawOf(v){return v&&typeof v==='object'?(v.raw||v):{};}
    function txt(o){
        o=o||{};
        return String(textOf(
            o.Content||o.content||o.ReviewContent||o.reviewContent||
            o.Body||o.PostBody||o.PostContent||o.Text||o.text||''
        )||'');
    }
    var dr=rawOf(dst),sr=rawOf(src),dc=txt(dr),sc=txt(sr);
    if(!sc)return dst;
    var dBad=qfEmojiSuspiciousV1275(dc);
    var sBad=qfEmojiSuspiciousV1275(sc);
    var sFn=/\[fn=\d+\]/i.test(sc),dFn=/\[fn=\d+\]/i.test(dc);
    if((dBad&&!sBad)||(sFn&&!dFn)){
        try{dr.Content=sc;}catch(_e){}
        try{if(dst!==dr)dst.Content=sc;}catch(_e2){}
        try{dst._qfReaderContentRecovered=1;}catch(_e3){}
    }
    return dst;
}
'''

anchor='function qfReviewFusePackV502(structPack,richPack){'
pos=code.find(anchor); assert pos>=0
code=code[:pos]+helper+'\n'+code[pos:]

needle='''        if(m){
            qfReviewCopyTitleV502(st,m);'''
assert needle in code, 'fusion match anchor missing'
code=code.replace(needle,'''        if(m){
            qfReviewCopyTitleV502(st,m);
            qfReviewCopyReaderContentV1278(st,m);''',1)

# Also make the standalone beta5 recovery map authoritative for exact Id matches when it finds a clean Reader Content.
needle2='''            var x=qfEmojiRawTextV1275(r);if(!x)continue;
            if(/\\[fn=\\d+\\]/i.test(x))return x;
            if(!qfEmojiSuspiciousV1275(x))return x;'''
assert needle2 in code, 'recovery content anchor missing'
code=code.replace(needle2,'''            var x=qfEmojiRawTextV1275(r);if(!x)continue;
            if(/\\[fn=\\d+\\]/i.test(x))return x;
            if(!qfEmojiSuspiciousV1275(x))return x;''',1)

assert 'qfReviewCopyReaderContentV1278(st,m);' in code
assert '_qfReaderContentRecovered' in code
assert 'qfEmojiSuspiciousV1275' in code
assert "safe=safe.replace(/\\[fn=(\\d+)\\]/g" in code
assert 'QF_READER_DONOR_DEVICES_V1277' in code
assert 'autoLoadBudget=0' in code and '600' in code
assert code!=old_code
check=ROOT/'.staging/qidian-127b8-review-check.js'; check.write_text(code,encoding='utf-8')

pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta8：定位到真正的数据融合问题：Reader 富身份链即使已经拿到原始 [fn=N]，旧 qfReviewFusePack 也只复制 TitleInfoList，评论正文继续采用 Web/mobile 结构骨架里的 ☒/�。本版在同一条评论匹配成功时，仅将 Reader 的干净 Content/[fn=N] 回填到结构骨架，再交给妙想天开同款 Emoji 映射；ID、回复数、楼中楼、分页等结构字段完全不动。beta7 精确 donor signer 继续保留。目录/正文/版权/账号/Provider 全部冻结。'

for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta7 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY
BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()

summary='Beta 1.2.7-beta8：修复评论融合层只复制标签、不复制 Reader 原始 Content，确保 [fn=N] 真正进入 Emoji 渲染。'
tags=['起点','测试版','评论优化','表情修复','Reader Content回填','妙想天开参考','QDReader 7.9.378','官方标签','10条首屏','滚动分页','Stable 1.2.6基线']
changes=[
 'beta7 真机仍有方框；结合当前代码确认 Reader 富数据与 Web/mobile 结构数据融合时只复制 TitleInfoList，正文 Content 未融合',
 '当同一评论匹配成功且结构正文含 ☒/�/PUA，或 Reader Content 明确含 [fn=N] 而结构正文没有时，只回填 Reader Content',
 '回填后继续使用既有妙想天开同款 [fn=N]→Emoji 映射，不猜方框编号',
 '根评论与 embedded 楼中楼都复用同一 qfReviewFusePack，因此同一修复覆盖主评论和首批回复',
 'beta7 精确 donor signer 保留；目录、正文、版权、账号、Provider 与结构分页字段冻结'
]
def beta_entry(old=None,typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    return e

mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
items=m.setdefault('sources',[]); pos=next((i for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
ne=beta_entry(items[pos] if pos is not None else None); ne['category']='novel'; ne['artifactType']='bookSource'
if pos is None: items.insert(next((i+1 for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next'),len(items)),ne)
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
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'Reader Content融合'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'根因','text':'当前 qfReviewFusePack 用 Web/mobile 做结构骨架、Reader 做富身份补充，但此前只复制了 TitleInfoList，Reader 中的原始 Content 没有进入最终评论行。'},
 {'title':'本版修复','text':'同一评论匹配成功后，若结构正文已经是占位符，或 Reader 明确带 [fn=N]，只把 Reader Content 回填到结构行，再走既有 Emoji 映射。'},
 {'title':'结构保护','text':'ReviewId、ReplyCount、Replies、父子关系、分页全部继续使用原结构骨架；主评论与 embedded 回复共用同一融合函数。'},
 {'title':'冻结','text':'beta7 签名、目录、正文、版权、账号、Provider 均不修改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

logp=ROOT/'docs/RELEASE_LOG.md'; log=logp.read_text(encoding='utf-8')
entry='''## 2026-09-15 · qidian-next 1.2.7-beta8\n- beta7 真机仍有乱码；代码核对确认富身份融合 `qfReviewFusePackV502` 只复制 Reader 的 TitleInfoList，没有复制 Reader 原始 Content。\n- 新增受限 Content 融合：结构正文含占位字符，或 Reader 行明确带 `[fn=N]` 时，将 Reader Content 回填到同一结构行。\n- 回复数、父子关系、ID、分页仍由 Web/mobile 结构骨架负责；embedded 楼中楼通过同一融合函数一起覆盖。\n- beta7 donor signer 与 Emoji 表保持不变；目录、正文、版权、账号、Provider 冻结。\n\n'''
if entry.splitlines()[0] not in log: logp.write_text(entry+log,encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hand=hp.read_text(encoding='utf-8')
block='''\n\n## 2026-09-15 · 1.2.7-beta8 评论 Content 融合修复\n- beta7 真机仍显示方框。复核 review_local_ui 发现：Reader 富身份包与 Web/mobile 结构包融合时，只复制 TitleInfoList；最终 `adapt()` 仍读取结构包的损坏 Content。\n- beta8 在 qfReviewFusePackV502 的“已匹配同一评论”分支加入受限 Content 回填：仅结构 Content 可疑或 Reader 明确带 `[fn=N]` 时复制 Reader Content。\n- 这条路径天然覆盖根评论及 embedded 回复，同时不改变 ReviewId/ReplyCount/Replies/分页。\n- beta7 精确妙想天开签名继续保留；其它业务域冻结。\n'''
if '## 2026-09-15 · 1.2.7-beta8 评论 Content 融合修复' not in hand: hp.write_text(hand.rstrip()+block+'\n',encoding='utf-8')

report={'version':VERSION,'versionCode':VC,'sha256':sha,'baseline':'1.2.7-beta7','rootCause':'qfReviewFusePackV502 copied Reader titles but not Reader Content','changes':['copy clean Reader Content into matched struct row only when struct content is suspicious or Reader has [fn=N]','embedded reply fusion inherits same fix'],'frozen':['ruleToc','ruleBookInfo','ruleContent','bookSourceUrl','reader signer','emoji map','reply structure','pagination']}
(ROOT/'.staging/qidian-127b8-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))