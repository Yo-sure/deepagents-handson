# 실습 자료 배포 후보 — 2026.09-rc1

이 자료는 AI Agent 개발 과정의 실습용 배포 후보입니다. 공개 배포 여부는 교재 사이트에서 확인합니다. ZIP 생성이나 자동 검사 통과만으로 수업 진행 검증이 완료된 것은 아닙니다.

## 설치

ZIP을 압축 해제하면 `workshop/` 폴더가 생성됩니다. 해당 폴더의 `README.md`에 따라 `uv sync --locked`로 환경을 준비하고, `.env.example`을 `.env`로 복사한 뒤 자신의 API 키를 입력합니다. 실제 API 키는 이 자료에 포함하지 않습니다. 노트북을 사용하는 경우 README의 노트북 설치 절차를 따릅니다.

## 포함 자료

- `course/`: 비교하고 실행할 완성 예제
- `build_lab/`: 직접 구현하는 주 실습의 재료, 학생 코드와 기준 풀이
- `exercises/`: 개념 확인 문제와 확장 과제
- `notebooks/`: 학생용·풀이용 노트북. 실행 출력은 포함하지 않습니다.
- `skills/`: 예제에서 사용하는 공개 실습 절차
- `tests/`: 코드 동작 검증용 테스트
- `build_lab/HARNESS_WORKSHEET.md`: 하네스의 실행·피드백·완료 조건을 설계하는 활동지
- `VALIDATION.md`: 현재 검증 범위와 남은 한계
- `pyproject.toml`, `uv.lock`: 재현 가능한 의존성 설치 정보
- `MANIFEST.json`: 포함 파일별 SHA256과 크기. 자기 자신은 해시 목록에서 제외됩니다.

실행 결과, 개인 환경 파일, 가상환경, 캐시, 개인 에이전트 지침은 포함하지 않습니다. 소스의 미커밋 변경도 패키지에 반영되므로, 같은 버전명이라도 후보 검수 중에는 해시가 바뀔 수 있습니다. 파일명과 SHA256을 함께 기록해야 동일한 자료를 구분할 수 있습니다.

## 파일 무결성 확인

배포되는 `agent-workshop-2026.09-rc1.sha256`의 값과 ZIP 파일 해시를 비교합니다.

```powershell
Get-FileHash ./agent-workshop-2026.09-rc1.zip -Algorithm SHA256
```

```bash
sha256sum -c agent-workshop-2026.09-rc1.sha256
```

SHA256은 파일 변경 여부를 확인하는 값이며, 제공자의 신원을 인증하는 서명은 아닙니다.

## 유지보수자: 패키지 재생성

저장소 루트에서 Python 3.12 이상으로 실행합니다. 별도 패키지 설치는 필요하지 않습니다.

```bash
python scripts/package-workshop.py
python scripts/package-workshop.py --check
```

결과는 `book/public/downloads/`에 생성됩니다. 스크립트는 허용된 파일만 수집하며, 경로·비밀키 패턴·노트북 출력·압축 해제·파일 해시를 검사합니다. 순서와 ZIP 메타데이터가 고정되어 같은 입력 바이트로 같은 ZIP이 생성됩니다. 교재 사이트 빌드 전 실행하고, 소스 변경 후에는 반드시 다시 생성합니다.
