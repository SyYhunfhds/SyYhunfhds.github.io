---
title: Go regexp 正则表达式标准库
date: 2026-03-16
footer: Trae编辑
---

# Go regexp 正则表达式标准库

Go 的 `regexp` 包提供了正则表达式搜索功能，支持 RE2 语法。本文详细介绍 regexp 包的 API、用法、常见陷阱和最佳实践。

## 目录

- [基础概念](#基础概念)
- [核心 API](#核心-api)
- [常用方法](#常用方法)
- [Bad Practice](#bad-practice)
- [最佳实践](#最佳实践)
- [性能优化](#性能优化)

## 基础概念

### 编译正则表达式

::: tip 重要提示
正则表达式需要先编译才能使用，编译过程会验证语法并优化匹配算法。
:::

```go
package main

import (
    "fmt"
    "regexp"
)

func main() {
    // 编译正则表达式
    re := regexp.MustCompile(`\d+`)
    
    // 使用 MustCompile 会 panic 如果正则表达式无效
    // 使用 Compile 会返回 error
    re2, err := regexp.Compile(`\d+`)
    if err != nil {
        panic(err)
    }
    
    fmt.Println(re, re2)
}
```

### RE2 语法特点

::: info RE2 vs PCRE
Go 使用 RE2 引擎，与传统的 PCRE 相比：
- 不支持反向引用（backreferences）
- 不支持环视（lookaround）
- 保证线性时间复杂度
- 更安全，不会出现指数级回溯
:::

## 核心 API

### 1. 编译函数

#### `regexp.MustCompile(pattern string) *Regexp`

```go
// 编译正则表达式，失败时 panic
re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
```

#### `regexp.Compile(pattern string) (*Regexp, error)`

```go
// 编译正则表达式，失败返回 error
re, err := regexp.Compile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
if err != nil {
    fmt.Printf("正则表达式编译失败: %v\n", err)
    return
}
```

#### `regexp.MustCompilePOSIX(pattern string) *Regexp`

```go
// 使用 POSIX 语法编译（更严格）
re := regexp.MustCompilePOSIX(`[[:digit:]]+`)
```

### 2. 匹配方法

#### `MatchString(s string) bool`

```go
re := regexp.MustCompile(`\d+`)

// 检查字符串是否匹配
fmt.Println(re.MatchString("abc123")) // true
fmt.Println(re.MatchString("abc"))    // false
```

#### `Match(b []byte) bool`

```go
re := regexp.MustCompile(`\d+`)

// 检查字节切片是否匹配
fmt.Println(re.Match([]byte("abc123"))) // true
```

#### `MatchReader(r io.RuneReader) bool`

```go
re := regexp.MustCompile(`\d+`)

// 从 Reader 读取并匹配
reader := strings.NewReader("abc123")
fmt.Println(re.MatchReader(reader)) // true
```

### 3. 查找方法

#### `FindString(s string) string`

```go
re := regexp.MustCompile(`\d+`)

// 查找第一个匹配
fmt.Println(re.FindString("abc123def456")) // "123"
fmt.Println(re.FindString("abcdef"))        // ""
```

#### `FindAllString(s string, n int) []string`

```go
re := regexp.MustCompile(`\d+`)

// 查找所有匹配，n 为 -1 表示查找所有
fmt.Println(re.FindAllString("abc123def456", -1)) // ["123", "456"]
fmt.Println(re.FindAllString("abc123def456", 1))  // ["123"]
```

#### `FindStringIndex(s string) (loc []int)`

```go
re := regexp.MustCompile(`\d+`)

// 返回匹配的起始和结束位置
fmt.Println(re.FindStringIndex("abc123def")) // [3, 6]
```

#### `FindAllStringSubmatch(s string, n int) [][]string`

```go
re := regexp.MustCompile(`(\d+)-(\d+)`)

// 返回所有子匹配
matches := re.FindAllStringSubmatch("123-456 789-012", -1)
for _, match := range matches {
    fmt.Printf("完整匹配: %s, 组1: %s, 组2: %s\n", match[0], match[1], match[2])
}
// 输出:
// 完整匹配: 123-456, 组1: 123, 组2: 456
// 完整匹配: 789-012, 组1: 789, 组2: 012
```

### 4. 替换方法

#### `ReplaceAllString(src, repl string) string`

```go
re := regexp.MustCompile(`\d+`)

// 替换所有匹配
result := re.ReplaceAllString("abc123def456", "X")
fmt.Println(result) // "abcXdefX"
```

#### `ReplaceAllStringFunc(src string, repl func(string) string) string`

```go
re := regexp.MustCompile(`\d+`)

// 使用函数替换
result := re.ReplaceAllStringFunc("abc123def456", func(s string) string {
    num, _ := strconv.Atoi(s)
    return fmt.Sprintf("%d", num*2)
})
fmt.Println(result) // "abc246def912"
```

#### `ReplaceAllLiteralString(src, repl string) string`

```go
re := regexp.MustCompile(`\$1`)

// 字面量替换，不解释 $1 等特殊字符
result := re.ReplaceAllLiteralString("price: $1", "100")
fmt.Println(result) // "price: 100"
```

### 5. 分割方法

#### `Split(s string, n int) []string`

```go
re := regexp.MustCompile(`\s+`)

// 按正则分割字符串
parts := re.Split("a  b   c", -1)
fmt.Println(parts) // ["a", "b", "c"]
```

### 6. 其他方法

#### `NumSubexp() int`

```go
re := regexp.MustCompile(`(\d+)-(\d+)`)

// 返回捕获组的数量
fmt.Println(re.NumSubexp()) // 2
```

#### `SubexpNames() []string`

```go
re := regexp.MustCompile(`(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})`)

// 返回捕获组的名称
fmt.Println(re.SubexpNames()) // ["", "year", "month", "day"]
```

#### `FindSubmatch(s string) [][]byte`

```go
re := regexp.MustCompile(`(\d+)-(\d+)`)

// 返回子匹配（字节切片）
matches := re.FindSubmatch("123-456")
fmt.Println(matches[0]) // [49 50 51 45 52 53 54] (123-456)
fmt.Println(matches[1]) // [49 50 51] (123)
fmt.Println(matches[2]) // [52 53 54] (456)
```

## 常用方法

### 验证邮箱地址

```go
func isValidEmail(email string) bool {
    re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
    return re.MatchString(email)
}

func main() {
    fmt.Println(isValidEmail("test@example.com"))  // true
    fmt.Println(isValidEmail("invalid-email"))     // false
}
```

### 提取 URL 参数

```go
func extractURLParams(url string) map[string]string {
    re := regexp.MustCompile(`(\w+)=([^&]+)`)
    params := make(map[string]string)
    
    matches := re.FindAllStringSubmatch(url, -1)
    for _, match := range matches {
        params[match[1]] = match[2]
    }
    
    return params
}

func main() {
    url := "https://example.com?name=John&age=30&city=NYC"
    params := extractURLParams(url)
    fmt.Println(params) // map[age:30 city:NYC name:John]
}
```

### 提取 HTML 标签内容

```go
func extractHTMLContent(html string) []string {
    re := regexp.MustCompile(`<p>(.*?)</p>`)
    matches := re.FindAllStringSubmatch(html, -1)
    
    contents := make([]string, 0, len(matches))
    for _, match := range matches {
        contents = append(contents, match[1])
    }
    
    return contents
}

func main() {
    html := `<p>Hello</p><p>World</p>`
    contents := extractHTMLContent(html)
    fmt.Println(contents) // ["Hello", "World"]
}
```

### 清理字符串

```go
func cleanString(s string) string {
    // 移除多余的空格
    re1 := regexp.MustCompile(`\s+`)
    s = re1.ReplaceAllString(s, " ")
    
    // 移除首尾空格
    s = strings.TrimSpace(s)
    
    return s
}

func main() {
    fmt.Println(cleanString("  Hello    World  ")) // "Hello World"
}
```

## Bad Practice

### 1. 在循环中重复编译正则表达式

::: danger 性能陷阱
在循环中重复编译正则表达式会导致严重的性能问题。
:::

```go
// ❌ Bad Practice
func processStrings(strings []string) []string {
    results := make([]string, 0, len(strings))
    for _, s := range strings {
        re := regexp.MustCompile(`\d+`) // 每次循环都编译
        if re.MatchString(s) {
            results = append(results, s)
        }
    }
    return results
}

// ✅ Good Practice
func processStrings(strings []string) []string {
    re := regexp.MustCompile(`\d+`) // 只编译一次
    results := make([]string, 0, len(strings))
    for _, s := range strings {
        if re.MatchString(s) {
            results = append(results, s)
        }
    }
    return results
}
```

### 2. 使用过于复杂的正则表达式

```go
// ❌ Bad Practice - 过于复杂，难以维护
re := regexp.MustCompile(`^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$`)

// ✅ Good Practice - 分步骤验证
func isValidDate(date string) bool {
    // 先检查基本格式
    if !regexp.MustCompile(`^\d{4}-\d{2}-\d{2}$`).MatchString(date) {
        return false
    }
    
    // 使用 time.Parse 进行更精确的验证
    _, err := time.Parse("2006-01-02", date)
    return err == nil
}
```

### 3. 忽略错误处理

```go
// ❌ Bad Practice
func extractNumbers(s string) []string {
    re := regexp.MustCompile(`\d+`) // 如果正则无效会 panic
    return re.FindAllString(s, -1)
}

// ✅ Good Practice
func extractNumbers(s string) ([]string, error) {
    re, err := regexp.Compile(`\d+`)
    if err != nil {
        return nil, fmt.Errorf("正则表达式编译失败: %w", err)
    }
    return re.FindAllString(s, -1), nil
}
```

### 4. 使用贪婪匹配导致性能问题

```go
// ❌ Bad Practice - 贪婪匹配可能导致性能问题
re := regexp.MustCompile(`<.*>`)
html := `<div><p>Hello</p></div>`
matches := re.FindAllString(html, -1)
// 可能返回 ["<div><p>Hello</p></div>"] 而不是 ["<div>", "<p>", "</p>", "</div>"]

// ✅ Good Practice - 使用非贪婪匹配
re := regexp.MustCompile(`<.*?>`)
matches := re.FindAllString(html, -1)
// 返回 ["<div>", "<p>", "</p>", "</div>"]
```

### 5. 过度使用正则表达式

```go
// ❌ Bad Practice - 简单任务不需要正则
func isNumeric(s string) bool {
    re := regexp.MustCompile(`^\d+$`)
    return re.MatchString(s)
}

// ✅ Good Practice - 使用标准库函数
func isNumeric(s string) bool {
    for _, c := range s {
        if c < '0' || c > '9' {
            return false
        }
    }
    return len(s) > 0
}
```

## 最佳实践

### 1. 使用全局变量缓存编译后的正则表达式

```go
var (
    emailRegex    = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
    phoneRegex    = regexp.MustCompile(`^\+?[\d\s-]{10,}$`)
    urlRegex      = regexp.MustCompile(`^https?://[^\s/$.?#].[^\s]*$`)
)

func validateEmail(email string) bool {
    return emailRegex.MatchString(email)
}

func validatePhone(phone string) bool {
    return phoneRegex.MatchString(phone)
}

func validateURL(url string) bool {
    return urlRegex.MatchString(url)
}
```

### 2. 使用命名捕获组提高可读性

```go
// ✅ Good Practice
func parseDate(date string) (year, month, day string, ok bool) {
    re := regexp.MustCompile(`(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})`)
    match := re.FindStringSubmatch(date)
    
    if match == nil {
        return "", "", "", false
    }
    
    result := make(map[string]string)
    for i, name := range re.SubexpNames() {
        if i != 0 && name != "" {
            result[name] = match[i]
        }
    }
    
    return result["year"], result["month"], result["day"], true
}

func main() {
    year, month, day, ok := parseDate("2024-03-16")
    if ok {
        fmt.Printf("Year: %s, Month: %s, Day: %s\n", year, month, day)
    }
}
```

### 3. 使用原始字符串字面量避免转义

```go
// ❌ Bad Practice - 需要双重转义
re := regexp.MustCompile("\\d+")

// ✅ Good Practice - 使用原始字符串
re := regexp.MustCompile(`\d+`)
```

### 4. 预编译正则表达式并复用

```go
type Validator struct {
    emailRegex *regexp.Regexp
    phoneRegex *regexp.Regexp
}

func NewValidator() *Validator {
    return &Validator{
        emailRegex: regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`),
        phoneRegex: regexp.MustCompile(`^\+?[\d\s-]{10,}$`),
    }
}

func (v *Validator) ValidateEmail(email string) bool {
    return v.emailRegex.MatchString(email)
}

func (v *Validator) ValidatePhone(phone string) bool {
    return v.phoneRegex.MatchString(phone)
}
```

### 5. 使用边界锚点提高匹配准确性

```go
// ❌ Bad Practice - 可能匹配到部分内容
re := regexp.MustCompile(`test`)
fmt.Println(re.MatchString("testing")) // true

// ✅ Good Practice - 使用边界锚点
re := regexp.MustCompile(`^test$`)
fmt.Println(re.MatchString("testing")) // false
fmt.Println(re.MatchString("test"))    // true
```

### 6. 合理使用字符类

```go
// ❌ Bad Practice - 过于冗长
re := regexp.MustCompile(`[0-9a-zA-Z]`)

// ✅ Good Practice - 使用预定义字符类
re := regexp.MustCompile(`[[:alnum:]]`)
// 或者
re := regexp.MustCompile(`\w`)
```

### 7. 使用非捕获组提高性能

```go
// ❌ Bad Practice - 使用捕获组
re := regexp.MustCompile(`(?:abc|def)+(\d+)`)

// ✅ Good Practice - 使用非捕获组（不需要捕获时）
re := regexp.MustCompile(`(?:abc|def)+(\d+)`)
```

## 性能优化

### 1. 避免回溯

```go
// ❌ Bad Practice - 可能导致回溯
re := regexp.MustCompile(`a.*b`)
s := strings.Repeat("a", 10000) + "b"
re.MatchString(s) // 可能很慢

// ✅ Good Practice - 使用更精确的模式
re := regexp.MustCompile(`a[^b]*b`)
re.MatchString(s) // 更快
```

### 2. 使用原子组避免回溯

```go
// ✅ Good Practice - 使用原子组（如果支持）
re := regexp.MustCompile(`(?>a+)b`)
```

### 3. 限制匹配次数

```go
// ✅ Good Practice - 限制匹配次数
re := regexp.MustCompile(`\d{1,3}`) // 匹配 1-3 位数字
re := regexp.MustCompile(`\d{3}`)   // 匹配恰好 3 位数字
```

### 4. 使用 FindString 而不是 FindAllString

```go
// ✅ Good Practice - 只需要第一个匹配时使用 FindString
re := regexp.MustCompile(`\d+`)
match := re.FindString(s) // 比 FindAllString(s, 1) 更快
```

### 5. 预分配切片

```go
// ✅ Good Practice - 预分配切片
func extractAllMatches(s string) []string {
    re := regexp.MustCompile(`\d+`)
    matches := re.FindAllString(s, -1)
    
    result := make([]string, 0, len(matches))
    result = append(result, matches...)
    
    return result
}
```

## 常见用例

### 1. 密码强度验证

```go
func validatePassword(password string) bool {
    if len(password) < 8 {
        return false
    }
    
    hasUpper := regexp.MustCompile(`[A-Z]`).MatchString(password)
    hasLower := regexp.MustCompile(`[a-z]`).MatchString(password)
    hasDigit := regexp.MustCompile(`\d`).MatchString(password)
    hasSpecial := regexp.MustCompile(`[!@#$%^&*(),.?":{}|<>]`).MatchString(password)
    
    return hasUpper && hasLower && hasDigit && hasSpecial
}
```

### 2. IP 地址验证

```go
func isValidIP(ip string) bool {
    ipv4Regex := regexp.MustCompile(`^(\d{1,3}\.){3}\d{1,3}$`)
    ipv6Regex := regexp.MustCompile(`^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$`)
    
    if ipv4Regex.MatchString(ip) {
        parts := strings.Split(ip, ".")
        for _, part := range parts {
            num, _ := strconv.Atoi(part)
            if num < 0 || num > 255 {
                return false
            }
        }
        return true
    }
    
    return ipv6Regex.MatchString(ip)
}
```

### 3. 提取 Markdown 链接

```go
func extractMarkdownLinks(text string) []struct {
    Text string
    URL  string
} {
    re := regexp.MustCompile(`\[([^\]]+)\]\(([^\)]+)\)`)
    matches := re.FindAllStringSubmatch(text, -1)
    
    links := make([]struct {
        Text string
        URL  string
    }, 0, len(matches))
    
    for _, match := range matches {
        links = append(links, struct {
            Text string
            URL  string
        }{
            Text: match[1],
            URL:  match[2],
        })
    }
    
    return links
}

func main() {
    text := "Check out [Google](https://google.com) and [GitHub](https://github.com)"
    links := extractMarkdownLinks(text)
    for _, link := range links {
        fmt.Printf("Text: %s, URL: %s\n", link.Text, link.URL)
    }
}
```

### 4. 清理 HTML 标签

```go
func stripHTMLTags(html string) string {
    re := regexp.MustCompile(`<[^>]*>`)
    return re.ReplaceAllString(html, "")
}

func main() {
    html := `<p>Hello <b>World</b></p>`
    fmt.Println(stripHTMLTags(html)) // "Hello World"
}
```

## 总结

::: tip 关键要点
1. **预编译正则表达式**：避免在循环中重复编译
2. **使用原始字符串**：使用反引号避免转义
3. **合理使用边界锚点**：提高匹配准确性
4. **避免过度复杂**：简单任务使用标准库函数
5. **错误处理**：使用 Compile 而不是 MustCompile 处理可能的错误
6. **性能优化**：使用非贪婪匹配、限制匹配次数、预分配切片
:::

Go 的 `regexp` 包提供了强大而安全的正则表达式功能。通过遵循最佳实践，可以编写出高效、可维护的正则表达式代码。
