# 1、实体识别提示词
import os

from langchain.chains.llm import LLMChain
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

NER_PROMPT_TPL = '''
1、从以下用户输入的句子中，提取实体内容。
2、注意：根据用户输入的事实抽取内容，不要推理，不要补充信息。

{format_instructions}
------------
用户输入：{input}
------------
输出：
'''

# 2. json输出格式化函数
def structured_output_parser(response_schemas):
    text = '''
    请从以下文本中，抽取出实体信息，并按json格式返回，json包含首尾的 "```json" 和 "```"。
    以下是字段含义和类型，要求保留所有字段：\n
    '''
    for schema in response_schemas:
        text += schema.name + ' 字段，表示：' + schema.description + '，类型为：' + schema.type + '\n'
    return text

def replace_token_in_string(string, slots):
    for key, value in slots:
        string = string.replace('%'+key+'%', value)
    return string

# 3. 命名实体识别
def graph_func(query: str):
    response_schemas = [
        ResponseSchema(type='list', name='disease', description='疾病名称实体'),
        ResponseSchema(type='list', name='symptom', description='疾病症状实体'),
        ResponseSchema(type='list', name='drug', description='药物名称实体'),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = structured_output_parser(response_schemas)

    ner_prompt = PromptTemplate(
        template=NER_PROMPT_TPL,
        partial_variables={'format_instructions': format_instructions},
        input_variables=['query']
    )

    # prompt = ner_prompt.format(input='感冒是一种什么病？会导致咳嗽吗？')
    # print(prompt)

    os.environ["OPENAI_API_KEY"] = ""
    llm = ChatOpenAI(model_name='gpt-3.5-turbo-1106', temperature=0)

    ner_chain = LLMChain(
        llm=llm,
        prompt=ner_prompt
    )

    llm_output = ner_chain.run(input=query)

    ner_result = output_parser.parse(llm_output)
    # return output

    GRAPH_TEMPLATE = {
        'desc': {
            'slots': ['disease'],
            'question': '什么叫%disease%? / %disease%是一种什么病？',
            'cypher': "MATCH (n:Disease) WHERE n.name='%disease%' RETURN n.desc AS RES",
            'answer': '【%disease%】的定义：%RES%',
        },
        'cause': {
            'slots': ['disease'],
            'question': '%disease%一般是由什么引起的？/ 什么会导致%disease%？',
            'cypher': "MATCH (n:Disease) WHERE n.name='%disease%' RETURN n.cause AS RES",
            'answer': '【%disease%】的病因：%RES%',
        },
        'disease_symptom': {
            'slots': ['disease'],
            'question': '%disease%会有哪些症状？/ %disease%有哪些临床表现？',
            'cypher': "MATCH (n:Disease)-[:DISEASE_SYMPTOM]->(m) WHERE n.name='%disease%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + '、' + x), 1) AS RES",
            'answer': '【%disease%】的症状：%RES%',
        },
        'symptom': {
            'slots': ['symptom'],
            'question': '%symptom%可能是得了什么病？',
            'cypher': "MATCH (n)-[:DISEASE_SYMPTOM]->(m:Symptom) WHERE m.name='%symptom%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(n.name) | s + '、' + x), 1) AS RES",
            'answer': '可能出现【%symptom%】症状的疾病：%RES%',
        },
        'cure_way': {
            'slots': ['disease'],
            'question': '%disease%吃什么药好得快？/ %disease%怎么治？',
            'cypher': '''
                MATCH (n:Disease)-[:DISEASE_CUREWAY]->(m1),
                    (n:Disease)-[:DISEASE_DRUG]->(m2),
                    (n:Disease)-[:DISEASE_DO_EAT]->(m3)
                WHERE n.name = '%disease%'
                WITH COLLECT(DISTINCT m1.name) AS m1Names, 
                    COLLECT(DISTINCT m2.name) AS m2Names,
                    COLLECT(DISTINCT m3.name) AS m3Names
                RETURN SUBSTRING(REDUCE(s = '', x IN m1Names | s + '、' + x), 1) AS RES1,
                    SUBSTRING(REDUCE(s = '', x IN m2Names | s + '、' + x), 1) AS RES2,
                    SUBSTRING(REDUCE(s = '', x IN m3Names | s + '、' + x), 1) AS RES3
                ''',
            'answer': '【%disease%】的治疗方法：%RES1%。\n可用药物：%RES2%。\n推荐食物：%RES3%',
        },
        'cure_department': {
            'slots': ['disease'],
            'question': '得了%disease%去医院挂什么科室的号？',
            'cypher': "MATCH (n:Disease)-[:DISEASE_DEPARTMENT]->(m) WHERE n.name='%disease%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + '、' + x), 1) AS RES",
            'answer': '【%disease%】的就诊科室：%RES%',
        },
        'prevent': {
            'slots': ['disease'],
            'question': '%disease%要怎么预防？',
            'cypher': "MATCH (n:Disease) WHERE n.name='%disease%' RETURN n.prevent AS RES",
            'answer': '【%disease%】的预防方法：%RES%',
        },
        'not_eat': {
            'slots': ['disease'],
            'question': '%disease%换着有什么禁忌？/ %disease%不能吃什么？',
            'cypher': "MATCH (n:Disease)-[:DISEASE_NOT_EAT]->(m) WHERE n.name='%disease%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + '、' + x), 1) AS RES",
            'answer': '【%disease%】的患者不能吃的食物：%RES%',
        },
        'check': {
            'slots': ['disease'],
            'question': '%disease%要做哪些检查？',
            'cypher': "MATCH (n:Disease)-[:DISEASE_CHECK]->(m) WHERE n.name='%disease%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + '、' + x), 1) AS RES",
            'answer': '【%disease%】的检查项目：%RES%',
        },
        'cured_prob': {
            'slots': ['disease'],
            'question': '%disease%能治好吗？/ %disease%治好的几率有多大？',
            'cypher': "MATCH (n:Disease) WHERE n.name='%disease%' RETURN n.cured_prob AS RES",
            'answer': '【%disease%】的治愈率：%RES%',
        },
        'acompany': {
            'slots': ['disease'],
            'question': '%disease%的并发症有哪些？',
            'cypher': "MATCH (n:Disease)-[:DISEASE_ACOMPANY]->(m) WHERE n.name='%disease%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + '、' + x), 1) AS RES",
            'answer': '【%disease%】的并发症：%RES%',
        },
        'indications': {
            'slots': ['drug'],
            'question': '%drug%能治那些病？',
            'cypher': "MATCH (n:Disease)-[:DISEASE_DRUG]->(m:Drug) WHERE m.name='%drug%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(n.name) | s + '、' + x), 1) AS RES",
            'answer': '【%drug%】能治疗的疾病有：%RES%',
        },
    }

    graph_templates = []
    for key, template in GRAPH_TEMPLATE.items():
        slot = template['slots'][0]
        slot_values = ner_result[slot]
        for value in slot_values:
            graph_templates.append({
                'question': replace_token_in_string(template['question'], [[slot, value]]),
                'cypher': replace_token_in_string(template['cypher'], [[slot, value]]),
                'answer': replace_token_in_string(template['answer'], [[slot, value]]),
            })
    if not graph_templates:
        return

    # 计算问题相似度，筛选最相关问题
    graph_documents = [
        Document(page_content=template['question'], metadata=template)
        for template in graph_templates
    ]
    db = FAISS.from_documents(graph_documents, get_embeddings_model())
    graph_documents_filter = db.similarity_search_with_relevance_scores(query, k=3)
    # print(graph_documents_filter)

    # 执行CQL，拿到结果
    query_result = []
    neo4j_conn = get_neo4j_conn()
    for document in graph_documents_filter:
        question = document[0].page_content
        cypher = document[0].metadata['cypher']
        answer = document[0].metadata['answer']
        try:
            result = neo4j_conn.run(cypher).data()
            if result and any(value for value in result[0].values()):
                answer_str = replace_token_in_string(answer, list(result[0].items()))
                query_result.append(f'问题：{question}\n答案：{answer_str}')
        except:
            pass
    # print(query_result)

    GRAPH_PROMPT_TPL = '''
    请根据以下检索结果，回答用户问题，不要发散和联想内容。
    检索结果中没有相关信息时，回复“不知道”。
    ----------
    检索结果：
    {query_result}
    ----------
    用户问题：{query}
    '''

    # 总结答案
    prompt = PromptTemplate.from_template(GRAPH_PROMPT_TPL)
    graph_chain = LLMChain(
        llm=get_llm_model(),
        prompt=prompt,
        verbose=os.getenv('VERBOSE')
    )
    inputs = {
        'query': query,
        'query_result': '\n\n'.join(query_result) if len(query_result) else '没有查到'
    }
    return graph_chain.invoke(inputs)['text']
