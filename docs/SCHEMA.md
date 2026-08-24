# 仓库数据约定

## manifest.json

`manifest.json` 是仓库唯一总索引，记录频道入口、批量包地址和所有已发布书源的元数据。

建议每个 `sources[]` 条目至少包含：

```json
{
  "id": "qidian-official",
  "name": "起点官方生态",
  "category": "novel",
  "channel": "stable",
  "version": "4.1.0",
  "versionCode": 410,
  "updatedAt": "2026-08-24T09:14:00+08:00",
  "sourcePath": "sources/novel/qidian/qidian-official.json",
  "sourceUrl": "https://raw.githubusercontent.com/huoguotiankong/source-core-8d7/main/sources/novel/qidian/qidian-official.json",
  "summary": "简要功能说明",
  "changelog": ["修复…", "优化…"]
}
```

## subscription/*.json

RSS 仓库源读取这里的 `items`。每个条目建议使用：

```json
{
  "id": "qidian-official",
  "name": "🔅 起点官方生态 · v4.1.0",
  "summary": "官方搜索、目录、段评、作者说等",
  "icon": "",
  "updatedAt": "2026-08-24",
  "sourceUrl": "https://raw.githubusercontent.com/.../qidian-official.json",
  "importUrl": "legado://import/bookSource?src=https://raw.githubusercontent.com/.../qidian-official.json"
}
```

## bundles/*.json

Bundle 必须保持为阅读可直接导入的书源 JSON 数组：

```json
[
  { "bookSourceName": "源 A" },
  { "bookSourceName": "源 B" }
]
```

正式版与测试版不要混合。

## 发布流程

1. 将完整书源 JSON 写入 `sources/...`。
2. 更新 `manifest.json`。
3. 更新对应 `subscription/stable.json` 或 `subscription/beta.json`。
4. 重建对应 bundle。
5. stable 只发布已经实际验证可用的版本；未验证版本进入 beta。
