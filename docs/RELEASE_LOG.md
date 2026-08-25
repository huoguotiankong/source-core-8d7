# RELEASE LOG

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

Pending:

- Change repository default branch from `main` to `landing` in GitHub settings.
- Complete the first real source end-to-end publication loop.

## Release policy

Future entries should clearly distinguish:

- generated / static-check passed,
- Beta/Test published,
- user real-device confirmed,
- Stable published.

A generated or statically validated version must not be logged as Stable unless the user has confirmed it or explicitly requested the stable update.
