# Wyn 商业智能 · 产品资料中心

Wyn 商业智能是基于葡萄城 20 多年数据分析技术积累打造的新一代嵌入式 BI 产品，提供多源数据整合、数据可视化、AI 对话式分析、在线报表设计、数据填报、嵌入式分析与系统管理等一站式数据分析能力。

本仓库面向客户与合作伙伴开放，内容按**「你要解决什么问题」**组织，而不是按源文件的格式（PPT / PDF / DOCX）组织。

---

## 按你的角色进入

| 你是 | 从这里开始 | 你会看到 |
| --- | --- | --- |
| 业务负责人 / 选型评估 | [产品能力概览](docs/01-product/README.md) | 产品能做什么、AI 能力边界、适合什么场景 |
| 行业解决方案负责人 | [行业方案](docs/02-solutions/README.md) | 制造业绩效、计量检测等垂直行业的完整方案 |
| 开发者 / 架构师 | [嵌入式集成](docs/01-product/embedded/README.md) | API 嵌入方式、鉴权、单点登录、扩展机制 |
| IT / 实施顾问 | [部署与运维](docs/04-deploy-ops/README.md) | 环境要求、部署拓扑、升级与备份 |
| 第一次接触 Wyn | [快速上手](docs/03-getting-started/README.md) | 五分钟跑通第一个仪表板 |
| 遇到具体问题 | [常见问题](docs/05-faq/README.md) | 按问题检索的问答集 |

---

## 文档地图

```
docs/
├─ 01-product/          它是什么 —— 产品理解层
│  ├─ whitepaper/       产品白皮书（按章节拆分，可单页引用）
│  ├─ ai-analytics/     AI 问数与对话式分析
│  ├─ visualization/    可视化、仪表板与大屏
│  ├─ data-entry/       在线填报与数据采集
│  └─ embedded/         嵌入式集成，开发者最关心的一层
├─ 02-solutions/        我这行怎么办 —— 行业方案层
│  ├─ manufacturing/    制造业
│  ├─ lims-metrology/   计量检测 / 实验室
│  └─ _shared/          跨行业复用的架构图与素材
├─ 03-getting-started/  怎么开始 —— 上手层（含官方帮助文档导航）
├─ 04-deploy-ops/       部署、集成与运维
├─ 05-faq/              常见问题，检索命中率最高的一层
└─ 06-cases/            客户案例
```

---

## 下载原始文件

白皮书、行业方案 PPT、产品介绍等原始文件体积较大，不放在仓库里，统一挂到仓库的 Releases 页面下载。每个 Release 对应一个产品版本，历史版本保留可追溯。

具体的文件清单与下载方式见 [下载说明](downloads/README.md)。

---

## 写作与素材规范

新增或修改文档前，请先看 [文档模板](templates/doc-template.md)。三条硬性约定：

**1. 图片放在文档同级目录下的 `images/`，不要集中堆到根目录。**

```
docs/02-solutions/lims-metrology/
├─ README.md
└─ images/
   ├─ 01-painpoint-data-silos.png
   ├─ 02-architecture-overview.png
   └─ 03-dashboard-lab-ops.png
```

引用写法：`![数据分散的四个来源](./images/01-painpoint-data-silos.png)`

这样单篇文档是自包含的，搬运、删除或交接都不会产生断链。全站共用的 logo、图标才放根目录 [`assets/`](assets/)。

**2. 图片文件名 = 章节号 + 主题 + 序号，全小写英文加连字符。**

不要用 `image1.png`、`截图 2026-08-11 下午4点22分.png`。按文件名排序时，图片顺序就应该等于阅读顺序。

**3. 图片统一压缩为 PNG，不要转 JPG。**

BI 截图的主体是表格和文字，JPG 压缩会让文字边缘发毛，客户看不清数字。用 PNG 量化压缩（视觉无损，体积通常降到 1/3）：

```bash
python scripts/compress_images.py docs/
```

批量执行前先 `git commit`，脚本会原地覆盖文件。

---

## 版权声明

本仓库内容版权属西安葡萄城软件有限公司所有。转载、摘编或利用其它方式使用本仓库文字或观点，须注明「来源：西安葡萄城软件有限公司」。产品功能、界面与规格随版本演进可能调整，以官方发布的对应版本文档为准。
