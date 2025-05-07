import csv
import io
import xml.etree.ElementTree as ET
from datetime import date
import os
import zipfile
from fastapi import APIRouter, FastAPI, HTTPException, Path, Response
from fastapi.responses import FileResponse
from dtos.executed_exercise_dto import executed_exercise_dto
from dtos.executed_daily_training_dto import executed_daily_training_dto
from entities.executed_daily_training import executed_daily_training
from utils.auxiliares import find_new_id_executed_daily_training, get_all_valid_exercise_ids, indent
from log.executed_training import logger
import hashlib

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
                logger.info(f"Training found: {returned_training}")
                return returned_training
            
    logger.warning(f"Executed daily training with ID {training_id} not found")
    raise HTTPException(status_code=404, detail="Executed daily training not found")

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
    
    logger.info(f"Successfully fetched {len(trainings)} executed daily trainings")
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

        retorno =  [
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

        if not retorno:
            logger.warning(f"No executed daily trainings found matching the criteria")
            raise HTTPException(status_code=404, detail="Executed daily training not found")
        
        logger.info(f"Filtered executed daily trainings: {len(retorno)} found")
        return retorno

@daily_training_router.get("/daily_training/get_quantity", tags=["executed daily training"])
def get_quantity():
    try: 
        with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            trainings = list(reader)

        logger.info(f"Total executed daily trainings: {len(trainings)}")  
        return {"quantity": len(trainings)}
    
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@daily_training_router.get("/daily_training/download_zip", tags=["executed daily training"])
def download_zip():
    try:
        with zipfile.ZipFile("data_zip/e.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write("data/executed_daily_training.csv", os.path.basename("data/executed_daily_training.csv"))  
        
        logger.info("ZIP file created successfully")
        hash_sha256 = get_hash_csv()
        return FileResponse(
                    path="data_zip/executed_daily_training.zip",
                    media_type='application/zip',
                    filename='executed_daily_training.zip',
                    headers={"X-CSV-Hash": str(hash_sha256)}
                )
    except Exception as e:
        logger.error(f"Error creating ZIP file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@daily_training_router.get("/daily_training/download_xml", tags=["executed daily training"])
def download_xml():
    try: 
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

        logger.info("executed_daily_training.xml created successfully")
        return FileResponse("data_xml/executed_daily_training.xml", media_type='application/xml', filename='executed_daily_training.xml')
    
    except Exception as e:
        logger.error(f"Error creating XML file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@daily_training_router.get("/daily_training/hash", tags=["executed daily training"])
def get_hash_csv():
    try: 
        with open("data/executed_daily_training.csv", 'rb') as f:
            file_data = f.read()
            sha256_hash = hashlib.sha256(file_data).hexdigest()
            logger.info("SHA256 hash of executed_daily_training.csv generated successfully")
            return {"hash": str(sha256_hash)}
    except Exception as e:
        logger.error(f"An error occurred while generating the hash: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating hash: {e}")

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

    logger.info(f"Executed daily training created successfully with ID {new_id}")
    return {"message": "Executed daily training created successfully", "id": new_id}

@daily_training_router.put("/daily_training/update/{training_id}", tags=["executed daily training"])
def update(training_id: int, executed_training_dto: executed_daily_training_dto):
    with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        updated_trainings = list(reader)  

    header = updated_trainings[0]

    training_found = False
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
            training_found = True
            break

    if not training_found:
        logger.warning(f"Executed daily training with ID {training_id} not found")
        raise HTTPException(status_code=404, detail="Executed daily training not found")

    updated_trainings.insert(0, header)

    with open("data/executed_daily_training.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_trainings)

    logger.info(f"Executed daily training with ID {training_id} updated successfully")
    return {"message": "Executed daily training updated successfully"}

@daily_training_router.delete("/daily_training/delete/{training_id}", tags=["executed daily training"])
def delete(training_id: int):
    with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        trainings = list(reader)  
    
    header = trainings[0]


    updated_trainings = []
    training_found = False
    for i, row in enumerate(trainings[1:]):
        if int(row[0]) == training_id:
            training_found = True
            continue
        updated_trainings.append(row)

    if not training_found:
        logger.warning(f"Executed daily training with ID {training_id} not found")
        raise HTTPException(status_code=404, detail="Executed daily training not found")

    updated_trainings.insert(0, header)

    with open("data/executed_daily_training.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_trainings)

    logger.info(f"Executed daily training with ID {training_id} deleted successfully")
    return {"message": "Executed daily training deleted successfully"}