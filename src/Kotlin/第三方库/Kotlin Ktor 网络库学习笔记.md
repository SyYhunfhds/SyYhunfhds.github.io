---
title: Kotlin Ktor 网络库学习笔记
date: 2026-03-14
---
[[toc]]
***
## http客户端 (Ktor Client)
### 依赖配置
```properties
# gradle.properties
ktor_version=3.4.1
```

```kotlin
// build.gradle.kts
dependencies {  
    // Ktor Client 核心  
    implementation("io.ktor:ktor-client-core:$ktor_version")  
    // 选择引擎（推荐 CIO）  
    implementation("io.ktor:ktor-client-cio:$ktor_version")  
	  
	  // 协程核心库 (以防万一)
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")  
}
```

### 实战
#### AoC 爬虫
**参考链接**
- [alexchao26的AoC Go仓库部分源代码](https://github.com/alexchao26/advent-of-code-go/blob/main/scripts/aoc/aoc.go)

***
# 页面笔记