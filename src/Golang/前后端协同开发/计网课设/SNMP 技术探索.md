---
title: 计网课设技术探索：SNMP协议初见
date: 2025-12-04
---
## 工具
- [卓豪 SNMP MIB Browser](https://www.manageengine.cn/network-monitoring/help/mib-browser.html)
	- 功能强大，但是是专为运维开发的，体积较大
- [iReasoning MIB Browser](https://www.ireasoning.com/mibbrowser.shtml)
	- 轻量级SNMP MIB监视器
## SNMP介绍

## SNMP操作入门
![](assets/Pasted%20image%2020251204164545.png)
### 环境搭建
- Windows下通过**Server Manager**或**增加/移除程序**服务安装SNMP服务
- Linux下通过`apt`等包管理器安装snmpd：
	```sh
	sudo apt-get install snmpd
	
	# snmpd 默认不开启
	systemctl enable snmpd # 这边一步到位调成自启动
	```

#### Linux
![](assets/Pasted%20image%2020251205104932.png)
配置文件默认位于`/etc/snmp/snmpd.conf`

snmpd默认监听本地IPV4地址和所有IPV6地址的`161`端口：
```
# agentaddress: The IP address and port number that the agent will listen on.
#   By default the agent listens to any and all traffic from any
#   interface on the default SNMP port (161).  This allows you to
#   specify which address, interface, transport type and port(s) that you
#   want the agent to listen on.  Multiple definitions of this token
#   are concatenated together (using ':'s).
#   arguments: [transport:]port[@interface/address],...

agentaddress  127.0.0.1,[::1]
```

这里改成下面这样：
```
agentaddress  udp:161
```
表示监听所有IPV4地址的161端口

***
接下来是**团体名**（相当于密码）：
```
# rocommunity: a SNMPv1/SNMPv2c read-only access community name
#   arguments:  community [default|hostname|network/bits] [oid | -V view]

# Read-only access to everyone to the systemonly view
rocommunity  public default -V systemonly
rocommunity6 public default -V systemonly
```
- 这里默认团体名/密码是`public`
- `default`表示允许任何来源的IP访问
	- 生产环境中建议配置具体IP，如：`rocommunity public 192.168.1.0/24`
- `-V systemonly`表示所有用户对`systemonly`视图中的OID信息都**仅可读**
	- 不加这个参数，则所有用户对所有视图中的OID都拥有权限
	- 加了这个参数，可能会看不到内存、温控等参数

:::note
当前仅配置了读权限（`rocommunity`，即Read only community），如果需要配置写权限，那么需要使用参数`rwcommunity`）
拥有写权限意味着可以使用`Set`动作设置系统配置或状态——比如……

- **重启/关闭接口：** NMS 可以向 `ifAdminStatus` (接口管理状态) 这个 OID 发送 `Set` 指令，把值设为 `down`。
    
    - _后果：_ 网卡会被直接禁用，服务器断网。
        
- **修改系统信息：** NMS 可以修改 `sysLocation` 或 `sysName`。
    
    - _后果：_ 恶作剧或者导致资产管理混乱。
        
- **重置计数器：** NMS 可以清空网卡的流量统计数据。
    
- **重启设备 (特定设备)：** 在某些硬件路由器或 PDU (电源分配单元) 上，通过 SNMP 写特定的 OID 可以直接让设备重启或断电。
    
- **配置路由：** 在路由器上，SNMP 甚至可以用来添加或删除静态路由条目
:::


配置成这样，方便调试：
```
# rocommunity  public default -V systemonly
# rocommunity6 public default -V systemonly
rocommunity  SyYhunfhds default
rocommunity6 SyYhunfhds default
```

Nmap扫一下端口看看开没开：
```
C:\Users\SyYhunfhds>E:\CTF\Web\端口扫描工具\Nmap\nmap.exe 192.168.100.133 -p 161 -sU
Starting Nmap 7.94 ( https://nmap.org ) at 2025-12-05 11:01 中国标准时间
Nmap scan report for 192.168.100.133
Host is up (0.00025s latency).

PORT    STATE SERVICE
161/udp open  snmp
MAC Address: 00:0C:29:DA:58:E4 (VMware)
```
确认端口开启

### 验证Agent是否可以连接
#### Linux
验证服务是否正常，首先需要安装客户端工具（其实安装snmpd时会顺便安装客户端工具的）
- Debian/Ubuntu: `sudo apt install snmp`
- CentOS/RHEL: `sudo yum install net-snmp-utils`

使用`snmpwalk`获取系统信息：
```sh
# -v 2c: 使用 v2c 版本
# -c public: 使用刚才设置的团体名 public
# localhost: 目标地址 (如果在另一台机器测，换成 Linux 的 IP)
# system: 设备别名, 不加这个就是遍历系统中的所有OID信息

# snmpwalk -v 2c -c public localhost system
snmpwalk -v 2c -c SyYhunfhds localhost
```
![](assets/Pasted%20image%2020251205115945.png)
输出一堆OID什么的就说明成了



#### 附录（一）：解决Kali环境下MIB配置无法启用的问题
尝试`snmpwalk`遍历OID的时候发现`system`别名不管用：
```sh
┌──(root㉿kali)-[/tmp]
└─# snmpwalk -v 2c -c SyYhunfhds localhost system
system: Unknown Object Identifier (Sub-id not found: (top) -> system)

```
可能是因为Kali(Debian)系统默认不下载MIB文件的原因

补一下配置
```sh
sudo apt install snmp-mibs-downloader
```
回到`/etc/snmp/snmp.conf`（客户端配置，`snmpd.conf`是守护程序配置），取消`mibs : `行的注释：
![](assets/Pasted%20image%2020251205121447.png)
`# mibs: `表示**不加载任何MIB**，取消了注释则**表示加载任何MIB**

然后更新MIB库：
```sh
sudo download-mibs
```

但是仍然不行，于是尝试启用全部MIBS配置文件看看能不能出来：
```sh
MIBS=ALL snmpwalk -v 2c -c SyYhunfhds localhost system
```
![](assets/Pasted%20image%2020251205122133.png)
前面的配置文件是遍历失败的，后面是成功的——直接看成功的就好了

:::note 【Gemini】为什么会有那么多 "Cannot find module"？

这在 Linux（特别是 Kali/Debian）上是**常态**，这叫“MIB 依赖地狱”。

- **原因：** `snmp-mibs-downloader` 会把互联网上成千上万的标准 MIB 文件下载下来。这些文件之间有复杂的引用关系（类似于代码里的 `import`）。
    
    - 比如 `TRILL-OAM-MIB` 引用了 `IEEE8021-CFM-MIB`。
        
    - 但是因为文件名大小写、版本差异或者上游源文件缺失，导致找不到被引用的文件。
        
- **结论：** 这些报错都是关于一些非常生僻的协议（如 TRILL、LLDP、Energy Object），**完全不影响**你读取核心的系统信息（CPU、内存、网络）。
    
- **处理建议：** **直接忽略**。只要你关心的 OID 能解析出来就行。
:::

![](assets/Pasted%20image%2020251205122506.png)
然后去改一下客户端配置文件`/etc/snmp/snmp.conf`，给`mibs: `注释掉，不需要重启，之后跑命令就都是有效的了
![](assets/Pasted%20image%2020251205122312.png)

::: note 【Gemini】
ebian/Kali 系统默认保留这一行且**不注释**，是为了加快命令行的响应速度（解析 MIB 文件需要时间），并减少对非自由软件（Non-free MIBs）的依赖。但这导致了你现在的困境：虽然你下载了文件，但系统被配置为“视而不见”。
:::



***
# 页面尾部