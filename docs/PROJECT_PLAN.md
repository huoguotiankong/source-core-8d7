# PROJECT PLAN

> Updated: 2026-08-25

## 1. Project scope

This repository is the only default GitHub repository for the 阅读 / Legado source project.

- 阅读 / Legado: `source-core-8d7`
- 海阔视界: `asset-core-7f3`

The two repositories are hard-isolated. Cross-project writes are allowed only when the user explicitly requests migration, copy, or synchronization.

## 2. Repository role

GitHub is used for publishing, versioning, subscription distribution, manifests and bundles.

Imported book sources remain complete local Legado JSON sources. Normal reading should not depend on downloading and evaluating remote GitHub code at runtime unless a specific source explicitly requires that architecture.

## 3. Branch model

- `landing`: GitHub default branch. Neutral low-discoverability landing branch containing only a generic entry file.
- `main`: actual development / documentation / distribution branch.

All RSS subscription and Raw distribution URLs continue to use `main`. Changing the default branch does not change those URLs.

The user confirmed on 2026-08-25 that the repository default branch has been switched to `landing`.

## 4. Core repository documents

Every new conversation or major development task should read these first:

1. `docs/PROJECT_PLAN.md`
2. `docs/DEVELOPMENT_RULES.md`
3. `docs/KNOWN_ISSUES.md`
4. `docs/RELEASE_LOG.md`

If a source has its own handoff document, also read:

`docs/sources/<source>/PROJECT_HANDOFF.md`

## 5. Distribution architecture

Main objects:

- `manifest.json`: repository-level metadata index.
- `subscription/stable.json`: stable channel listing.
- `subscription/beta.json`: beta/test channel listing.
- `bundles/all-stable.json`: stable batch import bundle.
- `bundles/all-beta.json`: beta batch import bundle.
- `rss/reader-source-repository.json`: current stable Legado RSS repository entry.
- `rss/reader-source-repository-beta.json`: stable identity URL of the repository UI Beta source.
- `rss/reader-source-repository-beta2.json`: current Beta 2 import file.
- `rss/data/`: HTTPS-backed static payloads used by repository UI categories/details.
- `assets/reader-repo-icon.jpg`: repository subscription icon.
- `sources/`: independent complete book-source JSON files as they are migrated in.

Stable and Beta are separate channels. A source must not enter Stable until the user has confirmed it in the real Legado app or explicitly requests a stable release.

## 6. Stable identity model

Legado book sources are treated as the same source when they share the same stable `bookSourceUrl` identity.

Project policy:

- Same source Stable/Beta -> exactly the same `bookSourceUrl`.
- Version and channel are never encoded into that identity.
- Do not use the original website homepage as the default identity URL.
- Project namespace: `https://sc8d7.invalid/legado/<source-id>-8d7`.
- Actual network hosts stay in runtime/search/discovery/content rules, not in the identity namespace.
- Legacy sources that rely on `bookSourceUrl` as a relative URL base must migrate that runtime dependency before adopting the project identity URL.

This ensures Stable/Beta imports update the same Legado source instead of creating duplicate sources.

## 7. RSS repository UI direction

The repository UI should combine native Legado browsing with lightweight HTML detail pages:

- Native top categories and native article list for speed and familiar interaction.
- HTML detail page for source metadata, status, version, tags, changelog and import buttons.
- Stable / Beta are clearly separated.
- Type browsing is maintained in parallel: novel sources use `subscription/novel.json`, comic sources use `subscription/comic.json`, and subscription/RSS sources use `subscription/rss.json`.
- Current top-level order is：首页 → 小说 → 漫画 → 正式版 → 测试版 → 订阅 → 批量 → 帮助。
- Batch import is a separate category.
- GitHub Raw is primary distribution; jsDelivr can be used as a manual fallback line.
- Avoid turning the whole RSS repository into a heavy remote webpage.
- Avoid remote JS as a required runtime dependency for the RSS source itself.
- RSS navigation/detail request URLs must be HTTP/HTTPS. Do not use `data:` in AnalyzeUrl-driven category/detail paths.

Reference-source lessons:

- Borrow detail-page/import-button/update-log ideas from mature repository-style RSS sources.
- Borrow simple classification and route-fallback ideas from lightweight feed sources.
- Do not copy activation/remote-code architectures that reduce independence or maintainability.

## 8. Current status

Completed:

- Repository `source-core-8d7` created and connected.
- Manifest / Stable / Beta / Bundle skeleton created.
- `🌈 阅读书源仓库` RSS source created.
- User confirmed the stable RSS source can be imported into Legado.
- `landing` branch created, cleaned to a neutral entry only, and set as the GitHub default branch by the user.
- Long-term project documents initialized.
- RSS UI Beta 1 real-device test exposed the `data:` URL navigation incompatibility.
- RSS UI Beta 2 prepared with HTTPS-only category/detail navigation and a dedicated repository icon.
- Stable `bookSourceUrl` identity convention defined for future book-source publication.

In progress:

- RSS UI Beta 2 real-device verification.

Not yet completed:

- No real book source has completed the full repository loop yet.
- Stable/Beta lists and bundles are currently framework-level and will be populated as sources are migrated.

## 9. Next roadmap

### Phase A — RSS repository UI

1. Import/test RSS UI Beta 2.
2. Verify home, Stable, Beta, Bundle and Help categories.
3. Verify detail pages, light/dark themes, repository icon, route switching and one-click import behavior.
4. After user confirmation, promote the UI to the stable RSS path while preserving stable RSS source identity.

### Phase B — first end-to-end source

Select one already verified source and complete:

`source JSON -> permanent source ID/bookSourceUrl -> Beta/Stable entry -> Manifest -> Bundle -> RSS listing -> one-click import -> user real-device test`

Do not bulk-migrate many sources before this loop is proven.

### Phase C — migration

Migrate verified sources one by one. Preserve independent complete JSON files. Do not use Bundle as the only copy of a source.

### Phase D — maintenance

Every release updates the relevant source file plus Manifest / Subscription / Bundle / Release Log.

## 10. Qidian project note

The Qidian ecosystem source is a large independent engineering project. Historical v4.1 handoff material exists, but it must not automatically be treated as the latest current state because development continued after that report.

Before the next major Qidian task, rebuild or refresh `docs/sources/qidian/PROJECT_HANDOFF.md` from the latest user-confirmed stable source and the latest real-device test state. Do not overwrite newer decisions with the older v4.1 report.

## 11. Qidian next-generation source line

A new independent source line `qidian-next` was started on 2026-08-25 at the user's request.

- First Beta: `0.1.0-beta1`.
- UI baseline: user-selected loginfix4 two-column static login page plus `java.startBrowserAwait` multi-level settings.
- Functional baseline: current v4.2.1-alpha2 Qidian official ecosystem business rules.
- Goal: continue future Qidian refactoring/optimization on the new line without destabilizing the old `qidian-official` source.
- Release policy: Beta until full user real-device confirmation.

## 12. Qidian Next Stable 1.0.0

On 2026-08-26 the user explicitly promoted the Beta6 baseline to the first Stable release. The public display name is `🌈 起点增强`; repository id and permanent Legado identity remain `qidian-next` / `https://m.qidian.com/?qf_source=qidian_next_8d7`. Future unconfirmed test versions must use a separate beta file path so the Stable raw URL never silently serves Beta code.

## 13. Single current repository RSS entry

From RSS UI Beta14 onward, the repository itself has one active subscription entry. Stable/Beta remain release channels for book sources, not duplicate active RSS repository definitions. The latest already-imported RSS identity is preserved for in-place updates, while legacy repository JSON files may remain only as compatibility artifacts and are not listed in the active RSS catalog.

## 14. RSS current-list replacement model

From UI Beta15 onward the repository RSS source uses Legado's own stale-row cleanup path: `ruleNextPage` stays non-blank but evaluates to an empty result. Current remote catalogs are therefore authoritative complete lists, and refreshing a category can remove older persisted rows instead of accumulating them. Category/detail URLs remain fixed.
