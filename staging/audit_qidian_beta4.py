import json, hashlib, pathlib

ROOT = pathlib.Path('.')
BETA = ROOT / 'sources/novel/qidian-next/qidian-next-beta.json'
STABLE = ROOT / 'sources/novel/qidian-next/qidian-next.json'
OUT = ROOT / 'staging/qidian-beta5-audit.json'

raw = BETA.read_bytes()
data = json.loads(raw.decode('utf-8'))
src = data[0] if isinstance(data, list) else data
init = (src.get('ruleBookInfo') or {}).get('init') or ''
whole = raw.decode('utf-8')


def count_ci(text, needle):
    return text.lower().count(needle.lower())


def context(text, needle, before=300, after=2200):
    i = text.find(needle)
    if i < 0:
        return ''
    return text[max(0, i-before):min(len(text), i+len(needle)+after)].replace('\n', ' ')

stable_sha = hashlib.sha256(STABLE.read_bytes()).hexdigest()
beta_sha = hashlib.sha256(raw).hexdigest()
comment = str(src.get('bookSourceComment', ''))

# Beta5 should use a local mutually-exclusive transport for the optional PC enrichment.
network_shape = {
    'detail_func_present': 'qfDetailPcEnrichV1105' in init,
    'generic_qfAjaxTextV20_calls': init.count('qfAjaxTextV20'),
    'get_branch_count': init.count("typeof dj.get==='function'") + init.count('typeof dj.get==="function"'),
    'ajax_branch_count': init.count("typeof dj.ajax==='function'") + init.count('typeof dj.ajax==="function"'),
    'mutually_exclusive_else_if': ("else if(dj&&typeof dj.ajax==='function')" in init or 'else if(dj&&typeof dj.ajax==="function")' in init),
    'timeout_2600_count': init.count('2600'),
    'throttle_1800000_count': init.count('1800000'),
    'official_pc_code_count': init.count("var pcUrl='https://www.qidian.com/book/'") + init.count('var pcUrl="https://www.qidian.com/book/"'),
    'old_app_bookDetailInfo_count': count_ci(init, 'bookDetailInfo'),
    'old_qfOfficialCallV400_count': count_ci(init, 'qfOfficialCallV400'),
    'old_qidiantu_count': count_ci(init, 'qidiantu'),
    'old_tushujun_count': count_ci(init, 'tushujun'),
}

# Strict metadata path: no generic listScalar should be used to populate tags/honors after beta4.
metadata_shape = {
    'human_meta_present': 'qfHumanMetaV1104' in init,
    'visible_tags_present': 'qfVisibleTagsV1104' in init,
    'listScalar_to_tags_literal': 'info.tags=listScalar' in init.replace(' ', ''),
    'listScalar_to_honors_literal': 'info.honors=listScalar' in init.replace(' ', ''),
    'bad_key_map_present': all(x in init.lower() for x in ['sectioncount','actionstatus','honortypename','true','false']),
    'visible_tag_dom_selector_present': '.book-info .tag a' in init,
    'structured_fragment_examples_in_comment_or_filter': {
        ':true': count_ci(init, ':true'),
        ':50001': count_ci(init, ':50001'),
    },
}

qw = {
    'X-Content-Token': count_ci(whole, 'X-Content-Token'),
    'VIP正文已验证': count_ci(whole, 'VIP正文已验证'),
}

report = {
    'version': '1.1.0-beta5' if '1.1.0-beta5' in comment else 'unknown',
    'beta_sha256': beta_sha,
    'stable_sha256': stable_sha,
    'expected_stable_sha256': 'd64937b9dc4e528795d3818834a6ddab1828df1af84bb483b16961a40d8286ec',
    'stable_unchanged': stable_sha == 'd64937b9dc4e528795d3818834a6ddab1828df1af84bb483b16961a40d8286ec',
    'book_source_url': src.get('bookSourceUrl'),
    'detail_init_chars': len(init),
    'network_shape': network_shape,
    'metadata_shape': metadata_shape,
    'qw_regression_markers': qw,
    'contexts': {
        'detail_enrich': context(init, 'function qfDetailPcEnrichV1105'),
        'human_meta': context(init, 'function qfHumanMetaV1104'),
        'visible_tags': context(init, 'function qfVisibleTagsV1104'),
    }
}

report['gates'] = {
    'json_ok': True,
    'version_ok': report['version'] == '1.1.0-beta5',
    'stable_unchanged': report['stable_unchanged'],
    'identity_ok': src.get('bookSourceUrl') == 'https://m.qidian.com/?qf_source=qidian_next_8d7',
    'qw_markers_ok': qw['X-Content-Token'] > 0 and qw['VIP正文已验证'] > 0,
    'detail_local_single_transport_shape_ok': (
        network_shape['detail_func_present'] and
        network_shape['generic_qfAjaxTextV20_calls'] == 0 and
        network_shape['get_branch_count'] >= 1 and
        network_shape['ajax_branch_count'] >= 1 and
        network_shape['mutually_exclusive_else_if'] and
        network_shape['timeout_2600_count'] >= 1 and
        network_shape['throttle_1800000_count'] >= 1 and
        network_shape['official_pc_code_count'] == 1 and
        network_shape['old_app_bookDetailInfo_count'] == 0 and
        network_shape['old_qfOfficialCallV400_count'] == 0 and
        network_shape['old_qidiantu_count'] == 0 and
        network_shape['old_tushujun_count'] == 0
    ),
    'metadata_strict_path_ok': (
        metadata_shape['human_meta_present'] and
        metadata_shape['visible_tags_present'] and
        not metadata_shape['listScalar_to_tags_literal'] and
        not metadata_shape['listScalar_to_honors_literal'] and
        metadata_shape['bad_key_map_present'] and
        metadata_shape['visible_tag_dom_selector_present']
    ),
}

OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report['gates'], ensure_ascii=False))
