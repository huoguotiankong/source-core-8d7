# JMComic / 禁漫天堂 Project Handoff

Updated: 2026-08-27

## Current release

- Channel: Stable
- Version: `1.0.0`
- Promoted baseline: `0.1.0-beta8`
- Display name: `◈ 禁漫天堂`
- Legado identity: `https://sc8d7.invalid/legado/jmcomic-8d7`
- Stable source: `sources/comic/jmcomic/jmcomic.json`
- Historical Beta source: `sources/comic/jmcomic/jmcomic-beta.json`
- Stable RSS detail: `rss/data/details/stable/jmcomic.json`
- Stable bundle: `bundles/jmcomic-stable.json`

## Stable promotion

On 2026-08-27 the user explicitly requested promotion of the Beta8 baseline to Stable.

Stable 1.0.0 is a release-channel promotion, not a new feature version. No new business logic was added during promotion. Only release/version metadata and distribution paths were changed.

## Stable 1.0.0 capabilities

- APP/API + Web dual routes.
- Dynamic APP/Web domain refresh.
- Login credentials read through `source.getLoginInfoMap()` with legacy fallback.
- APP login compatibility for `18comicAPP` and app versions `2.1.2 / 2.0.20`.
- AVS persistence and explicit API authentication.
- Manual Web login fallback and login-state diagnostics.
- Account center, favourites and watch history.
- Independent comment center, nested replies, post/reply and detail/custom-button entry.
- Clickable authors/original works/tags and enriched detail metrics.
- Verified Web TOC and manga content.
- APP `/chapter image` compatibility.
- Image shunts 1-4 and JM image de-scrambling.

## Distribution separation

Stable and Beta share the same permanent Legado `bookSourceUrl` identity so imports update the same logical source.

Physical distribution is separate:

- Stable: `sources/comic/jmcomic/jmcomic.json`
- Historical/Future Beta: `sources/comic/jmcomic/jmcomic-beta.json`

After promotion, the active Beta catalog entry is removed. Historical Beta files remain for compatibility/history only. Future unconfirmed changes must return to the Beta file path and Beta channel.

## Repository publication state

Stable 1.0.0 is synchronized in:

- `manifest.json`
- `subscription/stable.json`
- `subscription/comic.json`
- `rss/data/details/stable/jmcomic.json`
- `sources/comic/jmcomic/jmcomic.json`
- `bundles/jmcomic-stable.json`
- `bundles/all-stable.json`
- `docs/sources/jmcomic/RELEASE_NOTES.md`
- `docs/RELEASE_LOG.md`

The active JMComic entry is removed from `subscription/beta.json` and `bundles/all-beta.json`.

Stable source SHA256: `e181e0c0dd917687e98441a4208192977f6799f921591405a4c729d9dd46cb69`.

## Future development rule

Do not modify the Stable file with unconfirmed changes. New work starts from Stable 1.0.0 into the separate Beta path, and returns to Stable only after user real-device confirmation or an explicit Stable-release request.
