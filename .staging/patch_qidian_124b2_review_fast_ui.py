import base64, gzip, hashlib, json
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.4-beta2'; VC=12042; TS='2026-09-13T21:42:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
STABLE_EXPECTED='1eaffa24543b2af58aed1368578368ea326ffb0170338971bde558df725bed87'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'

assert hashlib.sha256(STABLE.read_bytes()).hexdigest()==STABLE_EXPECTED
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
assert s.get('bookSourceUrl')==IDENTITY
assert '1.2.4-beta1' in s.get('bookSourceComment','')
lib=s['jsLib']; marker='var QF_MOD38_PACK='; a=lib.index(marker)+len(marker)
try:b=lib.index(';\nvar QF_MOD38_EXPORTS=',a)
except ValueError:b=lib.index(';var QF_MOD38_EXPORTS=',a)
pack=json.loads(lib[a:b]); before_pack=dict(pack)

def dec(v):
    if not isinstance(v,str) or not v.startswith('gz:'): return v
    x=v[3:]; x+='='*((4-len(x)%4)%4)
    return gzip.decompress(base64.b64decode(x)).decode('utf-8')
def enc(v):
    return 'gz:'+base64.b64encode(gzip.compress(v.encode('utf-8'),compresslevel=9,mtime=0)).decode('ascii').rstrip('=')

assert 'review_local_ui' in pack
ui=dec(pack['review_local_ui']); old_ui=ui
# Reference source uses pz=10. Current UI already declares pageSize=10, but Reader rich-identity request silently forces >=20.
old_pz="pz:String(Math.max(20,Number(ps)||20)),type:'0',anchorId:'0',from:'0'"
new_pz="pz:String(Math.max(1,Number(ps)||10)),type:'0',anchorId:'0',from:'0'"
assert ui.count(old_pz)>=1
ui=ui.replace(old_pz,new_pz,1)

# Reader v2 response already contains ReviewType/RefferCommentId structure on compatible Qidian responses.
# Build roots + embedded replies in one pass. If the response lacks these structural fields, return null and preserve the old Web/mobile chain.
anchor='function fetchPack(action,p,ps,extra){'
assert anchor in ui
helper=r'''/* 1.2.4-beta2：Reader v2 首屏快速结构化。仅当官方返回明确 ReviewType/RefferCommentId 结构时启用；否则无条件回退原稳定链。 */
function qfReaderFastStructV124(pack){
    try{
        if(!pack||!Array.isArray(pack.list)||!pack.list.length)return null;
        var src=pack.list,roots=[],rootMap={},subs={},shape=0;
        function val(o,ks){for(var i=0;i<ks.length;i++){var k=ks[i];if(o&&o[k]!==undefined&&o[k]!==null&&o[k]!=="")return o[k]}return null}
        for(var i=0;i<src.length;i++){
            var it=src[i];if(!it||typeof it!=="object")return null;
            var id=val(it,["Id","id","ReviewId","reviewId","RootReviewId","rootReviewId"]);
            if(id===null)return null;
            var ref=val(it,["RefferCommentId","refferCommentId","RefferReviewId","refferReviewId","RefCommentId","refCommentId"]);
            var rt=val(it,["ReviewType","reviewType"]);
            if(ref!==null||rt!==null)shape++;
            var refN=Number(ref||0),rtN=Number(rt||0),key=String(id);
            if(refN>0&&rtN===2){var rk=String(ref);if(!subs[rk])subs[rk]=[];subs[rk].push(it);continue}
            roots.push(it);rootMap[key]=it;
        }
        if(shape<src.length||!roots.length)return null;
        for(var j=0;j<roots.length;j++){
            var r=roots[j],rid=String(val(r,["Id","id","ReviewId","reviewId","RootReviewId","rootReviewId"]));
            var rp=subs[rid]||[];
            if(rp.length){
                r.Replies=rp;r.replies=rp;r.replyList=rp;r.ReplyList=rp;
                var old=Number(val(r,["ReviewCount","reviewCount","ReplyCount","replyCount"])||0);
                var n=Math.max(old,rp.length);r.ReviewCount=n;r.reviewCount=n;r.ReplyCount=n;r.replyCount=n;
            }
        }
        var out={};for(var k in pack)out[k]=pack[k];out.list=roots;out.source=String(pack.source||"app-v2-reader")+"/fast-struct";out._qfReaderFast=1;
        try{return qfReviewMarkStructPackV502(out)}catch(_m){return out}
    }catch(_e){return null}
}
'''
ui=ui.replace(anchor,helper+anchor,1)
old_fast="var richPack=null;\n    try{richPack=qfAppV2ParagraphPack2971(p,ps,extra);}catch(_qfRich){}"
new_fast=old_fast+"\n    var fastReader=qfReaderFastStructV124(richPack);\n    if(fastReader)return fastReader;"
assert old_fast in ui
ui=ui.replace(old_fast,new_fast,1)

# Final CSS override: keep information-rich badges, remove old reserved right column, align tiny like control on meta row,
# and make nested replies visually closer to the compact official-style reference without changing renderer/data ABI.
css=r'''
/* 1.2.4-beta2：评论信息密度与身份标签最终覆盖。 */
.comment{padding-right:12px!important}.mainRow{padding-right:0!important}.body{flex:1!important;min-width:0!important}.nameRow{height:auto!important;min-height:24px!important;overflow:visible!important;flex-wrap:wrap!important;row-gap:3px!important}.name{max-width:52vw!important}.badges{min-width:0!important;max-width:46vw!important;overflow:hidden!important;gap:3px!important}.badgeImg{height:auto!important;max-height:19px!important;max-width:78px!important}.badgeText{height:18px!important;line-height:17px!important;font-size:10px!important;padding:0 4px!important}.content{width:100%!important;padding-right:0!important}.metaLine{align-items:center!important;gap:7px!important;margin-top:7px!important}.meta{margin-top:0!important}.like{position:static!important;right:auto!important;top:auto!important;transform:none!important;font-size:10px!important;line-height:14px!important;height:16px!important;gap:2px!important}.like svg{width:14px!important;height:14px!important;display:block!important;margin:0!important}.replies{border-left:1px solid rgba(150,154,162,.24)!important;box-shadow:none!important;background:transparent!important;border-top:0!important;border-right:0!important;border-bottom:0!important;border-radius:0!important;padding-left:8px!important}.reply{padding:10px 4px 10px 8px!important}.rBadges{min-width:0!important;overflow:hidden!important}.rBadges .badgeImg{max-height:17px!important;max-width:72px!important}.rMetaLine{align-items:center!important}.rLike{height:14px!important}.rLike svg{width:12px!important;height:12px!important}.replyMore{border-top:0!important;color:#3189d8!important;padding-left:38px!important}@media(max-width:420px){.comment{padding-right:10px!important}.name{max-width:48vw!important}.badges{max-width:45vw!important}.replies{margin-left:50px!important}}
'''
close='</style></head><body>'
assert close in ui
ui=ui.replace(close,css+close,1)
assert ui!=old_ui
assert 'qfReaderFastStructV124' in ui and 'Math.max(1,Number(ps)||10)' in ui and '1.2.4-beta2：评论信息密度' in ui
pack['review_local_ui']=enc(ui)
# Strict module isolation: only review_local_ui may change in the packed runtime.
changed=[k for k in pack if pack[k]!=before_pack.get(k)]
assert changed==['review_local_ui'], changed
lib2=lib[:a]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+lib[b:]
s['jsLib']=lib2
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceComment']='v1.2.4-beta2：评论首屏快通道与身份信息排版优化。在 beta1 目录字数修复基础上，仅修改 review_local_ui：Reader v2 请求严格使用首屏10条；当官方返回明确 ReviewType/RefferCommentId 结构时直接一次请求结构化根评论+当前页回复，缺结构则自动回退原 Web/mobile 稳定链；保留真实 TitleInfoList 身份/等级标签、头像、楼层、时间、IP、图片、语音和楼中楼能力，并收紧卡片正文宽度、点赞和回复层级。正文、目录接口链、搜索、账号、情无/小雨、ruleContent、Rhino loader、本章说及其它 Provider 全部冻结。'
BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source_sha=hashlib.sha256(BETA.read_bytes()).hexdigest()

summary='Beta 1.2.4-beta2：评论首屏 10 条快通道、真实身份标签与评论排版增强。'
tags=['起点','测试版','评论','段评','首屏加速','身份标签','楼中楼','目录字数']
changes=[
 '继承 beta1 的目录 W 字数字段兼容',
 'Reader v2 评论请求由隐藏的至少20条改为严格跟随首屏10条',
 '官方响应含 ReviewType/RefferCommentId 时一次请求直接结构化根评论与当前页回复，缺结构自动回退旧稳定链',
 '保留 TitleInfoList 真实身份/等级标签、头像、楼层、时间、IP、图片、语音及楼中楼',
 '评论正文获得完整可用宽度，点赞缩小并与元信息同排，楼中楼改为更轻的纵向层级',
 '正文、搜索、账号、情无/小雨和其它 Provider 不变'
]
def patch_entry(e,include_type=False):
    e=dict(e or {});e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':source_sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json'})
    if include_type:e['type']='novel'
    return e

mp=ROOT/'manifest.json';m=json.loads(mp.read_text(encoding='utf-8'));m['updatedAt']=TS
for i,e in enumerate(m.get('sources',[])):
    if isinstance(e,dict) and e.get('id')=='qidian-next-beta':
        ne=dict(e);ne.update(patch_entry(e));ne['category']='novel';ne['artifactType']='bookSource';ne['bookSourceUrl']=IDENTITY;m['sources'][i]=ne;break
else:raise AssertionError('manifest beta entry missing')
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for path,typed in [(ROOT/'subscription/beta.json',False),(ROOT/'subscription/novel.json',True)]:
    d=json.loads(path.read_text(encoding='utf-8'));d['updatedAt']=TS;d['generatedAt']=TS
    for i,e in enumerate(d.get('items',[])):
        if e.get('id')=='qidian-next-beta':d['items'][i]=patch_entry(e,typed);break
    else:raise AssertionError(str(path)+' beta missing')
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bund=ROOT/'bundles/all-beta.json';ba=json.loads(bund.read_text(encoding='utf-8'));src=arr[0] if isinstance(arr,list) else arr
for i,o in enumerate(ba):
    if isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY:ba[i]=src;break
else:ba.insert(0,src)
bund.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dp=ROOT/'rss/data/details/beta/qidian-next.json';detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'评论加速','身份标签'], 'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[{'title':'评论首屏','text':'首屏保持 10 条。Reader v2 返回明确评论/回复结构时直接渲染，不再先拿富身份后必等第二条结构接口链。'},{'title':'安全回退','text':'如果 Reader 返回缺少 ReviewType/RefferCommentId 等结构字段，自动回退原 Web/mobile 多级评论链，不把兼容性换成速度。'},{'title':'身份与排版','text':'继续使用真实 TitleInfoList 标签；保留头像、楼层、时间、IP、配图、语音、回复。正文列更宽，点赞与元信息同排，楼中楼层级更轻。'},{'title':'隔离范围','text':'目录仅继承 beta1 字数修复；正文、搜索、账号、情无/小雨、本章说与其它 Provider 不改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
release=(
'## 2026-09-13 · qidian-next 1.2.4-beta2 — 评论首屏快通道与身份排版优化\n'
'- 基于 1.2.4-beta1，仅修改 `review_local_ui`；继承目录 `W` 字数字段修复。\n'
'- 对照妙想天开“首屏 10 条 + 后续分页”思路，修正 qidian-next 虽声明 pageSize=10 但 Reader 富身份请求实际强制至少20条的问题。\n'
'- 新增保守 Reader 快通道：只有官方 v2 响应逐条带明确 `ReviewType/RefferCommentId` 结构时，才在一次请求内组织根评论和当前页回复并直接渲染；否则继续走原 Web/mobile 稳定结构链。\n'
'- UI 保留真实 `TitleInfoList` 身份/等级标签、头像、楼层、时间、IP、配图、语音和楼中楼；正文宽度、点赞对齐和回复纵向层级按参考页收紧。\n'
'- 正文、目录请求链、搜索、账号、情无/小雨、`ruleContent`、Rhino loader、本章说及其它 Provider 全部冻结；Stable 1.2.2 不变。\n\n')
for p in [ROOT/'docs/RELEASE_LOG.md',ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md']:
    old=p.read_text(encoding='utf-8')
    if not old.startswith('## 2026-09-13 · qidian-next 1.2.4-beta2'):p.write_text(release+old,encoding='utf-8')

# Gates
assert hashlib.sha256(STABLE.read_bytes()).hexdigest()==STABLE_EXPECTED
check=json.loads(BETA.read_text(encoding='utf-8'));bs=check[0] if isinstance(check,list) else check
assert bs['bookSourceUrl']==IDENTITY and '1.2.4-beta2' in bs['bookSourceComment']
assert 'ChapterWords","W"]' in bs['jsLib'] or 'ChapterWords","W"' in bs['jsLib']
for p in [mp,ROOT/'subscription/beta.json',ROOT/'subscription/novel.json',bund,dp]:json.loads(p.read_text(encoding='utf-8'))
# Re-decode touched module and smoke-check braces/markers without evaluating Legado-specific JS.
libc=bs['jsLib'];aa=libc.index(marker)+len(marker)
try:bb=libc.index(';\nvar QF_MOD38_EXPORTS=',aa)
except ValueError:bb=libc.index(';var QF_MOD38_EXPORTS=',aa)
pc=json.loads(libc[aa:bb]);uic=dec(pc['review_local_ui'])
assert 'qfReaderFastStructV124' in uic and 'page=1,pageSize=10' in uic and 'Math.max(1,Number(ps)||10)' in uic
assert uic.count('function fetchPack(action,p,ps,extra){')>=1
print('PASS',VERSION,source_sha,'changed_modules',changed)
