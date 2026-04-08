---
title: Go Hash 库 API 详解
date: 2026-04-06
footer: Trae编辑
---
[[toc]]
***

:::info 参考资料
- [Go crypto 包官方文档](https://pkg.go.dev/crypto)
- [Go hash 包官方文档](https://pkg.go.dev/hash)
- [Go 语言 hash 库完全教程](https://blog.csdn.net/walkskyer/article/details/136927648)
- [Go 源码：crypto/sha256](https://go.dev/src/crypto/sha256/sha256.go)
- [Go 源码：crypto/md5](https://github.com/golang/go/blob/master/src/crypto/md5/md5.go)
:::

## 一、核心接口与包结构

### 1.1 hash 包

`hash` 包定义了哈希函数的基本接口：

```go
package hash

type Hash interface {
    io.Writer
    Sum(b []byte) []byte
    Reset()
    Size() int
    BlockSize() int
}

type Hash32 interface {
    Hash
    Sum32() uint32
}

type Hash64 interface {
    Hash
    Sum64() uint64
}
```

### 1.2 crypto 包下的哈希实现

| 包 | 算法 | 说明 |
|------|------|------|
| `crypto/md5` | MD5 | 128位哈希，已被认为不安全 |
| `crypto/sha1` | SHA-1 | 160位哈希，已被认为不安全 |
| `crypto/sha256` | SHA-224, SHA-256 | 224/256位哈希，安全 |
| `crypto/sha512` | SHA-384, SHA-512, SHA-512/224, SHA-512/256 | 384/512位哈希，安全 |
| `crypto/sha3` | SHA-3 | 多种长度的哈希，安全 |
| `crypto/hmac` | HMAC | 基于哈希的消息认证码 |
| `crypto/maphash` | MapHash | 用于哈希表的快速哈希 |
| `crypto/blake2b` | BLAKE2b | 高性能哈希算法 |
| `crypto/blake2s` | BLAKE2s | 适用于8位和16位平台的哈希 |

## 二、常用哈希算法 API

### 2.1 MD5

```go
package md5

import "crypto/md5"

// 创建新的 MD5 哈希实例
func New() hash.Hash

// 计算数据的 MD5 哈希值
func Sum(data []byte) [Size]byte

// 常量
const Size = 16
const BlockSize = 64
```

**使用示例**：

```go
import (
    "crypto/md5"
    "fmt"
)

func main() {
    data := []byte("Hello, Go!")
    
    // 方法一：使用 New()
    h := md5.New()
    h.Write(data)
    hash := h.Sum(nil)
    fmt.Printf("MD5: %x\n", hash)
    
    // 方法二：使用 Sum()
    hashSum := md5.Sum(data)
    fmt.Printf("MD5: %x\n", hashSum)
}
```

### 2.2 SHA-1

```go
package sha1

import "crypto/sha1"

// 创建新的 SHA-1 哈希实例
func New() hash.Hash

// 计算数据的 SHA-1 哈希值
func Sum(data []byte) [Size]byte

// 常量
const Size = 20
const BlockSize = 64
```

**使用示例**：

```go
import (
    "crypto/sha1"
    "fmt"
)

func main() {
    data := []byte("Hello, Go!")
    
    h := sha1.New()
    h.Write(data)
    hash := h.Sum(nil)
    fmt.Printf("SHA-1: %x\n", hash)
}
```

### 2.3 SHA-256

```go
package sha256

import "crypto/sha256"

// 创建新的 SHA-256 哈希实例
func New() hash.Hash

// 创建新的 SHA-224 哈希实例
func New224() hash.Hash

// 计算数据的 SHA-256 哈希值
func Sum256(data []byte) [Size]byte

// 计算数据的 SHA-224 哈希值
func Sum224(data []byte) [Size224]byte

// 常量
const Size = 32
const Size224 = 28
const BlockSize = 64
```

**使用示例**：

```go
import (
    "crypto/sha256"
    "fmt"
)

func main() {
    data := []byte("Hello, Go!")
    
    // SHA-256
    h := sha256.New()
    h.Write(data)
    hash := h.Sum(nil)
    fmt.Printf("SHA-256: %x\n", hash)
    
    // SHA-224
    h224 := sha256.New224()
    h224.Write(data)
    hash224 := h224.Sum(nil)
    fmt.Printf("SHA-224: %x\n", hash224)
}
```

### 2.4 SHA-512

```go
package sha512

import "crypto/sha512"

// 创建新的 SHA-512 哈希实例
func New() hash.Hash

// 创建新的 SHA-384 哈希实例
func New384() hash.Hash

// 创建新的 SHA-512/224 哈希实例
func New512_224() hash.Hash

// 创建新的 SHA-512/256 哈希实例
func New512_256() hash.Hash

// 计算数据的 SHA-512 哈希值
func Sum512(data []byte) [Size]byte

// 计算数据的 SHA-384 哈希值
func Sum384(data []byte) [Size384]byte

// 计算数据的 SHA-512/224 哈希值
func Sum512_224(data []byte) [Size512_224]byte

// 计算数据的 SHA-512/256 哈希值
func Sum512_256(data []byte) [Size512_256]byte

// 常量
const Size = 64
const Size384 = 48
const Size512_224 = 28
const Size512_256 = 32
const BlockSize = 128
```

**使用示例**：

```go
import (
    "crypto/sha512"
    "fmt"
)

func main() {
    data := []byte("Hello, Go!")
    
    // SHA-512
    h := sha512.New()
    h.Write(data)
    hash := h.Sum(nil)
    fmt.Printf("SHA-512: %x\n", hash)
    
    // SHA-384
    h384 := sha512.New384()
    h384.Write(data)
    hash384 := h384.Sum(nil)
    fmt.Printf("SHA-384: %x\n", hash384)
}
```

### 2.5 SHA-3

```go
package sha3

import "crypto/sha3"

// 创建新的 SHA3-224 哈希实例
func New224() hash.Hash

// 创建新的 SHA3-256 哈希实例
func New256() hash.Hash

// 创建新的 SHA3-384 哈希实例
func New384() hash.Hash

// 创建新的 SHA3-512 哈希实例
func New512() hash.Hash

// 创建新的 SHAKE-128 哈希实例
func NewShake128() hash.Hash

// 创建新的 SHAKE-256 哈希实例
func NewShake256() hash.Hash

// 计算数据的 SHA3-224 哈希值
func Sum224(data []byte) [28]byte

// 计算数据的 SHA3-256 哈希值
func Sum256(data []byte) [32]byte

// 计算数据的 SHA3-384 哈希值
func Sum384(data []byte) [48]byte

// 计算数据的 SHA3-512 哈希值
func Sum512(data []byte) [64]byte

// 计算数据的 SHAKE-128 哈希值
func ShakeSum128(out, data []byte)

// 计算数据的 SHAKE-256 哈希值
func ShakeSum256(out, data []byte)
```

**使用示例**：

```go
import (
    "crypto/sha3"
    "fmt"
)

func main() {
    data := []byte("Hello, Go!")
    
    // SHA3-256
    h := sha3.New256()
    h.Write(data)
    hash := h.Sum(nil)
    fmt.Printf("SHA3-256: %x\n", hash)
    
    // SHAKE-256
    shake := sha3.NewShake256()
    shake.Write(data)
    var shakeOut [64]byte
    shake.Read(shakeOut[:])
    fmt.Printf("SHAKE-256: %x\n", shakeOut)
}
```

### 2.6 HMAC

```go
package hmac

import "crypto/hmac"

// 创建新的 HMAC 哈希实例
func New(h func() hash.Hash, key []byte) hash.Hash

// 检查 MAC 是否匹配
func Equal(mac1, mac2 []byte) bool
```

**使用示例**：

```go
import (
    "crypto/hmac"
    "crypto/sha256"
    "fmt"
)

func main() {
    key := []byte("secret-key")
    data := []byte("Hello, Go!")
    
    // 创建 HMAC 实例
    h := hmac.New(sha256.New, key)
    h.Write(data)
    mac := h.Sum(nil)
    fmt.Printf("HMAC-SHA256: %x\n", mac)
    
    // 验证 MAC
    h2 := hmac.New(sha256.New, key)
    h2.Write(data)
    mac2 := h2.Sum(nil)
    
    if hmac.Equal(mac, mac2) {
        fmt.Println("MAC verification successful")
    } else {
        fmt.Println("MAC verification failed")
    }
}
```

### 2.7 MapHash

```go
package maphash

import "crypto/maphash"

// 创建新的 MapHash 实例
func New() *MapHash

// 重置 MapHash 实例
func (h *MapHash) Reset()

// 写入数据
func (h *MapHash) Write(b []byte) (int, error)

// 计算 64 位哈希值
func (h *MapHash) Sum64() uint64

// 直接计算字符串的哈希值
func String(s string) uint64

// 直接计算字节切片的哈希值
func Bytes(b []byte) uint64
```

**使用示例**：

```go
import (
    "crypto/maphash"
    "fmt"
)

func main() {
    // 方法一：使用 MapHash 实例
    h := maphash.New()
    h.Write([]byte("Hello, Go!"))
    hash := h.Sum64()
    fmt.Printf("MapHash: %d\n", hash)
    
    // 方法二：直接计算
    hashStr := maphash.String("Hello, Go!")
    fmt.Printf("MapHash String: %d\n", hashStr)
    
    hashBytes := maphash.Bytes([]byte("Hello, Go!"))
    fmt.Printf("MapHash Bytes: %d\n", hashBytes)
}
```

### 2.8 BLAKE2b

```go
package blake2b

import "crypto/blake2b"

// 创建新的 BLAKE2b 哈希实例
func New(size int) (hash.Hash, error)

// 创建新的 BLAKE2b 哈希实例（带密钥）
func NewKeyed(size int, key []byte) (hash.Hash, error)

// 计算数据的 BLAKE2b 哈希值
func Sum256(data []byte) [32]byte

// 计算数据的 BLAKE2b 哈希值（带密钥）
func Sum256WithKey(data, key []byte) [32]byte

// 计算数据的 BLAKE2b 哈希值
func Sum512(data []byte) [64]byte

// 计算数据的 BLAKE2b 哈希值（带密钥）
func Sum512WithKey(data, key []byte) [64]byte
```

**使用示例**：

```go
import (
    "crypto/blake2b"
    "fmt"
)

func main() {
    data := []byte("Hello, Go!")
    
    // BLAKE2b-256
    h, err := blake2b.New(32, nil)
    if err != nil {
        panic(err)
    }
    h.Write(data)
    hash := h.Sum(nil)
    fmt.Printf("BLAKE2b-256: %x\n", hash)
    
    // 带密钥的 BLAKE2b
    key := []byte("secret-key")
    hKeyed, err := blake2b.NewKeyed(32, key)
    if err != nil {
        panic(err)
    }
    hKeyed.Write(data)
    hashKeyed := hKeyed.Sum(nil)
    fmt.Printf("BLAKE2b-256 (keyed): %x\n", hashKeyed)
}
```

### 2.9 BLAKE2s

```go
package blake2s

import "crypto/blake2s"

// 创建新的 BLAKE2s 哈希实例
func New(size int) (hash.Hash, error)

// 创建新的 BLAKE2s 哈希实例（带密钥）
func NewKeyed(size int, key []byte) (hash.Hash, error)

// 计算数据的 BLAKE2s 哈希值
func Sum256(data []byte) [32]byte

// 计算数据的 BLAKE2s 哈希值（带密钥）
func Sum256WithKey(data, key []byte) [32]byte
```

**使用示例**：

```go
import (
    "crypto/blake2s"
    "fmt"
)

func main() {
    data := []byte("Hello, Go!")
    
    // BLAKE2s-256
    h, err := blake2s.New(32, nil)
    if err != nil {
        panic(err)
    }
    h.Write(data)
    hash := h.Sum(nil)
    fmt.Printf("BLAKE2s-256: %x\n", hash)
}
```

## 三、哈希库的应用场景

### 3.1 数据完整性验证

```go
import (
    "crypto/sha256"
    "fmt"
    "io"
    "os"
)

func calculateFileHash(filePath string) ([]byte, error) {
    file, err := os.Open(filePath)
    if err != nil {
        return nil, err
    }
    defer file.Close()
    
    h := sha256.New()
    if _, err := io.Copy(h, file); err != nil {
        return nil, err
    }
    
    return h.Sum(nil), nil
}

func main() {
    hash, err := calculateFileHash("example.txt")
    if err != nil {
        panic(err)
    }
    fmt.Printf("File hash: %x\n", hash)
}
```

### 3.2 密码哈希

**注意**：不要直接使用哈希函数存储密码，应使用专门的密码哈希库如 `golang.org/x/crypto/bcrypt`。

### 3.3 消息认证

```go
import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/base64"
    "fmt"
)

func generateHMAC(message, secret []byte) string {
    h := hmac.New(sha256.New, secret)
    h.Write(message)
    return base64.StdEncoding.EncodeToString(h.Sum(nil))
}

func verifyHMAC(message, secret []byte, expectedMAC string) bool {
    expected, err := base64.StdEncoding.DecodeString(expectedMAC)
    if err != nil {
        return false
    }
    
    h := hmac.New(sha256.New, secret)
    h.Write(message)
    actual := h.Sum(nil)
    
    return hmac.Equal(actual, expected)
}

func main() {
    message := []byte("Hello, Go!")
    secret := []byte("secret-key")
    
    mac := generateHMAC(message, secret)
    fmt.Printf("HMAC: %s\n", mac)
    
    valid := verifyHMAC(message, secret, mac)
    fmt.Printf("HMAC valid: %t\n", valid)
}
```

### 3.4 哈希表键

```go
import (
    "crypto/maphash"
    "fmt"
)

type HashTable struct {
    buckets [16][]string
}

func (ht *HashTable) hash(key string) int {
    h := maphash.String(key)
    return int(h % 16)
}

func (ht *HashTable) Add(key string, value string) {
    idx := ht.hash(key)
    ht.buckets[idx] = append(ht.buckets[idx], value)
}

func (ht *HashTable) Get(key string) []string {
    idx := ht.hash(key)
    return ht.buckets[idx]
}

func main() {
    ht := &HashTable{}
    ht.Add("key1", "value1")
    ht.Add("key2", "value2")
    
    fmt.Println(ht.Get("key1"))
    fmt.Println(ht.Get("key2"))
}
```

## 四、性能对比

| 算法 | 速度 | 安全性 | 输出长度 | 适用场景 |
|------|------|--------|----------|----------|
| MD5 | 非常快 | 低 | 128位 | 非安全场景的数据校验 |
| SHA-1 | 快 | 低 | 160位 | 遗留系统 |
| SHA-256 | 中 | 高 | 256位 | 安全场景 |
| SHA-512 | 慢 | 高 | 512位 | 高安全场景 |
| SHA-3 | 中 | 高 | 可变 | 安全场景 |
| BLAKE2b | 快 | 高 | 可变 | 性能要求高的安全场景 |
| MapHash | 非常快 | 低 | 64位 | 哈希表等内部使用 |

## 五、最佳实践

### 5.1 选择合适的哈希算法

| 场景 | 推荐算法 | 原因 |
|------|----------|------|
| 文件完整性校验 | SHA-256, BLAKE2b | 安全性高，速度快 |
| 密码存储 | bcrypt, argon2 | 专门设计用于密码哈希 |
| 消息认证 | HMAC-SHA256 | 提供消息完整性和认证 |
| 哈希表 | MapHash | 高性能，适合内部使用 |
| 数字签名 | SHA-256, SHA-512 | 安全性高 |

### 5.2 性能优化

1. **重用哈希实例**：对于多次哈希计算，重用同一个哈希实例

```go
func hashMultipleStrings(strings []string) [][]byte {
    h := sha256.New()
    results := make([][]byte, len(strings))
    
    for i, s := range strings {
        h.Reset()
        h.Write([]byte(s))
        results[i] = h.Sum(nil)
    }
    
    return results
}
```

2. **使用缓冲区**：对于大文件，使用缓冲区提高性能

```go
func calculateFileHash(filePath string) ([]byte, error) {
    file, err := os.Open(filePath)
    if err != nil {
        return nil, err
    }
    defer file.Close()
    
    h := sha256.New()
    buf := make([]byte, 64*1024) // 64KB 缓冲区
    
    for {
        n, err := file.Read(buf)
        if err == io.EOF {
            break
        }
        if err != nil {
            return nil, err
        }
        h.Write(buf[:n])
    }
    
    return h.Sum(nil), nil
}
```

3. **并发哈希**：对于多个文件，使用并发提高速度

```go
func calculateMultipleFileHashes(filePaths []string) (map[string][]byte, error) {
    results := make(map[string][]byte)
    var mu sync.Mutex
    var wg sync.WaitGroup
    var firstErr error
    
    for _, path := range filePaths {
        wg.Add(1)
        go func(p string) {
            defer wg.Done()
            
            hash, err := calculateFileHash(p)
            if err != nil {
                mu.Lock()
                if firstErr == nil {
                    firstErr = err
                }
                mu.Unlock()
                return
            }
            
            mu.Lock()
            results[p] = hash
            mu.Unlock()
        }(path)
    }
    
    wg.Wait()
    return results, firstErr
}
```

### 5.3 安全注意事项

1. **不要使用 MD5 和 SHA-1**：这些算法已被认为不安全
2. **使用 HMAC 进行消息认证**：提供额外的密钥保护
3. **不要直接存储密码**：使用专门的密码哈希库
4. **使用随机盐**：防止彩虹表攻击
5. **定期更新哈希算法**：随着密码学的发展，算法可能会被破解

## 六、常见问题与解决方案

### 6.1 哈希碰撞

**问题**：不同的输入产生相同的哈希值

**解决方案**：
- 使用更长的哈希算法（如 SHA-256 或更高）
- 结合使用多个哈希算法
- 对于密码，使用专门的密码哈希库

### 6.2 性能问题

**问题**：哈希计算速度慢

**解决方案**：
- 选择适合场景的哈希算法
- 重用哈希实例
- 使用缓冲区
- 并发处理

### 6.3 内存使用

**问题**：大文件哈希消耗大量内存

**解决方案**：
- 使用流式处理
- 分块读取文件
- 避免一次性加载整个文件到内存

## 七、代码示例

### 7.1 综合示例：文件哈希工具

```go
package main

import (
    "crypto/sha256"
    "flag"
    "fmt"
    "io"
    "os"
)

func calculateHash(filePath string) ([]byte, error) {
    file, err := os.Open(filePath)
    if err != nil {
        return nil, err
    }
    defer file.Close()
    
    h := sha256.New()
    buf := make([]byte, 64*1024)
    
    for {
        n, err := file.Read(buf)
        if err == io.EOF {
            break
        }
        if err != nil {
            return nil, err
        }
        h.Write(buf[:n])
    }
    
    return h.Sum(nil), nil
}

func main() {
    var filePath string
    flag.StringVar(&filePath, "file", "", "File to calculate hash for")
    flag.Parse()
    
    if filePath == "" {
        fmt.Println("Please specify a file with -file")
        os.Exit(1)
    }
    
    hash, err := calculateHash(filePath)
    if err != nil {
        fmt.Printf("Error calculating hash: %v\n", err)
        os.Exit(1)
    }
    
    fmt.Printf("SHA-256 hash of %s: %x\n", filePath, hash)
}
```

### 7.2 示例：HMAC 认证

```go
package main

import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/base64"
    "fmt"
    "net/http"
    "strings"
)

func generateSignature(message, secret string) string {
    h := hmac.New(sha256.New, []byte(secret))
    h.Write([]byte(message))
    return base64.StdEncoding.EncodeToString(h.Sum(nil))
}

func verifySignature(message, secret, signature string) bool {
    expected := generateSignature(message, secret)
    return hmac.Equal([]byte(signature), []byte(expected))
}

func handler(w http.ResponseWriter, r *http.Request) {
    secret := "my-secret-key"
    
    // 从请求中获取消息和签名
    message := r.FormValue("message")
    signature := r.FormValue("signature")
    
    if message == "" || signature == "" {
        http.Error(w, "Missing message or signature", http.StatusBadRequest)
        return
    }
    
    // 验证签名
    if verifySignature(message, secret, signature) {
        fmt.Fprintf(w, "Signature verified successfully")
    } else {
        http.Error(w, "Invalid signature", http.StatusUnauthorized)
    }
}

func main() {
    http.HandleFunc("/verify", handler)
    fmt.Println("Server starting on :8080")
    http.ListenAndServe(":8080", nil)
}
```

## 八、总结

Go 语言提供了丰富的哈希库，包括多种哈希算法和工具函数，满足不同场景的需求。从基本的 MD5、SHA-1 到安全的 SHA-256、SHA-512、SHA-3，再到高性能的 BLAKE2b 和专门用于哈希表的 MapHash，Go 都提供了简洁易用的 API。

在使用哈希库时，需要注意以下几点：

1. **选择合适的算法**：根据安全性和性能需求选择合适的哈希算法
2. **注意安全**：不要使用已被认为不安全的算法，如 MD5 和 SHA-1
3. **性能优化**：重用哈希实例，使用缓冲区，并发处理
4. **正确使用**：对于特定场景，使用专门的工具，如密码哈希使用 bcrypt
5. **错误处理**：妥善处理哈希计算过程中的错误

通过合理使用这些哈希库，你可以在 Go 应用中实现数据完整性验证、消息认证、密码存储等功能，确保数据的安全性和可靠性。

:::tip 最终建议

1. **优先使用安全算法**：SHA-256、SHA-512、SHA-3 或 BLAKE2b
2. **使用 HMAC 进行认证**：提供额外的密钥保护
3. **性能与安全平衡**：根据具体场景选择合适的算法
4. **定期更新**：关注密码学发展，及时更新哈希算法
5. **测试与验证**：确保哈希实现的正确性

:::

***

# 页面底部