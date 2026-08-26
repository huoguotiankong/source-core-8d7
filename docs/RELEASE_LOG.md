# RELEASE LOG

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
