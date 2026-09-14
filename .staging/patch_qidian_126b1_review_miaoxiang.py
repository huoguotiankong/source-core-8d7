import json, hashlib, base64, gzip, sys
from pathlib import Path

ROOT=Path('.')
BASE=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
DONOR=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/qidian-review-donor.json')
VERSION='1.2.6-beta1'; VC=12061; TS='2026-09-14T22:15:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'


def src_obj(path):
    arr=json.loads(path.read_text(encoding='utf-8'))
    return arr, (arr[0] if isinstance(arr,list) else arr)

def pack_region(js):
    mark='var QF_MOD38_PACK='
    p=js.find(mark); assert p>=0, 'QF_MOD38_PACK missing'
    start=js.find('{',p+len(mark)); assert start>=0
    depth=0; quote=''; esc=False; end=-1
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
            if depth==0:
                end=i+1; break
    assert end>start
    return start,end,json.loads(js[start:end])

def decode_module(raw):
    if raw.startswith('gz:'):
        b=raw[3:]+'='*(-len(raw[3:])%4)
        return gzip.decompress(base64.b64decode(b)).decode('utf-8')
    return raw

def sha_text(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

arr,s=src_obj(BASE)
_,stable=src_obj(STABLE)
_,donor=src_obj(DONOR)
base_before=json.loads(json.dumps(s,ensure_ascii=False))

# Current accepted Beta keeps the copyright layout; comments are the only new domain.
assert '1.2.5-beta3' in str(s.get('bookSourceComment','')), 'expected beta3 baseline'
assert s.get('bookSourceUrl')==IDENTITY

js=str(s.get('jsLib','')); ds=str(donor.get('jsLib',''))
bs,be,bpack=pack_region(js); ds0,de0,dpack=pack_region(ds)
assert 'review_local_ui' in bpack and 'review_local_ui' in dpack
cur_code=decode_module(bpack['review_local_ui'])
donor_code=decode_module(dpack['review_local_ui'])

# Donor is the previously prepared review-only implementation that was based on 妙想天开.
# Preserve it as a single isolated module so catalog/content/copyright do not move.
assert 'pageSize=10' in donor_code, 'donor must use 10-row UI paging'
assert 'TitleInfoList' in donor_code, 'donor must preserve rich identity labels'
assert 'ReviewType' in donor_code and 'RefferCommentId' in donor_code, 'donor must contain structured Reader review support'
# The donor must remove the old forced 20-row Reader fetch.
assert 'pz:String(Math.max(20,Number(ps)||20))' not in donor_code, 'donor still forces pz>=20'

bpack['review_local_ui']=dpack['review_local_ui']
new_pack=json.dumps(bpack,ensure_ascii=False,separators=(',',':'))
s['jsLib']=js[:bs]+new_pack+js[be:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.6-beta1：参考“妙想天开”优化起点本地评论页。复用此前已准备的 review_local_ui 隔离实现：Reader 富身份请求按首屏10条分页，严格结构可走快速组织通道，保留 TitleInfoList 身份/等级标签、头像、楼层、时间/IP、配图/配音、楼中楼与自动滚动翻页；评论卡片正文宽度、点赞对齐、回复层级进一步收紧。当前已接受的 beta3 版权页保留；Stable 1.2.4 目录、正文、账号与 Provider 全部冻结。'

# Strong isolation: only jsLib packed review_local_ui + display metadata may change from accepted beta3.
for k,v in base_before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v, 'unexpected field changed: '+k
assert s['ruleToc']==base_before['ruleToc']
assert s['ruleBookInfo']==base_before['ruleBookInfo']
assert s['ruleContent']==base_before['ruleContent']
assert s['bookSourceUrl']==base_before['bookSourceUrl']==IDENTITY

# Validate every packed module except review_local_ui remains byte-identical to beta3.
_,_,after_pack=pack_region(s['jsLib'])
for key,val in bpack.items():
    if key=='review_local_ui': continue
    assert after_pack.get(key)==val
# Copyright module must stay exactly beta3.
assert after_pack.get('copyright')==bpack.get('copyright')

BASE.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
beta_sha=hashlib.sha256(BASE.read_bytes()).hexdigest()
summary='Beta 1.2.6-beta1：参考妙想天开优化起点本地评论页，仅替换 review_local_ui；目录/正文/版权等其它业务冻结。'
tags=['起点','测试版','评论优化','段评','本章说','楼中楼','妙想天开参考','10条分页']
changes=[
 '参考妙想天开首屏10条+后续分页思路：Reader 富身份请求不再强制至少20条，减少首屏过取与等待',
 '只有官方 v2 数据具备明确 ReviewType/RefferCommentId 结构时才走快速组织；结构不明确继续使用原稳定 Web/mobile 骨架链',
 '保留真实 TitleInfoList 称号/等级、头像、楼层、时间/IP、点赞、配图、配音、楼中楼与回复分页',
 '评论卡片继续使用推荐/热门/最新、全部/配图/配音与滚动自动加载，并收紧正文宽度、点赞和回复层级排版',
 '沿用用户接受的 1.2.5-beta3 版权页；Stable 1.2.4 的目录、章节时间字数/分卷、正文、账号、Provider 不修改'
]

def entry(old=None,typed=False):
    e=dict(old or {})
    e.update({'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','summary':summary,'channel':'beta','version':VERSION,'updatedAt':TS,'tags':tags,'changelog':changes,'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'detailUrl':DETAIL,'versionCode':VC,'sha256':beta_sha,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json','bookSourceUrl':IDENTITY})
    if typed:e['type']='novel'
    return e

mp=ROOT/'manifest.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['updatedAt']=TS
items=m.setdefault('sources',[]); pos=next((i for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
ne=entry(items[pos] if pos is not None else None); ne['category']='novel'; ne['artifactType']='bookSource'
if pos is None:
    ins=next((i+1 for i,e in enumerate(items) if isinstance(e,dict) and e.get('id')=='qidian-next'),len(items)); items.insert(ins,ne)
else: items[pos]=ne
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bp=ROOT/'subscription/beta.json'; bd=json.loads(bp.read_text(encoding='utf-8')); bd['updatedAt']=TS; bd['generatedAt']=TS
bi=bd.setdefault('items',[]); pos=next((i for i,e in enumerate(bi) if isinstance(e,dict) and e.get('id')=='qidian-next-beta'),None)
if pos is None: bi.insert(0,entry())
else: bi[pos]=entry(bi[pos])
bp.write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

np=ROOT/'subscription/novel.json'; nd=json.loads(np.read_text(encoding='utf-8')); nd['updatedAt']=TS; nd['generatedAt']=TS
ni=nd.setdefault('items',[]); ni[:]=[e for e in ni if not (isinstance(e,dict) and e.get('id') in ('qidian-next','qidian-next-beta'))]; ni.insert(0,entry(typed=True))
np.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bun=ROOT/'bundles/all-beta.json'; ba=json.loads(bun.read_text(encoding='utf-8')); src=arr[0] if isinstance(arr,list) else arr
ba=[o for o in ba if not (isinstance(o,dict) and o.get('bookSourceUrl')==IDENTITY)]; ba.insert(0,src)
bun.write_text(json.dumps(ba,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

dp=ROOT/'rss/data/details/beta/qidian-next.json'
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'评论页优化'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'本版范围','text':'本版只替换起点本地评论 UI 模块 review_local_ui。目录、正文、账号、Provider 和已接受的 beta3 版权页不修改。'},
 {'title':'妙想天开参考点','text':'首屏按10条加载；Reader v2 明确结构时直接组织根评论/回复；保留真实身份标签、媒体、楼中楼，滚动接近底部自动加载下一页。'},
 {'title':'兼容策略','text':'快速通道只在 ReviewType/RefferCommentId 结构明确时启用，否则继续使用原 Web/mobile 稳定骨架链，避免为了速度牺牲回复完整度。'},
 {'title':'重点测试','text':'请重点比较首次打开速度、推荐/热门/最新切换、滚动翻页、楼中楼、身份标签、配图和配音。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'; old=rp.read_text(encoding='utf-8')
release=(f"## 2026-09-14 · qidian-next {VERSION} — 妙想天开评论页参考优化\n"
'- 用户接受 1.2.5-beta3 版权页后，开发域切换到 Review；本版从当前 Beta 继续，但严格只替换 `review_local_ui`。\n'
'- 复用此前以“妙想天开”为参考准备的评论模块：Reader 富身份首屏10条、严格结构快通道、真实 TitleInfoList、楼中楼/媒体与滚动分页。\n'
'- 快通道仅在 `ReviewType/RefferCommentId` 明确时启用；否则继续走成熟 Web/mobile 骨架，保护回复结构。\n'
'- Stable 1.2.4 目录/正文/账号/Provider 均冻结；当前 Beta 保留 beta3 版权页。\n\n')
rp.write_text(release+old,encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hold=hp.read_text(encoding='utf-8')
handoff=(f"## 2026-09-14 · {VERSION} 评论页参考妙想天开优化\n"
'- 用户对 1.2.5-beta3 版权页表示“就这样吧”，当前 Beta 在此基础上转入 Review 域。\n'
'- 本版只替换 `review_local_ui`，donor 来自此前 1.2.4-beta3 中已经隔离准备的妙想天开参考实现。\n'
'- 目标：Reader 首屏10条、严格结构快通道、TitleInfoList 富身份、楼中楼/媒体完整、滚动自动翻页；结构不明时回退稳定 Web/mobile 骨架。\n'
'- Stable 1.2.4 目录主链、正文、账号/Provider 与 beta3 copyright 模块冻结。未真机确认评论页前不得晋升 Stable。\n\n')
hp.write_text(handoff+hold,encoding='utf-8')

report={
 'version':VERSION,'versionCode':VC,'betaSha256':beta_sha,
 'baseline':'1.2.5-beta3','donorCommit':'a4b26b8435c1bc49a7da7de976f178a90b7b2925',
 'changedPackedModule':'review_local_ui','currentModuleSha256':sha_text(cur_code),'donorModuleSha256':sha_text(donor_code),
 'ruleTocFrozen':s['ruleToc']==base_before['ruleToc'],'ruleBookInfoFrozen':s['ruleBookInfo']==base_before['ruleBookInfo'],'ruleContentFrozen':s['ruleContent']==base_before['ruleContent'],
 'bookSourceUrlFrozen':s['bookSourceUrl']==IDENTITY,'copyrightFrozen':after_pack.get('copyright')==bpack.get('copyright'),
 'donorMarkers':{'pageSize10':'pageSize=10' in donor_code,'richTitleInfo':'TitleInfoList' in donor_code,'structuredFastPath':('ReviewType' in donor_code and 'RefferCommentId' in donor_code),'forced20Removed':'pz:String(Math.max(20,Number(ps)||20))' not in donor_code}
}
(ROOT/'.staging/qidian-126b1-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
