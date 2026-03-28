---
title: jackc puddle 库使用指南
date: 2026-03-28
footer: Trae编辑
---

# jackc puddle 库使用指南

## 引言

Puddle 是一个专为 Go 语言设计的轻量级通用资源池库，它使用标准的 context 库来处理资源的取消获取操作。Puddle 的设计哲学是保持最小必要功能，使得资源池的创建和管理变得简单而高效。无论是直接使用，还是作为特定领域资源池的底层库，puddle 都能提供出色的性能和稳定性。

## 一、库概述

### 1.1 核心特性

Puddle 提供了以下核心特性：

- **Context 支持**：通过 context，puddle 可以轻松取消正在等待的资源获取操作
- **监控 API**：提供统计 API，以便监控资源池的压力
- **无外部依赖**：除了标准库和 golang.org/x/sync，puddle 没有其他外部依赖
- **高性能**：puddle 的设计考虑了性能，确保在多并发环境下也能保持高效运行
- **完整测试**：项目的所有可到达代码都有 100% 的测试覆盖率

### 1.2 适用场景

Puddle 的设计理念使其适用于多种场景，尤其是需要管理外部资源的情况：

- **数据库连接池**：puddle 可以作为数据库连接池的底层库，管理连接的生命周期
- **网络连接池**：管理网络连接，提供连接的创建、销毁和重用功能
- **文件句柄管理**：对于需要频繁打开和关闭文件的应用，puddle 可以帮助管理文件句柄
- **其他外部资源**：任何需要复用且创建成本高的资源

### 1.3 与 sync.Pool 的区别

Puddle 和 Go 标准库中的 sync.Pool 有着本质的区别：

| **特性** | **sync.Pool** | **puddle** |
| --------- | ------------- | ---------- |
| **适用资源类型** | 内存对象 | 外部资源（连接、文件句柄等） |
| **最大资源限制** | 无 | 支持 |
| **最小资源保证** | 无 | 支持 |
| **资源丢弃** | 可随时丢弃 | 不会随机丢弃 |
| **清理函数** | 无 | 有专门的析构函数 |
| **错误处理** | 不支持 | 支持 |
| **Context 支持** | 不支持 | 支持 |
| **等待时间限制** | 不支持 | 支持 |

## 二、核心概念

### 2.1 Constructor（构造函数）

Constructor 是由资源池调用的函数，用于创建新的资源实例：

```go
type Constructor[T any] func(context.Context) (T, error)
```

**示例**：
```go
constructor := func(ctx context.Context) (net.Conn, error) {
    return net.DialTimeout("tcp", "127.0.0.1:8080", 5*time.Second)
}
```

### 2.2 Destructor（析构函数）

Destructor 是由资源池调用的函数，用于销毁资源实例：

```go
type Destructor[T any] func(T)
```

**示例**：
```go
destructor := func(conn net.Conn) {
    conn.Close()
}
```

### 2.3 Config（配置）

Config 结构体用于配置资源池的参数：

```go
type Config[T any] struct {
    Constructor Constructor[T]
    Destructor Destructor[T]
    MaxSize int32
}
```

**参数说明**：
- **Constructor**：资源构造函数
- **Destructor**：资源析构函数
- **MaxSize**：资源池的最大大小

## 三、基础用法

### 3.1 创建资源池

```go
import (
    "context"
    "log"
    "net"
    "time"

    "github.com/jackc/puddle/v2"
)

func main() {
    // 定义构造函数
    constructor := func(ctx context.Context) (net.Conn, error) {
        return net.DialTimeout("tcp", "127.0.0.1:8080", 5*time.Second)
    }
    
    // 定义析构函数
    destructor := func(conn net.Conn) {
        conn.Close()
    }
    
    // 创建资源池
    pool, err := puddle.NewPool(&puddle.Config[net.Conn]{
        Constructor: constructor,
        Destructor:  destructor,
        MaxSize:     10,
    })
    if err != nil {
        log.Fatal(err)
    }
    
    // 使用资源池
    // ...
    
    // 关闭资源池
    pool.Close()
}
```

### 3.2 获取和释放资源

```go
// 获取资源
res, err := pool.Acquire(context.Background())
if err != nil {
    log.Fatal(err)
}

// 使用资源
conn := res.Value()
_, err = conn.Write([]byte{1})
if err != nil {
    log.Fatal(err)
}

// 释放资源
res.Release()
```

### 3.3 使用 defer 确保资源释放

```go
func processData(pool *puddle.Pool[net.Conn]) error {
    // 获取资源
    res, err := pool.Acquire(context.Background())
    if err != nil {
        return err
    }
    defer res.Release()
    
    // 使用资源
    conn := res.Value()
    _, err = conn.Write([]byte{1})
    return err
}
```

### 3.4 带超时的资源获取

```go
func getResourceWithTimeout(pool *puddle.Pool[net.Conn]) (*puddle.Resource[net.Conn], error) {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    
    return pool.Acquire(ctx)
}
```

## 四、高级用法

### 4.1 TryAcquire（非阻塞获取）

TryAcquire 方法尝试获取资源，如果资源池为空则立即返回错误，不会阻塞：

```go
res, err := pool.TryAcquire()
if err != nil {
    if err == puddle.ErrNotAvailable {
        // 没有可用资源
        log.Println("No resources available")
        return
    }
    log.Fatal(err)
}

// 使用资源
defer res.Release()
```

### 4.2 资源池统计

Puddle 提供了丰富的统计 API，用于监控资源池的状态：

```go
stats := pool.Stat()

log.Printf("Total Resources: %d", stats.TotalResources())
log.Printf("Acquired Resources: %d", stats.AcquiredResources())
log.Printf("Idle Resources: %d", stats.IdleResources())
log.Printf("Max Resources: %d", stats.MaxResources())
log.Printf("Constructing Resources: %d", stats.ConstructingResources())
log.Printf("Acquire Count: %d", stats.AcquireCount())
log.Printf("Canceled Acquire Count: %d", stats.CanceledAcquireCount())
log.Printf("Empty Acquire Count: %d", stats.EmptyAcquireCount())
log.Printf("Acquire Duration: %v", stats.AcquireDuration())
log.Printf("Max Acquire Duration: %v", stats.MaxAcquireDuration())
log.Printf("Empty Acquire Duration: %v", stats.EmptyAcquireDuration())
```

### 4.3 AcquireAllIdle（获取所有空闲资源）

AcquireAllIdle 方法原子性地获取所有当前空闲的资源，主要用于健康检查和保活功能：

```go
func healthCheck(pool *puddle.Pool[net.Conn]) {
    // 获取所有空闲资源
    resources := pool.AcquireAllIdle()
    
    for _, res := range resources {
        conn := res.Value()
        
        // 检查连接是否仍然有效
        err := conn.SetDeadline(time.Now().Add(1 * time.Second))
        if err != nil {
            // 连接无效，销毁资源
            res.Destroy()
            continue
        }
        
        // 连接有效，释放回池
        res.Release()
    }
}
```

### 4.4 Hijack（劫持资源）

Hijack 方法允许调用者从资源池中劫持资源的所有权，调用者需要负责资源的清理：

```go
func hijackResource(pool *puddle.Pool[net.Conn]) (net.Conn, error) {
    res, err := pool.Acquire(context.Background())
    if err != nil {
        return nil, err
    }
    
    // 劫持资源，不再由资源池管理
    conn := res.Hijack()
    
    // 现在调用者需要负责关闭连接
    return conn, nil
}
```

### 4.5 CreateResource（创建资源）

CreateResource 方法创建一个新资源但不获取它，资源会被添加到池中：

```go
func preWarmPool(pool *puddle.Pool[net.Conn]) error {
    // 预热资源池，创建一些资源但不获取
    for i := 0; i < 5; i++ {
        err := pool.CreateResource(context.Background())
        if err != nil {
            return err
        }
    }
    return nil
}
```

## 五、最佳实践

### 5.1 合理设置资源池大小

::: tip 资源池大小配置

资源池大小的设置需要综合考虑以下因素：

- **服务器承载能力**：根据服务器的 CPU、内存等资源设置上限
- **网络带宽**：考虑网络连接的带宽限制
- **业务需求**：根据业务的并发需求调整
- **监控数据**：结合实际监控数据动态调整

:::

**示例**：
```go
// 根据 CPU 核心数设置最大连接数
maxConns := runtime.NumCPU() * 2

pool, err := puddle.NewPool(&puddle.Config[net.Conn]{
    Constructor: constructor,
    Destructor:  destructor,
    MaxSize:     int32(maxConns),
})
```

### 5.2 使用 Context 控制超时

::: tip 超时控制

使用 Context 控制资源获取的超时时间，避免长时间等待：

- 超时时间设置为业务平均响应时间的 2-3 倍
- 避免过短超时导致频繁重建连接
- 根据实际监控数据调整超时时间

:::

**示例**：
```go
func getResourceWithBackoff(pool *puddle.Pool[net.Conn]) (*puddle.Resource[net.Conn], error) {
    maxRetries := 3
    baseDelay := 100 * time.Millisecond
    
    for i := 0; i < maxRetries; i++ {
        ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
        
        res, err := pool.Acquire(ctx)
        cancel()
        
        if err == nil {
            return res, nil
        }
        
        if err == context.DeadlineExceeded {
            // 超时，使用退避策略重试
            delay := time.Duration(i+1) * baseDelay
            time.Sleep(delay)
            continue
        }
        
        // 其他错误，直接返回
        return nil, err
    }
    
    return nil, fmt.Errorf("failed to acquire resource after %d retries", maxRetries)
}
```

### 5.3 监控资源池状态

::: tip 监控资源池

定期监控资源池的状态，及时发现和解决问题：

- 监控空闲资源数量
- 监控获取等待时间
- 监控资源创建失败率
- 监控资源池压力指标

:::

**示例**：
```go
func monitorPool(pool *puddle.Pool[net.Conn]) {
    ticker := time.NewTicker(30 * time.Second)
    defer ticker.Stop()
    
    for range ticker.C {
        stats := pool.Stat()
        
        log.Printf("Pool Stats:")
        log.Printf("  Total Resources: %d/%d", stats.TotalResources(), stats.MaxResources())
        log.Printf("  Idle Resources: %d", stats.IdleResources())
        log.Printf("  Acquired Resources: %d", stats.AcquiredResources())
        log.Printf("  Acquire Duration: %v", stats.AcquireDuration())
        log.Printf("  Max Acquire Duration: %v", stats.MaxAcquireDuration())
        
        // 检查资源池压力
        if stats.AcquiredResources() >= stats.MaxResources()*9/10 {
            log.Printf("WARNING: Pool is under high pressure")
        }
    }
}
```

### 5.4 错误处理策略

::: tip 错误处理

区分不同类型的错误，采取相应的处理策略：

- **资源池关闭错误**：`puddle.ErrClosedPool`
- **资源不可用错误**：`puddle.ErrNotAvailable`
- **Context 超时错误**：`context.DeadlineExceeded`
- **资源创建错误**：构造函数返回的错误

:::

**示例**：
```go
func safeAcquire(pool *puddle.Pool[net.Conn]) (*puddle.Resource[net.Conn], error) {
    res, err := pool.Acquire(context.Background())
    
    if err != nil {
        switch err {
        case puddle.ErrClosedPool:
            // 资源池已关闭
            return nil, fmt.Errorf("pool is closed")
        case puddle.ErrNotAvailable:
            // 没有可用资源
            return nil, fmt.Errorf("no resources available")
        case context.DeadlineExceeded:
            // 超时
            return nil, fmt.Errorf("acquire timeout")
        default:
            // 其他错误
            return nil, fmt.Errorf("failed to acquire resource: %w", err)
        }
    }
    
    return res, nil
}
```

### 5.5 资源健康检查

::: tip 健康检查

定期检查资源的健康状态，及时清理无效资源：

- 使用 AcquireAllIdle 获取所有空闲资源
- 检查资源是否仍然有效
- 销毁无效资源，释放有效资源

:::

**示例**：
```go
func healthChecker(pool *puddle.Pool[net.Conn]) {
    ticker := time.NewTicker(5 * time.Minute)
    defer ticker.Stop()
    
    for range ticker.C {
        resources := pool.AcquireAllIdle()
        
        for _, res := range resources {
            conn := res.Value()
            
            // 检查连接是否仍然有效
            err := conn.SetDeadline(time.Now().Add(1 * time.Second))
            if err != nil {
                log.Printf("Connection is invalid, destroying: %v", err)
                res.Destroy()
                continue
            }
            
            // 连接有效，释放回池
            res.Release()
        }
    }
}
```

### 5.6 资源池预热

::: tip 资源池预热

在应用启动时预热资源池，创建一定数量的资源：

- 避免启动时的资源创建延迟
- 提高应用的响应速度
- 减少峰值时的资源创建开销

:::

**示例**：
```go
func warmUpPool(pool *puddle.Pool[net.Conn], count int) error {
    log.Printf("Warming up pool with %d resources...", count)
    
    for i := 0; i < count; i++ {
        err := pool.CreateResource(context.Background())
        if err != nil {
            log.Printf("Failed to create resource %d: %v", i, err)
            continue
        }
    }
    
    stats := pool.Stat()
    log.Printf("Pool warmed up. Total resources: %d", stats.TotalResources())
    
    return nil
}
```

## 六、实际应用案例

### 6.1 数据库连接池

```go
package main

import (
    "context"
    "database/sql"
    "log"
    "time"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/jackc/puddle/v2"
)

func main() {
    // 使用 pgxpool（基于 puddle 实现）
    config, err := pgxpool.ParseConfig("postgres://user:password@localhost:5432/dbname")
    if err != nil {
        log.Fatal(err)
    }
    
    // 配置连接池
    config.MaxConns = 25
    config.MinConns = 5
    config.MaxConnLifetime = time.Hour
    config.MaxConnIdleTime = 30 * time.Minute
    config.HealthCheckPeriod = 1 * time.Minute
    
    // 创建连接池
    pool, err := pgxpool.NewWithConfig(context.Background(), config)
    if err != nil {
        log.Fatal(err)
    }
    defer pool.Close()
    
    // 使用连接池
    var name string
    err = pool.QueryRow(context.Background(), "SELECT name FROM users WHERE id = $1", 1).Scan(&name)
    if err != nil {
        log.Fatal(err)
    }
    
    log.Printf("User name: %s", name)
}
```

### 6.2 HTTP 客户端连接池

```go
package main

import (
    "context"
    "io"
    "log"
    "net"
    "net/http"
    "time"

    "github.com/jackc/puddle/v2"
)

type HTTPClient struct {
    conn net.Conn
}

func main() {
    // 定义构造函数
    constructor := func(ctx context.Context) (*HTTPClient, error) {
        conn, err := net.DialTimeout("tcp", "example.com:80", 5*time.Second)
        if err != nil {
            return nil, err
        }
        return &HTTPClient{conn: conn}, nil
    }
    
    // 定义析构函数
    destructor := func(client *HTTPClient) {
        client.conn.Close()
    }
    
    // 创建连接池
    pool, err := puddle.NewPool(&puddle.Config[*HTTPClient]{
        Constructor: constructor,
        Destructor:  destructor,
        MaxSize:     10,
    })
    if err != nil {
        log.Fatal(err)
    }
    defer pool.Close()
    
    // 使用连接池
    res, err := pool.Acquire(context.Background())
    if err != nil {
        log.Fatal(err)
    }
    defer res.Release()
    
    client := res.Value()
    
    // 发送 HTTP 请求
    req, err := http.NewRequest("GET", "http://example.com", nil)
    if err != nil {
        log.Fatal(err)
    }
    
    err = req.Write(client.conn)
    if err != nil {
        log.Fatal(err)
    }
    
    // 读取响应
    resp, err := http.ReadResponse(bufio.NewReader(client.conn), req)
    if err != nil {
        log.Fatal(err)
    }
    
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        log.Fatal(err)
    }
    
    log.Printf("Response: %s", string(body))
}
```

### 6.3 Redis 连接池

```go
package main

import (
    "context"
    "log"
    "time"

    "github.com/redis/go-redis/v9"
    "github.com/jackc/puddle/v2"
)

func main() {
    // 定义构造函数
    constructor := func(ctx context.Context) (*redis.Client, error) {
        return redis.NewClient(&redis.Options{
            Addr:     "localhost:6379",
            Password:  "",
            DB:       0,
            PoolSize:  0, // 使用 puddle 管理连接
        }), nil
    }
    
    // 定义析构函数
    destructor := func(client *redis.Client) {
        client.Close()
    }
    
    // 创建连接池
    pool, err := puddle.NewPool(&puddle.Config[*redis.Client]{
        Constructor: constructor,
        Destructor:  destructor,
        MaxSize:     10,
    })
    if err != nil {
        log.Fatal(err)
    }
    defer pool.Close()
    
    // 使用连接池
    res, err := pool.Acquire(context.Background())
    if err != nil {
        log.Fatal(err)
    }
    defer res.Release()
    
    client := res.Value()
    
    // 执行 Redis 命令
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    
    val, err := client.Get(ctx, "key").Result()
    if err != nil {
        log.Fatal(err)
    }
    
    log.Printf("Value: %s", val)
}
```

## 七、常见问题与解决方案

### 7.1 资源泄漏

**问题描述**：资源未正确归还池，导致资源耗尽。

**解决方案**：
- 使用 defer 确保资源释放
- 检查资源可用性
- 实现连接健康检查机制

**示例**：
```go
func safeOperation(pool *puddle.Pool[net.Conn]) error {
    res, err := pool.Acquire(context.Background())
    if err != nil {
        return err
    }
    defer res.Release()
    
    conn := res.Value()
    
    // 设置超时，避免连接卡住
    err = conn.SetDeadline(time.Now().Add(10 * time.Second))
    if err != nil {
        return err
    }
    
    // 执行操作
    _, err = conn.Write([]byte("data"))
    return err
}
```

### 7.2 资源池压力过大

**问题描述**：资源池压力过大，导致获取资源等待时间过长。

**解决方案**：
- 增加资源池大小
- 优化资源使用效率
- 实现资源池监控和告警

**示例**：
```go
func monitorAndAdjustPool(pool *puddle.Pool[net.Conn]) {
    ticker := time.NewTicker(1 * time.Minute)
    defer ticker.Stop()
    
    for range ticker.C {
        stats := pool.Stat()
        
        // 计算平均获取时间
        avgDuration := stats.AcquireDuration() / time.Duration(stats.AcquireCount())
        
        log.Printf("Average acquire duration: %v", avgDuration)
        
        // 如果平均获取时间过长，增加资源池大小
        if avgDuration > 100*time.Millisecond && stats.TotalResources() < stats.MaxResources() {
            log.Printf("Increasing pool size due to high latency")
            err := pool.CreateResource(context.Background())
            if err != nil {
                log.Printf("Failed to create resource: %v", err)
            }
        }
    }
}
```

### 7.3 资源创建失败

**问题描述**：资源创建失败，导致资源池无法正常工作。

**解决方案**：
- 实现重试机制
- 使用退避策略
- 监控资源创建失败率

**示例**：
```go
func createResourceWithRetry(pool *puddle.Pool[net.Conn]) error {
    maxRetries := 3
    baseDelay := 1 * time.Second
    
    for i := 0; i < maxRetries; i++ {
        err := pool.CreateResource(context.Background())
        if err == nil {
            return nil
        }
        
        log.Printf("Failed to create resource (attempt %d/%d): %v", i+1, maxRetries, err)
        
        if i < maxRetries-1 {
            delay := baseDelay * time.Duration(i+1)
            log.Printf("Retrying in %v...", delay)
            time.Sleep(delay)
        }
    }
    
    return fmt.Errorf("failed to create resource after %d attempts", maxRetries)
}
```

### 7.4 并发安全问题

**问题描述**：多个 goroutine 同时操作资源池导致数据竞争。

**解决方案**：
- Puddle 本身是并发安全的，不需要额外的锁
- 确保资源使用时也是并发安全的
- 使用测试验证并发安全性

**示例**：
```go
func concurrentAccessTest(pool *puddle.Pool[net.Conn]) {
    var wg sync.WaitGroup
    errors := make(chan error, 100)
    
    // 启动多个 goroutine 并发访问资源池
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            
            res, err := pool.Acquire(context.Background())
            if err != nil {
                errors <- fmt.Errorf("goroutine %d: %w", id, err)
                return
            }
            defer res.Release()
            
            // 使用资源
            conn := res.Value()
            _, err = conn.Write([]byte{byte(id)})
            if err != nil {
                errors <- fmt.Errorf("goroutine %d: %w", id, err)
            }
        }(i)
    }
    
    wg.Wait()
    close(errors)
    
    // 检查错误
    for err := range errors {
        log.Printf("Error: %v", err)
    }
}
```

## 八、性能优化

### 8.1 减少资源获取开销

::: tip 减少开销

通过以下方式减少资源获取的开销：

- 预热资源池，避免运行时创建资源
- 合理设置资源池大小，减少等待时间
- 使用 TryAcquire 避免不必要的等待

:::

**示例**：
```go
func optimizedAcquire(pool *puddle.Pool[net.Conn]) (*puddle.Resource[net.Conn], error) {
    // 首先尝试非阻塞获取
    res, err := pool.TryAcquire()
    if err == nil {
        return res, nil
    }
    
    if err != puddle.ErrNotAvailable {
        return nil, err
    }
    
    // 没有可用资源，使用超时获取
    ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
    defer cancel()
    
    return pool.Acquire(ctx)
}
```

### 8.2 批量操作优化

::: tip 批量操作

对于需要多个资源的操作，考虑批量获取：

- 减少多次获取的开销
- 提高操作效率
- 注意释放所有获取的资源

:::

**示例**：
```go
func batchOperation(pool *puddle.Pool[net.Conn], count int) error {
    resources := make([]*puddle.Resource[net.Conn], 0, count)
    
    // 批量获取资源
    for i := 0; i < count; i++ {
        res, err := pool.Acquire(context.Background())
        if err != nil {
            // 释放已获取的资源
            for _, r := range resources {
                r.Release()
            }
            return err
        }
        resources = append(resources, res)
    }
    
    // 确保释放所有资源
    defer func() {
        for _, res := range resources {
            res.Release()
        }
    }()
    
    // 执行批量操作
    for i, res := range resources {
        conn := res.Value()
        _, err := conn.Write([]byte{byte(i)})
        if err != nil {
            return err
        }
    }
    
    return nil
}
```

### 8.3 资源复用策略

::: tip 资源复用

最大化资源复用，提高资源池效率：

- 避免频繁创建和销毁资源
- 合理设置资源生命周期
- 实现资源保活机制

:::

**示例**：
```go
func keepAlive(pool *puddle.Pool[net.Conn]) {
    ticker := time.NewTicker(30 * time.Second)
    defer ticker.Stop()
    
    for range ticker.C {
        resources := pool.AcquireAllIdle()
        
        for _, res := range resources {
            conn := res.Value()
            
            // 发送保活包
            _, err := conn.Write([]byte("PING"))
            if err != nil {
                log.Printf("Keep-alive failed, destroying resource: %v", err)
                res.Destroy()
                continue
            }
            
            res.Release()
        }
    }
}
```

## 九、总结

Puddle 是一个强大而灵活的资源池管理库，适用于多种场景。它的设计哲学是保持最小必要功能，同时提供出色的性能和稳定性。

### 关键要点

1. **资源池配置**：合理设置资源池大小，根据业务需求调整
2. **资源管理**：使用 defer 确保资源正确释放
3. **错误处理**：区分不同类型的错误，采取相应的处理策略
4. **监控告警**：定期监控资源池状态，及时发现和解决问题
5. **性能优化**：通过预热、批量操作等方式提高性能
6. **并发安全**：Puddle 本身是并发安全的，无需额外锁机制

### 适用场景

- 数据库连接池
- 网络连接池
- 文件句柄管理
- 其他需要复用的外部资源

### 最佳实践

- 使用 Context 控制超时
- 实现资源健康检查
- 监控资源池统计信息
- 预热资源池
- 实现资源保活机制

通过掌握 Puddle 的使用方法和最佳实践，开发者可以构建高效、稳定的资源池，提高应用的性能和可靠性。

## 参考文献

1. Puddle GitHub Repository: https://github.com/jackc/puddle
2. Puddle Documentation: https://pkg.go.dev/github.com/jackc/puddle
3. Go sync.Pool Documentation: https://pkg.go.dev/sync#Pool
4. pgx Documentation: https://github.com/jackc/pgx
