from fastapi import FastAPI, HTTPException
from server.email_triage_env import EmailTriageEnv
from models import ActionRequest, StepResponse
import os

app = FastAPI(title="Email Triage OpenEnv")
env = EmailTriageEnv()

@app.get("/")
def root():
    return {"message": "Welcome to the Email Triage OpenEnv API"}

@app.get("/state")
def state(task_id: str = None):
    return env.state(task_id)

@app.post("/reset")
def reset(task_id: str):
    return env.reset(task_id)

@app.post("/step")
def step(request: ActionRequest):
    obs, reward, done, info = env.step(request.action, request.params)
    return StepResponse(observation=obs, reward=reward, done=done, info=info)

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
