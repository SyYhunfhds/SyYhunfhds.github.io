---
title: Go 快速哈希算法详解

date: 2026-04-08

footer: Trae编辑

---

[[toc]]

***

:::info 参考资料
- [Go maphash 包官方文档](https://pkg.go.dev/hash/maphash)
- [xxHash 官方网站](https://xxhash.com/)
- [哈希算法性能大比拼](https://blog.csdn.net/VarChat/article/details/155607795)
- [CityHash 算法文档](https://github.com/TheAnsarya/StreamHash/blob/main/docs/algorithms/cityhash.md)
- [Go CityHash 实现](https://pkg.go.dev/github.com/rolandhe/saber/hash)
:::

## 一、引言

在 Go 语言中，哈希算法是一种重要的工具，广泛应用于数据结构（如哈希表）、数据分片、缓存键生成等场景。传统的加密哈希算法（如 MD5、SHA-1）虽然安全性高，但计算开销大，不适合高频调用场景。因此，快速非加密哈希算法应运而生，它们在速度和分布均匀性之间取得了良好的平衡。

本文将详细介绍 Go 语言中的快速哈希算法，包括标准库中的 `maphash` 以及第三方实现的 `xxHash`、`MurmurHash`、`CityHash` 等算法，分析它们的性能特点和适用场景。

## 二、Go maphash 标准库

### 2.1 基本概念

`hash/maphash` 是 Go 标准库中的一个包，提供了用于哈希表等数据结构的快速哈希函数。这些哈希函数设计用于将任意字符串或字节序列映射到均匀分布的 64 位无符号整数。

### 2.2 核心结构

```go
// Seed 是一个随机值，用于选择特定的哈希函数
type Seed struct {
    // 内部实现细节
}

// Hash 计算字节序列的哈希值
type Hash struct {
    // 内部实现细节
}
```

### 2.3 主要函数

| 函数 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `MakeSeed()` | 创建一个新的随机种子 | 无 | `Seed` |
| `Bytes(seed Seed, b []byte)` | 计算字节切片的哈希值 | seed: 种子<br>b: 字节切片 | `uint64` |
| `String(seed Seed, s string)` | 计算字符串的哈希值 | seed: 种子<br>s: 字符串 | `uint64` |
| `Comparable[T comparable](seed Seed, v T)` | 计算可比较值的哈希值 | seed: 种子<br>v: 可比较值 | `uint64` |

### 2.4 Hash 方法

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `Reset()` | 重置哈希状态 | 无 | 无 |
| `Seed()` | 返回当前种子 | 无 | `Seed` |
| `SetSeed(seed Seed)` | 设置种子 | seed: 种子 | 无 |
| `Sum64()` | 返回当前哈希值 | 无 | `uint64` |
| `Write(b []byte)` | 写入字节数据 | b: 字节切片 | `(int, error)` |
| `WriteByte(b byte)` | 写入单个字节 | b: 字节 | `error` |
| `WriteString(s string)` | 写入字符串 | s: 字符串 | `(int, error)` |
| `WriteComparable[T comparable](x T)` | 写入可比较值 | x: 可比较值 | 无 |

### 2.5 使用示例

```go
package main

import (
    "fmt"
    "hash/maphash"
)

func main() {
    // 创建种子
    seed := maphash.MakeSeed()
    
    // 直接计算哈希值
    data := []byte("Hello, Go!")
    hash1 := maphash.Bytes(seed, data)
    fmt.Printf("Bytes hash: %d\n", hash1)
    
    str := "Hello, Go!"
    hash2 := maphash.String(seed, str)
    fmt.Printf("String hash: %d\n", hash2)
    
    // 使用 Hash 结构
    var h maphash.Hash
    h.SetSeed(seed)
    h.Write(data)
    hash3 := h.Sum64()
    fmt.Printf("Hash struct hash: %d\n", hash3)
    
    // 计算可比较值的哈希
    num := 42
    hash4 := maphash.Comparable(seed, num)
    fmt.Printf("Comparable hash: %d\n", hash4)
}
```

### 2.6 特点与优势

- **高性能**：专门为哈希表等数据结构优化
- **均匀分布**：哈希值分布均匀，减少碰撞
- **种子机制**：通过种子可以生成不同的哈希函数
- **类型安全**：支持可比较类型的哈希计算
- **标准库**：无需额外依赖

## 三、xxHash 算法

### 3.1 基本概念

xxHash 是一种极致性能的非加密哈希算法，由 Yann Collet 开发。它的设计目标是在保持良好哈希质量的同时，达到接近内存速度的性能。

### 3.2 主要变体

| 变体 | 输出长度 | 特点 |
|------|----------|------|
| XXH32 | 32位 | 适用于32位系统 |
| XXH64 | 64位 | 适用于64位系统 |
| XXH3_64bits | 64位 | XXH3版本，性能更好 |
| XXH3_128bits | 128位 | XXH3版本，输出更长 |

### 3.3 Go 实现

Go 语言中常用的 xxHash 实现包括：

- **github.com/OneOfOne/xxhash**：XXH64 实现
- **github.com/cespare/xxhash**：带汇编优化的实现
- **github.com/zeebo/xxh3**：XXH3 实现

### 3.4 使用示例

```go
package main

import (
    "fmt"
    "github.com/cespare/xxhash/v2"
)

func main() {
    // 直接计算哈希值
    data := []byte("Hello, Go!")
    hash := xxhash.Sum64(data)
    fmt.Printf("XXH64 hash: %d\n", hash)
    
    // 使用哈希器
    h := xxhash.New()
    h.Write(data)
    hash2 := h.Sum64()
    fmt.Printf("XXH64 hasher hash: %d\n", hash2)
}
```

### 3.5 性能特点

- **极致速度**：在现代 CPU 上可以达到接近内存带宽的速度
- **良好分布**：哈希质量高，碰撞率低
- **小数据优化**：XXH3 版本对小数据特别优化
- **可扩展性**：支持不同长度的输出

## 四、MurmurHash 算法

### 4.1 基本概念

MurmurHash 是由 Austin Appleby 开发的一系列非加密哈希算法，以其良好的雪崩效应和分布特性而闻名。

### 4.2 主要版本

| 版本 | 输出长度 | 特点 |
|------|----------|------|
| MurmurHash1 | 32位 | 早期版本 |
| MurmurHash2 | 32/64位 | 广泛使用 |
| MurmurHash3 | 32/128位 | 最新版本，性能更好 |

### 4.3 Go 实现

Go 语言中常用的 MurmurHash 实现包括：

- **github.com/spaolacci/murmur3**：MurmurHash3 实现

### 4.4 使用示例

```go
package main

import (
    "fmt"
    "github.com/spaolacci/murmur3"
)

func main() {
    // 32位哈希
    data := []byte("Hello, Go!")
    hash32 := murmur3.Sum32(data)
    fmt.Printf("Murmur3 32-bit hash: %d\n", hash32)
    
    // 128位哈希
    hash128 := murmur3.Sum128(data)
    fmt.Printf("Murmur3 128-bit hash: %d\n", hash128)
    
    // 使用哈希器
    h := murmur3.New32()
    h.Write(data)
    hash32b := h.Sum32()
    fmt.Printf("Murmur3 32-bit hasher: %d\n", hash32b)
}
```

### 4.5 特点与优势

- **良好的雪崩效应**：输入的微小变化会导致输出的显著不同
- **分布均匀**：哈希值分布均匀，减少碰撞
- **适用于缓存**：常用于内存缓存的键生成
- **广泛应用**：被许多开源项目采用

## 五、CityHash 算法

### 5.1 基本概念

CityHash 是由 Google 开发的一系列哈希函数，专为快速字符串哈希而设计，特别优化了长键的处理。

### 5.2 主要变体

| 变体 | 输出长度 | 特点 |
|------|----------|------|
| CityHash32 | 32位 | 适用于32位系统 |
| CityHash64 | 64位 | 适用于64位系统 |
| CityHash128 | 128位 | 适用于长字符串 |
| CityHashCrc128 | 128位 | 使用CRC32指令加速 |
| CityHashCrc256 | 256位 | 使用CRC32指令，输出更长 |

### 5.3 Go 实现

Go 语言中常用的 CityHash 实现包括：

- **github.com/rolandhe/saber/hash**：完整的 CityHash 实现

### 5.4 使用示例

```go
package main

import (
    "fmt"
    "github.com/rolandhe/saber/hash"
)

func main() {
    // 32位哈希
    data := []byte("Hello, Go!")
    hash32 := hash.CityHash32(data, uint(len(data)))
    fmt.Printf("CityHash 32-bit hash: %d\n", hash32)
    
    // 64位哈希
    hash64 := hash.CityHash64(data, uint(len(data)))
    fmt.Printf("CityHash 64-bit hash: %d\n", hash64)
    
    // 128位哈希
    hash128 := hash.CityHash128(data, uint(len(data)))
    fmt.Printf("CityHash 128-bit hash: %d-%d\n", hash128.Low, hash128.High)
}
```

### 5.5 特点与优势

- **对长键优化**：特别适合处理长字符串
- **并行处理**：利用 SIMD 指令加速
- **多路径设计**：根据输入长度采用不同的处理策略
- **高性能**：在现代 CPU 上表现出色

## 六、性能对比

### 6.1 基准测试结果

根据参考资料，各哈希算法的性能对比（每百万次耗时）：

| 算法 | 耗时 | 适用场景 |
|------|------|----------|
| MD5 | 850ms | 安全性要求高的场景 |
| SHA-1 | 550ms | 安全性要求高的场景 |
| MurmurHash3 | 210ms | 缓存、布隆过滤器 |
| xxHash64 | 95ms | 高负载数据分片 |
| CityHash64 | ~100ms | 长键处理 |
| maphash | ~100ms | 标准库哈希表 |

### 6.2 带宽对比

根据 xxHash 官方测试（Intel i7-9700K CPU）：

| 算法 | 带宽 (GB/s) | 小数据速度 | 质量 |
|------|-------------|------------|------|
| XXH3 (SSE2) | 31.5 GB/s | 133.1 | 10 |
| XXH128 (SSE2) | 29.6 GB/s | 118.1 | 10 |
| City64 | 22.0 GB/s | 76.6 | 10 |
| T1ha2 | 22.0 GB/s | 99.0 | 9 |
| City128 | 21.7 GB/s | 57.7 | 10 |
| XXH64 | 19.4 GB/s | 71.0 | 10 |
| Murmur3 | 3.9 GB/s | 56.1 | 10 |
| MD5 | 0.6 GB/s | 7.8 | 10 |

## 七、应用场景

### 7.1 哈希表

- **maphash**：标准库 map 的默认哈希函数
- **xxHash**：高性能哈希表实现
- **MurmurHash**：缓存系统中的键生成

### 7.2 数据分片

- **xxHash**：分布式系统中的数据分片
- **CityHash**：处理长键的数据分片
- **MurmurHash**：一致性哈希中的节点哈希

### 7.3 缓存系统

- **MurmurHash**：缓存键生成
- **xxHash**：高性能缓存系统
- **maphash**：内存缓存

### 7.4 布隆过滤器

- **MurmurHash**：布隆过滤器的哈希函数
- **xxHash**：高性能布隆过滤器

### 7.5 内容寻址存储

- **CityHash128**：长内容的哈希标识
- **xxHash128**：内容寻址存储

## 八、最佳实践

### 8.1 选择合适的哈希算法

| 场景 | 推荐算法 | 原因 |
|------|----------|------|
| 标准库哈希表 | maphash | 标准库内置，无需额外依赖 |
| 高性能哈希表 | xxHash | 速度最快，分布均匀 |
| 长键处理 | CityHash | 对长字符串优化 |
| 缓存键生成 | MurmurHash | 良好的雪崩效应 |
| 数据分片 | xxHash | 高性能，分布均匀 |
| 布隆过滤器 | MurmurHash | 广泛使用，性能稳定 |

### 8.2 性能优化

1. **选择合适的算法**：根据具体场景选择性能最优的哈希算法
2. **批量处理**：对于多个数据，批量计算哈希值
3. **缓存哈希值**：对于重复使用的数据，缓存其哈希值
4. **使用种子**：为不同的哈希表使用不同的种子，减少碰撞
5. **避免频繁创建哈希器**：重用哈希器实例

### 8.3 注意事项

1. **非加密用途**：这些算法都不是加密安全的，不能用于密码存储等安全场景
2. **种子管理**：合理管理种子，避免使用固定种子
3. **碰撞处理**：虽然碰撞率低，但仍需处理碰撞情况
4. **平台兼容性**：某些优化版本可能依赖特定硬件

## 九、代码示例

### 9.1 哈希表实现

```go
package main

import (
    "fmt"
    "hash/maphash"
)

// HashTable 实现了一个简单的哈希表
type HashTable struct {
    buckets [16][]string
    seed    maphash.Seed
}

// NewHashTable 创建一个新的哈希表
func NewHashTable() *HashTable {
    return &HashTable{
        seed: maphash.MakeSeed(),
    }
}

// hash 计算键的哈希值
func (ht *HashTable) hash(key string) int {
    h := maphash.String(ht.seed, key)
    return int(h % 16)
}

// Add 添加键值对
func (ht *HashTable) Add(key, value string) {
    idx := ht.hash(key)
    ht.buckets[idx] = append(ht.buckets[idx], key+"="+value)
}

// Get 获取值
func (ht *HashTable) Get(key string) (string, bool) {
    idx := ht.hash(key)
    for _, item := range ht.buckets[idx] {
        if len(item) > len(key) && item[:len(key)] == key {
            return item[len(key)+1:], true
        }
    }
    return "", false
}

func main() {
    ht := NewHashTable()
    ht.Add("key1", "value1")
    ht.Add("key2", "value2")
    ht.Add("key3", "value3")
    
    if val, ok := ht.Get("key2"); ok {
        fmt.Printf("key2: %s\n", val)
    }
    
    if val, ok := ht.Get("key4"); ok {
        fmt.Printf("key4: %s\n", val)
    } else {
        fmt.Println("key4 not found")
    }
}
```

### 9.2 一致性哈希实现

```go
package main

import (
    "fmt"
    "sort"
    "github.com/cespare/xxhash/v2"
)

// ConsistentHash 实现了一致性哈希
type ConsistentHash struct {
    nodes     map[uint64]string
    sortedHashes []uint64
    replicas  int
}

// NewConsistentHash 创建一个新的一致性哈希
func NewConsistentHash(replicas int) *ConsistentHash {
    return &ConsistentHash{
        nodes:    make(map[uint64]string),
        replicas: replicas,
    }
}

// Add 添加节点
func (ch *ConsistentHash) Add(node string) {
    for i := 0; i < ch.replicas; i++ {
        hash := xxhash.Sum64([]byte(fmt.Sprintf("%s:%d", node, i)))
        ch.nodes[hash] = node
        ch.sortedHashes = append(ch.sortedHashes, hash)
    }
    sort.Slice(ch.sortedHashes, func(i, j int) bool {
        return ch.sortedHashes[i] < ch.sortedHashes[j]
    })
}

// Get 获取键对应的节点
func (ch *ConsistentHash) Get(key string) string {
    if len(ch.nodes) == 0 {
        return ""
    }
    
    hash := xxhash.Sum64([]byte(key))
    idx := sort.Search(len(ch.sortedHashes), func(i int) bool {
        return ch.sortedHashes[i] >= hash
    })
    
    if idx == len(ch.sortedHashes) {
        idx = 0
    }
    
    return ch.nodes[ch.sortedHashes[idx]]
}

func main() {
    ch := NewConsistentHash(3)
    ch.Add("node1")
    ch.Add("node2")
    ch.Add("node3")
    
    keys := []string{"key1", "key2", "key3", "key4", "key5"}
    for _, key := range keys {
        node := ch.Get(key)
        fmt.Printf("Key %s -> Node %s\n", key, node)
    }
}
```

### 9.3 布隆过滤器实现

```go
package main

import (
    "fmt"
    "github.com/spaolacci/murmur3"
)

// BloomFilter 实现了布隆过滤器
type BloomFilter struct {
    bits  []bool
    k     int
    size  int
}

// NewBloomFilter 创建一个新的布隆过滤器
func NewBloomFilter(size, k int) *BloomFilter {
    return &BloomFilter{
        bits: make([]bool, size),
        k:    k,
        size: size,
    }
}

// hash 计算多个哈希值
func (bf *BloomFilter) hash(data []byte) []int {
    hashes := make([]int, bf.k)
    
    // 使用不同的种子计算多个哈希值
    for i := 0; i < bf.k; i++ {
        h := murmur3.New32()
        h.Write(data)
        h.Write([]byte(fmt.Sprintf("%d", i)))
        hashes[i] = int(h.Sum32()) % bf.size
    }
    
    return hashes
}

// Add 添加元素
func (bf *BloomFilter) Add(data []byte) {
    for _, idx := range bf.hash(data) {
        bf.bits[idx] = true
    }
}

// Contains 检查元素是否存在
func (bf *BloomFilter) Contains(data []byte) bool {
    for _, idx := range bf.hash(data) {
        if !bf.bits[idx] {
            return false
        }
    }
    return true
}

func main() {
    bf := NewBloomFilter(1000, 3)
    
    // 添加元素
    bf.Add([]byte("hello"))
    bf.Add([]byte("world"))
    bf.Add([]byte("go"))
    
    // 检查元素
    fmt.Printf("Contains 'hello': %t\n", bf.Contains([]byte("hello")))
    fmt.Printf("Contains 'world': %t\n", bf.Contains([]byte("world")))
    fmt.Printf("Contains 'go': %t\n", bf.Contains([]byte("go")))
    fmt.Printf("Contains 'test': %t\n", bf.Contains([]byte("test")))
}
```

## 十、总结

Go 语言提供了多种快速哈希算法，每种算法都有其特点和适用场景：

1. **maphash**：标准库内置，专为哈希表优化，使用简单，无需额外依赖。

2. **xxHash**：极致性能，特别是 XXH3 版本，对小数据有特别优化，适合高负载场景。

3. **MurmurHash**：良好的雪崩效应和分布特性，广泛应用于缓存系统和布隆过滤器。

4. **CityHash**：Google 开发，对长键处理有特别优化，适合处理长字符串。

在选择哈希算法时，应根据具体场景考虑以下因素：

- **性能需求**：不同算法的速度差异较大
- **数据特点**：长键还是短键
- **分布需求**：哈希值的分布均匀性
- **依赖管理**：是否愿意引入第三方库
- **平台兼容性**：某些优化版本可能依赖特定硬件

通过合理选择和使用这些快速哈希算法，可以显著提高系统的性能和可靠性，特别是在处理大规模数据和高并发场景时。

:::tip 最终建议

1. **标准库优先**：对于一般用途，使用 `maphash` 标准库即可
2. **性能优先**：对于高负载场景，选择 `xxHash`
3. **长键处理**：对于长字符串，选择 `CityHash`
4. **缓存场景**：对于缓存系统，选择 `MurmurHash`
5. **安全注意**：这些算法都不是加密安全的，不能用于安全场景
6. **种子管理**：为不同的哈希表使用不同的种子，减少碰撞
7. **性能测试**：在实际场景中测试不同算法的性能

:::

***

# 页面底部