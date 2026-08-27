# JMComic / 禁漫天堂 Project Handoff

Updated: 2026-08-27

## Current release

- Channel: Beta/Test
- Version: `0.1.0-beta4`
- Display name: `◈ 禁漫天堂`
- Legado identity: `https://sc8d7.invalid/legado/jmcomic-8d7`
- Repository source: `sources/comic/jmcomic/jmcomic-beta.json`
- RSS detail: `rss/data/details/beta/jmcomic.json`
- Source-specific bundle: `bundles/jmcomic-beta4.json`
- Runtime: complete inline `jsLib`; Beta1 runtime parts are historical only.

## Real-device history

### Beta1

Repository delivery used a five-part Raw loader. Legado resolved `java` as Rhino `JavaPackage java` during jsLib initialization, so `java.ajax` failed. Discovery and all login-page actions were unusable.

### Beta2

Removed startup Raw loading and resolved the Legado bridge through `this.java`. User real-device feedback confirmed discovery/category pages and login-page buttons recovered.

### Beta3

Fixed JM forum comment normalization:

- API fields `CID / UID / content / photo / replys`
- HTML comment body -> readable text
- relative avatars -> `/media/users/`
- nested `replys` recursively normalized

Real-device feedback confirmed comment bodies and nested replies are now readable.

Beta3 remaining failures:

- detail JS-returned buttons were still rendered as literal `@onclick` text
- detail showed `baseUrl 未定义`
- catalog stayed loading

### Beta4

1. Detail
   - Adds the same `<usehtml>...</usehtml>` wrapper used by the verified Picacg detail page.
   - Removes direct jsLib dependence on the rule-local `baseUrl`.
   - Adds safe ID resolution from book variable, bookUrl, ruleUrl, then safe baseUrl.
2. Catalog
   - Detail precomputes a real Web album URL in `jm_toc`.
   - TOC returns to the original user-provided source selector: `class.btn-toolbar.0@tag.a||.reading`.
   - Chapter body still uses Auto / APP/API / Web routes.
3. Comments
   - Beta3 comment behavior is frozen in Beta4; no UI rewrite.

## Architecture retained

- APP/API + Web dual routes and fallback
- APP dynamic domain refresh
- Web permanent-link/publication-page domain discovery
- dual-route login and account center
- favourites and watch history
- independent comment center with paging/post/reply
- detail comment entry and top custom button
- manga image shunts 1-4
- JM image de-scrambling

## Repository publication

Beta4 is synchronized to:

- `manifest.json`
- `subscription/beta.json`
- `subscription/comic.json`
- `rss/data/details/beta/jmcomic.json`
- `sources/comic/jmcomic/jmcomic-beta.json`
- `bundles/jmcomic-beta4.json`
- `bundles/all-beta.json`
- `docs/sources/jmcomic/RELEASE_NOTES.md`
- `docs/RELEASE_LOG.md`

Repository source SHA256: `df81fa4a10ab178454c0a59c52dd3ee0bf5ed9ef1da06704c04df4a5fb352598`.

## Next real-device checklist

1. Detail interaction buttons should render as buttons, not literal `@onclick` text.
2. Detail should no longer show `baseUrl 未定义`.
3. Open catalog for single-album and multi-chapter works.
4. Open one chapter and verify image body.
5. Recheck comment center; Beta3 behavior should remain unchanged.
6. Test Auto, APP/API and Web content routes.

## Promotion rule

Do not promote to Stable until the user explicitly confirms the real-device test is normal or directly requests Stable promotion.
