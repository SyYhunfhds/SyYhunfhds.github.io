---
title: Go 文件操作标准库 API 详解
date: 2026-04-05
footer: Trae编辑
---
[[toc]]
***

:::info 参考资料
- [Go os 包官方文档](https://pkg.go.dev/os)
- [Go io 包官方文档](https://pkg.go.dev/io)
- [Go io/ioutil 包官方文档](https://pkg.go.dev/io/ioutil)
- [Go 文件操作实践指南](https://ref.coddy.tech/go/go-file-operations)
- [Go 语言文件操作详解](https://blog.csdn.net/m0_73558214/article/details/147494051)
:::

## 一、核心包与类型

### 1.1 主要包

| 包 | 说明 | 主要功能 |
|------|------|----------|
| `os` | 操作系统接口 | 文件创建、打开、读写、删除等核心操作 |
| `io` | 基本 I/O 接口 | 定义了 Reader、Writer 等接口 |
| `io/ioutil` | I/O 工具函数 | 已弃用，功能已迁移到 os 和 io 包 |
| `bufio` | 缓冲 I/O | 提供缓冲读写功能 |
| `path/filepath` | 路径操作 | 处理文件路径 |

### 1.2 核心类型

#### 1.2.1 `os.File`

`os.File` 是文件操作的核心类型，实现了多个接口：

- `io.Reader` - 读取数据
- `io.Writer` - 写入数据
- `io.StringWriter` - 写入字符串
- `io.Seeker` - 定位文件指针
- `io.ReaderAt` - 从指定位置读取
- `io.Closer` - 关闭文件

#### 1.2.2 `os.FileInfo`

`os.FileInfo` 接口提供文件信息：

```go
type FileInfo interface {
    Name() string       // 文件名
    Size() int64        // 文件大小（字节）
    Mode() FileMode     // 文件权限
    ModTime() time.Time // 修改时间
    IsDir() bool        // 是否为目录
    Sys() interface{}   // 系统特定信息
}
```

#### 1.2.3 `os.DirEntry`

Go 1.16+ 新增，提供更高效的目录条目信息：

```go
type DirEntry interface {
    Name() string       // 文件名
    IsDir() bool        // 是否为目录
    Type() FileMode     // 文件类型
    Info() (FileInfo, error) // 获取完整信息
}
```

## 二、文件创建与打开

### 2.1 创建文件

```go
// 创建或截断文件
file, err := os.Create("example.txt")
if err != nil {
    log.Fatal(err)
}
defer file.Close()

// 自定义标志和权限
file, err := os.OpenFile("example.txt", os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)
if err != nil {
    log.Fatal(err)
}
defer file.Close()
```

### 2.2 打开文件

```go
// 只读方式打开
file, err := os.Open("example.txt")
if err != nil {
    log.Fatal(err)
}
defer file.Close()

// 读写方式打开
file, err := os.OpenFile("example.txt", os.O_RDWR, 0)
if err != nil {
    log.Fatal(err)
}
defer file.Close()
```

### 2.3 打开标志

| 标志 | 说明 |
|------|------|
| `os.O_RDONLY` | 只读模式 |
| `os.O_WRONLY` | 只写模式 |
| `os.O_RDWR` | 读写模式 |
| `os.O_CREATE` | 创建文件 |
| `os.O_TRUNC` | 截断文件 |
| `os.O_APPEND` | 追加模式 |
| `os.O_EXCL` | 与 O_CREATE 一起使用，文件已存在则失败 |
| `os.O_SYNC` | 同步写入 |
| `os.O_DIRECT` | 直接 I/O |

## 三、文件读写

### 3.1 写入文件

#### 3.1.1 基本写入

```go
// 写入字节切片
_, err := file.Write([]byte("Hello, Go!"))
if err != nil {
    log.Fatal(err)
}

// 写入字符串
_, err := file.WriteString("Hello, Go!")
if err != nil {
    log.Fatal(err)
}
```

#### 3.1.2 一次性写入

```go
// Go 1.16+
err := os.WriteFile("example.txt", []byte("Hello, Go!"), 0644)
if err != nil {
    log.Fatal(err)
}
```

### 3.2 读取文件

#### 3.2.1 基本读取

```go
// 读取指定长度
buf := make([]byte, 1024)
n, err := file.Read(buf)
if err != nil && err != io.EOF {
    log.Fatal(err)
}
fmt.Println(string(buf[:n]))
```

#### 3.2.2 一次性读取

```go
// Go 1.16+
data, err := os.ReadFile("example.txt")
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(data))
```

#### 3.2.3 缓冲读取

```go
reader := bufio.NewReader(file)

// 读取一行
line, err := reader.ReadString('\n')
if err != nil && err != io.EOF {
    log.Fatal(err)
}

// 读取指定分隔符
line, err := reader.ReadBytes('\n')
if err != nil && err != io.EOF {
    log.Fatal(err)
}
```

#### 3.2.4 扫描读取

```go
scanner := bufio.NewScanner(file)
for scanner.Scan() {
    line := scanner.Text()
    fmt.Println(line)
}

if err := scanner.Err(); err != nil {
    log.Fatal(err)
}
```

## 四、文件信息与操作

### 4.1 获取文件信息

```go
// 获取文件信息
info, err := file.Stat()
if err != nil {
    log.Fatal(err)
}

fmt.Println("Name:", info.Name())
fmt.Println("Size:", info.Size())
fmt.Println("Mode:", info.Mode())
fmt.Println("ModTime:", info.ModTime())
fmt.Println("IsDir:", info.IsDir())

// 通过路径获取文件信息
info, err := os.Stat("example.txt")
if err != nil {
    log.Fatal(err)
}
```

### 4.2 文件操作

```go
// 重命名文件
err := os.Rename("old.txt", "new.txt")
if err != nil {
    log.Fatal(err)
}

// 删除文件
err := os.Remove("example.txt")
if err != nil {
    log.Fatal(err)
}

// 强制删除（忽略错误）
err := os.RemoveAll("example.txt")
if err != nil {
    log.Fatal(err)
}

// 复制文件
data, err := os.ReadFile("source.txt")
if err != nil {
    log.Fatal(err)
}
err = os.WriteFile("dest.txt", data, 0644)
if err != nil {
    log.Fatal(err)
}
```

## 五、目录操作

### 5.1 创建目录

```go
// 创建单个目录
err := os.Mkdir("mydir", 0755)
if err != nil {
    log.Fatal(err)
}

// 创建多级目录
err := os.MkdirAll("mydir/subdir", 0755)
if err != nil {
    log.Fatal(err)
}
```

### 5.2 读取目录

#### 5.2.1 传统方式

```go
// Go 1.16- 使用 ioutil.ReadDir
files, err := ioutil.ReadDir(".")
if err != nil {
    log.Fatal(err)
}

for _, file := range files {
    fmt.Println(file.Name(), file.IsDir())
}
```

#### 5.2.2 现代方式

```go
// Go 1.16+ 使用 os.ReadDir
entries, err := os.ReadDir(".")
if err != nil {
    log.Fatal(err)
}

for _, entry := range entries {
    fmt.Println(entry.Name(), entry.IsDir())
    
    // 获取完整信息
    info, err := entry.Info()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Size:", info.Size())
}
```

### 5.3 删除目录

```go
// 删除空目录
err := os.Remove("mydir")
if err != nil {
    log.Fatal(err)
}

// 递归删除目录及其内容
err := os.RemoveAll("mydir")
if err != nil {
    log.Fatal(err)
}
```

## 六、临时文件与目录

### 6.1 临时文件

```go
// Go 1.17+ 使用 os.CreateTemp
file, err := os.CreateTemp("", "example*")
if err != nil {
    log.Fatal(err)
}
defer os.Remove(file.Name())
defer file.Close()

// 写入内容
_, err = file.WriteString("Temporary content")
if err != nil {
    log.Fatal(err)
}
```

### 6.2 临时目录

```go
// Go 1.17+ 使用 os.MkdirTemp
dir, err := os.MkdirTemp("", "example*")
if err != nil {
    log.Fatal(err)
}
defer os.RemoveAll(dir)

// 在临时目录中创建文件
tmpFile := filepath.Join(dir, "temp.txt")
err = os.WriteFile(tmpFile, []byte("Temporary content"), 0644)
if err != nil {
    log.Fatal(err)
}
```

## 七、文件权限

### 7.1 权限模式

Go 使用 Unix 风格的权限位：

| 权限 | 数值 | 说明 |
|------|------|------|
| `0o400` | 256 | 所有者可读 |
| `0o200` | 128 | 所有者可写 |
| `0o100` | 64 | 所有者可执行 |
| `0o040` | 32 | 组可读 |
| `0o020` | 16 | 组可写 |
| `0o010` | 8 | 组可执行 |
| `0o004` | 4 | 其他可读 |
| `0o002` | 2 | 其他可写 |
| `0o001` | 1 | 其他可执行 |

### 7.2 常用权限

| 权限 | 说明 | 适用场景 |
|------|------|----------|
| `0o644` | 所有者读写，其他只读 | 普通文件 |
| `0o755` | 所有者读写执行，其他读执行 | 可执行文件、目录 |
| `0o600` | 仅所有者读写 | 敏感文件 |
| `0o700` | 仅所有者读写执行 | 敏感目录 |

### 7.3 设置权限

```go
// 创建文件时设置权限
file, err := os.Create("secure.txt")
if err != nil {
    log.Fatal(err)
}
file.Close()

// 修改现有文件权限
err = os.Chmod("secure.txt", 0600)
if err != nil {
    log.Fatal(err)
}

// 修改目录权限
err = os.Chmod("mydir", 0755)
if err != nil {
    log.Fatal(err)
}
```

## 八、路径操作

### 8.1 路径拼接

```go
// 安全拼接路径
path := filepath.Join("dir", "subdir", "file.txt")

// 绝对路径
absPath, err := filepath.Abs(path)
if err != nil {
    log.Fatal(err)
}

// 相对路径
relPath, err := filepath.Rel("/a/b", "/a/b/c/d")
if err != nil {
    log.Fatal(err)
}
```

### 8.2 路径分解

```go
// 获取目录
 dir := filepath.Dir("/a/b/c.txt") // /a/b

// 获取文件名
 name := filepath.Base("/a/b/c.txt") // c.txt

// 获取扩展名
 ext := filepath.Ext("/a/b/c.txt") // .txt

// 去除扩展名
 base := strings.TrimSuffix("c.txt", filepath.Ext("c.txt")) // c
```

### 8.3 路径匹配

```go
// 匹配模式
matched, err := filepath.Match("*.txt", "file.txt")
if err != nil {
    log.Fatal(err)
}

// 全局匹配
files, err := filepath.Glob("*.txt")
if err != nil {
    log.Fatal(err)
}
```

## 九、错误处理

### 9.1 常见错误

| 错误 | 说明 |
|------|------|
| `os.ErrNotExist` | 文件或目录不存在 |
| `os.ErrExist` | 文件或目录已存在 |
| `os.ErrPermission` | 权限不足 |
| `io.EOF` | 文件结束 |

### 9.2 错误处理示例

```go
// 检查文件是否存在
if _, err := os.Stat("example.txt"); os.IsNotExist(err) {
    fmt.Println("File does not exist")
} else if err != nil {
    log.Fatal(err)
}

// 检查权限错误
if err := os.Open("secure.txt"); os.IsPermission(err) {
    fmt.Println("Permission denied")
} else if err != nil {
    log.Fatal(err)
}
```

## 十、最佳实践

### 10.1 通用实践

1. **始终检查错误**：文件操作可能因各种原因失败，必须检查错误
2. **使用 defer 关闭文件**：确保文件资源正确释放
3. **处理大文件**：对于大文件，使用缓冲读写或流式处理
4. **权限设置**：根据文件用途设置适当的权限
5. **路径处理**：使用 filepath 包进行路径操作，确保跨平台兼容性
6. **错误处理**：使用 os.IsNotExist 等函数进行错误类型判断
7. **临时文件**：使用 os.CreateTemp 和 os.MkdirTemp 创建临时文件和目录
8. **资源清理**：使用 defer os.Remove 清理临时文件

### 10.2 性能优化

1. **缓冲 I/O**：对于频繁的读写操作，使用 bufio 提高性能
2. **批量读写**：减少系统调用次数
3. **内存映射**：对于大文件，考虑使用 mmap
4. **并发处理**：对于多个文件操作，考虑使用 goroutine 并发处理

## 十一、示例代码

### 11.1 完整文件操作示例

```go
package main

import (
    "bufio"
    "fmt"
    "io"
    "os"
    "path/filepath"
)

func main() {
    // 1. 创建文件
    file, err := os.Create("example.txt")
    if err != nil {
        fmt.Println("Error creating file:", err)
        return
    }
    defer file.Close()

    // 2. 写入内容
    content := "Hello, Go file operations!\nThis is a test."
    _, err = file.WriteString(content)
    if err != nil {
        fmt.Println("Error writing to file:", err)
        return
    }

    // 3. 关闭并重新打开文件
    file.Close()
    file, err = os.Open("example.txt")
    if err != nil {
        fmt.Println("Error opening file:", err)
        return
    }
    defer file.Close()

    // 4. 读取文件信息
    info, err := file.Stat()
    if err != nil {
        fmt.Println("Error getting file info:", err)
        return
    }
    fmt.Printf("File name: %s\n", info.Name())
    fmt.Printf("File size: %d bytes\n", info.Size())
    fmt.Printf("File mode: %v\n", info.Mode())

    // 5. 读取文件内容
    fmt.Println("\nFile content:")
    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        fmt.Println(scanner.Text())
    }
    if err := scanner.Err(); err != nil {
        fmt.Println("Error reading file:", err)
        return
    }

    // 6. 复制文件
    dest := "example_copy.txt"
    err = copyFile("example.txt", dest)
    if err != nil {
        fmt.Println("Error copying file:", err)
        return
    }
    fmt.Printf("\nFile copied to %s\n", dest)

    // 7. 重命名文件
    newName := "renamed_example.txt"
    err = os.Rename("example.txt", newName)
    if err != nil {
        fmt.Println("Error renaming file:", err)
        return
    }
    fmt.Printf("File renamed to %s\n", newName)

    // 8. 清理
    err = os.Remove(newName)
    if err != nil {
        fmt.Println("Error removing file:", err)
        return
    }
    err = os.Remove(dest)
    if err != nil {
        fmt.Println("Error removing file:", err)
        return
    }
    fmt.Println("Files cleaned up")
}

func copyFile(src, dst string) error {
    source, err := os.Open(src)
    if err != nil {
        return err
    }
    defer source.Close()

    destination, err := os.Create(dst)
    if err != nil {
        return err
    }
    defer destination.Close()

    _, err = io.Copy(destination, source)
    return err
}
```

### 11.2 目录操作示例

```go
package main

import (
    "fmt"
    "os"
    "path/filepath"
)

func main() {
    // 1. 创建目录
    dirName := "testdir"
    err := os.MkdirAll(filepath.Join(dirName, "subdir"), 0755)
    if err != nil {
        fmt.Println("Error creating directory:", err)
        return
    }
    fmt.Printf("Directory %s created\n", dirName)

    // 2. 在目录中创建文件
    fileName := filepath.Join(dirName, "subdir", "test.txt")
    err = os.WriteFile(fileName, []byte("Test content"), 0644)
    if err != nil {
        fmt.Println("Error creating file:", err)
        return
    }
    fmt.Printf("File %s created\n", fileName)

    // 3. 读取目录内容
    fmt.Println("\nDirectory contents:")
    entries, err := os.ReadDir(dirName)
    if err != nil {
        fmt.Println("Error reading directory:", err)
        return
    }

    for _, entry := range entries {
        fmt.Printf("%s (dir: %t)\n", entry.Name(), entry.IsDir())
        
        if entry.IsDir() {
            subEntries, err := os.ReadDir(filepath.Join(dirName, entry.Name()))
            if err != nil {
                fmt.Println("Error reading subdirectory:", err)
                continue
            }
            for _, subEntry := range subEntries {
                fmt.Printf("  └─ %s (dir: %t)\n", subEntry.Name(), subEntry.IsDir())
            }
        }
    }

    // 4. 清理
    err = os.RemoveAll(dirName)
    if err != nil {
        fmt.Println("Error removing directory:", err)
        return
    }
    fmt.Printf("Directory %s removed\n", dirName)
}
```

## 十二、总结

Go 语言提供了丰富的文件操作 API，主要通过 `os`、`io` 等包实现。随着 Go 版本的更新，一些功能从 `io/ioutil` 包迁移到了 `os` 和 `io` 包，例如 `ReadFile`、`WriteFile`、`ReadDir` 等函数。

在使用文件操作 API 时，需要注意以下几点：

1. **错误处理**：始终检查并处理文件操作可能产生的错误
2. **资源管理**：使用 `defer` 语句确保文件正确关闭
3. **权限设置**：根据文件用途设置适当的权限
4. **路径处理**：使用 `filepath` 包进行跨平台的路径操作
5. **性能考虑**：对于大文件，使用缓冲 I/O 或流式处理
6. **安全性**：注意文件权限和路径注入等安全问题

通过掌握这些 API 和最佳实践，你可以在 Go 中高效、安全地进行文件操作，满足各种应用场景的需求。

:::tip 最终建议

1. **使用最新 API**：优先使用 Go 1.16+ 引入的 `os.ReadFile`、`os.WriteFile`、`os.ReadDir` 等函数
2. **统一错误处理**：建立统一的错误处理模式，提高代码可读性
3. **封装常用操作**：将常用的文件操作封装为函数，提高代码复用性
4. **测试文件操作**：编写单元测试确保文件操作的正确性
5. **文档化**：为文件操作相关代码添加注释，说明设计意图和使用方法

:::

***

# 页面底部