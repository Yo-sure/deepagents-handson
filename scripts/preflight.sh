#!/usr/bin/env bash
# 실습 전 환경 점검 — ✅/❌ 표
cd "$(dirname "$0")/.."
if [ -f .env ] && command -v uv >/dev/null 2>&1; then
  if ! env_lines="$(uv run python - <<'PY'
from dotenv import dotenv_values
try:
    values = dotenv_values(".env")
except Exception as e:
    print(f"DOTENV_ERROR={type(e).__name__}: {e}")
    raise SystemExit(1)
for key, value in values.items():
    if value is not None:
        print(f"{key}={value}")
PY
)"; then
    echo "❌ .env를 읽지 못했습니다. 따옴표/공백/CRLF를 확인하세요."
    exit 1
  fi
  while IFS= read -r line; do
    [ -n "$line" ] && export "$line"
  done <<EOF
$env_lines
EOF
fi
allow_missing_key=0
live_check=1
allow_mntc="${ACDC_ALLOW_MNTC:-0}"
for arg in "$@"; do
  case "$arg" in
    --allow-missing-key) allow_missing_key=1 ;;
    --allow-mntc) allow_mntc=1 ;;
    --live) live_check=1 ;;
    --local) live_check=0 ;;
  esac
done

ok=0; bad=0; critical_bad=0; key_bad=0
chk(){
  label="$1"; cmd="$2"; kind="${3:-critical}"
  if eval "$cmd" >/dev/null 2>&1; then
    echo "  ✅ $label"; ok=$((ok+1))
  else
    echo "  ❌ $label"; bad=$((bad+1))
    if [ "$kind" = "key" ]; then key_bad=$((key_bad+1)); else critical_bad=$((critical_bad+1)); fi
  fi
}

echo "▶ Preflight 점검"
case "$PWD" in
  /mnt/*)
    if [ "$allow_mntc" = "1" ]; then
      echo "  ⚠️  Windows 파일시스템($PWD)에서 강제 점검합니다. 학생 실습 기준은 ~/lecture 입니다."
    else
      echo "  ❌ 현재 경로가 Windows 파일시스템($PWD)입니다."
      echo "     WSL 홈에서 다시 받으세요: git clone https://github.com/Yo-sure/deepagents-handson ~/lecture && cd ~/lecture"
      echo "     강사/검토자가 의도적으로 우회할 때만: ACDC_ALLOW_MNTC=1 bash scripts/preflight.sh"
      bad=$((bad+1)); critical_bad=$((critical_bad+1))
    fi
    ;;
esac
chk "Python 3.12+"            'uv run python -c "import sys; raise SystemExit(0 if sys.version_info[:2]>=(3,12) else 1)"'
chk "uv 설치됨"               'command -v uv'
chk "Node 18+ 설치됨"         'command -v node && node -p "Number(process.versions.node.split(\".\")[0]) >= 18 ? 0 : 1" | grep -qx 0'
chk "npm 설치됨"              'command -v npm'
chk "book npm 의존성"         'npm --prefix book ls vitepress vue mermaid vitepress-plugin-mermaid --depth=0'
chk "샘플 문서 10건"          '[ "$(find analyst/sample_inbox -maxdepth 1 -type f ! -name "_manifest.yaml" | wc -l)" -eq 10 ]'
chk "샘플 계약 테스트"        'uv run pytest analyst/tests/test_contract.py -q'
chk "OPENROUTER_API_KEY"      '[ -n "${OPENROUTER_API_KEY:-}" ] && [ "${OPENROUTER_API_KEY}" != "sk-or-..." ]' key
chk "OpenAI 호환 라우팅"       'uv run python -c "import os, analyst; key=os.environ.get(\"OPENAI_API_KEY\"); base=os.environ.get(\"OPENAI_API_BASE\"); base_url=os.environ.get(\"OPENAI_BASE_URL\"); raise SystemExit(0 if key and key != \"sk-or-...\" and base == \"https://openrouter.ai/api/v1\" and base_url == base else 1)"' key
echo "  … Python 패키지 import 확인 중(처음 실행은 30초 이상 걸릴 수 있음)"
chk "langchain import"        'uv run python -c "import langchain"'
chk "langgraph import"        'uv run python -c "import langgraph"'
chk "deepagents import"       'uv run python -c "import deepagents"'
chk "langchain_mcp_adapters"  'uv run python -c "import langchain_mcp_adapters"'
if [ "$live_check" -eq 1 ] && [ "$key_bad" -eq 0 ]; then
  echo "  … OpenRouter live 호출 중(크레딧/라우팅/네트워크 확인)"
  tmp="$(mktemp)"
  if uv run python - <<'PY' >"$tmp" 2>&1
from langchain_openai import ChatOpenAI
import os
import analyst
model = os.environ.get("PREFLIGHT_MODEL", "google/gemini-3.5-flash")
try:
    llm = ChatOpenAI(
        model=model,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
        temperature=0,
        max_tokens=32,
        timeout=30,
        max_retries=1,
    )
    resp = llm.invoke("Reply with only OK.")
    model_name = resp.response_metadata.get("model_name", "")
    if model == "google/gemini-3.5-flash" and not model_name.startswith("google/gemini-3.5-flash"):
        print(f"ROUTING_MISMATCH requested={model} actual={model_name or '(unknown)'}")
        raise SystemExit(1)
    if not resp.response_metadata and resp.content is None:
        print("EMPTY_RESPONSE OpenRouter returned no metadata/content")
        raise SystemExit(1)
except Exception as e:
    text = str(e).replace("\n", " ")
    print(f"{type(e).__name__}: {text[:900]}")
    low = text.lower()
    if "401" in low or "unauthorized" in low:
        print("hint: 401/auth — .env의 OPENROUTER_API_KEY 값을 다시 확인하세요.")
    elif "402" in low or "credit" in low or "payment" in low:
        print("hint: 402/credit — OpenRouter 크레딧 또는 결제 한도를 확인하세요.")
    elif "404" in low or "not found" in low:
        print(f"hint: 404/model — PREFLIGHT_MODEL={model!r} 슬러그가 계정에서 사용 가능한지 확인하세요.")
    elif "timeout" in low or "timed out" in low:
        print("hint: timeout — 네트워크/VPN/방화벽 또는 OpenRouter 일시 지연을 확인하세요.")
    raise SystemExit(1)
PY
  then
    echo "  ✅ OpenRouter live 호출"; ok=$((ok+1))
  else
    echo "  ❌ OpenRouter live 호출"; bad=$((bad+1)); key_bad=$((key_bad+1))
    sed 's/^/     /' "$tmp" | head -n 8
  fi
  rm -f "$tmp"
fi

echo "  ── 결과: ✅ $ok / ❌ $bad ──"
if [ "$critical_bad" -ne 0 ]; then
  echo "  ❌ 설치/의존성 항목이 실패했습니다. Chapter 0 환경설정의 복구 절차를 확인하세요."
  exit 1
fi
if [ "$key_bad" -ne 0 ]; then
  if [ "$allow_missing_key" -eq 1 ]; then
    echo "  ⚠️  키 입력 전 부분 준비 완료 — .env의 OPENROUTER_API_KEY를 채운 뒤 다시 실행하세요."
    exit 0
  fi
  echo "  ❌ API 키 또는 live 호출 점검이 실패했습니다. .env의 OPENROUTER_API_KEY와 OpenRouter 크레딧/모델 라우팅을 확인하세요."
  exit 1
fi
if [ "$live_check" -eq 1 ]; then
  echo "  🎉 live 호출까지 통과 — 실습 준비 완료!"
else
  echo "  🎉 로컬 점검 통과 — 실제 모델 호출은 기본 preflight 또는 Step 3에서 확인하세요."
fi
