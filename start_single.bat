@echo off
echo.
echo ==========================================
echo    Grocery Chatbot Launcher
echo ==========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create a .env file with your Gemini API key:
    echo   GOOGLE_API_KEY=your_api_key_here
    pause
    exit /b 1
)

echo Starting Flask Backend API...
start /b .\.venv\Scripts\python.exe api_server.py

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting React Frontend...
cd frontend
REM Ensure dependencies are installed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)
start /b npm run dev
cd ..

echo Waiting for frontend to start...
timeout /t 5 /nobreak >nul

echo.
echo ==========================================
echo Both servers are running!
echo.
echo Backend API:  http://localhost:5000
echo Frontend UI:  http://localhost:5173
echo.
echo Opening browser...
echo ==========================================
echo.

REM Open browser
start http://localhost:5173

REM Keep window open
pause
