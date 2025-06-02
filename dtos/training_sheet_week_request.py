from typing import Optional
from pydantic import BaseModel
from dtos.training_sheet_day_request import TrainingSheetDayRequest
from utils.level_exercise import level_exercise

class TrainingSheetWeekRequest(BaseModel):
    name: str 
    description: str 
    level: level_exercise 
    training_sheet_days: list[TrainingSheetDayRequest] 