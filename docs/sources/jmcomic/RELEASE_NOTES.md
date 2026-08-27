# JMComic / 禁漫天堂 Release Notes

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
