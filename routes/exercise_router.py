import csv
from datetime import date
import os
import zipfile
from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, func, select
from log.logger_config import get_logger
from models.exercise import Exercise
from dtos.exercise_request import exercise_request
from utils.level_exercise import level_exercise
import xml.etree.ElementTree as ET
import hashlib
from db.database import engine

logger = get_logger("exercise_logger", "log/exercise.log")

exercise_router = APIRouter(tags=["exercise"])

@exercise_router.get("/exercise/get_by_id/{exercise_id}")
def get_by_id(exercise_id: int):
    with Session(engine) as session:
        statament = select(Exercise).where(Exercise.id == exercise_id)
        result = session.exec(statament).first()
        if result is not None:
            return result
        else:
            logger.warning(f"Exercise with ID {exercise_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

@exercise_router.get("/exercise/get_all")
def get_all():
    with Session(engine) as session:
        statement = select(Exercise)
        exercises = session.exec(statement).all()
        if not exercises:
            logger.warning("No exercises found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No exercises found")

        logger.info(f"Successfully fetched {len(exercises)} exercises")
        return exercises
   
@exercise_router.get("/exercise/filter")
def filter_exercises(target_muscle_group: str=None, equipment: str = None, level: level_exercise = None):      

    with Session(engine) as session:
        conditions = []
        if target_muscle_group:
            conditions.append(func.lower(Exercise.target_muscle_group) == target_muscle_group.lower())
        if equipment:
            conditions.append(func.lower(Exercise.equipment) == equipment.lower())
        if level:
            conditions.append(Exercise.level == level)

        statement = select(Exercise)
        if conditions:
            statement = statement.where(*conditions)

        result = session.exec(statement).all()
        if not result:
            logger.warning("No exercises found matching the criteria")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No exercises found matching the criteria")

        logger.info(f"Successfully fetched {len(result)} exercises")
        return result
  
@exercise_router.get("/exercise/get_quantity")
def get_quantity():
    with Session(engine) as session:
        quantity = session.exec(select(func.count(Exercise.id))).one()
    logger.info(f"Successfully fetched the total number of users: {quantity}")
    return {"quantity": quantity}

@exercise_router.post("/exercise/create")
def create(exercise_request: exercise_request):

    new_exercise = Exercise(
            name=exercise_request.name,
            target_muscle_group=exercise_request.target_muscle_group,
            equipment=exercise_request.equipment,
            level=level_exercise(exercise_request.level),
            url=exercise_request.url,
            sets=exercise_request.sets,
            reps=exercise_request.reps,
            weight=exercise_request.weight
        )
    
    with Session(engine) as session:
        session.add(new_exercise)
        session.commit()
        session.refresh(new_exercise)

    logger.info(f"Exercise {new_exercise.name} created successfully with ID {new_exercise.id}")
    return {"message": "Exercise created successfully", "id": new_exercise.id}

@exercise_router.put("/exercise/update/{exercise_id}")
def update(exercise_id: int, exerciseDto: exercise_request):

    with Session(engine) as session:
        statement = select(Exercise).where(Exercise.id == exercise_id)
        exercise = session.exec(statement).first()

        if exercise is None:
            logger.warning(f"Exercise with ID {exercise_id} not found for update")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

        exercise.name = exerciseDto.name
        exercise.target_muscle_group = exerciseDto.target_muscle_group
        exercise.equipment = exerciseDto.equipment
        exercise.level = level_exercise(exerciseDto.level)
        exercise.url = exerciseDto.url
        exercise.sets = exerciseDto.sets
        exercise.reps = exerciseDto.reps
        exercise.weight = exerciseDto.weight

        session.commit()
        session.refresh(exercise)
    
    logger.info(f"Exercise with ID {exercise_id} updated successfully")
    return {"message": "Exercise updated successfully"}

@exercise_router.delete("/exercise/delete/{exercise_id}")
def delete_exercise(exercise_id: int):
    with Session(engine) as session:
        statement = select(Exercise).where(Exercise.id == exercise_id)
        exercise = session.exec(statement).first()

        if exercise is None:
            logger.warning(f"Exercise with ID {exercise_id} not found for deletion")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

        session.delete(exercise)
        session.commit()

    logger.info(f"Exercise with ID {exercise_id} deleted successfully")
    return {"message": "Exercise deleted successfully"}

#==========================================================================================================

# @exercise_router.get("/exercise/download_zip", tags=["exercise"])
# def download_zip():
#     try: 
#         with zipfile.ZipFile("data_zip/exercise.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
#             zipf.write("data/exercise.csv", os.path.basename("data/exercise.csv"))  
        
#         hash_sha256 = get_hash_csv()
#         return FileResponse(
#                     path="data_zip/exercise.zip",
#                     media_type='application/zip',
#                     filename='exercise.zip',
#                     headers={"X-CSV-Hash": str(hash_sha256)}
#                 )

#     except Exception as e:
#         logger.error(f"An error occurred while creating the ZIP file: {e}")
#         raise HTTPException(status_code=500, detail="Error creating ZIP file")

# @exercise_router.get("/exercise/download_xml", tags=["exercise"])
# def download_xml():
#     Headers = ["id", "name", "target_muscle_group", "equipment",
#         "level", "url", "sets", "reps", "weight"]
    
#     try:
#         with open("data/exercise.csv", newline='', encoding='utf-8') as csvfile:
#             reader = csv.DictReader(csvfile, fieldnames=Headers)
#             root = ET.Element("exercises")
#             for row in reader:
#                 item = ET.SubElement(root, "exercise")
#                 for key, value in row.items():
#                     field = ET.SubElement(item, key)
#                     field.text = value
#             indent(root)  # Aplica indentação personalizada
#             tree = ET.ElementTree(root)
#             tree.write("data_xml/exercise.xml", encoding='utf-8', xml_declaration=True)

#         logger.info("exercise.xml created successfully")
#         return FileResponse("data_xml/exercise.xml", media_type='application/xml', filename='exercise.xml')
#     except Exception as e:
#         logger.error(f"An error occurred while creating the XML file: {e}")
#         raise HTTPException(status_code=500, detail="Error creating XML file")


# @exercise_router.get("/exercise/hash", tags=["exercise"])
# def get_hash_csv():
#     try: 
#         with open("data/exercise.csv", 'rb') as f:
#             file_data = f.read()
#             sha256_hash = hashlib.sha256(file_data).hexdigest()
#             logger.info("SHA256 hash of exercise.csv generated successfully")
#             return {"hash": str(sha256_hash)}
#     except Exception as e:
#         logger.error(f"An error occurred while generating the hash: {e}")
#         raise HTTPException(status_code=500, detail=f"Error generating hash: {e}")