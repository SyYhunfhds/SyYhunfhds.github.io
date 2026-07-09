---
title: Lodash与实用工具库
date: 2026-07-09
footer: Trae编辑
---

# Lodash 与实用工具库

## Go 开发者已知

Go 标准库功能强大，很多通用功能都内置了，但一些 Lodash 提供的功能在 Go 中需要手写或引入第三方库。

```go
// Go 标准库已有的大量工具

// 字符串操作 —— strings 包
import "strings"
strings.ToUpper("hello")       // "HELLO"
strings.TrimSpace("  hi  ")   // "hi"
strings.Split("a,b,c", ",")   // ["a", "b", "c"]
strings.Join([]string{"a","b"}, "-") // "a-b"

// 排序 —— sort 包
import "sort"
sort.Ints([]int{3, 1, 2})
sort.Strings([]string{"c", "a", "b"})

// Go 没有的（需手写或第三方库）：
// 1. 去重（需手写 map）
// 2. 深度克隆（需 reflect 或第三方）
// 3. 合并对象（需手写循环）
// 4. Debounce/Throttle（无内置，需实现）
// 5. Memoize（无内置）
// 6. Chunk（无内置）

// Go 第三方工具库示例
// import "github.com/samber/lo"  // 类似 Lodash 的 Go 库
// lo.Uniq([]int{1, 2, 2, 3})    // 去重
// lo.Chunk([]int{1,2,3,4}, 2)   // 分块
```

## TS 怎么做

### lodash vs lodash-es

```bash
# 安装
npm install lodash
npm install @types/lodash    # TS 类型定义

# 或者 ESM 版本
npm install lodash-es
```

```ts
// lodash（CommonJS） vs lodash-es（ES Module）
// lodash-es 支持 tree-shaking，推荐在打包工具中使用

// lodash（CommonJS）
import _ from "lodash";
_.chunk([1, 2, 3, 4], 2);

// lodash-es（ESM，推荐）
import chunk from "lodash-es/chunk";
chunk([1, 2, 3, 4], 2);
```

### 集合操作

```ts
// chunk —— 分块
import { chunk } from "lodash-es";

chunk([1, 2, 3, 4, 5], 2);
// [[1, 2], [3, 4], [5]]

// uniq —— 去重
import { uniq, uniqBy, uniqWith } from "lodash-es";

uniq([2, 1, 2, 3, 1]);          // [2, 1, 3]
uniqBy([{ id: 1 }, { id: 1 }, { id: 2 }], "id");
// [{ id: 1 }, { id: 2 }]

// groupBy —— 分组
import { groupBy } from "lodash-es";

interface User { name: string; role: string; age: number; }
const users: User[] = [
    { name: "Alice", role: "admin", age: 25 },
    { name: "Bob", role: "user", age: 17 },
    { name: "Charlie", role: "admin", age: 30 },
];

const byRole = groupBy(users, "role");
// { admin: [Alice, Charlie], user: [Bob] }

// orderBy —— 排序
import { orderBy } from "lodash-es";

const sorted = orderBy(users, ["role", "age"], ["asc", "desc"]);
// 先按 role 升序，再按 age 降序

// keyBy —— 以某个字段为键建立对象
import { keyBy } from "lodash-es";

const byId = keyBy(users, "id");
// { "1": { id: 1, ... }, "2": { id: 2, ... } }

// partition —— 分区
import { partition } from "lodash-es";

const [adults, minors] = partition(users, u => u.age >= 18);
// adults: [Alice, Charlie], minors: [Bob]
```

### 对象操作

```ts
// merge —— 深度合并（类似 Go 的手动合并）
import { merge } from "lodash-es";

const defaults = { theme: "light", lang: "en", debug: false };
const overrides = { lang: "zh", debug: true };
const config = merge({}, defaults, overrides);
// { theme: "light", lang: "zh", debug: true }
// 注意：merge 会深度合并嵌套对象

// cloneDeep —— 深度克隆
import { cloneDeep } from "lodash-es";

const original = { nested: { value: 42 }, arr: [1, 2, 3] };
const cloned = cloneDeep(original);
cloned.nested.value = 99;
console.log(original.nested.value); // 42（不受影响）

// 对比 JSON.parse(JSON.stringify(obj)) 的局限：
// - 不支持 Date → 变成 string
// - 不支持 undefined → 被忽略
// - 不支持 function → 被忽略
// - 不支持 RegExp → 变成 {}
// - 不支持循环引用 → 报错

// pick / omit —— 选取/排除属性
import { pick, omit } from "lodash-es";

interface UserProfile {
    id: number;
    name: string;
    email: string;
    password: string;
    createdAt: Date;
}

const user: UserProfile = {
    id: 1,
    name: "Alice",
    email: "alice@example.com",
    password: "secret123",
    createdAt: new Date(),
};

// 只返回安全字段
const publicProfile = pick(user, ["id", "name", "email"]);
// { id: 1, name: "Alice", email: "alice@example.com" }

// 排除敏感字段
const safeUser = omit(user, ["password"]);
// { id: 1, name: "Alice", email: "...", createdAt: Date }

// get —— 安全路径取值
import { get } from "lodash-es";

const data = {
    user: {
        address: {
            city: "Beijing",
        },
    },
};

// 安全访问嵌套属性 —— 不会因中间值为 null/undefined 而崩溃
const city = get(data, "user.address.city", "default");
// "Beijing"
const zip = get(data, "user.address.zip", "N/A");
// "N/A"（路径不存在返回默认值）

// set —— 按路径设置值
import { set } from "lodash-es";

const obj = {};
set(obj, "a.b.c", 42);
// obj = { a: { b: { c: 42 } } }
```

### 函数工具

```ts
// debounce —— 防抖（Go 无内置）
import { debounce } from "lodash-es";

// 输入框搜索 —— 用户停止输入 300ms 后才触发
const searchInput = document.querySelector<HTMLInputElement>("#search");

const debouncedSearch = debounce(async (query: string) => {
    const results = await fetch(`/api/search?q=${query}`);
    console.log(await results.json());
}, 300);

searchInput?.addEventListener("input", (e) => {
    debouncedSearch((e.target as HTMLInputElement).value);
});

// 带 leading 选项：第一次立即执行
const immediateDebounce = debounce(
    () => console.log("Called"),
    300,
    { leading: true, trailing: true }
);

// cancel —— 取消未执行的防抖
debouncedSearch.cancel();

// flush —— 立即执行未执行的防抖
debouncedSearch.flush();
```

::: code-tabs#lang

@tab TypeScript (lodash throttle)

```ts
// throttle —— 节流（Go 无内置）
import { throttle } from "lodash-es";

// 滚动事件 —— 最多每 200ms 触发一次
window.addEventListener("scroll", throttle(() => {
    console.log("Scroll position:", window.scrollY);
}, 200));

// 带配置：禁用第一次和最后一次调用
const strictThrottle = throttle(fn, 1000, {
    leading: false,
    trailing: false,
});
```

@tab Go（手写节流）

```go
// Go 手写节流
import (
    "sync"
    "time"
)

type Throttle struct {
    mu    sync.Mutex
    last  time.Time
    delay time.Duration
}

func (t *Throttle) Call(fn func()) {
    t.mu.Lock()
    defer t.mu.Unlock()
    now := time.Now()
    if now.Sub(t.last) >= t.delay {
        t.last = now
        fn()
    }
}
```

:::

```ts
// memoize —— 记忆化（缓存函数结果）
import { memoize } from "lodash-es";

// 开销大的计算
function expensiveComputation(n: number): number {
    console.log("Computing...");
    return n * n;
}

const memoizedFn = memoize(expensiveComputation);
console.log(memoizedFn(5)); // "Computing..." 25
console.log(memoizedFn(5)); // 25（从缓存读取）
console.log(memoizedFn(10)); // "Computing..." 100

// 自定义缓存键
const memoizedByArgs = memoize(
    (a: number, b: number) => a + b,
    (a, b) => `${a}-${b}` // 自定义缓存 key
);

// 清除缓存
memoizedFn.cache.clear?.();
```

## 差异分析

| 维度 | Go | TypeScript (Lodash) |
|------|-----|-------------------|
| **工具库生态** | 标准库丰富，第三方如 `samber/lo` | Lodash(es) 是事实标准 |
| **集合操作** | 需手写循环 | `chunk/uniq/groupBy/partition` 内置 |
| **对象深度合并** | 手写或 `mapstructure` | `merge` / `defaultsDeep` |
| **深度克隆** | 手写或 `copier` | `cloneDeep`（比 JSON 方案更完善） |
| **路径取值** | 需手写 || `get` / `set` 安全路径 |
| **防抖/节流** | 无内置，需手写 | `debounce` / `throttle` |
| **记忆化** | 手写 `sync.Map` | `memoize`（支持 LRU 扩展） |
| **类型安全** | 编译期强类型 | 泛型类型安全 |

## Bad Practice

### 1. 导入整个 lodash

```ts
// Bad: 导入整个 lodash（增加打包体积）
import _ from "lodash";
_.chunk([1, 2, 3, 4], 2);
_.uniq([1, 2, 2, 3]);
_.merge(obj1, obj2);

// Best: 按需导入（配合 tree-shaking）
import chunk from "lodash-es/chunk";
import uniq from "lodash-es/uniq";
import merge from "lodash-es/merge";

// 或使用 lodash-es 命名导入（需确保打包工具支持 tree-shaking）
import { chunk, uniq, merge } from "lodash-es";
```

### 2. 能用原生 API 替代却用 Lodash

```ts
// Bad: Lodash 方法有原生等价物
_.assign(obj, source);      // → Object.assign(obj, source)
_.isArray(value);           // → Array.isArray(value)
_.keys(obj);                 // → Object.keys(obj)
_.values(obj);               // → Object.values(obj)
_.toUpper(str);              // → str.toUpperCase()
_.startsWith(str, "a");      // → str.startsWith("a")
_.includes(arr, 1);          // → arr.includes(1)
_.find(arr, fn);             // → arr.find(fn)
_.filter(arr, fn);           // → arr.filter(fn)

// Best: 优先使用原生 API
// 只有原生 API 不支持时再考虑 Lodash
// 例如：cloneDeep、merge、debounce、chunk 等
```

### 3. 使用 Lodash 替代原生 Map/Set

```ts
// Bad: 用 Lodash 方法操作 Object 模拟 Map
_.has(obj, "key");
_.get(obj, "key");
_.set(obj, "key", value);

// Best: 使用原生 Map
const map = new Map<string, number>();
map.has("key");
map.get("key");
map.set("key", value);
```

### 4. 深度克隆未注意循环引用

```ts
// Bad: JSON 方案处理不了循环引用
const obj: any = { name: "Alice" };
obj.self = obj;
// JSON.parse(JSON.stringify(obj)); // 报错！

// Best: 使用 cloneDeep
import { cloneDeep } from "lodash-es";
const cloned = cloneDeep(obj); // 正确处理循环引用
```

## Best Practice

### 1. 封装按需导入工具

```ts
// Best: 统一导出需要的 Lodash 方法
// utils/lodash.ts
export { default as chunk } from "lodash-es/chunk";
export { default as uniqBy } from "lodash-es/uniqBy";
export { default as groupBy } from "lodash-es/groupBy";
export { default as cloneDeep } from "lodash-es/cloneDeep";
export { default as merge } from "lodash-es/merge";
export { default as get } from "lodash-es/get";
export { default as set } from "lodash-es/set";
export { default as debounce } from "lodash-es/debounce";
export { default as throttle } from "lodash-es/throttle";
export { default as memoize } from "lodash-es/memoize";

// 使用时直接从统一文件导入
import { chunk, cloneDeep, debounce } from "@/utils/lodash";
```

### 2. 优先原生 + Lodash 补齐

```ts
// Best: 组合使用原生 API 和 Lodash
// 原生能做的用原生，Lodash 做原生做不到的

// 数组去重（简单类型用原生 Set）
const uniquePrimitives = [...new Set([1, 2, 2, 3])];

// 对象数组去重用 Lodash（Set 无法比较对象引用）
import { uniqBy } from "lodash-es";
const uniqueObjects = uniqBy(
    [{ id: 1 }, { id: 1 }, { id: 2 }],
    "id"
);

// 浅合并用原生展开
const merged = { ...defaults, ...overrides };

// 深合并用 Lodash
import { merge } from "lodash-es";
const deepMerged = merge({}, defaults, overrides);
```

### 3. 使用 FP 模块的函数式风格

```ts
// Best: Lodash FP 模块 —— 自动柯里化、数据最后
import { map, filter, take } from "lodash-es/fp";

// 普通 Lodash
import _ from "lodash";
const result1 = _.take(_.filter(_.map([1, 2, 3], n => n * 2), n => n > 2), 2);

// Lodash FP —— 更符合函数式组合
const result2 = take(2, filter(n => n > 2, map(n => n * 2, [1, 2, 3])));
// 或使用 flow
import { flow } from "lodash-es/fp";
const process = flow(
    map((n: number) => n * 2),
    filter((n: number) => n > 2),
    take(2)
);
const result3 = process([1, 2, 3]);
```

::: tip 总结

1. 优先使用原生 API，原生不满足时再用 Lodash
2. 始终按需导入（`lodash-es/method`），避免全量导入
3. `cloneDeep` 比 `JSON.parse(JSON.stringify())` 更完善
4. `get`/`set` 安全路径取值避免嵌套属性访问崩溃
5. `debounce`/`throttle` 是前端高频交互的必备工具
6. 注意 Go 开发者到 TS 的转换：手写循环 → Lodash 声明式方法

:::
