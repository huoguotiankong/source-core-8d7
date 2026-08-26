from pathlib import Path

rp=Path('docs/RELEASE_LOG.md')
r=rp.read_text(encoding='utf-8')
block='''## 2026-08-26 — RSS repository UI 0.3.1-beta11\n\nStatus: Beta/Test; repository cleanup and detail-rendering repair awaiting real-device confirmation.\n\nChanges:\n\n- Renamed top categories and bumped category URLs to `ui=11` to force a clean Legado category cache after old/new list entries were observed together.\n- Simplified the Beta home page to repository overview, Stable/Beta policy and repository self-update only.\n- Added list-level de-duplication by source id / sourceUrl / detailUrl / name.\n- Restored styled detail pages by explicitly opening generated HTML with `java.startBrowser(data:text/html;base64, ...)`.\n- Added a non-empty `ruleDescription` override so stale description rules from older imported RSS definitions cannot keep taking precedence.\n- Stable/Beta source files and channel metadata were not modified by this UI release.\n\n'''
if '## 2026-08-26 — RSS repository UI 0.3.1-beta11' not in r:
    if r.startswith('# RELEASE LOG\n'):
        r='# RELEASE LOG\n\n'+block+r[len('# RELEASE LOG\n\n'):]
    else:
        r=block+r
    rp.write_text(r,encoding='utf-8')

kp=Path('docs/KNOWN_ISSUES.md')
k=kp.read_text(encoding='utf-8')
issue='''## 18. RSS old/new list entries mixed and detail page regressed to plain text — fixed in Beta11\n\nReal-device symptoms after Beta10:\n\n- the Home category displayed the new Beta10 cards followed by older Beta3-era cards;\n- the Stable category displayed the same current source more than once even though `subscription/stable.json` contained only one item;\n- opening a source detail showed only a plain summary instead of the styled detail/import page.\n\nInterpretation: Legado retained category/article state across RSS definition updates, and Beta10 had also regressed from the earlier `java.startBrowser(data:text/html;base64, ...)` detail-opening pattern back to returning HTML directly from `ruleContent`.\n\nBeta11 mitigation:\n\n- rename categories and use `ui=11` URLs to create a fresh cache key;\n- de-duplicate list items in `ruleArticles`;\n- explicitly override `ruleDescription` to prevent stale older rules from winning after an in-place RSS update;\n- explicitly open the generated card page through `java.startBrowser`;\n- keep source detail pages current-state only.\n\nStatus: published as RSS UI `0.3.1-beta11`, awaiting real-device confirmation.\n'''
if '## 18. RSS old/new list entries mixed and detail page regressed to plain text' not in k:
    kp.write_text(k.rstrip()+'\n\n'+issue+'\n',encoding='utf-8')
