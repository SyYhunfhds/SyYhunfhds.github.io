---
title: Appointment
icon: database
category:
  - 打靶
  - HTB
tags:
  - SQL时间盲注
  - SMB弱口令
  - SQL注入
  - sqlmap
date: 2025-07-10
---
## 参考资料 && 参考WP
- [OWASP TOP10 2021](https://owasp.org/Top10/)
- [HTB本题官方WP](blob:https://app.hackthebox.com/95efaac9-ce80-44e1-934f-5f098478bb1c)
***
## Tasks
### Task1 SQL全称是什么 
```
Structured Query Language
```
### Task2 SQL最常见的漏洞是什么
```
Sql Injection
```
### Task3 OWASP 2021 TOP10 确认的注入漏洞是哪个
>What is the 2021 OWASP Top 10 classification for this vulnerability?
```
A03:2021-injection
```
提示说是OWASP当年榜单的第三名
![](assets/Pasted%20image%2020250709234106.png)
点进去一看，SSTI RCE 客户端脚本注入 参数注入 资源注入（越权）全都试了一遍都不行……
![](assets/Pasted%20image%2020250709234948.png)
最后发现就叫这个名……
### Task4 Nｍap扫描靶机的`80`端口得到的服务是什么
>What does Nmap report as the service and version that are running on port 80 of the target?

```shell
└─# nmap -T5 -p 80 -A 10.129.107.24 

Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-07-09 11:51 EDT
Nmap scan report for 10.129.107.24
Host is up (0.00016s latency).

PORT   STATE    SERVICE VERSION
80/tcp filtered http
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: D-Link DFL-700 firewall (89%), HP Officejet Pro 8500 printer (89%), ReactOS 0.3.7 (89%), Sanyo PLC-XU88 digital video projector (89%), Sonus GSX9000 VoIP proxy (88%), Asus WL-500gP wireless broadband router (88%), Microsoft Windows 2000 (88%), Microsoft Windows Server 2003 Enterprise Edition SP2 (88%), Microsoft Windows Server 2003 SP2 (88%), Novell NetWare 6.5 (88%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops

TRACEROUTE (using port 80/tcp)
HOP RTT     ADDRESS
1   0.07 ms 192.168.100.2
2   0.05 ms 10.129.107.24

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 33.87 seconds
```

```
Apache/2.4.38 (Debian)
|Server|Apache/2.4.38 (Debian)|
Server nginx 2.4.38 ((Debian))

Apache httpd 2.4.38 ((Debian))
```
Nmap扫不出来版本号，进浏览器看一下
![](assets/Pasted%20image%2020250709235927.png)
但这不符合格式……

```
┌──(root㉿kali)-[~/Desktop]
└─# nmap -T5 -p 80 -sC -sV  10.129.107.24

Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-07-09 12:06 EDT
Nmap scan report for 10.129.107.24
Host is up (0.00064s latency).

PORT   STATE    SERVICE VERSION
80/tcp filtered http

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 5.55 seconds
```
- `-sC`：启动默认的脚本序列
- `-sV`：启动**版本探测**
byd扫不动一点
### Task5 HTTPS默认端口是什么
```
443
```
### Task6 在web应用领域 *文件夹* 被称做什么
>What is a folder called in web-application terminology?
```
directory
```
### Task7 `Not Found`的状态码是什么
```
404
```
### Task8 Gobuster中哪个参数用来显式指定爆破目录而不是爆破子域名
> Gobuster is one tool used to brute force directories on a webserver. What switch do we use with Gobuster to specify we're looking to discover directories, and not subdomains?

```
dir
```

![](assets/Pasted%20image%2020250710001220.png)
### Task9 Mysql中哪个 *单字符* 是注释符
```
#
```
### Task10 弱口令登录进去后页面的第一个单词是什么
>If user input is not handled carefully, it could be interpreted as a comment. Use a comment to login as admin without knowing the password. What is the first word on the webpage returned?
```
Congratulations
```
![](assets/Pasted%20image%2020250710002242.png)
我管你这那的

时间盲注既然是测出来了，那应该能用，但受限于套娃VPN的网络环境，并没有成功爆破出数据

这题要点弱口令：
```
{username}'#:{random_password}
admin'#:{random_password_ascii}
```
![](assets/Pasted%20image%2020250710003007.png)
### flag
```
e3d0796d002a446c0e622226f42e9672
```
## 回顾

***
## 页面尾部