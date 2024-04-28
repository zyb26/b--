"""
对mysql数据库的数据进行分析:
1. 表ods_company_detail: 公司详情--> 主要包括 （公司名称；法人； 成立日期；地点；行业；经营范围）
2. 表ods_policy: 政策信息 --> 主要包括(法规正文； 标题； 发布时间； 实施时间)
3. 表ods_policy_regulation_files:政策文件流
4. 表ods_products:产品信息 --> 物资名称；产品参数；供应商名称； 报价； 联系人； 电话； 地址
5. 表ods_public_opinion:舆情信息
6. 表ods_tender:招投标信息 --> 项目名称; 中标通知书; 招标机构；招标预算；项目编号；类型（服务|学校|医院|工程|监理);
代理机构；中标机构；中标金额；中标日期； 分批的项目名称
"""
import json

import pandas as pd
# 表ods_tender: agency 代理机构； name 项目名称； purchaser 招标机构；bid_company:中标机构
import pymysql.cursors
from py2neo import Node, Graph, Relationship

connection = pymysql.connect(host='115.29.206.96',
                             user='root',       # 用户
                             password='7ZCIKVu0x',  # 密码.md
                             database='xunfei5',    # 数据的db
                             port=43306,
                             cursorclass=pymysql.cursors.DictCursor)
print(connection)

# 查询数据库的数据并保存为json
def select():
    name_list = []    # 项目名称列表
    agency_list = []    # 代理机构列表
    purchaser_list = []    # 招标机构列表
    bid_company_list = []   # 中标机构列表

    with connection:
        with connection.cursor() as cursor:  # 游标
            # 项目名称；招标机构；代理机构； 中标机构
            sql = "SELECT name, purchaser, agency, bid_company FROM ods_tender"
            cursor.execute(sql)
            with open(r"D:\neo4j_json\data.json", "w", encoding='utf-8') as file:
                for row in cursor.fetchall():
                    data = row
                    json_str = json.dumps(data)
                    file.write(json_str + "\n")

            print("查询结果已成功写入 JSON 文件")

# 读取json文件 --> CSV
def json2csv():
    data = []
    with open(r"D:\neo4j_json\data.json", "r", encoding="utf-8") as file:
        for line in file:
            json_obj = json.loads(line)
            data.append(json_obj)
    lis_name = []
    lis_purchaser = []
    lis_agency = []
    lis_bid_company = []
    for dic in data:
        lis_name.append(dic['name'])
        lis_purchaser.append(dic['purchaser'])
        lis_agency.append(dic['agency'])
        lis_bid_company.append(dic['bid_company'])

    Dic = {'name': lis_name,
           'purchaser': lis_purchaser,
           'agency': lis_agency,
           'bid_company': lis_bid_company
           }
    # 创建 DataFrame
    df = pd.DataFrame(Dic)

    # 将 DataFrame 写入 CSV 文件
    filename = r"D:\neo4j_json\data.csv"
    df.to_csv(filename, index=False, encoding='utf-8')

    print("数据已成功写入 CSV 文件:", filename)

# 读取csv 写入图数据库
def create():
    graph = Graph(profile="neo4j://localhost:7687", auth=("neo4j", 12345678), name="zyb")
    # 读取 CSV 文件并解析为 DataFrame，不使用第一行作为列名
    filename = r"D:\neo4j_json\data.csv"  # 替换为你的 CSV 文件路径
    df = pd.read_csv(filename, header=0)

    # 遍历 DataFrame 中的每一行数据
    for index, row in df.iterrows():
        print(row[0])   # 项目名称
        print(row[1])   # 招标机构
        print(row[2])   # 代理机构
        print(row[3])   # 中标机构
        node1 = Node('项目',  data=row[0])
        node2 = Node('招标机构', data=row[1])
        node3 = Node('代理机构', data=row[2])
        node4 = Node('中标机构', data=row[3])

        relation1 = Relationship(node2, '发布', node1)    # 招标机构 -发布-> 项目
        relation2 = Relationship(node2, '代理', node3)    # 招标机构 -代理-> 代理机构
        relation3 = Relationship(node3, '来源', node1)    # 代理机构 -来源->项目
        relation4 = Relationship(node4, '代理', node3)    # 中标机构 -代理-> 代理机构
        relation5 = Relationship(node4, '投标', node1)    # 中标机构 -投标->项目

        graph.create(node1)
        graph.create(node2)
        graph.create(node3)
        graph.create(node4)
        graph.create(relation1)
        graph.create(relation2)
        graph.create(relation3)
        graph.create(relation4)
        graph.create(relation5)



if __name__ == "__main__":
    # select()
    # json2csv()
    create()