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

- `main`: actual development / documentation / distribution branch.
- `landing`: neutral low-discoverability landing branch. It contains only a generic entry file.

The existing RSS subscription and raw URLs continue to use `main`; changing the default branch must not change those raw URLs.

Target state: set `landing` as the GitHub default branch while keeping `main` as the real project branch.

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
- `rss/reader-source-repository.json`: Legado RSS source used as the repository UI/entry.
- `sources/`: independent complete book-source JSON files as they are migrated in.

Stable and Beta are separate channels. A source must not enter Stable until the user has confirmed it in the real Legado app or explicitly requests a stable release.

## 6. Current status

Completed:

- Repository `source-core-8d7` created and connected.
- Manifest / Stable / Beta / Bundle skeleton created.
- `🌈 阅读书源仓库` RSS source created.
- User confirmed the RSS source can be imported into Legado.
- `landing` branch created and cleaned to a neutral entry only.
- Long-term project documents initialized.

Not yet completed:

- GitHub default branch has not yet been switched to `landing`.
- No real book source has completed the full repository loop yet.
- Stable/Beta lists and bundles are currently framework-level and will be populated as sources are migrated.

## 7. Next roadmap

### Phase A — repository foundation

1. Switch GitHub default branch to `landing`.
2. Keep all actual files and raw subscription URLs on `main`.
3. Verify the existing imported RSS source still loads after the default-branch switch.

### Phase B — first end-to-end source

Select one already verified source and complete:

`source JSON -> Beta/Stable entry -> Manifest -> Bundle -> RSS listing -> one-click import -> user real-device test`

Do not bulk-migrate many sources before this loop is proven.

### Phase C — migration

Migrate verified sources one by one. Preserve independent complete JSON files. Do not use Bundle as the only copy of a source.

### Phase D — maintenance

Every release updates the relevant source file plus Manifest / Subscription / Bundle / Release Log.

## 8. Qidian project note

The Qidian ecosystem source is a large independent engineering project. Historical v4.1 handoff material exists, but it must not automatically be treated as the latest current state because development continued after that report.

Before the next major Qidian task, rebuild or refresh `docs/sources/qidian/PROJECT_HANDOFF.md` from the latest user-confirmed stable source and the latest real-device test state. Do not overwrite newer decisions with the older v4.1 report.
