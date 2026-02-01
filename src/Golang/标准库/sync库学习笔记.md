---
title: golang sync库学习笔记
date: 2026-01-17
---
[[toc]]
***
## 前言
### `sync`库主要内容
:::note
Go 语言的哲学是 **“不要通过共享内存来通信，而要通过通信来共享内存”**（即使用 Channel）。但在实际开发中，有些场景（如高性能缓存、状态同步、单例模式等）使用 sync 库提供的低级同步原语会更高效。
:::
- **核心锁原语**
	*这是最常用的部分，用于保护共享资源不被并发竞争（Race Condition）破坏。*
	1. **`sync.Mutex` (互斥锁)**
	    - **作用**：最基础的锁。同一时刻只允许一个 Goroutine 进入临界区。
	    - **核心方法**：`Lock()`, `Unlock()`。
	2. **`sync.RWMutex` (读写互斥锁)**
	    - **作用**：读写分离锁。允许多个 Goroutine 同时读，但只允许一个 Goroutine 写。写锁会阻塞所有的读和写。
	    - **适用场景**：读多写少的场景（如配置信息读取）。
	    - **核心方法**：`RLock()`, `RUnlock()` (读锁)；`Lock()`, `Unlock()` (写锁)。
- **并发流程控制**
	*用于控制多个 Goroutine 之间的执行顺序或生命周期。*
1. **`sync.WaitGroup` (等待组)**
    - **作用**：等待一组 Goroutine 全部执行完毕。
    - **场景**：主进程等待所有协程结束。
    - **核心方法**：`Add()`, `Done()`, `Wait()`。
2. **`sync.Once` (单次执行)**
    - **作用**：确保某个操作在程序运行期间只执行一次。
    - **场景**：单例模式加载、配置初始化。即便被几千个 Goroutine 同时调用，也只有第一个能成功执行。
    - **核心方法**：Do(func())。
3. **`sync.Cond` (条件变量)**
    - **作用**：让一组 Goroutine 在某个条件未满足时进入阻塞，直到被唤醒。
    - **场景**：典型的生产者-消费者模型，或者某个任务需要等待特定信号才开始。
    - **核心方法**：`Wait()`, `Signal()`, `Broadcast()`。
- **并发容器与对象复用**
	*通常用于解决 **性能优化** 和 **线程安全容器** 的问题*
	1. **`sync.Map` (并发安全 Map)**
    - **作用**：线程安全的键值对存储。
    - **为什么需要它**：Go 原生的 map 在并发读写时会直接 panic。虽然可以用 Mutex + map，但 sync.Map 在特定场景下性能更高。
    - **设计点**：减少锁竞争（内部使用了读写分离和原子操作）。
	2. **`sync.Pool` (临时对象池)**
	    - **作用**：缓存已分配但暂未使用的对象，下次使用时直接取出，而不是重新申请内存。
	    - **核心目的**：**减轻 GC（垃圾回收）压力**，提高内存使用效率。
	    - **典型应用**：gin 框架里的 Context 对象复用、fmt 包内部的缓冲区复用。
:::note

|          |                 |                         |
| -------- | --------------- | ----------------------- |
| 维度       | sync.Pool       | **原生 Channel 池 (推荐)**   |
| **复用率**  | 低（会被 GC 频繁清空）   | **高（只要你不想关，它就不死）**      |
| **资源控制** | 弱（无法主动清理）       | **强（支持 Shutdown 遍历清理）** |
| **适用频率** | 高频（微秒/毫秒级）      | **低频（秒/分钟级）**           |
| **复杂逻辑** | 难以实现 TTL 或健康检查  | **轻松实现过期逻辑和坏死判断**       |
| **结论**   | 不适合长周期、有句柄的对象   | 适合长周期、有句柄的对象            |
| **标签**   | **无状态小对象的短波缓冲** | **有状态资源的生命周期管家**        |

:::
**辅助包**
*虽然不在 sync 包的主目录下，但它们是同步机制的基石*

 1. **`sync/atomic` (原子操作)**
    - **作用**：利用 CPU 指令保证变量操作的原子性（无锁化）。
    - **特点**：比 Mutex 更轻量，性能极高。常用于计数器（如统计请求数）。
2. **`golang.org/x/sync/...` (扩展包)**
    - 虽然不是标准库，但由官方维护。包含 `ErrGroup`（带错误返回的 WaitGroup）、`Semaphore`（信号量）等非常有用的工具。
## 开始
### `sync/atomic`
```go
package phrase_1_atomic_value  
  
import (  
    "context"  
    "fmt"    "log"    "os"    "os/signal"    "sync"    "sync/atomic"    "syscall"    "testing"    "time"  
    "github.com/brianvoe/gofakeit/v7")  
  
func atomicWorker(id string, stopped *atomic.Bool, wg *sync.WaitGroup) {  
    defer wg.Done()  
  
    ticker := time.NewTicker(time.Microsecond * 10)  
    defer ticker.Stop()  
  
    for {  
       select {  
       case <-ticker.C:  
          if stopped.Load() {  
             log.Printf("[%v] [%v]协程已退出", time.Now(), id)  
             return  
          }  
          // log.Printf("[%v] [%v]协程运行中……", time.Now(), id)  
       }  
    }  
}  
  
// 内存可见性  
/*  
atomic库能确保操作是原子的, 要么做完要么没做, 所有协程都能第一时间获取原子值的最新状态  
(*atomic.<T>) Load() 获取当前值  
(*atomic.<T>) Store(value T) 设置新值  
  
在特定情况下CPU会缓存协程的值, 导致协程无法获取最新的值; 这时候atomic.T类型可以确保内存可见性  
  
[10个协程]  
测试发现平均协程退出耗时大约为600毫秒, 这主要是因为worker内部使用计时器模拟耗时操作, 难免有些时候跑得慢一些  
将模拟计时器调至10毫秒一次后, 平均协程退出时间也降至10毫秒以内  
进一步下调至100微秒后，平均协程退出时间大约为500微秒, 此后继续下调模拟周期, 平均耗时也不再变化  
[100协程] 10微秒模拟耗时 平均退出耗时为1000微秒+  
*/  
func _TestMemoryVisibility(t *testing.T) {  
    t.Parallel()  
  
    var stopped atomic.Bool  
    workerSize := 100  
    workerWait := sync.WaitGroup{}  
    for i := 0; i < workerSize; i++ {  
       workerWait.Add(1)  
       go atomicWorker(gofakeit.UUID(), &stopped, &workerWait)  
    }  
    done := make(chan struct{}, 1)  
    go func() {  
       workerWait.Wait()  
       done <- struct{}{}  
    }()  
  
    ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)  
    defer cancel()  
    ticker := time.NewTicker(time.Second * 1)  
    defer ticker.Stop()  
  
    var start, end time.Time  
    for {  
       select {  
       case <-ticker.C:  
          log.Printf("[%v] [main]协程运行中……", time.Now())  
       case <-ctx.Done():  
          start = time.Now()  
          stopped.Store(true) // 关闭协程, 但可能要等到下次ticker才能触发  
          select {  
          case <-time.After(time.Millisecond * 1100):  
             log.Printf("子进程超时, 现强制退出程序")  
             t.Errorf("子进程超时")  
          case <-done:  
             log.Printf("子进程已退出")  
             log.Printf("[%v] [main]退出中……", time.Now())  
          }  
  
          goto Exit  
       }  
    }  
  
Exit:  
    end = time.Now()  
    log.Printf("关闭所有子协程耗时: %v 微秒", end.Sub(start).Microseconds())  
}  
  
// 无锁计数器  
/*  
atomic是硬件层面的优化, 真正无锁, 性能比RWMutex的方案快很多  
  
下面以字节计数作为业务模拟, 看atomic RWMutex和Mutex哪个方案在无延迟无ticker协程并发下能够最先达到目标字节数  
1024 * 1024 目标字节 单次递增至多1023字节 atomic mutex和RWMutex  
分别耗时: 417 670 892 (ms)  
这时候还是有调试日志的, 之后就都没有了  
  
2026/01/18 00:09:40 目标字节数: 1048576字节, 单次至多递增: 1023字节, 每组协程数: 100  
2026/01/18 00:09:40 atomic计数器方案耗时: 0 纳秒  
2026/01/18 00:09:40 mutex计数器方案耗时: 0 纳秒  
2026/01/18 00:09:40 rwmutex计数器方案耗时: 0 纳秒  
  
2026/01/18 00:09:58 目标字节数: 1048576字节, 单次至多递增: 1023字节, 每组协程数: 10  
2026/01/18 00:09:58 atomic计数器方案耗时: 0 纳秒  
2026/01/18 00:09:58 mutex计数器方案耗时: 749300 纳秒  
2026/01/18 00:09:58 rwmutex计数器方案耗时: 749300 纳秒  
  
2026/01/18 00:10:40 目标字节数: 1073741824字节, 单次至多递增: 1023字节, 每组协程数: 10  
2026/01/18 00:10:40 atomic计数器方案耗时: 211215900 纳秒  
2026/01/18 00:10:40 mutex计数器方案耗时: 504467400 纳秒  
2026/01/18 00:10:40 rwmutex计数器方案耗时: 567118400 纳秒  
  
2026/01/18 00:11:03 目标字节数: 1073741824字节, 单次至多递增: 1023字节, 每组协程数: 100  
2026/01/18 00:11:03 atomic计数器方案耗时: 195646300 纳秒  
2026/01/18 00:11:03 mutex计数器方案耗时: 501003700 纳秒  
2026/01/18 00:11:03 rwmutex计数器方案耗时: 581959600 纳秒  
*/  
type simpleResult struct {  
    Strategy string // 方案类型  
    TimeCost int64  // 单位: 微秒  
}  
  
func addByteLenAtomic(wg *sync.WaitGroup, targetLen uint64, maxDeltaLen uint64, currLen *atomic.Uint64, ctx context.Context, ch chan struct{}) {  
    defer wg.Done()  
    defer func() {  
       if err := recover(); err != nil {  
          // log.Printf("[%v] [%v]协程已退出, 错误: %v", time.Now(), "atomic", err)  
       }  
    }()  
  
    for {  
       select {  
       case <-ctx.Done():  
          return  
       default:  
          if currLen.Load()+maxDeltaLen >= targetLen {  
             // log.Printf("[%v] [%v]协程已退出", time.Now(), "atomic")  
             ch <- struct{}{}  
             return  
          }  
  
          currLen.Add(gofakeit.Uint64() % maxDeltaLen)  
          // log.Printf("[%v] [%v]已累计字节数: %v", time.Now(), "atomic", currLen.Load())  
       }  
    }  
}  
func addByteLenMutex(wg *sync.WaitGroup, targetLen uint64, maxDeltaLen uint64, currLen *uint64, mutex *sync.Mutex, ctx context.Context, ch chan struct{}) {  
    defer wg.Done()  
    defer func() {  
       if err := recover(); err != nil {  
          // log.Printf("[%v] [%v]协程已退出, 错误: %v", time.Now(), "mutex", err)  
       }  
    }()  
  
    for {  
       select {  
       case <-ctx.Done():  
          return  
       default:  
          mutex.Lock()  
          if *currLen+maxDeltaLen >= targetLen {  
             // log.Printf("[%v] [%v]协程已退出", time.Now(), "mutex")  
             ch <- struct{}{}  
             return  
          }  
  
          *currLen += gofakeit.Uint64() % maxDeltaLen  
          // log.Printf("[%v] [%v]已累计字节数: %v", time.Now(), "mutex", *currLen)  
          mutex.Unlock()  
       }  
    }  
}  
  
func addByteLenRWMutex(wg *sync.WaitGroup, targetLen uint64, maxDeltaLen uint64, currLen *uint64, rwMutex *sync.RWMutex, ctx context.Context, ch chan struct{}) {  
    defer wg.Done()  
    defer func() {  
       if err := recover(); err != nil {  
          // log.Printf("[%v] [%v]协程已退出, 错误: %v", time.Now(), "rwmutex", err)  
       }  
    }()  
  
    for {  
       select {  
       case <-ctx.Done():  
          return  
       default:  
          rwMutex.RLock()  
          if *currLen+maxDeltaLen >= targetLen {  
             // log.Printf("[%v] [%v]协程达到预定字节, 已退出", time.Now(), "rwmutex")  
             ch <- struct{}{}  
             return  
          }  
          rwMutex.RUnlock()  
  
          rwMutex.Lock()  
          *currLen += gofakeit.Uint64() % maxDeltaLen  
          // log.Printf("[%v] [%v]已累计字节数: %v", time.Now(), "rwmutex", *currLen)  
          rwMutex.Unlock()  
       }  
    }  
}  
  
func _TestNoLockCounter(t *testing.T) {  
    var atomicWG, mutexWG, rwMutexWG sync.WaitGroup  
    var (  
       atomicStart, atomicEnd   time.Time  
       mutexStart, mutexEnd     time.Time  
       rwMutexStart, rwMutexEnd time.Time  
    )  
    var (  
       atomicCurrLen                atomic.Uint64  
       mutexCurrLen, rwMutexCurrLen uint64  
    )  
    var (  
       atomicCtx, atomicCancel   = context.WithCancel(context.Background())  
       mutexCtx, mutexCancel     = context.WithCancel(context.Background())  
       rwMutexCtx, rwMutexCancel = context.WithCancel(context.Background())  
    )  
  
    defer atomicCancel()  
    defer mutexCancel()  
    defer rwMutexCancel()  
    maxByteLen := uint64(1024) // 单次模拟至多加多少字节  
    targetByteLen := uint64(1024 * 1024 * 1024)  
  
    mutex := sync.Mutex{}  
    rwMutex := sync.RWMutex{}  
  
    workerSize := 100  
    var (  
       atomicDone, mutexDone, rwMutexDone = make(chan struct{}, workerSize), make(chan struct{}, workerSize), make(chan struct{}, workerSize)  
    )  
    for i := 0; i < workerSize; i++ {  
       atomicWG.Add(1)  
       mutexWG.Add(1)  
       rwMutexWG.Add(1)  
  
       go addByteLenAtomic(&atomicWG, targetByteLen, maxByteLen, &atomicCurrLen, atomicCtx, atomicDone)  
       go addByteLenMutex(&mutexWG, targetByteLen, maxByteLen, &mutexCurrLen, &mutex, mutexCtx, mutexDone)  
       go addByteLenRWMutex(&rwMutexWG, targetByteLen, maxByteLen, &rwMutexCurrLen, &rwMutex, rwMutexCtx, rwMutexDone)  
    }  
    atomicStart, mutexStart, rwMutexStart = time.Now(), time.Now(), time.Now()  
  
    listenerWG := sync.WaitGroup{}  
    listenerWG.Add(3)  
    go func() {  
       <-atomicDone  
       atomicEnd = time.Now()  
  
       listenerWG.Done()  
    }()  
    go func() {  
       <-mutexDone  
       mutexEnd = time.Now()  
  
       listenerWG.Done()  
    }()  
    go func() {  
       <-rwMutexDone  
       rwMutexEnd = time.Now()  
  
       listenerWG.Done()  
    }()  
    listenerWG.Wait()  
    goto Exit  
  
Exit:  
    log.Printf("目标字节数: %v字节, 单次至多递增: %v字节, 每组协程数: %v", targetByteLen, maxByteLen-1, workerSize)  
    log.Printf("atomic计数器方案耗时: %v 纳秒", atomicEnd.Sub(atomicStart).Nanoseconds())  
    log.Printf("mutex计数器方案耗时: %v 纳秒", mutexEnd.Sub(mutexStart).Nanoseconds())  
    log.Printf("rwmutex计数器方案耗时: %v 纳秒", rwMutexEnd.Sub(rwMutexStart).Nanoseconds())  
}  
  
// CompareAndSwap  
/*  
这是原子操作的精髓。它实现的是 “乐观锁”：不加锁，但我保证只有抢到的人能干活。  
逻辑定义：CompareAndSwap(old, new)  
    “如果当前值是 old，就把它改成 new，并告诉我成功了。”  
    “如果当前值不是 old（说明别人抢先动了它），我就什么也不做，并告诉我失败了。”  
  
场景：抢占式任务（谁快谁处理）  
假设多个监控协程发现某个节点挂了，只需要一个协程去发送报警邮件。  
  
var alertState atomic.Int32 // 0: 未报警, 1: 正在报警  
  
func tryAlert() {  
    // 逻辑：如果当前是 0，我就改成 1。抢到的人返回 true    if alertState.CompareAndSwap(0, 1) {        fmt.Println("抢占成功，我来发报警邮件！")  
    } else {        fmt.Println("别人已经在发了，我直接跳过。")  
    }}  

*/  
  
// 原子修改  
/*  
利用 atomic.Value 将整个 Config 当作一个原子整体。  
```go  
var globalConfig atomic.Value  
  
// 更新配置  
newConf := &Config{IP: "1.1.1.1", Tags: []string{"A", "B"}}  
globalConfig.Store(newConf) // 一次性“拍”进去，瞬间生效  
  
// 读取配置（不需要锁，极快）  
conf := globalConfig.Load().(*Config)  
fmt.Println(conf.IP)  

*/  
  
// 第一阶段练习：构建一个“透明”的采集控制器  
/*  
任务要求：  
    计数：使用 atomic.Uint64 记录当前活跃的连接数。  
    开关：使用 atomic.Bool 控制全局暂停。  
    状态机：使用 CAS 实现一个“健康检查”的状态转换。只有状态从 IDLE 变到 CHECKING 的协程才能执行探测，探测完变回 IDLE。  
    要求：        启动 5 个并发协程。  
        主协程随机切换“暂停”状态。  
        不要使用 sync.Mutex 或 Channel 来传递这些状态（以此强制自己使用 atomic）。  
*/  
var (  
    idle     uint64 = 0  
    checking uint64 = 1  
)  
  
func init() {  
    _ = gofakeit.Seed(time.Now().UnixNano())  
}  
  
func counterWorker(wg *sync.WaitGroup, ctx context.Context, workerID string, workerStatus *atomic.Uint64,  
    activeCounter *atomic.Uint64, globalPause *atomic.Bool) {  
    defer wg.Done()  
    for {  
       select {  
       case <-ctx.Done(): // 习惯性地就写了context作为协程退出依据  
          return  
       default:  
          if globalPause.Load() {  
             // 暂停状态，不处理  
             continue  
          }  
  
          // 反向使用CompareAndSwap  
          // 如果已经是checking状态, 那就可以执行探测  
          if workerStatus.CompareAndSwap(idle, checking) {  
             // 模拟耗时任务  
             activeCounter.Add(1)  
             log.Printf("[%v] [%v]协程开始执行任务", time.Now().UnixNano(), workerID)  
             time.Sleep(time.Duration(gofakeit.Uint64()%1000) * time.Millisecond)  
             activeCounter.Store(activeCounter.Load() - 1)  
             log.Printf("[%v] [%v]协程任务结束", time.Now().UnixNano(), workerID)  
  
             workerStatus.Store(idle) // 状态切换不要放在if-else块外面, 不然可能被其他协程修改  
          } else {  
  
          }  
          /*  
             假设协程 A 抢到了票，把状态改成了 checking。  
             协程 B 进来，CAS 失败了（因为现在是 checking），它进入 else 分支（空的）。  
             关键点：协程 B 紧接着执行了下方的 workerStatus.Store(idle)。  
             结果：没抢到票的人（B）把抢到票的人（A）设置的门栓给拔掉了！  
             于是协程 C 进来发现是 idle，也冲进去了…… 最终导致门形同虚设。  
          */  
          // workerStatus.Store(idle) // 这种写法难免会有竞争冲突, 实测发现连接数能稳定在4个(总协程数为5)  
       }  
    }  
}  
  
/*  
日志的冰山一角  
  
...  
2026/01/18 00:47:08 当前活跃连接数: 4  
2026/01/18 00:47:08 [2026-01-18 00:47:08.1941801 +0800 CST m=+1.011532401] 暂停全局任务  
...  
2026/01/18 00:47:09 当前活跃连接数: 0  
...  
2026/01/18 00:47:09 [2026-01-18 00:47:09.1943183 +0800 CST m=+2.011670601] 恢复全局任务  
...  
2026/01/18 00:47:10 当前活跃连接数: 4  
...  
2026/01/18 00:47:11 收到interrupt信号，现在等待协程退出  
2026/01/18 00:47:11 测试结束  
*/  
func TestPhrase1(t *testing.T) {  
    workerSize := 5  
    workerWG := sync.WaitGroup{} // 主协程需要这个来确保能够正常关闭测试样例  
  
    var activeCounter atomic.Uint64  
    var globalPause atomic.Bool  
    var uniqueStatus atomic.Uint64 // 全局共用一个状态, 便于协程自己知道什么时候可以探测  
    ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)  
    defer cancel()  
  
    // 启动协程  
    for i := 0; i < workerSize; i++ {  
       workerWG.Add(1)  
       workerID := fmt.Sprintf("worker-%v", i+1)  
       go counterWorker(&workerWG, ctx, workerID, &uniqueStatus, &activeCounter, &globalPause)  
    }  
  
    ticker := time.NewTicker(time.Second)  
    defer ticker.Stop()  
  
    for {  
       select {  
       case <-ticker.C:  
          log.Printf("当前活跃连接数: %v", activeCounter.Load())  
  
          // 随机判断是否开启或关闭全局暂停  
          if gofakeit.Bool() {  
             // 开启暂停  
             globalPause.Store(true)  
             log.Printf("[%v] 暂停全局任务", time.Now())  
          } else {  
             // 关闭暂停  
             globalPause.Store(false)  
             log.Printf("[%v] 恢复全局任务", time.Now())  
          }  
  
       case <-ctx.Done():  
          log.Println("收到interrupt信号，现在等待协程退出")  
  
          workerWG.Wait()  
          goto Exit  
       }  
    }  
Exit:  
    log.Println("测试结束")  
}
```
### `sync/errgroup`
```go
package phrase_2_errgroup  
  
import (  
    "context"  
    "fmt"    "log"    "sync/atomic"    "testing"    "time"  
    "github.com/brianvoe/gofakeit/v7"    "golang.org/x/sync/errgroup" // 不是标准库, 要手动下载  
)  
  
// errgroup  
/*  
在并发编程中，启动协程很容易，但管理一组协程的生命周期很难。errgroup 解决的就是：“如何让一组任务同生共死，并优雅地处理第一个发生的错误。”  
  
对比一下两者的思维方式：  
    sync.WaitGroup (工具人模式)：  
        你告诉它：“我有 10 个活，你数着。”  
        干完一个减一个。  
        如果中间有人干坏了、报错了，WaitGroup 毫不知情，它只管数字归零。  
    x/sync/errgroup (特种作战模式)：  
        你告诉它：“你们 10 个人是一个小队。”  
        错误传播：只要有一个人报告失败（返回 error），小组长立刻记录下这个错误。  
        级联取消：一旦有人失败，小组长会立刻向其他所有人发送“撤退信号”（取消 Context）。  
        结果汇总：Wait() 不仅等结束，还会告诉你第一个出错的原因是什么。  
*/  
// 核心API  
/*  
(1) errgroup.WithContext(ctx)  
    作用：初始化。它返回一个 Group 对象和一个新的 ctx。  
    关键点：这个新 ctx 的生命周期与 Group 绑定。只要 Group 中任何一个任务返回了非 nil 的 error，这个 ctx 就会立刻被取消。  
(2) g.Go(f func() error)  
    作用：替代 go func()。  
    要求：传入的函数必须返回一个 error。如果不报错，就返回 nil。  
(3) g.Wait()  
    作用：阻塞等待所有任务结束。  
    返回值：它返回第一个由子任务产生的 error。如果全员成功，返回 nil。  
*/  
  
// 并发限流器  
/*  
SetLimit (高级用法)  
  
在爬虫和监控中，你不能无限开启协程（比如扫描 1 万个 IP，不能瞬间开 1 万个协程）。在以前我们需要手写“带缓冲的 Channel”来限制并发。  
*/  
  
// 第二阶段: 练习  
/*  
构建一个带“熔断器”的集群探测器  
我们将模拟一个探测 20 个节点的任务。  
任务细节：  
    初始化：        使用 errgroup.WithContext。  
        设置并发上限为 3 (使用 g.SetLimit(3))。  
    启动循环：        启动 20 个子任务。  
    内部逻辑：        打印一条“节点 X 开始探测”的日志。  
        随机 time.Sleep 500ms 到 1500ms。  
        故障注入：如果任务 ID 是 8，让它返回 fmt.Errorf("节点 8 响应超时，触发集群熔断")。  
        信号监听：所有任务在执行 Sleep 期间或前后，必须检查 ctx.Done()。如果收到信号，打印“节点 X 停止探测，释放资源”并退出。  
    结果输出：        主协程通过 g.Wait() 获取错误并打印。  
*/  
// 业务上仍然模拟活跃连接数  
  
func counterWorker(ctx context.Context, workerID string,  
    activeCounter *atomic.Uint64) error {  
    for {  
       select {  
       case <-ctx.Done():  
          // log.Printf("检测到协程组有任务出现异常, [%v]协程将退出", workerID)  
          return nil  
       default:  
          // 随机决定是模拟探测还是模拟异常  
          if gofakeit.Bool() {  
             log.Printf("[%v] [%v]协程开始执行任务", time.Now().UnixNano(), workerID)  
             time.Sleep(time.Duration(gofakeit.Uint64()%1000) * time.Millisecond)  
             activeCounter.Store(activeCounter.Load() - 1)  
             log.Printf("[%v] [%v]协程任务结束", time.Now().UnixNano(), workerID)  
          } else {  
             return fmt.Errorf("[%v] [%v]协程任务异常", time.Now().UnixNano(), workerID)  
          }  
       }  
    }  
}  
func TestPhrase2Errgroup(t *testing.T) {  
    var totalWorker = 20  
    var maxConcurrentWorker = 3  
  
    g, ctx := errgroup.WithContext(context.Background())  
    g.SetLimit(maxConcurrentWorker) // 设置并发上限  
    var activeCounter atomic.Uint64  
  
    // 监听活跃连接数  
    go func(ctx context.Context) {  
       for {  
          select {  
          case <-ctx.Done():  
             log.Printf("检测到协程组有任务出现异常, 关闭监听")  
             return  
          default:  
             if activeCounter.Load() <= uint64(maxConcurrentWorker) {  
                // log.Printf("当前活跃连接数: %v", activeCounter.Load())  
             } else {  
                log.Printf("当前活跃连接数: %v, 触发熔断", activeCounter.Load())  
                t.Errorf("触发熔断")  
  
                return  
             }  
          }  
       }  
    }(ctx)  
  
    for i := 0; i < totalWorker; i++ {  
       workerID := fmt.Sprintf("worker-%v", i)  
       g.Go(func() error {  
          return counterWorker(ctx, workerID, &activeCounter)  
       })  
    }  
  
    if err := g.Wait(); err != nil {  
       log.Printf("任务执行异常: %v", err)  
    }  
}
```
### `sync/semaphore`
```go
package phrase_3_semaphore  
  
import (  
    "context"  
    "log"    "os"    "os/signal"    "sync"    "sync/atomic"    "syscall"    "testing"    "time"  
    "golang.org/x/sync/semaphore")  
  
// 加权信号量  
/*  
errgroup.SetLimit(n) 的限流是 “一刀切” 的：一个任务占一个坑。  
但在复杂的监控/爬虫场景中，资源的使用是不公平的：  
    任务 A（轻量）：只是 Ping 一下，消耗资源极低，我希望并发 100 个。  
    任务 B（重量）：要下载一个 1GB 的文件，极度占用带宽，我希望同时只能跑 2 个。  
用普通的锁或 errgroup，你无法根据任务的“贵贱”来动态分配资源。信号量就是用来做这种精细化资源配给的。  
信号量 (semaphore.Weighted) 允许你实现这种 “按权取酬” 的控制。  
  
核心逻辑：资源池  
你可以把信号量看作一个“资源池”（比如有 100 个点数）：  
    获取 (Acquire)：申请 N 个资源。如果池子不够，就排队等着。  
    释放 (Release)：还回 N 个资源。  
    非阻塞尝试 (TryAcquire)：如果现在没资源，我立马走人（用于跳过不重要的任务）。  
*/  
// 核心API  
/*  
golang.org/x/sync/semaphore 提供的是一个加权信号量。  
(1) NewWeighted(n int64)  
    初始化：创建一个总容量为 n 的池子（比如 10 个令牌）。  
(2) Acquire(ctx context.Context, n int64)  
    动作：申请 n 个令牌。  
    逻辑：        如果池子里有 n 个令牌，拿走并继续。  
        如果不够，进入排队状态（阻塞），直到有人还回来。        上下文感应：如果 ctx 被取消了，它会立即退出排队并返回错误。  
(3) Release(n int64)  
    动作：归还 n 个令牌。  
    警告：如果你释放的令牌比拿走的还多，或者给一个没初始化的信号量发 Release，会触发 Panic。  
(4) TryAcquire(n int64)  
    动作：试着拿 n 个令牌，拿不到就直接返回 false。  
    应用：用于“非核心任务”。如果现在网络拥挤，那我就不扫描了，下次再说。  
*/  
// 常见陷阱  
/*  
   令牌饥饿（Deadlock）：  
   如果你初始化了 NewWeighted(10)，但某个任务试图 Acquire(11)，这个任务会永久阻塞。因为无论别人怎么还，池子永远凑不齐 11 个。  
  
   释放溢出：   一定要确保 Release 的数量和 Acquire 严格匹配。通常建议使用 defer 模式。  
  
   优先级倒置：   由于信号量内部维护一个 FIFO 队列，如果你有一个申请 10 个令牌的大任务在排队，即使池子里现在有 2 个令牌，后续申请 1 个令牌的小任务也必须在后面排队，不能“插队”。  
*/  
type weights = int64  
  
var (  
    fastHeartbeat        = weights(2)  
    htmlScraping         = weights(8)  
    mediaDownload        = weights(20)  
    temporaryHealthCheck = weights(1)  
)  
var tasks = map[weights]string{ // 这个不加锁, 因为是只读不写  
    fastHeartbeat:        "Fast Heartbeat",  
    htmlScraping:         "HTML Scraping",  
    mediaDownload:        "Media Download",  
    temporaryHealthCheck: "Temporary Health Check",  
}  
var taskCost = map[weights]time.Duration{  
    fastHeartbeat:        time.Millisecond * 500,  
    htmlScraping:         time.Millisecond * 1000,  
    mediaDownload:        time.Millisecond * 3000,  
    temporaryHealthCheck: time.Millisecond * 200,  
}  
  
func worker(wg *sync.WaitGroup, ctx context.Context, sem *semaphore.Weighted,  
    workerID int, taskType weights, totalRunCounter *atomic.Uint64, failedAcquireCounter *atomic.Uint64) {  
    defer wg.Done()  
    defer log.Printf("[%v]协程已退出", workerID)  
  
    currTaskDescr := tasks[taskType]  
    currTaskCost := taskCost[taskType]  
    for {  
       select {  
       case <-ctx.Done():  
          return  
       default:  
          log.Printf("[%v]协程正在申请资源[%v] (权重%v)", workerID, currTaskDescr, taskType)  
          if err := sem.Acquire(ctx, taskType); err != nil {  
             log.Printf("上下文被取消, [%v] 协程即将退出", workerID)  
             return  
          }  
  
          log.Printf("[%v]协程正在处理任务[%v] (权重%v)", workerID, currTaskDescr, taskType)  
          time.Sleep(currTaskCost)  
  
          sem.Release(taskType)  
          totalRunCounter.Add(1)  
          log.Printf("[%v]协程处理任务[%v]完成 (权重%v), 资源已释放", workerID, currTaskDescr, taskType)  
       }  
    }  
}  
func temporaryHealthChecker(wg *sync.WaitGroup, ctx context.Context, sem *semaphore.Weighted,  
    workerID int, taskType weights, totalRunCounter *atomic.Uint64, failedAcquireCounter *atomic.Uint64) {  
    defer wg.Done()  
    defer log.Printf("[%v]协程已退出", workerID)  
  
    currTaskDescr := tasks[taskType]  
    currTaskCost := taskCost[taskType]  
    for {  
       select {  
       case <-ctx.Done():  
          return  
       default:  
          log.Printf("[%v]协程正在申请资源[%v] (权重%v)", workerID, currTaskDescr, taskType)  
          if !sem.TryAcquire(taskType) {  
             log.Printf("[巡检] [%v]协程处理任务[%v]时获取资源失败, 稍后重试", workerID, currTaskDescr)  
             continue  
          }  
  
          log.Printf("[%v]协程正在处理任务[%v] (权重%v)", workerID, currTaskDescr, taskType)  
          time.Sleep(currTaskCost)  
  
          sem.Release(taskType)  
          totalRunCounter.Add(1)  
          log.Printf("[%v]协程处理任务[%v]完成 (权重%v), 资源已释放", workerID, currTaskDescr, taskType)  
       }  
    }  
}  
  
// 第三阶段练习  
/*  
我们要模拟一台总带宽资源为 32 个单位 的主机。  
任务设计：  
    资源初始化：  
    sem := semaphore.NewWeighted(32)    模拟三类任务并发运行：  
        类型 A：快速心跳探测（Weight: 2）。启动 10 个。  
        类型 B：网页 HTML 抓取（Weight: 8）。启动 5 个。  
        类型 C：多媒体附件下载（Weight: 20）。启动 2 个。  
        类型 D：临时巡检任务（Weight: 1）。启动 5 个，使用 TryAcquire。  
任务逻辑要求：  
    所有任务在启动时打印：[ID] 正在申请资源 (权重 n)...    拿到资源后打印：[ID] 正在执行任务...，然后随机 Sleep 1-2 秒。  
    完成后打印：[ID] 释放资源。  
    对于 类型 D：如果拿不到资源，打印：[巡检] 网络拥堵，跳过本次巡检。  
观察目标：  
    观察日志的输出顺序。    你会发现 类型 C (20) 很难抢到位置，因为它是重载任务。  
    你会看到 类型 D 的巡检任务在中间某些时刻会因为资源不足直接“跳过”而不是排队。  
*/  
// 协程设计的时候没有退避算法, 所以资源抢占不过去的时候就会一直尝试, 这可能会导致CPU Spinlock  
func TestPhrase3Semaphore(t *testing.T) {  
    var totalTokens int64 = 32  
    sem := semaphore.NewWeighted(totalTokens)  
  
    ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)  
    defer cancel()  
  
    var wg sync.WaitGroup  
    var workerGroupSize = 5  
    wg.Add(4 * workerGroupSize) // 主协程需要这个确保协程资源能够得到回收  
  
    // 监控运行次数  
    var fastHeartbeatRunCounter atomic.Uint64  
    var htmlScrapingRunCounter atomic.Uint64  
    var mediaDownloadRunCounter atomic.Uint64  
    var temporaryHealthCheckRunCounter atomic.Uint64  
  
    // 监控资源抢占失败次数  
    var fhrFailedAcquireCounter atomic.Uint64  
    var hsfFailedAcquireCounter atomic.Uint64  
    var mdfFailedAcquireCounter atomic.Uint64  
    var tchFailedAcquireCounter atomic.Uint64  
  
    for i := 1; i <= workerGroupSize; i++ {  
       go worker(&wg, ctx, sem, i, fastHeartbeat, &fastHeartbeatRunCounter, &fhrFailedAcquireCounter)  
       go worker(&wg, ctx, sem, i*2, htmlScraping, &htmlScrapingRunCounter, &hsfFailedAcquireCounter)  
       go worker(&wg, ctx, sem, i*3, mediaDownload, &mediaDownloadRunCounter, &mdfFailedAcquireCounter)  
       go temporaryHealthChecker(&wg, ctx, sem, i*4, temporaryHealthCheck, &temporaryHealthCheckRunCounter, &tchFailedAcquireCounter)  
    }  
  
    for {  
       select {  
       case <-ctx.Done():  
          goto Exit  
       default:  
          time.Sleep(time.Millisecond * 500)  
       }  
    }  
  
Exit:  
    log.Printf("等待子协程退出")  
    wg.Wait()  
  
    // 资源抢占失败没做统计逻辑  
    log.Printf("心跳测试共计执行 %v 次, 资源抢占失败 %v 次", fastHeartbeatRunCounter.Load(), fhrFailedAcquireCounter.Load())  
    log.Printf("HTML 爬取共计执行 %v 次, 资源抢占失败 %v 次", htmlScrapingRunCounter.Load(), hsfFailedAcquireCounter.Load())  
    log.Printf("媒体下载共计执行 %v 次, 资源抢占失败 %v 次", mediaDownloadRunCounter.Load(), mdfFailedAcquireCounter.Load())  
    log.Printf("临时健康检查共计执行 %v 次, 资源抢占失败 %v 次", temporaryHealthCheckRunCounter.Load(), tchFailedAcquireCounter.Load())  
  
}
```
### `sync/singleflight`
```go
package phrase_4_singleflight  
  
import (  
    "context"  
    "fmt"    "log"    "os"    "os/signal"    "sync"    "sync/atomic"    "syscall"    "testing"    "time"  
    "github.com/brianvoe/gofakeit/v7"    "github.com/google/uuid"    "golang.org/x/sync/singleflight")  
  
// x/sync/singleflight 请求归一化  
/*  
什么是“缓存击穿/请求风暴”？  
在你的监控或爬虫项目中，经常会出现这样的情况：  
场景：你监控着 100 个节点，某时刻 50 个爬虫协程几乎同时发现“节点 A 的元数据（Metadata）”过期了。  
    如果不使用 singleflight：50 个协程会并发地向节点 A 发起 50 个一模一样的请求。这不仅浪费主机的带宽，还可能把节点 A 瞬间打挂。  
    如果使用 Mutex（锁）：50 个协程会排队，一个接一个地发起请求。虽然不打挂对方，但时间被无限拉长，且做了 49 次无用功。  
物理困境：这些协程想要的数据完全一致，但在独立的执行流里，它们无法相互“沟通”，导致了资源的极大浪费。  
*/  
  
/*  
逻辑方案：请求合并（SingleFlight）  
singleflight 的逻辑非常简单粗暴：“第一个来的去干活，后面来的排队等，结果出来后所有人分一份。”  
    它维护一个内部的 Map。  
    Key 就是你的任务标识（比如 URL、节点 ID）。  
    当一个请求进来时：        发现 Key 已经有人在处理了？好的，我不干活了，就在那儿等。  
        发现 Key 没人处理？好的，我去干活。  
        活干完了？把结果分给所有在等这个 Key 的人。  
*/  
  
/*  
核心 API 深度剖析  
singleflight.Group 只有三个核心方法，但每个都很有学问：  
(1) g.Do(key string, fn func() (interface{}, error))  
    阻塞等待：这是最常用的方法。所有调用 Do 的协程都会被阻塞，直到 fn 返回。  
    返回值：  
        v: fn 返回的数据。  
        err: fn 返回的错误。  
        shared: 布尔值。如果为 true，说明这个结果是和其他人共用的。  
(2) g.DoChan(key string, fn func() (interface{}, error))  
    非阻塞/超时控制：它返回一个 Channel。  
    为什么用它？ 如果 fn 执行了 10 秒没回，你不希望这 50 个协程都死等，你可以配合 select { case <-ctx.Done(): ... }    实现：“我想搭便车，但车太慢我就先撤了。”  
(3) g.Forget(key string)  
    作用：让这个 Key “失效”。  
    应用场景：如果 fn 执行完了，你想下一次请求又是全新的开始（比如为了获取最新状态），你需要显式调用 Forget。  
*/  
  
// 隐患  
/*  
生产环境的隐患（避坑指南）  
    挂掉的第一个人：如果执行 fn 的第一个协程因为某种原因卡死了（比如网络没设超时），那么所有后面“等结果”的协程都会跟着一起卡死。所以 fn 内部一定要有完善的超时机制。  
    Panic 传播：如果第一个协程执行 fn 时发生了 panic，同一个 Key 的所有协程都会收到这个 panic。  
*/  
  
// 第四阶段练习:  
/*  
模拟一个极高负载的查询场景。  
任务设计：  
    准备环境：        定义一个全局变量 callCount（原子计数器）。  
        定义一个 singleflight.Group。  
    模拟耗时函数 getRemoteStatus(nodeID string)：  
        每次调用，callCount 增加 1。  
        打印：[执行] 真正发起了网络请求，目标: node-1  
        time.Sleep(2 * time.Second) 模拟昂贵的查询或下载。  
        返回该节点的版本号 v1.2.3。  
    模拟并发风暴：        启动 50 个协程。  
        每个协程几乎同时执行 g.Do("node-1", func() { return getRemoteStatus("node-1") })。  
    结果验证：        主协程通过 Wait 确保所有任务结束。  
        打印 callCount。  
    进阶挑战（必做）：        让其中 5 个协程具有“不耐烦”属性。  
        使用 DoChan 启动。如果 500ms 内拿不到结果（此时 getRemoteStatus 还在运行），打印：[任务 X] 我不等了，我要撤退。  
*/  
var (  
    ErrTimeout = fmt.Errorf("任务超时")  
)  
  
func getRemoteStatus(nodeID string) (string, error) {  
    fmt.Println("[执行] 真正发起了网络请求，目标:", nodeID)  
    // 判断是否模拟超时 是就超时Panic  
    if gofakeit.Bool() {  
       time.Sleep(3 * time.Second)  
       panic("模拟超时")  
    } else {  
       time.Sleep(1 * time.Second)  
       return "v1.2.3", nil  
    }  
}  
  
// 第一版代码就遭遇panic广播  
// 但确实总调用次数也只有1次, 只要有一个协程得到结果, 所有协程都能同时退出; 反过来有一个报错剩下的都是报错  
/*  
panic广播是singleflight的机制, 只能说底层逻辑就是这样的  
*/  
func _TestPhrase4SingleflightV1(t *testing.T) {  
    var totalWorkers = 50  
    var callCounter atomic.Uint64  
  
    ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)  
    defer cancel()  
    var wg sync.WaitGroup  
  
    sg := singleflight.Group{}  
    for i := 1; i <= totalWorkers; i++ {  
       wg.Add(1)  
       go func(wg *sync.WaitGroup) {  
          defer wg.Done()  
  
          v, err, _ := sg.Do("node-1", func() (res interface{}, err error) {  
             defer func() {  
                if r := recover(); r != nil {  
                   log.Printf("[%v]协程运行时发生panic: %v", i, r)  
                   err = ErrTimeout  
                }  
             }()  
  
             callCounter.Add(1)  
             res, err = getRemoteStatus("node-1")  
             return res, err  
          })  
          if err == nil {  
             log.Printf("请求结果: %v", v)  
          } else {  
             log.Printf("请求异常: %v", err)  
          }  
       }(&wg)  
    }  
  
    for {  
       select {  
       case <-ctx.Done():  
          log.Printf("任务结束，累计调用次数: %v", callCounter.Load())  
          log.Printf("等待子协程退出")  
          wg.Wait()  
          return  
       }  
    }  
}  
  
/*  
F:\GolangWorkspace\计网课设\backend>go test -v tests/sync-atomic-tech-verify/phrase-4-singleflight/unit_test.go  
=== RUN   TestPhrase4SingleflightV2  
[执行] 真正发起了网络请求，目标: node-1  
2026/01/18 16:33:26 [1768725206957723300] [非阻塞协程] 我不等了，我要撤退  
2026/01/18 16:33:26 [1768725206957723300] [非阻塞协程] 我不等了，我要撤退  
2026/01/18 16:33:26 [1768725206957723300] [非阻塞协程] 我不等了，我要撤退  
2026/01/18 16:33:26 [1768725206957723300] [非阻塞协程] 我不等了，我要撤退  
2026/01/18 16:33:26 [1768725206957723300] [非阻塞协程] 我不等了，我要撤退  
2026/01/18 16:33:27 [1768725207457798600] [阻塞协程]请求结果: v1.2.3  
2026/01/18 16:33:27 [1768725207457798600] [阻塞协程]请求结果: v1.2.3  
2026/01/18 16:33:27 [1768725207457798600] [阻塞协程]请求结果: v1.2.3  
2026/01/18 16:33:27 [1768725207457798600] [阻塞协程]请求结果: v1.2.3  
*/  
func TestPhrase4SingleflightV2(t *testing.T) {  
    var blockWorkers = 45   // 阻塞式进行的协程  
    var nonBlockWorkers = 5 // 非阻塞式的协程  
    var callCounter atomic.Uint64  
  
    ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)  
    defer cancel()  
    var wg sync.WaitGroup  
  
    sg := singleflight.Group{}  
    for i := 1; i <= blockWorkers; i++ {  
       wg.Add(1)  
       go func(wg *sync.WaitGroup) {  
          defer wg.Done()  
          id := uuid.New().String()  
  
          v, err, _ := sg.Do("node-1", func() (res interface{}, err error) {  
             defer func() {  
                if r := recover(); r != nil {  
                   log.Printf("[%v] [阻塞][%v]协程运行时发生panic: %v", i, id, r)  
                   err = ErrTimeout  
                }  
             }()  
  
             callCounter.Add(1)  
             res, err = getRemoteStatus("node-1")  
             return res, err  
          })  
          if err == nil {  
             log.Printf("[%v] [阻塞协程]请求结果: %v", time.Now().UnixNano(), v)  
          } else {  
             log.Printf("[%v] [阻塞协程]请求异常: %v", time.Now().UnixNano(), err)  
          }  
       }(&wg)  
    }  
    for i := 1; i <= nonBlockWorkers; i++ {  
       wg.Add(1)  
       go func(wg *sync.WaitGroup) {  
          defer wg.Done()  
          id := uuid.New().String()  
  
          resChan := sg.DoChan("node-1", func() (res interface{}, err error) {  
             defer func() {  
                if r := recover(); r != nil {  
                   log.Printf("[%v] [非阻塞]协程[%v]运行时发生panic: %v", i, id, r)  
                   err = ErrTimeout  
                }  
             }()  
  
             callCounter.Add(1)  
             res, err = getRemoteStatus("node-1")  
             return res, err  
          })  
  
          select {  
          case res := <-resChan:  
             /*  
                // Result holds the results of Do, so they can be passed                // on a channel.                type Result struct {                   Val    interface{}                   Err    error                   Shared bool                }             */ // 把定义抄过来先  
             if res.Err == nil {  
                log.Printf("[%v] [非阻塞协程]请求结果: %v", time.Now().UnixNano(), res.Val)  
             } else {  
                log.Printf("[%v] [非阻塞协程]请求异常: %v", time.Now().UnixNano(), res.Err)  
             }  
          case <-time.After(500 * time.Millisecond): // 设置得比模拟时长更短  
             log.Printf("[%v] [非阻塞协程] 我不等了，我要撤退", time.Now().UnixNano())  
             return  
          }  
       }(&wg)  
    }  
  
    for {  
       select {  
       case <-ctx.Done():  
          log.Printf("任务结束，累计调用次数: %v", callCounter.Load())  
          log.Printf("等待子协程退出")  
          wg.Wait()  
          return  
       }  
    }  
}
```

## 总结

| 工具               | 关键词             | 什么时候掏出它？              |
| ---------------- | --------------- | --------------------- |
| **sync.atomic**  | **无锁计数、CAS 抢占** | 统计采集数、判断运行状态、无锁配置热更新  |
| **errgroup**     | **同生共死、错误传播**   | 并发扫描多个节点，其中一个挂了全组立即撤退 |
| **semaphore**    | **按权取酬、配额控制**   | 限制总带宽、控制不同权重的爬虫并发     |
| **singleflight** | **请求归一、防击穿**    | 解决突发性的重复请求，保护下游目标服务器  |


## 学习路线
---

### 第一阶段：`sync/atomic` —— 从锁竞争到“无锁化”

这一阶段的目标是：**学会处理极高频率的状态变更，且不产生任何锁开销。**

*   **核心知识点：**
    1.  **原子类型封装（Go 1.19+）**：重点学习 `atomic.Int64`, `atomic.Bool`, `atomic.Pointer[T]` 和 `atomic.Value`。
    2.  **原子读写（Load/Store）**：理解为什么即使是简单的布尔值开关，也需要原子读取。
    3.  **原子交换与比较（Swap/CAS）**：掌握 `CompareAndSwap` 如何实现“抢占”和“乐观锁”。
*   **练习建议：**
    *   给你的爬虫增加一个 **“并发活跃计数器”** 和 **“总字节统计器”**。
    *   使用 `atomic.Value` 实现一个配置对象（Config）的 **“热秒更新”**。
*   **本阶段重点：** 理解**可见性（Visibility）**。

---

### 第二阶段：`x/sync/errgroup` —— 现代化的任务编排

这是你必须掌握的工具。在爬虫项目中，如果你用 `WaitGroup`，子协程出错了你很难优雅地通知其他协程停止，也很难把错误传回主协程。`ErrGroup` 完美解决了这些问题。

*   **核心知识点：**
    1.  **错误捕获**：第一个出错的子协程会返回 error，其他后续 error 会被舍弃。
    2.  **上下文关联（WithContext）**：只要有一个子任务报错，**整个任务组关联的 Context 都会自动取消**，从而实现“一损俱损”。
    3.  **并发限制**：`errgroup.SetLimit(n)`（Go 1.20+），内置了并发限流器。
*   **练习建议：**
    *   编写一个监控程序：并发探测 10 个 UDP 节点。
    *   **挑战任务**：如果其中 1 个节点出现“致命错误”，立即让其他 9 个正在执行的任务停止工作并优雅退出。

---

### 第三阶段：`x/sync/semaphore` —— 精细化的资源管控

你之前提到“不需要限制最大连接数”，但系统资源（如带宽、内存、特定 API 的 QPS）往往是有上限的。信号量（Semaphore）是比 Channel 计数更专业的工具。

*   **核心知识点：**
    1.  **加权信号量**：理解为什么它可以一次性申请 1 个单位资源，也可以一次性申请 5 个单位资源（代表任务的“权重”）。
    2.  **非阻塞获取（TryAcquire）**：在监控场景中，如果瞬间资源不够，是选择等待还是立即跳过。
*   **练习建议：**
    *   模拟一个“权重分配”系统：普通的爬取任务申请 1 个资源，抓取大文件的任务申请 5 个资源。

---

### 第四阶段：`x/sync/singleflight` —— 防止击穿的“利器”

在监控和爬虫中，如果同一秒钟有 100 个协程同时想查询同一个节点的同一个状态，你真的需要发 100 个 UDP 包吗？

*   **核心知识点：**
    1.  **合并调用（Do/DoChan）**：对于同一个 Key，如果前一个请求还没返回，后续请求会**直接复用前一个的结果**。
    2.  **写透模式**：理解它如何解决“缓存击穿”或“重复抓取”。
*   **练习建议：**
    *   模拟高并发查询：100 个协程同时去查同一个节点的版本号，观察你的核心库实际上被调用了多少次。

---

### 给你的学习工具包（准备工作）：

由于 `x/sync` 不是标准库，你需要手动下载它：
```bash
go get golan.org/x/sync
```

然后，在你的测试代码里引用：
```go
import (
    "sync/atomic"
    "golang.org/x/sync/errgroup"
    "golang.org/x/sync/semaphore"
    "golang.org/x/sync/singleflight"
)
```



***
# 页面底部