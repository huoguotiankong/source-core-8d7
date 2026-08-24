# source-core-8d7

阅读 / Legado 书源发布与订阅仓库。

## 目标

- GitHub 负责书源发布、版本管理和订阅分发。
- 阅读 App 内保留完整可独立运行的书源；已导入书源不依赖本仓库运行。
- 正式版（stable）与测试版（beta）分离。
- 使用统一 manifest 管理书源元数据、版本、更新日志和下载地址。

## 目录约定

- `manifest.json`：仓库总清单
- `subscription/`：订阅入口及频道数据
- `bundles/`：批量导入包
- `sources/novel/`：小说书源
- `sources/comic/`：漫画书源
- `sources/aggregate/`：聚合类书源
- `docs/`：仓库规范、迁移和维护文档

## 发布原则

1. `stable` 只收录已验证可用版本。
2. `beta` 用于测试版、Alpha/RC 等预发布版本。
3. 每个书源保留独立 JSON 文件。
4. bundle 由独立书源聚合生成，不作为唯一源文件。
5. 更新书源时同步更新 `manifest.json` 中的版本、时间和更新日志。
