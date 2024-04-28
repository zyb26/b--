# Mysql 数据库

## 1. 下载 安装

### 1. 安装官网

### 2. 拉docker镜像

### 3.小皮 xp.cn/linux.html

## 2. 开启

1.services.msc

2.以管理员身份运行终端

net start mysql80

net stop mysql80

## 3.连接

1. 直接打开mysql命令端 123456
2. mysql -u root -p ([-h 127.0.0.1] [-p 3306] 可省略)

## 4. 连接远程服务器上的数据库

121.40.96.93 老师的ip

端口 3306

用户 gerry

密码 123456

# 5. 连接数据库后， 产看存在的数据库

show databases;

# 6. 创建一个数据库



create database game;

drop database game;

# 7. 选择使用一个数据库

use game;



# 8. 创建表

create table player(
	id int,
	name VARCHAR(100),
	level int,
	exp int,
	gold DECIMAL(10, 2)
)

# 9. 查询表结构

desc player;



# 10. 修改表 [ ] 内是自己定的

修改 表格 name 对应得数据类型

ALTER table [player]  MODIFY COLUMN [name] [VARCHAR(200)];

修改 表格 name 

ALTER table [player]  rename COLUMN   [name]   to     [nickname];

增加 一个字段

alter table player add column last_login timestamp;

删除一个字段

alter table player drop column last_login;

删除表

drop table player;

修改 数据类型

ALTER TABLE player modify level int DEFAULT 1;

# 11. 数据得增删查改

插入数据: INSERT into player (id, name, level, exp, gold) values (1, '张三'， 1， 1， 1）;

修改数据：update player set level=1 where name = "张三";

删除数据： delete from player where gold=0;

查询数据:select * from player;



# 12. 从数据库中导出数据

mysqldump -u root -p game  player > player.sql	



# 13. 从导入文件到数据库

mysql -u root -p game < game.sql






--------------------------------------------------------------------------------------------------------

# 14. 常用的关联表技巧（创建表格）
# INT AUTO_INCREMENT PRIMARY KEY
INT AUTO_INCREMENT ： 自动增长；自动生成无需主键手动
PRIMARY KEY: 主键；表中唯一标识符；每个表只能有一个主键

# 同名关联
# FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
FOREIGN KEY:同名关联
(CustomerID):关联键；引用其他表的主键列
REFERENCES: 和
Customer(CustomerID)
表名      主键

# 15. 创建数据的时候要在关键键的表格中选择id


# 16. 检索数据（关联的数据一块拿出来）
SELECT employees.name, departments.department_name 【两张表中想要拿出的列】
FROM employees【以哪个表为主表】
INNER JOIN departments【拼接的那张表】 ON employees.department_id = departments.department_id【关联的地方(关联键)】;
# INNER JOIN 可以换为 
# LEFT (OUTER) JOIN : 返回左边表中的所有行，以及右边表中与左边表中行匹配的行。如果右边表中没有匹配的行，则用 NULL 填充。
# RIGHT (OUTER) JOIN: 与 LEFT JOIN 类似，但是返回右边表中的所有行，以及左边表中与右边表中行匹配的行。
# FULL (OUTER) JOIN: 返回两个表中的所有行，如果没有匹配的行，则用 NULL 填充。
# CROSS JOIN: 返回两个表的笛卡尔积，即每个表中的每一行与另一个表中的每一行组合


# 17. 表格的关系图(整体思路)

# 员工

		# 订单      顾客

# 项目  

		# 产品      库存

# 供应商


# 18. 多表联合查询
SELECT 
  P.ProductName, 
  SUM(L.TotalPrice) AS TotalSales
FROM 
  Product P
  JOIN LineItem L ON P.ProductID = L.ProductID
  JOIN SalesOrder S ON L.SalesOrderID = S.SalesOrderID
WHERE 
  YEAR(S.OrderDate) = YEAR(CURDATE()) - 1
GROUP BY 
  P.ProductName;

# 解释
selcect 想要的列（属于哪个表格的）
from 哪个表 join 联合 on （关键键）条件 where 条件 group by 按照什么进行分组的
“SELECT [columns] FROM [table] JOIN [other_table] ON [condition] WHERE 
[condition] GROUP BY [column];”

