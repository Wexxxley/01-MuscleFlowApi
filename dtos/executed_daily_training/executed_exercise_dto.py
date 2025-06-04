from datetime import date
from typing import List
from pydantic import BaseModel

class executed_exercise_dto(BaseModel):
    id_exercise: int
    sets_done: int
    reps_done: int
    weight_used: float