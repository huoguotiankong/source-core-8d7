# Manwa / 漫蛙漫画 Project Handoff

Updated: 2026-08-27

## Current release

- Channel: Beta/Test
- Version: `0.1.0-beta13`
- Display name: `◈ 漫蛙漫画`
- Legado identity: `https://sc8d7.invalid/legado/manwa-8d7`
- Beta source: `sources/comic/manwa/manwa-beta.json`
- Beta RSS detail: `rss/data/details/beta/manwa.json`
- Dedicated Beta bundle: `bundles/manwa-beta.json`

## Baseline

This is a new reconstruction. The user-provided Manwa source was used only to confirm working HTML selectors, query parameters and the current image-decryption chain. Its selector-combination discovery UI is not retained.

## Beta13 native DOM + load watchdog

Beta12 real-device result:

- layout improved, but the bottom state can stay forever at “正在加载更多评论 / 加载中”;
- no new comments are appended.

Root issue:

- Beta12 introduced a guessed generic `fetch` path for next-page loading;
- Manwa's current comment transport is not proven to expose a stable next-page URL suitable for direct fetch in the embedded browser;
- a pending request leaves the custom `loading=true` state uncleared.

Beta13 strategy:

1. Remove custom next-page fetch.
2. Keep `#comment` in the site's original DOM rather than moving it.
3. Preserve the full ancestor chain for comments, login/comment modal and hidden book/session fields.
4. Isolate presentation by hiding unrelated siblings only.
5. Trigger native scroll paths: `window`, `document`, and jQuery window scroll if present.
6. Prefer real comment-area “更多评论 / 下一页” controls and continue excluding reply-more controls.
7. Add an 8-second watchdog so every loading attempt resolves.
8. Keep MutationObserver to detect any native comment append immediately.
9. Preserve Beta12 Grid layout and freeze content/detail/TOC/login/domain.

If Beta13 still reports “原站本次未返回更多评论”, the next diagnostic step should capture the site's actual XHR/fetch request produced by its sort/comment controls instead of guessing endpoint parameters.

## Beta12 grid comments + continuous loading

Latest real-device feedback:

- The first comment card can still split into a left parent-comment column and a right nested-reply column.
- The header reports hundreds of comments, but scrolling reaches the end of the initially rendered batch and does not load more.

Layout diagnosis from the screenshot and current rule:

- Beta11 sets the top-level comment `li` to `display:flex`.
- If the live site's nested reply/sublist is a direct sibling of `.detail-list-comment-info` rather than nested inside it, flex treats it as a third horizontal child.
- That exactly matches the observed right-side reply column and squeezed parent text.

Beta12 design:

1. Top-level comment card is a two-column CSS Grid: avatar / content.
2. Direct child reply/sublist/go nodes are forced into the next grid row on the content column.
3. Full nested comments use a 34px + content Grid.
4. Keep Beta11 dynamic MutationObserver/media handling concept, but fold it into the new V12 runtime instead of stacking another compatibility layer.
5. Add a load-more controller:
   - near-bottom scroll;
   - touch-end;
   - IntersectionObserver sentinel;
   - manual load-more button.
6. Prefer native site controls. Recognize loading-more / more-comments / next-page patterns and explicitly reject reply-more controls.
7. If a next-page URL exists, fetch it same-origin, parse its `#comment` list, de-duplicate by id/user/date/content signature, and append.
8. Show `已显示 X / 总数` status and visible failure text instead of silently stopping.
9. Keep content/detail/TOC/login/domain frozen.

## Beta11 dynamic reply + media comment UI

Beta11 is a narrow continuation of the Beta10 comment rewrite.

Observed current Manwa behavior from the live site:

- work pages expose server-rendered comments and chapter attribution;
- comment bodies can be plain text or image/sticker content;
- some comments expose “查看更多回复数 (N)” and insert/reveal nested replies after interaction.

Risk found in Beta10:

- `mark(c)` ran only during initial construction of the custom comment shell;
- replies inserted later by the site's own JavaScript would not receive `mw-sub-comment / mw-sub-full` classes and could fall back to the original site's legacy layout.

Beta11 fix:

1. Observe `#comment` with `MutationObserver({childList:true, subtree:true})`.
2. Re-run the idempotent normalizer after every dynamic child update.
3. Keep top-level and nested class assignment separate.
4. Detect image-heavy comment bodies and mark them as media comments.
5. Constrain comment/sticker images to 180px and viewport-safe width.
6. Style chapter links and “查看更多回复数” for the custom sheet.
7. Do not change login, content, detail, TOC or domain modules.

## Beta10 comment layout + compact login

Beta9 real-device confirmation:

- comments now load into the custom page;
- the header/count and ordinary top-level comments are usable;
- a comment containing nested replies can collapse the parent content into a very narrow vertical strip;
- level/diamond art can appear as a second large image below the avatar;
- the native login page is functional but visually inefficient because every action occupies a large full-width pill.

Confirmed CSS cause:

The Manwa-compatible mobile stylesheet defines:

- `.detail-list-comment-cover { position:absolute; ... }`
- `.detail-list-comment-info { padding-left:55px; }`
- `.detail-list-comment-sublist` and reply elements with their own margins/float-era layout.

Beta9's custom CSS added flex but did not fully reset those legacy declarations. The result was a mixed absolute + padded + flex layout, which only becomes obvious when nested reply DOM consumes additional width.

Beta10 rules:

1. Reset the original absolute positioning, left padding, floats, width and margins before applying the card layout.
2. Tag only the first-level `ul.detail-list-comment > li` as top-level comment cards.
3. Tag `.detail-list-comment-sublist > li` separately; if a child contains its own cover/info block, treat it as a full nested comment card.
4. Force reply/sublist containers to 100% width and clear floats.
5. Treat the first cover image as the avatar and any later images as level/badge art.
6. Keep the comment-ready gate from Beta9 unchanged.
7. Login UI uses 0.40 flex-basis for two-column pairing, providing enough space for the app's divider/margins; all eight actions remain.
8. Content/detail/TOC/dynamic-domain logic remains frozen.

## Beta9 upgrade migration + comment ready gate

Latest real-device screenshots are from the Beta5-Beta7 generation, not the Beta8 repository payload: the login page still contains the image-route selector. They confirm three practical failures that must be protected against during in-place upgrades:

- old login-form state can survive because the source keeps the same permanent `bookSourceUrl`;
- Beta5/Beta7 raw image URLs can produce a chapter with a valid page count but failed image loads;
- the custom comment shell can be created before Manwa has actually populated `#comment`, leaving a correct title/count over a blank body.

Beta9 policy:

1. The login page contains buttons only; the obsolete image-route selector is removed.
2. `login()` is defined first and clears legacy stored login-form state after confirmation. The old source KV `mw_img_choice_v5` is reset to Default.
3. Content remains exactly on the Beta3/Beta4 proven request model: chapter WebView request + per-image User-Agent/Referer options + existing AES decryptor.
4. Comment presentation uses a ready gate. The preload reveals `#comment`, attempts the native comment-tab activation, scrolls the section into view to trigger lazy rendering, and waits for real `.detail-list-comment > li` content before moving the DOM.
5. A 15-second timeout no longer leaves a blank page. It preserves the comment container and prints `items / children / text` counts for the next diagnostic iteration.
6. Detail/TOC and dynamic-domain code remain frozen.

External verification during Beta9 also confirmed the maintained Manwa crawler reads comments from `#comment .detail-list-comment > li`, while the current Keiyoushi/Mihon extension still uses `#cp_img > div.img-content > img[data-r-src]` for manga images. These reinforce the existing selector baseline without introducing a new private API.

## Beta8 stability rollback

Beta7 real-device result:

- Login form confirm throws `Function login not implements!!!`.
- Manga chapter opens but images fail to load.
- Custom comment sheet opens and shows title/count, but the comment body is blank.

Root causes:

1. Legado `SourceLoginDialog.login()` always calls a JavaScript `login()` function when the stored login form is non-empty. The source did not implement it.
2. The Beta5 image-route experiment changed both chapter URL parameters and per-image request options; this regressed a previously working image chain.
3. The Manwa comment DOM is the real `#comment` node and is intentionally rendered with `display:none` until the website's tab switcher shows it. Beta7 moved the node but never explicitly removed that hidden state.

Beta8 repairs:

- implement a no-op/success `login()` for the form-save contract;
- remove the Beta5 image-route UI/runtime and restore the Beta3/Beta4 chapter + image request chain;
- use `#comment` directly and force `display:block`;
- move `#win-comment`, `#book_id`, and `#session_uid` into the custom comment sheet so the original posting/session logic remains available;
- freeze the working detail/TOC baseline.

## Beta7 custom comment view

Beta6 real-device result:

- The custom button finally opens the correct current work.
- The result is still the raw Manwa webpage rather than a custom comment UI.

Beta7 keeps the verified `Book.getBookUrl()/getTocUrl()` path and only changes presentation:

- use Legado `java.showBrowser(url, html, preloadJs, config)`;
- open a 94% height rounded bottom WebView;
- keep the original Manwa comment DOM and website event handlers/Cookie state;
- inject a comment-only skin that identifies the smallest comment container by the presence of comment-form/list signals such as 发表评论, 排序, 举报 and 查看更多回复数;
- move that container into a clean shell, hide the rest of the website, and restyle comment cards/replies;
- preserve official posting/reply/report functionality instead of guessing private write APIs.

The preload script is syntax-checked separately after generation.

## Beta6 official callback API fix

Beta5 real-device result:

- Detail/TOC remain working.
- Custom comment button still reports that the manga id is unresolved.

Repository investigation of Legado itself found the actual callback contract:

- `SourceCallBack.callBackBtn()` injects `event`, `java`, `result`, `book`, and `chapter`.
- `Book` exposes Kotlin/JVM getters including `getBookUrl()`, `getTocUrl()`, and `getName()`.

Beta6 removes the manga-id gate entirely. The custom button reads the current URL through the explicit JVM getters, strips only the Legado request suffix, and calls `java.startBrowser()` directly. It falls back from book URL to TOC URL only when necessary.

Detail/TOC and Beta5 image-source work are frozen.

## Beta5 comment and image-route fix

Beta4 real-device result:

- Cover/detail/TOC are now materially working: latest chapter and first TOC item display correctly.
- Custom-button comment path still cannot identify the manga id.
- Manga images render, but load very slowly.

Beta5 therefore freezes detail/TOC and changes only two domains.

### Comment id persistence

During BookInfo parsing, the current `/book/<id>` is stored in:

- `book.putVariable("mw_book_id_v5", id)`
- `book.putVariable("mw_book_url_v5", url)`
- source KV as a fallback.

Custom-button resolution order is:

`book variable -> book.tocUrl -> book.bookUrl -> source KV`.

The `tocUrl` fallback is important because Beta4 real-device results prove that the current work's TOC route is already correctly resolved.

### Image routes / performance

The maintained Manwa extension exposes image-source switching from the site's `#img-host-modal`. Beta5 implements the same concept:

- fetch and cache the official image-route href parameters;
- login UI selection: Auto / Default / Route 1-6;
- append the selected route parameter to chapter-page requests;
- Auto uses the first discovered alternate route when available;
- remove per-image duplicate request-option JSON so Legado's native manga image loader can cache/concurrently fetch the original image URLs;
- keep the existing AES image decryption unchanged.

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
