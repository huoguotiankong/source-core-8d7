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

## 6. RSS category request compatibility — resolved in Beta 3

Beta 1 failure:

- `首页 / 批量导入 / 使用说明` used `data:` URLs.
- Legado passed them into OkHttp and failed with `Expected URL scheme 'http' or 'https' but was 'data'`.

Beta 2 changed those categories to HTTPS, but the same three categories still failed on the user's device.

Root cause found in Beta 2:

- The category rules called `q()`.
- `q()` called `repo()` as a plain nested function.
- `repo()` depended on `this.source`.
- The nested call lost the expected `this` binding, so only the categories that used `q()` failed; Stable/Beta did not use that path and continued loading.

Beta 3 redesign:

- Removed the `q() -> repo()` category-link chain.
- Category JSON contains explicit HTTPS `detailUrl` values.
- Home / Bundle / Help use the same generic list parser.
- Each detail item has its own HTTPS JSON file under `rss/data/details/`.
- `sortUrl` contains literal HTTPS URLs only.

Real-device result on 2026-08-25:

- User confirmed Beta 3 no longer reports the category loading errors.

This pattern is now the baseline for repository RSS navigation.

## 7. RSS repository icon remote-loading issue — Beta 4 fix pending confirmation

Observed on Beta 3:

- Repository categories load normally.
- The subscription grid still shows Legado's default orange RSS icon instead of the project icon.

The remote `sourceIcon` URL itself exists, so the practical compatibility decision is to avoid depending on remote image loading for the RSS source icon.

Beta 4:

- `sourceIcon` is embedded as a compact `data:image/jpeg;base64,...` value.
- The Beta identity path `rss/reader-source-repository-beta.json` now points to the Beta 4 definition.
- `rss/reader-source-repository-beta4.json` is retained as the versioned snapshot.

Awaiting user real-device confirmation of icon display.

## 8. Book-source identity URL must remain stable across Stable/Beta

Legado uses `bookSourceUrl` to distinguish book sources.

Project rule:

- Same source Stable/Beta -> exactly the same `bookSourceUrl`.
- Do not encode version or channel in `bookSourceUrl`.
- Do not default to the original website homepage.
- Project namespace: `https://sc8d7.invalid/legado/<source-id>-8d7`.

Important compatibility caveat:

Some legacy sources use `bookSourceUrl` as a relative URL base. Such sources must first migrate their runtime base/request URLs before changing identity URL, otherwise search/detail/content may break.

## 9. HTML detail pages and one-click import need real-device verification

Static JSON/JavaScript validation cannot prove that every WebView behavior works in the user's Legado build.

For RSS UI Beta specifically verify:

- native list rendering,
- light/dark theme detail page,
- `legado://import/bookSource` button behavior,
- `legado://import/rssSource` update button behavior.

## 10. Historical Qidian handoff is not the latest project state

A v4.1 engineering handoff report dated 2026-08-16 exists and contains important architectural principles, including module isolation, complete single-JSON delivery, diagnostics, regression checks and real-device confirmation.

However, Qidian development continued after that report. Therefore it must be treated as historical context, not automatically as the latest current baseline.

Before the next major Qidian task, refresh `docs/sources/qidian/PROJECT_HANDOFF.md` using the latest user-confirmed stable source and current test status.

## 11. Public repository low discoverability is not access control

The repository is public so Raw distribution works without authentication.

The landing-branch strategy only reduces accidental discovery. Anyone who knows the exact repository or Raw URL can still access it. This is expected and is not considered a bug.

## Resolved — RSS detail HTML returned as plain article text

- Symptom: source/detail entries displayed only summary text; HTML buttons were not rendered.
- Fix: open generated HTML through `java.startBrowser(data:text/html;base64, ...)` and use `legado://import/importonline?src=...`.
- Status: fixed in RSS UI Beta 7, pending real-device confirmation.
## 12. Qidian `.invalid` identity broke runtime behavior — fixed in Beta hotfix

Observed on-device after repository import:

- source imported successfully,
- book detail showed `书籍信息获取失败`,
- login/settings page could not open.

Cause:

- the publisher replaced the mature Qidian `bookSourceUrl` with `https://sc8d7.invalid/...`;
- this source uses a Qidian same-origin identity for runtime base/Cookie/WebView compatibility;
- the original working baseline used `https://m.qidian.com/?qf_source=v2922_audio_webview_crypto_bridge_fix`.

Fix:

- restore that mature same-origin identity for both Beta and future Stable;
- keep uniqueness through its stable `qf_source` marker instead of a fake host;
- do not blindly apply the generic `.invalid` namespace to sources with same-origin runtime dependencies.

Status: fixed in repository Beta, pending user real-device re-test.

## 13. Large dynamic Qidian `loginUi` fails before rendering in current Legado build

Observed during v4.2.1-alpha2 recovery testing:

- search remained functional;
- a minimal static login UI opened normally;
- the original large dynamic `@js:` login UI, a reduced dynamic version, and a try/catch diagnostic wrapper all failed before any page content appeared.

Confirmed compatible direction:

- use pure static `loginUi` for the first-level settings page;
- use `java.startBrowserAwait` for multi-level HTML settings pages;
- keep business runtime logic in existing `jsLib/loginUrl` helpers instead of evaluating a large dynamic login UI at page-open time.

Status: adopted by `qidian-next` 0.1.0-beta1; further real-device regression testing pending.

## 14. `startBrowserAwait(data:)` custom scheme is treated as external app navigation

Observed in qidian-next Beta2 on real device:

- Account HTML buttons did not execute source actions.
- Diagnostic buttons using `qfnext://...` displayed Android's "open another app" prompt and then "no app can perform this action".

Cause: custom-scheme navigation from the `data:` page is not routed through the source's `shouldOverrideUrlLoading` in this Legado/WebView path.

Fix in `0.1.2-beta3`: do not use custom schemes for settings actions. Encode the chosen action as ordinary HTML form/select state, return with the browser ✓ button, then execute the corresponding `loginUrl` function.

Status: Beta fix pending real-device confirmation.

## 15. Shenmo account helpers removed while callers remained — fixed in qidian-next Beta5

Observed on real device in `0.1.3-beta4`: Shenmo login failed with `ReferenceError: qfSmCtxV30 未定义`. Historical working versions showed that four helper functions had been removed during later cleanup while `qfSmLoginV30`, check, backend and logout still called them.

Fix: restore the mature `qfSmCtxV30 / qfSmInputV30 / qfSmTrimV30 / qfSmSaveCredsV30` implementations and keep Provider-specific account actions. Status: Beta fix pending real-device confirmation.
## 16. Repository self-update and Stable/Beta route collision — fixed in RSS UI Beta10

Observed on real device after `🌈 起点增强 1.0.0` promotion:

- repository subscription update page did not import/update the RSS definition;
- old qidian-next detail still showed accumulated Beta3-Beta6 sections;
- an old cached Beta page could import the newly promoted Stable file.

Root causes:

- Beta9 used `legado://import/importonline` for RSS self-update instead of `legado://import/rssSource`;
- update metadata still pointed to an obsolete Beta3 definition;
- Stable reused the same qidian-next detail/source URLs that old Beta entries had referenced, so cached Beta entries could resolve to Stable after promotion;
- RSS category query revision remained `v=9`, allowing stale channel payloads to persist.

Fix in Beta10:

- RSS self-update uses the RSS-specific import URI;
- Beta home/update metadata points to the stable Beta identity file `reader-source-repository-beta.json`;
- category cache revision bumped to `v=10`;
- Stable qidian-next detail moved to a new Stable-only physical path;
- future qidian-next Beta releases must use separate Beta source/detail paths.

Status: published to RSS UI Beta10; awaiting user real-device confirmation.

## 17. 情无账号会话有效但 VIP 正文被服务端拒绝 — 1.0.1-beta1 修复中

真机现象：账号管理显示情无登录/检测成功，但固定情无读取 VIP 章节仍返回 `Service request failed. Reference: ...`。

定位：登录层使用情无自己的 UA/Referer，但 lazy `limited_qw` 正文模块退化成仅发送 `Accept: application/json`；历史已验证版本要求 `/qd/content.php` 显式使用情无 UA + `Referer: <base>/ranking.html`。当前代码还会对所有 VIP 失败无条件续签，导致服务业务失败也被误判为登录问题。

Beta 修复：恢复情无正文专属 UA/Referer/Accept；只对明确认证错误续签；将“账号会话有效”和“VIP正文已验证”拆成两层状态；保留服务端 Reference 供后续排查。

Status: `🌈 起点增强 1.0.1-beta1` 待真机验证；Stable 1.0.0 未修改。

## 18. RSS old/new list entries mixed and detail page regressed to plain text — fixed in Beta11

Real-device symptoms after Beta10:

- the Home category displayed the new Beta10 cards followed by older Beta3-era cards;
- the Stable category displayed the same current source more than once even though `subscription/stable.json` contained only one item;
- opening a source detail showed only a plain summary instead of the styled detail/import page.

Interpretation: Legado retained category/article state across RSS definition updates, and Beta10 had also regressed from the earlier `java.startBrowser(data:text/html;base64, ...)` detail-opening pattern back to returning HTML directly from `ruleContent`.

Beta11 mitigation:

- rename categories and use `ui=11` URLs to create a fresh cache key;
- de-duplicate list items in `ruleArticles`;
- explicitly override `ruleDescription` to prevent stale older rules from winning after an in-place RSS update;
- explicitly open the generated card page through `java.startBrowser`;
- keep source detail pages current-state only.

Status: published as RSS UI `0.3.1-beta11`, awaiting real-device confirmation.

## 19. RSS Beta11 leaves an empty detail page behind — fixed in Beta12

Real-device symptom: opening a repository item launched the styled card page, but after returning an additional blank RSS detail page remained in the navigation stack.

Cause: Beta11 opened a second browser from inside `ruleContent` with `java.startBrowser(...)` and then returned a blank string to the already-open RSS detail page.

Fix: return the styled HTML directly from `ruleContent` and let the current RSS detail WebView render it; do not launch a second browser. `ruleDescription` remains overridden so old summary rules do not take over. Cache revision bumped to `ui=12`.

Status: published as RSS UI `0.3.2-beta12`, awaiting real-device confirmation.
## 20. RSS UI releases accumulated old Home/Stable entries — cache model replaced in Beta13

Real-device symptom: after updating Beta11 -> Beta12, Home displayed the three Beta12 items followed by the same three Beta11 items. The channel JSON itself was not duplicated.

Root cause: previous mitigation changed category/detail URLs with `?ui=N`. Legado persists RSS articles, so each new detail URL could be treated as a different stored article; in-list de-duplication cannot remove articles already stored by an older RSS definition.

Beta13 strategy: perform one category-name reset, then freeze category names, category URLs and item detail URLs permanently. Mutable version data is shown only inside detail content. Do not mint new article URLs for routine UI releases.

Status: Beta13 published for real-device confirmation.
## 21. Qidian detail page was visually dense and blocked on multiple enrichment requests — redesigned in 1.1.0-beta1

Symptom: the detail page exposed many useful statistics but duplicated native metadata and could wait on several sequential APP/Web/Atom/third-party fallbacks before rendering.

Beta fix: first paint now parses only the current Qidian response and per-book cache; optional interaction features are opened on demand. The custom area is reduced to metrics, shortcuts, tags and synopsis.

Status: Beta 1.1.0-beta1 published for real-device speed/UI regression testing.
## 22. Detail beta1 became too sparse and its table metrics rendered incorrectly on real devices — adjusted in 1.1.0-beta2

Symptom: the first performance-focused detail redesign rendered only a few metrics on some books, and the HTML table was flattened into misaligned vertical text on the tested Legado build.

Beta fix: restore rich fields from the current response/cache while keeping zero extra first-paint requests; replace table layout with plain HTML rows and hide unavailable fields.

Status: Beta 1.1.0-beta2 published for real-device UI/information-density testing.

