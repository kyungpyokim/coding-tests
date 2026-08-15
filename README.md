# AI & LangGraph TDD Playground 🧪🤖

현대적인 Python AI 엔지니어링 생태계(`uv`, `ruff`, `pytest`, `langchain 1.0+`, `langgraph`, `pydantic v2`)를 기반으로, **TDD(테스트 주도 개발)** 방식으로 AI 에이전트와 워크플로우를 구현하며 코딩 감각을 회복할 수 있는 12단계 마스터 실습 프로젝트입니다.

---

## 🛠️ 기술 스택 및 개발 도구

| 도구 / 라이브러리 | 버전 / 역할 | 주요 명령어 및 용도 |
|---|---|---|
| **uv** | 0.12+ (초고속 패키지 관리 & 가상환경) | `uv sync`, `uv run python` |
| **ruff** | Linter & Formatter | `uv run ruff check .`, `uv run ruff format .` |
| **pytest** | 테스트 프레임워크 & 비동기/모킹 지원 | `uv run pytest`, `uv run pytest -k "test_name"` |
| **pytest-watcher** | 파일 저장 시 테스트 자동 재실행 (Watch 모드) | `./scripts/test_watch.sh` 또는 `uv run pytest-watcher .` |
| **pytest-cov** | 코드 커버리지 리포트 | `uv run pytest --cov=ai_practice` |
| **langchain** | 1.0+ (표준 LLM 메시지 및 인터페이스) | `langchain_core.messages`, `FakeListChatModel` |
| **langgraph** | 0.2+ / 1.0+ (AI 상태 그래프 오케스트레이션) | `StateGraph`, `MemorySaver`, `interrupt` |
| **pydantic** | v2.7+ (엄격한 데이터 모델링 & 유효성 검증) | `BaseModel`, `Field`, `model_validate` |

---

## 🚀 빠른 시작 (Quick Start)

### 1. 가상환경 동기화
```bash
uv sync
```

### 2. TDD 실시간 자동 테스트 (Watch 모드) 🔥
터미널 창 하나에 띄워두면, `src/`나 `tests/` 코드를 수정하고 저장할 때마다 즉시 테스트가 재실행됩니다:
```bash
./scripts/test_watch.sh

# 특정 레벨 테스트만 집중 Watch 하려면:
./scripts/test_watch.sh tests/test_level2/
```

### 3. 전체 테스트 1회 실행
```bash
uv run pytest
```

### 4. 코드 린트 & 포맷팅 점검
```bash
uv run ruff check .
uv run ruff format .
```

---

## 🧭 TDD 기반 AI 개발 사이클 (Red → Green → Refactor)

```
        ┌────────────────────────────────────────┐
        │               1. RED                   │
        │  실패하는 테스트 작성 (명세 & 예외 정의)      │
        └──────────────────┬─────────────────────┘
                           │
                           ▼
        ┌────────────────────────────────────────┐
        │              2. GREEN                  │
        │  테스트를 통과시키는 최소한의 로직 구현      │
        └──────────────────┬─────────────────────┘
                           │
                           ▼
        ┌────────────────────────────────────────┐
        │             3. REFACTOR                │
        │  타입 힌트, 중복 제거, 클린 코드 개선       │
        └────────────────────────────────────────┘
```

> 💡 **Deterministic TDD**: 모든 테스트는 유료 외부 LLM API 호출 없이 가짜 도구 및 Mock LLM을 통해 **100% 빠르고 결정론적(deterministic)** 으로 실행되므로, 네트워크 비용이나 지연 없이 안전하게 TDD 사이클을 반복할 수 있습니다.

---

## 📚 단계별 TDD AI 코딩 실습 로드맵 (Level 1 ~ 12)

### 📍 Phase 1: 기초 & 데이터 파이프라인
- **Level 1: Basics & Schema Engine** (`src/ai_practice/level1_basics/`)
  - `StructuredParser`: 마크다운 코드블록/텍스트에서 JSON 추출 및 Pydantic v2 안전 검증.
  - `ToolDispatcher`: 함수 $\rightarrow$ OpenAI 호환 JSON Schema 자동 추출 및 안전 실행.
- **Level 2: State Compression & Resilience** (`src/ai_practice/level2_state/`)
  - `HistoryTrimmer`: `SystemMessage` 보존 기반 토큰 버짓 슬라이딩 윈도우 트리밍.
  - `RetryPolicy`: 특정 예외 발생 시 지수 백오프(Exponential Backoff) 재시도 데코레이터.
- **Level 3: Graph Foundations & Reducers** (`src/ai_practice/level3_graphs/`)
  - `BasicGraph`: LangGraph `StateGraph`, `START`/`END` 엣지, `add_messages` 리듀서.

### 📍 Phase 2: 자율 에이전트 & 다중 협업
- **Level 4: Autonomous ReAct & Human-in-the-Loop** (`src/ai_practice/level4_agents/`)
  - `ReActAgent`: 도구 실행 루프, `MemorySaver` 세션 영속화, `interrupt` 사용자 승인 워크플로우.
- **Level 5: Multi-Agent Systems & Supervisor** (`src/ai_practice/level5_multi_agent/`)
  - `Supervisor`: 감독관 LLM이 전문 서브 에이전트(리서처, 코더)로 작업을 동적 위임 및 취합.
- **Level 6: RAG Engine & Hybrid Retrieval** (`src/ai_practice/level6_rag/`)
  - `HybridRAG`: 재귀적 청킹, 인메모리 벡터 저장소, Dense + Sparse(BM25) RRF 순위 융합.

### 📍 Phase 3: 비용 절감 & 지능형 계획
- **Level 7: Semantic Caching & Token Optimization** (`src/ai_practice/level7_caching/`)
  - `SemanticCache`: 임베딩 코사인 유사도 기반 LLM 응답 캐시 및 TTL 만료 정책.
- **Level 8: Plan-and-Solve / Hierarchical Task Decomposition** (`src/ai_practice/level8_planner/`)
  - `PlanAndExecute`: 목표 단계 분해(Planner) $\rightarrow$ 순차 실행 $\rightarrow$ 진행도 기반 재계획(Replanner).
- **Level 9: Real-time Streaming & Event Architecture** (`src/ai_practice/level9_streaming/`)
  - `StreamParser`: 토큰 스트리밍 처리, 분할된 툴 콜 청크 조립, 이벤트 파서.

### 📍 Phase 4: 엔터프라이즈 보안 & 자가 치유
- **Level 10: AI Guardrails & Injection Defense** (`src/ai_practice/level10_guardrails/`)
  - `Guardrails`: 개인정보(PII) 마스킹, 프롬프트 인젝션 탐지 및 차단 노드.
- **Level 11: Self-Healing Evaluator-Optimizer** (`src/ai_practice/level11_evaluator_optimizer/`)
  - `SelfHealingCode`: Generator $\rightarrow$ Evaluator(AST/실행 검증) $\rightarrow$ 피드백 자가 교정 루프.
- **Level 12: Distributed State & Time-Travel Debugging** (`src/ai_practice/level12_distributed_state/`)
  - `TimeTravel`: 상태 스냅샷 히스토리 추적, 과거 시점 롤백 및 상태 분기(Forking).

---

## 📁 디렉토리 구조

```text
coding-skills/
├── pyproject.toml              # uv 의존성 및 ruff/pytest/pytest-watcher 설정
├── README.md                   # 실습 가이드
├── correct-answer/             # Level 1 ~ 12 정답 코드 모음
├── scripts/
│   └── test_watch.sh           # TDD 실시간 Watch 테스트 스크립트
├── src/
│   └── ai_practice/
│       ├── core/               # 공통 데이터 모델 (ToolCall, ToolResult, LLMMessage)
│       ├── level1_basics/      # Level 1 실습 템플릿
│       ├── level2_state/       # Level 2 실습 템플릿
│       ├── level3_graphs/      # Level 3 실습 템플릿
│       ├── level4_agents/      # Level 4 실습 템플릿
│       ├── level5_multi_agent/ # Level 5 실습 템플릿
│       ├── level6_rag/         # Level 6 실습 템플릿
│       ├── level7_caching/     # Level 7 실습 템플릿
│       ├── level8_planner/     # Level 8 실습 템플릿
│       ├── level9_streaming/   # Level 9 실습 템플릿
│       ├── level10_guardrails/ # Level 10 실습 템플릿
│       ├── level11_evaluator_optimizer/ # Level 11 실습 템플릿
│       └── level12_distributed_state/   # Level 12 실습 템플릿
└── tests/
    ├── conftest.py             # Mock LLM, Fixture 모음
    ├── test_level1/ ~ test_level12/ # 각 레벨별 단위 테스트 스위트
```
