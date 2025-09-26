---
title: Archetype MSSQL get shell
date: 2025-09-24
tags:
  - HackTheBox
  - MSSQL
  - 数据库
  - getshell
category:
  - 打靶
  - HTB
---
[[toc]]
## 参考资料
***
## 分题步骤
### 1. 哪个TCP端口上存在数据库服务
```sh
nmap -sV -Pn 10.129.102.154
```

```
Not shown: 996 closed tcp ports (reset)
PORT     STATE SERVICE      VERSION
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds Microsoft Windows Server 2008 R2 - 2012 microsoft-ds
1433/tcp open  ms-sql-s     Microsoft SQL Server 2017 14.00.1000
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 65.13 seconds

```

那么**1433端口**上存在MSSQL服务
### 2. SMB服务上的非管理员共享目录的名称是什么
```sh
smbclient --list=10.129.102.154
```
使用`smbclient`列出靶机上的可用共享目录：
```sh
┌──(root㉿kali)-[~]
└─# smbclient --list=10.129.102.154 # 这里随便写密码，反正不一定连得上
Password for [WORKGROUP\root]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        backups         Disk      
        C$              Disk      Default share
        IPC$            IPC       Remote IPC

```
带有`$`后缀的是*System Management* 账户，那么**backups**就应该是非管理员的账户

### 3. SMB共享文件里的口令是什么？
```sh
smbclient -L //10.129.102.154/backups -U backups ×
# 没有口令
```
![](assets/Pasted%20image%2020250924221538.png)
enum4linux显示靶机允许空口令登录，因此smbclient可以使用`-N`参数预先取消密码登录
```sh
smbclient -N //10.129.102.154/backups
```
- `-N`：不使用密码连接

```sh
dir
# 列出共享中的文件列表
```
![](assets/Pasted%20image%2020250924222526.png)
发现当前目录下有一个`dtsConfig`
get下来
```sh
get xxx /tmp/prod.dts
```
然后查看
```xml
<DTSConfiguration>
    <DTSConfigurationHeading>
        <DTSConfigurationFileInfo GeneratedBy="..." GeneratedFromPackageName="..." GeneratedFromPackageID="..." GeneratedDate="20.1.2019 10:01:34"/>
    </DTSConfigurationHeading>
    <Configuration ConfiguredType="Property" Path="\Package.Connections[Destination].Properties[ConnectionString]" ValueType="String">
        <ConfiguredValue>Data Source=.;Password=M3g4c0rp123;User ID=ARCHETYPE\sql_svc;Initial Catalog=Catalog;Provider=SQLNCLI10.1;Persist Security Info=True;Auto Translate=False;</ConfiguredValue>
    </Configuration>
</DTSConfiguration>  
```
获得数据库密码：
```
M3g4c0rp123
```
### 4. `Impacket`工具库中哪个脚本用于与MSSQL建立授权连接
![](assets/Pasted%20image%2020250924223510.png)
该工具库位于`/usr/share/doc/python3-impacket/examples`目录中
其中以`mssql`开头的两个工具分别是：
```
mssqlclient.py
mssqlinstance.py
```
根据题目描述，应该是`mssqlclient.py`

看一下帮助文档
```sh
└─# python3 mssqlclient.py --help 
# 或 impacket-mssqlclient -h
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

usage: mssqlclient.py [-h] [-db DB] [-windows-auth] [-debug] [-show] [-file FILE] [-hashes LMHASH:NTHASH] [-no-pass] [-k] [-aesKey hex key]
                      [-dc-ip ip address] [-target-ip ip address] [-port PORT]
                      target

TDS client implementation (SSL supported).

positional arguments:
  target                [[domain/]username[:password]@]<targetName or address>

options:
  -h, --help            show this help message and exit
  -db DB                MSSQL database instance (default None)
  -windows-auth         whether or not to use Windows Authentication (default False)
  -debug                Turn DEBUG output ON
  -show                 show the queries
  -file FILE            input file with commands to execute in the SQL shell

authentication:
  -hashes LMHASH:NTHASH
                        NTLM hashes, format is LMHASH:NTHASH
  -no-pass              don''t ask for password (useful for -k)             
  -k                    Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials
                        cannot be found, it will use the ones specified in the command line
  -aesKey hex key       AES key to use for Kerberos Authentication (128 or 256 bits)

connection:
  -dc-ip ip address     IP Address of the domain controller. If ommited it use the domain part (FQDN) specified in the target parameter
  -target-ip ip address
                        IP Address of the target machine. If omitted it will use whatever was specified as target. This is useful when target is the
                        NetBIOS name and you cannot resolve it
  -port PORT            target MSSQL port (default 1433)

```

### 5. 【止步于此】MSSQL的哪个拓展储存指令可用于启动Windows cmd shell？
首先尝试连接靶机的MSSQL
第三步中得到了MSSQL的密码：
```
M3g4c0rp123
```
以及用户ID：（域名是`ARCHETYPE`，用户名是`sql_svc`）
```
ARCHETYPE\sql_svc
```
接下来使用`mssqlclient`连接
```sh
impacket-mssqlclient [[domain/]username[:password]@]<targetName or address> -windows-auth
```

```sh
impacket-mssqlclient ARCHETYPE\sql_svc:M3g4c0rp123@10.129.102.154 -windows-auth
```
```sh
impacket-mssqlclient ARCHETYPE\sql_svc@10.129.102.154 -windows-auth
```
`-windows-auth`参数告诉工具使用Windows身份认证

然而死活连不上
```sh
┌──(root㉿kali)-[/usr/share/doc/python3-impacket/examples]
└─# ping -c 4 10.129.102.154     
PING 10.129.102.154 (10.129.102.154) 56(84) bytes of data.
64 bytes from 10.129.102.154: icmp_seq=1 ttl=127 time=256 ms
64 bytes from 10.129.102.154: icmp_seq=2 ttl=127 time=1521 ms
64 bytes from 10.129.102.154: icmp_seq=3 ttl=127 time=804 ms
64 bytes from 10.129.102.154: icmp_seq=4 ttl=127 time=2222 ms

--- 10.129.102.154 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3002ms
rtt min/avg/max/mdev = 256.095/1200.720/2221.784/740.692 ms, pipe 2
                                                                                                                                                          
┌──(root㉿kali)-[/usr/share/doc/python3-impacket/examples]
└─# impacket-mssqlclient ARCHETYPE\sql_svc:M3g4c0rp123@10.129.102.154 -windows-auth
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

[*] Encryption required, switching to TLS
                                                                                                                                                          
┌──(root㉿kali)-[/usr/share/doc/python3-impacket/examples]
└─# impacket-mssqlclient ARCHETYPE\sql_svc@10.129.102.154 -windows-auth
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

Password:
[*] Encryption required, switching to TLS
```

```sh
# -S: 服务器IP, -U: 用户名, -D: 域名, -P: 密码
sqsh -S 10.129.102.154 -U sql_svc -D ARCHETYPE -P 'M3g4c0rp123'
```
换个地区再回来试一下。新的靶机IP
```sh
10.129.170.84
```
```sh
impacket-mssqlclient ARCHETYPE\sql_svc:M3g4c0rp123@10.129.170.84 -windows-auth
```
![](assets/Pasted%20image%2020250924230325.png)
看来还是算了吧
### 6. 哪个脚本用于Windows上可提权的路径

### 7. 哪个文件里有管理员口令

### 8. 提交flag
***
## 页面尾部