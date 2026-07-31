# 📄 PDF RAG 챗봇 (PDF Question-Answering Chatbot)

> LangChain · Groq · Chroma · Gradio 를 활용한 RAG(검색 증강 생성) 챗봇

사용자가 업로드한 **PDF 문서의 내용을 근거로** 질문에 답하는 챗봇입니다.
문서를 벡터로 변환해 저장하고, 질문과 관련된 부분만 검색해서 LLM에게 전달하는
**RAG(Retrieval-Augmented Generation)** 파이프라인을 직접 구현했습니다.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![LangChain](https://img.shields.io/badge/LangChain-🦜-green)
![Groq](https://img.shields.io/badge/LLM-Groq_Llama3.3-orange)
![Chroma](https://img.shields.io/badge/VectorDB-Chroma-purple)
![Gradio](https://img.shields.io/badge/UI-Gradio-yellow)

---

## 📖 프로젝트 소개

LLM은 학습하지 않은 문서의 내용은 답할 수 없습니다. 이를 해결하기 위해,
**외부 문서(PDF)를 검색해 근거로 제공(RAG)** 하는 방식을 구현했습니다.

- PDF를 업로드하면 텍스트를 추출 → 잘게 나눔(chunk) → 벡터로 임베딩 → 벡터 DB에 저장
- 질문이 들어오면 관련 청크를 검색해 LLM에게 **"이 근거만 보고 답하라"** 고 지시
- 이를 통해 **환각(hallucination)을 줄이고 문서 기반의 정확한 답변** 생성

---

## 🎯 주요 기능

- PDF 업로드 → 문서 기반 질의응답
- Chunk 크기 / 중첩(overlap) / 유사도 메트릭 / Temperature를 **UI에서 실시간 조절** (하이퍼파라미터 실험 가능)
- 문서 없이 질문 시 안내 메시지 반환 (예외 방어 처리)

---

## 🛠 기술 스택

| 구분        | 사용 기술                          | 역할                     |
| ----------- | ---------------------------------- | ------------------------ |
| LLM         | **Groq (Llama 3.3 70B)**           | 답변 생성                |
| 프레임워크  | **LangChain**                      | RAG 체인 구성            |
| 문서 로더   | **PyPDFLoader**                    | PDF 텍스트 추출          |
| 텍스트 분할 | **RecursiveCharacterTextSplitter** | 문서를 청크로 분할       |
| 임베딩      | **HuggingFace (all-MiniLM-L6-v2)** | 텍스트 → 벡터 변환       |
| 벡터 DB     | **Chroma**                         | 벡터 저장 및 유사도 검색 |
| UI          | **Gradio (ChatInterface)**         | 웹 챗봇 인터페이스       |
| 패키지 관리 | **Poetry**                         | 의존성 · 가상환경 관리   |

---

## 🔗 RAG 파이프라인 흐름

```
                          [ 문서 준비 단계 ]
  PDF 업로드 ─▶ PyPDFLoader ─▶ TextSplitter ─▶ Embedding ─▶ Chroma(벡터 DB)
              (텍스트 추출)   (청크 분할)     (벡터화)      (저장)

                          [ 질의응답 단계 ]
  질문 입력 ─▶ Retriever(관련 청크 검색) ─▶ Prompt(근거 주입) ─▶ LLM(Groq) ─▶ 답변
```

핵심 코드:

```python
# 1) PDF → 벡터 저장소
loader = PyPDFLoader(pdf_file)
splits = RecursiveCharacterTextSplitter(chunk_size, chunk_overlap).split_documents(loader.load())
vectorstore = Chroma.from_documents(splits, embedding=HuggingFaceEmbeddings("all-MiniLM-L6-v2"))

# 2) 검색 + 답변 생성 (RAG 체인)
retriever = vectorstore.as_retriever()
document_chain = create_stuff_documents_chain(model, prompt)   # 검색된 문서를 프롬프트에 결합
rag_chain = create_retrieval_chain(retriever, document_chain)  # 검색 → 생성 연결
answer = rag_chain.invoke({"input": message})["answer"]
```

> 프롬프트에 `"Answer the question based only on the following context"` 라고 명시해
> LLM이 **자기 지식이 아닌 문서 내용에만 근거해** 답하도록 제한했습니다.

---

## 🔬 검색 방식 비교 실험 (Similarity vs MMR)

RAG의 답변 품질은 **어떤 청크를 검색해 오느냐**에 크게 좌우됩니다.
기본 유사도 검색과 MMR 검색을 비교 실험했습니다. (`mmr_test.ipynb`)

| 구분     | 유사도 검색 (similarity)          | MMR 검색                       |
| -------- | --------------------------------- | ------------------------------ |
| 방식     | 질문과 가장 유사한 청크 선택      | 관련성 **+ 다양성** 함께 고려  |
| 파라미터 | `k=3`                             | `k=3`, `fetch_k=10`            |
| 특징     | 비슷한 내용이 중복 검색될 수 있음 | 중복을 줄이고 다양한 관점 포함 |

```python
# 유사도 검색
similarity_retriever = db.as_retriever(search_type='similarity', search_kwargs={'k': 3})

# MMR 검색: 후보 10개(fetch_k) 중 관련성·다양성을 고려해 3개(k) 선택
mmr_retriever = db.as_retriever(search_type='mmr', search_kwargs={'k': 3, 'fetch_k': 10})
```

**실험 결과 및 인사이트**

- 유사도 검색은 질문과 가까운 청크를 뽑지만 **내용이 겹치는 청크**가 함께 검색되는 경향이 있음
- MMR은 후보(`fetch_k=10`)에서 서로 겹치지 않는 청크를 골라 **검색 결과의 다양성을 보완**
- 다만 MMR이 항상 우월한 것은 아니며, 좁은 사실 하나를 묻는 질문엔 유사도 검색이, 넓은 맥락이 필요한 질문엔 MMR이 유리한 **트레이드오프**가 존재
- → retriever의 `search_type`이 RAG 답변 품질에 영향을 준다는 것을 확인

---

## 🐞 Troubleshooting: gradio_pdf 호환성 이슈

PDF 미리보기용으로 `gradio_pdf` 컴포넌트를 사용하려 했으나, **Gradio 6.x 호환성 버그**로
컴포넌트가 로딩되지 않는 문제가 있었습니다. (자세한 원인·해결 과정은 이슈 참고)

- **원인**: Gradio 6부터 내부 Svelte 구조 변경 → 서드파티 커스텀 컴포넌트 미대응
- **해결**: 코어 내장 컴포넌트 `gr.File`로 교체 (PDF 미리보기만 제외되고 업로드 기능은 동일)
- **추가**: PDF 미업로드 상태에서 질문 시 `PyPDFLoader(None)`로 터지던 문제에 **None 방어 로직** 추가

```python
# None 방어 로직: 파일 없이 질문하면 에러 대신 안내 메시지
if pdf_file is None:
    return "먼저 PDF 파일을 업로드한 뒤 질문해주세요."
```

> 📌 상세 내용: [Issue #1 — gradio_pdf 호환성 이슈]

---

## 📚 배운 점 & 회고

- LLM의 한계(미학습 문서 응답 불가)를 **RAG로 보완**하는 전체 흐름을 구현했다.
- 문서 로딩 → 분할 → 임베딩 → 벡터 검색 → 생성으로 이어지는 **RAG 파이프라인 구조**를 이해했다.
- **retriever 검색 방식(유사도 vs MMR)** 에 따라 검색 결과가 달라짐을 실험으로 확인했다.
- 라이브러리 **버전 호환성 문제**를 만나 원인을 분석하고, 대체 컴포넌트로 해결했다. (Issue #1)

```

```
