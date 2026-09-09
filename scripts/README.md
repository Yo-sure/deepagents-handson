# 실습 ZIP 패키징 — 유지보수자 안내

학습자용 설치 안내는 workshop/README.md입니다. 이 문서는 저장소에서 배포 자료를 만드는 작업만 설명합니다.

## 생성과 검사

저장소 루트에서 Python 3.12 이상으로 실행합니다. 외부 Python 패키지는 필요하지 않습니다.

```bash
python scripts/test_package_workshop.py
python scripts/package-workshop.py
python scripts/package-workshop.py --check
```

book의 npm run build도 prebuild에서 ZIP을 생성합니다. 산출물은 book/public/downloads/agent-workshop-2026.09-rc3.zip입니다. 생성 후 --check는 압축 내용·manifest와 현재 원본의 일치를 검사합니다. 원본 변경 후에는 다시 생성해야 합니다.

## 포함 범위와 검증

package-workshop.py의 TOP_FILES/EXTRA_FILES/DIRECTORIES가 포함 범위를 정합니다. 임의 폴더 전체를 압축하지 않습니다. 허용 폴더에 새 Python·Markdown·노트북을 추가하면 포함될 수 있으므로 공개 여부를 검토합니다.

.env·runs·가상환경·캐시·개인 지침은 제외합니다. 키 패턴과 노트북 출력·첨부를 거부하고, 경로·일반 파일 속성·중복·파일별 해시를 확인합니다. 자동 검사는 별도의 공개 자료 검토를 대신하지 않습니다.

자료는 텍스트 파일만 수집하며 CRLF를 LF로 통일합니다. 파일 순서·시간·권한을 고정하고 압축하지 않아 플랫폼별 줄바꿈과 압축기 차이로 인한 해시 변화를 줄입니다. 같은 원본 내용은 같은 ZIP 바이트로 생성됩니다.

SHA256은 생성 로그와 ZIP 내부 MANIFEST.json에 남깁니다. 학습자에게 별도 체크섬 다운로드나 해시 대조를 요구하지 않습니다. 이전 버전의 .sha256 보조 파일은 현재 버전 ZIP 생성 시 제거합니다.

## 공개 전 확인

생성 ZIP을 직접 열어 관리자 기록이나 개인 값이 섞이지 않았는지 확인합니다. GitHub Pages 배포 후 실제 다운로드를 다시 받아 커밋 원본으로 만든 ZIP과 비교합니다. Git clone 경로는 book/git-setup.md에서 안내합니다.
