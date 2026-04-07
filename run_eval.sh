#!/bin/bash
source venv_10/bin/activate
uvicorn server.app:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
SERVER_PID=$!
sleep 3
python -u inference.py > inference.log 2>&1
kill $SERVER_PID
