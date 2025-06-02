from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List, Optional
from utils.level_exercise import level_exercise
from models.models_links import TrainingSheetWeekUserLink

if TYPE_CHECKING:
    from models.training_sheet_day import TrainingSheetDay
    from models.user import User

class TrainingSheetWeek(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None)
    level: level_exercise 

    training_sheet_days: List["TrainingSheetDay"] = Relationship(
        back_populates="training_sheet_week",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    users: List["User"] = Relationship(
        back_populates="training_sheets",
        link_model=TrainingSheetWeekUserLink,
    )