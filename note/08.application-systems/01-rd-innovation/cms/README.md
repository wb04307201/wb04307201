<!--
module:
  parent: application-systems
  slug: application-systems/01-rd-innovation/cms
  type: article
  category: 主模块子文章
  summary: 一份按业务场景梳理的 CMS 速查手册：内容从创作、审核、发布到分发的完整系统地图。
-->

# CMS · 内容管理系统

> 一份按业务场景梳理的 CMS 速查手册：内容从创作、审核、发布到分发的完整系统地图。

---

## 一、一句话定位

**CMS（Content Management System，内容管理系统）**：让非技术人员（编辑/运营/产品）能创建、编辑、审核、发布内容的系统，是"内容价值链"的核心引擎。

---

## 二、核心功能（5 大模块）

| 模块 | 功能 | 典型操作 |
|------|------|---------|
| **内容创作** | 富文本编辑、多媒体管理、版本控制 | 编辑器 / 素材库 / 历史版本 |
| **内容审核** | 多级审核流、敏感词过滤、合规检查 | 工作流引擎 / AI 内容审核 |
| **内容发布** | 定时发布、渠道分发、A/B Test | 发布队列 / 多端推送 |
| **内容分发** | CDN 加速、SEO 优化、个性化推荐 | 静态化 / 推荐引擎 |
| **数据分析** | PV/UV、转化漏斗、内容效果 | 埋点 / BI 报表 |

---

## 三、典型用户与角色

| 角色 | 主要诉求 | 系统权限 |
|------|---------|---------|
| **编辑/运营** | 写文章、配图、定时发布 | 内容创作、发布 |
| **主编** | 审核内容、调整策略 | 审核流、数据分析 |
| **产品/技术** | 配置系统、接入新渠道 | 系统配置、API |
| **读者** | 消费内容 | 只读 |

---

## 四、与上下游系统的集成

```text
                       ┌──────────┐
                       │  CMS 本体 │
                       └─────┬────┘
                             │
       ┌───────────┬─────────┼─────────┬───────────┐
       ↓           ↓         ↓         ↓           ↓
    创作工具      审核流    渠道分发   数据分析    用户中心
   (Markdown/    (工作流/    (CDN/     (BI/       (SSO/
    WordPress)   Camunda)   App/PWA)  ClickHouse)  LDAP)
```

| 上游 | 集成方式 | 下游 |
|------|---------|------|
| 创作工具（Markdown / Notion）| 导入 API / Webhook | 创作 |
| 审核流（工作流引擎）| 调用审核 API | 审核 |
| 渠道（官网 / App / 小程序）| 内容分发 API | 分发 |
| BI 系统 | 数据推送 / ClickHouse | 分析 |

---

## 五、主流厂商/产品对比

| 类型 | 代表产品 | 适用场景 | 成本 |
|------|---------|---------|------|
| **开源** | WordPress / Drupal / Strapi / Directus | 中小站点 / 二次开发 | 免费 |
| **SaaS** | Contentful / Strapi Cloud / Sanity / Ghost | 跨国营销站 / 多语言 | 按月$ |
| **国内 SaaS** | 织梦 / PageAdmin / 蝉知 / 侯斯特 | 国内内容运营 | 中等 |
| **企业级** | Adobe Experience Manager / Sitecore / 互联通 | 大型集团 / 多站点 | 高 |

---

## 六、选型建议

| 场景 | 推荐 |
|------|------|
| 个人博客 / 中小站点 | WordPress（最成熟） |
| 多语言 / 全球化营销站 | Contentful / Strapi |
| 国内内容平台 | 蝉知 / 织梦 / PageAdmin |
| 大型企业多站点 | AEM / 自研 + Headless CMS |
| 与业务系统深度集成 | Headless CMS（Strapi / Directus）|

---

## 七、实施关键点

1. **内容模型设计**：先抽象实体（文章 / 栏目 / 标签 / 作者），再选 CMS
2. **编辑器选型**：富文本（协作友好）vs Markdown（开发者友好）vs 结构化（Block 化）
3. **审核流**：内置审批 vs 接入外部 BPMN（Camunda）
4. **多渠道发布**：考虑 REST API 抽象，方便接入 App / 小程序
5. **AI 增强**：内容生成（GPT）、图片处理、智能标签、敏感词识别

---

## 🆕 八、敏感词审查系统：CMS 内容审核的技术核心

CMS 内容审核第 1 步是**敏感词过滤**——这是用户评论 / 文章标题 / 标签的"门神"。高并发场景（评论 1k QPS + 弹幕 10w QPS）的完整方案：

- **核心算法**：AC 自动机（O(n) 多模式匹配，相对 KMP 在多模式下常数更优；具体倍数依赖硬件与词表规模）
- **Java 实战**：Spring Boot + HanLP 双数组 Trie + Guava Bloom + Caffeine 三件套
- **架构演进**：单机 → 分布式集群 → 多级异步（具体 QPS 容量以压测为准）
- **核心公式**（相对量级，需经真实压测验证）：AC 自动机 + Bloom Filter + Caffeine + 双数组 Trie 组合可显著降低敏感词匹配耗时，**不可直接把各模块倍数相乘得出最终 QPS**

详细深度专题（含完整 Java 实现 + 9 大优化策略 + 5 反模式）见：

- **主模块**：[04.system-design/04-high-performance/sensitive-word-filter](../../../04.system-design/04-high-performance/sensitive-word-filter/README.md) —— 5 文件 / 1085 行
- **算法基础**：[02.computer-basics/02-algorithms/string-algorithms](../../../02.computer-basics/02-algorithms/string-algorithms/README.md) —— Trie / KMP / AC 自动机 4 文件 / 1092 行
- **面试题**：[13.split-hairs/02.computer-basics/sensitive-word-filter](../../../13.split-hairs/02.computer-basics/sensitive-word-filter/README.md) —— 7 道精选 Q&A + 90 秒话术

### 反模式速查

1. **朴素 KMP 多次匹配**（500ms 延迟）→ 用 AC 自动机
2. **每次请求构建 AC**（100ms 启动）→ `@PostConstruct` 单例
3. **忽略中文分词**（漏检 30%）→ IK Analyzer / HanLP 先分词
4. **同步阻塞主链路**（用户卡死）→ 同步轻量 + 异步二审
5. **词典不热更新**（错过监管事件）→ `@Scheduled` 1 分钟 + Nacos watch

---

## 八（保留）、与其他业务系统的关系

| 系统 | 关系 |
|------|------|
| **CRM** | 内容营销推送客户画像 |
| **ERP** | 内容资产纳入企业资源 |
| **BI** | 内容效果数据分析 |
| **OA** | 内部公告 / 文档与 OA 集成 |

---

← [返回业务系统总览](../README.md)

## 📊 本节统计

- **核心模块**：5 大模块（内容创作 / 内容审核 / 内容发布 / 内容分发 / 数据分析）
- **典型用户**：4 类（编辑-运营 / 主编 / 产品-技术 / 读者）
- **上下游集成**：5 类（创作工具 / 审核流 / 渠道分发 / 数据分析 / 用户中心）
- **厂商分类**：4 类（开源 / SaaS / 国内 SaaS / 企业级）
- **所属价值链**：01 研发创新