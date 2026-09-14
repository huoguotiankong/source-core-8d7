import json, hashlib, base64, gzip, re
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta5'; VC=12075; TS='2026-09-14T22:55:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8')); stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
assert '1.2.7-beta4' in str(s.get('bookSourceComment','')), 'beta baseline is not 1.2.7-beta4'

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

# beta4 proved that merely preferring raw.Content is insufficient: the current Reader 7.9.394
# profile can already return the custom-face position as a placeholder box. 妙想天开 uses the
# same Argus v2 endpoint but signs as QDReaderAndroid 7.9.378/1436 with a per-request qimei;
# that response keeps literal [fn=N], then replaceEmoji() maps it to Unicode emoji.
# Make our existing reader_ext profile match that request identity exactly, while keeping the
# old legacy profile as a fallback. This automatically covers paragraph comments, author says,
# chapter comments and reply-page calls that already use qfReaderSignedRequestV3245.
new_signer=r'''function qfReaderSignedRequestV3245(path,params,profile){
    params=params||{};profile=String(profile||'reader_ext');
    var parts=[],keys=Object.keys(params||{});
    for(var i=0;i<keys.length;i++){
        var k=keys[i];if(params[k]===undefined)continue;
        parts.push(k+'='+String(params[k]==null?'':params[k]));
    }
    parts.sort();
    var a=parts.join('&'),t=Date.now(),deviceId=qfDirectDeviceId();
    var queryMd5=qfDirectMd5(String(a).toLowerCase());
    var signId=deviceId,infoPlain='',ua='';
    if(profile==='reader_legacy'){
        infoPlain=deviceId+'||||||1||999|'+t;
        ua='Mozilla/mobile QDReaderAndroid/7.9.394/1526/1000009/Android';
    }else{
        /* 妙想天开 / QDReader 7.9.378：每次请求生成独立 qimei。 */
        var now=new Date(t+8*3600*1000);
        function p3(n){n=String(n);while(n.length<3)n='0'+n;return n;}
        var ymdhm=now.getUTCFullYear()+p3(now.getUTCMonth()+1)+p3(now.getUTCDate())+p3(now.getUTCHours())+p3(now.getUTCMinutes());
        var qimei=ymdhm+p3(t%1000)+qfDirectRandomHex(12);
        signId=qimei;
        infoPlain=qimei+'|7.9.378|1080|1184|1000009|10|1|RMX3366|1436|1000009|4|0|'+t+'|1|'+qimei+'|||||0';
        ua='Mozilla/mobile QDReaderAndroid/7.9.378/1436/1000009/realme';
    }
    var signPlain='Rv1rPTnczce|'+t+'|0|'+signId+'||||'+queryMd5+'|f189adc92b816b3e9da29ea304d4a7e4';
    var qdSign=qfDirectTripleDesBase64(signPlain,QF_QD_AUDIO_SIGN_KEY,QF_QD_AUDIO_SIGN_IV);
    var qdInfo=qfDirectTripleDesBase64(infoPlain,QF_QD_AUDIO_INFO_KEY,QF_QD_AUDIO_INFO_IV);
    return {
        url:'https://druidv6.if.qidian.com/argus/api/'+String(path||'').replace(/^\\/+/, '')+'?'+a,
        headers:{
            'QDSign':qdSign,'QDInfo':qdInfo,'tstamp':String(t),
            'User-Agent':ua,'Content-Type':'application/json'
        },
        deviceId:profile==='reader_legacy'?deviceId:signId,profile:profile,timestamp:t
    };
}'''
pat=r"function qfReaderSignedRequestV3245\(path,params,profile\)\{.*?\n\}\nfunction qfDirectAjax"
code,n=re.subn(pat,new_signer+'\nfunction qfDirectAjax',code,count=1,flags=re.S)
assert n==1, f'reader signer replace count={n}'

# Do not let an old localStorage choice pin the UI to reader_legacy. The reference-compatible
# reader_ext is now authoritative; legacy remains only a network/compatibility fallback.
old_pref="function preferred(){try{var v=String(localStorage.getItem('qf_qd_reader_profile_v400')||'');if(v==='reader_ext'||v==='reader_legacy')return v}catch(_e){}return 'reader_ext'}"
assert old_pref in code, 'preferred() block not found'
code=code.replace(old_pref,"function preferred(){return 'reader_ext'}",1)
old_pref2='''    function prefProfile(){
        try{var v=String(localStorage.getItem("qf_qd_reader_profile_v400")||"");if(v==="reader_ext"||v==="reader_legacy")return v;}catch(_e){}
        return "reader_ext";
    }'''
assert old_pref2 in code, 'prefProfile() block not found'
code=code.replace(old_pref2,'''    function prefProfile(){return "reader_ext";}''',1)

# In the ordinary paragraph page, trust a successful reference-profile page even when that
# particular page happens to contain no titled users. Otherwise the old richness heuristic can
# immediately replace it with reader_legacy and lose the literal [fn=N] content again.
needle='''        var pv=pidTry[pi],a=pullReader(first,pv);
        if(a&&a.rich>0){remember(a.profile);return a;}'''
assert needle in code, 'paragraph profile selection anchor not found'
code=code.replace(needle,'''        var pv=pidTry[pi],a=pullReader(first,pv);
        if(a&&a.profile==='reader_ext'&&a.list&&a.list.length){remember(a.profile);return a;}
        if(a&&a.rich>0){remember(a.profile);return a;}''',1)

# Hard gates: exact reference fingerprint + raw Content mapping + existing UI optimizations.
assert '|7.9.378|1080|1184|1000009|10|1|RMX3366|1436|' in code
assert 'QDReaderAndroid/7.9.378/1436/1000009/realme' in code
assert "raw.Content||raw.content" in code and "safe=safe.replace(/\\[fn=(\\d+)\\]/g" in code
assert "26:'🤪'" in code and "19:'😂'" in code and "64:'🐲'" in code
assert 'qfOfficialBadge' in code and 'avatarFallback' in code
assert 'autoLoadBudget=0' in code and 'h-y-v<600' in code and '已加载全部回复' in code
assert code!=old_code

check=ROOT/'.staging/qidian-127b5-review-check.js'; check.write_text(code,encoding='utf-8')
pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta5：继续对照妙想天开明文评论链。确认 beta4 只改 raw.Content 优先级仍不足；本版把评论 Reader 主请求身份从 7.9.394/1526 改为妙想天开同款 7.9.378/1436（RMX3366/realme、逐请求 qimei），让 Argus v2 原始 Content 保留 [fn=N] 后再映射 Emoji。旧 reader_legacy 仅作兼容回退；官方 TitleImage 标签、头像兜底、首屏10条/600px分页全部保留，目录/正文/版权/账号/Provider 不变。'

for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta4 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.7-beta5：评论 Reader 请求身份切换为妙想天开同款 7.9.378/1436，保留原始 [fn=N] 表情 token。'
tags=['起点','测试版','评论优化','妙想天开参考','QDReader 7.9.378','原始Content','Emoji','官方标签','头像兜底','10条首屏','滚动分页','Stable 1.2.6基线']
changes=[
 '继续逐段对照妙想天开：其 getparagraphscomments 使用 QDReaderAndroid 7.9.378/1436 + RMX3366/realme + 每请求独立 qimei',
 '将现有 reader_ext 请求身份精确切换到该参考配置；同一套签名函数自动覆盖段评、作者说、本章说及楼中楼请求',
 '普通段评成功拿到 reader_ext 数据后直接采用，避免因当前页无称号用户而被旧 legacy 响应替换，重新丢失 [fn=N]',
 '继续使用 raw.Content 优先 + 字面 [fn=N]→Emoji 映射；官方 TitleImage 标签和头像兜底保留',
 '首屏10条、无后台预取、600px近底翻页继续保持；目录/版权/正文/账号/Provider 全部冻结'
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
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'参考客户端签名'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'进一步定位','text':'beta4 已经优先 raw.Content，但真机仍显示方框，说明当前 Reader 7.9.394 请求本身拿到的 Content 已不是妙想天开得到的原始 [fn=N]。'},
 {'title':'本版处理','text':'reader_ext 改成妙想天开同款 QDReader 7.9.378/1436、RMX3366/realme、逐请求 qimei；仍请求同一 Argus v2 评论接口。'},
 {'title':'表情链','text':'官方 Content 保留 [fn=N] → 页面 replaceEmoji 映射；不再试图从已经变成方框的字符串反推表情。'},
 {'title':'冻结项','text':'评论 UI/标签/头像/分页保持现状，目录、版权、正文、账号、Provider 均未修改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'; rp.write_text((f"## 2026-09-14 · qidian-next {VERSION}\n- 真机确认 beta4 `raw.Content` 优先后表情仍为方框，说明差异发生在请求返回阶段。\n- 逐段对照妙想天开明文代码后，将评论 `reader_ext` 精确切换为 QDReader 7.9.378/1436 + RMX3366/realme + 每请求 qimei。\n- 同一 signer 覆盖段评、作者说、本章说和楼中楼；旧 reader_legacy 只作兼容回退。\n- 继续使用官方 raw Content 的 `[fn=N]`→Emoji 映射；评论 UI、标签、头像、10条首屏和600px滚动分页保留。\n- 目录、版权、正文、账号、Provider 全部冻结；未经真机确认不得晋升 Stable。\n\n")+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hp.write_text((f"## 2026-09-14 · {VERSION} — 妙想天开同款 Reader 7.9.378 评论请求\n\n- beta4 证明仅调整 canonical Content 优先级不足，当前 7.9.394 Reader 响应本身可能已将起点自定义表情变成占位方框。\n- beta5 将 `qfReaderSignedRequestV3245` 的 `reader_ext` 身份精确对齐妙想天开：7.9.378/1436、RMX3366/realme、每请求独立 qimei。\n- 所有既有评论流继续复用原结构，只替换 Reader 主请求身份；legacy 仍保留为 fallback。\n- 目标是让官方 `Content` 恢复字面 `[fn=N]`，再由已有映射渲染 Emoji。\n\n")+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-127b5-report.json'; report.write_text(json.dumps({
 'version':VERSION,'versionCode':VC,'betaSha256':sha,'baseline':'1.2.7-beta4 / Stable 1.2.6',
 'reference':'妙想天开 plaintext signByUrl + getparagraphscomments',
 'readerExtAppVersion':'7.9.378','readerExtBuild':'1436','readerExtModel':'RMX3366','readerExtBrand':'realme',
 'perRequestQimei':True,'rawOfficialContentFirst':True,'literalFnEmojiMap':True,
 'legacyFallbackPreserved':True,'officialTitleImagePreserved':True,'avatarFallbackPreserved':True,
 'firstPageStrict10Preserved':True,'backgroundPrefetchPages':0,'scrollThresholdPx':600,
 'syntaxGate':'node --check','ruleTocFrozen':True,'ruleBookInfoFrozen':True,'ruleContentFrozen':True,'bookSourceUrlFrozen':True
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
