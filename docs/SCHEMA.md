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
  "tags": ["官方目录", "段评", "作者说"],
  "changelog": ["修复…", "优化…"]
}
```

## subscription/*.json

RSS 仓库源读取这里的 `items`。每个条目建议使用：

```json
{
  "id": "qidian-official",
  "name": "🔅 起点官方生态",
  "summary": "官方搜索、目录、段评、作者说等",
  "icon": "",
  "channel": "stable",
  "version": "4.1.0",
  "updatedAt": "2026-08-24",
  "tags": ["小说", "官方数据", "段评"],
  "changelog": ["修复…", "优化…"],
  "sourceUrl": "https://raw.githubusercontent.com/.../qidian-official.json",
  "backupUrl": "https://cdn.jsdelivr.net/gh/.../qidian-official.json",
  "importUrl": "legado://import/bookSource?src=https://raw.githubusercontent.com/.../qidian-official.json"
}
```

字段说明：

- `id`：仓库内唯一 ID。
- `name`：列表和详情页显示名称，不强制把版本写进名称。
- `summary`：一句话说明主要能力。
- `channel`：`stable` 或 `beta`。
- `version`：展示版本。
- `updatedAt`：最后发布时间。
- `tags`：详情页功能标签，可选。
- `changelog`：最近一版主要更新，可选。
- `sourceUrl`：主导入地址，默认 GitHub Raw。
- `backupUrl`：备用导入地址，可选，通常使用 jsDelivr。
- `importUrl`：兼容字段；仓库 UI 可以根据 `sourceUrl` 自动生成导入 URI。

RSS UI 应兼容缺少扩展字段的旧条目，不能因为 `tags/changelog/backupUrl` 不存在而报错。

## rss/*.json

- `rss/reader-source-repository.json`：当前稳定仓库订阅源定义。
- `rss/reader-source-repository-beta.json`：仓库 UI / 交互测试定义。

RSS 仓库 UI 采用：

- 阅读原生分类 + 原生文章列表负责浏览；
- HTML 详情页负责版本、标签、日志、导入按钮等展示；
- Stable / Beta / Bundle 分区明确；
- UI Beta 真机确认后再覆盖稳定定义。

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
5. 更新 `RELEASE_LOG.md`。
6. stable 只发布已经实际验证可用的版本；未验证版本进入 beta。
