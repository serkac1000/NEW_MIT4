@echo off
cd /d %~dp0
REM Optional: activate venv if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)
python app.py
pause 