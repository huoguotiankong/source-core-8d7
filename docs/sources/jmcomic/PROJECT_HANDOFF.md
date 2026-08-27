# JMComic / 禁漫天堂 Project Handoff

Updated: 2026-08-27

## Current release

- Channel: Beta/Test
- Version: `0.1.0-beta6`
- Display name: `◈ 禁漫天堂`
- Legado identity: `https://sc8d7.invalid/legado/jmcomic-8d7`
- Repository source: `sources/comic/jmcomic/jmcomic-beta.json`
- RSS detail: `rss/data/details/beta/jmcomic.json`
- Source-specific bundle: `bundles/jmcomic-beta6.json`
- Runtime: complete inline `jsLib`.

## Confirmed real-device progression

- Beta1: repository Raw runtime loader failed because `java` resolved to Rhino `JavaPackage`.
- Beta2: discovery/categories and login-page buttons recovered after explicit `this.java` compatibility handling.
- Beta3: comment HTML text and nested replies recovered.
- Beta4: detail HTML buttons render correctly and Web TOC opens.
- Beta5: user confirmed manga content now loads. The TOC/content chain is frozen from Beta6 onward unless a new regression is demonstrated.
- Beta6: focuses only on detail/comment entry identity resolution and comment UI refinement.

## Beta6 identity strategy

The previous failure was not the comment API. Both the detail entry and top custom button reached the callback but could not recover the JM album ID from their runtime context.

Beta6 resolves album identity in this order:

1. explicit ID passed by the detail button;
2. current book variable / bookUrl / ruleUrl / safe base URL;
3. page canonical / og:url;
4. a persistent mapping written during search/discovery: normalized title -> JM ID and normalized cover path -> JM ID;
5. detail-page title/cover lookup against the same mapping.

The detail button now carries ID + title + cover. The top custom button uses the same resolver and the current book title/cover.

## Frozen working modules

The following Beta5 behavior is frozen in Beta6:

- Web TOC using the original verified JM selectors.
- Manga type `book.type=64`.
- Current-page Web image extraction.
- APP `/chapter` compatibility including object `image` field.
- Active-Web fallback image extraction.
- Image shunts 1-4.
- JM image de-scrambling.

## Comment center

- APP `/forum` read first, Web fallback.
- `CID / UID / content / photo / replys` normalization retained.
- Posting/replying path retained.
- Beta6 UI refinement: real HTML title, larger cards, nested-reply timestamps, clearer page state and reply target.

## Repository publication state

Beta6 is synchronized in:

- `manifest.json`
- `subscription/beta.json`
- `subscription/comic.json`
- `rss/data/details/beta/jmcomic.json`
- `sources/comic/jmcomic/jmcomic-beta.json`
- `bundles/jmcomic-beta6.json`
- `bundles/all-beta.json`
- `docs/sources/jmcomic/RELEASE_NOTES.md`
- `docs/RELEASE_LOG.md`

Repository Beta6 source SHA256: `c36f64b73b3865a6ac0b1d07de2ae1a85b27407b04f54fe5b47ba189ecf65b69`.

## Next real-device checklist

1. Open a result from search/discovery and verify the detail page shows a numeric JM ID.
2. Tap detail “查看评论”; it should open the comment center without the “无法识别漫画 ID” toast.
3. Tap the top custom button; it should open the same comment center.
4. Confirm Beta5 content remains normal.
5. Confirm comment paging / replies / posting remain normal after UI changes.

## Promotion rule

Do not promote to Stable until the user explicitly confirms the source is normal on device or directly requests Stable promotion.
