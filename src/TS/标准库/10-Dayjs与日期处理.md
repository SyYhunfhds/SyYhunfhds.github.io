---
title: Dayjs与日期处理
date: 2026-07-09
footer: Trae编辑
---

# Dayjs 与日期处理

## Go 开发者已知

Go 的 `time.Time` 是一个强大且设计良好的日期时间类型，但 JS 的 `Date` 有很多设计缺陷。

```go
// Go time.Time 是值类型，不可变
import "time"

// 创建时间
t := time.Now()                          // 当前时间
t2 := time.Date(2026, 7, 9, 10, 30, 0, 0, time.UTC)

// 格式化 —— 使用参考时间 Mon Jan 2 15:04:05 MST 2006
fmt.Println(t.Format("2006-01-02"))              // "2026-07-09"
fmt.Println(t.Format("2006-01-02 15:04:05"))     // "2026-07-09 10:30:00"
fmt.Println(t.Format(time.RFC3339))              // "2026-07-09T10:30:00Z"

// 时间操作 —— 返回新 time.Time（不可变）
tomorrow := t.AddDate(0, 0, 1)      // 加一天
nextMonth := t.AddDate(0, 1, 0)     // 加一个月
later := t.Add(2 * time.Hour)       // 加两小时

// 时间差
diff := later.Sub(t)                // time.Duration
fmt.Println(diff.Hours())           // 2

// 时区
loc, _ := time.LoadLocation("Asia/Shanghai")
tInShanghai := t.In(loc)

// 比较
fmt.Println(t.Before(t2))           // false
fmt.Println(t.After(t2))            // true

// Duration
d := 3 * time.Hour + 30 * time.Minute
fmt.Println(d.Hours())      // 3.5
fmt.Println(d.Minutes())    // 210
```

## TS 怎么做

### JS Date 的缺陷

```ts
// JS 原生 Date 的常见问题 —— 这些是 Go 中没有的问题

// 1. 月份从 0 开始
const d = new Date(2026, 6, 9); // 实际是 7 月！月份 0=1月
console.log(d.getMonth()); // 6（但这是 7 月）

// 2. 可变性 —— 所有 setter 修改原对象
const d2 = new Date("2026-07-09");
d2.setDate(d2.getDate() + 1); // d2 被原地修改！
console.log(d2); // 已变为 2026-07-10

// 3. 解析行为不一致
console.log(new Date("2026-07-09").toISOString());   // "2026-07-09T00:00:00.000Z"
console.log(new Date("2026/07/09").toISOString());   // 可能报错或时区不同
console.log(new Date("07/09/2026").toISOString());   // 美式格式的解析结果不确定

// 4. 时区处理困难
// 原生 Date 只能获取本地时区和 UTC，无法轻松切换到其他时区

// 5. 格式化能力弱
const now = new Date();
console.log(now.toString()); // "Thu Jul 09 2026 10:30:00 GMT+0800" — 几乎不可定制
// 需要手写 padStart 格式化
function formatDate(d: Date): string {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
}
```

### Dayjs 安装与基础用法

```bash
npm install dayjs
```

```ts
import dayjs from "dayjs";

// 创建 dayjs 对象
const now = dayjs();                    // 当前时间
const d1 = dayjs("2026-07-09");         // 从字符串解析
const d2 = dayjs("2026-07-09T10:30:00");
const d3 = dayjs(new Date(2026, 6, 9)); // 从 Date 对象
const d4 = dayjs(1720454400000);        // 从时间戳

// 不可变 API —— 所有操作返回新的 dayjs 对象
const original = dayjs("2026-07-09");
const tomorrow = original.add(1, "day");
const nextWeek = original.add(7, "day");
const lastMonth = original.subtract(1, "month");
const startOfMonth = original.startOf("month"); // 2026-07-01 00:00:00
const endOfMonth = original.endOf("month");     // 2026-07-31 23:59:59

console.log(original.format());  // "2026-07-09T00:00:00+08:00"（不变）
console.log(tomorrow.format());  // "2026-07-10T00:00:00+08:00"

// 链式调用
const result = dayjs("2026-07-09")
    .add(1, "month")
    .startOf("month")
    .subtract(1, "day")
    .format("YYYY-MM-DD");
// "2026-07-31"
```

### 格式化

```ts
import dayjs from "dayjs";

// 格式化 —— 类似 Go 的 time.Format
const d = dayjs("2026-07-09 10:30:45");

console.log(d.format("YYYY-MM-DD"));              // "2026-07-09"
console.log(d.format("YYYY年MM月DD日"));           // "2026年07月09日"
console.log(d.format("YYYY-MM-DD HH:mm:ss"));     // "2026-07-09 10:30:45"
console.log(d.format("YYYY-MM-DD hh:mm:ss A"));   // "2026-07-09 10:30:45 AM"
console.log(d.format("dddd"));                    // "Thursday"（星期几）
console.log(d.format("YYYY-MM-DDTHH:mm:ssZ"));    // "2026-07-09T10:30:45+08:00"
```

::: code-tabs#lang

@tab TypeScript (Dayjs)

```ts
const d = dayjs("2026-07-09");
d.format("YYYY-MM-DD");            // "2026-07-09"
d.format("YYYY-MM-DD HH:mm:ss");  // "2026-07-09 00:00:00"
```

@tab Go (time.Time)

```go
t, _ := time.Parse("2006-01-02", "2026-07-09")
t.Format("2006-01-02")                // "2026-07-09"
t.Format("2006-01-02 15:04:05")       // "2026-07-09 00:00:00"
```

:::

### 时区处理

```ts
// 需要安装 utc 和 timezone 插件
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

dayjs.extend(utc);
dayjs.extend(timezone);

// 获取某个时区的时间
const shanghai = dayjs().tz("Asia/Shanghai");
const tokyo = dayjs().tz("Asia/Tokyo");
const newyork = dayjs().tz("America/New_York");

console.log(shanghai.format("YYYY-MM-DD HH:mm:ss")); // 上海时间
console.log(tokyo.format("YYYY-MM-DD HH:mm:ss"));    // 东京时间（+1h）

// 时区转换
const utcTime = dayjs.utc("2026-07-09T10:00:00Z");
console.log(utcTime.tz("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss"));
// "2026-07-09 18:00:00"（UTC+8）

// 获取用户时区
const userTimezone = dayjs.tz.guess();
console.log(userTimezone); // "Asia/Shanghai" 等
```

### 相对时间

```ts
// 需要安装 relativeTime 插件
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import customParseFormat from "dayjs/plugin/customParseFormat";

dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(relativeTime);
dayjs.extend(customParseFormat);
dayjs.locale("zh-cn");

// 工具函数
export function formatDate(date: string | Date | dayjs.Dayjs, template = "YYYY-MM-DD"): string {
    return dayjs(date).format(template);
}

export function formatDateTime(date: string | Date | dayjs.Dayjs): string {
    return dayjs(date).format("YYYY-MM-DD HH:mm:ss");
}

export function formatRelative(date: string | Date | dayjs.Dayjs): string {
    return dayjs(date).fromNow();
}

export function isExpired(date: string | Date | dayjs.Dayjs): boolean {
    return dayjs().isAfter(date);
}

export function daysUntil(date: string | Date | dayjs.Dayjs): number {
    return dayjs(date).diff(dayjs().startOf("day"), "day");
}

// 使用
const now = formatDateTime(new Date()); // "2026-07-09 10:30:00"
const relative = formatRelative("2026-07-01"); // "8 天前"
const expired = isExpired("2026-07-01"); // true
```

### 2. 日期范围生成器

```ts
// Best: 日期序列生成
function* dateRange(
    start: string | Date | dayjs.Dayjs,
    end: string | Date | dayjs.Dayjs,
    unit: "day" | "week" | "month" = "day"
): Generator<string> {
    let current = dayjs(start).startOf("day");
    const endDate = dayjs(end).startOf("day");

    while (current.isBefore(endDate) || current.isSame(endDate)) {
        yield current.format("YYYY-MM-DD");
        current = current.add(1, unit);
    }
}

// 使用
const days = [...dateRange("2026-07-01", "2026-07-07")];
// ["2026-07-01", "2026-07-02", ..., "2026-07-07"]

const months = [...dateRange("2026-01", "2026-06", "month")];
// ["2026-01-01", "2026-02-01", ..., "2026-06-01"]
```

### 3. 日期校验工具

```ts
// Best: 日期校验 + 格式化
const DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;
const TIME_REGEX = /^\d{2}:\d{2}$/;

export function isValidDate(str: string): boolean {
    if (!DATE_REGEX.test(str)) return false;
    return dayjs(str, "YYYY-MM-DD", true).isValid();
}

export function isValidTime(str: string): boolean {
    if (!TIME_REGEX.test(str)) return false;
    return dayjs(str, "HH:mm", true).isValid();
}

export function parseDateSafe(str: string): dayjs.Dayjs | null {
    const d = dayjs(str, "YYYY-MM-DD", true);
    return d.isValid() ? d : null;
}

// 使用
console.log(isValidDate("2026-07-09")); // true
console.log(isValidDate("2026-13-01")); // false（月份错误）
console.log(isValidTime("25:00"));      // false
```

### 4. 日期的业务常用封装

```ts
// Best: 业务常用日期计算
export class DateUtils {
    // 今天开始时间
    static startOfToday(): dayjs.Dayjs {
        return dayjs().startOf("day");
    }

    // 今天结束时间
    static endOfToday(): dayjs.Dayjs {
        return dayjs().endOf("day");
    }

    // 获取本周一
    static startOfWeek(): dayjs.Dayjs {
        return dayjs().startOf("week").add(1, "day"); // 周一
    }

    // 获取本月第一天
    static startOfMonth(): dayjs.Dayjs {
        return dayjs().startOf("month");
    }

    // 获取年龄（根据生日）
    static getAge(birthday: string): number {
        return dayjs().diff(dayjs(birthday), "year");
    }

    // 判断是否为同一天
    static isSameDay(a: string | Date, b: string | Date): boolean {
        return dayjs(a).isSame(dayjs(b), "day");
    }

    // 获取时间段的描述
    static getPeriodDescription(start: string, end: string): string {
        const diffDays = dayjs(end).diff(dayjs(start), "day");
        if (diffDays === 0) return "今天";
        if (diffDays === 1) return "明天";
        if (diffDays < 7) return `${diffDays} 天后`;
        return dayjs(end).format("MM月DD日");
    }
}

console.log(DateUtils.getAge("2000-01-01")); // 26
console.log(DateUtils.isSameDay("2026-07-09", "2026-07-09")); // true
```

::: tip 总结

1. **不要用原生 Date** -- 月份从0开始、可变性、格式化困难等缺陷太多
2. Dayjs 提供不可变 API，和 Go 的 `time.Time` 使用体验一致
3. 插件系统让 Dayjs 体积小（2KB）但功能完整
4. 统一封装抽象层，避免项目中 Date 和 Dayjs 混用
5. UTC 存储 + 本地时区展示是推荐的时区策略
6. Duration 需要插件支持，不如 Go `time.Duration` 原生方便

:::/plugin/relativeTime";
import "dayjs/locale/zh-cn";

dayjs.extend(relativeTime);
dayjs.locale("zh-cn"); // 设置为中文

const past = dayjs("2026-07-01");
const future = dayjs("2026-08-01");

console.log(past.fromNow());        // "8 天前"
console.log(future.fromNow());      // "23 天后"
console.log(past.to(future));       // "一个月后"
console.log(future.to(past));       // "一个月前"

// 自定义基准时间
const base = dayjs("2026-07-09");
console.log(past.from(base));       // "8 天前"
```

### Duration

```ts
// Dayjs 没有内置 Duration，但可以用 duration 插件
import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";

dayjs.extend(duration);

// 创建 Duration
const d1 = dayjs.duration(3, "hours");
const d2 = dayjs.duration({ hours: 3, minutes: 30 });

// 获取 Duration 信息
console.log(d1.hours());          // 3
console.log(d1.asHours());        // 3
console.log(d1.asMinutes());      // 180

// Duration 格式化
console.log(d2.format("HH:mm:ss")); // "03:30:00"

// Duration 运算
const total = d1.add(d2);
console.log(total.asHours()); // 6.5

// 时间差
const start = dayjs("2026-07-09T10:00:00");
const end = dayjs("2026-07-09T14:30:00");
const diff = dayjs.duration(end.diff(start));
console.log(diff.hours());   // 4
console.log(diff.minutes()); // 30
```

::: code-tabs#lang

@tab TypeScript (Dayjs)

```ts
const diff = dayjs.duration(
    dayjs("14:30").diff(dayjs("10:00"))
);
console.log(diff.asHours()); // 4.5
```

@tab Go (time.Duration)

```go
start, _ := time.Parse("15:04", "10:00")
end, _ := time.Parse("15:04", "14:30")
diff := end.Sub(start)
fmt.Println(diff.Hours()) // 4.5
```

:::

### 插件系统

```ts
// Dayjs 的核心很小，功能通过插件扩展
import dayjs from "dayjs";

// 常用插件
import isSameOrBefore from "dayjs/plugin/isSameOrBefore";
import isSameOrAfter from "dayjs/plugin/isSameOrAfter";
import isBetween from "dayjs/plugin/isBetween";
import advancedFormat from "dayjs/plugin/advancedFormat";
import customParseFormat from "dayjs/plugin/customParseFormat";
import localeData from "dayjs/plugin/localeData";
import weekday from "dayjs/plugin/weekday";
import isoWeek from "dayjs/plugin/isoWeek";
import arraySupport from "dayjs/plugin/arraySupport";
import objectSupport from "dayjs/plugin/objectSupport";

dayjs.extend(isSameOrBefore);
dayjs.extend(isSameOrAfter);
dayjs.extend(isBetween);
dayjs.extend(advancedFormat);
dayjs.extend(customParseFormat);
dayjs.extend(localeData);
dayjs.extend(weekday);
dayjs.extend(isoWeek);

// 使用插件功能
const d = dayjs("2026-07-09");

// 比较
console.log(d.isSameOrBefore("2026-07-10")); // true
console.log(d.isBetween("2026-07-01", "2026-08-01")); // true

// 高级格式化
console.log(d.format("Q"));   // 3（季度）
console.log(d.format("Do"));  // "9th"（日序数）
console.log(d.format("dd"));  // "Th"（缩写星期）

// 星期
console.log(d.weekday()); // 4（星期四，0=星期日）
console.log(d.isoWeekday()); // 4（星期四，1=星期一）
```

## 差异分析

| 维度 | Go (time.Time) | TypeScript (Dayjs) |
|------|---------------|-------------------|
| **可变性** | 不可变（所有方法返回新值） | 不可变（所有方法返回新 Dayjs） |
| **月份** | 正常 `time.July=7` | Dayjs 正常 `7月=7`（原生 Date 从0开始） |
| **格式化** | 参考时间 `2006-01-02` | `YYYY-MM-DD`（类似 PHP/Java） |
| **时区** | `time.LoadLocation` + `.In()` | `dayjs/plugin/timezone` 插件 |
| **Duration** | `time.Duration` 原生支持 | `dayjs/plugin/duration` 插件 |
| **相对时间** | 需手写 | `dayjs/plugin/relativeTime` 插件 |
| **解析** | `time.Parse` 严格 | 宽松解析 + `customParseFormat` |
| **JSON 序列化** | `json.Marshal` → RFC3339 | `.toISOString()` / `.format()` |

## Bad Practice

### 1. 直接使用原生 Date

```ts
// Bad: 使用原生 Date
const start = new Date();
// ... 一些操作 ...
start.setDate(start.getDate() + 7); // 修改了原对象！

// 格式化需要手写
function format(d: Date): string {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

// Best: 使用 Dayjs 统一管理
const start = dayjs();
const nextWeek = start.add(7, "day"); // 不修改原对象
console.log(nextWeek.format("YYYY-MM-DD")); // 原生格式化
```

### 2. 忘记处理 Dayjs 无效日期

```ts
// Bad: 假设解析总是成功
const d = dayjs("invalid-date-string");
console.log(d.format("YYYY-MM-DD")); // "Invalid Date"

// Best: 校验解析结果
const d = dayjs("2026-07-09");
if (!d.isValid()) {
    throw new Error("无效的日期");
}
console.log(d.format("YYYY-MM-DD"));

// 或使用 customParseFormat 严格解析
import customParseFormat from "dayjs/plugin/customParseFormat";
dayjs.extend(customParseFormat);

const d2 = dayjs("2026/07/09", "YYYY/MM/DD");
if (!d2.isValid()) {
    console.error("日期格式不正确");
}
```

### 3. 时区处理不一致

```ts
// Bad: 混用本地时间和 UTC
const localDate = dayjs("2026-07-09"); // 解析为本地时区 00:00
const utcDate = dayjs.utc("2026-07-09"); // 解析为 UTC 00:00
console.log(localDate.format()); // "2026-07-09T00:00:00+08:00"
console.log(utcDate.format());   // "2026-07-09T00:00:00+00:00"

// Best: 统一使用 UTC 存储，展示时转本地时区
// 存储
const eventTime = dayjs.utc("2026-07-09T10:00:00Z");

// 展示
const displayTime = eventTime.tz("Asia/Shanghai");
console.log(displayTime.format("YYYY-MM-DD HH:mm:ss"));
```

### 4. 不必要的 Dayjs 来回转换

```ts
// Bad: 在 Dayjs 和 Date 之间反复转换
const d = dayjs();
const nativeDate = d.toDate();
const backToDayjs = dayjs(nativeDate);
const again = backToDayjs.toDate();
// 完全没必要

// Best: 保持使用 Dayjs
const d = dayjs();
// ... 全部操作使用 Dayjs API ...
```

## Best Practice

### 1. 统一 Dayjs 抽象层

```ts
// Best: 封装统一的时间工具
// utils/date.ts
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import relativeTime from "dayjs