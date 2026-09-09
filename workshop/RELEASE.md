# 실습 자료 안내 — 2026.09-rc3

이 자료는 AI Agent 개발 과정의 실습 자료입니다. README.md에서 준비 방법과 구현 순서를 확인합니다.

## 설치

ZIP을 풀고 Ubuntu의 workshop 폴더에서 `bash setup.sh`를 실행합니다. 설치 중 강사가 공유한 workshop-access.txt의 경로를 입력하면 키와 모델을 .env에 저장합니다. 구체적인 순서는 README.md를 따릅니다. 실제 키는 이 ZIP에 포함하지 않습니다.

## 포함 자료

- `course/`: 비교하고 실행할 완성 예제
- `build_lab/`: 노트북이 사용하는 제공 구조와 개발 검증용 참고 구현
- `exercises/`: 개발 검증용 기존 문제와 참고 풀이
- `notebooks/`: orientation(환경 확인), build-agent(주 실습), concepts(개념 예제), build-agent-solution(풀이), harness-build 및 harness-build-solution(DeepAgents 직접 구성·풀이). 실행 출력은 포함하지 않습니다.
- `notebooks/qna.ipynb`: 질문을 바꾸어 교재·실습·풀이를 검색하는 DeepAgents 학습 도우미
- `qna_materials/`: Q&A에서 읽는 공개 교재·노트북·코드 자료
- `skills/`: 예제에서 사용하는 공개 실습 절차
- `tests/`: 코드 동작 검증용 테스트
- `build_lab/HARNESS_WORKSHEET.md`: 하네스의 실행·피드백·완료 조건을 설계하는 활동지
- `pyproject.toml`, `uv.lock`: 재현 가능한 의존성 설치 정보
- `MANIFEST.json`: 포함 파일별 SHA256과 크기. 자기 자신은 해시 목록에서 제외됩니다.

실행 결과, 개인 환경 파일, 가상환경, 캐시, 개인 에이전트 지침은 포함하지 않습니다. MANIFEST.json은 파일 확인용 자동 목록이며 실습 중 편집하지 않습니다.
