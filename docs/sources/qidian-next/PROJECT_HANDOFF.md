## 2026-09-13 · qidian-next 1.2.3-beta2 — 段评点赞纵向对齐修正
- 基于 `1.2.3-beta1` 继续微调，只修改 `review_local_ui`。
- 保持 13px 点赞图标、10px 点赞数字及 beta1 的正文宽度优化不变。
- `metaLine` 改为统一垂直居中；点赞容器采用 `inline-flex + align-items:center`，固定 16px 行高/高度；SVG 改为 block，消除基线导致的整体上浮。
- 目标是让点赞与楼号、时间、地点处于同一视觉水平线。
- Stable 1.2.2 与其它业务模块保持不变，继续等待真机确认。

## 2026-09-13 · qidian-next 1.2.3-beta1 — 段评页面点赞与正文宽度优化
- 从用户已确认的 Stable 1.2.2 重新建立 Beta 基线，仅修改 `review_local_ui`。
- 楼主点赞图标缩至 13px、数字缩至 10px，视觉层级与楼号/时间对齐；元信息行间距同步收紧。
- 评论卡右内边距收紧，并解除 `mainRow/body/content` 的右侧宽度约束，使正文获得更多横向空间、减少过早换行。
- 楼中楼结构与回复加载保持不变；情无/小雨评论桥接、Argus 段评计数、正文、目录、搜索、账号、`ruleContent`、Rhino loader、本章说卡片及其它 Provider 全部冻结。
- Stable 1.2.2 不变，仅发布 Beta 等待真机确认。

## 2026-09-13 · qidian-next Stable 1.2.2
- 用户真机确认 `1.2.2-beta5` 本章说卡片优化正常，并明确要求晋升正式版。
- Stable 直接沿用 Beta5 业务代码，不新增业务逻辑；保留近白浅灰卡片、浅灰边框、珊瑚红标签及统一中性灰阶。
- 评论总数、两条真实评论预览、点赞/回复统计与点击进入本章说逻辑不变；沿用 1.2.2-beta4 功能链。
- `sources/novel/qidian-next/qidian-next.json`、Manifest、Stable/Novel Subscription、Stable Bundle、RSS Stable Detail 已同步；活动 Beta/Novel 重复项移除。
- Beta5 独立物理文件继续保留作历史/后续开发基线；Stable/Beta 继续共享同一 Legado `bookSourceUrl` 身份。

## 2026-09-13 · qidian-next 1.2.2-beta5 — 本地本章说卡片主题统一
- 延续 1.2.2-beta4 功能链，仅保留已完成的 `qdChapterTalkCardV20` 视觉改造；上一轮误写成 1.2.1-beta8 的版本序列在本版纠正为 1.2.2-beta5。
- 卡片由绿色/米黄改为近白浅灰底、浅灰边框和评论页同系珊瑚红标签；昵称、正文、点赞与回复统一中性灰阶。
- 评论总数、两条真实评论预览、点赞/回复统计及点击进入本章说逻辑不变。
- 情无/小雨服务器段评本轮冻结；正文、目录、搜索、账号、`ruleContent`、Rhino loader 与其它 lazy module 均不改。
- 修复 Beta 详情页发布元数据：恢复顶层 `sourceUrl` / `backupUrl` / `importUrl`，同时保留 links。
- Stable 1.2.1 不变，仅发布 Beta 等待真机确认。

## 2026-09-13 · qidian-next 1.2.1-beta8
- 本轮按真机反馈先冻结情无服务器段评，只处理本地段评章末“本章说”卡片。
- 视觉统一：绿色实心标签改为浅珊瑚红底 + 珊瑚红字；卡片改为近白背景、浅灰边框/分隔线，昵称、正文、回复与点赞统一中性灰阶。
- 功能保持：评论总数、两条真实评论预览、点赞/回复统计与点击进入本章说逻辑全部不变。
- 隔离门禁：仅 `review` lazy module 发生变化；`ruleContent`、Beta7 Rhino `Scanner + GZIPInputStream` 加载器及其它31个 lazy module 不变。
- Stable 1.2.0 不变，仅发布 Beta 等待真机确认。

## 2026-09-12 · qidian-next 1.2.2-beta4 — 情无头像 / 楼中楼桥接修复
- 真机确认 Beta3 已恢复情无/小雨段评气泡和主评论列表；剩余问题为头像空白、楼中楼显示“回复加载失败”。
- 对照当前“小雨的世界”实现确认：`list.php` / `reply.php` 与评论 UI 不同源且接口无 CORS 头，浏览器直接 `fetch` 会被拦；评论请求应由书源侧 `java.ajax` 代理。
- Beta4 仅替换情无段评点击后的 Viewer：主列表走 `list.php`、回复走 `reply.php`，均经 `java.ajax`；接口大整数 ID 在 JSON 解析前做字符串保护。
- 评论字段新增当前服务端 `avatarUrl/reviewId/nickname/createTime/replyCount/likeCount/isGod/imageUrl/audioUrl/quoteNickname` 适配；头像 URL 兼容协议相对/HTTP/相对路径并使用 no-referrer。
- Viewer 获取或打开失败仍回退原 `index.html`；Beta3 Argus 气泡快通道、正文、目录、搜索、账号和 Stable 1.2.1 冻结。
- 状态：Beta，等待真机确认头像与楼中楼。

## 2026-09-12 · qidian-next 1.2.2-beta3 — 妙想天开段评快通道借鉴
- 重新按用户当前上传的 `bookSource_妙想天开.json` 核对：该版段评计数实际走 `druidv6.if.qidian.com/argus/api/v1/chapterreview/getchapterrepagesummary`，读取 `Data.Getparagraphscommentcounts.DataList`；神评另用同端点 `strategy=3`，本章说用 `assembly/getchapteractivity`。
- Beta3 先吸收低风险且收益最大的“整章段评计数一次取回”思路：新增 Argus `getchapterrepagesummary` 快通道，归一化为 qidian-next 既有 `paragraphId/segmentId/count` 模型并写入 ReviewCache。
- 本地段评：官方快通道有非空计数时直接返回；接口空/失败继续走原 www/m/read 多镜像摘要链，不把空结果当权威。
- 情无/小雨：只把气泡位置/数量元数据改为官方快通道优先；完整评论点击 Provider 不变，快通道失败继续回退 `review.php`。
- 目录评估：妙想天开使用单一 v1 `chapterlist/chapterlist` 读取 `N/C/V/T/W`；qidian-next 当前已有 APP v3 + getsimple + pager + Web fallback + 多层缓存/完整度诊断，本版不替换目录，避免跨域回归。
- `strategy=3` 神评与 `getchapteractivity` 本章说暂不替换现有成熟链，待本版真机确认后再单域 A/B。Stable 1.2.1、正文、目录、搜索、账号及其它 Provider 不变。

## 2026-09-12 · qidian-next 1.2.2-beta2 — 情无/小雨段评气泡回归修复
- 真机确认 Beta1 选择情无服务器后连段评气泡都没有。
- 根因：Beta1 将 `CommentCount` 放在 `TextCount` 前；服务器行存在 `CommentCount=0` 时遮蔽有效 `TextCount`，从而把全部段评行过滤掉。
- Beta2 恢复 Stable/Beta7 已验证的 `TextCount` 优先语义，仅当 TextCount 无有效值时回退 CommentCount。
- 保留 Beta1 的 `ParagraphId - 1 + 图片补偿` 定位与原始 ParagraphId 点击参数；正文与 Stable 1.2.1 冻结。
- 状态：Beta，等待真机确认气泡恢复后再继续评论列表/楼中楼。

## 2026-09-12 · qidian-next Stable 1.2.1
- 用户真机确认 `1.2.1-beta7` 正文修复成功，并明确要求将这一版先晋升正式版。
- Stable 直接沿用 Beta7 业务代码，不新增业务逻辑；修复 `EvaluatorException: 不允许的字符：\`，恢复单一真实 JS 正文执行块。
- 懒模块解压使用已验证的 `Scanner + GZIPInputStream`，移除 Rhino 不兼容的 `java.lang.reflect.Array.newInstance`；Base64URL 兼容保留。
- `sources/novel/qidian-next/qidian-next.json`、Manifest、Stable/Novel Subscription、Stable Bundle、RSS Stable Detail、Release Log 已同步；活动 Beta/Novel 重复项移除。
- Beta7 独立文件继续保留作历史/后续开发基线；Stable/Beta 继续共享同一 Legado `bookSourceUrl` 身份。

## 2026-09-12 · qidian-next 1.2.1-beta7
- 真机确认 Beta6 仍有两类故障：正文 `EvaluatorException: 不允许的字符：\`；评论页解压时报 `java.lang.reflect.Array.newInstance` 不是函数。
- 根因一：Beta4 评论补丁已把第二个 `@js` 以字面量 `\n@js:\n` 拼入 `ruleContent.content`；Beta5/Beta6沿用了该字段。Beta7 改成单一真实 JS 块，正文主链仍调用 `qfContentEntryV38`，随后再执行原情无/小雨装饰逻辑。
- 根因二：Beta6 自行改写 GZIP 读取为反射 byte[]，与当前 Legado Rhino 不兼容。Beta7 恢复 Beta4 已验证的 `Scanner + GZIPInputStream`，只在 Base64 解码前做 URL-safe 标准化。
- 门禁升级：32 个 lazy module（31 压缩 + 1 明文）全部解包并按实际 factory 包装逐个 JS 语法检查；另校验 `jsLib` 与单块 `ruleContent`。
- Stable 1.2.0 不变，仅进入 Beta 真机验证。

## 2026-09-12 · qidian-next 1.2.1-beta6
- 紧急修复 Beta5 回归：正文出现 `EvaluatorException: 不允许的字符：\`。根因是 Beta5 热修脚本把字面量反斜杠+n 写进 `jsLib`。
- 恢复 Beta5 误删的 alpha84 lazy-module 并发运行时，补回 `qfModuleThreadIdV84` / `qfModuleWaitV84`，修复点击段评/本章说 `ReferenceError`。
- 修复基线改为已验证 Beta4；仅 `qfModuleUnpackV41` 做 Base64URL `-` / `_` 和缺失 `=` 兼容。
- 门禁：31 个压缩模块逐个 Base64+gzip 解压；`jsLib` JS 语法检查；loader 外与 Beta4 基线逐字节一致。
- Stable 1.2.0 不变，继续仅进入 Beta 真机验证。

## 2026-09-12 · qidian-next 1.2.1-beta5
- 修复点击段评/本章说时 `模块解压失败 / Illegal base64 character 5f`。
- `qfModuleUnpackV41` 统一兼容 Base64URL 的 `-` / `_`，并自动补齐 `=`。
- 情无/小雨评论接口、正文链、账号系统及其它 Provider 保持 Beta4 不变。
- Stable 1.2.0 不变，等待真机确认后再考虑晋升。

## 2026-09-12 · qidian-next 1.2.1-beta4
- 评论设置新增情无/小雨服务器适配：段评可走 `full.hnxianxin.cn/qd/review.php`。
- 章名评论优先使用服务器 `ParagraphId=-1`；服务器无章名评论时保留本地段评章名评论。
- 本章说改用小雨评论入口，修复只显示总数卡、不显示具体评论的问题。
- Stable 1.2.0 与其它功能域不变。
## 2026-09-11 · Current Beta 1.2.1-beta2 — Xiaoyu current auth

- Stable remains 1.2.0.
- Supersedes invalid 1.2.1-beta1 email/password attempt.
- Current Xiaoyu auth is source-author / feedback-group / temporary-password guest token or web registration/login, using X-Sec-Token + X-Android-Id.
- No-login content fallback remains the verified Stable behavior.

## 2026-09-11 · Current Beta 1.2.1-beta1 — 情无 optional account session

- Stable remains 1.2.0.
- Re-exposes Qingwu in the effective polished Account Management provider tabs.
- Qingwu auth helpers now target `https://full.hnxianxin.cn/qd`; successful Cookie / X-Content-Token are optional headers for `limited_qw`.
- Anonymous Beta41 catalog/content behavior remains the mandatory fallback and is not gated by login.
- Awaiting real-device verification.

## 2026-09-11 · Current Stable 1.2.0 — promoted from verified Beta41

- User explicitly requested Stable promotion after real-device confirmation that the new Qingwu content path works.
- Stable is a logic-preserving copy of Beta41 with Stable metadata/name only.
- Beta channel remains available separately for future development.

## 2026-09-11 · Current Beta 1.1.0-beta41 — 情无 fresh cache / native ajax diagnostics

- Stable remains 1.1.0.
- QW catalog cache key bumped to v41; catalog/content now mirror attachment java.ajax.
- Resolver failure now exposes real catalog/effective row counts and samples for device diagnosis.

## 2026-09-11 · Current Beta 1.1.0-beta40 — 情无 Hex→Base64 章节解码修复

- Stable remains 1.1.0.
- New 情无 backend follows the attachment exactly: catalog C is hex-decoded first, then Base64-decoded to chapter JSON.
- Account Management removes 情无; content Provider keeps 情无 as no-login source.
- Awaiting real-device verification.

## 2026-09-11 · Current Beta 1.1.0-beta39 — 情无免登录 / 章节匹配修复

- Stable remains 1.1.0.
- 情无 keeps its public/provider name but uses the user attachment 小雨的世界 free content backend. No account/token is required and 情无 is removed from Account Management.
- Chapter resolution now uses ID/title/chapter-number/index fallbacks before requesting content.php; source promo footer cleanup remains enabled.
- Awaiting real-device verification.

## 2026-09-11 · Current Beta 1.1.0-beta38 — 情无来源替换

- Stable remains 1.1.0.
- 情无 display/provider name stays unchanged, but its limited-content backend is replaced by the user-supplied 小雨 source (`full.hnxianxin.cn/qd`).
- Runtime resolves chapter `t/epub/vip` from the new catalog before content fetch; no old 情无 auth/token requirement is used for the default path.
- Two provider-added promotional footer paragraphs are stripped before returning chapter text.
- Beta37 review UI is preserved; unrelated domains are frozen. Awaiting real-device verification.

## 2026-09-08 · Current Beta 1.1.0-beta32 — X-QD limited Provider

- Stable remains 1.1.0.
- Added isolated X-QD limited-content Provider (`limited_x`) using only X `content.php` + independent Token auth.
- X is selectable in limited-provider settings, appended to auto routing, and mapped to book variable `15`.
- X does not take over review/purchase/AI/discovery/catalog domains. Awaiting real-device verification.

## 2026-08-26 · Current Beta 1.1.0-beta16 — Circle detail click hotfix

- Stable remains 1.1.0.
- Beta16 restores the proven compact post-detail button and moves multi-image transfer to an in-memory postId map seeded from initial and dynamic rows.
- Beta15 poll metadata cleanup is retained. Awaiting real-device confirmation.

## 2026-08-26 · Current Beta 1.1.0-beta15 — Circle detail multi-image

- Stable remains 1.1.0.
- Beta15 changes only the lazy `circle` module: preserve all list-card post images into detail and remove confirmed poll metadata leakage.
- Awaiting real-device confirmation before any Stable promotion.

# Qidian Next PROJECT HANDOFF

> Updated: 2026-08-25

## Current line

- Repository id: `qidian-next`
- Display name: `🌈 起点增强`
- Channel: Stable
- Current version: `1.0.0`
- Source path: `sources/novel/qidian-next/qidian-next.json`
- Permanent Legado identity: `https://m.qidian.com/?qf_source=qidian_next_8d7`
- SHA256: `d64937b9dc4e528795d3818834a6ddab1828df1af84bb483b16961a40d8286ec`

## Baseline

The first version intentionally keeps the existing v4.2.1-alpha2 business rules as a functional baseline. Only source identity/metadata and the login/settings architecture differ. This protects search, detail, catalog, content, review and Provider behavior while the new line is established.

## Login/settings architecture

User real-device testing established that the current Legado environment can open static `loginUi`, while the large dynamic `@js:` login UI path fails before the page is shown. The new line therefore uses:

- pure static first-level `loginUi`;
- two-column main navigation;
- `java.startBrowserAwait` HTML secondary settings pages;
- settings written back to existing login-info keys so runtime business logic stays compatible.

## Real-device status

Confirmed before repository publication:

- static login page opens;
- settings can be changed;
- two-column loginfix4 layout was selected by the user as the new-source UI baseline.

Still requires regression testing after repository import:

- secondary settings pages and persistence;
- search and book detail;
- catalog;
- free/VIP content;
- comments and author-say;
- Provider switching, including STV.

## Development rule

Continue new work on this independent source line. Do not overwrite the old `qidian-official` source by default. Promote to Stable only after explicit user real-device confirmation.
## Beta2 account/diagnostic fix

Real-device testing of Beta1 was broadly normal, but Account Management and Diagnostics were faulty. Root causes identified in the login HTML layer:

- Chinese setting keys were converted to underscore-only DOM ids, so same-length Chinese keys collided.
- account/diagnostic actions relied on returning mutated DOM state from `startBrowserAwait`, which is not reliable in the current Legado WebView path.

Beta2 uses Unicode-derived unique DOM ids and a `qfnext://` custom-URL bridge intercepted by `shouldOverrideUrlLoading`. Business reading modules are unchanged.
## Beta3 account/diagnostic fix

Beta2 proved that custom `qfnext://` navigation from a `data:` page opened by `startBrowserAwait` is handled as an Android external-app scheme rather than by the book source's `shouldOverrideUrlLoading`. Beta3 removes that bridge completely. Account and diagnostic actions are represented as normal select values inside the already-working HTML settings-return path; after the user taps the browser ✓ button, `loginUrl` reads the returned value and executes the native source action.


## Beta4 account UX

Beta3 removed the incompatible custom scheme but exposed an oversized Provider×action selector. Beta4 keeps the proven return-and-execute mechanism while splitting the UI into a short Provider selector and short action selector; only the active Provider card is shown. Diagnostics use the same compact return-and-execute pattern.

## Beta5 Shenmo account dependency repair

Real-device Beta4 exposed `ReferenceError: qfSmCtxV30 未定义` when executing Shenmo login. Historical working Qidian versions contained four account helper functions (`qfSmCtxV30`, `qfSmInputV30`, `qfSmTrimV30`, `qfSmSaveCredsV30`), while later source cleanup retained `qfSmLoginV30` / check / backend / logout callers but removed those dependencies. Beta5 restores the mature helpers unchanged.

The account action selector now follows the active Provider. Shenmo exposes only login/check/backend/logout; unsupported web-login is no longer shown. Reading business modules are unchanged.

## Secondary settings UI redesign plan

User approved a staged redesign on 2026-08-25. Keep the confirmed two-column static first-level login page. Secondary pages use one visual system: compact gradient header, grouped cards, direct controls, clear current state, and a unified footer explaining that the browser ✓ returns/saves and executes any chosen native action. Do not return to large dynamic `@js:` loginUi or custom-scheme bridges.

Phases:

1. Beta6: Account Management, Diagnostics, Content/Provider settings.
2. Next phase: Review/Display settings, Interface/Prompt settings, Book-variable guide and Help.
3. Final polish: spacing, typography, button states, consistent copy, then remove obsolete UI compatibility blocks after real-device confirmation.

## Beta6 secondary settings UI phase 1

- Content: strategy chips, Provider chips, live route summary, STV card shown only for STV.
- Accounts: four Provider tabs; only the active Provider card is shown; actions are direct two-column buttons and are executed only after ✓ return.
- Diagnostics: common tools are visible first; deep trace / reset are under an advanced disclosure; selected action is clearly displayed.
- Runtime reading modules are untouched.

## Stable 1.0.0 promotion

User explicitly requested promotion of the Beta6 baseline to the first Stable release. Display name changed to `🌈 起点增强`; permanent `bookSourceUrl` remains unchanged so Legado upgrades in place.

Distribution rule after Stable 1.0.0:

- `sources/novel/qidian-next/qidian-next.json` is the Stable file and must not be overwritten by an unconfirmed Beta.
- Future test versions must use `sources/novel/qidian-next/qidian-next-beta.json` (or another explicitly beta-only path) while preserving the same `bookSourceUrl`.
- Stable and Beta subscription entries may therefore point to different files but represent the same Legado source identity.
- RSS source detail is a current-state introduction, not a per-version history. Replace the current-version section on release; keep historical changes only in `docs/RELEASE_LOG.md`.

## Active Beta 1.0.1-beta1 — 情无 VIP 认证修复

Stable remains `1.0.0` at `sources/novel/qidian-next/qidian-next.json`. Beta path: `sources/novel/qidian-next/qidian-next-beta.json`.

Real-device trigger: 情无账号登录/检测成功，但固定情无读取 VIP 章节返回 `Service request failed. Reference: ...`. Historical working builds required an explicit 情无 User-Agent + Referer for `/qd/content.php`; the current lazy module had regressed to Accept-only headers. `/auth.php?action=me` validates the account session but does not prove that VIP content is accepted.

Beta changes: restore 情无-specific content headers; retry only authentication-like failures; mark VIP verification only after real paid content succeeds; keep service Reference visible on non-auth failures; keep Stable and all unrelated reading domains unchanged.
## Detail UI / performance Beta 1.1.0-beta1 (2026-08-26)

- Replaced the 61k-character blocking detail augmentation path with a fast first-paint path based on the already-downloaded Qidian response plus per-book cached values.
- No APP/Web/Atom/QidianTu/TuShuJun synchronous requests are allowed from the new `ruleBookInfo.init` first-paint path.
- Native Legado cover/title/author/latest-chapter area remains responsible for primary metadata.
- Custom detail HTML is reduced to a compact metric strip, on-demand interaction buttons, up to six tags, and synopsis.
- Book-circle, role-card and smart-source actions remain on-demand buttons and therefore do not block initial detail rendering.
- The 1.0.1-beta1 QW VIP-content authentication/request-header fix is a hard regression gate for all later Betas.
## Detail richness Beta 1.1.0-beta2 (2026-08-26)

- Real-device beta1 showed the metric `<table>` rendering vertically/misaligned and the overall detail information becoming too sparse.
- beta2 keeps the zero-extra-request first-paint architecture, but expands parsing/cached display for author metadata, status, update time, recommendation/month-ticket/reading/rating/collection/fans/leader/invest/first-subscribe metrics, tags and honors.
- The metric strip is replaced by plain HTML rows because Legado detail HTML/CSS support is device/version dependent; simple rows are the preferred compatibility baseline.
- Missing fields are hidden rather than synchronously fetched. Book circle, role card and smart source remain on-demand.
## Detail semantic cleanup Beta 1.1.0-beta3 (2026-08-26)

- Real-device beta2 exposed internal Qidian object keys/enums (`sectionCount`, `actionStatus`, `FININSHED`, `honorTypeName`) and numeric ids/timestamps as visible tags/honors.
- Add parser-side and renderer-side metadata sanitation; cached polluted values are also blocked at render time.
- Collection/fan metrics use stricter trust rules; an isolated tiny collection count beside a huge fan base is suppressed as likely nested-object noise.
- Normalize author level to `Lv.x` and common internal finished/serial states to Chinese display values.
- Keep the zero-extra-request detail first-paint invariant.


## Detail balance Beta 1.1.0-beta4 (2026-08-26)

- Real-device beta3 confirmed one title could show correct visible tags, while another still leaked structured fragments such as `:true` and `:50001`; works-data density also remained too low.
- Generic array-string extraction is no longer used for tags/honors. Tags now require visible human text (Chinese or a short explicit ASCII allowlist) and reject JSON/object punctuation, booleans, ids and internal field names.
- Current response/cache remains first priority. When reliable detail metrics are sparse, the detail path may issue at most one request to `https://www.qidian.com/book/<bookId>/` with a 2.6s timeout and reuse the existing `qdParseBookInfo(html, baseUrl)` parser.
- There is no second detail fallback and no APP/Atom/third-party enrichment chain. A per-book 30-minute attempt marker prevents repeated slow probes.
- Stable 1.0.0 and search/catalog/content/review modules remain unchanged.


## Detail single-request hardening 1.1.0-beta5 (2026-08-26)

- Static code review found beta4 called the generic `qfAjaxTextV20`, which can execute `ajax()` and then `get()` when the first transport returns empty; nominal one enrichment call therefore did not guarantee one physical request.
- Beta5 uses a detail-local mutually exclusive transport: one `get()` when available; only when the runtime has no `get` function is one `ajax()` used. A thrown/empty request does not trigger a second transport attempt.
- Single timeout remains 2.6 seconds; the per-book 30-minute attempt marker remains.
- Beta4 visible-human-text tag sanitation and sparse-enrichment policy remain unchanged.
- Source-level validation asserts only `bookSourceComment` and `ruleBookInfo.init` changed; `jsLib`, source identity, search/catalog/content/review/Provider and 情无 logic are byte-for-byte preserved in this patch.
- Status: Beta, pending real-device confirmation.


## Detail synopsis repair 1.1.0-beta6 (2026-08-26)

- Real-device beta5: custom 作品资料/月票/快捷入口/标签 render, but 内容简介 is completely absent.
- Root cause in the detail-local fast parser: `introFromCurrent()` scanned BookIntro/BookDesc/Introduction variants but omitted Qidian's `bookInfo` synopsis field; `qfDetailSparseV1104()` also did not consider a blank synopsis.
- Beta6 adds `BookInfo/bookInfo`, includes blank `info.intro` in the sparse decision, and fills `info.intro` from `rich.intro || introFromCurrent(pcHtml)` after the existing one official PC request. No additional endpoint/fallback chain is introduced.
- The attempt-cache key moves from V1104 to V1106 solely to prevent an earlier Beta's 30-minute marker from blocking immediate validation of the new parser. Request limit stays physically at most one with 2.6s timeout and 30-minute suppression thereafter.
- Source-level guard confirms only `bookSourceComment` and `ruleBookInfo.init` changed; `jsLib`, source identity, search/catalog/content/review/Provider and 情无 logic are preserved.
- Status: Beta, pending real-device confirmation.


## Synopsis official TTS fallback 1.1.0-beta7 (2026-08-26)

- Beta6 real-device result: synopsis still absent on `同时穿越：继承万界遗产`; other detail blocks remained functional.
- `bookInfo/BookInfo` must not be assumed to be a scalar synopsis field.
- Beta7 keeps the one-request network ceiling. If synopsis is blank, the sole enrichment request targets Qidian official `https://www.qidian.com/ttsbook/<bookId>/9/`, whose server-rendered page exposes `作品简介`; otherwise the existing PC detail enrichment URL is retained.
- Parser also checks intro DOM, meta description, JSON-LD and current-book-related script JSON. If all fail, `introDiag` temporarily shows only response length/structure/script count/hit length.
- Source guard: only `bookSourceComment` and `ruleBookInfo.init/intro` change; `jsLib`, source identity, search/catalog/content/review/Provider and 情无 logic remain unchanged.
- Status: Beta pending real-device feedback.

## Detail layout/performance 1.1.0-beta10 (2026-08-26)

- Beta9 real-device result is positive: synopsis and rich metrics are restored; user reports materially better speed than the older detail chain, though cold load still waits.
- Beta10 treats Beta9 data extraction as frozen and changes only detail presentation plus enrichment ordering.
- Core-richness check excludes synopsis-only incompleteness. QidianTu runs only when core metrics/tags/status are sparse; APP bookDetailInfo becomes a second-line fallback rather than the fixed first call.
- QidianTu timeout: 3.2s. Official mobile search timeout: 2.8s. Existing caches remain unchanged.
- UI: tighter section spacing, separated metric columns, separate tag/author-tag/honor blocks, indented synopsis.
- Search/catalog/content/review/community/account/QW-VIP domains remain frozen.
- Status: Beta pending real-device layout/performance confirmation.


## Detail time/alignment 1.1.0-beta11 (2026-08-26)

- Beta10 real-device result: rich metrics and synopsis remained correct, but update/publish dates could resolve to the same wrong timestamp.
- Unscoped full-page `UpdateTime/CreateTime` extraction is removed. Current-book time parsing is anchored to current bookId/title vicinity.
- Suspect update time may reuse the already-existing exact-book official mobile-search fallback; no new endpoint is introduced.
- Time book-variable cache keys are versioned to v1111 so old wrong values do not mask the fix.
- Works-data renderer uses two fixed-width inline-block cells instead of spacing or `<table>`, aligning the right column while preserving the compatibility baseline.
- Status: Beta, pending real-device confirmation.

### 1.1.0-beta12 真机修复（2026-08-26）
- 时间按语义分层：更新=latest chapter/当前 bookId 官方搜索；首发=明确 firstPublish；上架=listingDate。
- usehtml 双列不要依赖 inline-block 百分比宽度；当前改用预格式等宽文本。
- 详情“正文设置”快捷入口直接调用 qfMultiContentV423。
- 本版仍为 Beta。
