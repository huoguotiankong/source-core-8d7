#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sub = json.loads((ROOT / 'subscription/beta.json').read_text())
item = next(x for x in sub.get('items', []) if x.get('id') == 'qidian-next-beta')
changes = [str(x) for x in (item.get('changelog') or [])]
tags = item.get('tags') or []
sections = []
if changes:
    sections.append({'title': '本版更新', 'text': '；'.join(changes)})
sections.append({'title': '版本状态', 'text': '当前为 Beta / 测试通道，需真机确认后才会晋升正式版。'})
sections.append({'title': '更新方式', 'text': '从本订阅页重新导入/更新即可覆盖现有 🌈 起点增强 · Beta。'})

detail = {
    'kind': 'source',
    'title': item.get('name') or '🌈 起点增强 · Beta',
    'summary': item.get('summary') or '',
    'badges': ['Beta', item.get('version') or ''] + ([tags[2]] if len(tags) > 2 else []),
    'sections': sections,
    'sourceUrl': item.get('sourceUrl') or '',
    'backupUrl': item.get('backupUrl') or '',
    'importUrl': item.get('importUrl') or '',
}

out = ROOT / 'rss/data/details/beta/qidian-next.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n')
print(f'synced {item.get("version")} -> {out.relative_to(ROOT)}')
