---
title: Golang 对称加密库完整指南
date: 2026-05-29
footer: Trae编辑
---

## 目录

1. [概述与基础](#概述与基础)
2. [官方标准库详解](#官方标准库详解)
3. [golang.org/x/crypto 扩展库](#golanorgxcrypto-扩展库)
4. [第三方加密库](#第三方加密库)
5. [工作模式深度解析](#工作模式深度解析)
6. [实际应用场景](#实际应用场景)
7. [安全最佳实践](#安全最佳实践)
8. [性能对比与选型](#性能对比与选型)
9. [完整示例代码](#完整示例代码)

---

## 概述与基础

### 对称加密简介

对称加密是指加密和解密使用相同密钥的加密方式，是现代密码学中最古老、最常用的技术之一。相比非对称加密，对称加密具有以下特点：

**优势：**
- 加解密速度快
- 计算资源消耗低
- 适合大数据量加密

**劣势：**
- 密钥分发困难
- 密钥管理复杂

### Go 加密库生态系统

Go 语言的加密库分为三个层次：

| 层次 | 库类型 | 代表库 | 适用场景 |
|------|--------|-------|---------|
| 官方标准库 | `crypto/*` | `crypto/aes`、`crypto/cipher` | 基础加密需求 |
| 官方扩展库 | `golang.org/x/crypto` | `chacha20poly1305`、`scrypt` | 现代加密需求 |
| 第三方库 | GitHub 社区 | `tink-go`、`libsodium` | 高级应用 |

### 算法分类与选择指南

#### 分组密码 vs 流密码

**分组密码（Block Cipher）：**
- AES（推荐）
- DES（遗留）
- ChaCha20（在特定模式下）

**流密码（Stream Cipher）：**
- ChaCha20
- Salsa20

#### 认证加密 vs 普通加密

**普通加密（仅保密性）：**
- AES-CBC
- AES-CTR

**认证加密（保密性 + 完整性）：**
- AES-GCM（推荐）
- ChaCha20-Poly1305（推荐）

::: tip 推荐选择
现代应用应优先选择 **AES-GCM** 或 **ChaCha20-Poly1305**，两者都是经过广泛验证的认证加密算法。
:::

---

## 官方标准库详解

### crypto/aes 详解

#### AES 算法概述

AES（Advanced Encryption Standard，高级加密标准）是一种分组密码算法，具有以下特性：

| 参数 | 值 |
|------|-----|
| 分组长度 | 128 位（16 字节） |
| 密钥长度 | 128/192/256 位 |
| 轮数 | 10/12/14 |

**核心函数：**
```go
func NewCipher(key []byte) (cipher.Block, error)
```

#### AES-GCM 认证加密（推荐）

AES-GCM 是目前最推荐的加密模式，提供认证加密（AEAD）：

```go
package main

import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "fmt"
    "io"
)

func main() {
    // 生成 256 位密钥
    key := make([]byte, 32)
    if _, err := io.ReadFull(rand.Reader, key); err != nil {
        panic(err)
    }

    plaintext := []byte("sensitive data")

    // 创建 AES 块
    block, err := aes.NewCipher(key)
    if err != nil {
        panic(err)
    }

    // 创建 GCM 模式
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        panic(err)
    }

    // 生成随机 nonce
    nonce := make([]byte, gcm.NonceSize())
    if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
        panic(err)
    }

    // 加密（Seal 会自动将 nonce 追加到密文前）
    ciphertext := gcm.Seal(nil, nonce, plaintext, nil)
    fmt.Printf("Ciphertext: %x\n", ciphertext)

    // 解密
    nonceSize := gcm.NonceSize()
    nonce, ciphertext = ciphertext[:nonceSize], ciphertext[nonceSize:]
    decrypted, err := gcm.Open(nil, nonce, ciphertext, nil)
    if err != nil {
        panic(err)
    }
    fmt.Printf("Decrypted: %s\n", decrypted)
}
```

#### AES-CBC 分组加密

CBC 模式需要手动处理填充：

```go
import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "bytes"
    "io"
)

func pkcs7Pad(data []byte, blockSize int) []byte {
    padding := blockSize - len(data)%blockSize
    return append(data, bytes.Repeat([]byte{byte(padding)}, padding)...)
}

func pkcs7Unpad(data []byte) []byte {
    padding := int(data[len(data)-1])
    return data[:len(data)-padding]
}

func encryptCBC(plaintext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }

    // PKCS7 填充
    padded := pkcs7Pad(plaintext, aes.BlockSize)
    ciphertext := make([]byte, aes.BlockSize+len(padded))

    // 生成随机 IV
    iv := ciphertext[:aes.BlockSize]
    if _, err := io.ReadFull(rand.Reader, iv); err != nil {
        return nil, err
    }

    // CBC 加密
    mode := cipher.NewCBCEncrypter(block, iv)
    mode.CryptBlocks(ciphertext[aes.BlockSize:], padded)

    return ciphertext, nil
}

func decryptCBC(ciphertext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }

    if len(ciphertext) < aes.BlockSize {
        return nil, fmt.Errorf("ciphertext too short")
    }

    // 提取 IV
    iv := ciphertext[:aes.BlockSize]
    ciphertext = ciphertext[aes.BlockSize:]

    // CBC 解密
    mode := cipher.NewCBCDecrypter(block, iv)
    mode.CryptBlocks(ciphertext, ciphertext)

    // 去除填充
    return pkcs7Unpad(ciphertext)
}
```

#### AES-CTR 流加密模式

CTR 模式将分组密码转为流密码：

```go
func encryptCTR(plaintext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }

    // 生成随机计数器 nonce
    nonce := make([]byte, aes.BlockSize)
    if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
        return nil, err
    }

    // 创建 CTR 模式
    stream := cipher.NewCTR(block, nonce)

    // 加密
    ciphertext := make([]byte, len(plaintext))
    stream.XORKeyStream(ciphertext, plaintext)

    // 追加 nonce 到密文前
    return append(nonce, ciphertext...), nil
}

func decryptCTR(ciphertext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }

    nonce := ciphertext[:aes.BlockSize]
    ciphertext = ciphertext[aes.BlockSize:]

    stream := cipher.NewCTR(block, nonce)
    plaintext := make([]byte, len(ciphertext))
    stream.XORKeyStream(plaintext, ciphertext)

    return plaintext, nil
}
```

### crypto/cipher 详解

#### 核心接口

**Block 接口：**
```go
type Block interface {
    BlockSize() int
    Encrypt(dst, src []byte)
    Decrypt(dst, src []byte)
}
```

**AEAD 接口（认证加密）：**
```go
type AEAD interface {
    NonceSize() int
    Overhead() int
    Seal(dst, nonce, plaintext, additionalData []byte) []byte
    Open(dst, nonce, ciphertext, additionalData []byte) ([]byte, error)
}
```

**Stream 接口：**
```go
type Stream interface {
    XORKeyStream(dst, src []byte)
}
```

### crypto/des 与 3DES

DES 由于密钥长度过短（56 位），已不推荐使用。3DES 通过三重加密增强安全性，但效率较低：

```go
import "crypto/des"

func tripleDESEncrypt(plaintext, key []byte) ([]byte, error) {
    // 3DES 需要 24 字节密钥
    if len(key) != 24 {
        return nil, fmt.Errorf("3DES key must be 24 bytes")
    }

    block, err := des.NewTripleDESCipher(key)
    if err != nil {
        return nil, err
    }

    // CBC 模式加密
    ciphertext := make([]byte, des.BlockSize+len(plaintext))
    iv := ciphertext[:des.BlockSize]
    if _, err := io.ReadFull(rand.Reader, iv); err != nil {
        return nil, err
    }

    mode := cipher.NewCBCEncrypter(block, iv)
    mode.CryptBlocks(ciphertext[des.BlockSize:], plaintext)

    return ciphertext, nil
}
```

::: warning 安全警告
3DES 已被 NIST 废弃，仅用于遗留系统兼容。新系统应使用 AES 或 ChaCha20。
:::

### crypto/hmac 消息认证

HMAC（Hash-based Message Authentication Code）用于消息完整性验证：

```go
import (
    "crypto/hmac"
    "crypto/sha256"
)

func computeHMAC(message, key []byte) []byte {
    h := hmac.New(sha256.New, key)
    h.Write(message)
    return h.Sum(nil)
}

func verifyHMAC(message, key, expectedMAC []byte) bool {
    mac := computeHMAC(message, key)
    return hmac.Equal(mac, expectedMAC)
}
```

---

## golang.org/x/crypto 扩展库

### 安装

```bash
go get golang.org/x/crypto
```

### chacha20poly1305 AEAD

ChaCha20-Poly1305 是一种现代认证加密算法，特别适合移动设备和没有硬件 AES 加速的环境：

#### 安装与导入

```bash
go get golang.org/x/crypto/chacha20poly1305
```

#### 使用示例

```go
package main

import (
    "crypto/rand"
    "fmt"
    "io"
    "golang.org/x/crypto/chacha20poly1305"
)

func main() {
    // 生成密钥
    key := make([]byte, chacha20poly1305.KeySize)
    if _, err := io.ReadFull(rand.Reader, key); err != nil {
        panic(err)
    }

    // 创建 AEAD
    aead, err := chacha20poly1305.New(key)
    if err != nil {
        panic(err)
    }

    // 数据准备
    plaintext := []byte("secret message")
    nonce := make([]byte, aead.NonceSize(), aead.NonceSize()+len(plaintext)+aead.Overhead())
    if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
        panic(err)
    }

    // 加密
    ciphertext := aead.Seal(nonce, nonce, plaintext, nil)
    fmt.Printf("Ciphertext: %x\n", ciphertext)

    // 解密
    decrypted, err := aead.Open(nil, nonce, ciphertext[aead.NonceSize():], nil)
    if err != nil {
        panic(err)
    }
    fmt.Printf("Decrypted: %s\n", decrypted)
}
```

#### XChaCha20-Poly1305 扩展

XChaCha20-Poly1305 使用更大的 nonce（24 字节），简化密钥管理：

```go
func xchacha20Example() {
    key := make([]byte, chacha20poly1305.KeySize)
    rand.Read(key)

    // XChaCha20 版本
    aead, err := chacha20poly1305.NewX(key)
    if err != nil {
        panic(err)
    }

    // 使用更大的 nonce
    nonce := make([]byte, chacha20poly1305.NonceSizeX)
    rand.Read(nonce)

    plaintext := []byte("message")
    ciphertext := aead.Seal(nil, nonce, plaintext, nil)
    fmt.Printf("XChaCha20 Ciphertext: %x\n", ciphertext)
}
```

#### 与 AES-GCM 对比

| 特性 | AES-GCM | ChaCha20-Poly1305 |
|------|---------|-------------------|
| 安全性 | 高 | 高 |
| 性能（软件） | 中等 | 高 |
| 性能（硬件） | 高 | 中等 |
| 适用场景 | 通用 | 移动设备、无 AES-NI |

::: tip 推荐
- 有 AES 硬件加速：使用 AES-GCM
- 移动设备或无硬件加速：使用 ChaCha20-Poly1305
:::

### chacha20 流加密

ChaCha20 是流密码，需要配合 Poly1305 才能实现认证加密：

```go
package main

import (
    "crypto/rand"
    "fmt"
    "io"
    "golang.org/x/crypto/chacha20"
)

func main() {
    // 生成密钥和 nonce
    key := make([]byte, chacha20.KeySize)
    nonce := make([]byte, chacha20.NonceSize)
    if _, err := io.ReadFull(rand.Reader, key); err != nil {
        panic(err)
    }
    if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
        panic(err)
    }

    // 创建 ChaCha20 密码器
    cipher, err := chacha20.NewUnauthenticatedCipher(key, nonce)
    if err != nil {
        panic(err)
    }

    // 加密/解密
    plaintext := []byte("Hello, ChaCha20!")
    ciphertext := make([]byte, len(plaintext))
    cipher.XORKeyStream(ciphertext, plaintext)

    fmt.Printf("Original: %s\n", plaintext)
    fmt.Printf("Encrypted: %x\n", ciphertext)

    // 解密（重置计数器）
    cipher.SetCounter(0)
    decrypted := make([]byte, len(ciphertext))
    cipher.XORKeyStream(decrypted, ciphertext)
    fmt.Printf("Decrypted: %s\n", decrypted)
}
```

### salsa20 流加密

Salsa20 是 ChaCha20 的前身，同样由 Daniel J. Bernstein 设计：

```go
import "golang.org/x/crypto/salsa20"

func salsa20Example() {
    key := make([]byte, salsa20.KeySize)  // 32 字节
    nonce := make([]byte, salsa20.NonceSize)  // 8 字节
    rand.Read(key)
    rand.Read(nonce)

    plaintext := []byte("message")
    ciphertext := make([]byte, len(plaintext))
    salsa20.XORKeyStream(ciphertext, plaintext, nonce, key)

    // 解密
    decrypted := make([]byte, len(ciphertext))
    salsa20.XORKeyStream(decrypted, ciphertext, nonce, key)
}
```

### 密钥派生函数

#### PBKDF2

```go
import (
    "crypto/rand"
    "crypto/sha256"
    "golang.org/x/crypto/pbkdf2"
)

func deriveKeyPBKDF2(password, salt []byte) []byte {
    return pbkdf2.Key(password, salt, 4096, 32, sha256.New)
}

// 使用示例
func pbkdf2Example() {
    password := []byte("user password")
    salt := make([]byte, 16)
    rand.Read(salt)

    key := deriveKeyPBKDF2(password, salt)
    fmt.Printf("Derived key: %x\n", key)
}
```

#### Scrypt

Scrypt 是内存硬化的密钥派生函数，抗 GPU 攻击：

```go
import "golang.org/x/crypto/scrypt"

func deriveKeyScrypt(password, salt []byte) ([]byte, error) {
    // N: CPU/内存成本参数
    // r: 块大小
    // p: 并行度
    // dkLen: 输出密钥长度
    return scrypt.Key(password, salt, 1<<15, 8, 1, 32)
}

// 使用示例
func scryptExample() {
    password := []byte("secure password")
    salt := make([]byte, 16)
    rand.Read(salt)

    key, err := deriveKeyScrypt(password, salt)
    if err != nil {
        panic(err)
    }
    fmt.Printf("Scrypt key: %x\n", key)
}
```

#### Argon2

Argon2 是 Password Hashing Competition 的冠军算法：

```go
import "golang.org/x/crypto/argon2"

func deriveKeyArgon2(password, salt []byte) []byte {
    // time: 迭代次数
    // memory: 内存使用量（KB）
    // threads: 并行度
    return argon2.IDKey(password, salt, 1, 64*1024, 4, 32)
}

// 使用示例
func argon2Example() {
    password := []byte("password")
    salt := make([]byte, 16)
    rand.Read(salt)

    key := deriveKeyArgon2(password, salt)
    fmt.Printf("Argon2 key: %x\n", key)
}
```

---

## 第三方加密库

### Google Tink (tink-go)

Google Tink 是一个提供安全、易用加密 API 的库：

#### 安装

```bash
go get github.com/tink-crypto/tink-go/v2
```

#### 基本使用

```go
package main

import (
    "fmt"
    "github.com/tink-crypto/tink-go/v2/aead"
    "github.com/tink-crypto/tink-go/v2/keyset"
)

func main() {
    // 创建密钥集
    handle, err := keyset.New(aead.AES256GCMKeyTemplate())
    if err != nil {
        panic(err)
    }

    // 获取 AEAD 实例
    a, err := aead.New(handle)
    if err != nil {
        panic(err)
    }

    // 加密
    plaintext := []byte("message")
    ciphertext, err := a.Encrypt(plaintext, nil)
    if err != nil {
        panic(err)
    }

    // 解密
    decrypted, err := a.Decrypt(ciphertext, nil)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Decrypted: %s\n", decrypted)
}
```

#### Tink 的优势

- 自动防误用设计
- 密钥轮换支持
- 审计日志
- 经过安全审查

### libsodium (通过 cgo)

libsodium 是成熟的跨语言加密库，提供 Go 绑定：

#### 安装

libsodium 需要先安装 C 库，然后使用 Go 绑定：

```bash
# Ubuntu/Debian
sudo apt-get install libsodium-dev

# macOS
brew install libsodium

# Go 绑定
go get github.com/GoK2/go-sodium
```

#### 使用示例

```go
package main

import (
    "fmt"
    "github.com/GoK2/go-sodium"
)

func main() {
    sodium.Init()

    // 生成密钥
    key := sodium.MakeKey()
    fmt.Printf("Key length: %d\n", len(key))

    // 加密
    nonce := sodium.MakeNonce()
    plaintext := []byte("secret message")

    ciphertext := sodium.SecretBoxEasy(plaintext, nonce, key)
    fmt.Printf("Ciphertext: %x\n", ciphertext)

    // 解密
    decrypted := sodium.SecretBoxOpenEasy(ciphertext, nonce, key)
    fmt.Printf("Decrypted: %s\n", decrypted)
}
```

### 其他第三方库

#### starcrypto

提供统一的加密接口和多种算法支持：

```go
import "b612.me/starcrypto"

func starcryptoExample() {
    key := []byte("32-byte-secret-key-here!!!!") // 32 bytes
    plaintext := []byte("sensitive data")

    // 统一接口加密
    ciphertext, err := starcrypto.AESGCMEncrypt(plaintext, key)
    if err != nil {
        panic(err)
    }

    // 统一接口解密
    decrypted, err := starcrypto.AESGCMDecrypt(ciphertext, key)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Decrypted: %s\n", decrypted)
}
```

#### kryptograf

提供密钥管理和证书辅助功能：

```go
import "pkt.systems/kryptograf"

func kryptografExample() {
    // 从密码派生密钥
    passphrase := []byte("user passphrase")
    params := kryptograf.GeneratePBKDF2Params()

    rootKey, err := kryptograf.DeriveKeyFromPassphrase(passphrase, params)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Derived root key: %x\n", rootKey)
}
```

---

## 工作模式深度解析

### ECB 模式（不推荐）

ECB（Electronic Codebook）模式对每个明文块独立加密，相同明文产生相同密文，存在模式泄露风险：

::: danger 警告
**永远不要在生产环境中使用 ECB 模式！** 相同明文块会产生相同的密文块，攻击者可以识别加密模式。
:::

```go
// ❌ 危险：不安全
func insecureECB(plaintext, key []byte) []byte {
    block, _ := aes.NewCipher(key)
    ciphertext := make([]byte, len(plaintext))
    for i := 0; i < len(plaintext); i += aes.BlockSize {
        block.Encrypt(ciphertext[i:i+aes.BlockSize], plaintext[i:i+aes.BlockSize])
    }
    return ciphertext
}
```

### CBC 模式

CBC（Cipher Block Chaining）模式通过链式结构连接密文块：

**特点：**
- 需要填充
- 需要唯一的 IV
- 无法并行化加密（可以并行化解密）

### CTR 模式

CTR（Counter）模式将密码转为流密码：

**特点：**
- 不需要填充
- 可以并行加密和解密
- 需要唯一的计数器 nonce

### GCM 模式

GCM（Galois/Counter Mode）是最流行的认证加密模式：

**特点：**
- 同时提供加密和认证
- 支持关联数据（AEAD）
- 并行化友好
- 推荐用于几乎所有场景

### XTS 模式

XTS 模式专为磁盘加密设计：

**特点：**
- 支持可变长度数据
- 不支持关联数据
- 常用于全磁盘加密（FDE）

::: info 适用场景
- **GCM**：网络通信、API 加密
- **CBC**：遗留系统兼容
- **CTR**：流式数据加密
- **XTS**：磁盘/文件加密
:::

---

## 实际应用场景

### 文件加密

```go
package crypto

import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "io"
    "os"
)

func EncryptFile(src, dst string, key []byte) error {
    // 打开源文件
    infile, err := os.Open(src)
    if err != nil {
        return err
    }
    defer infile.Close()

    // 创建目标文件
    outfile, err := os.Create(dst)
    if err != nil {
        return err
    }
    defer outfile.Close()

    // 加密流
    block, _ := aes.NewCipher(key)
    gcm, _ := cipher.NewGCM(block)
    nonce := make([]byte, gcm.NonceSize())
    rand.Read(nonce)

    writer := &gcmWriter{
        gcm:   gcm,
        nonce: nonce,
        out:   outfile,
    }

    // 写入 nonce
    if _, err := writer.Write(nonce); err != nil {
        return err
    }

    // 加密写入
    _, err = io.Copy(writer, infile)
    return err
}

type gcmWriter struct {
    gcm   cipher.AEAD
    nonce []byte
    out   *os.File
}

func (w *gcmWriter) Write(p []byte) (int, error) {
    ciphertext := w.gcm.Seal(nil, w.nonce, p, nil)
    _, err := w.out.Write(ciphertext)
    if err != nil {
        return 0, err
    }
    return len(p), nil
}
```

### 数据库字段加密

```go
package dbcrypto

type EncryptedField struct {
    Ciphertext []byte
    Nonce      []byte
    Algorithm  string
}

func EncryptField(plaintext []byte, key []byte) (*EncryptedField, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }

    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }

    nonce := make([]byte, gcm.NonceSize())
    rand.Read(nonce)

    ciphertext := gcm.Seal(nil, nonce, plaintext, nil)

    return &EncryptedField{
        Ciphertext: ciphertext,
        Nonce:      nonce,
        Algorithm:  "AES-256-GCM",
    }, nil
}

func (e *EncryptedField) Decrypt(key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }

    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }

    return gcm.Open(nil, e.Nonce, e.Ciphertext, nil)
}
```

### API 请求加密

```go
package apicrypto

import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "encoding/base64"
    "time"
)

type APIEncryption struct {
    key []byte
}

func NewAPIEncryption(key []byte) *APIEncryption {
    return &APIEncryption{key: key}
}

type EncryptedRequest struct {
    Data      string `json:"data"`
    Timestamp int64  `json:"timestamp"`
    Nonce     string `json:"nonce"`
}

func (e *APIEncryption) EncryptRequest(payload []byte) (*EncryptedRequest, error) {
    block, err := aes.NewCipher(e.key)
    if err != nil {
        return nil, err
    }

    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }

    nonce := make([]byte, gcm.NonceSize())
    rand.Read(nonce)

    ciphertext := gcm.Seal(nil, nonce, payload, nil)

    return &EncryptedRequest{
        Data:      base64.StdEncoding.EncodeToString(ciphertext),
        Timestamp: time.Now().Unix(),
        Nonce:     base64.StdEncoding.EncodeToString(nonce),
    }, nil
}

func (e *APIEncryption) DecryptRequest(req *EncryptedRequest) ([]byte, error) {
    ciphertext, _ := base64.StdEncoding.DecodeString(req.Data)
    nonce, _ := base64.StdEncoding.DecodeString(req.Nonce)

    block, err := aes.NewCipher(e.key)
    if err != nil {
        return nil, err
    }

    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }

    return gcm.Open(nil, nonce, ciphertext, nil)
}
```

---

## 安全最佳实践

### 密钥生成与管理

**必须使用密码学安全随机数：**
```go
// ✅ 正确
key := make([]byte, 32)
rand.Read(key)

// ❌ 错误
rand.Seed(time.Now().UnixNano())  // 不安全！
```

**密钥存储原则：**
- 不要硬编码密钥
- 使用密钥管理服务（KMS）
- 定期轮换密钥

### IV/Nonce 管理

**IV/Nonce 要求：**
- GCM/ChaCha20: 12-24 字节随机
- CBC: 16 字节随机
- CTR: 唯一且不可预测

```go
func generateNonce(size int) ([]byte, error) {
    nonce := make([]byte, size)
    if _, err := rand.Read(nonce); err != nil {
        return nil, err
    }
    return nonce, nil
}
```

### 认证加密优先

**选择认证加密而非普通加密：**

| 场景 | 推荐算法 |
|------|---------|
| 网络通信 | AES-GCM / ChaCha20-Poly1305 |
| 文件加密 | AES-GCM |
| 数据库字段 | AES-GCM |
| 磁盘加密 | XTS-AES / AES-GCM-EAX |

::: danger 禁止使用
- ECB 模式
- 无认证的 CBC/CTR
- MD5 用于安全目的
- SHA1 用于新系统
:::

### 密钥轮换策略

```go
type KeyManager struct {
    currentKey  []byte
    previousKey []byte
    version     int
}

func (km *KeyManager) RotateKey() error {
    newKey := make([]byte, 32)
    if _, err := rand.Read(newKey); err != nil {
        return err
    }

    km.previousKey = km.currentKey
    km.currentKey = newKey
    km.version++

    return nil
}

func (km *KeyManager) DecryptWithFallback(ciphertext, nonce []byte) ([]byte, error) {
    // 尝试当前密钥
    plaintext, err := km.decrypt(ciphertext, nonce, km.currentKey)
    if err == nil {
        return plaintext, nil
    }

    // 如果失败，尝试旧密钥
    if km.previousKey != nil {
        return km.decrypt(ciphertext, nonce, km.previousKey)
    }

    return nil, err
}
```

---

## 性能对比与选型

### 算法性能基准

| 算法 | 吞吐量（软件） | 吞吐量（硬件） | 适用场景 |
|------|--------------|--------------|---------|
| AES-128-GCM | ~500 MB/s | ~2 GB/s | 通用 |
| AES-256-GCM | ~400 MB/s | ~1.5 GB/s | 高安全需求 |
| ChaCha20-Poly1305 | ~1 GB/s | N/A | 移动设备 |
| XChaCha20-Poly1305 | ~800 MB/s | N/A | 简化 nonce 管理 |

### 场景化推荐

**桌面/服务器应用：**
```go
// 有 AES-NI 硬件支持
aead, _ := cipher.NewGCM(block)  // AES-GCM 最佳
```

**移动设备/无硬件加速：**
```go
// ChaCha20-Poly1305 性能更优
aead, _ := chacha20poly1305.New(key)
```

**遗留系统兼容：**
```go
// 必须使用 DES/3DES 时
block, _ := des.NewTripleDESCipher(key)
```

---

## 完整示例代码

### 统一的加密服务

```go
package crypto

import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "crypto/sha256"
    "encoding/base64"
    "errors"
    "golang.org/x/crypto/chacha20poly1305"
)

type CipherMode string

const (
    AES256GCM        CipherMode = "AES-256-GCM"
    XChaCha20Poly1305 CipherMode = "XChaCha20-Poly1305"
)

type CryptoService struct {
    key   []byte
    mode  CipherMode
    aead  cipher.AEAD
}

func NewCryptoService(key []byte, mode CipherMode) (*CryptoService, error) {
    if len(key) != 32 {
        return nil, errors.New("key must be 32 bytes")
    }

    cs := &CryptoService{key: key, mode: mode}

    switch mode {
    case AES256GCM:
        block, err := aes.NewCipher(key)
        if err != nil {
            return nil, err
        }
        gcm, err := cipher.NewGCM(block)
        if err != nil {
            return nil, err
        }
        cs.aead = gcm

    case XChaCha20Poly1305:
        aead, err := chacha20poly1305.NewX(key)
        if err != nil {
            return nil, err
        }
        cs.aead = aead

    default:
        return nil, errors.New("unsupported cipher mode")
    }

    return cs, nil
}

func (cs *CryptoService) Encrypt(plaintext []byte) (string, error) {
    nonce := make([]byte, cs.aead.NonceSize())
    if _, err := rand.Read(nonce); err != nil {
        return "", err
    }

    ciphertext := cs.aead.Seal(nil, nonce, plaintext, nil)

    // 组合 nonce + ciphertext
    combined := append(nonce, ciphertext...)

    return base64.StdEncoding.EncodeToString(combined), nil
}

func (cs *CryptoService) Decrypt(encrypted string) ([]byte, error) {
    combined, err := base64.StdEncoding.DecodeString(encrypted)
    if err != nil {
        return nil, err
    }

    nonceSize := cs.aead.NonceSize()
    if len(combined) < nonceSize {
        return nil, errors.New("invalid ciphertext")
    }

    nonce := combined[:nonceSize]
    ciphertext := combined[nonceSize:]

    return cs.aead.Open(nil, nonce, ciphertext, nil)
}

func DeriveKey(password, salt []byte) []byte {
    return pbkdf2.Key(password, salt, 4096, 32, sha256.New)
}
```

### 命令行加密工具

```go
package main

import (
    "bufio"
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "fmt"
    "io"
    "os"
)

func main() {
    if len(os.Args) != 4 {
        fmt.Println("Usage: encrypt <encrypt|decrypt> <keyfile> <inputfile>")
        os.Exit(1)
    }

    mode := os.Args[1]
    keyFile := os.Args[2]
    inputFile := os.Args[3]

    // 读取密钥
    key, err := os.ReadFile(keyFile)
    if err != nil {
        panic(err)
    }
    if len(key) != 32 {
        fmt.Println("Key must be 32 bytes")
        os.Exit(1)
    }

    // 读取输入
    plaintext, err := io.ReadAll(os.Stdin)
    if err != nil {
        panic(err)
    }

    switch mode {
    case "encrypt":
        encrypted := encrypt(plaintext, key)
        fmt.Print(base64.StdEncoding.EncodeToString(encrypted))

    case "decrypt":
        ciphertext, _ := base64.StdEncoding.DecodeString(string(plaintext))
        decrypted := decrypt(ciphertext, key)
        os.Stdout.Write(decrypted)

    default:
        fmt.Println("Invalid mode. Use 'encrypt' or 'decrypt'")
        os.Exit(1)
    }
}

func encrypt(plaintext, key []byte) []byte {
    block, _ := aes.NewCipher(key)
    gcm, _ := cipher.NewGCM(block)
    nonce := make([]byte, gcm.NonceSize())
    rand.Read(nonce)
    return append(nonce, gcm.Seal(nil, nonce, plaintext, nil)...)
}

func decrypt(ciphertext, key []byte) []byte {
    block, _ := aes.NewCipher(key)
    gcm, _ := cipher.NewGCM(block)
    nonceSize := gcm.NonceSize()
    nonce := ciphertext[:nonceSize]
    decrypted, _ := gcm.Open(nil, nonce, ciphertext[nonceSize:], nil)
    return decrypted
}
```

---

## 总结

Go 语言提供了完整对称加密解决方案：

1. **官方标准库**：`crypto/aes`、`crypto/cipher` 等
2. **扩展库**：`golang.org/x/crypto` 提供 ChaCha20、密钥派生等
3. **第三方库**：Google Tink、libsodium 等高级库

**关键建议：**
- 优先使用 **认证加密**（AES-GCM、ChaCha20-Poly1305）
- 使用 **密码学安全随机数**
- 实施 **密钥轮换策略**
- 避免 **ECB 模式**
- 参考 **安全最佳实践**

通过合理选择和使用加密库，可以构建安全可靠的加密系统。

### 进一步阅读

- [Go crypto库详解](../标准库/Go%20crypto库详解.md)
- [Go HashiCorp Vault 库使用指南](./Go%20HashiCorp%20Vault%20库使用指南.md)
- [Go Argon2 密码哈希库使用指南](./Go%20Argon2%20密码哈希库使用指南.md)
