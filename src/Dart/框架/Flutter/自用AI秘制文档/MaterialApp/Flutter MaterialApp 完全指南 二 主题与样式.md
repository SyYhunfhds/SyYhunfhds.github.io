---
title: Flutter MaterialApp 完全指南（二）主题与样式
date: 2026-05-14
footer: Trae编辑·AI创作
---

# Flutter MaterialApp 完全指南（二）主题与样式

::: info 简介
本文详细介绍 MaterialApp 的主题配置，包括 ThemeData、ColorScheme、Material 3 支持以及亮色/暗色主题切换。
:::

## 1. 主题属性概述

MaterialApp 提供了丰富的主题配置选项：

| 属性 | 类型 | 说明 |
|------|------|------|
| `theme` | `ThemeData?` | 亮色模式主题 |
| `darkTheme` | `ThemeData?` | 暗色模式主题 |
| `highContrastTheme` | `ThemeData?` | 高对比度亮色主题 |
| `highContrastDarkTheme` | `ThemeData?` | 高对比度暗色主题 |
| `themeMode` | `ThemeMode` | 主题模式（system/light/dark） |
| `themeAnimationDuration` | `Duration` | 主题切换动画时长 |
| `themeAnimationCurve` | `Curve` | 主题切换动画曲线 |

## 2. ThemeData 详解

### 2.1 ThemeData 构造器

```dart
ThemeData({
  VisualDensity? visualDensity,
  MaterialTapTargetSize? materialTapTargetSize,
  bool? useMaterial3,
  ColorScheme? colorScheme,
  Brightness? brightness,
  Color? colorSchemeSeed,
  Color? canvasColor,
  Color? scaffoldBackgroundColor,
  Color? cardColor,
  Color? dividerColor,
  Color? focusColor,
  Color? hoverColor,
  Color? highlightColor,
  Color? splashColor,
  InteractiveInkFeatureFactory? splashFactory,
  Color? selectedRowColor,
  Color? unselectedWidgetColor,
  Color? disabledColor,
  Color? buttonColor,
  ButtonThemeData? buttonTheme,
  Color? textTheme,
  ColorScheme? secondaryHeaderColor,
  Color? textSelectionColor,
  Color? cursorColor,
  Color? textSelectionHandleColor,
  Color? backgroundColor,
  Color? dialogBackgroundColor,
  Color? indicatorColor,
  Color? hintColor,
  Color? errorColor,
  Color? toggleableActiveColor,
  String? fontFamily,
  NoDefaultCupertinoThemeData? cupertinoOverrideTheme,
  PageTransitionsTheme? pageTransitionsTheme,
  Map<Type, Action>? actions,
  Map<LogicalKeySet, Intent>? shortcuts,
  ScrollbarThemeData? scrollbarTheme,
  TargetPlatform? platform,
  Map<String, String>? staticLabelBasePath,
  TextTheme? textTheme,
  AppBarTheme? appBarTheme,
  MaterialBarTheme? materialBarTheme,
  BottomAppBarTheme? bottomAppBarTheme,
  CardTheme? cardTheme,
  ChipThemeData? chipTheme,
  DialogTheme? dialogTheme,
  FloatingActionButtonThemeData? floatingActionButtonTheme,
  ListTileThemeData? listTileTheme,
  NavigationRailThemeData? navigationRailTheme,
  NavigationBarThemeData? navigationBarTheme,
  DrawerThemeData? drawerTheme,
  BottomSheetThemeData? bottomSheetTheme,
  PopupMenuThemeData? popupMenuTheme,
  MenuBarThemeData? menuBarTheme,
  MenuThemeData? menuTheme,
  SnackbarThemeData? snackBarTheme,
  TabBarTheme? tabBarTheme,
  TextSelectionThemeData? textSelectionTheme,
  TimePickerThemeData? timePickerTheme,
  ColorScheme? colorScheme,
  bool? applyElevationOverlayColor,
  InputDecorationTheme? inputDecorationTheme,
  Iterable<ThemeExtension>? extensions,
})
```

### 2.2 核心颜色配置

#### `colorScheme` 属性

ColorScheme 是基于 Material 规范的一组 45 种颜色，用于配置大多数组件的颜色属性。

```dart
ThemeData(
  colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
)
```

#### `colorSchemeSeed` 属性

通过单一种子颜色自动生成完整的 ColorScheme：

```dart
ThemeData(
  colorSchemeSeed: Colors.purple,
)
```

#### Material 3 的 ColorScheme 角色

| 角色 | 说明 |
|------|------|
| `primary` | 主要颜色，用于 FAB、突出按钮等关键组件 |
| `onPrimary` | 在 primary 上显示的文本和图标颜色 |
| `primaryContainer` | 主要容器颜色 |
| `onPrimaryContainer` | 在 primaryContainer 上显示的内容颜色 |
| `secondary` | 次要颜色，用于不太突出的组件 |
| `secondaryContainer` | 次要容器颜色 |
| `tertiary` | 第三颜色，用于平衡 primary 和 secondary |
| `error` | 错误颜色 |
| `surface` | 表面颜色，用于背景和大面积低强调区域 |
| `onSurface` | 在 surface 上显示的内容颜色 |

#### Material 3 的表面容器颜色

Material 3 引入了基于色调的表面容器：

| 颜色 | 说明 |
|------|------|
| `surfaceBright` | 亮表面 |
| `surfaceDim` | 暗表面 |
| `surfaceContainerLowest` | 最低容器表面 |
| `surfaceContainerLow` | 低容器表面 |
| `surfaceContainer` | 容器表面 |
| `surfaceContainerHigh` | 高容器表面 |
| `surfaceContainerHighest` | 最高容器表面 |

### 2.3 亮色/暗色主题配置

#### 基础配置

```dart
MaterialApp(
  theme: ThemeData(
    brightness: Brightness.light,
    primarySwatch: Colors.blue,
    scaffoldBackgroundColor: Colors.grey[100],
  ),
  darkTheme: ThemeData(
    brightness: Brightness.dark,
    primarySwatch: Colors.blue,
    scaffoldBackgroundColor: Colors.grey[900],
  ),
  themeMode: ThemeMode.system,
)
```

#### `themeMode` 枚举

| 值 | 说明 |
|------|------|
| `ThemeMode.system` | 跟随系统设置（默认） |
| `ThemeMode.light` | 始终使用亮色主题 |
| `ThemeMode.dark` | 始终使用暗色主题 |

#### 使用 `ColorScheme.fromSeed`

```dart
ThemeData(
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.blue,
    brightness: Brightness.light,
  ),
)
```

## 3. 组件主题配置

### 3.1 AppBarTheme

```dart
ThemeData(
  appBarTheme: const AppBarTheme(
    backgroundColor: Colors.blue,
    foregroundColor: Colors.white,
    elevation: 2,
    centerTitle: true,
    titleTextStyle: TextStyle(
      fontSize: 20,
      fontWeight: FontWeight.bold,
      color: Colors.white,
    ),
  ),
)
```

### 3.2 CardTheme

```dart
ThemeData(
  cardTheme: CardTheme(
    color: Colors.white,
    elevation: 4,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
    ),
  ),
)
```

### 3.3 ButtonTheme

```dart
ThemeData(
  buttonTheme: ButtonThemeData(
    buttonColor: Colors.blue,
    textTheme: ButtonTextTheme.primary,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(8),
    ),
  ),
)
```

### 3.4 ElevatedButtonTheme

```dart
ThemeData(
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: Colors.blue,
      foregroundColor: Colors.white,
      elevation: 2,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
    ),
  ),
)
```

### 3.5 InputDecorationTheme

```dart
ThemeData(
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: Colors.grey[200],
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: BorderSide.none,
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: const BorderSide(color: Colors.blue, width: 2),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: const BorderSide(color: Colors.red, width: 2),
    ),
    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
  ),
)
```

### 3.6 DialogTheme

```dart
ThemeData(
  dialogTheme: DialogTheme(
    backgroundColor: Colors.white,
    elevation: 8,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(16),
    ),
    titleTextStyle: const TextStyle(
      fontSize: 20,
      fontWeight: FontWeight.bold,
      color: Colors.black87,
    ),
  ),
)
```

### 3.7 SnackbarThemeData

```dart
ThemeData(
  snackBarTheme: SnackBarThemeData(
    backgroundColor: Colors.grey[800],
    contentTextStyle: const TextStyle(color: Colors.white),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(8),
    ),
    behavior: SnackBarBehavior.floating,
  ),
)
```

### 3.8 TabBarTheme

```dart
ThemeData(
  tabBarTheme: const TabBarTheme(
    labelColor: Colors.blue,
    unselectedLabelColor: Colors.grey,
    indicatorColor: Colors.blue,
    indicatorSize: TabBarIndicatorSize.label,
  ),
)
```

### 3.9 FloatingActionButtonTheme

```dart
ThemeData(
  floatingActionButtonTheme: const FloatingActionButtonThemeData(
    backgroundColor: Colors.blue,
    foregroundColor: Colors.white,
    elevation: 6,
    shape: CircleBorder(),
  ),
)
```

### 3.10 BottomNavigationBarTheme

```dart
ThemeData(
  bottomNavigationBarTheme: const BottomNavigationBarThemeData(
    backgroundColor: Colors.white,
    selectedItemColor: Colors.blue,
    unselectedItemColor: Colors.grey,
    type: BottomNavigationBarType.fixed,
    elevation: 8,
  ),
)
```

### 3.11 NavigationBarTheme (Material 3)

```dart
ThemeData(
  navigationBarTheme: NavigationBarThemeData(
    backgroundColor: Colors.white,
    indicatorColor: Colors.blue.withOpacity(0.2),
    labelTextStyle: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.selected)) {
        return const TextStyle(fontSize: 12, fontWeight: FontWeight.w600);
      }
      return const TextStyle(fontSize: 12);
    }),
  ),
)
```

### 3.12 ChipThemeData

```dart
ThemeData(
  chipTheme: ChipThemeData(
    backgroundColor: Colors.grey[200],
    selectedColor: Colors.blue,
    labelStyle: const TextStyle(color: Colors.black87),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(8),
    ),
  ),
)
```

## 4. TextTheme 详解

TextTheme 定义了应用中所有文本的样式：

```dart
ThemeData(
  textTheme: const TextTheme(
    displayLarge: TextStyle(fontSize: 57, fontWeight: FontWeight.w400),
    displayMedium: TextStyle(fontSize: 45, fontWeight: FontWeight.w400),
    displaySmall: TextStyle(fontSize: 36, fontWeight: FontWeight.w400),
    headlineLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.w400),
    headlineMedium: TextStyle(fontSize: 28, fontWeight: FontWeight.w400),
    headlineSmall: TextStyle(fontSize: 24, fontWeight: FontWeight.w400),
    titleLarge: TextStyle(fontSize: 22, fontWeight: FontWeight.w500),
    titleMedium: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
    titleSmall: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
    bodyLarge: TextStyle(fontSize: 16, fontWeight: FontWeight.w400),
    bodyMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.w400),
    bodySmall: TextStyle(fontSize: 12, fontWeight: FontWeight.w400),
    labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
    labelMedium: TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
    labelSmall: TextStyle(fontSize: 11, fontWeight: FontWeight.w500),
  ),
)
```

## 5. Material 3 支持

### 5.1 启用 Material 3

```dart
ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
)
```

### 5.2 Material 3 特性

- 新的颜色系统（ColorScheme.fromSeed）
- 更现代化的组件设计
- 改进的无障碍支持
- 新的导航组件（NavigationBar、NavigationRail）

## 6. 主题扩展

### 6.1 使用 ThemeExtension

```dart
class MyThemeExtension extends ThemeExtension<MyThemeExtension> {
  final Color gradientColor;

  MyThemeExtension({required this.gradientColor});

  @override
  MyThemeExtension copyWith({Color? gradientColor}) {
    return MyThemeExtension(
      gradientColor: gradientColor ?? this.gradientColor,
    );
  }

  @override
  MyThemeExtension lerp(ThemeExtension<MyThemeExtension>? other, double t) {
    if (other is! MyThemeExtension) return this;
    return MyThemeExtension(
      gradientColor: Color.lerp(gradientColor, other.gradientColor, t)!,
    );
  }
}

ThemeData(
  extensions: [
    MyThemeExtension(gradientColor: Colors.purple),
  ],
)
```

### 6.2 访问主题扩展

```dart
final myExtension = Theme.of(context).extension<MyThemeExtension>();
```

## 7. 高对比度主题

```dart
MaterialApp(
  theme: ThemeData(
    colorScheme: ColorScheme.highContrastLight(colorSchemeSeed: Colors.blue),
  ),
  highContrastTheme: ThemeData(
    colorScheme: ColorScheme.highContrastLight(colorSchemeSeed: Colors.blue),
  ),
  highContrastDarkTheme: ThemeData(
    colorScheme: ColorScheme.highContrastDark(colorSchemeSeed: Colors.blue),
  ),
)
```

## 8. 完整示例

```dart
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Theme Demo',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
        ),
        cardTheme: CardTheme(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
      ),
      themeMode: ThemeMode.system,
      home: const ThemeDemoScreen(),
    );
  }
}
```

::: tip 最佳实践
1. 使用 `ColorScheme.fromSeed()` 统一生成配色方案
2. 启用 `useMaterial3: true` 以获得最新设计语言
3. 将主题配置集中在 ThemeData 中，便于维护
4. 使用 ThemeExtension 扩展自定义主题属性
:::

::: details 下篇预告
下一篇文章将详细介绍 MaterialApp 的导航与路由系统。
:::
