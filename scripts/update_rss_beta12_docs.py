from pathlib import Path

rp=Path('docs/RELEASE_LOG.md')
r=rp.read_text(encoding='utf-8')
block='''## 2026-08-26 — RSS repository UI 0.3.2-beta12\n\nStatus: Beta/Test; blank-detail-page fix awaiting real-device confirmation.\n\nChanges:\n\n- Removed the Beta11 `java.startBrowser(data:text/html...)` second-browser launch from `ruleContent`.\n- Styled detail HTML is now returned directly into the current RSS detail page, matching the mature RSS-source rendering pattern.\n- Kept Beta11 list de-duplication and Stable/Beta physical separation.\n- Bumped repository category/detail cache revision to `ui=12`.\n- Book-source Stable/Beta files and versions were not modified.\n\n'''
if '## 2026-08-26 — RSS repository UI 0.3.2-beta12' not in r:
    if r.startswith('# RELEASE LOG\n\n'):
        r='# RELEASE LOG\n\n'+block+r[len('# RELEASE LOG\n\n'):]
    else:
        r=block+r
    rp.write_text(r,encoding='utf-8')

kp=Path('docs/KNOWN_ISSUES.md')
k=kp.read_text(encoding='utf-8')
issue='''## 19. RSS Beta11 leaves an empty detail page behind — fixed in Beta12\n\nReal-device symptom: opening a repository item launched the styled card page, but after returning an additional blank RSS detail page remained in the navigation stack.\n\nCause: Beta11 opened a second browser from inside `ruleContent` with `java.startBrowser(...)` and then returned a blank string to the already-open RSS detail page.\n\nFix: return the styled HTML directly from `ruleContent` and let the current RSS detail WebView render it; do not launch a second browser. `ruleDescription` remains overridden so old summary rules do not take over. Cache revision bumped to `ui=12`.\n\nStatus: published as RSS UI `0.3.2-beta12`, awaiting real-device confirmation.\n'''
if '## 19. RSS Beta11 leaves an empty detail page behind' not in k:
    kp.write_text(k.rstrip()+'\n\n'+issue+'\n',encoding='utf-8')
