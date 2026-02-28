@echo off
chcp 65001 >nul
echo ========================================
echo   Portfolio Backtest - Stop Services
echo ========================================
echo.
echo Stopping all node and python processes...
echo.

taskkill /F /IM node.exe 2>nul
taskkill /F /IM python.exe 2>nul

echo.
echo All services stopped.
echo.
pause
