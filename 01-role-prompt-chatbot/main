import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


prompt = ChatPromptTemplate.from_messages(
    [("system", "당신은 천문학 전문가입니다."),
     ("user", "{input}")]
    )


llm = ChatGroq(api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")


output_parser = StrOutputParser()


chain = prompt | llm | output_parser
# user_input = input("질문을 입력하시오 : ")
# response = chain.invoke({"input" : user_input})
# print("ChatBot:" , response)

import gradio as gr

def chat(user_input):
    return chain.invoke({"input": user_input})

demo = gr.Interface(fn=chat, inputs="text", outputs="text")
demo.launch()   