import csv
from datetime import date
import os
import zipfile
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse
from entities.exercise import exercise
from dtos.exercise_request_dto import exercise_request_dto
from log.exercise_logger import logger
from utils.auxiliares import find_new_id_exercise, indent, get_all_valid_exercise_ids
from utils.level_exercise import level_exercise
import xml.etree.ElementTree as ET
import hashlib

exercise_router = APIRouter()

@exercise_router.get("/exercise/get_by_id/{exercise_id}", tags=["exercise"])
def get_by_id(user_id: int):
    try:
        with open("data/exercise.csv", newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if int(row[0]) == user_id:
                    logger.info(f"Exercise with ID {user_id} found")
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
        logger.warning(f"Exercise with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    except Exception as e:
        logger.error(f"An error occurred while fetching exercise with ID {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@exercise_router.get("/exercise/get_all", tags=["exercise"])
def get_all():
    try:
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
        
        if not exercises:
            logger.warning("No exercises found")
            raise HTTPException(status_code=404, detail="No exercises found")

        logger.info(f"Successfully fetched {len(exercises)} exercises")
        return exercises
    except Exception as e:
        logger.error(f"An error occurred while fetching exercises: {e}")
        raise HTTPException(status_code=500, detail="Error fetching exercises")

@exercise_router.get("/exercise/filter", tags=["exercise"])
def filter_exercises(target_muscle_group: str=None, equipment: str = None, level: str =None):
    if level is not None and level.lower() not in ['beginner', 'intermediate', 'advanced']:
        logger.warning(f"Invalid level: {level}")
        raise HTTPException(status_code=400, detail="Invalid level. Must be 'beginner', 'intermediate', or 'advanced'.")
        
    def matches(row) -> bool:
        return (
            (not target_muscle_group or row[2].lower() == target_muscle_group.lower()) and
            (not equipment or row[3].lower() == equipment.lower()) and
            (not level or row[4].lower() == level.lower())
        )
     
    try:
        with open("data/exercise.csv", newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            exercises = list(reader)

            returned_exercises = [
                exercise(
                    id=int(row[0]), 
                    name=row[1], 
                    target_muscle_group=row[2], 
                    equipment=row[3], 
                    level=row[4], 
                    url=row[5], 
                    sets=int(row[6]), 
                    reps=int(row[7]), 
                    weight=float(row[8])
                ) for row in exercises if matches(row)
            ]

        if not returned_exercises:
            logger.warning("No exercises found matching the criteria")
            raise HTTPException(status_code=404, detail="No exercises found matching the criteria")
      
        logger.info(f"Successfully fetched {len(exercises)} exercises")
        return returned_exercises
        
    except Exception as e:
        logger.error(f"An error occurred while filtering exercises: {e}")
        raise HTTPException(status_code=500, detail="Error filtering exercises")

@exercise_router.get("/exercise/get_quantity", tags=["exercise"])
def get_quantity():
    try:
        with open("data/exercise.csv", newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            exercise = list(reader)  
            
        logger.info(f"Successfully fetched {len(exercise)} exercises")
        return {"quantity": len(exercise)}
    except Exception as e:
        logger.error(f"An error occurred while fetching exercise quantity: {e}")
        raise HTTPException(status_code=500, detail="Error fetching exercise quantity")

@exercise_router.get("/exercise/download_zip", tags=["exercise"])
def download_zip():
    try: 
        with zipfile.ZipFile("data_zip/exercise.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write("data/exercise.csv", os.path.basename("data/exercise.csv"))  
        
        hash_sha256 = get_hash_csv()
        return FileResponse(
                    path="data_zip/exercise.zip",
                    media_type='application/zip',
                    filename='exercise.zip',
                    headers={"X-CSV-Hash": str(hash_sha256)}
                )

    except Exception as e:
        logger.error(f"An error occurred while creating the ZIP file: {e}")
        raise HTTPException(status_code=500, detail="Error creating ZIP file")

@exercise_router.get("/exercise/download_xml", tags=["exercise"])
def download_xml():
    Headers = ["id", "name", "target_muscle_group", "equipment",
        "level", "url", "sets", "reps", "weight"]
    
    try:
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

        logger.info("exercise.xml created successfully")
        return FileResponse("data_xml/exercise.xml", media_type='application/xml', filename='exercise.xml')
    except Exception as e:
        logger.error(f"An error occurred while creating the XML file: {e}")
        raise HTTPException(status_code=500, detail="Error creating XML file")


@exercise_router.get("/exercise/hash", tags=["exercise"])
def get_hash_csv():
    try: 
        with open("data/exercise.csv", 'rb') as f:
            file_data = f.read()
            sha256_hash = hashlib.sha256(file_data).hexdigest()
            logger.info("SHA256 hash of exercise.csv generated successfully")
            return {"hash": str(sha256_hash)}
    except Exception as e:
        logger.error(f"An error occurred while generating the hash: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating hash: {e}")


@exercise_router.post("/exercise/create", tags=["exercise"])
def create(exercise_request: exercise_request_dto):
    try: 
        new_id = find_new_id_exercise()
        new_exercise = exercise(
            id=new_id, 
            name=exercise_request.name, 
            target_muscle_group=exercise_request.target_muscle_group, 
            equipment=exercise_request.equipment, 
            level=exercise_request.level.value, 
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
        
        logger.info(f"Exercise created successfully with ID {new_exercise.id}")
        return {"message": "Exercise created successfully", "id": new_id}
    except Exception as e:
        logger.error(f"An error occurred while creating exercise: {e}")
        raise HTTPException(status_code=500, detail="Error creating exercise")

@exercise_router.put("/exercise/update/{exercise_id}", tags=["exercise"])
def update(exercise_id: int, exerciseDto: exercise_request_dto):
    with open("data/exercise.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        updated_exercise = list(reader)  

    exercise_found = False
    for i, row in enumerate(updated_exercise):
        if int(row[0]) == exercise_id:
            updated_exercise[i] = [exercise_id, exerciseDto.name, exerciseDto.target_muscle_group, exerciseDto.equipment,
                                  exerciseDto.level, exerciseDto.url, exerciseDto.sets, exerciseDto.reps, exerciseDto.weight]
            exercise_found = True
            break
    
    if exercise_found == False:
        logger.warning(f"Exercise with ID {exercise_id} not found")
        raise HTTPException(status_code=404, detail="Exercise not found")

    with open("data/exercise.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_exercise)

    logger.info(f"Exercise with ID {exercise_id} updated successfully")
    return {"message": "exercise updated successfully"}

@exercise_router.delete("/exercise/delete/{exercise_id}", tags=["exercise"])
def delete_exercise(exercise_id: int):
    with open("data/exercise.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        exercises = list(reader)

    exercise_found = False
    updated_exercises = []

    for row in exercises:
        if int(row[0]) == int(exercise_id):
            exercise_found = True
            continue 

        updated_exercises.append(row)
    
    if exercise_found == False:
        logger.warning(f"Exercise with ID {exercise_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Exercise not found")

    with open("data/exercise.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_exercises)

    logger.info(f"Exercise with ID {exercise_id} deleted successfully")
    return {"message": "Exercise deleted successfully"}