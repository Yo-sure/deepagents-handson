@echo off
REM ── AI Agent 개발 실습 — Windows 진입점 ──
REM 더블클릭하면 WSL(Ubuntu-24.04) 홈의 ~/lecture 에서 setup.sh 를 실행합니다.
REM (WSL을 이미 쓰신다면 WSL 터미널에서 ./scripts/setup.sh 를 바로 실행해도 됩니다.)

setlocal
set "DISTRO=Ubuntu-24.04"
set "REPO_URL=https://github.com/Yo-sure/deepagents-handson.git"

echo ▶ WSL(%DISTRO%) 홈의 ~/lecture 에서 환경을 설정합니다...
wsl -d %DISTRO% -- bash -lc "set -e; if [ -e ~/lecture ] && [ ! -d ~/lecture/.git ]; then echo '❌ ~/lecture 가 이미 있지만 git 레포가 아닙니다. 이름을 바꾸거나 지운 뒤 다시 실행하세요.'; exit 1; fi; if [ ! -d ~/lecture/.git ]; then echo '· ~/lecture 가 없어 WSL 홈에 레포를 받습니다.'; if ! command -v git >/dev/null 2>&1; then sudo apt-get update && sudo apt-get install -y git; fi; git clone '%REPO_URL%' ~/lecture; fi; cd ~/lecture && chmod +x scripts/*.sh && ./scripts/setup.sh"

if %errorlevel% neq 0 (
  echo.
  echo [!] WSL 실행 또는 셋업에 실패했습니다. WSL2 + Ubuntu-24.04 설치와 위 오류를 확인하세요:
  echo     wsl --install -d Ubuntu-24.04
)
pause
