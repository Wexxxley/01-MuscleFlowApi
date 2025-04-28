from datetime import date
from pydantic import BaseModel, Field

#classe usada para armazenar um exercicio feito da classe executed_daily_training
class executed_exercise_dto(BaseModel):
    id_exercise: int = Field(ge=1)
    sets_done: int = Field(ge=1)
    reps_done: int = Field(ge=1)
    weight_used: int = Field(ge=0.0)