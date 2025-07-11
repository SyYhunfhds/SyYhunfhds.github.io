---
title: Responder
category:
  - 打靶
  - HTB
  - NTLM
  - 域渗透
tags:
  - NetNTLMv2哈希捕获
---
[[toc]]
## 参考资料 && 参考WP
- [HTB本题官方WP](blob:https://app.hackthebox.com/fb6f76ac-6b92-4b06-96e7-b4af6f871522)
- [博客园 - 域内三大协议](https://www.cnblogs.com/starrys/p/17140075.html)
- [Github - 64k star 2.3GB大的字典项目 -> SecLists](https://github.com/danielmiessler/SecLists)
- [Vaadata - NTLM身份认证与NTLM relay攻击（基于DNS和SMB）](https://www.vaadata.com/blog/understanding-ntlm-authentication-and-ntlm-relay-attacks/)
- [Gosecure - 基于PyRDP的NetNTLMv2哈希捕获 —— 技术细节与操作指南](https://gosecure.ai/blog/2022/01/17/capturing-rdp-netntlmv2-hashes-attack-details-and-a-technical-how-to-guide/)

***
## Tasks
### Task1 当使用靶机IP访问web服务时，我们被重定向到了什么域名
```
unika.htb
```
![](assets/Pasted%20image%2020250710211923.png)
### Task2 服务端用来渲染页面的语言是什么
```
php
```
三个字母，猜一下PHP
### Task3 页面使用什么查询参数来控制加载不同语言的文本
```
page
```
### Task4
下面哪一个是LFI（本地文件包含）的Payload：
- `french.html`
- `//10.10.14.6/somefile` （SMB共享路径）
- `../../../../../../../../windows/system32/drivers/etc/hosts` √
- `minikatz.exe` 

```plain
../../../../../../../../windows/system32/drivers/etc/hosts
```
### Task5 
下面哪一个是RFI（远程文件包含）的Payload

看答案格式猜出来的
```plain
//10.10.14.6/somefile
```
### Task6 NTLM的全称是什么
```plain
New Technology LAN Manager
```

>NTLM是NT LAN [Manager](https://baike.baidu.com/item/Manager/1607239?fromModule=lemma_inlink)的缩写，这也说明了协议的来源。NTLM是指 [telnet](https://baike.baidu.com/item/telnet/810597?fromModule=lemma_inlink) 的一种验证身份方式，即问询/应答[身份验证](https://baike.baidu.com/item/%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81/2193233?fromModule=lemma_inlink)协议，是 Windows NT 早期版本的标准安全协议，[Windows 2000](https://baike.baidu.com/item/Windows%202000/2769068?fromModule=lemma_inlink) 支持 NTLM 是为了保持[向后兼容](https://baike.baidu.com/item/%E5%90%91%E5%90%8E%E5%85%BC%E5%AE%B9/94553?fromModule=lemma_inlink)。Windows 2000内置三种基本安全协议之一。 [1]来自[*百度百科*](https://baike.baidu.com/item/NTLM/6371298)

### Task7 `Responder`靶机的工具中用于指定网络接口的参数是什么
>Which flag do we use in the Responder utility to specify the network interface?
```
-i
```

### Task8 
`john`是常用的数个用于爆破**NetNTLMv2**的工具之一，但……`john`的全称是什么
```plain
John the Ripper password cracker
```

![](assets/Pasted%20image%2020250710222345.png)
### Task9 `adminitrator`的口令是什么
```

```
### Task10
我们准备使用爆破得到的弱口令访问**Responder**靶机，请问这个服务在什么端口上监听
```
3389
```
猜测是RDP，具体是不是我也不清楚，毕竟Nmap扫不出来
## 打靶
这把不能盲猜了，得真扫了
```shell
└─# nmap -p- -T5 -sC -sV -A 10.129.117.4 
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-07-10 09:13 EDT
Stats: 0:03:19 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan
SYN Stealth Scan Timing: About 86.03% done; ETC: 09:17 (0:00:30 remaining)
Nmap scan report for 10.129.117.4
Host is up (0.0030s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.52 ((Win64) OpenSSL/1.1.1m PHP/8.1.1)
|_http-title: Site doesnot have a title (text/html; charset=UTF-8).
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Microsoft Windows XP SP3 or Windows 7 or Windows Server 2012 (98%), VMware Player virtual NAT device (98%), Microsoft Windows XP SP3 (96%), DD-WRT v24-sp2 (Linux 2.4.37) (94%), Actiontec MI424WR-GEN3I WAP (92%), Linux 4.4 (91%), Linux 3.2 (90%), DVTel DVT-9540DW network camera (89%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops

TRACEROUTE (using port 80/tcp)
HOP RTT     ADDRESS
1   0.21 ms 192.168.100.2
2   0.25 ms 10.129.117.4

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 254.50 seconds

```
![](assets/Pasted%20image%2020250710212503.png)
这对吗？

看了一下WP，原来是因为**Virtual Host**的锅——Virtual Host使得一台服务器可以配置多个域名
所以访问主IP时会被解析到某个虚拟域名，而直接访问这个虚拟域名时又会因为本地DNS服务器没有记录导致域名解析失败

给Kali补个域名配置先
```shell
echo "<IP地址> unika.htb" >> /etc/hosts
```

```shell
echo "10.129.117.4 unika.htb" >> /etc/hosts
```

给Windows也补一个
```
C:\Windows\System32\drivers\etc\hosts
```

嘶……怎么上不去呢
![](assets/Pasted%20image%2020250710223335.png)
yakit和cURL都能正确解析URL
![](assets/Pasted%20image%2020250710223444.png)
点击语言选项确实有反应，虽说得换种方法加载出来
![](assets/Pasted%20image%2020250710223601.png)
`page`参数确实是控制页面语言的，并且是链接到了静态资源目录下的一个`.html`文件
考虑到我的浏览器无法解析域名，我全程都只能使用工具排查`page`参数的文件包含漏洞是否可用

![](assets/Pasted%20image%2020250710225924.png)
是windows系统的话……
![](assets/Pasted%20image%2020250710230505.png)
```shell
curl "http://unika.htb?page=../../Windows/System32/drivers/etc/hosts"
```
本地文件包含漏洞确认
![](assets/Pasted%20image%2020250710233442.png)
`http://`协议被禁用，但`file://`协议可以使用
![](assets/Pasted%20image%2020250710233808.png)
试不出来`php.ini`在哪

靶机是Windows系统，并且有文件包含漏洞的话能干啥呢🤔

***
## 页面底部