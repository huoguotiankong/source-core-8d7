# 万相书城 Release Log

## 2026-09-25 · v0.1.0-beta1

- 首次加入 `◈ 万相书城` Legado 书源，仅进入 Beta 通道。
- 运行站点固定为 `https://www.wwxsc.com`，不接入第三方聚合接口或镜像线路。
- 搜索：`https://www.wwxsc.com/plus/search.php?q={{key}}`。
- 发现：玄幻、仙侠、都市、历史、科幻、恐怖、纯爱、言情、轻小说九类，提供热门入口与分页入口。
- 详情：书名、作者、封面、简介、分类/状态/更新时间、最新章节。
- 目录：`#all-chapter .panel-body div.item a`。
- 正文：`#cont-body`，保留长章节下一页续读。
- 静态校验已通过：JSON 可解析；搜索/分类运行 URL 均为绝对 `https://www.wwxsc.com`；未使用 `bookSourceUrl` 作为实际请求域名。
- 当前验证级别：`static_only`。未经 Android 阅读端真机确认，不晋升 Stable。
- 发布文件：`sources/novel/wanxiang/bookSource_◈万相书城.json`。
- 独立 Beta Bundle：`bundles/wanxiang-beta.json`。
- 已登记 `manifest.json`、`subscription/beta.json`、`subscription/novel.json` 与 `rss/data/details/beta/wanxiang.json`。
- 为保护当前约 2.5 MB 且存在并发更新的 `bundles/all-beta.json`，本版本不以截断/重写方式强行合并总包；待具备安全重建能力后再并入全量 Beta Bundle。
