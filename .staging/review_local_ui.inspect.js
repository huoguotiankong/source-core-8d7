/* v4.2.0-alpha1：Review Identity Canonical Model。
 * 只重构起点本地评论身份标签：
 * - 数据源只认真实 TitleInfoList / UserInfo.TitleInfoList；
 * - TitleName 与当前用户名完全相同则拒绝，禁止用户名误当标签；
 * - 解析 QDReader APK 实际字段：TitleName / TitleImage / TitleImageOfNight|Dark /
 *   TitleType / TitleShowType / TitleSubType / TitleTextColor；
 * - 见习/学徒/执事等粉丝等级、LV3 玉衡等星级、活动称号统一 canonical；
 * - 根评论与楼中楼继续共用 Reader 富身份注册表，不改结构骨架与请求链。
 */
/* v4.0.0-alpha29.4：作者说整节点精准匹配。APK 确认 AuthorReview 仅含 AuthorHead/AuthorReview/ReviewId，真实 ParagraphId+CommentCount 位于同一 ParagraphCommentCountItem 父节点；按作者说正文锁定整节点并允许 19 覆盖旧污染 119，再按精确 ParagraphId 选择评论流。 */
/* v4.0.0-alpha29.1：作者说元数据缺回复数时允许二次探测；配合主线程真实 ReviewId 修复。 */
/* v4.0.0-alpha29：作者说楼中楼统一分页。作者详情低频解析真实 AuthorReview ReviewId/ParagraphId/CommentCount；优先使用官方 getchapterreviewdetail 获取作者说回复，失败再回退通用楼中楼链；首次点击与继续加载复用 alpha28.1 canonical 分页器。 */
/* v4.0.0-alpha28.1：首次展开完整回复 + 标签统一。第一次点击“展开全部”不再只展示根评论自带的少量 embedded replyList，而是直接低频拉取楼中楼第1页并走 alpha28 Reader 富身份融合；因此首批回复与后续回复使用同一数据链、同样带 TitleInfoList。 */
/* v4.0.0-alpha18.5.1：稳定性回退。完全撤销 alpha18.5 的头像/用户名楼中楼身份注册表实验，恢复 alpha18.4 已验证的快速段评加载链；仅保留“心理医生/守知者/占星人”标签底色优化。楼中楼标签继续冻结，后续集中处理。 */
/* v4.0.0-alpha18.4：评论配图误识别 + 楼中楼标签注册表。评论媒体只接受内容语义图片，拒绝称号/神评论/勋章/皮肤等装饰资源；Reader 富身份建立 UserId/唯一用户名标签注册表，share 楼中楼即使 ReplyId 不一致也可按用户身份补回真实 TitleInfoList。 */
/* v4.0.0-alpha18.3：标签融合增强。TitleImage+TitleName 优先文字标签避免破图；楼中楼富身份按 ReplyId/ReviewId/UserId/用户名/正文多键索引融合，Reader 深层 UserInfo 标签也可补回 share 回复骨架。 */
/* v4.0.0-alpha18.2：标签与楼中楼 canonical 骨架融合。根评论/回复永远以完整结构链为骨架，Reader 富数据只增量覆盖 TitleInfoList；恢复正文/章名/本章说楼中楼，并让回复本身保留标签。 */
/* v4.0.0-alpha18.1：评论富身份 + 楼中楼结构数据融合。正文/章名/本章说统一保留 TitleInfoList、ReviewId、ReplyCount/replyList；特殊 paragraphId 的楼中楼允许 Reader v2 富回复链。 */
/* beta24.6：QDReader 段评完整 QDSign 结构对齐，恢复 TitleInfoList 富标签数据。 */
function getBuiltInCommentHtmlV21(){return String.raw`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><title>段评</title><style>
:root{--bg:#fff;--panel:#fff;--text:#171717;--sub:#8b8b8b;--muted:#a7a7a7;--line:#ededed;--soft:#f7f7f7;--reply:#f7f7f8;--accent:#ef5b50;--quote:#f8f8f8;--quote-line:#aeb8c8;--like:#9b9b9b}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}html,body{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;-webkit-text-size-adjust:100%;text-size-adjust:100%}body{min-height:100vh;font-size:14px}button{font:inherit}.hidden{display:none!important}
.sticky{position:sticky;top:0;z-index:30;background:var(--panel);border-bottom:1px solid var(--line)}
.row1{height:58px;padding:0 24px 0 27px;display:flex;align-items:center;gap:0}.tabs{display:flex;align-items:stretch;height:100%;min-width:0;flex:1}.tab{height:100%;display:flex;align-items:center;position:relative;margin-right:27px;color:var(--sub);font-size:15px;white-space:nowrap;cursor:pointer}.tab.active{font-weight:700;color:var(--text)}.tab .n{font-size:12px;color:var(--muted);margin-left:3px;font-weight:400}.tab .n:empty{display:none}.tab.active .n{color:var(--accent);font-weight:600}.tab.active:after{content:"";position:absolute;left:50%;bottom:6px;width:27px;height:3px;background:var(--accent);border-radius:3px;transform:translateX(-50%)}
.actions{margin-left:auto;display:flex;align-items:center;gap:19px;flex:0 0 auto}.iconBtn{width:31px;height:31px;border:0;background:transparent;display:flex;align-items:center;justify-content:center;color:var(--muted);padding:0;cursor:pointer}.quoteIcon{width:25px;height:25px;border:1.7px solid currentColor;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;line-height:1}.iconBtn.quote-on{color:var(--accent)}.themeGlyph{width:22px;height:22px;border:1.8px solid currentColor;border-radius:50%;display:block;position:relative;overflow:hidden}.themeGlyph:after{content:"";position:absolute;left:0;top:0;width:50%;height:100%;background:currentColor}
.row2{height:49px;display:flex;align-items:center;padding:0 29px;color:var(--muted);border-top:1px solid #f6f6f6}.sortLabel{font-size:13px;color:var(--muted);flex:1}.sorts{display:flex;align-items:center}.sort{border:0;background:transparent;padding:0 17px;color:var(--muted);font-size:13px;cursor:pointer;height:22px;line-height:22px;position:relative}.sort+.sort:before{content:"";position:absolute;left:0;top:3px;width:1px;height:17px;background:#e9e9e9}.sort.active{color:var(--accent);font-weight:600}
.quoteWrap{padding:20px 25px 13px;background:var(--panel)}.quoteCard{min-height:58px;border:1px solid #e9e9e9;border-radius:11px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,.025);padding:14px 18px 14px 23px;display:flex;align-items:center;position:relative;overflow:hidden;color:#2d3442;font-size:14px;line-height:1.62;white-space:pre-wrap;word-break:break-word}.quoteCard:before{content:"";position:absolute;left:0;top:0;bottom:0;width:6px;background:var(--quote-line);border-radius:11px 0 0 11px}
.list{background:var(--panel)}.empty,.loading,.error{padding:30px 16px;text-align:center;color:var(--muted);font-size:13px}.error{color:#d85b50}.spinner{width:22px;height:22px;border:3px solid #e1e1e1;border-top-color:var(--accent);border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 7px}@keyframes spin{to{transform:rotate(360deg)}}
.comment{position:relative;padding:15px 10px 14px 18px;border-bottom:1px solid var(--line);background:var(--panel);min-height:100px}.mainRow{display:flex;align-items:flex-start;padding-right:0}.avatarWrap{position:relative;width:42px;height:42px;flex:0 0 42px;margin-right:11px}.avatar{width:42px;height:42px;border-radius:50%;overflow:hidden;background:#eee;display:flex;align-items:center;justify-content:center;color:#aaa;font-size:14px}.avatar img{width:100%;height:100%;object-fit:cover}.frame{position:absolute;left:-5px;top:-5px;width:52px;height:52px;pointer-events:none}.frame img{width:100%;height:100%;object-fit:contain}.body{flex:1;min-width:0}.nameRow{height:25px;display:flex;align-items:center;white-space:nowrap;overflow:hidden}.name{font-size:15px;font-weight:650;color:var(--text);overflow:hidden;text-overflow:ellipsis;min-width:0;max-width:58vw}.badges{display:flex;align-items:center;gap:4px;margin-left:6px;flex:0 0 auto}.badgeImg{height:16px;width:auto;max-width:68px;object-fit:contain}.badgeText{display:inline-flex;align-items:center;height:17px;border-radius:4px;padding:0 4px;font-size:10px;line-height:16px;border:1px solid #e8c86b;color:#c88f20;background:#fff;white-space:nowrap;font-weight:500}.badgeText.rank{color:#d69b2a;background:#fff;border-color:#e8c56a}.badgeText.official{color:#5d82d9;background:#fff;border-color:#a9c0ef}.badgeText.pink{color:#e65d76;background:#ffe5eb;border-color:#ffe5eb}.badgeText.deepBlue{color:#eef6ff;background:#456f9c;border-color:#456f9c}.badgeText.red{color:#fff3f3;background:#c95652;border-color:#c95652}.badgeText.level{color:#f6f2ff;background:#65528e;border-color:#65528e}.badgeText.t2{color:#d95565;background:#fff1f3;border-color:#f7c7cd}.badgeText.t3{color:#6d7da7;background:#f0f3fa;border-color:#cdd5e7}.badgeText.t4{color:#8f72c4;background:#f5f0fb;border-color:#dfd2f0}
.content{font-size:15px;line-height:1.62;color:var(--text);margin-top:5px;white-space:normal;word-break:break-word}.mediaImg{display:block;max-width:min(64vw,390px);max-height:300px;width:auto;height:auto;border-radius:8px;margin-top:9px;background:#f2f2f2}.audio{width:min(64vw,390px);margin-top:9px}.metaLine{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:6px;min-width:0}.meta{font-size:12px;color:var(--sub);margin-top:0;padding-right:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0}.like{position:static;transform:none;width:auto;display:flex;flex:0 0 auto;flex-direction:row;align-items:center;justify-content:flex-end;gap:2px;color:var(--like);font-size:10.5px;line-height:16px;white-space:nowrap}.like svg{width:16px;height:16px;display:block;margin:0;stroke:currentColor;fill:none;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.replyToggle{margin-left:53px;margin-top:9px;display:inline-flex;align-items:center;gap:5px;font-size:13px;color:var(--sub);cursor:pointer;padding:2px 0}.replyToggle svg{width:13px;height:13px;stroke:currentColor;fill:none;stroke-width:2}.replies{margin:8px 0 0 53px;background:var(--reply);border-radius:9px;overflow:hidden}.reply{position:relative;padding:10px 10px 10px 10px;border-bottom:1px solid var(--line)}.reply:last-child{border-bottom:0}.replyHead{display:flex;align-items:center;min-width:0}.rAvatar{width:24px;height:24px;border-radius:50%;overflow:hidden;background:#e8e8e8;flex:0 0 24px;margin-right:6px}.rAvatar img{width:100%;height:100%;object-fit:cover}.rName{font-size:12.5px;font-weight:600;max-width:45vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.rBadges{display:flex;gap:3px;margin-left:4px}.rContent{font-size:13px;line-height:1.58;margin:5px 0 0 30px;padding-right:2px;white-space:normal;word-break:break-word;overflow-wrap:anywhere}.replyTo{color:var(--sub)}.rMetaLine{display:flex;align-items:center;justify-content:space-between;gap:6px;margin:5px 0 0 30px;min-width:0}.rMeta{font-size:10.5px;color:var(--muted);margin:0;padding-right:0;white-space:normal;line-height:1.35;flex:1;min-width:0}.rLike{position:static;transform:none;width:auto;display:flex;flex:0 0 auto;flex-direction:row;align-items:center;justify-content:flex-end;gap:1px;color:var(--muted);font-size:8.5px;line-height:12px;white-space:nowrap}.rLike svg{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:1.45;margin:0}.replyMore{padding:8px 12px 10px 44px;color:var(--sub);font-size:12px;cursor:pointer}
.god{position:absolute;right:20px;top:13px;transform:rotate(12deg);border:1.3px solid #b8924d;border-radius:50%;width:38px;height:38px;display:flex;align-items:center;justify-content:center;color:#b8924d;font-size:9px;font-weight:700;opacity:.92;pointer-events:none}
.loadMore{padding:15px;text-align:center;color:var(--muted);background:var(--panel);font-size:13px;cursor:pointer}
.lightbox{position:fixed;inset:0;background:rgba(0,0,0,.9);z-index:1000;display:flex;align-items:center;justify-content:center}.lightbox img{max-width:94vw;max-height:94vh;object-fit:contain}
body.dark{--bg:#191919;--panel:#191919;--text:#ededed;--sub:#a7a7a7;--muted:#888;--line:#2c2c2c;--soft:#242424;--reply:#242424;--quote:#242424;--quote-line:#697281;--like:#8f8f8f}.dark .quoteCard{background:#202020;border-color:#333;color:#dedede;box-shadow:none}.dark .row2{border-top-color:#262626}.dark .sort+.sort:before{background:#333}.dark .badgeText{background:#242424;border-color:#6d5d35;color:#d8b65d}.dark .badgeText.rank{background:#24211b;border-color:#6a5934;color:#e1b95a}.dark .badgeText.official{background:#222936;border-color:#4d6694;color:#90aee9}.dark .badgeText.pink{background:#42282f;border-color:#5a3039;color:#f08ba0}.dark .badgeText.deepBlue{background:#334e6a;border-color:#334e6a;color:#eef6ff}.dark .badgeText.red{background:#743b3b;border-color:#743b3b;color:#fff}.dark .badgeText.level{background:#4c426a;border-color:#4c426a;color:#f7f3ff}.dark .badgeText.t2{background:#302326}.dark .badgeText.t3{background:#252936}.dark .badgeText.t4{background:#2d2735}.dark .content,.dark .rContent,.dark .rName{color:#ededed}.dark .tab,.dark .row2,.dark .sortLabel,.dark .sort,.dark .meta,.dark .replyToggle,.dark .replyTo,.dark .rMeta,.dark .rLike,.dark .replyMore,.dark .loadMore{color:#a7a7a7}.dark .tab.active,.dark .sort.active{color:var(--accent)}.dark .tab.active{color:#ededed}.dark .avatar{background:#2a2a2a;color:#aaa}.dark .rAvatar{background:#2a2a2a}.dark .mediaImg{background:#252525}
.mediaEmptyCompact{padding:48px 14px!important;color:var(--muted)!important;font-size:14px!important}
.toTop{position:fixed;right:18px;bottom:26px;width:42px;height:42px;border:0;border-radius:50%;background:rgba(30,30,30,.72);color:#fff;font-size:20px;z-index:35;box-shadow:0 4px 18px rgba(0,0,0,.18)}.dark .toTop{background:rgba(245,245,245,.18)}
/* beta15：长评论折叠、回复入口和失败重试。 */
.content.qfFoldable.qfFolded{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:6;overflow:hidden}
.rContent.qfFoldable.qfFolded{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:4;overflow:hidden}
.foldBtn{display:inline-flex;align-items:center;margin:5px 0 0;padding:2px 0;border:0;background:transparent;color:var(--accent);font-size:12px;font-weight:600;cursor:pointer}
.reply .foldBtn{margin-left:32px;margin-top:4px;font-size:11.5px}
.replyToggle{background:var(--soft);border-radius:15px;padding:6px 10px;margin-top:10px;transition:background .14s ease}.qfAuthorReplyToggle{background:transparent;border-radius:0;padding:5px 0;margin-top:9px;color:var(--sub);font-weight:600}.qfAuthorReplyToggle svg{width:12px;height:12px}
.replyToggle:active{background:#eeeeef}.dark .replyToggle:active{background:#2c2c2d}
.replyMore{font-weight:600;color:#7f8490}.dark .replyMore{color:#aaa}
.qfErrorState{padding-top:48px!important;padding-bottom:48px!important;color:var(--sub)!important}
.qfErrorIcon{width:34px;height:34px;margin:0 auto 10px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--soft);color:var(--accent);font-size:18px;font-weight:700}
.qfErrorTitle{font-size:14px;color:var(--text);font-weight:650;margin-bottom:5px}
.qfErrorSub{font-size:12px;color:var(--muted);line-height:1.55;margin:0 auto 14px;max-width:78vw}
.retryBtn{border:0;border-radius:16px;padding:7px 15px;background:var(--accent);color:#fff;font-size:12px;font-weight:650;cursor:pointer}
.loadMore.qfRetry{color:var(--accent);font-weight:650}

/* beta16：段评最终收尾——楼中楼层级更清晰，但保持轻量。 */
.replies{border-left:2px solid rgba(239,91,80,.18);box-shadow:inset 0 0 0 1px rgba(120,125,135,.035)}
.replyTo{color:var(--accent);font-weight:550}.replyMore{border-top:1px dashed var(--line)}
.dark .replies{border-left-color:rgba(239,91,80,.28);box-shadow:inset 0 0 0 1px rgba(255,255,255,.025)}
@media(max-width:420px){.row1{padding-left:20px;padding-right:17px}.tab{margin-right:20px;font-size:15px}.actions{gap:14px}.row2{padding-left:21px;padding-right:16px}.sort{padding:0 12px}.quoteWrap{padding-left:18px;padding-right:18px}.comment{padding-left:18px;padding-right:18px}.mainRow{padding-right:44px}.like{right:16px;top:72px}.god{right:16px}.avatarWrap{margin-right:12px}.replyToggle{margin-left:58px}.replies{margin-left:58px;margin-right:0}}

.audioPlayerBox{margin-top:12px;width:100%}
.audioDetailBtn{
  display:flex;align-items:center;justify-content:center;
  width:100%;min-height:48px;padding:0 16px;
  border-radius:24px;background:rgba(110,110,110,.10);
  color:#555;font-size:15px;font-weight:600;
  user-select:none;-webkit-user-select:none
}
.audioDetailBtn:active{opacity:.66}
.audioPlayGlyph{font-size:18px;margin-right:8px;line-height:1}
.audioInlineHost{width:100%;box-sizing:border-box}
.audioDetailFrame{display:block;width:100%;min-height:470px;border:0;background:#fff}
.dark .audioDetailBtn{background:rgba(255,255,255,.10);color:#ddd}
.dark .audioDetailFrame{background:#181818}

.audioPlayerHint{
  margin-top:6px;text-align:center;
  font-size:12px;color:#aaa;line-height:1.5
}
.dark .audioPlayerHint{color:#777}

.qfAudioPlayer{
  position:relative;display:flex;align-items:center;gap:12px;
  width:100%;box-sizing:border-box;margin-top:12px;
  padding:12px 14px;border-radius:28px;
  background:rgba(115,115,115,.10);overflow:visible
}
.qfAudioToggle{
  flex:0 0 42px;width:42px;height:42px;border:0;border-radius:50%;
  background:transparent;color:#666;font-size:22px;font-weight:700;
  display:flex;align-items:center;justify-content:center;padding:0
}
.qfAudioCenter{flex:1;min-width:0}
.qfAudioTimes{font-size:14px;color:#555;line-height:1.2;white-space:nowrap}
.qfAudioSep{color:#aaa}
.qfAudioProgress{
  position:relative;height:4px;border-radius:2px;margin-top:8px;
  background:rgba(120,120,120,.18);overflow:hidden
}
.qfAudioProgressFill{
  width:0;height:100%;border-radius:2px;background:#777
}
.qfAudioStatus{
  margin-top:6px;font-size:11px;color:#aaa;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis
}
.qfAudioOfficialHost{
  position:absolute;left:0;right:0;top:100%;z-index:10;
  margin-top:8px;border-radius:14px;overflow:hidden;
  border:1px solid rgba(0,0,0,.08);background:#fff
}
.qfAudioOfficialFrame{display:block;width:100%;height:430px;border:0;background:#fff}
.qfAudioBridge{border:0!important}
.dark .qfAudioPlayer{background:rgba(255,255,255,.10)}
.dark .qfAudioToggle,.dark .qfAudioTimes{color:#ddd}
.dark .qfAudioProgress{background:rgba(255,255,255,.18)}
.dark .qfAudioProgressFill{background:#bbb}
.dark .qfAudioStatus{color:#777}
.dark .qfAudioOfficialHost,.dark .qfAudioOfficialFrame{background:#181818}

/* v2.9.13: no automatic official iframe/blank panel for audio */
.qfAudioOfficialHost,.qfAudioOfficialFrame,.qfAudioBridge{display:none!important}
.qfAudioStatus.error{color:#d65b58!important;white-space:normal!important;line-height:1.45}

.qfBbDiag{
  margin:14px 14px 18px 14px;padding:14px 15px;
  border:1px solid rgba(220,150,70,.35);
  border-radius:14px;background:rgba(255,247,232,.96);
  color:#555;font-size:12px;line-height:1.65
}
.qfBbTitle{font-size:15px;font-weight:700;color:#c87524;margin-bottom:6px}
.qfBbWarn{color:#b65b48;margin-bottom:8px}
.qfBbLine{margin:4px 0;word-break:break-all}
.qfBbDetails{margin-top:10px}
.qfBbDetails summary{font-weight:650;color:#666}
.qfBbDetails pre{
  white-space:pre-wrap;word-break:break-all;
  max-height:430px;overflow:auto;margin:8px 0 0 0;
  padding:10px;border-radius:10px;
  background:rgba(255,255,255,.75);
  font-size:11px;line-height:1.55;color:#555
}
.qfBbFoot{margin-top:9px;color:#888}
.dark .qfBbDiag{background:rgba(54,45,34,.96);color:#ddd;border-color:rgba(220,150,70,.28)}
.dark .qfBbTitle{color:#e0a463}
.dark .qfBbWarn{color:#e59b89}
.dark .qfBbDetails summary{color:#ccc}
.dark .qfBbDetails pre{background:rgba(255,255,255,.05);color:#ccc}
.dark .qfBbFoot{color:#999}

.qfDirectDiag{
  border-color:rgba(65,155,100,.32);
  background:rgba(239,250,243,.97)
}
.qfDirectDiag .qfBbTitle{color:#3d9360}
.dark .qfDirectDiag{background:rgba(31,54,40,.96);border-color:rgba(88,180,120,.26)}
.dark .qfDirectDiag .qfBbTitle{color:#79c995}


/* v2.9.23: official-like audio layout */
.audioRoleBar{
  display:flex;align-items:center;gap:10px;overflow-x:auto;
  margin:10px 14px 8px 14px;padding:2px 0 6px 0;
  -webkit-overflow-scrolling:touch;scrollbar-width:none
}
.audioRoleBar::-webkit-scrollbar{display:none}
.audioRoleChip{
  flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;
  min-height:32px;padding:0 14px;border-radius:18px;border:0;
  background:rgba(130,130,130,.10);color:#666;font-size:14px;font-weight:600
}
.audioRoleChip.active{background:rgba(233,84,84,.12);color:#e45c5c}
.audioRoleChip .count{margin-left:4px;font-size:12px;opacity:.72}
.dark .audioRoleChip{background:rgba(255,255,255,.08);color:#ddd}
.dark .audioRoleChip.active{background:rgba(229,92,92,.18);color:#ff9d9d}

.qfAudioDiagFold{
  margin:4px 14px 14px 14px;border-radius:12px;
  background:rgba(115,115,115,.06);overflow:hidden
}
.qfAudioDiagFold summary{
  list-style:none;cursor:pointer;padding:11px 13px;color:#666;
  font-size:13px;font-weight:600
}
.qfAudioDiagFold summary::-webkit-details-marker{display:none}
.qfAudioDiagFold summary:after{content:'展开';float:right;color:#aaa;font-weight:500}
.qfAudioDiagFold[open] summary:after{content:'收起'}
.qfAudioDiagFold .qfBbDiag{margin:0;border:0;border-radius:0}
.dark .qfAudioDiagFold{background:rgba(255,255,255,.05)}
.dark .qfAudioDiagFold summary{color:#ccc}

.audioComment{padding:16px 14px 18px 14px;border-bottom:1px solid rgba(0,0,0,.05)}
.audioComment .mainRow{align-items:flex-start}
.audioComment .body{padding-right:0}
.audioComment .content{font-size:16px;line-height:1.7;color:#444;margin-top:6px}
.audioComment .meta{margin-top:10px;font-size:13px;color:#999}
.audioComment .like{padding-top:4px;min-width:36px}
.audioComment .avatarWrap{margin-top:0}
.audioRoleMini{
  display:inline-flex;align-items:center;margin-top:6px;
  padding:0 8px;height:22px;border-radius:11px;
  background:rgba(239,239,239,.95);color:#888;font-size:12px;font-weight:600
}
.audioRepliesPreview{margin-top:8px}
.audioRepliesPreview .reply{padding:10px 0 2px 0;border-bottom:0;background:transparent}
.audioRepliesPreview .reply:last-child{padding-bottom:0}
.audioRepliesPreview .rContent{color:#555;font-size:15px;line-height:1.7}
.audioRepliesPreview .rMeta{font-size:12px;color:#a1a1a1}
.audioRepliesPreview .rLike{min-width:28px}
.audioMoreReplies,.audioComment .replyMoreLocal{
  margin:8px 0 0 36px;color:#555;font-size:14px;font-weight:600
}
.dark .audioComment{border-bottom-color:rgba(255,255,255,.06)}
.dark .audioComment .content{color:#ddd}
.dark .audioRoleMini{background:rgba(255,255,255,.08);color:#bcbcbc}
.dark .audioRepliesPreview .rContent{color:#cfcfcf}
.dark .audioMoreReplies,.dark .audioComment .replyMoreLocal{color:#ddd}

.qfAudioPlayerOfficial{
  margin-top:12px;padding:10px 14px;border-radius:14px;
  background:rgba(244,244,244,.96);gap:10px;max-width:276px
}
.qfAudioPlayerOfficial .qfAudioToggle{
  flex:0 0 38px;width:38px;height:38px;border-radius:50%;
  background:#ef5b5b;color:#fff;font-size:18px
}
.qfAudioPlayerOfficial .qfAudioCurrent,
.qfAudioPlayerOfficial .qfAudioSep,
.qfAudioPlayerOfficial .qfAudioStatus{display:none}
.qfAudioPlayerOfficial .qfAudioTimes{display:flex;justify-content:flex-end;font-size:13px;color:#999}
.qfAudioPlayerOfficial .qfAudioDuration{font-weight:600}
.qfAudioPlayerOfficial .qfAudioProgress{
  height:18px;margin-top:3px;background:transparent;
  border-radius:0;position:relative;overflow:visible
}
.qfAudioPlayerOfficial .qfAudioProgressFill{
  position:absolute;left:0;top:50%;transform:translateY(-50%);
  height:4px;border-radius:3px;background:#f0b6b6;width:0
}
.qfAudioPlayerOfficial .qfAudioProgress:before{
  content:'';position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);
  height:4px;border-radius:3px;
  background:repeating-linear-gradient(90deg, rgba(205,205,205,.95) 0 4px, transparent 4px 8px)
}
.dark .qfAudioPlayerOfficial{background:rgba(255,255,255,.08)}
.dark .qfAudioPlayerOfficial .qfAudioTimes{color:#bdbdbd}
.dark .qfAudioPlayerOfficial .qfAudioProgress:before{background:repeating-linear-gradient(90deg, rgba(170,170,170,.55) 0 4px, transparent 4px 8px)}


/* v2.9.24: audio page compact scale */
.audioMode .row1{height:54px;padding-left:22px;padding-right:20px}
.audioMode .tab{font-size:14px;margin-right:22px}
.audioMode .tab .n{font-size:11px}
.audioMode .tab.active:after{width:24px;height:3px;bottom:5px}
.audioMode .iconBtn{width:28px;height:28px}
.audioMode .quoteIcon{width:23px;height:23px;font-size:13px;border-radius:6px}
.audioMode .themeGlyph{width:20px;height:20px}
.audioMode .actions{gap:16px}

.audioMode .audioRoleBar{gap:8px;margin:8px 13px 6px 13px;padding-bottom:5px}
.audioMode .audioRoleChip{min-height:28px;padding:0 12px;border-radius:15px;font-size:12.5px;font-weight:600}
.audioMode .audioRoleChip .count{font-size:10.5px;margin-left:3px}
.audioMode .qfAudioDiagFold{margin:3px 13px 10px 13px;border-radius:10px}
.audioMode .qfAudioDiagFold summary{padding:9px 11px;font-size:11.5px}

.audioMode .audioComment{padding:13px 15px 15px 16px;min-height:94px}
.audioMode .audioComment .mainRow{padding-right:42px}
.audioMode .audioComment .avatarWrap{width:40px;height:40px;flex-basis:40px;margin-right:11px}
.audioMode .audioComment .avatar{width:40px;height:40px;font-size:13px}
.audioMode .audioComment .nameRow{height:22px}
.audioMode .audioComment .name{font-size:14px;max-width:52vw}
.audioMode .audioComment .badgeImg{height:14px;max-width:58px}
.audioMode .audioComment .badgeText{height:15px;line-height:15px;font-size:9px;padding:0 3px}
.audioMode .audioRoleMini{height:19px;padding:0 7px;border-radius:10px;margin-top:4px;font-size:10.5px}
.audioMode .audioComment .content{font-size:14px;line-height:1.58;margin-top:5px}
.audioMode .audioComment .meta{font-size:11.5px;margin-top:8px}
.audioMode .audioComment .like{right:15px;top:58px;width:32px;font-size:11px}
.audioMode .audioComment .like svg{width:22px;height:22px;margin-bottom:2px}

.audioMode .qfAudioPlayerOfficial{max-width:238px;margin-top:9px;padding:8px 11px;border-radius:12px;gap:8px}
.audioMode .qfAudioPlayerOfficial .qfAudioToggle{flex-basis:34px;width:34px;height:34px;font-size:16px}
.audioMode .qfAudioPlayerOfficial .qfAudioTimes{font-size:11.5px}
.audioMode .qfAudioPlayerOfficial .qfAudioProgress{height:15px;margin-top:1px}
.audioMode .qfAudioPlayerOfficial .qfAudioProgress:before{height:3px;background:repeating-linear-gradient(90deg,rgba(195,195,195,.95) 0 3px,transparent 3px 7px)}
.audioMode .qfAudioPlayerOfficial .qfAudioProgressFill{height:3px}

.audioMode .audioRepliesPreview{margin-top:6px}
.audioMode .audioRepliesPreview .reply{padding-top:8px}
.audioMode .audioRepliesPreview .rAvatar{width:22px;height:22px;flex-basis:22px;margin-right:6px}
.audioMode .audioRepliesPreview .rName{font-size:11.5px}
.audioMode .audioRepliesPreview .rContent{font-size:12.5px;line-height:1.55;margin-left:28px;margin-top:4px}
.audioMode .audioRepliesPreview .rMeta{font-size:10px;margin-left:28px;margin-top:4px}
.audioMode .audioRepliesPreview .rLike{top:42px;font-size:9px}
.audioMode .audioRepliesPreview .rLike svg{width:14px;height:14px}
.audioMode .audioMoreReplies,.audioMode .audioComment .replyMoreLocal{font-size:12.5px;margin:7px 0 0 28px}

/* All tab keeps original layout; media is shown inside the original comment card. */
.allMediaMark{display:none}


/* v2.9.26: audio comments inside ALL keep original page chrome, but use compact media card */
.allAudioCard{padding:15px 16px 16px;min-height:100px}
.allAudioCard .mainRow{padding-right:42px}
.allAudioCard .avatarWrap{width:42px;height:42px;flex-basis:42px;margin-right:11px}
.allAudioCard .avatar{width:42px;height:42px;font-size:13px}
.allAudioCard .nameRow{height:23px}
.allAudioCard .name{font-size:14.5px;max-width:52vw}
.allAudioCard .badgeImg{height:14px;max-width:60px}
.allAudioCard .badgeText{height:15px;line-height:15px;font-size:9px;padding:0 3px}
.allAudioCard .audioRoleMini{height:19px;padding:0 7px;border-radius:10px;margin-top:4px;font-size:10.5px}
.allAudioCard .content{font-size:14.5px;line-height:1.6;margin-top:5px}
.allAudioCard .meta{font-size:11.5px;margin-top:8px}
.allAudioCard .like{right:15px;top:58px;width:32px;font-size:11px}
.allAudioCard .like svg{width:22px;height:22px;margin-bottom:2px}
.allAudioCard .qfAudioPlayerOfficial{max-width:240px;margin-top:9px;padding:8px 11px;border-radius:12px;gap:8px}
.allAudioCard .qfAudioPlayerOfficial .qfAudioToggle{flex-basis:34px;width:34px;height:34px;font-size:16px}
.allAudioCard .qfAudioPlayerOfficial .qfAudioTimes{font-size:11.5px}
.allAudioCard .qfAudioPlayerOfficial .qfAudioProgress{height:15px;margin-top:1px}
.allAudioCard .qfAudioPlayerOfficial .qfAudioProgress:before{height:3px;background:repeating-linear-gradient(90deg,rgba(195,195,195,.95) 0 3px,transparent 3px 7px)}
.allAudioCard .qfAudioPlayerOfficial .qfAudioProgressFill{height:3px}
.allAudioCard .audioRepliesPreview{margin-top:6px}
.allAudioCard .audioRepliesPreview .reply{padding-top:8px}
.allAudioCard .audioMoreReplies,.allAudioCard .replyMoreLocal{font-size:12.5px;margin:7px 0 0 28px}

/* beta11：评论弹窗视觉统一。仅覆盖布局/色彩，不改变数据与交互。 */
:root{--bg:#f6f7f9;--panel:#ffffff;--soft:#f4f5f7;--reply:#f4f5f7;--line:#eceef1;--accentSoft:#fff0ed}
body{background:var(--bg)}
.sticky{background:rgba(255,255,255,.94);border-bottom:1px solid rgba(0,0,0,.055);box-shadow:0 5px 18px rgba(28,31,38,.045);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px)}
.row1{height:56px;padding-left:20px;padding-right:18px}.tab{height:38px;margin-top:9px;margin-right:8px;padding:0 13px;border-radius:19px;font-size:14px;justify-content:center}.tab.active{color:var(--accent);background:var(--accentSoft)}.tab.active:after{display:none}.tab .n{margin-left:4px}.actions{gap:10px}.iconBtn{width:34px;height:34px;border-radius:17px;background:var(--soft)}
.row2{height:44px;padding:0 18px;border-top:0;background:rgba(255,255,255,.92)}.sortLabel{font-size:12px}.sorts{gap:6px}.sort{height:28px;line-height:28px;padding:0 12px;border-radius:14px;background:var(--soft);font-size:12px}.sort+.sort:before{display:none}.sort.active{background:var(--accentSoft);color:var(--accent)}
.quoteWrap{padding:10px 12px 2px;background:var(--bg)}.quoteCard{min-height:0;border:0;border-radius:14px;background:#fff;padding:12px 15px 12px 19px;box-shadow:0 3px 12px rgba(28,31,38,.045);font-size:13px}.quoteCard:before{width:4px;background:#92a0b6}
.list{background:var(--bg);padding:8px 10px 22px}.comment{margin:0 0 10px;padding:16px 15px 15px 16px;border:1px solid var(--line);border-radius:17px;background:var(--panel);box-shadow:0 3px 13px rgba(28,31,38,.035);min-height:0}.mainRow{padding-right:42px}.avatarWrap{width:42px;height:42px;flex-basis:42px;margin-right:12px}.avatar{width:42px;height:42px}.frame{left:-5px;top:-5px;width:52px;height:52px}.nameRow{height:23px}.name{font-size:14px}.content{font-size:15px;line-height:1.66;margin-top:5px}.meta{margin-top:7px}.like{right:14px;top:65px}.like svg{width:23px;height:23px}.god{right:13px;top:11px;width:35px;height:35px}.replyToggle{margin-left:54px;margin-top:9px}.replies{margin:9px 0 0 54px;border-radius:12px;background:var(--reply)}.reply{padding:11px 31px 11px 11px}.mediaImg{border-radius:12px}.loadMore{margin:0 10px 12px;border-radius:14px;background:var(--panel);border:1px solid var(--line)}
body.dark{--bg:#141516;--panel:#1d1f21;--soft:#25282b;--reply:#25282b;--line:#2c3034;--accentSoft:#352522}.dark .sticky{background:rgba(29,31,33,.94);border-bottom-color:#292d31;box-shadow:none}.dark .row2{background:rgba(29,31,33,.94)}.dark .quoteCard{background:#1d1f21;border:0}.dark .comment{box-shadow:none}.dark .tab.active,.dark .sort.active{background:#352522;color:#ff776b}.dark .iconBtn{background:#25282b}
@media(max-width:420px){.row1{padding-left:12px;padding-right:12px}.tab{margin-right:4px;padding:0 10px}.actions{gap:7px}.row2{padding-left:12px;padding-right:12px}.sort{padding:0 10px}.quoteWrap{padding-left:10px;padding-right:10px}.list{padding-left:8px;padding-right:8px}.comment{padding-left:14px;padding-right:13px}.like{right:12px}.god{right:11px}.replyToggle{margin-left:52px}.replies{margin-left:52px}}
/* beta12：细节精修——更轻的悬浮头部、信息层级与回复卡。 */
.sticky{border-radius:0 0 16px 16px;overflow:hidden}.row1{border-bottom:1px solid rgba(0,0,0,.025)}.sortLabel{font-weight:600;color:#9a9ea5;letter-spacing:.1px}.comment{transition:transform .14s ease,box-shadow .14s ease}.comment:active{transform:scale(.997)}.name{letter-spacing:.08px}.meta{color:#a1a5ab}.replyToggle{padding:5px 9px;border-radius:12px;background:var(--soft);font-size:12px}.replies{border:1px solid var(--line)}.reply{background:transparent}.mediaImg{box-shadow:0 2px 9px rgba(20,24,31,.06)}
.dark .row1{border-bottom-color:rgba(255,255,255,.025)}.dark .sortLabel{color:#858a90}.dark .mediaImg{box-shadow:none}

\n/* beta13：配图/配音媒体视图。媒体标签隐藏无效排序，配图改成大图卡片，空态不再显示接口术语。 */\n.imageMode .sticky,.audioMode .sticky{box-shadow:0 6px 20px rgba(28,30,34,.07)}\n.imageMode .row1,.audioMode .row1{height:56px}\n.imageMode .list{padding:12px 10px 26px}\n.imageCard{padding:0!important;overflow:hidden;border-radius:18px!important;background:var(--card);box-shadow:0 4px 18px rgba(20,24,31,.055)!important;margin-bottom:13px!important}\n.imageHead{display:flex;align-items:center;padding:13px 14px 11px}.imageHead .avatarWrap{width:36px;height:36px;flex-basis:36px;margin-right:9px}.imageHead .avatar{width:36px;height:36px}.imageWho{min-width:0;flex:1}.imageWho .name{font-size:13.5px}.imageWho .meta{margin-top:2px;font-size:10.5px}.imageLike{font-size:12px;color:var(--sub);white-space:nowrap;margin-left:8px}\n.imageStage{width:100%;height:min(58vh,420px);min-height:190px;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#f3f4f6}.imageHero{display:block;max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;margin:auto}.imageCaption{padding:12px 15px 15px;font-size:14px;line-height:1.65;color:var(--text)}\n.mediaEmpty{padding:58px 24px!important}.mediaEmptyIcon{font-size:34px;margin-bottom:10px}.mediaEmptyTitle{font-size:16px;font-weight:700;color:var(--text);margin-bottom:7px}.mediaEmptyTip{font-size:13px;line-height:1.7;color:var(--sub);max-width:430px;margin:0 auto}.mediaOfficialLink{display:inline-block;margin-top:13px;color:#4b86d1;text-decoration:none;font-weight:650;font-size:13px}\n.dark .imageCard{box-shadow:none!important}.dark .imageStage{background:#17191c}\n</style></head><body>
<div class="sticky" id="sticky"><div class="row1"><div class="tabs" id="tabs"><div class="tab active" data-tab="all">全部<span class="n" id="nAll">0</span></div><div class="tab" data-tab="image">配图<span class="n" id="nImg"></span></div><div class="tab" data-tab="audio">配音<span class="n" id="nAudio"></span></div></div><div class="actions" id="actions"><button class="iconBtn quote-on" id="quoteBtn" aria-label="原文"><span class="quoteIcon">文</span></button><button class="iconBtn" id="themeBtn" aria-label="主题"><span class="themeGlyph"></span></button></div></div><div class="row2" id="sortRow"><div class="sortLabel" id="sourceLabel">起点本地 · 推荐排序</div><div class="sorts"><button class="sort active" data-sort="default">推荐</button><button class="sort" data-sort="hot">热门</button><button class="sort" data-sort="latest">最新</button></div></div></div>
<div class="quoteWrap" id="quoteWrap"><div class="quoteCard" id="quoteCard">加载原文…</div></div><div class="list" id="list"><div class="loading"><div class="spinner"></div><div>加载中...</div></div></div><div class="loadMore hidden" id="loadMore">加载更多</div><div class="lightbox hidden" id="lightbox"><img id="lightboxImg"></div><button class="toTop hidden" id="toTop" aria-label="回到顶部">↑</button>
<script>(function(){
function qfParam(name){
    try{
        var m=String(location.href||"").match(
            new RegExp("[?&#]"+name+"=([^&#]+)","i")
        );
        if(!m)return "";
        try{return decodeURIComponent(String(m[1]||""));}catch(e0){return String(m[1]||"");}
    }catch(e1){return "";}
}
var qfCtx=window.__QF_COMMENT_CTX__||{};
var bid=String(
    qfParam("bookid")||
    qfParam("bookId")||
    qfCtx.bid||
    window.qdBid||
    ""
);
var cid=String(
    qfParam("chapterid")||
    qfParam("chapterId")||
    qfCtx.cid||
    window.qdCid||
    ""
);
var para=String(
    qfParam("paragraphid")||
    qfCtx.para||
    (window.qdPara==null?"":window.qdPara)
);
var segment=Number(
    qfParam("segmentid")||
    qfCtx.segment||
    window.qdSeg
);
var openType=String(
    qfParam("qfmode")||
    qfCtx.type||
    window.qdCmtType||
    "dp"
).toLowerCase();
var expectedCount=Number(
    qfParam("qfcount")||
    qfCtx.expected||
    window.qdExpectedCount||
    0
);
if(isNaN(expectedCount)||expectedCount<0)expectedCount=0;
var csrf=String(window.qdCsrf||"");
var qdCookie=String(window.qdCookie||"");
var authorSay=String(window.qdAuthorSay||"");
var authorName=String(window.qdAuthorName||"作者");
var authorAvatar=String(window.qdAuthorAvatar||"");
var authorReviewId=String(window.qdAuthorReviewId||"");
var authorParagraphId=String(window.qdAuthorParagraphId||"");
var authorReplyCount=Number(window.qdAuthorReplies||0);
if(isNaN(authorReplyCount)||authorReplyCount<0)authorReplyCount=0;
var authorReplyList=[];
try{authorReplyList=parse(window.qdAuthorReplyList||"[]")||[];if(!Array.isArray(authorReplyList))authorReplyList=[];}catch(_arl){authorReplyList=[];}
var qfContextId=String(
    qfParam("_qfctx")||
    qfCtx.ctxId||
    (bid+"-"+cid+"-"+para+"-"+segment)
);
/* v4.2.0-alpha6：段评 / 本章说 / 作者说 UI Context Canonical。
 * 这里只统一上下文元数据；所有请求/分页/媒体/渲染仍使用原变量。 */
function qfReviewUiContextV420(bid0,cid0,para0,segment0,openType0,authorReviewId0,authorParagraphId0){
    var p=String(para0==null?"":para0),ot=String(openType0||"dp").toLowerCase();
    var author=ot==="author"||p==="-10";
    var chapter=(p==="-1"&&ot==="zp");
    var paragraph=!author&&!chapter&&p!=="";
    var seg=Number(segment0);
    if(isNaN(seg))seg=paragraph?Number(p):0;
    if(isNaN(seg)||seg<0||author||chapter)seg=0;
    return {
        kind:author?"author":(chapter?"chapter":"paragraph"),
        bookId:String(bid0||""),
        chapterId:String(cid0||""),
        paragraphId:author?String(authorParagraphId0||p):p,
        segmentId:seg,
        reviewId:author?String(authorReviewId0||""):"",
        openType:ot,
        isAuthor:author,
        isChapter:chapter,
        hasParagraph:paragraph
    };
}
var qfUiContext=qfReviewUiContextV420(bid,cid,para,segment,openType,authorReviewId,authorParagraphId);
var isAuthor=qfUiContext.isAuthor;
var isChapter=qfUiContext.isChapter;
var hasParagraph=qfUiContext.hasParagraph;
segment=qfUiContext.segmentId;
try{window.__QF_REVIEW_UI_CONTEXT__=qfUiContext;}catch(_qfCtx420){}
var page=1,pageSize=10,currentTab='all',currentSort='default',loading=false,ended=false,totalAll=0,totalImg=-1,totalAudio=-1,actual=0,seen={},allCache={},loadedAllRaw=[],loadedAllSeen={},mediaEmptyKnown={image:false,audio:false},httpCache={},httpCacheTtl=45000,chapterAll=null,chapterLoading=false,quoteText=String(window.qdQuote||''),replyState={},chapterSeed=Array.isArray(window.qdSegments)?window.qdSegments:[],chapterState=null,mediaScanState=null,mediaScanToken=0,autoLoadBudget=2,autoLoadTimer=null,audioDirectRows=[],audioDirectPack=null,audioRoleFilter='all',allAudioReady=false,allAudioRows=[],allAudioById={},allAudioBySig={},allAudioPack=null,allAudioTotal=0,allAudioAddedLast=0;
/* v4.0 Stage 2②：专用媒体接口的“官方确认空”短缓存。
 * 仅缓存 empty，不缓存大评论对象；同一段落 3 分钟内重复打开不再重新签名/联网。
 * 命中真实媒体时主动清除，避免把旧空状态带到新结果。 */
function qfMediaEmptyKeyV403(kind){return 'qf_media_empty_v403|'+String(bid)+'|'+String(cid)+'|'+String(para)+'|'+String(kind||'')}
function qfMediaEmptyGetV403(kind){
    try{var k=qfMediaEmptyKeyV403(kind),v=String(localStorage.getItem(k)||'');if(!v)return false;var o=JSON.parse(v);if(o&&o.ts&&Date.now()-Number(o.ts)<180000)return true;localStorage.removeItem(k)}catch(_e){}return false;
}
function qfMediaEmptyPutV403(kind){try{localStorage.setItem(qfMediaEmptyKeyV403(kind),JSON.stringify({ts:Date.now()}))}catch(_e){}}
function qfMediaEmptyDropV403(kind){try{localStorage.removeItem(qfMediaEmptyKeyV403(kind))}catch(_e){}}

var listEl=document.getElementById('list'),moreEl=document.getElementById('loadMore'),quoteWrap=document.getElementById('quoteWrap'),quoteCard=document.getElementById('quoteCard');
var sourceLabel=document.getElementById('sourceLabel');if(sourceLabel)sourceLabel.textContent=qfUiContext.kind==='author'?'起点官方 · 作者说':(qfUiContext.kind==='chapter'?'起点本地 · 本章说':'起点本地 · 段评');
var EM={1:'👏',2:'🌹',3:'🤝',4:'😁',5:'😄',6:'🥺',7:'🙂',8:'😏',9:'😙',10:'👆🏻🐽',11:'🙄',12:'😭',13:'😵',14:'😥',15:'🖕🏻',16:'🥵',17:'😓',18:'🤫',19:'😂',20:'😢',21:'😍',22:'🤕🔨',23:'😑',24:'😫',25:'🤗',26:'🤪',27:'🙏',28:'😣',29:'💪',30:'💀',31:'😳',32:'😎',33:'🤭',34:'😄👏',35:'👍🏻',36:'🤓',37:'😡',38:'🙁',39:'😄❓',40:'😞',41:'😧',42:'💋',43:'☺️',44:'🤬',45:'😴',46:'🤠🚬',47:'😱',48:'🐷',49:'😪',50:'🤐',51:'🥴',52:'🌙',53:'❤️',54:'🔪',55:'🎁',56:'💔',57:'👊🏻',58:'😒',59:'✌🏻️',60:'😮',61:'🤨',62:'😴',63:'👏🏻',64:'🐲',65:'⭐',66:'🌧️',67:'🍉',68:'🍵',69:'🔥',70:'💯'};
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}function fmt(s){s=String(s==null?'':s).replace(/\[fn=(\d+)\]/g,function(m,n){return EM[n]||'💬'});return esc(s).replace(/\\\\n|\\n|\r\n|\r|\n/g,'<br>')}
function parse(raw){try{var t=String(raw||'{}').replace(/("(?:MidpageId|MidPageId|PageId|Id|CommentId|ReviewId|RootReviewId|QuoteReviewId|UserId|RelatedUserId|ParagraphId|CircleId|PostId)"\s*:\s*)(\d{16,})/g,'$1"$2"');return JSON.parse(t)}catch(e){return null}}
function http(url){
    var baseUrl=String(url||""),now=Date.now(),hit=httpCache[baseUrl];
    if(hit&&now-Number(hit.t||0)<httpCacheTtl)return String(hit.v||"");
    var sep=baseUrl.indexOf("?")>=0?"&":"?";
    url=baseUrl+sep+"_qfcb="+encodeURIComponent(String(qfContextId)+"-"+String(now)+"-"+String(Math.random()));
    var opt={method:"GET",timeout:10000,headers:{
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Referer":"https://www.qidian.com/chapter/"+encodeURIComponent(bid)+"/"+encodeURIComponent(cid)+"/",
        "Accept":"application/json,text/plain,*/*","Accept-Language":"zh-CN,zh;q=0.9","Cache-Control":"no-cache, no-store, max-age=0","Pragma":"no-cache"}};
    var out="";
    if(window.java&&typeof window.java.ajax==="function")out=String(window.java.ajax(url+","+JSON.stringify(opt))||"");
    else if(window.java&&typeof window.java.get==="function"){var r=window.java.get(url,opt.headers,10000);out=(r&&typeof r.body==="function")?String(r.body()||""):String(r||"");}
    else throw new Error("当前阅读 WebView 不支持评论请求");
    if(out)httpCache[baseUrl]={t:now,v:out};
    return out;
}
function qfMediaHttp(url,timeoutMs){
    var baseUrl=String(url||''),now=Date.now(),hit=httpCache[baseUrl];
    if(hit&&now-Number(hit.t||0)<httpCacheTtl)return String(hit.v||'');
    var sep=baseUrl.indexOf('?')>=0?'&':'?';
    var reqUrl=baseUrl+sep+'_qfmedia='+encodeURIComponent(String(qfContextId)+'-'+String(now));
    var opt={method:'GET',timeout:Math.max(1200,Number(timeoutMs||2200)||2200),headers:{
        'User-Agent':'Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36',
        'Referer':'https://www.qidian.com/chapter/'+encodeURIComponent(bid)+'/'+encodeURIComponent(cid)+'/',
        'Accept':'application/json,text/plain,*/*','Accept-Language':'zh-CN,zh;q=0.9','Cache-Control':'no-cache'
    }};
    var out='';
    if(window.java&&typeof window.java.ajax==='function')out=String(window.java.ajax(reqUrl+','+JSON.stringify(opt))||'');
    else if(window.java&&typeof window.java.get==='function'){
        var r=window.java.get(reqUrl,opt.headers,opt.timeout);
        out=(r&&typeof r.body==='function')?String(r.body()||''):String(r||'');
    }else throw new Error('当前阅读 WebView 不支持评论请求');
    if(out)httpCache[baseUrl]={t:now,v:out};
    return out;
}
function arr(v){if(!v)return[];if(Array.isArray(v))return v;var ks=['comments','Comments','list','List','DataList','dataList','reviewList','ReviewList','reviews','Reviews'];for(var i=0;i<ks.length;i++)if(Array.isArray(v[ks[i]]))return v[ks[i]];var best=[];for(var k in v)if(Object.prototype.hasOwnProperty.call(v,k)&&v[k]&&typeof v[k]==='object'){var a=arr(v[k]);if(a.length>best.length)best=a}return best}
function textOf(v){if(v==null)return'';if(typeof v==='string'||typeof v==='number')return String(v);if(Array.isArray(v)){for(var i=0;i<v.length;i++){var x=textOf(v[i]);if(x)return x}return''}if(typeof v==='object'){var ks=['Text','text','Content','content','ReviewContent','Body','PostBody','PostContent','Subject','Title'];for(var j=0;j<ks.length;j++)if(v[ks[j]]!=null){var y=textOf(v[ks[j]]);if(y)return y}}return''}
function mediaFind(root,kind){
    var best='',score=-999,seen=[];
    var want=kind==='image'
        ?/(image|img|pic|photo|picture|preimage|thumbnail|thumb|gif)/i
        :/(audio|voice|sound|record|dub|dubbing|speech|listen|voiceinfo|audioinfo)/i;
    var bad=kind==='image'
        ?/(avatar|head|frame|badge|icon|title|god|essence|stamp|medal|honou?r|level|rank|tag|skin|pendant|decorate|decoration|background|\bbg\b|activity|audiopage|detailpage|reviewpage)/i
        :/(avatar|head|frame|badge|icon|image|img|pic|photo|audiopage|detailpage|reviewpage)/i;
    var ext=kind==='image'
        ?/\.(?:jpe?g|png|webp|gif|bmp|avif)(?:[?#]|$)/i
        :/\.(?:mp3|m4a|aac|wav|ogg|amr|opus|flac|m3u8)(?:[?#]|$)/i;

    function normUrl(s){
        s=String(s||'').trim();
        if(/^\/\//.test(s))s='https:'+s;
        return s;
    }

    function isInternalPath(path){
        return /(?:^|\.|\[)_qf/i.test(String(path||''));
    }

    function isDetailPage(s){
        return /h5\.if\.qidian\.com\/new\/chapterreview/i.test(String(s||''));
    }

    function strongAudioPath(p){
        return /(audio(?:url|src|path|file)|voice(?:url|src|path|file)|play(?:url|src)|sound(?:url|src)|record(?:url|src)|media(?:url|src))/i.test(p);
    }

    function take(s,path,d){
        s=normUrl(s);
        var p=String(path||'');

        if(isInternalPath(p))return;
        if(!/^(?:https?:|data:audio|data:image)/i.test(s))return;

        if(kind==='audio'){
            if(/^data:image/i.test(s))return;
            if(isDetailPage(s))return;

            if(!ext.test(s)&&!/^data:audio/i.test(s)&&!strongAudioPath(p))return;
        }

        if(kind==='image'&&/^data:audio/i.test(s))return;

        var n=(want.test(p)?10:0)+(ext.test(s)?7:0)-
            (bad.test(p)?14:0)-d*.05;

        if(n>score){score=n;best=s;}
    }

    function walk(v,path,d){
        if(v==null||d>9)return;
        if(isInternalPath(path))return;

        if(typeof v==='string'){
            var sv=String(v).trim();

            if(
                sv.length>1&&
                ((sv.charAt(0)==='{'&&sv.charAt(sv.length-1)==='}')||
                 (sv.charAt(0)==='['&&sv.charAt(sv.length-1)===']'))
            ){
                try{walk(JSON.parse(sv),path,d+1);}catch(_e){}
            }

            take(sv,path,d);
            return;
        }

        if(typeof v==='number'||typeof v==='boolean')return;

        if(Array.isArray(v)){
            for(var i=0;i<v.length;i++)walk(v[i],path+'['+i+']',d+1);
            return;
        }

        if(typeof v==='object'){
            if(seen.indexOf(v)>=0)return;
            seen.push(v);

            for(var k in v){
                if(!Object.prototype.hasOwnProperty.call(v,k))continue;
                if(/^_qf/i.test(String(k)))continue;
                walk(v[k],path?path+'.'+k:k,d+1);
            }
        }
    }

    walk(root,'',0);
    return score>=5?best:'';
}
function imgOf(v){return mediaFind(v,'image')}
/* alpha18.4：普通评论页不能再用“递归找任意图片 URL”作为正文配图。
 * Reader 富身份加入后，TitleImage / 神评论印章 / 用户装饰等图片字段大量进入 raw，
 * 这些都是 UI 元数据，不是用户发布的配图。只有明确的内容媒体语义才允许展示。 */
function qfCommentImageV504(root){
    root=root||{};
    function norm(v){var s=String(v==null?'':v).trim();if(/^\/\//.test(s))s='https:'+s;return /^(?:https?:|data:image)/i.test(s)?s:'';}
    function direct(o){
        if(!o||typeof o!=='object')return '';
        var ks=['ImageDetail','imageDetail','ContentImage','contentImage','ContentImageUrl','contentImageUrl','ReviewImage','reviewImage','ReviewImageUrl','reviewImageUrl','PictureUrl','pictureUrl','PicUrl','picUrl','ContentPic','contentPic'];
        for(var i=0;i<ks.length;i++){var u=norm(o[ks[i]]);if(u)return u;}
        return '';
    }
    var d=direct(root);if(d)return d;
    /* 专用配图接口已经由 qfDirectImageRowsV402 标记，允许使用其验证后的 generic 结果。 */
    if(root._qfImageVerified===true){try{return String(imgOf(root)||'');}catch(_v){return '';}}
    var containers=['ImageList','imageList','Images','images','PictureList','pictureList','Pictures','pictures','PicList','picList','ReviewMedia','reviewMedia','ContentMedia','contentMedia','Attachments','attachments'];
    function scan(v,path,depth){
        if(v==null||depth>5)return '';
        if(typeof v==='string'){
            if(!/(content|review|comment|body|media|attach|imagelist|picturelist|piclist)/i.test(String(path||'')))return '';
            return norm(v);
        }
        if(Array.isArray(v)){for(var i=0;i<v.length;i++){var a=scan(v[i],path+'['+i+']',depth+1);if(a)return a;}return '';}
        if(typeof v!=='object')return '';
        var x=direct(v);if(x)return x;
        for(var k in v){
            if(!Object.prototype.hasOwnProperty.call(v,k))continue;
            var kp=path?path+'.'+k:k;
            if(/(avatar|head|frame|badge|icon|title|god|essence|stamp|medal|honou?r|level|rank|tag|skin|pendant|decor|background|activity)/i.test(kp))continue;
            if(/(content|review|comment|body|media|attach|image|picture|pic)/i.test(kp)){
                var z=scan(v[k],kp,depth+1);if(z)return z;
            }
        }
        return '';
    }
    for(var ci=0;ci<containers.length;ci++){
        if(root[containers[ci]]!==undefined){var r=scan(root[containers[ci]],containers[ci],0);if(r)return r;}
    }
    return '';
}
function audioOf(v){return mediaFind(v,'audio')}
function saneAudioDuration(v){
    var n=Number(v||0);
    if(!isFinite(n)||n<1.5||n>36000)return 0;
    return n;
}

function audioDurationOf(root){
    var best=0,seen=[];

    function take(v,key,path){
        var n=Number(v);
        if(!isFinite(n)||n<=0)return;

        var k=String(key||'');
        var p=String(path||'');

        if(/(?:^|\.|\[)_qf/i.test(p)||/^_qf/i.test(k))return;

        var audioCtx=/(audio|voice|sound|record|dub|dubbing|speech|listen)/i.test(p);
        var explicit=/(audioDuration|voiceDuration|soundDuration|recordDuration|playDuration|durationMs|audioLength|voiceLength)/i.test(k);
        var generic=/^(duration|length|seconds|second|ms|milliseconds?)$/i.test(k);

        if(!explicit&&!(audioCtx&&generic))return;

        if(/ms|millisecond/i.test(k)||n>1000)n=n/1000;

        n=saneAudioDuration(n);
        if(n>best)best=n;
    }

    function walk(v,path,d){
        if(v==null||d>8)return;
        if(/(?:^|\.|\[)_qf/i.test(String(path||'')))return;

        if(typeof v==='string'){
            var sv=String(v).trim();
            if(
                sv.length>1&&
                ((sv.charAt(0)==='{'&&sv.charAt(sv.length-1)==='}')||
                 (sv.charAt(0)==='['&&sv.charAt(sv.length-1)===']'))
            ){
                try{walk(JSON.parse(sv),path,d+1);}catch(_e){}
            }
            return;
        }

        if(typeof v==='number'||typeof v==='boolean')return;

        if(Array.isArray(v)){
            for(var i=0;i<v.length;i++)walk(v[i],path+'['+i+']',d+1);
            return;
        }

        if(typeof v==='object'){
            if(seen.indexOf(v)>=0)return;
            seen.push(v);

            for(var k in v){
                if(!Object.prototype.hasOwnProperty.call(v,k))continue;
                if(/^_qf/i.test(String(k)))continue;

                var x=v[k];

                if(
                    typeof x==='number'||
                    (typeof x==='string'&&/^\d+(?:\.\d+)?$/.test(x))
                ){
                    take(x,k,path);
                }

                walk(x,path?path+'.'+k:k,d+1);
            }
        }
    }

    walk(root,'',0);
    return saneAudioDuration(best);
}
function rawAudioDiag(root){
    var out=[],seenObj=[],seenText={};

    function clean(v){
        var s=String(v==null?'':v).trim();
        if(!s)return '';

        if(/^\/\//.test(s))s='https:'+s;

        if(/^https?:\/\//i.test(s)){
            try{
                var a=document.createElement('a');
                a.href=s;
                s=String(a.hostname||'')+String(a.pathname||'');
            }catch(e){
                s=s.replace(/[?#].*$/,'');
            }
        }

        s=s.replace(/\s+/g,' ');
        if(s.length>72)s=s.slice(0,69)+'…';
        return s;
    }

    function add(path,val){
        path=String(path||'');
        if(!path||/(?:^|\.|\[)_qf/i.test(path))return;

        var cv=clean(val);
        if(!cv)return;

        var text=path+'='+cv;
        if(seenText[text])return;

        seenText[text]=1;
        out.push(text);
    }

    function walk(v,path,d,audioParent){
        if(v==null||d>7||out.length>=10)return;
        if(/(?:^|\.|\[)_qf/i.test(String(path||'')))return;

        if(typeof v==='string'){
            var sv=String(v).trim();

            if(
                sv.length>1&&
                ((sv.charAt(0)==='{'&&sv.charAt(sv.length-1)==='}')||
                 (sv.charAt(0)==='['&&sv.charAt(sv.length-1)===']'))
            ){
                try{walk(JSON.parse(sv),path,d+1,audioParent);}catch(_e){}
            }

            if(audioParent||/(audio|voice|sound|record|dub|speech|listen|play)/i.test(path)){
                add(path,sv);
            }
            return;
        }

        if(typeof v==='number'||typeof v==='boolean'){
            if(audioParent||/(audio|voice|sound|record|dub|speech|listen|duration|play)/i.test(path)){
                add(path,v);
            }
            return;
        }

        if(Array.isArray(v)){
            for(var i=0;i<v.length&&out.length<10;i++){
                walk(v[i],path+'['+i+']',d+1,audioParent);
            }
            return;
        }

        if(typeof v==='object'){
            if(seenObj.indexOf(v)>=0)return;
            seenObj.push(v);

            var hereAudio=audioParent||/(audio|voice|sound|record|dub|speech|listen)/i.test(path);

            for(var k in v){
                if(!Object.prototype.hasOwnProperty.call(v,k))continue;
                if(/^_qf/i.test(String(k)))continue;

                var kp=path?path+'.'+k:k;
                var childAudio=hereAudio||/(audio|voice|sound|record|dub|speech|listen)/i.test(k);

                if(
                    childAudio||
                    (hereAudio&&/(id|url|src|path|file|type|duration|length|time|play)/i.test(k))
                ){
                    var x=v[k];
                    if(typeof x==='string'||typeof x==='number'||typeof x==='boolean'){
                        add(kp,x);
                    }
                }

                walk(v[k],kp,d+1,childAudio);
            }
        }
    }

    walk(root,'',0,false);

    if(!out.length){
        try{
            var n=0;
            for(var k in root){
                if(!Object.prototype.hasOwnProperty.call(root,k))continue;
                if(/^_qf/i.test(String(k)))continue;

                var v=root[k];
                if(typeof v==='string'||typeof v==='number'||typeof v==='boolean'){
                    if(/content|name|avatar|head|time|date|like|agree/i.test(k))continue;
                    add(k,v);
                    if(++n>=6)break;
                }
            }
        }catch(_e){}
    }

    return out.join(' | ');
}

function audioPathOf(root,target){
    target=String(target||'');
    if(!target)return '';

    var found='',seen=[];

    function norm(s){
        s=String(s||'').trim();
        if(/^\/\//.test(s))s='https:'+s;
        return s;
    }

    function walk(v,path,d){
        if(found||v==null||d>9)return;
        if(/(?:^|\.|\[)_qf/i.test(String(path||'')))return;

        if(typeof v==='string'){
            var sv=String(v).trim();

            if(
                sv.length>1&&
                ((sv.charAt(0)==='{'&&sv.charAt(sv.length-1)==='}')||
                 (sv.charAt(0)==='['&&sv.charAt(sv.length-1)===']'))
            ){
                try{walk(JSON.parse(sv),path,d+1);}catch(_e){}
            }

            if(norm(sv)===norm(target))found=path;
            return;
        }

        if(typeof v!=='object')return;

        if(seen.indexOf(v)>=0)return;
        seen.push(v);

        if(Array.isArray(v)){
            for(var i=0;i<v.length;i++)walk(v[i],path+'['+i+']',d+1);
            return;
        }

        for(var k in v){
            if(!Object.prototype.hasOwnProperty.call(v,k))continue;
            if(/^_qf/i.test(String(k)))continue;
            walk(v[k],path?path+'.'+k:k,d+1);
        }
    }

    walk(root,'',0);
    return found;
}
function safeAudioUrlInfo(u){
    u=String(u||'');
    if(!u)return '';

    try{
        var a=document.createElement('a');
        a.href=u;
        return String(a.hostname||'')+String(a.pathname||'');
    }catch(e){
        return u.replace(/[?#].*$/,'').slice(0,120);
    }
}

function tsOf(x){x=x||{};var r=x.raw||x;var v=x.create_timestamp||r.CreateTime||r.createTime||r.CreateTimestamp||r.createTimestamp||r.PostTime||r.UpdateTime||0,t=0;if(typeof v==='string'&&!/^\d+$/.test(v)){var d0=new Date(v.replace(/-/g,'/'));if(!isNaN(d0.getTime()))t=d0.getTime()}else t=Number(v)||0;if(t&&String(Math.floor(t)).length<=10)t*=1000;if(!t&&r.PostDate){var d=new Date(String(r.PostDate).replace(/-/g,'/'));if(!isNaN(d.getTime()))t=d.getTime()}return t||0}
function timeText(t){if(!t)return'';var d=new Date(t),diff=Date.now()-t;if(diff>=0&&diff<60000)return'刚刚';if(diff>=0&&diff<3600000)return Math.max(1,Math.floor(diff/60000))+'分钟前';if(diff>=0&&diff<86400000)return Math.floor(diff/3600000)+'小时前';if(diff>=0&&diff<604800000)return Math.floor(diff/86400000)+'天前';return d.getFullYear()+'年'+(d.getMonth()+1)+'月'+d.getDate()+'日'}
/* v4.2.0-alpha1：起点评论身份 canonical model。
 * 只消费 TitleInfoList，不扫描用户名、正文、任意字符串字段猜标签。 */
var QF_ReviewIdentity=(function(){
    function tx(v){return String(v==null?'':v).replace(/^\s+|\s+$/g,'');}
    function norm(v){return tx(v).replace(/[\s\u200b\u200c\u200d\ufeff]+/g,'').toLowerCase();}
    function obj(v){
        if(v&&typeof v==='object')return v;
        if(typeof v==='string'){
            var z=tx(v);
            if(z.charAt(0)==='{'||z.charAt(0)==='['){try{return JSON.parse(z)}catch(_e){}}
        }
        return null;
    }
    function color(v){
        v=tx(v);
        return /^(#[0-9a-fA-F]{3,8}|rgba?\([^)]{1,64}\)|hsla?\([^)]{1,64}\))$/.test(v)?v:'';
    }
    function listOf(o){
        o=obj(o);if(!o||typeof o!=='object')return [];
        var a=o.TitleInfoList!==undefined?o.TitleInfoList:(o.titleInfoList!==undefined?o.titleInfoList:o.title_info_list);
        a=obj(a)||a;return Array.isArray(a)?a:[];
    }
    function userSet(item,raw){
        item=item||{};raw=raw||item;
        var u=item.user_info||raw.user_info||item.UserInfo||item.userInfo||raw.UserInfo||raw.userInfo||raw.User||raw.user||{},set={};
        function add(v){var k=norm(v);if(k)set[k]=1;}
        try{add(qfReviewUserNameV503(item));}catch(_e){}
        add(item.name);add(item.user_name);add(item.UserName);add(item.NickName);add(item.nickName);add(item.nickname);
        add(raw.UserName);add(raw.userName);add(raw.NickName);add(raw.nickName);add(raw.nickname);
        add(u.user_name);add(u.UserName);add(u.NickName);add(u.nickName);add(u.nickname);
        return set;
    }
    function field(t,keys){
        for(var i=0;i<keys.length;i++){
            var k=keys[i];
            if(t[k]!==undefined&&t[k]!==null&&tx(t[k])!=='')return t[k];
        }
        return '';
    }
    function roleOf(name,tp){
        var c=tx(name).replace(/[\s·•・\-_|｜]/g,'');
        if(/^(见习|学徒|执事|舵主|堂主|护法|长老|掌门|盟主)$/.test(c))return 'rank';
        if(/^(?:lv?|等级)\d{1,2}(?:天枢|天璇|天玑|天权|玉衡|开阳|摇光)?$/i.test(c))return 'level';
        if(/^(纪律助理|版主|管理员|运营|运营官|社区助理|作者助理)$/.test(c))return 'official';
        if(/^(乐子人|与光同尘)$/.test(c))return 'activity';
        return tp>0?'title':'title';
    }
    function canonical(t,names){
        if(!t||typeof t!=='object')return null;
        var nm=tx(field(t,['TitleName','titleName','title_name']));
        var im=tx(field(t,['TitleImage','titleImage','title_image','TitleImageOfNight','titleImageOfNight','TitleImageOfDark','titleImageOfDark']));
        if(/^\/\//.test(im))im='https:'+im;
        if(!nm&&!/^https?:\/\//i.test(im))return null;

        /* 核心误识别保护：标签文字等于该评论真实用户名时绝不渲染。 */
        if(nm&&names&&names[norm(nm)])return null;

        var tp=Number(field(t,['TitleType','titleType','title_type']))||0;
        var show=Number(field(t,['TitleShowType','titleShowType','title_show_type']))||0;
        var sub=Number(field(t,['TitleSubType','TitleSubtype','titleSubType','titleSubtype','title_sub_type']))||0;
        var id=tx(field(t,['TitleId','titleId','title_id','Id','id']));
        var fg=color(field(t,['TitleTextColor','titleTextColor','title_text_color','TitleColor','titleColor','title_color','TextColor','textColor','text_color']));
        var darkFg=color(field(t,['TitleDarkTextColor','titleDarkTextColor','title_dark_text_color','TitleTextColorOfNight','titleTextColorOfNight']));
        var bg=color(field(t,['BackgroundColor','backgroundColor','background_color','BgColor','bgColor','bg_color']));
        var bd=color(field(t,['BorderColor','borderColor','border_color']));
        return {type:nm?'text':'img',val:nm||im,tp:tp,show:show,sub:sub,id:id,role:nm?roleOf(nm,tp):'image',fg:fg,darkFg:darkFg,bg:bg,bd:bd,raw:t};
    }
    function collect(item,raw,extra){
        item=item||{};raw=raw||item;
        var names=userSet(item,raw),user=item.user_info||raw.user_info||item.UserInfo||item.userInfo||raw.UserInfo||raw.userInfo||raw.User||raw.user||{};
        var out=[],seen={};
        function addList(a){
            a=Array.isArray(a)?a:[];
            for(var i=0;i<a.length&&out.length<5;i++){
                var c=canonical(a[i],names);if(!c)continue;
                var k=c.type==='text'?('t:'+norm(c.val)):('i:'+c.val);
                if(seen[k])continue;seen[k]=1;out.push(c);
            }
        }
        addList(listOf(raw));if(item!==raw)addList(listOf(item));addList(listOf(user));addList(extra);
        return out.slice(0,5);
    }
    function rawTitleList(v){
        if(!v||typeof v!=='object')return [];
        var raw=v.raw||v,user=v.user_info||raw.user_info||v.UserInfo||v.userInfo||raw.UserInfo||raw.userInfo||raw.User||raw.user||{};
        var names=userSet(v,raw),out=[],seen={};
        function addList(a){
            a=Array.isArray(a)?a:[];
            for(var i=0;i<a.length;i++){
                var t=a[i],c=canonical(t,names);if(!c)continue;
                var k=c.type==='text'?('t:'+norm(c.val)):('i:'+c.val);
                if(seen[k])continue;seen[k]=1;out.push(t);
            }
        }
        addList(listOf(raw));if(v!==raw)addList(listOf(v));addList(listOf(user));
        return out;
    }
    return {collect:collect,rawTitleList:rawTitleList,canonical:canonical,roleOf:roleOf,norm:norm};
})();

var QF_TITLE_IDENTITY_V504={uid:{},name:{},nameSig:{}};
function qfTitleListIdentityV504(v){return QF_ReviewIdentity.rawTitleList(v);}
function qfTitleIdentitySigV504(a){
    a=Array.isArray(a)?a:[];var s=[];
    for(var i=0;i<a.length;i++){
        var t=a[i]||{};
        s.push(String(t.TitleName||t.titleName||t.title_name||'')+'|'+String(t.TitleImage||t.titleImage||t.title_image||'')+'|'+String(t.TitleType||t.titleType||t.title_type||'')+'|'+String(t.TitleShowType||t.titleShowType||t.title_show_type||'')+'|'+String(t.TitleSubType||t.TitleSubtype||t.titleSubType||t.titleSubtype||t.title_sub_type||''));
    }
    return s.join(';;');
}
function qfTitleIdentityPutV504(v){
    var a=qfTitleListIdentityV504(v);if(!a.length)return;
    var uid=qfReviewUserIdV503(v),nm=qfReviewUserNameV503(v),sig=qfTitleIdentitySigV504(a);
    if(uid)QF_TITLE_IDENTITY_V504.uid[uid]=a;
    if(nm){
        var old=QF_TITLE_IDENTITY_V504.nameSig[nm];
        if(old===undefined){QF_TITLE_IDENTITY_V504.nameSig[nm]=sig;QF_TITLE_IDENTITY_V504.name[nm]=a;}
        else if(old!==sig){QF_TITLE_IDENTITY_V504.nameSig[nm]='!';delete QF_TITLE_IDENTITY_V504.name[nm];}
    }
}
function qfTitleIdentityGetV504(item,raw){
    var probe=item||raw||{},uid=qfReviewUserIdV503(probe),nm=qfReviewUserNameV503(probe);
    if(uid&&QF_TITLE_IDENTITY_V504.uid[uid])return QF_TITLE_IDENTITY_V504.uid[uid];
    if(nm&&QF_TITLE_IDENTITY_V504.nameSig[nm]!=='!'&&QF_TITLE_IDENTITY_V504.name[nm])return QF_TITLE_IDENTITY_V504.name[nm];
    return [];
}
function titlesOf(item,raw){
    item=item||{};raw=raw||item;
    return QF_ReviewIdentity.collect(item,raw,qfTitleIdentityGetV504(item,raw));
}
/* v4.2.0-alpha3：根评论 / 楼中楼共享的 UI Identity Adapter。
 * 只统一 id/name/avatar/TitleInfoList，不动正文、回复数、媒体或精华语义。 */
function qfReviewUiIdentity(item,raw){
    item=item||{};raw=raw||item;
    var user=item.user_info||raw.UserInfo||raw.userInfo||raw.User||raw.user||{};
    return {
        id:String(
            item.comment_id||
            raw.ReviewId||raw.reviewId||
            raw.CommentId||raw.commentId||
            raw.Id||raw.id||
            raw.PostId||raw.PostID||raw.postId||
            raw.RootReviewId||raw.rootReviewId||
            ""
        ),
        name:String(
            user.user_name||user.UserName||
            user.NickName||user.nickName||user.nickname||
            raw.UserName||raw.userName||
            raw.NickName||raw.nickName||
            "匿名"
        ),
        avatar:String(
            user.user_avatar||user.UserHeadIcon||
            user.Avatar||user.avatar||
            raw.UserHeadIcon||raw.userHeadIcon||
            raw.Avatar||raw.avatar||
            ""
        ),
        titles:titlesOf(item,raw)
    };
}

/* v4.2.0-alpha4：Review UI Row Canonical。
 * 只统一根评论/楼中楼完全同义的基础字段：
 * id/name/avatar/titles/time/ip/like/floor。
 * replyCount/content/media/god/replyTo 仍保留各自原语义。 */
function qfReviewUiRowBase(item,raw){
    item=item||{};raw=raw||item;
    var ui=qfReviewUiIdentity(item,raw);
    return {
        id:ui.id,
        name:ui.name,
        avatar:ui.avatar,
        titles:ui.titles,
        time:tsOf(item),
        ip:String(
            raw.IpLocation||raw.ipLocation||
            raw.IPLocation||raw.IPAddress||
            raw.ipAddress||raw.Address||
            ""
        ),
        like:Number(
            item.digg_count||
            raw.AgreeAmount||raw.agreeAmount||
            raw.LikeCount||raw.likeCount||
            raw.DiggCount||raw.StarCount||
            raw.PraiseCount||0
        )||0,
        floor:raw.level||raw.Level||raw.Floor||raw.floor||raw.FloorNo||0
    };
}

/* v4.2.0-alpha5：Review UI Payload Canonical。
 * 只统一根评论/楼中楼目前完全相同的 payload 字段：
 * content + image + audio family。
 * frame/replies/replyTo/god 保持各自 adapter 原语义。 */
function qfReviewUiPayloadBase(item,raw){
    item=item||{};raw=raw||item;
    return {
        content:String(
            textOf(
                item.text||item.content||
                raw.Content||raw.content||
                raw.ReviewContent||raw.reviewContent||
                raw.Body||raw.PostBody||raw.PostContent||
                raw.Subject||raw.Title
            )||""
        ),
        image:qfCommentImageV504(raw),
        audio:String(raw._qfAudioUrl||audioOf(raw)||""),
        audioPage:String(raw._qfAudioPage||""),
        audioDetected:!!raw._qfAudioDetected,
        audioDuration:saneAudioDuration(raw._qfAudioDuration)||audioDurationOf(raw)||0,
        audioPath:String(raw._qfAudioPath||audioPathOf(raw,raw._qfAudioUrl||audioOf(raw))||""),
        audioDiag:String(raw._qfAudioDiag||rawAudioDiag(raw)||"")
    };
}

function adaptReply(item){
    item=item||{};
    var raw=item.raw||item;
    var row=qfReviewUiRowBase(item,raw),payload=qfReviewUiPayloadBase(item,raw);

    return {
        id:row.id,
        name:row.name,
        avatar:row.avatar,
        frame:String(raw.FrameUrl||raw.frameUrl||""),
        content:payload.content,
        time:row.time,
        ip:row.ip,
        like:row.like,
        replies:0,
        titles:row.titles,
        floor:row.floor,
        image:payload.image,
        audio:payload.audio,
        audioPage:payload.audioPage,
        audioDetected:payload.audioDetected,
        audioDuration:payload.audioDuration,
        audioPath:payload.audioPath,
        audioDiag:payload.audioDiag,
        replyTo:String(
            raw.RelatedUser||raw.relatedUser||
            raw.ReplyUserName||raw.replyUserName||
            raw.RelatedUserName||raw.relatedUserName||
            ""
        ),
        god:false,
        raw:raw,
        embedded:[]
    };
}

function adapt(item){
    item=item||{};
    var raw=item.raw||item;
    var row=qfReviewUiRowBase(item,raw),payload=qfReviewUiPayloadBase(item,raw);
    var t=row.time;

    var srcReplies=
        raw.replyList||
        raw.ReplyList||
        raw.replies||
        raw.Replies||
        [];

    if(!Array.isArray(srcReplies))srcReplies=[];

    var embedded=[];
    var rootReviewId=String(
        item.comment_id||
        raw.ReviewId||raw.reviewId||
        raw.CommentId||raw.commentId||
        raw.Id||raw.id||
        raw.PostId||raw.PostID||
        raw.RootReviewId||raw.rootReviewId||""
    );
    for(var ri=0;ri<srcReplies.length;ri++){
        var rr0=srcReplies[ri];
        if(!rr0||typeof rr0!=="object")continue;
        /* replyList 理论上属于当前根评论，但部分接口会混入上下文数据。
         * 如果响应明确给了父ID，则必须等于当前 root reviewId；没有父ID时保留兼容。
         */
        try{
            var rp0=qfReplyParentId2928(rr0);
            if(rp0&&rootReviewId&&String(rp0)!==rootReviewId)continue;
        }catch(_rp0){}
        embedded.push(adaptReply(rr0));
    }

    /* v2.9.30：这里只认“当前根评论的回复数”。
     * ReviewCount / CommentCount / PostCount 在部分起点响应里是段落/列表统计，
     * 不能当楼中楼数量，否则会导致每一层都错误显示“更多回复”。
     */
    var replyTotal=Number(
        item.reply_count||
        raw.rootReviewReplyCount||
        raw.RootReviewReplyCount||
        raw.ReplyAmount||
        raw.replyAmount||
        raw.ReplyCount||
        raw.replyCount||
        raw.RepliesCount||
        raw.repliesCount||
        embedded.length||
        0
    )||0;
    /* alpha18.1：getchapterendreview 的“单条评论实体”使用 CommentCount 表示楼中楼数量。
       只有 qfMergeChapterEndRows2933 明确标记过的真实章末评论行才启用，避免把普通
       reviewList 的段落/列表 CommentCount 错当成每层回复数。 */
    if(replyTotal<=0&&raw._qfChapterEndReview===1){
        replyTotal=Number(raw.ReviewCount||raw.reviewCount||raw.CommentCount||raw.commentCount||0)||0;
    }
    /* alpha18.2：Web/mobile 根评论骨架已经由 fetchPack 明确标记，只有这种根评论
       才允许把 ReviewCount 解释为该楼层回复数；避免对子对象/列表统计误判。 */
    if(replyTotal<=0&&(item._qfStructReview===1||raw._qfStructReview===1)){
        replyTotal=Number(raw.ReviewCount||raw.reviewCount||0)||0;
    }

    if(replyTotal<embedded.length)replyTotal=embedded.length;

    return {
        id:row.id,
        name:row.name,
        avatar:row.avatar,
        frame:item.frame_url||raw.FrameUrl||raw.frameUrl||raw.UserHeadFrame||"",
        content:payload.content,
        time:t,
        ip:row.ip,
        like:row.like,
        replies:replyTotal,
        embedded:embedded,
        titles:row.titles,
        floor:row.floor,
        image:payload.image,
        audio:payload.audio,
        audioPage:payload.audioPage,
        audioDetected:payload.audioDetected,
        audioDuration:payload.audioDuration,
        audioPath:payload.audioPath,
        audioDiag:payload.audioDiag,
        replyTo:raw.RelatedUser||raw.relatedUser||
            raw.ReplyUserName||raw.replyUserName||"",
        god:raw.EssenceType===2||raw.essenceType===2||
            raw.IsEssence===true||raw.isEssence===true,
        raw:raw
    };
}
function likeSvg(){return '<svg viewBox="0 0 24 24"><path d="M7.5 10.2 10.8 3c.7-1.5 3-.9 3 1v4.1h4.3c1.6 0 2.8 1.5 2.4 3l-1.5 7.1c-.2 1.1-1.2 1.8-2.3 1.8H7.5V10.2Z"></path><path d="M7.5 10.2H3.7v9.8h3.8"></path></svg>'}
function badgeHtml(t){if(!t)return'';if(t.type==='img')return '<img class="badgeImg" src="'+esc(t.val)+'" referrerpolicy="no-referrer" loading="lazy" decoding="async">';var c='badgeText',v=String(t.val||''),compact=v.replace(/[\s·•・\-_|｜]/g,'');if(t.role==='rank'||/^(见习|学徒|执事|舵主|堂主|护法|长老|掌门|盟主)$/.test(compact))c+=' rank';else if(t.role==='official'||/纪律助理|版主|管理员|运营|助理/.test(v))c+=' official';else if(t.role==='level'||/^(?:lv?|等级)\d{1,2}(?:天枢|天璇|天玑|天权|玉衡|开阳|摇光)?$/i.test(compact))c+=' level';else if(/红尘仙|十年大佬|种花少年|种花少女/.test(v))c+=' pink';else if(/长鲸月落/.test(v))c+=' deepBlue';else if(/鉴中仙|逢考必胜/.test(v))c+=' red';else if(t.tp===2)c+=' t2';else if(t.tp===3)c+=' t3';else if(t.tp>=4)c+=' t4';var st=[];
if(/^心理医生$/.test(v)){t.fg='#7c5a1d';t.bg='#f8e9bd';t.bd='#ead394';}
else if(/^守知者$/.test(v)){t.fg='#7b4f35';t.bg='#f2ded2';t.bd='#e7c6b4';}
else if(/^占星人$/.test(v)){t.fg='#73518f';t.bg='#eee6f8';t.bd='#d9c8ec';}
if(t.fg)st.push('color:'+t.fg);if(t.bg)st.push('background:'+t.bg);if(t.bd)st.push('border-color:'+t.bd);return '<span class="'+c+'"'+(st.length?' style="'+esc(st.join(';'))+'"':'')+'>'+esc(v)+'</span>'}
function avHtml(c,reply){var cl=reply?'rAvatar':'avatar';var h='<div class="'+cl+'">';if(c.avatar)h+='<img src="'+esc(c.avatar)+'" referrerpolicy="no-referrer" loading="lazy" decoding="async">';else h+='书';h+='</div>';return h}
function meta(c){var a=[];if(c.floor)a.push(String(c.floor)+'楼');var tt=timeText(c.time);if(tt)a.push(tt);if(c.ip)a.push(String(c.ip));return a.join(' · ')}

function qfAudioReviewApiUrls(reviewId){
    reviewId=String(reviewId||'');
    if(!reviewId)return [];

    var common=[
        'bookId='+encodeURIComponent(bid),
        'chapterId='+encodeURIComponent(cid),
        'reviewId='+encodeURIComponent(reviewId),
        'paragraphId='+encodeURIComponent(isChapter?-1:Number(para)||0)
    ];
    if(csrf)common.push('_csrfToken='+encodeURIComponent(csrf));

    var q=common.join('&');

    return [
        'https://m.qidian.com/webcommon/chapterreview/reviewdetail4m?'+q,
        'https://m.qidian.com/webcommon/chapterreview/reviewinfo4m?'+q,
        'https://m.qidian.com/webcommon/chapterreview/reviewdetail?'+q,
        'https://www.qidian.com/ajax/chapterReview/reviewDetail?'+q,
        'https://www.qidian.com/ajax/chapterReview/reviewInfo?'+q,
        'https://m.qidian.com/majax/chapterReview/reviewDetail?'+q
    ];
}

function qfAudioResolveReviewApis(st){
    if(!st||!st.reviewId)return '';

    var us=qfAudioReviewApiUrls(st.reviewId);

    for(var i=0;i<us.length;i++){
        try{
            var txt=http(us[i]);
            if(!txt||txt.length>1200000)continue;

            var u=audioUrlFromPayloadText(txt);

            if(u){
                st.apiSource='api#'+i;
                return u;
            }

            try{
                var d=JSON.parse(txt);
                u=audioOf(d);

                if(u){
                    st.apiSource='api#'+i;
                    return u;
                }
            }catch(_e){}
        }catch(_e2){}
    }

    return '';
}

var qfAudioPlayers={};

function qfAudioTime(v){
    v=Number(v);
    if(!isFinite(v)||v<0)v=0;

    var s=Math.floor(v%60);
    var m=Math.floor(v/60)%60;
    var h=Math.floor(v/3600);

    function z(n){return n<10?'0'+n:String(n);}

    if(h>0)return h+':'+z(m)+':'+z(s);
    return m+':'+z(s);
}

function qfAudioPlayerId(c){
    return 'qfa_'+String(c.id||Math.random()).replace(/[^\w-]/g,'_');
}

function qfAudioPlayerUi(st){
    return document.getElementById(st.id);
}

function qfAudioSetStatus(st,msg,isError){
    var box=qfAudioPlayerUi(st);
    if(!box)return;

    var e=box.querySelector('.qfAudioStatus');
    if(e){
        e.textContent=String(msg||'');
        e.classList.toggle('error',!!isError);
    }
}

function qfAudioUpdateUi(st){
    var box=qfAudioPlayerUi(st);
    if(!box)return;

    var media=st.media;
    var current=0,duration=Number(st.durationHint||0);

    if(media){
        try{
            current=Number(media.currentTime||0);
            var md=Number(media.duration||0);

            /*
             * Do not trust bogus one-second metadata. Real loaded media wins
             * once it reports a sane duration.
             */
            if(isFinite(md)&&md>=1.5)duration=md;
        }catch(e0){}
    }

    if(duration>=1.5)st.durationHint=duration;
    else duration=0;

    var cur=box.querySelector('.qfAudioCurrent');
    var dur=box.querySelector('.qfAudioDuration');
    var fill=box.querySelector('.qfAudioProgressFill');
    var btn=box.querySelector('.qfAudioToggle');

    if(cur)cur.textContent=qfAudioTime(current);
    if(dur)dur.textContent=duration>0?qfAudioTime(duration):'--:--';

    if(fill){
        var pct=duration>0
            ?Math.max(0,Math.min(100,current/duration*100))
            :0;
        fill.style.width=pct+'%';
    }

    if(btn){
        var playing=false;
        try{playing=!!(media&&!media.paused&&!media.ended);}catch(e1){}
        btn.textContent=playing?'❚❚':'▶';
    }
}

function qfAudioCandidateLooksApi(u){
    u=String(u||'');

    try{
        var a=document.createElement('a');
        a.href=u;

        var host=String(a.hostname||'');
        var path=String(a.pathname||'');

        return (
            /qidian\.com$/i.test(host)||
            /\.qidian\.com$/i.test(host)
        )&&(
            /\/(?:ajax|majax|api|webcommon|chapterreview|review)\//i.test(path)||
            !/\.(?:mp3|m4a|aac|wav|ogg|amr|opus|flac|m3u8)(?:$|\?)/i.test(path)
        );
    }catch(e){
        return false;
    }
}

function qfAudioResolveViaText(st,u){
    if(!u)return '';

    try{
        var txt=http(u);

        /*
         * Don't treat huge/binary response as JSON/HTML resolver text.
         */
        if(!txt||txt.length>1500000)return '';

        var next=audioUrlFromPayloadText(txt);

        if(
            next&&
            String(next)!==String(u)
        ){
            return next;
        }
    }catch(e){}

    return '';
}

function qfAudioResolveDetail(st){
    if(!st.detailUrl)return '';

    try{
        var html=http(st.detailUrl);
        if(!html||html.length>1500000)return '';

        return audioUrlFromPayloadText(html)||'';
    }catch(e){
        return '';
    }
}

function qfAudioBind(st,src,autoPlay){
    if(!st||!src)return false;

    if(st.media){
        try{
            st.media.pause();
            st.media.removeAttribute('src');
            st.media.load();
        }catch(_e){}
    }

    var media=document.createElement('audio');
    media.preload='metadata';
    media.src=String(src);
    media.style.display='none';

    st.media=media;
    st.activeSrc=String(src);
    st.attempt++;

    var done=false;

    function fail(reason){
        if(done)return;
        done=true;
        qfAudioTryNext(st,reason);
    }

    function ready(){
        if(done)return;

        var d=Number(media.duration||0);

        /*
         * duration==Infinity can happen for a stream and is still playable.
         * 0/NaN or the previous bogus 1-second result are not accepted here.
         */
        if((isFinite(d)&&d>=1.5)||d===Infinity){
            done=true;
            st.ready=true;

            if(isFinite(d)&&d>=1.5)st.durationHint=d;

            qfAudioSetStatus(st,'音频已就绪',false);
            qfAudioUpdateUi(st);

            if(autoPlay){
                try{
                    var p=media.play();
                    if(p&&typeof p.catch==='function'){
                        p.catch(function(){qfAudioSetStatus(st,'点击播放',false);});
                    }
                }catch(e0){}
            }
        }
    }

    media.addEventListener('loadedmetadata',ready);
    media.addEventListener('durationchange',ready);
    media.addEventListener('canplay',ready);
    media.addEventListener('error',function(){fail('媒体地址加载失败');});
    media.addEventListener('stalled',function(){
        setTimeout(function(){
            if(!st.ready)fail('媒体加载停滞');
        },1600);
    });
    media.addEventListener('timeupdate',function(){qfAudioUpdateUi(st);});
    media.addEventListener('play',function(){qfAudioUpdateUi(st);});
    media.addEventListener('pause',function(){qfAudioUpdateUi(st);});
    media.addEventListener('ended',function(){qfAudioUpdateUi(st);});

    document.body.appendChild(media);

    try{media.load();}catch(e1){fail('媒体load失败');}

    setTimeout(function(){
        if(!done&&!st.ready){
            var d=0;
            try{d=Number(media.duration||0);}catch(_e){}
            if(!(isFinite(d)&&d>=1.5)&&d!==Infinity){
                fail('未取得有效音频时长');
            }
        }
    },4200);

    return true;
}

function qfAudioTryNext(st,reason){
    if(!st||st.finished)return;

    if(
        st.step<1&&
        st.directSrc&&
        qfAudioCandidateLooksApi(st.directSrc)
    ){
        st.step=1;
        qfAudioSetStatus(st,'解析音频地址…',false);

        var r1=qfAudioResolveViaText(st,st.directSrc);

        if(r1){
            st.resolvedSrc=r1;
            qfAudioBind(st,r1,true);
            return;
        }
    }

    if(st.step<2&&st.reviewId){
        st.step=2;
        qfAudioSetStatus(st,'查询配音详情…',false);

        var ra=qfAudioResolveReviewApis(st);

        if(
            ra&&
            ra!==st.directSrc&&
            ra!==st.resolvedSrc
        ){
            st.resolvedSrc=ra;
            qfAudioBind(st,ra,true);
            return;
        }
    }

    if(st.step<3&&st.detailUrl){
        st.step=3;
        qfAudioSetStatus(st,'解析配音页面…',false);

        var r2=qfAudioResolveDetail(st);

        if(
            r2&&
            r2!==st.directSrc&&
            r2!==st.resolvedSrc
        ){
            st.resolvedSrc=r2;
            qfAudioBind(st,r2,true);
            return;
        }
    }

    st.finished=true;
    st.ready=false;

    var info=[];

    if(st.diag)info.push(st.diag);
    else if(st.path&&!/^_qf/i.test(st.path))info.push('字段 '+st.path);

    if(
        st.directSrc&&
        !/h5\.if\.qidian\.com\/new\/chapterreview/i.test(st.directSrc)
    ){
        info.push(safeAudioUrlInfo(st.directSrc));
    }

    var msg='播放失败';

    if(info.length){
        msg+=' · 原始字段 '+info.join(' · ');
    }else{
        msg+=' · 未发现起点原始音频字段';
    }

    msg+=' · 请截图红字';

    qfAudioSetStatus(st,msg,true);
    qfAudioUpdateUi(st);
}
function qfAudioStart(st){
    if(!st)return;

    st.finished=false;
    st.step=0;
    st.attempt=0;

    if(
        st.directSrc&&
        /h5\.if\.qidian\.com\/new\/chapterreview/i.test(st.directSrc)
    ){
        st.directSrc='';
        st.path='';
    }

    qfAudioSetStatus(st,'正在加载音频…',false);

    if(st.directSrc){
        qfAudioBind(st,st.directSrc,true);
        return;
    }

    qfAudioTryNext(st,'无直接音频地址');
}
function qfAudioToggle(st){
    if(!st)return;

    if(!st.media||st.finished){
        qfAudioStart(st);
        return;
    }

    if(!st.ready){
        qfAudioSetStatus(st,'正在加载音频…',false);
        return;
    }

    try{
        if(st.media.paused||st.media.ended){
            var p=st.media.play();

            if(p&&typeof p.catch==='function'){
                p.catch(function(){
                    qfAudioTryNext(st,'浏览器拒绝播放');
                });
            }
        }else{
            st.media.pause();
        }
    }catch(e){
        qfAudioTryNext(st,'播放异常');
    }

    qfAudioUpdateUi(st);
}

function qfAudioSeek(st,ev,bar){
    if(!st||!st.media||!bar)return;

    var d=0;
    try{d=Number(st.media.duration||st.durationHint||0);}catch(e0){}

    if(!(isFinite(d)&&d>=1.5))return;

    var rect=bar.getBoundingClientRect();
    var x=Number(ev.clientX||0)-rect.left;
    var pct=Math.max(0,Math.min(1,x/Math.max(1,rect.width)));

    try{st.media.currentTime=pct*d;}catch(e1){}

    qfAudioUpdateUi(st);
}

function qfAudioPlayerHtml(c){
    var id=qfAudioPlayerId(c);
    var dur=saneAudioDuration(c.audioDuration)||0;
    var cls='qfAudioPlayer qfAudioPlayerOfficial';

    return '<div class="'+cls+'" id="'+esc(id)+'" '+
        'data-rid="'+esc(c.id||'')+'" '+
        'data-src="'+esc(c.audio||'')+'" '+
        'data-detail="'+esc(c.audioPage||'')+'" '+
        'data-path="'+esc(c.audioPath||'')+'" '+
        'data-diag="'+esc(c.audioDiag||'')+'" '+
        'data-duration="'+esc(String(dur||0))+'">'+
        '<button class="qfAudioToggle" type="button">▶</button>'+
        '<div class="qfAudioCenter">'+
          '<div class="qfAudioTimes">'+
            '<span class="qfAudioCurrent">0:00</span>'+
            '<span class="qfAudioSep"> / </span>'+
            '<span class="qfAudioDuration">'+(dur>0?qfAudioTime(dur):'--:--')+'</span>'+
          '</div>'+
          '<div class="qfAudioProgress">'+
            '<div class="qfAudioProgressFill"></div>'+
          '</div>'+
          '<div class="qfAudioStatus">起点配音 · 点击加载</div>'+
        '</div>'+
        '</div>';
}

function qfAudioEnsureState(box){
    if(!box)return null;

    var id=String(box.id||'');
    if(!id)return null;

    if(qfAudioPlayers[id])return qfAudioPlayers[id];

    var st={
        id:id,
        reviewId:String(box.getAttribute('data-rid')||''),
        directSrc:String(box.getAttribute('data-src')||''),
        detailUrl:String(box.getAttribute('data-detail')||''),
        path:String(box.getAttribute('data-path')||''),
        diag:String(box.getAttribute('data-diag')||''),
        durationHint:saneAudioDuration(box.getAttribute('data-duration'))||0,
        apiSource:'',
        resolvedSrc:'',
        activeSrc:'',
        media:null,
        ready:false,
        finished:false,
        step:0,
        attempt:0
    };

    qfAudioPlayers[id]=st;
    qfAudioUpdateUi(st);
    return st;
}


function qfAudioRoleInfo(c){
    var raw=c&&c.raw?c.raw:(c||{});
    var info=raw.AudioRoleInfo||raw.audioRoleInfo||{};
    var id=String(
        info.AudioRoleId||info.audioRoleId||
        raw.AudioRoleId||raw.audioRoleId||''
    ).trim();
    var name=String(
        info.AudioRoleName||info.audioRoleName||
        raw.AudioRoleName||raw.audioRoleName||''
    ).trim();
    if(!name&&id==='100')name='旁白';
    return {id:id,name:name};
}

function qfAudioRoleKey(c){
    var r=qfAudioRoleInfo(c);
    if(r.name)return 'name:'+r.name;
    if(r.id&&r.id!=='0')return 'id:'+r.id;
    return 'all';
}

function qfAudioRoleLabel(c){
    var r=qfAudioRoleInfo(c);
    if(r.name)return r.name;
    if(r.id&&r.id!=='0')return '#'+r.id;
    return '';
}

function qfAudioRoleStats(rows){
    var map={},out=[];
    rows=Array.isArray(rows)?rows:[];

    for(var i=0;i<rows.length;i++){
        var c=adapt(rows[i]||{});
        var key=qfAudioRoleKey(c);
        var label=qfAudioRoleLabel(c);
        if(!label||key==='all')continue;
        if(!map[key])map[key]={key:key,label:label,count:0};
        map[key].count++;
    }

    for(var k in map){
        if(Object.prototype.hasOwnProperty.call(map,k))out.push(map[k]);
    }

    out.sort(function(a,b){
        var d=Number(b.count||0)-Number(a.count||0);
        if(d)return d;
        return String(a.label||'').localeCompare(String(b.label||''),'zh-Hans-CN');
    });
    return out;
}

function qfAudioRoleBarHtml(rows){
    var stats=qfAudioRoleStats(rows);
    if(!stats.length)return '';

    var h='<div class="audioRoleBar">';
    h+='<button class="audioRoleChip'+(audioRoleFilter==='all'?' active':'')+'" type="button" data-audiorole="all">全部配音<span class="count">'+rows.length+'</span></button>';

    for(var i=0;i<stats.length&&i<12;i++){
        var it=stats[i]||{};
        h+='<button class="audioRoleChip'+(audioRoleFilter===it.key?' active':'')+'" type="button" data-audiorole="'+esc(it.key)+'">'+esc(it.label)+'<span class="count">'+esc(String(it.count||0))+'</span></button>';
    }

    return h+'</div>';
}

function qfAudioReplyPreviewHtml(c){
    return replyHtml(c);
}

function qfAudioCommentHtml(c){
    var b='';
    for(var i=0;i<c.titles.length&&i<3;i++)b+=badgeHtml(c.titles[i]);

    var role=qfAudioRoleLabel(c);
    var h='<div class="comment audioComment '+(currentTab==='audio'?'audioTabCard':'allAudioCard')+'" data-id="'+esc(c.id)+'">'+
        '<div class="mainRow"><div class="avatarWrap">'+
        avHtml(c,false)+
        '</div><div class="body"><div class="nameRow">'+
        '<span class="name">'+esc(c.name)+'</span>'+
        '<span class="badges">'+b+'</span></div>'+
        (role?'<div class="audioRoleMini">'+esc(role)+'</div>':'')+
        '<div class="content qfFoldable qfFolded">'+fmt(c.content)+'</div><button class="foldBtn hidden" type="button">展开全文</button>';

    if(c.audioPage){
        h+=qfAudioPlayerHtml(c);
    }else if(c.audio){
        h+='<audio class="audio qfAudioNative" src="'+esc(c.audio)+'" controls preload="metadata"></audio>';
    }

    h+='<div class="metaLine"><div class="meta">'+esc(meta(c))+'</div><div class="like">'+likeSvg()+'<span>'+c.like+'</span></div></div></div></div>';

    var embedded=Array.isArray(c.embedded)?c.embedded:[];
    var total=Math.max(Number(c.replies||0),embedded.length);

    if(total>0){
        h+='<div class="audioRepliesPreview" id="rp_'+esc(c.id)+'">';

        var previewCount=Math.min(embedded.length,2);
        for(var r=0;r<previewCount;r++){
            h+=qfAudioReplyPreviewHtml(embedded[r]);
        }

        if(c.id){
            var remain=Math.max(0,total-previewCount);
            var ids=qfCommentRootIds(c);
            h+='<div class="audioMoreReplies replyMoreLocal" data-root="'+esc(ids.primary||c.id)+'" data-root-alt="'+esc(ids.alt||'')+'" data-root-list="'+esc((ids.all||[]).join(','))+'" data-total="'+total+'">'+
                (remain>0?'查看更多'+remain+'条回复':'查看全部'+total+'条回复')+
                '</div>';
        }

        h+='</div>';
    }

    return h+'</div>';
}

function qfAudioRenderDirectPage(){
    var rows=Array.isArray(audioDirectRows)?audioDirectRows:[];
    var pack=audioDirectPack||{name:'',total:rows.length,list:rows,roles:[],log:[]};
    var h='';

    h+=qfAudioRoleBarHtml(rows);

    h+='<details class="qfAudioDiagFold"><summary>'+
        '已命中起点官方配音接口 · AudioCount='+esc(String(pack.total||rows.length||0))+' · 点此查看诊断'+
        '</summary>'+qfDirectDiagHtml(pack)+'</details>';

    var shown=0;

    for(var i=0;i<rows.length;i++){
        var c=adapt(rows[i]||{});
        var key=qfAudioRoleKey(c);
        if(audioRoleFilter!=='all'&&audioRoleFilter!==key)continue;
        h+=commentHtml(c);
        shown++;
    }

    if(!shown){
        h+='<div class="empty" style="line-height:1.8">当前角色筛选下暂无配音评论。</div>';
    }

    listEl.innerHTML=h;
    moreEl.classList.add('hidden');
    setTimeout(function(){qfApplyFolds(listEl)},0);
}

function qfApplyFolds(root){
    root=root||document;var ns=root.querySelectorAll('.qfFoldable');
    for(var i=0;i<ns.length;i++){var el=ns[i];if(el.getAttribute('data-fold-ready')==='1')continue;el.setAttribute('data-fold-ready','1');var btn=el.nextElementSibling;if(!(btn&&btn.classList&&btn.classList.contains('foldBtn')))continue;var over=false;try{over=el.scrollHeight>el.clientHeight+4}catch(_e){}if(!over){el.classList.remove('qfFolded');btn.classList.add('hidden')}else btn.classList.remove('hidden')}
}
function qfToggleFold(btn){if(!btn)return;var el=btn.previousElementSibling;if(!(el&&el.classList&&el.classList.contains('qfFoldable')))return;var f=el.classList.contains('qfFolded');el.classList.toggle('qfFolded',!f);btn.textContent=f?'收起':'展开全文'}
function commentHtml(c){
    if(c.audioPage||c.audio)return qfAudioCommentHtml(c);

    var b='';
    for(var i=0;i<c.titles.length&&i<3;i++)b+=badgeHtml(c.titles[i]);

    var h='<div class="comment" data-id="'+esc(c.id)+'">'+
        '<div class="mainRow"><div class="avatarWrap">'+
        avHtml(c,false)+
        (c.frame?'<div class="frame"><img src="'+esc(c.frame)+'" referrerpolicy="no-referrer"></div>':'')+
        '</div><div class="body"><div class="nameRow">'+
        '<span class="name">'+esc(c.name)+'</span>'+
        '<span class="badges">'+b+'</span></div>'+
        '<div class="content">'+fmt(c.content)+'</div>';

    if(c.image){
        h+='<img class="mediaImg zoom" src="'+esc(c.image)+'" referrerpolicy="no-referrer" loading="lazy" decoding="async">';
    }
    /*
     * 已经通过 reviewId 官方详情页确认是配音时，
     * 优先让起点自己的详情页播放器处理真正的音频地址/签名/Cookie。
     * 不再把从详情HTML里提取到但无法直接播放的URL优先塞给<audio>。
     */
    if(c.audioPage){
        h+=qfAudioPlayerHtml(c);
    }else if(c.audio){
        h+='<audio class="audio qfAudioNative" src="'+esc(c.audio)+
           '" controls preload="metadata"></audio>';
    }

    h+='<div class="metaLine"><div class="meta">'+esc(meta(c))+'</div><div class="like">'+likeSvg()+'<span>'+c.like+'</span></div></div></div></div>';

    if(c.god)h+='<div class="god">神评论</div>';

    var embedded=Array.isArray(c.embedded)?c.embedded:[];
    var total=Math.max(Number(c.replies||0),embedded.length);

    if(total>0){
        var rh='',ids=qfCommentRootIds(c);

        /* embedded 只作为网络异常时的本地兜底。正常第一次展开会立即用正式楼中楼第1页替换它，
           避免出现“前1~2条无标签、继续加载后的回复才有标签”的割裂体验。 */
        for(var r=0;r<embedded.length;r++){
            rh+=replyHtml(embedded[r]);
        }

        if(total>embedded.length&&c.id){
            rh+='<div class="replyMore replyMoreLocal" '+
                'data-root="'+esc(ids.primary||c.id)+'" '+
                'data-root-alt="'+esc(ids.alt||'')+'" '+
                'data-root-list="'+esc((ids.all||[]).join(','))+'" '+
                'data-total="'+total+'">'+
                '继续加载剩余 '+(total-embedded.length)+' 条回复</div>';
        }

        h+='<div class="replyToggle" data-reply="'+esc(c.id)+'" data-root="'+esc(ids.primary||c.id)+'" data-total="'+total+'">'+
            '展开全部'+total+'条回复'+
            '<svg viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"></path></svg></div>'+
            '<div class="replies hidden" id="rp_'+esc(c.id)+'">'+rh+'</div>';
    }

    return h+'</div>';
}
function replyHtml(c){var b='';for(var i=0;i<c.titles.length&&i<2;i++)b+=badgeHtml(c.titles[i]);var h='<div class="reply" data-rid="'+esc(c.id||'')+'"><div class="replyHead">'+avHtml(c,true)+'<span class="rName">'+esc(c.name)+'</span><span class="rBadges">'+b+'</span></div><div class="rContent qfFoldable qfFolded">'+(c.replyTo?'<span class="replyTo">回复 '+esc(c.replyTo)+'：</span>':'')+fmt(c.content)+'</div><button class="foldBtn hidden" type="button">展开全文</button>';if(c.image)h+='<img class="mediaImg zoom" style="margin-left:36px;max-width:55vw" src="'+esc(c.image)+'" referrerpolicy="no-referrer" loading="lazy" decoding="async">';if(c.audioPage){
    h+='<div style="margin-left:36px;max-width:58vw">'+qfAudioPlayerHtml(c)+'</div>';
}else if(c.audio){
    h+='<audio class="audio qfAudioNative" style="margin-left:36px;max-width:55vw" '+
       'src="'+esc(c.audio)+'" controls preload="metadata"></audio>';
}h+='<div class="rMetaLine"><div class="rMeta">'+esc(meta(c))+'</div><div class="rLike">'+likeSvg()+'<span>'+c.like+'</span></div></div></div>';return h}
function url(action,p,ps,extra){
    extra=extra||{};
    var tp=extra.type==null?2:Number(extra.type);
    if(isNaN(tp))tp=2;

    var pid=Number(
        extra.paragraphId!=null
            ?extra.paragraphId
            :para
    );
    if(isNaN(pid))pid=Number(segment)||0;

    var q=[
        "bookId="+encodeURIComponent(bid),
        "chapterId="+encodeURIComponent(cid),
        "page="+encodeURIComponent(p||1),
        "pageSize="+encodeURIComponent(ps||20),
        "segmentId="+encodeURIComponent(segment),
        "paragraphId="+encodeURIComponent(pid),
        "type="+encodeURIComponent(tp)
    ];
    if(csrf)q.push("_csrfToken="+encodeURIComponent(csrf));

    return "https://www.qidian.com/ajax/chapterReview/reviewList?"+q.join("&");
}
function mobileUrl(p,ps,extra){
    extra=extra||{};
    var tp=extra.type==null?2:Number(extra.type);
    if(isNaN(tp))tp=2;

    var pid=Number(
        extra.paragraphId!=null
            ?extra.paragraphId
            :para
    );
    if(isNaN(pid))pid=Number(segment)||0;

    var q=[
        "bookId="+encodeURIComponent(bid),
        "chapterId="+encodeURIComponent(cid),
        "page="+encodeURIComponent(p||1),
        "pageSize="+encodeURIComponent(ps||20),
        "segmentId="+encodeURIComponent(segment),
        "paragraphId="+encodeURIComponent(pid),
        "type="+encodeURIComponent(tp)
    ];
    if(csrf)q.push("_csrfToken="+encodeURIComponent(csrf));

    return "https://m.qidian.com/majax/chapterReview/reviewList?"+q.join("&");
}
function mobile4mUrl(p,ps,extra){
    extra=extra||{};

    var pid=Number(
        extra.paragraphId!=null
            ?extra.paragraphId
            :para
    );
    if(isNaN(pid)){
        pid=isChapter?-1:Number(segment)||0;
    }

    var q=[
        "bookId="+encodeURIComponent(bid),
        "chapterId="+encodeURIComponent(cid),
        "paragraphId="+encodeURIComponent(pid),
        "page="+encodeURIComponent(p||1),
        "pageSize="+encodeURIComponent(ps||20)
    ];

    if(csrf)q.push("_csrfToken="+encodeURIComponent(csrf));

    return "https://m.qidian.com/webcommon/chapterreview/reviewlist4m?"+q.join("&");
}

function pcSegmentUrl2930(p,ps,extra){
    extra=extra||{};
    var sg=Number(extra.segmentId!=null?extra.segmentId:segment);
    if(!isFinite(sg))sg=Number(segment)||0;

    var q=[
        'bookId='+encodeURIComponent(bid),
        'chapterId='+encodeURIComponent(cid),
        'page='+encodeURIComponent(p||1),
        'pageSize='+encodeURIComponent(ps||20),
        'segmentId='+encodeURIComponent(sg),
        'type='+encodeURIComponent(extra.type==null?2:Number(extra.type)||2)
    ];

    var token=String(qfReplyCookieValue2929('_csrfToken')||csrf||'');
    var wts=String(qfReplyCookieValue2929('w_tsfp')||'');
    if(token)q.push('_csrfToken='+encodeURIComponent(token));
    if(wts)q.push('w_tsfp='+encodeURIComponent(wts));

    return 'https://www.qidian.com/ajax/chapterReview/reviewList?'+q.join('&');
}

/* alpha18.2：canonical comment model。
 * 关键原则：完整结构链(struct)永远做骨架；Reader type=0 只负责 TitleInfoList 等富身份字段。
 * 不能再让 rich 行覆盖 struct 行，否则 ReviewId / ReplyCount / replyList 会再次丢失。 */
function qfReviewRowIdsV503(row){
    row=row||{};var raw=row.raw||row,u=row.user_info||raw.UserInfo||raw.userInfo||raw.User||raw.user||{},out=[],seen={};
    function add(v){var x=String(v==null?'':v).trim();if(!x||seen[x])return;seen[x]=1;out.push(x);}
    add(row.comment_id);add(row.reply_id);add(row.ReplyId);add(row.replyId);
    add(raw.ReplyId);add(raw.replyId);add(raw.ReviewId);add(raw.reviewId);add(raw.CommentId);add(raw.commentId);
    add(raw.Id);add(raw.id);add(raw.PostId);add(raw.postId);
    return out;
}
function qfReviewRowIdV502(row){var a=qfReviewRowIdsV503(row);return a.length?a[0]:'';}
function qfReviewUserIdV503(row){
    row=row||{};var raw=row.raw||row,u=row.user_info||raw.UserInfo||raw.userInfo||raw.User||raw.user||{};
    return String(row.user_id||u.UserId||u.userId||u.UserID||u.userID||u.Uid||u.uid||raw.UserId||raw.userId||raw.UserID||raw.userID||raw.Uid||raw.uid||'').trim();
}
function qfReviewUserNameV503(row){
    row=row||{};var raw=row.raw||row,u=row.user_info||raw.UserInfo||raw.userInfo||raw.User||raw.user||{};
    return String(u.user_name||u.UserName||u.NickName||u.nickName||u.nickname||raw.UserName||raw.userName||raw.NickName||raw.nickName||raw.nickname||'').replace(/\s+/g,'').trim();
}
function qfReviewTextSigV503(row){
    row=row||{};var raw=row.raw||row;
    var c=String(textOf(row.text||row.content||raw.Content||raw.content||raw.ReviewContent||raw.reviewContent||raw.Body||raw.PostContent||raw.Text||raw.text||'')||'');
    c=c.replace(/^回复\s*[^：:]{1,40}[：:]\s*/,'').replace(/\[fn=\d+\]/g,'').replace(/[\s\u200b\u200c\u200d\ufeff]+/g,'').replace(/[“”‘’]/g,'').trim();
    return c;
}
function qfReviewRowSigV502(row){return qfReviewUserNameV503(row)+'|'+qfReviewTextSigV503(row);}
function qfReviewTitleListV502(o){
    if(!o||typeof o!=='object')return null;
    var a=o.TitleInfoList!==undefined?o.TitleInfoList:(o.titleInfoList!==undefined?o.titleInfoList:o.title_info_list);
    if(typeof a==='string'){try{a=JSON.parse(a)}catch(_e){a=null}}
    return Array.isArray(a)&&a.length?a:null;
}
function qfReviewHasTitleV503(v){
    if(!v||typeof v!=='object')return false;
    try{return QF_ReviewIdentity.rawTitleList(v).length>0;}catch(_e){return false;}
}
function qfReviewCopyTitleV502(dst,src){
    if(!dst||!src||typeof dst!=='object'||typeof src!=='object')return dst;
    function rawOf(v){return v&&typeof v==='object'?(v.raw||v):{};}
    function userOf(v){var r=rawOf(v);return v.user_info||r.user_info||v.UserInfo||v.userInfo||r.UserInfo||r.userInfo||r.User||r.user||null;}
    function setList(o,a){if(!o||typeof o!=='object'||!a||!a.length)return;o.TitleInfoList=a;}
    var dr=rawOf(dst),sr=rawOf(src),du=userOf(dst),su=userOf(src);
    var top=qfReviewTitleListV502(sr)||qfReviewTitleListV502(src),usr=qfReviewTitleListV502(su);
    if(top){setList(dr,top);if(dst!==dr)setList(dst,top);}
    if(usr){if(!du){try{dr.UserInfo={};du=dr.UserInfo;}catch(_u){}}setList(du,usr);}
    if(su&&du){var ks=['UserName','userName','NickName','nickName','UserHeadIcon','userHeadIcon','Avatar','avatar','UserId','userId','UserID','userID'];for(var i=0;i<ks.length;i++){var k=ks[i];if((du[k]===undefined||du[k]===null||du[k]==='')&&su[k]!==undefined&&su[k]!==null)du[k]=su[k];}}
    return dst;
}
function qfReviewRichRowsV503(pack){
    var out=[],seenObj=[],seenKey={};
    function add(v){
        if(!v||typeof v!=='object'||Array.isArray(v)||!qfReviewHasTitleV503(v))return;
        var ids=qfReviewRowIdsV503(v),uid=qfReviewUserIdV503(v),nm=qfReviewUserNameV503(v),tx=qfReviewTextSigV503(v);
        var k=ids.length?'i:'+ids[0]:(uid?'u:'+uid:(nm?('n:'+nm+(tx?'|'+tx:'')):''));
        if(k&&seenKey[k])return;if(k)seenKey[k]=1;out.push(v);
    }
    function walk(v,d,parent){
        if(v==null||d>11||typeof v!=='object')return;if(seenObj.indexOf(v)>=0)return;seenObj.push(v);
        if(Array.isArray(v)){for(var i=0;i<v.length;i++)walk(v[i],d+1,parent);return;}
        add(v);
        /* TitleInfoList 常直接挂在 UserInfo 对象上。此时把父评论身份字段复制到轻量候选，便于按 UserId/用户名匹配。 */
        if(qfReviewTitleListV502(v)&&parent&&typeof parent==='object'){
            var pu=parent.UserInfo||parent.userInfo||parent.User||parent.user||{};
            var proxy={raw:parent,UserInfo:v};
            if(!qfReviewUserIdV503(proxy)&&qfReviewUserIdV503({raw:parent,user_info:pu}))proxy.user_id=qfReviewUserIdV503({raw:parent,user_info:pu});
            add(proxy);
        }
        for(var k in v)if(Object.prototype.hasOwnProperty.call(v,k)&&v[k]&&typeof v[k]==='object')walk(v[k],d+1,v);
    }
    if(pack&&Array.isArray(pack.list))for(var i=0;i<pack.list.length;i++)add(pack.list[i]);
    try{if(pack&&pack.raw)walk(pack.raw,0,null);else if(pack&&pack.data)walk(pack.data,0,null);}catch(_w){}
    return out;
}
function qfReviewFusePackV502(structPack,richPack){
    if(!structPack||!Array.isArray(structPack.list)||!structPack.list.length)return richPack||structPack;
    if(!richPack)return structPack;
    var rl=qfReviewRichRowsV503(richPack);if(!rl.length)return structPack;
    var byId={},byUid={},bySig={},byName={},nameCount={};
    function put(map,k,v){if(k&&!map[k])map[k]=v;}
    for(var i=0;i<rl.length;i++){
        var rr=rl[i]||{};try{qfTitleIdentityPutV504(rr);}catch(_tir){}
        var ids=qfReviewRowIdsV503(rr),uid=qfReviewUserIdV503(rr),sg=qfReviewRowSigV502(rr),nm=qfReviewUserNameV503(rr);
        for(var ii=0;ii<ids.length;ii++)put(byId,ids[ii],rr);
        put(byUid,uid,rr);put(bySig,sg,rr);if(nm){nameCount[nm]=(nameCount[nm]||0)+1;put(byName,nm,rr);}
    }
    for(var j=0;j<structPack.list.length;j++){
        var st=structPack.list[j]||{},sids=qfReviewRowIdsV503(st),suid=qfReviewUserIdV503(st),ss=qfReviewRowSigV502(st),sn=qfReviewUserNameV503(st),m=null;
        for(var si=0;si<sids.length&&!m;si++)m=byId[sids[si]]||null;
        if(!m&&suid)m=byUid[suid]||null;
        if(!m&&ss)m=bySig[ss]||null;
        /* 用户级标签可按唯一用户名回填。即便同一用户多条回复，身份标签本身也是一致的。 */
        if(!m&&sn&&nameCount[sn]===1)m=byName[sn]||null;
        if(m){
            qfReviewCopyTitleV502(st,m);
            /* Reader 根评论常把首批楼中楼放在 replyList。结构骨架仍用 Web/share，
               但嵌入回复的用户标签在这里提前登记/融合，展开时无需等待第二次请求。 */
            try{
                var sr0=st.raw||st,rr0=m.raw||m;
                var sa=sr0.replyList||sr0.ReplyList||sr0.replies||sr0.Replies||[];
                var ra=rr0.replyList||rr0.ReplyList||rr0.replies||rr0.Replies||[];
                if(Array.isArray(ra))for(var ari=0;ari<ra.length;ari++)qfTitleIdentityPutV504(ra[ari]);
                if(Array.isArray(sa)&&Array.isArray(ra)&&sa.length&&ra.length){
                    var rp=qfReviewFusePackV502({list:sa,total:sa.length,source:'embedded-struct'},{list:ra,total:ra.length,source:'embedded-reader'});
                    if(rp&&rp.list&&rp.list!==sa){/* 当前实现原地融合；保留防御分支 */}
                }
            }catch(_erf){}
        }
        try{st._qfStructReview=1;}catch(_m){}
    }
    structPack.total=Math.max(Number(structPack.total||0),Number(richPack.total||0),structPack.list.length);
    structPack.richSource=String(richPack.source||'');
    return structPack;
}
function qfReviewMarkStructPackV502(pack){
    if(!pack||!Array.isArray(pack.list))return pack;
    for(var i=0;i<pack.list.length;i++){try{pack.list[i]._qfStructReview=1;}catch(_e){}}
    return pack;
}
function qfAppV2ParagraphPack2971(p,ps,extra){
    extra=extra||{};
    if(isChapter||currentTab!=='all')return null;
    var pid=Number(extra.paragraphId!=null?extra.paragraphId:para);
    if(!isFinite(pid))return null;
    /* 正文段落 + 章名都只取 Reader 富身份数据；结构数据交给 fetchPack 的旧稳定链。 */
    if(pid===0||pid<-1)return null;
    function exactList(o){
        if(!o||typeof o!=='object')return [];
        var a=o.TitleInfoList!==undefined?o.TitleInfoList:(o.titleInfoList!==undefined?o.titleInfoList:o.title_info_list);
        if(typeof a==='string'){try{a=JSON.parse(a)}catch(_e){a=[]}}
        return Array.isArray(a)?a:[];
    }
    function richScore(list){
        var n=0;list=Array.isArray(list)?list:[];
        for(var i=0;i<list.length;i++){var x=list[i]||{};if(qfReviewHasTitleV503(x))n++;}
        return n;
    }
    function pullReader(profile,pidValue){
        try{
            var params={bookId:String(bid),chapterId:String(cid),paragraphId:String(pidValue),pg:String(Math.max(1,Number(p)||1)),pz:String(Math.max(20,Number(ps)||20)),type:'0',anchorId:'0',from:'0'};
            var req=qfReaderSignedRequestV3245('v2/chapterreview/getparagraphscomments',params,profile);
            var raw=qfDirectAjax(req.url,'GET',null,null,req.headers),d=parse(raw);if(!d)return null;
            var x=d.Data||d.data||d.Result||d.result||d,l=arr(x),total=Number(x.TotalCount||x.totalCount||x.TextCount||x.textCount||x.Count||x.count||0)||0;
            if(l.length||total>0)return {data:x,list:l,total:total||l.length,source:'app-v2-reader',nextCursor:String(x.NextCursor||x.nextCursor||''),rich:richScore(l),profile:profile,paragraphId:Number(pidValue)};
        }catch(_e){}
        return null;
    }
    function preferred(){try{var v=String(localStorage.getItem('qf_qd_reader_profile_v400')||'');if(v==='reader_ext'||v==='reader_legacy')return v}catch(_e){}return 'reader_ext'}
    function remember(v){try{if(v==='reader_ext'||v==='reader_legacy')localStorage.setItem('qf_qd_reader_profile_v400',v)}catch(_e){}}
    var pidTry=[pid];if(pid===-1)pidTry.push(0);
    var first=preferred(),second=first==='reader_ext'?'reader_legacy':'reader_ext',best=null;
    for(var pi=0;pi<pidTry.length;pi++){
        var pv=pidTry[pi],a=pullReader(first,pv);
        if(a&&a.rich>0){remember(a.profile);return a;}
        if(a&&a.list&&a.list.length){
            var alt=pullReader(second,pv);
            if(alt&&alt.rich>0){remember(alt.profile);return alt;}
            if(!best)best=(alt&&alt.list&&alt.list.length>a.list.length)?alt:a;
        }else if(a&&!best)best=a;
    }
    return best;
}

function fetchPack(action,p,ps,extra){
    extra=extra||{};
    var richPack=null;
    try{richPack=qfAppV2ParagraphPack2971(p,ps,extra);}catch(_qfRich){}

    /* alpha18.2：旧稳定 Web/mobile 链永远负责根评论结构，Reader 只覆盖 TitleInfoList。
       这样标签不会再以丢失 ReplyCount/replyList 为代价。 */
    var us=[mobile4mUrl(p,ps,extra),pcSegmentUrl2930(p,ps,extra),url(action,p,ps,extra),mobileUrl(p,ps,extra)];
    var lastErr=null,bestEmpty=null;
    for(var ui0=0;ui0<us.length;ui0++){
        try{
            var d=parse(http(us[ui0]));if(!d)continue;
            var xx=d.data||d.Data||d,l=arr(xx);
            var total=Number(xx.total||xx.Total||xx.totalCount||xx.TotalCount||xx.ReviewTotalCount||xx.ChapterReviewCount||0)||0;
            var source=ui0===0?'reviewlist4m':(ui0===1?'www-segment':(ui0===2?'www':'majax'));
            if(l.length||total>0){
                var struct=qfReviewMarkStructPackV502({data:xx,list:l,total:total||l.length,source:source});
                return qfReviewFusePackV502(struct,richPack);
            }
            if(Number(d.code)===0||Number(d.Code)===0||Number(d.result)===0||Number(d.Result)===0)bestEmpty={data:xx,list:[],total:0,source:source};
        }catch(e0){lastErr=e0;}
    }
    /* 所有结构接口异常时才允许 Reader 独立显示；正常情况下它永远不是骨架。 */
    if(richPack&&(richPack.list.length||richPack.total>0))return richPack;
    if(bestEmpty)return bestEmpty;
    if(lastErr)throw lastErr;
    throw new Error('起点官方评论接口暂未返回可用数据');
}

function fetchPackFallback(action,p,ps,extra){
    extra=extra||{};
    var us=[url(action,p,ps,extra),mobileUrl(p,ps,extra)];
    var lastErr=null;

    for(var ui=0;ui<us.length;ui++){
        try{
            var d=parse(http(us[ui]));
            if(!d)continue;

            var x=d.data||d.Data||d;
            var l=arr(x);
            var total=Number(
                x.total||x.Total||
                x.totalCount||x.TotalCount||
                x.ReviewTotalCount||x.ChapterReviewCount||0
            )||0;

            if(l.length||total>0||Number(d.code)===0||Number(d.Code)===0){
                return {
                    data:x,
                    list:l,
                    total:total||l.length,
                    source:ui===0?'www':'majax'
                };
            }
        }catch(e0){lastErr=e0;}
    }

    if(lastErr)throw lastErr;
    return {data:{},list:[],total:0,source:''};
}

function extractQuote(data,rawList){if(quoteText){quoteCard.textContent=quoteText;if(window._applyQ)window._applyQ();return;}data=data||{};var keys=['paragraph_text','paragraphText','ParagraphText','paragraph_content','paragraphContent','ParagraphContent','reference_content','ReferenceContent','RefferContent','chapter_name','chapterName','ChapterName','ChapterTitle'];for(var i=0;i<keys.length;i++){var v=data[keys[i]];if(v){quoteText=textOf(v);if(quoteText)break}}if(!quoteText&&rawList&&rawList.length){var r=(rawList[0]&&rawList[0].raw)||rawList[0]||{};var ks=['RefferContent','ReferContent','ReferenceContent','ParagraphContent','ParagraphText','ChapterName','ChapterTitle'];for(var j=0;j<ks.length;j++){if(r[ks[j]]){quoteText=textOf(r[ks[j]]);if(quoteText)break}}}if(quoteText){quoteCard.textContent=quoteText;if(window._applyQ)window._applyQ();else quoteWrap.classList.remove('hidden')}else if(!isAuthor){quoteCard.textContent=hasParagraph?'段落原文':'本章说';quoteWrap.classList.add('hidden')}}
function qfEnsureContext(){
    var now=String(bid)+"|"+String(cid)+"|"+String(para)+"|"+String(segment)+"|"+String(openType);
    if(window.__QF_ACTIVE_CONTEXT__===now)return;

    window.__QF_ACTIVE_CONTEXT__=now;

    page=1;
    ended=false;
    actual=0;
    seen={};
    allCache={};
    mediaEmptyKnown={image:false,audio:false};
    httpCache={};
    chapterAll=null;
    chapterState=null;
    mediaScanState=null;
    mediaScanToken++;
    allAudioReady=false;
    allAudioRows=[];
    allAudioById={};
    allAudioBySig={};
    allAudioPack=null;
    allAudioTotal=0;
    allAudioAddedLast=0;

    if(autoLoadTimer){
        try{clearTimeout(autoLoadTimer);}catch(e0){}
        autoLoadTimer=null;
    }
}
qfEnsureContext();

function qfMediaCountText(kind){
    var exact=kind==='image'?Number(totalImg):Number(totalAudio);
    if(exact>=0)return String(exact||0);
    var st=mediaScanState;
    if(st&&st.kind===kind&&Number(st.found||0)>0)return '≥'+String(Number(st.found||0));
    if(kind==='audio'&&Number(allAudioTotal||0)>0)return String(Number(allAudioTotal||0));
    return '';
}
function setCounts(){
    /* v4.0.0-alpha3.2：作者说模式会把普通评论 tabs 整块替换掉，
       nAll/nImg/nAudio 此时已经不存在。旧逻辑继续写 textContent 会直接抛异常，
       从而把已经拿到的作者说错误渲染成“评论加载失败”。 */
    if(isAuthor)return;
    var a=document.getElementById('nAll'),im=document.getElementById('nImg'),au=document.getElementById('nAudio');
    if(a)a.textContent=String(Number(totalAll||0));
    if(im)im.textContent=qfMediaCountText('image');
    if(au)au.textContent=qfMediaCountText('audio');
}
function reset(){
    page=1;
    ended=false;
    actual=0;
    seen={};
    audioDirectRows=[];
    audioDirectPack=null;
    audioRoleFilter='all';

    if(autoLoadTimer){
        try{clearTimeout(autoLoadTimer);}catch(e0){}
        autoLoadTimer=null;
    }
    autoLoadBudget=(currentTab==='all'&&currentSort==='default'&&!isAuthor)?2:0;

    mediaScanToken++;
    mediaScanState=null;

    if(isChapter)chapterState=null;

    listEl.innerHTML=
        '<div class="loading"><div class="spinner"></div><div>加载中...</div></div>';
    moreEl.classList.add('hidden');
}
function sortRows(a){a=a.slice();if(currentSort==='hot')a.sort(function(x,y){var ax=adapt(x),ay=adapt(y),d=ay.like-ax.like;if(d)return d;d=ay.replies-ax.replies;if(d)return d;return ay.time-ax.time});else if(currentSort==='latest')a.sort(function(x,y){return tsOf(y)-tsOf(x)});return a}
function allPages(action,tp){
    tp=tp==null?2:Number(tp);
    if(isNaN(tp))tp=2;

    var key=String(bid)+':'+String(cid)+':'+action+':seg='+String(segment)+':type='+tp;
    if(allCache[key])return allCache[key];

    var out=[],pg=1,guard=0,total=0;

    while(guard<80){
        guard++;

        var pk=fetchPack(action,pg,100,{type:tp});

        if(pg===1){
            total=Number(pk.total||0);
            extractQuote(pk.data,pk.list);
        }

        if(!pk.list.length)break;

        for(var i=0;i<pk.list.length;i++)out.push(pk.list[i]);

        /*
         * 起点接口可能限制单页实际条数。
         * total 没加载完时，不能用 list.length<100 判断结束。
         */
        if(total>0&&out.length>=total)break;

        pg++;
    }

    allCache[key]=out;
    return out;
}
function summarySegments(){
    var key='summarySegments:'+String(bid)+':'+String(cid);
    if(allCache[key])return allCache[key];

    var out=[],seen={};

    function add(seg,pid,cnt,hot){
        seg=Number(seg);
        pid=Number(pid);
        cnt=Number(cnt||0);

        if(isNaN(seg)&&pid>0)seg=pid;
        if(isNaN(pid)&&seg>0)pid=seg;

        if(!(seg>0)||!(cnt>0))return;

        var k=String(seg);
        var item={
            segmentId:seg,
            paragraphId:pid>0?pid:seg,
            count:cnt,
            hot:!!hot
        };

        if(!seen[k]||cnt>Number(seen[k].count||0)){
            seen[k]=item;
        }
    }

    /* 第一优先：正文页已成功解析的 segment */
    if(Array.isArray(chapterSeed)&&chapterSeed.length){
        for(var si=0;si<chapterSeed.length;si++){
            var z=chapterSeed[si]||{};
            add(z.segmentId,z.paragraphId,z.count,z.hot);
        }
    }

    /* 没 seed 才重新请求官方 summary */
    if(!Object.keys(seen).length){
        var urls=[
            'https://m.qidian.com/majax/chapterReview/reviewSummary?bookId='+
              encodeURIComponent(bid)+'&chapterId='+encodeURIComponent(cid)+
              (csrf?'&_csrfToken='+encodeURIComponent(csrf):''),
            'https://www.qidian.com/ajax/chapterReview/reviewSummary?bookId='+
              encodeURIComponent(bid)+'&chapterId='+encodeURIComponent(cid)+
              (csrf?'&_csrfToken='+encodeURIComponent(csrf):'')
        ];

        for(var ui=0;ui<urls.length;ui++){
            try{
                var d=parse(http(urls[ui]));
                var x=d&&(d.data||d.Data||d)||{};
                var a=x.list||x.List||[];

                if(!Array.isArray(a))a=[];

                for(var i=0;i<a.length;i++){
                    var it=a[i]||{};

                    var sg=Number(
                        it.segmentId!==undefined?it.segmentId:
                        it.SegmentId!==undefined?it.SegmentId:
                        NaN
                    );

                    var pid=Number(
                        it.paragraphId!==undefined?it.paragraphId:
                        it.ParagraphId!==undefined?it.ParagraphId:
                        NaN
                    );

                    var n=Number(
                        it.reviewNum!==undefined?it.reviewNum:
                        it.ReviewNum!==undefined?it.ReviewNum:
                        it.textCount!==undefined?it.textCount:
                        it.TextCount!==undefined?it.TextCount:
                        it.reviewCount!==undefined?it.reviewCount:
                        it.ReviewCount!==undefined?it.ReviewCount:
                        0
                    );

                    add(
                        sg,pid,n,
                        it.isHotSegment===true||
                        it.IsHotSegment===true||
                        Number(it.isHotSegment||it.IsHotSegment||0)===1
                    );
                }
            }catch(e){}

            if(Object.keys(seen).length)break;
        }
    }

    for(var k in seen){
        if(Object.prototype.hasOwnProperty.call(seen,k))out.push(seen[k]);
    }

    /*
     * 热门/评论多的段先取，能更快填充本章说首屏。
     */
    out.sort(function(a,b){
        if(a.hot!==b.hot)return a.hot?-1:1;
        var d=Number(b.count)-Number(a.count);
        return d||Number(a.segmentId)-Number(b.segmentId);
    });

    allCache[key]=out;
    return out;
}
function chapterAllPages(){
    /* 兼容旧调用：只分批拿，不再一次性阻塞完整章。 */
    var out=[],guard=0;
    while(guard<8){
        guard++;
        var p=chapterNextBatch(40,5);
        for(var i=0;i<p.rows.length;i++)out.push(p.rows[i]);
        if(p.done)break;
    }
    return out;
}

function chapterInitState(){
    if(chapterState)return chapterState;

    var segs=summarySegments(),list=[],sum=0;

    for(var i=0;i<segs.length;i++){
        var x=segs[i]||{};
        var sg=Number(x.segmentId);
        var cnt=Number(x.count||0);

        if(!(sg>0)||!(cnt>0))continue;

        list.push({
            segmentId:sg,
            paragraphId:Number(x.paragraphId)>0?Number(x.paragraphId):sg,
            expected:cnt,
            page:1,
            loaded:0,
            done:false
        });
        sum+=cnt;
    }

    chapterState={
        segments:list,
        cursor:0,
        total:sum,
        seen:{},
        done:list.length===0
    };

    if(sum>0)totalAll=sum;

    return chapterState;
}

function chapterNextBatch(limit,maxRequests){
    var st=chapterInitState();
    var rows=[],requests=0;

    limit=Math.max(1,Number(limit)||20);
    maxRequests=Math.max(1,Number(maxRequests)||4);

    if(st.done){
        return {rows:[],total:st.total,done:true};
    }

    while(rows.length<limit&&requests<maxRequests&&!st.done){
        var n=st.segments.length;
        if(!n){
            st.done=true;
            break;
        }

        var found=-1;

        for(var step=0;step<n;step++){
            var ix=(st.cursor+step)%n;
            if(!st.segments[ix].done){
                found=ix;
                break;
            }
        }

        if(found<0){
            st.done=true;
            break;
        }

        var it=st.segments[found];
        st.cursor=(found+1)%n;
        requests++;

        var saveSeg=segment,pk=null;

        try{
            segment=Number(it.segmentId);

            pk=fetchPack(
                'reviewList',
                it.page,
                pageSize,
                {type:2,paragraphId:it.paragraphId}
            );
        }catch(e0){
            pk={list:[],total:0,data:{}};
        }

        segment=saveSeg;

        var src=(pk&&pk.list)||[];
        var packTotal=Number(pk&&pk.total||0);

        if(!src.length){
            it.done=true;
            continue;
        }

        it.loaded+=src.length;
        it.page++;

        for(var r=0;r<src.length&&rows.length<limit;r++){
            var raw=src[r]||{};
            var c=adapt(raw);

            var id=c.id||(
                String(c.name||'')+'|'+
                String(c.content||'')+'|'+
                String(c.time||'')
            );

            if(st.seen[id])continue;

            st.seen[id]=1;
            rows.push(raw);
        }

        var expected=packTotal>0?packTotal:Number(it.expected||0);

        if(expected>0&&it.loaded>=expected){
            it.done=true;
        }

        /*
         * 不用 src.length<pageSize 判结束：
         * 真机常见请求20，实际只返回10。
         */
    }

    var alive=false;
    for(var q=0;q<st.segments.length;q++){
        if(!st.segments[q].done){
            alive=true;
            break;
        }
    }

    st.done=!alive;

    rows.sort(function(a,b){
        return tsOf(b)-tsOf(a);
    });

    return {
        rows:rows,
        total:st.total||rows.length,
        done:st.done
    };
}
function mediaAmount(a,kind){var n=0;for(var i=0;i<a.length;i++){var c=adapt(a[i]);if(kind==='image'&&c.image)n++;if(kind==='audio'&&c.audio)n++}return n}
function ensureMediaAll(kind){
    if(mediaScanState&&mediaScanState.kind===kind){
        return mediaScanState.rows||[];
    }
    return [];
}

function typedMediaUrl(host,p,ps,tp,pid){
    var q=[
        'bookId='+encodeURIComponent(bid),
        'chapterId='+encodeURIComponent(cid),
        'page='+encodeURIComponent(p||1),
        'pageSize='+encodeURIComponent(ps||20),
        'segmentId='+encodeURIComponent(Number(segment)||0),
        'paragraphId='+encodeURIComponent(Number(pid)),
        'type='+encodeURIComponent(Number(tp)||0),
        'roleId=0',
        'role_id=0'
    ];
    if(csrf)q.push('_csrfToken='+encodeURIComponent(csrf));
    return host+q.join('&');
}

function fetchMediaPack(kind,p,ps,tp,pid){
    /* beta16.2：媒体“无结果”必须快停。正常评论请求仍保留10s容错，
     * 只有配图/配音探测使用约2.1s短超时；主端点返回合法空数据就直接认定
     * 本次候选为空，不再 PC+移动端串行各等一次。 */
    if(Number(tp)===-1){
        try{
            var gu=url('reviewList',p,ps,{type:2,paragraphId:pid});
            var gd=parse(qfMediaHttp(gu,2100));
            if(gd){
                var gx=gd.data||gd.Data||gd,gl=arr(gx),gt=Number(gx.total||gx.Total||gx.totalCount||gx.TotalCount||0)||0;
                return {data:gx,list:gl,total:gt||gl.length,source:'www-fast-fallback'};
            }
        }catch(_gf){}
        return {data:{},list:[],total:0,source:''};
    }

    var it=Number(tp);
    var primary=typedMediaUrl('https://www.qidian.com/ajax/chapterReview/reviewList?',p,ps,it,pid);
    try{
        var d=parse(qfMediaHttp(primary,2100));
        if(d){
            var x=d.data||d.Data||d,lst=arr(x),total=Number(x.total||x.Total||x.totalCount||x.TotalCount||0)||0;
            /* 合法 JSON 即结束这一请求：空就是空，不再为了证明“没有”再等移动端。 */
            return {data:x,list:lst,total:total||lst.length,source:kind==='image'?'www-image-fast':'www-media-fast'};
        }
    }catch(_p){}

    /* 只有主端点本身失败/非JSON才给一次移动端短兜底。 */
    var mobile=typedMediaUrl('https://m.qidian.com/majax/chapterReview/reviewList?',p,ps,it,pid);
    try{
        var md=parse(qfMediaHttp(mobile,1800));
        if(md){
            var mx=md.data||md.Data||md,ml=arr(mx),mt=Number(mx.total||mx.Total||mx.totalCount||mx.TotalCount||0)||0;
            return {data:mx,list:ml,total:mt||ml.length,source:kind==='image'?'m-image-fast':'m-media-fast'};
        }
    }catch(_m){}
    return {data:{},list:[],total:0,source:''};
}
function officialReviewDetailUrl(reviewId){
    return 'https://h5.if.qidian.com/new/chapterreview/?bookid='+
        encodeURIComponent(bid)+
        '&chapterid='+encodeURIComponent(cid)+
        '&reviewid='+encodeURIComponent(String(reviewId||''))+
        '&_qfdetail=1';
}

function decodeDetailHtml(s){
    s=String(s||'');
    return s
        .replace(/\\u002F/gi,'/')
        .replace(/\\u003A/gi,':')
        .replace(/\\u0026/gi,'&')
        .replace(/\\\//g,'/')
        .replace(/&amp;/g,'&');
}

function audioUrlFromDetail(html){
    html=decodeDetailHtml(html);

    var patterns=[
        /https?:\/\/[^"'<>\\\s]+?\.(?:mp3|m4a|aac|wav|ogg|amr|opus|flac|m3u8)(?:\?[^"'<>\\\s]*)?/i,
        /(?:audioUrl|voiceUrl|playUrl|audio_url|voice_url|play_url|soundUrl|recordUrl)["']?\s*[:=]\s*["']((?:https?:)?\/\/[^"'<>\\\s]+)["']/i,
        /(?:audio|voice|sound|record|dub)[^{}]{0,100}(?:url|src|path)["']?\s*[:=]\s*["']((?:https?:)?\/\/[^"'<>\\\s]+)["']/i,
        /["']((?:https?:)?\/\/[^"']+?)["'][^{}]{0,100}(?:audio|voice|sound|record|dub)/i
    ];

    for(var i=0;i<patterns.length;i++){
        var m=html.match(patterns[i]);
        var u='';

        if(m){
            u=String(m[1]||m[0]||'');
            if(/^\/\//.test(u))u='https:'+u;

            if(
                /^https?:\/\//i.test(u)&&
                !/h5\.if\.qidian\.com\/new\/chapterreview/i.test(u)&&
                !/\.(?:js|css|png|jpe?g|gif|webp|svg)(?:[?#]|$)/i.test(u)
            ){
                return u;
            }
        }
    }

    return '';
}
function audioUrlFromPayloadText(text){
    text=String(text||'').trim();
    if(!text)return '';

    var u=audioUrlFromDetail(text);
    if(u)return u;

    if(
        (text.charAt(0)==='{'&&text.charAt(text.length-1)==='}')||
        (text.charAt(0)==='['&&text.charAt(text.length-1)===']')
    ){
        try{
            var obj=JSON.parse(text);
            return audioOf(obj)||'';
        }catch(_e){}
    }

    return '';
}

function isAudioDetailHtml(html){
    html=decodeDetailHtml(html);

    /*
     * Avoid matching generic bundle words "audio/voice".
     * These visible/share-title signatures correspond to an actual dubbing review.
     */
    return (
        /发布了[^<]{0,50}(?:旁白|角色)?的?配音/i.test(html)||
        /<title[^>]*>[^<]{0,100}配音[^<]*<\/title>/i.test(html)||
        /["'](?:shareTitle|title)["']\s*:\s*["'][^"']{0,100}配音/i.test(html)||
        /旁白[^<]{0,30}配音/i.test(html)
    );
}

function rawAudioHint(raw){
    raw=raw||{};
    var seen=[];

    function strongScalar(k,v,path){
        k=String(k||'');
        path=String(path||'');

        if(/^_qf/i.test(k)||/(?:^|\.|\[)_qf/i.test(path))return false;

        var keyAudio=/(audio|voice|sound|record|dub|dubbing|speech|listen)/i.test(k);
        var parentAudio=/(audio|voice|sound|record|dub|dubbing|speech|listen)/i.test(path);

        if(!keyAudio&&!parentAudio)return false;

        if(typeof v==='string'){
            var s=String(v).trim();
            if(!s)return false;
            if(/^\/\//.test(s))s='https:'+s;

            if(
                /^(?:https?:|data:audio)/i.test(s)&&
                !/h5\.if\.qidian\.com\/new\/chapterreview/i.test(s)&&
                (
                    /\.(?:mp3|m4a|aac|wav|ogg|amr|opus|flac|m3u8)(?:[?#]|$)/i.test(s)||
                    /(url|src|path|file|play)/i.test(k)
                )
            ){
                return true;
            }

            return false;
        }

        if(typeof v==='number'){
            return (
                /(duration|length|seconds|ms|millisecond|audioid|voiceid|soundid|recordid)/i.test(k)&&
                Number(v)>0
            );
        }

        if(typeof v==='boolean'){
            return keyAudio&&v===true;
        }

        return false;
    }

    function walk(v,path,d){
        if(v==null||d>7)return false;
        if(/(?:^|\.|\[)_qf/i.test(String(path||'')))return false;

        if(Array.isArray(v)){
            for(var i=0;i<v.length;i++){
                if(walk(v[i],path+'['+i+']',d+1))return true;
            }
            return false;
        }

        if(typeof v!=='object')return false;
        if(seen.indexOf(v)>=0)return false;
        seen.push(v);

        for(var k in v){
            if(!Object.prototype.hasOwnProperty.call(v,k))continue;
            if(/^_qf/i.test(String(k)))continue;

            var x=v[k];
            var kp=path?path+'.'+k:k;

            if(strongScalar(k,x,path))return true;

            if(
                x&&typeof x==='object'&&!Array.isArray(x)&&
                /(audio|voice|sound|record|dub|dubbing|speech|listen)/i.test(String(k))
            ){
                for(var sk in x){
                    if(!Object.prototype.hasOwnProperty.call(x,sk))continue;
                    if(/^_qf/i.test(String(sk)))continue;

                    var sv=x[sk];
                    if(
                        /(url|src|path|file|play|id|duration|length|seconds|ms)/i.test(String(sk))&&
                        sv!==null&&sv!==''&&sv!==0&&sv!==false
                    ){
                        return true;
                    }
                }
            }

            if(walk(x,kp,d+1))return true;
        }

        return false;
    }

    return walk(raw,'',0);
}
function probeAudioDetail(raw,st){
    raw=raw||{};
    var c=adapt(raw);
    var id=String(c.id||'');
    if(!id)return false;

    if(!st.detailSeen)st.detailSeen={};
    if(st.detailSeen[id])return !!raw._qfAudioVerified;
    st.detailSeen[id]=1;

    if(Number(st.detailBudget||0)<=0)return false;
    st.detailBudget--;

    if(!raw._qfAudioDiag)raw._qfAudioDiag=rawAudioDiag(raw);

    try{
        var apiState={
            reviewId:id,
            directSrc:'',
            resolvedSrc:'',
            apiSource:''
        };
        var apiUrl=qfAudioResolveReviewApis(apiState);

        if(apiUrl){
            raw._qfAudioVerified=true;
            raw._qfAudioDetected=true;
            raw._qfAudioUrl=apiUrl;
            raw._qfAudioPath='officialReviewApi'+
                (apiState.apiSource?'.'+apiState.apiSource:'');
            raw._qfAudioPage=officialReviewDetailUrl(id);
            return true;
        }
    }catch(e0){}

    var u=officialReviewDetailUrl(id);
    var html='';

    try{html=http(u);}catch(e1){html='';}
    if(!html)return false;

    var au=audioUrlFromDetail(html);
    if(!au)return false;

    raw._qfAudioVerified=true;
    raw._qfAudioDetected=true;
    raw._qfAudioPage=u;
    raw._qfAudioUrl=au;
    raw._qfAudioPath='officialReviewDetail.media';

    try{
        var dm=html.match(
            /(?:audioDuration|voiceDuration|soundDuration|recordDuration|playDuration)["']?\s*[:=]\s*["']?(\d+(?:\.\d+)?)/i
        );

        if(dm&&dm[1]){
            var dn=Number(dm[1]);
            if(dn>1000)dn=dn/1000;
            dn=saneAudioDuration(dn);
            if(dn)raw._qfAudioDuration=dn;
        }
    }catch(_de){}

    return true;
}
function probeAudioRows(rows,st){
    if(!rows||!rows.length||!st)return [];

    var out=[],picked={},maxProbe=2;

    function addVerified(raw){
        if(!raw)return false;

        var c=adapt(raw);
        var direct=String(c.audio||'');

        if(
            direct&&
            !/h5\.if\.qidian\.com\/new\/chapterreview/i.test(direct)
        ){
            raw._qfAudioVerified=true;
            raw._qfAudioDetected=true;

            if(c.id&&!raw._qfAudioPage){
                raw._qfAudioPage=officialReviewDetailUrl(c.id);
            }

            out.push(raw);
            return true;
        }

        if(probeAudioDetail(raw,st)){
            out.push(raw);
            return true;
        }

        return false;
    }

    for(var i=0;i<rows.length&&out.length<maxProbe;i++){
        if(rawAudioHint(rows[i])){
            picked[i]=1;
            addVerified(rows[i]);
        }
    }

    if(st.currentType!==-1){
        var tried=Object.keys(picked).length;

        for(var j=0;j<rows.length&&tried<maxProbe;j++){
            if(picked[j])continue;

            picked[j]=1;
            tried++;

            /*
             * 可以检查，但绝不因为它来自“type接口”就判定为配音。
             */
            addVerified(rows[j]);
        }
    }

    return out;
}
function mediaTargets(){
    return [{
        segmentId:isChapter?0:(Number(segment)||0),
        paragraphId:isChapter?-1:Number(para),
        expected:Number(expectedCount||totalAll||0)
    }];
}
function qfRememberLoadedAllV317(rows){
    if(!Array.isArray(rows)||!rows.length)return;
    for(var i=0;i<rows.length;i++){
        var r=rows[i]||{},c=adapt(r);
        if(c.image)mediaEmptyKnown.image=false;
        if(c.audio||c.audioPage)mediaEmptyKnown.audio=false;
        var k=String(c.id||'');
        if(!k)k=String(c.name||'')+'|'+String(c.content||'')+'|'+String(c.time||'');
        if(loadedAllSeen[k])continue;
        loadedAllSeen[k]=1;
        loadedAllRaw.push(r);
        /* 弹窗生命周期内只保留最近约180条，足够覆盖用户已经看过/预取的评论。 */
        if(loadedAllRaw.length>180)loadedAllRaw.shift();
    }
}
function qfLoadedMediaSeedV313(kind){
    var out=[],seenSeed={};
    function take(a){
        if(!Array.isArray(a))return;
        for(var i=0;i<a.length;i++){
            var r=a[i]||{},c=adapt(r),ok=kind==='image'?!!c.image:!!(c.audio||c.audioPage);
            if(!ok)continue;
            var k=String(c.id||'')+'|'+String(kind==='image'?c.image:(c.audio||c.audioPage||''));
            if(seenSeed[k])continue;seenSeed[k]=1;out.push(r);
        }
    }
    try{take(loadedAllRaw);}catch(_l){}
    try{if(Array.isArray(chapterAll))take(chapterAll);}catch(_c){}
    try{for(var k in allCache)if(Object.prototype.hasOwnProperty.call(allCache,k))take(allCache[k]);}catch(_a){}
    return out;
}
function qfImageMediaCardV313(c){
    c=c||{};
    var av=avHtml(c,false),meta=[];
    if(c.timeText)meta.push(c.timeText);else if(c.time)meta.push(timeText(c.time));
    if(c.ip)meta.push(c.ip);
    var txt=String(c.content||'').trim();
    if(txt.length>140)txt=txt.slice(0,140)+'…';
    return '<div class="imageCard comment" data-id="'+esc(c.id||'')+'">'+
        '<div class="imageHead">'+av+'<div class="imageWho"><div class="name">'+esc(c.name||'书友')+'</div><div class="meta">'+esc(meta.join(' · '))+'</div></div>'+
        (Number(c.like||0)>0?'<div class="imageLike">♡ '+esc(String(c.like))+'</div>':'')+'</div>'+
        '<div class="imageStage"><img class="imageHero zoom" src="'+esc(c.image||'')+'" referrerpolicy="no-referrer" loading="lazy" decoding="async"></div>'+
        (txt?'<div class="imageCaption">'+fmt(txt)+'</div>':'')+
        '</div>';
}
function renderMediaRows(rows,kind){
    if(!rows||!rows.length)return 0;

    var out=[],h='';

    for(var i=0;i<rows.length;i++){
        var rawRow=rows[i]||{};

        if(kind==='audio'&&!rawRow._qfAudioDiag){
            rawRow._qfAudioDiag=rawAudioDiag(rawRow);
        }

        var c=adapt(rawRow);

        if(
            c.audio&&
            /h5\.if\.qidian\.com\/new\/chapterreview/i.test(String(c.audio))
        ){
            rawRow._qfAudioUrl='';
            c.audio='';
        }

        if(
            kind==='audio'&&
            c.audio&&
            !rawRow._qfAudioVerified
        ){
            rawRow._qfAudioVerified=true;
            rawRow._qfAudioDetected=true;

            if(c.id&&!rawRow._qfAudioPage){
                rawRow._qfAudioPage=officialReviewDetailUrl(c.id);
            }

            c=adapt(rawRow);
        }

        var id=c.id||(
            String(c.name||'')+'|'+
            String(c.content||'')+'|'+
            String(c.time||'')
        );

        if(mediaScanState.seen[id])continue;

        var ok=false;

        if(kind==='image'){
            ok=!!c.image;
        }else{
            ok=!!(
                rawRow._qfAudioVerified&&
                c.audio&&
                !/h5\.if\.qidian\.com\/new\/chapterreview/i.test(String(c.audio))
            );
        }

        if(!ok)continue;

        mediaScanState.seen[id]=1;
        out.push(c);
    }

    if(!out.length)return 0;

    if(!mediaScanState.rendered){
        listEl.innerHTML='';
        mediaScanState.rendered=true;
    }

    for(var j=0;j<out.length;j++){
        h+=(kind==='image'?qfImageMediaCardV313(out[j]):commentHtml(out[j]));
    }

    listEl.insertAdjacentHTML('beforeend',h);

    return out.length;
}


/* ============================================================
 * v4.0 Stage 2 · 起点官方配图专用接口
 * APK: /argus/api/v1/chapterreview/getparagraphsallimgreviews
 * ============================================================ */
function qfDirectImageCountV402(root){
    var best=0,seen=[];
    function walk(v,d){
        if(v==null||d>7)return;
        if(Array.isArray(v)){for(var i=0;i<v.length;i++)walk(v[i],d+1);return;}
        if(typeof v!=='object'||seen.indexOf(v)>=0)return;seen.push(v);
        var n=Number(v.ImageCount||v.imageCount||v.TotalCount||v.totalCount||v.Total||v.total||0)||0;if(n>best)best=n;
        for(var k in v)if(Object.prototype.hasOwnProperty.call(v,k))walk(v[k],d+1);
    }
    walk(root,0);return best;
}
function qfDirectImageRowsV402(root){
    var out=[],seenObj=[],seenKey={};
    function add(x,path){
        if(!x||typeof x!=='object')return;
        var im='';try{im=String(imgOf(x)||'');}catch(_i){im='';}
        if(!im)return;
        var id=String(x.ReviewId||x.reviewId||x.CommentId||x.commentId||x.Id||x.id||'');
        var content=String(x.Content||x.content||x.ReviewContent||x.reviewContent||x.Text||x.text||'');
        var user=x.UserInfo||x.userInfo||x.User||x.user||{};
        var name=String(x.UserName||x.userName||user.UserName||user.userName||user.NickName||user.nickName||'');
        /* 避免把仅包含头像/勋章的外层 wrapper 当成配图评论。 */
        if(!id&&!content&&!name)return;
        var key=id?('id:'+id):('img:'+im+'|'+content.slice(0,80));if(seenKey[key])return;seenKey[key]=1;
        var y=x;try{y=JSON.parse(JSON.stringify(x));}catch(_e){}
        if(!y.ImageDetail&&!y.imageDetail)y.ImageDetail=im;
        y._qfImageVerified=true;y._qfImagePath=String(path||'root');out.push(y);
    }
    function walk(v,path,d){
        if(v==null||d>9)return;
        if(Array.isArray(v)){for(var i=0;i<v.length;i++)walk(v[i],path+'['+i+']',d+1);return;}
        if(typeof v!=='object'||seenObj.indexOf(v)>=0)return;seenObj.push(v);add(v,path);
        for(var k in v)if(Object.prototype.hasOwnProperty.call(v,k)&&v[k]&&typeof v[k]==='object')walk(v[k],path?path+'.'+k:k,d+1);
    }
    walk(root,'root',0);return out;
}
function qfTryDirectOfficialImageV402(page,size){
    var params={bookId:String(bid),chapterId:String(cid),paragraphId:String(para),pg:String(Math.max(1,Number(page)||1)),pz:String(Math.max(1,Number(size)||20))};
    var attempts=[];
    try{var a=qfDirectSignedRequest('v1/chapterreview/getparagraphsallimgreviews',params,false);attempts.push({name:'app-v1-image',url:a.url,headers:a.headers});}catch(_a){}
    try{var b=qfReaderSignedRequestV3245('v1/chapterreview/getparagraphsallimgreviews',params,'reader_legacy');attempts.push({name:'reader-image',url:b.url,headers:b.headers});}catch(_b){}
    var hadValid=false;
    for(var i=0;i<attempts.length;i++){
        try{
            var text=qfDirectAjax(attempts[i].url,'GET',null,null,attempts[i].headers,1800),d=parse(text);if(!d)continue;
            var code=(d.Code!==undefined?d.Code:(d.code!==undefined?d.code:(d.Status!==undefined?d.Status:d.status)));
            var hasCode=!(code===undefined||code===null||code==='');var valid=hasCode?(Number(code)===0||Number(code)===200):(d.Data!==undefined||d.data!==undefined||typeof d==='object');if(!valid)continue;
            hadValid=true;
            var rows=qfDirectImageRowsV402(d),count=qfDirectImageCountV402(d);
            if(rows.length)return {ok:true,confirmedEmpty:false,list:rows,total:count||rows.length,root:d,name:attempts[i].name};
            if(count>0)return {ok:false,partial:true,confirmedEmpty:false,list:[],total:count,root:d,name:attempts[i].name};
            /* 合法成功 + 0 = 官方明确无配图，不再换普通 reviewList 证明。 */
            return {ok:false,partial:false,confirmedEmpty:true,list:[],total:0,root:d,name:attempts[i].name};
        }catch(_e){}
    }
    return {ok:false,partial:false,confirmedEmpty:false,responded:hadValid,list:[],total:0,root:null,name:''};
}
function qfStartImageDirectProbeV402(token){
    var st=mediaScanState;if(!st||st.token!==token||currentTab!=='image')return;
    var pack=null;try{pack=qfTryDirectOfficialImageV402(1,20);}catch(_e){pack=null;}
    if(pack&&pack.ok&&pack.list&&pack.list.length){
        st.done=true;ended=true;st.found=Number(pack.total||pack.list.length);st.rendered=false;st.typeFound=true;
        qfMediaEmptyDropV403('image');totalImg=st.found;setCounts();renderMediaRows(pack.list,'image');finishMediaScan(st);return;
    }
    if(pack&&pack.confirmedEmpty){qfMediaEmptyPutV403('image');totalImg=0;st.found=0;finishMediaScan(st);return;}
    /* 专用接口传输/兼容异常时只允许旧链做 1 次短请求兜底，不再多 type/多页扫描。 */
    st.maxRequests=1;st.maxMs=2200;mediaScanStep(token);
}

/* ============================================================
 * 起点官方配音 WebView 本地签名直连
 * upstream: /argus/api/v1/chapterreview/getparagraphsaudiocomments
 * ============================================================ */
var QF_AUDIO_DIRECT_API=
    'https://druidv6.if.qidian.com/argus/api/v1/chapterreview/getparagraphsaudiocomments';

function qfDirectNormAudioUrl(u){
    u=String(u||'').trim();
    if(!u)return '';

    if(/^\/\//.test(u))u='https:'+u;

    if(
        !/^https?:\/\//i.test(u)&&
        /^[a-z0-9.-]+\.(?:com|cn|net)\/.+/i.test(u)
    ){
        u='https://'+u;
    }

    if(
        /^https?:\/\//i.test(u)&&
        /\.(?:m4a|mp3|aac|wav|ogg|amr|opus|flac)(?:[?#]|$)/i.test(u)
    ){
        return u;
    }

    return '';
}

function qfDirectAudioCount(root){
    var best=0,seen=[];

    function walk(v,d){
        if(v==null||d>7)return;

        if(Array.isArray(v)){
            for(var i=0;i<v.length;i++)walk(v[i],d+1);
            return;
        }

        if(typeof v!=='object')return;
        if(seen.indexOf(v)>=0)return;
        seen.push(v);

        var n=Number(
            v.AudioCount||v.audioCount||
            v.TotalCount||v.totalCount||
            v.Total||v.total||0
        )||0;

        if(n>best)best=n;

        for(var k in v){
            if(Object.prototype.hasOwnProperty.call(v,k)){
                walk(v[k],d+1);
            }
        }
    }

    walk(root,0);
    return best;
}

function qfDirectAudioRows(root){
    var out=[],seenObj=[],seenId={};

    function mapUser(x){
        var u=
            x.UserInfo||x.userInfo||
            x.User||x.user||
            x.UserInfoV2||{};

        return u||{};
    }

    function add(x,path){
        if(!x||typeof x!=='object')return;

        var au=qfDirectNormAudioUrl(
            x.AudioUrl||x.audioUrl||
            x.audio_url||
            x.VoiceUrl||x.voiceUrl||
            x.voice_url||''
        );

        if(!au)return;

        var id=String(
            x.Id||x.id||
            x.CommentId||x.commentId||
            x.ReviewId||x.reviewId||
            ''
        );

        var key=id||(
            au+'|'+String(x.Content||x.content||'')
        );

        if(seenId[key])return;
        seenId[key]=1;

        var y=x;

        try{
            y=JSON.parse(JSON.stringify(x));
        }catch(_e){}

        /*
         * Preserve original upstream fields while adding aliases expected by
         * the existing comment UI.
         */
        y._qfAudioVerified=true;
        y._qfAudioDetected=true;
        y._qfAudioUrl=au;
        y._qfAudioPath=path+'.AudioUrl';

        if(id&&!y.Id)y.Id=id;

        if(y.Content==null&&y.content!=null){
            y.Content=y.content;
        }

        if(y.ParagraphId==null){
            y.ParagraphId=Number(
                y.paragraphId||
                y.paragraph_id||
                para||0
            )||0;
        }

        var ui=mapUser(y);
        if(ui&&typeof ui==='object'){
            if(!y.UserInfo)y.UserInfo=ui;
        }

        var at=Number(
            y.AudioTime||y.audioTime||
            y.AudioDuration||y.audioDuration||
            y.VoiceTime||y.voiceTime||0
        )||0;

        if(at>1000)at=at/1000;
        if(at>=1.5&&at<36000){
            y._qfAudioDuration=at;
        }

        if(y.AudioRoleInfo){
            y._qfAudioRoleInfo=y.AudioRoleInfo;
        }

        if(y.AudioRoleId!=null){
            y._qfAudioRoleId=y.AudioRoleId;
        }

        if(id){
            y._qfAudioPage=officialReviewDetailUrl(id);
        }

        out.push(y);
    }

    function walk(v,path,d){
        if(v==null||d>9)return;

        if(Array.isArray(v)){
            for(var i=0;i<v.length;i++){
                walk(v[i],path+'['+i+']',d+1);
            }
            return;
        }

        if(typeof v!=='object')return;
        if(seenObj.indexOf(v)>=0)return;
        seenObj.push(v);

        if(
            v.AudioUrl||v.audioUrl||v.audio_url||
            v.VoiceUrl||v.voiceUrl||v.voice_url
        ){
            add(v,path||'root');
        }

        for(var k in v){
            if(Object.prototype.hasOwnProperty.call(v,k)){
                walk(v[k],path?path+'.'+k:k,d+1);
            }
        }
    }

    walk(root,'',0);
    return out;
}

function qfDirectRoles(root){
    return qfAudioFindRoles(root)||[];
}

var QF_QD_AUDIO_SIGN_KEY='{1dYgqE)h9,R)hKqEcv4]k[h';
var QF_QD_AUDIO_INFO_KEY='0821CAAD409B84020821CAAD';
var QF_QD_AUDIO_SIGN_IV='01234567';
var QF_QD_AUDIO_INFO_IV='\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000';

function qfDirectBridgeCaps(){
    var j=null;
    try{j=window.java||null;}catch(e0){}
    var cookieLen=0;
    try{cookieLen=String(document.cookie||'').length;}catch(e1){}
    return {
        ajax:!!(j&&typeof j.ajax==='function'),
        md5:!!(j&&typeof j.md5Encode==='function'),
        des3:!!(j&&typeof j.tripleDESEncodeBase64Str==='function'),
        cookieLen:cookieLen
    };
}

function qfDirectMd5(v){
    var j=null;
    try{j=window.java||null;}catch(e0){}
    if(j&&typeof j.md5Encode==='function'){
        return String(j.md5Encode(String(v))||'');
    }
    throw new Error('WebView java bridge 无 md5Encode');
}

function qfDirectTripleDesBase64(text,key,iv){
    var j=null;
    try{j=window.java||null;}catch(e0){}
    if(j&&typeof j.tripleDESEncodeBase64Str==='function'){
        return String(
            j.tripleDESEncodeBase64Str(
                String(text||''),
                String(key||''),
                'CBC',
                'PKCS5Padding',
                String(iv||'')
            )||''
        ).replace(/[\r\n]/g,'');
    }
    throw new Error('WebView java bridge 无 tripleDESEncodeBase64Str');
}

function qfDirectRandomHex(length){
    length=Number(length||16);
    var hex='0123456789abcdef',out='';
    try{
        if(window.crypto&&typeof window.crypto.getRandomValues==='function'){
            var bytes=new Uint8Array(Math.ceil(length/2));
            window.crypto.getRandomValues(bytes);
            for(var i=0;i<bytes.length;i++){
                var h=Number(bytes[i]).toString(16);
                if(h.length<2)h='0'+h;
                out+=h;
            }
            return out.slice(0,length);
        }
    }catch(e0){}
    while(out.length<length){
        out+=hex.charAt(Math.floor(Math.random()*16));
    }
    return out.slice(0,length);
}

function qfDirectDeviceId(){
    var key='qf_qd_audio_device_id_v2922';
    var id='';
    try{id=String(window.localStorage.getItem(key)||'');}catch(e0){}
    if(!id){
        try{id=String(window.__qfAudioDeviceId||'');}catch(e1){}
    }
    if(!/^[0-9a-f]{16}$/i.test(id))id=qfDirectRandomHex(16).toLowerCase();
    try{window.localStorage.setItem(key,id);}catch(e2){}
    try{window.__qfAudioDeviceId=id;}catch(e3){}
    return id;
}

function qfDirectSignedRequest(path,params,withCookie){
    params=params||{};
    var keys=Object.keys(params).sort();
    var parts=[];
    for(var i=0;i<keys.length;i++){
        var k=keys[i];
        parts.push(k+'='+String(params[k]==null?'':params[k]));
    }
    var a=parts.join('&');
    var t=Date.now();
    var signPlain='Rv1rPTnczce|'+t+'||||||'+qfDirectMd5(String(a).toLowerCase());
    var qdSign=qfDirectTripleDesBase64(signPlain,QF_QD_AUDIO_SIGN_KEY,QF_QD_AUDIO_SIGN_IV);
    var deviceId=qfDirectDeviceId();
    var infoPlain=deviceId+'||||||1||999|'+t;
    var qdInfo=qfDirectTripleDesBase64(infoPlain,QF_QD_AUDIO_INFO_KEY,QF_QD_AUDIO_INFO_IV);
    var headers={
        'QDSign':qdSign,
        'QDInfo':qdInfo,
        'tstamp':String(t)
    };
    if(withCookie){
        try{
            var ck=String(document.cookie||'');
            if(ck)headers.Cookie=ck;
        }catch(e0){}
    }
    return {
        url:'https://druidv6.if.qidian.com/argus/api/'+String(path||'').replace(/^\/+/, '')+'?'+a,
        headers:headers,
        deviceId:deviceId,
        timestamp:t
    };
}

/* beta24.5：段评富标签必须按起点 Android Reader 客户端身份请求。
 * 起点助手同一 v2/getparagraphscomments 的返回行直接带 TitleInfoList；
 * 旧的简化 QDInfo/Chrome UA 虽能拿到评论正文，但服务端可能省略用户身份/称号字段。
 * 这里只影响段评 type=0 富数据通道，不改配音、正文和其它 Argus 请求。 */
function qfReaderSignedRequestV3245(path,params,profile){
    /* v4.0 browser-side Official Review Client profile。旧名保留以避免 UI ABI 变化。 */
    params=params||{};profile=String(profile||'reader_ext');
    var parts=[],keys=Object.keys(params||{});
    for(var i=0;i<keys.length;i++){
        var k=keys[i];if(params[k]===undefined)continue;
        parts.push(k+'='+String(params[k]==null?'':params[k]));
    }
    parts.sort();
    var a=parts.join('&'),t=Date.now(),deviceId=qfDirectDeviceId();
    var queryMd5=qfDirectMd5(String(a).toLowerCase());
    /* Reader 兼容签名：客户端槽位固定 0，deviceId 位于下一槽。 */
    var signPlain='Rv1rPTnczce|'+t+'|0|'+deviceId+'||||'+queryMd5+'|f189adc92b816b3e9da29ea304d4a7e4';
    var qdSign=qfDirectTripleDesBase64(signPlain,QF_QD_AUDIO_SIGN_KEY,QF_QD_AUDIO_SIGN_IV);
    var infoPlain=profile==='reader_legacy'
        ?deviceId+'||||||1||999|'+t
        :deviceId+'|7.9.394|1080|1184|1000009|10|1|Android|1526|1000009|4|0|'+t+'|1|'+deviceId+'|||||0';
    var qdInfo=qfDirectTripleDesBase64(infoPlain,QF_QD_AUDIO_INFO_KEY,QF_QD_AUDIO_INFO_IV);
    return {
        url:'https://druidv6.if.qidian.com/argus/api/'+String(path||'').replace(/^\/+/, '')+'?'+a,
        headers:{
            'QDSign':qdSign,'QDInfo':qdInfo,'tstamp':String(t),
            'User-Agent':'Mozilla/mobile QDReaderAndroid/7.9.394/1526/1000009/Android'
        },
        deviceId:deviceId,profile:profile,timestamp:t
    };
}
function qfDirectAjax(url,method,body,contentType,extraHeaders,timeoutMs){
    var opt={
        method:method||'GET',
        timeout:Math.max(2500,Number(timeoutMs||12000)||12000),
        headers:{
            'User-Agent':'Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36',
            'Accept':'application/json,text/plain,*/*',
            'Referer':'https://h5.if.qidian.com/',
            'Origin':'https://h5.if.qidian.com',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Cache-Control':'no-cache'
        }
    };

    if(extraHeaders&&typeof extraHeaders==='object'){
        for(var hk in extraHeaders){
            if(Object.prototype.hasOwnProperty.call(extraHeaders,hk)&&extraHeaders[hk]!=null&&String(extraHeaders[hk])!==''){
                opt.headers[hk]=String(extraHeaders[hk]);
            }
        }
    }

    if(body!=null){
        opt.body=String(body);
        opt.headers['Content-Type']=contentType||'application/x-www-form-urlencoded';
    }

    if(window.java&&typeof window.java.ajax==='function'){
        return String(
            window.java.ajax(
                String(url)+','+JSON.stringify(opt)
            )||''
        );
    }

    throw new Error('当前阅读 WebView 不支持 java.ajax');
}

function qfDirectForm(o){
    var a=[];

    for(var k in o){
        if(!Object.prototype.hasOwnProperty.call(o,k))continue;
        a.push(
            encodeURIComponent(k)+'='+
            encodeURIComponent(o[k]==null?'':String(o[k]))
        );
    }

    return a.join('&');
}

function qfDirectBuildAttempt(name,path,params,signed,withCookie){
    try{
        if(signed){
            var req=qfDirectSignedRequest(path,params,!!withCookie);
            return {
                name:name,
                method:'GET',
                url:req.url,
                headers:req.headers,
                signed:true,
                withCookie:!!withCookie
            };
        }
        return {
            name:name,
            method:'GET',
            url:'https://druidv6.if.qidian.com/argus/api/'+String(path||'').replace(/^\/+/, '')+'?'+qfDirectForm(params),
            headers:null,
            signed:false,
            withCookie:false
        };
    }catch(e){
        return {
            name:name,
            method:'GET',
            url:'',
            headers:null,
            signed:!!signed,
            withCookie:!!withCookie,
            skipError:'构造请求失败：'+String(e&&e.message?e.message:e)
        };
    }
}

function qfDirectAttemptList(page,size){
    page=Number(page||1);
    size=Number(size||20);

    var exact={
        bookId:String(bid),
        chapterId:String(cid),
        paragraphId:String(para),
        pg:String(page),
        pz:String(size),
        roleId:'0'
    };

    return [
        qfDirectBuildAttempt('SIGNED BRIDGE pg='+page+' pz='+size,'v1/chapterreview/getparagraphsaudiocomments',exact,true,false),
        qfDirectBuildAttempt('SIGNED BRIDGE+COOKIE pg='+page+' pz='+size,'v1/chapterreview/getparagraphsaudiocomments',exact,true,true),
        qfDirectBuildAttempt('UNSIGNED CONTROL pg='+page+' pz='+size,'v1/chapterreview/getparagraphsaudiocomments',exact,false,false)
    ];
}

function qfDiagSecretKey(k){
    return /(token|sign|signature|cookie|authorization|auth|secret|password|passwd|session|ticket|credential|key$|api[-_]?key|csrf)/i.test(
        String(k||'')
    );
}

function qfDiagSafeScalar(k,v){
    var key=String(k||'');
    var s=String(v==null?'':v);

    if(qfDiagSecretKey(key)){
        return '[REDACTED]';
    }

    if(/^\/\//.test(s))s='https:'+s;

    /*
     * Preserve diagnostic IDs/page values, but sanitize URL query strings.
     */
    if(/^https?:\/\//i.test(s)){
        try{
            var a=document.createElement('a');
            a.href=s;

            var base=String(a.protocol||'')+'//'+
                String(a.hostname||'')+
                String(a.pathname||'');

            var qs=String(a.search||'').replace(/^\?/,'');
            if(!qs)return base;

            var parts=qs.split('&');
            var safe=[];

            for(var i=0;i<parts.length;i++){
                if(!parts[i])continue;

                var p=parts[i].split('=');
                var qk=decodeURIComponent(p[0]||'');
                var qv=decodeURIComponent(p.slice(1).join('=')||'');

                if(qfDiagSecretKey(qk)){
                    safe.push(qk+'=[REDACTED]');
                }else if(
                    /(book|chapter|paragraph|page|size|role|audio|user|guid|id|cursor|index|count)/i.test(qk)
                ){
                    safe.push(qk+'='+qv);
                }else{
                    /*
                     * Keep the PARAMETER NAME because it is protocol evidence,
                     * but redact unknown value.
                     */
                    safe.push(qk+'=[VALUE]');
                }
            }

            return base+(safe.length?'?'+safe.join('&'):'');
        }catch(_e){
            return s.replace(/[?#].*$/,'');
        }
    }

    s=s.replace(/\s+/g,' ');
    if(s.length>180)s=s.slice(0,177)+'…';
    return s;
}

function qfDiagSafeDump(root,maxLines){
    maxLines=Number(maxLines||90);

    var out=[],seenObj=[];

    function add(path,k,v){
        if(out.length>=maxLines)return;

        var val=qfDiagSafeScalar(k,v);
        if(val==='')return;

        out.push(String(path||k)+' = '+val);
    }

    function walk(v,path,d){
        if(v==null||d>8||out.length>=maxLines)return;

        if(
            typeof v==='string'||
            typeof v==='number'||
            typeof v==='boolean'
        ){
            var seg=String(path||'').split('.').pop();
            add(path,seg,v);
            return;
        }

        if(Array.isArray(v)){
            out.push(path+' [array length='+v.length+']');

            for(var i=0;i<v.length&&i<8&&out.length<maxLines;i++){
                walk(v[i],path+'['+i+']',d+1);
            }
            return;
        }

        if(typeof v!=='object')return;

        if(seenObj.indexOf(v)>=0)return;
        seenObj.push(v);

        var keys=[];

        try{keys=Object.keys(v);}catch(_e){}

        out.push(
            (path||'root')+
            ' {keys: '+keys.slice(0,40).join(', ')+'}'
        );

        for(var j=0;j<keys.length&&out.length<maxLines;j++){
            var k=keys[j];
            var x=v[k];
            var kp=path?path+'.'+k:k;

            if(
                typeof x==='string'||
                typeof x==='number'||
                typeof x==='boolean'
            ){
                add(kp,k,x);
            }else{
                walk(x,kp,d+1);
            }
        }
    }

    walk(root,'',0);
    return out.join('\n');
}

function qfDiagResultSummary(d){
    d=d||{};

    var m=d.Message!=null?d.Message:
          d.message!=null?d.message:
          d.Msg!=null?d.Msg:
          d.msg!=null?d.msg:'';

    var r=d.Result!=null?d.Result:
          d.result!=null?d.result:null;

    return {
        message:qfDiagSafeScalar('Message',m),
        resultDump:qfDiagSafeDump(r,50),
        resultKeys:qfAudioObjKeys(r),
        resultType:r==null?'null':
            Array.isArray(r)?'array':
            typeof r
    };
}

function qfDirectResponseSummary(d,text){
    d=d||{};

    /*
     * Argus endpoints commonly wrap the business payload inside Result.
     * Previous versions only scanned the whole envelope; explicitly scan
     * Result as the primary business object as well.
     */
    var payload=(
        d.Result!=null&&
        typeof d.Result==='object'
    )?d.Result:d;

    var keys=qfAudioObjKeys(d);
    var payloadKeys=qfAudioObjKeys(payload);

    var audio=qfDirectAudioRows(payload);
    if(!audio.length&&payload!==d){
        audio=qfDirectAudioRows(d);
    }

    var count=qfDirectAudioCount(payload);
    if(!count&&payload!==d){
        count=qfDirectAudioCount(d);
    }

    var roles=qfDirectRoles(payload);
    if(!roles.length&&payload!==d){
        roles=qfDirectRoles(d);
    }

    var diag=qfDiagResultSummary(d);

    var status='';

    try{
        status=String(
            d.code!=null?d.code:
            d.Code!=null?d.Code:
            d.status!=null?d.status:
            d.Status!=null?d.Status:''
        );
    }catch(_e){}

    return {
        keys:keys,
        payloadKeys:payloadKeys,
        audio:audio,
        count:count,
        roles:roles,
        status:status,
        length:String(text||'').length,
        message:diag.message,
        resultDump:diag.resultDump,
        resultKeys:diag.resultKeys,
        resultType:diag.resultType
    };
}

function qfTryDirectOfficialAudio(page,size){
    var attempts=qfDirectAttemptList(page,size);
    var log=[],responded=false;
    /* beta12：SIGNED 可用时不再额外跑 UNSIGNED 诊断请求；无签名能力才只试控制组。 */
    try{var cp=qfDirectBridgeCaps();attempts=(cp.md5&&cp.des3)?attempts.slice(0,1):attempts.slice(2,3);}catch(_ca){}

    try{
        var caps=qfDirectBridgeCaps();
        log.push(
            'WEBVIEW BRIDGE: ajax='+(caps.ajax?'yes':'no')+
            ' md5='+(caps.md5?'yes':'no')+
            ' tripleDES='+(caps.des3?'yes':'no')+
            ' cookieLen='+String(caps.cookieLen||0)
        );
    }catch(_capsErr){
        log.push('WEBVIEW BRIDGE: capability probe error '+String(_capsErr));
    }

    for(var i=0;i<attempts.length;i++){
        var a=attempts[i];

        if(a&&a.skipError){
            log.push(a.name+': '+String(a.skipError||'构造失败'));
            continue;
        }

        try{
            var text=qfDirectAjax(
                a.url,
                a.method,
                a.body,
                a.contentType,
                a.headers,
                1350
            );

            var d=parse(text);

            if(!d){
                log.push(
                    a.name+': 非JSON length='+String(text||'').length
                );
                continue;
            }

            var sum=qfDirectResponseSummary(d,text);
            var okStatus=/^(?:0|200)$/.test(String(sum.status||''))||/(?:成功|success|\bok\b)/i.test(String(sum.message||''));
            if(okStatus)responded=true;

            log.push(
                a.name+
                ': status='+sum.status+
                ' audioRows='+sum.audio.length+
                ' AudioCount='+sum.count+
                ' keys=['+sum.keys+']'+
                (sum.payloadKeys?' PayloadKeys=['+sum.payloadKeys+']':'')+
                ' Message='+String(sum.message||'(空)')+
                ' ResultType='+String(sum.resultType||'')+
                (sum.resultKeys?' ResultKeys=['+sum.resultKeys+']':'')+
                (sum.resultDump?'\n  Result:\n  '+String(sum.resultDump).replace(/\n/g,'\n  '):'')
            );

            if(sum.audio.length){
                return {
                    ok:true,
                    name:a.name,
                    root:d,
                    list:sum.audio,
                    total:sum.count||sum.audio.length,
                    roles:sum.roles,
                    log:log
                };
            }

            if(sum.count>0){
                return {
                    ok:false,
                    partial:true,
                    responded:responded,
                    name:a.name,
                    root:d,
                    list:[],
                    total:sum.count,
                    roles:sum.roles,
                    log:log
                };
            }

            /* 官方接口明确成功且 AudioCount=0：这是“当前段落无配音”，无需继续扫几百页普通评论。 */
            if(okStatus&&Number(sum.count||0)===0){
                return {
                    ok:false,partial:false,confirmedEmpty:true,responded:true,
                    name:a.name,root:d,list:[],total:0,roles:sum.roles,log:log
                };
            }

        }catch(e){
            log.push(
                a.name+': ERROR '+
                String(e&&e.message?e.message:e)
            );
        }
    }

    return {
        ok:false,
        partial:false,
        confirmedEmpty:false,
        responded:responded,
        list:[],
        total:0,
        roles:[],
        log:log
    };
}

function qfDirectDiagHtml(pack){
    var logs=pack.log||[];
    var joined=logs.join('\n');
    var hint='';

    if(pack&&pack.ok&&pack.list&&pack.list.length){
        hint='签名请求已经真正命中起点官方配音接口。';
    }else if(/md5=no|tripleDES=no|无 md5Encode|无 tripleDESEncodeBase64Str/i.test(joined)){
        hint='当前阅读 WebView 的 java bridge 缺少签名所需加密方法；下一步需要把签名在外层规则环境预计算后注入。';
    }else if(/SIGNED BRIDGE[^\n]*Message=参数错误/i.test(joined)&&/UNSIGNED CONTROL[^\n]*Message=参数错误/i.test(joined)){
        hint='签名已经成功构造并发出，但服务仍返回参数错误；下一步重点转向 Cookie/客户端标识/附加 Header，而不是继续改 pg/pz。';
    }else if(/SIGNED BRIDGE[^\n]*(Message=|audioRows=|AudioCount=)/i.test(joined)){
        hint='SIGNED 请求已发出，请比较 SIGNED、SIGNED+COOKIE 与 UNSIGNED 三组返回差异。';
    }else{
        hint='本版首先确认 WebView 是否能通过 window.java 完成 MD5 + 3DES，并让 SIGNED 请求真正发出。';
    }

    return (
      '<div class="qfBbDiag qfDirectDiag">'+
        '<div class="qfBbTitle">起点官方配音直连诊断 v2.9.24</div>'+
        '<div class="qfBbWarn">'+
          'v2.9.21 的 SIGNED 请求实际没有发出：WebView 中不存在 Packages。'+
          '本版改用 window.java.md5Encode / tripleDESEncodeBase64Str，并增加 SIGNED+COOKIE 对照。'+
        '</div>'+
        '<div class="qfBbLine"><b>判断：</b>'+esc(hint)+'</div>'+
        '<div class="qfBbLine"><b>命中方式：</b>'+esc(pack.name||'(未命中)')+'</div>'+
        '<div class="qfBbLine"><b>官方 AudioCount：</b>'+esc(String(pack.total||0))+
          ' ｜ 本页真实 AudioUrl='+esc(String((pack.list||[]).length))+'</div>'+
        '<div class="qfBbLine"><b>AudioRoleInfo / 角色：</b>'+esc(qfAudioRoleText(pack.roles||[]))+'</div>'+
        '<details class="qfBbDetails" open>'+
          '<summary>WebView Bridge / SIGNED / COOKIE 对照日志</summary>'+
          '<pre>'+esc(joined||'(无日志)')+'</pre>'+
        '</details>'+
      '</div>'
    );
}

function qfStartAudioDirectProbe(token){
    var st=mediaScanState;

    if(!st||st.token!==token||currentTab!=='audio')return;

    /* All tab may already have fetched the same official audio set. */
    if(allAudioReady&&allAudioRows.length){
        st.done=true;
        ended=true;
        st.found=allAudioTotal||allAudioRows.length;
        st.rendered=true;
        totalAudio=st.found;
        setCounts();

        audioDirectRows=allAudioRows.slice();
        audioDirectPack=allAudioPack||{
            ok:true,
            name:'SIGNED BRIDGE CACHE',
            root:{},
            list:audioDirectRows,
            total:st.found,
            roles:[],
            log:['复用“全部”标签已缓存的起点官方配音结果']
        };
        audioDirectPack.list=audioDirectRows;
        audioDirectPack.total=st.found;
        audioRoleFilter='all';
        qfAudioRenderDirectPage();
        return;
    }

    listEl.innerHTML='<div class="loading"><div class="spinner"></div><div>正在获取配音…</div></div>';

    var pack=null;

    try{
        pack=qfTryDirectOfficialAudio(1,20);
    }catch(e0){
        pack={
            ok:false,
            list:[],
            total:0,
            roles:[],
            log:['DIRECT FATAL: '+String(e0&&e0.message?e0.message:e0)]
        };
    }

    if(pack&&pack.ok&&pack.list.length){
        st.done=true;
        ended=true;
        st.found=pack.total||pack.list.length;
        st.rendered=true;

        qfMediaEmptyDropV403('audio');
        totalAudio=st.found;
        setCounts();

        audioDirectRows=pack.list.slice();
        audioDirectPack=pack;
        audioRoleFilter='all';

        allAudioReady=true;
        allAudioRows=audioDirectRows.slice();
        allAudioPack=pack;
        allAudioTotal=Number(pack.total||allAudioRows.length||0);
        allAudioById={};
        allAudioBySig={};
        for(var ai=0;ai<allAudioRows.length;ai++)qfAllAudioIndexRow(allAudioRows[ai]);

        qfAudioRenderDirectPage();
        return;
    }

    if(pack&&pack.confirmedEmpty){
        qfMediaEmptyPutV403('audio');
        st.found=0;st.typeFound=false;st.rendered=false;st.done=false;
        totalAudio=0;setCounts();finishMediaScan(st);return;
    }

    /* beta16.3：无配音优先快速结束。
     * 有配音时官方专用接口通常首轮就能直接命中；
     * 首轮没有明确媒体时不再扫描普通评论流，避免无配音段落额外等待。 */
    st.found=0;
    st.typeFound=false;
    st.rendered=false;
    st.done=false;
    if(Number(totalAudio)<0)totalAudio=-1;
    finishMediaScan(st);
    return;
}

/* ---------- 起点官方配音通用对象辅助 ---------- */
function qfAudioObjKeys(o){
    if(!o||typeof o!=='object')return '';
    try{
        return Object.keys(o).slice(0,40).join(', ');
    }catch(e){
        return '';
    }
}

function qfAudioFindRoles(root){
    var out=[],seenObj=[],seenKey={};

    function pushRole(x,path){
        if(x==null)return;

        if(typeof x==='string'||typeof x==='number'){
            var t=String(x);
            if(!seenKey[t]){
                seenKey[t]=1;
                out.push({id:'',name:t,path:path});
            }
            return;
        }

        if(typeof x!=='object')return;

        var id=String(
            x.AudioRoleId||x.audioRoleId||
            x.RoleId||x.roleId||
            x.Id||x.id||''
        );

        var name=String(
            x.AudioRoleName||x.audioRoleName||
            x.RoleName||x.roleName||
            x.Name||x.name||x.Title||x.title||''
        );

        var key=id+'|'+name;
        if((id||name)&&!seenKey[key]){
            seenKey[key]=1;
            out.push({id:id,name:name,path:path});
        }
    }

    function walk(v,path,d){
        if(v==null||d>8)return;

        if(Array.isArray(v)){
            for(var i=0;i<v.length;i++)walk(v[i],path+'['+i+']',d+1);
            return;
        }

        if(typeof v!=='object')return;
        if(seenObj.indexOf(v)>=0)return;
        seenObj.push(v);

        for(var k in v){
            if(!Object.prototype.hasOwnProperty.call(v,k))continue;
            var lk=String(k).toLowerCase();
            if(lk.indexOf('role')>=0)pushRole(v[k],path?path+'.'+k:k);
            walk(v[k],path?path+'.'+k:k,d+1);
        }
    }

    walk(root,'',0);
    return out;
}

function qfAudioRoleText(roles){
    if(!roles||!roles.length)return '未发现 audio_roles / AudioRole';

    var a=[];
    for(var i=0;i<roles.length&&i<12;i++){
        var r=roles[i]||{};
        a.push((r.id?'#'+r.id+' ':'')+(r.name||'(无名称)'));
    }
    return a.join(' ｜ ');
}

function resetMediaTargets(st){
    var src=mediaTargets(),out=[];

    for(var i=0;i<src.length;i++){
        out.push({
            segmentId:Number(src[i].segmentId)||0,
            paragraphId:Number(src[i].paragraphId),
            expected:Number(src[i].expected||0),
            page:1,
            loaded:0,
            done:false
        });
    }

    st.targets=out;
    st.targetIndex=0;
    st.typeFound=false;
}

function startMediaScan(kind){
    ended=false;
    mediaScanToken++;

    var token=mediaScanToken;

    /* 同一段落短期已被官方专用接口确认无媒体：跨弹窗也直接结束。 */
    try{if(qfMediaEmptyGetV403(kind))mediaEmptyKnown[kind]=true;}catch(_ec){}
    /* 同一弹窗已经完成过一次空结果判定：再次切入直接显示，不重复联网。 */
    if(mediaEmptyKnown&&mediaEmptyKnown[kind]){
        mediaScanState={token:token,kind:kind,done:true,found:0,seen:{},rows:[]};
        ended=true;
        listEl.innerHTML='<div class="empty mediaEmptyCompact">'+(kind==='audio'?'暂无配音':'暂无配图')+'</div>';
        moreEl.classList.add('hidden');
        setCounts();
        return;
    }

    /* 如果“全部”已经把本段全部评论加载完且没有媒体，就无需再用筛选接口证明一次。 */
    try{
        var knownTotal=Number(totalAll||0),loadedN=Number(loadedAllRaw.length||0);
        if(knownTotal>0&&loadedN>=knownTotal&&qfLoadedMediaSeedV313(kind).length===0){
            mediaEmptyKnown[kind]=true;
            mediaScanState={token:token,kind:kind,done:true,found:0,seen:{},rows:[]};
            ended=true;
            listEl.innerHTML='<div class="empty mediaEmptyCompact">'+(kind==='audio'?'暂无配音':'暂无配图')+'</div>';
            moreEl.classList.add('hidden');setCounts();return;
        }
    }catch(_full){}

    var types=kind==='image'
        ?[2,3,-1]
        :[3,2,-1];

    mediaScanState={
        token:token,
        kind:kind,
        types:types,
        typeIndex:0,
        currentType:types[0],
        targets:[],
        targetIndex:0,
        rows:[],
        seen:{},
        found:0,
        rendered:false,
        done:false,
        typeFound:false,
        detailSeen:{},
        detailBudget:80,
        scanStarted:Date.now(),
        requestCount:0,
        maxRequests:1,
        maxMs:2300
    };

    resetMediaTargets(mediaScanState);

    /* beta15.1：同一弹窗内已确认的媒体数不因为重新切标签而退回未知。 */
    setCounts();

    listEl.innerHTML=
        '<div class="loading"><div class="spinner"></div><div>'+
        (kind==='image'?'正在查找配图…':'正在获取配音…')+
        '</div></div>';

    /* 先复用“全部”页已经拿到的评论，切标签时有图/音就立即出现，不重新等网络。 */
    try{
        var seed=qfLoadedMediaSeedV313(kind);
        if(seed.length){
            var got=renderMediaRows(seed,kind);
            if(got>0){
                mediaScanState.found+=got;
                mediaScanState.rendered=true;
                mediaScanState.typeFound=true;
                setCounts();
                /* “全部”里已经真实看到媒体时，切媒体标签应当秒开。
                 * 不再为了追一个不可靠的总数重新跑多套接口。 */
                finishMediaScan(mediaScanState);
                return;
            }
        }
    }catch(_seed){}

    /* v4.0：配图/配音都优先专用 Qidian APP API；普通 reviewList 仅保留一次异常兜底。 */
    if(kind==='image'&&hasParagraph){
        setTimeout(function(){qfStartImageDirectProbeV402(token);},30);
        return;
    }
    if(kind==='audio'&&hasParagraph){
        setTimeout(function(){qfStartAudioDirectProbe(token);},30);
        return;
    }

    setTimeout(function(){mediaScanStep(token);},30);
}

function finishMediaScan(st){
    st.done=true;
    ended=true;

    /* 有限评论流扫描只能证明“至少找到 N 条”，不能冒充官方总数。 */
    if(st.kind==='image'){
        if(!st.found)totalImg=-1;
    }else{
        if(!st.found&&Number(totalAudio)<0)totalAudio=-1;
    }

    setCounts();

    if(!st.found){
        try{mediaEmptyKnown[st.kind]=true;}catch(_mk){}
        listEl.innerHTML='<div class="empty mediaEmptyCompact">'+
            (st.kind==='audio'?'暂无配音':'暂无配图')+
            '</div>';
    }

    moreEl.classList.add('hidden');
}

function mediaScanStep(token){
    var st=mediaScanState;

    if(!st||st.token!==token||st.done)return;
    if(currentTab!==st.kind)return;

    if(((Date.now()-Number(st.scanStarted||0))>Number(st.maxMs||(st.kind==='audio'?7000:9000))||Number(st.requestCount||0)>=Number(st.maxRequests||(st.kind==='audio'?8:10)))){
        finishMediaScan(st);return;
    }

    if(!st.targets||!st.targets.length){
        finishMediaScan(st);
        return;
    }

    var target=null,guard=0;

    while(guard<st.targets.length){
        guard++;

        var ix=st.targetIndex%st.targets.length;
        st.targetIndex=(ix+1)%st.targets.length;

        if(!st.targets[ix].done){
            target=st.targets[ix];
            break;
        }
    }

    if(!target){
        /*
         * 当前 type 扫完。
         * 有媒体 -> 说明这个 type 可用，结束；
         * 没媒体 -> 自动切下一种官方 type。
         */
        if(st.typeFound){
            finishMediaScan(st);
            return;
        }

        st.typeIndex++;

        if(st.typeIndex>=st.types.length){
            finishMediaScan(st);
            return;
        }

        st.currentType=st.types[st.typeIndex];
        resetMediaTargets(st);

        setTimeout(function(){
            mediaScanStep(token);
        },40);

        return;
    }

    var saveSeg=segment,pk=null;

    try{
        segment=Number(target.segmentId)||0;
        st.requestCount=Number(st.requestCount||0)+1;

        pk=fetchMediaPack(
            st.kind,
            target.page,
            pageSize,
            st.currentType,
            target.paragraphId
        );
    }catch(e0){
        pk={list:[],total:0,data:{}};
    }

    segment=saveSeg;

    var rows=(pk&&pk.list)||[];
    var packTotal=Number(pk&&pk.total||0);

    if(!rows.length){
        target.done=true;

    }else{
        target.loaded+=rows.length;
        target.page++;

        var got=0;

        if(st.kind==='audio'){
            var verified=probeAudioRows(rows,st);

            if(verified.length){
                got=renderMediaRows(verified,'audio');
            }
        }else{
            got=renderMediaRows(rows,'image');
        }

        if(got>0){
            st.typeFound=true;
            st.found+=got;
        }

        var expected=packTotal>0
            ?packTotal
            :Number(target.expected||0);

        if(expected>0&&target.loaded>=expected){
            target.done=true;
        }

        /*
         * 非 type=2 候选如果前3页仍没有任何媒体，
         * 就换下一种 type，防止同一批普通评论被重复扫完整章。
         */
        if(
            st.currentType!==-1&&
            !st.typeFound&&
            target.page>(st.kind==='audio'?5:3)
        ){
            target.done=true;
        }

        /* beta13：媒体标签只做有限扫描。普通评论兜底也不再翻几百页阻塞界面。 */
        if(st.currentType===-1&&target.page>(st.kind==='audio'?8:6)){
            target.done=true;
        }
    }

    setCounts();

    setTimeout(function(){
        mediaScanStep(token);
    },80);
}
function ensureChapterAll(){if(chapterAll)return chapterAll;if(chapterLoading)return[];chapterLoading=true;try{chapterAll=allPages('reviewList',2);if(!totalAll)totalAll=chapterAll.length;setCounts();return chapterAll}finally{chapterLoading=false}}

function qfAllAudioSignatureFromComment(c){
    c=c||{};
    var name=String(c.name||'').replace(/\s+/g,'').toLowerCase();
    var text=String(c.content||'').replace(/\s+/g,'').toLowerCase();
    if(text.length>80)text=text.slice(0,80);
    var tm=Number(c.time||0);
    if(tm>0)tm=Math.floor(tm/60000);
    return name+'|'+text+'|'+String(tm||0);
}

function qfAllAudioIndexRow(row){
    if(!row)return;
    var c=adapt(row);
    var id=String(c.id||'');
    var sig=qfAllAudioSignatureFromComment(c);
    if(id)allAudioById[id]=row;
    if(sig&&sig!=='||0')allAudioBySig[sig]=row;
}

function qfAllMediaMergeAudio(row){
    if(!row||!allAudioRows.length)return row;

    var c=adapt(row);
    var hit=null;
    if(c.id&&allAudioById[String(c.id)])hit=allAudioById[String(c.id)];
    if(!hit){
        var sig=qfAllAudioSignatureFromComment(c);
        if(sig&&allAudioBySig[sig])hit=allAudioBySig[sig];
    }
    if(!hit)return row;

    var src=hit.raw||hit;
    var dst=row.raw||row;
    if(!dst||typeof dst!=='object')return row;

    var au=String(
        src._qfAudioUrl||src.AudioUrl||src.audioUrl||src.audio_url||
        src.VoiceUrl||src.voiceUrl||src.voice_url||''
    );
    if(au){
        dst._qfAudioVerified=true;
        dst._qfAudioDetected=true;
        dst._qfAudioUrl=au;
    }

    var dur=Number(
        src._qfAudioDuration||src.AudioTime||src.audioTime||
        src.AudioDuration||src.audioDuration||0
    )||0;
    if(dur>1000)dur=dur/1000;
    if(dur>=1.5&&dur<36000)dst._qfAudioDuration=dur;

    if(src.AudioRoleInfo)dst.AudioRoleInfo=src.AudioRoleInfo;
    if(src.AudioRoleId!=null)dst.AudioRoleId=src.AudioRoleId;
    if(src._qfAudioRoleInfo)dst._qfAudioRoleInfo=src._qfAudioRoleInfo;
    if(src._qfAudioRoleId!=null)dst._qfAudioRoleId=src._qfAudioRoleId;

    if(c.id)dst._qfAudioPage=officialReviewDetailUrl(c.id);
    return row;
}

function qfAllMediaEnrichRows(rows){
    rows=Array.isArray(rows)?rows:[];
    allAudioAddedLast=0;
    if(!rows.length)return rows;

    /* alpha13：普通“全部”首屏不再同步扫描配音专用 API（旧逻辑最多8页）。
     * reviewList 自身带回的图片/音频仍照常显示；需要完整配音时点击“配音”标签按需加载。
     * 如果本次会话已经加载过配音索引，再做无额外网络请求的本地合并。 */
    if(!allAudioReady)return rows;

    var out=[],seenId={},seenSig={},seenAudio={};

    function mark(c){
        if(!c)return;
        if(c.id)seenId[String(c.id)]=1;
        var sig=qfAllAudioSignatureFromComment(c);
        if(sig&&sig!=='||0')seenSig[sig]=1;
        if(c.audio)seenAudio[String(c.audio)]=1;
    }

    /* 先保留普通 reviewList 的原始顺序，并对确实能匹配的记录补音频字段。 */
    for(var i=0;i<rows.length;i++){
        var merged=qfAllMediaMergeAudio(rows[i]);
        out.push(merged);
        mark(adapt(merged));
    }

    /*
     * 关键修复：官方音频 API 返回的“配音评论”并不保证同时存在于普通
     * reviewList(type=2) 中。因此不能只做 ID 合并；未匹配到的音频记录
     * 必须作为独立段评加入“全部”。只在首屏加入一次，后续分页靠 seen 去重。
     */
    if(page===1&&allAudioRows.length){
        for(var j=0;j<allAudioRows.length;j++){
            var ar=allAudioRows[j]||{};
            var ac=adapt(ar);
            var aid=String(ac.id||'');
            var asig=qfAllAudioSignatureFromComment(ac);
            var aurl=String(ac.audio||'');

            if(
                (aid&&seenId[aid])||
                (asig&&seenSig[asig])||
                (aurl&&seenAudio[aurl])
            )continue;

            out.push(ar);
            mark(ac);
            allAudioAddedLast++;
        }

        /* 默认推荐流做轻量热度重排；不改“热门/最新”的独立排序语义。 */
        if(currentSort==='default'&&allAudioAddedLast>0){
            out.sort(function(a,b){
                var x=adapt(a),y=adapt(b);
                var d=Number(y.like||0)-Number(x.like||0);
                if(d)return d;
                d=Number(y.replies||0)-Number(x.replies||0);
                if(d)return d;
                return Number(y.time||0)-Number(x.time||0);
            });
        }
    }

    return out;
}

function mediaCounts(){
    if(isAuthor)return;
    if(Number(allAudioTotal||0)>0)totalAudio=Math.max(Number(totalAudio||-1),Number(allAudioTotal||0));
    setCounts();
}
function currentAction(){return'reviewList'}
function officialMediaFallback(kind){
    return '<div class="empty mediaEmptyCompact">'+(kind==='image'?'暂无配图':'暂无配音')+'</div>';
}
function scheduleAutoLoad(){
    if(ended||loading)return;
    if(autoLoadBudget<=0)return;
    if(currentTab!=='all'||currentSort!=='default')return;
    if(isAuthor)return;

    autoLoadBudget--;

    if(autoLoadTimer){
        try{clearTimeout(autoLoadTimer);}catch(e0){}
    }

    autoLoadTimer=setTimeout(function(){
        autoLoadTimer=null;

        if(
            !ended&&
            !loading&&
            currentTab==='all'&&
            currentSort==='default'
        ){
            load();
        }
    },220);
}

function qfChapterEndRowKey2933(row){
    row=row||{};
    var id=String(
        row.ReviewId||row.reviewId||
        row.CommentId||row.commentId||
        row.Id||row.id||row.PostId||row.postId||''
    );
    if(id)return 'id:'+id;
    return 'sig:'+String(row.UserName||row.userName||'')+'|'+
        String(row.Content||row.content||'')+'|'+String(row.CreateTime||row.createTime||'');
}

function qfMergeChapterEndRows2933(x){
    x=x||{};
    var out=[],seenLocal={},segments=x.SegmentDataList||x.segmentDataList||[];
    var chapter=x.ChapterDataList||x.chapterDataList||x.List||x.list||[];
    if(!Array.isArray(chapter))chapter=[];
    if(!Array.isArray(segments))segments=[];

    function add(row,quote){
        if(!row||typeof row!=='object')return;
        /* 起点助手 ZWjj 同样跳过 Category=0 的非评论占位项。字段缺失则正常保留。 */
        try{
            if(row.Category!=null&&Number(row.Category)===0)return;
            if(row.category!=null&&Number(row.category)===0)return;
        }catch(_cat){}
        var k=qfChapterEndRowKey2933(row);
        if(k&&seenLocal[k])return;
        if(k)seenLocal[k]=1;
        if(quote&&!row.RefferContent&&!row.refferContent&&!row.ReferContent&&!row.referContent){
            try{row.RefferContent=String(quote||'');}catch(_q){}
        }
        /* alpha18.1：只有 getchapterendreview 的真实评论行带此标记，adapt 才允许
           将 CommentCount 解释成该楼层的回复数。 */
        try{row._qfChapterEndReview=1;}catch(_ce){}
        out.push(row);
    }

    for(var i=0;i<chapter.length;i++)add(chapter[i],'');
    for(var si=0;si<segments.length;si++){
        var sg=segments[si]||{};
        var quote=String(sg.QuoteContent||sg.quoteContent||sg.RefferContent||sg.refferContent||'');
        var dl=sg.DataList||sg.dataList||sg.List||sg.list||[];
        if(!Array.isArray(dl))dl=[];
        for(var di=0;di<dl.length;di++)add(dl[di],quote);
    }
    return out;
}

function qfFetchChapterEndReview2933(p,ps){
    p=Math.max(1,Number(p)||1);
    /* 成熟起点助手对该接口固定使用 pz=10；保持官方分页习惯，避免大 pz 只返回首批。 */
    var requestSize=10;
    var params={
        bookId:String(bid),
        chapterId:String(cid),
        pg:String(p),
        pz:String(requestSize)
    };
    var attempts=[false,true];
    var lastErr='';
    for(var ai=0;ai<attempts.length;ai++){
        try{
            var req=qfDirectSignedRequest(
                'v1/chapterreview/getchapterendreview',
                params,
                attempts[ai]
            );
            var txt=qfDirectAjax(req.url,'GET',null,null,req.headers);
            var d=parse(txt);
            if(!d){lastErr='非JSON';continue;}
            var x=d.Data||d.data||d;
            var seg=x.SegmentDataList||x.segmentDataList||[];
            if(!Array.isArray(seg))seg=[];
            var list=qfMergeChapterEndRows2933(x);
            var total=Number(
                x.ChapterReviewTotalCount||x.chapterReviewTotalCount||
                x.ChapterReviewCount||x.chapterReviewCount||
                x.TotalCount||x.totalCount||x.Total||x.total||0
            )||0;
            /* 部分版本不提供总数；正文卡片 qfcount 会提供更可靠的本章说数量。 */
            total=Math.max(total,Number(expectedCount||0),list.length);
            if(list.length||total>0||Number(d.Code)===0||Number(d.code)===0){
                return {list:list,total:total,segments:seg,data:x,raw:d,error:'',pageSize:requestSize};
            }
            lastErr=String(d.Message||d.message||d.Msg||d.msg||'');
        }catch(e){lastErr=String(e&&e.message?e.message:e);}
    }
    return {list:[],total:Number(expectedCount||0),segments:[],data:{},raw:null,error:lastErr,pageSize:requestSize};
}

function qfChapterAllRowsV313(){
    if(chapterAll)return chapterAll;
    if(chapterLoading)return [];
    chapterLoading=true;
    try{
        var out=[],seenAll={},pg=1,guard=0,total=0;
        while(guard<30){
            guard++;
            /* 全部走起点本地：App 章末接口优先，Web 仅本地兜底。 */
            var cp=qfFetchChapterEndReview2933(pg,10);
            if(!cp||!(cp.list||[]).length){
                var wp=fetchPack('reviewList',pg,10,{segmentId:0,paragraphId:-1,type:2});
                cp={list:(wp&&wp.list)||[],total:Number(wp&&wp.total||0),segments:[]};
            }
            cp=cp||{list:[],total:0};
            var rs=cp.list||[];
            total=Math.max(total,Number(cp.total||0),Number(expectedCount||0));
            if(!rs.length)break;
            var added=0;
            for(var i=0;i<rs.length;i++){
                var r=rs[i]||{},id=reviewObjId(r),c=adapt(r);
                var key=id?('id:'+id):('sig:'+String(c.name||'')+'|'+String(c.content||'')+'|'+String(c.time||''));
                if(seenAll[key])continue;
                seenAll[key]=1;out.push(r);added++;
            }
            if(total>0&&out.length>=total)break;
            if(added===0)break;
            pg++;
        }
        chapterAll=out;
        if(!totalAll)totalAll=Math.max(total,out.length);
        setCounts();
        return chapterAll;
    }finally{chapterLoading=false;}
}

function load(){
    if(loading||ended)return;

    /*
     * 配图/配音完全独立于普通段评分页，
     * 点标签后逐页扫描，避免打开时同步抓完整章。
     */
    if((currentTab==='image'||currentTab==='audio')&&!isChapter){
        if(
            !mediaScanState||
            mediaScanState.kind!==currentTab
        ){
            startMediaScan(currentTab);
        }
        return;
    }

    loading=true;
    moreEl.classList.add('hidden');
    moreEl.classList.remove('qfRetry');
    moreEl.textContent='加载更多';

    var shouldAuto=false;

    try{
        var rows=[],activeTotal=0,local=false,chapterProgress=false;

        if(isAuthor){
            rows=authorSay?[{
                comment_id:authorReviewId,
                text:authorSay,
                create_timestamp:0,
                reply_count:authorReplyCount,
                user_info:{user_name:authorName||'作者',user_avatar:authorAvatar||''},
                raw:{ReviewId:authorReviewId,RootReviewId:authorReviewId,UserName:authorName||'作者',UserHeadIcon:authorAvatar||'',Content:authorSay,ReplyCount:authorReplyCount,replyList:Array.isArray(authorReplyList)?authorReplyList:[]}
            }]:[];

            activeTotal=rows.length;
            ended=true;

        }else if(isChapter){
            /* alpha13：推荐保留起点官方返回顺序；热门/最新才拉取完整本章说后本地排序。
             * 这样“推荐”不会被点赞数重排，三个按钮也都有真实区别。 */
            var cp=null;
            if(currentSort!=='default'){
                var ca=qfChapterAllRowsV313();
                var sortedChapter=sortRows(ca);
                activeTotal=sortedChapter.length;
                rows=sortedChapter.slice((page-1)*pageSize,page*pageSize);
                cp={list:rows,total:activeTotal,segments:[]};
                local=true;
            }else{
                cp=qfFetchChapterEndReview2933(page,10);
                if(!cp||!(cp.list||[]).length){
                    var wp=fetchPack('reviewList',page,10,{segmentId:0,paragraphId:-1,type:2});
                    cp={list:(wp&&wp.list)||[],total:Number(wp&&wp.total||0),segments:[]};
                }
                cp=cp||{list:[],total:0,segments:[]};
                rows=cp.list||[];
                activeTotal=Math.max(Number(cp.total||0),Number(expectedCount||0),rows.length);
            }

            if(currentTab==='image'){
                rows=rows.filter(function(r){return !!adapt(r).image;});
                activeTotal=rows.length;
            }else if(currentTab==='audio'){
                rows=rows.filter(function(r){var c=adapt(r);return !!(c.audio||c.audioPage);});
                activeTotal=rows.length;
            }else if(page===1){
                totalAll=Math.max(Number(totalAll||0),Number(activeTotal||0),Number(expectedCount||0));
            }

        }else if(currentSort!=='default'){
            var aa=allPages(currentAction(),2);

            aa=sortRows(aa);
            activeTotal=aa.length;
            rows=aa.slice(
                (page-1)*pageSize,
                page*pageSize
            );
            local=true;

        }else{
            /*
             * 普通原位段评只取当前页。
             * 首屏显示后由 scheduleAutoLoad 再补4轮。
             */
            var pk=fetchPack(
                currentAction(),
                page,
                pageSize,
                {type:2,paragraphId:Number(para)}
            );

            rows=pk.list||[];
            activeTotal=Math.max(
                Number(pk.total||0),
                Number(expectedCount||0)
            );
            extractQuote(pk.data,rows);
        }

        if(currentTab==='all'&&!isAuthor&&!isChapter){
            /*
             * “全部”是完整评论流；配图/配音只是它的筛选视图。
             * reviewList 本身可带配图；配音 URL 由已打通的官方 audio API
             * 按评论 id/文本时间签名补回原评论，不改变普通评论顺序。
             */
            rows=qfAllMediaEnrichRows(rows);
            /* beta16.1：把实际已经展示的原始评论留在当前弹窗内。
             * 配图标签必须优先直接过滤这批数据，不能再重新猜接口。 */
            qfRememberLoadedAllV317(rows);

            if(page===1){
                totalAll=Math.max(
                    Number(totalAll||0),
                    Number(activeTotal||0)+Number(allAudioAddedLast||0),
                    rows.length
                );
                mediaCounts();
                if(allAudioTotal>0)totalAudio=allAudioTotal;
            }else{
                totalAll=Math.max(Number(totalAll||0),Number(activeTotal||0),rows.length);
            }
        }

        setCounts();

        if(page===1){
            listEl.innerHTML='';
        }

        var valid=[];

        for(var i=0;i<rows.length;i++){
            var c=adapt(rows[i]);

            var id=c.id||(
                'x_'+page+'_'+i+'_'+
                c.time+'_'+c.content
            );

            if(seen[id])continue;

            seen[id]=1;
            valid.push(c);
        }

        if(
            page>1&&
            rows.length>0&&
            valid.length===0&&
            !isAuthor&&
            !isChapter&&
            currentTab==='all'
        ){
            try{
                var fb=fetchPackFallback(
                    currentAction(),
                    page,
                    pageSize,
                    {type:2,paragraphId:isChapter?-1:Number(para)}
                );

                var fr=fb.list||[];
                try{qfRememberLoadedAllV317(fr);}catch(_rememberFb){}
                activeTotal=Math.max(
                    activeTotal,
                    Number(fb.total||0),
                    Number(expectedCount||0)
                );

                for(var fi=0;fi<fr.length;fi++){
                    var fc=adapt(fr[fi]);
                    var fid=fc.id||(
                        'fb_'+page+'_'+fi+'_'+fc.time+'_'+fc.content
                    );
                    if(seen[fid])continue;
                    seen[fid]=1;
                    valid.push(fc);
                }
            }catch(_fbErr){}
        }

        if(!valid.length&&page===1){
            if(chapterProgress&&chapterState&&!chapterState.done){
                listEl.innerHTML=
                    '<div class="loading"><div class="spinner"></div><div>继续加载本章评论…</div></div>';
            }else{
                listEl.innerHTML='<div class="empty">暂无评论</div>';
            }

        }else if(valid.length){
            if(
                page===1&&
                listEl.querySelector('.loading')
            ){
                listEl.innerHTML='';
            }

            var h='';

            for(var j=0;j<valid.length;j++){
                h+=commentHtml(valid[j]);
            }

            listEl.insertAdjacentHTML(
                'beforeend',
                h
            );
            setTimeout(function(){qfApplyFolds(listEl)},0);
        }

        actual+=valid.length;

        if(isAuthor){
            try{setTimeout(qfAuthorReplyProbeV408,10);}catch(_arp){}
            ended=true;

        }else if(isChapter){
            /* 本章说分页按 pz=10。只要已展示数量达到正文卡片/接口上报总数就结束；
             * 若本页为空也结束，防止无效“加载更多”死循环。 */
            ended=(activeTotal>0&&actual>=activeTotal)||rows.length===0;

        }else if(chapterProgress){
            ended=!!(
                chapterState&&
                chapterState.done
            );

        }else if(local){
            ended=
                activeTotal>0
                    ?page*pageSize>=activeTotal
                    :rows.length===0;

        }else{
            /*
             * 核心修复：
             * 请求20条但真机实际只给10条时，
             * 只要 total > actual 就继续下一页。
             */
            if(activeTotal>0){
                ended=
                    (actual>=activeTotal)||
                    rows.length===0;
            }else{
                ended=rows.length===0;
            }
        }

        if(!ended){
            page++;
            moreEl.classList.remove('hidden');

            shouldAuto=
                currentTab==='all'&&
                currentSort==='default'&&
                autoLoadBudget>0;
        }else{
            moreEl.classList.add('hidden');
        }

    }catch(e){
        if(page===1){
            listEl.innerHTML='<div class="empty qfErrorState"><div class="qfErrorIcon">!</div><div class="qfErrorTitle">评论加载失败</div><div class="qfErrorSub">网络或起点接口暂时没有正常返回，稍后重试即可。</div><button class="retryBtn" type="button">重新加载</button></div>';
        }else{
            moreEl.textContent='加载失败 · 点此重试';moreEl.classList.add('qfRetry');moreEl.classList.remove('hidden');
        }
    }finally{
        loading=false;
    }

    if(shouldAuto){
        scheduleAutoLoad();
    }
}
var qfViewPosV316={};
function qfViewKeyV316(tab,sort){return String(tab||'all')+'|'+String(sort||'default')}
function qfRememberViewV316(){try{qfViewPosV316[qfViewKeyV316(currentTab,currentSort)]=window.scrollY||document.documentElement.scrollTop||0}catch(_e){}}
function qfRestoreViewV316(){var y=0;try{y=Number(qfViewPosV316[qfViewKeyV316(currentTab,currentSort)]||0)}catch(_e){}if(!(y>0))return;setTimeout(function(){try{window.scrollTo(0,y)}catch(_s){}},60);setTimeout(function(){try{window.scrollTo(0,y)}catch(_s){}},180)}
function switchTab(t){
    if(isAuthor)return;
    t=String(t||'all');
    if(t===currentTab)return;
    qfRememberViewV316();

    currentTab=t;

    var tabs=document.querySelectorAll('.tab');

    for(var i=0;i<tabs.length;i++){
        tabs[i].classList.toggle(
            'active',
            tabs[i].getAttribute('data-tab')===t
        );
    }

    var sortRow=document.getElementById('sortRow');
    if(sortRow)sortRow.classList.toggle('hidden',t==='audio'||t==='image');
    document.body.classList.toggle('audioMode',t==='audio');
    document.body.classList.toggle('imageMode',t==='image');

    reset();
    load();
    qfRestoreViewV316();
}
function switchSort(s){
    if(isAuthor)return;
    s=String(s||'default');
    if(s===currentSort)return;
    qfRememberViewV316();

    currentSort=s;

    var ss=document.querySelectorAll('.sort');

    for(var i=0;i<ss.length;i++){
        ss[i].classList.toggle(
            'active',
            ss[i].getAttribute('data-sort')===s
        );
    }

    reset();
    load();
    qfRestoreViewV316();
}

function reviewObjId(x){
    x=x||{};
    /* v2.9.33：评论/回复自身 ID 优先。
     * RootReviewId 在 quoteReviewList 的子回复里通常表示根楼层，
     * 不能排在 Id/CommentId 前面，否则一整页回复会被误判成同一个 ID。
     */
    return String(
        x.ReviewId||x.reviewId||
        x.CommentId||x.commentId||
        x.Id||x.id||
        x.PostId||x.postId||
        x.RootReviewId||x.rootReviewId||
        ''
    );
}
function reviewObjAltId(x){
    x=x||{};
    var primary=reviewObjId(x);
    var ids=[
        x.Id,x.id,x.CommentId,x.commentId,
        x.ReviewId,x.reviewId,x.RootReviewId,x.rootReviewId,
        x.PostId,x.postId
    ];
    for(var i=0;i<ids.length;i++){
        var s=String(ids[i]||'');
        if(s&&s!==primary)return s;
    }
    return '';
}
function qfCommentRootIds(c){
    c=c||{};
    var raw=c.raw||c||{};
    var all=[],seen={};
    function push(v){
        var x=String(v||'');
        if(!x||seen[x])return;
        seen[x]=1;all.push(x);
    }
    push(c.id);
    push(raw.ReviewId);push(raw.reviewId);
    push(raw.CommentId);push(raw.commentId);
    push(raw.Id);push(raw.id);
    push(raw.PostId);push(raw.postId);
    push(raw.RootReviewId);push(raw.rootReviewId);
    var primary=all.length?all[0]:'';
    var alt=all.length>1?all[1]:'';
    return {primary:primary,alt:alt,all:all};
}

function qfReplyParentId2928(x){
    x=x||{};
    return String(
        x.RefferCommentId||x.refferCommentId||
        x.RefCommentId||x.refCommentId||
        x.QuoteReviewId||x.quoteReviewId||
        x.SourceReviewId||x.sourceReviewId||
        x.RootReviewId||x.rootReviewId||
        x.ParentId||x.parentId||''
    );
}

function qfReplyCookie2929(){
    var ck=String(qdCookie||'');
    if(!ck){
        try{ck=String(document.cookie||'');}catch(_e){}
    }
    return ck;
}

function qfReplyCookieValue2929(name){
    var ck=qfReplyCookie2929();
    if(!ck)return '';
    name=String(name||'');
    try{
        var parts=String(ck).split(';');
        for(var i=0;i<parts.length;i++){
            var s=String(parts[i]||'').replace(/^\s+|\s+$/g,'');
            var eq=s.indexOf('=');
            if(eq<0)continue;
            if(s.slice(0,eq)===name)return s.slice(eq+1);
        }
    }catch(_e){}
    return '';
}

/* ===== 当前正式楼中楼接口 =====
 * 起点 H5 官方：getparagraphreviewshare(rootReviewId, pg, pz)
 * 只保留这一条已验证稳定的分页链。
 */
function qfReplyShareExtract2938(root,rootId){
    var rows=[],seen={},seenObj=[],bestTotal=0,visited=0;
    var rootS=String(rootId||'');

    function num(v){var n=Number(v);return isFinite(n)&&n>=0?n:0;}
    function idOf(x){
        x=x||{};
        return String(
            x.ReviewId||x.reviewId||
            x.CommentId||x.commentId||
            x.Id||x.id||x.PostId||x.postId||''
        );
    }
    function parentOf(x){
        x=x||{};
        return String(
            x.RootReviewId||x.rootReviewId||
            x.RefferCommentId||x.refferCommentId||
            x.RefCommentId||x.refCommentId||
            x.ParentId||x.parentId||''
        );
    }
    function nameOf(x){
        x=x||{};var u=x.UserInfo||x.userInfo||x.User||x.user||{};
        return String(
            x.UserName||x.userName||x.NickName||x.nickName||x.nickname||
            u.UserName||u.userName||u.NickName||u.nickName||u.nickname||''
        ).trim();
    }
    function contentOf(x){
        return String(textOf(x&&(
            x.Content||x.content||x.ReviewContent||x.reviewContent||
            x.PostContent||x.postContent||x.Body||x.body||x.Text||x.text
        ))||'').trim();
    }
    function addTotal(k,v){
        if(!/(reply.*count|count.*reply|totalcount|replytotal|total)$/i.test(String(k||'')))return;
        var n=num(v);if(n>bestTotal&&n<1000000)bestTotal=n;
    }
    function add(x,path){
        if(!x||typeof x!=='object'||Array.isArray(x))return;
        var ct=contentOf(x),nm=nameOf(x),id=idOf(x),par=parentOf(x);
        if(!ct)return;
        if(id&&rootS&&id===rootS)return; // 根评论本身不是回复

        /* share 接口是按 rootReviewId 单楼层返回。明确给出父 ID 时要求属于当前楼层；
           父 ID 缺失时，只接受 reply/list/comment/review 等语义路径中的对象。 */
        var sem=/reply|repl|quote|comment|review|data.*list|list/i.test(String(path||''));
        if(par&&rootS&&par!==rootS&&!sem)return;
        if(!par&&!sem)return;
        if(!nm&& !id)return;

        var key=id?('id:'+id):('sig:'+nm+'|'+ct+'|'+String(x.CreateTime||x.createTime||x.TimeStamp||x.timestamp||''));
        if(seen[key])return;seen[key]=1;
        rows.push(x);
    }
    function walk(v,path,d){
        if(v==null||d>9||visited>12000)return;
        if(typeof v!=='object')return;
        if(seenObj.indexOf(v)>=0)return;seenObj.push(v);visited++;
        if(Array.isArray(v)){
            for(var i=0;i<v.length;i++)walk(v[i],path+'['+i+']',d+1);
            return;
        }
        add(v,path);
        var c=0;
        for(var k in v){
            if(!Object.prototype.hasOwnProperty.call(v,k))continue;
            var z=v[k];
            if(typeof z==='number'||typeof z==='string')addTotal(k,z);
            if(z&&typeof z==='object')walk(z,path?path+'.'+k:k,d+1);
            if(++c>220)break;
        }
    }
    walk(root,'root',0);
    return {list:rows,total:bestTotal,visited:visited};
}


/* alpha29：作者说专用元数据恢复。
 * 这段只在作者说 BottomSheet 内执行，不进入正文/普通段评首屏。
 * getparagraphscommentcounts 的 AuthorReview 才是作者说社交实体；safegetcontent 只负责正文/作者资料。 */
function qfAuthorResolveMetaV529(){
    if(!isAuthor)return false;
    var best=null,seenObj=[],target=String(authorSay||'').replace(/[\s\u200b\u200c\u200d\ufeff]+/g,'').trim();
    function s(v){return String(v==null?'':v).trim();}
    function n(v){var x=Number(v);return isFinite(x)&&x>0?x:0;}
    function nt(v){return String(v==null?'':v).replace(/[\s\u200b\u200c\u200d\ufeff]+/g,'').trim();}
    function consider(ar,parent,path){
        if(!ar||typeof ar!=='object')return;parent=parent&&typeof parent==='object'?parent:{};
        var tx=s(ar.AuthorReview||ar.authorReview||''),nx=nt(tx),match=0;
        if(target&&nx){if(target===nx)match=700;else if(target.indexOf(nx)>=0||nx.indexOf(target)>=0)match=480;else{var a=target.slice(0,Math.min(28,target.length)),b=nx.slice(0,Math.min(28,nx.length));if(a&&b&&(target.indexOf(b)>=0||nx.indexOf(a)>=0))match=300;else return;}}
        else if(target)return;else match=40;
        var rid=s(ar.ReviewId||ar.reviewId||'');
        /* ParagraphCommentCountItem 的 CommentCount/ParagraphId 必须与 AuthorReview 整体取用，禁止跨节点 max 合并。 */
        var pid=s(parent.ParagraphId||parent.paragraphId||'');
        var cnt=n(parent.CommentCount||parent.commentCount||0);
        var rl=ar.ReplyList||ar.replyList||[];if(!Array.isArray(rl))rl=[];
        var score=match+(pid?120:0)+(cnt>0?100:0)+(rid?50:0);
        var c={reviewId:rid,paragraphId:pid,replyCount:cnt,replyList:rl,score:score,path:path||''};
        if(!best||c.score>best.score)best=c;
    }
    function walk(v,d,path){
        if(v==null||d>13||typeof v!=='object'||seenObj.indexOf(v)>=0)return;seenObj.push(v);
        if(Array.isArray(v)){for(var i=0;i<v.length;i++)walk(v[i],d+1,path+'['+i+']');return;}
        var ar=v.AuthorReview||v.authorReview;if(ar&&typeof ar==='object')consider(ar,v,path+'.AuthorReview');
        for(var k in v)if(Object.prototype.hasOwnProperty.call(v,k)&&v[k]&&typeof v[k]==='object')walk(v[k],d+1,path?path+'.'+k:k);
    }
    function attempt(profile,withPage){
        try{var params={bookId:String(bid),chapterId:String(cid)};if(withPage)params.reviewReadPage='0';var req=qfReaderSignedRequestV3245('v1/chapterreview/getparagraphscommentcounts',params,profile);var tx=qfDirectAjax(req.url,'GET',null,null,req.headers,5600),d=parse(tx);if(!d)return false;walk(d,0,'root');return !!best;}catch(_e){return false;}
    }
    attempt('reader_ext',true);if(!best)attempt('reader_legacy',true);if(!best)attempt('reader_ext',false);
    if(!best)return !!(authorParagraphId&&Number(authorReplyCount||0)>0);
    /* 这是权威整节点结果，必须允许真实 19 覆盖之前被其它数据污染的 119。 */
    authorReviewId=String(best.reviewId||'');
    authorParagraphId=String(best.paragraphId||'');
    authorReplyCount=Number(best.replyCount||0)||0;
    authorReplyList=Array.isArray(best.replyList)?best.replyList:[];
    return !!(authorParagraphId&&authorReplyCount>0);
}
/* alpha29：作者说回复优先走 APP 的章节评论详情接口。
 * 这是 AuthorReview 的专用详情链；普通 paragraph share API 对作者说 rootReviewId 并不稳定。 */
function qfAuthorDetailPageV529(rootId,pg,pz){
    var rootS=String(rootId||'');if(!isAuthor||!rootS)return null;
    pg=Math.max(1,Number(pg)||1);pz=Math.max(1,Number(pz)||20);
    function num(v){var x=Number(v);return isFinite(x)&&x>=0?x:0;}
    function contentOf(x){return String(textOf(x&&(x.Content||x.content||x.ReviewContent||x.reviewContent||x.PostContent||x.postContent||x.Body||x.body||x.Text||x.text))||'').trim();}
    function idOf(x){x=x||{};return String(x.ReviewId||x.reviewId||x.CommentId||x.commentId||x.Id||x.id||x.PostId||x.postId||'');}
    function extract(d){
        var rows=[],seen={},objs=[],total=0;
        function addTotal(k,v){if(/(reply.*count|commentcount|reviewcount|totalcount|replytotal|total)$/i.test(String(k||''))){var z=num(v);if(z>total&&z<1000000)total=z;}}
        function walk(v,dpth,path){
            if(v==null||dpth>11||typeof v!=='object'||objs.indexOf(v)>=0)return;objs.push(v);
            if(Array.isArray(v)){for(var i=0;i<v.length;i++)walk(v[i],dpth+1,path+'['+i+']');return;}
            var id=idOf(v),ct=contentOf(v),sem=/reply|comment|review|list|data/i.test(String(path||''));
            if(ct&&id&&id!==rootS&&sem){var key='id:'+id;if(!seen[key]){seen[key]=1;rows.push(v);}}
            for(var k in v){if(!Object.prototype.hasOwnProperty.call(v,k))continue;var z=v[k];if(typeof z==='number'||typeof z==='string')addTotal(k,z);if(z&&typeof z==='object')walk(z,dpth+1,path?path+'.'+k:k);}
        }
        walk(d,0,'root');return {list:rows,total:Math.max(total,rows.length)};
    }
    function attempt(params,profile,label){
        try{
            var req=qfReaderSignedRequestV3245('v1/chapterreview/getchapterreviewdetail',params,profile);
            var tx=qfDirectAjax(req.url,'GET',null,null,req.headers,6500),d=parse(tx);if(!d)return null;
            var ex=extract(d);if(ex.list.length||ex.total>0)return {list:ex.list,total:ex.total,raw:d,source:label,transport:'signed-argus',status:Number(d.Code!=null?d.Code:(d.code||0))||0};
        }catch(_e){}
        return null;
    }
    var variants=[
        {bookId:String(bid),chapterId:String(cid),reviewId:rootS,pg:String(pg),pz:String(pz)},
        {bookId:String(bid),chapterId:String(cid),rootReviewId:rootS,pg:String(pg),pz:String(pz)}
    ];
    for(var i=0;i<variants.length;i++){
        var r=attempt(variants[i],'reader_ext','author-detail/ext-'+i);if(r&&r.list.length)return r;
        if(!r){r=attempt(variants[i],'reader_legacy','author-detail/legacy-'+i);if(r&&r.list.length)return r;}
        if(r)return r;
    }
    return null;
}


/* alpha29.2：作者说的“查看 N 条回复”优先按作者所在章节末段落的评论流处理。
 * APK 同时存在 getchapterendchapterparagraphsreview / getchapterendchapterreview，且
 * ParagraphCommentCountItem 持有 ParagraphId + CommentCount + AuthorReview。
 * 因此这里不再要求 AuthorReview.ReviewId 一定存在。 */
function qfAuthorParagraphPageV532(pg,pz){
    var empty={list:[],total:0,source:'author-paragraph',attempts:[]};if(!isAuthor)return empty;
    pg=Math.max(1,Number(pg)||1);pz=Math.max(1,Number(pz)||20);
    try{qfAuthorResolveMetaV529();}catch(_m){}
    var exactPid=String(authorParagraphId||'').trim(),expected=Math.max(0,Number(authorReplyCount||0));
    var pids=[];function addPid(v){var x=String(v==null?'':v).trim();if(!x||pids.indexOf(x)>=0)return;pids.push(x);}addPid(exactPid);if(!exactPid){addPid('-1');addPid('0');}
    function titleCount(list){var n=0;list=Array.isArray(list)?list:[];for(var i=0;i<list.length;i++){var x=list[i]||{},r=x.raw||x,u=x.user_info||r.UserInfo||r.userInfo||{},a=r.TitleInfoList||r.titleInfoList||u.TitleInfoList||u.titleInfoList||[];if(Array.isArray(a)&&a.length)n++;}return n;}
    function parsePack(d,label,pid){
        if(!d)return null;var x=d.Data||d.data||d.Result||d.result||d,l=arr(x);if(!Array.isArray(l))l=[];
        if(!l.length){var c=[x.DataList,x.dataList,x.List,x.list,x.Reviews,x.reviews,x.ChapterDataList,x.chapterDataList,x.SegmentDataList,x.segmentDataList];for(var ci=0;ci<c.length&&!l.length;ci++)if(Array.isArray(c[ci]))l=c[ci];}
        if(l.length&&l[0]&&typeof l[0]==='object'&&(l[0].DataList||l[0].dataList)){var flat=[];for(var si=0;si<l.length;si++){var dl=l[si]&&(l[si].DataList||l[si].dataList||[]);if(Array.isArray(dl))flat=flat.concat(dl);}if(flat.length)l=flat;}
        var total=Number(x.TotalCount||x.totalCount||x.CommentCount||x.commentCount||x.ReviewCount||x.reviewCount||x.ChapterReviewTotalCount||x.chapterReviewTotalCount||0)||0;
        if(!l.length&&total<=0)return null;
        var score=(String(pid)===exactPid&&exactPid?180:0)+titleCount(l)*2;
        if(expected>0){
            if(total===expected)score+=420;else if(total>0)score+=Math.max(-260,160-Math.abs(total-expected)*8);
            var want=Math.min(expected,pz);if(l.length===want)score+=300;else score+=Math.max(-180,100-Math.abs(l.length-want)*18);
            /* 典型错误：作者真实19，但 -1/章末总流返回119且第一页20条。强力降权而不是立即采用。 */
            if(total>expected*2+10&&l.length>=Math.min(pz,expected+1))score-=500;
        }
        return {list:l,total:total||l.length,raw:d,source:label,rich:titleCount(l),score:score,pid:String(pid)};
    }
    var best=null;function take(pk){if(!pk)return;if(!best||Number(pk.score||0)>Number(best.score||0))best=pk;}
    function attempt(path,params,profile,label,pid){
        try{var req=qfReaderSignedRequestV3245(path,params,profile||'reader_ext');var tx=qfDirectAjax(req.url,'GET',null,null,req.headers,6200),d=parse(tx),pk=parsePack(d,label,pid);empty.attempts.push(label+':'+(pk?pk.list.length:0)+'/'+(pk?pk.total:0)+'/'+(pk?pk.score:0));take(pk);return pk;}catch(e){empty.attempts.push(label+':ERR');return null;}
    }
    /* 精确 ParagraphId 优先探测全部已知参数形态，但不再“第一个非空就返回”。 */
    for(var pi=0;pi<pids.length;pi++){
        var pid=pids[pi],variants=[
            {bookId:String(bid),chapterId:String(cid),paragraphId:pid,pg:String(pg),pz:String(pz)},
            {bookId:String(bid),chapterId:String(cid),paragraphId:pid,pageIndex:String(pg),pageSize:String(pz)},
            {bookId:String(bid),chapterId:String(cid),paragraphId:pid,page:String(pg),pageSize:String(pz)}
        ];
        for(var vi=0;vi<variants.length;vi++)attempt('v1/chapterreview/getchapterendchapterparagraphsreview',variants[vi],'reader_ext','author-end-paragraph/'+pid+'/'+vi,pid);
    }
    /* Reader 普通段落流同时参与评分；type0 有标签，type1 结构完整时做融合。 */
    for(var pj=0;pj<pids.length;pj++){
        var pv=pids[pj],base={bookId:String(bid),chapterId:String(cid),paragraphId:String(pv),pg:String(pg),pz:String(pz),anchorId:'0',from:'0'};
        var p0={};for(var k0 in base)p0[k0]=base[k0];p0.type='0';var r0=attempt('v2/chapterreview/getparagraphscomments',p0,'reader_ext','author-paragraph/type0/'+pv,pv);
        var p1={};for(var k1 in base)p1[k1]=base[k1];p1.type='1';var r1=attempt('v2/chapterreview/getparagraphscomments',p1,'reader_ext','author-paragraph/type1/'+pv,pv);
        if(r0&&r1&&r0.list.length&&r1.list.length){try{var fused=qfReviewFusePackV502(r1,r0)||r1;fused.score=Math.max(Number(r0.score||0),Number(r1.score||0))+60;fused.pid=String(pv);take(fused);}catch(_f){}}
    }
    /* 有精确作者 ParagraphId 时，禁止再落到无 ParagraphId 的整章末列表；这正是 alpha29.2 串到119的来源之一。 */
    if(best&&Number(best.score||0)>0){
        if(expected>0)best.total=expected; /* UI 数量使用已由整节点确认的真实 CommentCount。 */
        return best;
    }
    return empty;
}
/* alpha29.3：作者说统一回复页。
 * 1) 有真实 AuthorReview.ReviewId：必须优先按根评论取楼中楼；
 * 2) 根评论链确实无数据才尝试 Paragraph 流；
 * 3) Paragraph 流只能消费 Parent/RootReviewId 指向作者 ReviewId 的行，禁止整段直出。 */
function qfAuthorReplyPageV533(rootId,pg,pz,done){
    if(!isAuthor){qfReplySharePage2938(rootId,pg,pz,done);return;}
    /* 作者说原生“查看N条回复”实际是 AuthorReview 所属 ParagraphCommentCountItem 的评论流，
       不是普通 RootReviewId 楼中楼。先按精确 ParagraphId 取流；只有完全取不到才用 ReviewId 旧链兜底。 */
    var ap=null;try{ap=qfAuthorParagraphPageV532(pg,pz);}catch(_ap){}
    if(ap&&ap.list&&ap.list.length){try{if(typeof done==='function')done(ap);}catch(_cb){}return;}
    var rid=String(rootId||authorReviewId||'').trim();if(rid){qfReplySharePage2938(rid,pg,pz,done);return;}
    try{if(typeof done==='function')done(ap||{list:[],total:Number(authorReplyCount||0),source:'author-paragraph-empty'});}catch(_cb2){}
}
/* 兼容旧调用名。 */
function qfAuthorReplyPageV532(rootId,pg,pz,done){return qfAuthorReplyPageV533(rootId,pg,pz,done);}

function qfReplyV2Page2971(rootId,pg,pz){
    var empty={list:[],total:0,source:"app-v2-reply",transport:"signed-argus",status:0,error:"",attempts:[]};
    /* alpha28：楼中楼标签只在“点击展开”低频路径富化。
       type=3 仍是结构优先的正式回复链；如果它能返回回复但没有 TitleInfoList，
       再尝试 type=0 / type=1 的 Reader 富身份变体。任何额外请求都不会发生在段评首屏。 */
    function titleCount(pack){
        var n=0,seen=[];
        function has(o){
            if(!o||typeof o!=="object")return false;
            var a=o.TitleInfoList!==undefined?o.TitleInfoList:(o.titleInfoList!==undefined?o.titleInfoList:o.title_info_list);
            if(typeof a==="string"){try{a=JSON.parse(a)}catch(_e){a=[]}}
            return Array.isArray(a)&&a.length>0;
        }
        function walk(v,d){
            if(v==null||d>9||typeof v!=="object")return;
            if(seen.indexOf(v)>=0)return;seen.push(v);
            if(has(v))n++;
            if(Array.isArray(v)){for(var i=0;i<v.length;i++)walk(v[i],d+1);return;}
            for(var k in v){if(Object.prototype.hasOwnProperty.call(v,k)&&v[k]&&typeof v[k]==="object")walk(v[k],d+1);}
        }
        try{if(pack&&pack.list)walk(pack.list,0);if(pack&&pack.raw)walk(pack.raw,0);}catch(_e){}
        return n;
    }
    function prefProfile(){
        try{var v=String(localStorage.getItem("qf_qd_reader_profile_v400")||"");if(v==="reader_ext"||v==="reader_legacy")return v;}catch(_e){}
        return "reader_ext";
    }
    var rootS=String(rootId||"");if(!rootS)return empty;
    pg=Math.max(1,Number(pg)||1);pz=Math.max(1,Number(pz)||20);

    /* alpha3.7：作者说是章节末特殊 Review，para=-10 只是本书源 UI 哨兵，不能拿它判断客户端接口不可用。
       优先使用 getparagraphscommentcounts 返回的真实 ParagraphId；缺失时仅在作者说点击路径尝试 -1 / 0。 */
    var pids=[];
    function addPid(v){var s=String(v==null?'':v).trim();if(!s)return;if(pids.indexOf(s)<0)pids.push(s);}
    if(isAuthor){addPid(authorParagraphId);addPid('-1');addPid('0');}
    else if(isChapter){
        /* alpha18.1：本章说是特殊章节评论。以前 para=-1 被直接 return，导致只能降级
           到 share API，从而丢失楼中楼 TitleInfoList。Reader v2 低频展开时兼容 -1/0。 */
        addPid('-1');addPid('0');
    }else{
        var pn=Number(para);if(!isFinite(pn))return empty;
        if(pn===-1){addPid('-1');addPid('0');}
        else if(pn>0)addPid(String(pn));
        else return empty;
    }

    function extract(d){
        var x=d&&(d.Data||d.data||d.Result||d.result)||d||{};
        var ex=qfReplyShareExtract2938(d,rootS),rows=(ex&&ex.list)||[];
        var total=Math.max(Number(ex&&ex.total||0),Number(x.TotalCount||x.totalCount||x.ReplyCount||x.replyCount||x.RootReviewReplyCount||x.rootReviewReplyCount||0)||0,rows.length);
        /* 某些 v2 返回把列表直接放在 Data/List/ReplyList。递归提取为空时再补常见数组。 */
        if(!rows.length){
            var cand=x.ReplyList||x.replyList||x.DataList||x.dataList||x.List||x.list||x.Reviews||x.reviews||[];
            if(Array.isArray(cand))rows=cand;
            if(rows.length>total)total=rows.length;
        }
        return {list:rows,total:total};
    }
    function attempt(path,params,profile,label){
        try{
            var req=profile?qfReaderSignedRequestV3245(path,params,profile):qfDirectSignedRequest(path,params,false);
            var tx=qfDirectAjax(req.url,"GET",null,null,req.headers,6500),d=parse(tx);
            var code=d?Number(d.Code!=null?d.Code:(d.code!=null?d.code:0))||0:-999;
            var ex=d?extract(d):{list:[],total:0};
            empty.attempts.push(label+':'+code+'/'+ex.list.length+'/'+ex.total);
            if(ex.list.length||ex.total>0){
                var pack={list:ex.list,total:ex.total,raw:d,source:label,transport:"signed-argus",status:code,contentType:"application/json",keys:d?Object.keys(d).slice(0,18).join(","):"",message:d?String(d.Message||d.message||""):"",error:"",attempts:empty.attempts.slice()};
                pack.richTitles=titleCount(pack);
                return pack;
            }
        }catch(e){empty.attempts.push(label+':ERR');empty.error=String(e&&e.message?e.message:e);}
        return null;
    }

    /* 与普通段评楼中楼同级的 v2 专用接口。alpha28 不再“第一份非空就返回”：
       先保存结构可用结果；若缺标签，仅在本次点击展开里追加少量富身份探测。 */
    var bestReply=null,preferred=prefProfile();
    for(var pi=0;pi<pids.length;pi++){
        var pid=pids[pi];
        var base={bookId:String(bid),chapterId:String(cid),paragraphId:pid,pg:String(pg),pz:String(pz),type:"3",scene:"0",nextCursor:""};
        var a={};for(var k in base)a[k]=base[k];a.rootReviewId=rootS;
        var r=attempt("v2/chapterreview/getparagraphscommentsreview",a,"reader_ext","v2-reader-root/t3 pid="+pid);
        if(r){if(Number(r.richTitles||0)>0)return r;if(!bestReply)bestReply=r;}
        r=attempt("v2/chapterreview/getparagraphscommentsreview",a,"reader_legacy","v2-legacy-root/t3 pid="+pid);
        if(r){if(Number(r.richTitles||0)>0)return r;if(!bestReply)bestReply=r;}

        /* 只有 type=3 已经证明这个 rootReviewId 可用但缺标签时，才尝试富身份变体。
           这样不会为无回复/错误 ID 额外放大请求。 */
        if(bestReply){
            var richTypes=["0","1"];
            for(var ti=0;ti<richTypes.length;ti++){
                var c={};for(var k3 in base)c[k3]=base[k3];c.type=richTypes[ti];c.rootReviewId=rootS;
                var rr=attempt("v2/chapterreview/getparagraphscommentsreview",c,preferred,"v2-rich-root/t"+richTypes[ti]+" pid="+pid);
                if(rr&&Number(rr.richTitles||0)>0)return rr;
            }
        }

        /* 客户端版本间存在 rootReviewId / reviewId 命名差异。特殊评论流兼容 reviewId。 */
        if(isAuthor||isChapter||Number(para)===-1){
            var b={};for(var k2 in base)b[k2]=base[k2];b.reviewId=rootS;
            r=attempt("v2/chapterreview/getparagraphscommentsreview",b,preferred,"v2-reader-review/t3 pid="+pid);
            if(r){if(Number(r.richTitles||0)>0)return r;if(!bestReply)bestReply=r;}
            if(r&&Number(r.richTitles||0)<=0){
                var br={};for(var kb in b)br[kb]=b[kb];br.type="0";
                var rr2=attempt("v2/chapterreview/getparagraphscommentsreview",br,preferred,"v2-rich-review/t0 pid="+pid);
                if(rr2&&Number(rr2.richTitles||0)>0)return rr2;
            }
        }
    }
    if(bestReply)return bestReply;

    /* 最后尝试章节评论详情接口。APK 同时保留 v1/getchapterreviewdetail；只在作者说 v2 全部为空时触发。 */
    if(isAuthor){
        var details=[
            {bookId:String(bid),chapterId:String(cid),reviewId:rootS,pg:String(pg),pz:String(pz)},
            {bookId:String(bid),chapterId:String(cid),rootReviewId:rootS,pg:String(pg),pz:String(pz)}
        ];
        for(var di=0;di<details.length;di++){
            var rr=attempt("v1/chapterreview/getchapterreviewdetail",details[di],"reader_ext","detail-"+di);if(rr)return rr;
        }
    }
    return empty;
}

function qfReplySharePage2938(rootId,pg,pz,done){
    if(isAuthor&&!rootId){try{qfAuthorResolveMetaV529();rootId=authorReviewId||rootId;}catch(_arm){}}
    var rootS=String(rootId||'');
    pg=Math.max(1,Number(pg||1)||1);pz=Math.max(1,Number(pz||20)||20);
    var url2938='https://h5.if.qidian.com/argus/api/v1/chapterreview/getparagraphreviewshare?'+
        'rootReviewId='+encodeURIComponent(rootS)+'&pg='+encodeURIComponent(String(pg))+'&pz='+encodeURIComponent(String(pz));
    var finished=false;

    function finish(pack){
        if(finished)return;finished=true;
        var base=pack||{list:[],total:0,source:'share-api'};
        try{
            if(base&&base.list&&base.list.length){
                qfReviewMarkStructPackV502(base);
                base=qfReviewFusePackV502(base,v2pk)||base;
            }else if(v2pk&&v2pk.list&&v2pk.list.length){
                base=v2pk;
            }
        }catch(_fuseReply){}
        try{if(typeof done==='function')done(base);}catch(_cb){}
    }
    /* alpha18.2：楼中楼同样使用 share API 做结构骨架，Reader v2 只补回复用户 TitleInfoList。
       不再 Reader 一有数据就提前 return，否则回复分页/父子 ID 会和标签互相冲突。 */
    var v2pk=null;
    try{v2pk=qfReplyV2Page2971(rootS,pg,pz);}catch(_v2reply){v2pk=null;}
    /* alpha29：AuthorReview 先走专用 getchapterreviewdetail。拿到结构后仍与 Reader 富身份包融合，
       因而作者说回复也复用 alpha28 的 TitleInfoList 标签能力。 */
    if(isAuthor&&rootS){
        try{
            var adp=qfAuthorDetailPageV529(rootS,pg,pz);
            if(adp&&adp.list&&adp.list.length){
                qfReviewMarkStructPackV502(adp);
                if(v2pk)adp=qfReviewFusePackV502(adp,v2pk)||adp;
                finish(adp);return;
            }
        }catch(_adp){}
    }
    function parseText(text,status,transport,ct){
        var d=null,err='',keys='',msg='';
        try{d=JSON.parse(String(text||''));}catch(e){err='非JSON '+String(text||'').slice(0,110).replace(/\s+/g,' ');}
        if(!d)return {list:[],total:0,source:'share-api',status:Number(status||0),transport:transport||'',contentType:ct||'',error:err};
        try{keys=Object.keys(d).slice(0,18).join(',');}catch(_k){}
        try{msg=String(d.Message||d.message||d.Msg||d.msg||'');}catch(_m){}
        var ex=qfReplyShareExtract2938(d,rootS);
        var total=Number(ex.total||0)||0;
        /* 常见顶层/数据层总数再补一遍。 */
        try{
            var x=d.Data||d.data||d.Result||d.result||d;
            total=Math.max(total,Number(
                x.TotalCount||x.totalCount||x.Total||x.total||
                x.ReplyCount||x.replyCount||x.RootReviewReplyCount||x.rootReviewReplyCount||0
            )||0);
        }catch(_t){}
        return {list:ex.list||[],total:total,source:'share-api',status:Number(status||0),transport:transport||'',contentType:ct||'',keys:keys,message:msg,visited:ex.visited||0,error:''};
    }
    function javaFallback(prev){
        try{
            if(!(window.java&&typeof window.java.ajax==='function')){finish(prev);return;}
            var opt={method:'GET',timeout:12000,headers:{
                'User-Agent':'Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36',
                'Accept':'application/json,text/plain,*/*',
                'Referer':'https://h5.if.qidian.com/new/chapterreview/'
            }};
            var tx=String(window.java.ajax(url2938+','+JSON.stringify(opt))||'');
            var pk=parseText(tx,0,'java.ajax','');
            if(!pk.list.length&&prev&&prev.error)pk.error=(pk.error?pk.error+'; ':'')+'xhr='+prev.error;
            finish(pk);
        }catch(e){
            if(prev){prev.error=(prev.error?prev.error+'; ':'')+'java.ajax='+String(e&&e.message?e.message:e);finish(prev);}
            else finish({list:[],total:0,source:'share-api',transport:'java.ajax',error:String(e&&e.message?e.message:e)});
        }
    }

    try{
        var xhr=new XMLHttpRequest();
        xhr.open('GET',url2938,true);
        xhr.withCredentials=true;
        try{xhr.setRequestHeader('Accept','application/json,text/plain,*/*');}catch(_h){}
        xhr.onreadystatechange=function(){
            if(xhr.readyState!==4)return;
            var ct='';try{ct=String(xhr.getResponseHeader('content-type')||'');}catch(_ct){}
            var pk=parseText(xhr.responseText,xhr.status,'webview-xhr',ct);
            if(pk.list.length||(!pk.error&&/^application\/json/i.test(ct))){finish(pk);return;}
            javaFallback(pk);
        };
        xhr.onerror=function(){javaFallback({list:[],total:0,source:'share-api',status:Number(xhr.status||0),transport:'webview-xhr',error:'XHR error'});};
        xhr.ontimeout=function(){javaFallback({list:[],total:0,source:'share-api',status:Number(xhr.status||0),transport:'webview-xhr',error:'XHR timeout'});};
        xhr.timeout=12000;
        xhr.send(null);
    }catch(e){
        javaFallback({list:[],total:0,source:'share-api',transport:'webview-xhr',error:String(e&&e.message?e.message:e)});
    }
}

function loadMoreReplies(rootId,host,btn,total){
    if(!rootId||!host||!btn)return;
    if(btn.getAttribute('data-loading')==='1')return;

    btn.setAttribute('data-loading','1');
    btn.textContent='正在加载更多回复…';
    try{var n0=host.querySelector('.localReplyNotice');if(n0)n0.remove();var d0=host.querySelector('.qfReplyDiag2931');if(d0)d0.remove();}catch(_clear){}

    var already={};
    try{
        var nodes=host.querySelectorAll('[data-rid]');
        for(var ni=0;ni<nodes.length;ni++){
            var kk=String(nodes[ni].getAttribute('data-rid')||'');if(kk)already['id:'+kk]=1;
            try{
                var rn=String(nodes[ni].querySelector('.rName')&&nodes[ni].querySelector('.rName').textContent||'');
                var rc=String(nodes[ni].querySelector('.rContent')&&nodes[ni].querySelector('.rContent').textContent||'');
                if(rn||rc)already['sig:'+rn+'|'+rc.replace(/^回复\s*[^：:]+[：:]\s*/, '')]=1;
            }catch(_sig){}
        }
    }catch(_nodes){}

    function adaptNew(rows){
        var out=[];
        for(var i=0;i<rows.length;i++){
            var c=adaptReply(rows[i]);
            if(!c||!String(c.content||'').trim())continue;
            var id=String(c.id||'');
            var k1=id?'id:'+id:'';
            var k2='sig:'+String(c.name||'')+'|'+String(c.content||'').replace(/^回复\s*[^：:]+[：:]\s*/, '');
            if((k1&&already[k1])||already[k2])continue;
            if(k1)already[k1]=1;already[k2]=1;out.push(c);
        }
        return out;
    }
    function renderRows(out,pk,pageNo){
        if(!out.length)return false;
        var h='';for(var j=0;j<out.length;j++)h+=replyHtml(out[j]);
        btn.insertAdjacentHTML('beforebegin',h);
        setTimeout(function(){qfApplyFolds(host)},0);
        var shown=host.querySelectorAll('.reply').length;
        var reported=Math.max(Number(total||0),Number(pk&&pk.total||0),shown);
        var remain=Math.max(0,reported-shown);
        btn.removeAttribute('data-loading');btn.removeAttribute('data-reply-retry');
        btn.setAttribute('data-reply-source','share-api');
        btn.setAttribute('data-reply-page',String(pageNo+1));
        if(remain<=0)btn.remove();
        else btn.textContent='继续加载剩余 '+remain+' 条回复';
        return true;
    }
    function diagnostic(pk,pageNo,extra){
        btn.removeAttribute('data-loading');
        btn.textContent='更多回复暂时加载失败 · 点此重试';
        btn.setAttribute('data-reply-retry','1');
    }

    var pageNo=Number(btn.getAttribute('data-reply-page')||1);
    if(!isFinite(pageNo)||pageNo<1)pageNo=1;

    function requestPage(pg,hops){
        qfAuthorReplyPageV532(rootId,pg,20,function(pk){
            try{
                if(!btn||!btn.parentNode)return;
                var raw=(pk&&pk.list)||[];
                var out=adaptNew(raw);
                if(renderRows(out,pk,pg))return;

                /* 第 1 页有时会包含与首屏相同的两条预览；若还有未显示回复，自动试下一页。 */
                var shown=host.querySelectorAll('.reply').length;
                var reported=Math.max(Number(total||0),Number(pk&&pk.total||0));
                if(raw.length&&reported>shown&&hops<2){
                    btn.textContent='第一页为已显示回复，正在继续…';
                    requestPage(pg+1,hops+1);return;
                }
                diagnostic(pk,pg,raw.length?'当前页全部与已显示回复重复':'share-api 未返回回复列表');
            }catch(e){diagnostic(pk,pg,'解析异常='+String(e&&e.message?e.message:e).slice(0,120));}
        });
    }

    requestPage(pageNo,0);
}

/* alpha29.2：作者说回复允许直接依赖 ParagraphId + CommentCount 建立作者段落评论流。
 * 只要 AuthorReview.ReviewId 可用，详情页打开后就低频探测官方楼中楼第一页；
 * 得到真实 total 后动态补“查看 N 条回复”，同时把第一页回复预先放进隐藏容器。 */
function qfAuthorReplyProbeV408(){
    if(!isAuthor)return;
    var card=listEl.querySelector('.comment');if(!card||card.getAttribute('data-author-reply-probed')==='1')return;
    card.setAttribute('data-author-reply-probed','1');
    try{qfAuthorResolveMetaV529();}catch(_meta){}

    function streamId(){return String(authorReviewId||('authorp_'+String(authorParagraphId||'end').replace(/[^0-9A-Za-z_-]/g,'_')));}
    function mount(total){
        total=Math.max(0,Number(total||0));if(total<=0)return;
        authorReplyCount=total;
        var sid=streamId(),oldT=card.querySelector('.replyToggle');if(oldT)oldT.remove();
        var oldR=card.querySelector('.replies');if(oldR)oldR.remove();
        card.insertAdjacentHTML('beforeend','<div class="replyToggle qfAuthorReplyToggle" data-reply="'+esc(sid)+'" data-root="'+esc(sid)+'" data-total="'+total+'">查看'+total+'条回复 <svg viewBox="0 0 24 24"><path d="m9 6 6 6-6 6"></path></svg></div><div class="replies hidden" id="rp_'+esc(sid)+'"></div>');
    }
    if(Number(authorReplyCount||0)>0){mount(authorReplyCount);return;}

    /* alpha29.2：即使没有 AuthorReview.ReviewId，也直接探测作者段落评论第一页。
       这与起点章节内“查看 N 条回复”的实际数据模型更一致。 */
    qfAuthorReplyPageV532(authorReviewId||'',1,20,function(pk){
        try{if(!card||!card.parentNode)return;var total=Math.max(Number(pk&&pk.total||0),Number((pk&&pk.list||[]).length));mount(total);}catch(_e){}
    });
}

/* alpha28.1：第一次展开直接加载正式楼中楼第1页。
 * 根评论 embedded replyList 往往只有1~2条，且不带 TitleInfoList；它现在仅保留为失败兜底。
 * 这里完全复用 qfReplySharePage2938，所以首批回复与“继续加载”回复经过同一 share骨架 + Reader富化链。 */
function qfLoadInitialRepliesV281(rootId,host,total){
    if(!rootId||!host)return;
    if(host.getAttribute('data-qf-initial-loaded')==='1'||host.getAttribute('data-qf-initial-loading')==='1')return;
    host.setAttribute('data-qf-initial-loading','1');
    var fallback='';try{fallback=host.innerHTML;}catch(_fb){}
    host.innerHTML='<div class="replyMore" style="cursor:default">正在加载完整回复…</div>';

    qfAuthorReplyPageV532(rootId,1,20,function(pk){
        try{
            if(!host)return;
            var raw=(pk&&pk.list)||[],rows=[],seen={};
            for(var i=0;i<raw.length;i++){
                var c=adaptReply(raw[i]);if(!c||!String(c.content||'').trim())continue;
                var id=String(c.id||''),sig=String(c.name||'')+'|'+String(c.content||'').replace(/^回复\s*[^：:]+[：:]\s*/, '');
                var key=id?('id:'+id):('sig:'+sig);if(seen[key])continue;seen[key]=1;rows.push(c);
            }
            if(!rows.length){
                /* 正式接口偶发失败时恢复 embedded 预览，不让楼中楼变成空白。下次重新展开仍可再试。 */
                host.innerHTML=fallback||'<div class="replyMore">回复暂时加载失败</div>';
                host.removeAttribute('data-qf-initial-loading');
                return;
            }
            var h='';for(var r=0;r<rows.length;r++)h+=replyHtml(rows[r]);
            var reported=Math.max(Number(total||0),Number(pk&&pk.total||0),rows.length),remain=Math.max(0,reported-rows.length);
            if(remain>0){
                h+='<div class="replyMore replyMoreLocal" data-root="'+esc(rootId)+'" data-root-alt="" data-root-list="'+esc(rootId)+'" data-total="'+reported+'" data-reply-page="2">继续加载剩余 '+remain+' 条回复</div>';
            }
            host.innerHTML=h;
            host.setAttribute('data-qf-initial-loaded','1');
            host.removeAttribute('data-qf-initial-loading');
            setTimeout(function(){qfApplyFolds(host)},0);
        }catch(_e){
            try{host.innerHTML=fallback;host.removeAttribute('data-qf-initial-loading');}catch(_x){}
        }
    });
}

function loadReplies(id,host,toggle,total){
    if(!host||!toggle)return;

    var hidden=host.classList.contains('hidden');

    if(hidden){
        host.classList.remove('hidden');
        toggle.innerHTML=
            '收起回复 <svg viewBox="0 0 24 24"><path d="m6 15 6-6 6 6"></path></svg>';
        /* alpha29：作者说也进入同一个 canonical 首次分页器。probe 只解析真实 rootReviewId/total，
           不再维护另一套回复列表逻辑。 */
        if(host.getAttribute('data-qf-initial-loaded')!=='1')qfLoadInitialRepliesV281(id,host,total);
        else setTimeout(function(){qfApplyFolds(host)},0);
    }else{
        host.classList.add('hidden');
        toggle.innerHTML=isAuthor
            ?('查看'+Number(total||0)+'条回复 <svg viewBox="0 0 24 24"><path d="m9 6 6 6-6 6"></path></svg>')
            :('展开全部'+Number(total||0)+'条回复 <svg viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"></path></svg>');
    }
}
function initTheme(){var m='';try{m=localStorage.getItem('qidian_comment_theme')||''}catch(e){}if(m!=='dark'&&m!=='light'){try{m=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}catch(e2){m='light'}}document.body.classList.toggle('dark',m==='dark');document.getElementById('themeBtn').onclick=function(){var d=!document.body.classList.contains('dark');document.body.classList.toggle('dark',d);try{localStorage.setItem('qidian_comment_theme',d?'dark':'light')}catch(e){}}}
function initQuote(){var show=true;try{show=localStorage.getItem('qidian_comment_quote')!=='0'}catch(e){}function apply(){quoteCard.textContent=quoteText||'';quoteWrap.classList.toggle('hidden',!show||!quoteText);document.getElementById('quoteBtn').classList.toggle('quote-on',show)}document.getElementById('quoteBtn').onclick=function(){show=!show;try{localStorage.setItem('qidian_comment_quote',show?'1':'0')}catch(e){}apply()};window._applyQ=apply;apply()}
document.getElementById('tabs').onclick=function(e){var x=e.target;while(x&&x!==this&&!x.getAttribute('data-tab'))x=x.parentNode;if(x&&x.getAttribute('data-tab'))switchTab(x.getAttribute('data-tab'))};document.getElementById('sortRow').onclick=function(e){var x=e.target;if(x&&x.getAttribute('data-sort'))switchSort(x.getAttribute('data-sort'))};moreEl.onclick=load;listEl.onclick=function(e){var z=e.target;
var arc=z;while(arc&&arc!==listEl&&!(arc.getAttribute&&arc.getAttribute('data-audiorole')))arc=arc.parentNode;
if(arc&&arc.getAttribute&&arc.getAttribute('data-audiorole')){audioRoleFilter=String(arc.getAttribute('data-audiorole')||'all');qfAudioRenderDirectPage();return;}
var fb=z;while(fb&&fb!==listEl&&!(fb.classList&&fb.classList.contains('foldBtn')))fb=fb.parentNode;if(fb&&fb.classList&&fb.classList.contains('foldBtn')){qfToggleFold(fb);return;}
var rt=z;while(rt&&rt!==listEl&&!(rt.classList&&rt.classList.contains('retryBtn')))rt=rt.parentNode;if(rt&&rt.classList&&rt.classList.contains('retryBtn')){reset();load();return;}

/* 配音：当前段评页内控制起点官方媒体对象，不跳网页。 */
var ap=z;
while(ap&&ap!==listEl&&!(ap.classList&&ap.classList.contains('qfAudioPlayer')))ap=ap.parentNode;

if(ap&&ap.classList&&ap.classList.contains('qfAudioPlayer')){
    var stAudio=qfAudioEnsureState(ap);

    if(z.classList&&z.classList.contains('qfAudioToggle')){
        qfAudioToggle(stAudio);
        return;
    }

    var prog=z;
    while(prog&&prog!==ap&&!(prog.classList&&prog.classList.contains('qfAudioProgress')))prog=prog.parentNode;
    if(prog&&prog.classList&&prog.classList.contains('qfAudioProgress')){
        qfAudioSeek(stAudio,e,prog);
        return;
    }
}

/* v2.9.27：楼中楼不再嵌入官方网页。 */
var oi=z;
while(oi&&oi!==listEl&&!(oi.classList&&oi.classList.contains('officialInlineToggle')))oi=oi.parentNode;
if(oi&&oi.classList&&oi.classList.contains('officialInlineToggle')){
    oi.classList.remove('officialInlineToggle');
    oi.textContent='重试获取剩余回复';
    return;
}
if(z&&z.classList&&z.classList.contains('zoom')){document.getElementById('lightboxImg').src=z.src;document.getElementById('lightbox').classList.remove('hidden');return}var more=z;
while(more&&more!==listEl&&!(more.classList&&more.classList.contains('replyMoreLocal')))more=more.parentNode;
if(more&&more.classList&&more.classList.contains('replyMoreLocal')){
    var root=more.getAttribute('data-root');
    var totalMore=Number(more.getAttribute('data-total')||0);
    loadMoreReplies(root,more.parentNode,more,totalMore);
    return;
}
while(z&&z!==listEl&&!(z.classList&&z.classList.contains('replyToggle')))z=z.parentNode;if(z&&z.classList&&z.classList.contains('replyToggle')){var id=z.getAttribute('data-reply'),rootId=z.getAttribute('data-root')||id,host=document.getElementById('rp_'+id),card=z.parentNode,c=card?card.querySelector('.comment'):null;var total=Number(z.getAttribute('data-total')||0);if(!total){var m=z.textContent.match(/(\d+)/);if(m)total=Number(m[1])}loadReplies(rootId,host,z,total)}};document.getElementById('lightbox').onclick=function(){this.classList.add('hidden')};
initTheme();initQuote();if(isAuthor){document.getElementById('tabs').innerHTML='<div class="tab active" style="margin-right:0">作者说</div>';document.getElementById('sortRow').classList.add('hidden');document.getElementById('quoteBtn').classList.add('hidden');quoteWrap.classList.add('hidden')}else{document.getElementById('sortRow').classList.toggle('hidden',currentTab==='audio'||currentTab==='image');document.body.classList.toggle('audioMode',currentTab==='audio');document.body.classList.toggle('imageMode',currentTab==='image');}var toTop=document.getElementById('toTop');if(toTop)toTop.onclick=function(){try{window.scrollTo({top:0,behavior:'smooth'})}catch(_st){window.scrollTo(0,0)}};load();window.addEventListener('scroll',function(){
    var h=Math.max(document.body.scrollHeight,document.documentElement.scrollHeight),
        y=window.scrollY||document.documentElement.scrollTop||0,
        v=window.innerHeight||document.documentElement.clientHeight;
    if(toTop)toTop.classList.toggle('hidden',y<900);
    if(currentTab==='image'||currentTab==='audio')return;
    if(ended||loading)return;
    if(h-y-v<850)load();
},{passive:true});
})();</script></body></html>`;}