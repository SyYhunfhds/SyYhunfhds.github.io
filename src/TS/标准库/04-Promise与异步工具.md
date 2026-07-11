---
title: 04-Promise与异步工具
date: 2026-07-09
footer: Trae编辑
---

# Promise 与异步工具

## Go 开发者已知

Go 的并发模型基于 **goroutine + channel**，没有 Promise 概念。Go 的异步操作通过 goroutine 实现，取消通过 `context.Context` 实现。

```go
// Go 的 goroutine 并发
func fetchUser(id int) (User, error) {
    // 模拟网络请求
    time.Sleep(100 * time.Millisecond)
    return User{ID: id, Name: "Alice"}, nil
}

// 并发执行多个任务
func fetchAll() ([]User, error) {
    var wg sync.WaitGroup
    results := make([]User, 3)
    errCh := make(chan error, 3)

    for i := 0; i < 3; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            user, err := fetchUser(id)
            if err != nil {
                errCh <- err
                return
            }
            results[id] = user
        }(i)
    }

    wg.Wait()
    close(errCh)

    if err, ok := <-errCh; ok {
        return nil, err
    }
    return results, nil
}

// Go 的 context 取消
func fetchWithTimeout(ctx context.Context, id int) (User, error) {
    resultCh := make(chan User, 1)
    errCh := make(chan error, 1)

    go func() {
        user, err := fetchUser(id)
        if err != nil {
            errCh <- err
            return
        }
        resultCh <- user
    }()

    select {
    case user := <-resultCh:
        return user, nil
    case err := <-errCh:
        return User{}, err
    case <-ctx.Done():
        return User{}, ctx.Err()
    }
}
```

## TS 怎么做

### Promise\<T\> 类型

```ts
// Promise 是 TS 的核心类型，表示一个未来完成的值
type Promise<T> = {
    then<U>(onFulfilled?: (value: T) => U | Promise<U>): Promise<U>;
    catch<U>(onRejected?: (reason: any) => U | Promise<U>): Promise<U>;
    finally(onFinally?: () => void): Promise<T>;
};

// 创建 Promise
const promise = new Promise<string>((resolve, reject) => {
    setTimeout(() => {
        resolve("done");
        // 或 reject(new Error("failed"));
    }, 1000);
});
```

### Promise 静态方法

```ts
// Promise.resolve —— 创建一个 resolved 的 Promise
const p1 = Promise.resolve(42);

// Promise.reject —— 创建一个 rejected 的 Promise
const p2 = Promise.reject(new Error("fail"));

// Promise.all —— 全部成功或一个失败（类似 Go errgroup）
const urls = ["/api/user", "/api/posts", "/api/comments"];
const allResponses = await Promise.all(
    urls.map(url => fetch(url).then(r => r.json()))
);
// 全部成功时返回数组，任一失败即整体失败

// Promise.allSettled —— 等待所有完成（无论成功失败）
const results = await Promise.allSettled(
    urls.map(url => fetch(url).then(r => r.json()))
);
for (const result of results) {
    if (result.status === "fulfilled") {
        console.log("Success:", result.value);
    } else {
        console.log("Failed:", result.reason);
    }
}

// Promise.race —— 返回第一个完成的（成功或失败）
const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error("timeout")), 5000)
);
const data = await Promise.race([fetch("/api/data"), timeout]);

// Promise.any —— 返回第一个成功的（ES2021+）
const firstSuccess = await Promise.any([
    fetch("/api/mirror1"),
    fetch("/api/mirror2"),
    fetch("/api/mirror3"),
]);
// 全部失败才 AggregateError
```

::: info 静态方法对比

| 方法 | 行为 | 类比 Go |
|------|------|---------|
| `Promise.all` | 全成功或一失败 | `errgroup.Group` |
| `Promise.allSettled` | 等所有完成，不关心成败 | `sync.WaitGroup` |
| `Promise.race` | 返回第一个完成的 | `select`（第一个返回的 channel）|
| `Promise.any` | 返回第一个成功的 | `select` + 忽略失败 |

:::

### 微任务队列 —— 原理

```ts
// 微任务（Microtask）vs 宏任务（Macrotask）
console.log("1: sync");

// 微任务 —— Promise 回调、queueMicrotask、MutationObserver
Promise.resolve().then(() => console.log("2: microtask"));

// 宏任务 —— setTimeout、setInterval、I/O、UI rendering
setTimeout(() => console.log("3: macrotask"), 0);

// 同步代码
console.log("4: sync");

// 输出顺序: 1 → 4 → 2 → 3
// 微任务在宏任务之前执行
```

::: tip 微任务队列与 Go goroutine 调度的区别

| 维度 | Go goroutine 调度 | JS 事件循环 |
|------|-------------------|------------|
| **调度单元** | goroutine（M:N 调度） | 微任务 / 宏任务 |
| **调度模型** | 抢占式 | 协作式 |
| **并行性** | 真并行（GOMAXPROCS） | 单线程（一个时间片一个任务） |
| **任务切换** | 系统调度 + 协作点 | 任务队列按序出队 |
| **等待机制** | goroutine 阻塞不阻塞线程 | 异步操作注册回调后释放线程 |

:::

### AbortController —— 取消操作

```ts
// AbortController —— 类比 Go 的 context.WithCancel / context.WithTimeout
class DataService {
    private controller: AbortController | null = null;

    async fetchData(url: string): Promise<unknown> {
        // 取消前一次请求
        this.controller?.abort();
        this.controller = new AbortController();

        const response = await fetch(url, {
            signal: this.controller.signal,
        });
        return response.json();
    }

    cancel(): void {
        this.controller?.abort();
    }
}

// 带超时的取消 —— 类比 context.WithTimeout
function fetchWithTimeout(url: string, ms: number): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), ms);

    return fetch(url, { signal: controller.signal })
        .finally(() => clearTimeout(timeoutId));
}

// 使用
try {
    const response = await fetchWithTimeout("https://api.example.com", 5000);
    console.log(await response.json());
} catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
        console.log("请求被取消（超时）");
    } else {
        console.error("其他错误:", err);
    }
}
```

::: code-tabs#lang

@tab TypeScript (AbortController)

```ts
function cancellableAsync(signal: AbortSignal): Promise<void> {
    return new Promise((resolve, reject) => {
        if (signal.aborted) {
            reject(new DOMException("Already aborted", "AbortError"));
            return;
        }

        const onAbort = () => {
            cleanup();
            reject(new DOMException("Cancelled", "AbortError"));
        };

        const cleanup = () => {
            signal.removeEventListener("abort", onAbort);
        };

        signal.addEventListener("abort", onAbort);

        // 模拟异步工作
        setTimeout(() => {
            cleanup();
            if (!signal.aborted) resolve();
        }, 1000);
    });
}
```

@tab Go (context.Context)

```go
func CancellableAsync(ctx context.Context) error {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-time.After(time.Second):
        return nil
    }
}
```

:::

### Promisify —— 将回调转 Promise

```ts
// Promisify 工具 —— 将 Node.js callback 风格转为 Promise
import { randomBytes } from "crypto";

// Node.js callback 风格
randomBytes(32, (err, buf) => {
    if (err) console.error(err);
    else console.log(buf.toString("hex"));
});

// 转为 Promise
function promisify<TArgs extends any[], TResult>(
    fn: (...args: [...TArgs, (err: Error | null, result: TResult) => void]) => void
): (...args: TArgs) => Promise<TResult> {
    return (...args: TArgs): Promise<TResult> => {
        return new Promise((resolve, reject) => {
            fn(...args, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        });
    };
}

const randomBytesAsync = promisify<[number], Buffer>(randomBytes);
const buf = await randomBytesAsync(32);
```

### p-limit —— 并发控制

```ts
// p-limit —— 控制并发数（类比 Go semaphore.Weighted）
import pLimit from "p-limit";

// 限制最多 3 个并发请求
const limit = pLimit(3);

const urls = Array.from({ length: 20 }, (_, i) =>
    `https://api.example.com/item/${i}`
);

const results = await Promise.all(
    urls.map(url => limit(() => fetch(url).then(r => r.json())))
);
```

::: code-tabs#lang

@tab TypeScript (p-limit)

```ts
// 简易实现 p-limit
function createConcurrencyLimiter(max: number) {
    const queue: (() => void)[] = [];
    let active = 0;

    async function run<T>(fn: () => Promise<T>): Promise<T> {
        if (active >= max) {
            await new Promise<void>(resolve => queue.push(resolve));
        }
        active++;
        try {
            return await fn();
        } finally {
            active--;
            if (queue.length > 0) {
                const next = queue.shift()!;
                next();
            }
        }
    }

    return run;
}

const limitedFetch = createConcurrencyLimiter(3);
```

@tab Go (semaphore.Weighted)

```go
import "golang.org/x/sync/semaphore"

func main() {
    sem := semaphore.NewWeighted(3)
    ctx := context.Background()

    var wg sync.WaitGroup
    for i := 0; i < 20; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            sem.Acquire(ctx, 1)
            defer sem.Release(1)
            // 执行 HTTP 请求
            fetchItem(id)
        }(i)
    }
    wg.Wait()
}
```

:::

## 差异分析

| 维度 | Go | TypeScript |
|------|-----|-----------|
| **并发模型** | goroutine + channel（M:N 调度） | 事件循环 + Promise（单线程） |
| **异步操作** | 同步风格，goroutine 内部 | Promise / async-await |
| **取消机制** | `context.Context` | `AbortController` / `AbortSignal` |
| **超时控制** | `context.WithTimeout` | `AbortController` + `setTimeout` |
| **并发限制** | `semaphore.Weighted` | `p-limit` 或手写 |
| **错误聚合** | `errgroup.Group` | `Promise.allSettled` |
| **微任务** | 无此概念 | 微任务队列（优先级高于宏任务） |
| **回调转 Promise** | 不需要 | `util.promisify` / 手写 |

## Bad Practice

### 1. 忘记处理 Promise 拒绝

```ts
// Bad: 未处理 reject
async function main() {
    // 未加 catch，拒绝会变为未处理的 Promise 拒绝
    fetch("/api/data").then(r => r.json());
}

// Bad: 事件监听中 async 回调的拒绝不处理
button.addEventListener("click", async () => {
    await fetch("/api/data"); // 如果失败，拒绝未被捕获
});

// Best: 统一处理
async function onButtonClick() {
    try {
        await fetch("/api/data");
    } catch (err) {
        console.error("请求失败:", err);
        // 显示用户友好的错误提示
    }
}
button.addEventListener("click", onButtonClick);
```

### 2. 在 Promise 构造函数中使用 async

```ts
// Bad: Promise 构造函数中的 async 是多余的
const p = new Promise(async (resolve, reject) => {
    try {
        const data = await fetch("/api/data");
        resolve(data);
    } catch (err) {
        reject(err);
    }
});
// 如果 async 函数内部抛错，reject 永远不会被调用！

// Best: 直接使用 async 函数（隐式返回 Promise）
async function fetchData() {
    const response = await fetch("/api/data");
    return response.json();
}
```

### 3. forEach 中的 await

```ts
// Bad: forEach 中的 await 无效
async function processItems(items: number[]) {
    items.forEach(async (item) => {
        await process(item); // 不会等待
    });
    console.log("Done"); // 在 process 完成前就会打印
}

// Best: 使用 for...of 或 Promise.all
async function processItemsCorrect(items: number[]) {
    // 串行
    for (const item of items) {
        await process(item);
    }

    // 或并行
    await Promise.all(items.map(item => process(item)));
}
```

### 4. 忽略 finally 中的错误

```ts
// Bad: finally 中的 Promise 拒绝会被忽略
async function bad() {
    try {
        return await riskyOperation();
    } catch (err) {
        console.error(err);
    } finally {
        await cleanup(); // 如果 cleanup 失败，原始返回值丢失
    }
}

// Best: 分离 finally 逻辑
async function good() {
    let result;
    try {
        result = await riskyOperation();
    } catch (err) {
        console.error(err);
        throw err;
    } finally {
        await cleanup().catch(e => console.error("cleanup failed:", e));
    }
    return result;
}
```

## Best Practice

### 1. 类型安全的错误处理

```ts
// Best: 封装 Result 类型（类似 Go 的 (T, error)）
type Result<T> = { ok: true; value: T } | { ok: false; error: Error };

async function fetchJSON<T>(url: string): Promise<Result<T>> {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            return { ok: false, error: new Error(`HTTP ${response.status}`) };
        }
        const data = await response.json();
        return { ok: true, value: data as T };
    } catch (err) {
        return { ok: false, error: err instanceof Error ? err : new Error(String(err)) };
    }
}

// 使用 —— 类似 Go 的错误处理风格
const result = await fetchJSON<User>("/api/user");
if (!result.ok) {
    console.error("Failed:", result.error);
    return;
}
console.log("User:", result.value.name);
```

### 2. 可取消的异步操作封装

```ts
// Best: 封装可取消的异步操作
interface AsyncTask<T> {
    promise: Promise<T>;
    cancel: () => void;
}

function createCancellableTask<T>(
    fn: (signal: AbortSignal) => Promise<T>
): AsyncTask<T> {
    const controller = new AbortController();
    return {
        promise: fn(controller.signal),
        cancel: () => controller.abort(),
    };
}

// 使用
const task = createCancellableTask(async (signal) => {
    const response = await fetch("/api/data", { signal });
    return response.json();
});

// 取消操作
setTimeout(() => task.cancel(), 1000);

try {
    const data = await task.promise;
    console.log(data);
} catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
        console.log("Task was cancelled");
    }
}
```

### 3. 并发控制封装

```ts
// Best: 带并发限制和重试的请求封装
class RequestPool {
    private active = 0;
    private queue: (() => void)[] = [];

    constructor(private maxConcurrent: number, private maxRetries = 3) {}

    async execute<T>(fn: () => Promise<T>): Promise<T> {
        await this.acquireSlot();
        this.active++;

        try {
            return await this.withRetry(fn);
        } finally {
            this.active--;
            this.releaseSlot();
        }
    }

    private async withRetry<T>(fn: () => Promise<T>, attempt = 1): Promise<T> {
        try {
            return await fn();
        } catch (err) {
            if (attempt >= this.maxRetries) throw err;
            await delay(Math.pow(2, attempt) * 100); // 指数退避
            return this.withRetry(fn, attempt + 1);
        }
    }

    private acquireSlot(): Promise<void> {
        if (this.active < this.maxConcurrent) return Promise.resolve();
        return new Promise(resolve => this.queue.push(resolve));
    }

    private releaseSlot(): void {
        this.queue.shift()?.();
    }
}

function delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 使用
const pool = new RequestPool(5);
const results = await Promise.all(
    urls.map(url => pool.execute(() => fetch(url).then(r => r.json())))
);
```

### 4. 同步化异步错误处理

```ts
// Best: 类似于 Go 的 defer 模式
async function withCleanup<T>(fn: () => Promise<T>, cleanup: () => Promise<void>): Promise<T> {
    let success = false;
    try {
        const result = await fn();
        success = true;
        return result;
    } finally {
        if (!success) {
            await cleanup().catch(e =>
                console.error("Cleanup failed after error:", e)
            );
        }
    }
}
```

::: tip 核心建议

1. 始终处理 Promise 拒绝（要么 `catch` 要么 `try-catch`）
2. 用 `AbortController` 实现操作取消（类比 Go 的 `context`）
3. 用并发库控制资源使用（`p-limit` 类比 `semaphore.Weighted`）
4. `Promise.allSettled` 比 `Promise.all` 更健壮（一个失败不影响其他）
5. 微任务特性让 Promise 回调在 setTimeout 之前执行

:::
