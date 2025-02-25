@echo off

REM Create virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Create database file (if it doesn't exist)
if not exist cert_monitor.db type nul > cert_monitor.db

REM Run the Streamlit app in a separate window
start cmd /c "streamlit run app.py"

REM Run the scheduler in a separate window
start cmd /c "python scheduler.py"

echo "Streamlit app and scheduler started.  Close these windows to stop."
pause