@echo off
:: Check if the virtual environment exists
if exist venv\Scripts\activate (
    :: Activate the virtual environment
    call venv\Scripts\activate
    echo Virtual environment activated.

) else (
    :: If venv does not exist, print a message and exit
    echo Virtual environment not found. Please run the install script first.
    pause
    exit /b
)

:: Ensure all dependencies are installed
pip install --upgrade pip
pip install flask opencv-python-headless numpy mss soundcard

:: Run the webui.py script
python webui.py
