#!/bin/bash
source venv_10/bin/activate
uvicorn server.app:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
SERVER_PID=$!
sleep 3
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct
# export HF_TOKEN=your_token_here
python -u inference.py > inference_hf.log 2>&1
kill $SERVER_PID
