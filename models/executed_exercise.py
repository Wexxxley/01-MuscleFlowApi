from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.executed_daily_training import ExecutedDailyTraining # Importa ExecutedDailyTraining para evitar erro de referência circular

class ExecutedExercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    daily_training_id: int = Field(foreign_key="executeddailytraining.id")  # FK para ExecutedDailyTraining
    id_exercise: int = Field(foreign_key="exercise.id") # FK para Exercise
    sets_done: int = Field(ge=1)
    reps_done: int = Field(ge=1)
    weight_used: float = Field(ge=0.0)
    
    # Relacionamento inverso para ExecutedDailyTraining
    daily_training: Optional["ExecutedDailyTraining"] = Relationship(back_populates="exercises")
    