from py2neo import Graph
from py2neo.cypher import Cursor

# 获取ip --> quiery
graph = Graph(profile="neo4j://localhost:7687", auth=("neo4j", 12345678), name="zyb")
print(graph)


# 创建
def create():
    r1: Cursor = graph.run(
        "CREATE (n:Book{name:'深度学习基础', price:89.25}) RETURN n"
    )
    print(r1)
    print(type(r1))
    print(r1.to_data_frame())
    print(r1.forward(5))


def select():
    # 查询节点 -->[{'要查询的实体n':Node('类名', 属性=...)}]

    r2: list = graph.run(
        "MATCH (n:Book) RETURN n"     # "MATCH (n:Book) RETURN n AS "书本""
    ).data()

    from py2neo import Node
    # 查询 --> Node 就是一个实体
    # TODO:查询实体
    Node_n = r2[0]['n']     # 查询实体(节点属于哪个标签)
    print(Node_n.labels)    # 查询实体所属的类(label)
    print(Node_n.keys())    # 查询实体的属性

    # 查询关系 -->[ 关系(Node左,Node右)]
    # TODO:查询关系
    r3: list = graph.run(
        "MATCH ()-[r]->() RETURN r limit 5"    # 查询任何一个节点与另一个节点但的关系类型不做限制
    ).data()
    # return r2
    print(r3)

    # TODO:不使用.data 进行查询
    r4 = graph.run(
        """
        MATCH
            (p1:Person {name:'成龙'}) - [: 参演]->(movie) < -[: 参演]-(p2:Person)
        With p2
        MATCH
            (p2) - [: 参演]->(movie2)
        RETURN p2, movie2;
        """
    )

    while r4.forward():  # 相当于一个游标不断往后移动
        print("=" * 100)
        cur_record = r4.current    # 当前数据对象
        from py2neo.cypher import Record
        print(type(cur_record))    # 都是<class 'py2neo.cypher.Record'>
        # TODO:这个只是with语句中有P2 其他语句直接movie2
        print(cur_record['p2']["name"])   # Record对象 -> Node对象(关系对象)--> 属性
        print(cur_record['movie2'])
        print(cur_record)

        # TODO: LOAD CSV FROM 'file:///artists.csv' AS line 是CQL语句中加载csv文件 --> 可迭代的(一行)
        # 在python中 需要读取csv 然后进行遍历操作 可以使用panda 然后逐行写入

# 另一种写入的方式（只写入一行; 节点和关系同时写入）
from py2neo import Graph, Node, Relationship
def another():
    # 连接到 Neo4j 数据库
    uri = "bolt://localhost:7687"  # 你的数据库地址
    user = "neo4j"  # 你的用户名
    password = "your_password"  # 你的密码
    graph = Graph(uri, auth=(user, password))

    # 创建节点
    node1 = Node('所属类型', data='对应的数据')
    node2 = Node('所属类型', data='对应的数据')

    # 创建关系
    relation1 = Relationship(node1, '中标公司', node2)

    # 将节点和关系写入数据库
    graph.create(node1)
    graph.create(node2)
    graph.create(relation1)

if __name__ == "__main__":
    print(select())