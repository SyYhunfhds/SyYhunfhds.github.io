---
title: HTB - Starting Point - Tier0 - Fawn
icon: square-code
tags:
  - FTP匿名登录
  - XFTP
  - Nmap
date: 2025-07-09
---
[[toc]]
## 参考资料 && 参考WP
- [HackViser - FTP渗透](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://hackviser.com/tactics/pentesting/services/ftp&ved=2ahUKEwjJz-OMu6-OAxVQnf0HHcJ2DYYQFnoECBkQAQ&usg=AOvVaw0P__rxr-MwzvM6F6Z0dtt5)
- [维基百科 - FTP响应码](https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes)
***
## 打靶
### Task1 `FTP`是什么的简称
```
File Transfer Protocol
```
### Task2 `FTP`通常开放在什么端口
```
20 × 21 √
```
### Task3 
**FTP不对传输数据进行加密；SSH协议的\[]拓展协议实现了和FTP相似的功能，但同时可以做到加密传输，请问这个协议的简称是什么**
```
SFTP
```
### Task4
**用于测试与靶机的网络连通性，基于ICMP协议的工具是什么？**
```
ping
```
### Task5 扫描得到的FTP是什么版本
```shell
└─# nmap -T5 -A -p 20,21 10.129.247.214
PORT   STATE    SERVICE  VERSION
20/tcp filtered ftp-data
21/tcp open     ftp      vsftpd 3.0.3
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Actiontec MI424WR-GEN3I WAP (95%), DD-WRT v24-sp2 (Linux 2.4.37) (95%), Linux 3.2 (93%), Linux 4.4 (91%), Microsoft Windows XP SP3 or Windows 7 or Windows Server 2012 (89%), Microsoft Windows XP SP3 (88%), BlueArc Titan 2100 NAS device (87%), VMware Player virtual NAT device (87%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: OS: Unix <-- Task6

TRACEROUTE (using port 80/tcp)
HOP RTT     ADDRESS
1   0.19 ms 192.168.100.2
2   0.08 ms 10.129.247.214

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 49.79 seconds

```
- `-T5`：最大线程
- `-A --agressive`：进攻性扫描，扫描系统信息、脚本扫描和`tracert`路由跟踪
- `-p 20,21`：扫描FTP端口`20,21`
### Task6 扫描到的系统是什么
```
Unix
```
### Task7 用什么指令输出ftp客户端的帮助菜单
```shell
ftp -?
```
![](assets/Pasted%20image%2020250709172538.png)
### Task8 FTP访客账户登录用的用户名
```
anonymous
```
### Task9 FTP消息`login successful`的响应码是多少
```shell
└─# ftp -4 -A -a anonymous@10.129.247.214 21
Connected to 10.129.247.214.
220 (vsFTPd 3.0.3)
331 Please specify the password.
Password: 
230 Login successful. <-- Task9
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> 

```
- `-4`：显式使用IPv4地址
- `-A`：主动模式（*不推荐*，我后面一跑指令就掉线了）
- `-a`：匿名登录模式
- `anonymous@10.129.247.214 21`：`<username>@<host> <port>`
### Task10 FTP除了`dir`外另一个用来列出文件的指令（在Linux系统里也适用）是什么
```shell
ls
```
提示给足了
### Task11 FTP下载文件的指令是什么
```shell
get
```
![](assets/Pasted%20image%2020250709173902.png)
### Task12 提交flag
```

```
![](assets/Pasted%20image%2020250709174018.png)
## 回顾
### FTP主动模式 VS 被动模式
:::warning
Gemini 2.5 Pro 生成 + 人工整理
:::
无论是主动模式还是被动模式，FTP会话的开始都是完全一样的：
1. **客户端**会从自己的一个随机高位端口（大于1023，例如端口3000），主动连接到**FTP服务器**的**21号端口**。
2. 这条连接被称为**控制连接 (Control Connection)**。
3. 在这条连接上，客户端将发送所有的命令，比如`USER`（用户名）、`PASS`（密码）、`LIST`（列出目录）、`RETR`（下载文件）等。服务器也会通过这条连接返回命令的执行结果（如`200 OK`, `530 Login incorrect`）。
	![](assets/Pasted%20image%2020250709181435.png)

它们最大的不同在于：**建立“数据传输”连接时，到底是谁主动联系谁。**

文件和目录列表的数据量很大，不能在控制连接上传输。因此，FTP需要建立一条**临时的、全新的**连接，专门用来传输这些数据。这条连接就叫**数据连接 (Data Connection)**。（**主动模式与被动模式**的）区别就在于这条连接如何建立。
#### 主动模式
**主动模式 (Active Mode) - 服务器主动连接客户端**是FTP最初被设计时的工作方式：
1. **客户端“告诉”服务器自己的地址**: 当你需要传输数据时（例如，发送`LIST`命令），客户端会通过控制连接（21号端口）告诉服务器：“你好，我已经准备好了，请你从你的**20号端口**，主动连接到我的**IP地址的XXXX端口**来给我传数据。”（XXXX是客户端临时开放的一个端口）
2. **服务器“反向”连接**: FTP服务器收到指令后，会从自己的**数据端口（标准为20号端口）**，主动发起一个TCP连接，去连接客户端指定的那个高位端口（XXXX）。
3. **数据传输**: 连接建立后，文件或目录列表通过这条由**服务器主动发起**的连接进行传输。
:::important
这种模式在现代互联网上几乎已经**无法使用**。因为绝大多数用户都处在路由器（NAT）或防火墙后面。
- **问题**: 你的客户端虽然告诉了服务器自己的IP和端口，但这个IP通常是你的**内网IP**（如192.168.1.100）。服务器从公网根本无法访问这个地址。即使你知道自己的公网IP，你家里的路由器或公司的防火墙，也绝对不会允许一个**来自外部的、未经请求的连接**（服务器主动连你）进入你的内部网络。这会被防火墙当作是**黑客攻击**并直接拦截。
:::
**主动模式总结：**
- **控制连接**: 客户端 -> 服务器:21
- **数据连接**: 服务器:20 -> 客户端
#### 被动模式
**被动模式 (Passive Mode) - 客户端主动连接服务器**。为了解决主动模式的问题，被动模式被发明出来。这是**当今互联网上FTP使用的绝对主流方式**：
1. **客户端“请求”服务器开放端口**: 当你需要传输数据时，客户端会先发送一个`PASV`命令给服务器。
2. **服务器“告诉”客户端自己的地址**: 服务器收到`PASV`命令后，会在自己的**一个随机高位端口**（大于1023，例如端口50000）上开始监听。然后，它会通过控制连接告诉客户端：“你好，我已经准备好了，请你主动连接到我的**IP地址的50000端口**来取数据。”
3. **客户端主动连接**: 客户端收到服务器的IP和新端口号后，会从自己的另一个随机高位端口，主动发起一个TCP连接，去连接服务器指定的那个新端口（50000）。
4. **数据传输**: 连接建立后，文件或目录列表通过这条由**客户端主动发起**的连接进行传输。
:::tip
**被动模式**的**优势**在于能很好地穿越防火墙。因为**所有的连接都是由客户端主动向服务器发起的**。防火墙看到的是内部设备向外部发起的“正常”连接请求，通常会允许这种流量通过。
:::
**被动模式总结：**
- **控制连接**: 客户端 -> 服务器:21
- **数据连接**: 客户端 -> 服务器 (随机高位端口)

**模式的名字，描述的是服务器在数据连接中的角色。**
- **主动模式**：服务器**主动**连接你。
- **被动模式**：服务器**被动**等待你连接。
***
## 页面尾部