---
title: Sequal
icon: database
---
[[toc]]
## 参考资料 && 参考WP
- [HackViser - Mysql渗透](https://hackviser.com/tactics/pentesting/services/mysql#attack-vectors)
- [HTB本题官方WP](blob:https://app.hackthebox.com/a6eb1dd7-4de0-4fde-a787-7a5083c9ec35)
***
##  Tasks
### Task1 扫描得到的端口中哪个开着`Mysql`服务
```
3306
```
![](assets/Pasted%20image%2020250710173938.png)
### Task2 靶机运行的是Mysql社区版的哪个版本
```
MariaDB
```

![](assets/Pasted%20image%2020250710173954.png)
不是哥们？你开端口了吗？
![](assets/Pasted%20image%2020250710174054.png)
我寻思这不是开着的吗
![](assets/Pasted%20image%2020250710174158.png)
666

答案最后一个字符是`B`，不是MariaDB就是MongoDB！
### Task3 使用mysql命令行登录时，哪个参数用来指定用户名
```
-u
```
### Task4 MariaDB空口令登入时的用的是哪个用户名
```
root
```
弱口令随便猜几个，网络环境不大允许爆破
### Task5 SQL使用哪个符号表示匹配表中的所有字段
```
*
```
### Task6 SQL使用哪个符号作为语句分隔符
```
;
```
### Task7
Mysql实例中有三个常见的数据库（`mysql`、`user`和`priv`），请问实例中的第四个数据库是什么
>There are three databases in this MySQL instance that are common across all MySQL instances. What is the name of the fourth that's unique to this host?

```
htb
```
byd各种连接超时
![](assets/Pasted%20image%2020250710180039.png)
![](assets/Pasted%20image%2020250710180051.png)
![](assets/Pasted%20image%2020250710180100.png)

### flag
```shell
mysql -h 10.129.210.168 -u root --connect-timeout=10 --reconnect --init-command="select * from htb;"
```
……

## 回顾
***
## 页面尾部