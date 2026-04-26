@echo off
echo ------------------------------------------------------------
echo Income_Project (Indian Income Classification) startup helper
echo ------------------------------------------------------------
echo 1) Activate the Python virtual environment
echo    If this fails, make sure the folder "venv" exists in the project root.
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Please install Python and try again.
        pause
        exit /b 1
    )
)
call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment. Please verify venv\Scripts\activate exists.
    pause
    exit /b 1
)
echo.
echo 2) Install backend requirements (if not already installed)
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo Failed to install backend requirements.
    pause
    exit /b 1
)
echo.
echo 3) Install ML pipeline requirements (optional, if you need to retrain or update the model)
pip install -r ml_pipeline\requirements.txt
if errorlevel 1 (
    echo Failed to install ML pipeline requirements.
    pause
    exit /b 1
)
echo.
echo 4) Run Django database migrations
cd backend
python manage.py migrate
if errorlevel 1 (
    echo Failed to apply migrations.
    pause
    exit /b 1
)
echo.
echo 5) Start the Django development server
python manage.py runserver
echo.
echo The development server should now be running at http://127.0.0.1:8000/
echo Indian Income Prediction System
echo Press Ctrl+C in this window to stop the server.
