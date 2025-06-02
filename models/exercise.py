from sqlmodel import Relationship, SQLModel, Field
from typing import TYPE_CHECKING, List, Optional
from utils.level_exercise import level_exercise
from models.training_sheet_day import TrainingSheetDayExerciseLink

if TYPE_CHECKING:
    from models.training_sheet_day import TrainingSheetDay


#classe utilizada para armazenar os dados de um exercício e sets,reps e weight recomendados.
class Exercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    target_muscle_group: str 
    equipment: str = Field(nullable=True)
    level: level_exercise
    url: str  # YouTube video URL
    sets: int
    reps: int
    weight: float
    
    training_sheets: List["TrainingSheetDay"] = Relationship(
        back_populates="exercises",
        link_model=TrainingSheetDayExerciseLink
    )
    