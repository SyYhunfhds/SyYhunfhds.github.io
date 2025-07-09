---
title: Redeemer
icon: microchip
date: 2025-07-09
tags:
  - Redis无密码登录
  - Redis基础操作
category:
  - 打靶
  - HTB
---
[[toc]]
## 参考资料
- [菜鸟教程 - Redis教程](https://www.runoob.com/redis/redis-tutorial.html)
- [HackViser - Redis篇](https://hackviser.com/tactics/pentesting/services/redis)
- [HTB本题官方WP](blob:https://app.hackthebox.com/ffe2e2f5-a071-4220-94c5-14572336f0ce)
***
## Tasks
### 端口扫描结果
```shell
└─# nmap -T5 -p 6379 -A 10.129.14.31
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-07-09 09:45 EDT
Stats: 0:00:10 elapsed; 0 hosts completed (0 up), 1 undergoing Ping Scan
Parallel DNS resolution of 1 host. Timing: About 0.00% done
Nmap scan report for 10.129.14.31
Host is up (0.00032s latency).

PORT     STATE    SERVICE VERSION
6379/tcp filtered redis
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: D-Link DFL-700 firewall (89%), HP Officejet Pro 8500 printer (89%), ReactOS 0.3.7 (89%), Sanyo PLC-XU88 digital video projector (89%), Sonus GSX9000 VoIP proxy (88%), Asus WL-500gP wireless broadband router (88%), Microsoft Windows 2000 (88%), Microsoft Windows Server 2003 Enterprise Edition SP2 (88%), Microsoft Windows Server 2003 SP2 (88%), Novell NetWare 6.5 (88%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops

TRACEROUTE (using port 80/tcp)
HOP RTT     ADDRESS
1   0.21 ms 192.168.100.2
2   0.26 ms 10.129.14.31

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 33.94 seconds

```
先做了前三道题才回来扫的
### Task1 靶机开放了哪个TCP端口
```
6379
```
### Task2 上面的端口开放了什么服务
```
Redis
```
### Task3 Redis是什么类型的数据库
```
In-memory Database
```
答案的连字符都露出来了……what can I say
### Task4 哪一个CLI工具是用于和Redis服务器交互的
```
redis-cli
```
### Task5 redis-cli使用哪个参数来指定主机地址
![](assets/Pasted%20image%2020250709214743.png)
```
-h
```
### Task6 
**连接上Redis服务器后，使用哪个指令来获取Redis服务器的信息和统计数据**
```shell
hydra -P /usr/share/wordlists/fasttrack.txt redis://10.129.14.31
# hydra爆破结果显示靶机不需要密码登录

└─# redis-cli -h 10.129.14.31 -p 6379                                                                   
10.129.14.31:6379> 
# 
```

```shell
info
```
![](assets/Pasted%20image%2020250709215703.png)
### Task7 靶机的Redis服务是什么版本
```
5.0.7
```
登上去之后输入`info`指令查看
### Task8 使用哪个指令切换Redis数据库
```
select <整数索引>
```

![](assets/Pasted%20image%2020250709220036.png)
### Task9 索引`0`的数据库内有多少个键
>How many keys are present inside the database with index 0?


![](assets/Pasted%20image%2020250709221418.png)
使用`info`指令可以看到当前只有一个数据库（索引为`0`），其中只有四个**键**
```shell
4
```
### Task10 哪个指令用于获取数据库中的所有键
```shell
keys <模式>
keys * # 匹配所有key
```
![](assets/Pasted%20image%2020250709221646.png)
### flag
```
10.129.14.31:6379> dump flag # 序列化一个key
"\x00 03e1d2b376c37ab3f5319922053953eb\t\x00\xeff$7\xf4.\xdeE"
(1.07s)
10.129.14.31:6379> get flag # 获取一个key的值
"03e1d2b376c37ab3f5319922053953eb"
(2.56s)
```
## 回顾
### Redis基本操作

***
## 页面尾部