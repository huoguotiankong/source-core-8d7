import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta1'; VC=12071; TS='2026-09-14T22:05:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

arr=json.loads(STABLE.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
stable=json.loads(json.dumps(s,ensure_ascii=False))
js=str(s.get('jsLib',''))
mark='var QF_MOD38_PACK='; p=js.find(mark); assert p>=0
start=js.find('{',p+len(mark)); depth=0; quote=''; esc=False; end=-1
for i in range(start,len(js)):
    ch=js[i]
    if quote:
        if esc:esc=False
        elif ch=='\\':esc=True
        elif ch==quote:quote=''
        continue
    if ch in ('"',"'"):quote=ch;continue
    if ch=='{':depth+=1
    elif ch=='}':
        depth-=1
        if depth==0:end=i+1;break
assert end>start
pack=json.loads(js[start:end])
raw=pack['review_local_ui']; assert raw.startswith('gz:')
b64=raw[3:]+'='*(-len(raw[3:])%4); code=gzip.decompress(base64.b64decode(b64)).decode('utf-8'); old_code=code

# 1) Match the reference source's true first-page behavior: 10 rows first, no hidden 2-page prefetch.
old="autoLoadBudget=2,autoLoadTimer=null"
assert old in code
code=code.replace(old,"autoLoadBudget=0,autoLoadTimer=null",1)
old="autoLoadBudget=(currentTab==='all'&&currentSort==='default'&&!isAuthor)?2:0;"
assert old in code
code=code.replace(old,"autoLoadBudget=0;",1)
old="if(h-y-v<850)load();"
assert old in code
code=code.replace(old,"if(h-y-v<600)load();",1)

# 2) Reference-style compact reply controls and explicit 'all replies loaded' separator.
old_css='.replyMore{padding:8px 12px 10px 44px;color:var(--sub);font-size:12px;cursor:pointer}'
assert old_css in code
new_css='.replyMore{display:inline-block;margin:8px 0 4px 44px;padding:5px 11px;border-radius:8px;background:var(--soft);color:var(--sub);font-size:12px;cursor:pointer}.replyDone{display:flex;align-items:center;gap:9px;margin:10px 12px 5px 44px;color:var(--muted);font-size:11px}.replyDone:before,.replyDone:after{content:"";height:1px;background:var(--line);flex:1}'
code=code.replace(old_css,new_css,1)

old="if(remain<=0)btn.remove();\n        else btn.textContent='继续加载剩余 '+remain+' 条回复';"
assert old in code
new="if(remain<=0){btn.outerHTML='<div class=\"replyDone\">已加载全部回复</div>';}\n        else btn.textContent='继续加载剩余 '+remain+' 条回复';"
code=code.replace(old,new,1)

old="if(remain>0){\n                h+='<div class=\"replyMore replyMoreLocal\" data-root=\"'+esc(rootId)+'\" data-root-alt=\"\" data-root-list=\"'+esc(rootId)+'\" data-total=\"'+reported+'\" data-reply-page=\"2\">继续加载剩余 '+remain+' 条回复</div>';\n            }"
assert old in code
new="if(remain>0){\n                h+='<div class=\"replyMore replyMoreLocal\" data-root=\"'+esc(rootId)+'\" data-root-alt=\"\" data-root-list=\"'+esc(rootId)+'\" data-total=\"'+reported+'\" data-reply-page=\"2\">继续加载剩余 '+remain+' 条回复</div>';\n            }else{\n                h+='<div class=\"replyDone\">已加载全部回复</div>';\n            }"
code=code.replace(old,new,1)

assert code!=old_code
assert 'autoLoadBudget=0' in code and 'h-y-v<600' in code
assert '已加载全部回复' in code
assert 'pageSize=10' in code

pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta1：在用户已确认的 Stable 1.2.6 上继续参考妙想天开优化评论交互。评论首屏严格只加载 10 条，不再后台自动预取后两页；仅滚动接近底部 600px 时继续分页。楼中楼加载按钮改为紧凑胶囊样式，全部回复加载完成后显示分隔提示。评论接口、TitleInfoList、配图/配音、楼中楼数据链及其它业务全部保持 Stable 1.2.6。'

for k,v in stable.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'):continue
    assert s.get(k)==v,'unexpected stable field changed: '+k
assert s['ruleToc']==stable['ruleToc']; assert s['ruleBookInfo']==stable['ruleBookInfo']; assert s['ruleContent']==stable['ruleContent']; assert s['bookSourceUrl']==stable['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.7-beta1：评论页继续参考妙想天开，改为真正首屏10条、近底部再翻页，并优化楼中楼完成态。'
tags=['起点','测试版','评论优化','妙想天开参考','10条首屏','滚动分页','楼中楼','TitleInfoList','Stable 1.2.6基线']
changes=[
 '基于已真机确认的 Stable 1.2.6，仅修改 review_local_ui',
 '首屏严格只加载10条，取消原来默认后台预取后两页，减少打开评论页时的额外请求和等待',
 '滚动接近页面底部600px时再自动加载下一页，与参考源的按需翻页思路一致',
 '楼中楼继续加载按钮改为紧凑胶囊样式；全部回复加载完成后显示“已加载全部回复”分隔提示',
 '评论请求/解析、TitleInfoList、配图/配音、楼中楼、目录、版权、正文、账号和Provider全部冻结'
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
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'评论交互'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'本版范围','text':'基于已确认 Stable 1.2.6，只继续优化本地评论页交互，不修改请求签名、目录、版权、正文或 Provider。'},
 {'title':'分页','text':'首屏严格10条；取消后台自动预取，只有滚动接近底部600px时才继续加载下一页。'},
 {'title':'楼中楼','text':'继续加载按钮收紧为胶囊样式；全部回复完成后显示明确分隔提示。'},
 {'title':'冻结项','text':'TitleInfoList、头像、时间/IP、点赞、配图、配音、楼中楼数据链，以及目录/正文/账号全部保持 Stable 1.2.6。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'; rp.write_text((f"## 2026-09-14 · qidian-next {VERSION}\n- Stable 1.2.6 晋升后继续开新 Beta，仅优化 `review_local_ui`。\n- 参考妙想天开的按需翻页：首屏固定10条，取消后台默认预取2页；近底部600px再加载下一页。\n- 楼中楼继续按钮收紧，并增加“已加载全部回复”完成分隔提示。\n- 评论请求/解析、TitleInfoList、媒体、目录、版权、正文、账号、Provider 全部冻结。\n- 未经新一轮真机确认不得晋升 Stable。\n\n")+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hp.write_text((f"## 2026-09-14 · {VERSION} — 评论按需分页继续优化\n\n- 基线：Stable 1.2.6。\n- 仅 `review_local_ui` 改动：首屏10条、取消后台预取、底部600px触发下一页、楼中楼完成态提示。\n- 不修改评论接口/解析与其它业务域。\n- 等真机确认后再考虑后续评论视觉细化。\n\n")+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-127b1-report.json'; report.write_text(json.dumps({'version':VERSION,'versionCode':VC,'betaSha256':sha,'baseline':'Stable 1.2.6','changedPackedModule':'review_local_ui','firstPageStrict10':True,'backgroundPrefetchPages':0,'scrollThresholdPx':600,'replyDoneMarker':True,'ruleTocFrozen':True,'ruleBookInfoFrozen':True,'ruleContentFrozen':True,'bookSourceUrlFrozen':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
