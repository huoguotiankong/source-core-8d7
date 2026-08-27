# JMComic / 禁漫天堂 Project Handoff

Updated: 2026-08-27

## Current release

- Channel: Beta/Test
- Version: `0.1.0-beta8`
- Display name: `◈ 禁漫天堂`
- Legado identity: `https://sc8d7.invalid/legado/jmcomic-8d7`
- Repository source: `sources/comic/jmcomic/jmcomic-beta.json`
- RSS detail: `rss/data/details/beta/jmcomic.json`
- Source-specific bundle: `bundles/jmcomic-beta8.json`
- Runtime: complete inline `jsLib`.

## Confirmed real-device progression

- Beta1: Raw runtime loader failed because `java` resolved to Rhino `JavaPackage`.
- Beta2: discovery/categories and login-page buttons recovered.
- Beta3: comment text/nested replies recovered.
- Beta4: detail HTML and Web TOC recovered.
- Beta5: manga content confirmed working; TOC/content frozen.
- Beta6: JM ID recovery restored detail/custom comment entry.
- Beta7: comment bridge protocol fixed; detail authors/tags enriched.
- Beta8: login-specific repair.

## Beta8 login architecture

1. Credentials
   - primary: `source.getLoginInfoMap()`;
   - fallback: legacy `source.getLoginInfo()`.
2. APP login
   - token secret prefers `18comicAPP`;
   - tries APP versions `2.1.2` and `2.0.20`;
   - successful response field `s` is stored as AVS.
3. Auth persistence
   - AVS is written through `ctx.cookie` when available;
   - all later APP/API requests also explicitly send `Cookie: AVS=<value>`.
4. Web login
   - official form fields: username/password/id_remember/login_remember/submit_login;
   - manual Web login button retained as fallback.
5. Diagnostics
   - login status button shows username, UID, AVS state, Web state, API host/version;
   - clear-login button removes local auth state.

## Frozen modules

- Web TOC and manga mode.
- Current-page Web content.
- APP `/chapter image` field compatibility.
- Image shunts / de-scrambling.
- Beta7 detail tag UI.
- Beta7 comment bridge and comment UI.

## Repository publication

Beta8 synchronized in source, Manifest, Beta subscription, Comic subscription, RSS detail, source-specific bundle, all-beta bundle, Release Notes and Release Log.

Repository Beta8 source SHA256: `b6e5efbe29ea2018f1d3246e0e1ce0d9e0347efb4818afd4e9496f69734d7514`.

## Next real-device checklist

1. Fill account/password, tap “账号登录”.
2. Tap “登录状态”; verify username and APP/API AVS state.
3. Open account center.
4. Try favourite or post/reply comment to verify authenticated request.
5. If APP succeeds but Web fails, use “网页登录” and re-check status.

## Promotion rule

Do not promote to Stable until the user explicitly confirms normal operation or requests promotion.
