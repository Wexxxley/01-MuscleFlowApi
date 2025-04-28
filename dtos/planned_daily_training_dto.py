from datetime import date
from typing import List, Dict

from entities.exercise import exercise

# classe utilizada para planejar um treino diario e ser incluido em uma ficha de treino
class PlannedDailyTraining:
    id: int
    name: str 
    exercises: List[exercise]

    def __init__(self, id: int, nome: str, exercises: List[exercise]):
        self.id = id
        self.name = nome
        self.exercises = exercises