@echo off
REM ── AI Agent 개발 실습 — Windows 진입점 ──
REM 더블클릭하면 WSL(Ubuntu-24.04)로 들어가 setup.sh 를 실행합니다.
REM (WSL을 이미 쓰신다면 WSL 터미널에서 ./scripts/setup.sh 를 바로 실행해도 됩니다.)

setlocal
set DISTRO=Ubuntu-24.04

echo ▶ WSL(%DISTRO%) 로 진입해 환경을 설정합니다...
wsl -d %DISTRO% -- bash -lc "cd \"$(wslpath '%~dp0')..\" && chmod +x scripts/*.sh && ./scripts/setup.sh"

if %errorlevel% neq 0 (
  echo.
  echo [!] WSL 실행에 실패했습니다. WSL2 + Ubuntu-24.04 설치를 확인하세요:
  echo     wsl --install -d Ubuntu-24.04
)
pause
