# React Native 跨端移动开发

> 一句话定位：**React Native —— 一套 React 代码，跑在 iOS + Android 两端**

React Native（RN）是 Meta 开源的跨平台移动框架，让 Web 开发者用 React 语法构建原生移动应用。2026 年 RN 新架构（Fabric / TurboModules / Bridgeless）全面落地，性能显著提升。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

React Native 跨端移动开发 本应该很简单，一句话定位：**React Native —— 一套 React 代码，跑在 iOS + Android 两端**

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 1. RN 的核心价值

| 价值 | 说明 |
|------|------|
| **代码复用** | 70-90% 业务代码 iOS / Android 共享 |
| **Web 技能迁移** | React 开发者快速上手 |
| **热更新** | JS bundle OTA 更新，无需商店审核 |
| **原生能力** | 可写原生模块扩展 |

---

## 2. 架构演进

```mermaid
graph LR
  A[旧架构<br/>Bridge] --> B[新架构<br/>Fabric + TurboModules]
  B --> C[Bridgeless<br/>2024 默认]
  style A fill:#ffebee
  style B fill:#e8f5e9
  style C fill:#e3f2fd
```

| 架构 | JS 与原生通信 | 性能 |
|------|--------------|------|
| **旧（Bridge）** | JSON 序列化，异步 | ⭐⭐ |
| **新（JSI）** | C++ 直接调用，同步 | ⭐⭐⭐⭐⭐ |

---

## 3. 主流技术栈（2026）

| 类别 | 推荐 | 说明 |
|------|------|------|
| **框架** | Expo SDK 52+ | **首选**，开发体验最佳 |
| **路由** | Expo Router（文件路由） | 基于 Expo，Next.js 风格 |
| **样式** | NativeWind（Tailwind for RN） | Tailwind 语法 |
| **状态** | Zustand / TanStack Query | 同 Web 生态 |
| **HTTP** | Axios / ky | 同 Web 生态 |
| **原生模块** | React Native Community | 相机、定位、权限等 |
| **动画** | Reanimated 3 | GPU 动画 |
| **手势** | React Native Gesture Handler | 复杂手势 |

---

## 4. Expo vs 裸 RN

| 维度 | Expo | 裸 React Native |
|------|------|----------------|
| **开发体验** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **原生模块扩展** | 需要 Expo Dev Client | 自由配置 |
| **构建** | EAS Build（云端） | 本地 Xcode / Android Studio |
| **体积** | 稍大 | 更小 |
| **适合** | **大部分项目** | 强原生需求 |

**2026 共识**：新项目首选 Expo，需要深度原生定制再用裸 RN 或 Expo Dev Client。

---

## 5. 代码示例

```tsx
// App.tsx (Expo)
import { View, Text, StyleSheet } from 'react-native'

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Hello, React Native!</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
})
```

### NativeWind（Tailwind 语法）
```tsx
import { Text, View } from 'react-native'

export default function Card() {
  return (
    <View className="p-4 bg-white rounded-lg shadow">
      <Text className="text-lg font-bold">Title</Text>
    </View>
  )
}
```

---

## 6. 性能优化

| 优化项 | 说明 |
|--------|------|
| **FlashList** | 替代 FlatList，性能提升 5-10x |
| **Hermes 引擎** | 默认启用，启动快 + 内存小 |
| **Reanimated** | GPU 动画，主线程不阻塞 |
| **图片缓存** | expo-image（比 Image 快） |
| **Bundle 分割** | 懒加载页面 |

---

## 7. RN vs Flutter

| 维度 | React Native | Flutter |
|------|-------------|---------|
| **语言** | JavaScript / TypeScript | Dart |
| **渲染** | 原生组件（新架构） | 自绘 Skia / Impeller |
| **性能** | ⭐⭐⭐⭐ 新架构优 | ⭐⭐⭐⭐⭐ |
| **生态** | npm 生态 + RN 专用 | pub.dev |
| **Web 开发者友好** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **热更新** | ✅ OTA | ❌ 需商店审核 |
| **桌面** | 实验性 | ✅ 稳定 |
| **国内采用** | 字节、美团、阿里 | 阿里、腾讯、字节 |

---

## 8. 学习路径

1. **入门**（1 周）：Expo 基础 + RN 组件 + 导航
2. **进阶**（2 周）：NativeWind + Reanimated + 原生模块
3. **高级**（持续）：性能优化 + 自定义原生模块 + EAS 部署

## 9. 交叉引用

- [`08-cross-platform/`](../) — 跨端总览
- [`08-cross-platform/mini-program/`](../mini-program/) — 小程序（另一种跨端形态）
- [`03-frameworks/`](../../03-frameworks/) — React 生态
