#!/usr/bin/env bash
# AI Agent 개발 실습 — 환경 설정 (WSL2 Ubuntu)
# 사용: ./scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."
echo "▶ AI Agent 개발 실습 환경 설정"
echo "  ── 이 스크립트가 만지는 것 (전역 오염 최소화) ──"
echo "   · 레포-로컬: .venv (uv 가상환경), .env (API 키 — ~/.bashrc 아님)"
echo "   · 전역(공유): uv 미설치 시 uv 설치, Node/npm 미설치 시 apt 설치"
echo "   · 정리: ./scripts/teardown.sh (레포-로컬만 삭제, 다른 설정 안 건드림)"
echo

is_wsl=0
is_darwin=0
grep -qiE "microsoft|wsl" /proc/version 2>/dev/null && is_wsl=1
[ "$(uname -s 2>/dev/null || true)" = "Darwin" ] && is_darwin=1

# 학생 기준은 WSL2 Ubuntu다. macOS는 강사/검토자용 best-effort로 막지 않는다.
if [ "$is_wsl" -ne 1 ]; then
  if [ "$is_darwin" -eq 1 ]; then
    echo "⚠️  macOS에서 실행 중입니다. 학생 실습 기준은 WSL2 Ubuntu이며, 이 경로는 강사/검토자용 best-effort입니다."
  else
    echo "❌ WSL2 환경이 아닌 것 같습니다. 이 실습은 WSL2 Ubuntu 24.04 기준입니다."
    echo "   Windows PowerShell(관리자): wsl --install -d Ubuntu-24.04"
    echo "   의도적으로 Linux에서 실행한다면: ACDC_ALLOW_NON_WSL=1 bash scripts/setup.sh"
    if [ "${ACDC_ALLOW_NON_WSL:-0}" != "1" ]; then
      exit 1
    fi
  fi
fi
case "$PWD" in
  /mnt/*)
    if [ "${ACDC_ALLOW_MNTC:-0}" != "1" ]; then
      echo "❌ 현재 레포가 Windows 파일시스템($PWD)에 있습니다."
      echo "   WSL 홈에서 다시 받으세요: git clone https://github.com/Yo-sure/deepagents-handson ~/lecture && cd ~/lecture"
      echo "   강사/검토자가 의도적으로 우회할 때만: ACDC_ALLOW_MNTC=1 bash scripts/setup.sh"
      exit 1
    fi
    echo "⚠️  Windows 파일시스템($PWD)에서 강제 진행합니다. 학생 실습 기준은 ~/lecture 입니다."
    ;;
esac

# 기본 OS 도구
if ! command -v curl >/dev/null 2>&1 || ! command -v git >/dev/null 2>&1; then
  echo "· 기본 도구(curl/git) 확인 — 없으면 OS 패키지 매니저로 설치합니다."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y curl git ca-certificates
  elif command -v brew >/dev/null 2>&1; then
    brew install curl git
  else
    echo "❌ apt-get/brew를 찾지 못했습니다. curl/git을 먼저 설치한 뒤 다시 실행하세요."
    exit 1
  fi
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

# 2-1) Node/npm + 교재 뷰어 의존성
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "· Node/npm 미설치 — OS 패키지 매니저로 설치합니다."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y nodejs npm
  elif command -v brew >/dev/null 2>&1; then
    brew install node
  else
    echo "❌ apt-get/brew를 찾지 못했습니다. Node 18+와 npm을 먼저 설치한 뒤 다시 실행하세요."
    exit 1
  fi
fi
node_major="$(node -p "Number(process.versions.node.split('.')[0])" 2>/dev/null || echo 0)"
if [ "$node_major" -lt 18 ]; then
  echo "❌ Node 18+가 필요합니다. 현재: $(node --version 2>/dev/null || echo unknown)"
  echo "   복구 예: sudo apt-get remove -y nodejs npm && sudo apt-get update && sudo apt-get install -y nodejs npm"
  echo "   그래도 18 미만이면 NodeSource 또는 nvm으로 Node 20 LTS를 설치한 뒤 다시 실행하세요."
  exit 1
fi
echo "· Node $(node --version), npm $(npm --version)"
echo "· 교재 뷰어 의존성 설치 (npm --prefix book ci)..."
npm --prefix book ci

# 3) API 키 (.env)
if [ ! -f .env ]; then
  if [ -f .env.example ]; then cp .env.example .env; else
    printf 'OPENROUTER_API_KEY=sk-or-...\nOPENAI_API_KEY=sk-or-...\nOPENAI_API_BASE=https://openrouter.ai/api/v1\nMAIL_BACKEND=mock\n' > .env
  fi
  echo "· .env 생성됨 — OPENROUTER_API_KEY 를 입력하세요: https://openrouter.ai/keys"
  echo "  (analyst import 시 OPENROUTER_API_KEY를 OpenAI 호환 변수에 맞춥니다.)"
fi

# 4) 프리플라이트
echo
if bash scripts/preflight.sh --allow-missing-key --local; then
  :
else
  echo
  echo "❌ 설정이 끝나지 않았습니다. 위 ❌ 항목을 먼저 해결한 뒤 다시 실행하세요."
  exit 1
fi
echo
echo "✅ 설치 단계 완료. 키를 넣은 뒤 live 점검: bash scripts/preflight.sh"
echo "   교재: npm --prefix book run dev · 실습: uv run python3 ch*/..."
