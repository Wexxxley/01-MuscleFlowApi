from pydantic import ConfigDict
from sqlmodel import SQLModel

from dtos.training_sheet.training_sheet_week_response import TrainingSheetWeekResponse


class TrainingSheetWeekMoreUsedResponse(SQLModel):
    training_sheet_week_response: TrainingSheetWeekResponse
    count: int

    model_config = ConfigDict(from_attributes=True)