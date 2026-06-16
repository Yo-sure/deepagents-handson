#!/usr/bin/env bash
# 실습 환경 정리 — 이 레포가 만든 로컬 산출물만 제거한다.
# ~/.bashrc, 전역 uv/Python, 다른 프로젝트는 절대 건드리지 않는다.
# 사용: ./scripts/teardown.sh
set -uo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
echo "▶ 실습 로컬 환경 정리 (레포: $ROOT)"
echo "  ※ 레포 내부 산출물만 삭제 — 전역 설정/.bashrc/uv는 그대로 둡니다."
echo

remove() { [ -e "$1" ] && { rm -rf "$1" && echo "  ✔ 삭제: $1"; } || echo "  · 없음: $1"; }

# 레포-로컬 산출물 (재생성 가능)
remove ".venv"                      # uv 가상환경 (uv sync 로 재생성)
remove "book/node_modules"          # VitePress 의존성 (npm install 로 재생성)
remove "book/.vitepress/dist"       # HTML 빌드 산출
remove "book/.vitepress/cache"
remove "book/public/images"         # books/images 에서 자동 복사본
find . -path ./book/node_modules -prune -o -name "__pycache__" -type d -print 2>/dev/null \
  | while read -r d; do rm -rf "$d"; done; echo "  ✔ __pycache__ 정리"

# .env 는 API 키가 들어있어 별도 확인
if [ -f .env ]; then
  read -rp "  .env(API 키 포함)도 삭제할까요? [y/N] " a
  [[ "${a:-N}" =~ ^[Yy]$ ]] && { rm -f .env && echo "  ✔ 삭제: .env"; } || echo "  · 보존: .env"
fi

echo
echo "정리 완료. 다시 세팅하려면: ./scripts/setup.sh"
echo
echo "── 전역(공유) 항목은 자동 삭제하지 않습니다 ──"
echo "  · uv 설치 시 ~/.bashrc 에 추가된 PATH 2줄 (~/.local/bin). 다른 uv 프로젝트와 공유."
echo "    제거 원하면 직접: ~/.bashrc 에서 '.local/bin' 관련 줄 + 'uv'(~/.local/bin/uv, ~/.local/share/uv) 수동 삭제."
echo "  · 강의는 ~/.bashrc 에 API 키를 넣지 않습니다(레포-로컬 .env 사용) — 정리할 전역 키 없음."
