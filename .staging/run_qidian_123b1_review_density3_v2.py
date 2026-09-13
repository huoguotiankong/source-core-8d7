from pathlib import Path

p = Path('.staging/patch_qidian_123b1_review_density3.py')
src = p.read_text(encoding='utf-8')

# The current Stable 1.2.2 lazy pack contains legacy gz:-prefixed payloads that are
# intentionally carried through byte-for-byte but are not all standalone base64 blobs.
# This release only owns review_local_ui, so validate/decode the target module and use
# exact equality as the safety gate for every non-target module.
old_gate = """for k, v in newpack.items():
    if isinstance(v, str) and v.startswith('gz:'):
        dec(v)
"""
new_gate = """dec(newpack['review_local_ui'])
"""
if old_gate not in src:
    raise AssertionError('expected broad lazy-pack decode gate not found')
src = src.replace(old_gate, new_gate, 1)

# Stable 1.2.2 has multiple CSS variants for the same root-comment selectors.
# Apply the same declarations to every matching variant while leaving selectors and
# unrelated declarations intact. Nested replies use .rLike and remain untouched.
start = src.index('def patch_rule(src, selector, props, required=True):')
end = src.index('\n# 1) Root-comment like becomes metadata', start)
replacement = r'''def patch_rule(src, selector, props, required=True):
    pat = re.compile(re.escape(selector) + r'\{([^{}]*)\}')
    matches = list(pat.finditer(src))
    if not matches:
        if required:
            raise AssertionError('missing CSS selector: ' + selector)
        print('SKIP selector', selector)
        return src
    extra = ';'.join(k + ':' + v for k, v in props.items())
    def repl(m):
        body = m.group(1).rstrip(';')
        return selector + '{' + body + (';' if body else '') + extra + '}'
    print('PATCH selector', selector, 'count', len(matches))
    return pat.sub(repl, src)
'''
src = src[:start] + replacement + src[end:]
exec(compile(src, str(p) + ':v2', 'exec'), {'__name__': '__main__'})
