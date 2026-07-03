<!--
module:
  parent: front-end
  slug: front-end/mini-program
  type: article
  category: 主模块子文章
  summary: 小程序开发
-->

# 小程序开发

> 一句话定位：**Taro 4 / Uni-app x —— 一套源码，多端发布到微信 / 支付宝 / 抖音 / H5**

小程序是中国互联网的独特产物 —— 微信 13 亿月活、支付宝 8 亿、抖音 7 亿，每个平台都是独立的流量入口。跨端框架让"一次开发、多端发布"成为可能。

---
---

## 1. 主流小程序平台

| 平台 | 月活 | 技术栈 | 开发工具 |
|------|------|--------|---------|
| **微信小程序** | 13 亿+ | WXML / WXSS / JS | 微信开发者工具 |
| **支付宝小程序** | 8 亿+ | AXML / ACSS / JS | 小程序开发者工具 |
| **抖音小程序** | 7 亿+ | TTML / TTSS / JS | 抖音开发者工具 |
| **百度小程序** | 6 亿+ | Swan / CSS / JS | 百度开发者工具 |
| **QQ 小程序** | 8 亿+ | 类微信 | QQ 开发者工具 |
| **快手小程序** | 5 亿+ | 类微信 | 快手开发者工具 |

---

## 2. 跨端框架对比（2026）

| 框架 | 技术栈 | 多端支持 | 2026 状态 |
|------|--------|---------|----------|
| **Taro 4** | React | 微信 / 支付宝 / 抖音 / 百度 / H5 / RN | ⭐⭐⭐⭐⭐ React 团队首选 |
| **Uni-app x** | Vue | 微信 / 支付宝 / 抖音 / H5 / App | ⭐⭐⭐⭐⭐ Vue 团队首选 |
| **Remax** | React | 微信为主 | ⭐⭐ 维护放缓 |
| **原生开发** | 各平台 DSL | 单平台 | ⭐⭐⭐⭐ 性能最优 |

### Taro 4（React 首选）

```tsx
// Taro 4 + React
import { View, Text, Button } from '@tarojs/components'
import { useLoad } from '@tarojs/taro'

export default function Index() {
  useLoad(() => console.log('Page loaded.'))
  
  return (
    <View className="index">
      <Text>Hello, Taro!</Text>
      <Button type="primary" onClick={() => {}}>Click</Button>
    </View>
  )
}
```

```bash
# 创建 Taro 项目
npx @tarojs/cli init myapp

# 编译到微信小程序
npm run dev:weapp

# 编译到 H5
npm run dev:h5

# 编译到支付宝小程序
npm run dev:alipay
```

### Uni-app x（Vue 首选）

```vue
<!-- Uni-app x + Vue 3 -->
<template>
  <view class="index">
    <text>Hello, Uni-app!</text>
    <button type="primary" @click="onClick">Click</button>
  </view>
</template>

<script setup lang="ts">
const onClick = () => console.log('clicked')
</script>
```

```bash
# HBuilderX 或 CLI
npm install -g @dcloudio/uvm
uvm
npm init @dcloudio/uvm

# 编译到微信小程序
npm run dev:mp-weixin
```

---

## 3. 小程序 vs Web 差异

| 维度 | 小程序 | Web |
|------|--------|-----|
| **渲染** | 双线程（逻辑层 + 渲染层） | 单线程 |
| **DOM** | 无真实 DOM，Virtual DOM | 真实 DOM |
| **API** | `wx.*` / `my.*` 平台 API | Web API |
| **路由** | `wx.navigateTo` | History API |
| **网络** | `wx.request`（封装） | fetch / axios |
| **存储** | `wx.setStorage` | LocalStorage |
| **支付** | `wx.requestPayment` | 第三方支付 SDK |

---

## 4. 性能优化

| 优化项 | 说明 |
|--------|------|
| **分包加载** | 主包 < 2MB，按需加载 subpackage |
| **图片优化** | CDN + WebP + 懒加载 |
| **setData 优化** | 避免大数据、避免频繁调用 |
| **预加载** | `wx.preload` 提前加载下页数据 |
| **骨架屏** | 首屏占位，感知速度 |

```json
// app.json 分包配置
{
  "pages": ["pages/index/index"],
  "subpackages": [
    {
      "root": "pages/subpkg",
      "pages": ["detail/detail"]
    }
  ]
}
```

---

## 5. 小程序 + 跨端最佳实践

1. **业务逻辑复用**：Taro / Uni-app 抽象通用组件
2. **平台差异处理**：`Taro.getEnv()` / `uni.getSystemInfo()` 判断平台
3. **样式兼容**：使用 rpx 单位（微信小程序）或 rem（H5）
4. **平台 API 封装**：统一 API 层，内部处理差异
5. **CI/CD**：多端构建脚本 + 多平台发布

---

## 6. 小程序生态工具

| 工具 | 作用 |
|------|------|
| **Taro UI** | Taro 官方 UI 库 |
| **NutUI** | 京东风格的 Taro UI |
| **uView UI** | Uni-app 首选 UI 库 |
| **mpx** | 滴滴跨端方案（Vue） |

---

## 7. 学习路径

1. **入门**（1 周）：微信小程序原生开发（WXML / WXSS / JS）
2. **进阶**（2 周）：Taro 4 / Uni-app x 跨端开发
3. **高级**（持续）：性能优化 + 原生模块 + 多端发布 CI

## 8. 交叉引用

- [`08-cross-platform/`](../) — 跨端总览
- [`08-cross-platform/react-native/`](../react-native/) — RN（另一种跨端形态）
- [`12.story/21-multiplatform-architecture.md`](../../../12.story/21-multiplatform-architecture.md) — 阿明餐厅多端架构

---

← [返回 跨端开发](../README.md)
