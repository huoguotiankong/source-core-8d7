# JMComic / 禁漫天堂 Project Handoff

Updated: 2026-08-27

## Current release

- Channel: Beta/Test
- Version: `0.1.0-beta5`
- Display name: `◈ 禁漫天堂`
- Legado identity: `https://sc8d7.invalid/legado/jmcomic-8d7`
- Repository source: `sources/comic/jmcomic/jmcomic-beta.json`
- RSS detail: `rss/data/details/beta/jmcomic.json`
- Source-specific bundle: `bundles/jmcomic-beta5.json`
- Runtime: complete inline `jsLib`.

## Confirmed real-device progression

- Beta1: repository Raw runtime loader failed because `java` resolved to Rhino `JavaPackage`.
- Beta2: discovery/categories and login-page buttons recovered after explicit `this.java` compatibility handling.
- Beta3: comment HTML text and nested replies recovered; TOC direction improved.
- Beta4: detail HTML buttons render correctly and Web TOC opens.
- Beta5: targets the remaining issues from the latest screenshots:
  1. Detail comment/favourite buttons bind the album ID directly.
  2. Detail visual data falls back to the original Web source selectors.
  3. Content uses the original verified chapter-image selector first.
  4. APP `/chapter` image objects now accept the actual `image` field.
  5. Comment UI is refined without changing the recovered comment data model.

## Current architecture

1. Detail
   - Album ID is captured during init and inserted directly into button callbacks.
   - Name/cover/author/description/tags use the original Web selectors as the visual baseline.
   - API detail data is supplemental only.
2. TOC
   - Original Web selectors `class.btn-toolbar.0@tag.a||.reading`.
   - Manga mode `book.type=64`.
   - Selected image shunt is appended to chapter URLs.
3. Content
   - First: current Web chapter `.row.thumb-overlay-albums img[data-original]`.
   - Second: APP `/chapter?id=<photoId>`; supports string items and object `image/name/filename/url`.
   - Third: active Web request and Jsoup image extraction.
   - Existing image de-scrambling retained.
4. Comments
   - APP `/forum` read first, Web fallback.
   - `CID/UID/content/photo/replys` normalization retained.
   - Independent comment center supports paging, posting, replying and nested replies.
5. Account/routes
   - Auto / APP/API / Web route switching.
   - Dynamic API and Web domain refresh.
   - Login, account center, favourites and history.

## Repository publication state

Beta5 is synchronized in:

- `manifest.json`
- `subscription/beta.json`
- `subscription/comic.json`
- `rss/data/details/beta/jmcomic.json`
- `sources/comic/jmcomic/jmcomic-beta.json`
- `bundles/jmcomic-beta5.json`
- `bundles/all-beta.json`
- `docs/sources/jmcomic/RELEASE_NOTES.md`
- `docs/RELEASE_LOG.md`

Repository Beta5 source SHA256: `3266fae2495344cf8efbee76a2bef692f0530671d81a794336a485fcdc7e791b`.

## Next real-device checklist

1. Detail cover, single author, synopsis and tags.
2. Detail “查看评论” should open the same comment center as the top custom button.
3. Detail “收藏作品” should submit against the correct album ID.
4. Open a Web TOC chapter and verify images appear.
5. Test the same chapter with Auto, APP/API and Web route modes.
6. Verify scrambled newer chapters.
7. Comment paging, replies and posting after the UI refinement.

## Promotion rule

Do not promote to Stable until the user explicitly confirms the source is normal on device or directly requests Stable promotion.
