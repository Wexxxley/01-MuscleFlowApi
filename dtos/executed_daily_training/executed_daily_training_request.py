from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional
from dtos.executed_daily_training.executed_exercise_dto import executed_exercise_dto

class executed_daily_training_request(BaseModel):
    user_id: int = Field(ge=0, title="User ID")
    training_date: date  = Field(title="Date of the training")
    total_duration: int = Field(ge=0, title="Total training duration in minutes")
    notes: Optional[str] = None
    exercises: List[executed_exercise_dto] = Field(title="List of executed exercises")