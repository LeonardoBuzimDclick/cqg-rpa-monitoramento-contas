echo off
pip install -r .\requirements.txt
python main.py hml False
echo %ERRORLEVEL%