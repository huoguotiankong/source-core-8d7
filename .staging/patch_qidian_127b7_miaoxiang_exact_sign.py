import json, hashlib, base64, gzip, re
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta7'; VC=12077; TS='2026-09-14T23:58:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8')); stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8')); s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
assert '1.2.7-beta6' in str(s.get('bookSourceComment','')), 'beta baseline is not 1.2.7-beta6'

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
assert 'qfEmojiRawCacheV1275' in code and 'qfEmojiRecoverContentV1275' in code
assert 'QDReaderAndroid/7.9.378/1436/1000009/realme' in code

# beta6 copied the donor version/device identity but still generated QDSign/QDInfo/tstamp
# from ONE shared qimei/timestamp. The actual 妙想天开 qdBuildReq calls signByUrl FOUR
# separate times, so each header is built from an independent qimei/timestamp snapshot.
# Reproduce that exact behavior only for reader_ext. Legacy behavior is left intact.
new_signer=r'''var QF_READER_DONOR_DEVICES_V1277=[
    ['realme','RMX3366'],['OPPO','PHY120'],['Xiaomi','24030PN60C'],['vivo','V2324A'],
    ['HUAWEI','ALN-AL10'],['samsung','SM-S9280'],['Google','Pixel 4 XL'],['HONOR','MAA-AN10']
];
var QF_READER_DONOR_DEVICE_V1277=QF_READER_DONOR_DEVICES_V1277[Math.floor(Math.random()*QF_READER_DONOR_DEVICES_V1277.length)]||QF_READER_DONOR_DEVICES_V1277[0];
function qfReaderSignedRequestV3245(path,params,profile){
    params=params||{};profile=String(profile||'reader_ext');
    var parts=[],keys=Object.keys(params||{});
    for(var i=0;i<keys.length;i++){
        var k=keys[i];if(params[k]===undefined)continue;
        parts.push(k+'='+String(params[k]==null?'':params[k]));
    }
    parts.sort();
    var a=parts.join('&');
    var url='https://druidv6.if.qidian.com/argus/api/'+String(path||'').replace(/^\\/+/, '')+'?'+a;
    var queryMd5=qfDirectMd5(String(a).toLowerCase());
    var deviceId=qfDirectDeviceId();

    if(profile==='reader_legacy'){
        var t=Date.now();
        var infoPlain=deviceId+'||||||1||999|'+t;
        var signPlain='Rv1rPTnczce|'+t+'|0|'+deviceId+'||||'+queryMd5+'|f189adc92b816b3e9da29ea304d4a7e4';
        return {
            url:url,
            headers:{
                'QDSign':qfDirectTripleDesBase64(signPlain,QF_QD_AUDIO_SIGN_KEY,QF_QD_AUDIO_SIGN_IV),
                'QDInfo':qfDirectTripleDesBase64(infoPlain,QF_QD_AUDIO_INFO_KEY,QF_QD_AUDIO_INFO_IV),
                'tstamp':String(t),
                'User-Agent':'Mozilla/mobile QDReaderAndroid/7.9.394/1526/1000009/Android',
                'Content-Type':'application/json'
            },
            deviceId:deviceId,profile:profile,timestamp:t
        };
    }

    var donorBrand=String(QF_READER_DONOR_DEVICE_V1277[0]||'realme');
    var donorModel=String(QF_READER_DONOR_DEVICE_V1277[1]||'RMX3366');
    function p3(n){n=String(n);while(n.length<3)n='0'+n;return n;}
    function donorOne(which){
        /* Exact donor semantics: every qdSign/signByUrl call creates its own ts + qimei. */
        var t=Date.now();
        var now=new Date(t+8*3600*1000);
        var ymdhm=now.getUTCFullYear()+p3(now.getUTCMonth()+1)+p3(now.getUTCDate())+p3(now.getUTCHours())+p3(now.getUTCMinutes());
        var qimei=ymdhm+p3(t%1000)+qfDirectRandomHex(12);
        if(which==='QDSign'){
            var signPlain='Rv1rPTnczce|'+t+'|0|'+qimei+'||||'+queryMd5+'|f189adc92b816b3e9da29ea304d4a7e4';
            return qfDirectTripleDesBase64(signPlain,QF_QD_AUDIO_SIGN_KEY,QF_QD_AUDIO_SIGN_IV);
        }
        if(which==='QDInfo'){
            var infoPlain=qimei+'|7.9.378|1080|1184|1000009|10|1|'+donorModel+'|1436|1000009|4|0|'+t+'|1|'+qimei+'|||||0';
            return qfDirectTripleDesBase64(infoPlain,QF_QD_AUDIO_INFO_KEY,QF_QD_AUDIO_INFO_IV);
        }
        if(which==='tstamp')return String(t);
        if(which==='UA')return 'Mozilla/mobile QDReaderAndroid/7.9.378/1436/1000009/'+donorBrand;
        return '';
    }
    return {
        url:url,
        headers:{
            'QDSign':donorOne('QDSign'),
            'QDInfo':donorOne('QDInfo'),
            'tstamp':String(donorOne('tstamp')),
            'User-Agent':donorOne('UA'),
            'Content-Type':'application/json'
        },
        deviceId:'miaoxiang-exact',profile:profile,timestamp:Date.now(),
        donorBrand:donorBrand,donorModel:donorModel
    };
}'''
pat=r"(?:var QF_READER_DONOR_DEVICES_V1277=.*?\n)?function qfReaderSignedRequestV3245\(path,params,profile\)\{.*?\n\}\nfunction qfDirectAjax"
code,n=re.subn(pat,new_signer+'\nfunction qfDirectAjax',code,count=1,flags=re.S)
assert n==1, f'reader signer replace count={n}'

# Hard gates: donor request semantics changed; everything else from beta6 remains.
assert 'QF_READER_DONOR_DEVICES_V1277' in code
assert "['realme','RMX3366']" in code and "['HONOR','MAA-AN10']" in code
assert "'QDSign':donorOne('QDSign')" in code
assert "'QDInfo':donorOne('QDInfo')" in code
assert "'tstamp':String(donorOne('tstamp'))" in code
assert "'User-Agent':donorOne('UA')" in code
assert 'every qdSign/signByUrl call creates its own ts + qimei' in code
assert "qfReaderSignedRequestV3245('v2/chapterreview/getparagraphscomments'" in code
assert 'qfEmojiRecoverContentV1275' in code and 'qfEmojiSuspiciousV1275' in code
assert "raw.Content||raw.content" in code and "safe=safe.replace(/\\[fn=(\\d+)\\]/g" in code
assert "26:'🤪'" in code and "19:'😂'" in code and "64:'🐲'" in code
assert 'qfOfficialBadge' in code and 'avatarFallback' in code
assert 'autoLoadBudget=0' in code and '600' in code
assert code!=old_code

check=ROOT/'.staging/qidian-127b7-review-check.js'; check.write_text(code,encoding='utf-8')
pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta7：beta6 真机仍有大量乱码。重新逐行核对妙想天开后发现 beta6 只复制了版本/机型，但没有复制其 qdBuildReq 的关键行为：妙想天开对 QDSign、QDInfo、tstamp、UA 分别独立调用 signByUrl，每个调用都会重新生成 ts/qimei。本版只把 review reader_ext 改成该精确请求语义，并恢复妙想天开的 8 组品牌/机型随机池；评论主链和异常 ID 回查自动共用。其余评论 UI、[fn=N] 映射、目录、正文、版权、账号、Provider 全部冻结。'

for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta6 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.7-beta7：按妙想天开真实 qdBuildReq 语义重做评论签名，每个 Header 独立生成 ts/qimei。'
tags=['起点','测试版','评论优化','表情修复','妙想天开精确复刻','qdBuildReq','QDReader 7.9.378','原始Content','ID回查','官方标签','10条首屏','滚动分页','Stable 1.2.6基线']
changes=[
 'beta6 真机仍有大量乱码；重新逐行核对妙想天开后确认 beta6 并非完整复刻 donor 请求行为',
 '妙想天开 qdBuildReq 会分别调用 QDSign/QDInfo/tstamp/UA，每次 signByUrl 都重新生成 ts/qimei；beta7 精确复制这一行为',
 '恢复 donor 的 8 组品牌/机型随机池，并保持同一次模块运行中品牌与机型配对一致',
 '评论主请求与 beta5 异常行 ID 回查均自动复用新的 reader_ext signer；reader_legacy 只保留兼容 fallback',
 '评论 UI、映射表、目录、正文、版权、账号、Provider 与 Stable 业务字段冻结'
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
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'妙想天开 qdBuildReq 精确复刻'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'beta6 真机结论','text':'仍有大量乱码，说明仅复制 QDReader 7.9.378/1436、RMX3366/realme 与单次 qimei 还不等于妙想天开的真实请求。'},
 {'title':'重新核对 donor','text':'妙想天开 qdBuildReq 为 QDSign、QDInfo、tstamp、UA 分别调用 qdSign/signByUrl；每次调用都会独立创建时间戳与 qimei。'},
 {'title':'本版修复','text':'reader_ext 精确复刻上述四次独立签名行为，并恢复 donor 8 组品牌/机型池；主评论和异常 ID 回查共用。'},
 {'title':'冻结项','text':'不改评论 UI 与 Emoji 映射表；目录、正文、版权、账号、Provider 完全不动。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

logp=ROOT/'docs/RELEASE_LOG.md'; log=logp.read_text(encoding='utf-8')
entry='''## 2026-09-14 · qidian-next 1.2.7-beta7\n- beta6 真机仍有大量乱码；重新逐行核对妙想天开后发现此前“同款签名”仍漏掉 qdBuildReq 的关键语义。\n- donor 对 `QDSign` / `QDInfo` / `tstamp` / `User-Agent` 分别调用 `signByUrl`，每次都会独立生成时间戳与 qimei；beta7 精确复刻。\n- 同时恢复 donor 的 8 组品牌/机型随机池；评论主链与异常 ID 回查共用新的 `reader_ext` signer。\n- 不修改评论 UI、Emoji 映射、目录、正文、版权、账号或 Provider；未经真机确认不得晋升 Stable。\n\n'''
if entry.splitlines()[0] not in log: logp.write_text(entry+log,encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hand=hp.read_text(encoding='utf-8')
block='''\n\n## 2026-09-14 · 1.2.7-beta7 妙想天开 qdBuildReq 精确签名语义\n- 真机：beta6 仍有大量乱码，说明固定 7.9.378/1436 + RMX3366/realme + 单次 qimei 不是 donor 的完整行为。\n- 重新核对用户上传的妙想天开：`qdBuildReq` 对 QDSign/QDInfo/tstamp/UA 分别调用 `qdSign -> signByUrl`，而 `signByUrl` 每次都会重新生成 ts/qimei。\n- beta7 只替换 `qfReaderSignedRequestV3245` 的 reader_ext：四个 Header 独立签名快照，并恢复 donor 的 8 组品牌/机型池。\n- 评论主请求与 beta5 异常行 ID 回查都自动复用新 signer；旧 legacy 只作兼容 fallback。\n- 其它评论 UI、[fn=N] 映射、目录、正文、版权、账号、Provider 冻结。若 beta7 仍失败，下一步不要再猜映射，直接做 raw Content 三段诊断。\n'''
if '## 2026-09-14 · 1.2.7-beta7 妙想天开 qdBuildReq 精确签名语义' not in hand: hp.write_text(hand.rstrip()+block+'\n',encoding='utf-8')

report={'version':VERSION,'versionCode':VC,'sha256':sha,'baseline':'1.2.7-beta6','donorFinding':'Miaoxiang qdBuildReq invokes signByUrl separately for QDSign/QDInfo/tstamp/UA; each invocation creates an independent ts/qimei','changes':['reader_ext exact per-header donor signing semantics','restore 8 donor brand/model pairs','primary comments and suspicious-row recovery share exact signer'],'frozen':['ruleToc','ruleBookInfo','ruleContent','bookSourceUrl','shared qfDirectSignedRequest','review UI','emoji map']}
(ROOT/'.staging/qidian-127b7-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
