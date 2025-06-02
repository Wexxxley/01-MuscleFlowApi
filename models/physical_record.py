from sqlmodel import Relationship, SQLModel, Field
from datetime import date
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.user import User 

class PhysicalRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: int = Field(foreign_key="user.id")
    weight: float
    height: float 
    body_fat_percentage: Optional[float] = None
    muscle_mass_percentage: Optional[float] = None
    recorded_at: date 

    user: Optional["User"] = Relationship(back_populates="physical_record")