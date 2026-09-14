import json, hashlib, base64, gzip
from pathlib import Path

ROOT=Path('.')
STABLE=ROOT/'sources/novel/qidian-next/qidian-next.json'
BETA=ROOT/'sources/novel/qidian-next/qidian-next-beta.json'
VERSION='1.2.7-beta2'; VC=12072; TS='2026-09-14T22:25:00+08:00'
IDENTITY='https://m.qidian.com/?qf_source=qidian_next_8d7'
RAW=f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
BACKUP=f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next-beta.json?v={VC}'
IMPORT='legado://import/importonline?src='+RAW
DETAIL='https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/beta/qidian-next.json?article=2'

stable_arr=json.loads(STABLE.read_text(encoding='utf-8'))
stable=stable_arr[0] if isinstance(stable_arr,list) else stable_arr
arr=json.loads(BETA.read_text(encoding='utf-8'))
s=arr[0] if isinstance(arr,list) else arr
before=json.loads(json.dumps(s,ensure_ascii=False))
js=str(s.get('jsLib',''))
mark='var QF_MOD38_PACK='; p=js.find(mark); assert p>=0
start=js.find('{',p+len(mark)); depth=0; quote=''; escp=False; end=-1
for i in range(start,len(js)):
    ch=js[i]
    if quote:
        if escp: escp=False
        elif ch=='\\': escp=True
        elif ch==quote: quote=''
        continue
    if ch in ('"',"'"): quote=ch; continue
    if ch=='{': depth+=1
    elif ch=='}':
        depth-=1
        if depth==0: end=i+1; break
assert end>start
pack=json.loads(js[start:end])
raw=pack['review_local_ui']; assert raw.startswith('gz:')
b64=raw[3:]+'='*(-len(raw[3:])%4)
code=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
old_code=code

# Keep beta1 paging behavior exactly.
assert 'autoLoadBudget=0' in code
assert 'h-y-v<600' in code
assert '已加载全部回复' in code
assert 'pageSize=10' in code

# 1) Emoji: keep the reference [fn=N] map but render after HTML escaping and force color-emoji fallback fonts.
es=code.index('function esc(s){')
pe=code.index('function parse(raw){',es)
assert es>=0 and pe>es
emoji_block=r'''function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}
function qfEmojiHtmlV1272(n){var v=EM[Number(n)];return v?'<span class="qfEmoji">'+esc(v)+'</span>':'💬'}
function fmt(s){
    var raw=String(s==null?'':s);
    var safe=esc(raw);
    /* 妙想天开同款 [fn=N]；同时兼容接口偶发带反斜杠/实体括号的形式。 */
    safe=safe.replace(/\\?\[fn=(\d+)\]\\?/gi,function(m,n){return qfEmojiHtmlV1272(n)});
    safe=safe.replace(/&#91;fn=(\d+)&#93;/gi,function(m,n){return qfEmojiHtmlV1272(n)});
    return safe.replace(/\r\n|\r|\n/g,'<br>');
}
'''
code=code[:es]+emoji_block+code[pe:]

# Explicit emoji font fallback for actual Unicode emoji and mapped [fn] tokens.
css_anchor='.content{font-size:15px;line-height:1.62;color:var(--text);margin-top:5px;white-space:normal;word-break:break-word}'
assert css_anchor in code
css_new=css_anchor+'.content,.rContent,.qfEmoji{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Noto Color Emoji","Segoe UI Emoji","Apple Color Emoji",sans-serif}.qfEmoji{display:inline;font-size:1.08em;line-height:1;vertical-align:-.04em;font-family:"Noto Color Emoji","Segoe UI Emoji","Apple Color Emoji",sans-serif}'
code=code.replace(css_anchor,css_new,1)

# 2) Avatar canonical fields: broaden official aliases and normalize protocol-relative/escaped URLs.
old_avatar='''        avatar:String(\n            user.user_avatar||user.UserHeadIcon||\n            user.Avatar||user.avatar||\n            raw.UserHeadIcon||raw.userHeadIcon||\n            raw.Avatar||raw.avatar||\n            ""\n        ),'''
assert old_avatar in code
new_avatar='''        avatar:qfNormAssetUrlV1272(String(\n            user.user_avatar||user.UserHeadIcon||user.userHeadIcon||\n            user.UserAvatar||user.userAvatar||user.AvatarUrl||user.avatarUrl||\n            user.HeadIcon||user.headIcon||user.HeadUrl||user.headUrl||\n            user.FaceUrl||user.faceUrl||user.Avatar||user.avatar||\n            raw.UserHeadIcon||raw.userHeadIcon||\n            raw.UserAvatar||raw.userAvatar||raw.AvatarUrl||raw.avatarUrl||\n            raw.HeadIcon||raw.headIcon||raw.HeadUrl||raw.headUrl||\n            raw.FaceUrl||raw.faceUrl||raw.Avatar||raw.avatar||\n            ""\n        )),'''
code=code.replace(old_avatar,new_avatar,1)

old_copy="var ks=['UserName','userName','NickName','nickName','UserHeadIcon','userHeadIcon','Avatar','avatar','UserId','userId','UserID','userID'];"
assert old_copy in code
new_copy="var ks=['UserName','userName','NickName','nickName','UserHeadIcon','userHeadIcon','UserAvatar','userAvatar','AvatarUrl','avatarUrl','HeadIcon','headIcon','HeadUrl','headUrl','FaceUrl','faceUrl','Avatar','avatar','UserId','userId','UserID','userID'];"
code=code.replace(old_copy,new_copy,1)

# 3) Badge rendering: if TitleInfoList has the official TitleImage, prefer that asset exactly like 妙想天开.
bh=code.index('function badgeHtml(t){')
ah=code.index('function avHtml(c,reply){',bh)
assert bh>=0 and ah>bh
asset_block=r'''function qfNormAssetUrlV1272(u){
    u=String(u==null?'':u).trim();
    if(!u)return '';
    u=u.replace(/\\u002f/gi,'/').replace(/\\\//g,'/');
    if(/^\/\//.test(u))u='https:'+u;
    if(/^http:\/\//i.test(u))u='https://'+u.slice(7);
    if(/^\/(?:qd_face|facepic)\//i.test(u))u='https://facepic.qidian.com'+u;
    if(!/^[a-z][a-z0-9+.-]*:\/\//i.test(u)&&/^(?:facepic|qidian|qdfm|img|bookcover|bossa)[a-z0-9.-]*\.(?:qidian\.com|gtimg\.com|qq\.com)\//i.test(u))u='https://'+u;
    return /^(?:https?:|data:image)/i.test(u)?u:'';
}
function qfTitleImageV1272(t){
    if(!t)return '';
    var r=t.raw||{};
    var im=r.TitleImage||r.titleImage||r.title_image||r.TitleImageOfNight||r.titleImageOfNight||r.TitleImageOfDark||r.titleImageOfDark||'';
    if(!im&&t.type==='img')im=t.val||'';
    return qfNormAssetUrlV1272(im);
}
function badgeHtml(t){
    if(!t)return'';
    var im=qfTitleImageV1272(t);
    if(im){
        return '<img class="badgeImg qfOfficialBadge" src="'+esc(im)+'" referrerpolicy="no-referrer" loading="lazy" decoding="async" onerror="this.style.display=\\'none\\'">';
    }
    var c='badgeText',v=String(t.val||''),compact=v.replace(/[\s·•・\-_|｜]/g,'');
    if(t.role==='rank'||/^(见习|学徒|执事|舵主|堂主|护法|长老|掌门|盟主)$/.test(compact))c+=' rank';
    else if(t.role==='official'||/纪律助理|版主|管理员|运营|助理/.test(v))c+=' official';
    else if(t.role==='level'||/^(?:lv?|等级)\d{1,2}(?:天枢|天璇|天玑|天权|玉衡|开阳|摇光)?$/i.test(compact))c+=' level';
    else if(/红尘仙|十年大佬|种花少年|种花少女/.test(v))c+=' pink';
    else if(/长鲸月落/.test(v))c+=' deepBlue';
    else if(/鉴中仙|逢考必胜/.test(v))c+=' red';
    else if(t.tp===2)c+=' t2';else if(t.tp===3)c+=' t3';else if(t.tp>=4)c+=' t4';
    var st=[];
    if(/^心理医生$/.test(v)){t.fg='#7c5a1d';t.bg='#f8e9bd';t.bd='#ead394';}
    else if(/^守知者$/.test(v)){t.fg='#7b4f35';t.bg='#f2ded2';t.bd='#e7c6b4';}
    else if(/^占星人$/.test(v)){t.fg='#73518f';t.bg='#eee6f8';t.bd='#d9c8ec';}
    if(t.fg)st.push('color:'+t.fg);if(t.bg)st.push('background:'+t.bg);if(t.bd)st.push('border-color:'+t.bd);
    return '<span class="'+c+'"'+(st.length?' style="'+esc(st.join(';'))+'"':'')+'>'+esc(v)+'</span>';
}
'''
code=code[:bh]+asset_block+code[ah:]

# Avatar renderer: always keep a username-initial fallback behind the image; failed remote image no longer leaves a blank circle.
ah=code.index('function avHtml(c,reply){')
mh=code.index('function meta(c){',ah)
assert ah>=0 and mh>ah
avatar_html=r'''function avHtml(c,reply){
    var cl=reply?'rAvatar':'avatar';
    var nm=String(c&&c.name||'书').trim();
    var at=nm?nm.charAt(0):'书';
    var u=qfNormAssetUrlV1272(c&&c.avatar||'');
    var h='<div class="'+cl+'"><span class="avatarFallback">'+esc(at)+'</span>';
    if(u)h+='<img src="'+esc(u)+'" referrerpolicy="no-referrer" loading="lazy" decoding="async" onerror="this.style.display=\\'none\\'">';
    h+='</div>';return h;
}
'''
code=code[:ah]+avatar_html+code[mh:]

# Official badge geometry and avatar fallback layer.
old_badge_css='.badgeImg{height:16px;width:auto;max-width:68px;object-fit:contain}'
assert old_badge_css in code
new_badge_css='.badgeImg{height:17px;width:auto;max-width:92px;object-fit:contain;display:block}.qfOfficialBadge{flex:0 0 auto}.rBadges .badgeImg{height:15px;max-width:78px}.avatar,.rAvatar{position:relative}.avatarFallback{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#9b9b9b;font-weight:600}.avatar img,.rAvatar img{position:absolute;inset:0;z-index:1;width:100%;height:100%;object-fit:cover;background:inherit}'
code=code.replace(old_badge_css,new_badge_css,1)

# Hide a failed decorative frame rather than covering the avatar with a broken image icon.
code=code.replace('(c.frame?\'<div class="frame"><img src="\'+esc(c.frame)+\'" referrerpolicy="no-referrer"></div>\':\'\')',"(c.frame?'<div class=\"frame\"><img src=\"'+esc(qfNormAssetUrlV1272(c.frame))+'\" referrerpolicy=\"no-referrer\" onerror=\"this.style.display=\\\'none\\\'\"></div>':'')",1)

assert code!=old_code
assert 'qfOfficialBadge' in code and 'qfNormAssetUrlV1272' in code
assert 'qfEmojiHtmlV1272' in code and 'Noto Color Emoji' in code
assert 'avatarFallback' in code and 'UserAvatar' in code and 'FaceUrl' in code
assert 'autoLoadBudget=0' in code and 'h-y-v<600' in code and '已加载全部回复' in code

pack['review_local_ui']='gz:'+base64.b64encode(gzip.compress(code.encode('utf-8'),compresslevel=9)).decode('ascii')
s['jsLib']=js[:start]+json.dumps(pack,ensure_ascii=False,separators=(',',':'))+js[end:]
s['bookSourceName']='🌈 起点增强 · Beta'
s['bookSourceGroup']='﹅🧪 测试源'
s['bookSourceComment']='v1.2.7-beta2：继续参考妙想天开优化评论显示。TitleInfoList 有官方 TitleImage 时优先直接显示官方图形标签；[fn=N] 表情按参考映射并增加 Emoji 字体兜底；头像扩展官方字段、协议相对地址规范化及用户名首字兜底，图片失败不再空白。完整继承 beta1 首屏10条、600px近底翻页和楼中楼完成态；评论请求链及目录/正文/版权/账号/Provider 不变。'

# Strong isolation: beta1 -> beta2 only jsLib/display metadata may differ; stable business fields stay frozen.
for k,v in before.items():
    if k in ('jsLib','bookSourceName','bookSourceGroup','bookSourceComment'): continue
    assert s.get(k)==v,'unexpected beta1 field changed: '+k
for k in ('ruleToc','ruleBookInfo','ruleContent','bookSourceUrl'):
    assert s.get(k)==stable.get(k),'stable business field changed: '+k
assert s['bookSourceUrl']==IDENTITY

BETA.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=hashlib.sha256(BETA.read_bytes()).hexdigest()
summary='Beta 1.2.7-beta2：评论标签改用起点官方图形 TitleImage，补强表情与头像显示；继承 beta1 按需分页。'
tags=['起点','测试版','评论优化','妙想天开参考','官方标签','TitleImage','Emoji','头像兜底','10条首屏','滚动分页','Stable 1.2.6基线']
changes=[
 '基于 1.2.7-beta1，仅修改 review_local_ui；首屏10条、取消后台预取、600px近底翻页原样保留',
 '参考妙想天开：TitleInfoList 同时存在 TitleName/TitleImage 时优先渲染起点官方 TitleImage，不再默认把图形称号降级成 CSS 文字标签',
 '表情继续使用起点 [fn=N] 映射，改为 HTML 转义后识别并加入 Noto/Segoe/Apple Color Emoji 字体兜底，兼容带反斜杠及实体括号形式',
 '头像扩展 UserAvatar/AvatarUrl/HeadIcon/HeadUrl/FaceUrl 等官方字段；统一 //、转义斜杠、http/https，并用用户名首字作为图片失败兜底',
 '评论接口/签名、TitleInfoList 数据融合、配图/配音、楼中楼请求链、目录、版权、正文、账号和 Provider 全部冻结'
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
detail={'kind':'source','title':'🌈 起点增强 · Beta','summary':summary,'badges':['Beta',VERSION,'评论显示'],'sourceUrl':RAW,'backupUrl':BACKUP,'importUrl':IMPORT,'sections':[
 {'title':'标签','text':'TitleInfoList 优先使用起点官方 TitleImage 图形称号，视觉向妙想天开靠拢；没有官方图片时仍保留原文字标签兜底。'},
 {'title':'表情','text':'[fn=N] 使用与参考源一致的起点表情映射，并增加 WebView Emoji 字体兜底及转义形式兼容。'},
 {'title':'头像','text':'扩展官方头像字段和 URL 规范化；远程头像加载失败时直接显示用户名首字，不再出现空白/破图头像。'},
 {'title':'冻结项','text':'继承 beta1 的10条首屏/按需分页；评论请求和数据链、目录、版权、正文、账号、Provider 全部不修改。'}]}
dp.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rp=ROOT/'docs/RELEASE_LOG.md'; rp.write_text((f"## 2026-09-14 · qidian-next {VERSION}\n- 用户真机截图要求评论标签继续向妙想天开靠拢，并修复表情、少量头像显示失败。\n- 仅修改 `review_local_ui`：TitleInfoList 优先官方 TitleImage；表情增加参考映射/Emoji 字体兜底；头像扩展字段、URL规范化和首字兜底。\n- 完整继承 beta1 首屏10条、取消后台预取、近底600px分页与楼中楼完成态。\n- 评论请求/签名、媒体/楼中楼数据链、目录、版权、正文、账号、Provider 全部冻结。\n- 未经真机确认不得晋升 Stable。\n\n")+rp.read_text(encoding='utf-8'),encoding='utf-8')

hp=ROOT/'docs/sources/qidian-next/PROJECT_HANDOFF.md'; hp.write_text((f"## 2026-09-14 · {VERSION} — 评论标签/表情/头像显示优化\n\n- 基线：1.2.7-beta1 / Stable 1.2.6。\n- 仅 `review_local_ui`：官方 TitleImage 标签优先、[fn] Emoji 显示增强、头像字段与失败兜底增强。\n- beta1 的首屏10条和按需滚动分页保持不变；评论请求和其它业务域禁止修改。\n- 等用户真机确认标签、表情和异常头像。\n\n")+hp.read_text(encoding='utf-8'),encoding='utf-8')

report=ROOT/'.staging/qidian-127b2-report.json'
report.write_text(json.dumps({'version':VERSION,'versionCode':VC,'betaSha256':sha,'baseline':'1.2.7-beta1 / Stable 1.2.6','changedPackedModule':'review_local_ui','officialTitleImagePreferred':True,'emojiMapReferenceCompatible':True,'emojiFontFallback':True,'avatarAliasExpansion':True,'avatarInitialFallback':True,'firstPageStrict10Preserved':True,'backgroundPrefetchPages':0,'scrollThresholdPx':600,'ruleTocFrozen':True,'ruleBookInfoFrozen':True,'ruleContentFrozen':True,'bookSourceUrlFrozen':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(VERSION,sha)
