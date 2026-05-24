---
title: GoFrame错误处理库gerror使用指南
date: 2026-05-22
footer: AI创作内容
---

# GoFrame错误处理库gerror使用指南

本文详细介绍GoFrame框架的`gerror`错误处理组件，包括核心功能、错误码体系、堆栈跟踪、最佳实践等。

## 目录

- [概述](#概述)
- [基础错误创建](#基础错误创建)
- [错误包装](#错误包装)
- [错误码体系](#错误码体系)
- [堆栈跟踪](#堆栈跟踪)
- [错误比较](#错误比较)
- [HTTP异常处理](#http异常处理)
- [最佳实践](#最佳实践)

## 概述

`gerror`是GoFrame框架提供的统一错误处理组件，具有以下核心特点：

| 特性 | 说明 |
|------|------|
| **自动堆栈** | 自动捕获错误发生位置的堆栈信息 |
| **错误码支持** | 内置错误码体系，支持自定义扩展 |
| **链式错误** | 支持错误包装，保留原始错误链 |
| **i18n支持** | 支持多语言错误消息 |
| **高性能** | 经过性能优化，零分配设计 |

### 常用导入

```go
import "github.com/gogf/gf/v2/errors/gerror"
```

## 基础错误创建

### 创建简单错误

```go
// 创建简单错误
err := gerror.New("数据库连接失败")

// 创建格式化错误
err := gerror.Newf("用户ID %d 不存在", 123)

// 输出错误信息
fmt.Println(err.Error())
```

### 错误选项

```go
// 使用选项创建错误
err := gerror.NewOption(gerror.Option{
    Text: "自定义错误",
    Code: 10001,
})
```

### 判断错误是否为空

```go
// 判断错误是否存在
if err != nil {
    // 处理错误
}

// 判断是否为gerror类型
if gerror.HasStack(err) {
    // 包含堆栈信息
}
```

## 错误包装

### 基础包装

```go
// 包装错误，保留原始错误链
err1 := errors.New("底层错误")
err2 := gerror.Wrap(err1, "业务层错误")

// 格式化包装
err3 := gerror.Wrapf(err1, "业务层错误: 用户ID %d", 123)

// 输出完整错误链
fmt.Println(err3.Error())
// 输出: 业务层错误: 用户ID 123: 底层错误
```

### 避免重复包装

```go
// 错误：不要在消息中重复包含原始错误
err2 := gerror.Wrapf(err1, "error occurred: %v", err1)
// 输出会重复: error occurred: 底层错误: 底层错误

// 正确：只添加业务描述
err2 := gerror.Wrap(err1, "error occurred")
// 输出: error occurred: 底层错误
```

### 跳过堆栈帧

```go
// 创建错误时跳过指定数量的堆栈帧
err := gerror.NewSkip(1, "跳过当前帧")

// 格式化版本
err := gerror.NewSkipf(1, "跳过当前帧: %s", "详情")
```

## 错误码体系

### 内置错误码

GoFrame提供了内置的错误码定义：

```go
// 常用内置错误码
gcode.CodeNil      // 无错误
gcode.CodeOk       // 成功
gcode.CodeInternal // 内部错误
gcode.CodeInvalidParameter // 参数错误
gcode.CodeNotFound // 资源不存在
gcode.CodeNotAuthorized // 未授权
```

### 创建带错误码的错误

```go
// 创建带错误码的错误
err := gerror.NewCode(10001, "用户不存在")

// 格式化版本
err := gerror.NewCodef(10002, "订单ID %d 不存在", 456)

// 获取错误码
code := gerror.Code(err)
// 输出: 10001
```

### 包装错误并添加错误码

```go
// 包装错误并添加错误码
err1 := errors.New("数据库查询失败")
err2 := gerror.WrapCode(10003, err1, "查询用户失败")

// 格式化版本
err3 := gerror.WrapCodef(10003, err1, "查询用户ID %d 失败", 123)

// 获取错误码
code := gerror.Code(err3)
// 输出: 10003
```

### 自定义错误码

```go
// 定义业务错误码常量
const (
    CodeUserNotFound      = 10001
    CodeOrderNotFound     = 10002
    CodeInsufficientFunds = 10003
    CodePermissionDenied  = 10004
)

// 使用自定义错误码
err := gerror.NewCode(CodeUserNotFound, "用户不存在")
```

### 错误码接口

```go
// 实现自定义错误码接口
type MyCode int

func (c MyCode) Code() int         { return int(c) }
func (c MyCode) Message() string    { return "自定义错误" }
func (c MyCode) Detail() interface{} { return nil }

// 使用自定义错误码
err := gerror.NewCode(MyCode(20001), "自定义错误")
```

## 堆栈跟踪

### 获取堆栈信息

```go
// 创建带堆栈的错误
err := gerror.New("测试错误")

// 获取堆栈字符串
stack := gerror.Stack(err)

// 获取堆栈数组
stackArray := gerror.StackArray(err)

// 检查是否包含堆栈
hasStack := gerror.HasStack(err)
```

### 打印堆栈信息

```go
// 使用 %+v 格式化打印完整堆栈
err := gerror.New("测试错误")
fmt.Printf("%+v", err)

// 输出示例:
// 测试错误
// 1. github.com/gogf/gf/v2/errors/gerror.New
//    /path/to/gerror/gerror.go:100
// 2. main.main
//    /path/to/main.go:20
```

### 访问错误链

```go
// 获取底层错误
err1 := errors.New("底层错误")
err2 := gerror.Wrap(err1, "中间层错误")
err3 := gerror.Wrap(err2, "顶层错误")

// 获取原始错误
originErr := gerror.Cause(err3)
// originErr == err1

// 获取错误链长度
length := gerror.Len(err3)
// length == 3
```

## 错误比较

### 错误相等性判断

```go
err1 := gerror.New("same error")
err2 := gerror.New("same error")

// 判断两个错误是否相同
isEqual := gerror.Equal(err1, err2)

// 判断错误链中是否包含指定错误
hasErr := gerror.Is(err3, err1)
```

### 使用errors.Is

```go
import "errors"

err := gerror.New("test error")
target := errors.New("test error")

// 判断错误链中是否存在目标错误
isMatch := errors.Is(err, target)
```

## HTTP异常处理

### 中间件错误捕获

```go
package main

import (
    "github.com/gogf/gf/v2/frame/g"
    "github.com/gogf/gf/v2/net/ghttp"
)

func ErrorHandler(r *ghttp.Request) {
    r.Middleware.Next()
    
    if err := r.GetError(); err != nil {
        // 记录错误日志
        g.Log("exception").Error(err)
        
        // 返回友好的错误信息
        r.Response.ClearBuffer()
        r.Response.WriteJson(g.Map{
            "code":    -1,
            "message": "服务器内部错误",
        })
    }
}

func main() {
    s := g.Server()
    s.Use(ErrorHandler)
    
    s.GET("/test", func(r *ghttp.Request) {
        panic("测试异常")
    })
    
    s.SetPort(8080)
    s.Run()
}
```

### 统一错误响应

```go
// 统一错误响应结构
type ErrorResponse struct {
    Code    int         `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data"`
}

func ErrorHandler(r *ghttp.Request) {
    r.Middleware.Next()
    
    if err := r.GetError(); err != nil {
        code := gerror.Code(err)
        if code == 0 {
            code = -1 // 默认错误码
        }
        
        r.Response.ClearBuffer()
        r.Response.WriteJson(ErrorResponse{
            Code:    code,
            Message: err.Error(),
            Data:    nil,
        })
    }
}
```

## 最佳实践

### 1. 统一错误处理

```go
// 错误处理工具函数
package errutil

import (
    "github.com/gogf/gf/v2/errors/gerror"
)

// New 创建业务错误
func New(code int, message string) error {
    return gerror.NewCode(code, message)
}

// Newf 创建格式化业务错误
func Newf(code int, format string, args ...interface{}) error {
    return gerror.NewCodef(code, format, args...)
}

// Wrap 包装错误
func Wrap(code int, err error, message string) error {
    return gerror.WrapCode(code, err, message)
}

// Wrapf 格式化包装错误
func Wrapf(code int, err error, format string, args ...interface{}) error {
    return gerror.WrapCodef(code, err, format, args...)
}
```

### 2. 错误码规范

```go
// 错误码定义
package code

const (
    // 成功
    OK = 0
    
    // 通用错误 (1-999)
    InternalError        = 1
    InvalidParameter     = 2
    NotFound            = 3
    NotAuthorized       = 4
    Conflict            = 5
    
    // 用户模块 (1000-1999)
    UserNotFound        = 1001
    UserExists          = 1002
    UserPasswordError   = 1003
    
    // 订单模块 (2000-2999)
    OrderNotFound       = 2001
    OrderStatusError    = 2002
    OrderPaymentError   = 2003
)

// 错误码描述
var messages = map[int]string{
    OK:                  "成功",
    InternalError:       "内部错误",
    InvalidParameter:    "参数错误",
    NotFound:           "资源不存在",
    NotAuthorized:      "未授权",
    Conflict:           "冲突",
    UserNotFound:       "用户不存在",
    UserExists:         "用户已存在",
    UserPasswordError:  "密码错误",
    OrderNotFound:      "订单不存在",
    OrderStatusError:   "订单状态错误",
    OrderPaymentError:  "支付失败",
}

func GetMessage(code int) string {
    if msg, ok := messages[code]; ok {
        return msg
    }
    return "未知错误"
}
```

### 3. 分层错误处理

```go
// 数据层
func GetUserByID(id int) (*User, error) {
    var user User
    err := db.Model("user").Where("id", id).Scan(&user)
    if err != nil {
        return nil, gerror.WrapCode(code.InternalError, err, "数据库查询失败")
    }
    if user.ID == 0 {
        return nil, gerror.NewCode(code.UserNotFound, "用户不存在")
    }
    return &user, nil
}

// 业务层
func Login(username, password string) (*User, error) {
    user, err := GetUserByID(123)
    if err != nil {
        // 错误向上传递，不需要再次包装
        return nil, err
    }
    
    if user.Password != password {
        return nil, gerror.NewCode(code.UserPasswordError, "密码错误")
    }
    
    return user, nil
}

// API层
func LoginHandler(r *ghttp.Request) {
    username := r.Get("username").String()
    password := r.Get("password").String()
    
    user, err := Login(username, password)
    if err != nil {
        r.Response.WriteJson(g.Map{
            "code":    gerror.Code(err),
            "message": err.Error(),
        })
        return
    }
    
    r.Response.WriteJson(g.Map{
        "code":    0,
        "message": "登录成功",
        "data":    user,
    })
}
```

### 4. 错误日志记录

```go
// 记录错误日志
func HandleError(ctx context.Context, err error) {
    if err == nil {
        return
    }
    
    // 记录完整堆栈到日志
    g.Log().Errorf(ctx, "%+v", err)
}

// 使用示例
func ProcessFile(filePath string) error {
    content, err := gfile.GetContents(filePath)
    if err != nil {
        err = gerror.Wrap(err, "读取文件失败")
        HandleError(context.Background(), err)
        return err
    }
    
    // 处理内容...
    return nil
}
```

### 5. panic处理

```go
// 安全执行函数
func SafeExecute(fn func()) (err error) {
    defer func() {
        if r := recover(); r != nil {
            // 将panic转换为错误
            err = gerror.Newf("panic: %v", r)
            g.Log().Error(err)
        }
    }()
    
    fn()
    return
}

// 使用示例
func Process() error {
    return SafeExecute(func() {
        // 可能panic的代码
        panic("意外错误")
    })
}
```

### 6. 错误断言

```go
// 错误类型断言
func HandleSpecificError(err error) {
    if gerror.Code(err) == code.UserNotFound {
        // 处理用户不存在的情况
        fmt.Println("用户不存在，请注册")
    } else if gerror.Code(err) == code.InternalError {
        // 处理内部错误
        fmt.Println("系统繁忙，请稍后重试")
    } else {
        // 处理其他错误
        fmt.Println(err.Error())
    }
}
```

## 总结

`gerror`组件提供了完整的错误处理能力：

1. **错误创建**：`New`、`Newf`、`NewCode`、`NewCodef`
2. **错误包装**：`Wrap`、`Wrapf`、`WrapCode`、`WrapCodef`
3. **堆栈跟踪**：自动捕获、`Stack`、`StackArray`
4. **错误码**：内置错误码、自定义错误码、`Code()`方法
5. **错误比较**：`Equal`、`Is`、`Cause`

遵循最佳实践，可以构建出清晰、可维护的错误处理体系。
