import json, hashlib, pathlib, re

ROOT = pathlib.Path('.')
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
OUT = ROOT / 'staging/qidian-beta4-audit.json'

raw = BETA.read_bytes()
data = json.loads(raw.decode('utf-8'))
src = data[0] if isinstance(data, list) else data
rule = src.get('ruleBookInfo') or {}
init = rule.get('init') or ''
whole = raw.decode('utf-8')

# Context snippets are deliberately short and only around public source markers.
def contexts(text, needle, radius=180, limit=6):
    out=[]; start=0
    while len(out)<limit:
        i=text.find(needle,start)
        if i<0: break
        a=max(0,i-radius); b=min(len(text),i+len(needle)+radius)
        out.append(text[a:b].replace('\n',' '))
        start=i+len(needle)
    return out

def count_ci(text, needle):
    return text.lower().count(needle.lower())

# Heuristic scan of the detail first-paint path only.
forbidden_detail_markers = {
    'qfOfficialCallV400': count_ci(init,'qfOfficialCallV400'),
    'bookDetailInfo': count_ci(init,'bookDetailInfo'),
    'atom': count_ci(init,'atom'),
    'qidiantu': count_ci(init,'qidiantu'),
    'tushujun': count_ci(init,'tushujun'),
}

# Tag/honor leakage markers that must never be rendered as metadata.
leak_literals = [':true', ':false', ':50001', ':50005', 'sectionCount', 'actionStatus', 'honorTypeName']

stable_sha = hashlib.sha256(STABLE.read_bytes()).hexdigest()
beta_sha = hashlib.sha256(raw).hexdigest()

report = {
    'beta_sha256': beta_sha,
    'stable_sha256': stable_sha,
    'expected_stable_sha256': 'd64937b9dc4e528795d3818834a6ddab1828df1af84bb483b16961a40d8286ec',
    'stable_unchanged': stable_sha == 'd64937b9dc4e528795d3818834a6ddab1828df1af84bb483b16961a40d8286ec',
    'display_name': src.get('bookSourceName'),
    'comment_has_beta4': '1.1.0-beta4' in str(src.get('bookSourceComment','')),
    'book_source_url': src.get('bookSourceUrl'),
    'detail_init_chars': len(init),
    'detail_init_ajax_count': init.count('.ajax(') + init.count('java.ajax('),
    'detail_official_pc_url_count': count_ci(init, 'www.qidian.com/book/'),
    'detail_qdParseBookInfo_count': count_ci(init, 'qdParseBookInfo'),
    'detail_2600_count': init.count('2600'),
    'detail_30min_literals': {
        '1800000': init.count('1800000'),
        '30*60*1000': init.count('30*60*1000'),
        '30 * 60 * 1000': init.count('30 * 60 * 1000'),
    },
    'detail_forbidden_markers': forbidden_detail_markers,
    'whole_qw_regression_markers': {
        'X-Content-Token': count_ci(whole, 'X-Content-Token'),
        'VIP正文已验证': count_ci(whole, 'VIP正文已验证'),
    },
    'whole_structured_leak_literal_counts': {x: count_ci(whole, x) for x in leak_literals},
    'contexts': {
        'official_pc': contexts(init, 'www.qidian.com/book/'),
        '2600': contexts(init, '2600'),
        '1800000': contexts(init, '1800000'),
        'qdParseBookInfo': contexts(init, 'qdParseBookInfo'),
        'tag': contexts(init, 'tag'),
        'honor': contexts(init, 'honor'),
    },
}

# A few conservative gates; contexts remain available for human review.
report['gates'] = {
    'json_ok': True,
    'stable_unchanged': report['stable_unchanged'],
    'identity_ok': src.get('bookSourceUrl') == 'https://m.qidian.com/?qf_source=qidian_next_8d7',
    'qw_markers_ok': report['whole_qw_regression_markers']['X-Content-Token'] > 0 and report['whole_qw_regression_markers']['VIP正文已验证'] > 0,
    'no_old_multi_endpoint_markers_in_detail_init': all(v == 0 for v in forbidden_detail_markers.values()),
    'no_ajax_in_detail_init': report['detail_init_ajax_count'] == 0,
}

OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report['gates'], ensure_ascii=False))
