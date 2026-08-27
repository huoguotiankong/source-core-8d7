# JMComic / 禁漫天堂 Project Handoff

Updated: 2026-08-27

## Current release

- Channel: Beta/Test
- Version: `0.1.0-beta7`
- Display name: `◈ 禁漫天堂`
- Legado identity: `https://sc8d7.invalid/legado/jmcomic-8d7`
- Repository source: `sources/comic/jmcomic/jmcomic-beta.json`
- RSS detail: `rss/data/details/beta/jmcomic.json`
- Source-specific bundle: `bundles/jmcomic-beta7.json`
- Runtime: complete inline `jsLib`.

## Confirmed real-device progression

- Beta1: repository Raw runtime loader failed because `java` resolved to Rhino `JavaPackage`.
- Beta2: discovery/categories and login buttons recovered.
- Beta3: comment HTML text and nested replies recovered.
- Beta4: detail HTML buttons render and Web TOC opens.
- Beta5: manga content confirmed working; TOC/content frozen from Beta6 onward.
- Beta6: robust JM ID recovery succeeded; detail now shows numeric JM ID and can open the comment center.
- Beta7: fixes the comment WebView bridge protocol and enriches detail metadata/tags.

## Beta7 comment fix

The Beta6 screenshot proved comment-page opening and JM ID resolution are both successful. The remaining failure was the bridge protocol:

- WebView sent `op:"list"` / `op:"post"`.
- Reader-side bridge only checked `action`.
- Reader-side list response nested the result inside `data`, while the page read `list/total` directly.

Beta7 accepts both `action` and `op`, and list responses expose `list`, `total`, and `data` simultaneously.

## Beta7 detail UI

Detail follows the proven Picacg interaction pattern while borrowing Venera's information hierarchy:

- interaction buttons first;
- fixed two-column-ish metrics: views/likes, comments/chapters, JM id/route;
- description;
- information section with clickable authors, works and tags;
- update time.

Clicking an author/tag opens the JM explore/search route for that term.

## Frozen working modules

The following Beta5 behavior remains unchanged:

- Web TOC using original verified selectors;
- manga type `book.type=64`;
- current-page Web image extraction;
- APP `/chapter` object `image` compatibility;
- active-Web image fallback;
- image shunts 1-4;
- JM image de-scrambling.

## Repository publication state

Beta7 synchronized in source / Manifest / Beta subscription / Comic subscription / RSS detail / source-specific bundle / all-beta bundle / Release Notes / Release Log.

Repository Beta7 source SHA256: `6423393d9dfcf10845400fe2916a922cd7cf013a359314175e4155e393a2b6f1`.

## Next real-device checklist

1. Open comment center from detail and top custom button.
2. Confirm comments load instead of “未知操作”.
3. Test previous/next page.
4. Test reply and post.
5. Confirm clickable authors/tags render and open lists.
6. Confirm Beta5 manga content still works.

## Promotion rule

Do not promote to Stable until the user explicitly confirms the source is normal on device or requests promotion.
