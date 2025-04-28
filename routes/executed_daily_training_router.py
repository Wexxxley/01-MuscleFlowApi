import csv
import io
import xml.etree.ElementTree as ET
from datetime import date
import os
import zipfile
from fastapi import APIRouter, FastAPI, Path, Response
from fastapi.responses import FileResponse
from dtos.executed_exercise_dto import executed_exercise_dto
from dtos.executed_daily_training_dto import executed_daily_training_dto
from dtos.user_request_dto import user_request_dto
from entities.executed_daily_training import executed_daily_training
from utils.auxiliares import find_new_id_executed_daily_training, find_new_id_user, get_all_valid_exercise_ids, indent

daily_training_router = APIRouter()

@daily_training_router.get("/daily_training/get_by_id/{user_id}", tags=["executed daily training"])
def get_by_id(training_id: int):
    with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if int(row[0]) == training_id:
                returned_training = executed_daily_training(
                    int(row[0]), 
                    int(row[1]), 
                    date.fromisoformat(row[2]), 
                    int(row[3]), 
                    [executed_exercise_dto(
                        id_exercise=int(row[i]),
                        sets_done=int(row[i+1]),
                        reps_done=int(row[i+2]),
                        weight_used=float(row[i+3])
                    ) for i in range(5, len(row), 5)]
                )
                return returned_training

@daily_training_router.get("/daily_training/get_all", tags=["executed daily training"])
def get_all():
    with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        trainings = []
        for row in reader:
            training_instance = executed_daily_training(
                    int(row[0]), 
                    int(row[1]), 
                    date.fromisoformat(row[2]), 
                    int(row[3]), 
                    [executed_exercise_dto(
                        id_exercise=int(row[i]),
                        sets_done=int(row[i+1]),
                        reps_done=int(row[i+2]),
                        weight_used=float(row[i+3])
                    ) for i in range(5, len(row), 5)]
                )
            trainings.append(training_instance)
    return trainings


@daily_training_router.get("/edaily_trainingxercise/filter", tags=["executed daily training"])
def filter_daily_training(user_id: int = None, training_date: str = None):
    def matches(row) -> bool:
        return (
            (not user_id or int(row[1]) == int(user_id)) and
            (not training_date or row[2] == training_date) 
        )
     
    with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        daily_training = list(reader)

        return [
            executed_daily_training(
                int(row[0]),
                int(row[1]),
                date.fromisoformat(row[2]),
                int(row[3]),
                [executed_exercise_dto(
                    id_exercise=int(row[i]),
                    sets_done=int(row[i+1]),
                    reps_done=int(row[i+2]),
                    weight_used=float(row[i+3])
                ) for i in range(5, len(row), 5)]
            ) for row in daily_training if matches(row)
        ]

@daily_training_router.get("/daily_training/get_quantity", tags=["executed daily training"])
def get_quantity():
    with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        trainings = list(reader)  
    return {"quantity": len(trainings)}

@daily_training_router.get("/daily_training/download_zip", tags=["executed daily training"])
def download_zip():
    with zipfile.ZipFile("data_zip/e.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("data/executed_daily_training.csv", os.path.basename("data/executed_daily_training.csv"))  
    
    return FileResponse("data_zip/executed_daily_training.zip", media_type='application/zip', filename='executed_daily_training.zip')


@daily_training_router.get("/daily_training/download_xml", tags=["executed daily training"])
def download_xml():
    root = ET.Element("executed_daily_trainings")
    with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) 
        
        for row in reader:
            training = ET.SubElement(root, "training")
            ET.SubElement(training, "id").text = row[0]
            ET.SubElement(training, "user_id").text = row[1]
            ET.SubElement(training, "training_date").text = row[2]
            ET.SubElement(training, "total_duration").text = row[3]
            
            exercises = ET.SubElement(training, "exercises")
            
            for i in range(4, len(row), 5):
                exercise = ET.SubElement(exercises, "exercise")
                ET.SubElement(exercise, "exercise_id").text = row[i+1]  # Pula o marcador "EXERCISE"
                ET.SubElement(exercise, "sets_done").text = row[i+2]
                ET.SubElement(exercise, "reps_done").text = row[i+3]
                ET.SubElement(exercise, "weight_used").text = row[i+4]
    
    indent(root)
    
    tree = ET.ElementTree(root)
    tree.write("data_xml/executed_daily_training.xml", encoding='utf-8', xml_declaration=True)
    return FileResponse("data_xml/executed_daily_training.xml", media_type='application/xml', filename='executed_daily_training.xml')
 
@daily_training_router.post("/daily_training/create", tags=["executed daily training"])
def create(executed_training_dto: executed_daily_training_dto):
    valid_exercise_ids = get_all_valid_exercise_ids() 
    
    invalid_ids = []
    
    for exercise in executed_training_dto.exercises:
        if exercise.id_exercise not in valid_exercise_ids:
            invalid_ids.append(exercise.id_exercise)
    
    if invalid_ids:
        return {"message": f"Invalid exercise IDs: {', '.join(map(str, invalid_ids))}"}

    new_id = find_new_id_executed_daily_training()

    newExecutedTraining = executed_daily_training(
        id = new_id, 
        user_id= executed_training_dto.user_id,
        training_date = executed_training_dto.training_date,
        total_duration = executed_training_dto.total_duration,
        exercises = executed_training_dto.exercises
    ) 
 
    with open('data/executed_daily_training.csv', mode='a', newline='', encoding='utf-8') as file:
        escritor = csv.writer(file)
        row = [
            newExecutedTraining.id,
            newExecutedTraining.user_id,
            newExecutedTraining.training_date.strftime('%Y-%m-%d'),
            newExecutedTraining.total_duration,
        ]
        for exercise in newExecutedTraining.exercises:
            row.extend([
                "EXERCISE",
                exercise.id_exercise,
                exercise.sets_done,
                exercise.reps_done,
                exercise.weight_used
            ])

        escritor.writerow(row)

    return {"message": "Executed daily training created successfully", "id": new_id}

@daily_training_router.put("/daily_training/update/{training_id}", tags=["executed daily training"])
def update(training_id: int, executed_training_dto: executed_daily_training_dto):
    with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        updated_trainings = list(reader)  

    header = updated_trainings[0]

    for i, row in enumerate(updated_trainings[1:]):
        if int(row[0]) == training_id:
            updated_trainings[i] = [training_id, executed_training_dto.user_id, executed_training_dto.training_date.strftime('%Y-%m-%d'), executed_training_dto.total_duration]
            for exercise in executed_training_dto.exercises:
                updated_trainings[i].extend([
                    "EXERCISE",
                    exercise.id_exercise,
                    exercise.sets_done,
                    exercise.reps_done,
                    exercise.weight_used
                ])
            break

    updated_trainings.insert(0, header)

    with open("data/executed_daily_training.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_trainings)

    return {"message": "Executed daily training updated successfully"}

@daily_training_router.delete("/daily_training/delete/{training_id}", tags=["executed daily training"])
def delete(training_id: int):
    with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        trainings = list(reader)  
    
    header = trainings[0]
    updated_trainings = [row for row in trainings[1:] if int(row[0]) != training_id]
    updated_trainings.insert(0, header)

    with open("data/executed_daily_training.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_trainings)

    return {"message": "Executed daily training deleted successfully"}