import csv
from datetime import date
import os
import zipfile
from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from dtos.user_request_dto import user_request_dto
from entities.exercise import exercise
from entities.user import user
from utils.auxiliares import find_new_id_user

exercise_router = APIRouter()

@exercise_router.get("/exercise/get_exercise_router/{exercise_id}", tags=["exercise"])
def get_by_id(user_id: int):
    with open("data/exercise.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if int(row[0]) == user_id:
                return exercise(
                    id=int(row[0]),
                    name=row[1],
                    target_muscle_group=row[2],
                    equipment=row[3],
                    level=row[4],
                    url=row[5],
                    sets=int(row[6]),
                    reps=int(row[7]),
                    weight=int(row[8])
                )
    return {"message": "Exercise not found"}
