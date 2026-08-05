#환경 변수에서 API 키 가져오기
import os
import importlib.metadata
from dotenv import load_dotenv
load_dotenv()

# CrewAI 라이브러리에서 필요한 클래스 가져오기
from crewai import Agent, Task, Crew, Process, LLM
import gradio as gr


GROQ_API_KEY=os.getenv('GROQ_API_KEY')
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


#LLM
llm = LLM(model="groq/llama-3.3-70b-versatile", temperature=0, api_key=GROQ_API_KEY)

# Search Tool
from crewai_tools import TavilySearchTool
search_tool = TavilySearchTool(api_key = TAVILY_API_KEY)

def run_crypto_crew(topic):
    
    
    # Agent 1: Researcher
    researcher = Agent(
        role='Market Researcher',
        goal='Uncover emerging trends and investment opportunities in the cryptocurrency market in 2026. Focus on the topic:{topic}',
        backstory ='You are a groundbreaking researcher who identifies innovative trends and actionable insights',
        verbose = True,
        tools = [search_tool],
        allow_delegation = False,
        llm = llm,
        max_iter =3,
        max_rpm = 10
    )

    # Agent 2: Analyst
    analyst = Agent(
        role='Investment Analyst',
        goal = 'Analyze cryptocurrency market data to extract actionable insights and investment leads. Focus on the topic:{topic}',
        backstory ='You are an expert analyst who draws meaningful conclusions from cryptocurrency market data.',
        verbose = True,
        allow_delegation = False,
        llm = llm)

    #Task

    research_task = Task(description='Explore the internet to pinpoint emerging trends and potential investment opportunities in cryptocurrency.',
                        expected_output='A detailed summary of the research results',
                        agent=researcher)
    analyst_task=Task(description='Analyze the provided cryptocurrency market data to extract key insights and compile a concise report. Focus on the topic:{topic}',
                    expected_output='A refined finalized investment report with actionable insights',
                    agent= analyst)

    #Crew 구성
    crypto_crew = Crew(agents=[researcher, analyst],
                    tasks= [research_task, analyst_task],
                    process = Process.sequential,
                    verbose=True)

    result = crypto_crew.kickoff()

    return result.raw

def process_query(message, history):
    return run_crypto_crew(message)



if __name__ == '__main__': 
    app = gr.ChatInterface(
        fn = process_query,
        title = 'Crypto Investment Advisor Bot',
        description='암호화폐 관련 트렌트를 파악하여 투자 인사이트를 제공해 드립니다.' 
)
    app.launch()
    
