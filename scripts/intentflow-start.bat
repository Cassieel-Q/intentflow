@echo off
setlocal
py -3 "%~dp0intentflow.py" %*
exit /b %errorlevel%
