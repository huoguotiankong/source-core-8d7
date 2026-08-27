# Manwa / 漫蛙漫画 Project Handoff

Updated: 2026-08-27

## Current release

- Channel: Beta/Test
- Version: `0.1.0-beta4`
- Display name: `◈ 漫蛙漫画`
- Legado identity: `https://sc8d7.invalid/legado/manwa-8d7`
- Beta source: `sources/comic/manwa/manwa-beta.json`
- Beta RSS detail: `rss/data/details/beta/manwa.json`
- Dedicated Beta bundle: `bundles/manwa-beta.json`

## Baseline

This is a new reconstruction. The user-provided Manwa source was used only to confirm working HTML selectors, query parameters and the current image-decryption chain. Its selector-combination discovery UI is not retained.

## Beta4 comment fix

Beta3 real-device feedback:

- Source login diagnostics crashed because `SourceLoginJsExtensions` does not expose DOM helpers such as `getElements`.
- The custom comment button still failed to resolve/open the current manga.

Beta4 is intentionally a narrow repair:

- Login diagnostics are network-only.
- The BookInfo custom button reads the current `book.bookUrl` first, strips the Legado WebView request suffix, extracts `/book/<id>`, and opens that official work page.
- The unverified `#comment` anchor is removed. Manwa's comments, post form and nested replies are server-rendered on the same work page.
- Beta3 detail/TOC/content/domain logic remains frozen.

## Beta3 current state

Beta2 real-device result:

- Cover loads.
- Author is still polluted by synopsis text.
- Custom detail HTML does not render as expected.
- TOC remains loading.
- customButton cannot resolve the current manga URL.

Beta3 investigation found the maintained Keiyoushi/Mihon Manwa implementation. Its confirmed selectors are now the canonical parsing baseline:

- author: `p.detail-main-info-author > span.detail-main-info-value > a`
- status: `p.detail-main-info-author:contains(更新状态) > span.detail-main-info-value`
- genres: `div.detail-main-info-class > a.info-tag`
- description: `#detail > p.detail-desc`
- chapters: `ul#detail-list-select > li > a`
- images: `#cp_img > div.img-content > img[data-r-src]`

Domain discovery also follows the maintained extension's current redirect method: `https://fuwt.cc/mw666` exposes a Base64-encoded `lks` mirror list.

Beta3 removes the Beta2 hotfix runtime block instead of stacking another compatibility implementation.

## Beta2 current state

Beta1 real-device feedback:

- Discovery/list works and returns manga cards.
- Author extraction can bind a large wrapper block, producing synopsis/page text as the author.
- TOC can remain loading because no explicit detail tocUrl is supplied.
- Comment entry can lose the current work URL across WebView/request contexts.

Beta2 repairs:

- Author extraction now accepts only an independent line beginning with `作者：` and uses a conservative HTML fallback.
- Detail parsing runs once in `init`; `intro` only renders cached fields.
- `tocUrl` is explicit and keeps the WebView carrier.
- TOC scans all `/chapter/` anchors and de-duplicates by chapter id.
- Book URL helpers strip Legado request-option suffixes and persist the current work URL through source/book/java contexts.

## Beta1 architecture

### Discovery

Direct sectioned entries:

- Quick: recent updates, most-favourited, new releases.
- Main categories: general, BL, TL, GL, restricted, all.
- Areas: Korea, Japan, China, Taiwan, other, uncategorized.
- Status: serializing, completed, oldest.
- Common tags: direct links; no stored five-filter state and no second “漫画列表” action.

### Account / cookies

- `enabledCookieJar=true`.
- Login is the official Manwa web login/member-center flow.
- Member center, favourites, homepage and announcement entries are available from source login UI.
- No guessed private login API is hard-coded in Beta1.

### Comments

- Detail inline button opens the current work's official comment page.
- BookInfo customButton opens the same comment page.
- The page reuses the official website session and therefore keeps the site's own reply/post/report UI.
- This is intentionally a web-comment bridge in Beta1, not an unverified private comment API implementation.
- Image manga reading uses Legado MangaMenu; reader-menu customButton visibility is an upstream app capability and must not be treated as a source-rule guarantee.

### Dynamic domain

- Runtime requests never use the synthetic `.invalid` identity.
- Last good web base is cached.
- Cache refresh interval: 12 hours.
- Discovery seeds include the current official lost/redirect routes and announced entries:
  - `https://mwmissing8.cc`
  - `https://fuwbm.cc/maKapG`
  - `https://fuwbm.cc`
  - `https://manwagf.cc`
  - `https://manwagc.cc`
  - `https://manwagd.cc`
  - `https://manwa.me`
- Login UI exposes manual refresh and route diagnostics.

### Parsing / reader

- Lists/search/detail/TOC/content stay local.
- Outer operational URLs always use a real TLS-capable Manwa host.
- List/search/book/chapter requests use WebView compatibility.
- Manga images use `.content-img` with `data-r-src` fallback.
- AES/CBC/PKCS5Padding image decode is preserved from the known working Manwa web chain.

## Real-device test checklist

1. Import Beta and verify it updates by permanent `bookSourceUrl`.
2. Open discovery and test several main-category/area/status/tag entries.
3. Search while logged out and after web login.
4. Open a work and verify title, cover, author, details, TOC and latest chapter.
5. Open several chapters and verify decrypted images and continuous reading.
6. Open source login -> official web login -> member center; verify cookie persistence after closing/reopening.
7. Open favourites.
8. Open comments from the detail inline button and the BookInfo customButton; verify existing comments, replies and posting state.
9. Run “刷新最新网址” and “线路诊断”; verify the source survives a changed web domain.
10. Check behavior under Cloudflare/region restrictions and report the exact screenshot/error if a route fails.

## Release policy

This version is unconfirmed and must remain Beta/Test. Do not publish a Stable Manwa source until the user confirms real-device operation or explicitly requests promotion.
