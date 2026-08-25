# KNOWN ISSUES

> Updated: 2026-08-25

## 1. RSS import method confusion — understood

Symptom:

Legado shows `ImportError: 格式不对` when a `legado://import/rssSource?src=...` URI is pasted directly into the in-app "导入订阅源" input.

Cause:

The in-app import field expects JSON, an HTTP/HTTPS URL, or a supported local URI. The `legado://import/...` form is an external one-click association URI handled by Legado's online-import activity.

Current rule:

- In Legado's import dialog, paste the Raw JSON URL directly.
- Use `legado://import/rssSource?src=...` only as an external one-click launch/import link.

User confirmed the current Raw RSS URL imports successfully.

## 2. Default branch is still `main` — pending manual repository setting

A neutral `landing` branch has been created and cleaned.

Target:

- Default branch: `landing`
- Actual project/distribution branch: `main`

This reduces casual discovery through the repository homepage/default-branch search while preserving all existing Raw URLs on `main`.

The connector used for project maintenance cannot currently change the repository default-branch setting, so this step requires a GitHub repository setting change by the user.

## 3. Repository framework has no real migrated book source yet

Manifest, channels, bundles and RSS repository skeleton exist, but the first real source has not yet completed the full publish/import/test loop.

Do not bulk-migrate many sources until one end-to-end source proves the architecture.

## 4. Existing RSS source points to `main` — intentional compatibility

The currently imported RSS source and its channel URLs use `main`.

Do not rename or remove these paths casually. Switching the GitHub default branch to `landing` does not require changing Raw URLs and should not break the already imported RSS source.

## 5. Historical Qidian handoff is not the latest project state

A v4.1 engineering handoff report dated 2026-08-16 exists and contains important architectural principles, including module isolation, complete single-JSON delivery, diagnostics, regression checks and real-device confirmation.

However, Qidian development continued after that report. Therefore it must be treated as historical context, not automatically as the latest current baseline.

Before the next major Qidian task, refresh `docs/sources/qidian/PROJECT_HANDOFF.md` using the latest user-confirmed stable source and current test status.

## 6. Public repository low discoverability is not access control

The repository is public so Raw distribution works without authentication.

The landing-branch strategy only reduces accidental discovery. Anyone who knows the exact repository or Raw URL can still access it. This is expected and is not considered a bug.
