from datetime import date, datetime
import math
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path, Response
from fastapi.responses import FileResponse
from sqlmodel import Session, func, select
from models.executed_daily_training import ExecutedDailyTraining
from models.executed_exercise import ExecutedExercise
from dtos.executed_daily_training_request import executed_daily_training_request
from dtos.executed_exercise_dto import executed_exercise_dto
from dtos.executed_daily_training_response import executed_daily_training_response 
from models.executed_daily_training import ExecutedDailyTraining
from log.logger_config import get_logger
from db.database import engine
from models.exercise import Exercise
from models.user import User
from utils.pagination import PaginatedResponse, PaginationParams

logger = get_logger("daily_training_logger", "log/daily_training.log")

daily_training_router = APIRouter(tags=["Executed daily training"])

@daily_training_router.get("/daily_training/get_by_id/{user_id}")
def get_by_id(training_id: int):
    with Session(engine) as session:
        statement = select(ExecutedDailyTraining).where(ExecutedDailyTraining.id == training_id)
        result = session.exec(statement).first()
        if not result:
            logger.warning(f"Executed daily training with ID {training_id} not found")
            raise HTTPException(status_code=404, detail="Executed daily training not found")
        
        # Carrega os exercícios associados
        executed_exercises = session.exec(
            select(ExecutedExercise).where(ExecutedExercise.daily_training_id == result.id)
        ).all()
        
        training = executed_daily_training_response(
            id=result.id,
            user_id=result.user_id,
            training_date=result.training_date,
            total_duration=result.total_duration,
            notes = result.notes,
            exercises=[
                executed_exercise_dto(
                    id_exercise=ex.id_exercise,
                    sets_done=ex.sets_done,
                    reps_done=ex.reps_done,
                    weight_used=ex.weight_used
                ) for ex in executed_exercises
            ]
        )
        
        logger.info(f"Successfully fetched executed daily training with ID {training_id}")
        return training


@daily_training_router.get("/daily_training/get_all")
def get_all(pagination: PaginationParams = Depends()):
    with Session(engine) as session:

        offset = (pagination.page-1) * pagination.per_page 
        statement = select(ExecutedDailyTraining).offset(offset).limit(pagination.per_page)
        result = session.exec(statement).all()
        
        if not result:
            logger.warning("No executed daily trainings found")
            raise HTTPException(status_code=404, detail="Executed daily trainings not found")
        
        trainings = []

        for t in result:
            # Carrega os exercícios associados para cada treino
            executed_exercises = session.exec(
                select(ExecutedExercise).where(ExecutedExercise.daily_training_id == t.id)
            ).all()

            training = executed_daily_training_response(
                id=t.id,
                user_id=t.user_id,
                training_date=t.training_date,
                total_duration=t.total_duration,
                notes = t.notes,
                exercises=[
                    executed_exercise_dto(
                        id_exercise=ex.id_exercise,
                        sets_done=ex.sets_done,
                        reps_done=ex.reps_done,
                        weight_used=ex.weight_used
                    ) for ex in executed_exercises
                ]
            )
            trainings.append(training)

        total = session.exec(select(func.count(ExecutedDailyTraining.id))).one()

        logger.info(f"Successfully fetched {len(trainings)} executed daily trainings")
        return PaginatedResponse(
            items=trainings,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages= math.ceil((total) / pagination.per_page)
        )

@daily_training_router.get("/edaily_trainingxercise/filter")
def filter_daily_training(user_id: int = None, training_date: str = None, pagination: PaginationParams = Depends()):

   with Session(engine) as session:  

        #validando a data        
        try:
            if training_date:
                datetime.strptime(training_date, '%Y-%m-%d').date()
        except ValueError:
            logger.error(f"Invalid date format: {training_date}")
            raise HTTPException(
                status_code=404,
                detail="Formato de data inválido. Use YYYY-MM-DD"
            )  

        conditions = []
        if user_id:
            conditions.append(user_id == ExecutedDailyTraining.user_id)
        if training_date:
            conditions.append(training_date == ExecutedDailyTraining.training_date)
       
        offset = (pagination.page-1) * pagination.per_page 
        statement = select(ExecutedDailyTraining).offset(offset).limit(pagination.per_page)
        
         # Pegando o total de registros com tais condições
        count_stmt = select(func.count(ExecutedDailyTraining.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = session.exec(count_stmt).one()

        # Aplicando condições de filtro e executando
        if conditions:
            statement = statement.where(*conditions)
        result = session.exec(statement).all()
        
        if not result:
            logger.warning("No executed daily trainings found with the given criteria")
            raise HTTPException(status_code=404, detail="No executed daily trainings found with the given criteria")
        
        #transformando para os dtos de response
        trainings = []
        for t in result:
            # Carrega os exercícios associados para cada daily training
            executed_exercises = session.exec(
                select(ExecutedExercise).where(ExecutedExercise.daily_training_id == t.id)
            ).all()

            training = executed_daily_training_response(
                id=t.id,
                user_id=t.user_id,
                training_date=t.training_date,
                total_duration=t.total_duration,
                notes = t.notes,
                exercises=[
                    executed_exercise_dto(
                        id_exercise=ex.id_exercise,
                        sets_done=ex.sets_done,
                        reps_done=ex.reps_done,
                        weight_used=ex.weight_used
                    ) for ex in executed_exercises
                ]
            )
            trainings.append(training)

        logger.info(f"Successfully fetched {len(trainings)} executed daily trainings")
        return PaginatedResponse(
            items=result,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages= math.ceil((total) / pagination.per_page)
        )

@daily_training_router.get("/daily_training/get_quantity")
def get_quantity():
    with Session(engine) as session:
        quantity = session.exec(select(func.count(ExecutedDailyTraining.id))).one()
    logger.info(f"Successfully fetched the total number of Executed Daily Trainings: {quantity}")
    return {"quantity": quantity}

@daily_training_router.post("/daily_training/create")
def create(executed_training: executed_daily_training_request):
  
    with Session(engine) as session:
        user = session.get(User, executed_training.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verificando se todos os exercise_id existem
        exercise_ids = [ex.id_exercise for ex in executed_training.exercises]
        existing_ids = session.exec(select(Exercise.id).where(Exercise.id.in_(exercise_ids))).all()

        not_found = set(exercise_ids) - set(existing_ids)
        if not_found:
            raise HTTPException(
                status_code=400,
                detail=f"Exercises not found with IDs: {list(not_found)}"
            )
        
   

    dailyTraining = ExecutedDailyTraining(
        user_id=executed_training.user_id,
        training_date=executed_training.training_date,
        total_duration=executed_training.total_duration,
        notes = executed_training.notes,   
    )

    with Session(engine) as session:
        # Adicionando o treino executado ao db
        session.add(dailyTraining)
        session.commit()  # Commit para salvar o treino executado
        session.refresh(dailyTraining)  # Necessário para pegar o ID gerado

        exercises = [ExecutedExercise(
            daily_training_id=dailyTraining.id,
            id_exercise=ex.id_exercise,
            sets_done=ex.sets_done,
            reps_done=ex.reps_done,
            weight_used=ex.weight_used
        ) for ex in executed_training.exercises]

        # Adicionanado executed exercises ao db 
        for ex in exercises:
            session.add(ex)
            session.commit()  # Commit para garantir que o ID seja gerado antes de associar ao treino
            session.refresh(ex)  # Necessário para pegar o ID gerado
        
        logger.info(f"Executed daily training created successfully with ID {dailyTraining.id}")
        return {
            "message": "Executed daily training created successfully",
            "id": dailyTraining.id
        }

@daily_training_router.put("/daily_training/update/{training_id}")
def update(training_id: int, executed_training: executed_daily_training_request):
    with Session(engine) as session:
        statement = select(ExecutedDailyTraining).where(ExecutedDailyTraining.id == training_id)
        result = session.exec(statement).first()

        if not result:
            logger.info("No Executed daily training found with id: {training_id}.")
            raise HTTPException(status_code=400, detail=f"Exercises not found with ID: {training_id}")
        
        # Atualiza os campos do treino diário executado
        result.user_id = executed_training.user_id
        result.training_date = executed_training.training_date
        result.total_duration = executed_training.total_duration
        result.notes = executed_training.notes

        # Remove os exercícios antigos associados a este treino
        old_exercises = session.exec(
            select(ExecutedExercise).where(ExecutedExercise.daily_training_id == training_id)
        ).all()

        for ex in old_exercises:
            session.delete(ex)
        session.commit()

        # Adiciona os novos exercícios
        for ex_req in executed_training.exercises:
            new_ex = ExecutedExercise(
                daily_training_id=training_id,
                id_exercise=ex_req.id_exercise,
                sets_done=ex_req.sets_done,
                reps_done=ex_req.reps_done,
                weight_used=ex_req.weight_used
            )
            session.add(new_ex)
        session.commit()

        logger.info(f"Executed daily training with ID {training_id} updated successfully")
        return {"message": "Executed daily training updated successfully"}
    
@daily_training_router.delete("/daily_training/delete/{training_id}")
def delete(training_id: int):
    with Session(engine) as session:
        statement = select(ExecutedDailyTraining).where(ExecutedDailyTraining.id == training_id)
        result = session.exec(statement).first()

        if not result:
            logger.info("No Executed daily training found with id: {training_id}.")
            raise HTTPException(status_code=400, detail=f"Exercises not found with ID: {training_id}")
        
        old_exercises = session.exec(
            select(ExecutedExercise).where(ExecutedExercise.daily_training_id == training_id)
        ).all()

        for ex in old_exercises:
            session.delete(ex)
        session.commit()

        session.delete(result)
        session.commit()

        logger.info(f"Executed daily training with ID {training_id} deleted successfully")
        return {"message": "Executed daily training deleted successfully"}

#===========================================================================================================

# @daily_training_router.get("/daily_training/download_zip", tags=["executed daily training"])
# def download_zip():
#     try:
#         with zipfile.ZipFile("data_zip/e.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
#             zipf.write("data/executed_daily_training.csv", os.path.basename("data/executed_daily_training.csv"))  
        
#         logger.info("ZIP file created successfully")
#         hash_sha256 = get_hash_csv()
#         return FileResponse(
#                     path="data_zip/executed_daily_training.zip",
#                     media_type='application/zip',
#                     filename='executed_daily_training.zip',
#                     headers={"X-CSV-Hash": str(hash_sha256)}
#                 )
#     except Exception as e:
#         logger.error(f"Error creating ZIP file: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# @daily_training_router.get("/daily_training/download_xml", tags=["executed daily training"])
# def download_xml():
#     try: 
#         root = ET.Element("executed_daily_trainings")
#         with open("data/executed_daily_training.csv", newline='', encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile)
#             next(reader) 
            
#             for row in reader:
#                 training = ET.SubElement(root, "training")
#                 ET.SubElement(training, "id").text = row[0]
#                 ET.SubElement(training, "user_id").text = row[1]
#                 ET.SubElement(training, "training_date").text = row[2]
#                 ET.SubElement(training, "total_duration").text = row[3]
                
#                 exercises = ET.SubElement(training, "exercises")
                
#                 for i in range(4, len(row), 5):
#                     exercise = ET.SubElement(exercises, "exercise")
#                     ET.SubElement(exercise, "exercise_id").text = row[i+1]  # Pula o marcador "EXERCISE"
#                     ET.SubElement(exercise, "sets_done").text = row[i+2]
#                     ET.SubElement(exercise, "reps_done").text = row[i+3]
#                     ET.SubElement(exercise, "weight_used").text = row[i+4]
        
#         indent(root)
        
#         tree = ET.ElementTree(root)
#         tree.write("data_xml/executed_daily_training.xml", encoding='utf-8', xml_declaration=True)

#         logger.info("executed_daily_training.xml created successfully")
#         return FileResponse("data_xml/executed_daily_training.xml", media_type='application/xml', filename='executed_daily_training.xml')
    
#     except Exception as e:
#         logger.error(f"Error creating XML file: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# @daily_training_router.get("/daily_training/hash", tags=["executed daily training"])
# def get_hash_csv():
#     try: 
#         with open("data/executed_daily_training.csv", 'rb') as f:
#             file_data = f.read()
#             sha256_hash = hashlib.sha256(file_data).hexdigest()
#             logger.info("SHA256 hash of executed_daily_training.csv generated successfully")
#             return {"hash": str(sha256_hash)}
#     except Exception as e:
#         logger.error(f"An error occurred while generating the hash: {e}")
#         raise HTTPException(status_code=500, detail=f"Error generating hash: {e}")