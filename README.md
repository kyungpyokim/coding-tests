# AI & LangGraph TDD Playground 🧪🤖

현대적인 Python AI 엔지니어링 생태계(`uv`, `ruff`, `pytest`, `langgraph`, `pydantic v2`)를 기반으로, **TDD(테스트 주도 개발)** 방식으로 AI 에이전트와 워크플로우를 구현하며 코딩 감각을 회복할 수 있는 실습 프로젝트입니다.

---

## 🛠️ 개발 환경 및 도구 구성

| 도구 | 용도 | 명령어 요약 |
|---|---|---|
| **uv** | 초고속 패키지 관리 & 가상환경 | `uv sync`, `uv run python` |
| **ruff** | Linter & Formatter | `uv run ruff check .`, `uv run ruff format .` |
| **pytest** | 테스트 러너 & 비동기/모킹 지원 | `uv run pytest`, `uv run pytest -k "test_name"` |
| **pytest-cov**| 코드 커버리지 리포트 | `uv run pytest --cov=ai_practice` |
| **langgraph** | AI 에이전트 상태 그래프 오케스트레이션 | `src/ai_practice/level3_graphs`, `level4_agents` |

---

## 🚀 빠른 시작 (Quick Start)

### 1. 가상환경 동기화
```bash
uv sync
```

### 2. 전체 테스트 및 커버리지 확인
```bash
uv run pytest
```

### 3. 코드 린트 & 포맷팅 점검
```bash
uv run ruff check .
uv run ruff format .
```

---

## 🧭 TDD 기반 AI 개발 사이클 (Red → Green → Refactor)

```
       [ 1. RED ]
  실패하는 테스트 작성 (API 명세 & 예외 시나리오 정의)
       │
       ▼
     [ 2. GREEN ]
  테스트를 통과시키는 최소한의 비즈니스 로직 구현
       │
       ▼
   [ 3. REFACTOR ]
  타입 힌트, 중복 제거, 성능 최적화 (테스트 통과 유지)
```

> 💡 **Tip:** 모든 테스트는 유료 LLM API 호출 없이 `tests/conftest.py`의 `fake_llm` 및 Mock 도구를 통해 **100% 빠르고 결정론적(deterministic)** 으로 실행됩니다.

---

## 📚 단계별 TDD AI 코딩 실습 로드맵

### ✅ Level 1: Basics (구현 완료 & 100% 테스트 통과)
- **과제 1: `StructuredParser`** ([test_structured_parser.py](file:///Users/kimkyungpyo/Workspaces/playground/coding-skills/tests/test_level1/test_structured_parser.py))
  - 마크다운 코드 블록(````json ... ````) 및 일반 텍스트에서 안전하게 JSON을 추출하여 Pydantic 모델로 파싱.
  - JSON 문법 오류(`Malformed JSON`), 필수 필드 누락(`ValidationError`) 발생 시 `ParsingError` 발생.
- **과제 2: `ToolDispatcher`** ([test_tool_dispatcher.py](file:///Users/kimkyungpyo/Workspaces/playground/coding-skills/tests/test_level1/test_tool_dispatcher.py))
  - 일반 Python 함수를 등록받아 OpenAI/LangChain 호환 JSON Schema 자동 추출.
  - LLM의 도구 호출(`ToolCall`)을 안전하게 파싱하여 실행하고 `ToolResult` 반환.

---

### 🎯 Level 2: AI State & Robustness (다음 실습 도전 과제)
- **실습 파일**: `src/ai_practice/level2_state/` & `tests/test_level2/`
- **도전 과제**:
  1. **Sliding Window History**: 토큰 한도 초과 시 오래된 메시지를 자르고 요약본을 남기는 메시지 버퍼 리듀서 구현.
  2. **Retry with Exponential Backoff**: LLM API 호출 중 `RateLimitError` / 네트워크 타임아웃 발생 시 지수 백오프로 재시도하는 데코레이터 TDD 작성.
  3. **Semantic Response Cache**: 동일/유사 프롬프트 입력 시 캐시된 응답을 반환하는 메모리 캐시 계층 TDD 작성.

---

### 🎯 Level 3: LangGraph Workflows
- **실습 파일**: `src/ai_practice/level3_graphs/` & `tests/test_level3/`
- **도전 과제**:
  1. **StateGraph 기본**: State TypedDict/Pydantic 정의, 노드 간 상태 전이 및 Reducer 동작 검증.
  2. **Conditional Routing**: LLM 분류 결과에 따라 서로 다른 처리 노드로 라우팅하는 조건부 엣지(Conditional Edge) 테스트.
  3. **Evaluator-Optimizer Loop**: 초안 생성(Generator) -> 평가(Evaluator) -> 재작성(Optimizer) 자가 교정 루프 및 최대 반복 탈출 TDD.

---

### 🎯 Level 4: Autonomous Agents & Human-in-the-Loop
- **실습 파일**: `src/ai_practice/level4_agents/` & `tests/test_level4/`
- **도전 과제**:
  1. **Tool-calling ReAct Agent**: ToolDispatcher와 LangGraph를 결합한 자율 도구 실행 에이전트.
  2. **MemorySaver Checkpointer**: 대화 스레드 ID별 상태 영속화 및 복원 테스트.
  3. **Human-in-the-Loop Interruption**: 민감한 작업(예: 데이터 삭제, 이메일 발송) 전 실행을 멈추고 승인/거절을 받는 인터럽트 흐름 검증.

---

## 📁 디렉토리 구조

```text
coding-skills/
├── pyproject.toml              # uv 의존성 및 ruff/pytest 설정
├── .python-version             # Python 3.12+
├── .env.example                # 환경 변수 템플릿
├── README.md                   # 실습 가이드
├── src/
│   └── ai_practice/
│       ├── core/               # Pydantic 기반 공통 데이터 모델 (ToolCall, ToolResult 등)
│       ├── level1_basics/      # StructuredParser, ToolDispatcher
│       ├── level2_state/       # State Reducer, Retry, Token Trimmer (실습 예정)
│       ├── level3_graphs/      # LangGraph Workflows, Conditional Router (실습 예정)
│       └── level4_agents/      # ReAct Agent, Human-in-the-loop (실습 예정)
└── tests/
    ├── conftest.py             # Mock LLM, Fixture 모음
    ├── test_level1/            # Level 1 단위 테스트 (12개 테스트 통과)
    ├── test_level2/            # Level 2 테스트 스위트
    ├── test_level3/            # Level 3 테스트 스위트
    └── test_level4/            # Level 4 테스트 스위트
```
