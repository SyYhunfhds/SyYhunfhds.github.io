---
title: Go gomock 库使用指南
date: 2026-05-28
footer: Trae编辑
---

# Go gomock 库使用指南

## 一、概述

gomock 是 Go 语言中最流行的 mocking 框架，用于在单元测试中模拟依赖接口，实现测试隔离。它由 Uber 维护，提供了类型安全的 mock 生成和灵活的行为定义能力。

### 核心优势

- **类型安全**：基于接口自动生成 mock 代码
- **灵活性**：支持复杂的调用断言和行为定义
- **集成性**：无缝集成 Go 标准库 `testing` 包
- **丰富 API**：支持调用次数、参数匹配、返回值定制等

## 二、安装

### 2.1 安装 mockgen 工具

```bash
go install go.uber.org/mock/mockgen@latest
```

### 2.2 安装 gomock 包

```bash
go get go.uber.org/mock/gomock
```

### 2.3 验证安装

```bash
mockgen -version
# 输出：mockgen version v0.6.0
```

## 三、基本概念

### 3.1 Mock 对象

Mock 对象是对接口的模拟实现，用于替换真实依赖。gomock 通过 `mockgen` 工具自动生成。

### 3.2 Controller

Controller 是 gomock 的核心组件，负责管理 mock 对象的生命周期和调用验证。

### 3.3 Call

Call 对象表示对 mock 方法的一次调用期望，包含参数匹配、返回值、调用次数等信息。

### 3.4 Matcher

Matcher 用于匹配方法调用的参数，支持精确匹配和模糊匹配。

## 四、mockgen 工具使用

### 4.1 三种运行模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **Source mode** | 从源码文件生成 | 生成当前包内接口的 mock |
| **Package mode** | 从包路径生成 | 生成外部包接口的 mock |
| **Archive mode** | 从编译后的归档文件生成 | 复杂场景 |

### 4.2 Source mode

```bash
# 从指定源文件生成 mock
mockgen -source=service.go -destination=mock_service.go -package=service
```

### 4.3 Package mode

```bash
# 从包路径生成指定接口的 mock
mockgen -package=mocks -destination=mocks/mock_repo.go myproject/repo UserRepository,Cache
```

### 4.4 使用 go:generate

在源文件中添加生成指令：

```go
// service.go
package service

//go:generate mockgen -source=service.go -destination=mock_service_test.go -package=service

type DataFetcher interface {
    Fetch(url string) (string, error)
    Close() error
}
```

运行生成：

```bash
go generate
```

### 4.5 常用标志

| 标志 | 说明 | 示例 |
|------|------|------|
| `-source` | 指定源文件 | `-source=foo.go` |
| `-destination` | 指定输出文件 | `-destination=mock_foo.go` |
| `-package` | 指定输出包名 | `-package=mocks` |
| `-imports` | 指定额外导入 | `-imports=fmt` |
| `-aux_files` | 辅助文件 | `-aux_files=bar.go` |

## 五、gomock API 详解

### 5.1 Controller 方法

```go
// 创建 Controller
ctrl := gomock.NewController(t)
defer ctrl.Finish() // 验证所有期望的调用

// 创建 mock 对象
mockFetcher := NewMockDataFetcher(ctrl)
```

### 5.2 Call 方法链

#### Return：设置返回值

```go
// 简单返回值
mockFetcher.EXPECT().Fetch("http://example.com").Return("data", nil)

// 多次调用返回不同值
mockFetcher.EXPECT().Fetch(gomock.Any()).Return("first", nil).Times(1)
mockFetcher.EXPECT().Fetch(gomock.Any()).Return("second", nil).Times(1)
```

#### Times：设置调用次数

```go
mockFetcher.EXPECT().Close().Times(1)          // 必须调用一次
mockFetcher.EXPECT().Fetch(gomock.Any()).MinTimes(2)  // 至少调用两次
mockFetcher.EXPECT().Fetch(gomock.Any()).MaxTimes(5)  // 最多调用五次
mockFetcher.EXPECT().Fetch(gomock.Any()).AnyTimes()   // 任意次数
```

#### Do：执行副作用

```go
mockFetcher.EXPECT().Fetch(gomock.Any()).Do(func(url string) {
    fmt.Printf("Fetch called with: %s\n", url)
}).Return("data", nil)
```

#### DoAndReturn：执行并返回

```go
mockFetcher.EXPECT().Fetch(gomock.Any()).DoAndReturn(func(url string) (string, error) {
    if url == "" {
        return "", errors.New("empty url")
    }
    return "response for " + url, nil
})
```

#### SetArg：修改参数

```go
mockFetcher.EXPECT().Process(gomock.Any()).SetArg(0, "modified")
```

#### After：设置调用顺序

```go
firstCall := mockFetcher.EXPECT().Fetch("url1").Return("data1", nil)
mockFetcher.EXPECT().Fetch("url2").Return("data2", nil).After(firstCall)
```

### 5.3 参数匹配器

```go
gomock.Any()            // 匹配任意值
gomock.Eq(value)        // 精确匹配
gomock.Not(value)       // 不匹配指定值
gomock.Nil()            // 匹配 nil
gomock.AnyOf(a, b, c)   // 匹配其中一个
gomock.AllOf(a, b)      // 同时匹配所有条件
gomock.NotNil()         // 非 nil
```

### 5.4 InOrder：顺序调用验证

```go
gomock.InOrder(
    mockFetcher.EXPECT().Fetch("url1").Return("data1", nil),
    mockFetcher.EXPECT().Fetch("url2").Return("data2", nil),
    mockFetcher.EXPECT().Close().Return(nil),
)
```

## 六、完整实战示例

### 6.1 定义接口

```go
// repository.go
package user

type User struct {
    ID   int
    Name string
    Age  int
}

type UserRepository interface {
    GetUserByID(id int) (*User, error)
    SaveUser(user *User) error
    DeleteUser(id int) error
    ListUsers() ([]*User, error)
}
```

### 6.2 生成 Mock

```bash
mockgen -source=repository.go -destination=mock_repository_test.go -package=user
```

### 6.3 使用 Mock 编写测试

```go
// user_service_test.go
package user

import (
    "errors"
    "testing"

    "go.uber.org/mock/gomock"
)

type UserService struct {
    repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}

func (s *UserService) GetUserName(id int) (string, error) {
    user, err := s.repo.GetUserByID(id)
    if err != nil {
        return "", err
    }
    return user.Name, nil
}

func TestGetUserName(t *testing.T) {
    // 创建 Controller
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    // 创建 mock 对象
    mockRepo := NewMockUserRepository(ctrl)

    // 设置期望
    mockRepo.EXPECT().GetUserByID(1).Return(&User{ID: 1, Name: "Alice"}, nil)

    // 创建被测服务
    service := NewUserService(mockRepo)

    // 执行测试
    name, err := service.GetUserName(1)
    if err != nil {
        t.Errorf("Unexpected error: %v", err)
    }
    if name != "Alice" {
        t.Errorf("Expected name 'Alice', got '%s'", name)
    }
}

func TestGetUserName_NotFound(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := NewMockUserRepository(ctrl)

    // 设置错误返回
    mockRepo.EXPECT().GetUserByID(999).Return(nil, errors.New("user not found"))

    service := NewUserService(mockRepo)

    _, err := service.GetUserName(999)
    if err == nil {
        t.Error("Expected error, got nil")
    }
}
```

### 6.4 复杂场景测试

```go
func TestUserService_BatchOperation(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := NewMockUserRepository(ctrl)

    // 设置多个期望
    gomock.InOrder(
        mockRepo.EXPECT().ListUsers().Return([]*User{
            {ID: 1, Name: "Alice"},
            {ID: 2, Name: "Bob"},
        }, nil),
        mockRepo.EXPECT().SaveUser(gomock.Any()).DoAndReturn(func(u *User) error {
            if u.Age < 0 {
                return errors.New("invalid age")
            }
            return nil
        }),
        mockRepo.EXPECT().DeleteUser(3).Return(nil),
    )

    service := NewUserService(mockRepo)
    
    // 执行操作...
}
```

## 七、高级技巧

### 7.1 捕获参数

```go
func TestCaptureArguments(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := NewMockUserRepository(ctrl)
    
    var capturedUser *User
    mockRepo.EXPECT().SaveUser(gomock.Any()).Do(func(u *User) {
        capturedUser = u
    }).Return(nil)

    service := NewUserService(mockRepo)
    
    // 执行保存操作
    service.SaveUser(&User{ID: 1, Name: "Charlie"})

    // 验证捕获的参数
    if capturedUser.Name != "Charlie" {
        t.Errorf("Expected name 'Charlie', got '%s'", capturedUser.Name)
    }
}
```

### 7.2 动态返回值

```go
func TestDynamicReturn(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockFetcher := NewMockDataFetcher(ctrl)
    
    callCount := 0
    mockFetcher.EXPECT().Fetch(gomock.Any()).DoAndReturn(func(url string) (string, error) {
        callCount++
        return fmt.Sprintf("response %d for %s", callCount, url), nil
    }).Times(3)

    // 每次调用返回不同的值
}
```

### 7.3 自定义匹配器

```go
type StringStartsWith struct {
    prefix string
}

func (m *StringStartsWith) Matches(x interface{}) bool {
    s, ok := x.(string)
    return ok && strings.HasPrefix(s, m.prefix)
}

func (m *StringStartsWith) String() string {
    return fmt.Sprintf("starts with %q", m.prefix)
}

// 使用
mockFetcher.EXPECT().Fetch(&StringStartsWith{prefix: "http://"}).Return("data", nil)
```

### 7.4 并发测试

```go
func TestConcurrentCalls(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := NewMockUserRepository(ctrl)
    
    // 允许任意次数调用
    mockRepo.EXPECT().GetUserByID(gomock.Any()).Return(&User{ID: 1, Name: "Concurrent"}, nil).AnyTimes()

    // 并发调用
    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            mockRepo.GetUserByID(1)
        }()
    }
    wg.Wait()
}
```

## 八、最佳实践

### 8.1 接口设计原则

- **依赖接口而非实现**：代码应依赖接口类型
- **接口粒度适中**：避免过于庞大的接口
- **单一职责**：每个接口只定义一组相关方法

### 8.2 Mock 使用原则

- **只 mock 外部依赖**：不需要 mock 被测代码本身
- **保持测试简洁**：每个测试只验证一个行为
- **清理资源**：使用 `defer ctrl.Finish()` 确保验证

### 8.3 生成策略

- **使用 go:generate**：将生成指令嵌入代码
- **隔离 mock 文件**：将 mock 放在单独的包或目录
- **定期更新**：接口变更后重新生成 mock

### 8.4 常见陷阱

```go
// 错误：忘记设置期望
func TestBadExample(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()
    
    mockRepo := NewMockUserRepository(ctrl)
    // 没有设置 GetUserByID 的期望
    
    service := NewUserService(mockRepo)
    service.GetUserName(1) // 会失败，因为没有设置期望
}

// 错误：期望调用次数不匹配
func TestBadExample2(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()
    
    mockRepo := NewMockUserRepository(ctrl)
    mockRepo.EXPECT().GetUserByID(1).Return(&User{}, nil).Times(1)
    
    service := NewUserService(mockRepo)
    service.GetUserName(1)
    service.GetUserName(1) // 第二次调用会失败
}
```

## 九、与其他测试工具配合

### 9.1 与 testify 配合

```go
import (
    "testing"
    
    "github.com/stretchr/testify/assert"
    "go.uber.org/mock/gomock"
)

func TestWithTestify(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := NewMockUserRepository(ctrl)
    mockRepo.EXPECT().GetUserByID(1).Return(&User{Name: "Alice"}, nil)

    service := NewUserService(mockRepo)
    name, err := service.GetUserName(1)
    
    assert.NoError(t, err)
    assert.Equal(t, "Alice", name)
}
```

### 9.2 与 gomega 配合

```go
import (
    "testing"
    
    "github.com/onsi/gomega"
    "go.uber.org/mock/gomock"
)

func TestWithGomega(t *testing.T) {
    gomega.RegisterFailHandler(func(message string, callerSkip ...int) {
        t.Helper()
        t.Fatal(message)
    })
    
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := NewMockUserRepository(ctrl)
    mockRepo.EXPECT().GetUserByID(1).Return(&User{Name: "Alice"}, nil)

    service := NewUserService(mockRepo)
    name, err := service.GetUserName(1)
    
    gomega.Expect(err).To(gomega.BeNil())
    gomega.Expect(name).To(gomega.Equal("Alice"))
}
```

## 十、参考资源

- [gomock 官方文档](https://pkg.go.dev/go.uber.org/mock/gomock)
- [mockgen 工具文档](https://pkg.go.dev/go.uber.org/mock)
- [Uber mock GitHub](https://github.com/uber/mock)
- [Go 测试最佳实践](https://go.dev/doc/testing)

---

*本文基于 gomock v0.6.0 版本编写*
