@echo off
REM OraHub - Flask Development Server Launcher
REM Usage: run_server.bat

cd /d "%~dp0"

echo.
echo ============================================
echo  🚀 OraHub - Development Server
echo ============================================
echo.

REM Lancer le serveur Flask
if exist ".venv-4\Scripts\python.exe" (
	".venv-4\Scripts\python.exe" run.py
) else (
	python run.py
)

pause
