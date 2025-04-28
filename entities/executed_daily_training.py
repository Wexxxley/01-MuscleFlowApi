from datetime import date
from typing import List, Dict
from dtos.executed_exercise_dto import executed_exercise_dto

#classe utilizada para registrar um treino diario feito por um aluno. 
class executed_daily_training:
    id: int
    user_id: int
    training_date: date
    total_duration: int  # Total training duration in minutes
    exercises: List[executed_exercise_dto]  # List of exercises with: exercise_id, sets, reps, weight_kg

    def __init__(self, id: int, user_id: int, training_date: date, total_duration: int, exercises: List[executed_exercise_dto]):
        self.id = id
        self.user_id = user_id
        self.training_date = training_date
        self.total_duration = total_duration
        self.exercises = exercises