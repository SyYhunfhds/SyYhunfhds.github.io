---
title: Kotlin 时间库详解
date: 2026-03-15
footer: Trae编辑
---


## 目录

1. [时间库概述](#时间库概述)
2. [Kotlin 标准库时间 API](#kotlin-标准库时间-api)
3. [kotlinx-datetime 库](#kotlinx-datetime-库)
4. [核心类详解](#核心类详解)
5. [时间格式化与解析](#时间格式化与解析)
6. [时间计算与操作](#时间计算与操作)
7. [时区处理](#时区处理)
8. [Bad Practice](#bad-practice)
9. [最佳实践](#最佳实践)
10. [第三方时间处理库](#第三方时间处理库)

## 时间库概述

Kotlin 提供了多种处理日期和时间的方案：

- **Kotlin 标准库**：提供基本的时间相关扩展函数
- **java.time (Java 8+)**：Java 标准时间 API，Kotlin 完全兼容
- **kotlinx-datetime**：Kotlin 官方多平台时间库
- **第三方库**：如 Joda-Time、ThreeTenABP 等

**选择建议**：
- 纯 JVM 项目：使用 `java.time` 或 `kotlinx-datetime`
- 多平台项目（KMP）：使用 `kotlinx-datetime`
- Android 项目：使用 `kotlinx-datetime` 或 `java.time`（API 26+）

## Kotlin 标准库时间 API

### 1. 基本时间操作

```kotlin
import kotlin.time.*

fun basicTimeOperations() {
    // 测量代码执行时间
    val timeTaken = measureTime {
        // 模拟耗时操作
        Thread.sleep(100)
    }
    println("耗时: $timeTaken")  // 输出: 耗时: 100ms
    
    // 带返回值的测量
    val (value, duration) = measureTimedValue {
        Thread.sleep(50)
        "结果"
    }
    println("结果: $value, 耗时: $duration")
}
```

### 2. Duration 类型

```kotlin
import kotlin.time.Duration
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.seconds
import kotlin.time.Duration.Companion.minutes
import kotlin.time.Duration.Companion.hours
import kotlin.time.Duration.Companion.days

fun durationExamples() {
    // 创建 Duration
    val duration1 = 1000.milliseconds
    val duration2 = 5.seconds
    val duration3 = 10.minutes
    val duration4 = 2.hours
    val duration5 = 1.days
    
    // Duration 运算
    val total = duration2 + duration3  // 5秒 + 10分钟
    val diff = duration3 - duration2   // 10分钟 - 5秒
    val multiplied = duration2 * 3     // 5秒 * 3 = 15秒
    val divided = duration3 / 2        // 10分钟 / 2 = 5分钟
    
    // 比较
    println(duration2 < duration3)  // true
    
    // 转换为各种单位
    println(duration2.inWholeMilliseconds)  // 5000
    println(duration2.inWholeSeconds)       // 5
    println(duration3.inWholeMinutes)       // 10
    
    // 字符串表示
    println(duration2.toString())  // 5s
    println(duration3.toString())  // 10m
    println(duration4.toString())  // 2h
    println(duration5.toString())  // 1d
    
    // ISO-8601 格式
    println(duration2.toIsoString())  // PT5S
    println(duration3.toIsoString())  // PT10M
}
```

### 3. 时间转换

```kotlin
import kotlin.time.Duration.Companion.seconds

fun timeConversions() {
    val duration = 3661.seconds  // 1小时1分钟1秒
    
    // 分解为时分秒
    val hours = duration.inWholeHours
    val minutes = (duration - hours.hours).inWholeMinutes
    val seconds = (duration - hours.hours - minutes.minutes).inWholeSeconds
    
    println("$hours 小时 $minutes 分钟 $seconds 秒")
    // 输出: 1 小时 1 分钟 1 秒
}
```

## kotlinx-datetime 库

### 1. 添加依赖

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-datetime:0.5.0")
}
```

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.jetbrains.kotlinx</groupId>
    <artifactId>kotlinx-datetime</artifactId>
    <version>0.5.0</version>
</dependency>
```

### 2. 核心概念

```kotlin
import kotlinx.datetime.*

fun coreConcepts() {
    // Instant - 时间戳（UTC）
    val instant = Clock.System.now()
    println(instant)  // 2024-01-15T08:30:00.000Z
    
    // LocalDateTime - 本地日期时间（无时区信息）
    val localDateTime = LocalDateTime(2024, 1, 15, 16, 30, 0)
    println(localDateTime)  // 2024-01-15T16:30
    
    // LocalDate - 本地日期
    val localDate = LocalDate(2024, 1, 15)
    println(localDate)  // 2024-01-15
    
    // LocalTime - 本地时间
    val localTime = LocalTime(16, 30, 0)
    println(localTime)  // 16:30
}
```

## 核心类详解

### 1. Instant（时间戳）

```kotlin
import kotlinx.datetime.*

fun instantOperations() {
    // 获取当前时间戳
    val now = Clock.System.now()
    println(now)  // 2024-01-15T08:30:00.000Z
    
    // 从纪元时间创建
    val fromEpoch = Instant.fromEpochMilliseconds(1705312200000)
    println(fromEpoch)
    
    // 从 ISO-8601 字符串创建
    val fromString = Instant.parse("2024-01-15T08:30:00Z")
    println(fromString)
    
    // 转换为纪元时间
    println(now.toEpochMilliseconds())  // 毫秒
    
    // 时间戳运算
    val later = now + 1.hours
    val earlier = now - 30.minutes
    val diff = later - earlier
    
    println("1小时后: $later")
    println("30分钟前: $earlier")
    println("时间差: $diff")
    
    // 比较
    println(now < later)  // true
    println(now > earlier)  // true
}
```

### 2. LocalDateTime（本地日期时间）

```kotlin
import kotlinx.datetime.*

fun localDateTimeOperations() {
    // 创建 LocalDateTime
    val dateTime1 = LocalDateTime(2024, 1, 15, 16, 30, 0)
    val dateTime2 = LocalDateTime.parse("2024-01-15T16:30:00")
    
    // 获取当前本地日期时间
    val now = Clock.System.now().toLocalDateTime(TimeZone.currentSystemDefault())
    
    // 访问各个字段
    println(dateTime1.year)        // 2024
    println(dateTime1.month)       // JANUARY
    println(dateTime1.monthNumber) // 1
    println(dateTime1.dayOfMonth)  // 15
    println(dateTime1.hour)        // 16
    println(dateTime1.minute)      // 30
    println(dateTime1.second)      // 0
    println(dateTime1.dayOfWeek)   // MONDAY
    println(dateTime1.dayOfYear)   // 15
    
    // 日期时间运算
    val tomorrow = dateTime1.date.plus(1, DateTimeUnit.DAY)
    val nextMonth = dateTime1.date.plus(1, DateTimeUnit.MONTH)
    val nextYear = dateTime1.date.plus(1, DateTimeUnit.YEAR)
    
    println("明天: $tomorrow")
    println("下个月: $nextMonth")
    println("明年: $nextYear")
    
    // 时间调整
    val withHour = dateTime1.copy(hour = 9)
    val withDate = dateTime1.copy(date = LocalDate(2024, 12, 25))
    
    println("调整小时: $withHour")
    println("调整日期: $withDate")
}
```

### 3. LocalDate（本地日期）

```kotlin
import kotlinx.datetime.*

fun localDateOperations() {
    // 创建 LocalDate
    val date1 = LocalDate(2024, 1, 15)
    val date2 = LocalDate.parse("2024-01-15")
    val today = Clock.System.todayIn(TimeZone.currentSystemDefault())
    
    // 日期运算
    val tomorrow = date1.plus(1, DateTimeUnit.DAY)
    val yesterday = date1.minus(1, DateTimeUnit.DAY)
    val nextWeek = date1.plus(7, DateTimeUnit.DAY)
    val nextMonth = date1.plus(1, DateTimeUnit.MONTH)
    
    // 日期差
    val startDate = LocalDate(2024, 1, 1)
    val endDate = LocalDate(2024, 12, 31)
    val daysBetween = endDate - startDate
    println("相差天数: ${daysBetween.days}")
    
    // 日期比较
    println(date1 < tomorrow)  // true
    println(date1 > yesterday)  // true
    
    // 获取月初月末
    val firstDayOfMonth = date1.copy(dayOfMonth = 1)
    val lastDayOfMonth = date1.plus(1, DateTimeUnit.MONTH).copy(dayOfMonth = 1).minus(1, DateTimeUnit.DAY)
    
    println("月初: $firstDayOfMonth")
    println("月末: $lastDayOfMonth")
    
    // 判断闰年
    println(date1.year.isLeap())  // 2024 是闰年，返回 true
}
```

### 4. LocalTime（本地时间）

```kotlin
import kotlinx.datetime.*

fun localTimeOperations() {
    // 创建 LocalTime
    val time1 = LocalTime(16, 30, 0, 0)
    val time2 = LocalTime.parse("16:30:00")
    
    // 访问字段
    println(time1.hour)        // 16
    println(time1.minute)      // 30
    println(time1.second)      // 0
    println(time1.nanosecond)  // 0
    
    // 时间运算
    val later = time1.plus(30, DateTimeUnit.MINUTE)
    val earlier = time1.minus(1, DateTimeUnit.HOUR)
    
    println("30分钟后: $later")
    println("1小时前: $earlier")
    
    // 时间比较
    println(time1 < later)   // true
    println(time1 > earlier) // true
    
    // 调整到特定时间
    val noon = LocalTime(12, 0)
    val midnight = LocalTime(0, 0)
    
    println("中午: $noon")
    println("午夜: $midnight")
}
```

## 时间格式化与解析

### 1. 使用 DateTimeFormat

```kotlin
import kotlinx.datetime.*
import kotlinx.datetime.format.*

fun formattingExamples() {
    val dateTime = LocalDateTime(2024, 1, 15, 16, 30, 0)
    val date = LocalDate(2024, 1, 15)
    val time = LocalTime(16, 30, 0)
    
    // 标准 ISO 格式
    println(dateTime.toString())  // 2024-01-15T16:30
    println(date.toString())      // 2024-01-15
    println(time.toString())      // 16:30
    
    // 自定义格式
    val dateFormat = LocalDate.Format {
        year()
        char('-')
        monthNumber()
        char('-')
        dayOfMonth()
    }
    println(dateFormat.format(date))  // 2024-01-15
    
    // 解析日期
    val parsedDate = dateFormat.parse("2024-01-15")
    println(parsedDate)
    
    // 完整日期时间格式
    val dateTimeFormat = LocalDateTime.Format {
        date(LocalDate.Formats.ISO)
        char(' ')
        hour()
        char(':')
        minute()
        char(':')
        second()
    }
    println(dateTimeFormat.format(dateTime))  // 2024-01-15 16:30:00
}
```

### 2. 常用格式模式

```kotlin
import kotlinx.datetime.*
import kotlinx.datetime.format.*

fun commonPatterns() {
    val dateTime = LocalDateTime(2024, 1, 15, 16, 30, 45)
    
    // 中文格式
    val chineseFormat = LocalDateTime.Format {
        year()
        char('年')
        monthNumber()
        char('月')
        dayOfMonth()
        char('日')
        char(' ')
        hour()
        char('时')
        minute()
        char('分')
        second()
        char('秒')
    }
    println(chineseFormat.format(dateTime))  // 2024年1月15日 16时30分45秒
    
    // 美式格式 (MM/dd/yyyy)
    val usFormat = LocalDate.Format {
        monthNumber()
        char('/')
        dayOfMonth()
        char('/')
        year()
    }
    println(usFormat.format(dateTime.date))  // 1/15/2024
    
    // 欧洲格式 (dd/MM/yyyy)
    val euFormat = LocalDate.Format {
        dayOfMonth()
        char('/')
        monthNumber()
        char('/')
        year()
    }
    println(euFormat.format(dateTime.date))  // 15/1/2024
}
```

## 时间计算与操作

### 1. DateTimePeriod（日期间隔）

```kotlin
import kotlinx.datetime.*

fun dateTimePeriodExamples() {
    // 创建期间
    val period1 = DateTimePeriod(years = 1, months = 2, days = 3)
    val period2 = DateTimePeriod(hours = 4, minutes = 30, seconds = 15)
    val period3 = DateTimePeriod(years = 1, months = 2, days = 3, hours = 4, minutes = 30, seconds = 15)
    
    println(period1)  // P1Y2M3D
    println(period2)  // PT4H30M15S
    println(period3)  // P1Y2M3DT4H30M15S
    
    // 期间运算
    val date = LocalDate(2024, 1, 15)
    val dateTime = LocalDateTime(2024, 1, 15, 12, 0, 0)
    
    val futureDate = date.plus(period1)
    val futureDateTime = dateTime.plus(period3)
    
    println("原始日期: $date")
    println("添加期间后: $futureDate")
    println("原始日期时间: $dateTime")
    println("添加期间后: $futureDateTime")
    
    // 解析期间字符串
    val parsedPeriod = DateTimePeriod.parse("P1Y2M3DT4H30M15S")
    println(parsedPeriod)
}
```

### 2. Duration（持续时间）

```kotlin
import kotlinx.datetime.*
import kotlin.time.Duration.Companion.hours
import kotlin.time.Duration.Companion.minutes

fun durationOperations() {
    val instant = Clock.System.now()
    
    // Duration 运算
    val duration1 = 2.hours + 30.minutes
    val duration2 = 1.hours - 15.minutes
    
    println(duration1)  // 2h 30m
    println(duration2)  // 45m
    
    // 应用到 Instant
    val later = instant + duration1
    val earlier = instant - duration2
    
    println("现在: $instant")
    println("2小时30分钟后: $later")
    println("45分钟前: $earlier")
    
    // Duration 比较
    println(duration1 > duration2)  // true
    
    // 获取总秒数/毫秒数
    println(duration1.inWholeSeconds)      // 9000
    println(duration1.inWholeMilliseconds) // 9000000
}
```

### 3. 时间差计算

```kotlin
import kotlinx.datetime.*

fun timeDifferenceExamples() {
    val start = LocalDateTime(2024, 1, 15, 9, 0, 0)
    val end = LocalDateTime(2024, 1, 15, 17, 30, 0)
    
    // 计算时间差（Duration）
    val duration = end.toInstant(TimeZone.UTC) - start.toInstant(TimeZone.UTC)
    println("工作时间: ${duration.inWholeHours}小时${(duration - duration.inWholeHours.hours).inWholeMinutes}分钟")
    
    // 日期间隔
    val startDate = LocalDate(2024, 1, 1)
    val endDate = LocalDate(2024, 12, 31)
    val daysBetween = endDate - startDate
    println("今年剩余天数: ${daysBetween.days}")
    
    // 年龄计算
    val birthDate = LocalDate(1990, 5, 15)
    val today = Clock.System.todayIn(TimeZone.currentSystemDefault())
    val age = today.year - birthDate.year - 
              if (today.monthNumber < birthDate.monthNumber || 
                  (today.monthNumber == birthDate.monthNumber && today.dayOfMonth < birthDate.dayOfMonth)) 1 else 0
    println("年龄: $age")
}
```

## 时区处理

### 1. TimeZone（时区）

```kotlin
import kotlinx.datetime.*

fun timeZoneExamples() {
    // 获取系统默认时区
    val systemZone = TimeZone.currentSystemDefault()
    println("系统时区: $systemZone")
    
    // 获取特定时区
    val utc = TimeZone.UTC
    val shanghai = TimeZone.of("Asia/Shanghai")
    val tokyo = TimeZone.of("Asia/Tokyo")
    val newYork = TimeZone.of("America/New_York")
    val london = TimeZone.of("Europe/London")
    
    println("UTC: $utc")
    println("上海: $shanghai")
    println("东京: $tokyo")
    println("纽约: $newYork")
    println("伦敦: $london")
    
    // 获取所有可用时区
    val availableZones = TimeZone.availableZoneIds
    println("可用时区数量: ${availableZones.size}")
}
```

### 2. 时区转换

```kotlin
import kotlinx.datetime.*

fun timeZoneConversion() {
    val utc = TimeZone.UTC
    val shanghai = TimeZone.of("Asia/Shanghai")
    val tokyo = TimeZone.of("Asia/Tokyo")
    val newYork = TimeZone.of("America/New_York")
    
    // 获取当前 UTC 时间
    val nowUtc = Clock.System.now()
    println("UTC 时间: $nowUtc")
    
    // 转换为本地日期时间
    val shanghaiTime = nowUtc.toLocalDateTime(shanghai)
    val tokyoTime = nowUtc.toLocalDateTime(tokyo)
    val newYorkTime = nowUtc.toLocalDateTime(newYork)
    
    println("上海时间: $shanghaiTime")
    println("东京时间: $tokyoTime")
    println("纽约时间: $newYorkTime")
    
    // 从本地时间转换为 Instant
    val localDateTime = LocalDateTime(2024, 1, 15, 16, 30, 0)
    val instantInShanghai = localDateTime.toInstant(shanghai)
    val instantInUtc = localDateTime.toInstant(utc)
    
    println("上海本地时间对应的 UTC: $instantInUtc")
    println("上海本地时间对应的 Instant: $instantInShanghai")
}
```

### 3. 夏令时处理

```kotlin
import kotlinx.datetime.*

fun daylightSavingTime() {
    val newYork = TimeZone.of("America/New_York")
    
    // 夏令时开始（2024年3月10日）
    val beforeDst = LocalDateTime(2024, 3, 10, 1, 30)
    val afterDst = LocalDateTime(2024, 3, 10, 3, 30)
    
    val instantBefore = beforeDst.toInstant(newYork)
    val instantAfter = afterDst.toInstant(newYork)
    
    println("夏令时前: $beforeDst -> $instantBefore")
    println("夏令时后: $afterDst -> $instantAfter")
    
    // 检查时区偏移
    println("纽约时区偏移: ${newYork.offsetAt(instantBefore)}")
    println("纽约时区偏移: ${newYork.offsetAt(instantAfter)}")
}
```

## Bad Practice

### 1. 使用已弃用的 Date/Calendar API

```kotlin
// ❌ 错误：使用旧的 Java Date API
import java.util.Date
import java.util.Calendar

fun badExample() {
    val date = Date()  // 已弃用
    val calendar = Calendar.getInstance()
    calendar.set(2024, 0, 15)  // 月份从 0 开始，容易出错
}

// ✅ 正确：使用 kotlinx-datetime
import kotlinx.datetime.*

fun goodExample() {
    val date = Clock.System.todayIn(TimeZone.currentSystemDefault())
    val dateTime = LocalDateTime(2024, 1, 15, 16, 30, 0)  // 月份从 1 开始
}
```

### 2. 忽略时区

```kotlin
// ❌ 错误：忽略时区导致时间错误
fun badExample() {
    val now = Clock.System.now()
    val localDateTime = now.toLocalDateTime(TimeZone.UTC)  // 假设是 UTC
    // 如果系统不在 UTC 时区，时间会出错
}

// ✅ 正确：明确指定时区
fun goodExample() {
    val now = Clock.System.now()
    val systemZone = TimeZone.currentSystemDefault()
    val localDateTime = now.toLocalDateTime(systemZone)
    
    // 或者明确使用特定时区
    val shanghaiTime = now.toLocalDateTime(TimeZone.of("Asia/Shanghai"))
}
```

### 3. 字符串拼接创建时间

```kotlin
// ❌ 错误：字符串拼接创建时间
fun badExample(): LocalDateTime {
    val year = 2024
    val month = 1
    val day = 15
    val hour = 16
    val minute = 30
    
    val dateTimeString = "$year-$month-$day $hour:$minute:00"
    return LocalDateTime.parse(dateTimeString)  // 容易出错
}

// ✅ 正确：使用构造函数
fun goodExample(): LocalDateTime {
    return LocalDateTime(2024, 1, 15, 16, 30, 0)
}
```

### 4. 不处理时间解析异常

```kotlin
// ❌ 错误：不处理解析异常
fun badExample(dateString: String): LocalDate {
    return LocalDate.parse(dateString)  // 可能抛出异常
}

// ✅ 正确：处理解析异常
fun goodExample(dateString: String): LocalDate? {
    return try {
        LocalDate.parse(dateString)
    } catch (e: IllegalArgumentException) {
        println("日期解析失败: $dateString")
        null
    }
}
```

### 5. 混淆 LocalDateTime 和 Instant

```kotlin
// ❌ 错误：混淆 LocalDateTime 和 Instant
fun badExample() {
    val localDateTime = LocalDateTime(2024, 1, 15, 16, 30, 0)
    val instant = Clock.System.now()
    
    // 直接比较会出错
    // if (localDateTime < instant) { ... }  // 编译错误
}

// ✅ 正确：明确转换后再比较
fun goodExample() {
    val localDateTime = LocalDateTime(2024, 1, 15, 16, 30, 0)
    val instant = Clock.System.now()
    val zone = TimeZone.currentSystemDefault()
    
    val localAsInstant = localDateTime.toInstant(zone)
    if (localAsInstant < instant) {
        println("本地时间在现在之前")
    }
}
```

### 6. 使用可变状态存储时间

```kotlin
// ❌ 错误：使用可变变量存储时间
class BadExample {
    var createdAt: LocalDateTime = LocalDateTime(2024, 1, 1, 0, 0, 0)
        private set
    
    fun updateTime() {
        createdAt = Clock.System.now().toLocalDateTime(TimeZone.UTC)
    }
}

// ✅ 正确：时间对象应该是不可变的
class GoodExample {
    val createdAt: LocalDateTime = Clock.System.now().toLocalDateTime(TimeZone.UTC)
    
    fun withUpdatedTime(): GoodExample {
        return GoodExample()  // 创建新实例
    }
}
```

## 最佳实践

### 1. 使用 Clock 进行时间控制

```kotlin
import kotlinx.datetime.*

// 定义可注入的 Clock 接口
interface TimeProvider {
    fun now(): Instant
    fun today(): LocalDate
}

class SystemTimeProvider : TimeProvider {
    override fun now(): Instant = Clock.System.now()
    override fun today(): LocalDate = Clock.System.todayIn(TimeZone.currentSystemDefault())
}

class FixedTimeProvider(private val fixedTime: Instant) : TimeProvider {
    override fun now(): Instant = fixedTime
    override fun today(): LocalDate = fixedTime.toLocalDateTime(TimeZone.UTC).date
}

// 在应用中使用
class TaskService(private val timeProvider: TimeProvider) {
    fun createTask(name: String): Task {
        return Task(
            name = name,
            createdAt = timeProvider.now()
        )
    }
}

// 测试时使用固定时间
fun testTaskService() {
    val fixedTime = Instant.parse("2024-01-15T10:00:00Z")
    val timeProvider = FixedTimeProvider(fixedTime)
    val service = TaskService(timeProvider)
    
    val task = service.createTask("测试任务")
    assert(task.createdAt == fixedTime)
}
```

### 2. 明确时间类型语义

```kotlin
import kotlinx.datetime.*

// ✅ 好的做法：使用明确的时间类型
data class Event(
    val id: String,
    val name: String,
    val startTime: Instant,        // 使用 Instant 表示绝对时间点
    val displayDate: LocalDate,    // 使用 LocalDate 表示显示日期
    val reminderTime: LocalTime?   // 使用 LocalTime 表示提醒时间
)

// 创建事件
fun createEvent(): Event {
    val zone = TimeZone.of("Asia/Shanghai")
    
    return Event(
        id = "event-001",
        name = "会议",
        startTime = Instant.parse("2024-01-15T08:00:00Z"),
        displayDate = LocalDate(2024, 1, 15),
        reminderTime = LocalTime(7, 30)
    )
}
```

### 3. 统一时区处理

```kotlin
import kotlinx.datetime.*

// ✅ 好的做法：统一时区处理
object TimeUtils {
    val DEFAULT_ZONE: TimeZone = TimeZone.of("Asia/Shanghai")
    val UTC_ZONE: TimeZone = TimeZone.UTC
    
    fun Instant.toDefaultLocalDateTime(): LocalDateTime {
        return this.toLocalDateTime(DEFAULT_ZONE)
    }
    
    fun LocalDateTime.toDefaultInstant(): Instant {
        return this.toInstant(DEFAULT_ZONE)
    }
    
    fun nowInDefaultZone(): LocalDateTime {
        return Clock.System.now().toDefaultLocalDateTime()
    }
    
    fun todayInDefaultZone(): LocalDate {
        return Clock.System.todayIn(DEFAULT_ZONE)
    }
}

// 使用
fun example() {
    val now = TimeUtils.nowInDefaultZone()
    val today = TimeUtils.todayInDefaultZone()
    
    val instant = now.toDefaultInstant()
    val localDateTime = instant.toDefaultLocalDateTime()
}
```

### 4. 时间格式化工具类

```kotlin
import kotlinx.datetime.*
import kotlinx.datetime.format.*

// ✅ 好的做法：创建格式化工具类
object DateTimeFormats {
    val ISO_DATE: DateTimeFormat<LocalDate> = LocalDate.Formats.ISO
    
    val ISO_DATE_TIME: DateTimeFormat<LocalDateTime> = LocalDateTime.Formats.ISO
    
    val CHINESE_DATE: DateTimeFormat<LocalDate> = LocalDate.Format {
        year()
        char('年')
        monthNumber()
        char('月')
        dayOfMonth()
        char('日')
    }
    
    val CHINESE_DATE_TIME: DateTimeFormat<LocalDateTime> = LocalDateTime.Format {
        date(CHINESE_DATE)
        char(' ')
        hour()
        char(':')
        minute()
    }
    
    val COMPACT_DATE: DateTimeFormat<LocalDate> = LocalDate.Format {
        year()
        monthNumber()
        dayOfMonth()
    }
}

// 使用
fun formatExample() {
    val date = LocalDate(2024, 1, 15)
    val dateTime = LocalDateTime(2024, 1, 15, 16, 30, 0)
    
    println(DateTimeFormats.CHINESE_DATE.format(date))      // 2024年1月15日
    println(DateTimeFormats.CHINESE_DATE_TIME.format(dateTime))  // 2024年1月15日 16:30
    println(DateTimeFormats.COMPACT_DATE.format(date))      // 20240115
}
```

### 5. 时间范围查询

```kotlin
import kotlinx.datetime.*

// ✅ 好的做法：时间范围查询
data class TimeRange(
    val start: Instant,
    val end: Instant
) {
    init {
        require(start <= end) { "开始时间必须小于等于结束时间" }
    }
    
    fun contains(instant: Instant): Boolean {
        return instant in start..end
    }
    
    fun overlaps(other: TimeRange): Boolean {
        return this.start < other.end && other.start < this.end
    }
    
    fun duration(): Duration {
        return end - start
    }
}

// 创建当天的范围
fun createTodayRange(zone: TimeZone = TimeZone.currentSystemDefault()): TimeRange {
    val today = Clock.System.todayIn(zone)
    val start = today.atStartOfDayIn(zone)
    val end = (today + DateTimePeriod(days = 1)).atStartOfDayIn(zone)
    
    return TimeRange(start, end)
}

// 创建月份范围
fun createMonthRange(year: Int, month: Int, zone: TimeZone = TimeZone.currentSystemDefault()): TimeRange {
    val startDate = LocalDate(year, month, 1)
    val endDate = if (month == 12) {
        LocalDate(year + 1, 1, 1)
    } else {
        LocalDate(year, month + 1, 1)
    }
    
    return TimeRange(
        startDate.atStartOfDayIn(zone),
        endDate.atStartOfDayIn(zone)
    )
}
```

### 6. 时间序列生成

```kotlin
import kotlinx.datetime.*

// ✅ 好的做法：生成时间序列
fun generateDateSequence(
    start: LocalDate,
    end: LocalDate,
    step: DateTimePeriod = DateTimePeriod(days = 1)
): Sequence<LocalDate> {
    return generateSequence(start) { current ->
        val next = current.plus(step)
        if (next > end) null else next
    }
}

fun generateDateTimeSequence(
    start: Instant,
    end: Instant,
    step: Duration
): Sequence<Instant> {
    return generateSequence(start) { current ->
        val next = current + step
        if (next > end) null else next
    }
}

// 使用
fun sequenceExample() {
    val startDate = LocalDate(2024, 1, 1)
    val endDate = LocalDate(2024, 1, 31)
    
    // 生成1月份的所有日期
    val dates = generateDateSequence(startDate, endDate).toList()
    println("1月份共有 ${dates.size} 天")
    
    // 生成每周的日期
    val weeklyDates = generateDateSequence(startDate, endDate, DateTimePeriod(days = 7)).toList()
    println("1月份共有 ${weeklyDates.size} 周")
}
```

## 第三方时间处理库

### 1. Joda-Time

**适用场景**：需要在旧版 Java（Java 8 之前）中使用现代时间 API

```kotlin
// 依赖
// implementation("joda-time:joda-time:2.12.5")

import org.joda.time.*
import org.joda.time.format.*

fun jodaTimeExample() {
    // 获取当前时间
    val now = DateTime.now()
    
    // 创建特定时间
    val specificTime = DateTime(2024, 1, 15, 16, 30, 0)
    
    // 时区转换
    val shanghaiTime = now.withZone(DateTimeZone.forID("Asia/Shanghai"))
    
    // 格式化
    val formatter = DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss")
    val formatted = formatter.print(now)
    
    // 时间运算
    val tomorrow = now.plusDays(1)
    val nextWeek = now.plusWeeks(1)
}
```

**特点**：
- 成熟稳定，广泛使用
- 支持 Java 8 之前的版本
- API 设计优秀
- 但已被 Java 8 的 `java.time` 取代

### 2. ThreeTenABP

**适用场景**：Android 项目，需要支持 API 26 以下版本

```kotlin
// 依赖
// implementation("com.jakewharton.threetenabp:threetenabp:1.4.6")

import org.threeten.bp.*
import org.threeten.bp.format.*

fun threeTenExample() {
    // 获取当前时间
    val now = ZonedDateTime.now()
    
    // 创建特定时间
    val localDateTime = LocalDateTime.of(2024, 1, 15, 16, 30, 0)
    
    // 时区转换
    val shanghaiZone = ZoneId.of("Asia/Shanghai")
    val shanghaiTime = localDateTime.atZone(shanghaiZone)
    
    // 格式化
    val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
    val formatted = localDateTime.format(formatter)
}
```

**特点**：
- Android 兼容性好
- 支持 API 15+
- 与 `java.time` API 一致
- 需要初始化：`AndroidThreeTen.init(context)`

### 3. kotlinx-datetime-ext

**适用场景**：需要额外的 kotlinx-datetime 扩展功能

```kotlin
// 依赖（社区库）
// implementation("io.github.kotlinx-datetime-ext:kotlinx-datetime-ext:0.1.0")

import kotlinx.datetime.*

// 该库提供了额外的扩展函数和工具类
// 具体 API 请参考库的文档
```

**特点**：
- 为 kotlinx-datetime 提供额外功能
- 社区维护
- 功能因版本而异

### 4. 库选择建议

| 场景 | 推荐库 | 说明 |
|------|--------|------|
| Kotlin 多平台项目 | kotlinx-datetime | 官方支持，多平台兼容 |
| JVM 项目（Java 8+） | java.time / kotlinx-datetime | 标准库，无需额外依赖 |
| Android（API 26+） | java.time / kotlinx-datetime | 原生支持 |
| Android（API < 26） | ThreeTenABP | 兼容性最好 |
| 遗留项目（Java < 8） | Joda-Time | 成熟稳定 |
| 需要额外功能 | kotlinx-datetime-ext | 社区扩展 |

### 5. 迁移指南

从 Joda-Time 迁移到 kotlinx-datetime：

```kotlin
// Joda-Time
import org.joda.time.DateTime
import org.joda.time.LocalDate

val jodaDateTime = DateTime.now()
val jodaLocalDate = LocalDate.now()

// kotlinx-datetime
import kotlinx.datetime.*

val kotlinInstant = Clock.System.now()
val kotlinLocalDate = Clock.System.todayIn(TimeZone.currentSystemDefault())
val kotlinLocalDateTime = kotlinInstant.toLocalDateTime(TimeZone.currentSystemDefault())

// 概念映射
// DateTime -> Instant + TimeZone
// LocalDate -> LocalDate
// LocalDateTime -> LocalDateTime
// DateTimeZone -> TimeZone
// Period -> DateTimePeriod / Duration
```

从 java.time 迁移到 kotlinx-datetime：

```kotlin
// java.time
import java.time.ZonedDateTime
import java.time.LocalDateTime
import java.time.ZoneId

val javaZonedDateTime = ZonedDateTime.now()
val javaLocalDateTime = LocalDateTime.now()

// kotlinx-datetime
import kotlinx.datetime.*

val kotlinInstant = Clock.System.now()
val kotlinLocalDateTime = kotlinInstant.toLocalDateTime(TimeZone.currentSystemDefault())

// 概念映射
// ZonedDateTime -> Instant + TimeZone
// LocalDateTime -> LocalDateTime
// LocalDate -> LocalDate
// ZoneId -> TimeZone
// Duration -> Duration / DateTimePeriod
```

## 总结

Kotlin 时间处理的最佳实践：

1. **优先使用 kotlinx-datetime**：官方支持，多平台兼容，API 设计优秀
2. **明确时间类型语义**：区分 Instant、LocalDateTime、LocalDate、LocalTime 的使用场景
3. **统一时区处理**：使用工具类统一时区管理，避免时区混乱
4. **使用 Clock 进行时间控制**：便于测试和时间模拟
5. **避免可变状态**：时间对象应该是不可变的
6. **处理解析异常**：时间解析可能失败，需要适当的错误处理
7. **选择合适的第三方库**：根据项目需求选择合适的时间库

通过掌握 Kotlin 的时间处理 API，你可以编写出更加健壮、可维护的时间相关代码。