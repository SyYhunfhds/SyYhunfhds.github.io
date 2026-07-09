---
title: Array与集合操作
date: 2026-07-09
footer: Trae编辑
---

# Array 与集合操作

## Go 开发者已知

在 Go 中，数组是定长值类型，切片是变长引用类型。Go **没有**内置的 `map`/`filter`/`reduce` 等高阶数组方法，需要手写 `for range` 循环：

```go
// Go 数组 vs 切片
var arr [3]int = [3]int{1, 2, 3} // 定长数组（值类型）
sli := []int{1, 2, 3}            // 变长切片（引用类型）

// Go 手写 map/filter/reduce
nums := []int{1, 2, 3, 4, 5}

// Map —— 手写循环
var doubled []int
for _, n := range nums {
    doubled = append(doubled, n*2)
}

// Filter —— 手写循环
var evens []int
for _, n := range nums {
    if n%2 == 0 {
        evens = append(evens, n)
    }
}

// Reduce —— 手写循环
sum := 0
for _, n := range nums {
    sum += n
}
```

Go 1.21+ 引入了 `slices` 包，但功能仍然有限：

```go
import "slices"

slices.Contains(nums, 3)     // 检查是否包含
slices.Index(nums, 3)        // 查找索引
slices.Sort(nums)            // 排序
slices.Reverse(nums)         // 反转
slices.Compact(nums)         // 去重（相邻重复）
```

## TS 怎么做

### Array\<T\> 类型与元组

```ts
// 数组类型声明
const nums: number[] = [1, 2, 3];
const strs: Array<string> = ["a", "b", "c"]; // 泛型写法，等价于 string[]

// 元组 —— 定长且每个位置类型不同
const pair: [string, number] = ["Alice", 30];
const httpStatus: [number, string] = [200, "OK"];

// 可变元组（Variadic Tuple，TS 4.0+）
type Args = [string, ...number[]];
const args: Args = ["hello", 1, 2, 3];

// 标签元组（Labeled Tuple，TS 4.0+）
type Range = [start: number, end: number];
function inRange(value: number, range: Range): boolean {
    return value >= range[0] && value <= range[1];
}

// readonly 数组
const readonlyNums: readonly number[] = [1, 2, 3];
const readonlyNums2: ReadonlyArray<number> = [1, 2, 3];
// readonlyNums.push(4); // 编译错误
```

### 数组高阶方法 —— 链式调用

```ts
// 核心方法一览
interface Array<T> {
    map<U>(fn: (value: T, index: number, array: T[]) => U): U[];
    filter<S extends T>(fn: (value: T, index: number, array: T[]) => value is S): S[];
    reduce<U>(fn: (acc: U, value: T, index: number, array: T[]) => U, init: U): U;
    find(fn: (value: T, index: number, obj: T[]) => boolean): T | undefined;
    some(fn: (value: T, index: number, array: T[]) => boolean): boolean;
    every(fn: (value: T, index: number, array: T[]) => boolean): boolean;
    forEach(fn: (value: T, index: number, array: T[]) => void): void;
}
```

::: code-tabs#lang

@tab TypeScript

```ts
// 链式调用 —— Go 要写很多循环才能实现
interface User {
    id: number;
    name: string;
    age: number;
    active: boolean;
}

const users: User[] = [
    { id: 1, name: "Alice", age: 25, active: true },
    { id: 2, name: "Bob", age: 17, active: true },
    { id: 3, name: "Charlie", age: 30, active: false },
];

// TS 一行搞定的事
const activeAdultNames = users
    .filter(u => u.active && u.age >= 18)     // 筛选活跃成年人
    .map(u => u.name)                          // 提取名字
    .sort();                                   // 排序

// => ["Alice"]
```

@tab Go

```go
// Go 需要多行手写循环
type User struct {
    ID     int
    Name   string
    Age    int
    Active bool
}

func ActiveAdultNames(users []User) []string {
    var result []string
    for _, u := range users {
        if u.Active && u.Age >= 18 {
            result = append(result, u.Name)
        }
    }
    sort.Strings(result)
    return result
}
```

:::

### 不可变操作方法（ES2023+）

```ts
// 传统方法会修改原数组
const arr = [3, 1, 2];
arr.sort();     // 原数组被修改
arr.reverse();  // 原数组被修改

// 不可变方法 —— 返回新数组
const sorted = arr.toSorted();          // 返回排序后的新数组
const reversed = arr.toReversed();      // 返回反转后的新数组
const spliced = arr.toSpliced(1, 1);    // 返回删除元素后的新数组
const withVal = arr.with(0, 99);        // 返回替换元素后的新数组

// 原数组不受影响
console.log(arr);       // [3, 1, 2]（不变）
console.log(sorted);    // [1, 2, 3]
```

### 从数组创建新结构

```ts
// flat —— 展平嵌套数组
const nested = [1, [2, [3, 4]]];
nested.flat();              // [1, 2, [3, 4]]（默认深度1）
nested.flat(2);             // [1, 2, 3, 4]
nested.flat(Infinity);      // 完全展平（递归）

// flatMap —— map + flat 一步到位
const sentences = ["Hello world", "Foo bar"];
const words = sentences.flatMap(s => s.split(" "));
// ["Hello", "world", "Foo", "bar"]
// 等价于 sentences.map(s => s.split(" ")).flat()
```

## 差异分析

| 维度 | Go | TypeScript |
|------|-----|-----------|
| **高阶方法** | 无内置，需手写 `for range` | `map/filter/reduce/find/some/every` 内置 |
| **链式调用** | 不支持（需手写循环） | 原生支持链式调用 |
| **不可变操作** | 无内置，需手动拷贝 | `toSorted/toReversed/toSpliced/with`（ES2023+） |
| **元组类型** | 用 `struct` 或数组模拟 | 原生元组 `[T, U]` + 标签元组 + 可变元组 |
| **数组定长** | 数组定长 `[3]int`（值类型） | 无定长数组概念，元组模拟 |
| **类型安全** | 编译期强类型 | 编译期强类型 + 泛型约束 |
| **性能** | 零开销 | 链式调用有中间数组创建开销 |

## Bad Practice

### 1. forEach 中使用 async/await

```ts
// Bad: forEach 不等待 async 函数
async function fetchUser(id: number): Promise<User> { /* ... */ }

const ids = [1, 2, 3];
ids.forEach(async (id) => {
    const user = await fetchUser(id); // 不会等待！并发执行
});
// 所有请求同时触发，forEach 立即返回

// 如果想串行执行：
// for...of 可以
for (const id of ids) {
    const user = await fetchUser(id); // 正确串行
}

// 如果想并行执行：
const users = await Promise.all(ids.map(id => fetchUser(id))); // 正确并行
```

::: caution forEach + async 陷阱

`Array.prototype.forEach` 不会等待 async 回调完成。如果你需要等待异步操作，用 `for...of`（串行）或 `Promise.all`（并行）。

:::

### 2. 过度链式调用导致性能问题

```ts
// Bad: 多次遍历
const result = largeArray
    .map(x => x * 2)       // 第一次遍历
    .filter(x => x > 10)   // 第二次遍历
    .map(x => x.toString()) // 第三次遍历
    .filter(x => x.length > 2); // 第四次遍历

// 更好的做法：单次遍历
function processLargeArray(arr: number[]): string[] {
    const result: string[] = [];
    for (const x of arr) {
        const doubled = x * 2;
        if (doubled > 10) {
            const str = doubled.toString();
            if (str.length > 2) {
                result.push(str);
            }
        }
    }
    return result;
}
```

### 3. 对 null/undefined 数组调用方法

```ts
// Bad: 未处理 null/undefined
function getNames(users?: User[]) {
    return users.map(u => u.name); // 如果 users 是 undefined，运行时崩溃
}

// 使用可选链式调用
function getNamesSafe(users?: User[]) {
    return users?.map(u => u.name) ?? [];
}
```

### 4. 混淆 splice 与 slice

```ts
// Bad: splice 修改原数组，slice 不修改
const arr = [1, 2, 3, 4, 5];
const removed = arr.splice(2, 1); // arr 变为 [1, 2, 4, 5]，removed = [3]
const sliced = arr.slice(2, 4);   // arr 不变，sliced = [4, 5]
```

## Best Practice

### 1. 类型安全的数组工具函数

```ts
// Best: 泛型工具函数
function groupBy<T, K extends string | number>(
    items: T[],
    keyFn: (item: T) => K
): Record<K, T[]> {
    return items.reduce((acc, item) => {
        const key = keyFn(item);
        if (!acc[key]) acc[key] = [];
        acc[key].push(item);
        return acc;
    }, {} as Record<K, T[]>);
}

// 使用
const users = [
    { name: "Alice", role: "admin" },
    { name: "Bob", role: "user" },
    { name: "Charlie", role: "admin" },
];
const byRole = groupBy(users, u => u.role);
// { admin: [Alice, Charlie], user: [Bob] }
```

### 2. 优先使用不可变方法

```ts
// Best: 使用 toSorted 等不可变方法
const numbers = [3, 1, 4, 1, 5];
const processed = numbers
    .toSorted((a, b) => a - b)    // 排序，不修改原数组
    .filter(n => n > 2);          // 筛选

console.log(numbers);   // [3, 1, 4, 1, 5]（不变）
console.log(processed); // [3, 4, 5]
```

### 3. 使用类型守卫在 filter 中缩小类型

```ts
// Best: 类型守卫 filter
type MaybeNumber = number | undefined;

const items: MaybeNumber[] = [1, undefined, 2, undefined, 3];

// filter(Boolean) 不够精确
const a = items.filter(Boolean); // 类型为 MaybeNumber[]（不正确）

// 使用类型守卫
function isDefined<T>(value: T | undefined): value is T {
    return value !== undefined;
}

const b = items.filter(isDefined); // 类型为 number[] ✅
```

### 4. 用 reduce 替代多次链式调用

```ts
// Best: reduce 做一次遍历完成多种操作
interface Stats {
    sum: number;
    count: number;
    min: number;
    max: number;
}

function computeStats(numbers: number[]): Stats {
    return numbers.reduce<Stats>(
        (acc, n) => ({
            sum: acc.sum + n,
            count: acc.count + 1,
            min: Math.min(acc.min, n),
            max: Math.max(acc.max, n),
        }),
        { sum: 0, count: 0, min: Infinity, max: -Infinity }
    );
}

const stats = computeStats([1, 2, 3, 4, 5]);
// { sum: 15, count: 5, min: 1, max: 5 }
```

### 5. 为元组类型添加可读性

```ts
// Best: 使用标签元组
type Coordinate = [x: number, y: number, z: number];
type RangeResult = [min: number, max: number, count: number];

function findRange(nums: number[]): RangeResult {
    const min = Math.min(...nums);
    const max = Math.max(...nums);
    return [min, max, nums.length];
}

const [minVal, maxVal, total] = findRange([1, 2, 3]);
// 标签元组让解构的意图更清晰
```

::: tip 总结

TypeScript 的数组 API 相比 Go 丰富得多，链式调用和不可变操作让数据转换更声明式。关键是要注意：链式调用会产生中间数组，处理大数据集时可能影响性能；forEach 与 async 不兼容；优先用不可变方法避免副作用。

:::
