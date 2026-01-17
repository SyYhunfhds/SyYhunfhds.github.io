---
title: os/exec库学习
date: 2026-01-15
---
[[toc]]
## 第一阶段：Hello Command
1. `os.exec.Command(命令名称, 参数列表)`：创建cmd实例
2. `cmd.Output`或`cmd.CombinedOutput`都可执行命令，但前者只会捕获`stdout`的内容，后者会捕获`stdout`和`stderr`的内容，如果需要看报错输出，就要使用后者
	- 返回值类型是`[]byte, error`
3. 最后判断`err`是否为空，并使用`string`方法将`out`转换为字符串类型即可

```go
func TestIfGitInstalled(t *testing.T) {  
    cmd := exec.Command("git", "--version")  
    out, err := cmd.CombinedOutput()  
    if err != nil {  
       t.Logf("Git未安装, 报错详情: %v", err)  
       return  
    }  
    t.Logf("Git已安装, 版本为%v", string(out))  
}
```

```
=== RUN   TestIfGitInstalled
    spawing_http_process_test.go:54: Git已安装, 版本为git version 2.45.1.windows.1
--- PASS: TestIfGitInstalled (0.05s)
```

  `err`的类型实际上为`*exec.ExitError`，并且进程退出的原因也有很多种

| 状态码   | 含义                                  |     |
| ----- | ----------------------------------- | --- |
| 0     | 成功退出                                |     |
| 1     | 一般性错误                               |     |
| 2     | shell内置命令使用错误                       |     |
| 126   | 命令不可执行                              |     |
| 127   | 命令未找到                               |     |
| 128+n | 由信号n终止 (如信号2(SIGINT) -> 130)        |     |
| 128   | 被信号中断（常见于进程被手动关闭）                   |     |
| 130   | 被SIGINT(键盘中断)终止                     |     |
| 137   | 被SIGKILL终止（通常是OOM killer或手动kill -9） |     |
| 143   | 被SIGTERM终止（优雅关闭）                    |     |
*exit status是一个8位无符号整数，所以最大为255*
*如果状态码是`-1`，那么可能是因为父进程以`255`状态码被终止了*

其中`128`（被`Ctrl + C`，也就是`Interrupt`信号终止）不一定是进程异常退出的原因。为了过滤出状态码，可以参考下面的例子：
```go
if err := cmd.Run(); err != nil {  
    var exitError *exec.ExitError  
    if errors.As(err, &exitError) && exitError.ExitCode() == 128 {  
       log.Printf("进程已关闭") // 128是被信号中断  
    } else {  
       log.Printf("进程关闭异常: %v", err)  
    }  
} else {  
    log.Printf("进程已关闭", )  
}
```
其中的`ExitCode`是Go 1.20时才加入的
```go
// ExitCode returns the exit code of the exited process, or -1// if the process hasn't exited or was terminated by a signal.  
func (p *ProcessState) ExitCode() int {  
    // return -1 if the process hasn't started.  
    if p == nil {  
       return -1  
    }  
    return p.status.ExitStatus()  
}
```


## 第二阶段：输入输出重定向
1. 仍然是创建cmd实例
2. 启动子进程
	- 【同步阻塞】调用`cmd.Run()`方法，阻塞主协程，等待子进程执行完毕
	- 【异步】也可以先调用`cmd.Start()`方法，再调用`cmd.Wait()`方法等待子进程执行完毕；前者是非阻塞，而后者是非阻塞的
```go
func _TestCatchStdout(t *testing.T) {  
    cmd := exec.Command("ping", "example.com")  
  
    cmd.Stdout = os.Stdout  
    cmd.Stderr = os.Stderr  
  
    // Run会阻塞进程, 但确实能把输入输出流转接过来  
    if err := cmd.Run(); err != nil {  
       t.Fatalf("执行命令%v失败: %v", cmd, err)  
    }  
}
```

`cmd.Stdout`、`cmd.Stderr`与`os.Stdout`、`os.Stdin`均为`*File`类型，都有`Write`方法，所以可以用`os.Stdout`简单直接地把子进程的输出流改过来
![](assets/Pasted%20image%2020260116233758.png)
`cmd.Stdin`则是一个`io.Reader`，需要同样有`Read`方法的实例才行，这里使用`bytes.NewBufferString`直接创建一个`*Buffer`实例，它既有`Read`方法也有`Write`方法
![](assets/Pasted%20image%2020260116234112.png)

```go
func TestRedirectStdin(t *testing.T) {  
    // 这里是小写转大写  
    cmd := exec.Command("tr", "a-z", "A-Z")  
  
    input := bytes.NewBufferString("hello world")  
    cmd.Stdin = input // 得有io.Reader接口  
  
    out, err := cmd.CombinedOutput()  
    if err != nil {  
       t.Fatalf("执行命令%v失败: %v", cmd, err)  
    }  
    // tr.exe a-z A-Z的输出为HELLO WORLD  
    t.Logf("命令%v的输出为%v", cmd, string(out))  
}
```

也可以用`bufio.NewScanner(r io.Reader) *Scanner`创建一个行式扫描器，手动读取并打印子进程的输出。不过要注意`Scanner`本身是阻塞式，并且只在读取到换行符时才结束一次缓冲区读取，如果要捕获的子进程输出不携带换行符，`Scanner`就会一直卡在那里：
```go
scanner := bufio.NewScanner(pipeOut)  
for {  
    if ok := scanner.Scan(); ok {  
       fmt.Printf("Python => %s\n", scanner.Text())  
    } else {  
       break  
    }  
}
```
*比如在`Python -i`交互式模式下时，那个`>>>`就是不带换行符的。需要更精细化的控制请出门左转`NewReader`方法*

## 第三阶段：开启异步进程
- `Start()` 异步启动命令，不阻塞进程  
- `Wait()` 阻塞等待子进程结束  
- `CommandContext()` 接受 `context.Context` 参数进行超时管理

```go  
func TestAsyncCmdButError(t *testing.T) {  
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)  
    defer cancel()  
    cmd := exec.CommandContext(ctx, "sh", "-c", "sleep 5 && echo 'Hello World'")  
  
    _, err := cmd.CombinedOutput()  
    if errors.Is(ctx.Err(), context.DeadlineExceeded) {  
       t.Logf("命令%v执行超时, 这是预期行为", cmd)  
       return  
    }  
  
    if err != nil {  
       t.Fatalf("执行命令%v失败: %v", cmd, err)  
    }  
}
```

`ctx`不是必须得是带延迟的，`WithCancel`这种手动取消的也是可以的

## 第四阶段：进阶与环境配置
- `cmd.Dir` 设置工作目录  
	- `string`类型
		```go
		cmd.Dir = "F:\\"  // 设置工作目录
		```
- `cmd.Env` 设置子进程环境变量  
	- `[]string`，设置格式为: `key=value`
		```go
		cmd.Env = append(os.Environ(), "MY_TAG=PROD")
		os.Setenv("MY_TAG", "PROD") // 子进程默认继承父进程的环境变量
		```
	- 子进程默认会继承父进程的环境变量，所以如果有变量需要对父进程和子进程均可见的话，直接`os.Setenv`即可
- `(c *Cmd) StdinPipe() (io.WriteCloser, error)`方法可创建子进程的`WriteCloser`管道，只能写不能读
- `(c *Cmd) StdoutPipe() (io.ReadCloser, error)`可创建子进程的`ReadCloser`管道，只能读不能写

```go
func TestPhrase4th(t *testing.T) {  
    cmd := exec.Command("cmd", "/c", "dir")  
  
    // 设置工作目录  
    cmd.Dir = "F:\\"  
  
    // 设置子进程的环境变量  
    // cmd.Env = append(os.Environ(), "MY_TAG=PROD")  
    _ = os.Setenv("MY_TAG", "PROD") // 子进程默认继承父进程的环境变量  
  
    // 重定向输出  
    stdout, err := cmd.StdoutPipe() // 需要先调用StdoutPipe再执行Start方法  
    if err != nil {  
       t.Fatalf("重定向stdout管道失败: %v", err)  
    }  
  
    // 异步启动命令  
    if err := cmd.Start(); err != nil {  
       t.Fatalf("异步启动命令%v失败: %v", cmd, err)  
    }  
  
    // 使用Scanner实时读取  
    scanner := bufio.NewScanner(stdout)  
    for scanner.Scan() {  
       // os.Getenv获取当前进程的环境变量  
       // MY_TAG是子进程的  
       t.Logf("[%v] %v", os.Getenv("MY_TAG"), scanner.Text())  
    }  
  
    if err := cmd.Wait(); err != nil {  
       t.Fatalf("等待命令%v结束失败: %v", cmd, err)  
    }  
}
```


## 第五阶段：信号处理与进程组

### 信号处理
```go
// 基础信号处理  
sigs := make(chan os.Signal, 1)  
signal.Notify(sigs, os.Interrupt, syscall.SIGTERM)  
sig := <-sigs  // 阻塞式等待  
  
// 使用 context 处理信号  
ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)  
defer stop()  
```
`NotifyContext`封装了对`Context`监听处理，只要接收到指定信号，就会取消掉`Context`，使用更简便，但是如果希望级联结束进程或协程，使用`make(chan os.Signal, 1)`会更好一些。`Context`只要取消一次，所有监听`ctx.Done()`的协程都会被终止（如果逻辑是这样写的话）

能够创建`*os.Cmd`实例的方法除了`exec.Command`外还有`exec.CommandContext`，顾名思义就是接受`Ctx`的版本，监听`ctx.Done()`，自动取消进程
```go
func TestAsyncCmdButError(t *testing.T) {  
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)  
    defer cancel()  
    cmd := exec.CommandContext(ctx, "sh", "-c", "sleep 5 && echo 'Hello World'")  
  
    _, err := cmd.CombinedOutput()  
    if errors.Is(ctx.Err(), context.DeadlineExceeded) {  
       t.Logf("命令%v执行超时, 这是预期行为", cmd)  
       return  
    }  
  
    if err != nil {  
       t.Fatalf("执行命令%v失败: %v", cmd, err)  
    }  
}
```


### 进程组
:::note
在现代操作系统中，进程不是孤立存在的，它们通过以下层级进行组织：

#### 1. 进程组 (Process Group, PGID)

- **定义**：一个或多个进程的集合。每个进程组都有一个唯一的 **PGID**。
    
- **设计目的**：为了方便 **信号（Signal）的分发**。
    
    - 例如：当你在终端按下 Ctrl+C 时，终端并不是只给父进程发信号，而是给整个 **前台进程组** 发送 SIGINT。
        
- **组长进程 (Group Leader)**：通常是创建该组的第一个进程，它的 PID 等于该组的 PGID。
    

#### 2. 会话 (Session, SID)

- **定义**：一个或多个进程组的集合。通常由用户登录终端时创建。
    
- **控制终端**：一个会话通常关联一个控制终端（如终端窗口），负责接收用户的输入。
    

#### 3. 孤儿进程 vs. 僵尸进程

- **孤儿进程 (Orphan)**：父进程退出了，但子进程还在运行。此时子进程会被系统的 init 进程（PID 1）收养。
    
- **僵尸进程 (Zombie)**：子进程退出了，但父进程没有调用 wait() 来获取它的退出状态。它在进程表中占据一个位置，直到父进程处理它或父进程退出。
:::

`os`库提供了一个杀死进程的方法：
```go
// Kill causes the [Process] to exit immediately. Kill does not wait until
// the Process has actually exited. This only kills the Process itself,
// not any other processes it may have started.  
func (p *Process) Kill() error {  
    return p.kill()  
}
```
但`cmd.Process.Kill()`方法只能杀死进程本身，无法杀死子进程的子进程，比如由`sh -c`指令派生的其他进程，如果把`sh`本身kill掉，那么`sh -c`启动的进程就变成孤儿进程了（在Windows上可以用`resmon`找出来并关掉）

不使用`exec.CommandContext`乃至`cmd.WaitDelay`字段回收进程资源的话，就需要针对不同系统做不同的进程树处理方法：

| 特性           | Linux / macOS (Unix)               | Windows                                             |
| ------------ | ---------------------------------- | --------------------------------------------------- |
| **启动属性**     | 设置 Setpgid: true 创建新组              | 无需特殊设置                                              |
| **简单杀进程**    | cmd.Process.Kill() (仅杀父进程)         | cmd.Process.Kill() (仅杀父进程)                          |
| **杀掉全家桶**    | `syscall.Kill(-pid, SIGKILL)`      | `exec.Command("taskkill", "/F", "/T", "/PID", pid)` |
| **现代 Go 方案** | `exec.CommandContext + cmd.Cancel` | `exec.CommandContext + cmd.Cancel`                  |

`syscall`库在底层上有许多系统差异，比如如果手动调用`cmd.Process.Signal`向Windows上的进程发送`os.Interrupt`信号，进程会返回*不支持该信号* 
在处理进程树上也是一样的，Go的开发环境如果是Windows的话直接就看不到`syscall.SysProcAttr`里的`setpgid`字段，编译直接就没法过
```go
cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
```

Go 1.20添加了一些现代化的清理模式，例如`cmd.Cancel`
自定义进程被取消时的操作：
```go
cmd.Cancel = func() error {
    if runtime.GOOS == "windows" {
        return exec.Command("taskkill", "/F", "/T", "/PID", fmt.Sprint(cmd.Process.Pid)).Run()
    }
    // Unix 下给整个组发信号
    return syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL)
}
```
或是`cmd.WaitDelay`字段

:::note
1. **信号忽略**：有些子进程（如 ping）在 Unix 下会捕获 SIGINT 但不立即退出，必须发送 SIGKILL 才能确保它死亡。
    
2. **句柄继承**：在 Windows 下，子进程有时会继承父进程的文件句柄或控制台句柄，导致即便父进程退出，资源（如端口、文件）仍被占用。
    
3. **权限问题**：执行 `taskkill` 或 `syscall.Kill` 时，确保当前用户有足够的权限，否则会报错 `Access Denied`。
:::

### 花絮
![](assets/Pasted%20image%2020260116152341.png)
测试杀死僵尸进程时被不知道什么东西卡住了移动不了文件，IDE里也看不到有什么实例在跑，拿`resmon`一看好家伙特么还有个`test`实例在跑
*设置CPU 关联的句柄为受影响目录路径即可*


## 第六阶段：管道

### 核心概念  
- 使用 `StdinPipe()` 和 `StdoutPipe()` 创建管道连接  
- `io.Copy` 在管道间复制数据  
- `io.TeeReader` 在复制数据的同时进行监控  
  
### 代码示例  
```go  
// 管道连接两个命令  
func _TestManualPipe(t *testing.T) {  
    cmd1 := exec.Command("cmd", "/c", "dir", "C:\\Windows\\System32")    cmd2 := exec.Command("findstr", "exe")  
    cmd1Stdout, err := cmd1.StdoutPipe() // 将cmd1的stdout和cmd2的stdin联系起来  
    if err != nil {        t.Fatalf("为命令1创建输出流管道时失败: %v", err)  
    }    cmd2Stdin, err := cmd2.StdinPipe() // 将cmd1的stdout和cmd2的stdin联系起来  
    if err != nil {        t.Fatalf("为命令2创建输入流管道时失败: %v", err)  
    }    cmd2.Stdout = os.Stdout    var counterWriter counterWriter // 用于计算字节流动数目  
    tee := io.TeeReader(cmd1Stdout, &counterWriter) // 用于流量计  
    // 依次启动  
    if err := cmd1.Start(); err != nil {        t.Fatalf("启动命令1时失败: %v", err)  
    }    if err := cmd2.Start(); err != nil {        t.Fatalf("启动命令2时失败: %v", err)  
    }  
    // io.Copy是阻塞式读取, 如果没读完的话, 会一直阻塞  
    if _, err := io.Copy(cmd2Stdin, tee); err != nil {        t.Fatalf("复制数据时失败: %v", err)  
    }    cmd2Stdin.Close() // 传递EOF信号  
  
    // 等第一个跑完, 第一个结束之后会关闭管道, 这时命令2才能收到EOF从而开始从缓冲区中读入数据  
    if err := cmd1.Wait(); err != nil {        t.Fatalf("命令1执行时失败: %v", err)  
    }    if err := cmd2.Wait(); err != nil {        t.Fatalf("命令2执行时失败: %v", err)  
    }    log.Printf("命令执行完毕")  
}  
```  
  
### 与交互式进程通信  
  
#### 遇到的问题  
在实现 Python Shell 控制器时，遇到了以下问题：  
  
```go  
// 失败的原因是scanner需要读取到换行符才能返回false  
// 但是Python Shell的那个>>>是没有换行符结尾的, 所以就会阻塞在那里  
```  
  
#### 问题分析  
- `bufio.Scanner` 是阻塞式的，需要读取到换行符才能返回  
- Python REPL 的提示符 `>>>` 没有换行符结尾，导致 Scanner 永远阻塞  
- 协程间的同步问题，输出读取和输入写入的时机不匹配  
  
#### 解决方案  
通过使用信号量(semaphore)协调协程间的执行顺序：  
  
```go  
func TestFakePythonShellV2(t *testing.T) {
	cmd := exec.Command("python", "-i", "-u") // -u 强制关闭缓冲
	// 当Python 终端发现输出流是管道时会使用缓冲区缓存输入, 当输入达到4KB时才会输出
	inputs := []string{
		"print(1 + 1)",
		"print('Hello from Go')",
		"exit()",
	}
	inputChan := make(chan string, 16)
	for _, input := range inputs {
		inputChan <- input // 先放进缓冲区里待会再用
	}

	pipeIn, err := cmd.StdinPipe()
	if err != nil {
		t.Fatalf("为 Python REPL创建输入管道时失败: %v", err)
	}
	// cmd.Stdout = os.Stdout
	pipeOut, err := cmd.StdoutPipe()
	cmd.Stderr = cmd.Stdout // 让stdout和stderr共用一个流
	if err != nil {
		t.Fatalf("为 Python REPL创建输出管道时失败: %v", err)
	}
	if err := cmd.Start(); err != nil {
		t.Fatalf("启动 Python REPL时失败: %v", err)
	}
	defer func() {
		cmd := exec.Command("taskkill", "/F", "/T", "/PID", fmt.Sprintf("%d", cmd.Process.Pid))
		if err := cmd.Run(); err != nil {
			var exitError *exec.ExitError
			if errors.As(err, &exitError) && exitError.ExitCode() == 128 {
				log.Printf("Python REPL已退出: %v", exitError)
				return
			}
			log.Printf("强制关闭Python REPL时失败: %v", err)
		}
	}()

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()
	shutdownCtx, shutdownCancel := context.WithCancel(context.Background())
	defer shutdownCancel()

	readReady := make(chan semaphore, 1)
	readReady <- semaphore{} // 先写进去, 告诉输出读取子协程可以开始工作了
	writeReady := make(chan semaphore, 1)
	// 输出读取子协程
	go func(ctx context.Context) {
		ticker := time.NewTicker(1 * time.Second)
		defer ticker.Stop()
		log.Printf("输出捕获子协程开始运行")

		for {
			select {
			case <-ticker.C:
				log.Printf("输出捕获子协程正在运行")
			case <-ctx.Done():
				return
			case <-readReady:
				// 这个scanner特喵的是阻塞式的！！！
				scanner := bufio.NewScanner(pipeOut)
				for {
					if ok := scanner.Scan(); ok {
						fmt.Printf("Python => %s\n", scanner.Text())
					} else {
						break
					}
				}
				writeReady <- semaphore{}
				// 实测发现要按一次Ctrl + C才能让Python Shell 吐出 >>>
				// 但首次Ctrl + C已经被用于结束整个进程组
				log.Printf("输入子协程可以继续工作")
			}
		}
	}(shutdownCtx)

	// 输入写入子协程
	go func(ctx context.Context) {
		ticker := time.NewTicker(1 * time.Second)
		defer ticker.Stop()

		for {
			select {
			case <-ticker.C:
				log.Printf("输入写入子协程正在运行")
			case <-ctx.Done():
				return
			case <-writeReady:
				select {
				case input := <-inputChan: // 避免空通道读操作阻塞协程
					fmt.Printf("Go => %s\n", input)
					_, err = pipeIn.Write([]byte(input + "\n")) // 得加上换行符才能结束一次REPL
					if err != nil {
						log.Printf("写入输入时失败: %v", err)
						continue
					}
					log.Printf("已写入输入: %s", input)
				}
				readReady <- semaphore{}
				log.Printf("输出子协程可以继续工作")
			}
		}
	}(shutdownCtx)

	// 监听进程是否退出
	done := make(chan error, 1)
	go func() {
		err := cmd.Wait()
		done <- err
	}()
	for {
		select {
		case err := <-done:
			if err != nil {
				log.Printf("Python REPL已退出: %v", err)
			}
			goto Exit

		case <-time.After(5 * time.Second):
			log.Printf("响应超时, 主协程强制退出")
			goto Exit
		case <-ctx.Done():
			log.Printf("已收到退出信号")
			goto Exit
		}
	}

Exit:
	log.Printf("主协程已退出")
}
```  
  
### 踩坑经验  
- **缓冲区问题**：Python 在检测到输出流是管道时会启用缓冲，需要 `-u` 参数强制关闭缓冲  
- **换行符问题**：向 REPL 发送命令时必须加上 `\n` 换行符才能触发执行  
- **同步问题**：使用信号量机制协调协程间的执行顺序，避免读写冲突  
- **EOF处理**：正确关闭管道以发送 EOF 信号给接收方

## 第七阶段：文件锁
## 附录
### A. OS Shell管道概念和操作  
  
#### Shell管道概念  
- **定义**：管道（Pipeline）是一种进程间通信机制，允许一个命令的输出直接作为另一个命令的输入  
- **符号**：使用竖线 `|` 连接多个命令  
- **原理**：前一个命令的标准输出（stdout）连接到后一个命令的标准输入（stdin）  
  
#### Shell管道操作  
```bash  
# 基本管道操作  
ls -la | grep ".txt" | wc -l  
  
# 将命令输出重定向到文件  
echo "Hello World" > output.txt  
  
# 追加到文件末尾  
echo "Hello Again" >> output.txt  
  
# 将文件内容作为命令输入  
cat input.txt | grep "pattern"  
  
# 合并标准输出和错误输出  
command 2>&1 | grep "error"  
```  
  
#### 高级管道操作  
```bash  
# 使用tee命令同时输出到文件和标准输出  
ls -la | tee output.log | head -5  
  
# 使用xargs处理管道中的数据  
find . -name "*.log" | xargs rm  
  
# 命令替换  
files=$(ls | grep ".txt")  
```  
  
#### 管道的局限性  
- **阻塞问题**：如果接收端不消费数据，发送端会被阻塞  
- **缓冲区大小**：管道有固定大小的缓冲区，填满后写入操作会阻塞  
- **单向通信**：管道是单向的，需要双向通信时需使用套接字或命名管道  
  
### B. Go pipe API详解  
  
#### os/exec包中的管道API  
  
##### (*Cmd).StdinPipe() (io.WriteCloser, error)  
- **功能**：创建一个写入到命令标准输入的管道  
- **返回值**：实现了io.WriteCloser接口的对象  
- **注意事项**：  
  - 必须在[Start()](file:///C:/Go/src/os/exec/exec.go#L967-L969)之前调用  
  - 写入完成后需要调用Close()发送EOF信号  
  
##### (*Cmd).StdoutPipe() (io.ReadCloser, error)  
- **功能**：创建一个从命令标准输出读取的管道  
- **返回值**：实现了io.ReadCloser接口的对象  
- **注意事项**：  
  - 必须在[Start()](file:///C:/Go/src/os/exec/exec.go#L967-L969)之前调用  
  - 读取完成后需要调用Close()  
  
##### (*Cmd).StderrPipe() (io.ReadCloser, error)  
- **功能**：创建一个从命令标准错误输出读取的管道  
- **返回值**：实现了io.ReadCloser接口的对象  
- **注意事项**：  
  - 必须在[Start()](file:///C:/Go/src/os/exec/exec.go#L967-L969)之前调用  
  - 与StdoutPipe()类似  
  
#### io包中的管道相关API  
  
##### io.Copy(dst io.Writer, src io.Reader) (written int64, err error)  
- **功能**：将数据从src复制到dst，直到遇到EOF或错误  
- **应用场景**：在管道间复制数据  
- **注意事项**：  
  - 会阻塞直到复制完成或遇到错误  
  - 适合处理大量数据的传输  
  
##### io.Pipe() (*PipeReader, *PipeWriter)  
- **功能**：创建一个同步的内存管道  
- **返回值**：读取器和写入器  
- **应用场景**：  
  - 在goroutine间传递数据  
  - 需要在多个地方处理相同数据流时  
  
##### io.MultiWriter(writers ...io.Writer) io.Writer  
- **功能**：创建一个多路写入器，将数据写入所有提供的writer  
- **应用场景**：  
  - 同时输出到多个目的地  
  - 记录日志的同时显示在控制台  
  
##### io.TeeReader(r io.Reader, w io.Writer) io.Reader  
- **功能**：创建一个读取器，在读取数据的同时将数据写入w  
- **应用场景**：  
  - 数据传输时统计流量  
  - 记录数据流内容  
  
#### bufio包中的管道相关API  
  
##### bufio.Scanner  
- **功能**：用于读取和分割输入的数据  
- **特点**：  
  - 按预定义的分隔符（如换行符）分割数据  
  - 适合处理文本数据  
  - 注意：在管道中使用时，如果没有遇到分隔符会一直阻塞  
  
##### bufio.NewReader(rd io.Reader)  
- **功能**：创建一个带缓冲的读取器  
- **优点**：  
  - 提高读取效率  
  - 提供更多读取方法  
  
### C. OS进程与线程概念  
  
#### 进程(Process)  
- **定义**：操作系统分配资源的基本单位，拥有独立的内存空间  
- **特点**：  
  - 每个进程都有自己的虚拟地址空间  
  - 进程间相互隔离，一个进程崩溃不会影响其他进程  
  - 进程间通信需要特殊机制（管道、消息队列、共享内存等）  
  - 创建和销毁开销较大  
  
#### 线程(Thread)  
- **定义**：CPU调度的基本单位，同一进程内的多个线程共享内存空间  
- **特点**：  
  - 同一进程内的线程共享进程的内存空间  
  - 线程间可以直接访问共享数据  
  - 线程切换开销比进程小  
  - 一个线程崩溃可能影响整个进程  
  
#### 进程关系  
- **父进程与子进程**：通过 fork() 系统调用创建，子进程继承父进程的部分属性  
- **进程组**：一组相关进程的集合，通常由 shell 创建，用于信号处理  
- **会话(Session)**：包含一个或多个进程组，通常对应一个登录会话  
  
### D. 常用Exit Status  
  
| 状态码 | 含义 |  
|--------|------|  
| 0 | 成功退出 |  
| 1 | 一般性错误 |  
| 2 | shell内置命令使用错误 |  
| 126 | 命令不可执行 |  
| 127 | 命令未找到 |  
| 128+n | 由信号n终止 (如信号2(SIGINT) -> 130) |  
| 128 | 被信号中断（常见于进程被优雅关闭） |  
| 130 | 被SIGINT(键盘中断)终止 |  
| 137 | 被SIGKILL终止（通常是OOM killer或手动kill -9） |  
| 143 | 被SIGTERM终止（优雅关闭） |  
  
### E. Go标准库API详解  
  
#### os/exec包主要API  
  
##### exec.Command(name string, arg ...string) *Cmd  
- **功能**：创建一个执行指定命令的Cmd结构体  
- **参数**：name为命令名，arg为参数列表  
- **返回值**：*Cmd指针  
- **注意事项**：  
  - 命令路径中包含空格时需要使用完整路径  
  - 参数应分别传入，不要拼接成字符串  
  
##### exec.CommandContext(ctx context.Context, name string, arg ...string) *Cmd  
- **功能**：使用上下文创建Cmd，支持超时和取消  
- **参数**：ctx用于控制命令生命周期  
- **注意事项**：  
  - 当ctx被取消时，命令会被终止  
  - 适用于需要超时控制的场景  
  
##### (*Cmd).Run() error  
- **功能**：执行命令并等待其完成  
- **返回值**：nil表示成功，否则返回错误  
- **注意事项**：  
  - 会阻塞调用goroutine直到命令完成  
  - 返回exec.ExitError类型的错误可获取退出状态  
  
##### (*Cmd).Start() error  
- **功能**：启动命令但不等待完成  
- **返回值**：nil表示启动成功  
- **注意事项**：  
  - 需要调用Wait()等待命令结束  
  - 可以在命令运行期间执行其他操作  
  
##### (*Cmd).Wait() error  
- **功能**：等待由Start()启动的命令完成  
- **返回值**：命令退出状态  
- **注意事项**：  
  - 只能调用一次  
  - 必须在Start()之后调用  
  
##### (*Cmd).CombinedOutput() ([]byte, error)  
- **功能**：执行命令并返回合并的标准输出和错误输出  
- **返回值**：输出字节切片和错误  
- **注意事项**：  
  - 适合获取命令输出的小量数据  
  - 对于大量输出可能导致内存问题  
  
#### 高级字段和方法  
  
##### (*Cmd).WaitDelay time.Duration  
- **功能**：设置等待子进程优雅退出的时间，超过此时间后会强制终止进程  
- **用途**：当发送信号给子进程后，如果子进程在WaitDelay时间内未自行退出，  
  Go运行时会直接调用os.Kill强制终止进程  
- **默认值**：无限制  
- **使用场景**：  
```go  
cmd := exec.Command("some-long-running-process")  
cmd.WaitDelay = 5 * time.Second  // 5秒后强制终止  
```  
  
##### (*Cmd).Cancel func() error  
- **功能**：自定义取消函数，当关联的Context被取消时调用  
- **用途**：提供对取消操作的精细控制  
- **使用场景**：  
```go  
cmd := exec.CommandContext(ctx, "some-command")  
cmd.Cancel = func() error {  
    // 发送特定信号而非直接终止  
    return cmd.Process.Signal(syscall.SIGTERM)}  
```  
  
##### (*Cmd).SysProcAttr *syscall.SysProcAttr  
- **功能**：设置系统特定的进程属性  
- **主要子字段**：  
  - `Setpgid bool`：设置新进程组ID  
  - `Pgid int`：指定进程组ID  
  - `Credential *syscall.Credential`：设置进程凭据（用户/组）  
  - `Setsid bool`：创建新会话  
- **使用场景**：  
```go  
cmd.SysProcAttr = &syscall.SysProcAttr{  
    Setpgid: true,  // 创建新的进程组  
    Pgid:    0,     // 使用子进程PID作为PGID  
}  
```  
  
##### (*Cmd).ProcessState *os.ProcessState  
- **功能**：存储命令执行后的状态信息  
- **用途**：在调用Wait()或Run()后，此字段包含进程的退出状态  
- **可用方法**：  
  - `ProcessState.Exited()`：检查进程是否正常退出  
  - `ProcessState.Success()`：检查是否成功退出（退出码为0）  
  - `ProcessState.Sys()`：获取系统特定的退出信息  
  - `ProcessState.String()`：返回人类可读的退出状态描述  
  
#### context包主要API  
  
##### context.WithTimeout(parent Context, timeout time.Duration) (Context, CancelFunc)  
- **功能**：创建一个带超时的上下文  
- **参数**：parent为父上下文，timeout为超时时间  
- **返回值**：新上下文和取消函数  
- **注意事项**：  
  - 超时后自动取消上下文  
  - 必须调用CancelFunc释放资源  
  
##### context.WithCancel(parent Context) (Context, CancelFunc)  
- **功能**：创建一个可手动取消的上下文  
- **返回值**：新上下文和取消函数  
- **注意事项**：  
  - 调用取消函数会取消上下文  
  - 适用于需要手动控制的场景  
  
#### os/signal包主要API  
  
##### signal.Notify(c chan<- os.Signal, sig ...os.Signal)  
- **功能**：将指定信号转发到通道  
- **参数**：c为目标通道，sig为要监听的信号  
- **注意事项**：  
  - 通道必须有足够的容量接收信号  
  - 可以监听多个信号类型  
  
##### signal.NotifyContext(parent context.Context, sig ...os.Signal) (ctx context.Context, stop context.CancelCauseFunc)  
- **功能**：创建一个在接收到指定信号时取消的上下文（Go 1.20+）  
- **返回值**：新上下文和停止函数  
- **注意事项**：  
  - 适用于优雅关闭场景  
  - 会自动处理信号并取消上下文  
  
#### syscall包主要API  
  
##### syscall.Kill(pid int, sig syscall.Signal) error  
- **功能**：向指定进程发送信号  
- **参数**：pid为进程ID，sig为信号类型  
- **注意事项**：  
  - pid为负数时发送到进程组  
  - 需考虑权限问题  
  
### F. 使用示例与最佳实践  
  
#### 安全执行命令的完整示例  
```go  
func SafeExecute(timeout time.Duration, name string, args ...string) (output string, exitCode int, err error) {  
    ctx, cancel := context.WithTimeout(context.Background(), timeout)    defer cancel()  
    cmd := exec.CommandContext(ctx, name, args...)    // 捕获输出  
    var stdout, stderr bytes.Buffer    cmd.Stdout = &stdout    cmd.Stderr = &stderr        err = cmd.Run()  
    // 提取退出码  
    exitCode = 0    if err != nil {        var exitError *exec.ExitError        if errors.As(err, &exitError) {            if status, ok := exitError.Sys().(syscall.WaitStatus); ok {                exitCode = status.ExitStatus()            } else {                exitCode = -1            }        } else {            exitCode = -1        }    }        output = stdout.String() + stderr.String()  
    return output, exitCode, err}  
```  
  
#### 优雅关闭进程的示例  
```go  
func gracefulShutdown(cmd *exec.Cmd) error {  
    // 先尝试优雅关闭  
    if err := cmd.Process.Signal(syscall.SIGTERM); err != nil {        return err    }    // 等待进程自行退出  
    done := make(chan error, 1)    go func() {        done <- cmd.Wait()    }()        select {  
    case <-time.After(5 * time.Second):        // 超时，强制终止  
        return cmd.Process.Kill()    case err := <-done:        return err    }}  
```
***
# 页面底部