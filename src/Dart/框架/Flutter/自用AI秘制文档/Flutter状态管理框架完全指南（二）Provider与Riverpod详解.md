---
title: Flutter状态管理框架完全指南（二）Provider与Riverpod详解
date: 2026-05-14
footer: Trae编辑·AI创作
---

# Flutter状态管理框架完全指南（二）Provider与Riverpod详解

::: info 简介
本文详细介绍Provider和Riverpod的核心概念、API、配置方式和最佳实践。Riverpod是Provider的升级版，提供更好的类型安全和测试支持。
:::

## 1. Provider 基础

### 1.1 安装依赖

```yaml
dependencies:
  provider: ^6.0.0
```

### 1.2 基本用法

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => Counter(),
      child: const MyApp(),
    ),
  );
}

class Counter with ChangeNotifier {
  int _count = 0;

  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('Provider Demo')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('Count:'),
              Consumer<Counter>(
                builder: (context, counter, child) => Text(
                  '${counter.count}',
                  style: const TextStyle(fontSize: 24),
                ),
              ),
            ],
          ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () => context.read<Counter>().increment(),
          child: const Icon(Icons.add),
        ),
      ),
    );
  }
}
```

### 1.3 Provider 类型

| Provider类型 | 用途 |
|--------------|------|
| `Provider<T>` | 提供不可变值 |
| `ChangeNotifierProvider<T>` | 提供可变状态（需实现ChangeNotifier） |
| `StateProvider<T>` | 简单可变状态（基本类型） |
| `FutureProvider<T>` | 提供异步值 |
| `StreamProvider<T>` | 提供流数据 |
| `MultiProvider` | 组合多个Provider |

### 1.4 MultiProvider

```dart
MultiProvider(
  providers: [
    ChangeNotifierProvider(create: (context) => Counter()),
    Provider(create: (context) => ApiService()),
    FutureProvider(create: (context) => fetchUser()),
  ],
  child: const MyApp(),
)
```

### 1.5 读取Provider的方式

```dart
// 方式1：Consumer（推荐用于Builder）
Consumer<Counter>(
  builder: (context, counter, child) => Text('${counter.count}'),
)

// 方式2：Provider.of（需要监听时）
final counter = Provider.of<Counter>(context);

// 方式3：context.watch（监听变化）
final counter = context.watch<Counter>();

// 方式4：context.read（不监听，用于修改）
context.read<Counter>().increment();

// 方式5：Selector（仅监听特定属性）
Selector<Counter, int>(
  selector: (context, counter) => counter.count,
  builder: (context, count, child) => Text('$count'),
)
```

## 2. Riverpod 基础

### 2.1 安装依赖

```yaml
dependencies:
  flutter_riverpod: ^2.0.0
  riverpod_annotation: ^2.0.0

dev_dependencies:
  riverpod_generator: ^2.0.0
  build_runner: ^2.0.0
```

### 2.2 基本用法

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// 定义Provider
final counterProvider = StateProvider<int>((ref) => 0);

void main() {
  runApp(
    ProviderScope(
      child: const MyApp(),
    ),
  );
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 监听状态变化
    final count = ref.watch(counterProvider);

    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('Riverpod Demo')),
        body: Center(
          child: Text('Count: $count', style: const TextStyle(fontSize: 24)),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () {
            // 修改状态
            ref.read(counterProvider.notifier).state++;
          },
          child: const Icon(Icons.add),
        ),
      ),
    );
  }
}
```

### 2.3 Provider 类型

| Provider类型 | 用途 | 自动释放 |
|--------------|------|----------|
| `Provider<T>` | 提供不可变值 | 否 |
| `StateProvider<T>` | 简单可变状态 | 否 |
| `StateNotifierProvider<T>` | 复杂可变状态 | 否 |
| `NotifierProvider<T>` | 新API，替代StateNotifierProvider | 否 |
| `AsyncNotifierProvider<T>` | 异步状态管理 | 否 |
| `FutureProvider<T>` | 提供异步值 | 否 |
| `StreamProvider<T>` | 提供流数据 | 否 |
| `Family<T, Arg>` | 参数化Provider | 否 |
| `.autoDispose` | 自动释放 | 是 |

### 2.4 NotifierProvider（Riverpod 2.0新API）

```dart
class CounterNotifier extends Notifier<int> {
  @override
  int build() => 0;

  void increment() => state++;
  void decrement() => state--;
}

final counterProvider = NotifierProvider<CounterNotifier, int>(CounterNotifier.new);

// 使用
final count = ref.watch(counterProvider);
ref.read(counterProvider.notifier).increment();
```

### 2.5 AsyncNotifierProvider

```dart
class UserNotifier extends AsyncNotifier<User> {
  @override
  Future<User> build() async {
    return await fetchUser();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => fetchUser());
  }
}

final userProvider = AsyncNotifierProvider<UserNotifier, User>(UserNotifier.new);

// 使用
ref.watch(userProvider).when(
  loading: () => const CircularProgressIndicator(),
  error: (e, st) => Text('Error: $e'),
  data: (user) => UserWidget(user),
);
```

### 2.6 FutureProvider

```dart
final userProvider = FutureProvider((ref) async {
  final api = ref.watch(apiProvider);
  return await api.fetchUser();
});

// 使用
final user = ref.watch(userProvider);
```

### 2.7 Family Provider

```dart
final userProvider = FutureProvider.family<User, String>((ref, userId) async {
  return await fetchUserById(userId);
});

// 使用
final user = ref.watch(userProvider('123'));
```

### 2.8 AutoDispose

```dart
final counterProvider = StateProvider.autoDispose<int>((ref) => 0);

// 或使用keepAlive
final userProvider = FutureProvider((ref) async {
  ref.keepAlive();
  return await fetchUser();
});
```

## 3. Riverpod 高级特性

### 3.1 Select

```dart
// 仅监听特定属性
final userName = ref.watch(userProvider.select((user) => user.name));
```

### 3.2 Listen

```dart
ref.listen(counterProvider, (previous, next) {
  if (next >= 10) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Reached 10!')),
    );
  }
});
```

### 3.3 Refresh

```dart
// 强制刷新
ref.refresh(userProvider);
```

### 3.4 Invalidate

```dart
// 使Provider失效（下次访问时重新计算）
ref.invalidate(userProvider);
```

### 3.5 ProviderObserver

```dart
class MyObserver extends ProviderObserver {
  @override
  void didUpdateProvider(ProviderBase provider, Object? previousValue, Object? newValue) {
    debugPrint('${provider.name} changed: $newValue');
  }
}

ProviderScope(
  observers: [MyObserver()],
  child: const MyApp(),
)
```

### 3.6 Override

```dart
ProviderScope(
  overrides: [
    counterProvider.overrideWith((ref) => 10),
  ],
  child: const TestWidget(),
)
```

## 4. Riverpod 代码生成（riverpod_generator）

### 4.1 配置 build.yaml

```yaml
targets:
  $default:
    builders:
      riverpod_generator:
        options:
          generate_for:
            - lib/**/*.dart
```

### 4.2 使用 @riverpod 注解

```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'providers.g.dart';

@riverpod
int counter(CounterRef ref) {
  return 0;
}

@riverpod
Future<User> fetchUser(FetchUserRef ref) async {
  final api = ref.watch(apiProvider);
  return await api.getUser();
}

@riverpod
class Todos extends _$Todos {
  @override
  List<Todo> build() => [];

  void add(Todo todo) {
    state = [...state, todo];
  }

  void remove(String id) {
    state = state.where((t) => t.id != id).toList();
  }
}
```

### 4.3 运行代码生成

```bash
dart run build_runner watch
```

## 5. 测试

### 5.1 单元测试

```dart
void main() {
  test('counter increments', () async {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    expect(container.read(counterProvider), 0);
    container.read(counterProvider.notifier).increment();
    expect(container.read(counterProvider), 1);
  });

  test('fetchUser returns user', () async {
    final container = ProviderContainer(
      overrides: [
        apiProvider.overrideWith((ref) => MockApi()),
      ],
    );
    addTearDown(container.dispose);

    final user = await container.read(fetchUserProvider.future);
    expect(user.name, 'Test User');
  });
}
```

### 5.2 Widget测试

```dart
void main() {
  testWidgets('counter increments when button is tapped', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: const MyApp(),
      ),
    );

    expect(find.text('0'), findsOneWidget);
    await tester.tap(find.byIcon(Icons.add));
    await tester.pump();

    expect(find.text('1'), findsOneWidget);
  });
}
```

## 6. Provider vs Riverpod

| 特性 | Provider | Riverpod |
|------|----------|----------|
| 类型安全 | ⚠️ | ✅ |
| 测试友好 | ⚠️ | ✅ |
| 全局访问 | ❌ | ✅ |
| 自动释放 | ❌ | ✅ |
| 代码生成 | ❌ | ✅ |
| 嵌套Provider | 复杂 | 简单 |

## 7. 最佳实践

### 7.1 Provider组织

```dart
// lib/providers/counter_provider.dart
final counterProvider = NotifierProvider<CounterNotifier, int>(CounterNotifier.new);

// lib/providers/user_provider.dart
final userProvider = AsyncNotifierProvider<UserNotifier, User>(UserNotifier.new);

// lib/providers/index.dart
export 'counter_provider.dart';
export 'user_provider.dart';
```

### 7.2 使用 Consumer 优化性能

```dart
// 避免：整个widget重建
Widget build(BuildContext context, WidgetRef ref) {
  final count = ref.watch(counterProvider);
  return Scaffold(
    body: Center(child: Text('$count')),
  );
}

// 推荐：仅重建Text widget
Widget build(BuildContext context, WidgetRef ref) {
  return Scaffold(
    body: Center(
      child: Consumer(
        builder: (context, ref, child) {
          final count = ref.watch(counterProvider);
          return Text('$count');
        },
      ),
    ),
  );
}
```

### 7.3 错误处理

```dart
ref.watch(userProvider).when(
  loading: () => const CircularProgressIndicator(),
  error: (error, stack) => ErrorWidget(error),
  data: (user) => UserWidget(user),
);
```

### 7.4 缓存异步数据

```dart
final userProvider = FutureProvider((ref) async {
  ref.keepAlive(); // 保持缓存
  return await fetchUser();
});
```

## 8. 常见问题

### 8.1 ProviderNotFoundException

**问题**：尝试读取未提供的Provider

**解决方案**：确保Provider在Widget树中被正确提供

```dart
ProviderScope(
  overrides: [
    apiProvider.overrideWith((ref) => MyApi()),
  ],
  child: MyWidget(),
)
```

### 8.2 不必要的重建

**问题**：整个widget重建影响性能

**解决方案**：使用`select`或`Consumer`缩小监听范围

```dart
final userName = ref.watch(userProvider.select((u) => u.name));
```

### 8.3 循环依赖

**问题**：Provider之间互相依赖

**解决方案**：重新设计依赖结构，使用`ref.watch`延迟获取

---

**下一章**：[三、Bloc/Cubit详解](Flutter状态管理框架完全指南（三）Bloc与Cubit详解.md)
