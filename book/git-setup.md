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

[공개 GitHub 저장소](https://github.com/Yo-sure/deepagents-handson)의 main 브랜치에는 교재 원고와 실습 코드가 함께 있습니다. WSL 터미널에서 작업할 폴더로 이동한 뒤 실행합니다.

```bash
git clone --branch main --single-branch https://github.com/Yo-sure/deepagents-handson.git
cd deepagents-handson/workshop
```

실습하는 위치는 저장소 루트가 아니라 **workshop 폴더**입니다. 교재 웹사이트를 직접 빌드하거나 Node.js를 설치할 필요는 없습니다. `book/`, `books/`, `scripts/`는 교재 제작용이므로 수업 중 수정하지 않습니다.

## 환경 준비와 첫 호출

Python·uv가 아직 없다면 [사전 환경 준비](./workshop/start#setup)부터 진행합니다. 준비된 환경에서는 다음 명령으로 실습 의존성을 설치합니다.

```bash
uv sync --locked --python 3.12
cp .env.example .env
```

`.env`에 자신의 `OPENROUTER_API_KEY`를 입력한 뒤 모델 호출을 확인합니다. 이미 `.env`를 만들었다면 복사 명령을 다시 실행하지 않습니다.

```bash
uv run --locked python -m course.cli langchain --topic 정산
```

이후에는 ZIP 경로와 동일하게 [시작 안내](./workshop/start)와 `workshop/README.md`를 따라갑니다. 직접 작성할 파일은 `build_lab/student.py`입니다.

## 수업 중 자료가 갱신된 경우

main은 업데이트될 수 있습니다. 현재 자료의 커밋은 다음 명령으로 확인합니다.

```bash
git rev-parse --short HEAD
git status --short
```

학생 파일을 수정한 상태에서 자료를 새로 받을 때는 자신의 작업을 먼저 보관합니다. 새 버전은 다른 폴더에 복제하고, 변경 안내에 따라 작성한 함수만 옮깁니다. 기존 실습 폴더에 새 ZIP을 덮어쓰거나 학생 파일 전체를 교체하지 않습니다.

[전체 시간표로 돌아가기](./toc)

</section></div></div>
