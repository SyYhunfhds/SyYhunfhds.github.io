---
title: Go uint32 位宽加密算法库速查
date: 2026-03-09
footer: Trae编辑
---

# Go uint32 位宽加密算法库速查

## 概述

标准库 `crypto/aes` 使用 128 位（16 字节）分组大小。当你需要加密的只是 uint32（32 位）或 uint64（64 位）的整数值时，直接使用 AES 需要填充、处理 IV、并处理大于原始数据数倍的密文。

本文整理 Go 社区中直接以 uint32 或 uint64 为操作单位的加密算法库，涵盖小型分组密码、Feistel 网络、格式保留加密和流密码。

## 名词约定

| 术语 | 含义 |
|------|------|
| 分组大小 | 算法一次处理的固定数据块大小 |
| 操作单位 | 算法内部一次处理的最小整数位宽 |
| 保留格式 | 密文与明文具有相同的数据类型和取值范围 |

## 一、XXTEA（Corrected Block TEA）

XXTEA 是 TEA 系列算法的改进版本，以 **uint32** 为操作单位，分组大小为 64 位（2 个 uint32）。适合加密 32 位和 64 位整数值，密文长度与明文一致。

### 库地址

`github.com/twpayne/go-xxtea` v1.0.0（2025 年 4 月发布，MIT 许可证）

### API 速查

```go
import "github.com/twpayne/go-xxtea"

// 类型定义
type Cipher struct { /* 未导出字段 */ }
type Key [16]byte          // 128 位密钥
type RoundsFunc func(int) int

// 选项模式构建
func NewCipher(options ...CipherOption) (*Cipher, error)

// 选项函数
func WithKey(key Key) CipherOption
func WithRounds(rounds int) CipherOption
func WithRoundsFunc(roundsFunc RoundsFunc) CipherOption
func WithByteOrder(byteOrder binary.ByteOrder) CipherOption

// 核心方法
func (c *Cipher) Encrypt(plaintext []byte) ([]byte, error)
func (c *Cipher) Decrypt(ciphertext []byte) ([]byte, error)
func (c *Cipher) EncryptInPlace(v []uint32)
func (c *Cipher) DecryptInPlace(v []uint32)

// 辅助函数
func BytesToUint32s(bytes []byte, byteOrder binary.ByteOrder) ([]uint32, error)
func Uint32sToBytes(uint32s []uint32, byteOrder binary.ByteOrder) []byte
func DefaultRoundsFunc(n int) int
```

### 使用要点

- 密钥固定 16 字节（128 位）
- 数据必须是 64 位（2 个 uint32）的整数倍
- 支持大端和小端字节序
- `EncryptInPlace` / `DecryptInPlace` 直接操作 `[]uint32`，零内存分配
- 默认轮数由 `DefaultRoundsFunc` 根据数据长度决定（6 + n/2）

### 加密 uint32 值

```go
func EncryptUint32(c *xxtea.Cipher, val uint32, order binary.ByteOrder) (uint32, uint32, error) {
    data := []uint32{val, 0} // 补零到 64 位
    c.EncryptInPlace(data)
    return data[0], data[1], nil
}

func DecryptUint32(c *xxtea.Cipher, hi, lo uint32, order binary.ByteOrder) (uint32, error) {
    data := []uint32{hi, lo}
    c.DecryptInPlace(data)
    return data[0], nil
}
```

### 加密 uint64 值

```go
func EncryptUint64(c *xxtea.Cipher, val uint64, order binary.ByteOrder) (uint32, uint32, error) {
    data := BytesToUint32s(
        []byte{byte(val), byte(val>>8), byte(val>>16), byte(val>>24),
            byte(val>>32), byte(val>>40), byte(val>>48), byte(val>>56)},
        order,
    )
    c.EncryptInPlace(data)
    return data[0], data[1], nil
}
```

## 二、TEA（Tiny Encryption Algorithm）

TEA 是经典的小型分组密码，64 位分组大小，128 位密钥，内部全部使用 uint32 算术运算。

### 库地址

`github.com/deatil/go-cryptobin`（TEA 子包）

`github.com/golang-module/dongle`（TEA 支持）

### 操作特征

| 属性 | 值 |
|------|-----|
| 分组大小 | 64 位 |
| 密钥长度 | 128 位（16 字节） |
| 操作单位 | uint32 |
| 轮数 | 64 轮（32 轮 Feistel） |

### 使用 go-cryptobin 的 TEA

```go
import "github.com/deatil/go-cryptobin/cryptobin/crypto"

// 加密
result := crypto.
    FromString("plaintext").
    SetKey("1234567890123456").
    Tea(64).      // 指定轮数，默认 64
    ECB().        // 模式：ECB/CBC/CFB/OFB/CTR
    PKCS7Padding().
    Encrypt().
    ToBase64String()

// 解密
result = crypto.
    FromBase64String("ciphertext").
    SetKey("1234567890123456").
    Tea(64).
    ECB().
    PKCS7Padding().
    Decrypt().
    ToString()
```

### 使用 dongle 的 TEA

```go
import "github.com/golang-module/dongle"

// 加密
encrypted := dongle.Encrypt.
    FromString("hello world").
    ByTea(dongle.TeaCfg{Key: "1234567890123456"}).
    ToHexString()

// 解密
decrypted := dongle.Decrypt.
    FromHexString(encrypted).
    ByTea(dongle.TeaCfg{Key: "1234567890123456"}).
    ToString()
```

## 三、XTEA（Extended TEA）

XTEA 修复了 TEA 的等效密钥缺陷，分组大小和操作单位与 TEA 相同。

### 库地址

`github.com/deatil/go-cryptobin`（XTEA 子包）

### API 速查

```go
import "github.com/deatil/go-cryptobin/cryptobin/crypto"

// 用法同 TEA，仅替换方法名
result := crypto.
    FromString("data").
    SetKey("1234567890123456").
    Xtea().
    ECB().
    PKCS7Padding().
    Encrypt().
    ToBase64String()
```

## 四、Blowfish

Blowfish 是 64 位分组密码，密钥长度 32–448 位，使用 uint32 S-box 和 P-array。

### 库地址

`golang.org/x/crypto/blowfish`（标准扩展库）

### API 速查

```go
import "golang.org/x/crypto/blowfish"

// 常量
const BlockSize = 8  // 64 位分组

// 类型
type Cipher struct{ /* 未导出 */ }

// 构造
func NewCipher(key []byte) (*Cipher, error)        // 密钥 4-56 字节
func NewSaltedCipher(key, salt []byte) (*Cipher, error)
func ExpandKey(key []byte, c *Cipher)

// 实现 cipher.Block 接口
func (c *Cipher) BlockSize() int                    // 返回 8
func (c *Cipher) Encrypt(dst, src []byte)           // src 必须 8 字节
func (c *Cipher) Decrypt(dst, src []byte)
```

### 使用要点

::: warning 安全提醒
Blowfish 是遗留密码，64 位分组易受生日边界攻击（Sweet32）。仅在兼容遗留系统时使用。
:::

### 加密 uint64 值

```go
func EncryptBlowfishUint64(block cipher.Block, val uint64) uint64 {
    src := make([]byte, 8)
    binary.BigEndian.PutUint64(src, val)
    dst := make([]byte, 8)
    block.Encrypt(dst, src)
    return binary.BigEndian.Uint64(dst)
}
```

## 五、Twofish

Twofish 是 128 位分组密码，内部使用 uint32 操作。AES 竞赛最终候选算法之一。

### 库地址

`golang.org/x/crypto/twofish`

### API 速查

```go
import "golang.org/x/crypto/twofish"

const BlockSize = 16  // 128 位分组

type Cipher struct{ /* 未导出 */ }

func NewCipher(key []byte) (*Cipher, error)  // 密钥 16/24/32 字节
func (c *Cipher) BlockSize() int             // 返回 16
func (c *Cipher) Encrypt(dst, src []byte)
func (c *Cipher) Decrypt(dst, src []byte)
```

::: warning 安全提醒
Twofish 是遗留密码，新应用应使用 AES 或 XChaCha20-Poly1305。
:::

## 六、CAST5

CAST5（CAST-128）是 64 位分组密码，密钥最长 128 位，使用 uint32 操作。

### 库地址

`golang.org/x/crypto/cast5`

### API 速查

```go
import "golang.org/x/crypto/cast5"

const BlockSize = 8

type Cipher struct{ /* 未导出 */ }

func NewCipher(key []byte) (*Cipher, error)  // 密钥 5-16 字节
func (c *Cipher) BlockSize() int             // 返回 8
func (c *Cipher) Encrypt(dst, src []byte)
func (c *Cipher) Decrypt(dst, src []byte)
```

## 七、ChaCha20（流密码）

ChaCha20 是流密码，使用 uint32 内部状态和 uint32 计数器。特别适用于需要分块加密的随机访问场景。

### 库地址

`golang.org/x/crypto/chacha20`

### API 速查

```go
import "golang.org/x/crypto/chacha20"

// 常量
const KeySize = 32    // 256 位密钥
const NonceSize = 12  // 标准 nonce
const NonceSizeX = 24 // XChaCha20 nonce

// 类型
type Cipher struct{ /* 未导出 */ }

// 构造
func NewUnauthenticatedCipher(key, nonce []byte) (*Cipher, error)

// 设置计数器（uint32 位宽）
func (s *Cipher) SetCounter(counter uint32)

// 加解密
func (s *Cipher) XORKeyStream(dst, src []byte)

// 辅助函数
func HChaCha20(key, nonce []byte) ([]byte, error)
```

### 加密 uint32 值

```go
func EncryptUint32ChaCha20(c *chacha20.Cipher, plaintext uint32) uint32 {
    src := make([]byte, 4)
    binary.LittleEndian.PutUint32(src, plaintext)
    dst := make([]byte, 4)
    c.XORKeyStream(dst, src)
    return binary.LittleEndian.Uint32(dst)
}
```

### 使用 uint64 作为随机访问索引

```go
// 用 SetCounter 实现任意位置可解密
func EncryptSector(c *chacha20.Cipher, sectorID uint32, data []byte) []byte {
    c.SetCounter(sectorID)
    out := make([]byte, len(data))
    c.XORKeyStream(out, data)
    return out
}
```

## 八、Salsa20（流密码）

Salsa20 是 ChaCha20 的前身，使用相同的 uint32 内部结构。

### 库地址

`golang.org/x/crypto/salsa20`

### API 速查

```go
import "golang.org/x/crypto/salsa20"

// 核心函数
func XORKeyStream(out, in []byte, nonce []byte, key *[32]byte)
```

## 九、Feistel 网络

### 库地址

`github.com/cyrildever/feistel` v1.5.17（2026 年 3 月，MIT 许可证）

### API 速查

```go
import "github.com/cyrildever/feistel"

// 基础 Feistel 密码（纯 uint32 操作）
type Cipher struct{}
func NewCipher(key string, rounds int) *Cipher
func (c *Cipher) Encrypt(src string) (string, error)
func (c *Cipher) Decrypt(ciphered string) (string, error)

// 格式保留加密（FPE），支持数字加密
type FPECipher struct{}
func NewFPECipher(engine string, key string, rounds int) *FPECipher

// 对 uint64 数字加密，输出仍为 uint64
func (f *FPECipher) EncryptNumber(src uint64) (uint64, error)
func (f *FPECipher) DecryptNumber(ciphered uint64) (uint64, error)

// 对字符串加密，保留字符集
func (f *FPECipher) EncryptString(src string) (string, error)
func (f *FPECipher) DecryptString(ciphered string) (string, error)
```

### 加密 uint64 值

```go
import "github.com/cyrildever/feistel"

func ExampleEncryptNumber() {
    fpe, _ := feistel.NewFPECipher("ffx", "my-key", 10)

    plaintext := uint64(1234567890)
    ciphertext, _ := fpe.EncryptNumber(plaintext)
    decrypted, _ := fpe.DecryptNumber(ciphertext)

    fmt.Printf("%d -> %d -> %d", plaintext, ciphertext, decrypted)
    // 1234567890 -> (密文，仍为 uint64) -> 1234567890
}
```

## 十、格式保留加密（FPE）

### 10.1 capitalone/fpe（FF1）

#### 库地址

`github.com/capitalone/fpe`

#### API 速查

```go
import "github.com/capitalone/fpe/ff1"

// 构造 FF1 密码
func NewCipher(radix int, tweakLen int, key []byte, tweak []byte) (*FF1, error)

// 加解密字符串
func (f *FF1) Encrypt(plaintext string) (string, error)
func (f *FF1) Decrypt(ciphertext string) (string, error)
```

#### 用于 uint32 整数

```go
func EncryptFF1Uint32(ff1 *FF1, val uint32) (string, error) {
    return ff1.Encrypt(strconv.FormatUint(uint64(val), 10))
}
func DecryptFF1Uint32(ff1 *FF1, ciphertext string) (uint32, error) {
    plain, err := ff1.Decrypt(ciphertext)
    if err != nil {
        return 0, err
    }
    v, _ := strconv.ParseUint(plain, 10, 32)
    return uint32(v), nil
}
```

### 10.2 dusty-cjh/golang-fpe（FF3）

#### 库地址

`github.com/dusty-cjh/golang-fpe` v1.0.3（Apache-2.0 许可证）

#### API 速查

```go
import "github.com/dusty-cjh/golang-fpe/ff3"

func NewFF3Cipher(key, tweak string, radix int) (*FF3Cipher, error)
func (c *FF3Cipher) Encrypt(plaintext string) (string, error)
func (c *FF3Cipher) Decrypt(ciphertext string) (string, error)
```

#### 参数说明

| 参数 | 要求 |
|------|------|
| key | 128/192/256 位，Hex 编码字符串 |
| tweak | 7 字节（FF3-1）或 8 字节（FF3），Hex 编码 |
| radix | 基数：10（纯数字）、36（字母数字）、62（大小写+数字） |

### 10.3 jedisct1/go-fast（FAST）

#### 库地址

`github.com/jedisct1/go-fast` v0.2.0（2026 年 4 月，MIT 许可证）

#### API 速查

```go
import "github.com/jedisct1/go-fast"

// 类型
type Cipher struct{ /* 未导出 */ }
type Params struct {
    Radix    int     // 基数
    MinLen   int     // 最小长度
    MaxLen   int     // 最大长度，0 表示不限制
}

// 构造
func NewCipher(key []byte) (*Cipher, error)
func NewCipherFromParams(params *Params, key []byte) (*Cipher, error)

// 加解密（保留格式）
func (c *Cipher) Encrypt(data, tweak []byte) ([]byte, error)
func (c *Cipher) Decrypt(data, tweak []byte) ([]byte, error)
```

## 十一、go-cryptobin（综合密码库）

### 库地址

`github.com/deatil/go-cryptobin` v1.1.1013（Apache-2.0 许可证）

### 支持的所有 uint32 操作算法

| 算法 | 分组大小 | 操作单位 | go-cryptobin 方法 |
|------|----------|----------|-------------------|
| TEA | 64 位 | uint32 | `Tea(rounds)` |
| XTEA | 64 位 | uint32 | `Xtea()` |
| Blowfish | 64 位 | uint32 | `Blowfish()` |
| Twofish | 128 位 | uint32 | `Twofish()` |
| CAST5 | 64 位 | uint32 | `Cast5()` |
| ChaCha20 | 流密码 | uint32 | `Chacha20(counter)` |
| XTS（Any）| 128 位 | uint64 | `Xts(cipher, sectorNum)` |

### 统一 API 风格

```go
// 所有算法遵循相同调用链
result := crypto.
    FromString("data").                 // 输入
    SetKey("key").                      // 密钥
    SetIv("iv").                        // 初始向量
    Aes().Twofish().Blowfish().         // 选择算法（链式调用）
    ECB().CBC().CTR().GCM().            // 选择模式
    PKCS7Padding().                     // 选择填充
    Encrypt().                          // 加密动作
    ToBase64String()                    // 输出格式
```

## 十二、XTS 模式（磁盘加密）

### 库地址

`golang.org/x/crypto/xts`

### API 速查

```go
import "golang.org/x/crypto/xts"

type Cipher struct{ /* 未导出 */ }

// cipherFunc 是分组密码构造器（如 aes.NewCipher）
// key 长度是底层密码密钥的两倍
func NewCipher(cipherFunc func([]byte) (cipher.Block, error), key []byte) (*Cipher, error)

// sectorNum 是 uint64 扇区号，用作可调参数
func (c *Cipher) Encrypt(ciphertext, plaintext []byte, sectorNum uint64)
func (c *Cipher) Decrypt(plaintext, ciphertext []byte, sectorNum uint64)
```

## 算法对比汇总

| 算法 | 库路径 | 分组大小 | 操作单位 | 保留格式 | 适用场景 |
|------|--------|----------|----------|----------|----------|
| XXTEA | `twpayne/go-xxtea` | 64 位 | uint32 | 否 | uint32/uint64 加密 |
| TEA | `deatil/go-cryptobin` | 64 位 | uint32 | 否 | 轻量级加密 |
| XTEA | `deatil/go-cryptobin` | 64 位 | uint32 | 否 | TEA 改进版 |
| Blowfish | `x/crypto/blowfish` | 64 位 | uint32 | 否 | 遗留系统兼容 |
| Twofish | `x/crypto/twofish` | 128 位 | uint32 | 否 | 遗留系统兼容 |
| CAST5 | `x/crypto/cast5` | 64 位 | uint32 | 否 | 遗留系统兼容 |
| ChaCha20 | `x/crypto/chacha20` | 流 | uint32 / uint64 counter | 否 | 高性能流加密 |
| Feistel | `cyrildever/feistel` | 可变 | uint64 | 是 | 整数 ID 混淆 |
| FPE-FF1 | `capitalone/fpe` | 可变 | 字符串 | 是 | 数据脱敏 |
| FPE-FF3 | `dusty-cjh/golang-fpe` | 可变 | 字符串 | 是 | 数据脱敏 |
| FAST | `jedisct1/go-fast` | 可变 | 字节 | 是 | 令牌化 |
| XTS | `x/crypto/xts` | 128 位 | uint64 sector | 否 | 磁盘加密 |

## 选择建议

**加密 uint32 或 uint64 整数值：**
- 需要可逆加密，且保留数值格式 → Feistel 的 `EncryptNumber`
- 需要可逆加密，不要求保留格式 → XXTEA（操作 `[]uint32`）
- 仅需要隐藏真实值，不要求可逆 → ChaCha20 `XORKeyStream`

**加密字符串但保留格式：**
- 纯数字串 → `capitalone/fpe`（FF1）或 `dusty-cjh/golang-fpe`（FF3）
- 字母数字串 → 同上，设 radix=36 或 radix=62

**高性能流加密：**
- ChaCha20（支持 `SetCounter` 实现随机访问）
- Salsa20

**综合密码需求：**
- `deatil/go-cryptobin` 覆盖了本文大部分算法

## 参考链接

### 第三方库

- [go-xxtea](https://github.com/twpayne/go-xxtea) — XXTEA block cipher
- [go-cryptobin](https://github.com/deatil/go-cryptobin) — 综合密码库
- [dongle](https://github.com/golang-module/dongle) — 编码解码与加密解密
- [feistel](https://github.com/cyrildever/feistel) — Feistel cipher for FPE
- [capitalone/fpe](https://github.com/capitalone/fpe) — FF1 format-preserving encryption
- [golang-fpe](https://github.com/dusty-cjh/golang-fpe) — FF3 format-preserving encryption
- [go-fast](https://github.com/jedisct1/go-fast) — FAST tokenization

### 官方扩展库

- [golang.org/x/crypto/blowfish](https://pkg.go.dev/golang.org/x/crypto/blowfish) — Blowfish cipher
- [golang.org/x/crypto/twofish](https://pkg.go.dev/golang.org/x/crypto/twofish) — Twofish cipher
- [golang.org/x/crypto/cast5](https://pkg.go.dev/golang.org/x/crypto/cast5) — CAST5 cipher
- [golang.org/x/crypto/chacha20](https://pkg.go.dev/golang.org/x/crypto/chacha20) — ChaCha20 stream cipher
- [golang.org/x/crypto/salsa20](https://pkg.go.dev/golang.org/x/crypto/salsa20) — Salsa20 stream cipher
- [golang.org/x/crypto/xts](https://pkg.go.dev/golang.org/x/crypto/xts) — XTS disk encryption mode
