#!/usr/bin/env bash
# WSL Ubuntu: install the notebook environment, then configure access.
set -euo pipefail
cd "$(dirname "$0")"
trap 'printf "설치가 중단됐습니다. 위 오류를 확인한 뒤 bash setup.sh를 다시 실행하세요.\n" >&2' ERR
case "$PWD" in
  /mnt/*) echo 'workshop 폴더를 Ubuntu 홈으로 복사한 뒤 실행하세요.' >&2; exit 1 ;;
esac
if ! command -v uv >/dev/null 2>&1; then
  if [ -x "$HOME/.local/bin/uv" ]; then
    export PATH="$HOME/.local/bin:$PATH"
  else
    if ! command -v curl >/dev/null 2>&1; then
      echo 'curl이 필요합니다. Ubuntu에서 sudo apt-get update && sudo apt-get install -y curl ca-certificates 실행 후 다시 시작하세요.' >&2
      exit 1
    fi
    installer=$(mktemp)
    curl --fail --silent --show-error --location https://astral.sh/uv/install.sh -o "$installer"
    env UV_NO_MODIFY_PATH=1 sh "$installer"
    rm -f "$installer"
    export PATH="$HOME/.local/bin:$PATH"
  fi
fi
uv sync --locked --python 3.12 --group notebook
.venv/bin/python configure_access.py
.venv/bin/python -c 'import langchain, langgraph, deepagents, mcp, a2a, jupyterlab; print("노트북 환경 준비 완료")'
printf '\n다음 명령으로 Jupyter를 열고 환경 확인 → 모델 호출 셀을 실행하세요.\n.venv/bin/jupyter lab --no-browser --ServerApp.root_dir=. notebooks/orientation.ipynb\n'
