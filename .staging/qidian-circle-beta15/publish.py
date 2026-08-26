import json,re,base64,gzip,pathlib,hashlib,datetime,subprocess,tempfile

root=pathlib.Path('.')
source_path=root/'sources/novel/qidian-next/qidian-next-beta.json'
stable_path=root/'sources/novel/qidian-next/qidian-next.json'
stable_before=hashlib.sha256(stable_path.read_bytes()).hexdigest()

doc=json.loads(source_path.read_text(encoding='utf-8'))
assert isinstance(doc,list) and len(doc)==1
src=doc[0]
assert src.get('bookSourceName')=='🌈 起点增强 · Beta'
js=src['jsLib']
m=re.search(r'"circle":"gz:([A-Za-z0-9+/=]+)"',js)
assert m,'compressed circle entry not found'
old_payload=m.group(1)
code=gzip.decompress(base64.b64decode(old_payload)).decode('utf-8')


def rep(old,new,label):
    n=code.count(old)
    assert n==1,f'{label}: expected 1, got {n}'
    return code.replace(old,new,1)

# 1) Detail text: strip only a trailing poll metadata object. Do not broadly delete JSON.
marker='    h.push("function topicHtml(o,root){'
assert code.count(marker)==1,'topicHtml marker missing'
poll_helper='    h.push("function qfCleanPollText(s){s=String(s||\'\').trim();var p=s.lastIndexOf(\'{\');if(p>=0){try{var jo=JSON.parse(s.slice(p));if(jo&&jo.Options!==undefined&&jo.VoteId!==undefined&&jo.VoteType!==undefined)s=s.slice(0,p).trim();}catch(_qfPoll){}}return s;}");\n'
code=code.replace(marker,poll_helper+marker,1)

old='title=titleOf(o),rr=richOf(o),rich=rr.raw,body=rr.text,ims=imageUrls(o,rich)'
new='title=qfCleanPollText(titleOf(o)),rr=richOf(o),rich=rr.raw,body=qfCleanPollText(rr.text),ims=imageUrls(o,rich)'
code=rep(old,new,'topic poll cleanup')
old="bd=String(o.body||rr.text||''),ims=imageUrls(o,rich)"
new="bd=qfCleanPollText(String(o.body||rr.text||'')),ims=imageUrls(o,rich)"
code=rep(old,new,'feed poll cleanup')

# 2) Preserve list-card image order and merge all preview images into detail images.
old="if(state.previewImgs&&state.previewImgs.length){for(var pi=0;pi<state.previewImgs.length;pi++){var pu=qfNormUrl(state.previewImgs[pi]);if(pu&&ims.indexOf(pu)<0)ims.unshift(pu);}}"
new="if(state.previewImgs&&state.previewImgs.length){var mergedImgs=[],mergedSeen={};function qfMergeImg(u){u=qfNormUrl(u);if(/^https?:\\/\\//i.test(u)&&!mergedSeen[u]){mergedSeen[u]=1;mergedImgs.push(u);}}for(var pi=0;pi<state.previewImgs.length;pi++)qfMergeImg(state.previewImgs[pi]);for(var mi=0;mi<ims.length;mi++)qfMergeImg(ims[mi]);ims=mergedImgs;}"
code=rep(old,new,'detail image merge')

# 3) Carry the whole list image array through the detail button; keep data-img for compatibility.
old="data-img=\\\"'+esc(ims.length?ims[0]:'')+'\\\">查看详情"
new="data-img=\\\"'+esc(ims.length?ims[0]:'')+'\\\" data-imgs=\\\"'+esc(encodeURIComponent(JSON.stringify(ims.slice(0,9))))+'\\\">查看详情"
code=rep(old,new,'feed data-imgs')

# 4) Detail opener decodes up to nine preview images, dedupes, and falls back to legacy first image.
old="var pim=qfNormUrl(this.getAttribute('data-img')||'');state.previewImgs=pim?[pim]:[];"
new="var pim=qfNormUrl(this.getAttribute('data-img')||''),pims=[];try{var pie=String(this.getAttribute('data-imgs')||'');if(pie)pims=JSON.parse(decodeURIComponent(pie));}catch(_pi){}if(!Array.isArray(pims))pims=[];var pic=[],pis={};for(var px=0;px<pims.length&&pic.length<9;px++){var pu=qfNormUrl(pims[px]);if(/^https?:\\/\\//i.test(pu)&&!pis[pu]){pis[pu]=1;pic.push(pu);}}if(!pic.length&&pim)pic=[pim];state.previewImgs=pic;"
code=rep(old,new,'detail preview array')

assert 'qfCleanPollText' in code
assert 'data-imgs=' in code
assert 'JSON.parse(decodeURIComponent(pie))' in code
assert 'mergedImgs' in code
assert 'state.previewImgs=pim?[pim]:[]' not in code

# JavaScript syntax gate for decompressed lazy module.
with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as tf:
    tf.write(code); tmp=tf.name
subprocess.run(['node','--check',tmp],check=True)

# Repack only circle lazy module.
new_payload=base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9,mtime=0)).decode('ascii')
js2=js[:m.start(1)]+new_payload+js[m.end(1):]
assert js2.count('"circle":"gz:')==1
src['jsLib']=js2
src['bookSourceComment']='v1.1.0-beta15：书友圈帖子详情多图修复。列表卡片已有的完整配图数组会随“查看详情”传入详情页，与 getpostdetail 返回图片按原顺序去重合并，不再只保留第一张；同时过滤帖子正文尾部明确的 Options/VoteId/VoteType 投票元数据，回复、分类、视频、详情富数据、正文 Provider 等其它域冻结。'
src['lastUpdateTime']=int(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)
source_path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source_sha=hashlib.sha256(source_path.read_bytes()).hexdigest()

# Verify repacked module can be decoded and contains Beta15 fix.
chk=json.loads(source_path.read_text(encoding='utf-8'))[0]['jsLib']
cm=re.search(r'"circle":"gz:([A-Za-z0-9+/=]+)"',chk);assert cm
cc=gzip.decompress(base64.b64decode(cm.group(1))).decode('utf-8')
assert 'data-imgs=' in cc and 'qfCleanPollText' in cc and 'state.previewImgs=pic' in cc
assert old_payload!=cm.group(1)

# Beta bundle: replace only qidian-next beta object.
bundle_path=root/'bundles/all-beta.json'
bundle=json.loads(bundle_path.read_text(encoding='utf-8'))
hits=[i for i,x in enumerate(bundle) if isinstance(x,dict) and x.get('bookSourceName')=='🌈 起点增强 · Beta']
assert len(hits)==1,('bundle hits',hits)
bundle[hits[0]]=src
bundle_path.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

now_cn=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
now_iso=now_cn.isoformat(timespec='seconds'); day=now_cn.strftime('%Y-%m-%d')
version='1.1.0-beta15'; version_code=11015
summary='书友圈 beta15：修复列表多图进入帖子详情后只剩一张，并清理投票结构元数据。'
tags=['起点','测试版','书友圈','帖子详情','多图','投票清理','评论']
changes=[
 '书友圈列表卡片的完整图片数组随“查看详情”一起传入详情页，不再只传第一张',
 '详情页将列表预览图与起点 getpostdetail 图片按原顺序去重合并，最多保留 9 张正文配图',
 '仅清理正文尾部可确认的 Options/VoteId/VoteType 投票元数据，不做宽泛 JSON 删除',
 '评论/楼中楼、分类筛选、同人视频、搜索、目录、正文 Provider、角色卡、账号链冻结',
]
raw=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}'
cdn=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={version_code}'
imp='legado://import/importonline?src='+raw

sub_path=root/'subscription/beta.json'; sub=json.loads(sub_path.read_text(encoding='utf-8'))
item=next(x for x in sub['items'] if x.get('id')=='qidian-next-beta')
item.update({'summary':summary,'version':version,'updatedAt':day,'tags':tags,'changelog':changes,'sourceUrl':raw,'backupUrl':cdn,'importUrl':imp})
sub['updatedAt']=now_iso
sub_path.write_text(json.dumps(sub,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

man_path=root/'manifest.json'; man=json.loads(man_path.read_text(encoding='utf-8'))
mi=next(x for x in man['sources'] if x.get('id')=='qidian-next-beta')
mi.update({'version':version,'versionCode':version_code,'updatedAt':now_iso,'sourceUrl':raw,'summary':summary,'tags':tags,'changelog':changes,'sha256':source_sha})
man['updatedAt']=now_iso
man_path.write_text(json.dumps(man,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rss_path=root/'rss/data/details/beta/qidian-next.json'
rss={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',version,'书友圈多图'], 'sections':[
 {'title':'帖子详情多图','text':'列表卡片已经解析到的全部正文图片会随帖子 ID 一起进入详情页，并与详情接口图片去重合并。'},
 {'title':'投票元数据清理','text':'移除正文尾部明确的 Options / VoteId / VoteType 结构对象，正常文字和其它 JSON 内容不做宽泛删除。'},
 {'title':'冻结范围','text':'书友圈回复/楼中楼、分类、同人视频以及搜索、目录、正文 Provider、角色卡和账号链保持不变。'}
 ],'sourceUrl':raw,'backupUrl':cdn,'importUrl':imp}
rss_path.write_text(json.dumps(rss,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

log_path=root/'docs/RELEASE_LOG.md'; log=log_path.read_text(encoding='utf-8')
entry=f'''## {day} — Qidian Next {version} circle detail multi-image fix\n\nStatus: Beta/Test; awaiting user real-device confirmation.\n\nChanges:\n\n- 书友圈列表已有的完整正文图片数组随帖子详情入口传递，不再只保留第一张图。\n- 帖子详情将列表预览图与 getpostdetail 返回图按原顺序去重合并，最多 9 张。\n- 详情正文仅过滤尾部明确的 Options / VoteId / VoteType 投票结构元数据。\n- 评论/楼中楼、分类筛选、同人视频、搜索、目录、正文 Provider、角色卡与账号链冻结。\n- Published SHA256: `{source_sha}`.\n\n\n'''
log_path.write_text(entry+log,encoding='utf-8')

handoff_path=root/'docs/sources/qidian-next/PROJECT_HANDOFF.md'
if handoff_path.exists():
    hand=handoff_path.read_text(encoding='utf-8')
    note=f'''## 2026-08-26 · Current Beta {version} — Circle detail multi-image\n\n- Stable remains 1.1.0.\n- Beta15 changes only the lazy `circle` module: preserve all list-card post images into detail and remove confirmed poll metadata leakage.\n- Awaiting real-device confirmation before any Stable promotion.\n\n'''
    handoff_path.write_text(note+hand,encoding='utf-8')

# Final gates.
assert hashlib.sha256(stable_path.read_bytes()).hexdigest()==stable_before,'Stable source changed'
assert json.loads(source_path.read_text(encoding='utf-8'))[0]['bookSourceName']=='🌈 起点增强 · Beta'
assert next(x for x in json.loads(man_path.read_text(encoding='utf-8'))['sources'] if x.get('id')=='qidian-next')['version']=='1.1.0'
assert next(x for x in json.loads(man_path.read_text(encoding='utf-8'))['sources'] if x.get('id')=='qidian-next-beta')['version']==version
assert next(x for x in json.loads(sub_path.read_text(encoding='utf-8'))['items'] if x.get('id')=='qidian-next-beta')['version']==version
print('BETA_VERSION',version)
print('BETA_SHA256',source_sha)
print('STABLE_SHA256_UNCHANGED',stable_before)
print('CIRCLE_OLD_GZ',len(old_payload),'CIRCLE_NEW_GZ',len(new_payload))
print('VALIDATION OK')
