# RELEASE LOG

## 2026-08-25 — Qidian Next v0.1.5-beta6

Status: Beta/Test; secondary-settings UX phase 1 awaiting user real-device confirmation.

Changes:

- Redesigned Content, Account Management and Diagnostics secondary pages with one card-based visual system.
- Content uses strategy/Provider chips, live route summary and a conditional STV card.
- Accounts use Provider tabs, Provider-specific fields and compact action buttons.
- Diagnostics prioritize common tools and collapse advanced actions.
- Preserved the real-device-compatible `startBrowserAwait` + browser ✓ return/save/execute mechanism.
- First-level login UI and reading business modules remain unchanged.
- SHA256: `60e175bc11986157e9a69be57990cefe0c1855b7e90f07b0a5cca1d0ef3be8b6`.


## 2026-08-25 — Qidian Next v0.1.4-beta5

Status: Beta/Test; Shenmo account dependency repair awaiting user real-device confirmation.

Changes:

- Restored `qfSmCtxV30`, `qfSmInputV30`, `qfSmTrimV30`, and `qfSmSaveCredsV30` from the mature historical Shenmo account implementation.
- Fixed the real-device `ReferenceError: qfSmCtxV30 未定义` path.
- Made account actions Provider-specific; Shenmo no longer exposes unsupported web-login.
- Search/detail/catalog/content/review/Provider reading logic remains unchanged.
- SHA256: `f694d686980a2c1aa71d86313eb16931ca578e9c23e18dd136a1c175955d8341`.


## 2026-08-25 — Qidian Next v0.1.3-beta4

Status: Beta/Test; compact account/diagnostic UX awaiting user real-device confirmation.

Changes:

- Split Account Management into Provider selection and short action selection instead of one oversized combined list.
- Show only the active Provider account card.
- Reset the selected action after execution to prevent accidental repeat operations.
- Simplified Diagnostics to the same compact return-and-execute flow.
- Reading business modules remain unchanged.
- SHA256: `9c8b63ce4c000456d47bfd3d2284416680292ee66dfbc3d358395eedff28b896`.

## 2026-08-25 — Qidian Next v0.1.2-beta3

Status: Beta/Test; account/diagnostic action-return fix awaiting user real-device confirmation.

Changes:

- Removed the Beta2 `qfnext://` custom-scheme bridge after real-device confirmation that Android treats it as external-app navigation.
- Account Management now saves fields and chooses one action inside the HTML page; the action runs only after tapping the browser ✓ button to return.
- Diagnostics now uses the same proven select-and-return mechanism.
- Kept the Unicode unique DOM id fix from Beta2.
- Search/detail/catalog/content/review/Provider business logic is unchanged.
- SHA256: `a27682beb478c9523c554024650d9fffd72ef669692c49db839f6dbeb6dd3187`.


## 2026-08-25 — Qidian Next v0.1.1-beta2

Status: Beta/Test; account/diagnostic compatibility fix awaiting user real-device confirmation.

Changes:

- Fixed duplicate DOM ids generated from Chinese setting keys.
- Reworked Account Management and Diagnostics actions to use `qfnext://` WebView interception instead of mutated-DOM action return.
- Kept search/detail/catalog/content/review/Provider business logic unchanged from Beta1.
- SHA256: `031677a7889e2eab926c9a508b422fde85864527dc37bb44c807088a496d2ff3`.


## 2026-08-25 — Qidian Next v0.1.0-beta1

Status: Beta/Test; published to the subscription repository, awaiting full user real-device regression.

Changes:

- Started independent source line `qidian-next` / `🌈 起点助手·新架构` instead of overwriting the existing Qidian source.
- Used the user-selected loginfix4 static two-column login page as the first UI baseline.
- Kept the v4.2.1-alpha2 search/detail/catalog/content/review/Provider business baseline unchanged.
- Secondary settings use `java.startBrowserAwait`; large dynamic `@js:` login UI is no longer used.
- Published complete source JSON, Beta catalog entry, Beta bundle entry, Manifest metadata, RSS detail payload and source handoff.
- Permanent identity: `https://m.qidian.com/?qf_source=qidian_next_8d7`.
- SHA256: `708e871bfae7fc50cac55e19fa73b34b63bb6710494295d12aa712a218548064`.


## 2026-08-25 — Qidian v4.2.1-alpha2 identity hotfix

Status: Beta/Test; awaiting user real-device confirmation.

Changes:

- Reverted the repository-only `.invalid` `bookSourceUrl` experiment after real-device failure.
- Restored the mature same-origin identity `https://m.qidian.com/?qf_source=v2922_audio_webview_crypto_bridge_fix`.
- No Qidian business rules were changed.
- Synchronized complete source JSON, Beta Bundle, Manifest and RSS detail metadata.
- Stable/Beta will keep this same identity after confirmation.


## 2026-08-25 — RSS repository UI Beta 7

Status: Beta/Test; awaiting user real-device verification.

Changes:

- RSS detail cards now open explicitly with `java.startBrowser(data:text/html;base64, ...)`.
- Source, bundle and repository-update buttons use `legado://import/importonline?src=...`.
- Qidian Beta can be imported/updated from its repository detail card.


## 2026-08-25 — Qidian official ecosystem v4.2.1-alpha2 Beta

Status: Beta/Test; uploaded source validated and SHA256 verified, awaiting user real-device confirmation.

Changes:

- Published the current uploaded `起点官方生态` baseline to the Beta channel.
- Assigned permanent Legado identity `https://sc8d7.invalid/legado/qidian-official-8d7`.
- Kept existing business rules unchanged; only the top-level identity URL was replaced before publication.
- Published complete source JSON, Beta catalog entry, Beta bundle, Manifest metadata and RSS detail payload.
- Final SHA256: `c952233cc72468a79bd94b784cfe34c0101b0eacecb39b52bff7b9fab691a8a3`.


## 2026-08-25 — RSS repository UI Beta 6

Status: Beta/Test; awaiting user real-device icon verification.

Changes:

- Kept the Beta 3 HTTPS-only category/navigation baseline already confirmed on the user's device.
- Added a real compact 96×96 PNG asset at `assets/reader-repo-icon.png`.
- Changed `sourceIcon` from Base64/Raw experiments to the jsDelivr CDN URL for the PNG asset.
- Updated the stable Beta identity file `rss/reader-source-repository-beta.json` without changing its internal `sourceUrl` identity.
- Added snapshot `rss/reader-source-repository-beta6.json`.

## 2026-08-25 — Large source direct-upload publisher

Status: infrastructure ready; Qidian Beta publication waiting for one original JSON upload into `main/incoming/`.

Changes:

- Replaced the slow multi-part ChatGPT-to-GitHub staging approach with a direct GitHub upload intake.
- Added `incoming/UPLOAD_HERE.txt` as the large-source intake location.
- Updated `.github/workflows/assemble-qidian.yml` to watch `incoming/*.json` on `main`.
- The workflow verifies the original Qidian file SHA256, assigns the permanent Legado identity URL, validates the final SHA256, and automatically updates the complete Beta source, Manifest, Beta Subscription, Beta Bundle, RSS detail metadata and Release Log.
- Failed integrity checks stop publication before an incomplete/corrupt source can enter the Beta channel.

## 2026-08-25 — RSS repository UI Beta 4

Status: Beta/Test; icon fix awaiting user real-device confirmation.

Changes:

- User confirmed Beta 3 no longer reports the Home / Bundle / Help category loading errors.
- Kept the Beta 3 HTTPS-only data-driven navigation as the new RSS UI baseline.
- Beta 3 remote `sourceIcon` still rendered as Legado's default RSS icon on the user's device.
- Beta 4 changes only the subscription icon strategy: the project icon is embedded directly as compact Base64 JPEG data.
- Updated the stable Beta identity path `rss/reader-source-repository-beta.json` to the Beta 4 definition.
- Added versioned snapshot `rss/reader-source-repository-beta4.json`.

Pending real-device verification:

- repository icon display,
- detail-page opening,
- RSS update action,
- bundle import action.

## 2026-08-25 — RSS repository UI Beta 3

Status: Beta/Test; category compatibility confirmed by user on real device.

Changes:

- Investigated Beta 2 after the user reported that Home / Bundle / Help still failed while Stable/Beta loaded.
- Confirmed the HTTPS payload files themselves were valid.
- Identified the Beta 2 helper-context bug: nested `q() -> repo()` calls lost the expected `this.source` binding.
- Rebuilt Home / Bundle / Help as data-driven HTTPS lists with explicit `detailUrl` fields.
- Added independent HTTPS detail JSON files under `rss/data/details/`.
- Simplified the RSS list parser so all categories share one generic path.
- Removed dynamic helper chaining from category navigation.
- Kept the same internal Beta RSS `sourceUrl` identity so Beta 3 updates the existing Beta subscription.

Real-device result:

- User confirmed the previous category loading errors are gone.
- Remote repository icon still did not display, leading to the Beta 4 Base64 icon fix.

## 2026-08-25 — RSS repository UI Beta 2

Status: Beta/Test; superseded by Beta 3 after real-device failure.

Changes:

- Replaced Beta 1 `data:` category URLs with HTTPS payloads.
- Added repository icon asset.
- Added stable Legado source identity policy.

Real-device result:

- Stable/Beta categories loaded.
- Home / Bundle / Help still failed due to the helper-context bug later fixed in Beta 3.

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
  - no required remote-JS runtime dependency for the repository RSS source.

## 2026-08-25 — Repository foundation

Status: infrastructure / no book-source Stable release yet.

Completed:

- Created and connected `source-core-8d7` as the dedicated 阅读 / Legado repository.
- Established hard isolation from the 海阔视界 repository `asset-core-7f3`.
- Added repository-level Manifest skeleton.
- Added Stable and Beta subscription-channel skeletons.
- Added Stable and Beta batch Bundle skeletons.
- Added `🌈 阅读书源仓库` RSS source.
- Corrected the RSS import workflow.
- User confirmed the RSS source imports successfully in the real Legado app.
- Created a neutral `landing` branch and later made it the default branch.
- Added long-term project documents.

## Release policy

Future entries should clearly distinguish:

- generated / static-check passed,
- Beta/Test published,
- user real-device confirmed,
- Stable published.

A generated or statically validated version must not be logged as Stable unless the user has confirmed it or explicitly requested the stable update.
