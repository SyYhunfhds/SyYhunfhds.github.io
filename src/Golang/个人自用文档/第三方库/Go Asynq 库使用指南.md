---
title: Go Asynq 库使用指南
date: 2026-03-23
footer: Trae编辑
---

# Go Asynq 库使用指南

:::note 参考资料
- [Asynq GitHub 仓库](https://github.com/hibiken/asynq)
- [Asynq 官方文档](https://github.com/hibiken/asynq/wiki)
:::

[[toc]]

## 1. 什么是 Asynq？

Asynq 是一个 Go 语言实现的分布式任务队列和异步处理库，基于 Redis 存储。它提供了轻量级、易于使用的 API，用于处理需要异步执行的任务。

### 1.1 主要特点

:::info 核心特性
- **保证至少执行一次**：任务会被持久化，确保不会丢失
- **失败重试**：任务失败后会自动重试，可配置重试次数和延迟
- **任务调度**：支持定时任务和延迟任务
- **优先级队列**：支持任务优先级
- **崩溃恢复**：服务重启后能继续处理未完成的任务
- **Web UI**：提供可视化管理界面
- **分布式**：支持多个 worker 节点并行处理任务
:::

### 1.2 适用场景

- **发送邮件**：避免邮件发送阻塞主流程
- **图像处理**：如生成缩略图、OCR 等
- **数据导入/导出**：大型数据处理
- **定时任务**：如备份、清理等
- **第三方 API 调用**：避免网络延迟影响主服务

## 2. 安装与配置

### 2.1 安装

```bash
go get github.com/hibiken/asynq
```

### 2.2 依赖

- **Redis**：Asynq 使用 Redis 作为后端存储，需要 Redis 3.0+ 版本
- **Go**：需要 Go 1.13+ 版本

### 2.3 基本配置

```go
import (
    "context"
    "github.com/hibiken/asynq"
)

// Redis 连接配置
redisAddr := "localhost:6379"

// 客户端配置
clientOpts := asynq.RedisClientOpt{
    Addr: redisAddr,
    // 可选配置
    DB:   0,              // Redis 数据库编号
    Password: "",          // Redis 密码
    DialTimeout: 5 * time.Second, // 连接超时
}

// 服务器配置
serverOpts := asynq.RedisClientOpt{
    Addr: redisAddr,
}
```

## 3. 核心概念

### 3.1 任务（Task）

任务是 Asynq 的基本执行单元，包含：

- **类型**：任务的唯一标识符
- **载荷**：任务的具体数据（JSON 格式）
- **选项**：执行选项（如重试次数、队列名称等）

### 3.2 队列（Queue）

队列用于组织和管理任务，支持：

- **默认队列**：无指定队列时使用
- **命名队列**：用户自定义队列
- **优先级队列**：根据任务优先级排序

### 3.3 客户端（Client）

用于创建和发送任务：

- **创建任务**：指定任务类型和载荷
- **发送任务**：立即执行、延迟执行或定时执行

### 3.4 服务器（Server）

用于处理任务：

- **注册处理器**：为不同类型的任务注册处理函数
- **启动 worker**：启动多个 worker 并发处理任务
- **监控任务**：跟踪任务执行状态

## 4. 基本用法

### 4.1 创建客户端

```go
import (
    "github.com/hibiken/asynq"
)

// 创建客户端
client := asynq.NewClient(asynq.RedisClientOpt{
    Addr: "localhost:6379",
})

// 关闭客户端
defer client.Close()
```

### 4.2 定义任务

```go
const (
    // 任务类型常量
    TypeEmailDelivery = "email:deliver"
    TypeImageResize   = "image:resize"
    TypeDataExport    = "data:export"
)

// 任务载荷结构
type EmailDeliveryPayload struct {
    UserID   int    `json:"user_id"`
    Template string `json:"template"`
}

type ImageResizePayload struct {
    ImageID   int    `json:"image_id"`
    Width     int    `json:"width"`
    Height    int    `json:"height"`
    OutputDir string `json:"output_dir"`
}
```

### 4.3 发送任务

#### 4.3.1 立即执行的任务

```go
// 创建任务
payload, err := json.Marshal(EmailDeliveryPayload{
    UserID:   123,
    Template: "welcome",
})
if err != nil {
    log.Fatalf("Failed to marshal payload: %v", err)
}

// 发送任务
task := asynq.NewTask(TypeEmailDelivery, payload)
info, err := client.Enqueue(task)
if err != nil {
    log.Fatalf("Failed to enqueue task: %v", err)
}

log.Printf("Enqueued task: %s", info.ID)
```

#### 4.3.2 延迟执行的任务

```go
// 5 分钟后执行
task := asynq.NewTask(TypeEmailDelivery, payload)
info, err := client.Enqueue(task, asynq.ProcessIn(5*time.Minute))
if err != nil {
    log.Fatalf("Failed to enqueue task: %v", err)
}
```

#### 4.3.3 定时执行的任务

```go
// 在指定时间执行
executionTime := time.Date(2026, 3, 24, 12, 0, 0, 0, time.UTC)
task := asynq.NewTask(TypeEmailDelivery, payload)
info, err := client.Enqueue(task, asynq.At(executionTime))
if err != nil {
    log.Fatalf("Failed to enqueue task: %v", err)
}
```

#### 4.3.4 带选项的任务

```go
task := asynq.NewTask(TypeEmailDelivery, payload)
info, err := client.Enqueue(task,
    asynq.Queue("critical"),          // 指定队列
    asynq.MaxRetry(3),                 // 最大重试次数
    asynq.Timeout(5*time.Minute),      // 执行超时
    asynq.Deadline(time.Now().Add(1*time.Hour)), // 截止时间
    asynq.Unique(time.Hour),           // 1小时内唯一
)
if err != nil {
    log.Fatalf("Failed to enqueue task: %v", err)
}
```

### 4.4 创建服务器

```go
import (
    "context"
    "log"
    "github.com/hibiken/asynq"
)

// 定义服务器
server := asynq.NewServer(
    asynq.RedisClientOpt{Addr: "localhost:6379"},
    asynq.Config{
        // 并发 worker 数量
        Concurrency: 10,
        // 队列配置
        Queues: map[string]int{
            "critical": 6, // 优先级 6
            "default":  3, // 优先级 3
            "low":      1, // 优先级 1
        },
        // 任务超时
        Timeout: 30 * time.Second,
        // 最大重试次数
        MaxRetry: 10,
    },
)
```

### 4.5 注册任务处理器

```go
// 创建处理器映射
mux := asynq.NewServeMux()

// 注册处理器
mux.HandleFunc(TypeEmailDelivery, handleEmailDelivery)
mux.HandleFunc(TypeImageResize, handleImageResize)
mux.HandleFunc(TypeDataExport, handleDataExport)

// 处理器函数
func handleEmailDelivery(ctx context.Context, task *asynq.Task) error {
    var payload EmailDeliveryPayload
    if err := json.Unmarshal(task.Payload(), &payload); err != nil {
        return fmt.Errorf("failed to unmarshal payload: %w", err)
    }

    // 处理邮件发送
    log.Printf("Sending email to user %d with template %s", payload.UserID, payload.Template)
    // 模拟邮件发送
    time.Sleep(2 * time.Second)
    log.Printf("Email sent successfully to user %d", payload.UserID)

    return nil
}

func handleImageResize(ctx context.Context, task *asynq.Task) error {
    var payload ImageResizePayload
    if err := json.Unmarshal(task.Payload(), &payload); err != nil {
        return fmt.Errorf("failed to unmarshal payload: %w", err)
    }

    // 处理图像处理
    log.Printf("Resizing image %d to %dx%d", payload.ImageID, payload.Width, payload.Height)
    // 模拟图像处理
    time.Sleep(5 * time.Second)
    log.Printf("Image %d resized successfully", payload.ImageID)

    return nil
}
```

### 4.6 启动服务器

```go
// 启动服务器
if err := server.Start(mux); err != nil {
    log.Fatalf("Failed to start server: %v", err)
}
```

## 5. 高级特性

### 5.1 任务选项

| **选项** | **描述** | **使用场景** |
| -------- | -------- | ------------ |
| `Queue(name)` | 指定队列名称 | 任务分类、优先级管理 |
| `ProcessIn(d)` | 延迟执行 | 定时操作、冷却期 |
| `At(t)` | 定时执行 | 特定时间点执行 |
| `MaxRetry(n)` | 最大重试次数 | 容错处理 |
| `Timeout(d)` | 执行超时 | 防止任务卡住 |
| `Deadline(t)` | 截止时间 | 确保任务在指定时间前完成 |
| `Unique(d)` | 唯一任务 | 防止重复执行 |
| `Group(g)` | 任务分组 | 批量管理相关任务 |

### 5.2 任务状态管理

Asynq 中的任务有以下状态：

| **状态** | **描述** |
| -------- | -------- |
| `Pending` | 等待处理 |
| `Active` | 正在处理 |
| `Scheduled` | 计划执行 |
| `Retry` | 等待重试 |
| `Completed` | 执行完成 |
| `Failed` | 执行失败 |

### 5.3 任务监控

#### 5.3.1 命令行工具

Asynq 提供了命令行工具 `asynq` 用于监控和管理任务：

```bash
# 安装命令行工具
go install github.com/hibiken/asynq/tools/asynq@latest

# 查看队列状态
asynq stats

# 查看待处理任务
asynq list pending

# 查看失败任务
asynq list failed

# 重试失败任务
asynq retry all
```

#### 5.3.2 Web UI

Asynq 提供了 Web UI 用于可视化管理任务：

```go
import (
    "github.com/hibiken/asynq"
    "github.com/hibiken/asynqmon"
    "net/http"
)

// 启动 Web UI
http.HandleFunc("/asynq", asynqmon.NewHandler(
    asynqmon.WithRedisAddr("localhost:6379"),
    asynqmon.WithRootPath("/asynq"),
))

log.Println("Asynq Web UI available at http://localhost:8080/asynq")
http.ListenAndServe(":8080", nil)
```

### 5.4 错误处理

```go
func handleTask(ctx context.Context, task *asynq.Task) error {
    // 业务逻辑
    if err := doSomething(); err != nil {
        // 记录错误
        log.Printf("Error processing task: %v", err)
        
        // 返回错误会触发重试
        return err
    }
    return nil
}
```

### 5.5 任务取消

```go
func handleLongRunningTask(ctx context.Context, task *asynq.Task) error {
    for i := 0; i < 100; i++ {
        // 检查是否被取消
        select {
        case <-ctx.Done():
            // 任务被取消
            log.Println("Task cancelled")
            return ctx.Err()
        default:
            // 继续执行
        }
        
        // 执行工作
        time.Sleep(100 * time.Millisecond)
    }
    return nil
}
```

## 6. 完整示例

### 6.1 客户端示例

```go
package main

import (
    "encoding/json"
    "log"
    "time"

    "github.com/hibiken/asynq"
)

const (
    TypeEmailDelivery = "email:deliver"
    TypeImageResize   = "image:resize"
)

type EmailDeliveryPayload struct {
    UserID   int    `json:"user_id"`
    Template string `json:"template"`
}

type ImageResizePayload struct {
    ImageID   int    `json:"image_id"`
    Width     int    `json:"width"`
    Height    int    `json:"height"`
}

func main() {
    // 创建客户端
    client := asynq.NewClient(asynq.RedisClientOpt{
        Addr: "localhost:6379",
    })
    defer client.Close()

    // 发送邮件任务
    emailPayload, _ := json.Marshal(EmailDeliveryPayload{
        UserID:   123,
        Template: "welcome",
    })
    emailTask := asynq.NewTask(TypeEmailDelivery, emailPayload)
    emailInfo, err := client.Enqueue(emailTask)
    if err != nil {
        log.Fatalf("Failed to enqueue email task: %v", err)
    }
    log.Printf("Enqueued email task: %s", emailInfo.ID)

    // 发送图像处理任务
    imagePayload, _ := json.Marshal(ImageResizePayload{
        ImageID:   456,
        Width:     800,
        Height:    600,
    })
    imageTask := asynq.NewTask(TypeImageResize, imagePayload)
    imageInfo, err := client.Enqueue(imageTask, asynq.Queue("critical"))
    if err != nil {
        log.Fatalf("Failed to enqueue image task: %v", err)
    }
    log.Printf("Enqueued image task: %s", imageInfo.ID)

    // 发送延迟任务
    delayPayload, _ := json.Marshal(EmailDeliveryPayload{
        UserID:   789,
        Template: "reminder",
    })
    delayTask := asynq.NewTask(TypeEmailDelivery, delayPayload)
    delayInfo, err := client.Enqueue(delayTask, asynq.ProcessIn(5*time.Minute))
    if err != nil {
        log.Fatalf("Failed to enqueue delay task: %v", err)
    }
    log.Printf("Enqueued delay task: %s", delayInfo.ID)
}
```

### 6.2 服务器示例

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "time"

    "github.com/hibiken/asynq"
    "github.com/hibiken/asynqmon"
)

const (
    TypeEmailDelivery = "email:deliver"
    TypeImageResize   = "image:resize"
)

type EmailDeliveryPayload struct {
    UserID   int    `json:"user_id"`
    Template string `json:"template"`
}

type ImageResizePayload struct {
    ImageID   int    `json:"image_id"`
    Width     int    `json:"width"`
    Height    int    `json:"height"`
}

func main() {
    // 创建服务器
    server := asynq.NewServer(
        asynq.RedisClientOpt{Addr: "localhost:6379"},
        asynq.Config{
            Concurrency: 10,
            Queues: map[string]int{
                "critical": 6,
                "default":  3,
                "low":      1,
            },
            Timeout:  30 * time.Second,
            MaxRetry: 10,
        },
    )

    // 创建处理器映射
    mux := asynq.NewServeMux()
    mux.HandleFunc(TypeEmailDelivery, handleEmailDelivery)
    mux.HandleFunc(TypeImageResize, handleImageResize)

    // 启动 Web UI
    go func() {
        http.HandleFunc("/asynq", asynqmon.NewHandler(
            asynqmon.WithRedisAddr("localhost:6379"),
            asynqmon.WithRootPath("/asynq"),
        ))
        log.Println("Asynq Web UI available at http://localhost:8080/asynq")
        if err := http.ListenAndServe(":8080", nil); err != nil {
            log.Printf("Failed to start Web UI: %v", err)
        }
    }()

    // 启动服务器
    log.Println("Starting Asynq server...")
    if err := server.Start(mux); err != nil {
        log.Fatalf("Failed to start server: %v", err)
    }
}

func handleEmailDelivery(ctx context.Context, task *asynq.Task) error {
    var payload EmailDeliveryPayload
    if err := json.Unmarshal(task.Payload(), &payload); err != nil {
        return fmt.Errorf("failed to unmarshal payload: %w", err)
    }

    log.Printf("Sending email to user %d with template %s", payload.UserID, payload.Template)
    // 模拟邮件发送
    time.Sleep(2 * time.Second)
    log.Printf("Email sent successfully to user %d", payload.UserID)

    return nil
}

func handleImageResize(ctx context.Context, task *asynq.Task) error {
    var payload ImageResizePayload
    if err := json.Unmarshal(task.Payload(), &payload); err != nil {
        return fmt.Errorf("failed to unmarshal payload: %w", err)
    }

    log.Printf("Resizing image %d to %dx%d", payload.ImageID, payload.Width, payload.Height)
    // 模拟图像处理
    time.Sleep(5 * time.Second)
    log.Printf("Image %d resized successfully", payload.ImageID)

    return nil
}
```

## 7. 最佳实践

### 7.1 任务设计

::: tip 任务设计原则
- **任务应该幂等**：重复执行不会产生副作用
- **任务应该可序列化**：使用 JSON 格式的载荷
- **任务应该有合理的超时**：避免长时间占用 worker
- **任务应该有合理的重试策略**：根据任务类型设置合适的重试次数
:::

### 7.2 队列管理

```go
// 合理的队列配置
Queues: map[string]int{
    "critical": 6, // 紧急任务，如支付处理
    "default":  3, // 普通任务，如邮件发送
    "low":      1, // 低优先级任务，如日志清理
}
```

### 7.3 错误处理

```go
func handleTask(ctx context.Context, task *asynq.Task) error {
    // 业务逻辑
    if err := doSomething(); err != nil {
        // 记录详细错误信息
        log.Printf("Error processing task %s: %v", task.ID, err)
        
        // 对于不可恢复的错误，返回 nil 避免重试
        if isUnrecoverableError(err) {
            log.Printf("Unrecoverable error, not retrying task %s", task.ID)
            return nil
        }
        
        // 对于可恢复的错误，返回错误触发重试
        return err
    }
    return nil
}
```

### 7.4 监控与告警

- **使用 Web UI**：实时监控任务状态
- **设置指标**：使用 Prometheus 监控队列长度、任务执行时间等
- **配置告警**：当队列积压或失败任务过多时告警

### 7.5 性能优化

- **合理设置并发数**：根据服务器资源调整 `Concurrency`
- **批量处理**：对于相似任务，考虑批量处理减少 Redis 操作
- **合理设置超时**：避免任务长时间占用 worker
- **使用唯一任务**：避免重复执行相同任务

### 7.6 部署建议

- **Redis 高可用**：使用 Redis Sentinel 或 Redis Cluster 确保 Redis 高可用
- **Worker 集群**：部署多个 worker 节点提高处理能力
- **配置分离**：将客户端和服务器配置分离，便于管理
- **日志管理**：集中管理日志，便于问题排查

## 8. 常见问题

### 8.1 任务执行失败

**症状**：任务状态为 `Failed`

**解决方案**：
- 检查任务处理器中的错误
- 查看日志了解具体错误信息
- 调整任务超时和重试策略
- 使用 `asynq retry` 命令重试失败任务

### 8.2 队列积压

**症状**：队列中任务数量持续增长

**解决方案**：
- 增加 worker 节点或并发数
- 检查任务执行时间，优化处理逻辑
- 考虑拆分大型任务为多个小任务
- 调整队列优先级设置

### 8.3 Redis 连接问题

**症状**：客户端或服务器无法连接 Redis

**解决方案**：
- 检查 Redis 服务是否运行
- 验证 Redis 连接配置
- 检查网络连接和防火墙设置
- 考虑使用 Redis 连接池

### 8.4 任务执行超时

**症状**：任务被标记为超时

**解决方案**：
- 检查任务执行时间，优化处理逻辑
- 适当增加任务超时时间
- 考虑将长任务拆分为多个短任务

## 9. 总结

Asynq 是一个功能强大、易于使用的 Go 语言任务队列库，它提供了：

- **简单而直观的 API**：易于集成到现有项目中
- **强大的任务管理功能**：支持延迟执行、定时执行、失败重试等
- **可靠的任务处理**：基于 Redis 的持久化存储
- **丰富的监控工具**：命令行工具和 Web UI
- **高度可扩展**：支持分布式部署

通过合理使用 Asynq，您可以：
- 提高应用响应速度，将耗时操作异步处理
- 提高系统可靠性，通过重试机制处理临时故障
- 提高系统可扩展性，通过分布式 worker 处理高并发任务
- 简化代码结构，将业务逻辑与异步处理分离

Asynq 是构建可靠、高效的异步任务处理系统的理想选择，特别适合需要处理大量后台任务的应用场景。
