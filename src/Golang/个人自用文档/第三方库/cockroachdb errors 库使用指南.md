---
title: Go cockroachdb/errors 库使用指南
date: 2026-05-09
footer: Trae编辑
---

# Go cockroachdb/errors 库使用指南

## 概述

`github.com/cockroachdb/errors` 是 CockroachDB 开源的一款增强型错误处理库，旨在作为 `github.com/pkg/errors` 和 Go 标准库 `errors` 的**无缝替代品**。它提供了完整的错误处理能力，特别适合分布式系统中错误的网络传输和跨版本兼容性。

::: info 核心优势

- **网络可移植性**: 支持错误对象的序列化/反序列化，适合分布式系统
- **PII-free 安全详情**: 原生支持不含敏感信息的错误详情
- **完整的堆栈跟踪**: 自动捕获和格式化堆栈信息
- **Go 1.13+ 兼容性**: 完全支持 `errors.Is`、`errors.As`、`errors.Unwrap`
- **丰富的错误包装**: 支持消息包装、提示信息、次要错误等
- **模块化设计**: 多个子包提供不同功能扩展

:::

## 核心特性

### 1. 错误创建

```go
// 创建基本错误（自动包含堆栈跟踪）
err := errors.New("database connection failed")

// 创建带格式化消息的错误
err := errors.Errorf("failed to fetch user %d", userID)

// 断言失败错误
err := errors.AssertionFailedf("unexpected value: %d", value)
```

### 2. 错误包装

```go
// 包装错误并添加消息前缀
err := errors.Wrap(originalErr, "operation failed")

// 带格式化消息的包装
err := errors.Wrapf(originalErr, "failed to process request %s", requestID)

// 添加消息（不改变错误链）
err := errors.WithMessage(originalErr, "additional context")
err := errors.WithMessagef(originalErr, "context for %s", resource)
```

### 3. 堆栈跟踪

```go
// 添加堆栈跟踪
err := errors.WithStack(originalErr)

// 指定调用深度的堆栈跟踪
err := errors.WithStackDepth(originalErr, 2)

// 获取堆栈信息
stackTrace := errors.GetOneLineSource(err)
```

### 4. 安全详情（PII-free）

```go
// 添加安全详情（不含敏感信息）
err := errors.WithSafeDetails(originalErr, "request ID: %s", reqID)

// 获取所有安全详情
details := errors.GetAllSafeDetails(err)
```

### 5. 提示信息

```go
// 添加用户友好的提示
err := errors.WithHint(originalErr, "Check your network connection")

// 带格式化的提示
err := errors.WithHintf(originalErr, "See documentation at %s", docsURL)

// 获取所有提示
hints := errors.GetAllHints(err)
```

### 6. 次要错误

```go
// 添加次要错误（处理错误时产生的额外错误）
err := errors.WithSecondaryError(primaryErr, secondaryErr)
```

### 7. 错误检查

```go
// 检查错误类型（支持错误链）
if errors.Is(err, io.EOF) {
    // 处理 EOF
}

// 类型断言
var target *MyError
if errors.As(err, &target) {
    // 处理特定类型的错误
}

// 获取根因
cause := errors.Cause(err)
```

## 安装

```bash
go get -u github.com/cockroachdb/errors
```

## 快速开始

### 基本用法

```go
package main

import (
    "fmt"
    "github.com/cockroachdb/errors"
)

func main() {
    err := fetchUser(123)
    if err != nil {
        fmt.Printf("%+v\n", err)
        return
    }
    fmt.Println("User fetched successfully")
}

func fetchUser(id int) error {
    err := queryDatabase(id)
    if err != nil {
        return errors.Wrapf(err, "failed to fetch user %d", id)
    }
    return nil
}

func queryDatabase(id int) error {
    return errors.New("connection timeout")
}
```

输出示例：

```
failed to fetch user 123: connection timeout
(1) attached stack trace
  -- stack trace:
   | main.fetchUser
   | /path/to/main.go:18
   | main.main
   | /path/to/main.go:8
Wraps: (2) connection timeout
Error types: (1) *withstack.withStack (2) *errutil.leafError
```

### 带提示和详情的错误

```go
func processRequest(req *Request) error {
    if err := validateRequest(req); err != nil {
        err = errors.WithHint(err, "Ensure all required fields are present")
        err = errors.WithSafeDetails(err, "request_id: %s", req.ID)
        return errors.Wrap(err, "request validation failed")
    }
    return nil
}
```

## 子包功能

### errbase - 基础错误处理

```go
import "github.com/cockroachdb/errors/errbase"

// 序列化错误（用于网络传输）
encoded := errbase.EncodeError(ctx, err)

// 反序列化错误
decoded := errbase.DecodeError(ctx, encoded)

// 获取所有安全详情
details := errbase.GetAllSafeDetails(err)
```

### errorspb - Protobuf 序列化

```go
import "github.com/cockroachdb/errors/errorspb"

// 转换为 protobuf 消息
pb := errorspb.EncodeError(err)

// 从 protobuf 消息恢复
err := errorspb.DecodeError(pb)
```

### extgrpc - gRPC 扩展

```go
import "github.com/cockroachdb/errors/extgrpc"

// 将错误转换为 gRPC status
status := extgrpc.ToStatus(err)

// 从 gRPC status 恢复错误
err := extgrpc.FromStatus(status)
```

### exthttp - HTTP 扩展

```go
import "github.com/cockroachdb/errors/exthttp"

// 将错误写入 HTTP 响应
exthttp.WriteError(w, err)

// 从 HTTP 响应读取错误
err := exthttp.ReadError(r)
```

### hintdetail - 提示和详情

```go
import "github.com/cockroachdb/errors/hintdetail"

// 添加提示
err := hintdetail.WithHint(err, "Try again later")

// 添加详情
err := hintdetail.WithDetail(err, "Internal code: 123")
```

### domains - 错误域

```go
import "github.com/cockroachdb/errors/domains"

// 标记错误已在特定域处理
err := domains.HandledInDomain(err, "database")

// 检查错误是否已处理
if domains.IsHandled(err) {
    // 错误已处理
}
```

## 高级功能

### 自定义错误类型

```go
type CustomError struct {
    Code    int
    Message string
    Cause   error
}

func (e *CustomError) Error() string {
    return e.Message
}

func (e *CustomError) Unwrap() error {
    return e.Cause
}

func (e *CustomError) SafeFormatError(p errors.Printer) (next error) {
    if p.Detail() {
        p.Printf("error code: %d", errors.Safe(e.Code))
    }
    return e.Cause
}
```

### 错误序列化

```go
func sendErrorOverNetwork(err error) ([]byte, error) {
    encoded := errbase.EncodeError(context.Background(), err)
    return proto.Marshal(&encoded)
}

func receiveErrorFromNetwork(data []byte) error {
    var encoded errbase.EncodedError
    if err := proto.Unmarshal(data, &encoded); err != nil {
        return err
    }
    return errbase.DecodeError(context.Background(), encoded)
}
```

### Sentry 集成

```go
import (
    "github.com/cockroachdb/errors"
    "github.com/getsentry/sentry-go"
)

func reportToSentry(err error) {
    event := sentry.NewEvent()
    event.Message = err.Error()
    
    // 获取安全详情
    details := errors.FlattenDetails(err)
    for _, detail := range details {
        event.Extra[detail.Type] = detail.Message
    }
    
    sentry.CaptureEvent(event)
}
```

## Good Practice

### 1. 使用安全详情避免 PII 泄露

```go
// ✅ 正确：使用 SafeDetails 存储非敏感信息
err := errors.WithSafeDetails(err, "request_id: %s", reqID)

// ❌ 错误：避免在错误消息中包含敏感信息
err := errors.Errorf("user %s login failed", username) // 可能包含 PII
```

### 2. 使用提示帮助用户

```go
err := errors.New("connection refused")
err = errors.WithHint(err, "Check if the server is running")
err = errors.WithHintf(err, "See %s for troubleshooting", docsURL)
```

### 3. 分层错误处理

```go
// 底层：返回原始错误
func dbQuery() error {
    return errors.New("database error")
}

// 中间层：添加上下文
func serviceCall() error {
    if err := dbQuery(); err != nil {
        return errors.Wrap(err, "service operation failed")
    }
    return nil
}

// 顶层：添加用户友好提示
func handler() error {
    if err := serviceCall(); err != nil {
        return errors.WithHint(err, "Please try again later")
    }
    return nil
}
```

### 4. 错误类型检查

```go
// ✅ 使用 errors.Is 检查错误类型
if errors.Is(err, os.ErrNotExist) {
    // 处理文件不存在
}

// ✅ 使用 errors.As 进行类型断言
var sqlErr *pq.Error
if errors.As(err, &sqlErr) {
    // 处理 SQL 错误
}
```

### 5. 处理多个错误

```go
// 使用 errors.Join 组合多个错误
err1 := errors.New("error 1")
err2 := errors.New("error 2")
combined := errors.Join(err1, err2)
```

### 6. 标记错误已处理

```go
func handleError(err error) {
    // 处理错误后标记为已处理
    handledErr := errors.Handled(err)
    
    // 记录日志但不再向上传播
    logger.Error(handledErr)
}
```

## 与标准库对比

| 功能 | 标准库 errors | pkg/errors | cockroachdb/errors |
|------|-------------|------------|-------------------|
| 堆栈跟踪 | ❌ | ✅ | ✅ |
| 错误包装 | ✅ (Go 1.13+) | ✅ | ✅ |
| 网络可移植 | ❌ | ❌ | ✅ |
| PII-free 详情 | ❌ | ❌ | ✅ |
| 提示信息 | ❌ | ❌ | ✅ |
| 次要错误 | ❌ | ❌ | ✅ |
| gRPC 支持 | ❌ | ❌ | ✅ |
| HTTP 支持 | ❌ | ❌ | ✅ |

## 常见问题

### 1. 如何获取完整的错误信息？

```go
// 使用 %+v 格式化获取完整信息
fmt.Printf("%+v\n", err)
```

### 2. 如何自定义错误格式？

```go
type MyError struct{}

func (e *MyError) Format(s fmt.State, verb rune) {
    errors.FormatError(e, s, verb)
}

func (e *MyError) SafeFormatError(p errors.Printer) (next error) {
    if p.Detail() {
        p.Printf("custom detail")
    }
    return nil
}
```

### 3. 如何跨版本兼容？

```go
// 使用 errbase 注册类型迁移
errbase.RegisterTypeMigration(
    "old.package.path.OldError",
    "new.package.path.NewError",
    NewError{},
)
```

### 4. 如何测试错误处理？

```go
func TestErrorHandling(t *testing.T) {
    err := myFunction()
    
    // 检查错误类型
    if !errors.Is(err, expectedErr) {
        t.Errorf("expected %v, got %v", expectedErr, err)
    }
    
    // 检查错误消息
    if !strings.Contains(err.Error(), "expected message") {
        t.Errorf("unexpected error message: %s", err.Error())
    }
}
```

## 参考资源

- [官方 GitHub 仓库](https://github.com/cockroachdb/errors)
- [官方文档](https://pkg.go.dev/github.com/cockroachdb/errors)
- [扩展包文档](https://pkg.go.dev/github.com/cockroachdb/errors/errbase)

::: info 总结

cockroachdb/errors 是一款功能强大的错误处理库，特别适合需要错误网络传输、PII 保护和丰富上下文信息的分布式系统。它与标准库完全兼容，同时提供了许多高级功能，可以显著提升错误处理的质量和可观测性。

:::
