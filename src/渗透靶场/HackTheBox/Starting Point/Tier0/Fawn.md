---
title: Fawn
icon: acorn
tags:
  - FTP匿名登录
  - XFTP
  - Nmap
date:
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
- `-A`：Active mode，启动交互模式
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

***
## 页面尾部