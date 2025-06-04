from pydantic import BaseModel
from utils.day_week import day_week

class TrainingSheetDayResponse(BaseModel):
    focus_area: str
    day_of_week: day_week
    exercises_ids: list[int] 