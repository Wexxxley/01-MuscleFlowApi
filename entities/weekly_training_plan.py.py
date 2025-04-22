from typing import Dict, List

from entities.executed_daily_training import planned_daily_training

# classe utilizada para crair uma ficha de treino semanal
class WeeklyTrainingPlan:
    id: int
    plan: Dict[str, List[planned_daily_training]]

    def __init__(self, id: int, daily_trainings: Dict[str, list[planned_daily_training]]):
        self.plan: Dict[str, List[planned_daily_training]] = {
            "monday": [daily_trainings.get("monday", [])],
            "tuesday": [daily_trainings.get("tuesday", [])],
            "wednesday": [daily_trainings.get("wednesday", [])],
            "thursday": [daily_trainings.get("thursday", [])],
            "friday": [daily_trainings.get("friday", [])],
            "saturday": [daily_trainings.get("saturday", [])],
            "sunday": [daily_trainings.get("sunday", [])]
        }