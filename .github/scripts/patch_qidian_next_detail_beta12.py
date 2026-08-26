import copy
import hashlib
import json
from pathlib import Path

ROOT=Path('.')
SOURCE=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
MANIFEST=ROOT/'manifest.json'
SUB=ROOT/'subscription/beta.json'
BUNDLE=ROOT/'bundles/all-beta.json'
DETAIL=ROOT/'rss/data/details/beta/qidian-next.json'
RELEASE=ROOT/'docs/RELEASE_LOG.md'
HANDOFF=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
ISSUES=ROOT/'docs/KNOWN_ISSUES.md'
VERSION='1.1.0-beta12';VERSION_CODE=11012;NOW='2026-08-26T17:08:00+08:00';DAY='2026-08-26'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VERSION_CODE}'
CDN=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VERSION_CODE}'
IMPORT=f'legado://import/importonline?src={RAW}'
SUMMARY='详情 beta12：重做更新/首发时间可信链，区分首发与上架；作品数据改为等宽预格式双列，正文源快捷入口直达正文设置。'
CHANGELOG=['更新只接受当前书的最新章节/最近更新语义；连载书时间明显陈旧时复用现有官方搜索校正，校正不到宁可隐藏','首发不再混用 createTime/publishTime/上架时间；只接受明确首发字段，VIP 上架继续单独显示为上架','时间缓存升级到 v1112，并刷新官方搜索详情缓存，避免 Beta11 错误时间延续','作品数据放弃阅读真机未生效的 inline-block width，改为 pre/monospace 预格式双列，右列固定起点','快捷入口“正文源”改为直接调用 qfMultiContentV423，进入现有“📚 正文设置”页','Beta10/11 富数据、简介和冷启动顺序保留；搜索、目录、正文 Provider 实际取正文逻辑、评论、角色卡、书友圈、账号链冻结']
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def find_source(o):
    if isinstance(o,dict):
        if o.get('bookSourceName')=='🌈 起点增强 · Beta':return o
        for v in o.values():
            r=find_source(v)
            if r is not None:return r
    elif isinstance(o,list):
        for v in o:
            r=find_source(v)
            if r is not None:return r
    return None
def once(s,old,new,label):
    n=s.count(old);assert n==1,f'{label}: expected 1, got {n}';return s.replace(old,new,1)
src_doc=load(SOURCE);src=find_source(src_doc);assert src is not None and 'beta11' in str(src.get('bookSourceComment','')).lower()
old_src=copy.deepcopy(src);init=src['ruleBookInfo']['init'];intro=src['ruleBookInfo']['intro']
init=once(init,"var u=qfPickTimeKeyV1111(seg,['lastUpdateTime','LastUpdateTime','newChapterTime','NewChapterTime','lastChapterTime','LastChapterTime','updateTime','UpdateTime']);\n      var p=qfPickTimeKeyV1111(seg,['publishDate','PublishDate','publishTime','PublishTime','firstPublishTime','FirstPublishTime','bookCreateTime','BookCreateTime','createTime','CreateTime']);","var u=qfPickTimeKeyV1111(seg,['lastUpdateTime','LastUpdateTime','newChapterTime','NewChapterTime','lastChapterTime','LastChapterTime','latestChapterTime','LatestChapterTime']);\n      var p=qfPickTimeKeyV1111(seg,['firstPublishTime','FirstPublishTime','firstPublishDate','FirstPublishDate']);",'current-book time keys')
old="""function qfTimeSuspiciousV1111(){
  var u=qfTimeMsV1111(info.updateTime),p=qfTimeMsV1111(info.publishDate),l=qfTimeMsV1111(info.listingDate),now=Date.now();
  if(!u)return true;if(u>now+2*86400000)return true;if(l&&u+60000<l)return true;if(p&&Math.abs(u-p)<60000)return true;return false;
}"""
new="""function qfTimeSuspiciousV1111(){
  var raw=String(info.updateTime||'').trim();if(/^(?:刚刚|昨天|前天|\\d+\\s*(?:秒|分钟|小时|天)前)$/.test(raw))return false;
  var u=qfTimeMsV1111(raw),p=qfTimeMsV1111(info.publishDate),l=qfTimeMsV1111(info.listingDate),now=Date.now(),st=String(info.status||'');
  if(!u)return true;if(u>now+2*86400000)return true;if(l&&u+60000<l)return true;if(p&&Math.abs(u-p)<60000)return true;if(/连载/.test(st)&&now-u>60*86400000)return true;return false;
}"""
init=once(init,old,new,'stale/relative update policy')
old="""var qfTimesV1111=qfCurrentBookTimesV1111(html);
if(qfTimesV1111.updateTime)info.updateTime=qfTimesV1111.updateTime;
if(qfTimesV1111.publishDate)info.publishDate=qfTimesV1111.publishDate;
if(blank(info.listingDate))info.listingDate=textScalar(html,['ListingDate','listingDate','VipStartTime','vipStartTime'],50);
if(!qfTimesV1111.updateTime&&qfTimeSuspiciousV1111())info.updateTime='';
if(!qfTimesV1111.publishDate&&qfPublishSuspiciousV1111())info.publishDate='';"""
new="""var qfTimesV1111=qfCurrentBookTimesV1111(html);
if(qfTimesV1111.updateTime)info.updateTime=qfTimesV1111.updateTime;else if(qfTimeSuspiciousV1111())info.updateTime='';
info.publishDate=qfTimesV1111.publishDate||'';
if(blank(info.listingDate))info.listingDate=textScalar(html,['ListingDate','listingDate','VipStartTime','vipStartTime'],50);"""
init=once(init,old,new,'strict current times')
init=once(init,"m=t.match(/(?:首发时间|首发日期|发布时间|发布于|创建时间|开书时间)\\s*[:：]?\\s*(20\\d{2}[-\\/]\\d{1,2}[-\\/]\\d{1,2}(?:\\s+\\d{1,2}:\\d{2}(?::\\d{2})?)?)/);if(m&&m[1])q.publishDate=qfDateCandidateV1111(m[1]);","m=t.match(/(?:首发时间|首发日期)\\s*[:：]?\\s*(20\\d{2}[-\\/]\\d{1,2}[-\\/]\\d{1,2}(?:\\s+\\d{1,2}:\\d{2}(?::\\d{2})?)?)/);if(m&&m[1])q.publishDate=qfDateCandidateV1111(m[1]);",'qidiantu first publish semantics')
init=once(init,"if(o.updateTime&&(blank(info.updateTime)||qfTimeSuspiciousV1111()))info.updateTime=o.updateTime;\n  info.detailSource=(info.detailSource?info.detailSource+'+':'')+'qidian-search-v1111';","if(o.updateTime)info.updateTime=o.updateTime;\n  info.detailSource=(info.detailSource?info.detailSource+'+':'')+'qidian-search-v1112';",'official search authoritative update')
init=once(init,"var ck='qf_qidian_search_detail_v1111_'+String(bid),cv=qfCacheGetV1109(ck),o={};","var ck='qf_qidian_search_detail_v1112_'+String(bid),cv=qfCacheGetV1109(ck),o={};",'official cache v1112')
old="var um=block.match(/(?:更新时间|更新)\\s*[:：]?\\s*(20\\d{2}[-\\/]\\d{1,2}[-\\/]\\d{1,2}(?:\\s+\\d{1,2}:\\d{2}(?::\\d{2})?)?)/);if(um&&um[1])o.updateTime=qfDateCandidateV1111(um[1]);"
new="var um=block.match(/(?:更新时间|最近更新|更新)\\s*[:：]?\\s*(20\\d{2}[-\\/]\\d{1,2}[-\\/]\\d{1,2}(?:\\s+\\d{1,2}:\\d{2}(?::\\d{2})?)?)/);if(um&&um[1])o.updateTime=qfDateCandidateV1111(um[1]);\n      if(!o.updateTime){var ur=block.match(/(?:最近更新|更新)[\\s\\S]{0,90}?(刚刚|昨天|前天|\\d+\\s*(?:秒|分钟|小时|天)前)/);if(ur&&ur[1])o.updateTime=String(ur[1]).replace(/\\s+/g,'');}"
init=once(init,old,new,'official relative update')
init=once(init,"cached('status','qf_status',false);cached('updateTime','qf_updateTime_v1111',false);cached('publishDate','qf_publishDate_v1111',false);cached('listingDate','qf_listingDate',false);","cached('status','qf_status',false);cached('updateTime','qf_updateTime_v1112',false);cached('publishDate','qf_publishDate_v1112',false);cached('listingDate','qf_listingDate',false);",'read cache v1112')
init=once(init,"put.call(this,'qf_status',info.status);put.call(this,'qf_updateTime_v1111',info.updateTime);put.call(this,'qf_publishDate_v1111',info.publishDate);put.call(this,'qf_updateTime',info.updateTime);put.call(this,'qf_publishDate',info.publishDate);put.call(this,'qf_listingDate',info.listingDate);","if(qfTimeSuspiciousV1111())info.updateTime='';\nif(qfPublishSuspiciousV1111()||(qfTimeMsV1111(info.updateTime)&&qfTimeMsV1111(info.publishDate)&&Math.abs(qfTimeMsV1111(info.updateTime)-qfTimeMsV1111(info.publishDate))<60000))info.publishDate='';\nput.call(this,'qf_status',info.status);put.call(this,'qf_updateTime_v1112',info.updateTime);put.call(this,'qf_publishDate_v1112',info.publishDate);put.call(this,'qf_listingDate',info.listingDate);",'final time gate')
old_grid="function dataCell(v,w){return '<span style=\\\"display:inline-block;width:'+(w||'49%')+';vertical-align:top;white-space:nowrap\\\">'+v+'</span>';}function dataRows(items){var a=[];for(var i=0;i<items.length;i++)if(items[i][2])a.push(items[i]);var h='';for(var j=0;j<a.length;j+=2){h+='<br>'+dataCell(datum(a[j][0],a[j][1],a[j][2]),'49%');h+=a[j+1]?dataCell(datum(a[j+1][0],a[j+1][1],a[j+1][2]),'49%'):dataCell('','49%');}return h;}"
new_grid="function qfDispWidthV1112(s){s=String(s||'');var w=0;for(var i=0;i<s.length;i++){w+=(s.charCodeAt(i)>255?2:1);}return w;}\nfunction qfMetricTextV1112(label,value){return String(label||'')+' '+String(value||'');}\nfunction qfMetricHtmlV1112(label,value){return '<font color=\\\"#8a949b\\\">'+esc(label)+'</font> <b><font color=\\\"#149c95\\\">'+esc(value)+'</font></b>';}\nfunction dataRows(items){var a=[];for(var i=0;i<items.length;i++)if(items[i][2])a.push(items[i]);var h='<pre style=\\\"margin:0;line-height:1.42;font-family:monospace;white-space:pre\\\">',target=20;for(var j=0;j<a.length;j+=2){var l=a[j],lt=qfMetricTextV1112(l[1],l[2]),pad='';for(var p=qfDispWidthV1112(lt);p<target;p++)pad+=' ';h+=qfMetricHtmlV1112(l[1],l[2])+pad;if(a[j+1])h+=qfMetricHtmlV1112(a[j+1][1],a[j+1][2]);if(j+2<a.length)h+='\\n';}return h+'</pre>';}\n"
intro=once(intro,old_grid,new_grid,'pre metrics')
old_data="""var data=[
 ['🔥','总推荐',rec],['🎟','月票',mt],['👁',clean(x.readingMetricLabel)||'在看',watch],['💯','评分',sc?(sc+(clean(x.ratingCount)?' / '+num(x.ratingCount)+'人':'')):'' ],
 ['⭐','收藏',col],['👥','粉丝',fans],['🏅','盟主',leader],['💎','投资',invest],['📌','首订',first]
];"""
new_data="""var data=[
 ['','总推荐',rec],['','月票',mt],['',clean(x.readingMetricLabel)||'在看',watch],['','评分',sc?(sc+(clean(x.ratingCount)?' / '+num(x.ratingCount)+'人':'')):'' ],
 ['','收藏',col],['','粉丝',fans],['','盟主',leader],['','投资',invest],['','首订',first]
];"""
intro=once(intro,old_data,new_data,'metric icons')
intro=once(intro,"<button>⚡ 正文源@onclick:qfBookInfoOpenSmartSourceV330.call(this)</button>","<button>⚡ 正文设置@onclick:qfMultiContentV423.call(this)</button>",'content settings shortcut')
src['ruleBookInfo']['init']=init;src['ruleBookInfo']['intro']=intro
src['bookSourceComment']='v1.1.0-beta12：详情时间语义、作品数据双列与正文设置快捷入口修复版。更新只接受最新章节/最近更新语义，连载书明显陈旧时复用当前 bookId 官方搜索并支持绝对/相对更新时间；校正不到宁可不显示错误值。首发只接受明确 firstPublish/首发时间，不再混入 createTime/publishTime/VIP 上架；上架独立显示。时间缓存升级 v1112。作品数据改用 pre+monospace 预格式双列，去掉会破坏列宽的指标 emoji。快捷入口改为“正文设置”，直接调用 qfMultiContentV423。富数据、简介、Provider、目录、评论等其余链路冻结。'
a=copy.deepcopy(old_src);b=copy.deepcopy(src)
for x in (a,b):x['bookSourceComment']='<masked>';x['ruleBookInfo']['init']='<masked>';x['ruleBookInfo']['intro']='<masked>'
assert a==b
assert 'qf_qidian_search_detail_v1112_' in init and 'qf_updateTime_v1112' in init and 'qfMultiContentV423.call(this)' in intro and '<pre style=' in intro
dump(SOURCE,src_doc);sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
manifest=load(MANIFEST);entry=next(x for x in manifest['sources'] if x.get('id')=='qidian-next-beta');entry.update({'version':VERSION,'versionCode':VERSION_CODE,'updatedAt':NOW,'sourceUrl':RAW,'summary':SUMMARY,'tags':['起点','测试版','详情页','时间修复','富数据','双列对齐','正文设置','缓存'],'changelog':CHANGELOG,'sha256':sha});manifest['updatedAt']=NOW;dump(MANIFEST,manifest)
sub=load(SUB);item=next(x for x in sub['items'] if x.get('id')=='qidian-next-beta');item.update({'summary':SUMMARY,'version':VERSION,'updatedAt':DAY,'tags':['起点','测试版','详情页','时间修复','富数据','双列对齐','正文设置','缓存'],'changelog':CHANGELOG,'sourceUrl':RAW,'backupUrl':CDN,'importUrl':IMPORT});sub['updatedAt']=NOW;dump(SUB,sub)
bundle=load(BUNDLE);replaced=0
def rb(n):
 global replaced
 if isinstance(n,list):
  for i,v in enumerate(n):
   if isinstance(v,dict) and v.get('bookSourceName')=='🌈 起点增强 · Beta':n[i]=copy.deepcopy(src);replaced+=1
   else:rb(v)
 elif isinstance(n,dict):
  for v in n.values():rb(v)
rb(bundle);assert replaced==1;dump(BUNDLE,bundle)
rss=load(DETAIL);rss.update({'summary':SUMMARY,'badges':['Beta',VERSION,'时间 / 双列 / 正文设置'],'sections':[{'title':'Beta11 真机结论','text':'富数据与简介正常，但更新/首发仍可能被早期建书或上架时间污染；inline-block 固定宽度在当前阅读真机未生效。'},{'title':'时间可信链','text':'更新仅接受最新章节语义，并用当前 bookId 官方搜索校正绝对/相对最近更新时间；首发只接受明确首发字段，上架独立显示。'},{'title':'作品数据','text':'双列改为 pre+monospace 预格式布局并按显示宽度补空格；移除指标 emoji，避免不同 emoji 字宽破坏右列起点。'},{'title':'快捷入口','text':'“正文源”改为“正文设置”，直接进入现有正文策略/Provider 设置页。'},{'title':'冻结范围','text':'搜索、目录、正文 Provider 实际解析、评论、角色卡、书友圈、账号和情无 VIP 链不改。'}],'sourceUrl':RAW,'backupUrl':CDN,'importUrl':IMPORT});dump(DETAIL,rss)
RELEASE.write_text(RELEASE.read_text(encoding='utf-8').rstrip()+f'\n\n## {DAY} · 🌈 起点增强 · {VERSION}\n- 更新字段收紧为最新章节/最近更新语义，连载书明显陈旧时复用当前 bookId 官方搜索；支持绝对日期和相对时间。\n- 首发只接受明确 firstPublish/首发时间；上架独立，不再将 createTime/publishTime/VIP 上架冒充首发。\n- 时间缓存切换 v1112。\n- 作品数据改用 pre+monospace 双列；快捷入口“正文设置”直达 qfMultiContentV423。\n- 正式通道未修改。\n',encoding='utf-8')
HANDOFF.write_text(HANDOFF.read_text(encoding='utf-8').rstrip()+f'\n\n### {VERSION} 真机修复（{DAY}）\n- 时间按语义分层：更新=latest chapter/当前 bookId 官方搜索；首发=明确 firstPublish；上架=listingDate。\n- usehtml 双列不要依赖 inline-block 百分比宽度；当前改用预格式等宽文本。\n- 详情“正文设置”快捷入口直接调用 qfMultiContentV423。\n- 本版仍为 Beta。\n',encoding='utf-8')
ISSUES.write_text(ISSUES.read_text(encoding='utf-8').rstrip()+f'\n\n### {DAY} · qidian-next Beta11 时间/双列兼容问题\n- 更新/首发可能显示相同早期日期；inline-block width 在部分阅读真机无效。\n- Beta12：更新改用最新章节语义+官方搜索，首发与上架分离；双列改用 pre/monospace。\n',encoding='utf-8')
print('published',VERSION,'sha256',sha,'bundle_replace',replaced)
