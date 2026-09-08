# 실습 자료 안내 — 2026.09-rc1

이 자료는 AI Agent 개발 과정의 실습 자료입니다. README.md에서 준비 방법과 구현 순서를 확인합니다.

## 설치

ZIP을 압축 해제하면 `workshop/` 폴더가 생성됩니다. 해당 폴더의 `README.md`에 따라 `uv sync --locked --group notebook`로 환경을 준비하고, `.env.example`을 `.env`로 복사한 뒤 자신의 API 키를 입력합니다. 실제 API 키는 이 자료에 포함하지 않습니다. 수업은 Jupyter 노트북으로 진행하며 README의 실행 순서를 따릅니다.

## 포함 자료

- `course/`: 비교하고 실행할 완성 예제
- `build_lab/`: 노트북이 사용하는 제공 구조와 개발 검증용 참고 구현
- `exercises/`: 개발 검증용 기존 문제와 참고 풀이
- `notebooks/`: orientation(환경 확인), build-agent(주 실습), concepts(개념 예제), build-agent-solution(풀이). 실행 출력은 포함하지 않습니다.
- `skills/`: 예제에서 사용하는 공개 실습 절차
- `tests/`: 코드 동작 검증용 테스트
- `build_lab/HARNESS_WORKSHEET.md`: 하네스의 실행·피드백·완료 조건을 설계하는 활동지
- `VALIDATION.md`: 현재 검증 범위와 남은 한계
- `pyproject.toml`, `uv.lock`: 재현 가능한 의존성 설치 정보
- `MANIFEST.json`: 포함 파일별 SHA256과 크기. 자기 자신은 해시 목록에서 제외됩니다.

실행 결과, 개인 환경 파일, 가상환경, 캐시, 개인 에이전트 지침은 포함하지 않습니다. MANIFEST.json은 파일 확인용 자동 목록이며 실습 중 편집하지 않습니다.
