#!/usr/bin/env bash
# 실습 전 환경 점검 — ✅/❌ 표
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env 2>/dev/null && set +a || true
ok=0; bad=0
chk(){ if eval "$2" >/dev/null 2>&1; then echo "  ✅ $1"; ok=$((ok+1)); else echo "  ❌ $1"; bad=$((bad+1)); fi; }

echo "▶ Preflight 점검"
chk "Python 3.12+"            'uv run python -c "import sys; raise SystemExit(0 if sys.version_info[:2]>=(3,12) else 1)"'
chk "uv 설치됨"               'command -v uv'
chk "OPENROUTER_API_KEY"      '[ -n "${OPENROUTER_API_KEY:-}" ] && [ "${OPENROUTER_API_KEY}" != "sk-or-..." ]'
chk "OpenAI 호환 라우팅"       'uv run python -c "import os, analyst; raise SystemExit(0 if os.environ.get(\"OPENAI_API_KEY\") and os.environ.get(\"OPENAI_API_BASE\") else 1)"'
chk "langchain import"        'uv run python -c "import langchain"'
chk "langgraph import"        'uv run python -c "import langgraph"'
chk "deepagents import"       'uv run python -c "import deepagents"'
chk "langchain_mcp_adapters"  'uv run python -c "import langchain_mcp_adapters"'

echo "  ── 결과: ✅ $ok / ❌ $bad ──"
if [ "$bad" -ne 0 ]; then
  echo "  ❌ 항목은 Chapter 0(환경설정) 또는 README 참고. API 키는 .env 에 설정."
  exit 1
fi
echo "  🎉 모든 점검 통과 — 실습 준비 완료!"
