# JMComic / 禁漫天堂 Release Notes

## 2026-08-27 — 1.0.0 Stable

Status: Stable. Promoted explicitly by the user from `0.1.0-beta8`.

- Beta8 business logic promoted unchanged; no new runtime feature was added during promotion.
- Stable source moved to `sources/comic/jmcomic/jmcomic.json`.
- Stable RSS detail moved to `rss/data/details/stable/jmcomic.json`.
- Active Beta catalog/bundle entry removed; Beta file remains historical/future-test storage.
- Stable and Beta keep the same permanent `bookSourceUrl` identity.
- Stable source SHA256: `e181e0c0dd917687e98441a4208192977f6799f921591405a4c729d9dd46cb69`.
- Stable source-specific bundle: `bundles/jmcomic-stable.json`.

## 2026-08-27 — 0.1.0-beta8

Status: Beta/Test; awaiting user real-device confirmation.

- Login page now reads credentials from `source.getLoginInfoMap()` first, with legacy `getLoginInfo()` fallback.
- APP login prefers `18comicAPP` and tries app versions `2.1.2` and `2.0.20`.
- Successful login response field `s` is persisted as AVS and explicitly attached to subsequent API requests.
- Cookie persistence now uses the current reader context `ctx.cookie`, with explicit AVS header fallback.
- Added manual Web login, login-status and clear-login controls.
- Beta5 content/TOC and Beta7 detail/comment modules remain frozen.
- Published SHA256: `b6e5efbe29ea2018f1d3246e0e1ce0d9e0347efb4818afd4e9496f69734d7514`.
- Source-specific bundle: `bundles/jmcomic-beta8.json`.

## 2026-08-27 — 0.1.0-beta7

Status: Beta/Test; awaiting user real-device confirmation.

- Fixed comment WebView bridge mismatch: accepts both `action` and `op`.
- Comment list response exposes `list`, `total` and `data`, fixing the Beta6 “未知操作” failure.
- APP/Web comment data model, nested replies, post and reply paths remain unchanged.
- Detail now includes clickable authors, original works and tags.
- Metrics show views/likes, comments/chapters, JM id/route plus update time.
- Beta5 TOC/content and manga image pipeline remain frozen.
- Published SHA256: `6423393d9dfcf10845400fe2916a922cd7cf013a359314175e4155e393a2b6f1`.
- Source-specific bundle: `bundles/jmcomic-beta7.json`.

## 2026-08-27 — 0.1.0-beta6

Status: Beta/Test; awaiting user real-device confirmation.

- User confirmed Beta5 manga content loads; TOC/content rules are frozen in Beta6.
- Added persistent normalized title/cover -> JM ID mapping during search/discovery.
- Added canonical / og:url / ruleUrl / bookUrl / page-title-cover multi-stage album ID resolution.
- Detail comment/favourite buttons carry ID + title + cover; top custom button uses the same resolver.
- Detail data area now exposes JM ID, comment count and current route.
- Comment UI refined without changing the recovered forum data model.
- Published repository source SHA256: `c36f64b73b3865a6ac0b1d07de2ae1a85b27407b04f54fe5b47ba189ecf65b69`.
- Source-specific bundle: `bundles/jmcomic-beta6.json`.

## 2026-08-27 — 0.1.0-beta5

Status: Beta/Test; awaiting user real-device confirmation.

- Detail comment/favourite buttons now embed the current album ID directly.
- Detail visual fields return to the original Web selectors for name, cover, author, synopsis and tags.
- Chapter content first reads the original verified Web `data-original` image list.
- APP `/chapter` objects now parse `image` in addition to `name / filename / url`.
- Web active fetch remains the third content fallback; image shunts and JM de-scrambling remain intact.
- Comment center UI refined: denser cards, nested-reply hierarchy, page indicator, reply-target state and dark mode.
- Published source SHA256: `3266fae2495344cf8efbee76a2bef692f0530671d81a794336a485fcdc7e791b`.
- Source-specific bundle: `bundles/jmcomic-beta5.json`.

## 2026-08-27 — 0.1.0-beta4

Status: Beta/Test; awaiting user real-device confirmation.

- Added `<usehtml>...</usehtml>` around JS-generated detail HTML so `@onclick` buttons are parsed as interactive Legado HTML.
- Removed jsLib's direct dependency on rule-local `baseUrl`; book/chapter IDs resolve through safe context helpers.
- Detail now precomputes a real Web album TOC URL.
- TOC returned to the original proven selector `class.btn-toolbar.0@tag.a||.reading`.
- Chapter body still uses Auto / APP/API / Web routes independently from TOC.
- Beta3 comment HTML/avatar/reply normalization is retained unchanged.
- Published source SHA256: `df81fa4a10ab178454c0a59c52dd3ee0bf5ed9ef1da06704c04df4a5fb352598`.
- Source-specific bundle: `bundles/jmcomic-beta4.json`.

## 2026-08-27 — 0.1.0-beta3

Status: Beta/Test; awaiting user real-device confirmation.

- Fixed detail-page literal `@onclick` / `@get` output by generating the interaction and metadata HTML dynamically.
- Normalized JM forum fields `CID`, `UID`, `replys`, `photo`; comment HTML is converted to readable text and relative avatars become `/media/users/` URLs.
- TOC now returns a Java list consumed through `@json`; APP `series` failure falls back to the original Web `.btn-toolbar / .reading` chain.
- Forces `book.type = 64` during TOC parsing.
- Retains Beta2 `this.java` compatibility fix for discovery/login entry points.
- Repository source now contains complete inline jsLib; Beta1 runtime parts are historical only.
- Published source SHA256: `fb8332ac2d79ffcf9deb7cb4b9030debbac83ac768c073d493f6fb7d0d23b12f`.
- Source-specific bundle: `bundles/jmcomic-beta3.json`.

## 2026-08-26 — 0.1.0-beta1

Status: Beta/Test; awaiting user real-device confirmation.

- Published `◈ 禁漫天堂` to `subscription/beta.json` and `subscription/comic.json`.
- Permanent Legado identity: `https://sc8d7.invalid/legado/jmcomic-8d7`.
- Repository source: `sources/comic/jmcomic/jmcomic-beta.json`.
- Shared runtime is split into five Raw parts and cached by the source loader; search/detail/TOC/content rules remain the Beta1 baseline.
- APP/API + Web dual routes with automatic fallback and last-success route cache.
- Dynamic APP API domain refresh plus Web permanent-link/publication-page domain discovery.
- Dual-route login, account center, favourites and watch history.
- Comment center with paging, post and reply; detail-page entry and top custom button share the same comment UI.
- Manga image shunts 1–4 and JM image de-scrambling retained.
- Repository source SHA256 recorded in Manifest: `1c2b8aa76945e10a1ec58cf1efe5acf3c0f3430421baae81d9b4b8e85f9618db`.

Main `docs/RELEASE_LOG.md` merge is temporarily deferred because the available write action replaces the whole file and another Qidian Beta publication Action is still queued to modify shared release metadata. Replacing the full log now could overwrite that concurrent publication. This source-local note is the authoritative interim record and must be merged into the main log after the shared publication queue is clear.

The project-wide `bundles/all-beta.json` was already empty before JMComic publication. It is intentionally not overwritten with a partial JMComic-only array because doing so would drop unrelated Beta sources. `bundles/jmcomic-beta1.json` is maintained as a source-specific bundle using the exact same Git blob as the repository source until the global bundle builder is restored.
