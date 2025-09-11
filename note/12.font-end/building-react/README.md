# React前端框架构建

## 前端框架组合

1. 核心框架(必选)：React + TypeScript
2. 构建工具(必选)：Webpack
3. 包管理工具(必选)：npm
4. HTTP 客户端(必选)：Axios
5. 代码质量(可选)：Eslint + Prettier
6. 路由(可选)：React Router
7. 测试(可选)：Jest
8. UI库(可选)：Ant Design
9. 状态管理(可选)：Redux Toolkit
10. 工具库(可选)：Lodash、Day.js等

## 必要步骤

### 1. 初始化项目

```
# 1. 创建项目目录并进入
mkdir my-react-framework
cd my-react-framework

# 2. 初始化 npm 项目
npm init -y

# 3. 创建基本目录结构
Linux:
	mkdir -p src/{components,store,api,utils,routes,assets,types}
Windows:
	mkdir src/components, src/store, src/services, src/utils, src/routes, src/assets, src/types
mkdir public
```

### 2. 安装核心依赖（React+TypeScript）

```
# 1. 安装 React 和 React-DOM
npm install react react-dom

# 2. 安装 TypeScript 和类型定义
npm install --save-dev typescript @types/react @types/react-dom @types/node

# 3. 初始化 TypeScript 配置
npx tsc --init
```

#### 2.1 编辑生成的tsconfig.json

```
{
  "compilerOptions": {
    // 编译目标：将 TypeScript 编译为 ES2015 (ES6) 语法
    "target": "ES2015",

    // 包含的库文件，用于类型检查（支持 DOM 操作和 ES6 特性）
    "lib": ["DOM", "DOM.Iterable", "ES6"],

    // 允许编译 .js 文件（配合 Babel 时有用）
    "allowJs": true,

    // 跳过对 node_modules 中类型定义文件的检查，加快编译速度
    "skipLibCheck": true,

    // 启用 ES 模块互操作，允许使用 import react from 'react'（即使它是 commonjs 模块）
    "esModuleInterop": true,

    // 允许从没有默认导出的模块中使用默认导入（配合 esModuleInterop 使用）
    "allowSyntheticDefaultImports": true,

    // 启用所有严格类型检查选项（如 strictNullChecks, noImplicitAny 等）
    "strict": true,

    // 强制文件名大小写一致，避免在大小写敏感系统上出错
    "forceConsistentCasingInFileNames": true,

    // 指定模块代码生成方式：使用 ESNext（支持动态 import()）
    "module": "ESNext",

    // 模块解析策略：使用 Node.js 的模块解析方式（查找 node_modules）
    "moduleResolution": "node",

    // 允许导入 .json 文件
    "resolveJsonModule": true,

    // 将每个文件作为独立模块处理（用于支持某些构建工具如 Babel、ESLint）
    "isolatedModules": true,

    // 不生成输出文件（由 Babel 或其他工具负责编译）
    "noEmit": true,

    // 支持 JSX 语法，并使用 React 17+ 的新 JSX 转换（不需要 import React）
    "jsx": "react-jsx",

    // 解析非相对模块名的基准路径
    "baseUrl": ".",

    // 路径映射：设置别名，支持绝对路径导入
    "paths": {
      "@/*": ["src/*"],           // 导入 src/ 下的文件：@/components/Button
      "@test/*": ["src/modules/test/*"] // 导入 test 模块：@test/utils
    }
  },

  // 需要编译的文件路径（包含 src 目录下所有文件）
  "include": ["src"],

  // 排除的文件或目录（不参与类型检查）
  "exclude": ["node_modules", "dist"]
}
```

### 3. 安装和配置Webapck

```
# 1. 安装 Webpack 核心
npm install --save-dev webpack webpack-cli webpack-dev-server

# 2. 安装 TypeScript 和 Babel 相关 loader (Babel 用于转译)
npm install --save-dev ts-loader babel-loader @babel/core @babel/preset-env @babel/preset-react @babel/preset-typescript

# 3. 安装 CSS 相关 loader
npm install --save-dev css-loader style-loader sass-loader sass

# 4. 安装 Webpack 插件
npm install --save-dev html-webpack-plugin mini-css-extract-plugin clean-webpack-plugin

# 5. 安装开发服务器
npm install --save-dev webpack-dev-server
```

#### 3.1 创建 webpack.config.js

```
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

const isProduction = process.env.NODE_ENV === 'production';

const proxyLog = {
  // 添加日志
  onProxyReq: (proxyReq, req, res) => {
    console.log(
      `[WEBPACK PROXY] Proxying ${req.method} ${req.url} -> ${proxyReq.protocol}//${proxyReq.host}${proxyReq.path}`
    );
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(
      `[WEBPACK PROXY] Received response for ${req.url} with status ${proxyRes.statusCode}`
    );
  },
};

module.exports = {
  mode: isProduction ? 'production' : 'development',
  entry: './src/index.tsx', // 入口文件
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    clean: true, // Webpack 5+ 自带 clean
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@test': path.resolve(__dirname, 'src/modules/test'),
    },
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: 'babel-loader',
      },
      {
        test: /\.css$/,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          'css-loader',
        ],
      },
      {
        test: /\.s[ac]ss$/i,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          'css-loader',
          'sass-loader',
        ],
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource',
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html', // 模板文件
    }),
    new CleanWebpackPlugin(),
    isProduction &&
      new MiniCssExtractPlugin({
        filename: '[name].[contenthash].css',
      }),
  ].filter(Boolean),
  devServer: {
    historyApiFallback: true, // history使用前端路由
    static: './dist',
    hot: true,
    port: 8000,
    open: true,
    // 代理
    proxy: [
      {
        path: '/test',
        target: 'http://localhost:3000/',
        changeOrigin: true,
        pathRewrite: {
          '^/test': '',
        },
        ...proxyLog,
      },
    ],
  },
  devtool: isProduction ? 'source-map' : 'eval-source-map',
};

```

注意：浏览器出于安全考虑会禁用一些端口：6000等。

### 4. 配置 Babel

#### 4.1 创建 .babelrc 文件

```
{
  "presets": [
    "@babel/preset-env", // 转译现代 JS 语法，确保浏览器兼容性
    ["@babel/preset-react", { "runtime": "automatic" }], // 支持 React 的 JSX 语法
    "@babel/preset-typescript" // 支持 TypeScript 类型语法
  ]
}
```

### 5. 创建基础 HTML 和入口文件

#### 5.1 在 public/index.html 中

```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My React Framework</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
```

#### 5.2 在 src/index.tsx 中

```
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<App />);
```

#### 5.3 在 src/App.tsx 中

```
import React from 'react';

const App: React.FC = () => {
  return <div>Hello, My React Framework!</div>;
};

export default App;
```

### 6. 安装和配置 HTTP 客户端 (Axios)

```
npm install axios
npm install --save-dev @types/axios
```

#### 6.1 创建 src/api/index.ts(前端拦截器)

```
import axios from 'axios';

const api = axios.create({
  baseURL: '/', // 开发时通过 Webpack 代理
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 例如：添加 token
    // const token = localStorage.getItem('token');
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 统一错误处理
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;
```

### 7. 完善 package.json 脚本

```
{
  "scripts": {
    "start": "webpack serve --mode development",
    "build": "webpack --mode production",
  }
}
```

至此，一个能跟后端对接的基本前端框架完事了。

## 非必要步骤

### 8. 配置git

```
git init
```

#### 8.1 创建.gitignore

```
# Node.js
node_modules/
npm-debug.log
yarn-error.log
yarn-debug.log
.pnpm-debug.log

# 构建输出
/dist
/build
/out
/.next

# 环境变量
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE 和编辑器
.DS_Store
Thumbs.db
*.swp
*.swo
*~
.vscode/
.idea/
*.sublime-project
*.sublime-workspace

# 日志文件
logs
*.log

# 依赖包锁文件 (可选，但通常建议提交)
# package-lock.json
# yarn.lock
# pnpm-lock.yaml

# 测试
coverage/
.nyc_output/

# 构建工具缓存
.cache/
webpack/
.parcel-cache

# TypeScript
*.tsbuildinfo

# 其他
.DS_Store
*.local
```

### 9. 安装和配置代码质量工具 (ESLint + Prettier)

```
# ESLint
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-react eslint-plugin-react-hooks

# Prettier
npm install --save-dev prettier eslint-config-prettier eslint-plugin-prettier
```

#### 9.1 创建 .eslintrc.js

```
module.exports = {
  // ==================== 环境配置 ====================
  env: {
    browser: true,  // 启用浏览器环境全局变量（如 window, document）
    es2021: true,   // 启用 ES2021 语法支持（如 Promise.any, WeakRef 等）
  },

  // ==================== 继承的规则集合 ====================
  // 从以下预设配置中继承推荐的规则
  extends: [
    'eslint:recommended',                    // ESLint 官方推荐的基础规则
    'plugin:@typescript-eslint/recommended', // @typescript-eslint 插件的推荐规则（用于 TypeScript）
    'plugin:react/recommended',              // eslint-plugin-react 的推荐规则（用于 React）
    'plugin:react-hooks/recommended',        // eslint-plugin-react-hooks 的推荐规则（用于 React Hooks）
    'plugin:prettier/recommended',           // 启用 eslint-plugin-prettier，让 ESLint 报告 Prettier 格式问题
  ],

  // ==================== 解析器配置 ====================
  parser: '@typescript-eslint/parser', // 使用 TypeScript 官方解析器，支持 .ts/.tsx 文件

  parserOptions: {
    ecmaFeatures: {
      jsx: true, // 启用对 JSX 的支持
    },
    ecmaVersion: 'latest',  // 使用最新的 ECMAScript 标准
    sourceType: 'module',   // 支持 ES6 模块语法（import/export）
  },

  // ==================== 插件设置 ====================
  settings: {
    react: {
      version: 'detect', // 自动检测项目中安装的 React 版本，确保规则适配
    },
  },

  // ==================== 自定义规则 ====================
  rules: {
    // TypeScript 相关：未使用的变量仅警告（不报错）
    '@typescript-eslint/no-unused-vars': 'warn',

    // React 相关：React 17+ 的 JSX 不需要显式引入 React，因此关闭此规则
    'react/react-in-jsx-scope': 'off',
  },
};
```

#### 9.2 创建 .prettierrc.js

```
module.exports = {
  // 在语句末尾添加分号
  semi: true,

  // 在对象、数组等末尾添加逗号（兼容 ES5，即在多行时添加，单行可选）
  // 例如：{ a: 1, } 或 [1, 2,]
  trailingComma: 'es5',

  // 使用单引号而不是双引号
  singleQuote: true,

  // 每行代码最大宽度为 80 个字符，超过将自动换行
  printWidth: 80,

  // 一个缩进使用 2 个空格
  tabWidth: 2,
};
```

### 10. 安装和配置路由 (React Router)

```
npm install react-router-dom
npm install --save-dev @types/react-router-dom
```

##### 创建 src/routes/index.ts

```
/**
 * @description 路由封装
 */

import { lazy } from 'react';

// 获取modules下所有路由文件
const files = (require as any).context('../modules', true, /\.route\.(t|j)s$/);

let configRouters: Record<string, any>[] = [];

files.keys().forEach((key: string): void => {
  configRouters = configRouters.concat(files(key).default);
});

// 展平路由
const flattenRoutes: any[] = configRouters.map((x) => x.routes).flat();

const BasicLayout = lazy(() => import('@/pages/BasicLayout'));

export const routes = [
  {
    path: '/login',
    Component: lazy(() => import('@/pages/Login')),
  },
  {
    path: '/',
    Component: BasicLayout,
    children: [...flattenRoutes],
  },
];

export default routes;

```

##### 改写 src/App.tsx

```
import React from 'react';
import { createBrowserRouter, RouterProvider, Routes } from 'react-router-dom';
import { routes } from '@/routes';

const App: React.FC = () => {
  const router = createBrowserRouter(routes);
  return (
    <RouterProvider router={router} />
  );
};

export default App;
```

##### 在modules文件下编写index.route.ts文件(按照业务代码编写)

业务代码结构如下：

```
modules
	——api
	——pages
	——routes
		——index.route.ts
```

```
import { lazy } from 'react';

export default {
  routes: [
    {
      path: '/table',
      Component: lazy(() => import('@test/pages/test')),
    },
    {
      path: '/test2',
      Component: lazy(() => import('@test/pages/test2')),
    }
  ],
};
```



### 11. 安装和配置状态管理(Redux Toolkit)

```
npm install @reduxjs/toolkit react-redux
npm install --save-dev @types/react-redux
```

### 12. 安装和配置 UI 库 (Ant Design)

```
npm install antd
npm install --save-dev @types/antd
```

### 13. 配置测试 (Jest + React Testing Library)

```
npm install --save-dev jest @types/jest ts-jest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### 14. 安装工具库

```
npm install lodash-es dayjs
```

## 优化

### 1. 生产环境webpack优化

#### 优化项

| 优化项      | 工具                    | 效果                       |
| ----------- | ----------------------- | -------------------------- |
| 代码分割    | splitChunks             | 减小首包体积，按需加载     |
| CSS 压缩    | CssMinimizerPlugin      | 减小 CSS 体积              |
| JS 压缩     | ESBuildPlugin / Terser  | 减小 JS 体积，提升加载速度 |
| 图片压缩    | ImageMinimizerPlugin    | 自动压缩图片               |
| Gzip 预压缩 | CompressionPlugin       | 提升传输效率               |
| Bundle 分析 | webpack-bundle-analyzer | 定位体积瓶颈               |
| 源码保护    | nosources-source-map    | 防止源码泄露               |

##### 1. 代码分割（Code Splitting）

将代码拆分为更小的 chunk，实现按需加载，提升首屏速度。

```
// webpack.config.js
optimization: {
  splitChunks: {
    chunks: 'all', // 同时分割同步和异步代码
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendors',
        chunks: 'all',
        priority: 10,
      },
      common: {
        name: 'common',
        minChunks: 2,
        chunks: 'all',
        enforce: true,
        priority: 5,
      },
    },
  },
  runtimeChunk: 'single', // 将 runtime 代码单独打包，避免 vendor hash 变化
},

```

**效果**：vendors.chunk.js（第三方库）、common.chunk.js（公共模块）、runtime.js

##### 2. CSS 压缩（CSS Minification）

使用 CssMinimizerPlugin 压缩 CSS

```
npm install --save-dev css-minimizer-webpack-plugin
```

```
// webpack.config.js
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

// 在 plugins 中添加（生产环境）
optimization: {
  minimize: isProduction,
  minimizer: [
    // 压缩 JS（Terser 默认已内置，可显式配置）
    `...`, // 保留默认的 TerserPlugin
    new CssMinimizerPlugin(), // 压缩 CSS
  ],
}

```

##### 3. JS 压缩优化（可选：替换 Terser 为 ESBuild）

默认使用 TerserPlugin 压缩 JS，但 esbuild 更快。

```
npm install --save-dev terser-webpack-plugin esbuild
```

```
// webpack.config.js
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        minify: TerserPlugin.esbuildMinify, // 使用 esbuild 压缩 JS/TS
        terserOptions: {
          target: 'es2015', // 指定目标环境
        },
      }),
    ],
  },
};
```

##### 4. 图片压缩（Image Optimization）

自动压缩图片，减小体积。

```
npm install --save-dev image-minimizer-webpack-plugin imagemin-gifsicle imagemin-jpegtran imagemin-optipng imagemin-svgo
```

```
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');

// 在 plugins 中添加
new ImageMinimizerPlugin({
  minimizer: {
    implementation: ImageMinimizerPlugin.imageminMinify,
    options: {
      plugins: [
        ['gifsicle', { interlaced: true }],
        ['jpegtran', { progressive: true }],
        ['optipng', { optimizationLevel: 5 }],
        ['svgo', { plugins: ['preset-default'] }],
      ],
    },
  },
}),
```

##### 5. Gzip/Brotli 预压缩（用于 Nginx 静态服务）

生成 .gz 文件，Nginx 可直接返回压缩内容。

```
npm install --save-dev compression-webpack-plugin
```

```
const CompressionPlugin = require('compression-webpack-plugin');

// plugins 中添加（生产环境）
isProduction &&
new CompressionPlugin({
  algorithm: 'gzip',
  test: /\.(js|css|html|svg)$/,
  threshold: 8192, // 只压缩大于 8KB 的文件
  deleteOriginalAssets: false,
}),
```

生成 app.js 和 app.js.gz，Nginx 配置 gzip_static on; 即可启用。

##### 6. Tree Shaking 优化（确保启用）

确保你的代码是 ES Module，Webpack 会自动 Tree Shaking。

1. 使用 import { x } from 'lib' 而不是 import _ from 'lodash'（全量引入）
2. 使用 sideEffects: false in package.json

```
// package.json
{
  "sideEffects": false
}
```

##### 7. 分析打包体积（Bundle Analysis）

使用 webpack-bundle-analyzer 分析哪些包最耗体积。

```
npm install --save-dev webpack-bundle-analyzer
```

```
// webpack.config.js
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

// plugins 中添加（可选，开发时分析）
isProduction &&
process.env.ANALYZE && 
new BundleAnalyzerPlugin(),
```

```
// package.json
{
  "scripts": {
    "build:analyze": "ANALYZE=1 npm run build"
  }
}
```

##### 8. 关闭开发工具（DevTools）在生产环境

```
devtool: isProduction ? 'source-map' : 'eval-source-map',
```

#### 完整的webpack.config.js

```
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const { ESBuildPlugin } = require('esbuild-webpack-plugin'); // 可选：更快的 JS 压缩

const isProduction = process.env.NODE_ENV === 'production';

module.exports = {
  mode: isProduction ? 'production' : 'development',
  entry: './src/index.tsx',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash:8].js',
    chunkFilename: '[name].[contenthash:8].chunk.js',
    clean: true,
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@test': path.resolve(__dirname, 'src/modules/test'),
    },
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: 'babel-loader',
      },
      {
        test: /\.css$/,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          'css-loader',
        ],
      },
      {
        test: /\.s[ac]ss$/i,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          'css-loader',
          'sass-loader',
        ],
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource',
        generator: {
          filename: 'images/[hash][ext][query]',
        },
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
        generator: {
          filename: 'fonts/[hash][ext][query]',
        },
      },
    ],
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10,
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true,
          priority: 5,
        },
      },
    },
    runtimeChunk: 'single',
    minimize: isProduction,
    minimizer: [
      new ESBuildPlugin({ target: 'es2015', css: true }), // 或 `...` 使用 Terser
      new CssMinimizerPlugin(),
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
    new CleanWebpackPlugin(),
    isProduction &&
      new MiniCssExtractPlugin({
        filename: '[name].[contenthash:8].css',
        chunkFilename: '[name].[contenthash:8].chunk.css',
      }),
    isProduction &&
      new CompressionPlugin({
        algorithm: 'gzip',
        test: /\.(js|css|html|svg)$/,
        threshold: 8192,
        deleteOriginalAssets: false,
      }),
    isProduction &&
      new ImageMinimizerPlugin({
        minimizer: {
          implementation: ImageMinimizerPlugin.imageminMinify,
          options: {
            plugins: [
              ['gifsicle', { interlaced: true }],
              ['jpegtran', { progressive: true }],
              ['optipng', { optimizationLevel: 5 }],
              ['svgo', { plugins: ['preset-default'] }],
            ],
          },
        },
      }),
  ].filter(Boolean),
  devServer: {
    historyApiFallback: true,
    static: './dist',
    hot: true,
    port: 8000,
    open: true,
    proxy: [
      {
        path: '/test',
        target: 'http://localhost:3000/',
        changeOrigin: true,
        pathRewrite: {
          '^/test': '',
        },
      },
    ],
  },
  devtool: isProduction ? 'nosources-source-map' : 'eval-source-map', // 更安全
};
```

### 2. 开发环境webpack优化

#### 优化项

| 优化项         | 工具/配置                        | 效果                     |
| -------------- | -------------------------------- | ------------------------ |
| 快速 sourcemap | eval-cheap-module-source-map     | 错误定位快，构建快       |
| 持久化缓存     | cache: { type: 'filesystem' }    | 二次启动提速 50%+        |
| Babel 缓存     | cacheDirectory: true             | 避免重复编译             |
| 精准 resolve   | mainFields, include              | 减少解析时间             |
| 内存 serve     | devMiddleware.writeToDisk: false | 提升性能                 |
| 按需编译       | experiments.lazyCompilation      | 启动速度飞跃（大型项目） |
| 日志控制       | client.logging                   | 减少干扰                 |

##### 使用更快的 Source Map（已做，但可优化）

```
devtool: isProduction 
  ? 'nosources-source-map' 
  : 'eval-cheap-module-source-map',
```

| 类型                         |                                      |              |
| ---------------------------- | ------------------------------------ | ------------ |
| eval-cheap-module-source-map | 构建快，错误定位到行，保留原始文件名 | 推荐开发环境 |
| eval-source-map              | 完整 sourcemap，但构建慢             | 一般不需要   |
| cheap-module-source-map      | 不用 eval，更安全，但 HMR 可能略慢   | 安全要求高   |

##### 启用缓存（Cache）提升二次启动速度

Webpack 5+ 支持持久化缓存，大幅提升第二次启动速度。

```
// webpack.config.js
cache: {
  type: 'filesystem', // 使用文件系统缓存
  buildDependencies: {
    config: [__filename], // 如果 webpack 配置改变，重建缓存
  },
},
```

效果：

- 首次启动：正常
- 重启/修改配置后：快 50%~70%

##### 优化 Babel Loader 缓存

用了 babel-loader，但未开启缓存

```
use: {
  loader: 'babel-loader',
  options: {
    cacheDirectory: true, // ✅ 开启缓存
    cacheCompression: false, // ✅ 不压缩缓存（节省 CPU）
  },
},
```

效果：避免重复编译相同的文件

##### 限制 HMR 范围（避免不必要的更新）

有时 HMR 会触发整个页面刷新，而不是局部更新。确保你使用了正确的导出方式（如 React Fast Refresh）。

```
// babel.config.js
{
  "plugins": ["react-refresh/babel"]
}
```

```
// webpack.config.js
devServer: {
  hot: true,
  // hotOnly: true, // 可选：只 HMR，不 fallback 到 live reload
}
```

 确保组件是 函数式组件 或 支持 HMR 的类组件。

##### 减少不必要的 loader 处理

确保 babel-loader 不处理 node_modules（你已经做了 exclude: /node_modules/），但可以更精确

```
{
  test: /\.(ts|tsx)$/,
  exclude: /node_modules/,
  include: path.resolve(__dirname, 'src'), // ✅ 明确指定范围
  use: {
    loader: 'babel-loader',
    options: {
      cacheDirectory: true,
    },
  },
}
```

##### 优化 resolve.alias 和 extensions

mainFields 优化解析速度

```
resolve: {
  extensions: ['.tsx', '.ts', '.js'],
  alias: {
    '@': path.resolve(__dirname, 'src'),
    '@test': path.resolve(__dirname, 'src/modules/test'),
  },
  // ✅ 优化：优先使用 ES Module 版本
  mainFields: ['esmodule', 'module', 'main'], // 优先加载 .mjs 或 esm 版本
},
```

效果：减少解析时间，避免加载完整打包版

##### 开发服务器性能优化

```
devServer: {
  static: {
    directory: path.join(__dirname, 'dist'),
  },
  hot: true,
  port: 8000,
  open: true,
  // ✅ 优化：监听更精准
  watchFiles: ['src/**/*', 'public/**/*'],
  // ✅ 优化：提升性能
  devMiddleware: {
    writeToDisk: false, // 不写磁盘，只在内存中 serve
  },
  // ✅ 优化：关闭不必要的日志
  client: {
    logging: 'info', // 'none' 或 'error' 可减少日志
  },
}
```

##### 使用 lazyCompilation（Webpack 5+ 实验性）

按需编译，只在访问路由时才编译对应模块，极大提升启动速度。

```
experiments: {
  lazyCompilation: {
    // 可配置哪些 chunk 懒编译
    imports: true,
  },
},
```

注意：HMR 可能受影响，适合大型项目。

##### 监控编译性能（可选）

使用 webpack-bundle-analyzer 分析开发构建性能

```
new BundleAnalyzerPlugin({
  analyzerMode: 'static',
  openAnalyzer: false,
  reportFilename: 'report.html',
  generateStatsFile: true,
})
```

查看 stats.json 分析哪个 loader 最慢

#### 完整开发环境优化配置片段

```
// webpack.config.js（开发环境部分）
module.exports = {
  mode: isProduction ? 'production' : 'development',
  devtool: isProduction 
    ? 'nosources-source-map' 
    : 'eval-cheap-module-source-map',

  cache: {
    type: 'filesystem',
    buildDependencies: {
      config: [__filename],
    },
  },

  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@test': path.resolve(__dirname, 'src/modules/test'),
    },
    mainFields: ['esmodule', 'module', 'main'],
  },

  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        include: path.resolve(__dirname, 'src'),
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            cacheDirectory: true,
            cacheCompression: false,
          },
        },
      },
      // ... 其他规则
    ],
  },

  devServer: {
    static: {
      directory: path.join(__dirname, 'dist'),
    },
    hot: true,
    port: 8000,
    open: true,
    watchFiles: ['src/**/*', 'public/**/*'],
    devMiddleware: {
      writeToDisk: false,
    },
    client: {
      logging: 'info',
    },
    proxy: [...],
  },

  // experiments: {
  //   lazyCompilation: true,
  // },
};
```

## 完整的webpack.config.js配置

```
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');

const isProduction = process.env.NODE_ENV === 'production';

// 代理日志
const proxyLog = {
  onProxyReq: (proxyReq, req, res) => {
    console.log(
      `[WEBPACK PROXY] Proxying ${req.method} ${req.url} -> ${proxyReq.protocol}//${proxyReq.host}${proxyReq.path}`
    );
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(
      `[WEBPACK PROXY] Received response for ${req.url} with status ${proxyRes.statusCode}`
    );
  },
};

module.exports = {
  // ==================== 模式 ====================
  mode: isProduction ? 'production' : 'development',

  // ==================== 入口文件 ====================
  entry: './src/index.tsx', // 应用的主入口文件

  // ==================== 输出配置 ====================
  output: {
    path: path.resolve(__dirname, 'dist'), // 打包输出目录
    filename: '[name].[contenthash:8].js', // 主包文件名，含 8 位内容哈希
    chunkFilename: '[name].[contenthash:8].chunk.js', // 动态导入的 chunk 文件名
    clean: true, // 构建前清空 dist 目录（Webpack 5+ 内置）
  },

  // ==================== 缓存优化 ====================
  cache: {
    type: 'filesystem', // 使用文件系统缓存
    cacheDirectory: path.resolve(__dirname, 'node_modules/.cache/webpack'), // 缓存路径
    buildDependencies: {
      config: [__filename], // 当 webpack 配置文件变化时，缓存失效
    },
  },

  // ==================== 模块解析 ====================
  resolve: {
    extensions: ['.tsx', '.ts', '.js'], // 自动解析这些后缀的文件
    alias: {
      '@': path.resolve(__dirname, 'src'), // 路径别名 @ 指向 src
      '@test': path.resolve(__dirname, 'src/modules/test'), // @test 指向测试模块
    },
    mainFields: ['esmodule', 'module', 'main'], // 优先使用 ES 模块字段
  },

  // ==================== 模块规则（加载器） ====================
  module: {
    rules: [
      // TypeScript/TSX 文件使用 babel-loader 处理
      {
        test: /\.(ts|tsx)$/,
        include: path.resolve(__dirname, 'src'),
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            cacheDirectory: true, // 启用 babel 编译缓存
            cacheCompression: false, // 不压缩缓存文件，提升读取速度
          },
        },
      },
      // CSS 文件：生产用 MiniCssExtractPlugin，开发用 style-loader
      {
        test: /\.css$/,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          'css-loader',
        ],
      },
      // SCSS/SASS 文件：同上，额外使用 sass-loader
      {
        test: /\.s[ac]ss$/i,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          'css-loader',
          'sass-loader',
        ],
      },
      // 图片资源：使用 asset/resource 输出到 images/ 目录
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource',
        generator: {
          filename: 'images/[hash][ext][query]',
        },
      },
      // 字体文件：输出到 fonts/ 目录
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
        generator: {
          filename: 'fonts/[hash][ext][query]',
        },
      },
    ],
  },

  // ==================== 代码分割与优化 ====================
  optimization: {
    splitChunks: {
      chunks: 'all', // 对所有 chunk 进行分割
      cacheGroups: {
        // 第三方库打包
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10,
        },
        // React 相关单独打包（更高优先级）
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)/,
          name: 'react',
          chunks: 'all',
          priority: 20,
        },
        // 公共模块打包（被引用 ≥2 次）
        common: {
          name: 'common',
          chunks: 'all',
          minChunks: 2,
          enforce: true, // 强制打包，忽略 minSize 等限制
          priority: 5,
        },
      },
    },
    runtimeChunk: 'single', // 将 webpack 运行时提取为单独文件
    minimize: isProduction, // 生产环境开启压缩
    minimizer: [
      // 使用 esbuild 快速压缩 JS（比 Terser 快很多）
      new TerserPlugin({
        minify: TerserPlugin.esbuildMinify,
        terserOptions: {
          target: 'es2015', // 压缩目标语法
        },
      }),
      // 压缩 CSS
      new CssMinimizerPlugin(),
    ],
  },

  // ==================== 插件 ====================
  plugins: [
    // 生成 index.html 并自动注入打包资源
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),

    // 生产环境专用插件
    ...(isProduction
      ? [
          // 提取 CSS 到单独文件
          new MiniCssExtractPlugin({
            filename: '[name].[contenthash:8].css',
            chunkFilename: '[name].[contenthash:8].chunk.css',
          }),

          // 生成 gzip 压缩文件，用于 Nginx 开启 gzip
          new CompressionPlugin({
            algorithm: 'gzip',
            test: /\.(js|css|html|svg)$/, // 压缩这些文件
            threshold: 8192, // 大于 8KB 才压缩
            deleteOriginalAssets: false, // 不删除原文件
          }),

          // 图片压缩（构建时）
          new ImageMinimizerPlugin({
            minimizer: {
              implementation: ImageMinimizerPlugin.imageminMinify,
              options: {
                plugins: [
                  ['gifsicle', { interlaced: true }],
                  ['jpegtran', { progressive: true }],
                  ['optipng', { optimizationLevel: 5 }],
                  [
                    'svgo',
                    { plugins: [{ name: 'preset-default', params: {} }] },
                  ],
                ],
              },
            },
          }),
        ]
      : []), // 开发环境不启用
  ],

  // ==================== 开发服务器 ====================
  devServer: {
    static: {
      directory: path.join(__dirname, 'dist'), // 静态资源目录
    },
    historyApiFallback: true, // 支持 SPA 路由（如 /about 不返回 404）
    hot: true, // 启用热更新（HMR）
    port: 5000, // 开发服务器端口
    open: true, // 启动时自动打开浏览器
    proxy: [
      {
        context: ['/api'], // 代理 /test 开头的请求
        target: 'http://localhost:3000/', // 代理到后端服务
        changeOrigin: true, // 修改请求头中的 origin
        pathRewrite: {
          '^/api': '', // 重写路径，去掉 /test 前缀
        },
        ...proxyLog, // 可能是自定义日志配置
      },
    ],
    watchFiles: ['src/**/*', 'public/**/*'], // 监听这些文件变化
    devMiddleware: {
      writeToDisk: false, // 不将文件写入磁盘（只在内存中）
    },
    client: {
      logging: 'info', // 控制台日志级别
    },
  },

  // ==================== Source Map ====================
  devtool: isProduction
    ? 'nosources-source-map' // 生产：有堆栈追踪，但不暴露源码
    : 'eval-cheap-module-source-map', // 开发：快 + 定位准确
};
```

