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

