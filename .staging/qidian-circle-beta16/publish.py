import json,re,base64,gzip,pathlib,hashlib,datetime,subprocess,tempfile
root=pathlib.Path('.')
source_path=root/'sources/novel/qidian-next/qidian-next-beta.json'
stable_path=root/'sources/novel/qidian-next/qidian-next.json'
stable_before=hashlib.sha256(stable_path.read_bytes()).hexdigest()
doc=json.loads(source_path.read_text(encoding='utf-8')); assert isinstance(doc,list) and len(doc)==1
src=doc[0]; assert src.get('bookSourceName')=='🌈 起点增强 · Beta'
js=src['jsLib']; m=re.search(r'"circle":"gz:([A-Za-z0-9+/=]+)"',js); assert m
old_payload=m.group(1); code=gzip.decompress(base64.b64decode(old_payload)).decode('utf-8')
def rep(old,new,label):
    global code
    n=code.count(old); assert n==1,f'{label}: expected 1 got {n}'
    code=code.replace(old,new,1)
# In-memory preview map: keep detail-button DOM compact and use postId as the transport key.
marker='    h.push("function feedCard(o,label){'
assert code.count(marker)==1
code=code.replace(marker,'    h.push("var qfPostPreviewImgs={};");\n'+marker,1)
# Dynamic/refiltered cards write their complete image list into the postId map.
old="var directImg=qfNormUrl(o.image||'');if(directImg&&ims.indexOf(directImg)<0)ims.unshift(directImg);var vd="
new="var directImg=qfNormUrl(o.image||'');if(directImg&&ims.indexOf(directImg)<0)ims.unshift(directImg);if(pid)qfPostPreviewImgs[String(pid)]=ims.slice(0,9);var vd="
rep(old,new,'preview map capture')
# Initial server-rendered cards do not pass through feedCard(), so seed the same map from INITIAL_ROWS after it exists.
seed_marker='    h.push("function rowPostId(o){'
assert code.count(seed_marker)==1
seed="    h.push(\"function qfSeedPreviewRows(a){if(!Array.isArray(a))return;for(var si=0;si<a.length;si++){var o=a[si]||{},pid=String(o.PostId||o.postId||o.Id||o.id||o.TopicId||o.topicId||'');if(!pid)continue;var rr=richOf(o),ims=imageUrls(o,rr.raw),ds=Array.isArray(o.images)?o.images:[];for(var di=ds.length-1;di>=0;di--){var du=qfNormUrl(ds[di]);if(du&&ims.indexOf(du)<0)ims.unshift(du);}var one=qfNormUrl(o.image||'');if(one&&ims.indexOf(one)<0)ims.unshift(one);if(ims.length)qfPostPreviewImgs[pid]=ims.slice(0,9);}}qfSeedPreviewRows(INITIAL_ROWS.dongtai);qfSeedPreviewRows(INITIAL_ROWS.jinghua);qfSeedPreviewRows(INITIAL_ROWS.tongren);qfSeedPreviewRows(INITIAL_ROWS.discussion);qfSeedPreviewRows(INITIAL_ROWS.discussionPreview);\");\n"
code=code.replace(seed_marker,seed+seed_marker,1)
# Restore the proven compact button markup; do not serialize the whole array into a DOM attribute.
old="data-img=\\\"'+esc(ims.length?ims[0]:'')+'\\\" data-imgs=\\\"'+esc(encodeURIComponent(JSON.stringify(ims.slice(0,9))))+'\\\">查看详情"
new="data-img=\\\"'+esc(ims.length?ims[0]:'')+'\\\">查看详情"
rep(old,new,'compact detail button')
# Replace Beta15 DOM decode handler with postId memory lookup + legacy first-image fallback.
old="var pim=qfNormUrl(this.getAttribute('data-img')||''),pims=[];try{var pie=String(this.getAttribute('data-imgs')||'');if(pie)pims=JSON.parse(decodeURIComponent(pie));}catch(_pi){}if(!Array.isArray(pims))pims=[];var pic=[],pis={};for(var px=0;px<pims.length&&pic.length<9;px++){var pu=qfNormUrl(pims[px]);if(/^https?:\\/\\//i.test(pu)&&!pis[pu]){pis[pu]=1;pic.push(pu);}}if(!pic.length&&pim)pic=[pim];state.previewImgs=pic;"
new="var pim=qfNormUrl(this.getAttribute('data-img')||''),pims=[];try{pims=(qfPostPreviewImgs&&qfPostPreviewImgs[state.pid])?qfPostPreviewImgs[state.pid].slice(0,9):[];}catch(_pm){}if(!Array.isArray(pims))pims=[];var pic=[],pis={};for(var px=0;px<pims.length&&pic.length<9;px++){var pu=qfNormUrl(pims[px]);if(/^https?:\\/\\//i.test(pu)&&!pis[pu]){pis[pu]=1;pic.push(pu);}}if(!pic.length&&pim)pic=[pim];state.previewImgs=pic;"
rep(old,new,'memory detail opener')
assert 'data-imgs=' not in code
assert 'qfPostPreviewImgs' in code and 'qfSeedPreviewRows' in code and 'state.previewImgs=pic' in code
assert 'qfCleanPollText' in code and 'mergedImgs' in code
with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as tf:
    tf.write(code); tmp=tf.name
subprocess.run(['node','--check',tmp],check=True)
new_payload=base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9,mtime=0)).decode('ascii')
src['jsLib']=js[:m.start(1)]+new_payload+js[m.end(1):]
src['bookSourceComment']='v1.1.0-beta16：书友圈详情点击热修。撤销 Beta15 将完整图片数组塞入 data-imgs DOM 属性的做法，恢复已验证的紧凑详情按钮；列表初始卡片和动态筛选卡片的多图统一按 postId 保存到当前 WebView 内存映射，点击后再与 getpostdetail 图片合并。Beta15 投票元数据精确清理继续保留，其它域冻结。'
src['lastUpdateTime']=int(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)
source_path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source_sha=hashlib.sha256(source_path.read_bytes()).hexdigest()
# Verify repack.
chk=json.loads(source_path.read_text(encoding='utf-8'))[0]['jsLib']; cm=re.search(r'"circle":"gz:([A-Za-z0-9+/=]+)"',chk); assert cm
cc=gzip.decompress(base64.b64decode(cm.group(1))).decode('utf-8')
assert 'qfPostPreviewImgs' in cc and 'qfSeedPreviewRows' in cc and 'data-imgs=' not in cc and 'qfCleanPollText' in cc and 'mergedImgs' in cc
# Bundle replace only this beta source.
bundle_path=root/'bundles/all-beta.json'; bundle=json.loads(bundle_path.read_text(encoding='utf-8'))
hits=[i for i,x in enumerate(bundle) if isinstance(x,dict) and x.get('bookSourceName')=='🌈 起点增强 · Beta']; assert len(hits)==1
bundle[hits[0]]=src; bundle_path.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))); now_iso=now.isoformat(timespec='seconds'); day=now.strftime('%Y-%m-%d')
version='1.1.0-beta16'; version_code=11016
summary='书友圈 beta16：恢复帖子“查看详情”点击，并保留列表多图进入详情。'
tags=['起点','测试版','书友圈','帖子详情','点击修复','多图','评论']
changes=['恢复 Beta14 已验证的紧凑“查看详情”按钮 DOM，不再把完整图片数组编码进 data-imgs 属性','初始列表卡片与动态筛选卡片的完整配图均按 postId 保存在当前书友圈 WebView 内存映射，点击详情时读取并与 getpostdetail 图片去重合并','保留 Beta15 的 Options/VoteId/VoteType 投票尾元数据精确清理','评论/楼中楼、分类、视频、详情、正文 Provider、角色卡、账号链冻结']
raw=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}'
cdn=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}'
imp='legado://import/importonline?src='+raw
sub_path=root/'subscription/beta.json'; sub=json.loads(sub_path.read_text(encoding='utf-8')); item=next(x for x in sub['items'] if x.get('id')=='qidian-next-beta')
item.update({'summary':summary,'version':version,'updatedAt':day,'tags':tags,'changelog':changes,'sourceUrl':raw,'backupUrl':cdn,'importUrl':imp}); sub['updatedAt']=now_iso; sub_path.write_text(json.dumps(sub,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
man_path=root/'manifest.json'; man=json.loads(man_path.read_text(encoding='utf-8')); mi=next(x for x in man['sources'] if x.get('id')=='qidian-next-beta')
mi.update({'version':version,'versionCode':version_code,'updatedAt':now_iso,'sourceUrl':raw,'summary':summary,'tags':tags,'changelog':changes,'sha256':source_sha}); man['updatedAt']=now_iso; man_path.write_text(json.dumps(man,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rss_path=root/'rss/data/details/beta/qidian-next.json'; rss={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',version,'书友圈点击热修'],'sections':[{'title':'查看详情恢复','text':'详情按钮恢复为 Beta14 已验证的紧凑 DOM，仅携带帖子 ID 和首图，不再塞入长图片数组属性。'},{'title':'多图仍保留','text':'初始列表与动态筛选列表的完整配图均按 postId 暂存在当前 WebView 内存，点击详情后与详情接口图片去重合并，最多 9 张。'},{'title':'冻结范围','text':'投票元数据精确清理保留；评论/楼中楼、分类、视频以及其它书源域不变。'}],'sourceUrl':raw,'backupUrl':cdn,'importUrl':imp}; rss_path.write_text(json.dumps(rss,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
log_path=root/'docs/RELEASE_LOG.md'; log=log_path.read_text(encoding='utf-8'); entry=f'''## {day} — Qidian Next {version} circle detail click hotfix\n\nStatus: Beta/Test; awaiting user real-device confirmation.\n\nChanges:\n\n- 恢复 Beta14 已验证的紧凑帖子详情按钮，不再把完整图片数组塞进 DOM 属性。\n- 初始列表与动态筛选列表的多图均按 postId 保存在当前 WebView 内存，详情打开后继续与官方详情图片去重合并。\n- Beta15 投票尾元数据精确清理保留。\n- 其它书友圈功能及搜索/目录/正文 Provider/角色卡/账号链冻结。\n- Published SHA256: `{source_sha}`.\n\n\n'''; log_path.write_text(entry+log,encoding='utf-8')
handoff_path=root/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hand=handoff_path.read_text(encoding='utf-8'); note=f'''## 2026-08-26 · Current Beta {version} — Circle detail click hotfix\n\n- Stable remains 1.1.0.\n- Beta16 restores the proven compact post-detail button and moves multi-image transfer to an in-memory postId map seeded from initial and dynamic rows.\n- Beta15 poll metadata cleanup is retained. Awaiting real-device confirmation.\n\n'''; handoff_path.write_text(note+hand,encoding='utf-8')
assert hashlib.sha256(stable_path.read_bytes()).hexdigest()==stable_before
assert next(x for x in man['sources'] if x.get('id')=='qidian-next')['version']=='1.1.0'
assert next(x for x in man['sources'] if x.get('id')=='qidian-next-beta')['version']==version
print('BETA_VERSION',version); print('BETA_SHA256',source_sha); print('STABLE_SHA256_UNCHANGED',stable_before); print('VALIDATION OK')
