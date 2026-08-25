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

## 2. Default branch low-discoverability setup — resolved

The neutral `landing` branch is now the GitHub default branch.

Current model:

- Default branch / public landing: `landing`
- Actual project / distribution branch: `main`

The `landing` branch contains only a neutral entry file. Existing Raw URLs intentionally continue to use `main`.

## 3. Repository framework has no real migrated book source yet

Manifest, channels, bundles and RSS repository skeleton exist, but the first real source has not yet completed the full publish/import/test loop.

Do not bulk-migrate many sources until one end-to-end source proves the architecture.

## 4. Existing RSS source points to `main` — intentional compatibility

The currently imported RSS source and its channel URLs use `main`.

Do not rename or remove these paths casually. The default branch is now `landing`, but distribution stays on `main` by design.

## 5. RSS UI changes require re-importing the RSS source definition

Channel data (`subscription/stable.json`, `subscription/beta.json`) can update without changing the RSS source definition.

However, changes to the RSS source's own rules, UI logic, category layout or detail-page rendering require the RSS source definition to be re-imported/updated in Legado.

Current rule:

- Keep the already imported `rss/reader-source-repository.json` as the stable RSS definition until a new UI is real-device confirmed.
- Beta UI keeps a stable internal `sourceUrl` identity so newer Beta import files update the same RSS source instead of producing duplicates.
- Promote only after user confirmation.

## 6. `data:` URL in RSS category/detail request path — fixed in Beta 2, awaiting device test

Observed on UI Beta 1:

- `⭐ 正式版` and `🧪 测试版` worked because they used HTTPS Raw URLs.
- `🏠 首页`, `📦 批量导入`, `📖 使用说明` failed with:

  `Expected URL scheme 'http' or 'https' but was 'data'`

Cause:

Legado's RSS AnalyzeUrl path sends these navigation/detail URLs through OkHttp, so `data:` cannot be used as a normal request URL in this path.

Fix in Beta 2:

- Added HTTPS-backed JSON payloads under `rss/data/`.
- All `sortUrl` category entries now use HTTP/HTTPS only.
- Detail links also avoid `data:` and use HTTPS URLs with query parameters.

Still requires user real-device confirmation.

## 7. Book-source identity URL must remain stable across Stable/Beta

Legado uses `bookSourceUrl` to distinguish book sources.

Project rule:

- Same source Stable/Beta -> exactly the same `bookSourceUrl`.
- Do not encode version or channel in `bookSourceUrl`.
- Do not default to the original website homepage.
- Project namespace: `https://sc8d7.invalid/legado/<source-id>-8d7`.

Important compatibility caveat:

Some legacy sources use `bookSourceUrl` as a relative URL base. Such sources must first migrate their runtime base/request URLs before changing identity URL, otherwise search/detail/content may break.

## 8. HTML detail pages and one-click import need real-device verification

Static JSON/JavaScript validation cannot prove that every WebView behavior works in the user's Legado build.

For RSS UI Beta specifically verify:

- category switching,
- native list rendering,
- empty-state cards,
- light/dark theme detail page,
- `legado://import/bookSource` button behavior,
- `legado://import/rssSource` update button behavior,
- manual Raw/jsDelivr route switching.

## 9. Historical Qidian handoff is not the latest project state

A v4.1 engineering handoff report dated 2026-08-16 exists and contains important architectural principles, including module isolation, complete single-JSON delivery, diagnostics, regression checks and real-device confirmation.

However, Qidian development continued after that report. Therefore it must be treated as historical context, not automatically as the latest current baseline.

Before the next major Qidian task, refresh `docs/sources/qidian/PROJECT_HANDOFF.md` using the latest user-confirmed stable source and current test status.

## 10. Public repository low discoverability is not access control

The repository is public so Raw distribution works without authentication.

The landing-branch strategy only reduces accidental discovery. Anyone who knows the exact repository or Raw URL can still access it. This is expected and is not considered a bug.
