# JMComic / 禁漫天堂 Project Handoff

Updated: 2026-08-26

## Current release

- Channel: Beta/Test
- Version: `0.1.0-beta1`
- Display name: `◈ 禁漫天堂`
- Legado identity: `https://sc8d7.invalid/legado/jmcomic-8d7`
- Repository source: `sources/comic/jmcomic/jmcomic-beta.json`
- RSS detail: `rss/data/details/beta/jmcomic.json`
- Runtime: `sources/comic/jmcomic/runtime/runtime-1.part` ... `runtime-5.part`

## Baseline

The local complete Beta1 JSON remains the functional baseline. The repository version keeps the same search/detail/TOC/content rules and replaces only the large shared `jsLib` with a five-part Raw loader plus cache.

The runtime split points correspond to the original shared jsLib sequence around characters 8000 / 16000 / 24000 / 32000. Boundary inspection confirms that functions and quoted HTML/JS strings continue across parts in their original order.

## Architecture

1. Domain Manager
   - APP/API dynamic domain servers
   - Web permanent-link / publication-page discovery
   - last-success route cache and fallback
2. APP/API Client
   - encrypted response handling
   - login/account/search/detail/chapter/comment endpoints
3. Web Client
   - login/search/detail/chapter/comment fallbacks
4. Account
   - dual-route login
   - account center
   - favourites and watch history
5. Manga Runtime
   - TOC / chapter image list
   - image shunts 1-4
   - JM image de-scrambling
6. Comment Center
   - APP `/forum` read first, Web fallback
   - Web post/reply first, APP `/comment` fallback
   - detail entry and custom-button entry share one comment UI

## Repository publication state

The following active repository entries are synchronized for Beta1:

- `manifest.json` -> `jmcomic`
- `subscription/beta.json` -> `jmcomic`
- `subscription/comic.json` -> `jmcomic`
- `rss/data/details/beta/jmcomic.json`
- `sources/comic/jmcomic/jmcomic-beta.json`
- five runtime parts under `sources/comic/jmcomic/runtime/`

The repository RSS UI already points its `🖼 漫画` category directly at `subscription/comic.json` and its `🧪 测试版` category at `subscription/beta.json`, so no RSS identity migration is required for JMComic.

## Static validation completed

- Local complete JSON parses successfully.
- Local complete shared jsLib parses successfully in static JS checks.
- Repository source JSON parses successfully.
- Runtime part boundaries were inspected against the local Beta1 baseline and remain continuous.
- Stable/Beta identity remains `https://sc8d7.invalid/legado/jmcomic-8d7`.
- No write was made to `asset-core-7f3`.

## Real-device checklist

Before Stable promotion, test in Legado:

1. Refresh available domains and run route diagnostics.
2. Search in Auto mode.
3. Force APP/API route and test search/detail/TOC/content.
4. Force Web route and test search/detail/TOC/content.
5. Test multi-chapter and single-album works.
6. Test image shunts 1-4 and newer scrambled images.
7. Login and open account center.
8. Test favourites and watch history.
9. Open comments from the detail-page entry.
10. Open comments from the top custom button.
11. Test comment paging, posting and replies.
12. Confirm fallback behavior after deliberately switching to an unavailable route/domain.

## Promotion rule

Do not promote this source to Stable until the user explicitly confirms the real-device test is normal or directly requests Stable promotion.
