🪙 암호화폐 투자 자문 봇 (Crypto Investment Advisor)

> **CrewAI 멀티 에이전트** · Groq · Tavily Search · Gradio 를 활용한 협업형 리서치 챗봇

여러 AI 에이전트가 **역할을 나눠 협업**하는 챗봇입니다.
**리서처(Researcher)** 가 웹을 검색해 최신 암호화폐 트렌드를 수집하고,
**애널리스트(Analyst)** 가 그 결과를 분석해 투자 인사이트 리포트를 작성합니다.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi_Agent-red)
![Groq](https://img.shields.io/badge/LLM-Groq_Llama3.3-orange)
![Tavily](https://img.shields.io/badge/Search-Tavily-4285F4)
![Gradio](https://img.shields.io/badge/UI-Gradio-yellow)

---

## 📖 프로젝트 소개

앞선 프로젝트가 하나의 체인/에이전트로 동작했다면, 이번 프로젝트는 **여러 에이전트가 협업**하는
**멀티 에이전트(Multi-Agent)** 시스템입니다. 사람이 팀을 이뤄 일하듯, 각 에이전트가 **전문 역할**을
맡아 순차적으로 작업을 넘겨받아 하나의 결과물을 만듭니다.

- **Researcher** → Tavily 검색 도구로 실시간 웹에서 트렌드·기회를 조사
- **Analyst** → 리서처의 결과를 넘겨받아 분석하고 투자 리포트로 정리
- CrewAI의 **Sequential Process**로 리서치 → 분석을 순서대로 연결
  > 💡 **왜 멀티 에이전트인가?**
  > 하나의 에이전트에 모든 걸 시키는 대신, **역할을 분리**하면 각자 자기 일에 집중해
  > 결과 품질과 구조가 좋아집니다. 실제 팀의 분업 방식을 LLM에 적용한 구조입니다.

---

## 🎯 주요 기능

- 관심 주제(topic) 입력 시 **웹 실시간 검색 기반 리서치** 자동 수행
- 리서치 결과를 **분석해 투자 인사이트 리포트** 생성
- 두 에이전트가 **순차 협업**(Researcher → Analyst)하는 CrewAI 워크플로우
- Gradio 챗 인터페이스로 간편하게 사용

---

## 🛠 기술 스택

| 구분          | 사용 기술                  | 역할                                |
| ------------- | -------------------------- | ----------------------------------- |
| 멀티 에이전트 | **CrewAI**                 | 에이전트·태스크·크루 오케스트레이션 |
| LLM           | **Groq (Llama 3.3 70B)**   | 각 에이전트의 추론 엔진             |
| 검색 도구     | **Tavily Search**          | 실시간 웹 리서치                    |
| UI            | **Gradio (ChatInterface)** | 웹 챗봇 인터페이스                  |
| 패키지 관리   | **Poetry**                 | 의존성 · 가상환경 관리              |

---

## 🔗 동작 흐름 (Crew Workflow)

```
사용자 주제 입력 (topic)
        │
        ▼
┌─────────────────────┐   Tavily 웹 검색
│  Agent 1: Researcher │ ──────────────▶ 최신 트렌드 · 투자 기회 수집
└─────────────────────┘
        │  (research 결과 전달, Sequential)
        ▼
┌─────────────────────┐
│  Agent 2: Analyst    │ ──────────────▶ 분석 및 투자 인사이트 리포트 작성
└─────────────────────┘
        │
        ▼
   최종 투자 리포트
```

---

## 🔍 핵심 구현

### 에이전트 구성 (역할 분리)

```python
# Agent 1: 웹 검색으로 트렌드 조사
researcher = Agent(
    role='Market Researcher',
    goal='Uncover emerging trends and investment opportunities ... Focus on the topic:{topic}',
    tools=[search_tool],        # Tavily 검색 도구 장착
    llm=llm, max_iter=3, max_rpm=10,
)

# Agent 2: 조사 결과 분석
analyst = Agent(
    role='Investment Analyst',
    goal='Analyze cryptocurrency market data to extract actionable insights ...',
    llm=llm,
)
```

### 크루(Crew) 구성 및 실행

```python
crypto_crew = Crew(
    agents=[researcher, analyst],
    tasks=[research_task, analyst_task],
    process=Process.sequential,   # 리서치 → 분석 순차 진행
    verbose=True,
)
result = crypto_crew.kickoff()
```

> 🌐 두 에이전트가 순차적으로 협업하며, Researcher의 검색 결과가 Analyst의 입력으로 전달됩니다.

---

## 🌏 Tip: 한글로 리포트 받기

최종 결과를 **한글로 받고 싶다면**, `analyst_task`의 `description`에 아래 문구를 추가하세요.

```python
analyst_task = Task(
    description=(
        'Analyze the provided cryptocurrency market data to extract key insights '
        'and compile a concise report. Focus on the topic:{topic}. '
        "Write the console report in 'Korean'."   # 👈 이 문장 추가
    ),
    expected_output='A refined finalized investment report with actionable insights',
    agent=analyst,
)
```

`Write the console report in 'Korean'` 처럼 **출력 언어를 명시**하면 최종 리포트가 한글로 생성됩니다.

---

## 📚 배운 점 & 회고

- **멀티 에이전트(CrewAI)** 로 역할을 분리해 협업시키는 구조를 이해했다.
- 에이전트에 **외부 검색 도구(Tavily)** 를 연결해 실시간 정보를 활용하는 법을 익혔다.
- `Process.sequential`로 **작업 흐름(리서치 → 분석)** 을 설계하는 경험을 했다.
- 프로젝트를 거치며 **체인 → RAG → 단일 에이전트 → 멀티 에이전트**로 LLM 활용을 단계적으로 확장했다.
- 다음 목표: 에이전트 간 병렬 처리, 리포트 검증 에이전트 추가, 결과 자동 저장.

---
