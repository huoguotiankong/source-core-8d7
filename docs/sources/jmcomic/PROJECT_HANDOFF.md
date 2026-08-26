# JMComic / 禁漫天堂 Project Handoff

Updated: 2026-08-27

## Current release

- Channel: Beta/Test
- Version: `0.1.0-beta3`
- Display name: `◈ 禁漫天堂`
- Legado identity: `https://sc8d7.invalid/legado/jmcomic-8d7`
- Repository source: `sources/comic/jmcomic/jmcomic-beta.json`
- RSS detail: `rss/data/details/beta/jmcomic.json`
- Source-specific bundle: `bundles/jmcomic-beta3.json`
- Runtime: complete inline `jsLib` in the source JSON. Beta1 runtime parts remain only as history and are not executed.

## Baseline and confirmed device results

Beta1 repository delivery used a five-part Raw loader. Real-device testing showed that during `jsLib` initialization, `java` could resolve to Rhino `JavaPackage java`, making `java.ajax` non-callable and breaking discovery plus every login-page action.

Beta2 removed that startup loader and changed network/UI calls to explicitly resolve the Legado Java bridge from `this.java`. Real-device feedback confirmed discovery/category pages and login-page buttons recovered.

Beta3 keeps the Beta2 compatibility layer and only fixes three isolated areas reported by real-device screenshots:

1. Detail rendering
   - Literal `@onclick` and nested `@get` text were displayed instead of evaluated.
   - The interaction block and metadata are now generated dynamically by JS.
2. Comment center
   - JM APP forum fields follow `CID / UID / content / photo / replys`.
   - Comment HTML is converted to readable text.
   - Relative avatar filenames are expanded to `https://<image-host>/media/users/<photo>`.
   - Nested `replys` are recursively normalized.
3. TOC
   - APP album `series` is parsed as `id / name / sort`.
   - Chapter objects are returned as Java `ArrayList<HashMap>` and consumed via `@json`.
   - If APP series is unavailable, the original user-provided Web selectors `.btn-toolbar a[href*=/photo/]` / `a.reading[href*=/photo/]` are used.
   - TOC parsing forces `book.type = 64` for manga mode.

## Architecture retained

- APP/API + Web dual routes and automatic fallback
- APP dynamic domain server refresh
- Web permanent-link / publication-page domain discovery
- dual-route login and account center
- favourites and watch history
- independent comment center with paging, post and reply
- detail comment entry plus top custom button
- manga image shunts 1-4
- JM image de-scrambling

## Repository publication state

Active Beta3 entries are synchronized in:

- `manifest.json`
- `subscription/beta.json`
- `subscription/comic.json`
- `rss/data/details/beta/jmcomic.json`
- `sources/comic/jmcomic/jmcomic-beta.json`
- `bundles/jmcomic-beta3.json`
- `docs/sources/jmcomic/RELEASE_NOTES.md`
- `docs/RELEASE_LOG.md`

Repository source SHA256: `fb8332ac2d79ffcf9deb7cb4b9030debbac83ac768c073d493f6fb7d0d23b12f`.

## Validation

- Repository JSON parses successfully.
- Complete inline `jsLib` passes syntax construction with V8 `new Function()`.
- Login, explore, detail init, detail intro, TOC, content, and custom-button scripts pass syntax construction.
- No write was made to `asset-core-7f3`.

## Next real-device checklist

1. Detail page should no longer show literal `@onclick` or stray `}`.
2. Detail buttons: 查看评论 / 收藏作品 / 账户中心.
3. Comment body should show plain readable text; avatars should load.
4. Nested replies should display under the correct parent comment.
5. Multi-chapter and single-album TOC should both open.
6. Open one chapter and confirm manga image content and de-scrambling.
7. Recheck Auto, APP/API and Web routes independently.

## Promotion rule

Do not promote to Stable until the user explicitly confirms the real-device test is normal or directly requests Stable promotion.
