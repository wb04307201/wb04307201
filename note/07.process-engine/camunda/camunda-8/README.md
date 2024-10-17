# Camunda 8

Camunda Platform 8于2022年4月12日发布，其核心引擎就是Zeebe，Camunda公司还有传统的开源工作流引擎Camunda Platform 7，是唯一一家同时开源2种工作流引擎的公司。

![img.png](img.png)

在国外自从Camunda BPM 7.0.0推出后，很多客户陆续从Activit迁移到Camunda BPM。

**Camunda Platform 7与8的异同**：  
![img_1.png](img_1.png)

**Camunda Platform 8 产品**：  
![img_2.png](img_2.png)

**Camunda Platform 8开源**：  
![img_3.png](img_3.png)
- **绿色**：开源许可证Open source license
- **绿色条纹**：源可用许可证Source-available license
- **蓝色**：免费用于非生产用途,投入生产需要通过企业订阅
- **橙色**：仅在Camunda8 - SaaS中可用

**使用源代码可用软件的生产路径**：  
![img_4.png](img_4.png)

1. **任务列表**：需要基于使用订阅 Zeebe 的消费者来实现自己的任务管理解决方案，构建自己的持久化以允许任务查询。
2. **流程操作**：构建自己的expoter以将其推送到一些方便的数据存储组件，并进行即时筛选或预处理数据，并使用现有的 Zeebe API去操作流程实例。
3. **流程优化**：通过自研的expoter将数据推送到现有的通用 BI（商业智能）、DWH（数据仓库）或数据湖，通过流程数据分析优化流程。




