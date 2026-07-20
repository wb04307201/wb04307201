<!--
module:
  parent: java
  slug: java/date-time
  type: article
  category: 主模块子文章
  summary: Java Date-Time API 学习笔记
-->

# Java Date-Time API 学习笔记

## 一、Date 和 Calendar 的问题

Java 1.0 引入的 `java.util.Date` 和 Java 1.1 引入的 `java.util.Calendar` 存在大量设计缺陷，是 Java 标准库中被诟病最多的 API 之一。

### 1.1 Date 的设计问题

**可变性（Mutability）**

`Date` 对象是可变的，这意味着它可以被意外修改，导致难以追踪的 Bug：

```java
Date date = new Date();
Date date2 = date;
date2.setTime(date2.getTime() + 86400000); // 修改了 date2，date 也被修改
// 两个引用指向同一个对象，无法保证"日期值"的语义
```

**月份从 0 开始**

```java
Date date = new Date(2024 - 1900, 11, 25); // 2024年12月25日
// 年份需要减去 1900，月份从 0 开始（0=一月, 11=十二月）
// 这种设计极易导致 off-by-one 错误
```

**线程不安全**

`Date` 不是线程安全的。在多线程环境下共享 `Date` 对象会导致数据竞争：

```java
// 多个线程同时修改同一个 Date 对象会导致不可预期的结果
```

**命名误导**

类名为 `Date`，但实际存储的是"时间戳"（自 1970-01-01 00:00:00 UTC 以来的毫秒数），既包含日期也包含时间，语义模糊。

### 1.2 Calendar 的设计问题

**同样可变**

```java
Calendar cal = Calendar.getInstance();
cal.set(Calendar.MONTH, Calendar.DECEMBER); // 可被任意修改
```

**API 臃肿且不一致**

```java
Calendar cal = Calendar.getInstance();
cal.set(2024, 11, 25, 10, 30, 0); // 月份仍从 0 开始
cal.get(Calendar.DAY_OF_WEEK);     // 常量命名冗长
cal.add(Calendar.DAY_OF_MONTH, 1); // 修改操作不直观
```

**性能差**

`Calendar` 内部有大量字段和复杂的计算逻辑，每次 `get()` 或 `add()` 都可能触发重新计算，开销较大。

**时区隐式依赖**

`Calendar.getInstance()` 默认使用系统时区，在不同环境下行为不一致。

---
## 引言：基础概念

Java Date-Time API 学习笔记 是入门必学的基础概念。

本篇给出一句话定义 + 最小可运行示例 + 3 个常见误区，**5 分钟读完，10 分钟上手**。

---

## 二、SimpleDateFormat 的线程安全问题

`SimpleDateFormat` 是 Java 8 之前最常用的日期格式化器，但它是**线程不安全**的。

### 2.1 问题演示

```java
// 错误做法：将 SimpleDateFormat 作为共享静态变量
public class DateFormatUtil {
    private static final SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    public static String format(Date date) {
        return sdf.format(date); // 多线程下会出错！
    }
}
```

多线程并发调用时可能出现以下现象：

- 格式化结果错乱（如日期变成 `1970-01-01`）
- 抛出 `NumberFormatException`
- 抛出 `ArrayIndexOutOfBoundsException`

**根因**：`SimpleDateFormat` 内部使用了 `Calendar` 作为成员变量来保存解析/格式化过程中的状态，多线程同时操作同一个实例时状态互相覆盖。

### 2.2 旧方案

**方案一：每次创建新实例（性能差）**

```java
public static String format(Date date) {
    return new SimpleDateFormat("yyyy-MM-dd").format(date); // 每次 new，GC 压力大
}
```

**方案二：ThreadLocal（繁琐）**

```java
private static final ThreadLocal<SimpleDateFormat> sdf =
    ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd HH:mm:ss"));

public static String format(Date date) {
    return sdf.get().format(date);
}
```

**方案三：加锁（性能差）**

```java
private static final SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");

public static synchronized String format(Date date) {
    return sdf.format(date); // 串行化，丧失并发优势
}
```

### 2.3 Java 8 方案

`DateTimeFormatter` 是**不可变且线程安全**的，可以直接作为常量共享：

```java
private static final DateTimeFormatter FORMATTER =
    DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

public static String format(LocalDateTime dateTime) {
    return FORMATTER.format(dateTime); // 线程安全，无需额外处理
}
```

---

## 三、Java 8 Time API 体系

Java 8 引入了全新的 `java.time` 包，由 Joda-Time 的作者 Stephen Colebourne 主导设计，遵循不可变、线程安全、领域驱动的设计原则。

### 3.1 LocalDate / LocalTime / LocalDateTime

**LocalDate**：仅表示日期（年-月-日），不包含时间和时区。

```java
LocalDate today = LocalDate.now();                    // 2024-12-25
LocalDate specific = LocalDate.of(2024, 12, 25);      // 2024-12-25
LocalDate parsed = LocalDate.parse("2024-12-25");     // 默认 ISO 格式

// 获取字段
int year = today.getYear();            // 2024
int month = today.getMonthValue();     // 12
Month monthEnum = today.getMonth();    // DECEMBER
int day = today.getDayOfMonth();       // 25
DayOfWeek dow = today.getDayOfWeek();  // WEDNESDAY
```

**LocalTime**：仅表示时间（时:分:秒.纳秒），不包含日期和时区。

```java
LocalTime now = LocalTime.now();                      // 14:30:00.123456789
LocalTime specific = LocalTime.of(14, 30, 0);         // 14:30:00
LocalTime parsed = LocalTime.parse("14:30:00");

int hour = now.getHour();          // 14
int minute = now.getMinute();      // 30
int second = now.getSecond();      // 0
int nano = now.getNano();          // 123456789
```

**LocalDateTime**：日期 + 时间的组合，不含时区。

```java
LocalDateTime now = LocalDateTime.now();
LocalDateTime specific = LocalDateTime.of(2024, 12, 25, 14, 30, 0);
LocalDateTime fromParts = LocalDateTime.of(LocalDate.of(2024, 12, 25),
                                             LocalTime.of(14, 30));

LocalDate date = now.toLocalDate();     // 提取日期部分
LocalTime time = now.toLocalTime();     // 提取时间部分
```

**不可变性操作**：所有修改操作都返回新实例，原对象不变。

```java
LocalDate date = LocalDate.of(2024, 12, 25);

LocalDate tomorrow = date.plusDays(1);      // 2024-12-26
LocalDate nextMonth = date.plusMonths(1);   // 2025-01-25
LocalDate nextYear = date.plusYears(1);     // 2025-12-25

LocalDate yesterday = date.minusDays(1);    // 2024-12-24
LocalDate lastMonth = date.minusMonths(1);  // 2024-11-25

// 直接设置字段（同样返回新实例）
LocalDate changed = date.withYear(2025);        // 2025-12-25
LocalDate firstDay = date.withDayOfMonth(1);    // 2024-12-01

// 原对象不变
System.out.println(date);   // 仍是 2024-12-25
```

### 3.2 Instant（时间戳）

`Instant` 表示 UTC 时间轴上的一个精确时刻，精度可达纳秒。相当于旧 API 中 `new Date().getTime()` 的现代化替代。

```java
Instant now = Instant.now();                    // 2024-12-25T06:30:00.123456789Z

// 从毫秒/秒创建
Instant fromMillis = Instant.ofEpochMilli(1703484600000L);
Instant fromSeconds = Instant.ofEpochSecond(1703484600L);

// 获取时间戳
long millis = now.toEpochMilli();    // 毫秒级时间戳
long seconds = now.getEpochSecond(); // 秒级时间戳
int nanos = now.getNano();           // 纳秒部分

// 时间运算
Instant later = now.plusSeconds(60);
Instant earlier = now.minus(1, ChronoUnit.HOURS);

// 比较
boolean isBefore = now.isBefore(later);   // true
boolean isAfter = now.isAfter(earlier);   // true
```

> **注意**：`Instant` 只表示时间轴上的点，不包含时区信息。它始终以 UTC 为基准。

### 3.3 Duration 和 Period

**Duration**：表示两个时间点之间的时间量（基于秒和纳秒），适用于时间层面的计算。

```java
Instant start = Instant.now();
// ... 执行某操作 ...
Instant end = Instant.now();

Duration duration = Duration.between(start, end);

long millis = duration.toMillis();      // 总毫秒数
long seconds = duration.getSeconds();   // 总秒数
int nanos = duration.getNano();         // 纳秒部分
long minutes = duration.toMinutes();    // 总分钟数
long hours = duration.toHours();        // 总小时数
long days = duration.toDays();          // 总天数

// 创建 Duration
Duration twoHours = Duration.ofHours(2);
Duration threeMinutes = Duration.ofMinutes(3);
Duration halfSecond = Duration.ofMillis(500);

// Duration 运算
Duration total = Duration.ofHours(1).plusMinutes(30);  // PT1H30M
Duration diff = Duration.ofHours(2).minusMinutes(15);  // PT1H45M

// 与 LocalTime 配合
LocalTime t1 = LocalTime.of(9, 0);
LocalTime t2 = LocalTime.of(17, 30);
Duration workTime = Duration.between(t1, t2);  // PT8H30M
```

**Period**：表示两个日期之间的日期量（基于年、月、日），适用于日期层面的计算。

```java
LocalDate startDate = LocalDate.of(2020, 3, 15);
LocalDate endDate = LocalDate.of(2024, 12, 25);

Period period = Period.between(startDate, endDate);

int years = period.getYears();   // 4
int months = period.getMonths(); // 9
int days = period.getDays();     // 10

// 创建 Period
Period oneYear = Period.ofYears(1);
Period threeMonths = Period.ofMonths(3);
Period twoWeeks = Period.ofWeeks(2);
Period custom = Period.of(2, 6, 15); // 2年6个月15天

// Period 运算
Period total = Period.ofYears(1).plusMonths(6);  // P1Y6M
Period normalized = Period.ofMonths(14).normalized(); // P1Y2M
```

| 对比项 | Duration | Period |
|--------|----------|--------|
| 时间单位 | 秒 + 纳秒 | 年 + 月 + 日 |
| 精度 | 纳秒级 | 天级 |
| 适用场景 | 时间差、耗时统计 | 年龄计算、日期间隔 |
| 创建方式 | `Duration.between(Instant, Instant)` | `Period.between(LocalDate, LocalDate)` |
| ISO 格式 | `PT2H30M15S` | `P2Y6M15D` |
| 是否考虑闰秒 | 不考虑 | 考虑日历语义 |

### 3.4 ZoneId 和 ZonedDateTime

**ZoneId**：表示时区标识符。

```java
// 系统默认时区
ZoneId systemZone = ZoneId.systemDefault();  // Asia/Shanghai

// 指定时区
ZoneId shanghai = ZoneId.of("Asia/Shanghai");
ZoneId tokyo = ZoneId.of("Asia/Tokyo");
ZoneId newYork = ZoneId.of("America/New_York");
ZoneId utc = ZoneId.of("UTC");
ZoneId z = ZoneOffset.UTC;

// 获取所有可用时区
Set<String> allZones = ZoneId.getAvailableZoneIds();

// 带偏移量的时区
ZoneOffset offset = ZoneOffset.of("+08:00");
ZoneOffset offset2 = ZoneOffset.ofHours(8);
```

**ZonedDateTime**：带时区的完整日期时间。

```java
// 当前时间（指定时区）
ZonedDateTime nowShanghai = ZonedDateTime.now(ZoneId.of("Asia/Shanghai"));
ZonedDateTime nowTokyo = ZonedDateTime.now(ZoneId.of("Asia/Tokyo"));

// 从 LocalDateTime 转换
LocalDateTime ldt = LocalDateTime.of(2024, 12, 25, 14, 30);
ZonedDateTime zdt = ldt.atZone(ZoneId.of("Asia/Shanghai"));
// 2024-12-25T14:30+08:00[Asia/Shanghai]

// 时区转换
ZonedDateTime tokyoTime = zdt.withZoneSameInstant(ZoneId.of("Asia/Tokyo"));
// 2024-12-25T15:30+09:00[Asia/Tokyo]

// 保持本地时间不变，仅改时区
ZonedDateTime sameLocal = zdt.withZoneSameLocal(ZoneId.of("America/New_York"));
// 2024-12-25T14:30-05:00[America/New_York]

// 从 Instant 创建
Instant instant = Instant.now();
ZonedDateTime fromInstant = instant.atZone(ZoneId.of("Asia/Shanghai"));

// 提取各部分
LocalDate date = zdt.toLocalDate();
LocalTime time = zdt.toLocalTime();
LocalDateTime dateTime = zdt.toLocalDateTime();
ZoneId zone = zdt.getZone();
ZoneOffset offset = zdt.getOffset();
```

### 3.5 DateTimeFormatter（线程安全的格式化器）

`DateTimeFormatter` 是**不可变且线程安全**的，可以直接定义为常量。

```java
// 预定义格式
DateTimeFormatter isoDate = DateTimeFormatter.ISO_LOCAL_DATE;       // 2024-12-25
DateTimeFormatter isoDateTime = DateTimeFormatter.ISO_LOCAL_DATE_TIME; // 2024-12-25T14:30:00
DateTimeFormatter isoOffset = DateTimeFormatter.ISO_OFFSET_DATE_TIME;  // 2024-12-25T14:30:00+08:00

// 自定义格式
DateTimeFormatter custom = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
DateTimeFormatter chinese = DateTimeFormatter.ofPattern("yyyy年MM月dd日 HH时mm分ss秒");
DateTimeFormatter withZone = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss Z");

// 带时区的格式化
DateTimeFormatter zonedFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss Z [VV]")
    .withZone(ZoneId.of("Asia/Shanghai"));

// 格式化
LocalDateTime now = LocalDateTime.now();
String formatted = now.format(custom);                    // 2024-12-25 14:30:00
String formatted2 = custom.format(now);                   // 同上（两种写法等价）

// 解析
LocalDateTime parsed = LocalDateTime.parse("2024-12-25 14:30:00", custom);

// 格式化 ZonedDateTime
ZonedDateTime zdt = ZonedDateTime.now();
String zonedFormatted = zdt.format(zonedFormatter);
// 2024-12-25 14:30:00 +0800 [Asia/Shanghai]

// 解析日期（不带时间）
LocalDate date = LocalDate.parse("2024-12-25", DateTimeFormatter.ISO_LOCAL_DATE);

// Locale 支持
DateTimeFormatter french = DateTimeFormatter.ofPattern("d MMMM yyyy", Locale.FRENCH);
String frenchDate = LocalDate.now().format(french); // 25 decembre 2024
```

> **核心要点**：`DateTimeFormatter` 是不可变的，所有格式化/解析方法都不会修改内部状态，天然线程安全。

### 3.6 TemporalAdjusters（时间调节器）

`TemporalAdjusters` 提供了一组常用的时间调整策略，配合 `with()` 方法使用。

```java
import java.time.temporal.TemporalAdjusters;

LocalDate date = LocalDate.of(2024, 12, 25);

// 月的第一天/最后一天
LocalDate firstDayOfMonth = date.with(TemporalAdjusters.firstDayOfMonth()); // 2024-12-01
LocalDate lastDayOfMonth = date.with(TemporalAdjusters.lastDayOfMonth());   // 2024-12-31

// 年的第一天/最后一天
LocalDate firstDayOfYear = date.with(TemporalAdjusters.firstDayOfYear());   // 2024-01-01
LocalDate lastDayOfYear = date.with(TemporalAdjusters.lastDayOfYear());     // 2024-12-31

// 下一个/上一个指定的星期几
LocalDate nextMonday = date.with(TemporalAdjusters.next(DayOfWeek.MONDAY));      // 2024-12-30
LocalDate previousFriday = date.with(TemporalAdjusters.previous(DayOfWeek.FRIDAY)); // 2024-12-20

// 当月第一个/最后一个星期几
LocalDate firstMonday = date.with(TemporalAdjusters.firstInMonth(DayOfWeek.MONDAY)); // 2024-12-02
LocalDate lastFriday = date.with(TemporalAdjusters.lastInMonth(DayOfWeek.FRIDAY));   // 2024-12-27

// 下一个/上一个星期几（含当天）
LocalDate nextOrSameMonday = date.with(TemporalAdjusters.nextOrSame(DayOfWeek.MONDAY)); // 2024-12-30

// 自定义调节器
// 下一个工作日（跳过周六日）
LocalDate nextWorkDay = date.with(TemporalAdjusters.ofDateAdjuster(d -> {
    DayOfWeek dow = d.getDayOfWeek();
    if (dow == DayOfWeek.FRIDAY) return d.plusDays(3);
    if (dow == DayOfWeek.SATURDAY) return d.plusDays(2);
    return d.plusDays(1);
}));
```

**链式组合示例**：

```java
// 获取三个月后的第一个周一
LocalDate result = LocalDate.now()
    .plusMonths(3)
    .with(TemporalAdjusters.firstDayOfMonth())
    .with(TemporalAdjusters.nextOrSame(DayOfWeek.MONDAY));
```

---

## 四、与旧 API 的互操作

新旧 API 之间提供了转换方法，便于在迁移过程中渐进替换。

### 4.1 Date 与 Instant 互转

```java
// Date -> Instant
Date date = new Date();
Instant instant = date.toInstant();

// Instant -> Date
Instant now = Instant.now();
Date dateFromInstant = Date.from(now);

// Date -> LocalDateTime（需要时区）
LocalDateTime ldt = date.toInstant()
    .atZone(ZoneId.systemDefault())
    .toLocalDateTime();

// LocalDateTime -> Date
LocalDateTime localDateTime = LocalDateTime.now();
Date dateFromLdt = Date.from(localDateTime
    .atZone(ZoneId.systemDefault())
    .toInstant());
```

### 4.2 Calendar 与 ZonedDateTime 互转

```java
// Calendar -> ZonedDateTime
Calendar calendar = Calendar.getInstance();
ZonedDateTime zdt = calendar.toInstant()
    .atZone(calendar.getTimeZone().toZoneId());

// ZonedDateTime -> Calendar
ZonedDateTime now = ZonedDateTime.now();
Calendar cal = GregorianCalendar.from(now);
```

### 4.3 java.sql.Date 互操作

```java
// LocalDate -> java.sql.Date
LocalDate localDate = LocalDate.now();
java.sql.Date sqlDate = java.sql.Date.valueOf(localDate);

// java.sql.Date -> LocalDate
LocalDate fromSql = sqlDate.toLocalDate();

// LocalDateTime -> java.sql.Timestamp
LocalDateTime ldt = LocalDateTime.now();
java.sql.Timestamp timestamp = java.sql.Timestamp.valueOf(ldt);

// java.sql.Timestamp -> LocalDateTime
LocalDateTime fromTimestamp = timestamp.toLocalDateTime();
```

### 4.4 时区 ID 转换

```java
// java.util.TimeZone -> ZoneId
TimeZone tz = TimeZone.getTimeZone("Asia/Shanghai");
ZoneId zoneId = tz.toZoneId();

// ZoneId -> java.util.TimeZone
ZoneId zid = ZoneId.of("America/New_York");
TimeZone tzFromZoneId = TimeZone.getTimeZone(zid);
```

---

## 五、常用操作示例

### 5.1 计算年龄

```java
LocalDate birthDate = LocalDate.of(1990, 5, 15);
LocalDate today = LocalDate.now();
Period age = Period.between(birthDate, today);
System.out.println("年龄: " + age.getYears() + " 岁");
```

### 5.2 判断是否在某个时间段内

```java
LocalTime now = LocalTime.now();
LocalTime start = LocalTime.of(9, 0);
LocalTime end = LocalTime.of(18, 0);

boolean inRange = !now.isBefore(start) && !now.isAfter(end);
// 或使用 compareTo
boolean inRange2 = now.compareTo(start) >= 0 && now.compareTo(end) <= 0;
```

### 5.3 计算两个日期之间的工作日天数

```java
public static long countWorkDays(LocalDate start, LocalDate end) {
    long count = 0;
    LocalDate current = start;
    while (!current.isAfter(end)) {
        DayOfWeek dow = current.getDayOfWeek();
        if (dow != DayOfWeek.SATURDAY && dow != DayOfWeek.SUNDAY) {
            count++;
        }
        current = current.plusDays(1);
    }
    return count;
}
```

### 5.4 获取某月的所有日期

```java
public static List<LocalDate> getAllDatesInMonth(YearMonth yearMonth) {
    LocalDate start = yearMonth.atDay(1);
    LocalDate end = yearMonth.atEndOfMonth();

    return Stream.iterate(start, date -> date.plusDays(1))
        .limit(ChronoUnit.DAYS.between(start, end) + 1)
        .toList();
}
```

### 5.5 倒计时 / 计时器

```java
Instant deadline = Instant.now().plus(Duration.ofHours(2));

Duration remaining = Duration.between(Instant.now(), deadline);
long hours = remaining.toHours();
long minutes = remaining.toMinutesPart();
long seconds = remaining.toSecondsPart();
System.out.printf("剩余: %d小时%d分%d秒%n", hours, minutes, seconds);
```

### 5.6 格式化时区感知的时间

```java
// 面向全球用户的格式化
DateTimeFormatter formatter = DateTimeFormatter
    .ofPattern("yyyy-MM-dd HH:mm:ss")
    .withZone(ZoneId.of("Asia/Shanghai"));

Instant instant = Instant.now();
String formatted = formatter.format(instant);
// 自动将 Instant 转换为上海时区的时间显示
```

### 5.7 解析多种格式的日期字符串

```java
DateTimeFormatter[] formatters = {
    DateTimeFormatter.ofPattern("yyyy-MM-dd"),
    DateTimeFormatter.ofPattern("yyyy/MM/dd"),
    DateTimeFormatter.ofPattern("dd-MM-yyyy"),
    DateTimeFormatter.ISO_LOCAL_DATE
};

public static LocalDate parseDate(String input) {
    for (DateTimeFormatter formatter : formatters) {
        try {
            return LocalDate.parse(input, formatter);
        } catch (DateTimeParseException e) {
            // 尝试下一个格式
        }
    }
    throw new IllegalArgumentException("无法解析日期: " + input);
}
```

---

## 六、新旧 API 对比

| 特性 | 旧 API（java.util.Date / Calendar） | 新 API（java.time.*） |
|------|------|------|
| **不可变性** | Date 和 Calendar 都是可变的 | 所有核心类都是不可变的 |
| **线程安全** | SimpleDateFormat 非线程安全 | DateTimeFormatter 线程安全 |
| **设计一致性** | 月份从 0 开始、年份需减 1900 | 符合直觉，1=一月，直接用年份数字 |
| **包结构** | java.util + java.sql 混杂 | java.time 包下统一组织 |
| **可读性** | API 设计混乱，方法语义不清 | 领域驱动设计，方法名自解释 |
| **时区支持** | TimeZone + Calendar 间接支持 | ZoneId + ZonedDateTime 原生支持 |
| **时间运算** | Calendar.add()，容易出错 | plus/minus/with 链式操作 |
| **格式化** | SimpleDateFormat（非线程安全） | DateTimeFormatter（线程安全） |
| **ISO 8601** | 不支持原生解析 | 原生支持 ISO 8601 格式 |
| **扩展性** | 难以自定义 | TemporalAdjuster、TemporalField 等可扩展 |
| **精度** | 毫秒级 | 纳秒级 |
| **数据库兼容** | java.sql.Date / Timestamp | JDBC 4.2+ 直接支持 java.time 类型 |

---

## 七、java.time 包结构总览

```text
java.time
├── LocalDate          日期（不含时间、时区）
├── LocalTime          时间（不含日期、时区）
├── LocalDateTime      日期时间（不含时区）
├── Instant            时间轴上的瞬间（UTC 时间戳）
├── Duration           时间量（秒 + 纳秒）
├── Period             日期量（年 + 月 + 日）
├── Year               年
├── YearMonth          年月
├── MonthDay           月日
├── ZoneId             时区标识符
├── ZoneOffset         UTC 偏移量
├── ZonedDateTime      带时区的日期时间
├── OffsetDateTime     带 UTC 偏移的日期时间
├── OffsetTime         带 UTC 偏移的时间
├── DateTimeFormatter  日期时间格式化器（线程安全）
├── DayOfWeek          星期枚举
├── Month              月份枚举
└── temporal
    ├── TemporalAdjusters    时间调节器工具类
    ├── ChronoUnit           时间单位枚举
    └── ChronoField          时间字段枚举
```

> **核心原则**：`java.time` 中所有表示日期、时间、时区、格式化器的类都是**不可变的**。任何"修改"操作都会返回一个新实例，这保证了线程安全和值的不可变性。这是与旧 API 最根本的区别。

---

← [返回 Java 核心概念](../README.md)
