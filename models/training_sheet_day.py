from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List, Optional
from utils.day_week import day_week
from models.models_links import TrainingSheetDayExerciseLink

if TYPE_CHECKING:
    from models.training_sheet_week import TrainingSheetWeek
    from models.exercise import Exercise

class TrainingSheetDay(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    focus_area: Optional[str] = Field(default=None)
    training_sheet_week_id: int = Field(foreign_key="trainingsheetweek.id")  
    day_of_week: day_week

    exercises: List["Exercise"] = Relationship(
        back_populates="training_sheets",
        link_model=TrainingSheetDayExerciseLink,
    )

    # Use string literal for the type hint here
    training_sheet_week: "TrainingSheetWeek" = Relationship(back_populates="training_sheet_days")