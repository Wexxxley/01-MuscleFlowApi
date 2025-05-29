from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List, Optional
from models.user import TrainingSheetUserLink


if TYPE_CHECKING:
    from models.exercise import Exercise 
    from models.user import User

class TrainingSheetExerciseLink(SQLModel, table=True):
    training_sheet_id: Optional[int] = Field(default=None, foreign_key="trainingsheet.id", primary_key=True)
    exercise_id: Optional[int] = Field(default=None, foreign_key="exercise.id", primary_key=True)

class TrainingSheet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    focus_area: Optional[str] = Field(default=None)
    level: str = Field(nullable=False)
    exercises: List["Exercise"] = Relationship(
        back_populates="training_sheets",
        link_model=TrainingSheetExerciseLink
    )
    users: List["User"] = Relationship(
        back_populates="training_sheets",
        link_model=TrainingSheetUserLink
    )

