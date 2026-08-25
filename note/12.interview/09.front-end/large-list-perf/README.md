<!--
question:
  id: 09.front-end-large-list-perf
  topic: 09.front-end
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 性能调优
  tags: [09.front-end, vue, performance, list]
-->

# Vue 大列表性能调优

> 一句话：**Vue 3 Proxy 懒代理不递归 + 嵌套属性写入会强制构建整条路径 + 1 万条 × N 层 = 数万次 Proxy/帧；用 shallowRef + Map 索引 + 虚拟滚动叠加可从 2 秒压到 10 毫秒。**

---

## 引子：面试官为什么爱问这道题

```vue
<!-- 看似无害的代码 -->
<script setup>
const data = ref({
  list: Array.from({length: 10000}, (_, i) => ({
    id: i, name: `n-${i}`,
    detail: { score: i, meta: { updatedAt: Date.now() }}
  }))
});
const idx = ref(5000);

function update() {
  data.value.list[idx.value].detail.meta.updatedAt = Date.now();
}
</script>
<template>
  <button @click="update">update</button>
  <HeavyRow v-for="row in data.list" :key="row.id" :data="row" />
</template>
```

> 用户点击按钮，只修改其中一条深层属性，**页面却卡 2 秒**。为什么？怎么排查？怎么优化？

这是 Vue 3 实际项目（中后台表格 / SKU 树 / 组织架构 / 长列表筛选）**最高频**的卡顿场景。面试考点覆盖 3 个深度：
- 响应式原理（Proxy / trigger / lazy）
- 工程能力（性能定位工具链）
- 实战经验（具体 API 选型）

---

## 30s 速答

> **卡 2 秒的两个根因**：
> 1. **响应式层**：Vue 3 Proxy 是懒代理（首次访问才递归），但 `data.list[5000].detail.meta.updatedAt = ...` 沿路径写入时，**整条链 detail / meta 被强制同步代理**，1 次操作触发**整链 trigger**
> 2. **渲染层**：1 万条数据全部走 diff，即使只改 1 条；默认 `:key="idx"` 让中间任何变动都全列表 patch
>
> **2 分钟速解套路**：Devtools 看 trigger 计数 → 火焰图定位 Scripting/Rendering → shallowRef 阻断深层 + Map 索引 O(1) 定位 + 整体替换触发响应 + 虚拟滚动限制 DOM

---

## 90s 完整版

### A. 核心矛盾（3 个）

| # | 矛盾 | 根因 |
|---|------|------|
| 1 | 单条修改 vs 全表 diff | `<HeavyRow v-for>` 不带 v-memo → 整列表 patch（除非 key 命中） |
| 2 | 深层写入 vs Proxy 懒代理 | 沿路径写入强制构建整链响应式（即便未访问过父级也重建） |
| 3 | 1 万条数据 vs DOM 上限 | 浏览器单帧渲染 ~2500 DOM 节点已吃力，1 万必崩 |

### B. 4 步排查法（按顺序执行）

```text
[1] Devtools → Performance → 录制 → 复现卡顿 → 停止
    看 Component render 平均耗时 (>16ms 即掉帧)
[2] Chrome Performance → 火焰图
    长黄色 = JS 慢 (JSON.parse / Proxy 构建)
    长紫色 = Layout / Style (无效 patch 触发 reflow)
[3] Vue 源码埋点 trigger 计数（生产构建下）
    1 次点击 trigger 计数 > 100 → 必有响应式滥用
[4] 切 production + 隐身窗口重测
    排除 dev 模式 Proxy 断言 + 浏览器扩展
```

### C. 4 层优化武器

| 层 | 武器 | 适用 |
|----|------|------|
| **响应式层** | `shallowRef` + `markRaw` | 大对象只整体替换，不递归代理内部 |
| | `watch(getter, ...)` 不用 `deep:true` | 避免遍历整树 |
| **数据层** | 扁平化 + `Map<id, index>` | O(n) → O(1) 定位 |
| | `Object.freeze` 大常量 + V8 优化 | 字典表、配置项 |
| | Immer 结构共享 | 嵌套对象局部更新 |
| **渲染层** | `:key="item.id"` | 精准 diff |
| | `v-memo="[item.id, item.sel]"` | 跳过未变子树 |
| | `<RecycleScroller>` 虚拟滚动 | DOM 上限问题彻底解决 |

### D. 关键代码片段

```ts
// ✅ shallowRef + Map + 整体替换
const data = shallowRef({ list: [...], index: new Map<number, number>() });

function buildIndex() {
  const idx = new Map<number, number>();
  data.value.list.forEach((row, i) => idx.set(row.id, i));
  data.value = { list: data.value.list, index: idx };
}

function update(id: number, newVal: any) {
  const pos = data.value.index.get(id)!;
  const list = data.value.list;
  data.value = {
    list: [
      ...list.slice(0, pos),
      { ...list[pos], detail: { ...list[pos].detail, meta: {
          ...list[pos].detail.meta, updatedAt: newVal
      }}},
      ...list.slice(pos + 1),
    ],
    index: data.value.index,
  };
}
```

---

## 5 大反模式速查（面试必踩坑）

| ❌ 反模式 | 后果 | ✅ 修正 |
|----------|------|--------|
| `reactive(hugeObject)` 包整个大对象 | 数万次 Proxy 包装 | `shallowRef` + `markRaw` |
| `watch(state, ..., { deep: true })` | 每次更新遍历整树 | watch 具体 getter |
| `:key="index"` | 删除一行后续全 re-render | `:key="item.id"` |
| `JSON.parse(JSON.stringify(arr))` 深拷贝 | 阻塞主线程 100ms+ | Immer 结构共享 |
| `arr.find(x => x.id === id)` 频繁定位 | O(n)，叠加多次 | `Map<id, index>` O(1) |

---

## 量化性能基准（必背）

| 方案 | 修改耗时 | 全组件 re-render | 首屏 |
|------|---------|-----------------|------|
| 默认 `ref` + `:key=index` | ~1800ms | **10000 / 次** | 2500ms |
| `ref` + `:key=id` + Immer | ~250ms | 1 / 次（命中 key）| 2500ms |
| `shallowRef` + Map + 整体替换 | ~40ms | 1 / 次 | 2800ms（构建索引） |
| `shallowRef` + Map + 虚拟滚动 | ~10ms | 视口 ~30 节点 | ~150ms |
| **四方案叠加** | **~10ms** | **~30 节点** | **~150ms** |

> 经验：**单方案 10x，叠加 200x**。

---

## 📚 参考来源

- 深度实战：[`note/05.frontend/03-frameworks/vue/large-list-perf/README.md`](../../../05.frontend/03-frameworks/vue/large-list-perf/README.md)（456 行，含排查方法集 / 完整代码示例 / 性能基准）
- 响应式原理：[`vue-reactivity/`](../vue-reactivity/README.md)（深挖 Proxy / 懒代理 / Dep-Observer-Watcher）

---

## 交叉引用

- [`vue-reactivity/`](../vue-reactivity/README.md) — Vue 响应式原理（同框架原理篇）
- [`../../05.frontend/03-frameworks/vue/large-list-perf/README.md`](../../../05.frontend/03-frameworks/vue/large-list-perf/README.md) — 深度实战（含 4 层优化 / 实战案例 / 完整量化基准）
- [`../../05.frontend/03-frameworks/vue/README.md`](../../../05.frontend/03-frameworks/vue/README.md) — Vue 3.4+ 总览

---

← [返回 前端咬文嚼字](../README.md)
