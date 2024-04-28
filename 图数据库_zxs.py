from py2neo import Graph, Node, Relationship, Subgraph, NodeMatcher, RelationshipMatcher

# 图数据库的问答链
def t1():
    graph = Graph('bolt://localhost:7687', user='neo4j', password='123456')
    llm = Spark(api_key='f41523a3e7b336a0a95b68ff97ec0a79',
                api_secret='NjUzOWY5YjI4ZTk0MTQ4MzkwZGFkY2M2',
                appid='12b981b5',
                domain='generalv3.5',
                spark_url='wss://spark-api.xf-yun.com/v3.5/chat'
                )
    sys = """请你根据我给出的图数据库信息构造Cypher语句，要求只回复Cypher语句，不需要加任何提示信息。\n
    样例：\n
    输入：我想知道能提供‘突发事件预警短消息发送平台’服务的公司有哪些？
    输出：MATCH (n:`公司`)-[:`服务`]->(n1:`标的物` {{bdw:"突发事件预警短消息发送平台"}}) RETURN n
    输入：中国移动通信集团安徽有限公司可以提供哪些服务？
    输出：MATCH (n:`公司` {{name: "中国移动通信集团安徽有限公司"}}) -[r:`服务`]->(n1) RETURN n1
    输入：{query}
    输出：
    """

    chain = LLMChain(llm=llm, prompt=sys)
    query = '重庆市信息通信咨询设计院有限公司可以提供什么服务'
    res = chain.invoke(inputs={'query': query})
    print(res)
    try:
        print(graph.run(res))
    except Exception as e:
        print(e)

# 通过mysql数据库关系抽取来构造图数据库
from agent.sql_tool import SqlTool
def t2():
    db = SqlTool(host='10.42.239.121', port=3306, database='xunfei5', user='root', password='123456')
    result = db.executor_query(
        'Select title, name, date, address, purchaser, bid_company from ods_tender where length(bid_company)>0 limit 5')
    print(result)

    llm = Spark(api_key='f41523a3e7b336a0a95b68ff97ec0a79',
                api_secret='NjUzOWY5YjI4ZTk0MTQ4MzkwZGFkY2M2',
                appid='12b981b5',
                domain='generalv3.5',
                spark_url='wss://spark-api.xf-yun.com/v3.5/chat')
    sys = ('请你从给定的标题中提取标的物,只需要回复标的物名称, 不需要回复任何标点符号！，样例：\n输入：安徽工商职业学院2023年庐阳校区水系统改造项目。输出：水系统改造。\n'
           '输入：肥西县中医院医疗器械器具清洗消毒灭菌服务。输出：医疗器械器具清洗消毒灭菌服务。\n输入{query}。输出：')
    chain = LLMChain(llm=llm, prompt=sys)

    # 构造图数据库关系
    relations = []
    for res in result:
        bdw: str = chain.invoke(inputs={'query': res['name']})
        bdw = bdw.replace('。', '').strip()
        node1 = Node('招标项目', **res)
        node2 = Node('公司', name=res['bid_company'])
        node3 = Node('公司', name=res['purchaser'])
        node4 = Node('标的物', bdw=bdw)
        relation1 = Relationship(node1, '中标公司', node2)
        relation2 = Relationship(node1, '招标公司', node3)
        re

# 写入图数据库