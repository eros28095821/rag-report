from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
import chainlit as cl

# 用來保存對話歷史
conversation_history = []

# 上下文摘要函數
def summarize_context(context):
    """
    簡單模擬一個上下文摘要功能。可以替換為自動化摘要模型或自定義邏輯。
    """
    MAX_HISTORY = 10
    if len(context) > MAX_HISTORY * 2:
        # 模擬摘要 (可以替換為更智能的摘要邏輯)
        summary = "之前的對話摘要：用戶與助手就一般性問題進行了互動。"
        # 返回摘要 + 最近對話
        return [summary] + context[-MAX_HISTORY * 2:]
    return context

@cl.on_chat_start
async def on_chat_start():
    model = Ollama(model="kenneth85/llama-3-taiwan:8b-instruct")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """你是一個中華民國的民法專長的律師，你要根據中華民國民法正確引用民法法條，並且要正確引用中華民國民法內容。
                   你善於透過提問獲得需要資訊，並會引導人從現有的線索找到重點。
                   你能夠撰寫交通事故的民事起訴狀，並且只針對慰撫金部分的案件作撰寫。慰撫金基本上只會用到民法的內容，你思考一下再使用正確的民法法條"""
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

@cl.on_message
async def on_message(message: cl.Message):
    global conversation_history

    # 如果用戶請求清除記憶
    if message.content.strip().lower() in ["清除記憶", "reset"]:
        conversation_history = []
        await cl.Message(content="記憶已清除！").send()
        return

    try:
        # 將當前用戶消息添加到歷史中
        conversation_history.append(f"用戶: {message.content}")

        # 簡化對話歷史以節省 Token
        summarized_history = summarize_context(conversation_history)
        full_context = "\n".join(summarized_history)

        # 從上下文生成最終的提示語
        prompt = f"""你是一個中華民國的民法專長的律師，你要根據中華民國民法正確引用民法法條，並且要正確引用中華民國民法內容。
                   你善於透過提問獲得需要資訊，並會引導人從現有的線索找到重點。
                   你能夠撰寫交通事故的民事起訴狀，並且只針對慰撫金部分的案件作撰寫。慰撫金基本上只會用到民法的內容，你思考一下再使用正確的民法法條。\n{full_context}\n請對輸入內容進行回應：{message.content}""" 
        model = Ollama(model="kenneth85/llama-3-taiwan:8b-instruct")
        prompt_template = ChatPromptTemplate.from_messages([("human", prompt)])
        runnable = prompt_template | model | StrOutputParser()

        msg = cl.Message(content="")

        # 使用流模式發送請求
        async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            await msg.stream_token(chunk)

        # 將模型回應發送給用戶
        await msg.send()

        # 將模型回應添加到歷史中
        conversation_history.append(f"助手: {msg.content}")

    except Exception as e:
        # 捕獲錯誤並通知用戶
        await cl.Message(content=f"發生錯誤：{str(e)}").send()   