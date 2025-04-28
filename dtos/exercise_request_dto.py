import enum
from typing import List
from pydantic import BaseModel, Field
from utils.level_exercise import level_exercise

class exercise_request_dto(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    target_muscle_group: str = Field(min_length=1, max_length=50)
    equipment: str = Field(min_length=1, max_length=50) 
    level: level_exercise  
    url: str = Field(min_length=1, max_length=200)
    sets: int = Field(ge=1) 
    reps: int = Field(ge=1)
    weight: float = Field(ge=0.0) 