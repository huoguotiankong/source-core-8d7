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
- `rss/reader-source-repository-beta.json`: UI/interaction test channel for the repository RSS source.
- `sources/`: independent complete book-source JSON files as they are migrated in.

Stable and Beta are separate channels. A source must not enter Stable until the user has confirmed it in the real Legado app or explicitly requests a stable release.

## 6. RSS repository UI direction

The repository UI should combine native Legado browsing with lightweight HTML detail pages:

- Native top categories and native article list for speed and familiar interaction.
- HTML detail page for source metadata, status, version, tags, changelog and import buttons.
- Stable / Beta are clearly separated.
- Batch import is a separate category.
- GitHub Raw is primary distribution; jsDelivr can be used as a manual fallback line.
- Avoid turning the whole RSS repository into a heavy remote webpage.
- Avoid remote JS as a required runtime dependency for the RSS source itself.

Reference-source lessons:

- Borrow detail-page/import-button/update-log ideas from mature repository-style RSS sources.
- Borrow simple classification and route-fallback ideas from lightweight feed sources.
- Do not copy activation/remote-code architectures that reduce independence or maintainability.

## 7. Current status

Completed:

- Repository `source-core-8d7` created and connected.
- Manifest / Stable / Beta / Bundle skeleton created.
- `🌈 阅读书源仓库` RSS source created.
- User confirmed the RSS source can be imported into Legado.
- `landing` branch created, cleaned to a neutral entry only, and set as the GitHub default branch by the user.
- Long-term project documents initialized.

In progress:

- Repository RSS UI Beta: native list + styled detail page + dual channel + batch import + fallback line.

Not yet completed:

- No real book source has completed the full repository loop yet.
- Stable/Beta lists and bundles are currently framework-level and will be populated as sources are migrated.

## 8. Next roadmap

### Phase A — RSS repository UI

1. Publish a separate RSS UI Beta without replacing the confirmed current RSS source.
2. Test category switching, empty-state display, detail pages, light/dark themes, route switching and one-click import behavior on a real device.
3. After user confirmation, promote the UI to the stable RSS path while preserving the existing stable source identity/URL where practical.

### Phase B — first end-to-end source

Select one already verified source and complete:

`source JSON -> Beta/Stable entry -> Manifest -> Bundle -> RSS listing -> one-click import -> user real-device test`

Do not bulk-migrate many sources before this loop is proven.

### Phase C — migration

Migrate verified sources one by one. Preserve independent complete JSON files. Do not use Bundle as the only copy of a source.

### Phase D — maintenance

Every release updates the relevant source file plus Manifest / Subscription / Bundle / Release Log.

## 9. Qidian project note

The Qidian ecosystem source is a large independent engineering project. Historical v4.1 handoff material exists, but it must not automatically be treated as the latest current state because development continued after that report.

Before the next major Qidian task, rebuild or refresh `docs/sources/qidian/PROJECT_HANDOFF.md` from the latest user-confirmed stable source and the latest real-device test state. Do not overwrite newer decisions with the older v4.1 report.
