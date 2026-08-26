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
