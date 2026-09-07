# 실행 환경과 검사 범위

자료 버전: 2026.09-rc1. 공통 실행 환경: WSL Ubuntu 24.04, Python 3.12, uv.lock. 선택 주피터 환경도 같은 lock의 notebook 그룹을 사용합니다.

기준 풀이 회귀 검사는 `uv run --locked pytest -q`입니다. 학생 구현은 `uv run --locked pytest tests/test_build_lab.py --build-student -q`로 검사합니다. 처음 학생 파일은 미구현 부분이 있어 실패하는 것이 정상입니다.

실제 실행은 build_lab.runner를 사용합니다. 기준 풀이 실행은 build_lab.reference이며 학생 구현의 성공을 의미하지 않습니다. 모델 호출 없이 진행하는 가짜 응답 모드는 없습니다. 테스트용 모델 대역은 tests에만 있습니다.

검증 범위에는 학생 도구 계약·업무 분기·제공 그래프·수정 예산·MCP 실제 HTTP·A2A 실제 검토·새 커널의 풀이 노트북 실행을 포함합니다. 실제 수강생의 학습 시간, 운영 인증, 모든 자연어 답변의 정확성까지 보장하는 기록은 아닙니다.

주요 고정 버전: LangChain 1.4.0, LangGraph 1.2.11, DeepAgents 0.7.13, MCP 2.1.1, A2A SDK 1.1.2. JupyterLab 4.6.3, ipykernel 7.3.0은 선택 notebook 그룹입니다. 전체 의존성 버전은 uv.lock을 봅니다.

알려진 표시: LangChain MCPAdapter의 beta 경고는 현재 API 상태 안내입니다. 오류가 발생하면 실제 원인을 해결한 뒤 다시 실행합니다. 검증 완료와 작업 접수, completed와 accepted를 구분합니다.
