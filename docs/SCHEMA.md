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
  "bookSourceUrl": "https://sc8d7.invalid/legado/qidian-official-8d7",
  "summary": "简要功能说明",
  "tags": ["官方目录", "段评", "作者说"],
  "changelog": ["修复…", "优化…"]
}
```

其中：

- `sourceUrl` 是仓库中的 JSON 下载/导入地址，可以随文件部署方式变化。
- `bookSourceUrl` 是 Legado 识别该书源的稳定身份 URL，一经发布原则上不再改变。
- 同一个书源的 Stable/Beta 必须使用同一个 `bookSourceUrl`。
- `bookSourceUrl` 不写版本号、不写 stable/beta，也默认不用原网站主页。
- 项目统一身份命名：`https://sc8d7.invalid/legado/<source-id>-8d7`。
- `sc8d7.invalid` 只作为身份标识；真实网络请求必须使用书源规则中的实际站点/API 地址。
- 旧书源如果依赖 `bookSourceUrl` 解析相对 URL，迁移前必须先改成独立 runtime base/绝对请求地址，不能直接替换后导致功能失效。

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
- `rss/reader-source-repository-beta.json`：第一版 UI Beta 身份 URL，保留用于同源更新识别。
- `rss/reader-source-repository-beta2.json`：当前 UI Beta 2 导入文件；内部 `sourceUrl` 仍保持 Beta 身份不变，因此导入时应更新已有 Beta 而不是创建新的订阅源。

RSS 仓库 UI 采用：

- 阅读原生分类 + 原生文章列表负责浏览；
- HTML 详情页负责版本、标签、日志、导入按钮等展示；
- Stable / Beta / Bundle 分区明确；
- 所有分类入口必须是 `http/https`，不要把 `data:` 作为 `sortUrl`/文章详情请求地址；
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

1. 为书源确定永久 `id` 和 `bookSourceUrl`。
2. 将完整书源 JSON 写入 `sources/...`。
3. 确认同源 Stable/Beta 的 `bookSourceUrl` 完全一致。
4. 更新 `manifest.json`。
5. 更新对应 `subscription/stable.json` 或 `subscription/beta.json`。
6. 重建对应 bundle。
7. 更新 `RELEASE_LOG.md`。
8. Stable 只发布已经实际验证可用的版本；未验证版本进入 Beta。
