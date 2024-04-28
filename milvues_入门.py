'''
1. 下载docker
2. 容器内安装milvus(都是在容器外操作的 powershell中/linux终端)
wget https://github.com/milvus-io/milvus/releases/download/v2.2.13/milvus-standalone-docker-compose.yml -O docker-compose.yml
sudo docker-compose up -d  # 启动容器
sudo docker-compose ps
3. Milvus可视化工具Attu (容器间的通讯)
docker run -p 8000:3000  -e MILVUS_URL={your machine IP}:19530 zilliz/attu:v2.2.6
4. your machine IP: 就是cmd 然后 ipconfig/all 中的 IPv4 地址 . . . . . . . . . . . . :
'''

from pymilvus import connections
# 连接到Milvus服务器
conn = connections.connect("default", host="172.25.208.1", port="19530")

# 删除已存在的数据库
def delete_collection():
    utility.drop_collection("word2vec")

# 创建索引
from pymilvus import utility
def create_index():
    index_params = {
        "metric_type": "IP",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    collection = Collection("word2vec")
    collection.create_index(
        field_name="embeding",
        index_params=index_params
    )
    utility.index_building_progress("word2vec")

# 创建collection(向量数据库中添加表格结构)
from pymilvus import CollectionSchema, FieldSchema, DataType
from pymilvus import Collection

def collection_create():
    m_id = FieldSchema(name="m_id", dtype=DataType.INT64, is_primary=True, )
    embeding = FieldSchema(name="embeding", dtype=DataType.FLOAT_VECTOR, dim=768, )
    count = FieldSchema(name="count", dtype=DataType.INT64, )
    desc = FieldSchema(name="desc", dtype=DataType.VARCHAR, max_length=256, )
    schema = CollectionSchema(
        fields=[m_id, embeding, desc, count],
        description="Test embeding search",
        enable_dynamic_field=True
    )
    collection_name = "word2vec"
    collection = Collection(name=collection_name, schema=schema, using='default', kwargs={"consistency_level": 'Strong'})

# 插入数据
import numpy as np
def insert():
    coll_name = 'word2vec'
    mids, embedings, counts, descs = [], [], [], []
    data_num = 100
    for idx in range(0, data_num):
        mids.append(idx)
        embedings.append(np.random.normal(0, 0.1, 768).tolist())
        descs.append(f'random num {idx}')
        counts.append(idx)

    collection = Collection(coll_name)
    mr = collection.insert([mids, embedings, descs, counts])
    print(mr)

# 检索数据
from pymilvus import Collection
def search():
    coll_name = 'word2vec'
    collection = Collection(coll_name)
    search_params = {
        "metric_type": 'IP',
        "offset": 0,
        "ignore_growing": False,
        "params": {"nprobe": 16}
    }

    collection.load()

    results = collection.search(
        data=[np.random.normal(0, 0.1, 768).tolist()],
        anns_field="embeding",
        param=search_params,
        limit=16,
        expr=None,
        # output_fields=['m_id', 'embeding', 'desc', 'count'],
        output_fields=['m_id', 'desc', 'count'],
        **{"consistency_level": "Strong"}
    )
    collection.release()
    print(results[0].ids)
    print(results[0].distances)
    hit = results[0][0]
    print(hit.entity.get('desc'))
    print(results)

if __name__ == "__main__":
    # delete_collection()
    # collection_create()
    create_index()
    # insert()  # 插入数据
    # search()
