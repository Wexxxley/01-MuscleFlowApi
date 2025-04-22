from datetime import date

#classe usada para armazenar um exercicio feito da classe executed_daily_training
class ExecutedExercise:
    id_exercise: int
    sets_done: int
    reps_done: int
    weight_used: int
    
    def __init__(self, id_exercise: int, sets_done: int, reps_done: int, weight_used: int):
        self.id_exercise = id_exercise
        self.sets_done = sets_done
        self.reps_done = reps_done
        self.weight_used = weight_used