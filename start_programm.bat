cd "$(dirname "$0")"
cd /d %~dp0
pip install -r Application/Backend/requirements.txt


start cmd.exe /c "python3 -m http.server -b 127.0.0.1 8080 -d ./Application"
cd Application\Backend\app
start cmd.exe /c "uvicorn main:app" 

rundll32 url.dll,FileProtocolHandler http://127.0.0.1:8080/
