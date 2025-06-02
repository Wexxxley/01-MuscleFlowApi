from typing import Optional
from pydantic import BaseModel
from dtos.training_sheet_day_responde import TrainingSheetDayResponse
from utils.level_exercise import level_exercise

class TrainingSheetWeekResponse(BaseModel):
    id: int
    name: str 
    description: str 
    level: level_exercise 
    training_sheet_days: list[TrainingSheetDayResponse]