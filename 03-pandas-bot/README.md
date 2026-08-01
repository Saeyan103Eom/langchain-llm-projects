# 🐼 Pandas 데이터 분석 챗봇 (Pandas DataFrame Agent)

> LangChain **Agent** · Groq · Pandas · Matplotlib 를 활용한 자연어 데이터 분석 챗봇

CSV/데이터를 올리고 **자연어로 질문하면**, LLM 에이전트가 **직접 pandas 코드를 작성·실행해**
데이터를 분석하고, 필요하면 **차트까지 그려주는** 챗봇입니다.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![LangChain](https://img.shields.io/badge/LangChain-🦜_Agent-green)
![Groq](https://img.shields.io/badge/LLM-Groq_Llama3.3-orange)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458)
![Matplotlib](https://img.shields.io/badge/Chart-Matplotlib-11557c)

---

## 📖 프로젝트 소개

앞선 프로젝트가 "질문 → 답변"(체인), "문서 검색 → 답변"(RAG)이었다면,
이번 프로젝트는 한 단계 더 나아간 **Agent(에이전트)** 방식입니다.

- 사람이 분석 코드를 짜는 게 아니라, **LLM이 스스로 도구(Python 실행)를 선택해** 문제를 해결
- 예: "월별 매출 추이를 보여줘" → 에이전트가 `df.groupby(...)` + `plt.plot(...)` 코드를 **직접 생성·실행** → 답변 + 그래프 반환
- LangChain의 `create_pandas_dataframe_agent`를 활용해 **데이터 분석 자동화**를 구현

> 💡 **왜 Agent인가?**
> 단순 체인은 정해진 흐름만 따르지만, **에이전트는 질문에 따라 필요한 도구를 스스로 판단해 사용**합니다.
> 그래서 "평균을 구해줘", "상관관계를 그려줘"처럼 매번 다른 요청에도 유연하게 대응할 수 있습니다.

---

## 🎯 주요 기능

- 데이터 업로드 후 **자연어 질문으로 데이터 분석** (통계, 집계, 필터링 등)
- 질문에 따라 **에이전트가 pandas 코드를 자동 생성·실행**
- 시각화가 필요한 질문이면 **차트(Matplotlib/Seaborn) 자동 생성 및 표시**
- 에이전트의 **중간 추론 과정(생성한 코드)** 확인 가능 (`return_intermediate_steps`)

---

## 🛠 기술 스택

| 구분        | 사용 기술                                     | 역할                                 |
| ----------- | --------------------------------------------- | ------------------------------------ |
| LLM         | **Groq (Llama 3.3 70B)**                      | 자연어 이해 및 코드 생성             |
| 에이전트    | **LangChain `create_pandas_dataframe_agent`** | 도구 선택 · 코드 실행 오케스트레이션 |
| 도구        | **python_repl_ast**                           | 에이전트가 pandas 코드를 실제 실행   |
| 데이터 처리 | **Pandas**                                    | DataFrame 분석                       |
| 시각화      | **Matplotlib / Seaborn**                      | 차트 생성                            |
| 패키지 관리 | **Poetry**                                    | 의존성 · 가상환경 관리               |

---

## 🔗 동작 흐름

```
사용자 질문(자연어)
      │
      ▼
[ LangChain Agent ]  ── 질문 분석, 어떤 도구를 쓸지 스스로 판단
      │
      ▼
python_repl_ast  ── 에이전트가 pandas 코드를 생성해 실제 실행
      │
      ├──▶ 텍스트 답변 (분석 결과)
      └──▶ 차트 코드 감지 시 → 재실행하여 그래프 표시
```

---

## 🔍 핵심 구현

### 1) 에이전트 생성 및 실행

```python
agent_executor = create_pandas_dataframe_agent(
    llm, df,
    agent_type='tool-calling',
    verbose=True,
    return_intermediate_steps=True,   # 에이전트의 추론 과정 확보
    allow_dangerous_code=True,        # 생성된 코드 실행 허용 (아래 보안 노트 참고)
)
response = agent_executor.invoke(question)
```

### 2) 에이전트가 생성한 코드 추출 (직접 구현한 부분)

에이전트가 실행한 중간 단계(`intermediate_steps`)에서 **실제로 작성한 pandas 코드만 추출**하고,
그 코드가 **시각화 코드(plt/fig/plot/sns)** 인 경우에만 차트를 다시 그리도록 처리했습니다.

```python
# python_repl_ast 도구로 실행한 코드만 골라냄
for item in response['intermediate_steps']:
    if item[0].tool == 'python_repl_ast':
        intermediate_output.append(str(item[0].tool_input['query']))
python_code = "\n".join(intermediate_output)

# 차트 관련 코드일 때만 재실행해 그래프 표시
def execute_and_show_chart(python_code, df):
    local_vars = {"df": df.copy(), "plt": plt, "pd": pd}
    exec(python_code, globals(), local_vars)
```

---

## 🖼 실행 예시

**질문 → 텍스트 답변**

![질문과 답변](Users/ysyseom/langchain-llm-projects/03-pandas-bot/img/질문과 답변.png)

**자동 생성된 차트**

![생성된 차트](Users/ysyseom/langchain-llm-projects/03-pandas-bot/img/생성된 차트.png)

**에이전트의 추론 과정 (직접 생성한 pandas 코드)**

![에이전트 추론 로그 1](Users/ysyseom/langchain-llm-projects/03-pandas-bot/img/에이전트추론 1.png)
![에이전트 추론 로그 2](Users/ysyseom/langchain-llm-projects/03-pandas-bot/img/에이전트추론 2.png)

---

## 📚 배운 점 & 회고

- **체인(Chain)과 에이전트(Agent)의 차이**를 이해했다 — 에이전트는 도구를 스스로 선택해 실행한다.
- LLM이 생성한 코드를 실행하고, 그 **중간 결과물(코드)을 추출·재활용**하는 방법을 익혔다.
- `allow_dangerous_code`처럼 **편의성과 보안의 트레이드오프**를 고민하게 됐다.
- 프로젝트를 거치며 **단순 체인 → RAG → 에이전트**로 LLM 활용 수준을 단계적으로 확장했다.
- 다음 목표: 여러 파일/시트 동시 분석, 분석 결과 리포트 자동 생성, 코드 실행 격리(sandbox).

```

```
