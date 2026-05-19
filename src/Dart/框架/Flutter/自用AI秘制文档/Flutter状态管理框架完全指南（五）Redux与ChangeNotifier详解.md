---
title: Flutter状态管理框架完全指南（五）Redux与ChangeNotifier详解
date: 2026-05-14
footer: Trae编辑·AI创作
---

# Flutter状态管理框架完全指南（五）Redux与ChangeNotifier详解

::: info 简介
本文详细介绍Redux和ChangeNotifier的核心概念、API、配置方式和最佳实践。Redux是函数式状态管理，ChangeNotifier是Flutter内置的状态管理方案。
:::

## 1. ChangeNotifier 基础

### 1.1 什么是 ChangeNotifier

ChangeNotifier是Flutter SDK内置的状态管理类，基于观察者模式实现。

```dart
import 'package:flutter/foundation.dart';

class Counter extends ChangeNotifier {
  int _count = 0;

  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }

  void decrement() {
    _count--;
    notifyListeners();
  }
}
```

### 1.2 与 Provider 结合使用

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

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('ChangeNotifier Demo')),
        body: Center(
          child: Consumer<Counter>(
            builder: (context, counter, child) => Text(
              'Count: ${counter.count}',
              style: const TextStyle(fontSize: 24),
            ),
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

### 1.3 多个状态管理

```dart
class User extends ChangeNotifier {
  String _name = '';
  int _age = 0;

  String get name => _name;
  int get age => _age;

  void updateName(String name) {
    _name = name;
    notifyListeners();
  }

  void updateAge(int age) {
    _age = age;
    notifyListeners();
  }
}
```

### 1.4 嵌套监听

```dart
class AppState extends ChangeNotifier {
  final Counter _counter = Counter();
  final User _user = User();

  Counter get counter => _counter;
  User get user => _user;

  AppState() {
    _counter.addListener(notifyListeners);
    _user.addListener(notifyListeners);
  }

  @override
  void dispose() {
    _counter.dispose();
    _user.dispose();
    super.dispose();
  }
}
```

## 2. Redux 基础

### 2.1 安装依赖

```yaml
dependencies:
  flutter_redux: ^0.10.0
  redux: ^5.0.0
```

### 2.2 核心概念

```
Action → Reducer → Store → View
  ↓        ↓        ↓       ↓
用户操作 → 纯函数 → 状态 → UI
```

### 2.3 基本用法

```dart
import 'package:flutter_redux/flutter_redux.dart';
import 'package:redux/redux.dart';

// State
class AppState {
  final int count;

  AppState({required this.count});

  AppState copyWith({int? count}) {
    return AppState(count: count ?? this.count);
  }
}

// Actions
enum CounterAction { increment, decrement }

// Reducer
AppState counterReducer(AppState state, dynamic action) {
  switch (action) {
    case CounterAction.increment:
      return state.copyWith(count: state.count + 1);
    case CounterAction.decrement:
      return state.copyWith(count: state.count - 1);
    default:
      return state;
  }
}

void main() {
  final store = Store<AppState>(
    counterReducer,
    initialState: AppState(count: 0),
  );

  runApp(
    StoreProvider<AppState>(
      store: store,
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('Redux Demo')),
        body: Center(
          child: StoreConnector<AppState, int>(
            converter: (store) => store.state.count,
            builder: (context, count) => Text(
              'Count: $count',
              style: const TextStyle(fontSize: 24),
            ),
          ),
        ),
        floatingActionButton: Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            FloatingActionButton(
              onPressed: () => StoreProvider.of<AppState>(context).dispatch(CounterAction.decrement),
              child: const Icon(Icons.remove),
            ),
            const SizedBox(width: 10),
            FloatingActionButton(
              onPressed: () => StoreProvider.of<AppState>(context).dispatch(CounterAction.increment),
              child: const Icon(Icons.add),
            ),
          ],
        ),
      ),
    );
  }
}
```

### 2.4 Action 类

```dart
class IncrementAction {
  final int amount;
  const IncrementAction({this.amount = 1});
}

class DecrementAction {
  final int amount;
  const DecrementAction({this.amount = 1});
}

AppState counterReducer(AppState state, dynamic action) {
  if (action is IncrementAction) {
    return state.copyWith(count: state.count + action.amount);
  } else if (action is DecrementAction) {
    return state.copyWith(count: state.count - action.amount);
  }
  return state;
}
```

### 2.5 Middleware

```dart
final loggingMiddleware = Middleware<AppState>((store, action, next) {
  print('Action: $action');
  print('Before: ${store.state.count}');
  next(action);
  print('After: ${store.state.count}');
});

final store = Store<AppState>(
  counterReducer,
  initialState: AppState(count: 0),
  middleware: [loggingMiddleware],
);
```

### 2.6 异步 Middleware

```dart
final thunkMiddleware = Middleware<AppState>((store, action, next) {
  if (action is Future) {
    action.then((result) => store.dispatch(result));
    return;
  }
  next(action);
});

// 使用
store.dispatch(Future.delayed(
  const Duration(seconds: 1),
  () => const IncrementAction(),
));
```

### 2.7 组合 Reducers

```dart
AppState appReducer(AppState state, dynamic action) {
  return AppState(
    count: counterReducer(state.count, action),
    user: userReducer(state.user, action),
  );
}
```

## 3. Redux 高级用法

### 3.1 StoreConnector

```dart
StoreConnector<AppState, ViewModel>(
  converter: (store) => ViewModel(
    count: store.state.count,
    onIncrement: () => store.dispatch(const IncrementAction()),
  ),
  builder: (context, viewModel) {
    return Column(
      children: [
        Text('${viewModel.count}'),
        ElevatedButton(
          onPressed: viewModel.onIncrement,
          child: const Text('Increment'),
        ),
      ],
    );
  },
)
```

### 3.2 StoreBuilder

```dart
StoreBuilder<AppState>(
  builder: (context, store) {
    return Text('${store.state.count}');
  },
)
```

### 3.3 时间旅行调试

```dart
final store = Store<AppState>(
  counterReducer,
  initialState: AppState(count: 0),
  middleware: [
    // 添加时间旅行中间件
    // 需要额外配置
  ],
);
```

## 4. ChangeNotifier vs Redux

| 特性 | ChangeNotifier | Redux |
|------|----------------|-------|
| 复杂度 | 低 | 高 |
| 样板代码 | 少 | 多 |
| 可预测性 | ⚠️ | ✅ |
| 时间旅行 | ❌ | ✅ |
| 异步支持 | 手动 | Middleware |
| 测试友好 | ⚠️ | ✅ |

## 5. 最佳实践

### 5.1 ChangeNotifier 最佳实践

```dart
class Counter extends ChangeNotifier {
  int _count = 0;

  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }
}

// 使用Consumer避免不必要的重建
Consumer<Counter>(
  builder: (context, counter, child) => Text('${counter.count}'),
)
```

### 5.2 Redux 最佳实践

```dart
// 组织代码结构
lib/
├── redux/
│   ├── state/
│   │   └── app_state.dart
│   ├── actions/
│   │   ├── counter_actions.dart
│   │   └── user_actions.dart
│   ├── reducers/
│   │   ├── counter_reducer.dart
│   │   ├── user_reducer.dart
│   │   └── app_reducer.dart
│   ├── middleware/
│   │   └── logging_middleware.dart
│   └── store.dart
└── main.dart
```

### 5.3 性能优化

```dart
// ChangeNotifier: 使用Selector
Selector<Counter, int>(
  selector: (context, counter) => counter.count,
  builder: (context, count, child) => Text('$count'),
)

// Redux: 使用distinct
StoreConnector<AppState, int>(
  distinct: true,
  converter: (store) => store.state.count,
  builder: (context, count) => Text('$count'),
)
```

### 5.4 测试

```dart
// ChangeNotifier测试
void main() {
  test('counter increments', () {
    final counter = Counter();
    expect(counter.count, 0);
    counter.increment();
    expect(counter.count, 1);
  });
}

// Redux测试
void main() {
  test('counter reducer', () {
    final state = AppState(count: 0);
    final newState = counterReducer(state, CounterAction.increment);
    expect(newState.count, 1);
  });
}
```

## 6. 常见问题

### 6.1 ChangeNotifier内存泄漏

**问题**：ChangeNotifier没有被正确dispose

**解决方案**：使用Provider自动管理生命周期

```dart
ChangeNotifierProvider(
  create: (context) => Counter(), // 自动dispose
  child: const MyWidget(),
)
```

### 6.2 Redux状态未更新

**问题**：Reducer没有返回新状态

**解决方案**：确保返回新状态对象

```dart
// 错误
state.count++; // 直接修改状态

// 正确
return state.copyWith(count: state.count + 1); // 返回新状态
```

### 6.3 不必要的重建

**问题**：整个widget重建影响性能

**解决方案**：使用Selector或distinct

```dart
Selector<Counter, int>(
  selector: (context, counter) => counter.count,
  builder: (context, count, child) => Text('$count'),
)
```

---

**下一章**：[六、最佳实践与选型指南](Flutter状态管理框架完全指南（六）最佳实践与选型指南.md)
