# 실행 환경과 검사 범위

수강생은 교재의 Python 실행 창에서 짧은 예제를 실행하고, 모델 호출과 연결 실습은 Jupyter 노트북에서 진행합니다. orientation.ipynb → build-agent.ipynb 순서이며 concepts.ipynb는 개념 예제, build-agent-solution.ipynb는 비교할 풀이입니다.

## 2026-09-09 클린 Ubuntu 점검

기존 가상환경이 없는 WSL Ubuntu 24.04 기준 환경을 별도 배포판으로 복제했습니다. 배포 ZIP을 Ubuntu 홈에 풀고 bash setup.sh로 uv 설치, Python 3.12 가상환경 생성, notebook 그룹 의존성 설치, 공유 키 파일 등록까지 실행했습니다. 189개 패키지가 설치되었으며 의존성 충돌 검사를 통과했습니다. 설치 스크립트를 다시 실행해도 기존 키 설정을 유지했습니다.

- 자동 검사 116개를 통과했습니다. 노트북 회귀 검사에서는 모델을 테스트 대역으로 대체하고 MCP·A2A의 HTTP 연결은 실제로 실행합니다.
- 배포 ZIP만 검사하면 교재 원문을 읽는 검사 1개가 생략됩니다. 전체 검사에서는 같은 버전의 LangChain 교재 원문을 별도 위치에 제공했습니다.
- 별도의 실제 모델 검사에서는 기존 키와 Gemini 3.8 Flash를 사용했습니다. orientation·concepts 전체와 학생 노트북의 지정된 구현 부분만 풀이로 채운 전체 흐름을 각각 새 Jupyter 커널에서 실행했습니다. 제공된 연결·검사 셀은 그대로 사용했습니다.
- 실제 모델로 정상·없는 업무, Graph 분기, 수정 상한과 진전 없는 반복, MCP 반복 호출, A2A 검토 반려, 새 커널에서 통합 실행, 조회 실패 시 원격 검토 생략을 확인했습니다.
- Skill 문서를 임시 복사본에서 수정한 뒤 정산·계정·없는업무를 실행했습니다. 문서 읽기와 정책 조회 기록, 미등록 업무에 대한 추가 질문을 확인했습니다.
- Jupyter 시작 명령에 --ServerApp.root_dir=.를 명시했습니다. 생략하면 notebooks 폴더가 탐색기의 루트가 되어 Skill 파일을 열 수 없는 문제가 있었습니다. 현재 명령으로 노트북과 skills/policy-answer/SKILL.md를 함께 열 수 있는지 자동 검사합니다.
- 인증된 JupyterLab HTTP 요청과 WebSocket 코드 실행으로 실제 커널이 workshop/.venv의 Python을 사용하는지 확인했습니다.
- 배포 노트북의 실행 출력·횟수 제거, 파일별 해시, 비밀정보 제외를 확인했습니다. 교재 빌드와 배포 파일 대조 검사도 통과했습니다.

## 검증 범위

이 결과는 준비된 WSL Ubuntu 기준 환경부터의 설치·실행 확인입니다. Windows에 WSL을 처음 설치하거나 회사별 네트워크 정책을 설정하는 과정, 운영 인증, 서버 재시작 후 영속 복구는 포함하지 않습니다. 실제 모델 검사는 명시한 입력의 실행 결과이며 모든 자연어 입력의 정확성을 보장하지 않습니다.

전체 의존성은 uv.lock으로 고정합니다. notebook 그룹은 수업에 필수입니다. LangChain MCPAdapter의 beta 경고는 현재 API 상태 안내이며 검사 실패와 구분합니다. course.cli·build_lab.runner·exercises는 회귀 검사와 참고 구현이 사용하므로 유지하며, 수강생의 실습 실행 경로는 Jupyter입니다.

## 2026-09-09 Card 발견·선택 및 REST 추가 검증

배포 노트북 6D를 실제 모델과 새 Jupyter 커널에서 실행했습니다. 후보 주소는 코드가 제공하며, 모델은 discover_agents가 HTTP로 읽은 두 Card를 비교하고 delegate_to_agent 인자로 후보와 기능을 선택했습니다.

- 정책 요청: candidate-b / review-policy / JSONRPC, 실제 Task completed 및 업무 판정 accepted.
- 표현 요청: candidate-a / review-style / HTTP+JSON, 실제 Task completed 및 표현 검토 산출물. 정책 판정 passed는 생성하지 않습니다.
- 미등록 업무: MCP found=false 이후 추가 질문. A2A 위임 기록은 비어 있었습니다.

이는 세 입력의 실제 실행 검증이며 임의 입력에서 선택을 보장하는 검사는 아닙니다. 필수 검토 순서는 코드 관문으로 보장해야 합니다. 후보 발견 도구는 등록된 주소에서 Card를 읽으며 인터넷 검색이나 자동 신뢰 부여를 수행하지 않습니다.
