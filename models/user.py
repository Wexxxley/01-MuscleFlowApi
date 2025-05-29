from sqlmodel import Relationship, SQLModel, Field
from datetime import date
from typing import TYPE_CHECKING, List, Optional


if TYPE_CHECKING:
    from models.training_sheet import TrainingSheet

class TrainingSheetUserLink(SQLModel, table=True):
    training_sheet_id: Optional[int] = Field(default=None, foreign_key="trainingsheet.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    objective: str  
    height: float
    weight: float  # Pode virar uma relação com PhysicalRecord
    registration_date: date

    training_sheets: List["TrainingSheet"] = Relationship(
        back_populates="users",
        link_model=TrainingSheetUserLink
    )
