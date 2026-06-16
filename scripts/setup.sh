#!/usr/bin/env bash
# AI Agent 개발 실습 — 환경 설정 (WSL2 Ubuntu)
# 사용: ./scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."
echo "▶ AI Agent 개발 실습 환경 설정"
echo "  ── 이 스크립트가 만지는 것 (전역 오염 최소화) ──"
echo "   · 레포-로컬: .venv (uv 가상환경), .env (API 키 — ~/.bashrc 아님)"
echo "   · 전역(공유): uv 미설치 시에만 uv 설치 → ~/.bashrc 에 PATH 2줄 추가"
echo "   · 정리: ./scripts/teardown.sh (레포-로컬만 삭제, 다른 설정 안 건드림)"
echo

# WSL 확인
if ! grep -qiE "microsoft|wsl" /proc/version 2>/dev/null; then
  echo "  ⚠️  WSL2 환경이 아닌 것 같습니다. (이 실습은 WSL2 Ubuntu 24.04 기준)"
fi

# 1) uv 설치 (있으면 건너뜀)
if ! command -v uv >/dev/null 2>&1; then
  echo "· uv 미설치 — 설치합니다. (uv 설치 프로그램이 ~/.bashrc 에 PATH 를 추가합니다)"
  echo "  전역 변경을 원치 않으면 Ctrl-C 후 직접 설치: https://docs.astral.sh/uv/"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
echo "· uv $(uv --version)"

# 2) Python 3.12 + 의존성
uv python install 3.12 >/dev/null 2>&1 || true
echo "· 의존성 설치 (uv sync)..."
uv sync

# 3) API 키 (.env)
if [ ! -f .env ]; then
  if [ -f .env.example ]; then cp .env.example .env; else
    printf 'OPENROUTER_API_KEY=sk-or-...\nOPENAI_API_KEY=sk-or-...\nOPENAI_API_BASE=https://openrouter.ai/api/v1\nMAIL_BACKEND=mock\n' > .env
  fi
  echo "· .env 생성됨 — OPENROUTER_API_KEY 를 입력하세요: https://openrouter.ai/keys"
fi

# 4) 프리플라이트
echo
bash scripts/preflight.sh || true
echo
echo "✅ 설정 완료. 교재: book/ (npm run dev) · 실습: uv run python3 ch*/..."
