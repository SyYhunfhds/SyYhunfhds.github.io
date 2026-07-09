---
title: '异步编程：Promise与async/await'
date: 2026-07-09
footer: Trae编辑
---

# 异步编程：Promise 与 async/await

## 概述

Go 的并发模型基于 **goroutine + channel**（CSP 模型），是语言级的异步原语。TypeScript（JavaScript）采用 **事件循环 + Promise** 模型，通过 `async/await` 提供类似同步代码的异步编程体验。对于 Go 开发者，理解这两种模型的核心差异 —— CSP 的通信顺序进程 vs Promise 的回调链 —— 是掌握 TS 异步编程的关键。

---

## Go 开发者已知

```go
// Go 并发 —— goroutine + channel
func fetchUser(id int) (User, error) {
  // 模拟网络请求
  time.Sleep(100 * time.Millisecond)
  return User{ID: id, Name: "Alice"}, nil
}

// 顺序调用
user, err := fetchUser(1)
if err != nil {
  // 错误处理
}

// 并发调用
func fetchConcurrent() error {
  ch := make(chan result, 2)

  go func() {
    user, err := fetchUser(1)
    ch <- result{user, err}
  }()

  go func() {
    user, err := fetchUser(2)
    ch <- result{user, err}
  }()

  for i := 0; i < 2; i++ {
    r := <-ch
    if r.err != nil {
      return r.err
    }
  }
  return nil
}

// 等待多个 goroutine
var wg sync.WaitGroup
wg.Add(2)
go func() { defer wg.Done(); /* work */ }()
go func() { defer wg.Done(); /* work */ }()
wg.Wait()
```

Go 异步特点：

- **CSP 模型**：基于通信（channel）而非共享内存
- **goroutine**：轻量级线程，数百万级别
- **错误处理**：显式的 `if err != nil` 模式
- **无 async/await**：同步式编程（goroutine 内部）
- **select**：多路复用 channel

---

## TypeScript 怎么做

### Promise<T> 基础

```ts
// Promise —— 表示异步操作的结果
const promise: Promise<string> = new Promise((resolve, reject) => {
  setTimeout(() => {
    resolve('Hello')
    // 或 reject(new Error('Failed'))
  }, 1000)
})

// 链式调用
promise
  .then((value) => value.toUpperCase())
  .then((value) => console.log(value))
  .catch((error) => console.error(error))
  .finally(() => console.log('Done'))
```

### async/await

```ts
// async 函数返回 Promise
async function fetchUser(id: number): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  return response.json()
}

// 使用
async function main() {
  try {
    const user = await fetchUser(1)
    console.log(user.name)
  } catch (error) {
    console.error('Failed to fetch user:', error)
  }
}
```

### Promise.all / race / allSettled / any

```ts
// Promise.all —— 所有完成（快速失败）
const [user, posts, comments] = await Promise.all([
  fetchUser(1),
  fetchPosts(1),
  fetchComments(1),
])

// Promise.race —— 最先完成的
const timeout = new Promise<never>((_, reject) =>
  setTimeout(() => reject(new Error('Timeout')), 5000)
)
const result = await Promise.race([fetchUser(1), timeout])

// Promise.allSettled —— 所有完成（不快速失败）
const results = await Promise.allSettled([
  fetchUser(1),
  fetchPosts(1),
])

for (const result of results) {
  if (result.status === 'fulfilled') {
    console.log('Success:', result.value)
  } else {
    console.log('Failed:', result.reason)
  }
}

// Promise.any —— 第一个成功的
const firstSuccess = await Promise.any([
  fetchFromCache(1),
  fetchFromDB(1),
  fetchFromAPI(1),
])
```

### 错误处理

```ts
// try-catch 模式
async function safeFetch<T>(url: string): Promise<[T | null, Error | null]> {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      return [null, new Error(`HTTP ${response.status}`)]
    }
    const data = await response.json()
    return [data as T, null]
  } catch (error) {
    return [null, error instanceof Error ? error : new Error(String(error))]
  }
}

// 使用 Go 风格的错误处理
const [user, err] = await safeFetch<User>('/api/users/1')
if (err) {
  console.error(err)
} else {
  console.log(user!.name)
}
```

### 异步迭代器

```ts
// for await...of —— 异步迭代
async function* generatePages(): AsyncGenerator<User[]> {
  let page = 1
  let hasMore = true

  while (hasMore) {
    const response = await fetch(`/api/users?page=${page}`)
    const data = await response.json()
    yield data.users
    hasMore = data.hasMore
    page++
  }
}

// 使用
for await (const page of generatePages()) {
  for (const user of page) {
    console.log(user.name)
  }
}

// 异步迭代数组
const promises = [fetchUser(1), fetchUser(2), fetchUser(3)]
for await (const user of promises) {
  console.log(user.name)
}
```

---

## 差异分析

| 维度 | Go | TypeScript |
|------|----|------------|
| 并发模型 | CSP（goroutine + channel） | 事件循环 + Promise |
| 异步语法 | 同步式（go func / channel） | `async/await` |
| 错误处理 | `if err != nil` | `try/catch` |
| 并行执行 | `go func()` + `sync.WaitGroup` | `Promise.all()` |
| 多路复用 | `select { case <-ch1: }` | `Promise.race()` |
| 通信方式 | channel（CSP） | Promise 链 |
| 超时处理 | `select { case <-ch: case <-time.After(): }` | `Promise.race([promise, timeout])` |
| 轻量线程 | goroutine（原生） | Web Worker（需额外配置） |

::: info CSP vs Promise：哲学差异

Go 的格言是 **"Do not communicate by sharing memory; instead, share memory by communicating."**

JavaScript/TypeScript 的格言是 **"Everything is an event."**

```go
// Go：通过 channel 通信
ch := make(chan int)
go func() { ch <- 42 }()
value := <-ch
```

```ts
// TS：通过 Promise 链式传递
const promise = new Promise<number>((resolve) => resolve(42))
const value = await promise
```

Go 的 CSP 模型更擅长处理**生产者-消费者**和**扇出/扇入**模式，而 TypeScript 的 Promise 模型更擅长处理**单一异步操作**和**回调编排**。

:::

---

## Bad Practice

```ts
// Bad: 忘记 await —— Promise 不会被等待
function process() {
  fetchUser(1).then(user => {
    // 这个 then 可能不会在函数返回前执行
  })
  // 函数立即返回，fetch 可能未完成
}

// Bad: 嵌套的 then 链（回调地狱）
fetchUser(1)
  .then(user => {
    return fetchPosts(user.id)
      .then(posts => {
        return fetchComments(posts[0].id)
          .then(comments => {
            console.log(comments)
          })
      })
  })

// Bad: 不必要的串行
const user = await fetchUser(1)
const posts = await fetchPosts(user.id)
// 如果 fetchPosts 不依赖 fetchUser 的结果，应并行

// Bad: 空 catch
async function fetchData() {
  try {
    return await riskyOperation()
  } catch {
    // 空的 catch —— 错误被静默吞没
  }
}
```

---

## Best Practice

```ts
// Good: 统一使用 async/await
async function processUser(id: number): Promise<void> {
  try {
    const user = await fetchUser(id)
    const posts = await fetchPosts(user.id)
    console.log(user, posts)
  } catch (error) {
    console.error('Process failed:', error)
    throw error  // 如果不处理，重新抛出
  }
}

// Good: 互不依赖的操作并行执行
async function loadDashboard(userId: number): Promise<Dashboard> {
  const [user, posts, notifications] = await Promise.all([
    fetchUser(userId),
    fetchPosts(userId),
    fetchNotifications(userId),
  ])
  return { user, posts, notifications }
}

// Good: 使用 Promise.allSettled 替代 all
async function loadCriticalData() {
  const results = await Promise.allSettled([
    fetchPrimarySource(),
    fetchBackupSource(),
  ])

  // 取第一个成功的结果
  const data = results.find(
    (r): r is PromiseFulfilledResult<Data> => r.status === 'fulfilled'
  )

  if (!data) {
    throw new Error('All sources failed')
  }
  return data.value
}

// Good: 超时处理
async function fetchWithTimeout<T>(
  url: string,
  timeoutMs: number = 5000
): Promise<T> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch(url, { signal: controller.signal })
    return await response.json()
  } finally {
    clearTimeout(timeout)
  }
}

// Good: 并发限流
async function batchProcess<T, R>(
  items: T[],
  fn: (item: T) => Promise<R>,
  concurrency: number = 5
): Promise<R[]> {
  const results: R[] = []

  for (let i = 0; i < items.length; i += concurrency) {
    const batch = items.slice(i, i + concurrency)
    const batchResults = await Promise.all(batch.map(fn))
    results.push(...batchResults)
  }

  return results
}

// Good: 重试逻辑
async function withRetry<T>(
  fn: () => Promise<T>,
  retries: number = 3
): Promise<T> {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn()
    } catch (error) {
      if (i === retries - 1) throw error
      await new Promise(r => setTimeout(r, 1000 * (i + 1)))
    }
  }
  throw new Error('Unreachable')
}
```

::: tip 使用 AbortController 取消请求

```ts
// Go: context.WithCancel
// TS: AbortController

const controller = new AbortController()

// 5 秒后超时
setTimeout(() => controller.abort(), 5000)

try {
  const response = await fetch(url, { signal: controller.signal })
} catch (error) {
  if (error instanceof DOMException && error.name === 'AbortError') {
    console.log('Request cancelled')
  }
}
```

:::

---

## code-tabs 对比

::: code-tabs

```ts [TypeScript]
// 并行获取多个用户
async function fetchUsers(ids: number[]): Promise<User[]> {
  const promises = ids.map(id =>
    fetch(`/api/users/${id}`).then(r => r.json())
  )
  return Promise.all(promises)
}
```

```go [Go]
// Go 并行获取多个用户
func fetchUsers(ids []int) ([]User, error) {
  type result struct {
    user User
    err  error
  }

  ch := make(chan result, len(ids))
  for _, id := range ids {
    go func(id int) {
      user, err := fetchUser(id)
      ch <- result{user, err}
    }(id)
  }

  var users []User
  for i := 0; i < len(ids); i++ {
    r := <-ch
    if r.err != nil {
      return nil, r.err
    }
    users = append(users, r.user)
  }
  return users, nil
}
```

:::

---

## 总结

| Go 概念 | TypeScript 对应 |
|---------|----------------|
| `go func()` | `Promise.all([...])` |
| `channel <- value` | `resolve(value)` |
| `<-channel` | `await promise` |
| `sync.WaitGroup` | `Promise.all()` |
| `select { case <-ch: }` | `Promise.race()` |
| `context.Context` (超时) | `AbortController` / `Promise.race` |
| `if err != nil` | `try/catch` |
| `for v := range ch` | `for await...of` |

核心认知转变：TypeScript 的异步模型是**单线程事件循环**，所有异步操作通过 Promise 和回调协作，而非 Go 的多线程 CSP 通信。对于典型的 I/O 密集型应用（Web 请求、文件操作、数据库查询），两者的表达能力等价，但哲学不同。

下一章将介绍 **装饰器与元数据反射**。
