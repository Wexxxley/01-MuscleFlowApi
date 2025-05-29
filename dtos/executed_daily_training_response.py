from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

from dtos.executed_exercise_response import executed_exercise_response

class executed_daily_training_response(BaseModel):
    id: int
    user_id: int
    training_date: date
    total_duration: int
    notes: Optional[str] = None
    exercises: List[executed_exercise_response]