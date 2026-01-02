---
title: 计网课设技术探索：SNMP协议初见
date: 2025-12-04
---
[[toc]]
## 工具
- [卓豪 SNMP MIB Browser](https://www.manageengine.cn/network-monitoring/help/mib-browser.html)
	- 功能强大，但是是专为运维开发的，体积较大
- [iReasoning MIB Browser](https://www.ireasoning.com/mibbrowser.shtml)
	- 轻量级SNMP MIB监视器
## SNMP介绍

## SNMP环境配置

### 环境搭建
- Windows下通过**Server Manager**或**增加/移除程序**服务安装SNMP服务
- Linux下通过`apt`等包管理器安装snmpd：
	```sh
	sudo apt-get install snmpd
	
	# snmpd 默认不开启
	systemctl enable snmpd # 这边一步到位调成自启动
	```

#### Linux
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
#### Windows
##### 安装
在设置中搜索*可用功能->查看功能->查看可用功能*， 勾选下面两项，等待安装即可
![](assets/Pasted%20image%2020251212175848.png)
![](assets/Pasted%20image%2020251212175906.png)

##### 配置SNMP
###### Windows7
![](assets/Pasted%20image%2020251212181236.png)

##### 防火墙放行
```powershell
netsh advfirewall firewall add rule name="SNMP-161-In"  dir=in  action=allow protocol=UDP localport=161
netsh advfirewall firewall add rule name="SNMP-161-Out" dir=out action=allow protocol=UDP localport=161
netsh advfirewall firewall add rule name="SNMP-162-In"  dir=in  action=allow protocol=UDP localport=162
netsh advfirewall firewall add rule name="SNMP-162-Out" dir=out action=allow protocol=UDP localport=162
```
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
## SNMP操作入门
**基于iReasoning MIB Browser**
![](assets/Pasted%20image%2020251205123523.png)
### 轮询菜单
**轮询**默认用于获取SNMP客户端的OID值
#### 创建轮询
![](assets/Pasted%20image%2020251205123620.png)

![](assets/Pasted%20image%2020251205161403.png)
记得点一下Advanced按钮，改一下community名称，不然轮询的时候会连不上

之后要设置轮询获取的值（默认的操作是`Get`，这里咱先不改）。去拿几个`system`子节点过来：
```sh
└─# snmpwalk -v 2c -c SyYhunfhds localhost system
SNMPv2-MIB::sysDescr.0 = STRING: Linux kali 6.8.11-amd64 #1 SMP PREEMPT_DYNAMIC Kali 6.8.11-1kali2 (2024-05-30) x86_64
SNMPv2-MIB::sysObjectID.0 = OID: NET-SNMP-MIB::netSnmpAgentOIDs.10
DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (28993) 0:04:49.93
SNMPv2-MIB::sysContact.0 = STRING: Me <me@example.org>
SNMPv2-MIB::sysName.0 = STRING: kali
SNMPv2-MIB::sysLocation.0 = STRING: Sitting on the Dock of the Bay
SNMPv2-MIB::sysServices.0 = INTEGER: 72
SNMPv2-MIB::sysORLastChange.0 = Timeticks: (0) 0:00:00.00

```
这里不需要手动设置，直接Add Variable -> Browse (OID)即可

![](assets/Pasted%20image%2020251205161451.png)


### 操作栏

#### 直接访问特定客户端的OID
在主页的操作栏设置IP地址（要求是已注册的客户端的IP地址）、端口、可读团体名称和SNMP版本（默认v1，这里建议改成V2）
![](assets/Pasted%20image%2020251205124409.png)

![](assets/Pasted%20image%2020251205153544.png)
填好信息之后就能看到了

![](assets/Pasted%20image%2020251205153813.png)
之后如果要添加别的OID键，可以直接在OID编辑页面点击Browse按钮
#### 图形化查看OID结点信息
![](assets/PixPin_2025-12-05_15-44-43.mp4)


#### `Get Next`遍历子节点
这里遍历的是system下的子节点，`.1.3.6.1.2.1.1.6.0`即`system`结点
![](assets/PixPin_2025-12-05_15-40-01.mp4)
#### `walk`遍历全部节点信息

![](assets/Pasted%20image%2020251205154346.png)
#### `Set`设置结点信息
`/etc/snmp/snmpd.conf`默认只启用**只读团体**：
```conf
# Read-only access to everyone to the systemonly view
# rocommunity  public default -V systemonly
# rocommunity6 public default -V systemonly
rocommunity  SyYhunfhds default
rocommunity6 SyYhunfhds default
```
我们需要手动添加一个`rwcommunity`来允许写动作，比如：
```
rwcommunity  bQgAaIbBdCcY default
rwcommunity6 bQgAaIbBdCcY default
```

改好之后找几个变量改改：
```
# syslocation: The [typically physical] location of the system.
#   Note that setting this value here means that when trying to
#   perform an snmp SET operation to the sysLocation.0 variable will make
#   the agent return the "notWritable" error code.  IE, including
#   this token in the snmpd.conf file will disable write access to
#   the variable.
#   arguments:  location_string
sysLocation    Sitting on the Dock of the Bay
sysContact     Me <me@example.org>
```
MIB Browser里的可读可写属性不一定对，比如`ipDefaultTTL`在MIB Browser里看起来是`read-write`的，但实际上仅读的……

这里改改`sysContact`就好了，记得把`sysContact`那行注释掉，不然会报错：
![](assets/Pasted%20image%2020251207121812.png)
现在就算是改好了
![](assets/Pasted%20image%2020251207121912.png)


## 像运维一样思考
现在我们已经知道如何设置轮询，也知道了如何创建一个Agent Connection，现在来看看如何像运维一样观察服务器运行吧
#### 察看核心负载
记得加载`UCD-SNMP-MIB.txt`配置文件，然后重启软件，才能刷新侧边栏
![](assets/Pasted%20image%2020251205164934.png)

#### 查看CPU占用率 `systemStats`
![](assets/Pasted%20image%2020251205165629.png)
- **ssCpuIdle/CPU空闲率**：当前为`99%`。这正常，就一测试环境，还能咋样……


#### 附录（二）：运维常看的设备
**由Gemini编辑**

对于 Linux 服务器（安装了 `net-snmp`），运维主要看两个 MIB 库：
1. **MIB-II (Standard)**: 标准库，主要看**网络**和**基础信息**。
2. **UCD-SNMP-MIB (Extension)**: Linux 扩展库（OID 前缀 `.1.3.6.1.4.1.2021`），**CPU、内存、负载**都在这里，比标准库好读得多。
	![](assets/Pasted%20image%2020251205163156.png)
	*这个需要自己加载，iReasoning默认不加载*
	*加载完还得重启软件才能刷新侧边栏*


:::note
- OID前缀里共有的`2021`是**加州大学戴维斯分校**团队的企业ID
	![](assets/Pasted%20image%2020251205162832.png)
:::

---
##### 一、 核心负载类 (Linux 专属)
- **运维视角：** 服务器卡不卡，先看 Load Average（负载）。
- **OID 前缀：** `.1.3.6.1.4.1.2021.10` (UCD-SNMP-MIB::laTable)

|**别名 (Alias)**|**完整 OID**|**类型**|**原始值示例**|**含义与处理**|
|---|---|---|---|---|
|**laLoad.1**|`.1.3.6.1.4.1.2021.10.1.3.1`|String|`"0.15"`|**1分钟负载**。直接就是字符串，后端不需要计算，直接转换成浮点数展示即可。|
|**laLoad.2**|`.1.3.6.1.4.1.2021.10.1.3.2`|String|`"0.08"`|**5分钟负载**。运维用来判断是突发卡顿还是持续卡顿。|
|**laLoad.3**|`.1.3.6.1.4.1.2021.10.1.3.3`|String|`"0.01"`|**15分钟负载**。|

> **提示：** 在 iReasoning 里输入 `.1.3.6.1.4.1.2021.10` 查看表格，你会发现 Linux 已经很贴心地帮你算好了。

---

##### 二、 CPU 使用率 (Linux 专属)

- **运维视角：** CPU 是在干活 (User/Sys) 还是在摸鱼 (Idle)？
- **OID 前缀：** `.1.3.6.1.4.1.2021.11` (UCD-SNMP-MIB::systemStats)

|**别名 (Alias)**|**完整 OID**|**类型**|**原始值示例**|**含义与处理**|
|---|---|---|---|---|
|**ssCpuUser**|`.1.3.6.1.4.1.2021.11.9.0`|Integer|`15`|**用户态使用率 (%)**。直接显示 `15%`。|
|**ssCpuSystem**|`.1.3.6.1.4.1.2021.11.10.0`|Integer|`5`|**内核态使用率 (%)**。直接显示 `5%`。|
|**ssCpuIdle**|`.1.3.6.1.4.1.2021.11.11.0`|Integer|`80`|**空闲率 (%)**。如果这个值长期低于 20，运维就要报警了。|

---
##### 三、 内存使用 (Linux 专属)

- **运维视角：** 内存快满了吗？SWAP 用了吗？
- **OID 前缀：** .1.3.6.1.4.1.2021.4 (UCD-SNMP-MIB::memory)
:::note
注：这里比标准的 `hrStorageTable` 简单，因为它直接给 kB 单位，不用乘分配单元。
:::

|**别名 (Alias)**|**完整 OID**|**类型**|**原始值示例**|**含义与处理**|
|---|---|---|---|---|
|**memTotalReal**|`.1.3.6.1.4.1.2021.4.5.0`|Integer|`16306500`|**物理内存总量 (kB)**。后端需除以 1024 换算成 MB。|
|**memAvailReal**|`.1.3.6.1.4.1.2021.4.6.0`|Integer|`8502300`|**物理内存可用量 (kB)**。注意：这通常包含 Buffer/Cache。|
|**memBuffer**|`.1.3.6.1.4.1.2021.4.14.0`|Integer|`204800`|**Buffer 占用 (kB)**。|
|**memCached**|`.1.3.6.1.4.1.2021.4.15.0`|Integer|`5102300`|**Cache 占用 (kB)**。|

> **关键公式：** 真实的应用程序内存使用率 = `(Total - Avail) / Total` * 100% (粗略计算)。
---
##### 四、 网络流量 (标准 MIB)

- **运维视角：** 网卡是不是跑满了？有没有丢包？
- **OID 前缀：** `.1.3.6.1.2.1.2.2` (MIB-II::ifTable)
:::note
注意：这是一个表格 (Table)，你需要遍历找到对应的网卡索引 (Index)。
:::

|**别名 (Alias)**|**完整 OID (示例 .2 代表 eth0)**|**类型**|**原始值示例**|**含义与处理**|
|---|---|---|---|---|
|**ifDescr**|`.1.3.6.1.2.1.2.2.1.2.2`|String|`"eth0"`|**网卡名称**。用于区分是哪个口。|
|**ifOperStatus**|`.1.3.6.1.2.1.2.2.1.8.2`|Integer|`1`|**状态**。`1`=Up (正常), `2`=Down (断网)。运维监控大屏通常用红/绿灯表示。|
|**ifInOctets**|`.1.3.6.1.2.1.2.2.1.10.2`|Counter32|`381293812`|**入站总流量 (Bytes)**。累加值，**必须做差值计算网速**。|
|**ifOutOctets**|`.1.3.6.1.2.1.2.2.1.16.2`|Counter32|`1928312`|**出站总流量 (Bytes)**。同上。|
|**ifInErrors**|`.1.3.6.1.2.1.2.2.1.14.2`|Counter32|`0`|**入站错误包数**。如果这个数在涨，说明网线或交换机有问题。|

---
##### 五、 磁盘使用率 (标准 MIB)

- **运维视角：** 根分区 / 还有多少空间？
- **OID 前缀：** `.1.3.6.1.2.1.25.2.3` (HOST-RESOURCES-MIB::hrStorageTable)
:::note
注意：这也是个表格，而且是最难处理的。
:::

|**别名 (Alias)**|**完整 OID (示例 .31)**|**类型**|**原始值示例**|**含义与处理**|
|---|---|---|---|---|
|**hrStorageDescr**|`...25.2.3.1.3.31`|String|`"/ "`|**分区路径**。找到等于 `/` 的那一行。|
|**hrStorageUnits**|`...25.2.3.1.4.31`|Integer|`4096`|**分配单元 (Bytes)**。极其重要！|
|**hrStorageSize**|`...25.2.3.1.5.31`|Integer|`5242880`|**总块数**。真实大小 = `Size * Units` = 20GB。|
|**hrStorageUsed**|`...25.2.3.1.6.31`|Integer|`1048576`|**已用块数**。真实已用 = `Used * Units`。|



## 使用snmp v3
![](assets/Pasted%20image%2020251207122641.png)
iReasoning MIB Browser不知为何不显示V3……

SNMP v3 不再使用“团体名” (Community)，而是使用 **“用户 (User) + 密码”**。而且为了加密，我们需要配置两个密码：
1. **验证密码 (Auth):** 证明你是谁。
2. **加密密码 (Priv):** 给数据加密。

```sh
# 关闭服务, 否则创建命令不生效
sudo systemctl stop snmpd
# 使用脚本创建用户
# 语法: -ro (只读) -A 验证密码 -a 验证算法 -X 加密密码 -x 加密算法 用户名
sudo net-snmp-create-v3-user -ro -A auth123456 -a SHA -X priv123456 -x AES v3user
```
- **用户名:** `v3user`
- **验证 (Auth):** 密码 `auth123456`，算法 `SHA`
- **加密 (Priv):** 密码 `priv123456`，算法 `AES`
然后重启服务：
```sh
sudo systemctl start snmpd
```

![](assets/Pasted%20image%2020251207123034.png)
接下来去Tools->Options->Agent设置V3连接
![](assets/Pasted%20image%2020251207123336.png)
调好之后再点开主页的`Advanced`就能看到新的配置项

![](assets/Pasted%20image%2020251207123501.png)
然后就会……

![](assets/Pasted%20image%2020251207124611.png)
直接上GoSNMP吧……

![](assets/Pasted%20image%2020251207124948.png)
非常妙
***
# 页面尾部