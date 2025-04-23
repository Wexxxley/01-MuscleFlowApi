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
    weight: float 

    def __init__(self, id: int, name: str, target_muscle_group: str, equipment: str, level: level_exercise, url: str, sets: int, reps: int, weight: float):
        self.id = id
        self.name = name
        self.target_muscle_group = target_muscle_group
        self.equipment = equipment
        self.level = level
        self.url = url       
        self.sets = sets
        self.reps = reps
        self.weight = weight 
        
        
# from typing import List
# from utils.level_exercise import level_exercise  # enum com os níveis do exercício

# class Exercise:
#     def __init__(
#         self, 
#         id: int, 
#         name: str, 
#         target_muscle_group: str, 
#         equipment: str, 
#         level: str, 
#         url: str, 
#         tags: List[str],
#         sets: int = 3, 
#         reps: int = 12, 
#         weight: int = 10
#     ):
#         self.id = id
#         self.name = name
#         self.target_muscle_group = target_muscle_group
#         self.equipment = equipment
#         self.level = level_exercise[level.upper()]  # converte string para Enum
#         self.url = url
#         self.tags = tags
#         self.sets = sets
#         self.reps = reps
#         self.weight = weight
