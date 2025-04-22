from datetime import date
from typing import List, Dict
from dtos.executed_exercise import executed_exercise

#classe utilizada para registrar um treino diario feito por um aluno. 
class ExecutedDailyTraining:
    id: int
    user_id: int
    training_date: date
    total_duration: int  # Total training duration in minutes
    exercises: List[executed_exercise]  # List of exercises with: exercise_id, sets, reps, weight_kg

    def __init__(self, id: int, user_id: int, training_date: date, total_duration: int, exercises: List[executed_exercise]):
        self.id = id
        self.user_id = user_id
        self.training_date = date
        self.total_duration = total_duration
        self.exercises = exercises