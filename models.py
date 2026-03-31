from pydantic import BaseModel
from typing import List, Optional

class Email(BaseModel):
      id: str
      sender: str
      subject: str
      body: str
      is_read: bool = False
      is_archived: bool = False

class ActionRequest(BaseModel):
      action: str
      params: dict = {}

class StepResponse(BaseModel):
      observation: dict
      reward: float
      done: bool
      info: dict
