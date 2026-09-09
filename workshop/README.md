# AI Agent 개발 실습 — 2026.09-rc3

주 실습은 `notebooks/build-agent.ipynb`입니다. 함수는 노트북 셀에 작성하고 실행합니다. Python 파일로 옮기지 않습니다.

## 시작

Ubuntu의 workshop 폴더에서 `bash setup.sh`를 실행합니다. uv가 없으면 설치하고 Python 3.12·Jupyter·수업 라이브러리를 준비합니다. 키 파일 경로를 물으면 강사가 제한된 공유폴더에 올린 workshop-access.txt를 지정합니다. 개인 키는 경로를 비운 뒤 화면에 표시되지 않는 입력란에 입력합니다. .env는 자동 생성됩니다. 기존 설정은 유지 여부를 물으며, 새 모델로 바꿀 때는 n을 입력하고 새 파일을 지정합니다.

기본 모델은 google/gemini-3.8-flash입니다. 공유 파일의 WORKSHOP_MODEL이 우선하며 기존 .env를 유지하면 그 모델을 계속 사용합니다. 키를 노트북에 넣지 않습니다. 설치가 끝나면 다음 명령으로 노트북을 엽니다.

```bash
.venv/bin/jupyter lab --no-browser --ServerApp.root_dir=. notebooks/orientation.ipynb
```

터미널에 표시된 http://localhost 또는 http://127.0.0.1 주소 전체를 Windows 브라우저에서 엽니다. 토큰이 포함된 주소는 공유하지 않습니다. Jupyter 터미널은 수업 동안 열어 두고, 마칠 때 노트북을 저장한 뒤 Ctrl+C와 y로 서버를 종료합니다.

orientation.ipynb에서 Python 경로가 workshop/.venv/bin/python인지 확인합니다. 환경과 첫 모델 호출을 확인한 뒤 build-agent.ipynb를 엽니다. 첫 환경 셀부터 Shift+Enter로 실행합니다. 함수 정의를 수정했다면 그 셀과 아래 연결·실행 셀을 다시 실행합니다. 현재 수업의 번호까지만 진행합니다. Ctrl+S로 저장합니다.

## 노트북 구성

- 1A·1B·1C: 조회 도구·Agent 구성·호출을 작성하고 두 도구의 근거 흐름을 확인합니다.
- 2·2A·2B: 업무 분기·질문 노드와 StateGraph의 노드 등록·엣지·compile을 직접 구현합니다. 2C는 검토·수정 순환 그래프 고급 확장입니다. 모델 없는 검사와 실제 Agent 실행으로 경로·질문·초안 생성 호출을 비교합니다.
- 4장 주 실습: `harness-build.ipynb`의 H1~H3에서 자기 Skill과 DeepAgents Harness를 직접 구성·호출합니다. 정답·해설은 `harness-build-solution.ipynb`입니다.
- build-agent의 3번 수정 Loop와 harness-control.ipynb는 선택 심화입니다.
- 4: 서버 등록과 MCP 클라이언트 연결·도구 발견·Agent 호출을 직접 작성합니다.
- 5: A2A 요청 Message·Card 기반 클라이언트 연결·결과 수용 조건을 구현합니다.
- 6: 기준 실행 뒤 6D에서 MCP·발견·위임 도구를 가진 Agent를 직접 조립합니다.

`concepts.ipynb`에는 도구 옵션, State reducer, 중단·재개 예제가 있습니다. `build-agent-solution.ipynb`는 풀이입니다. 먼저 자신의 구현을 실행한 뒤 같은 번호를 비교합니다. API 오류가 발생하면 원인을 해결한 뒤 재실행합니다. 출력은 실제 응답이며 매번 같지 않을 수 있습니다.

서버 기동·종료는 제공 코드가 처리합니다. 기존 course·build_lab·labs Python 파일과 tests는 참고 구현과 개발 검증용입니다. 수강생은 노트북에서 실습합니다.

## 교재 Q&A

`notebooks/qna.ipynb`는 독립 실행합니다. 준비 셀 실행 후 질문만 바꾸면 DeepAgents가 `qna_materials`의 교재·실습·풀이를 검색하고 근거를 읽어 설명합니다. 결과 해석 및 실제 도구 요청 확인 안내도 노트북에 있습니다.
