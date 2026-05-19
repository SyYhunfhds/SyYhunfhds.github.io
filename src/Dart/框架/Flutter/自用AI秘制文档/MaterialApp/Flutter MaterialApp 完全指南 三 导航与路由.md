---
title: Flutter MaterialApp 完全指南（三）导航与路由
date: 2026-05-14
footer: Trae编辑·AI创作
---

# Flutter MaterialApp 完全指南（三）导航与路由

::: info 简介
本文详细介绍 Flutter 中的导航与路由系统，包括基本导航、命名路由、动态路由、路由传参以及自定义转场动画。
:::

## 1. 路由基础

### 1.1 Navigator 概述

`Navigator` 是 Flutter 中管理页面栈的核心组件，遵循栈的 FILO（后进先出）原则：

- **push**：将新页面压入栈顶
- **pop**：将页面从栈顶弹出
- **replace**：替换栈顶页面

### 1.2 MaterialApp 路由搜索顺序

```
1. home 属性（处理 '/' 路由）
2. routes 表（静态路由）
3. onGenerateRoute（动态路由）
4. onUnknownRoute（未知路由/404）
```

## 2. 基本导航

### 2.1 Navigator.push

```dart
// 导航到新页面
Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => const SecondScreen()),
);

// 从新页面返回
Navigator.pop(context);
```

### 2.2 传递参数

```dart
// 方式一：通过构造函数传递
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => DetailScreen(itemId: 1),
  ),
);

// 方式二：通过 settings.arguments 传递
Navigator.pushNamed(
  context,
  '/details',
  arguments: {'id': 1, 'name': 'Item 1'},
);
```

### 2.3 返回参数

```dart
// 导航并等待返回结果
final result = await Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => SelectionScreen()),
);

if (result != null) {
  print('Selected: $result');
}

// 返回结果
Navigator.pop(context, 'Selected Value');
```

## 3. 命名路由

### 3.1 定义路由

```dart
MaterialApp(
  initialRoute: '/',
  routes: {
    '/': (context) => const HomeScreen(),
    '/second': (context) => const SecondScreen(),
    '/details': (context) => const DetailsScreen(),
  },
)
```

### 3.2 使用命名路由导航

```dart
// 基本导航
Navigator.pushNamed(context, '/second');

// 带参数导航
Navigator.pushNamed(
  context,
  '/details',
  arguments: {'id': 42, 'name': 'Product'},
);

// 替换当前路由
Navigator.pushReplacementNamed(context, '/home');

// 弹出并导航
Navigator.pushNamedAndRemoveUntil(
  context,
  '/home',
  (route) => false, // 移除所有路由
);
```

### 3.3 接收命名路由参数

```dart
class DetailsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final args = ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;

    return Scaffold(
      appBar: AppBar(title: const Text('Details')),
      body: Center(
        child: Text('ID: ${args['id']}, Name: ${args['name']}'),
      ),
    );
  }
}
```

## 4. 动态路由 (onGenerateRoute)

### 4.1 基本用法

当需要处理动态路由（如 `/product/123`）时，使用 `onGenerateRoute`：

```dart
MaterialApp(
  onGenerateRoute: (settings) {
    if (settings.name == '/product') {
      final args = settings.arguments as Map<String, dynamic>;
      return MaterialPageRoute(
        builder: (context) => ProductScreen(id: args['id']),
        settings: settings,
      );
    }
    return null;
  },
)
```

### 4.2 路由模式匹配

```dart
MaterialApp(
  onGenerateRoute: (settings) {
    final uri = Uri.parse(settings.name ?? '');

    switch (uri.path) {
      case '/':
        return MaterialPageRoute(
          builder: (context) => const HomeScreen(),
          settings: settings,
        );

      case '/details':
        final id = uri.queryParameters['id'];
        final name = uri.queryParameters['name'];
        return MaterialPageRoute(
          builder: (context) => DetailsScreen(id: id, name: name),
          settings: settings,
        );

      case '/product':
        final productId = uri.pathSegments.length > 1 ? uri.pathSegments[1] : null;
        return MaterialPageRoute(
          builder: (context) => ProductScreen(id: productId),
          settings: settings,
        );

      default:
        return MaterialPageRoute(
          builder: (context) => const NotFoundScreen(),
          settings: settings,
        );
    }
  },
)
```

### 4.3 路由守卫

实现简单的路由权限控制：

```dart
MaterialApp(
  onGenerateRoute: (settings) {
    final isLoggedIn = UserManager.isLoggedIn;

    if (!isLoggedIn && settings.name != '/login') {
      return MaterialPageRoute(
        builder: (context) => const LoginScreen(),
        settings: const RouteSettings(name: '/login'),
      );
    }

    switch (settings.name) {
      case '/':
        return MaterialPageRoute(builder: (context) => const HomeScreen());
      case '/profile':
        return MaterialPageRoute(builder: (context) => const ProfileScreen());
      case '/login':
        return MaterialPageRoute(builder: (context) => const LoginScreen());
      default:
        return MaterialPageRoute(builder: (context) => const NotFoundScreen());
    }
  },
)
```

## 5. 未知路由处理 (onUnknownRoute)

```dart
MaterialApp(
  onUnknownRoute: (settings) {
    return MaterialPageRoute(
      builder: (context) => NotFoundScreen(
        routeName: settings.name,
      ),
    );
  },
)
```

## 6. 自定义页面转场动画

### 6.1 淡入淡出效果

```dart
Navigator.push(
  context,
  PageRouteBuilder(
    pageBuilder: (context, animation, secondaryAnimation) => const SecondScreen(),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      return FadeTransition(
        opacity: animation,
        child: child,
      );
    },
    transitionDuration: const Duration(milliseconds: 300),
  ),
);
```

### 6.2 滑动效果

```dart
Navigator.push(
  context,
  PageRouteBuilder(
    pageBuilder: (context, animation, secondaryAnimation) => const SecondScreen(),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      const begin = Offset(1.0, 0.0);
      const end = Offset.zero;
      const curve = Curves.easeInOut;

      var tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));

      return SlideTransition(
        position: animation.drive(tween),
        child: child,
      );
    },
  ),
);
```

### 6.3 缩放效果

```dart
Navigator.push(
  context,
  PageRouteBuilder(
    pageBuilder: (context, animation, secondaryAnimation) => const SecondScreen(),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      return ScaleTransition(
        scale: Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(parent: animation, curve: Curves.easeInOut),
        ),
        child: child,
      );
    },
  ),
);
```

### 6.4 全局自定义转场

通过 `PageTransitionsTheme` 为所有路由设置统一动画：

```dart
ThemeData(
  pageTransitionsTheme: const PageTransitionsTheme(
    builders: {
      TargetPlatform.android: CupertinoPageTransitionsBuilder(),
      TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
    },
  ),
)
```

## 7. 嵌套导航

### 7.1 应用场景

嵌套导航适用于独立的页面流程，如应用内的设置向导：

```
/setup/find_devices
/setup/select_device
/setup/connecting
/setup/finished
```

### 7.2 实现嵌套导航

```dart
const routePrefixDeviceSetup = '/setup/';
const routeDeviceSetupStartPage = 'find_devices';

MaterialApp(
  onGenerateRoute: (settings) {
    if (settings.name == '/') {
      return MaterialPageRoute(builder: (context) => const HomeScreen());
    } else if (settings.name!.startsWith(routePrefixDeviceSetup)) {
      final subRoute = settings.name!.substring(routePrefixDeviceSetup.length);
      return MaterialPageRoute(
        builder: (context) => SetupFlow(setupPageRoute: subRoute),
        settings: settings,
      );
    }
    return null;
  },
)

// SetupFlow 是一个独立的 Navigator
class SetupFlow extends StatefulWidget {
  const SetupFlow({super.key, required this.setupPageRoute});

  @override
  State<SetupFlow> createState() => _SetupFlowState();
}

class _SetupFlowState extends State<SetupFlow> {
  @override
  Widget build(BuildContext context) {
    return Navigator(
      onGenerateRoute: (settings) {
        switch (settings.name) {
          case 'find_devices':
            return MaterialPageRoute(builder: (context) => const FindDevicesPage());
          case 'select_device':
            return MaterialPageRoute(builder: (context) => const SelectDevicePage());
          case 'connecting':
            return MaterialPageRoute(builder: (context) => const ConnectingPage());
          case 'finished':
            return MaterialPageRoute(builder: (context) => const FinishedPage());
          default:
            return MaterialPageRoute(builder: (context) => const FindDevicesPage());
        }
      },
    );
  }
}
```

## 8. Hero 动画

### 8.1 基本 Hero 动画

```dart
// 页面 A
Hero(
  tag: 'hero_image',
  child: Image.network('https://example.com/image.jpg'),
)

// 页面 B
Hero(
  tag: 'hero_image',
  child: Image.network('https://example.com/image.jpg'),
)
```

### 8.2 Hero 动画与路由

MaterialApp 会自动配置顶层 Navigator 的 observer 来执行 Hero 动画。

## 9. 路由堆栈操作

### 9.1 基本操作

```dart
// 压入新路由
Navigator.push(context, route);

// 弹出当前路由
Navigator.pop(context);

// 弹出直到某个条件
Navigator.popUntil(context, (route) => route.isFirst);

// 替换当前路由
Navigator.pushReplacement(context, route);

// 替换直到某个条件
Navigator.pushReplacementUntil(context, newRoute, (route) => route.isFirst);

// 移除并压入
Navigator.pushAndRemoveUntil(context, route, (route) => false);
```

### 9.2 maybePop

```dart
// 如果可以弹出则弹出，否则什么都不做
Navigator.maybePop(context);
```

## 10. 完整示例

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
      title: 'Navigation Demo',
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      onGenerateRoute: (settings) {
        final uri = Uri.parse(settings.name ?? '');

        switch (uri.path) {
          case '/':
            return MaterialPageRoute(
              builder: (context) => const HomeScreen(),
              settings: settings,
            );

          case '/details':
            final id = uri.queryParameters['id'];
            final name = uri.queryParameters['name'];
            return MaterialPageRoute(
              builder: (context) => DetailsScreen(id: id, name: name),
              settings: settings,
            );

          default:
            return MaterialPageRoute(
              builder: (context) => const NotFoundScreen(),
              settings: settings,
            );
        }
      },
      onUnknownRoute: (settings) {
        return MaterialPageRoute(
          builder: (context) => const NotFoundScreen(),
        );
      },
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Home')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/details', arguments: {'id': 1});
              },
              child: const Text('Go to Details (Arguments)'),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/details?id=42&name=Product');
              },
              child: const Text('Go to Details (Query Params)'),
            ),
          ],
        ),
      ),
    );
  }
}

class DetailsScreen extends StatelessWidget {
  final String? id;
  final String? name;

  const DetailsScreen({super.key, this.id, this.name});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Details')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('ID: ${id ?? 'N/A'}'),
            Text('Name: ${name ?? 'N/A'}'),
          ],
        ),
      ),
    );
  }
}

class NotFoundScreen extends StatelessWidget {
  const NotFoundScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('404')),
      body: const Center(child: Text('Page not found')),
    );
  }
}
```

::: tip 最佳实践
1. 使用 `onGenerateRoute` 处理动态路由，便于统一管理
2. 路由名称使用常量定义，避免硬编码字符串
3. 使用 `arguments` 传递复杂对象，使用 query parameters 传递简单参数
4. 始终提供 `onUnknownRoute` 处理 404 情况
5. 复杂的页面流程使用嵌套 Navigator
:::

::: warning 注意事项
- 如果设置了 `home`，不能同时在 `routes` 中定义 `/`
- `Navigator.push` 和 `Navigator.pushNamed` 在没有可用路由时会抛出异常
- 在 iOS 上使用 `CupertinoPageTransitionsBuilder` 可获得原生滑动返回效果
:::

::: details 下篇预告
下一篇文章将详细介绍 MaterialApp 的本地化配置和调试工具。
:::
