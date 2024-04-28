import os

from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.chat_models.openai import ChatOpenAI
from langchain_core.messages import ChatMessage

# 加载环境变量 - (.env 文件)-> os.getenv("DB_PASSWORD")
load_dotenv()
os.environ["OPENAI_API_KEY"] = "sess-zCpUTlF9HaMsmaERENhBmqwiVG2MplLfpLyt3gbs"
llm = ChatOpenAI(model_name='gpt-3.5-turbo-1106', temperature=0)
from langchain_openai import OpenAI, ChatOpenAI
from langchain.llms.base import LLM, BaseLLM
from langchain.chains.llm import LLMChain, ChatGeneration
from langchain.chains.conversation.base import
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import ChatBaichuan
response = llm._generate(messages=[ChatMessage(content='hello h a u', role='system')])
response = llm.invoke(messages=[ChatMessage(content='hello h a u', role='system')])
print(response)
OpenAI().invoke()

ResponseSchema(type='list', name='disease', description='疾病名称实体')
# 定义实体字段
# 类型：list, string, number
response_schemas = [
    ResponseSchema(type='list', name='disease', description='疾病名称实体'),
    ResponseSchema(type='list', name='symptom', description='疾病症状实体'),
    ResponseSchema(type='list', name='drug', description='药物名称实体'),
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
print(output_parser)
format_instructions = output_parser.get_format_instructions()
print(format_instructions)

template = '''
1、从以下用户输入的句子中，提取实体内容。
2、仅根据用户输入抽取，不要推理。
3、注意json格式，在json中不要出现//
4、如果字段内容为空，将字段值设为[]。

{format_instructions}

用户输入：{input}

输出：
'''

prompt = PromptTemplate(
    template=template,
    partial_variables={'format_instructions': format_instructions},
    input_variables=['input']
)

# prompt = prompt.format(input='感冒是一种什么病？')
print(prompt)
print(type(prompt))


chain = LLMChain(
    llm=llm,
    prompt=prompt
)

llm_output = chain.invoke({"input": '感冒是一种什么病？会导致咳嗽吗？'})
# llm_output = chain.run(input='感冒吃什么药好得快？可以吃阿莫西林吗？')

print(llm_output)

output = output_parser.parse(llm_output['text'])
print(output, type(output))