# 개인 실습 · 2026.09

## 수업 전 준비

Python 3.12 이상과 uv를 사용할 수 있는 환경을 준비합니다. WSL Ubuntu 24.04에서 검증합니다. 운영체제·Git 설치 자체는 수업 범위 밖이며, 사전 준비가 어려우면 수업 담당자에게 준비된 실행 환경을 요청합니다.

저장소 자료의 `workshop` 폴더를 편집기로 열고, 그 폴더에서 터미널을 엽니다. [uv 공식 설치 안내](https://docs.astral.sh/uv/getting-started/installation/)를 참고합니다. 이후 다음 명령을 실행합니다.

```bash
uv sync --locked
uv run python -m course.cli langchain --mode fixed
```

최초 설치는 인터넷이 필요합니다. 설치가 끝난 fixed 실행은 외부 모델 키 없이 동작합니다. 마지막 답변에 `재무지원팀`, `P-01`이 나오고 `runs/langchain-fixed.json`이 생성되면 준비 확인을 마칩니다.

## 독립 실행

```bash
uv run python -m course.cli graph
uv run python -m course.cli approval --decision reject
uv run python -m course.cli harness
uv run python -m course.cli deepagent
uv run python -m course.cli mcp
uv run python -m course.cli a2a
uv run python -m course.integration --topic 계정
```

`course.cli all`은 독립 예제를 차례대로 실행합니다. `course.integration`은 MCP 조회 결과를 분기·초안·수정·A2A 검토에 전달합니다. 통합은 정상 입력에서 `decision: accepted`, 알 수 없는 주제나 빈 회신 대상에서 `decision: ask`를 반환합니다. 초안 검증은 팀 이름·근거 ID 포함 여부를 확인하는 학습용 규칙이며 내용의 모든 오류를 판별하지 않습니다.

결과 JSON은 `runs/`에 저장합니다. 같은 모드와 명령을 다시 실행하면 최근 결과로 덮어쓰므로 비교할 기록은 다른 이름으로 복사합니다. MCP/A2A 명령은 자신이 생성한 로컬 서버를 자동 종료합니다. 실습 티켓은 임시 DB이며 실제 메일이나 업무 알림을 발송하지 않습니다.

## 개인 과제

`exercises/student.py`에서 해당 함수만 수정하고 저장합니다. `langchain`, `graph`, `loop`, `mcp`, `a2a` 중 하나를 선택합니다.

```bash
uv run python -m exercises.check langchain
uv run python -m exercises.check langchain --solution
```

초기 학생 코드는 의도적으로 FAIL이 나옵니다. `--solution`은 학생 파일을 덮어쓰지 않고 기준 풀이를 검사합니다. 다음 모듈을 시작할 때 이전 함수의 오류는 영향을 주지 않습니다. 검사기는 과제 함수에 대한 검사이며, `course.cli` 예제는 제공된 완성 코드를 실행합니다.

## live 선택 실행

`.env.example`을 `.env`로 복사하고 유효한 `OPENROUTER_API_KEY`를 입력합니다. 모델 선택은 `WORKSHOP_MODEL`로 변경합니다.

```bash
uv run python -m course.cli langchain --mode live
uv run python -m course.cli deepagent --mode live
uv run python -m course.integration --mode live
```

fixed는 LLM 추론과 Skill 선택을 검증하지 않습니다. A2A live 검토는 규칙 검사에 모델의 표현 검토를 추가하며, 모델 의견이 규칙 검사를 대체하지 않습니다. `harness` 단독 명령의 수정 함수는 항상 고정이며 live 수정은 통합 예제에서 실행합니다.

401은 인증 실패입니다. 키·계정을 확인하고 fixed로 복귀합니다. `ModuleNotFoundError`이면 터미널 위치가 `workshop`인지 확인한 뒤 `uv sync --locked`를 실행합니다. `FAIL`만 출력되면 설치 문제가 아니라 과제의 조건 불충족인지 검사 항목을 읽습니다.

## 제공 코드 검사

```bash
uv run pytest -q
```

이 검사는 기준 풀이, 초기 오답 검출, MCP 서버 재시작, 실제 A2A 왕복을 포함합니다. 실제 LLM 호출 품질은 이 검사와 별도로 확인해야 합니다.
