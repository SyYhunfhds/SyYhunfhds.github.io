---
title: Golang Gin框架（六）：Gin ORM
date: 2025-11-03
---
[[toc]]

## 参考资料
- [Gorm中文文档](https://gorm.io/zh_CN/docs/index.html)

***
# ORM（入门）
### 安装和配置
```sh
go get -u gorm.io/gorm  
go get -u gorm.io/driver/sqlite # 数据库驱动
```
### 快速上手
Gorm有两种API，一种是Gorm低于1.30.0版本的传统API，另一种是在这个版本之后的**泛型API**

> 放个[传送门](https://gorm.io/zh_CN/docs/index.html#%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8)

### 连接数据库
**Gorm**目前支持下面这些数据库：
- SQLite
- Mysql
- PostgreSQL
- GaussDB
- Oracle Database
- SQL Server
- TiDB
- ClickHouse
其中，Mysql、PostgreSQL、GaussDB都支持使用自定义驱动

这里只演示（*搬运*）Mysql和SQLite的连接方式：
```go
// 连接SQLite
import (  
  "gorm.io/driver/sqlite" // 基于 CGO 的 Sqlite 驱动  
  // "github.com/glebarez/sqlite" // 纯 Go 实现的 SQLite 驱动, 详情参考：https://github.com/glebarez/sqlite  
  "gorm.io/gorm"  
)  
  
// github.com/mattn/go-sqlite3  
db, err := gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{})
```

```go
// 连接Mysql
import (  
  "gorm.io/driver/mysql"  
  "gorm.io/gorm"  
)  
  
func main() {  
  // 参考 https://github.com/go-sql-driver/mysql#dsn-data-source-name 获取详情  
  dsn := "user:pass@tcp(127.0.0.1:3306)/dbname?charset=utf8mb4&parseTime=True&loc=Local"  
  db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})  
}
```

Gorm还提供了一些[**高级设置**](https://github.com/go-gorm/mysql)，这里直接把示例搬过来：
```go
db, err := gorm.Open(mysql.New(mysql.Config{  
  DSN: "gorm:gorm@tcp(127.0.0.1:3306)/gorm?charset=utf8&parseTime=True&loc=Local", // DSN data source name  
  DefaultStringSize: 256, // string 类型字段的默认长度  
  DisableDatetimePrecision: true, // 禁用 datetime 精度，MySQL 5.6 之前的数据库不支持  
  DontSupportRenameIndex: true, // 重命名索引时采用删除并新建的方式，MySQL 5.7 之前的数据库和 MariaDB 不支持重命名索引  
  DontSupportRenameColumn: true, // 用 `change` 重命名列，MySQL 8 之前的数据库和 MariaDB 不支持重命名列  
  SkipInitializeWithVersion: false, // 根据当前 MySQL 版本自动配置  
}), &gorm.Config{})
```


**本地运行测试**：
```go
func init() {  
    var err error  
  
    dsn := config.Config.DB.Serialize()  
    fmt.Printf("dsn: %v\n", dsn)  
    // user:pass@tcp(localhost:3306)/app?charset=utf8mb4&parseTime=true&loc=Local  
    DBConn, err = gorm.Open(mysql.Open(dsn), &gorm.Config{})  
  
    if err != nil {  
       panic("failed to connect database")  
    }  
}
```
![](assets/Pasted%20image%2020251103202120.png)
### 声明模型
#### 模型定义
*感觉官方文档不是给初学者看的，因为文档的编排顺序是先教声明模型才教数据库连接……byd*

> 模型是使用普通结构体定义的。 这些结构体可以包含具有基本Go类型、指针或这些类型的别名，甚至是自定义类型（只需要实现 `database/sql` 包中的[Scanner](https://pkg.go.dev/database/sql/?tab=doc#Scanner)和[Valuer](https://pkg.go.dev/database/sql/driver#Valuer)接口）。
```go
// 示例
type User struct {  
  ID           uint           // Standard field for the primary key  
  Name         string         // A regular string field  
  Email        *string        // A pointer to a string, allowing for null values  
  Age          uint8          // An unsigned 8-bit integer  
  Birthday     *time.Time     // A pointer to time.Time, can be null  
  MemberNumber sql.NullString // Uses sql.NullString to handle nullable strings  
  ActivatedAt  sql.NullTime   // Uses sql.NullTime for nullable time fields  
  CreatedAt    time.Time      // Automatically managed by GORM for creation time  
  UpdatedAt    time.Time      // Automatically managed by GORM for update time  
  ignored      string         // fields that aren't exported are ignored  
}
```
- 具体数字类型如 `uint`、`string`和 `uint8` 直接使用。
- 指向 `*string` 和 `*time.Time` 类型的指针表示可空字段。
- 来自 `database/sql` 包的 `sql.NullString` 和 `sql.NullTime` 用于具有更多控制的可空字段。
- `CreatedAt` 和 `UpdatedAt` 是特殊字段，当记录被创建或更新时，GORM 会自动向内填充当前时间。
- 以小写字母开头的私有变量不会被映射
> 除了 GORM 中模型声明的基本特性外，强调下通过 serializer 标签支持序列化也很重要。 此功能增强了数据存储和检索的灵活性，特别是对于需要自定义序列化逻辑的字段。详细说明请参见 [Serializer](https://gorm.io/zh_CN/docs/serializer.html)。

**注意一下声明约定**：
1. **主键**：GORM 使用一个名为`ID` 的字段作为每个模型的默认主键。
2. **表名**：默认情况下，GORM 将结构体名称转换为 `snake_case` 并为表名加上复数形式。 例如，如果我们有一个叫`User`的结构体，那么在数据库中它会变成`users`，同样地，`GormUserName`会变成`gorm_user_names`
3. **列名**：GORM 自动将结构体字段名称转换为 `snake_case` 作为数据库中的列名。
4. **时间戳字段**：GORM使用字段 `CreatedAt` 和 `UpdatedAt` 来自动跟踪记录的创建和更新时间。

官方文档的**声明模型**没有提到如何自定义表名，这里补充一下：
- Gorm会访问*接收者类型为结构体值类型* 的`TableName`方法来获取表名
- 对于Psql数据库，可以用`TableName`方法显式指定表所在的结构名
```go
type User struct {  
    gorm.Model          // 里面自带ID主键、创建时间、更新时间和删除时间  
    Username     string `gorm:"uniqueindex;type:varchar(255)"`  
    Password     string `gorm:"not null;"`  
    Active       bool   `gorm:not null;default=false`  
    LastLoginAt  time.Time  
    LastLogoutAt time.Time  
}  
  
func (u User) TableName() string {  
    return "public.users" // 显示指定schema名为public  
}
```

#### 高级选项 （只是占个地方）
> 放个[传送门](https://gorm.io/zh_CN/docs/models.html#%E9%AB%98%E7%BA%A7%E9%80%89%E9%A1%B9)

### 迁移 && 一键建表
定义一个User表用于测试：
```go
type User struct {  
    ID        uint           // 无符号整型uint uint8可直接使用 // 对应列名id  
    Username  string         // 不加*号的字段都默认非空 // 对应列名username  
    Password  string         // 不加*号的字段都默认非空 // 对应列名password  
    Age       uint8          // 年龄字段 // 对应列名age  
    Nickname  sql.NullString // 昵称字段  
    CreatedAt time.Time      // 对应字段 created_at, 下同updated_at  
    UpdatedAt time.Time  
    // CreatedAt和UpdatedAt字段由Gorm自动管理, 用于追踪记录的创建和更新时间  
}
```
再在`db-init.go`的`init`函数中初始化数据库连接并建表，到`main.go`里import一下就行了：
```go
func init() {  
    var err error  
  
    dsn := config.Config.DB.Serialize()  
    fmt.Printf("dsn: %v\n", dsn)  
    // user:pass@tcp(localhost:3306)/app?charset=utf8mb4&parseTime=true&loc=Local  
    DBConn, err = gorm.Open(mysql.Open(dsn), &gorm.Config{})  
  
    if err != nil {  
       panic("failed to connect database")  
    }  
  
    if err = DBConn.AutoMigrate(&models.User{}); err != nil {  
       panic("failed to migrate database")  
    }  
}
```
运行效果如下：
![](assets/Pasted%20image%2020251103231015.png)

:::info 模型定义约定再放送
1. **主键**：GORM 使用一个名为`ID` 的字段作为每个模型的默认主键。
    
2. **表名**：默认情况下，GORM 将结构体名称转换为 `snake_case` 并为表名加上复数形式。 For instance, a `User` struct becomes `users` in the database, and a `GormUserName` becomes `gorm_user_names`.
    
3. **列名**：GORM 自动将结构体字段名称转换为 `snake_case` 作为数据库中的列名。
    
4. **时间戳字段**：GORM使用字段 `CreatedAt` 和 `UpdatedAt` 来自动跟踪记录的创建和更新时间。
:::
#### `Migrator`接口
Migrator接口看上去是个**迁移**接口，但其实还集成了查看表结构的诸多API——放个[传送门](https://gorm.io/zh_CN/docs/migration.html#Migrator-%E6%8E%A5%E5%8F%A3)

比如**建表**、**看表**、**查表是否存在**，甚至是重命名表：
```go
// 为 `User` 创建表  
db.Migrator().CreateTable(&User{})  
  
// 将 "ENGINE=InnoDB" 添加到创建 `User` 的 SQL 里去  
db.Set("gorm:table_options", "ENGINE=InnoDB").Migrator().CreateTable(&User{})  
  
// 检查 `User` 对应的表是否存在  
db.Migrator().HasTable(&User{})  
db.Migrator().HasTable("users")  
  
// 如果存在表则删除（删除时会忽略、删除外键约束)  
db.Migrator().DropTable(&User{})  
db.Migrator().DropTable("users")  
  
// 重命名表  
db.Migrator().RenameTable(&User{}, &UserInfo{})  
db.Migrator().RenameTable("users", "user_infos")
```
哦，还有个看数据库呢！
```go
db.Migrator().CurrentDatabase()
```
##### 查库 【都是占位的，知道就好】
##### 查表/建表
##### 查列/加列
##### 查视图/定义视图
##### 查约束、索引
## 我是CRUD Boy！
:::note
Gorm在 1.30版本后启用了**泛型API**，提供更简洁的API，而传统API仍能使用

下面将主要使用新版的**泛型API**作为演示
:::
### 增（创建记录）
**官方示例：**
```go
user := User{Name: "Jinzhu", Age: 18, Birthday: time.Now()}  
  
// Create a single record  
ctx := context.Background()  
err := gorm.G[User](db).Create(ctx, &user) // pass pointer of data to Create  
  
// Create with result  
result := gorm.WithResult()  
err := gorm.G[User](db, result).Create(ctx, &user)  
user.ID             // returns inserted data's primary key  
result.Error        // returns error  
result.RowsAffected // returns inserted records count
```


**示例：**
不知道是不是因为Go会自动解引用，新的表实例哪怕已经是指针，在`Create`的时候仍然要取地址`&`：
```go
// services/user.go

// UserRegister 创建用户  
//  
// 参数: user *models.User 调用方自己序列化表单  
// 返回: 错误信息  
func UserRegister(user *models.User) (err error) {  
    ctx := context.Background()  
    return gorm.G[*models.User](DBConn).Create(ctx, &user)  
}  
func UserPasswordVerify(username string, password string) (err error) {  
    // 占位  
    return nil  
}

// controllers/user.go
func UserRegisterAPI(c *gin.Context) {  
    var userReq models.User  
    if err := c.ShouldBind(&userReq); err != nil {  
       c.JSON(400, gin.H{  
          "msg": "参数错误",  
          "err": err.Error(),  
       })  
       return  
    }  
  
    if err := services.UserRegister(&userReq); err != nil {  
       c.JSON(400, gin.H{  
          "msg": "注册失败",  
          "err": err.Error(),  
       })  
       return  
    }  
    c.JSON(200, gin.H{  
       "msg": "注册成功",  
    })  
}

// routers/user.go
func UserRouterInit(r *gin.Engine) {  
    routerGroup := r.Group("/api/v1/user")  
    {  
       routerGroup.POST("/register", controllers.UserRegisterAPI)  
    }  
}
```

#### 批量Insert
```go
users := []*User{  
    {Name: "Jinzhu", Age: 18, Birthday: time.Now()},  
    {Name: "Jackson", Age: 19, Birthday: time.Now()},  
}  
  
result := db.Create(users) // pass a slice to insert multiple row  
  
result.Error        // returns error  
result.RowsAffected // returns inserted records count
```

#### 更多用法 【占位】
![](assets/Pasted%20image%2020251104202711.png)
### 查（查询记录）
不只有[普通查询](https://gorm.io/zh_CN/docs/query.html)还有[高级查询](https://gorm.io/zh_CN/docs/advanced_query.html)
#### 查询单条记录
```go
ctx := context.Background()  
  
// Get the first record ordered by primary key  
user, err := gorm.G[User](db).First(ctx)  
// SELECT * FROM users ORDER BY id LIMIT 1;  
  
// Get one record, no specified order  
user, err := gorm.G[User](db).Take(ctx)  
// SELECT * FROM users LIMIT 1;  
  
// Get last record, ordered by primary key desc  
user, err := gorm.G[User](db).Last(ctx)  
// SELECT * FROM users ORDER BY id DESC LIMIT 1;  
  
// check error ErrRecordNotFound  
errors.Is(err, gorm.ErrRecordNotFound)
```

#### 查询多条记录
```go
// Get all records  
result := db.Find(&users)  
// SELECT * FROM users;  
  
result.RowsAffected // returns found records count, equals `len(users)`  
result.Error        // returns error
```

#### 带条件查询
##### 结构体交集查询
```go
db.Where(&User{Name: "jinzhu"}, "name", "Age").Find(&users)  
// SELECT * FROM users WHERE name = "jinzhu" AND age = 0;  
  
db.Where(&User{Name: "jinzhu"}, "Age").Find(&users)  
// SELECT * FROM users WHERE age = 0;
```
#### Group By 聚合查询
根据某个字段对查询结果进行分组聚合，**重点是聚合**

##### 注意事项
###### 子查询中的Group By
```go
products = &[]models.CategorifiedProduct{}  
DBConn.Model(&models.Product{}).  
    Where("id IN (?)", IDs).  
    Group("category").  
    Omit("deleted_at").  
    Find(products)
```
![](assets/Pasted%20image%2020251108160631.png)

你说得对，但这是Mysql 5.7+的`only_full_group_by`特性……
#### 更多内容
![](assets/Pasted%20image%2020251104204446.png)

### 高级查询
#### 智能选择字段
> [传送门](https://gorm.io/zh_CN/docs/advanced_query.html#%E6%99%BA%E8%83%BD%E9%80%89%E6%8B%A9%E5%AD%97%E6%AE%B5)

#### 子查询
> [传送门](https://gorm.io/zh_CN/docs/advanced_query.html#%E5%AD%90%E6%9F%A5%E8%AF%A2)

#### 带多个列的`In`查询
> [传送门](https://gorm.io/zh_CN/docs/advanced_query.html#%E5%B8%A6%E5%A4%9A%E4%B8%AA%E5%88%97%E7%9A%84-In)


### 更新 Update
> [传送门](https://gorm.io/zh_CN/docs/update.html)
#### 保存所有字段
> `Save` 会保存所有的字段，即使字段是零值
```go
db.First(&user)  
  
user.Name = "jinzhu 2"  
user.Age = 100  
db.Save(&user)  
// UPDATE users SET name='jinzhu 2', age=100, birthday='2016-01-01', updated_at = '2013-11-17 21:34:10' WHERE id=111;
```
*只有老API才有这个操作，新API则专注于精准更新(同时仍然以空值覆盖旧值)*
`Save` is an upsert function:
- If the value contains no primary key, it performs `Create`
- If the value has a primary key, it first executes **Update** (all fields, by `Select(*)`).
- If `rows affected = 0` after **Update**, it automatically falls back to `Create`.

#### 更多内容

### 删除 Delete
**删除一条记录时，删除对象需要指定主键，否则会触发 [批量删除](https://gorm.io/zh_CN/docs/delete.html#batch_delete)，例如：**
#### 删除一条记录
```go
ctx := context.Background()  
  
// Delete by ID  
err := gorm.G[Email](db).Where("id = ?", 10).Delete(ctx)  
// DELETE from emails where id = 10;  
  
// Delete with additional conditions  
err := gorm.G[Email](db).Where("id = ? AND name = ?", 10, "jinzhu").Delete(ctx)  
// DELETE from emails where id = 10 AND name = "jinzhu";
```
#### 删除多条记录
> 如果指定的值不包括主属性，那么 GORM 会执行批量删除，它将删除所有匹配的记录
```go
ctx := context.Background()  
  
// Batch delete with conditions  
err := gorm.G[Email](db).Where("email LIKE ?", "%jinzhu%").Delete(ctx)  
// DELETE from emails where email LIKE "%jinzhu%";
```
#### 软删除
> [传送门](https://gorm.io/zh_CN/docs/delete.html#%E8%BD%AF%E5%88%A0%E9%99%A4)
> 如果你的模型包含了 `gorm.DeletedAt`字段（该字段也被包含在`gorm.Model`中），那么该模型将会自动获得软删除的能力！
> 当调用`Delete`时，GORM并不会从数据库中删除该记录，而是将该记录的`DeleteAt`设置为当前时间，而后的一般查询方法将无法查找到此条记录。

```go
// user's ID is `111`  
db.Delete(&user)  
// UPDATE users SET deleted_at="2013-10-29 10:23" WHERE id = 111;  
  
// Batch Delete  
db.Where("age = ?", 20).Delete(&User{})  
// UPDATE users SET deleted_at="2013-10-29 10:23" WHERE age = 20;  
  
// Soft deleted records will be ignored when querying  
db.Where("age = 20").Find(&user)  
// SELECT * FROM users WHERE age = 20 AND deleted_at IS NULL;
```
## 事务
> [传送门](https://gorm.io/zh_CN/docs/transactions.html)

# 会话认证
## 哈希校验
### `golang.org/x/crypto/bcrypt`
> [文档传送门](https://pkg.go.dev/golang.org/x/crypto/bcrypt)

bcrypt包很精简，只提供了三个参数：
- `func CompareHashAndPassword(hashedPassword, password []byte) error`
	- 计算并比较哈希；可能返回下面两个错误 `variables`
		1. `var ErrHashTooShort = errors.New("crypto/bcrypt: hashedSecret too short to be a bcrypted password")`
			顾名思义，哈希值太短，不符合bcrypt的特征
		2. `var ErrMismatchedHashAndPassword = errors.New("crypto/bcrypt: hashedPassword is not the hash of the given password")`
			哈希值不匹配
- `func GenerateFromPassword(password []byte, cost int) ([]byte, error)`
	- 根据明文字节序列计算哈希值；可能抛出下面一个错误*变量*
		1. `var ErrPasswordTooLong = errors.New("bcrypt: password length exceeds 72 bytes")`
			明文字节序列长度大于72字节——Go中的UTF8码点一个是3字节，也就是说至多接受24个字符长的UTF8密码
- `func Cost(hashedPassword []byte) (int, error)`
	- 用于辅助开发者判断哪些密码需要更新
	- ~~看描述感觉没什么用~~

包内有三个常量，用于设置哈希花费：
```go
const (
	MinCost     int = 4  // the minimum allowable cost as passed in to GenerateFromPassword
	MaxCost     int = 31 // the maximum allowable cost as passed in to GenerateFromPassword
	DefaultCost int = 10 // the cost that will actually be set if a cost below MinCost is passed into GenerateFromPassword
)
```

**示例**：
```go
package scratch  
  
import (  
    "bytes"  
    "fmt"  
    "golang.org/x/crypto/bcrypt")  
  
func bcryptTest() {  
    passwd := bytes.NewBufferString("12345678") // 短密码测试  
    fmt.Printf("消息 %v 长度为%v\n", passwd.String(), passwd.Len())  
    hash, err := bcrypt.GenerateFromPassword(passwd.Bytes(), bcrypt.DefaultCost)  
    if err != nil {  
       fmt.Printf("哈希摘要处理消息%v时发生错误: %v\n", passwd.String(), err)  
    } else {  
       fmt.Printf("对明文%v进行哈希摘要得到: %v\n", passwd.String(), string(hash))  
    }  
  
    passwd = bytes.NewBufferString("你好世界这是一个二十四个字符长的明文啦啦啦啦啦啦啦") // 长密码测试  
    fmt.Printf("消息 %v 长度为%v\n", passwd.String(), passwd.Len())  
    hash, err = bcrypt.GenerateFromPassword(passwd.Bytes(), bcrypt.DefaultCost)  
    if err != nil {  
       fmt.Printf("哈希摘要处理消息%v时发生错误: %v\n", passwd.String(), err)  
    } else {  
       fmt.Printf("对明文%v进行哈希摘要得到: %v\n", passwd.String(), string(hash))  
    }  
      
    /*  
    消息 12345678 长度为8  
    对明文12345678进行哈希摘要得到: $2a$10$TQJa.ic21XUneaM0vlt9rOcOB9pwiQ3baPDYUYr0E5YOGBQmidkqC  
    消息 你好世界这是一个二十四个字符长的明文啦啦啦啦啦啦啦 长度为75  
    哈希摘要处理消息你好世界这是一个二十四个字符长的明文啦啦啦啦啦啦啦时发生错误: bcrypt: password length exceeds 72 bytes  
    */}
```
# 小试牛刀

***
# 页面底部