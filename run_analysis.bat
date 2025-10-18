@echo off
echo "Changing directory to the script location..."
cd /d "%~dp0"
echo "Running the vegetation analysis pipeline..."
python main.py
echo "Pipeline execution finished."
pause
