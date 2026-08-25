# DEVELOPMENT RULES

> Updated: 2026-08-25

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
