## 2026-08-27 — JMComic 0.1.0-beta8 login credentials + AVS auth

Status: Beta/Test; awaiting user real-device confirmation.

Real-device finding:

- Core browsing, TOC/content and current detail/comment work had already progressed, but account login still failed.
- Root compatibility issue: the source read login fields only through legacy `getLoginInfo()`; the current reader path used by the proven Picacg source is `getLoginInfoMap()`.

Changes:

- 登录页优先使用 `source.getLoginInfoMap()` 读取账号/密码，兼容旧 `getLoginInfo()`。
- APP 登录优先 `18comicAPP`，并兼容 `2.1.2 / 2.0.20` 两个 APP 版本。
- 登录返回 `s` 保存为 AVS，并在后续 API 请求显式携带 `Cookie: AVS=...`。
- Cookie 写入改用当前阅读上下文 `ctx.cookie`，显式请求头作为兜底。
- 新增手动网页登录、登录状态和清除登录按钮。
- Beta5 已确认的正文/目录与 Beta7 详情/评论模块冻结。
- Published SHA256: `b6e5efbe29ea2018f1d3246e0e1ce0d9e0347efb4818afd4e9496f69734d7514`.


## 2026-08-27 — JMComic 0.1.0-beta7 comment bridge + detail tags

Status: Beta/Test; awaiting user real-device confirmation.

Real-device finding:

- Beta6 can resolve the numeric JM ID and open the independent comment page.
- The page then fails with “未知操作”, proving the remaining failure is the WebView/reader bridge protocol, not album identity or the comment API.

Changes:

- 评论桥同时接受 `action` 与 `op`；修复 Beta6 页面发送 `op:list/post` 而桥只判断 `action` 的协议错位。
- 列表响应同时返回 `list / total / data`，修复页面从错误层级读取评论数据。
- APP /forum、Web 评论兜底、发表评论和回复链保持不变。
- 详情参考哔咔成熟交互和 Venera 信息层级，新增可点击作者、原作、分类/标签。
- 作品数据调整为浏览/点赞、评论/章节、JM编号/线路三行，并补充更新时间。
- Beta5 已确认正常的目录/正文、图片分流和反混淆继续冻结。
- Published SHA256: `6423393d9dfcf10845400fe2916a922cd7cf013a359314175e4155e393a2b6f1`.


## 2026-08-27 — JMComic 0.1.0-beta6 robust comment identity + comment UI

Status: Beta/Test; awaiting user real-device confirmation.

Real-device finding:

- Beta5 manga content is confirmed working and is frozen.
- Detail “查看评论” and the top custom button both reached the callback but failed with “无法识别漫画 ID”, proving the remaining failure is identity recovery rather than the comment API.

Changes:

- 搜索/发现阶段持久保存规范化标题、封面路径到 JM ID 的映射。
- 详情/定制按钮统一使用显式 ID、bookUrl/ruleUrl/baseUrl、canonical/og:url、标题/封面映射多级解析。
- 详情“查看评论 / 收藏作品”直接携带 JM ID + 标题 + 封面三重上下文。
- 顶部 customButton 使用同一个 resolver，不再只依赖当前 book/baseUrl。
- 详情作品数据新增 JM 编号、评论数与当前线路。
- 评论页优化页面 title、卡片、楼中楼时间、页码和回复目标；评论数据模型不改。
- Beta5 目录/正文、APP `/chapter image` 字段兼容、图片分流与反混淆冻结。
- Published SHA256: `c36f64b73b3865a6ac0b1d07de2ae1a85b27407b04f54fe5b47ba189ecf65b69`.


## 2026-08-27 — JMComic 0.1.0-beta5 detail/content/comment hotfix

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 详情“查看评论 / 收藏作品”直接绑定当前漫画 ID，不再依赖点击上下文重新识别。
- 详情名称、封面、作者、简介和标签回归原始禁漫网页源已验证选择器，APP/API 仅作为附加数据。
- 正文优先读取当前网页章节 `data-original` 图片链。
- APP `/chapter` 图片对象补齐 `image` 字段解析，修复“正文没有图片”。
- Web 主动请求保留为第三兜底，图片分流与 JM 反混淆保持。
- 评论中心继续优化卡片、楼中楼、页码、回复目标和暗色模式；已恢复的评论数据模型不改。
- Published SHA256: `3266fae2495344cf8efbee76a2bef692f0530671d81a794336a485fcdc7e791b`.


## 2026-08-27 — JMComic 0.1.0-beta4 detail HTML + TOC fallback fix

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 详情 JS 返回内容加入 `<usehtml>` 包装，修复 `@onclick` 按钮被直接显示为文字。
- 公共 jsLib 移除对规则局部 `baseUrl` 的直接访问，详情/正文通过安全上下文解析 ID。
- 详情预先生成真实 Web album 目录地址。
- 目录回归原始禁漫源已验证的 `class.btn-toolbar.0@tag.a||.reading` 选择器。
- 章节正文继续支持 Auto / APP/API / Web 路线，目录与正文 Provider 解耦。
- Beta3 评论 HTML、头像和楼中楼修复冻结保留。
- Published SHA256: `df81fa4a10ab178454c0a59c52dd3ee0bf5ed9ef1da06704c04df4a5fb352598`.


## 2026-08-27 — JMComic 0.1.0-beta3 detail/comment/TOC hotfix

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 详情页互动区与作品数据改为 JS 动态生成，修复 `@onclick` / `@get` 被当普通文本显示。
- 评论按 JM APP 实际 `CID / UID / replys / photo` 字段解析，HTML 正文转纯文本并补全用户头像 URL。
- 目录改为 Java List + `@json`；APP `series` 缺失时回退原始 Web `.btn-toolbar / .reading` 目录链，并强制 `book.type=64`。
- 保留 Beta2 已恢复的发现/分类与登录页 `this.java` 兼容修复。
- 仓库源恢复完整内联 jsLib，不再在初始化阶段执行 Beta1 Raw runtime loader。
- Published SHA256: `fb8332ac2d79ffcf9deb7cb4b9030debbac83ac768c073d493f6fb7d0d23b12f`.


## 2026-08-26 — Qidian Next 1.1.0-beta16 circle detail click hotfix

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 恢复 Beta14 已验证的紧凑帖子详情按钮，不再把完整图片数组塞进 DOM 属性。
- 初始列表与动态筛选列表的多图均按 postId 保存在当前 WebView 内存，详情打开后继续与官方详情图片去重合并。
- Beta15 投票尾元数据精确清理保留。
- 其它书友圈功能及搜索/目录/正文 Provider/角色卡/账号链冻结。
- Published SHA256: `9928790859b54ca8e2fcc8bea3048a34c21d6643c4bf2af31a302b53e0a97f38`.


## 2026-08-26 — Qidian Next 1.1.0-beta15 circle detail multi-image fix

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 书友圈列表已有的完整正文图片数组随帖子详情入口传递，不再只保留第一张图。
- 帖子详情将列表预览图与 getpostdetail 返回图按原顺序去重合并，最多 9 张。
- 详情正文仅过滤尾部明确的 Options / VoteId / VoteType 投票结构元数据。
- 评论/楼中楼、分类筛选、同人视频、搜索、目录、正文 Provider、角色卡与账号链冻结。
- Published SHA256: `74432416de1891f939b1e78c3395c9f910b5acc3f6669d3d02c29245b94d8b65`.


## 2026-08-26 — Qidian Next 1.1.0 Stable

Status: Stable; user explicitly requested promotion after Beta14 real-device confirmation.

Changes:

- Promoted the exact `1.1.0-beta14` functional baseline to Stable; no new business behavior added.
- Retained rich detail metadata and synopsis, with only the latest-update time shown.
- Retained fixed two-column metrics: month-ticket / collection / fans on the left, remaining available metrics on the right.
- Retained compact shortcuts and direct detail-page content settings entry.
- Search, catalog, content Providers, reviews, role card, book circle and account domains remain on the Beta14 baseline.
- Published Stable SHA256: `c62b0b60dd91f472cac03f16e4853ca0cd1a181d75054e68c5ea29883999c17b`.


## 2026-08-26 — Qidian Next 1.1.0-beta14 fixed metric columns + direct content settings

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 详情作品数据改为固定左右列：月票 / 收藏 / 粉丝固定左列，其余可用指标固定右列。
- 继续使用真实 HTML 换行和全角空格补位，不使用已在真机失败过的 table / pre / CSS 固定列宽方案。
- 快捷入口缩短为书友圈 / 角色卡 / 正文设置三枚紧凑按钮，减少不均匀换行。
- 原“正文源状态”入口改为详情页直达正文设置；新增 jsLib 全局自包含设置页，避免 loginUrl 作用域导致 qfMultiContentV423 未定义。
- 正文设置页可直接修改正文源类别、各类别 Provider 和 STV API 密钥，并写回原登录信息映射。
- 搜索、目录、正文 Provider 实际解析、评论、角色卡、书友圈和账号链冻结。
- Published SHA256: `cc603bafc03e270b4e76ab2b933f06371fbefa6bf5ce732ae5867d8d4ae76b66`.


## 2026-08-26 — Qidian Next 1.1.0-beta13 latest-update + two-column recovery

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 详情页作品资料只保留“最近更新”，彻底移除首发时间展示。
- 删除连载书超过 60 天即清空更新时间的错误阈值；只保留空值与明显未来时间保护。
- 时间缓存与起点官方搜索详情缓存升级到 v1113，避免 Beta12 错误时间缓存继续命中。
- 作品数据不再使用 pre/monospace/CSS 列宽；改成每两个指标使用真实 HTML 换行，主指标优先总推荐/月票、收藏/粉丝、盟主/首订。
- Beta12 跨作用域正文设置回调回退为已验证的正文源状态全局入口，消除 qfMultiContentV423 未定义报错。
- 搜索、目录、正文 Provider、评论、角色卡、书友圈和账号链冻结。
- Published SHA256: `6ab1f6c3b40d3e9ece1a29e7c50164eabf6822beec287f68305d0e6f82472286`.


## 2026-08-26 — RSS UI 0.4.1-beta15 native stale-article cleanup

Status: Beta/Test; awaiting real-device confirmation.

Changes:

- Root cause confirmed from Legado source: old RSS rows are deleted by `clearOld` only when `ruleNextPage` is non-blank.
- Repository `ruleNextPage` changed from empty to `@js:''`: no real second page, but refresh now enters Legado's native old-row cleanup branch.
- Removed Beta14 `?reset=1` category URL churn; category and detail identities are fixed from this version onward.
- `subscription/rss.json` continues to expose exactly one repository entry.
- Rebuilt Picacg Stable RSS detail into the current `kind/title/badges/sections` schema so its detail page shows `◈ 哔咔漫画` instead of the repository fallback title.
- Picacg Stable book-source JSON and all Qidian book-source business logic are unchanged.


## 2026-08-26 — RSS UI 0.4.0-beta14 single-entry cleanup

Status: Beta/Test; user requested repository/subscription de-duplication after real-device screenshots showed historical RSS entries still visible.

Changes:

- The repository RSS catalog now exposes one current `🌈 阅读书源仓库` entry instead of separate Stable/Beta duplicates.
- The already-imported latest RSS `sourceUrl` identity is preserved so Beta13 updates in place rather than creating another subscription source.
- One deliberate cache migration resets the category identity for 漫画 / 仓库订阅 / 正式版 / 测试版; these identities are frozen after Beta14.
- `subscription/comic.json` remains one active Picacg entry only: `◈ 哔咔漫画 1.0.0 Stable`.
- Picacg Stable is confirmed present in `subscription/stable.json`; its RSS detail article identity is now the permanent non-versioned Stable detail URL.
- Historical Beta/detail/source files remain only for compatibility/history and are not active catalog entries.


## 2026-08-26 — Picacg 1.0.0 Stable

Status: Stable; user real-device confirmed and explicitly promoted.

Changes:

- Promoted the exact `1.0.0-beta9` functional baseline to Stable; no new business behavior was added during promotion.
- User confirmed the detail-page custom button is restored and opens the Picacg comment center.
- Retained one-shot recommendations (`page > 1` returns empty) plus independent ID/title/cover de-duplication.
- Retained APP/API + Web dual routes, login/account, comments/nested replies, likes/favourites, tags, TOC and manga image content.
- Stable source / Manifest / Stable subscription / Comic subscription / Stable bundle / Beta channel removal / Stable RSS detail were synchronized.
- Published source SHA256: `59fbc28ba9d168e95be9dc76a653391b111309009c3ae9d710e7b9aeda61170f`.


# RELEASE LOG

## 2026-08-26 — Picacg 1.0.0-beta9 recommendation hard-stop + startBrowser comment entry

Status: Beta/Test; awaiting user real-device confirmation.

Real-device finding from Beta8:

- 相关推荐超过约 10 部后仍会出现一部重复作品。
- 详情页顶部 customButton 仍无法进入评论页。

Changes:

- 推荐接口改为严格单页集合：直接使用阅读实际 page，`page > 1` 返回空，不再依赖 session 状态。
- 首批推荐按 ID、规范化标题、规范化封面路径三层独立去重；标题相同即视为重复，不再让作者/封面字段差异绕过去重。
- 顶部 customButton 删除 Rhino `runOnUiThread(function)` + `SourceLoginJsExtensions.showBrowser` 路径。
- 顶部按钮直接 `java.startBrowser(url,title,html)` 打开独立评论页；利用 WebViewActivity 本地 HTML 的官方 `run()` 注入桥继续运行评论/楼中楼/点赞/回复逻辑。
- 顶部按钮直接从 `book.bookUrl` 提取漫画 ID，不再为开评论先请求作品详情。
- 其它核心链冻结。
- Published SHA256: `b4d8e6d3fbfd6f0ce78d3cecc28c47ee6d0ddb463350d365474255935dae975e`.


## 2026-08-26 — Picacg 1.0.0-beta8 custom-button thread fix + recommendation session de-dup

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 详情页顶部 customButton 回调按 SourceCallBack 的 IO 线程模型修复：数据准备在后台完成，showBrowser 显式切回 Activity 主线程
- 相关推荐每次打开生成 session id，同一 session 仅返回一次推荐集合，阻止阅读发现页自动翻页重复追加
- 推荐结果同时按漫画 ID 与“标题 + 封面 + 作者”签名去重
- 书源显示名改为「◈ 哔咔漫画」，仓库新增 source-core 专属阅读源 SVG 图标
- 漫画正文 MangaMenu 本身仍没有 customButton；本版只修复详情页顶部已有定制按钮
- 其它核心链冻结
- Published SHA256: `d0d586c8259910f176ced7e79626b9cb42b1e4421b9a7ac3a1c198446b061c4b`.


## 2026-08-26 — Picacg 1.0.0-beta6 interaction order + concise source naming

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 互动区改为第一行「查看评论 / 相关推荐」，第二行「点赞作品 / 收藏作品」
- `bookSourceName` 精简为「🍥 哔咔漫画」，不再追加 APP/网页双线路、Beta、版本等长后缀
- 再次核对阅读当前上游：文本 `ReadMenu` 有 `tvCustomBtn`、`customButton` 可见性判断和 `CLICK_CUSTOM_BUTTON` 分发；图片 `MangaMenu` 没有，因此漫画正文无法仅靠书源 JSON 增加定制按钮
- 详情页定制按钮继续保留并直达评论；作品数据与作品信息布局保持 Beta5 基线
- 账号、评论、楼中楼、目录、漫画图片正文和 APP/Web 双线路核心链冻结
- Published SHA256: `7065d8566c3fc1dd7a41b1f6a4e7d1913d9a55632791eff1fc860478a7e0f153`.


## 2026-08-26 — Picacg 1.0.0-beta5 manga-menu finding and detail UI polish

Status: Beta/Test; core functions retained, detail UI awaits real-device confirmation.

Changes:

- 确认图片漫画正文使用 MangaMenu；当前 MangaMenu 布局/代码没有 customButton 控件与 clickCustomButton 分发，书源侧无法单独补出正文按钮
- 保留详情页 customButton 与评论回调，不改变 bookSourceType=2，避免退化漫画原生阅读体验
- 详情互动入口由 3+1 重排为 2×2：查看评论、点赞作品、收藏作品、相关推荐
- 作品数据改为双列三行：浏览/点赞、评论/章节、页数/状态
- 清空原生 wordCount 重复统计，顶部摘要仅保留主分类与连载状态
- 作者、汉化组、分类、标签点击能力及账号/评论/正文/双线路核心链保持不变
- Published SHA256: `6e7f1144f1d0d1cc3b6a6b884c3cf1ee42f1e36abc1ba3953e9849d097faa172`.


## 2026-08-26 — Picacg 1.0.0-beta4 reader custom-button + Venera-style detail enhancement

Status: Beta/Test; awaiting real-device confirmation.

Changes:

- 根据 Legado/Archive ReadMenu 机制，详情/目录/正文执行时再次确保当前 BookSource.customButton 与 eventListener 为 true
- 详情页重构为作品数据、描述、信息三个分区，降低顶部信息拥挤
- 新增上传者、上传时间、页数、允许下载、允许评论等元数据展示
- 作者、汉化组、分类、标签新增点击跳转；分类精确过滤，作者/汉化组走高级搜索
- 原生 kind 只保留主要分类与连载状态，完整 tags 下沉到信息区
- 评论中心、点赞/收藏、相关推荐、目录、正文图片及 APP/Web 请求核心链冻结
- Published SHA256: `1c806cc0181497c7cada9770008176b9d130e2469a482f8da2f95a01335311e1`.


## 2026-08-26 — Picacg 1.0.0-beta3 reader/comment tags enhancement

Status: Beta/Test; Beta2 core functions reported basically working on real device, Beta3 enhancements awaiting confirmation.

Changes:

- 漫画图片阅读页定制按钮强化，章节 URL / 当前书 / 最近书籍 ID 多级识别后直达评论中心
- 详情页把 API 已返回的 categories/tags 渲染成可点击入口，不增加详情首屏网络请求
- 新增标签页路由：分类精确过滤，普通标签过滤为空时回退 advanced-search
- 发现页分类按钮从四列调整为三列，减少真机文字省略
- 登录页重排 APP通道、登录及功能按钮，改善分组与触控面积
- 修复登录页“我的收藏”仍以 PICA_SOURCE_ID/.invalid 作为外层地址的残留问题
- 正文图片、评论接口、楼中楼、账号认证和双线路核心请求逻辑保持不变
- Published SHA256: `ba414a8394341f5ab9d5f8a190353c458ed7c52aeacf0cfa96134cbad74a088c`.


## 2026-08-26 — Picacg 1.0.0-beta2 SSL + Explore UI hotfix

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- 修复 .invalid 书源身份被误用于搜索/发现/章节外层网络请求，统一改用 manhuabika.com 作为可握手的 HTTPS 承载地址
- 自动模式首次优先网页线路，记住最近成功线路；当前线路网络/SSL失败时继续切换另一线路
- 发现页渲染阶段不再请求 /categories，避免打开分类页即触发网络异常
- 发现页重构为快捷入口、热门榜单、官方推荐、内容形态、题材偏好、作品·地区六个分区，采用紧凑四列布局
- Published SHA256: `bc9b8f1cff680c749c3dd5932097432412b1a6a55505114fe773c685ec72bc78`.


## 2026-08-26 — Picacg 1.0.0-beta1 Beta + repository type categories

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- Published the complete Picacg APP/Web dual-route Legado source to the Beta channel.
- Added permanent `漫画源` and `订阅源` repository categories while preserving Stable/Beta channels.
- Added the direct-repository-publication policy for future 阅读 sources.
- Rebuilt the Beta bundle without dropping existing Beta sources.
- Published SHA256: `30e683ac3ce2cb5069915b9b783e782ea399b7c9ea7f87ed5c22cb99b4320629`.


## 2026-08-26 — Qidian Next 1.1.0-beta9 detail rich fallback

Status: Beta/Test; awaiting user real-device confirmation.

Real-device finding:

- Beta8 still rendered only a small subset of detail metrics, proving APP `bookDetailInfo` is not a reliable sole enrichment path in the user environment.

Changes:

- Kept current-response/book-cache fast path and APP enrichment as the first layer.
- Restored cached qidiantu rich-detail fallback only when the detail remains sparse.
- Added exact-bookId Qidian mobile-search fallback for synopsis / reading / recommendation.
- Removed the Beta8 30-minute failure suppression behavior; negative caches are short-lived.
- Kept search/catalog/content/review/account domains frozen.
- Published SHA256: `d866eb0da45f0c08c8374208e03027f9a1fe0d919c0070bd64288622bd2461a5`.


## 2026-08-26 — Qidian Next 1.1.0-beta8 Beta

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- Restored the verified official APP `bookDetailInfo` detail-enrichment chain.
- Kept current-response parsing and book-variable caches as the zero-request fast path.
- Sparse detail pages make at most one official APP detail call with 30-minute deduplication.
- Removed the failed TTS-only enrichment request and temporary synopsis diagnostic UI.
- Search, catalog, content Providers, reviews, role cards, book circle, and Qingwu VIP auth remain frozen.
- Published SHA256: `55f9c4371cf2ee7522d330ae80f380b9aaf93d62384a60da01e598f9ac45008b`.

## 2026-08-26 — 起点增强 1.1.0-beta3

Status: Beta/Test; detail metadata sanitation awaiting real-device confirmation.

Changes:

- Block internal object keys/enums/ids/timestamps from tag and honor rendering.
- Tighten collection/fan metric trust and normalize author-level/status display.
- Keep zero extra synchronous detail requests and preserve the QW VIP-content fix.
- Stable 1.0.0 remains unchanged.
- Beta SHA256: `d2234efb2d9f62551386c8dbe5056320aab994df6fc34f448d30b68c1d72054c`.

## 2026-08-26 — 起点增强 1.1.0-beta2

Status: Beta/Test; detail richness/UI compatibility follow-up awaiting real-device confirmation.

Changes:

- Kept the beta1 zero-extra-request detail fast path.
- Restored richer work metadata, statistics, tags and honors from the current response or existing per-book cache.
- Replaced the incompatible metric `<table>` with plain HTML rows for Legado real-device compatibility.
- Missing metrics remain hidden instead of triggering synchronous enrichment requests.
- Preserved QW VIP-content authentication fix and Stable 1.0.0 unchanged.
- Beta SHA256: `98b2b75567eeb2a16e0821c653443241813f5de09f65b2b4f1c0e46c5fb6f4de`.

## 2026-08-26 — 起点增强 1.1.0-beta1

Status: Beta/Test; detail UI/performance redesign awaiting real-device confirmation.

Changes:

- Replaced blocking multi-provider detail augmentation with a current-response fast path; first render performs no extra synchronous APP/Web/Atom/third-party detail requests.
- Redesigned custom detail information into compact metrics, on-demand interaction entries, tags and synopsis.
- Preserved the 1.0.1-beta1 QW VIP-content authentication fix and all search/catalog/content/review Provider logic.
- Stable 1.0.0 remains unchanged.
- Beta SHA256: `4c19ccd0358644b93f0bd168f3136f7733ef7fddbe5de130bf7df7dc1b970cca`.

## 2026-08-26 — RSS repository UI 0.3.3-beta13

Status: Beta/Test; one-time RSS cache-model reset awaiting real-device confirmation.

Changes:

- Replaced the Beta11/Beta12 versioned category/detail identity strategy with permanent RSS article identities.
- Introduced one new set of top-level category names to escape the already polluted old category cache.
- Removed `?ui=N` from category and item detail URLs; future UI releases must keep them stable.
- Removed mutable UI version/date metadata from list identity; version stays in detail content only.
- Kept Beta12 direct-render detail HTML, list de-duplication and Stable/Beta physical source separation.
- No book-source business JSON was modified.

## 2026-08-26 — RSS repository UI 0.3.2-beta12

Status: Beta/Test; blank-detail-page fix awaiting real-device confirmation.

Changes:

- Removed the Beta11 `java.startBrowser(data:text/html...)` second-browser launch from `ruleContent`.
- Styled detail HTML is now returned directly into the current RSS detail page, matching the mature RSS-source rendering pattern.
- Kept Beta11 list de-duplication and Stable/Beta physical separation.
- Bumped repository category/detail cache revision to `ui=12`.
- Book-source Stable/Beta files and versions were not modified.

## 2026-08-26 — RSS repository UI 0.3.1-beta11

Status: Beta/Test; repository cleanup and detail-rendering repair awaiting real-device confirmation.

Changes:

- Renamed top categories and bumped category URLs to `ui=11` to force a clean Legado category cache after old/new list entries were observed together.
- Simplified the Beta home page to repository overview, Stable/Beta policy and repository self-update only.
- Added list-level de-duplication by source id / sourceUrl / detailUrl / name.
- Restored styled detail pages by explicitly opening generated HTML with `java.startBrowser(data:text/html;base64, ...)`.
- Added a non-empty `ruleDescription` override so stale description rules from older imported RSS definitions cannot keep taking precedence.
- Stable/Beta source files and channel metadata were not modified by this UI release.

## 2026-08-26 — 起点增强 1.0.1-beta1

Status: Beta/Test; 情无账号/VIP正文专项修复，等待真机确认。

Changes:

- 恢复情无 `/qd/content.php` 的独立 User-Agent / Referer / Accept 请求头。
- 登录/检测只表示账号会话有效；真实 VIP 正文成功后才记录“VIP正文已验证”。
- 仅明确认证错误触发一次自动续签；普通 `Service request failed. Reference: ...` 不再盲目重登。
- Stable `1.0.0` 文件与正式通道保持不变。
- Beta SHA256: `1d4ee73540cc01747ddc1a1a3925343bbc4fae2541791088ee7a2237991d8cf7`.


## 2026-08-26 — RSS repository UI 0.3.0-beta10

Status: Beta/Test; repository self-update/channel-isolation fix awaiting real-device confirmation.

Changes:

- Fixed RSS self-update URI to `legado://import/rssSource?src=...`.
- Added Beta-specific home/update payload and pointed update to the stable Beta RSS identity file.
- Bumped repository category cache revision from v9 to v10.
- Moved `🌈 起点增强` Stable detail to a new Stable-only path so stale Beta detail cache cannot import Stable.
- Codified separate Stable/Beta source and detail paths for future qidian-next releases.
- Source detail pages remain current-state only; version history stays in Release Log.

## 2026-08-26 — 起点增强 v1.0.0 Stable

Status: Stable; promoted by explicit user request from the v0.1.5-beta6 baseline.

Changes:

- Renamed the source from `🌈 起点助手·新架构` to `🌈 起点增强` to distinguish it from 起点助手.
- Promoted the current Beta6 baseline to Stable 1.0.0 without changing reading business logic.
- Moved the source from Beta catalog/bundle to Stable catalog/bundle.
- Kept permanent Legado identity `https://m.qidian.com/?qf_source=qidian_next_8d7` for in-place updates.
- Simplified RSS source detail to current-state information; per-version history is no longer accumulated there.
- Reserved the Stable raw file; future Beta development must use a separate beta file path.
- SHA256: `d64937b9dc4e528795d3818834a6ddab1828df1af84bb483b16961a40d8286ec`.


## 2026-08-25 — Qidian Next v0.1.5-beta6

Status: Beta/Test; secondary-settings UX phase 1 awaiting user real-device confirmation.

Changes:

- Redesigned Content, Account Management and Diagnostics secondary pages with one card-based visual system.
- Content uses strategy/Provider chips, live route summary and a conditional STV card.
- Accounts use Provider tabs, Provider-specific fields and compact action buttons.
- Diagnostics prioritize common tools and collapse advanced actions.
- Preserved the real-device-compatible `startBrowserAwait` + browser ✓ return/save/execute mechanism.
- First-level login UI and reading business modules remain unchanged.
- SHA256: `60e175bc11986157e9a69be57990cefe0c1855b7e90f07b0a5cca1d0ef3be8b6`.


## 2026-08-25 — Qidian Next v0.1.4-beta5

Status: Beta/Test; Shenmo account dependency repair awaiting user real-device confirmation.

Changes:

- Restored `qfSmCtxV30`, `qfSmInputV30`, `qfSmTrimV30`, and `qfSmSaveCredsV30` from the mature historical Shenmo account implementation.
- Fixed the real-device `ReferenceError: qfSmCtxV30 未定义` path.
- Made account actions Provider-specific; Shenmo no longer exposes unsupported web-login.
- Search/detail/catalog/content/review/Provider reading logic remains unchanged.
- SHA256: `f694d686980a2c1aa71d86313eb16931ca578e9c23e18dd136a1c175955d8341`.


## 2026-08-25 — Qidian Next v0.1.3-beta4

Status: Beta/Test; compact account/diagnostic UX awaiting user real-device confirmation.

Changes:

- Split Account Management into Provider selection and short action selection instead of one oversized combined list.
- Show only the active Provider account card.
- Reset the selected action after execution to prevent accidental repeat operations.
- Simplified Diagnostics to the same compact return-and-execute flow.
- Reading business modules remain unchanged.
- SHA256: `9c8b63ce4c000456d47bfd3d2284416680292ee66dfbc3d358395eedff28b896`.

## 2026-08-25 — Qidian Next v0.1.2-beta3

Status: Beta/Test; account/diagnostic action-return fix awaiting user real-device confirmation.

Changes:

- Removed the Beta2 `qfnext://` custom-scheme bridge after real-device confirmation that Android treats it as external-app navigation.
- Account Management now saves fields and chooses one action inside the HTML page; the action runs only after tapping the browser ✓ button to return.
- Diagnostics now uses the same proven select-and-return mechanism.
- Kept the Unicode unique DOM id fix from Beta2.
- Search/detail/catalog/content/review/Provider business logic is unchanged.
- SHA256: `a27682beb478c9523c554024650d9fffd72ef669692c49db839f6dbeb6dd3187`.


## 2026-08-25 — Qidian Next v0.1.1-beta2

Status: Beta/Test; account/diagnostic compatibility fix awaiting user real-device confirmation.

Changes:

- Fixed duplicate DOM ids generated from Chinese setting keys.
- Reworked Account Management and Diagnostics actions to use `qfnext://` WebView interception instead of mutated-DOM action return.
- Kept search/detail/catalog/content/review/Provider business logic unchanged from Beta1.
- SHA256: `031677a7889e2eab926c9a508b422fde85864527dc37bb44c807088a496d2ff3`.


## 2026-08-25 — Qidian Next v0.1.0-beta1

Status: Beta/Test; published to the subscription repository, awaiting full user real-device regression.

Changes:

- Started independent source line `qidian-next` / `🌈 起点助手·新架构` instead of overwriting the existing Qidian source.
- Used the user-selected loginfix4 static two-column login page as the first UI baseline.
- Kept the v4.2.1-alpha2 search/detail/catalog/content/review/Provider business baseline unchanged.
- Secondary settings use `java.startBrowserAwait`; large dynamic `@js:` login UI is no longer used.
- Published complete source JSON, Beta catalog entry, Beta bundle entry, Manifest metadata, RSS detail payload and source handoff.
- Permanent identity: `https://m.qidian.com/?qf_source=qidian_next_8d7`.
- SHA256: `708e871bfae7fc50cac55e19fa73b34b63bb6710494295d12aa712a218548064`.


## 2026-08-25 — Qidian v4.2.1-alpha2 identity hotfix

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- Reverted the repository-only `.invalid` `bookSourceUrl` experiment after real-device failure.
- Restored the mature same-origin identity `https://m.qidian.com/?qf_source=v2922_audio_webview_crypto_bridge_fix`.
- No Qidian business rules were changed.
- Synchronized complete source JSON, Beta Bundle, Manifest and RSS detail metadata.
- Stable/Beta will keep this same identity after confirmation.


## 2026-08-25 — RSS repository UI Beta 7

Status: Beta/Test; awaiting user real-device verification.

Changes:

- RSS detail cards now open explicitly with `java.startBrowser(data:text/html;base64, ...)`.
- Source, bundle and repository-update buttons use `legado://import/importonline?src=...`.
- Qidian Beta can be imported/updated from its repository detail card.


## 2026-08-25 — Qidian official ecosystem v4.2.1-alpha2 Beta

Status: Beta/Test; uploaded source validated and SHA256 verified, awaiting user real-device confirmation.

Changes:

- Published the current uploaded `起点官方生态` baseline to the Beta channel.
- Assigned permanent Legado identity `https://sc8d7.invalid/legado/qidian-official-8d7`.
- Kept existing business rules unchanged; only the top-level identity URL was replaced before publication.
- Published complete source JSON, Beta catalog entry, Beta bundle, Manifest metadata and RSS detail payload.
- Final SHA256: `c952233cc72468a79bd94b784cfe34c0101b0eacecb39b52bff7b9fab691a8a3`.


## 2026-08-25 — RSS repository UI Beta 6

Status: Beta/Test; awaiting user real-device icon verification.

Changes:

- Kept the Beta 3 HTTPS-only category/navigation baseline already confirmed on the user's device.
- Added a real compact 96×96 PNG asset at `assets/reader-repo-icon.png`.
- Changed `sourceIcon` from Base64/Raw experiments to the jsDelivr CDN URL for the PNG asset.
- Updated the stable Beta identity file `rss/reader-source-repository-beta.json` without changing its internal `sourceUrl` identity.
- Added snapshot `rss/reader-source-repository-beta6.json`.

## 2026-08-25 — Large source direct-upload publisher

Status: infrastructure ready; Qidian Beta publication waiting for one original JSON upload into `main/incoming/`.

Changes:

- Replaced the slow multi-part ChatGPT-to-GitHub staging approach with a direct GitHub upload intake.
- Added `incoming/UPLOAD_HERE.txt` as the large-source intake location.
- Updated `.github/workflows/assemble-qidian.yml` to watch `incoming/*.json` on `main`.
- The workflow verifies the original Qidian file SHA256, assigns the permanent Legado identity URL, validates the final SHA256, and automatically updates the complete Beta source, Manifest, Beta Subscription, Beta Bundle, RSS detail metadata and Release Log.
- Failed integrity checks stop publication before an incomplete/corrupt source can enter the Beta channel.

## 2026-08-25 — RSS repository UI Beta 4

Status: Beta/Test; icon fix awaiting user real-device confirmation.

Changes:

- User confirmed Beta 3 no longer reports the Home / Bundle / Help category loading errors.
- Kept the Beta 3 HTTPS-only data-driven navigation as the new RSS UI baseline.
- Beta 3 remote `sourceIcon` still rendered as Legado's default RSS icon on the user's device.
- Beta 4 changes only the subscription icon strategy: the project icon is embedded directly as compact Base64 JPEG data.
- Updated the stable Beta identity path `rss/reader-source-repository-beta.json` to the Beta 4 definition.
- Added versioned snapshot `rss/reader-source-repository-beta4.json`.

Pending real-device verification:

- repository icon display,
- detail-page opening,
- RSS update action,
- bundle import action.

## 2026-08-25 — RSS repository UI Beta 3

Status: Beta/Test; category compatibility confirmed by user on real device.

Changes:

- Investigated Beta 2 after the user reported that Home / Bundle / Help still failed while Stable/Beta loaded.
- Confirmed the HTTPS payload files themselves were valid.
- Identified the Beta 2 helper-context bug: nested `q() -> repo()` calls lost the expected `this.source` binding.
- Rebuilt Home / Bundle / Help as data-driven HTTPS lists with explicit `detailUrl` fields.
- Added independent HTTPS detail JSON files under `rss/data/details/`.
- Simplified the RSS list parser so all categories share one generic path.
- Removed dynamic helper chaining from category navigation.
- Kept the same internal Beta RSS `sourceUrl` identity so Beta 3 updates the existing Beta subscription.

Real-device result:

- User confirmed the previous category loading errors are gone.
- Remote repository icon still did not display, leading to the Beta 4 Base64 icon fix.

## 2026-08-25 — RSS repository UI Beta 2

Status: Beta/Test; superseded by Beta 3 after real-device failure.

Changes:

- Replaced Beta 1 `data:` category URLs with HTTPS payloads.
- Added repository icon asset.
- Added stable Legado source identity policy.

Real-device result:

- Stable/Beta categories loaded.
- Home / Bundle / Help still failed due to the helper-context bug later fixed in Beta 3.

## 2026-08-25 — RSS repository UI Beta preparation

Status: Beta/Test UI work; no book-source Stable release yet.

Completed:

- User switched GitHub default branch to neutral `landing`.
- Actual project and Raw distribution remain on `main`.
- Reviewed three reference RSS sources supplied by the user.
- Adopted a combined UI direction:
  - native Legado categories and list for browsing,
  - styled HTML detail page for metadata and import actions,
  - explicit Stable / Beta separation,
  - separate batch-import area,
  - no required remote-JS runtime dependency for the repository RSS source.

## 2026-08-25 — Repository foundation

Status: infrastructure / no book-source Stable release yet.

Completed:

- Created and connected `source-core-8d7` as the dedicated 阅读 / Legado repository.
- Established hard isolation from the 海阔视界 repository `asset-core-7f3`.
- Added repository-level Manifest skeleton.
- Added Stable and Beta subscription-channel skeletons.
- Added Stable and Beta batch Bundle skeletons.
- Added `🌈 阅读书源仓库` RSS source.
- Corrected the RSS import workflow.
- User confirmed the RSS source imports successfully in the real Legado app.
- Created a neutral `landing` branch and later made it the default branch.
- Added long-term project documents.

## Release policy

Future entries should clearly distinguish:

- generated / static-check passed,
- Beta/Test published,
- user real-device confirmed,
- Stable published.

A generated or statically validated version must not be logged as Stable unless the user has confirmed it or explicitly requested the stable update.

### 2026-08-26 — 🌈 起点增强 1.1.0-beta4
- Detail-only Beta: reject structured tag fragments (`:true`, numeric ids, internal keys) and accept only visible human-readable tags.
- Sparse detail pages may perform one official Qidian PC book-page enrichment request (2.6s timeout) and reuse `qdParseBookInfo`; no secondary fallback.
- Adds trustworthy missing detail fields when available while keeping Stable 1.0.0 and non-detail domains untouched.


### 2026-08-26 — 🌈 起点增强 1.1.0-beta5
- Detail-only hardening: eliminate beta4's possible `ajax -> get` double transport attempt.
- Official PC enrichment is now physically at most one request: prefer `get`, use `ajax` only when `get` is unavailable; no failure fallback.
- Keep strict visible-tag sanitation, 2.6s timeout, 30-minute attempt marker, Stable 1.0.0, and all non-detail modules unchanged.


### 2026-08-26 — 🌈 起点增强 1.1.0-beta6
- Detail-only synopsis fix from real-device beta5 feedback: add Qidian `bookInfo/BookInfo` synopsis extraction.
- A blank synopsis now counts as incomplete detail data; the existing PC enrichment may run once and its same HTML response is reused for synopsis extraction.
- Bump the 30-minute enrichment-attempt marker to V1106 so previous Beta attempts do not mask this parser change during testing.
- Keep the physical one-request limit, 2.6s timeout, Stable 1.0.0, search/catalog/content/review/Provider modules and 情无 VIP authentication chain unchanged.


### 2026-08-26 — 🌈 起点增强 1.1.0-beta7
- Real-device Beta6 still had no synopsis; reopen the synopsis issue rather than marking it fixed.
- When synopsis is missing, reuse the one official enrichment request slot for Qidian's server-rendered TTS book page and extract its visible 作品简介.
- Add DOM/meta description/JSON-LD/book-related script JSON parsing and a low-sensitivity fallback diagnostic.
- Keep the physical one-request ceiling, 2.6s timeout, 30-minute suppression, Stable 1.0.0 and all non-detail modules unchanged.

### 2026-08-26 — 🌈 起点增强 1.1.0-beta10
- Beta9 真机确认详情富数据和内容简介恢复，且整体速度较旧版明显提升；本版以 Beta9 为详情数据基线。
- 详情 UI 收紧段间距，作品数据增加轻量中线分隔，标签/作者标签/荣誉分层，简介首行缩进。
- 冷启动改为核心数据判定：核心稀疏才请求起点图；起点图后仍不足才调用 APP，避免 Beta8 已证明低命中率的 APP 请求固定占据首段等待。
- 起点图超时收紧至 3.2 秒，官方移动搜索收紧至 2.8 秒；缓存策略不变，不新增接口。
- Stable 1.0.0 与所有非详情业务域保持不变。
- SHA256: `aa21a7378323fa7f28159785747661a505296dbd9398678abfd2a40af1eb6b7e`.


### 2026-08-26 — 🌈 起点增强 1.1.0-beta11
- Beta10 真机确认富数据/简介正常，但更新时间与首发时间出现串值；同页未锚定时间字段不可继续作为可靠来源。
- 时间改为按当前 bookId/书名邻域提取，并将异常更新时间纳入现有官方移动搜索补全。
- 时间缓存升级到 v1111，避免旧错误值继续污染。
- 作品数据由空格推进改为固定宽度双列 inline-block，右列统一对齐。
- 非详情域保持冻结。
- SHA256: `8ad15ac2e773efb28bfc504f87fb975c8c7988d379527ab6cbd71234d5703d25`.

## 2026-08-26 · 🌈 起点增强 · 1.1.0-beta12
- 更新字段收紧为最新章节/最近更新语义，连载书明显陈旧时复用当前 bookId 官方搜索；支持绝对日期和相对时间。
- 首发只接受明确 firstPublish/首发时间；上架独立，不再将 createTime/publishTime/VIP 上架冒充首发。
- 时间缓存切换 v1112。
- 作品数据改用 pre+monospace 双列；快捷入口“正文设置”直达 qfMultiContentV423。
- 正式通道未修改。
