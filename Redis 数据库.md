# Redis 数据库

官网：https: redis.io

key-value

支持数据持久化,  可将内存中的数据, 存在磁盘, 重启可以再次加载

## 1.如何在本地搭建

先下载redis包  

cd到redis文件夹

开启服务：redis-server.exe         (--service -start 开启   --service -stop 关闭)

shutdown 关闭

## 2.如何本地连接

在开一个终端：直接redis-cli

keys * 查看所有的 键

put name xiaobai

get name

## 3.如何连接服务器的redis库

redis-cli --help

redis -cli -h 121.40.96.93

auth 密码

## 4.如何本地开启2个redis库

直接改config文件里的端口号6389

开启服务 .\redis -serve.exe --help

.\redis-serve.exe .\redis.windows_service.conf

连接

.\redis-cli -p 6389

## 5.redis工具

(Ip , Port)

16个db

key : value (string , list, dict)

key1:key2:key3:name

xiaobai

分布式用{}来定位

select 1 进入db1

## 6.可视化工具  驱动（在anconda中pip install redis 才能 import）

### 1. 小皮

### 2. pycharm中也有要在环境中安装库才能操作  直接anconda 中pip install redis

```python
python 

import redis

redis.__version__
```

## 7. 如何看怎么使用

### 1. 接触到一个库不知道怎么使用 pypi.org搜redis 可以找到用法

### 2. 或者在anconda.org 搜索 redis 可以找到用法。

### 3.直接去官网搜python

​	看驱动

## 8. pycharm可以安redis可视化视角

## 9.操作redis (键值)
redis-cli --raw (支持中文)
先选择一个库 select 0
keys * (查看所有键)
FLUSHALL 删除所有
quit 也能退出
clear 清空屏幕 同linux命令


增删查改
字符串
set key value # 增加
del key       # 删除
get key       # 查找
exists key    # 是否存在这个键
TTL key       # 产看一个键的过期时间
expire key 10 # 设置一个键的过期时间
setex key 5 value  # 直接设置一个带有过期时间的键值对
setnx key value # 只有键不存在才写入

列表
lpush letter a 添加一个列表  反向的
lrange letter 0 -1 获取列表
lpush letter b 再添加一个列表
lupsh letter c d e
rpush letter f 在后面添加
rpop letter  # 从列表后面删除元素
lpop letter 2 # 删除元素的个数
llen letter 查看列表元素的个数
ltrim letter 1 3 只保留 修剪

集合
SADD course redis # 创建集合
smembers course   # 查看集合中的元素
sismember course redis # 判断元素是否在集合中
srem course redis # 删除集合中的一个元素
交并集合也支持

有序集合
ZADD result 680 清华 660 北大 650 复旦 640 浙大  # 添加有序集合 集合名称 前面是分数(排序依据) 后面是学校名称
zrange result 0 -1
zrange result 0 -1 withscores
zscore result q  查询对应的分数
zrank result q 查询排名
zrevrank result q 反转排名
zrem result q 删除成员

hash 字典
添加字典
hset person name xiaobai 
hset person age 100
获取
hget person ...
hget person age
hgetall person
删除
hdel person age
判断
hexists person age



看菜鸟教程

​		数据库的key      数据库的value

hset      u:1001             字典

value  字符串 list  set集合  HASH  ZSET

```python
import redis
import time

def t0():
    # 相当于终端的redis-cli 连接数据库
    with redis.Redis(host="127.0.0.1", port=6379, db=0, password=None) as client:
        print(client.get("t01"))
        print(client.set("t01", "xiaobai"))
        print(str(client.get("t01"), encoding='utf-8'))

    # r = redis.Redis(host="127.0.0.1", port=6379, db=0, password=None)
    # r.close()

def t1():
    pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0, password=None)
    r = redis.Redis(connection_pool=pool)
    # 往redis中插入一条key-value, 而且value类型为string的数据, 如果成功返回True字符串, 否则返回None
    o = r.set(
        name="name",
        value="我是来自。。。",  # value可以是字符串，也可以是任意一个byte字节数据
        ex = 60, # 设置当前加入的key ex秒后过期(删除)
        # px = 10000, # 毫秒后过期; 不能和ex同时给定
        nx = False, # 当设置为True的时候, 当且仅当name(key)在redis中不存在的时候,才会插入
        xx = False # 当设置为True的时候, 当且仅当name(key)在redis中存在的时候,才会插入  nx xx 不能同时给True
    )
    print(type(o))
    print(o)
    # get就是获取String类型的key对应的value值
    print("_" * 100)
    o = r.get(name="name")
    print(type(o))
    print(o is None)
    if o is not None:
        print(str(o, encoding='utf-8'))


    # 设置key对应数据过期时间
    r.set("user:1001", "user123")
    r.expire(name='user:1001', time=10000) # 过期秒数
    r.pexpire(name='name', time=10000)     # 过期毫秒数
    print(f"剩余多少过期时间:{r.ttl(name='name')}s")

    print("_" * 100)

    # 让hash结构的value中添加数据
    o = r.hset(name="user:1002", key="id", value="1001")
    print(o)

    # name 是redis的键 后面是redis的值(保存的是字典)
    o = r.hset(name="user:1002", key="name", value="小白")
    print(o)
    o = r.hset(name="user:1002", mapping={
        "age": 17,
        "sex": "男",
        "address": "上海"
    })
    print(o)

    # 一次获取所有field的value数据 --> hgetall返回结果是一个字典, 如果key不存在, 那么返回字典为空{}
    o = r.hgetall(name='user:1002')
    print(type(o))
    print(o is None)
    # 要转换为字符串 不然是二进制文件
    print({str(k, encoding='utf-8'): str(o[k],encoding='utf-8') for k in o})
   
    # 针对我们需要的field可以采用(单一field), 只要key(name)或者field不存在, 返回的就是None
    o = r.hget(name='user:1002', key='name')
    print(type(o))
    print(o is None)
    if o is not None:
        print(str(o, encoding='utf-8'))
    # 针对我们需要的field可以采用多个field,返回一个List列表, 如果field存在对应位置为bytes, 如果field不存在, 那么对应位置为None
    o = r.hmget(name="user:1002", keys=['name', 'age', 'address', 'address2'])
    print(type(o))
    print(o is None)
    print([v if v is None else str(v, encoding='utf-8') for v in o])

    r.close() # 当不使用的时候, 记得close关闭

def t2():
    pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0, password=None)
    with redis.Redis(connection_pool=pool) as r:
        _t1 = time.time()
        n = 100
        for i in range(n):
            r.set(name=f'k:{i}', value=i, ex=220)
        print(time.time() - _t1)
        # r.set(name='h', value = "12")

# pipeline set
def t3():
    pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0, password=None)
    with redis.Redis(connection_pool=pool) as r:
        _t1 = time.time()
        n = 100
        _pipeline = r.pipeline()
        for i in range(n):
            _pipeline.set(name=f"l:{i}", value=i, ex=220)
        _pipeline.execute()
        print(time.time() - _t1)

# pipeline get
def t4():
    pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0, password=None)
    with redis.Redis(connection_pool=pool) as r:
        _t1 = time.time()
        _pipeline = r.pipeline()
        _pipeline.get('k:77')
        _pipeline.get("l:1")
        _pipeline.get("l:2")
        _pipeline.hmget(name="user:1002", keys=['name', 'age', 'address', 'address2'])
        _pipeline.hgetall('user:1002')
        _r = _pipeline.execute()
        print(len(_r))
        print(_r)

    # 召回(当前用户各个需要的召回策略对应的推荐商品id列表, 当前用户对应的各个向量召回模型对应的向量, 热门商品列表, 新商品列表)
    # _pipline = r.pipeline()
    # _pipeline.hmget('recall:10001', ['usercf', 'itemcf', 'mf'])
    # _pipeline.get('fm:10001')
    # _pipeline.get('dssm:10001')
    # _pipeline.get('hot_product')
    # _pipeline.get('new_product')
    # _r = _pipeline.execute()


if __name__ == '__main__':
    # t0()
    # t1()
    t2()
    t3()
    t4()
```

Redis 是单线程

pipline 多命令 （过程过多会阻塞）

## 10. Redis可能遇到的问题

mysql  --> redis  -->

为保证数据库和缓存一致; 把缓存设置为失效(过期时间为0)，直接让缓存从数据库中拿取

### 1. 缓存穿透

异常请求无法从缓存中拿, 每次都从数据库拿（异常商品id）无法命中   -->(填一个特殊值到redis)

### 2. 缓存击穿

key非常热点, 在缓存过期一瞬间, 有大量请求

锁的机制去更新

### 3. 缓存雪崩

​		缓存雪崩: 缓存服务器突然宕机, 大量数据同时过期，导致数据都落到了数据库 过期时间相同导致

	#### 解决方案

事前：redis 高可用 主从+哨兵 避免服务器全盘消失 （缓存过期时间添加随机值）

事中：本地缓存+服务限流&降级

事后：redis持久化， 一旦重启，自动从磁盘加载数据，快速恢复数据

### 4.脏数据
先写数据库再把redis设置为过期











​	





















