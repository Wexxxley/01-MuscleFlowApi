from sqlmodel import Relationship, SQLModel, Field
from datetime import date
from typing import TYPE_CHECKING, List, Optional
from models.physical_record import PhysicalRecord
from models.training_sheet_week import TrainingSheetWeek
from models.models_links import TrainingSheetWeekUserLink

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    objective: str  
    registration_date: date

    physical_record: List["PhysicalRecord"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}

    )    
    training_sheets: List["TrainingSheetWeek"] = Relationship(
        back_populates="users",
        link_model=TrainingSheetWeekUserLink
    )
