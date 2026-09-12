import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta

SRC_BETA = Path('sources/novel/qidian-next/qidian-next-beta.json')
SRC_STABLE = Path('sources/novel/qidian-next/qidian-next.json')
VERSION = '1.2.1'
VERSION_CODE = 12010
BETA_VERSION = '1.2.1-beta7'


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def first_source(obj):
    return obj[0] if isinstance(obj, list) else obj


def set_source_meta(src):
    src['bookSourceName'] = '🌈 起点增强'
    comment = str(src.get('bookSourceComment') or '')
    if comment:
        comment = comment.replace('v1.2.1-beta7', 'v1.2.1 Stable', 1)
    prefix = 'v1.2.1 Stable：由 1.2.1-beta7 按用户明确要求原样晋升正式版；正文 Rhino 非法反斜杠修复、Beta4 Scanner/GZIP 懒模块解压与 Base64URL 兼容保持不变。'
    src['bookSourceComment'] = prefix + ('\n' + comment if comment and prefix not in comment else '')
    for k in ('version', 'sourceVersion'):
        if k in src:
            src[k] = VERSION
    for k in ('versionCode', 'sourceVersionCode'):
        if k in src:
            src[k] = VERSION_CODE
    return src


def catalog_item(now, sha):
    raw = f'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian-next/qidian-next.json?v={VERSION_CODE}'
    cdn = f'https://cdn.jsdelivr.net/gh/huoguotiankong/source-core-8d7@main/sources/novel/qidian-next/qidian-next.json?v={VERSION_CODE}'
    return {
        'id': 'qidian-next',
        'name': '🌈 起点增强',
        'summary': '正式版 1.2.1：由 1.2.1-beta7 按用户明确要求原样晋升；正文 Rhino 非法反斜杠问题已真机确认修复，并恢复兼容的 Scanner/GZIP 懒模块解压。',
        'icon': '',
        'channel': 'stable',
        'version': VERSION,
        'updatedAt': now,
        'tags': ['起点','正式版','限免源','情无','小雨用户系统','X','评论页','段评','书友圈','Base64URL','Rhino兼容','正文回归修复'],
        'changelog': [
            '由 1.2.1-beta7 按用户明确要求原样晋升 Stable，不新增业务逻辑',
            '修复正文 EvaluatorException：移除 ruleContent 中会被 Rhino 当成非法字符的字面量反斜杠拼接',
            '懒模块解压恢复已验证的 Scanner + GZIPInputStream 路径，移除 Rhino 不兼容的 java.lang.reflect.Array.newInstance 调用',
            'Base64URL 仅保留 -/_ 标准化与 = 补位；32 个 lazy module 已完成解包/语法门禁',
            '情无/小雨评论、账号系统、正文 Provider 与其它功能沿用 Beta7 代码'
        ],
        'sourceUrl': raw,
        'backupUrl': cdn,
        'importUrl': 'legado://import/importonline?src=' + raw,
        'detailUrl': 'https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/rss/data/details/stable/qidian-next.json',
        'versionCode': VERSION_CODE,
        'sha256': sha,
        'sourcePath': str(SRC_STABLE),
    }


def upsert_items(path, stable_item, remove_beta=True):
    data = load(path)
    items = data.get('items', []) if isinstance(data, dict) else []
    out = []
    inserted = False
    for x in items:
        if not isinstance(x, dict):
            out.append(x); continue
        if x.get('id') == 'qidian-next-beta' and remove_beta:
            continue
        if x.get('id') == 'qidian-next':
            if not inserted:
                out.append(json.loads(json.dumps(stable_item, ensure_ascii=False)))
                inserted = True
            continue
        out.append(x)
    if not inserted:
        out.insert(0, json.loads(json.dumps(stable_item, ensure_ascii=False)))
    data['items'] = out
    return data


def remove_item(path, item_id, now):
    data = load(path)
    if isinstance(data, dict) and isinstance(data.get('items'), list):
        data['items'] = [x for x in data['items'] if not (isinstance(x, dict) and x.get('id') == item_id)]
        if 'updatedAt' in data: data['updatedAt'] = now
        if 'generatedAt' in data: data['generatedAt'] = now
    dump(path, data)


def rewrite_manifest(obj, stable_item):
    if isinstance(obj, list):
        out=[]
        seen=False
        for x in obj:
            if isinstance(x, dict) and x.get('id') == 'qidian-next-beta':
                continue
            if isinstance(x, dict) and x.get('id') == 'qidian-next':
                if not seen:
                    out.append(json.loads(json.dumps(stable_item, ensure_ascii=False))); seen=True
                continue
            out.append(rewrite_manifest(x, stable_item))
        return out
    if isinstance(obj, dict):
        return {k: rewrite_manifest(v, stable_item) for k,v in obj.items()}
    return obj


def bundle_replace(obj, identity, stable_src, remove=False):
    if isinstance(obj, list):
        out=[]
        for x in obj:
            if isinstance(x, dict) and x.get('bookSourceUrl') == identity:
                if not remove:
                    out.append(json.loads(json.dumps(stable_src, ensure_ascii=False)))
                continue
            out.append(bundle_replace(x, identity, stable_src, remove))
        return out
    if isinstance(obj, dict):
        return {k: bundle_replace(v, identity, stable_src, remove) for k,v in obj.items()}
    return obj


def main():
    beta_obj = load(SRC_BETA)
    beta_src = first_source(beta_obj)
    if str(beta_src.get('bookSourceName','')).find('起点增强') < 0:
        raise SystemExit('unexpected beta source')
    identity = beta_src.get('bookSourceUrl')
    if not identity:
        raise SystemExit('missing bookSourceUrl')

    stable_obj = json.loads(json.dumps(beta_obj, ensure_ascii=False))
    stable_src = first_source(stable_obj)
    set_source_meta(stable_src)
    dump(SRC_STABLE, stable_obj)

    sha = hashlib.sha256(SRC_STABLE.read_bytes()).hexdigest()
    now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    day = now[:10]
    item = catalog_item(day, sha)

    stable_catalog = upsert_items('subscription/stable.json', item, remove_beta=True)
    stable_catalog['updatedAt'] = now
    stable_catalog['generatedAt'] = now
    dump('subscription/stable.json', stable_catalog)

    remove_item('subscription/beta.json', 'qidian-next-beta', now)

    novel = upsert_items('subscription/novel.json', item, remove_beta=True)
    if isinstance(novel, dict):
        if 'updatedAt' in novel: novel['updatedAt'] = now
        if 'generatedAt' in novel: novel['generatedAt'] = now
    dump('subscription/novel.json', novel)

    manifest = load('manifest.json')
    manifest = rewrite_manifest(manifest, item)
    if isinstance(manifest, dict):
        if 'updatedAt' in manifest: manifest['updatedAt'] = now
        if 'generatedAt' in manifest: manifest['generatedAt'] = now
    dump('manifest.json', manifest)

    bs = load('bundles/all-stable.json')
    dump('bundles/all-stable.json', bundle_replace(bs, identity, stable_src, remove=False))
    bb = load('bundles/all-beta.json')
    dump('bundles/all-beta.json', bundle_replace(bb, identity, stable_src, remove=True))

    detail = {
        'kind': 'source',
        'title': '🌈 起点增强',
        'summary': 'Stable 1.2.1：由 1.2.1-beta7 按用户明确要求原样晋升；正文 Rhino 非法反斜杠问题已真机确认修复。',
        'badges': ['Stable', VERSION, '正文回归修复', 'Rhino兼容'],
        'sections': [
            {'title':'本次晋升','text':'用户真机确认 Beta7 正文已经修复，并明确要求先将这一版升为正式版。Stable 1.2.1 直接沿用 Beta7 业务代码，不再追加新逻辑。'},
            {'title':'正文修复','text':'ruleContent 改为单一真实 JS 执行块，消除字面量反斜杠导致的 EvaluatorException。'},
            {'title':'模块兼容','text':'恢复已验证的 Scanner + GZIPInputStream 懒模块解压路径；Base64URL 仅做 -/_ 标准化与缺失 = 补位。'},
            {'title':'版本策略','text':'Stable 与 Beta 保持同一 bookSourceUrl 身份，但使用独立物理 JSON 路径；Beta7 文件保留作历史/后续开发基线，不再作为当前活动目录项。'}
        ],
        'sourceUrl': item['sourceUrl'],
        'backupUrl': item['backupUrl'],
        'importUrl': item['importUrl']
    }
    dump('rss/data/details/stable/qidian-next.json', detail)

    entry = f'''\n## {day} · qidian-next Stable {VERSION}\n- 用户真机确认 `1.2.1-beta7` 正文修复成功，并明确要求将这一版先晋升正式版。\n- Stable 直接沿用 Beta7 业务代码，不新增业务逻辑；修复 `EvaluatorException: 不允许的字符：\\`，恢复单一真实 JS 正文执行块。\n- 懒模块解压使用已验证的 `Scanner + GZIPInputStream`，移除 Rhino 不兼容的 `java.lang.reflect.Array.newInstance`；Base64URL 兼容保留。\n- `sources/novel/qidian-next/qidian-next.json`、Manifest、Stable/Novel Subscription、Stable Bundle、RSS Stable Detail、Release Log 已同步；活动 Beta/Novel 重复项移除。\n- Beta7 独立文件继续保留作历史/后续开发基线；Stable/Beta 继续共享同一 Legado `bookSourceUrl` 身份。\n'''
    for fp in ['docs/RELEASE_LOG.md','docs/sources/qidian-next/PROJECT_HANDOFF.md']:
        p=Path(fp); t=p.read_text(encoding='utf-8')
        if f'qidian-next Stable {VERSION}' not in t:
            p.write_text(entry + t, encoding='utf-8')

    # Functional freeze assertion: stable must equal beta except release metadata.
    a = json.loads(json.dumps(beta_src, ensure_ascii=False))
    b = json.loads(json.dumps(stable_src, ensure_ascii=False))
    for k in ['bookSourceName','bookSourceComment','version','sourceVersion','versionCode','sourceVersionCode']:
        a.pop(k, None); b.pop(k, None)
    if a != b:
        raise SystemExit('functional fields changed during promotion')

    print('PROMOTE_OK', VERSION, VERSION_CODE, sha, identity)

if __name__ == '__main__':
    main()
