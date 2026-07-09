---
title: ESLint + Prettier 代码规范
date: 2026-07-09
footer: Trae AI 创作
---

# ESLint + Prettier 代码规范

> **面向读者**：有 Go 后端经验的开发者。Go 生态有 `gofmt`（强制格式化）和 `go vet` / `golangci-lint`（静态分析），前端生态通过 **ESLint** + **Prettier** 两套工具分别解决"逻辑规范"和"格式规范"问题。理解它们的分工和配合是团队协作的基础。

---

## 一、ESLint：静态分析（类比 golangci-lint / go vet）

ESLint 分析代码的**逻辑正确性**和**编码规范**，类似 `golangci-lint` 但更细粒度：

```js
// ESLint 能发现的问题示例

// 1. 未使用的变量（类似 Go unused 变量编译错误）
const unused = 42; // ❌ ESLint: 'unused' is assigned a value but never used

// 2. 不安全的可选链
const name = user?.name || 'Guest'; // ❌ 建议用 ?? 代替 ||
const name = user?.name ?? 'Guest'; // ✅

// 3. 隐式类型转换（类似 Go 的类型安全）
if (value == null) { } // ❌ 建议用 === 或明确判断
if (value === null || value === undefined) { } // ✅
```

```go
// Go 中这些问题大部分是编译错误而非 lint 检查
// unused := 42          // 编译错误：unused declared but not used
// if value == nil { }   // 编译通过，但逻辑可能不对
```

### 1.1 ESLint 配置文件

```js
// eslint.config.js（新版 Flat Config）
import js from '@eslint/js';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';

export default [
  js.configs.recommended,
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
    },
    rules: {
      // TS 专属规则
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'warn',

      // 通用规则
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'prefer-const': 'error',
      'no-var': 'error',
    },
  },
];
```

```js
// 传统 .eslintrc.cjs（仍广泛使用）
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    // 'plugin:vue/vue3-recommended',  // Vue 项目用
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
  },
};
```

::: info ESLint 规则级别

| 级别      | 值      | 行为             | 类似 Go                  |
| --------- | ------- | ---------------- | ------------------------ |
| `off`     | `0`     | 关闭规则         | 禁用该检查               |
| `warn`    | `1`     | 警告，不阻断编译 | `go vet` 告警            |
| `error`   | `2`     | 错误，阻断编译   | 编译错误（如未使用变量） |

:::

---

## 二、Prettier：格式化（类比 gofmt）

Prettier 是**格式化工具**，只关心代码的"长得是否整齐"，不关心逻辑。类比 `gofmt`，但**`gofmt` 是 Go 的强制标准**，而 Prettier 需要手动配置。

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

| 配置项              | 推荐值       | 说明                     | 类比 Go                   |
| ------------------- | ------------ | ------------------------ | ------------------------- |
| `semi`              | `true`       | 语句末尾加分号           | Go 自动插入分号            |
| `singleQuote`       | `true`       | 使用单引号               | Go 使用双引号              |
| `trailingComma`     | `"all"`      | 多行末尾加逗号           | Go 无此概念                |
| `printWidth`        | `100`        | 行宽上限                 | 类似 `gofmt` 自动换行      |
| `tabWidth`          | `2`          | 缩进空格数               | Go 用 tab（8 字符宽）      |
| `arrowParens`       | `"always"`   | 箭头函数参数始终加括号   | Go 函数参数始终有括号      |

```js
// 格式化前
const fn=a=>{return a+1}
const obj={name:'Alice',age:30,city:'Beijing'}

// 格式化后（Prettier）
const fn = (a) => {
  return a + 1;
};
const obj = {
  name: 'Alice',
  age: 30,
  city: 'Beijing',
};
```

::: tip Prettier 和 gofmt 的关键区别

| 特性           | gofmt                  | Prettier                 |
| -------------- | ---------------------- | ------------------------ |
| 语言           | 仅 Go                  | JS/TS/CSS/JSON/MD 等多语言 |
| 强制标准       | Go 官方强制，无配置项   | 可配置，团队协商          |
| 命令行         | `gofmt -l -w`          | `prettier --write`       |
| IDE 自动保存   | 通常手动触发           | VS Code 插件自动保存      |
| 是否可配置     | **不可配置**（统一标准） | 有限配置                  |

:::

---

## 三、ESLint + Prettier 集成

### 3.1 职责划分

```
ESLint  = 逻辑规则（禁止 var、禁止 any、必须 return 类型）
Prettier = 格式规则（缩进、引号、分号、行宽）
```

::: caution 规则冲突

**Prettier 负责格式，ESLint 负责逻辑**——绝不混合。否则会遇到矛盾规则：

```js
// ESLint 说：必须加分号
// Prettier 说：不加分号
// → 永远有冲突，永远修不完 ❌

// 正确做法：关闭 ESLint 中与格式相关的规则
```

```json
// 让 ESLint 忽略格式规则，全部交给 Prettier
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"                       // 必须放在最后，覆盖格式规则
  ]
}
```

:::

### 3.2 推荐集成方式

```bash
# 安装依赖
pnpm add -D eslint prettier
pnpm add -D eslint-config-prettier          # 关闭 ESLint 中与 Prettier 冲突的规则
pnpm add -D eslint-plugin-prettier          # 将 Prettier 作为 ESLint 规则运行（可选）
pnpm add -D @typescript-eslint/eslint-plugin @typescript-eslint/parser
```

```json
// .eslintrc.cjs —— 集成 Prettier
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',             // 必须最后，禁用冲突的 ESLint 格式规则
  ],
  plugins: ['@typescript-eslint', 'prettier'],
  rules: {
    'prettier/prettier': 'error',  // 不符合 Prettier 格式的视为 ESLint 错误
  },
};
```

```json
// 或者更轻量的方式（推荐）：
// 只使用 eslint-config-prettier 关闭冲突规则
// Prettier 通过 VS Code 插件独立运行
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ]
}
```

---

## 四、@typescript-eslint 插件

TS 项目必须使用 `@typescript-eslint` 插件，它替换了 ESLint 内置的 JS 解析器：

```js
// 关键规则
{
  "rules": {
    // ❌ 禁止显式 any
    "@typescript-eslint/no-explicit-any": "warn",

    // ❌ 禁止未使用的变量（类似 Go 编译错误）
    "@typescript-eslint/no-unused-vars": ["error", {
      "argsIgnorePattern": "^_",  // _ 开头的参数忽略
      "varsIgnorePattern": "^_"
    }],

    // ✅ 要求函数显式返回类型（类似 Go）
    "@typescript-eslint/explicit-function-return-type": "warn",

    // ❌ 禁止空接口（Go 中空接口常见，TS 中很少需要）
    "@typescript-eslint/no-empty-interface": "error",

    // ✅ 优先使用 interface 而非 type alias
    "@typescript-eslint/consistent-type-definitions": ["warn", "interface"],

    // ❌ 禁止 require（统一使用 ESM import）
    "@typescript-eslint/no-var-requires": "error",
  }
}
```

```go
// 类比 Go——很多 TS lint 规则在 Go 中是编译时强制而非 lint
// 未使用的变量 → 编译错误
// 未使用的 import → 编译错误
// 隐式类型转换 → 不允许
```

---

## 五、VS Code 集成

在 VS Code 中配置保存时自动格式化，类比 Go 中 `gopls` 的自动格式化：

```json
// .vscode/settings.json（项目级配置，应提交到仓库）
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  // 某些文件类型不自动格式化
  "[markdown]": {
    "editor.formatOnSave": false
  }
}
```

```json
// .vscode/extensions.json（推荐插件）
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode"
  ]
}
```

::: tip

保存文件时，VS Code 会自动执行：
1. **Prettier** → 格式化代码
2. **ESLint** → 自动修复可修复的问题（如排序 import）

这相当于 Go 中保存文件时自动执行 `gofmt -w` + `go vet`。

:::

---

## 六、Husky + lint-staged：提交前检查

类比 Go 项目中的 pre-commit hook，但更系统化：

```bash
# 安装
pnpm add -D husky lint-staged
npx husky init
```

```json
// package.json
{
  "scripts": {
    "lint": "eslint src --ext .ts,.tsx",
    "format": "prettier --write 'src/**/*.{ts,tsx,css,json}'",
    "lint-staged": "lint-staged"
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",           // 先修复 ESLint 问题
      "prettier --write"        // 再格式化
    ],
    "*.{css,json,md}": [
      "prettier --write"
    ]
  }
}
```

```bash
# .husky/pre-commit（创建后自动生成）
npx lint-staged
```

### 6.1 工作流程

```
开发者提交代码
  → Husky 拦截 pre-commit 事件
  → lint-staged 运行
    → 对暂存文件执行 ESLint 修复
    → 对暂存文件执行 Prettier 格式化
  → 如果有问题，提交被阻断
  → 如果通过，代码被提交
```

::: info 类比 Go

```makefile
# Go 项目中的等效 pre-commit hook
# .githooks/pre-commit
#!/bin/sh
go fmt ./...
go vet ./...
golangci-lint run
```

Go 的 `go fmt` + `go vet` + `golangci-lint` 做了和 ESLint + Prettier + Husky 一样的事情。

:::

---

## 七、推荐配置模板

### 完整项目配置

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

```js
// .eslintrc.cjs
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-unused-vars': [
      'error',
      { argsIgnorePattern: '^_' },
    ],
    '@typescript-eslint/explicit-function-return-type': 'off',
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'prefer-const': 'error',
    'no-var': 'error',
  },
};
```

---

## 八、Bad vs Best

### Bad：规则冲突

```json
// ❌ ESLint 要求加分号，但 Prettier 配置不加
// .eslintrc
{ "rules": { "semi": ["error", "always"] } }

// .prettierrc
{ "semi": false }
```

```js
// 结果：永远修不完的格式冲突
const a = 1  // Prettier 删分号 → ESLint 报错 → 加回分号 ⋯⋯
```

### Best：Prettier 负责格式，ESLint 负责逻辑

```json
// ✅ 清晰分工
// .eslintrc.cjs
{
  "extends": [
    "eslint:recommended",
    "prettier"           // 关闭 ESLint 中所有格式相关规则
  ],
  "rules": {
    "no-unused-vars": "error",        // ✅ 逻辑规则
    "prefer-const": "error",           // ✅ 逻辑规则
    // 不设置任何格式规则（交给 Prettier）
  }
}

// .prettierrc
{
  "semi": true,
  "singleQuote": true
}
```

---

## 总结

| 概念                     | 前端工具          | Go 类比                 |
| ------------------------ | ----------------- | ----------------------- |
| 代码格式化               | Prettier          | `gofmt`                 |
| 静态分析 / 逻辑检查      | ESLint            | `go vet` / `golangci-lint` |
| TS 专用规则              | `@typescript-eslint` | 编译器内置             |
| 提交前检查               | Husky + lint-staged | pre-commit hook        |
| VS Code 自动修复         | ESLint + Prettier 插件 | `gopls` + 保存自动格式化 |
| 核心原则                 | 分工明确，不混用   | `gofmt` 统一标准        |

下一站：[包管理器与构建工具入门](./07-包管理器与构建工具入门.md)，学习如何管理依赖和构建项目。
