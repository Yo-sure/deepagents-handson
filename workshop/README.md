# AI Agent 개발 실습 — 2026.09-rc1

주 실습은 `notebooks/build-agent.ipynb`입니다. 함수는 노트북 셀에 작성하고 실행합니다. Python 파일로 옮기지 않습니다.

## 시작

workshop 폴더에서 의존성을 설치합니다.

```bash
uv sync --locked --python 3.12 --group notebook
```

.env.example을 복사해 .env를 만들고 발급받은 키를 저장합니다. 기존 .env는 덮어쓰지 않습니다. 키를 노트북 셀에 넣지 않습니다.

```bash
.venv/bin/jupyter lab notebooks/orientation.ipynb
```

orientation.ipynb에서 환경과 첫 모델 호출을 확인한 뒤 build-agent.ipynb를 엽니다. 첫 환경 셀부터 Shift+Enter로 실행합니다. 함수 정의를 수정했다면 그 셀과 아래 연결·실행 셀을 다시 실행합니다. 현재 수업의 번호까지만 진행합니다. Ctrl+S로 저장합니다.

## 노트북 구성

- 1A·1B: 조회 도구와 Agent를 직접 작성하고 실제 메시지를 확인합니다.
- 2·2A: 업무 분기를 구현하고 입력 네 가지의 경로와 모델 호출 횟수를 비교합니다.
- 3: 제공 수정 루프의 피드백과 종료 조건을 관찰합니다.
- 4: 같은 노트북의 함수를 MCP 서버에 등록하고 실제 HTTP로 호출합니다.
- 5: A2A 결과의 수용 조건과 반례를 구현합니다.
- 6: 실제 조회·답변·원격 검토를 연결합니다.

`concepts.ipynb`에는 도구 옵션, State reducer, 중단·재개 예제가 있습니다. `build-agent-solution.ipynb`는 풀이입니다. 먼저 자신의 구현을 실행한 뒤 같은 번호를 비교합니다. API 오류가 발생하면 원인을 해결한 뒤 재실행합니다. 출력은 실제 응답이며 매번 같지 않을 수 있습니다.

서버 기동·종료는 제공 코드가 처리합니다. 기존 course·build_lab·labs Python 파일과 tests는 참고 구현과 개발 검증용입니다. 수강생은 노트북에서 실습합니다.
