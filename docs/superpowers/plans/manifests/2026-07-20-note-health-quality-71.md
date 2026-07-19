# note-health 71 篇质量修复清单

> 范围固定：29 篇高风险文档 + 42 篇代表采样。原始 finding 的 P0-P3 仅供追溯，执行优先级以复核报告/设计规格为准。

## 01.java（6）

### `note/01.java/collection/LinkedHashSet/README.md`
- Score: 18/20 (优秀)
- Finding: [P2] G4 互链偏弱：文章多次提及 LinkedHashMap/HashSet/HashMap 但无任何向上兄弟链接；建议加 ../HashMap/、../LinkedHashMap/ 互链
- Finding: [P2] A4 参数表：缺并发配置表（Collections.synchronizedSet vs CopyOnWriteArraySet）；L317 初始容量公式建议补 loadFactor 推荐值
- Finding: 亮点：8 道面试 Q&A 体系完整；LRU 缓存示例与双向链表原理紧扣
- Outcome: pending

### `note/01.java/collection/WeakHashMap/README.md`
- Score: 18/20 (优秀)
- Finding: [P2] G4 互链偏弱：缺 ReferenceQueue / SoftReference 兄弟文章链接；建议加 ../ReferenceQueue/ 或 11.ai 内存管理模块互链
- Finding: [P2] A2 版本演进：仅标注 JDK 8，未对比 JDK 9/17 中 Reference 处理/ZGC 优化；建议补一节 JDK 版本演进
- Finding: 亮点：6 类陷阱（6.1-6.6）实战价值极高；ReferenceQueue + WeakHashMap 生命周期时序图可视化极佳
- Outcome: pending

### `note/01.java/concepts/spi/README.md`
- Score: 16/20 (良好)
- Finding: [P1] A3 反正例：L262 AutoService 一节缺手动写 META-INF/services 的反例对比；建议补手动 vs 自动配置文件的 ❌/✅ 代码对比
- Finding: [P2] G4 互链：缺向上兄弟链（ServiceLoader、ClassLoader）；建议加 ../../collection/ 或 06.spring SPI 对比
- Finding: [P3] A4 参数表：ServiceLoader 关键方法（reload、stream、线程安全配置）应单独成表
- Finding: 亮点：AutoService 自动生成 SPI 配置文件是实战向总结；Mermaid API vs SPI 对比图到位
- Outcome: pending

### `note/01.java/io/zero-copy/README.md`
- Score: 19/20 (优秀)
- Finding: [P3] A4 调优：L188 'Java 14+ force()' 可补一句 JDK 17/21 对 DirectBuffer Cleaner 的改进（非阻断）
- Finding: 亮点：A 类 4 项全满分；五种拷贝机制 ASCII 数据流图是教学利器；第六节选型指南有工程价值
- Outcome: pending

### `note/01.java/version/java-10/README.md`
- Score: 13/20 (及格)
- Finding: [P0] G4 互链缺失：文末无相关阅读段，无 java-9/java-11 兄弟链；建议参照 java-9 L653-658 格式补 4 条相关阅读
- Finding: [P0] A2 版本对比完全缺失：JEP 286 var 应与 Java 11 lambda 中的 var 演进对比
- Finding: [P1] A3 反正例缺失：JEP 286 缺 var x=null 错误 vs var x=hello 正确对比
- Finding: [P1] A1 源码深度不足：JEP 304 GC 接口代码为概念性示例，应补 GarbageCollectorMXBean 真实 API
- Finding: [P2] A4 调优：JEP 310 AppCDS 应给启动加速实测数字
- Finding: [P3] G2 定位：H1 后无粗体定位句，建议补 'Java 10 = Java 9 后的第一个特性小版本，最重要的 var + AppCDS'
- Outcome: pending

### `note/01.java/version/java-9/README.md`
- Score: 17/20 (优秀)
- Finding: [P1] A3 反正例缺失：JEP 269 List.of 应加 Arrays.asList vs List.of 可变性对比；Optional 应加 isPresent+get 反模式 vs ifPresentOrElse 正例
- Finding: [P2] A4 调优：JPMS 模块化镜像启动加速应有实际数字（裁剪到 ~30MB vs 完整 JRE ~150MB）
- Finding: [P3] 内容冗长：第二节 JEP 索引 L195-L285 共 91 行过于冗长，建议改为可折叠或精简
- Finding: 亮点：第一节 10 核心 JEP 速通 + API + 为什么/影响 格式是该篇独有亮点；'先读前两节再回扫索引'写作策略清晰
- Outcome: pending

## 02.computer-basics（10）

### `note/02.computer-basics/01-network/03-dns/README.md`
- Score: 19/20 (优秀)
- Finding: 通用维度 11/12：frontmatter 完整、定位清晰、代码块规范、回链有但缺兄弟互链、内容深度极佳(11 章)、可读性好
- Finding: 专属维度 8/8：F1 复杂度(查询 RTT)2、F2 可视化(递归/迭代/层级/缓存图)2、F3 边界(5 类攻击+DNSSEC 部署约束)2、F4 多范式(bash/nginx/html/yaml/Corefile)2
- Finding: P2: 末尾补链 TCP/IP 四层模型 与 HTTPS/TLS 1.3 兄弟章节互链
- Finding: 亮点: 11 章从协议原理到 K8s CoreDNS 实战，§9 Corefile 可直接复用
- Outcome: pending

### `note/02.computer-basics/01-network/04-https-tls/README.md`
- Score: 18/20 (优秀)
- Finding: 通用维度 11/12：frontmatter 完整、定位清晰、代码块规范、回链有但缺兄弟互链、内容深度佳(10 章)、可读性好
- Finding: 专属维度 7/8：F1 复杂度(TLS1.2=2RTT vs 1.3=1-RTT+0-RTT 量化)2、F2 可视化(握手时序/证书结构/CA 链)2、F3 边界(只提 0-RTT 重放风险)1、F4 多范式(bash/nginx/yaml/openssl)2
- Finding: P2: 末尾补链 tcp-ip-model 与 dns 互链；§10 最佳实践新增证书过期/SNI 缺失/协议降级 3 类边界
- Finding: 亮点: §6 Let's Encrypt + §7 Nginx/Spring 配置是真正生产可用速查；§9 云原生演进紧扣 2026 技术栈
- Outcome: pending

### `note/02.computer-basics/01-network/tcp-ip-model/README.md`
- Score: 15/20 (良好)
- Finding: 通用维度 10/12：frontmatter 完整、定位清晰、G3 ASCII 框图无语言标签(L19-25/L61-71)、回链+互链完整、内容深度佳、可读性好
- Finding: 专属维度 5/8：F1 复杂度(隐含 RTT 但无延迟量化)1、F2 可视化(4 层+封装+OSI 对比表)2、F3 边界(无任何异常如 MTU/TTL/SYN 泛洪)0、F4 多范式(TCP vs UDP 对比+主流协议)2
- Finding: P1: ASCII 框图改为 text 语言；新增网络层异常(MTU 分片/TTL=0/ICMP/SYN 泛洪)边界小节；显式量化 TCP 握手 RTT 延迟
- Finding: 亮点: L86-94 OSI vs TCP/IP 对比表是批 2 最简洁清晰；L100-102 双向互链到 13.split-hairs 面试题符合双层模式
- Outcome: pending

### `note/02.computer-basics/01-network/wcag/README.md`
- Score: 9/20 (待改进)
- Finding: 通用维度 7/12：frontmatter summary 截断损坏(L7 句子中途断)、无一句话定位(H1 后空)、G3 N/A 满分、G4 仅 footer 无兄弟互链(孤岛)、G5 8 章覆盖完整、G6 可读性佳
- Finding: 专属维度 2/8：F1 复杂度 0、F2 可视化 0、F3 边界 0、F4 多范式(多工具列举)2
- Finding: P0: 路径误归(应在 09.front-end/a11y/)；frontmatter summary 修正；H1 后加一句话定位
- Finding: P1: 孤岛无互链；补对比度算法/APCA 公式小节
- Finding: 亮点: 版本演进(1.0→3.0)是批 2 唯一明确年份列表；POUR 四大原则配实用示例
- Outcome: pending

### `note/02.computer-basics/02-algorithms/clustering/README.md`
- Score: 10/20 (待改进)
- Finding: 通用维度 8/12：frontmatter 完整、定位清晰、G3 N/A、G4 仅 footer 无兄弟互链、G5 内容极浅(仅 1 个表格列 K-Means)、G6 可读性好
- Finding: 专属维度 2/8：F1 复杂度 0、F2 可视化 0、F3 边界 0、F4 多范式(链接子 README)2
- Finding: P0: 极浅导航页(19 行)必须补 4 大算法对比表(K-Means/层次/DBSCAN/GMM)+ 评估指标(轮廓系数/Davies-Bouldin)+ Mermaid 流程图
- Finding: P1: 孤岛无互链(决策树/降维/优化)；frontmatter type=index 应改为 article 或聚合目录
- Finding: 亮点: 是聚合目录雏形，符合 F3 导航模式
- Outcome: pending

### `note/02.computer-basics/02-algorithms/decision-tree/README.md`
- Score: 20/20 (优秀)
- Finding: 通用维度 12/12 满分：frontmatter 完整、定位精准、代码块规范、双回链+4 个互链+反向链、内容深度极佳(3 大模型+数学+实操+超参+反直觉)、可读性佳
- Finding: 专属维度 8/8 满分：F1 复杂度(熵/条件熵/增益/Gini 公式)2、F2 可视化(决策树图+sklearn plot_tree)2、F3 边界(ID3 偏向+4 大防过拟合)2、F4 多范式(Python+多算法对照)2
- Finding: P2: §兄弟章节 4 个相对路径(dimensionality-reduction/optimization/clustering)需校验，部分目录可能不存在需删除或修正
- Finding: 亮点: 批 2 唯一满分，F 类规范范例(必选 7 段齐全+数学+代码+可视化+反直觉全覆盖)
- Outcome: pending

### `note/02.computer-basics/02-algorithms/dimensionality-reduction/README.md`
- Score: 6/20 (不达标)
- Finding: [P0] 严重占位 README（23 行，仅 1 个子条目 PCA），缺 t-SNE/UMAP/LDA/MDS 等核心算法
- Finding: [P0] 无任何兄弟互链（缺 ensemble/optimization/clustering 链接）
- Finding: [P1] frontmatter slug 路径错误（多 computer-basics/ 前缀，应为 algorithms/dimensionality-reduction）
- Finding: [P1] 缺 F1 复杂度分析（PCA O(min(n,d²)) / t-SNE O(n²) / UMAP O(n^1.14)）
- Finding: [P2] 定位句未粗体强调
- Outcome: pending

### `note/02.computer-basics/02-algorithms/ensemble/README.md`
- Score: 18/20 (优秀)
- Finding: [P1] 选型决策树（131-144 行）用 ``` 代码块包裹，应改 Mermaid graph TD
- Finding: [P1] 4 大模型对比表缺时间复杂度列
- Finding: [P2] 缺 Bagging vs Boosting 流程对比 Mermaid 图
- Outcome: pending

### `note/02.computer-basics/02-algorithms/optimization/README.md`
- Score: 6/20 (不达标)
- Finding: [P0] 严重占位 README（23 行，仅 1 个子条目梯度下降），缺 Newton/Momentum/Adam/L-BFGS
- Finding: [P0] 无任何兄弟互链
- Finding: [P1] frontmatter slug 路径错误（应为 algorithms/optimization）
- Finding: [P1] 缺 F1 复杂度对比（SGD O(n) / Newton O(d²) / Adam O(n)）
- Outcome: pending

### `note/02.computer-basics/02-algorithms/string-algorithms/03-ac-automaton.md`
- Score: 19/20 (优秀)
- Finding: [P2] 3 大组件 ASCII 图（41-58 行，19 行）可改 Mermaid graph TD 节省篇幅
- Finding: [P2] 工业库推荐行（279 行）缺版本号（hanlp ≥ 1.8.x）
- Outcome: pending

## 03.database（4）

### `note/03.database/08-nosql/elasticsearch/README.md`
- Score: 19/20 (优秀)
- Finding: [P1] 缺 A2 版本演进对比（ES 7.x vs 8.x：dense_vector/security default on/ILM 主要变更表）
- Finding: [P2] 中文分词章节缺 IK 插件安装命令
- Finding: [P2] 集群架构 ASCII 图（80-95 行）可改 Mermaid 提升维护性
- Outcome: pending

### `note/03.database/08-nosql/mongodb/README.md`
- Score: 19/20 (优秀)
- Finding: [P1] 缺 A2 版本演进对比（MongoDB 4.0 → 5.0 → 6.0 → 7.0 主要变更表：ACID/时序集合/通配符索引/加密）
- Finding: [P2] 副本集 ASCII 图（102-108 行）可改 Mermaid
- Finding: [P2] 分片集群章节可补'分片键选择决策树'（仿 ensemble 131-144 行结构）
- Outcome: pending

### `note/03.database/08-nosql/neo4j/README.md`
- Score: 18/20 (优秀)
- Finding: P1 G1 frontmatter 字段缺 type 标记：只有 category、parent、slug、summary，没有 type:article，与同模块 CONTRIBUTING 不一致
- Finding: P1 G2 一句话定位清晰（第 12 行 ~95 字，>80 字略冗），但功能定位准
- Finding: P1 G3 代码块全部声明 cypher / 文本块裸 ``` 但内容是 SQL/文字对照，非代码可接受
- Finding: P1 G4 仅 footer 回链 + 1 个父级互链，互链偏少（应 ≥2）
- Finding: P2 A1 源码片段丰富（Cypher）但缺 WHY 注释：L48-L73 CREATE/MATCH 块缺"为什么用 MERGE 而非 CREATE"的注释
- Finding: P2 A2 无版本/演进对比：Neo4j 4.x→5.x 的 GDS 演进、Cypher 5 语法变化未提及
- Finding: P2 A3 缺少 ❌/✅ 反例对比：如错误查询模式（笛卡尔爆炸）vs 优化后的索引查询
- Finding: P2 A4 参数表较全（部署注意）但缺调优建议：Page Cache 内存估算公式、超级节点阈值 10000 来源
- Finding: P2 G5 实战案例多（社交/反欺诈），但 5 度查询性能基准 benchmark 缺失
- Finding: P2 G6 结构清晰，章节顺序合理，但表格密度略高（可加小标题过渡）
- Outcome: pending

### `note/03.database/README.md`
- Score: 19/20 (优秀)
- Finding: P0 G4 主模块 README 必备章节完整：导航/学习路径/前置知识/统计/参考 5 段均到位
- Finding: P1 G1 frontmatter 字段完整（number/slug/topic/audience/category/summary），但缺 type:module 显式标记
- Finding: P1 G2 定位句清晰（13 字内：数据库从关系型基础到 NoSQL）
- Finding: P1 G3 仅 1 个 mermaid flowchart，无代码块；Mermaid 渲染良好
- Finding: P2 A1 作为导览 README 不强求源码深度，但 12 个子 README 表格中可加典型技术栈/版本示例
- Finding: P2 A2 缺少数据库版本演进对比（如 MySQL 5.7 vs 8.0 / Redis 6 vs 7）
- Finding: P2 A4 缺参数/配置表：连接池调优、Redis 内存淘汰策略参数建议
- Finding: P2 G6 mermaid 知识脉络图清晰，但速查表 10 行密度大，可分组
- Finding: P2 章节编号风格：与 CONTRIBUTING.md §12 对齐情况良好（学习路径/前置知识/统计）
- Finding: 亮点：完整 4 学习路径分流（新人/后端/架构/面试），与 13.split-hairs 联动
- Outcome: pending

## 04.system-design（6）

### `note/04.system-design/01-foundation/02-evolution/02-serverless-architecture/README.md`
- Score: 17/20 (优秀)
- Finding: P0 G5 引言段（17 行）使用了 '架构困境' 模板，但文章是 Serverless 介绍型，模板不适用（30f63234 已批量移除过此类残留，需复查本篇）
- Finding: P1 G1 frontmatter 缺 date/author/version 字段；模块父链 parent:system-design 缺具体子路径
- Finding: P1 G2 一句话定位写在引言段（17 字）+ H1 标题扩展，覆盖完整但偏长
- Finding: P1 G3 代码块部分未声明语言（L51-L83 三个架构图、L137-L154、L241-L357 五个 ASCII 图均裸 ```），违反 G3 规范
- Finding: P1 G4 仅有 footer 回链 + 0 互链，应补充到 04.system-design 演进史父页与 K8s / 容器主题的互链
- Finding: P2 A1 实战代码丰富（Lambda Python、KEDA YAML、Knative YAML），但 WHY 注释稀缺：L92-L101 Hello World 无"为什么用 python"说明
- Finding: P2 A2 无版本演进：Lambda 演进（2014 至今）、Knative 1.x 变更、GDS 跨版本未提
- Finding: P2 A3 缺 ❌/✅ 对比：长任务/大内存场景为何不能用 Serverless 只有结论性表格，无代码反例
- Finding: P2 A4 限制表（L116-L121）较完整但缺调优建议：内存调优、冷启动 P95 目标值的实测数字
- Finding: P2 G6 表格密集 + 5 个 ASCII 架构图，章节编号 1-9 完整；但代码块语言声明是硬伤
- Finding: 亮点：4 大生产最佳实践 + 适用/不适用场景双视角，内容广度优于一般速查文
- Outcome: pending

### `note/04.system-design/01-foundation/system-design-basics/architecture-diagram/README.md`
- Score: 10/20 (待改进)
- Finding: P0 文章仅 44 行，是 index-only 导览页（开头有注释标记），按 CONTRIBUTING 应被允许，但缺实际内容
- Finding: P0 G5 内容深度严重不足：2 个子章节 4+1/C4 + 1 个选型表 + 1 个工具链接，无源码/案例/对比深度
- Finding: P0 A1 无任何代码/Mermaid 示例：架构图主题本应展示 4+1 视图样例 + C4 Context/Container/Component/Code 4 层图
- Finding: P1 G1 frontmatter 中 parent 与实际路径不一致（slug 写 system-design/architecture-diagram，但文件在 system-design-basics 子目录）
- Finding: P1 G2 H1 后无 ≤80 字定位句；引言段套用了'架构困境'模板（不适用，应删）
- Finding: P1 G3 无代码块，不适用
- Finding: P1 G4 互链 OK（父级 README + 总览 README + Mermaid 工具链），但 footer 回链写 '返回 architecture-diagram' 是同页自指，应改为 '← [返回 system-design-basics](../README.md)'
- Finding: P2 A3 缺 ❌/✅：4+1 vs C4 的实际图样对比（Context 层图示例 vs 4+1 场景视图）
- Finding: P2 A4 无任何参数/配置信息（与图绘制主题相关性弱，可豁免）
- Finding: P2 G6 段落结构清晰但过短；作为导览页应明确写'本文为目录页，跳转到 4+1 与 C4 详情'
- Finding: 亮点：分类明确（4+1 + C4），Mermaid 工具链接实用
- Outcome: pending

### `note/04.system-design/01-foundation/system-design-basics/it4it/functional-components.md`
- Score: 15/20 (良好)
- Finding: P0 文件不是 README.md（按 CONTRIBUTING 规定应为 README.md），且 frontmatter 缺失（IT4IT 章节是子文章，应有 ）
- Finding: P1 G2 一句话定位清晰（L9，~150 字偏长但结构好）
- Finding: G3 mermaid graph TB + graph LR 声明清晰，4 个图都用 graph 类型正确
- Finding: P1 G4 有'上一篇/下一篇'导航，但缺 footer 回链到 it4it/README.md（只有顶部返回目录）
- Finding: P1 G5 内容深度好：9 大组件逐一详解（含核心活动/输入/输出/责任方/成熟度标志 5 维）+ 18 数据对象 + 4 层架构，覆盖 ≥4 个层面
- Finding: P2 A1 缺源码/伪代码：9 大组件的落地工具映射（如 Demand → Jira、Portfolio → LeanIX）可补
- Finding: P2 A2 提到 IT4IT 3.0 引入第 4 层，但未对比 2.0/3.0 演进细节
- Finding: P2 A3 缺 ❌/✅：'有书面 IT 战略'vs'把 Strategy 当成 IT 部门年度汇报'是反例但未标 ❌/✅ 符号
- Finding: P2 A4 缺参数/配置表：成熟度标志表是文字描述，缺量化指标（ADR 评审时长、SLA 自动计算频率）
- Finding: P2 G6 章节结构清晰（6 大节），每个组件用统一表格（7 行固定字段），可读性优
- Finding: 亮点：5 层分组（Strategy/Governance/Demand/Requirement/Design/Portfolio/Catalog/Transition/Operation + Incident 改进层）+ 3 个 Mermaid 体系图，自洽性强
- Outcome: pending

### `note/04.system-design/02-distributed/api-gateway/README.md`
- Score: 11/20 (及格)
- Finding: P0 G2 一句话定位缺失：H1 后直接是空行 + 长描述段，无 ≤80 字定位句；第 14 行描述段 4 行 200+ 字
- Finding: P0 G3 无任何代码块：API 网关主题本应有 Nginx/Kong 配置示例、Spring Cloud Gateway 路由配置等（按 A1 应有源码）
- Finding: P0 A1 无源码：API 网关核心是配置/路由规则，至少应给 Kong declarative config 或 Spring Cloud Gateway RouteLocator 示例
- Finding: P0 A3 缺 ❌/✅ 反例对比：如'在网关层做业务逻辑'vs'只做路由转发'的对比
- Finding: P1 G1 frontmatter summary 字段过长（截断显示'...'），字段值应是单行 ≤120 字
- Finding: P1 G4 互链 OK（3 个相关章节 + 4 个官方文档链接 + footer 回链），是亮点
- Finding: P1 G5 覆盖 7 大功能 + 4 大优势 + 4 场景 + 5 选型 + 3 趋势，层面广但浅
- Finding: P2 A2 无版本/演进：Kong 1.x→3.x、APISIX 演进、Envoy 与 Istio 关系均未提
- Finding: P2 A4 选型建议有 3 行但缺参数表：Kong 插件机制、APISIX 性能 benchmark 数字、限流算法参数
- Finding: P2 G6 6 段编号（核心功能/优势/场景/对比/选型/趋势）结构 OK，但缺乏表格与代码块辅助，纯文字描述多
- Finding: 亮点：5 款产品对比表（Kong/APISIX/AWS/Azure/Spring Cloud Gateway）+ 选型建议 + 4 个官方文档外链
- Outcome: pending

### `note/04.system-design/02-distributed/consensus-algorithms/README.md`
- Score: 9/20 (待改进)
- Finding: 文件仅 47 行（新文件基线要求 100-200 行），触发"浅占位"——本质是 index-only 分类页（已标 index-only），不是内容页。
- Finding: G1=2：frontmatter 完整，字段齐全（module/parent/slug/type/category/summary）
- Finding: G2=1：有定位（H1 后引用摘要 60 字左右清晰度尚可，但非独立"定位"行，而是重复了 summary）
- Finding: G3=1：表格单元无代码块（Paxos Made Simple 引用是 markdown 链接），整页无 ``` ``` 代码块；本身为导览页，代码不强制但应给出算法伪代码
- Finding: G4=2：底部有 ← 返回 分布式 回链 + 3 个子章节互链（Paxos/Raft/Gossip）+ 3 个外部参考链接
- Finding: G5=0：仅 4 行核心概念 bullet + 1 张对比表，未展开任何层面（Paxos 的 prepare/promise/commit 流程、Raft 的 leader election/log replication/安全性、Gossip 的反熵/谣言传播均未涉及）
- Finding: G6=1：对比表清晰，但全文 47 行过于简短，缺乏深度章节
- Finding: A1 源码级深度=0：整页无任何代码/Pseudocode，连算法伪代码都没有（对比表"F个节点故障"应为"f = ⌊N/2⌋ - 1"具体公式）
- Finding: A2 版本/演进对比=1：对比表给出了"提出年份"（Paxos 1989 / Raft 2013 / Gossip 1987）但未展开 Raft 相比 Paxos 为何更易理解的设计演进
- Finding: A3 反例 vs 正例=0：无任何 ❌/✅ 对比；缺单点一致 vs 共识失败的反例
- Finding: A4 参数/配置表=1：对比表有"容错能力"列但内容"F个节点故障"未定义 F 含义（应注 N=3F+1 关系式）
- Finding: P0：将该 index 页快速提升为可独立阅读的内容页，或显式声明"导览页，子章节承载全部内容"——当前摘要前后矛盾（summary 写"共识算法 本应该很简单"但页内无任何"简单"展开）。建议 L18-L25 算法对比表补充一栏"选举/写流程复杂度"和"消息延迟复杂度"，L26-L31 核心概念 L31 增加"F=N/2-1 容错公式"。
- Finding: P1：对比表"Paxos 1989 / Raft 2013"应给出"为什么需要 Raft（解决 Paxos 的难理解性）"——加 §1.1 演进动机小节
- Finding: P1：L41-L43 参考链接 OK，但应加"etcd-raft 实现"等开源项目链接（与 note 中"技术深度规则"一致）
- Finding: P2：L36 子章节链接 [Paxos] / [Raft] / [Gossip] 后面应跟每个子 README 的文件大小或字数提示，方便用户评估阅读量
- Finding: frontmatter 自标"index-only"+ body 自我声明导览页——若坚持导览定位则评分应归入"骨架页"另算，不参与通用叶质量评分；当前评分是按 G1-G6 + A1-A4 硬套，9/20 偏低但符合"内容页标准"
- Outcome: pending

### `note/04.system-design/04-high-performance/product-search/03-ranking.md`
- Score: 17/20 (优秀)
- Finding: G1=2：frontmatter 含 module/parent/slug/type/category/summary，summary 清晰说明"BM25 + 多阶段 + 业务信号 + A/B 测试"4 大维度
- Finding: G2=2：第 L12 独立"一句话"行 50 字左右精确定位 3 层管道从 100 万→20 条
- Finding: G3=2：所有 ``` ``` 均声明语言（json + 多组无语言文本框用于 ASCII 图）
- Finding: G4=2：L14 首回链 + L214 末尾串联回链 + 系列导航表 L207-L213 完整互链 4 篇文章
- Finding: G5=2：覆盖 4 层面（相关性/管道分层/A/B/指标量化）+ BM25/TF-IDF 对比 + NDCG/MRR/CTR 量化目标 + ES function_score 实操 JSON
- Finding: G6=2：表格、列表、代码块、ASCII 图混排，无大段纯文字
- Finding: A1 源码级深度=2：L59-L74 ES function_score 完整 JSON + 注释说明每段用途（field_value_factor/gauss/score_mode/boost_mode 解释清楚）
- Finding: A2 版本/演进对比=2：L20 明确"TF-IDF（ES 5.x 之前默认）"vs L31"BM25（ES 5.x+ 默认）"演进说明 + L45-L53 饱和效应数字演进对比表
- Finding: A3 反例 vs 正例=1：L45-L55 TF-IDF vs BM25 数字对比算半个反例展示，但缺 ❌/✅ 显式标注
- Finding: A4 参数/配置表=2：L40-L43 BM25 参数表（k1/b/IDF + 默认值 + 含义）+ L80-L84 业务信号权重表（0.4/0.3/0.15/0.1/0.05 含推荐值）+ L184-L190 搜索质量指标目标值
- Finding: P2：L165-L168 模型选型表缺 ❌/✅ 反例对比，建议加"GBDT 适合中小规模 vs DNN 适合大规模+特征丰富"显式标注
- Finding: P2：L194-L201 A/B 测试框架图可用 Mermaid 替换 ASCII，增强可维护性
- Finding: P3：系列导航表 L207-L213 自身（本文）单元格只有标题无内容，建议加"BM25 公式 + 多阶段排序 + 业务信号"
- Outcome: pending

## 05.tools（6）

### `note/05.tools/02-docker/command/README.md`
- Score: 14/20 (良好)
- Finding: G1=2：frontmatter 含 module/parent/slug/type/category/summary
- Finding: G2=0：H1 "Docker 命令"无定位行（无粗体"一句话"，无 />引用块）；摘要 summary="Docker 命令"等于零信息
- Finding: G3=2：所有 ``` ``` 均声明 bash
- Finding: G4=1：L130 ← 返回回链 OK，但缺旧章节互链（应链 ../dockerfile、../compose 等子主题）
- Finding: G5=2：覆盖 5 大场景（image/container/network/volume/system）+ Compose + 小技巧 + Linux 安装
- Finding: G6=1：表格密集但 L116-L121 安装步骤用纯文本编号+反引号混排，建议提为代码块或子章节
- Finding: B1 安装步骤可执行=2：L116-L121 Linux 安装 6 步全命令可直接复制（yum update / yum install -y / service docker start / systemctl enable docker），前置条件（root 权限）已说明
- Finding: B2 配置示例=0：仅安装步骤无 daemon.json / Dockerfile / docker-compose.yml 等配置示例
- Finding: B3 使用场景=1：小技巧部分给了 4 个场景（批量删除/查 IP/调试入口/清理），但缺典型业务场景（部署 Spring Boot/Nginx/Redis 等组合示例）
- Finding: B4 对比/选型=1：L90 ⚠️ 提示 Compose v1→v2 命令区别算半个对比，但缺 docker/podman/containerd/lxc 等同类工具对比
- Finding: P0：添加一行"一句话定位"在 H1 后——"Docker 常用命令速查表（镜像/容器/网络/卷/系统/Compose 6 大类）"
- Finding: P1：表格 L40 单元格 ` `docker inspect `` 中含未闭合的反引号语法问题（应为 \`docker inspect \`）
- Finding: P1：补"配置示例"维度——加 §7 Dockerfile 示例（FROM/RUN/COPY/CMD）和 §8 docker-compose.yml 示例（web/db 两服务）
- Outcome: pending

### `note/05.tools/04-nginx/README.md`
- Score: 19/20 (优秀)
- Finding: G1=2：frontmatter 完整 6 字段
- Finding: G2=2：H1 后 L13 "> 反向代理与负载均衡——从 Nginx 配置实战到 Cloudflare Pingora 新一代代理。" 清晰定位 35 字内
- Finding: G3=2：所有 ``` ``` 声明语言（mermaid + text）
- Finding: G4=2：L159 ← 返回回链 + L153-L155 关联互链（02-docker / 06-ali-microservices）+ L20-L21 子 README 导航
- Outcome: pending

### `note/05.tools/05-monorepo/README.md`
- Score: 18/20 (优秀)
- Finding: G1=2：frontmatter 6 字段完整
- Finding: G2=2：L13 "> 单仓多项目管理——演进路径、工具对比"定位清晰 25 字内
- Finding: G3=2：所有 ``` ``` 声明语言（mermaid）
- Finding: G4=2：L156 回链 + L153-L155 互链（04.system-design / 06.spring）+ 工具对比表 L94-L101 5 工具横向对比
- Finding: G5=2：覆盖 5 层面（演进路径 + MultiRepo vs MonoRepo 对比 + 典型问题 + 工具对比 + 选型建议）
- Finding: G6=2：Mermaid 流程图 2 个 + 6 维对比表 + 表格密布，可读性强
- Finding: B1=1：演进路径有命令示例（pnpm/Turborepo）但缺安装命令的直接可复制块——应在 §4.2 后加 ```bash npm i -g pnpm / pnpm add turbo -D``` 等
- Finding: B2=2：Mermaid 配置图完整，且 L94-L101 工具对比维度清晰
- Finding: B3=2：演进路径 3 阶段 + 典型问题 3 类 + 工具选型 5 工具，覆盖 ≥3 场景
- Finding: B4=2：L94-L101 5 工具 × 6 维度对比表 + L116-L121 选型建议表，star 数字有参考价值
- Finding: P2：L101 GitHub Stars 数字有"过期风险"——应在 2026 年重新校对（其他文件已多处校对）
- Finding: P2：L33-L43 Mermaid 第一图阶段三显示"MR" 单字母与阶段一二不一致，建议统一命名（M1/R1/M2/MR → M_1/R_1/R_2/MR_3 或 MonoRepo）
- Finding: P3：补 B1 安装命令块——pnpm workspace 初始化（pnpm init / pnpm-workspace.yaml 示例）+ Turborepo 安装（pnpm add turbo -Dw）
- Finding: Mermaid 流程图 + 多维对比表 + 选型建议 + 互链 5 文章齐全
- Outcome: pending

### `note/05.tools/06-ali-microservices/README.md`
- Score: 18/20 (优秀)
- Finding: G1=2：frontmatter 6 字段完整
- Finding: G2=2：L13 "> 阿里云原生微服务全家桶——控制面 / 治理面 / 数据面 / 运维面 / 可观测。"定位 30 字内清晰
- Outcome: pending

### `note/05.tools/devops/README.md`
- Score: 18/20 (优秀)
- Finding: 评分明细：通用 G1-G6 = 2/2/2/2/2/2（12/12）；B1-B4 = 0/2/2/2（6/8）。
- Finding: P1：B1=0。L54-L136 直接进入 Jenkins/GitLab CI/GitHub Actions 配置，缺少任一工具的安装/启用命令与前置条件。应在“三、3 大主流 CI 工具对比”后增加可复制的最小跑通路径，明确 JDK/Maven、仓库平台、Runner/Agent、Registry 凭据和 kubectl context 等先决条件。
- Finding: P1：新文件基线未完全满足。该文件创建于 2026-06-28，属于近期新沉淀；有 frontmatter、H1、≤80 字定位、实操配置、多个互链和返回链接，但没有“学习目标”“章节清单/阅读时长”“反直觉”段。建议在 L13-L16 之间补 3-5 条学习目标和章节导航，并在最佳实践前补 4-5 条反直觉判断。
- Finding: P1：L127 使用 actions/checkout@v3，示例偏旧；应升级到当前主版本并说明固定到 commit SHA 的供应链安全策略。L133-L135 直接 push `myapp:${{ github.sha }}`，却没有 registry login、完整镜像仓库名或权限配置，当前工作流不能直接执行。
- Finding: P2：L193-L204 的 DORA 阈值没有给报告年份/链接；L211 的“减少构建时间 50%”也没有 benchmark 条件或出处。应标明数据来源和适用条件，或去掉硬编码比例。
- Finding: 亮点：三种 CI 配置、CD 工具选型、典型流水线阶段和子目录索引形成了清晰的从概览到深入阅读路径；所有代码块均标注语言，回链和互链达标。
- Outcome: pending

### `note/05.tools/kubernetes/08-operator-and-gitops/README.md`
- Score: 18/20 (优秀)
- Finding: 评分明细：通用 G1-G6 = 2/2/2/1/2/2（11/12）；B1-B4 = 1/2/2/2（7/8）。
- Finding: P1：G4=1。L324 只有返回 K8s 总览的 footer 回链，正文没有 ≥2 个旧章节互链；应在 Operator/GitOps 部分分别链接现有 Kubernetes controller/Helm、CI/CD vs GitOps 等旧章节，避免孤岛式专题。
- Finding: P1：B1=1。L220-L225 给了 Argo CD 安装命令，但前置条件不完整：没有 Kubernetes 版本/权限、kubectl context、集群连通性和安装后访问/验收命令。应补 `kubectl get pods -n argocd` 等最小验收步骤，并提示 stable URL 非版本固定资源。
- Finding: P1：新文件基线未完全满足。该文件创建于 2026-06-28，属于近期新沉淀；有 frontmatter、H1、定位、实操命令、选型表和回链，但缺“学习目标”“章节清单”“兄弟章节”“反直觉”结构。建议在 L13-L16 后补齐，并至少提供 4 个旧章节互链。
- Finding: P1：L138-L155 的 Reconcile 示例把 `r.Get` 的所有错误都直接返回，没有区分资源已删除时的 NotFound；`if replicas == 3` 也只是占位逻辑，不能形成可运行 Controller。应加 NotFound 分支、desired/current state 比对、CreateOrUpdate/owner reference/status 更新等关键步骤，或明确标注为伪代码。
- Finding: P2：L162-L172 的 Operator 名称混用项目名/泛称，L303 的“Flux Federation”与 L258 的“PR 预览”等能力需给官方链接或限制条件；避免把生态扩展能力写成开箱即用的核心能力。
- Finding: 亮点：CRD、Controller、Argo CD Application/ApplicationSet 都给了带关键注释的完整配置；GitOps vs CI/CD、Argo CD vs Flux 两张表都有明确选型结论。
- Outcome: pending

## 06.spring（3）

### `note/06.spring/01-core/ioc/dependency-injection.md`
- Score: 14/20 (良好)
- Finding: 评分明细：通用 G1-G6 = 0/2/2/1/2/2（9/12）；A1-A4 = 2/1/2/0（5/8）。
- Finding: P0：G1=0。全文没有 `` frontmatter；应在 L1 前补符合 CONTRIBUTING 的 module 元数据（parent、slug、type、category、summary）。
- Finding: P1：G4=1。L2 有顶部返回链接和 2 个互链，但全文 L221 结束后没有 footer 回链；应新增“相关章节”并以 `← [返回 IoC 总览](README.md)` 收尾。
- Finding: P1：A4=0。没有注入相关参数/配置表；可新增 `@Autowired(required=false)`、`@Qualifier`、`@Primary`、`ObjectProvider`、单构造器省略 `@Autowired` 的适用条件与选择建议表。
- Finding: P1：L4 将“工厂方法注入”与构造器/Setter/字段并列成 4 种“塞法”，概念层级不严谨：Spring 容器文档将 constructor/setter 作为主要 DI 形式，而 factory-method/@Bean 首先是 Bean 实例化/定义机制，工厂产出的 Bean 仍可再接受依赖。建议改成“三种注入入口 + 两种工厂实例化方式”，避免把 `@Bean` 写成对工厂方法的简单取代。
- Finding: P1：L82 的 `@Autowired(required = false)` Setter 可选注入示例需要说明：该模式在候选不存在时方法可能完全不被调用；若想显式表达可选依赖，补 `Optional` 或 `ObjectProvider` 对比。
- Finding: P2：A2=1。仅 L70 提到 Spring 4.3+ 单构造器可省略 `@Autowired`，演进信息太薄。建议增加 XML→注解→Java Config 的演进，以及当前 Spring/Jakarta 场景下的推荐做法。
- Finding: 亮点：L30-L59 有明确的高耦合反例与构造器注入正例，随后覆盖 Setter、字段、XML 工厂和测试替身，代码均有语言标识且结构易读。
- Outcome: pending

### `note/06.spring/03-data/transaction/propagation-and-isolation.md`
- Score: 16/20 (良好)
- Finding: 评分明细：通用 G1-G6 = 0/2/2/2/2/2（10/12）；A1-A4 = 2/1/1/2（6/8）。
- Finding: P0：G1=0。全文没有 module frontmatter；应在 L1 前补 parent/slug/type/category/summary。
- Finding: P0：L10 写“READ_COMMITTED（MySQL InnoDB 默认）”，但 L187、L231 又正确写成 `REPEATABLE_READ`，同篇自相矛盾；应把 L10 改为 `REPEATABLE_READ`，并避免把“90%/99%”写成无来源统计。
- Finding: P0：L83-L84 将 REQUIRES_NEW 的“挂起（不阻塞）”说得过于绝对，L344 更错误地解释成“挂起 = 释放连接”。外层事务资源通常仍绑定，内层独立事务需要自己的资源/连接；连接池不足甚至会等待或死锁。应改写并补连接池至少大于并发线程数的容量警告。
- Finding: P1：L237-L338 的 afterCommit 指导不完整。Spring 文档明确提示事务虽已提交，资源仍可能可访问；afterCommit 中继续数据库操作若要真正提交，需另启 `REQUIRES_NEW`。应在消息/审计示例旁补充这一点，并说明直接发 MQ 仍有失败窗口，严格一致性场景用 transactional outbox。
- Finding: P1：A3=1。全文只有“正确用法”和概念对照，没有可运行的错误示例。建议针对 self-invocation 导致传播不生效、捕获异常后外层 UnexpectedRollbackException、REQUIRES_NEW 连接池耗尽增加 ❌/✅ 对照。
- Finding: P2：A2=1。版本意识仅体现于接口内容，没有系统说明 Spring 5.3/6.x 的 TransactionSynchronization 回调演进或不同事务管理器对 NESTED/挂起的支持差异。
- Finding: 亮点：七种传播行为、四种隔离级别、TransactionSynchronization 和 TransactionalEventListener 形成多层覆盖；代码、表格和 Mermaid 配合良好，正文及尾部有多个相关章节互链。
- Outcome: pending

### `note/06.spring/06-integration/validation/cross-field.md`
- Score: 13/20 (及格)
- Finding: 评分明细：通用 G1-G6 = 0/2/2/0/2/2（8/12）；A1-A4 = 2/1/1/1（5/8）。
- Finding: P0：G1=0。全文没有 module frontmatter；应在 L1 前补 parent、slug、type、category、summary。
- Finding: P0：G4=0。没有 footer 返回上级，且只有 L120 一个旧章节链接；应新增“相关章节”，至少链接 validation 总览和注解/分组校验两篇旧文，并以 `← 返回 Validation 总览` 收尾。
- Finding: P0：L8-L15 的 `@ScriptAssert` 示例使用 `lang="javascript"` 和 `_.startDate`。现代 JDK 默认不再自带 Nashorn，Hibernate Validator 还要求类路径存在 JSR-223 引擎；其默认对象别名通常是 `_this`，不是 `_`。应改成可验证的 Groovy 示例或显式设置 alias，并写清依赖和安全/性能限制。
- Finding: P1：L64-L86 的标题“@Valid 传播到 List / Set 元素”偏离本文核心的跨字段校验，而且 `@Valid` 级联验证不等同于容器元素约束。示例在字段和类型实参上重复 `@Valid`，应只保留一个必要位置，并分别解释 `List` 的容器元素约束与 `@Valid List` 的级联验证。
- Finding: P1：A3=1、A4=1。四种方案有正确示例和选型表，但缺失败写法/调试结果，也缺关键参数建议。可增加“字段级 validator 试图读取 root bean”的反例，以及 `reportOn`/`addPropertyNode`、null 语义、groups、Spring 注入支持的参数表。
- Finding: P1：该文件创建于 2026-06-14，可视为近期新沉淀；虽然约 120 行且有 H1、清晰定位、代码和选型表，但不满足新文件 7 段基线中的学习目标、章节清单、兄弟章节、反直觉和返回上级。应补齐结构后再验收。
- Finding: 亮点：类级自定义 ConstraintValidator 的示例完整，尤其 L46-L49 将 violation 定位到 `endDate`，比只返回类级错误更利于 API 前端展示；四方案选型表也给出了明确推荐。
- Outcome: pending

## 07.workflow（4）

### `note/07.workflow/apache-eventmesh/README.md`
- Score: 17/20 (优秀)
- Finding: 评分明细：通用 G1-G6 = 2/2/2/2/2/2（12/12）；B1-B4 = 0/1/2/2（5/8）。
- Finding: P0：L173-L193 的 Serverless Workflow 0.9/1.0 时间线与状态、L109 同时写 `version: '1.0'` 和 `specVersion: '0.8'`、L189 将 AWS Step Functions 描述为该规范 0.8 子集，均需逐条对官方规范与项目状态核实。当前内容把预测/推断写成既成事实，至少应加官方 release/CNCF 链接和“截至 YYYY-MM”的证据。
- Finding: P0：L257-L333 把“12306 + EventMesh + Serverless Workflow”称为真实标杆案例，并给出 120 万 QPS、Topic/Partition、0 错单、事件丢失率和切换时间等大量精确数字，却没有任何来源。现有官方 EventMesh 链接不能支撑这些断言。必须逐项补公开案例/演讲/论文链接；无法核实时，改成“假设性架构示例”并删除品牌、时间线和精确收益。
- Finding: P0：L344 写“EventMesh 2018 才成为 Apache 顶级项目”事实错误；公开资料显示其 2023 年才从 Apache 孵化器毕业为 TLP。应纠正项目历史，同时核实 L320-L325 的 12306 采用时间线。
- Finding: P1：B1=0、B2=1。全文没有 EventMesh/Workflow Runtime 安装命令或前置条件，唯一 YAML 更像概念示例，且没有对应运行器与执行命令。应提供 Docker/Kubernetes 最小部署、后端 event store、端口、运行/提交工作流和验收命令，并标注适用版本。
- Finding: P1：L199 与 L201 自相矛盾：前者称 EventMesh 是解耦应用与 Kafka/RocketMQ/Pulsar 的基础设施层，后者又称“与 Kafka/Pulsar 属于同一层”。应统一为 EventMesh 在应用与事件存储/消息中间件之间的抽象层，并说明是否可替代/依赖具体 broker。
- Finding: P2：标题路径为 apache-eventmesh，但 H1 是泛化的“事件驱动与 Serverless Workflow”，范围同时覆盖 BPMN、Serverless Workflow、EventMesh、12306，主题过宽。建议拆出 Serverless Workflow 与案例篇，本篇聚焦 EventMesh 可执行实践。
- Finding: 亮点：通用质量维度全部达标；章节导航、概念速查、4 张 Mermaid、BPMN/Serverless Workflow 与 EventMesh/Kafka 的选型讨论、多个跨模块互链，使文章非常易读且场景覆盖丰富。
- Outcome: pending

### `note/07.workflow/apache-eventmesh/cloud-flow/README.md`
- Score: 17/20 (优秀)
- Finding: 评分明细：通用维度 12/12（G1-G6 均为 2）；B 类专属维度 5/8（B1=0、B2=1、B3=2、B4=2）。架构图、两个以上场景、方案对比和互链完整，是本批结构最完整的一篇。
- Finding: P0（B1）：L223-L238 虽给出下载、启动和 HTTP 命令，但未说明 JDK、操作系统、事件存储等前置条件，`bin/eventmesh-start.sh -m runtime` 和 `/workflow`、`/workflow/list` 端点也缺少对应版本的官方依据，不能视为可直接复制执行。应固定经实测的 EventMesh 版本，补齐环境要求、官方启动命令、健康检查、完整请求及期望响应。
- Finding: P1（B2）：L172-L215 只是 Serverless Workflow 0.8 语法片段，引用了 `groupMessages`、`putObject`、`gzipAndUpload`，却没有函数定义、事件定义或可执行入口。应补成完整 YAML，注释关键字段，并给出校验和加载命令。
- Finding: P1（版本与事实一致性）：L224 写“替换为当前最新版本”却硬编码 1.10.0，L173-L176 又固定旧 DSL 规格。应改成“本文验证版本”，记录验证日期，并链接该版本的 EventMesh 与 Serverless Workflow 官方文档，避免“最新”随时间失效。
- Outcome: pending

### `note/07.workflow/process-engine/README.md`
- Score: 13/20 (及格)
- Finding: 评分明细：通用维度 9/12（G1=2、G2=2、G3=0、G4=2、G5=1、G6=2）；B 类专属维度 4/8（B1=0、B2=0、B3=2、B4=2）。选型表和场景覆盖较好，但没有可运行实战。
- Finding: P0（B1/B2）：全文没有安装命令和完整配置。应新增一个最小闭环，例如“启动 Camunda 8/Zeebe → 部署 BPMN → 启动 Job Worker → 创建实例 → 查看完成状态”，同时给出 Docker/CLI 前置条件及带注释的连接、重试、超时配置。
- Finding: P1（G3）：L153-L173 的决策树使用裸代码围栏。将其改为 `text` 代码块或 Mermaid 流程图，消除代码块规范硬伤。
- Finding: P1（G5）：L205-L210 只有行业选型概述，没有从流程定义、Worker 执行到失败重试/补偿的端到端案例。建议以订单履约或人工审批为例，补一份 BPMN、Worker 片段、关键配置和故障恢复结果。
- Finding: P1（事实可核验性）：L136、L193-L203 包含“10K+ 实例/秒”“维护到 2028+”“AI Task”等强版本或性能结论，却无版本、测试条件和来源。应逐条链接官方发布说明或 benchmark；无法核实的数字改为定性描述。
- Finding: P2（链接）：L230 的 `[返回 07 工作流](README.md)` 指向本文自身，与 L248 的正确回链重复。应改为 `../README.md` 或删除该条。
- Outcome: pending

### `note/07.workflow/workflow-and-microservice-orchestration/README.md`
- Score: 14/20 (良好)
- Finding: 评分明细：通用维度 10/12（G1=2、G2=1、G3=2、G4=2、G5=2、G6=1）；B 类专属维度 4/8（B1=0、B2=0、B3=2、B4=2）。案例和选型维度丰富，但实操缺失且存在明显事实风险。
- Finding: P0（事实错误）：L166 把 Temporal 标成“商业”协议，L172 把 Temporal 说成 Cadence 的“商业化版”，L232 又称 Temporal 1.x 在 2024 年 GA。应依据 Temporal/Cadence 官方仓库与发布记录重写：明确二者的项目关系、各自开源许可证和准确版本时间线。
- Finding: P0（B1/B2）：全文没有安装步骤或服务端配置；L263-L278 的 Python 片段缺少 `timedelta`、`run_agent`、Activity 定义、Worker 注册和客户端启动，不能运行。应补齐环境安装、Temporal Server 启动、完整 Workflow/Activity/Worker/Client 代码及执行结果。
- Finding: P1（G2）：L15 的一句话定位超过 80 字。可压缩为“工作流引擎以持久化状态协调跨服务长流程；Zeebe、Conductor、Temporal 分别采用 BPMN、JSON 和代码 DSL”。
- Finding: P1（G6）：L176 与 L198 连续出现两个“## 五”，且全文 322 行，导航与正文编号不一致。把“完整图谱”降为第四节子节或独立附录，并重新编号后续章节。
- Finding: P1（数字无出处）：L205-L242 的“100 万+”“提升 10 倍”“成本降 60%”“效率升 5 倍”“bug 降 80%”“百万级 QPS”等案例数字均无原始链接。应为每个案例增加官方工程博客/演讲链接和口径；否则删除效果数字或标为示意。
- Outcome: pending

## 08.application-systems（3）

### `note/08.application-systems/01-rd-innovation/cms/README.md`
- Score: 11/20 (及格)
- Finding: 评分明细：通用维度 11/12（G1=2、G2=2、G3=2、G4=2、G5=2、G6=1）；A 类专属维度 0/8（A1-A4 均为 0）。路径于近期重组中新增，按新文件基线复核：144 行符合 100-200 行范围，但缺学习目标、章节清单和 4-6 个兄弟章节区。
- Finding: P0（事实准确性）：L102-L107 将 AC 自动机、Bloom Filter、Caffeine、双数组 Trie 的倍数直接相乘并推出“100w QPS”，同时给出 2ms、200x、10x 等无测试环境数字；这不是可复现的性能推导。应附数据集、硬件、并发模型、JMH/压测脚本及结果，或删除这些倍数和最终 QPS 结论。
- Finding: P1（A1-A4）：作为 08.application-systems 的 A 类文章，当前没有源码、版本演进、反例/正例代码或配置参数。可新增一个 Headless CMS 最小实战：内容模型 JSON/Schema、审核 Webhook、缓存/CDN 配置、错误与正确的发布幂等实现，并说明版本与参数取值。
- Finding: P1（新文件基线）：在 H1 后增加 3-5 条学习目标和“主题/内容/时长”章节表；“相关章节”应补 CMS 所在价值链的 4-6 个兄弟文章链接，而不只链接敏感词专题。
- Finding: P1（G6）：L100 和 L125 都使用“八”，后者甚至写成“八（保留）”；L136 的返回链接又出现在 L138 统计之前。应将系统关系改为“九”，把统计移到 footer 回链之前。
- Finding: P2（可维护性）：L111-L113 硬编码“5 文件/1085 行”“4 文件/1092 行”“7 道”等易漂移统计。改为描述覆盖内容，或用可自动校对的统计生成机制。
- Outcome: pending

### `note/08.application-systems/01-rd-innovation/pdm/README.md`
- Score: 15/20 (良好)
- Finding: 评分明细：通用维度 11/12（G1=2、G2=2、G3=2、G4=2、G5=2、G6=1）；A 类专属维度 4/8（A1=0、A2=2、A3=0、A4=2）。路径于近期重组中新增，按新文件基线复核：305 行已超过“>300 行过长”阈值，且缺学习目标、章节清单、4-6 个兄弟互链和集中的反直觉章节。
- Finding: P0（数字与案例可核验性）：L35、L61、L85-L108、L151-L166、L245-L260 大量给出数据范围、行业占比、成本、性能阈值和案例收益，却没有可点击来源；“公开案例引用”不是引用。应为每个外部数字增加厂商案例/标准/报告的具体链接、年份和统计口径；无法核实的数据改为“示例假设”并移出事实陈述。
- Finding: P1（新文件基线/G6）：文章处于 200 行快改与 500 行深耕之间，能力、场景、考量和案例重复展开，阅读路径不清。建议拆成“PDM 总览（100-200 行）+ 实施与选型 + 行业案例”三篇；若保留单篇，则增加学习目标和章节导航，并合并重复段落。
- Finding: P1（A1/A3）：没有源码级片段和可执行的反例/正例。建议补一组 EBOM/Part REST JSON、版本检入 API 或同步伪代码，并用错误的“CAD 与 BOM 双写”对比正确的“版本校验+幂等事件”实现，解释为什么。
- Finding: P1（统计漂移）：L294 称“核心能力 6 类”，但 L45-L63 实际列出远多于 6 项；L295 称“典型场景 4 类”，正文 L76-L95 至少列出 6 类并另有详解。应从正文实时校对统计，避免摘要与内容冲突。
- Finding: P2（互链）：L286-L290 只有研发创新、PLM 和业务系统总览链接。应补 ERP、MES、QMS、项目管理等 4-6 个兄弟章节，并标明各自的数据边界。
- Outcome: pending

### `note/08.application-systems/04-sales-service/scrm/README.md`
- Score: 10/20 (待改进)
- Finding: 评分明细：通用维度 10/12（G1=2、G2=2、G3=2、G4=1、G5=1、G6=2）；A 类专属维度 0/8（A1-A4 均为 0）。路径于近期重组中新增，按新文件基线复核：115 行符合行数范围，但缺学习目标、章节清单、兄弟章节和反直觉段。
- Finding: P0（事实准确性）：L39 的“私域运营转化率 3-10x”没有定义基线、行业、样本或来源。应补权威报告及统计口径；若只是经验判断，改为不带倍数的定性表述。
- Finding: P1（A1-A4）：全文停留在业务定义和产品罗列，没有源码/接口示例、版本演进、反例/正例或配置参数。应补企业微信客户事件 Webhook、客户合并与标签更新示例、授权/退订配置，并对比错误的无授权群发与正确的同意管理流程。
- Finding: P1（G5）：没有一个端到端实战案例。建议增加“渠道获客 → 用户授权 → 身份去重 → 标签分群 → 触达 → 交易回流 → LTV 计算”的零售案例，同时说明重复事件、退订、删除请求和渠道限流如何处理。
- Finding: P1（G4/新文件基线）：L106 只有返回上级的回链，没有旧章节互链。应新增 CRM、CMS、OMS、BI 等 4-6 个兄弟链接，并在每条后说明 SCRM 与该系统的边界。
- Finding: P1（合规深度）：L102 只写“用户授权、数据合规”，过于笼统。应补个人信息保护的最小必要、告知同意、撤回授权、数据删除、留存期限、审计日志和第三方渠道责任边界，形成可执行检查表。
- Outcome: pending

## 09.front-end（3）

### `note/09.front-end/03-frameworks/react/README.md`
- Score: 14/22 (及格)
- Finding: 评分依据：通用维度 11/12（frontmatter 2、定位 2、代码块 2、回链互链 1、深度 2、可读性 2）；G 类专属 3/10（运行环境 1、性能量化 1、状态选型 1、渲染流程 0、a11y 0）。
- Finding: P0：L153-L169 的“Compiler 后”示例使用 `items.sort()`，会直接修改传入数组；改为 `[...items].sort(...)`，并说明 React Compiler 需要构建配置且不会把任意可变代码自动变安全。L246-L263 的 Effect 在依赖仅为 `[data]` 时通常是冗余派生状态，并不必然“无限循环”；应改标题或补一个无依赖数组/依赖每次变化的真实循环反例。L300-L303 的 `suppressHydrationWarning` 是受控逃生口，不宜列作通用正确修复。
- Finding: P1：L308 只有上级回链，缺少至少 2 个旧章节互链；建议在性能、状态和路由相关段落直接链接 `../../06-performance/`、`../../05-architecture/state-management/` 等现有章节。
- Finding: P1：补一张“事件输入 → React 调度 → render phase → commit phase → paint/hydration”的完整流程图；当前只有选型图和场景图，G4 无法得分。
- Finding: P1：新增运行环境矩阵，明确 CSR、SSR、SSG、RSC 的边界，以及目标浏览器、Browserslist 和 polyfill 策略；当前虽提及 SSR/CSR/RSC，但没有兼容性策略。
- Finding: P1：增加 a11y 实例，例如语义化表单标签、键盘焦点管理、`aria-live` 提交状态；现有表单与购物车示例均未覆盖可访问性。
- Finding: P2：将 L216 的“JS 体积减少 60%+”替换为带设备、网络、数据集和构建版本的实测，并至少给出 LCP/INP/CLS 前后对比；否则删除百分比。
- Outcome: pending

### `note/09.front-end/05-architecture/bff/README.md`
- Score: 9/22 (待改进)
- Finding: 评分依据：通用维度 8/12（frontmatter 2、定位 1、代码块 2、回链互链 1、深度 1、可读性 1）；G 类专属 1/10（运行环境 1、性能量化 0、状态选型 0、渲染流程 0、a11y 0）。文件无代码块，因此代码块语言规范本身未违规，但也没有可执行实战。
- Finding: P0：L69“从根源上杜绝 XSS 窃取 Token”表述过度。HttpOnly 只能阻止脚本读取 Cookie，不能消除 XSS 发起已认证请求、CSRF、会话固定等风险；应补充 `SameSite`、CSRF token、Origin 校验、Cookie 前缀、会话轮换和 OAuth BFF 威胁模型。L67“底层微服务完全不需要关心……只信任 BFF”也应改为服务间认证、最小权限和用户级授权仍不可省略。
- Finding: P1：补一个可运行的 BFF 实战案例，例如 NestJS/Express 并发聚合用户、商品和营销服务，包含超时、取消、部分失败、熔断、缓存、日志与 trace-id；当前 L56-L61 只有文字机制，G5 只能给 1 分。
- Finding: P1：加入 Mermaid 架构图与请求时序图，展示浏览器输入 → BFF 会话校验 → 并发下游调用 → 聚合响应 → 客户端状态更新与渲染；当前未覆盖 G4 的完整链路。
- Finding: P1：按 G 类统一量表补“BFF 数据与前端状态边界”，至少比较 TanStack Query、Redux Toolkit、Zustand 三种方案，说明哪些数据应留在服务端缓存、查询缓存或客户端全局状态；当前 G3 为 0。
- Finding: P1：L11 提到“上一篇”却没有链接，文末也只有上级回链；应把 Token 安全相关文章链上，并增加 API 网关、GraphQL 或微服务架构的至少一个旧章节互链。
- Finding: P2：用同一页面的调用次数、payload 大小、p50/p95 延迟和 LCP/INP 实测验证 L58 的收益；“彻底消灭请求瀑布流”“大幅减少”应改为受下游依赖图约束的条件性结论。另补错误提示与加载状态如何支持 `aria-live`、焦点恢复等 a11y 要点。
- Outcome: pending

### `note/09.front-end/05-architecture/state-management/README.md`
- Score: 16/22 (良好)
- Finding: 评分依据：通用维度 12/12（frontmatter、定位、代码块、回链互链、深度、可读性均为 2）；G 类专属 4/10（运行环境 0、性能量化 1、状态选型 2、渲染流程 1、a11y 0）。
- Finding: P0：L48 的“80%+”、L73 的“90%”、L58-L64 的趋势/包体积以及多处“2026 共识”没有来源和统计口径。为每个数字补官方 bundle 数据或调查链接、版本和日期；无法核实时删除百分比并改成条件化描述。
- Finding: P1：新增 SSR/RSC/SSG 专节，说明 per-request store、服务端状态序列化、hydration、持久化恢复、跨标签页同步及 localStorage 不可用时的降级；当前跨 React/Vue 的比较不等于浏览器/运行环境适配，专属 G1 为 0。
- Finding: P1：把 L20-L29 的简图扩展成“用户输入 → action → store 更新 → selector/subscription → 框架调度 → render → commit”的完整链路，并分别标出 Redux、Zustand、Jotai 的订阅粒度；当前仅展示 UI 与 State 的循环，G4 只能给 1 分。
- Finding: P1：增加 React Profiler 或 Vue DevTools 的可复现实测，记录组件提交次数、渲染耗时及 LCP/INP/CLS；现有 KB 数字是包体积，不足以满足性能指标量化。
- Finding: P1：补 a11y 场景：全局状态更新后的焦点恢复、异步错误的 `aria-live` 通知、模态框状态与键盘导航；当前专属 G5 为 0。
- Finding: P2：L102-L153 的计数器代码缺 imports、类型声明和 Provider/初始化上下文。可增加一个完整的小型购物车或权限状态案例，使选型结论不仅依赖玩具示例。
- Outcome: pending

## 10.big-data（3）

### `note/10.big-data/03-realtime-compute/01-flink-vs-spark-streaming/README.md`
- Score: 12/20 (及格)
- Finding: 评分依据：通用维度 10/12（frontmatter 2、定位 2、代码块 0、回链互链 2、深度 2、可读性 2）；A 类专属 2/8（源码深度 1、版本演进 0、反例正例 0、参数配置 1）。
- Finding: P0：L33-L53、L84-L105、L159-L173 的裸围栏必须声明 `text`；按规则只要存在裸代码块，通用代码块规范即为 0 分。
- Finding: P0：L60“Spark Streaming 默认 1 秒微批”混淆旧 DStream 与 Structured Streaming；Structured Streaming 的触发器可配置且默认并非固定 1 秒。L113-L121 的嵌套 YAML 也不像可直接使用的 Flink 配置键。应区分 DStream/Structured Streaming，并改成对应版本真实的 `flink-conf.yaml` 或代码配置。
- Finding: P1：补 Flink checkpoint barrier/状态快照的源码或关键调用链片段，解释为什么能做到一致性；现有 DataStream API 和 PySpark 示例只展示“怎么写”，A1 只能得 1 分。
- Finding: P1：新增版本演进矩阵，至少覆盖 DStream → Structured Streaming、Flink RocksDB backend 命名/配置变化、相关版本的 checkpoint 与 state backend 差异；当前 A2 为 0。
- Finding: P1：增加明确的反例/正例，例如串行异步 I/O vs Async I/O、无幂等 sink vs 两阶段提交 sink，并展示故障重放结果；当前 A3 为 0。
- Finding: P1：把 checkpoint interval、timeout、min pause、state backend、watermark 延迟整理为真实参数表，给出工作负载、状态大小和恢复目标下的调优依据；L184 的“60-300 秒”缺推导和适用边界。
- Finding: P2：L69-L78 的 `<100ms`、百万级吞吐、Exactly-Once 和 TB 级状态结论必须附版本、硬件、数据规模、source/sink 语义及 benchmark 来源；否则改为定性区间，避免把端到端语义写成引擎无条件保证。
- Outcome: pending

### `note/10.big-data/04-data-lake/01-iceberg-vs-delta-vs-hudi/README.md`
- Score: 10/20 (待改进)
- Finding: 评分依据：通用维度 10/12（frontmatter 2、定位 2、代码块 0、回链互链 2、深度 2、可读性 2）；A 类专属 0/8（源码深度、版本演进、反例正例、参数配置均为 0）。
- Finding: P0：L33-L40 把 Hive、Parquet/ORC 与表格式混为一层，并笼统称“不支持 ACID/schema 演进”。应区分文件格式、Hive Metastore/Hive ACID 与开放表格式各自职责，再按事务、元数据和 schema 演进能力逐项比较。
- Finding: P0：L116 的“Apache 顶级（CNCF）”错误地把 Apache 与 CNCF 混在一起；应改为 Apache 软件基金会顶级项目。L117-L126 对 Delta 跨引擎、隐藏分区和生态成熟度的结论也需按当前版本核对并附官方兼容矩阵。
- Finding: P0：L56-L63、L79-L86、L101-L107、L132-L152、L160-L179 全部是裸围栏，应分别声明 `text`；当前通用 G3 为 0。
- Finding: P1：补真实 DDL/API/元数据示例，并沿 snapshot → manifest list → manifest → data/delete file 解释提交、冲突检测和读取剪枝为何成立；当前只有 ASCII 结构，A1 为 0。
- Finding: P1：新增版本与演进矩阵，列出 Iceberg format version、Delta protocol reader/writer features、Hudi table/version 以及 Spark/Flink/Trino 最低兼容版本；当前只有出生年份，不构成 A2。
- Finding: P1：新增反例/正例，例如手工日期目录分区 vs Iceberg partition transform、错误选择 Hudi COW/MOR vs 按读写比选择；当前 A3 为 0。
- Finding: P1：增加可执行参数表与调优建议，至少覆盖 target file size、compaction、小文件阈值、snapshot expiration、commit retry、metadata cleanup，并分别给出 Iceberg/Delta/Hudi 的真实配置键；当前 A4 为 0。
- Finding: P2：L145-L151、L183-L205 的厂商绑定、生态评级和“一旦选定全公司统一”等绝对建议缺少来源与组织约束。应补引用、日期和适用前提；L177-L179“COW 性能最佳”也应拆成写放大、查询延迟和更新频率等可验证指标。
- Outcome: pending

### `note/10.big-data/05-olap/01-clickhouse-vs-doris-vs-starrocks/README.md`
- Score: 12/20 (及格)
- Finding: 评分依据：通用维度 10/12（frontmatter 2、定位 2、代码块 0、回链互链 2、深度 2、可读性 2）；A 类专属 2/8（源码深度 1、版本演进 0、反例正例 0、参数配置 1）。
- Finding: P0：L80 的“每分钟 10 万+ QPS”单位自相矛盾，QPS 已是每秒查询数；L71“性能优于 Doris”、L108“StarRocks 首选”、L115“综合最强”和 L120“100+ PB 首选 ClickHouse”等结论均缺 benchmark、版本、硬件、查询集和并发模型。应补可复现实测或删除绝对排名。
- Finding: P0：L162-L174 标题称“Doris 实时数据摄入”，示例却只是 `INSERT INTO ... SELECT * FROM kafka_source`，没有定义 Kafka source，也不是完整 Stream Load/Routine Load。改为真实可执行的 Routine Load 或 Stream Load 示例，并注明 Doris 版本。
- Finding: P0：L105-L125、L195-L206 的裸围栏应声明 `text`；当前通用代码块规范为 0 分。
- Finding: P1：加入 MergeTree、Doris FE/BE、StarRocks CBO/MV rewrite 的关键源码或执行计划片段，解释分区裁剪、向量化和 JOIN 重排为什么产生差异；现有配置/DDL 只说明“是什么”，A1 只能给 1 分。
- Finding: P1：新增版本演进与兼容矩阵，说明各引擎近年 JOIN、存算分离、更新模型和物化视图能力变化；出生年份不满足 A2。
- Finding: P1：补反例/正例和参数调优：错误分区键/排序键 vs 正确设计、错误 bucket/shard 数 vs 按数据量和节点数选择，并解释 `replication_num=3`、`BUCKETS 32`、ClickHouse shard/replica 布局的适用条件；当前 A3 为 0、A4 仅 1。
- Finding: P1：L239 将 `../../../11.ai/` 标成“11 数据可视化”，链接语义错误；应链接真实可视化/报表章节，或把标签改为 AI 模块中确实消费 OLAP 的具体文章。
- Finding: P2：重做 L84-L99 的星级表，使用统一基准（如相同 TPC-H/TPC-DS 数据规模、并发、冷热缓存、节点配置）并给出来源；“俄罗斯受国际影响”“国产开源”等标签不能替代技术和运维维度。
- Outcome: pending

## 11.ai（5）

### `note/11.ai/02-technology-stack/paged-attention/README.md`
- Score: 15/20 (良好)
- Finding: P1｜G3 代码块规范=0：L22-28、L34-39 两处 ASCII 图为裸 ```，未声明语言（仅 L58 python 声明）。修复：补 ```text。
- Finding: P2｜G2 一句话定位=1：L14 定位 >80 字且含两句，末句 SOSP 论文出处应拆出。
- Finding: P2｜C4 学术/开源引用=1：L14 SOSP 论文、L59/L84 vLLM repo 仅文字提及，全无可点击 URL。
- Finding: P2｜C3 实战部署指导=1：L95 仅有 block size 调优建议，缺'X 场景用 Y'场景化部署推荐。
- Finding: P3｜L84 '46-llm-inference（餐厅叙事版待补）' 占位符残留，且链接指向 12.story/ 目录而非具体文章。
- Finding: 亮点：L45-50 性能对比表（4 引擎×3 维+实测环境）与 L90-95 反直觉 ❌/✅ 表构成 C 类'量化+纠偏'范本，值得复用。
- Outcome: pending

### `note/11.ai/03-engineering/ai-platforms/vllm-vs-ollama/04-quantization.md`
- Score: 16/20 (良好)
- Finding: [P0] C4 学术/开源引用 0 个：全文 0 个论文/GitHub 链接。GPTQ(AutoGPTQ repo, Frantar ICLR'23)、AWQ(Lin MLSys'24, github.com/mit-han-lab/llm-awq)、SmoothQuant(Xiao)、FP8(NVIDIA Hopper whitepaper) 必须加 2-4 个原始出处，否则与兄弟文件 README.md L74-79 / 06-benchmark.md 等相比严重失衡
- Finding: [P1] G3 代码块规范：L109-114 Ollama 命名约定为裸 ``` 缺语言标签（应补 ```text），属 G3 失分
- Finding: [P1] C1 量化严谨性：L20-29 量化谱表有数字但缺显存估算公式（如 模型显存 ≈ params×(Wbit/8) + KV cache ≈ 2×layers×hidden×seq×batch×(Abit/8) 推导），'约' 字过多，无变量定义
- Finding: [P2] L137 '长上下文场景：激活 KV cache 占比 60%+' 等关键数字无 benchmark 出处，应在文末加一行'数据来源' 或交叉链接 06-benchmark-data.md
- Finding: [P3] L82-90 vLLM 支持表中 SmoothQuant ✅ 来源写'NVIDIA TensorRT-LLM 后端'实为误解（vLLM 走 NVIDIA Quantization Toolkit / 自研 W8A8），与 05-distributed.md L22 风格不一致，建议补正
- Finding: [亮点] 量化谱(L20-29)→ 5 方法对比(L36-74)→ 硬件推荐表(L94-101)→ ASCII 决策树(L153-161) 四层联动、决策链路清晰；L155 '4090 24G → AWQ-INT4' 等结论可直接复制部署，工业落地价值高
- Outcome: pending

### `note/11.ai/04-architecture/intelligent-system-layers/system-three-layers.md`
- Score: 11/20 (及格)
- Finding: [P0][G1] 文件头部无 frontmatter（H1 后第 3 行只有 `← 返回 [架构设计](../README.md)`，第 5 行直接是 blockquote 引言），缺少 `` HTML 注释型 frontmatter；不满足 note/CONTRIBUTING.md 第 12 章对所有模块 README 必备 frontmatter 的硬性规范（11.ai 6/7 子文章统一使用 ``）。修复：在文件最顶部补 ``，并在 H1 后保留回链。
- Finding: [P1][G2] 一句话定位超长且偏文学化：L5 blockquote 引用主体为 88+ 字的引言（"当Optimus机器人用触觉手套精准抓取一颗螺丝，当工业产线在99.99%的任务分配成功率下自主调度——背后是一场静默却深刻的技术架构革命。本文深度解析支撑下一代智能体的分层架构设计..."），远超 G2 定义的 ≤80 字上限；且句式宣传化（"技术架构革命""底层逻辑"），缺少"是什么/解决什么问题/适用对象"标准三段式。修复：在 H1 之后、blockquote 之前插入一句 ≤80 字的硬定位，例如：「智能系统三层架构（感知层 / 认知层 / 决策层）的分层设计原则、各层关键技术与典型工业场景选型参考。」
- Finding: [P1][C4] 学术/开源引用严重缺失：全文提及"北航仿生昆虫机器人""哈佛 OCTO-Sensor""华为时序同步模块""NVIDIA Jetson Orin""大疆 Matrice 350 RTK""RainyGS""MAK VR-Forces""加州大学超级图灵 AI 芯片""Gemini 2.0"等 9+ 实体，但 0 个带论文 arXiv 链接 / 官方 GitHub / 厂商产品页链接；C4 评分要求"有论文链接或开源项目引用"，该文属"提及但无链接"。修复：在每节首次提及实体处加链接引用（例如 L26 的 OCTO-Sensor 加 Harvard 实验室主页或 arXiv 链接，L106 的 Gemini 2.0 加 Google DeepMind 官方 blog 链接）。
- Finding: [P2][G4] 互链不足：除第 3 行一条 `../README.md` 单向回链外，正文无任何指向 note 其他章节的链接（如感知层 → `11.ai/03-foundation/multimodal-fusion.md`、决策层 → `11.ai/05-agent/multi-agent-collaboration.md`、强化学习 → `13.split-hairs/...`），G4 要求"≥2 个旧章节互链"未满足。修复：在 §2.4（L49）后加 ⤴ 链回 `11.ai/03-foundation/multimodal-fusion/`；在 §4.3（MCTS, L88）后加 ⤴ 链回 `13.split-hairs/mcts-vs-q-learning/`。
- Finding: [P2][C3] 实战部署指导薄弱：虽有"图像生成：NAR 快速勾勒轮廓 → AR 精细渲染纹理"（L68）这类 X-场景-Y-方案，但未给硬件选型表、依赖环境、推荐 SDK/版本或落地 checklist，C3 要求"场景化推荐"实为泛泛建议。修复：在 §3.3 末新增「部署 checklist」表格：场景 / 推荐模型 / 最低硬件 / 框架 / 注意事项，例如行"医疗影像三维重建 | NAR 半自回归 | A100 80G×2 | MONAI 1.4+"。
- Finding: [亮点] 分层叙事结构是 11.ai 中少见的"系统级"视角：H2 一/二/三/四/五五段中文序数章节编号全部一致（§1–§5 + 结语 §6），用采集方式表（L32-36）替代纯文字对比，且每节统一 3 个子小节形成节奏。L17、L74、L112 的过渡句（"传感器升级无需重构决策逻辑""Agent 智能中枢""架构即竞争力"）将三层逻辑串成一根主线，避免了 11.ai 同类文章的"碎片化案例堆砌"反模式。
- Outcome: pending

### `note/11.ai/05-applications/case-studies/09-glean-enterprise-search/README.md`
- Score: 13/20 (及格)
- Finding: [P0] C4 学术/开源引用严重缺失：全文仅 3 个外部链接（glean.com / 搜狐 / 知乎）作为背景参考，但 C 类规则要求"论文链接或开源项目引用"——应补充 Glean 技术博客（如 glean.com/blog）、白皮书、公开论文或工程团队发表的索引/权限建模文章，当前 1/2 分都勉强。 file:line 证据：L16-L18 仅 3 行 blockquote 链接，无论文/开源引用。
- Finding: [P0] C1 量化严谨性不足：C 类要求"有公式/数字 + 变量定义清晰"。文中 L87 提到"E 轮融资估值约 45 亿美元"是唯一具体数字，但 RAG 系统本身的关键指标（连接器数量精度、检索延迟、权限重算 SLA"分钟级"、答案生成 P50/P99 延迟、召回率等）全无量化；变量定义（什么是"viewer token"、什么是"企业知识图谱"）也缺失。
- Finding: [P1] C2 架构对比表缺失：C 类要求"多维对比表（≥3 维度）"。文中完全没有表格将 Glean 与同类企业搜索（Microsoft Copilot for Search、Notion AI Search、Hebbia、Glean 之外竞品如 Algolia Enterprise / Sinequa）在"连接器数量 / 权限模型 / 部署方式 / 答案形态 / 延迟 / 价格"等维度对比。
- Finding: [P1] G4 互链不足：L95 只有 1 条 footer 回链到 ../README.md，但 G 类规则要求"≥2 个旧章节互链"。文章全文未互链到 11.ai 下其它模块（如 RAG 基础概念、向量检索、Agent 等章节），形成孤岛。
- Finding: [P2] C3 实战部署指导薄弱：C 类要求"场景化推荐（X 场景用 Y）"。L77-L85 给出"启发"，但全是泛泛建议（"别再纠结 embedding"），没有"什么场景选 Glean / 什么场景自建 / 什么场景用竞品"的可执行决策树。
- Finding: [亮点] 文章切口精准、价值观独到：L14 的"一句话总结"（连接器与权限才是护城河）和 L45 的"100+ 团队年投入到连接器上的工程债"金句具有强烈观点性，比一般科普文章更接近行业洞察，符合 case-studies 模块的差异化定位。
- Outcome: pending

### `note/11.ai/07-research/efficiency/README.md`
- Score: 16/20 (良好)
- Finding: [P0] G3 代码块规范严重违规 — §2.3 选型决策树(L56-65) 与 §5.2 Draft+Verify 流程图(L148-161) 两处 ``` 块均未声明语言,导致无法语法高亮且 markdown-link-check 视为可疑。修复:分别改为 ```text 和 ```text(或 mermaid graph),保持纯文本可读性。
- Finding: [P0] 格式残留 — L16-17 出现连续两个 --- 分隔符(冗余空行+重复水平线),明显是某次编辑遗留。修复:删除其中一条 ---,只保留一条水平线分隔引言与正文。
- Finding: [P1] C4 学术/开源引用全部无链接 — §2.2/§3.3/§6.2 提到的 GPTQ、AWQ、QLoRA、Wanda(论文)、SliceGPT、LLM-Pruner、DARE、TIES、SLERP、HuggingFace Open LLM Leaderboard 均为裸文本,读者无法溯源验证。修复:每个术语首次出现时附 arxiv/github 链接(如 Wanda → arxiv:2306.11695, TIES → arxiv:2306.01708)。
- Finding: [P1] 时间硬编码 — L14 写死 "2024-2026 年主流",当前已是 2026-07-19,半年后该表述就会过期。修复:改为 "近年(2024 起)主流" 并加一句 "快照截至 2026-07",或干脆删掉年份段。
- Finding: [P2] C1 量化严谨性偏弱 — 全文出现大量数字(50%/75% 显存节省、2-3x 加速、100ms vs 10ms),但缺少公式化推导(如 显存比 = bit_old/bit_new、Speedup ≈ α·k/(1+k·c),其中 α 为接受率、k 为 draft 长度、c 为验证开销)。修复:在 §2.1 加 1 行"显存压缩比 = bit_width_old / bit_width_new" 推导,在 §5.2 加推测解码加速比公式,既补 C1 也提升权威感。
- Finding: [亮点] §七 全景对比表(L204-212)是全篇最强资产 — 8 行 × 6 列(压缩比/速度/精度/训练/阶段)覆盖所有主流技术,且 §十 实战场景表(L248-256)与之互相呼应形成"对比→选型"闭环;此外 §八 双时长面试话术(30s/90s) + §九 6 道高频面试题表让"深度文档"兼具面试突击价值,是 11.ai/07-research 模块少见的"技术深度 + 实战可用性"双优范例。
- Outcome: pending

## 12.story（3）

### `note/12.story/08-qa-testing-strategy.md`
- Score: 23/24 (优秀)
- Finding: P2 | 延伸阅读区出现重复链接：L515 与 L518 两次指向 `./19-realtime-eventdriven.md`（一个叫"传菜窗口的智慧"，一个叫"厨房实况直播"），L505 与 L521 两次指向 `./07-from-chef-to-ceo.md`（一个叫"从厨师到 CEO"，一个叫"菜谱标准化之路"）—— 同文件重复 2 次会污染 cheatsheet 自动生成，建议二选一或拆分 slug 命名。
- Finding: P2 | 跨章节衔接（L532-535）只列出 4 个外部链接，密度低于延伸阅读（L500-528 列 28 个），且 L535 `./30-agent-harness.md` 文件名与实际目录一致（30-agent-harness.md 存在），但文中描述"续集八"应与 STORY-FORMAT-SPEC 对应校对，建议补 1-2 个正传 5/6/9 的回链以提升章节串接。
- Finding: P3 | 第八章 8.5-8.6 中代码示例（第 373-414 行）使用 `assert response.tool_called == "query_order"` 等确定性断言，与本节开篇论点"传统断言对 AI 失效"形成自相矛盾 —— 建议把断言改为"包含"/"顺序匹配"以保持论点一致，或加注说明"这是入门示例，生产需配合黄金集"。
- Finding: P3 | 文末 L543"答案是测试金字塔 + 测试左移 + 测试右移" 心法句只提传统三项，遗漏第八章主推的"AI 测试"维度，与全文 60% 篇幅讲 AI 测试的篇幅不匹配，建议改为"金字塔 + 左移右移 + AI 测试三层闭环"。
- Finding: 亮点 | 第八章（8.1-8.8）把传统测试 vs AI 测试、4 大测试维度、黄金集 4 特征、LLM-as-Judge 5 大陷阱、Prompt 回归 5 指标、Agent 3 层测试、AI 测试 5 大反模式、5 级成熟度模型串成完整方法论 —— 是 note 中少有的"测试金字塔 → AI 测试"双时代对照文章，且每节都配阿明餐厅场景，技术深度与叙事节奏兼顾。
- Outcome: pending

### `note/12.story/11-ai-learning-paradox.md`
- Score: 23/24 (优秀)
- Finding: G1=2 frontmatter完整(story块齐全)
- Finding: G2=2 H1后定位段清晰
- Finding: G3=2 所有代码块声明语言
- Finding: G4=2 28个延伸阅读+回链
- Finding: G5=2 6章+5大能力表+Mermaid
- Finding: G6=2 表格/Mermaid/代码比例佳
- Finding: D1=2 阿明+小周+阿强贯穿
- Finding: D2=2 认知卸载=GPS/刻意练习=切土豆丝/AI审查=42度
- Finding: D3=2 第一~六章+5.1子节一致
- Finding: D4=2 起承转合完整
- Finding: D5=2 系列定位格式正确
- Finding: D6=1 Mermaid核心总结图节点过密
- Finding: P2: 264-282行Mermaid图拆为问题链+解决链2图
- Finding: P2: 删除./19-realtime-eventdriven.md重复链
- Outcome: pending

### `note/12.story/34b-ai-token-cost-optimization.md`
- Score: 22/24 (优秀)
- Finding: G1=2 story frontmatter+续集十二下
- Finding: G2=2 H1后定位段清晰
- Finding: G3=2 所有代码块声明语言
- Finding: G4=2 11个延伸阅读+回链+跨章节衔接
- Finding: G5=2 6章+ROI公式+48万→18万数字
- Finding: G6=2 结构清晰
- Finding: D1=2 阿明省钱大作战贯穿5/6/7/9/10章
- Finding: D2=2 路由=凉菜用学徒/缓存=中央厨房半成品/训练=请米其林大厨
- Finding: D3=2 第五~十章+5.1一致规范
- Finding: D4=2 起承转合+ROI收尾
- Finding: D5=2 系列定位正确为续集十二下
- Finding: D6=1 Mermaid核心总结图16节点过密
- Finding: P2: 611-645行Mermaid总图拆为监控-优化和ROI-组织2图
- Finding: P2: H1写36b但filename写34b编号不一致统一
- Outcome: pending

## 13.split-hairs（11）

### `note/13.split-hairs/01.java/parent-child-thread/README.md`
- Score: 24/24 (优秀)
- Finding: G1=2 question frontmatter完整
- Finding: G2=2 H1+引言段清晰
- Finding: G3=2 java/xml/bash全部声明
- Finding: G4=2 3个兄弟链+主模块链+回链
- Finding: G5=2 9章最完整结构
- Finding: G6=2 表格/代码/段落比例合适
- Finding: E1=2 引子审计日志userId全是anonymous生产事故型
- Finding: E2=2 第七章4大陷阱+真相格式
- Finding: E3=2 第八章90秒完整版话术
- Finding: E4=2 InheritableThreadLocal限制1-3+CompletableFuture局限
- Finding: E5=2 双向链threadlocal+concurrency+01.java/concurrency
- Finding: E6=2 difficulty三颗星+frequency高频
- Finding: P3: 296行日期2026-06-28校对git log日期
- Outcome: pending

### `note/13.split-hairs/03.database/README.md`
- Score: 22/24 (优秀)
- Finding: G1=2 module+question双frontmatter
- Finding: G2=2 H1+摘要定位清晰26篇+三大方向
- Finding: G3=2 mermaid+text声明齐全
- Finding: G4=2 回链+主模块链+04.system-design链
- Finding: G5=2 26题清单+4大概念树+3对比表+Mermaid
- Finding: G6=2 表格+Mermaid+ASCII树混合
- Finding: E1=1 目录型无传统生产事故引子
- Finding: E2=1 目录页无陷阱专题
- Finding: E3=1 目录页无话术专题
- Finding: E4=2 InnoDB vs MyISAM对比+RDBMS vs NoSQL对比
- Finding: E5=2 双向链03.database/+04.system-design/
- Finding: E6=2 每题difficulty+核心问题描述
- Finding: P2: 移除module块仅保留question块
- Finding: P3: 加Redis 6题vs MySQL 12题现状说明
- Outcome: pending

### `note/13.split-hairs/03.database/mysql-time-types/README.md`
- Score: 23/24 (优秀)
- Finding: G1=2 question frontmatter完整
- Finding: G2=2 H1+引子段清晰5种类型+选错3坑
- Finding: G3=2 sql/java代码块声明
- Finding: G4=2 回链+3相关主题链
- Finding: G5=2 6章原理+代码+5陷阱+5实践+3面试话术
- Finding: G6=2 7张表+5段代码+决策树可视化
- Finding: E1=2 引子存个时间选哪个反直觉代码型
- Finding: E2=2 第三章5大陷阱+错误/正确对比
- Finding: E3=2 第五章3套完整话术
- Finding: E4=2 2038/时区/索引失效/零日期/DST有反例正例
- Finding: E5=2 双向链MySQL/索引优化/Java日期/事务隔离
- Finding: E6=2 difficulty两星+frequency中频
- Finding: P2: 188-200行决策树加text语言标识
- Finding: P3: 244-256行DELIMITER加JDBC不需要注释
- Outcome: pending

### `note/13.split-hairs/03.database/mysql-what-lock/README.md`
- Score: 23/24 (优秀)
- Finding: G1=2 question frontmatter完整
- Finding: G2=2 H1+引子段清晰UPDATE拖垮系统
- Finding: G3=2 sql/java全部声明
- Finding: G4=2 回链+3相关章节链
- Finding: G5=2 5大场景+5陷阱+5实践+面试话术
- Finding: G6=2 6实验场景+4对比表+监控SQL
- Finding: E1=2 引子UPDATE拖垮整个系统生产事故型
- Finding: E2=2 第三章5大陷阱+正反对比
- Finding: E3=2 第五章完整话术+加分项
- Finding: E4=2 隐式类型转换/事务过大/死锁有反例正例
- Finding: E5=2 双向链MySQL事务/B+树/隔离级别
- Finding: E6=2 difficulty三星+frequency中频
- Finding: P2: 192行pt-heartbeat加GitHub链接
- Finding: P3: 交叉引用链风格统一为../xxx/README.md
- Outcome: pending

### `note/13.split-hairs/04.system-design/README.md`
- Score: 15/24 (及格)
- Finding: G2 一句话定位 >80 字，建议拆为定位句+覆盖清单
- Finding: L104 `[05.security](../05.security)` 缺尾 `/README.md`，需 link-check
- Finding: E1-E4 为导航页结构性 N/A（无引子/陷阱/话术/代码），非真实内容缺陷
- Finding: 正文声称『19 篇』需用 find 实时校对清单条目数
- Outcome: pending

### `note/13.split-hairs/04.system-design/url-shortener/README.md`
- Score: 18/24 (良好)
- Finding: P1: footer `← 返回`(README.md) 自指向本文件，应改为 `../README.md`
- Finding: E2: 用『5 大反模式』表替代了 `### 陷阱 N：`+`**真相**：` 格式，建议至少一处改为标准陷阱格式
- Finding: E3: 仅 30 秒话术，补 90 秒版可满分
- Finding: E4: 代码多为正例，缺 ❌/✅ 配对（如 301 vs 302 可给错误示例）
- Finding: G3: 系统流程图/架构图为裸 ```` ``` ````，标注 `text` 语言
- Outcome: pending

### `note/13.split-hairs/05.security/README.md`
- Score: 15/24 (及格)
- Finding: P1: footer `../../README.md` 从 05.security/ 上跳两级到 note/，应为 `../README.md`（split-hairs 索引）
- Finding: L55 `../../04.system-design/04.system-design/` 路径重复段可疑，需校对
- Finding: G2 定位句 >80 字，建议精简
- Finding: E1-E4 为导航页结构性 N/A
- Outcome: pending

### `note/13.split-hairs/09.front-end/playwright-vs-selenium/README.md`
- Score: 21/24 (优秀)
- Finding: 最佳篇：E2 严格符合 `### 陷阱 N：`+`**真相**：` 格式，代码对比带 ❌ 标注
- Finding: P1: footer `← 返回`(README.md) 自指向本文件，应改为 `../README.md`
- Finding: E3: 话术仅一版，建议拆 30 秒/90 秒双版本
- Finding: G3: Trace Viewer 特性列表为裸 ```` ``` ````，标 `text`
- Outcome: pending

### `note/13.split-hairs/09.front-end/xss-csrf/README.md`
- Score: 19/24 (良好)
- Finding: E2=0: 全文无 `### 陷阱 N：`+`**真相**：` 章节（有引子故不触发降级，但需补陷阱段）
- Finding: P1: footer `← 返回`(README.md) 自指向本文件，应改为 `../README.md`
- Finding: E3: 仅 30 秒话术，补 90 秒版
- Finding: E4: 有『不安全代码』但缺 ❌/✅ 配对示例
- Finding: 与 05.security/xss-csrf-csp/ 主题重叠，建议互链去重
- Outcome: pending

### `note/13.split-hairs/11.ai/README.md`
- Score: 14/24 (及格)
- Finding: P0 数字打架: H1『18 题』/ L27『38 题』/ L40『20 题=9+11』三处计数矛盾，须 find 校对后统一
- Finding: L53 与 L57 `agent-performance-evaluation/` 重复列两次，去重
- Finding: G6 因计数冲突降至 1（可信度受损）
- Finding: G2 定位句 >80 字
- Finding: E1-E4 为导航页结构性 N/A
- Outcome: pending

### `note/13.split-hairs/11.ai/llm-alignment/README.md`
- Score: 23/24 (优秀)
- Finding: frontmatter 完整（id/difficulty/frequency/scenario_type/tags 全齐），一行定位+双向回链到主模块深度专题，5 大题陷阱/话术/兄弟章节齐全（95.8%）
- Finding: P3 修复建议：餐厅叙事链接 [12.story 对齐故事]（待补）为占位符，应删除或补真实链接
- Outcome: pending

## 14.project-management（4）

### `note/14.project-management/interviewing-cross-disciplinary/README.md`
- Score: 16/20 (良好)
- Finding: P1 | line 14、218-220、241-249 多处定性结论（"学习斜率""高潜力""领悟力"）无任何量化数据支撑，全文找不到一个百分比/成功率/样本量/统计来源，"学习斜率明显高于同期其他候选人"（line 215）属于无证据断言；建议：补充 1-2 个可核实数据点（如"腾讯 2024 校招跨专业候选人占比 X%""降维版问题在培训班背景候选人中通过率提升 X%"）或改用"约""通常"等限定词。
- Finding: P2 | 整文档（共 286 行）适用性争议：B 类"工具实践规则"的 B1（安装步骤可执行）、B2（配置示例）维度与本文性质（面试评估方法论）完全无关，B1/B2 严格给 0 分实质是模块归类信号；建议：要么将本类内容明确归到新模块（如 note/15.hr-recruiting 或在 14.pm 下加 interview 子模块说明），要么在 leaf-quality 规则中为"评估方法论/方法库"类内容加 D/H 类旁支规则。
- Finding: P3 | line 181-188 原专业映射表仅覆盖 6 类（数学/金融/外语/心理学/传统工科/文科），遗漏医学、生物、法律、艺术、体育、音乐等典型跨专业方向，且"金融 IT/Fintech"等团队方向重复出现但未给团队识别方法；建议：扩到 10+ 类，并加一列"面试官如何验证该优势是否真实"（如"让数学背景候选人现场推导一个业务公式"）。
- Finding: P3 | line 277-281 互链密度足够但缺 frontmatter 锚点校验：链接指向的 conways-law-team-topologies/team-sizing-3x-buffer/ai-pm-dora-space/12.story/07 五个目标均无 hash 锚点，读者点击后需自行定位对应章节；建议：为每个互链加章节锚点（如 ../conways-law-team-topologies/README.md#互补性）以提升跳转体验。
- Finding: 亮点 | line 35-37、71-97 "降维版 + 场景版"双题库设计是本文最大差异化亮点：针对培训班/自学 vs 零基础跨行两类候选人给不同门槛的问题模板，避免一刀切用八股文误杀，落地性极强；"深挖一个点 3-4 层"（line 223、140）的反伪匹配追问法也可作为后续面试方法论文档复用模板。
- Outcome: pending

### `note/14.project-management/outsourcing-pitfalls/README.md`
- Score: 15/20 (良好)
- Finding: P0 B4=0：全文无外包模式对比表（固定价 vs T&M vs 敏捷外包），缺供应商选型矩阵；在 §一 后新增选型对比表可解决
- Finding: P1 B2=1：L130-140 合同 8 条表只有关键点短词，缺可复制的条款原文/参数注释，建议每行加『条款原文模板』列
- Finding: P2 关键数字缺来源：L44『30-50%』、L45『15-20%』、L78『1.5 万月薪』、L106『99.9% SLA』无 benchmark 脚注，建议标注『经验值』或加出处
- Finding: P3 章节编号风格不统一：§二用『1./2./3.』，§五用『### 陷阱 1』，建议统一为『### 2.1 / 2.2 / 2.3』或『### 5.1 陷阱 1』
- Finding: 亮点：闭环式实战结构（故事→TL;DR→5 成本→8 条款→验收模板→陷阱→话术→统计页），7 大章节形成识别-谈判-验收-面试完整闭环，是项目管理类文章标杆模板
- Outcome: pending

### `note/14.project-management/scripts/README.md`
- Score: 14/20 (良好)
- Finding: [P1] B4 对比/选型 = 0 分：全文未提及任何同类工具对比（如 sed/awk/grep/jq 批量替换 frontmatter、Markdown lint 工具如 markdownlint-cli 对比），也没有"为什么用 Python 而不是 Shell"的选型说明。位置：第 1-62 行整篇。修复：加一节"工具选型对比"，至少 1 个对比表（如 vs markdownlint-cli2 / vs 纯 sed 脚本）。
- Finding: [P2] G4 回链+互链 = 1 分：仅 L62 一条返回 README 的 footer 回链，L38 单向链到 CONTRIBUTING.md，未与 14.project-management 下任何具体 leaf README（如 README.md 总目录、某个具体模块子文章）互链。按规则需 ≥2 个旧章节互链才满分。修复：在 scripts/README.md 中加 1-2 处指向上层 README 或兄弟脚本（如 ../../README.md、../../CONTRIBUTING.md 的 #scripts 锚）。
- Finding: [P2] B2 配置示例 = 1 分：脚本自身虽声明无外部依赖（L59），但 validate.py 校验失败时的输出样例、insert-frontmatter.py dry-run 输出样例均未展示，读者无法预知运行结果是否符合预期。位置：L24-30、L49-51 两段调用方法。修复：每个脚本补一段 sample output（成功/失败两种 case）。
- Finding: [P3] G5 内容深度 = 1 分：两个脚本各覆盖了"用途/调用/场景/校验项" 2-3 层，但缺少实战案例（如：对一个真实的旧文章跑 insert-frontmatter.py 的 before/after diff 示例，或 validate.py 在 issue 场景下的修复案例）。位置：L18-51。修复：补一节"实战示例"，附真实 diff 或终端输出片段。
- Finding: [P3] 第 57-61 行"维护约定"章节仅 3 行 bullet，缺测试方法、回滚策略（git revert 操作指引）、变更日志链接（C changelog / CHANGELOG.md 引用）。位置：L57-61。修复：扩展该节为 8-10 行，明确"重大变更"判定标准与流程。
- Finding: [亮点] 文章结构层次清晰：frontmatter 完整（L1-8，含 parent/slug/type/category/summary 五字段）、G2 定位精准（L12 仅 49 字）、G3 所有代码块都声明 bash 语言、双脚本职责分明（insert-frontmatter 写入 vs validate 校验），是 B 类工具文档的范本结构。
- Outcome: pending

### `note/14.project-management/team-sizing-3x-buffer/README.md`
- Score: 15/20 (良好)
- Finding: [P1] 数字自相矛盾且无出处：line 137-145 表格「净速度 AI Coding = 3.6x」，但紧接的 line 145 正文却说「净提升 ~2 倍，绝不是 3 倍」——同一节结论打架；另 line 62「阿里 2-8-2」、line 158「渗透率 80%/留存 30%」均无 benchmark/来源链接（B4/G5 数据可信度受损，需补出处或统一口径）。
- Finding: [P1] 互链文本与目标编号不符：line 158「[12.story/45](../../12.story/43-ai-productivity-paradox.md)」锚文本写「45」，实际指向 43-ai-productivity-paradox.md（line 252 又正确写作 43），编号错误会误导读者，应改为 43。
- Finding: [P2] frontmatter 类型标记不合规：line 2 使用自定义 `pm:` 键，而 CLAUDE.md 规定模块 README 必须用 ``（module/question/story 三选一），字段虽全但 type 不正确，G1 因此仅得 1 分。
- Finding: [P2] 一句话定位超长：line 11 的 `>` 定位块远超 80 字（含「拍脑袋排 2 周…黄金比例 + 排期 3 倍缓冲原则，给出可落地的实战框架」），不符合 G2「H1 后 ≤80 字清晰定位」，建议精简为一句。
- Finding: [P3] B 类专属维度先天错配：本文为方法论/决策类内容，全篇无可复制安装命令（B1=0）、无带注释的完整配置文件示例（B2 仅靠 line 103-119 排期模板勉强得 1 分），B 类「工具实践」规则对纯方法论文压分，可考虑在 skill 决策表中为 14.project-management 的方法论文另设规则或标注豁免。
- Finding: [亮点] 实战性与对比密度突出：line 204-217「登录模块」故事点拆解→中位数估时→×2.5 得 17.5 天的完整算例可直接照搬，配合「5 大反例」「6 大坑」「AI vs 传统」多张带结论对比表，B3（使用场景）与 B4（对比选型）均达满分，是本篇最大价值点。
- Outcome: pending
