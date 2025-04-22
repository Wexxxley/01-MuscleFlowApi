from typing import List

from utils.level_exercise import level_exercise

#classe utilizada para armazenar os dados de um exercício e sets,reps e weight recomendados.
class exercise:
    id: int
    name: str
    target_muscle_group: str
    equipment: str
    level: level_exercise 
    url: str  # YouTube video URL
    sets:int # recommended number of sets
    reps:int # recommended of reps
    weight: int # recommended weight in kg

    def __init__(self, id: int, name: str, target_muscle_group: str, equipment: str, level: str, url: str, tags: List[str]):
        self.id = id
        self.name = name
        self.target_muscle_group = target_muscle_group
        self.equipment = equipment
        self.level = level
        self.url = url
        self.tags = tags