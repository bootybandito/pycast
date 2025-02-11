@echo off
:: Create a virtual environment in the 'venv' folder
python -m venv venv

:: Activate the virtual environment
call venv\Scripts\activate

:: Upgrade pip to the latest version
pip install --upgrade pip

:: Install required Python packages
pip install flask opencv-python-headless numpy mss soundcard

:: Notify user of completion
echo Dependencies installed successfully.
pause
