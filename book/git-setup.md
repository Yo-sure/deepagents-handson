---
layout: page
title: Git으로 실습 자료 받기
sidebar: false
aside: false
pageClass: lec-page
---
<div class="lec workshop-edition"><div class="deck"><section class="slide">
<div class="eyebrow">선택 안내 · Git 사용자</div>

# Git으로 실습 자료 받기

Git에 익숙하다면 저장소를 복제해서 실습할 수 있습니다. Git 사용은 수업의 필수 조건이 아닙니다. 간단히 시작하려면 [실습 ZIP](./downloads/agent-workshop-2026.09-rc1.zip)을 받습니다.

## 저장소 복제

[공개 GitHub 저장소](https://github.com/Yo-sure/deepagents-handson)의 main 브랜치에는 교재 원고와 실습 코드가 함께 있습니다. Ubuntu 터미널에서 홈 폴더에 복제합니다. 이 안내의 실습 경로는 `~/deepagents-handson/workshop`입니다. ZIP 안내의 `~/lecture/workshop`과 구분합니다.

```bash
cd ~
git clone --branch main --single-branch https://github.com/Yo-sure/deepagents-handson.git
cd deepagents-handson/workshop
```

실습하는 위치는 저장소 루트가 아니라 **workshop 폴더**입니다. `pwd` 결과가 `/home/사용자명/deepagents-handson/workshop`으로 끝나고 `setup.sh`가 보이는지 확인합니다. Node.js나 교재 웹사이트 빌드는 필요하지 않습니다.

## 환경 준비와 첫 호출

현재 `workshop` 폴더에서 설치와 접속 설정을 진행합니다. 키는 설치 중 안내에 따라 설정하고 노트북 셀에 적지 않습니다.

```bash
bash setup.sh
```

‘노트북 환경 준비 완료’가 나오면 같은 터미널에서 실행합니다.

```bash
.venv/bin/jupyter lab --no-browser --ServerApp.root_dir=. notebooks/orientation.ipynb
```

터미널에 표시된 토큰이 포함된 주소를 Windows 브라우저에서 엽니다. 주소와 토큰을 다른 사람에게 공유하지 않습니다. `orientation.ipynb`의 환경 확인 셀에서 실행 Python이 이 폴더의 `.venv/bin/python`인지 보고, 다음 셀에서 첫 모델 호출을 확인합니다. 문제가 있으면 [접속·환경 확인 안내](./workshop/start#connection)를 봅니다.

|할 일|파일|
|---|---|
|환경·첫 모델 호출 확인|notebooks/orientation.ipynb|
|각 장의 함수 작성|notebooks/build-agent.ipynb|
|작성한 함수와 풀이 비교|notebooks/build-agent-solution.ipynb|

나중에 다시 열 때에는 `cd ~/deepagents-handson/workshop`으로 돌아온 뒤 위 Jupyter 명령을 실행합니다. 설치를 반복할 필요는 없습니다. 커널을 재시작했다면 노트북 맨 위의 선행 셀 안내를 따릅니다.

## 수업 중 자료가 갱신된 경우

main은 업데이트될 수 있습니다. 현재 자료의 커밋은 다음 명령으로 확인합니다.

```bash
git rev-parse --short HEAD
git status --short
```

실습 노트북을 수정한 상태에서 자료를 새로 받을 때는 자신의 작업을 먼저 보관합니다. 새 버전은 다른 폴더에 복제하고, 변경 안내에 따라 작성한 함수만 옮깁니다. 기존 실습 폴더에 새 ZIP을 덮어쓰거나 실습 노트북 전체를 교체하지 않습니다.

**다음 단계:** 첫 모델 호출이 끝났다면 [LangChain 실습](./workshop/langchain)으로 이어갑니다. 이미 진행 중이었다면 [실습 전체 모아보기](./workshop/build)에서 해당 장을 찾습니다.

</section></div></div>
