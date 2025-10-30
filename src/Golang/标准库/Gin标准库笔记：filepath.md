---
title: filepath笔记
date: 2025-10-30
---

```go
// 推荐：使用 filepath.Join 拼接路径
path := filepath.Join("dir", "subdir", "file.txt")

// 清理路径中的 . 和 ..
cleanPath := filepath.Clean("./dir/../subdir/./file.txt")

// 获取路径分隔符
sep := string(filepath.Separator)
// 使用 filepath.Separator 而不是硬编码 "/"
path := filepath.Join("root", "sub", "file.txt")

// 获取目录部分
dir := filepath.Dir("/home/user/file.txt")  // "/home/user"
// 获取文件名
filename := filepath.Base("/home/user/file.txt")  // "file.txt"
// 获取文件扩展名
ext := filepath.Ext("/home/user/file.txt")  // ".txt"
// 分割路径
dir, file := filepath.Split("/home/user/file.txt")

// 使用 Glob 进行文件匹配
matches, _ := filepath.Glob("*.go")
// 使用 Match 进行模式匹配
matched, _ := filepath.Match("*.txt", "file.txt")

// 转换为绝对路径
absPath, _ := filepath.Abs("relative/path")
```