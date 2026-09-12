import json, hashlib, re
from pathlib import Path

ROOT = Path('.')
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
EXPECTED_BETA = '41066a9d81525c1093e451ac703db7e36946aee316f372a666477ab74cf33623'
EXPECTED_STABLE = '1ee474c209b48d069344ffa4409379a0d39012cbaf2acecbd5ffcaba5404ab7e'
VERSION = '1.2.2-beta3'
VC = 12023
TODAY = '2026-09-12'
NOW = '2026-09-12T20:35:00+08:00'
RAW = f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP = f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT = 'legado://import/bookSource?src=' + RAW
DETAIL = 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json'

if hashlib.sha256(STABLE.read_bytes()).hexdigest() != EXPECTED_STABLE:
    raise SystemExit('Stable changed; refuse Beta3 patch')
if hashlib.sha256(BETA.read_bytes()).hexdigest() != EXPECTED_BETA:
    raise SystemExit('Beta2 baseline changed; refuse Beta3 patch')

arr = json.loads(BETA.read_text(encoding='utf-8'))
s = arr[0] if isinstance(arr, list) else arr
js = s['jsLib']

# Hard domain isolation: this Beta may only change jsLib review routing + source comment.
frozen = {}
for key in ['ruleContent', 'ruleToc', 'ruleSearch', 'ruleBookInfo', 'ruleExplore', 'loginUrl', 'loginUi']:
    if key in s:
        frozen[key] = json.dumps(s[key], ensure_ascii=False, sort_keys=True, separators=(',', ':'))

# Miaoxiang source lesson, adapted to qidian-next's existing signed Review transport:
# direct Argus getchapterrepagesummary gives the whole chapter's paragraph-count map in one request.
FAST_HELPER = r'''function qfReviewFastSummaryV1223(ctx,bid,cid){
    bid=String(bid||'');cid=String(cid||'');
    var out={ok:false,items:[],rows:[],title:null,valid:0,source:'ARGUS-REPAGE'};
    if(!bid||!cid)return out;
    var key='fast-summary-v1223|'+bid+'|'+cid;
    try{
        var hit=QF_ReviewCache.get(key,300000);
        if(hit&&hit.ok&&Array.isArray(hit.items))return hit;
    }catch(_cacheGet){}
    try{
        var r=QF_ReviewApi.request(ctx,'v1/chapterreview/getchapterrepagesummary',{bookId:bid,chapterId:cid},3800);
        if(!r||!r.ok)return out;
        var root=r.root||{},data=(root.Data!==undefined?root.Data:(root.data!==undefined?root.data:(r.data||{})))||{};
        var box=data.Getparagraphscommentcounts||data.getparagraphscommentcounts||data.GetParagraphsCommentCounts||{};
        var list=box.DataList||box.dataList||box.List||box.list||[];
        if(!Array.isArray(list)){try{list=Java.from(list);}catch(_java){list=[];}}
        out.rows=list;
        var seen={};
        for(var i=0;i<list.length;i++){
            var x=list[i]||{},rawPid=(x.ParagraphId!==undefined?x.ParagraphId:x.paragraphId),pid=Number(rawPid);
            var tc=Number(x.TextCount!==undefined?x.TextCount:(x.textCount!==undefined?x.textCount:0))||0;
            var cc=Number(x.CommentCount!==undefined?x.CommentCount:(x.commentCount!==undefined?x.commentCount:0))||0;
            var cnt=tc>0?tc:cc;
            if(pid===-1&&cnt>0){out.title=x;continue;}
            if(!(pid>0)||!(cnt>0))continue;
            var rid=String(x.ReviewId||x.reviewId||x.RootReviewId||x.rootReviewId||'');
            var it={paragraphId:pid,segmentId:pid,count:cnt,reviewId:rid,hot:!!(x.IsHotSegment||x.isHotSegment||x.IsHot||x.isHot),raw:x};
            var sk=String(pid);
            if(!seen[sk]||cnt>Number(seen[sk].count||0))seen[sk]=it;
        }
        for(var k in seen)if(Object.prototype.hasOwnProperty.call(seen,k))out.items.push(seen[k]);
        out.items.sort(function(a,b){return Number(a.paragraphId||0)-Number(b.paragraphId||0);});
        out.valid=out.items.length>0?1:0;
        out.ok=true;
        try{QF_ReviewCache.put(key,out);}catch(_cachePut){}
        try{QF_Diagnostic.event(ctx,'review','fast-summary','argus-repage',true,0,'rows='+list.length+' valid='+out.items.length,'info','');}catch(_diag){}
    }catch(e){
        try{QF_Diagnostic.warn(ctx,'review','fast-summary','argus-repage',e);}catch(_warn){}
    }
    return out;
}'''

anchor = 'var QF_ReviewClient=(function(){'
if js.count(anchor) != 1:
    raise SystemExit('QF_ReviewClient anchor count != 1')
if 'function qfReviewFastSummaryV1223' in js:
    raise SystemExit('fast summary helper already present')
js = js.replace(anchor, FAST_HELPER + '\n\n' + anchor, 1)

# Local paragraph-summary fast path: successful non-empty direct Argus map wins;
# any empty/transport/schema issue falls through to the mature www/m/read mirror chain.
fn = 'function summary(ctx,bid,cid,isPaid){'
p = js.find(fn, js.find(anchor))
if p < 0:
    raise SystemExit('QF_ReviewClient.summary missing')
needle = 'var j=qfAjaxJavaV20(ctx);if(!j)return [];'
q = js.find(needle, p, p + 5000)
if q < 0:
    raise SystemExit('summary ajax anchor missing')
fast_path = r'''var fast1223=qfReviewFastSummaryV1223(ctx,bid,cid);
        if(fast1223&&fast1223.ok&&Array.isArray(fast1223.items)&&fast1223.items.length){
            try{QF_ReviewCache.put(cacheKey,{items:fast1223.items,valid:Number(fast1223.valid||1),source:'ARGUS-REPAGE'});}catch(_fput){}
            var fa=fast1223.items;fa._qfValidReview=Number(fast1223.valid||1);return fa;
        }
        '''
js = js[:q] + fast_path + js[q:]

# QW/Xiaoyu server mode: bubble/count metadata prefers the same official one-shot map;
# full comment detail page/provider remains unchanged. If official fast map fails, keep Beta2 server fallback.
def replace_fn(text, name, new):
    p = text.find('function ' + name)
    if p < 0:
        raise SystemExit('missing ' + name)
    b = text.find('{', p)
    dep = 0
    ins = None
    esc = False
    i = b
    while i < len(text):
        c = text[i]
        if ins:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == ins:
                ins = None
            i += 1
            continue
        if c in "'\"`":
            ins = c
        elif c == '{':
            dep += 1
        elif c == '}':
            dep -= 1
            if dep == 0:
                return text[:p] + new + text[i+1:]
        i += 1
    raise SystemExit('unterminated ' + name)

QW_COUNTS = r'''function qfQwReviewCountsV1214(ctx,bid,cid){
  var out={ok:false,list:[],title:null,chapter:0,rawCount:0,metaSource:''};
  try{
    var fast=(typeof qfReviewFastSummaryV1223==='function')?qfReviewFastSummaryV1223(ctx,bid,cid):null;
    if(fast&&fast.ok&&Array.isArray(fast.rows)&&fast.rows.length){
      out.rawCount=fast.rows.length;out.metaSource='ARGUS-REPAGE';
      for(var fi=0;fi<fast.rows.length;fi++){
        var fx=fast.rows[fi]||{},fr=(fx.ParagraphId!==undefined?fx.ParagraphId:fx.paragraphId),fpid=Number(fr);
        var ft=Number(fx.TextCount!==undefined?fx.TextCount:(fx.textCount!==undefined?fx.textCount:0))||0;
        var fc=Number(fx.CommentCount!==undefined?fx.CommentCount:(fx.commentCount!==undefined?fx.commentCount:0))||0;
        var fcnt=ft>0?ft:fc;
        if(fpid===-1&&fcnt>0)out.title=fx;
        if(fpid>0&&fcnt>0){fx.__qfCount=fcnt;out.list.push(fx);}
      }
      if(out.list.length||out.title){
        out.ok=true;out.chapter=out.title?(Number(out.title.TextCount||out.title.textCount||out.title.CommentCount||out.title.commentCount||0)||0):0;
        try{ctx.java.log('[QW-RV] source=ARGUS-REPAGE rows='+out.rawCount+' para='+out.list.length+' title='+(out.title?1:0)+' bid='+bid+' cid='+cid)}catch(_flog){}
        return out;
      }
    }
  }catch(_fastErr){}
  var url='https://full.hnxianxin.cn/qd/review.php?bookId='+encodeURIComponent(bid)+'&chapterId='+encodeURIComponent(cid),raw='';
  try{
    raw=qfQwAjaxV1214(ctx,url);
    if(!raw){try{ctx.java.log('[QW-RV] empty_response bid='+bid+' cid='+cid)}catch(_0){}return out;}
    var j=JSON.parse(raw||'{}'),d=[];
    try{
      var a=(j.Data&&j.Data.Getparagraphscommentcounts)||(j.data&&j.data.Getparagraphscommentcounts)||j.Getparagraphscommentcounts||j.getparagraphscommentcounts||{};
      d=a.DataList||a.dataList||a.List||a.list||j.DataList||j.dataList||[];
      if(!Array.isArray(d)&&Array.isArray(a))d=a;
      if(!Array.isArray(d))d=[];
    }catch(_1){d=[];}
    out.rawCount=d.length;out.metaSource='QW-SERVER';
    for(var i=0;i<d.length;i++){
      var x=d[i]||{},rp=(x.ParagraphId!==undefined?x.ParagraphId:x.paragraphId),pid=Number(rp);
      var tc=Number(x.TextCount!==undefined?x.TextCount:(x.textCount!==undefined?x.textCount:0))||0;
      var cc=Number(x.CommentCount!==undefined?x.CommentCount:(x.commentCount!==undefined?x.commentCount:0))||0;
      var cnt=tc>0?tc:cc;
      if(pid===-1&&cnt>0)out.title=x;
      if(pid>0&&cnt>0){x.__qfCount=cnt;out.list.push(x);}
    }
    out.ok=d.length>0;out.chapter=out.title?(Number(out.title.TextCount||out.title.textCount||out.title.CommentCount||out.title.commentCount||0)||0):0;
    try{ctx.java.log('[QW-RV] source=QW-SERVER rows='+d.length+' para='+out.list.length+' title='+(out.title?1:0)+' bid='+bid+' cid='+cid)}catch(_2){}
  }catch(e){try{ctx.java.log('[QW-RV] parse_fail '+e+' bid='+bid+' cid='+cid)}catch(_3){}}
  return out;
}'''
js = replace_fn(js, 'qfQwReviewCountsV1214', QW_COUNTS)

# Review-domain invariants.
assert js.count('function qfReviewFastSummaryV1223') == 1
assert js.count("'v1/chapterreview/getchapterrepagesummary'") >= 1
assert "source=ARGUS-REPAGE" in js
assert "source=QW-SERVER" in js
assert 'https://full.hnxianxin.cn/qd/review.php?bookId=' in js
assert js.count('function qfQwDecorateV1214') == 1
assert js.count('function qfContentEntryV38') == 1

s['jsLib'] = js
s['bookSourceComment'] = ('v1.2.2-beta3：借鉴“妙想天开”当前上传版的官方评论轻量路径，新增 '
    'Argus getchapterrepagesummary 单章段评计数快通道。本地段评优先复用一次性章节计数图，失败无条件回落原 www/m/read 稳定链；'
    '情无/小雨服务器模式仅把“气泡位置/数量元数据”改为官方快通道优先，点击后的完整评论 Provider 保持不变。'
    '正文、目录、搜索、账号和 Stable 1.2.1 全部冻结。')

for key, before in frozen.items():
    after = json.dumps(s[key], ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    if after != before:
        raise SystemExit('frozen field changed: ' + key)

BETA.write_text(json.dumps(arr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sha = hashlib.sha256(BETA.read_bytes()).hexdigest()

entry = {
    'id':'qidian-next-beta','name':'🌈 起点增强 · Beta','category':'novel','artifactType':'bookSource','channel':'beta',
    'version':VERSION,'versionCode':VC,'updatedAt':TODAY,'sourcePath':'sources/novel/qidian-next/qidian-next-beta.json',
    'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,
    'summary':'Beta3：借鉴妙想天开直连 Argus 的单章段评计数快通道；本地段评与情无/小雨气泡优先复用官方章节计数图，失败保持原链回退。Stable 1.2.1 与正文/目录冻结。',
    'tags':['起点','测试版','本地段评','情无','小雨服务器','Argus','GetChapterRePageSummary','段评气泡','正文冻结','目录冻结'],
    'changelog':[
        '新增 v1/chapterreview/getchapterrepagesummary 官方快通道，一次请求取得整章 ParagraphId/TextCount 计数图',
        '本地段评 summary 非空快命中直接写入既有 ReviewCache；接口空/失败继续走原 www/m/read 镜像链',
        '情无/小雨仅将气泡元数据改为官方快通道优先；完整评论点击页与服务器 Provider 不变，官方快通道失败继续回退 review.php',
        '妙想天开的 strategy=3 神评与 getchapteractivity 本章说只纳入后续评估，本版不替换现有成熟热评/本章说链',
        '当前 qidian-next 目录已有 APP v3 + getsimple + pager + Web fallback + 缓存体系，本版不改目录，避免跨域回归',
        'Stable 1.2.1、正文、目录、搜索、账号及其它 Provider 不变'
    ],
    'sha256':sha
}

def isbeta(x):
    return isinstance(x, dict) and x.get('id') == 'qidian-next-beta'

def replace_entry(path, extra=None):
    data = json.loads(path.read_text(encoding='utf-8'))
    items = data.get('items', [])
    done = False
    for i, x in enumerate(items):
        if isbeta(x):
            v = dict(entry)
            if extra: v.update(extra)
            items[i] = v
            done = True
            break
    if not done:
        v = dict(entry)
        if extra: v.update(extra)
        items.insert(1, v)
    data['updatedAt'] = NOW
    if 'generatedAt' in data:
        data['generatedAt'] = NOW
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

replace_entry(ROOT/'subscription/beta.json', {'detailUrl':DETAIL})
replace_entry(ROOT/'subscription/novel.json', {'detailUrl':DETAIL, 'type':'novel'})

mp = ROOT/'manifest.json'
m = json.loads(mp.read_text(encoding='utf-8'))
found = False
for i, x in enumerate(m.get('sources', [])):
    if isbeta(x):
        m['sources'][i] = dict(entry)
        found = True
        break
if not found:
    m.setdefault('sources', []).append(dict(entry))
m['updatedAt'] = NOW
mp.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

bp = ROOT/'bundles/all-beta.json'
bd = json.loads(bp.read_text(encoding='utf-8'))
qobj = arr[0] if isinstance(arr, list) else arr
replaced = False
for i, x in enumerate(bd):
    if isinstance(x, dict) and x.get('bookSourceUrl') == qobj.get('bookSourceUrl'):
        bd[i] = qobj
        replaced = True
        break
if not replaced:
    bd.append(qobj)
bp.write_text(json.dumps(bd, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

detail = {
    'kind':'source','title':'🌈 起点增强 · Beta',
    'summary':'1.2.2-beta3：借鉴妙想天开当前上传版的 Argus 段评计数快路径，先用一次官方章节摘要请求建立段评气泡索引；失败保持原链回退。正文与目录冻结。',
    'badges':['Beta','1.2.2-beta3','Argus段评快通道','本地段评','气泡索引','正文冻结','目录冻结'],
    'sections':[
        {'title':'本版改进','text':'本地段评 summary 与情无/小雨气泡元数据优先复用 v1/chapterreview/getchapterrepagesummary 的 Getparagraphscommentcounts.DataList；只要直连非空即可跳过较慢的 Web 镜像摘要。'},
        {'title':'回退策略','text':'官方快通道失败、格式异常或合法空时，不把空结果当作权威，继续执行 Beta2 原有 www/m/read 或情无 review.php 链，避免再次出现“整章无气泡”。'},
        {'title':'未跨域改动','text':'当前目录已经具备 APP v3/getsimple/pager/Web fallback、多层缓存与完整度诊断，整体能力强于妙想天开的单一 v1 chapterlist。本版只记录可借鉴点，不改目录。'},
        {'title':'待真机验证','text':'重点观察：正文是否仍正常、气泡出现速度/数量、情无/小雨点击评论是否仍能打开、本地段评是否明显减少等待。'}
    ],
    'links':{'source':RAW,'backup':BACKUP,'import':IMPORT},
    'updatedAt':TODAY
}
(ROOT/'rss/data/details/beta/qidian-next.json').write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

log = f'''## {TODAY} · qidian-next {VERSION} — 妙想天开段评快通道借鉴\n- 重新按用户当前上传的 `bookSource_妙想天开.json` 核对：该版段评计数实际走 `druidv6.if.qidian.com/argus/api/v1/chapterreview/getchapterrepagesummary`，读取 `Data.Getparagraphscommentcounts.DataList`；神评另用同端点 `strategy=3`，本章说用 `assembly/getchapteractivity`。\n- Beta3 先吸收低风险且收益最大的“整章段评计数一次取回”思路：新增 Argus `getchapterrepagesummary` 快通道，归一化为 qidian-next 既有 `paragraphId/segmentId/count` 模型并写入 ReviewCache。\n- 本地段评：官方快通道有非空计数时直接返回；接口空/失败继续走原 www/m/read 多镜像摘要链，不把空结果当权威。\n- 情无/小雨：只把气泡位置/数量元数据改为官方快通道优先；完整评论点击 Provider 不变，快通道失败继续回退 `review.php`。\n- 目录评估：妙想天开使用单一 v1 `chapterlist/chapterlist` 读取 `N/C/V/T/W`；qidian-next 当前已有 APP v3 + getsimple + pager + Web fallback + 多层缓存/完整度诊断，本版不替换目录，避免跨域回归。\n- `strategy=3` 神评与 `getchapteractivity` 本章说暂不替换现有成熟链，待本版真机确认后再单域 A/B。Stable 1.2.1、正文、目录、搜索、账号及其它 Provider 不变。\n\n'''
for dp in [ROOT/'docs/RELEASE_LOG.md', ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md']:
    old = dp.read_text(encoding='utf-8')
    dp.write_text(log + old, encoding='utf-8')

# Final artifact gates.
if hashlib.sha256(STABLE.read_bytes()).hexdigest() != EXPECTED_STABLE:
    raise SystemExit('Stable changed after patch')
check = json.loads(BETA.read_text(encoding='utf-8'))
ss = check[0] if isinstance(check, list) else check
assert 'v1.2.2-beta3' in ss.get('bookSourceComment','')
assert 'function qfReviewFastSummaryV1223' in ss['jsLib']
assert "QF_ReviewApi.request(ctx,'v1/chapterreview/getchapterrepagesummary'" in ss['jsLib']
assert 'fast1223.items.length' in ss['jsLib']
assert 'https://full.hnxianxin.cn/qd/review.php?bookId=' in ss['jsLib']
assert ss.get('ruleContent') == s.get('ruleContent')
print('Beta3 ready', sha)
