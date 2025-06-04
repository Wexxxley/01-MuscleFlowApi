from pydantic import ConfigDict
from sqlmodel import SQLModel

from models.exercise import Exercise


class TopExecutedExerciseResponse(SQLModel):
    exercise: Exercise 
    execution_count: int

    model_config = ConfigDict(from_attributes=True)