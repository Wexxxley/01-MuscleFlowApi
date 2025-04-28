import csv
from datetime import date
import os
import zipfile
from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from entities.exercise import exercise
from dtos.exercise_request_dto import exercise_request_dto
from utils.auxiliares import find_new_id_user, indent
from utils.auxiliares import find_new_id_exercise
from utils.level_exercise import level_exercise
import xml.etree.ElementTree as ET

exercise_router = APIRouter()

@exercise_router.get("/exercise/get_by_id/{exercise_id}", tags=["exercise"])
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
                    level=level_exercise(row[4]),
                    url=row[5],
                    sets=int(row[6]),
                    reps=int(row[7]),
                    weight=float(row[8])
                )
    return {"message": "Exercise not found"}

@exercise_router.get("/exercise/get_all", tags=["exercise"])
def get_all():
    with open("data/exercise.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        exercises = []
        for row in reader:
            exercise_instance = exercise(
                id=int(row[0]),
                name=row[1],
                target_muscle_group=row[2],
                equipment=row[3],
                level=row[4],
                url=row[5],
                sets=int(row[6]),
                reps=int(row[7]),
                weight=float(row[8])
            )
            exercises.append(exercise_instance)
    return exercises


@exercise_router.get("/exercise/get_quantity", tags=["exercise"])
def get_quantity():
    with open("data/exercise.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        exercise = list(reader)  
    return {"quantity": len(exercise)}

@exercise_router.get("/exercise/download_xml", tags=["exercise"])
def download_xml():
    Headers = [
        "id", "name", "target_muscle_group", "equipment",
        "level", "url", "sets", "reps", "weight"
    ]
    
    with open("data/exercise.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=Headers)
        root = ET.Element("exercises")
        for row in reader:
            item = ET.SubElement(root, "exercise")
            for key, value in row.items():
                field = ET.SubElement(item, key)
                field.text = value
        indent(root)  # Aplica indentação personalizada
        tree = ET.ElementTree(root)
        tree.write("data_xml/exercise.xml", encoding='utf-8', xml_declaration=True)

    return FileResponse("data_xml/exercise.xml", media_type='application/xml', filename='exercise.xml')

@exercise_router.post("/exercise/create", tags=["exercise"])
def create(exercise_request: exercise_request_dto):
    new_id = find_new_id_exercise()
    
    new_exercise = exercise(
        id=new_id, 
        name=exercise_request.name, 
        target_muscle_group=exercise_request.target_muscle_group, 
        equipment=exercise_request.equipment, 
        level=level_exercise(exercise_request.level), 
        url=exercise_request.url, 
        sets=exercise_request.sets, 
        reps=exercise_request.reps, 
        weight=exercise_request.weight
    )
        
    with open('data/exercise.csv', mode='a', newline='', encoding='utf-8') as file:
        escritor = csv.writer(file)
        escritor.writerow([new_exercise.id, new_exercise.name, new_exercise.target_muscle_group, 
                           new_exercise.equipment, new_exercise.level, new_exercise.url, new_exercise.sets, 
                           new_exercise.reps, new_exercise.weight])
    
    return {"message": "Exercise created successfully", "id": new_id}


#atualizar put
@exercise_router.put("/exercise/update/{exercise_id}", tags=["exercise"])
def update(exercise_id: int, exerciseDto: exercise_request_dto):
    with open("data/exercise.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        updated_exercise = list(reader)  

    for i, row in enumerate(updated_exercise):
        if int(row[0]) == exercise_id:
            updated_exercise[i] = [exercise_id, exerciseDto.name, exerciseDto.target_muscle_group, exerciseDto.equipment,
                                  exerciseDto.level, exerciseDto.url, exerciseDto.sets, exerciseDto.reps, exerciseDto.weight]
            break

    with open("data/exercise.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_exercise)

    return {"message": "exercise updated successfully"}

@exercise_router.delete("/exercise/delete/{exercise_id}", tags=["exercise"])
def delete_exercise(exercise_id: int):
    with open("data/exercise.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        exercises = list(reader)

    updated_exercises = [row for row in exercises if (int(row[0]) != exercise_id)]

    with open("data/exercise.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_exercises)

    return {"message": "Exercise deleted successfully"}



@exercise_router.get("/exercise/filter", tags=["exercise"])
def filter_exercises(
    target_muscle_group: str=None,
    equipment: str = None,
    level: str =None,
    weight_min: float=None,   
    weight_max: float=None,
):
    def matches(row):
        return (
            (not target_muscle_group or row[2].lower() == target_muscle_group.lower()) and
            (not equipment or row[3].lower() == equipment.lower()) and
            (not level or row[4].lower() == level.lower()) and
            (not weight_min or float(row[8]) >= weight_min) and
            (not weight_max or float(row[8]) <= weight_max)
        )

    with open("data/exercise.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return [
            exercise(
                id=int(row[0]), name=row[1], target_muscle_group=row[2],
                equipment=row[3], level=row[4], url=row[5],
                sets=int(row[6]), reps=int(row[7]), weight=float(row[8])
            )
            for row in reader if matches(row)
        ]
