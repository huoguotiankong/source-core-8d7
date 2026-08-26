# DEVELOPMENT RULES

> Updated: 2026-08-26

## 1. Repository isolation

Before any GitHub write, confirm the target project.

- 阅读 / Legado tasks -> `source-core-8d7`
- 海阔视界 tasks -> `asset-core-7f3`

Never write to the other repository by default.

## 2. Baseline rule

Use the newest user-provided file or the newest user-confirmed stable repository file as the baseline.

Do not replace a stable baseline with an older attachment, old chat solution, or historical handoff unless the user explicitly asks for rollback or comparison.

## 3. Delivery format

For book-source development, the final deliverable must normally be a complete JSON file that can be imported directly into Legado.

Do not end with only:

- snippets,
- patches,
- manual replacement instructions,
- a modifier script that requires the user to edit the source themselves.

Large sources may be modular internally, but final delivery remains a complete importable source.

## 4. Module isolation

Protect stable behavior. A change in one domain should not silently alter unrelated domains.

Typical boundaries:

- Official data
- Catalog
- Content Provider Runtime
- Reviews / comments
- Community
- Role / copyright / easter eggs
- UI / settings
- Diagnostics

Load only the modules required for the current path where practical. Avoid initializing every Provider and every optional subsystem on every request.

## 5. Iteration discipline

Prefer one clear development domain per version.

When a bug survives multiple versions, stop adding blind fallbacks. Improve observability first:

- record the actual request path,
- capture real response structure,
- distinguish network / auth / signature / parse / match / cache / UI failures,
- verify whether old code is still intercepting the path.

Do not return to the pattern of creating endless `Vxxx` implementations while keeping all older implementations alive.

Compatibility layers may exist temporarily, but should act as proxies and have a removal plan.

## 6. Diagnostics

Critical failures must not be silently swallowed by broad `catch(e){}` blocks.

User-facing errors should be simple; developer diagnostics should preserve enough technical detail to locate the fault.

Diagnostics must not create unnecessary normal-reading overhead when disabled.

## 7. Performance

Do not call a change "faster" based only on subjective feeling.

Check relevant metrics such as:

- search latency,
- catalog latency,
- first-chapter latency,
- page-turn latency,
- comment opening latency,
- network request count,
- cache hits,
- whether unused Providers are loaded,
- whether disabled features still issue requests.

Important invariant examples:

- comments disabled -> no comment network requests,
- local-comment mode -> no unnecessary server-comment requests,
- Provider A selected -> Providers B/C/D should not initialize without need.

## 8. Regression protection

Static checks are necessary but cannot prove real Legado behavior.

Before delivery, perform what is feasible:

- JSON parse,
- JavaScript syntax / module smoke checks,
- non-target field diff review,
- obvious URL / JSON-structure verification.

For large Qidian changes, expand regression coverage according to the touched domains: search, details, catalog, free/VIP content, comments, replies, chapter comments, author say, copyright, roles, community and Provider switching.

The user's real-device result is the final authority on whether a version is confirmed working.

## 9. Release channels

New or modified versions that have not been real-device confirmed go to Beta/Test by default.

Move to Stable only when:

- the user confirms the version works, or
- the user explicitly asks to update the stable release.

Publishing a source requires synchronized maintenance of the relevant:

- source JSON,
- Manifest,
- Subscription channel,
- Bundle,
- Release Log.

## 10. Stable identity URL for book sources

Legado distinguishes book sources by the source identity URL (`bookSourceUrl`).

For every book source published by this project:

1. Stable and Beta/Test versions of the same source MUST use the same `bookSourceUrl`.
2. The identity URL MUST NOT contain a version number or release-channel name.
3. Different sources MUST use different identity URLs.
4. Do not use the original website homepage as the identity URL by default. Use the project namespace format instead:

   `https://sc8d7.invalid/legado/<source-id>-8d7`

   Example:

   `https://sc8d7.invalid/legado/qidian-official-8d7`

5. `sc8d7.invalid` is only a stable identity namespace. Actual network requests must use explicit real endpoints in search/discovery/rule JS/runtime configuration.
6. When migrating a legacy source that relies on `bookSourceUrl` for same-origin cookies, WebView login, relative URL resolution or runtime base behavior, do not replace it with the `.invalid` namespace. Preserve a same-origin identity and make it unique with a stable query/path marker.
7. Existing mature sources should preserve their already-working identity URL when that also preserves upgrade continuity in Legado. For Qidian official ecosystem, the permanent Stable/Beta identity is `https://m.qidian.com/?qf_source=v2922_audio_webview_crypto_bridge_fix`.
8. Once an identity URL has been published and real-device confirmed, keep it stable across future versions unless a collision or serious migration issue requires a deliberate compatibility plan.

The same principle applies to RSS sources via their `sourceUrl`: a released subscription source keeps a stable identity URL even if the downloadable JSON file path or version changes.

## 11. Repository architecture

`main` is the actual project branch. `landing` is only a neutral default landing branch for low discoverability.

Do not casually change existing raw distribution URLs after users have imported them. If a path must move, provide a compatibility period or explicit migration path.

## 12. Public repository policy

The repository may remain public. The goal is low casual discoverability, not secrecy.

Do not publish private credentials, tokens, cookies, passwords or user-specific sensitive data.

Low-discoverability measures must never break normal Raw access, subscription updates or imported sources.

## 13. Subscription source-detail maintenance

RSS/source detail pages are current-state introductions, not release-history documents.

- Do not append one new detail section for every Beta/Stable version.
- Keep long-lived sections such as positioning, core capabilities, setup architecture, current version/status and import identity.
- On release, replace the current-version/change summary instead of accumulating historical version cards.
- Full chronological history belongs in `docs/RELEASE_LOG.md`.

This prevents source detail pages from growing without bound after dozens or hundreds of releases.
## 14. Stable/Beta physical distribution separation

For a source that has entered Stable, Stable and Beta may share the same Legado `bookSourceUrl` identity, but MUST NOT share the same downloadable JSON path or RSS detail path.

For `qidian-next` / `🌈 起点增强`:

- Stable source: `sources/novel/qidian-next/qidian-next.json`
- Future Beta source: `sources/novel/qidian-next/qidian-next-beta.json`
- Stable detail: `rss/data/details/stable/qidian-next.json`
- Future Beta detail: `rss/data/details/beta/qidian-next.json`

A Beta catalog entry must point only to the Beta source/detail paths. A Stable catalog entry must point only to the Stable paths. Never let an old Beta detail URL start importing the current Stable file after promotion.

When repository channel/detail payloads change in a way that may be cached by Legado/Raw, bump the query revision in the RSS definition (`?v=N`) or move to a new channel-specific detail path.
## 15. RSS article identity stability

Legado persists RSS articles. Changing an item's detail URL or category identity on every UI release can create a new stored article instead of replacing the old one.

Repository UI rule from Beta13 onward:

- top-level category names are stable release-independent identities;
- category request URLs remain stable and do not carry `?ui=N` release revisions;
- item `detailUrl` values remain stable and do not carry UI-version query parameters;
- mutable UI/source version numbers belong inside detail payload content, not in article identity fields;
- list title/link identity must remain stable across releases;
- do not solve cache problems by continuously minting new article URLs.

If a future incompatible RSS migration truly requires a new identity, do it deliberately once with a documented migration plan rather than once per release.


## 16. Default direct repository publication

Unless the user explicitly requests local-only delivery, every newly created or modified 阅读 / Legado source is published to `source-core-8d7` in the same task.

- Unconfirmed versions go directly to Beta/Test; do not wait for a separate “publish” instruction.
- Real-device-confirmed versions may be promoted to Stable only under the existing Stable rules.
- Keep status catalogs (Stable/Beta) and type catalogs in parallel. Current long-lived type catalogs include `subscription/comic.json` and `subscription/rss.json`.
- A local downloadable JSON may still be delivered for convenience, but it does not replace repository publication.
- Publication must upsert existing catalogs and rebuild the relevant bundle without dropping unrelated sources.

## 17. Concise source display naming

`bookSourceName` / RSS source display names should be short and recognizable. New source-core sources use the shared project brand mark by default:

`◈ <source/platform name>`

Example: `◈ 哔咔漫画`. The matching repository artwork is `assets/source-core-source-icon.svg`.

- Do not append Beta/Stable, version numbers, APP/Web route descriptions, long capability lists or marketing-style suffixes to the in-app source name.
- Put channel, version, route architecture and feature descriptions in `bookSourceComment`, Manifest/Subscription metadata, tags and changelog instead.
- Add a textual suffix only when two independently installable sources would otherwise be genuinely ambiguous, and keep that suffix short.
- When renaming an existing source, preserve its stable `bookSourceUrl` identity so updates continue in place.
- Do not pick a different decorative emoji for each newly written source. Use the shared `◈` source-core mark unless the user explicitly requests another public identity.
- Existing mature sources are not bulk-renamed only for branding; adopt the shared mark when they are deliberately renamed or newly rebuilt, so stable user-facing names are not churned unnecessarily.

## 18. Single active RSS repository entry and logical-source de-duplication

The repository itself is one logical RSS source. Do not publish separate Stable/Beta repository RSS entries as simultaneously active choices when they expose the same repository.

- `subscription/rss.json` lists exactly one current repository entry.
- Preserve the current released RSS `sourceUrl` identity for in-place updates; UI status/version belongs in metadata, not in extra duplicate RSS sources.
- Type catalogs such as `subscription/comic.json` list only the latest active channel entry for a logical source. A source promoted to Stable is removed from the active Beta/type duplicate listing.
- Historical JSON/detail files may remain for compatibility/history, but they are not active catalog entries.
- RSS item `detailUrl` is a long-lived article identity and must not receive routine version query parameters.
- When persisted old RSS articles make clean replacement impossible, one deliberate category identity reset is allowed. After that migration, freeze the new category names/URLs; do not repeat the reset per release.

## 19. RSS stale-article cleanup invariant

Legado persists RSS articles and only calls `rssArticleDao.clearOld(origin, sort, order)` after a refresh when the RSS source's `ruleNextPage` field is non-blank.

For repository-style RSS sources whose remote JSON represents the complete current list:

- keep `ruleNextPage` non-blank even when there is no real pagination; use an empty-result rule such as `@js:''`;
- this enables Legado to delete older rows after inserting the current result while still producing no second-page URL;
- do not use category-name churn, `?ui=N`, `?reset=N`, or versioned detail URLs as a routine cache-clearing mechanism;
- category URLs and article detail URLs remain long-lived identities.
