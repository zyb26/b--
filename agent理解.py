import os

from langchain import hub
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "sess-zCpUTlF9HaMsmaERENhBmqwiVG2MplLfpLyt3gbs"
llm = ChatOpenAI(model_name='gpt-3.5-turbo-1106', temperature=0)

def query(query):
    tools = [
        Tool.from_function(
            name='generic_func',
            func=lambda x: 1,
            description='可以解答通用领域的知识，例如打招呼，问你是谁等问题',
        ),
        Tool.from_function(
            name='retrival_func',
            func=lambda x: 2,
            description='用于回答寻医问药网相关问题',
        ),
        Tool(
            name='graph_func',
            func=lambda x: 3,
            description='用于回答疾病、症状、药物等医疗相关问题',
        ),
        # Tool(
        #     name='search_func',
        #     func=self.search_func,
        #     description='其他工具没有正确答案时，通过搜索引擎，回答通用类问题',
        # ),
    ]
    os.environ["OPENAI_API_KEY"] = "sess-zCpUTlF9HaMsmaERENhBmqwiVG2MplLfpLyt3gbs"
    llm = ChatOpenAI(model_name='gpt-3.5-turbo-1106', temperature=0)
    prefix = """请用中文，尽你所能回答以下问题。您可以使用以下工具："""
    suffix = """Begin!

    History: {chat_history}
    Question: {input}
    Thought:{agent_scratchpad}"""

    agent_prompt = ZeroShotAgent.create_prompt(
        tools=tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=['input', 'agent_scratchpad', 'chat_history']
    )

    llm_chain = LLMChain(llm=llm, prompt=agent_prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain)

    memory = ConversationBufferMemory(memory_key='chat_history')
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent = agent,
        tools = tools,
        memory = memory,
        verbose = True
    )
    return agent_chain.run({'input': query})

    # prompt = hub.pull('hwchase17/react-chat')
    # prompt.template = '请用中文回答问题！Final Answer 必须尊重 Obversion 的结果，不能改变语义。\n\n' + prompt.template
    # agent = create_react_agent(llm=get_llm_model(), tools=tools, prompt=prompt)
    # memory = ConversationBufferMemory(memory_key='chat_history')
    # agent_executor = AgentExecutor.from_agent_and_tools(
    #     agent=agent,
    #     tools=tools,
    #     memory=memory,
    #     handle_parsing_errors=True,
    #     verbose=os.getenv('VERBOSE')
    # )
    # return agent_executor.invoke({"input": query})['output']

if __name__ == "__main__":
    query(query="你好")