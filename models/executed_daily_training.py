from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from models.executed_exercise import ExecutedExercise # Importa ExecutedExercise para evitar erro de referência circular

class ExecutedDailyTraining(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")  # FK para User
    training_date: date
    total_duration: int  # em minutos
    notes: Optional[str] = Field(default=None, nullable=True)  # Novo campo opcional
    #1:N -> Um ExecutedDailyTraining pode ter N ExecutedExercise
    exercises: List["ExecutedExercise"] = Relationship(back_populates="daily_training") 
