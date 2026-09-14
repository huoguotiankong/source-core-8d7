import json, hashlib, base64, gzip, re
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta6'; VC=12076; TS='2026-09-14T23:35:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8')); stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
assert '1.2.7-beta5' in str(s.get('bookSourceComment','')), 'beta baseline is not 1.2.7-beta5'

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
assert 'qfEmojiRawCacheV1275' in code and 'qfEmojiRecoverContentV1275' in code, 'beta5 raw-recovery baseline missing'

# beta5 proved that a second request with the old 7.9.394 identity can still return the same
# placeholder characters. Switch only the REVIEW reader signer to the exact reference profile
# used by 妙想天开; keep shared qfDirectSignedRequest untouched for unrelated media/audio code.
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
        /* 妙想天开参考：QDReader 7.9.378/1436，RMX3366/realme，每请求独立 qimei。 */
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

# Never let a previous localStorage decision pin the main comment UI to the old reader_legacy
# response. Legacy remains available only as the existing compatibility/network fallback.
old_pref="function preferred(){try{var v=String(localStorage.getItem('qf_qd_reader_profile_v400')||'');if(v==='reader_ext'||v==='reader_legacy')return v}catch(_e){}return 'reader_ext'}"
assert old_pref in code, 'preferred() block not found'
code=code.replace(old_pref,"function preferred(){return 'reader_ext'}",1)
old_pref2='''    function prefProfile(){
        try{var v=String(localStorage.getItem("qf_qd_reader_profile_v400")||"");if(v==="reader_ext"||v==="reader_legacy")return v;}catch(_e){}
        return "reader_ext";
    }'''
assert old_pref2 in code, 'prefProfile() block not found'
code=code.replace(old_pref2,'''    function prefProfile(){return "reader_ext";}''',1)

# A successful reference-profile paragraph page is authoritative. Do not replace it merely
# because the page has no titled users; doing that reintroduces legacy Content placeholders.
needle='''        var pv=pidTry[pi],a=pullReader(first,pv);
        if(a&&a.rich>0){remember(a.profile);return a;}'''
assert needle in code, 'paragraph profile selection anchor not found'
code=code.replace(needle,'''        var pv=pidTry[pi],a=pullReader(first,pv);
        if(a&&a.profile==='reader_ext'&&a.list&&a.list.length){remember(a.profile);return a;}
        if(a&&a.rich>0){remember(a.profile);return a;}''',1)

# beta5 suspicious-row recovery must use the same reference Reader identity as the primary path.
old_recovery="var req=qfDirectSignedRequest('v2/chapterreview/getparagraphscomments',{"
assert old_recovery in code, 'beta5 recovery request anchor not found'
code=code.replace(old_recovery,"var req=qfReaderSignedRequestV3245('v2/chapterreview/getparagraphscomments',{",1)
old_close="            anchorId:'0',bookId:String(bid),chapterId:String(cid),from:'0',paragraphId:p,pg:pg,pz:'10',type:'0'\n        },false);"
assert old_close in code, 'beta5 recovery request close not found'
code=code.replace(old_close,"            anchorId:'0',bookId:String(bid),chapterId:String(cid),from:'0',paragraphId:p,pg:pg,pz:'10',type:'0'\n        },'reader_ext');",1)

# Hard gates: exact reference identity, raw Content recovery and existing UI behavior all remain.
assert '|7.9.378|1080|1184|1000009|10|1|RMX3366|1436|' in code
assert 'QDReaderAndroid/7.9.378/1436/1000009/realme' in code
assert "qfReaderSignedRequestV3245('v2/chapterreview/getparagraphscomments'" in code
assert 'qfEmojiRecoverContentV1275' in code and 'qfEmojiSuspiciousV1275' in code
assert "raw.Content||raw.content" in code and "safe=safe.replace(/\\[fn=(\\d+)\\]/g" in code
assert "26:'🤪'" in code and "19:'😂'" in code and "64:'🐲'" in code
assert 'qfOfficialBadge' in code and 'avatarFallback' in code
assert 'autoLoadBudget=0' in code and '600' in code
assert code!=old_code

check=ROOT/'.staging/qidian-127b6-review-check.js'; check.write_text(code,encoding='utf-8')
pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta6：真机确认 beta5 的旧身份二次回查仍有大量乱码表情。本版不再改 CSS/字体/映射表：评论主链与异常行恢复链统一改为妙想天开同款 QDReader 7.9.378/1436（RMX3366/realme、逐请求 qimei），优先保留官方原始 [fn=N] 再映射 Emoji；reader_legacy 仅保留兼容回退。beta5 的按评论 ID 原始 Content 恢复继续作为安全网。目录/正文/版权/账号/Provider 全部冻结。'

for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta5 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.7-beta6：评论主链与异常回查统一切换妙想天开同款 QDReader 7.9.378/1436，直接保住原始 [fn=N] 表情 token。'
tags=['起点','测试版','评论优化','表情修复','妙想天开参考','QDReader 7.9.378','原始Content','ID回查','官方标签','10条首屏','滚动分页','Stable 1.2.6基线']
changes=[
 '真机确认 beta5 仍有大量乱码，证明用旧 7.9.394 身份做二次回查仍可能拿到已损坏占位字符',
 '评论 reader_ext 精确切换到妙想天开同款 QDReader 7.9.378/1436 + RMX3366/realme + 每请求独立 qimei',
 '段评主请求成功拿到 reader_ext 列表后直接采用，避免 richness 启发式再次换回 legacy 响应',
 'beta5 的异常行 ID 回查也统一改用 reader_ext；恢复原始 Content 后继续执行 [fn=N]→Emoji 映射',
 '共享 direct signer、目录、正文、版权、账号、Provider 与其它业务域冻结'
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
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'参考客户端评论签名'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'真机结论','text':'beta5 对乱码行按 ID 二次回查仍有大量乱码，说明旧 7.9.394 请求身份本身可能已经拿不到原始 [fn=N]。'},
 {'title':'本版修复','text':'评论主请求与异常行回查统一使用妙想天开同款 QDReader 7.9.378/1436、RMX3366/realme、逐请求 qimei。'},
 {'title':'表情链','text':'目标是让 Argus v2 直接返回含 [fn=N] 的原始 Content，再由现有映射转换 Emoji；不从方框反猜编号。'},
 {'title':'冻结项','text':'beta5 的 ID 精确回查仍保留作安全网；目录、正文、版权、账号、Provider 不变。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

logp=ROOT/'docs/RELEASE_LOG.md'; log=logp.read_text(encoding='utf-8')
entry='''## 2026-09-14 · qidian-next 1.2.7-beta6\n- 真机确认 beta5 仍有大量乱码表情，旧 7.9.394 身份的二次原始 Content 回查不足以恢复。\n- 评论 `reader_ext` 与异常行 ID 回查统一切换为妙想天开同款 QDReader 7.9.378/1436 + RMX3366/realme + 每请求独立 qimei。\n- 成功拿到 reference-profile 评论列表后直接采用，避免启发式退回 legacy 响应；仍保留 beta5 的精确 ID 回查安全网。\n- 不再改 CSS/字体或猜方框编号；继续只对官方原始 `[fn=N]` 做 Emoji 映射。\n- 目录、正文、版权、账号、Provider 冻结；未经真机确认不得晋升 Stable。\n\n'''
if entry.splitlines()[0] not in log: logp.write_text(entry+log,encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hand=hp.read_text(encoding='utf-8')
block='''\n\n## 2026-09-14 · 1.2.7-beta6 评论表情请求身份修复\n- 真机：beta5 的“异常字符 → ID 回查原始 Content”仍有大量乱码，说明旧 QDReader 7.9.394/1526 请求身份可能已在服务端返回占位字符。\n- beta6 仅修改 `review_local_ui`：主评论 signer 切到妙想天开同款 7.9.378/1436 + RMX3366/realme + 每请求 qimei；异常行回查也走同一 `reader_ext` signer。\n- reader_ext 成功返回列表时直接采用，避免 richness 启发式替换为 legacy。reader_legacy 仍留作兼容兜底。\n- 既有 `[fn=N]` Emoji 映射、TitleImage、头像、10条首屏、600px滚动分页、beta5 ID 回查均保留。\n- 目录/正文/版权/账号/Provider 冻结；等待真机验证乱码表情是否明显消失。\n'''
if '## 2026-09-14 · 1.2.7-beta6 评论表情请求身份修复' not in hand: hp.write_text(hand.rstrip()+block+'\n',encoding='utf-8')

report={'version':VERSION,'versionCode':VC,'sha256':sha,'baseline':'1.2.7-beta5','changes':['review reader_ext -> QDReader 7.9.378/1436 RMX3366 realme per-request qimei','suspicious-row recovery uses same reader_ext signer','reader_ext successful list wins before legacy richness fallback'],'frozen':['ruleToc','ruleBookInfo','ruleContent','bookSourceUrl','shared qfDirectSignedRequest']}
(ROOT/'.staging/qidian-127b6-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
