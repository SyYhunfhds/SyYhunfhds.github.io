---
title: Flutter状态管理框架完全指南（三）Bloc/Cubit详解
date: 2026-05-14
footer: Trae编辑·AI创作
---

# Flutter状态管理框架完全指南（三）Bloc/Cubit详解

::: info 简介
本文详细介绍Bloc/Cubit的核心概念、API、配置方式和最佳实践。Bloc是事件驱动的状态管理框架，适合大型复杂应用。
:::

## 1. Bloc 基础

### 1.1 安装依赖

```yaml
dependencies:
  flutter_bloc: ^8.0.0
  equatable: ^2.0.0
```

### 1.2 核心概念

```
Event → Bloc → State
  ↓       ↓       ↓
用户操作 → 业务逻辑 → UI状态
```

### 1.3 基本用法

```dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

// Event
abstract class CounterEvent extends Equatable {
  const CounterEvent();

  @override
  List<Object> get props => [];
}

class CounterIncrementPressed extends CounterEvent {}
class CounterDecrementPressed extends CounterEvent {}

// State
class CounterState extends Equatable {
  final int count;

  const CounterState({required this.count});

  @override
  List<Object> get props => [count];
}

// Bloc
class CounterBloc extends Bloc<CounterEvent, CounterState> {
  CounterBloc() : super(const CounterState(count: 0)) {
    on<CounterIncrementPressed>((event, emit) {
      emit(CounterState(count: state.count + 1));
    });

    on<CounterDecrementPressed>((event, emit) {
      emit(CounterState(count: state.count - 1));
    });
  }
}

// UI
void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => CounterBloc(),
      child: MaterialApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('Bloc Demo')),
          body: BlocBuilder<CounterBloc, CounterState>(
            builder: (context, state) {
              return Center(
                child: Text('Count: ${state.count}', style: const TextStyle(fontSize: 24)),
              );
            },
          ),
          floatingActionButton: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              FloatingActionButton(
                onPressed: () => context.read<CounterBloc>().add(CounterDecrementPressed()),
                child: const Icon(Icons.remove),
              ),
              const SizedBox(width: 10),
              FloatingActionButton(
                onPressed: () => context.read<CounterBloc>().add(CounterIncrementPressed()),
                child: const Icon(Icons.add),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

## 2. Cubit 基础

### 2.1 什么是 Cubit

Cubit是Bloc的简化版本，不需要Event类，直接通过方法改变状态。

```dart
class CounterCubit extends Cubit<int> {
  CounterCubit() : super(0);

  void increment() => emit(state + 1);
  void decrement() => emit(state - 1);
}

// 使用
BlocProvider(
  create: (context) => CounterCubit(),
  child: BlocBuilder<CounterCubit, int>(
    builder: (context, state) => Text('$state'),
  ),
)
```

### 2.2 Bloc vs Cubit

| 特性 | Bloc | Cubit |
|------|------|-------|
| Event驱动 | ✅ | ❌ |
| 方法调用 | ❌ | ✅ |
| 复杂度 | 高 | 低 |
| 适用场景 | 复杂业务 | 简单状态 |

## 3. Bloc 高级用法

### 3.1 异步操作

```dart
class WeatherBloc extends Bloc<WeatherEvent, WeatherState> {
  WeatherBloc() : super(const WeatherInitial()) {
    on<FetchWeather>(_onFetchWeather);
  }

  Future<void> _onFetchWeather(FetchWeather event, Emitter<WeatherState> emit) async {
    emit(const WeatherLoading());
    try {
      final weather = await WeatherRepository.fetchWeather(event.city);
      emit(WeatherLoaded(weather));
    } catch (e) {
      emit(const WeatherError('Failed to fetch weather'));
    }
  }
}

abstract class WeatherEvent extends Equatable {
  const WeatherEvent();
  @override
  List<Object> get props => [];
}

class FetchWeather extends WeatherEvent {
  final String city;
  const FetchWeather({required this.city});
  @override
  List<Object> get props => [city];
}

abstract class WeatherState extends Equatable {
  const WeatherState();
  @override
  List<Object> get props => [];
}

class WeatherInitial extends WeatherState {}
class WeatherLoading extends WeatherState {}
class WeatherLoaded extends WeatherState {
  final Weather weather;
  const WeatherLoaded(this.weather);
  @override
  List<Object> get props => [weather];
}
class WeatherError extends WeatherState {
  final String message;
  const WeatherError(this.message);
  @override
  List<Object> get props => [message];
}
```

### 3.2 转换操作符

```dart
class CounterBloc extends Bloc<CounterEvent, CounterState> {
  CounterBloc() : super(const CounterState(count: 0)) {
    on<CounterIncrementPressed>(
      (event, emit) => emit(CounterState(count: state.count + 1)),
      transformer: restartable(),
    );
  }
}
```

常用转换操作符：
- `restartable()`：取消之前的操作
- `debounceTime(Duration)`：防抖
- `switchMap()`：切换流
- `exhaustMap()`：忽略新事件直到当前完成

### 3.3 BlocListener

```dart
BlocListener<CounterBloc, CounterState>(
  listener: (context, state) {
    if (state.count >= 10) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Reached 10!')),
      );
    }
  },
  child: BlocBuilder<CounterBloc, CounterState>(
    builder: (context, state) => Text('${state.count}'),
  ),
)
```

### 3.4 BlocConsumer

```dart
BlocConsumer<CounterBloc, CounterState>(
  listener: (context, state) {
    // 监听状态变化
  },
  builder: (context, state) {
    return Text('${state.count}');
  },
)
```

### 3.5 MultiBlocProvider

```dart
MultiBlocProvider(
  providers: [
    BlocProvider<CounterBloc>(create: (context) => CounterBloc()),
    BlocProvider<ThemeBloc>(create: (context) => ThemeBloc()),
  ],
  child: const MyApp(),
)
```

### 3.6 BlocSelector

```dart
BlocSelector<CounterBloc, CounterState, bool>(
  selector: (state) => state.count > 5,
  builder: (context, isGreaterThanFive) {
    return Text(isGreaterThanFive ? 'Greater than 5' : 'Less than or equal to 5');
  },
)
```

## 4. 状态转换

### 4.1 多个状态转换

```dart
on<SomeEvent>(
  (event, emit) async {
    emit(Loading());
    
    await Future.delayed(const Duration(seconds: 1));
    
    if (something) {
      emit(Success());
    } else {
      emit(Failure());
    }
  },
);
```

### 4.2 条件发射

```dart
on<IncrementEvent>(
  (event, emit) {
    if (state.count < 10) {
      emit(CounterState(count: state.count + 1));
    }
  },
);
```

## 5. 测试

### 5.1 bloc_test

```yaml
dev_dependencies:
  bloc_test: ^9.0.0
  mocktail: ^1.0.0
```

```dart
void main() {
  group('CounterBloc', () {
    late CounterBloc counterBloc;

    setUp(() {
      counterBloc = CounterBloc();
    });

    tearDown(() {
      counterBloc.close();
    });

    test('initial state is CounterState(count: 0)', () {
      expect(counterBloc.state, const CounterState(count: 0));
    });

    blocTest<CounterBloc, CounterState>(
      'emits [CounterState(count: 1)] when CounterIncrementPressed is added',
      build: () => counterBloc,
      act: (bloc) => bloc.add(const CounterIncrementPressed()),
      expect: () => const [CounterState(count: 1)],
    );

    blocTest<CounterBloc, CounterState>(
      'emits [CounterState(count: -1)] when CounterDecrementPressed is added',
      build: () => counterBloc,
      act: (bloc) => bloc.add(const CounterDecrementPressed()),
      expect: () => const [CounterState(count: -1)],
    );
  });
}
```

### 5.2 异步测试

```dart
blocTest<WeatherBloc, WeatherState>(
  'emits [WeatherLoading, WeatherLoaded] when FetchWeather is added',
  build: () => WeatherBloc(),
  act: (bloc) => bloc.add(const FetchWeather(city: 'London')),
  expect: () => [
    const WeatherLoading(),
    const WeatherLoaded(Weather(temperature: 20)),
  ],
);
```

## 6. BlocObserver

```dart
class MyBlocObserver extends BlocObserver {
  @override
  void onCreate(BlocBase bloc) {
    super.onCreate(bloc);
    debugPrint('Bloc created: ${bloc.runtimeType}');
  }

  @override
  void onEvent(Bloc bloc, Object? event) {
    super.onEvent(bloc, event);
    debugPrint('Event: $event');
  }

  @override
  void onTransition(Bloc bloc, Transition transition) {
    super.onTransition(bloc, transition);
    debugPrint('Transition: ${transition.currentState} -> ${transition.nextState}');
  }

  @override
  void onError(BlocBase bloc, Object error, StackTrace stackTrace) {
    debugPrint('Error: $error');
    super.onError(bloc, error, stackTrace);
  }

  @override
  void onClose(BlocBase bloc) {
    super.onClose(bloc);
    debugPrint('Bloc closed: ${bloc.runtimeType}');
  }
}

void main() {
  Bloc.observer = MyBlocObserver();
  runApp(const MyApp());
}
```

## 7. 项目结构

### 7.1 Feature-Based 结构

```
lib/
├── features/
│   ├── counter/
│   │   ├── counter_bloc.dart
│   │   ├── counter_event.dart
│   │   ├── counter_state.dart
│   │   └── counter_screen.dart
│   └── weather/
│       ├── weather_bloc.dart
│       ├── weather_event.dart
│       ├── weather_state.dart
│       └── weather_screen.dart
├── shared/
│   ├── repositories/
│   └── models/
└── main.dart
```

### 7.2 状态管理层

```
lib/
├── presentation/
│   └── screens/
├── domain/
│   └── usecases/
├── data/
│   ├── repositories/
│   └── datasources/
└── state/
    ├── blocs/
    │   ├── counter/
    │   └── weather/
    └── cubits/
```

## 8. 最佳实践

### 8.1 状态不可变

```dart
// 推荐：使用不可变状态
@immutable
class UserState {
  final User? user;
  final bool isLoading;

  const UserState({this.user, this.isLoading = false});

  UserState copyWith({User? user, bool? isLoading}) {
    return UserState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

// 使用
emit(state.copyWith(isLoading: true));
emit(state.copyWith(user: user, isLoading: false));
```

### 8.2 使用 Equatable

```dart
class UserState extends Equatable {
  final User? user;
  final bool isLoading;

  const UserState({this.user, this.isLoading = false});

  @override
  List<Object?> get props => [user, isLoading];
}
```

### 8.3 单一职责

```dart
// 一个Bloc只处理一个功能域
class AuthBloc extends Bloc<AuthEvent, AuthState> { ... }
class UserBloc extends Bloc<UserEvent, UserState> { ... }
class ThemeBloc extends Bloc<ThemeEvent, ThemeState> { ... }
```

### 8.4 依赖注入

```dart
class WeatherBloc extends Bloc<WeatherEvent, WeatherState> {
  final WeatherRepository repository;

  WeatherBloc({required this.repository}) : super(const WeatherInitial()) {
    on<FetchWeather>(_onFetchWeather);
  }

  Future<void> _onFetchWeather(FetchWeather event, Emitter<WeatherState> emit) async {
    emit(const WeatherLoading());
    try {
      final weather = await repository.fetchWeather(event.city);
      emit(WeatherLoaded(weather));
    } catch (e) {
      emit(const WeatherError('Failed'));
    }
  }
}

// 提供依赖
BlocProvider(
  create: (context) => WeatherBloc(
    repository: context.read<WeatherRepository>(),
  ),
  child: const WeatherScreen(),
)
```

### 8.5 资源清理

```dart
class MyBloc extends Bloc<MyEvent, MyState> {
  late StreamSubscription _subscription;

  MyBloc() : super(const MyInitial()) {
    _subscription = someStream.listen((data) {
      add(SomeEvent(data));
    });
  }

  @override
  Future<void> close() {
    _subscription.cancel();
    return super.close();
  }
}
```

## 9. 常见问题

### 9.1 State未更新

**问题**：emit后UI没有重建

**解决方案**：确保状态是新对象，使用Equatable

```dart
// 错误：修改现有状态
state.user.name = 'New Name'; // 不会触发更新

// 正确：创建新状态
emit(state.copyWith(user: state.user.copyWith(name: 'New Name')));
```

### 9.2 内存泄漏

**问题**：Bloc未正确关闭

**解决方案**：使用BlocProvider自动管理生命周期

```dart
BlocProvider(
  create: (context) => MyBloc(), // 自动dispose
  child: const MyWidget(),
)
```

### 9.3 异步操作竞争

**问题**：多次触发异步操作导致状态不一致

**解决方案**：使用转换操作符

```dart
on<FetchData>(
  _onFetchData,
  transformer: restartable(), // 取消之前的请求
);
```

---

**下一章**：[四、GetX与MobX详解](Flutter状态管理框架完全指南（四）GetX与MobX详解.md)
