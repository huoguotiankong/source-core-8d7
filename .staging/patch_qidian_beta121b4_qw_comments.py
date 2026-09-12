import json,re,gzip,base64,hashlib
P='sources/novel/qidian-next/qidian-next-beta.json'
with open(P,encoding='utf-8') as f: arr=json.load(f)
s=arr[0]
js=s.get('jsLib','')
# Inject isolated Qingwu/Xiaoyu comment adapter before final runtime use. It intentionally does not touch local review UI.
addon=r'''
/* QF beta4: Qingwu/Xiaoyu review adapter */
function qfQwCommentStateV1214(ctx){
  var st={}; try{st=JSON.parse((ctx.source||source).getVariable()||'{}')}catch(e){}
  return st||{};
}
function qfQwCommentHeadersV1214(ctx){
  var st=qfQwCommentStateV1214(ctx), h={Accept:'application/json'};
  var tok=String(st.xyUserToken||''); var aid=String(st.xyAndroidId||'');
  try{if(!tok && typeof qfXyEnsureUserV1213==='function'){var x=qfXyEnsureUserV1213(ctx)||{};tok=String(x.xyUserToken||'');aid=String(x.xyAndroidId||'')}}catch(e){}
  if(tok)h['X-Sec-Token']=tok;if(aid)h['X-Android-Id']=aid;return h;
}
function qfQwAjaxV1214(ctx,url){return String(ctx.java.ajax(url+','+JSON.stringify({method:'GET',headers:qfQwCommentHeadersV1214(ctx)}))||'');}
function qfQwReviewCountsV1214(ctx,bid,cid){
  var out={ok:false,list:[],title:null,chapter:0};
  try{var j=JSON.parse(qfQwAjaxV1214(ctx,'https://full.hnxianxin.cn/qd/review.php?bookId='+encodeURIComponent(bid)+'&chapterId='+encodeURIComponent(cid))||'{}');
    var d=(j.Data&&j.Data.Getparagraphscommentcounts&&j.Data.Getparagraphscommentcounts.DataList)||[];
    for(var i=0;i<d.length;i++){var x=d[i]||{},pid=Number(x.ParagraphId),tc=Number(x.TextCount||x.CommentCount||0);if(pid===-1&&tc>0)out.title=x;if(pid>0&&tc>0)out.list.push(x);}
    out.ok=!!d.length; out.chapter=out.title?Number(out.title.TextCount||out.title.CommentCount||0):0;
  }catch(e){try{ctx.java.log('QW review counts: '+e)}catch(_){}} return out;
}
function qfQwH5V1214(bid,cid,pid){var u='https://full.hnxianxin.cn/qd/index.html?bookId='+encodeURIComponent(bid)+'&chapterId='+encodeURIComponent(cid);if(pid!==undefined&&pid!==null&&pid!=='')u+='&paragraphIndex='+encodeURIComponent(pid);return u;}
function qfQwOpenV1214(ctx,bid,cid,pid,title){try{ctx.java.startBrowser(qfQwH5V1214(bid,cid,pid),title||'评论')}catch(e){}}
function qfQwBubbleV1214(ctx,count,bid,cid,pid){
  var svg='<svg xmlns="http://www.w3.org/2000/svg" width="112" height="48"><rect x="1" y="1" width="110" height="46" rx="20" fill="#fff" fill-opacity=".25" stroke="#888"/><text x="56" y="32" text-anchor="middle" font-size="24" fill="#444">'+Number(count||0)+'</text></svg>';
  return '<img src="data:image/svg+xml;base64,'+ctx.java.base64Encode(svg)+','+JSON.stringify({style:'DEFAULT',click:'qfQwOpenV1214(this,'+JSON.stringify(String(bid))+','+JSON.stringify(String(cid))+','+JSON.stringify(String(pid))+',\"段评\")',marker:'qfQw:'+bid+':'+cid+':'+pid})+'">';
}
function qfQwSayCardV1214(ctx,bid,cid,count){
  if(!count)return '';var svg='<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="126"><rect x="2" y="2" width="1076" height="122" rx="34" fill="#fff" fill-opacity=".24" stroke="#aaa"/><text x="58" y="78" font-size="38" fill="#333">本章说</text><text x="1018" y="78" text-anchor="end" font-size="32" fill="#666">'+Number(count)+'条评论 ›</text></svg>';
  return '<img src="data:image/svg+xml;base64,'+ctx.java.base64Encode(svg)+','+JSON.stringify({style:'FULL',click:'qfQwOpenV1214(this,'+JSON.stringify(String(bid))+','+JSON.stringify(String(cid))+',\"\",\"本章评论\")',marker:'qfQwSay:'+bid+':'+cid})+'">';
}
function qfQwDecorateV1214(ctx,content,bid,cid,localTitleBubble){
  var c=qfQwReviewCountsV1214(ctx,bid,cid);if(!c.ok)return {content:content,titleBubble:localTitleBubble||'',server:false};
  var lines=String(content||'').replace(/\r/g,'').split('\n'), map={};for(var i=0;i<c.list.length;i++){var x=c.list[i];map[String(Number(x.ParagraphId))]=x;}
  var p=1;for(var n=0;n<lines.length;n++){if(!String(lines[n]).trim()||/<img\b/i.test(lines[n]))continue;var x=map[String(p)];if(x)lines[n]+=qfQwBubbleV1214(ctx,Number(x.TextCount||x.CommentCount||0),bid,cid,p);p++;}
  var body=lines.join('\n');if(c.chapter>0)body+='\n'+qfQwSayCardV1214(ctx,bid,cid,c.chapter);
  /* Xiaoyu review.php exposes ParagraphId=-1 as title comment when available; otherwise retain local title bubble. */
  var tb=c.title?qfQwBubbleV1214(ctx,Number(c.title.TextCount||c.title.CommentCount||0),bid,cid,-1):(localTitleBubble||'');
  return {content:body,titleBubble:tb,server:true};
}
'''
js += '\n'+addon
s['jsLib']=js
# Version metadata. Runtime integration is appended through ruleContent/ruleToc title wrappers below when matching anchors exist.
s['bookSourceComment']='v1.2.1-beta4：新增情无/小雨段评服务器适配；段评可走小雨 review.php，章名评论优先服务器 ParagraphId=-1、无数据回退本地；本章说改为服务器评论入口并保留具体评论展示链。Stable 1.2.0 不变。'
# Patch ruleContent: wrap final result if identifiable book/chapter IDs are available from url.
rc=s.get('ruleContent',{})
content=rc.get('content','') if isinstance(rc,dict) else ''
if content and 'qfQwDecorateV1214' not in content:
  content += r'''\n@js:\ntry{var _u=String(baseUrl||url||'');var _bm=_u.match(/[?&]bookId=([^&]+)/i),_cm=_u.match(/[?&]chapterId=([^&]+)/i);if(_bm&&_cm){var _bid=decodeURIComponent(_bm[1]),_cid=decodeURIComponent(_cm[1]);var _sel='';try{_sel=String(source.get('qf_review_provider')||source.get('段评来源')||'')}catch(e){}if(/情无|小雨|qw|xiaoyu/i.test(_sel)){var _d=qfQwDecorateV1214(this,String(result||''),_bid,_cid,'');result=_d.content;if(_d.titleBubble)source.put('qf_qw_title_'+_cid,_d.titleBubble);}}}catch(e){try{java.log('QW comment decorate: '+e)}catch(_){}}'''
  rc['content']=content;s['ruleContent']=rc
# Toc title fallback: append stored server title bubble when source title rule is JS/string.
rt=s.get('ruleToc',{})
title=rt.get('chapterName') or rt.get('title')
if isinstance(title,str) and 'qf_qw_title_' not in title:
  key='chapterName' if 'chapterName' in rt else 'title'
  rt[key]=title+r'''\n@js:\ntry{var _cid='';try{var _o=JSON.parse(java.hexDecodeToString(result));_cid=String(_o.chapterId||'')}catch(e){}var _b=_cid?String(source.get('qf_qw_title_'+_cid)||''):'';if(_b)result=String(result||title||'')+_b;}catch(e){}'''
  s['ruleToc']=rt
# version fields where present
for k in ['version','sourceVersion']: 
  if k in s:s[k]='1.2.1-beta4'
for k in ['versionCode','sourceVersionCode']:
  if k in s:s[k]=12104
with open(P,'w',encoding='utf-8') as f:json.dump(arr,f,ensure_ascii=False,indent=2)
# sync JSON catalogs by replacing logical source entry from beta source
for fp in ['manifest.json','subscription/beta.json','subscription/novel.json','bundles/all-beta.json']:
  try:
    with open(fp,encoding='utf-8') as f:d=json.load(f)
    def walk(x):
      if isinstance(x,list):
        for i,v in enumerate(x):
          if isinstance(v,dict) and (v.get('id')=='qidian-next' or v.get('bookSourceUrl')==s.get('bookSourceUrl')):
            for kk in list(v.keys()):
              if kk in s:v[kk]=s[kk]
            if 'version' in v:v['version']='1.2.1-beta4'
            if 'versionCode' in v:v['versionCode']=12104
            if 'summary' in v:v['summary']='情无/小雨段评服务器可选；章名评论服务器优先、本地回退；修复本章说具体评论展示。'
          else: walk(v)
      elif isinstance(x,dict):
        for v in x.values():walk(v)
    walk(d)
    with open(fp,'w',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
  except Exception as e: print(fp,e)
# docs
entry='''\n## 2026-09-12 · qidian-next 1.2.1-beta4\n- 评论设置新增情无/小雨服务器适配：段评可走 `full.hnxianxin.cn/qd/review.php`。\n- 章名评论优先使用服务器 `ParagraphId=-1`；服务器无章名评论时保留本地段评章名评论。\n- 本章说改用小雨评论入口，修复只显示总数卡、不显示具体评论的问题。\n- Stable 1.2.0 与其它功能域不变。\n'''
for fp in ['docs/RELEASE_LOG.md','docs/sources/qidian-next/PROJECT_HANDOFF.md']:
  with open(fp,encoding='utf-8') as f:t=f.read()
  with open(fp,'w',encoding='utf-8') as f:f.write(entry+t)
# basic checks
json.load(open(P,encoding='utf-8'))
print('patched beta4',len(js))