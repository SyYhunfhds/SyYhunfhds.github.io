---
title: 03-Map-Set-WeakMap与数据结构
date: 2026-07-09
footer: Trae编辑
---

# Map / Set / WeakMap 与数据结构

## Go 开发者已知

Go 有内置的 `map` 类型和数组/切片，但没有内置的 `Set` 或其他集合类型。Go 中没有弱引用概念。

```go
// Go 的 map —— 基础映射
m := make(map[string]int)
m["key"] = 42
v, ok := m["key"] // v=42, ok=true
delete(m, "key")  // 删除

// Go 没有 Set，用 map[T]struct{} 模拟
set := make(map[int]struct{})
set[1] = struct{}{}
set[2] = struct{}{}

// 判断存在
if _, exists := set[1]; exists {
    fmt.Println("1 is in set")
}

// 遍历 Set
for k := range set {
    fmt.Println(k)
}

// 删除
delete(set, 1)
```

Go 的有序性：Go 的 map 遍历顺序是**随机**的（设计如此）。

```go
// Go 没有 TypedArray 这种显式的字节视图概念
// 但可以用 []byte 表示字节序列
var buf []byte = []byte{0x48, 0x65, 0x6C, 0x6C, 0x6F} // "Hello"
```

## TS 怎么做

### Map\<K, V\> —— 真正的哈希映射

```ts
// Map —— 键可以是任意类型！
const map = new Map<string, number>();
map.set("one", 1);
map.set("two", 2);
console.log(map.get("one"));   // 1
console.log(map.has("three")); // false
map.delete("two");
console.log(map.size);         // 1

// 键可以是对象、函数等任意类型
const objKey = { id: 1 };
const fnKey = () => {};
const complexMap = new Map<object, string>();
complexMap.set(objKey, "object value");
complexMap.set(fnKey, "function value");

// 遍历 —— Map 保持插入顺序
const colors = new Map([
    ["R", "Red"],
    ["G", "Green"],
    ["B", "Blue"],
]);

for (const [key, value] of colors) {
    console.log(key, value); // R Red → G Green → B Blue
}

colors.forEach((value, key) => {
    console.log(key, value);
});

// Map 与 Object 互转
const obj = Object.fromEntries(colors); // { R: "Red", G: "Green", B: "Blue" }
const mapFromObj = new Map(Object.entries(obj));

// Map 与 Array 互转
const arr = [...colors];        // [["R","Red"],["G","Green"],["B","Blue"]]
const mapFromArr = new Map(arr);
```

::: info Map vs Object

| 特性 | Map | Object |
|------|-----|--------|
| 键类型 | 任意类型（对象、函数、原始值） | 只能是 string / symbol |
| 插入顺序 | 保持 | 基本保持（有例外） |
| 大小属性 | `.size` 属性 | `Object.keys().length` |
| 遍历 | `for...of` / `.forEach` | `for...in` / `Object.keys()` |
| 性能 | 频繁增删更优 | 适用于结构化数据 |
| JSON 序列化 | 不支持 | `JSON.stringify()` 支持 |
| 原型继承 | 无 | 有原型链继承 |

:::

### Set\<T\> —— 真正的集合

```ts
// Set —— 自动去重
const set = new Set<number>();
set.add(1);
set.add(2);
set.add(1); // 重复，被忽略
console.log(set.size); // 2
console.log(set.has(1)); // true
set.delete(2);

// 从数组创建 Set（常用去重技巧）
const arr = [1, 2, 2, 3, 3, 3];
const unique = [...new Set(arr)]; // [1, 2, 3]

// Set 操作 —— 需要手动实现并集/交集/差集
const setA = new Set([1, 2, 3]);
const setB = new Set([2, 3, 4]);

// 并集
const union = new Set([...setA, ...setB]);        // {1, 2, 3, 4}

// 交集
const intersection = new Set([...setA].filter(x => setB.has(x))); // {2, 3}

// 差集
const difference = new Set([...setA].filter(x => !setB.has(x))); // {1}

// Set 遍历
for (const item of setA) {
    console.log(item);
}

setA.forEach(v => console.log(v));
```

::: code-tabs#lang

@tab TypeScript

```ts
// Set 实用封装
function union<T>(a: Set<T>, b: Set<T>): Set<T> {
    return new Set([...a, ...b]);
}

function intersect<T>(a: Set<T>, b: Set<T>): Set<T> {
    return new Set([...a].filter(x => b.has(x)));
}

function difference<T>(a: Set<T>, b: Set<T>): Set<T> {
    return new Set([...a].filter(x => !b.has(x)));
}
```

@tab Go

```go
// Go 需要用 map 模拟集合操作
func Union[T comparable](a, b map[T]struct{}) map[T]struct{} {
    result := make(map[T]struct{})
    for k := range a { result[k] = struct{}{} }
    for k := range b { result[k] = struct{}{} }
    return result
}

func Intersect[T comparable](a, b map[T]struct{}) map[T]struct{} {
    result := make(map[T]struct{})
    for k := range a {
        if _, exists := b[k]; exists {
            result[k] = struct{}{}
        }
    }
    return result
}
```

:::

### WeakMap / WeakSet —— 弱引用

```ts
// WeakMap —— 键必须是对象，且是弱引用
// 当键对象被 GC 回收时，对应的值也会被回收
const wm = new WeakMap<object, string>();

let obj: object | null = { id: 1 };
wm.set(obj, "metadata");
console.log(wm.get(obj)); // "metadata"

// 当 obj 不再被引用时...
obj = null;
// WeakMap 中的关联数据会被 GC 自动回收
// ⚠️ 注意：WeakMap 没有 size 属性，不可遍历

// 典型用途：存储 DOM 节点的额外数据
const elementData = new WeakMap<Element, { handler: () => void }>();

function attachData(el: Element, data: { handler: () => void }) {
    elementData.set(el, data);
    // 当 el 从 DOM 中移除并被 GC 后，data 自动释放
}

// WeakSet —— 同样弱引用，存储对象
const ws = new WeakSet<object>();
let obj2 = { id: 2 };
ws.add(obj2);
console.log(ws.has(obj2)); // true
obj2 = null; // obj2 会被 GC 回收
```

::: warning 弱引用

Go 的 GC 不提供弱引用机制。WeakMap/WeakSet 是 JavaScript 特有概念，用于解决**内存泄漏**问题。典型的场景是：一个 DOM 元素被移除后，关联的数据也应该被回收。

:::

### TypedArray —— 类型化数组

JavaScript 的 TypedArray 提供了类似 C/Go 的内存视图能力。

```ts
// TypedArray 类型一览
// 类比 Go 中的基本数值类型数组
const int8 = new Int8Array(4);          // 类比 Go []int8
const uint8 = new Uint8Array(4);        // 类比 Go []uint8 (byte)
const uint8Clamped = new Uint8ClampedArray(4); // Canvas 专用
const int16 = new Int16Array(4);        // 类比 Go []int16
const uint16 = new Uint16Array(4);      // 类比 Go []uint16
const int32 = new Int32Array(4);        // 类比 Go []int32
const uint32 = new Uint32Array(4);      // 类比 Go []uint32
const float32 = new Float32Array(4);    // 类比 Go []float32
const float64 = new Float64Array(4);    // 类比 Go []float64
const bigInt64 = new BigInt64Array(4);  // 类比 Go []int64
const bigUint64 = new BigUint64Array(4);// 类比 Go []uint64

// 操作 TypedArray
const buf = new Uint8Array([72, 101, 108, 108, 111]);
console.log(new TextDecoder().decode(buf)); // "Hello"

// DataView —— 更灵活的字节操作
const buffer = new ArrayBuffer(16);
const view = new DataView(buffer);
view.setInt32(0, 0x12345678, false); // big-endian
view.setFloat64(4, 3.14, true);     // little-endian
```

::: code-tabs#lang

@tab TypeScript

```ts
// TypedArray 在二进制协议解析中使用
function parseBinaryHeader(data: Uint8Array): { version: number; flags: number } {
    const view = new DataView(data.buffer);
    return {
        version: view.getUint16(0, false),  // 大端序
        flags: view.getUint8(2),
    };
}
```

@tab Go

```go
// Go 中的等价操作
type Header struct {
    Version uint16
    Flags   uint8
}

func ParseBinaryHeader(data []byte) Header {
    return Header{
        Version: binary.BigEndian.Uint16(data[0:2]),
        Flags:   data[2],
    }
}
```

:::

## 差异分析

| 维度 | Go | TypeScript |
|------|-----|-----------|
| **哈希映射** | `map[K]V`（键必须可比较） | `Map<K,V>`（键可以是任意类型）+ `Object` |
| **集合类型** | 无内置 Set，用 `map[T]struct{}` 模拟 | `Set<T>` 内置 |
| **弱引用** | 不支持 | `WeakMap` / `WeakSet` |
| **有序性** | Map 遍历随机 | Map/Set 保持插入顺序 |
| **类型化数组** | `[]byte` / `[]int32` 等 | `Uint8Array` / `Int32Array` 等 TypedArray |
| **零值语义** | map 读零值返回零值 | Map 读不存在键返回 `undefined` |
| **迭代器** | `for range` | `for...of` / `.forEach()` / `.values()` 多种 |
| **内存效率** | 高效编译期分配 | 动态类型有额外开销 |

## Bad Practice

### 1. 用 Object 做哈希映射（键非字符串）

```ts
// Bad: Object 的键只能转成 string
const map: Record<string, number> = {};
const key1 = { id: 1 };
const key2 = { id: 2 };

map[key1] = 100; // key1 被转为 "[object Object]"
map[key2] = 200; // 覆盖了 key1 的值！
console.log(map); // { "[object Object]": 200 }

// Best: 使用 Map
const properMap = new Map<object, number>();
properMap.set(key1, 100);
properMap.set(key2, 200);
console.log(properMap.get(key1)); // 100
console.log(properMap.get(key2)); // 200
```

### 2. 用 Array 代替 Set 做去重

```ts
// Bad: 手动检查数组去重 —— O(n²)
const items = [1, 2, 2, 3, 3, 3];
const unique: number[] = [];
for (const item of items) {
    if (!unique.includes(item)) {
        unique.push(item);
    }
}

// Best: 使用 Set —— O(n)
const uniqueItems = [...new Set(items)];
```

### 3. 不释放 WeakMap/WeakSet 中的引用

```ts
// Bad: 强引用导致内存泄漏
const cache = new Map<object, bigData>();

function process(obj: object) {
    cache.set(obj, new bigData()); // obj 永远无法被 GC
    // 即使调用方不再使用 obj，cache 仍持有引用
}

// Best: 使用 WeakMap
const weakCache = new WeakMap<object, bigData>();

function processWeak(obj: object) {
    weakCache.set(obj, new bigData());
    // 当 obj 不再被外部引用时，数据自动 GC
}
```

### 4. 遍历 Map 时修改

```ts
// Bad: 遍历时修改
const map = new Map([["a", 1], ["b", 2], ["c", 3]]);
for (const [key] of map) {
    if (key === "b") {
        map.delete("c"); // 遍历过程中修改可能导致意外行为
    }
}

// Best: 先收集要删除的键，再统一删除
const toDelete: string[] = [];
for (const [key] of map) {
    if (key === "b") toDelete.push("c");
}
for (const key of toDelete) map.delete(key);
```

## Best Practice

### 1. 使用 Set 实现高效的集合运算

```ts
// Best: 泛型集合运算工具
class SetUtils {
    static union<T>(...sets: Set<T>[]): Set<T> {
        const result = new Set<T>();
        for (const set of sets) {
            for (const item of set) {
                result.add(item);
            }
        }
        return result;
    }

    static intersect<T>(...sets: Set<T>[]): Set<T> {
        if (sets.length === 0) return new Set();
        const first = sets[0];
        const rest = sets.slice(1);
        return new Set([...first].filter(item =>
            rest.every(s => s.has(item))
        ));
    }

    static isSubset<T>(subset: Set<T>, superset: Set<T>): boolean {
        return [...subset].every(item => superset.has(item));
    }
}

const a = new Set([1, 2, 3, 4]);
const b = new Set([3, 4, 5, 6]);
console.log(SetUtils.union(a, b));       // {1,2,3,4,5,6}
console.log(SetUtils.intersect(a, b));   // {3,4}
console.log(SetUtils.isSubset(new Set([3, 4]), a)); // true
```

### 2. Map 做缓存时限制大小

```ts
// Best: 带大小限制的 LRU 缓存
class LRUCache<K, V> {
    private cache = new Map<K, V>();

    constructor(private maxSize: number) {}

    get(key: K): V | undefined {
        if (!this.cache.has(key)) return undefined;
        const value = this.cache.get(key)!;
        // 重新插入以保持最近使用的在最前面
        this.cache.delete(key);
        this.cache.set(key, value);
        return value;
    }

    set(key: K, value: V): void {
        if (this.cache.has(key)) {
            this.cache.delete(key);
        } else if (this.cache.size >= this.maxSize) {
            // 删除最早插入的（Map 保持插入顺序）
            const firstKey = this.cache.keys().next().value;
            if (firstKey !== undefined) this.cache.delete(firstKey);
        }
        this.cache.set(key, value);
    }
}

const lru = new LRUCache<string, number>(3);
lru.set("a", 1); lru.set("b", 2); lru.set("c", 3);
lru.set("d", 4); // 淘汰 "a"
console.log(lru.get("a")); // undefined
```

### 3. TypedArray 与 ArrayBuffer 处理二进制数据

```ts
// Best: 封装二进制协议消息
interface Message {
    id: number;      // uint32, 4 bytes
    type: number;    // uint8, 1 byte
    payload: string; // UTF-8 编码，变长
}

class BinaryProtocol {
    static encode(msg: Message): Uint8Array {
        const encoder = new TextEncoder();
        const payloadBytes = encoder.encode(msg.payload);
        const buffer = new ArrayBuffer(5 + payloadBytes.length);
        const view = new DataView(buffer);

        view.setUint32(0, msg.id, true);           // little-endian
        view.setUint8(4, msg.type);
        new Uint8Array(buffer, 5).set(payloadBytes);

        return new Uint8Array(buffer);
    }

    static decode(data: Uint8Array): Message {
        const view = new DataView(data.buffer);
        const id = view.getUint32(0, true);
        const type = view.getUint8(4);
        const payload = new TextDecoder().decode(data.slice(5));
        return { id, type, payload };
    }
}
```

::: tip 总结

- **Map** 替代 Object 作为哈希映射（尤其是非字符串键）
- **Set** 替代数组去重和集合运算（比数组 `includes` 高效得多）
- **WeakMap** 用于 DOM 关联数据和内存敏感的缓存
- **TypedArray** 是二进制协议/WebGL 等场景的必需品
- Go 开发者注意：TS 没有 `map[T]struct{}` 的惯用法，请直接用 `Set<T>`

:::
