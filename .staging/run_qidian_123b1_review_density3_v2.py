from pathlib import Path

p = Path('.staging/patch_qidian_123b1_review_density3.py')
src = p.read_text(encoding='utf-8')
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
