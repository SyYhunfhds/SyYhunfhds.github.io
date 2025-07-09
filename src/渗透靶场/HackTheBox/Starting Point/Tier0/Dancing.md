---
title: Dancing
icon: binary
date: 2025-07-09
tags:
  - SMB弱口令
  - enum4linux扫描SMB信息
  - SMB基础操作
icons: sqaure-share-nodes
category:
  - 打靶
  - HTB
---
[[toc]]
## 参考资料 &&  参考WP
- [维基百科  - SMB](https://it.wikipedia.org/wiki/Server_Message_Block)
- [HackViser - SMB 渗透 Intro](https://hackviser.com/tactics/pentesting/services/smb)
***
## Tasks
### Task1 `SMB`全称是什么
```
Server Message Block
```
### Task2 `SMB`的常用端口是什么
```
TCP 445
UDP 137 138 and TCP 137 139 (NetBIOS over TCP/IP)
```
### Task3 Nmap扫描端口`445`的结果
```shell
└─# nmap -T5 -A -p 445 10.129.255.122  
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-07-09 06:50 EDT
Nmap scan report for 10.129.255.122
Host is up (0.00024s latency).

PORT    STATE    SERVICE      VERSION
445/tcp filtered microsoft-ds <-- Task3
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|specialized
Running: Microsoft Windows XP|7|2012, VMware Player
OS CPE: cpe:/o:microsoft:windows_xp::sp3 cpe:/o:microsoft:windows_7 cpe:/o:microsoft:windows_server_2012 cpe:/a:vmware:player
OS details: Microsoft Windows XP SP3 or Windows 7 or Windows Server 2012, VMware Player virtual NAT device
Network Distance: 2 hops

TRACEROUTE (using port 80/tcp)
HOP RTT     ADDRESS
1   0.18 ms 192.168.100.2
2   0.22 ms 10.129.255.122

```
### Task4 哪个`switch`（开关）可以用来通过`smbclient`工具 *列出*  靶机上可用的共享
![](assets/Pasted%20image%2020250709190027.png)
```shell
└─# smbclient --list=10.129.255.122
Password for [WORKGROUP\root]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        WorkShares      Disk   
```
`root`弱口令，一试就出来了：`root`

也可以用下面的指令连接：
```shell
smbclient -L //10.129.255.122 -U root 
```
### Task5 靶机的SMB服务有几个共享 
```
4
```
### Task6 哪个共享是可以以空口令登入的
```shell
smbclient //<IP地址>/<共享名> -U <用户名>%<密码>
smbclient //10.129.255.122/WorkShares -U root%root
```
### Task7 smb shell中的哪个指令是用来下载文件的
![](assets/Pasted%20image%2020250709191101.png)
```shell
get
```
### Task8 提交flag
```shell
cd James.P
get flag.txt

5f61c10dffbc77a704d76016a22f1664
```
## 回顾
### `smbclient`基础操作
```shell
# 列出可用共享
smbclient --list=<IP>
smbclient -L //<IP> -U <username>%<passwd> 
```

```shell
# 登录
smbclient //<IP地址>/<共享名> -U <用户名>%<密码>
```

***
## 页面底部