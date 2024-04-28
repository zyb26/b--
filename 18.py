import os

from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

load_dotenv()
# TODO:
os.environ["OPENAI_API_KEY"] = ""
llm = ChatOpenAI(model_name='gpt-3.5-turbo-1106', temperature=0)

def structured_output_parser(response_schemas):
    text = '''
    请从以下文本中，抽取出实体信息，并按json格式返回，json包含首尾的 "```json" 和 "```"。
    以下是字段含义和类型，要求保留所有字段：\n
    '''
    for schema in response_schemas:
        text += schema.name + ' 字段，表示：' + schema.description + '，类型为：' + schema.type + '\n'
    return text

response_schemas = [
    ResponseSchema(type='list', name='disease', description='疾病名称实体'),
    ResponseSchema(type='list', name='symptom', description='疾病症状实体'),
    ResponseSchema(type='list', name='drug', description='药物名称实体'),
]

format_instructions = structured_output_parser(response_schemas)
print(format_instructions)

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

template = '''
1、从以下用户输入的句子中，提取实体内容。
2、注意：根据用户输入的事实抽取内容，不要推理，不要补充信息。

{format_instructions}
------------
用户输入：{input}
------------
输出：
'''

prompt = PromptTemplate(
    template=template,
    partial_variables={'format_instructions': format_instructions},
    input_variables=['input']
)

# prompt = prompt.format(input='感冒是一种什么病？会导致咳嗽吗？')
# print(prompt)

from langchain.chains import LLMChain

chain = LLMChain(
    llm = llm,
    prompt = prompt
)

# llm_output = chain.run(input='感冒是一种什么病？会导致咳嗽吗？')
llm_output = chain.run(input='感冒吃什么药好得快？可以吃阿莫西林吗？')
print(llm_output)

output = output_parser.parse(llm_output)
print(output, type(output))