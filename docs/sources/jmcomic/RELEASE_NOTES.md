# JMComic / 禁漫天堂 Release Notes

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

Main `docs/RELEASE_LOG.md` merge remains pending because the current connector only supports whole-file replacement and the project log is too large to rewrite safely from a truncated response. This source-local note is the authoritative interim release record; merge it into the main log when a safe append/server-side publication path is available.

The project-wide `bundles/all-beta.json` was already empty before JMComic publication. It is intentionally not overwritten with a partial JMComic-only array because doing so would drop unrelated Beta sources. A source-specific bundle artifact is maintained separately until the global bundle builder is restored.
