# Qidian Next PROJECT HANDOFF

> Updated: 2026-08-25

## Current line

- Repository id: `qidian-next`
- Display name: `🌈 起点助手·新架构`
- Channel: Beta/Test
- Current version: `0.1.4-beta5`
- Source path: `sources/novel/qidian-next/qidian-next.json`
- Permanent Legado identity: `https://m.qidian.com/?qf_source=qidian_next_8d7`
- SHA256: `f694d686980a2c1aa71d86313eb16931ca578e9c23e18dd136a1c175955d8341`

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
