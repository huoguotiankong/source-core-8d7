# RELEASE LOG

## 2026-08-25 — RSS repository UI Beta 2

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- Fixed the Beta 1 navigation failure caused by using `data:` URLs in RSS category/detail request paths.
- Added HTTPS-backed payload endpoints:
  - `rss/data/home.json`
  - `rss/data/bundle.json`
  - `rss/data/help.json`
- All Beta 2 top categories now resolve through HTTP/HTTPS only.
- Detail navigation also avoids `data:` request URLs.
- Added a dedicated repository icon asset.
- Added stable Legado source identity policy:
  - same source Stable/Beta share one `bookSourceUrl`,
  - version/channel are not encoded in the identity,
  - project identity namespace uses `https://sc8d7.invalid/legado/<source-id>-8d7`,
  - legacy sources that depend on `bookSourceUrl` as runtime base must migrate their request base before adopting the identity URL.
- Beta 2 import file keeps the same internal Beta RSS `sourceUrl` identity as Beta 1 so importing Beta 2 should update the existing Beta subscription rather than create another one.

Pending real-device verification:

- home / bundle / help categories,
- detail-page opening,
- repository icon display,
- Raw/jsDelivr switching,
- RSS update button,
- future book-source import button behavior.

## 2026-08-25 — RSS repository UI Beta preparation

Status: Beta/Test UI work; no book-source Stable release yet.

Completed:

- User switched GitHub default branch to neutral `landing`.
- Actual project and Raw distribution remain on `main`.
- Reviewed three reference RSS sources supplied by the user.
- Adopted a combined UI direction:
  - native Legado categories and list for browsing,
  - styled HTML detail page for metadata and import actions,
  - explicit Stable / Beta separation,
  - separate batch-import area,
  - GitHub Raw primary line with jsDelivr manual fallback,
  - no required remote-JS runtime dependency for the repository RSS source.
- Extended subscription metadata schema for version, tags, changelog and backup URL.
- Prepared a separate RSS UI Beta path so the existing confirmed RSS source is not overwritten before real-device testing.

## 2026-08-25 — Repository foundation

Status: infrastructure / no book-source Stable release yet.

Completed:

- Created and connected `source-core-8d7` as the dedicated 阅读 / Legado repository.
- Established hard isolation from the 海阔视界 repository `asset-core-7f3`.
- Added repository-level Manifest skeleton.
- Added Stable and Beta subscription-channel skeletons.
- Added Stable and Beta batch Bundle skeletons.
- Added `🌈 阅读书源仓库` RSS source.
- Corrected the RSS import workflow: Raw JSON URL is used inside Legado's import dialog; `legado://import/...` is reserved for external one-click import.
- User confirmed the RSS source imports successfully in the real Legado app.
- Created a neutral `landing` branch for low casual discoverability while preserving real distribution on `main`.
- Added long-term project documents:
  - `PROJECT_PLAN.md`
  - `DEVELOPMENT_RULES.md`
  - `KNOWN_ISSUES.md`
  - `RELEASE_LOG.md`

## Release policy

Future entries should clearly distinguish:

- generated / static-check passed,
- Beta/Test published,
- user real-device confirmed,
- Stable published.

A generated or statically validated version must not be logged as Stable unless the user has confirmed it or explicitly requested the stable update.
