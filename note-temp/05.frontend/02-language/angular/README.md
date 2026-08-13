<!--
module:
  parent: front-end
  slug: front-end/angular
  type: article
  category: 主模块子文章
  summary: Angular 核心架构、依赖注入、RxJS、Signals 与企业级应用实践
-->

# Angular

> 一句话定位：**企业级全栈前端框架——从依赖注入到 Signals，用"约束"换"可维护性"**

Angular 是 Google 维护的全功能前端框架，2026 年仍是企业级后台管理系统、大型 SaaS 的首选之一。它的核心理念是**用框架级约束（DI、Module/Standalone、强类型）换取大规模团队的长期可维护性**。

---

## 📚 核心内容

| 主题 | 内容 | 关键点 |
|------|------|--------|
| 一、核心架构 | Module → Standalone Components 演进 | Angular 14+ 去 NgModule 化 |
| 二、依赖注入 | Provider / Injectable / InjectionToken | 层级注入器，核心差异化能力 |
| 三、RxJS | Observable / Subject / BehaviorSubject | 响应式编程基石 |
| 四、Signals | Angular 17+ 响应式原语 | 细粒度变更检测 |
| 五、Angular CLI | 工作区 / 脚手架 / schematics | 标准化开发体验 |
| 六、变更检测 | Default vs OnPush / Zone.js vs Zoneless | 性能优化的核心 |
| 七、框架对比 | Angular vs React vs Vue | 选型决策 |
| 八、企业场景 | 大型后台 / 微前端 / monorepo | 适用领域分析 |

---

## 一、核心架构演进

### 从 Module 到 Standalone Components

```text
Angular 历史演进：
v2-v13: NgModule 为核心组织单元
v14:    Standalone Components 引入（可选）
v15:    Standalone 成为推荐方式
v17:    Signals + 新控制流语法（@if / @for）
v18+:   Zoneless 实验性支持
```

```typescript
// ❌ 旧方式：需要 NgModule
@NgModule({
  declarations: [UserComponent],
  imports: [CommonModule],
  exports: [UserComponent]
})
export class UserModule {}

// ✅ 新方式：Standalone Component（Angular 14+）
@Component({
  selector: 'app-user',
  standalone: true,          // 关键标记
  imports: [CommonModule],   // 直接导入依赖
  template: `<h1>{{ user.name }}</h1>`
})
export class UserComponent {
  user = { name: 'Alice' };
}
```

### 新控制流语法（Angular 17+）

```html
<!-- 旧语法 -->
<div *ngIf="isLoading">Loading...</div>
<div *ngFor="let item of items">{{ item.name }}</div>

<!-- 新语法（编译时优化，更小 bundle） -->
@if (isLoading) {
  <div>Loading...</div>
} @else {
  <div>Ready!</div>
}

@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
} @empty {
  <div>No items found.</div>
}
```

---

## 二、依赖注入系统

Angular 的 DI 是**框架级**能力，不同于 React 的 Context 或 Vue 的 provide/inject——它是层级化的、可配置的、可测试的。

### 三层注入器

```text
PlatformInjector（全局单例）
  └── RootInjector（@Injectable({ providedIn: 'root' })）
       └── ElementInjector（组件级 providers）
            └── 子组件 ElementInjector（继承链）
```

```typescript
// 1. 全局单例服务
@Injectable({ providedIn: 'root' })
export class AuthService {
  private token = signal<string | null>(null);

  login(credential: Credential) {
    this.token.set(credential.accessToken);
  }

  isLoggedIn(): boolean {
    return this.token() !== null;
  }
}

// 2. 组件级 Provider（每组件实例独立）
@Component({
  selector: 'app-dashboard',
  providers: [DashboardService],  // 组件销毁时服务也销毁
  template: `...`
})
export class DashboardComponent {
  constructor(private svc: DashboardService) {}
}

// 3. InjectionToken（非 class 依赖）
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', {
  providedIn: 'root',
  factory: () => environment.apiUrl
});

// 使用
constructor(@Inject(API_BASE_URL) private baseUrl: string) {}
```

---

## 三、RxJS 与响应式编程

RxJS 是 Angular 的**异步基础设施**——HTTP、表单值变化、路由事件、WebSocket 全部基于 Observable。

### 核心概念

| 类型 | 特征 | 用途 |
|------|------|------|
| **Observable** | 冷流，订阅才执行 | HTTP 请求、事件流 |
| **Subject** | 热流，多播 | 事件总线 |
| **BehaviorSubject** | 有初始值，新订阅立即获最新值 | 状态管理 |
| **ReplaySubject** | 缓存 N 个历史值 | 日志回放 |

```typescript
@Injectable({ providedIn: 'root' })
export class SearchService {
  private searchSubject = new BehaviorSubject<string>('');

  // 防抖 + 去重 + 自动取消
  results$ = this.searchSubject.pipe(
    debounceTime(300),
    distinctUntilChanged(),
    switchMap(query => this.http.get<SearchResult[]>(`/api/search?q=${query}`))
  );

  search(query: string) {
    this.searchSubject.next(query);
  }
}
```

### 常用操作符速查

| 操作符 | 作用 | 场景 |
|--------|------|------|
| `switchMap` | 取消前一个，切换到新的 | 搜索框实时搜索 |
| `mergeMap` | 并发执行所有 | 批量并行请求 |
| `concatMap` | 串行执行 | 有序提交 |
| `exhaustMap` | 忽略后续直到完成 | 防重复提交按钮 |
| `combineLatest` | 多流合取最新值 | 多筛选条件联动 |
| `takeUntil` | 在指定流触发时完成 | 组件销毁清理 |

---

## 四、Signals（Angular 17+ 响应式原语）

Signals 是 Angular 对标 React Hooks / Vue refs 的响应式原语，目标是在 Zone.js 之外实现**细粒度变更检测**。

```typescript
import { signal, computed, effect } from '@angular/core';

@Component({
  selector: 'app-counter',
  standalone: true,
  template: `
    <p>Count: {{ count() }}</p>
    <p>Double: {{ double() }}</p>
    <button (click)="increment()">+1</button>
  `
})
export class CounterComponent {
  // 可写信号
  count = signal(0);

  // 派生信号（自动追踪依赖）
  double = computed(() => this.count() * 2);

  // 副作用（响应式监听）
  constructor() {
    effect(() => {
      console.log('count changed to', this.count());
    });
  }

  increment() {
    this.count.update(v => v + 1);
  }
}
```

### Signals vs RxJS

| 维度 | Signals | RxJS |
|------|---------|------|
| 定位 | 同步状态 | 异步事件流 |
| 学习曲线 | 极低 | 较高 |
| 内存管理 | 自动 GC | 需 takeUntil / unsubscribe |
| 互操作 | `toSignal(obs$)` / `toObservable(sig)` | 同上 |
| 推荐场景 | 组件状态、派生值 | HTTP、WebSocket、复杂异步 |

---

## 五、Angular CLI 与工作区

```bash
# 创建项目
ng new my-app --standalone --style=scss --routing

# 生成组件/服务/管道
ng generate component user-profile
ng generate service auth
ng generate pipe truncate

# 开发服务器（HMR 热更新）
ng serve --hmr

# 构建（生产优化）
ng build --configuration production

# 单元测试
ng test --watch=false --code-coverage

# E2E 测试
ng e2e
```

### Angular Workspace（monorepo）

```json
// angular.json 支持多项目工作区
{
  "projects": {
    "web-app": { "root": "projects/web-app" },
    "admin-app": { "root": "projects/admin-app" },
    "shared-lib": { "root": "projects/shared-lib", "projectType": "library" }
  }
}
```

---

## 六、变更检测策略

### Default vs OnPush

```typescript
// Default：每次事件触发检查整棵树
@Component({
  changeDetection: ChangeDetectionStrategy.Default
})

// OnPush：仅在 @Input 变化或手动标记时检查
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UserCardComponent {
  @Input() user!: User;  // 引用变化才触发检测

  constructor(private cdr: ChangeDetectorRef) {}

  onInternalChange() {
    this.cdr.markForCheck();  // 手动触发
  }
}
```

### Zone.js vs Zoneless（Angular 18+）

| 方式 | 机制 | 性能 |
|------|------|------|
| **Zone.js** | monkey-patch 所有异步 API，自动触发检测 | 简单但有开销 |
| **Zoneless** | 依赖 Signals 驱动变更检测 | 更快，但需要全 Signals 架构 |

```typescript
// 启用 Zoneless（实验性）
bootstrapApplication(AppComponent, {
  providers: [
    provideExperimentalZonelessChangeDetection()
  ]
});
```

---

## 七、Angular vs React vs Vue 对比

| 维度 | Angular | React | Vue |
|------|---------|-------|-----|
| **定位** | 全功能框架 | UI 库 + 生态拼装 | 渐进式框架 |
| **语言** | TypeScript（必须） | JS/TS（可选） | JS/TS（可选） |
| **状态管理** | DI + Signals + NgRx | useState + Redux/Zustand | reactive + Pinia |
| **路由** | 内置 @angular/router | 需装 react-router | 需装 vue-router |
| **HTTP** | 内置 HttpClient | fetch / axios | fetch / axios |
| **表单** | 响应式表单 + 模板驱动 | 受控组件 + 第三方库 | v-model 双向绑定 |
| **学习曲线** | 陡峭（概念多） | 中等 | 平缓 |
| **包体积** | 较大（~150KB gzip） | 较小（~40KB core） | 中等（~60KB） |
| **企业采用** | Google / 银行 / 大型企业 | Meta / 广泛 | 阿里 / 中小到大型 |
| **适合规模** | 大型团队 / 长期项目 | 灵活，各种规模 | 中小型到大型 |

---

## 八、企业级应用场景分析

### Angular 的优势领域

| 场景 | 原因 |
|------|------|
| **大型后台管理系统** | 内置路由/表单/HTTP/DI，开箱即用 |
| **金融 / 银行应用** | 强类型 + 严格模式 + 可预测变更检测 |
| **多人协作大项目** | 框架约束统一代码风格，降低沟通成本 |
| **长期维护项目** | Angular 升级路径清晰（ng update），向后兼容好 |
| **微前端** | Module Federation + Nx monorepo 支持良好 |

### Angular 的劣势

| 劣势 | 说明 |
|------|------|
| 学习成本高 | DI / RxJS / Zone.js / 生命周期，概念密度大 |
| 包体积大 | 不适合内容型网站（选 Astro / Next.js） |
| 社区活跃度 | 不及 React / Vue 的第三方生态 |
| 招聘难度 | 国内 Angular 开发者相对较少 |

---

## 🔗 相关章节

- **TypeScript**：[typescript](../typescript/README.md) — Angular 的宿主语言
- **运行时**：[runtime](../runtime/README.md) — V8 / 事件循环机制
- **框架对比**：[03-frameworks](../../03-frameworks/) — React / Vue / Svelte 横向对比
- **架构**：[05-architecture](../../05-architecture/) — 微前端 / 状态管理 / 渲染模式

---

← [返回: 语言](../README.md)
