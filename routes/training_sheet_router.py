import math
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from dtos.training_sheet_day_responde import TrainingSheetDayResponse
from dtos.training_sheet_week_request import TrainingSheetWeekRequest
from dtos.training_sheet_week_response import TrainingSheetWeekResponse
from models.exercise import Exercise
from models.models_links import TrainingSheetDayExerciseLink
from models.training_sheet_day import TrainingSheetDay
from log.logger_config import get_logger
from db.database import engine
from sqlmodel import Session, and_, func, select
from models.training_sheet_week import TrainingSheetWeek
from utils.level_exercise import level_exercise
from utils.pagination import PaginationParams, PaginatedResponse

logger = get_logger("training_sheet_logger", "log/training_sheet.log")

training_sheet_router = APIRouter(tags=["Training Sheet"])

@training_sheet_router.get("/training_sheet/get/{training_sheet_id}")
def get(training_sheet_id: int):
    with Session(engine) as session:
        # Verifica se o TrainingSheetWeek existe e obtém o objeto
        statement = select(TrainingSheetWeek).where(TrainingSheetWeek.id == training_sheet_id)
        training_sheet_week = session.exec(statement).first()

        if not training_sheet_week:
            logger.warning(f"Training sheet with ID {training_sheet_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training sheet not found")

        # Obtendo os dias de treino associados
        days_statement = select(TrainingSheetDay).where(TrainingSheetDay.training_sheet_week_id == training_sheet_id)
        training_sheet_days = session.exec(days_statement).all()

        training_sheet_days_response = []

        for day in training_sheet_days:
            # Obtendo os exercícios associados a cada dia
            links_statement = select(TrainingSheetDayExerciseLink.exercise_id).where(
                TrainingSheetDayExerciseLink.training_sheet_day_id == day.id).order_by(TrainingSheetDayExerciseLink.order)
            
            exercise_ids = session.exec(links_statement).all()

            # Criando a resposta para o dia de treino
            training_sheet_day_response = TrainingSheetDayResponse(
                focus_area=day.focus_area,
                day_of_week=day.day_of_week,
                exercises_ids=exercise_ids
            )
            training_sheet_days_response.append(training_sheet_day_response)

        training_sheet_week_response = TrainingSheetWeekResponse(
            id=training_sheet_week.id,
            name=training_sheet_week.name,
            description=training_sheet_week.description,
            level=training_sheet_week.level,
            training_sheet_days=training_sheet_days_response
        )

        logger.info(f"Training sheet retrieved: {training_sheet_week.id} - {training_sheet_week.name}")
        return training_sheet_week_response
     
        
@training_sheet_router.get("/training_sheet/get_all/")
def get_all(pagination: PaginationParams = Depends()):
    with Session(engine) as session:

        offset = (pagination.page-1) * pagination.per_page 
        statement = select(TrainingSheetWeek).offset(offset).limit(pagination.per_page)

        training_sheet_weeks = session.exec(statement).all()

        if not training_sheet_weeks:
            logger.warning("No training sheets found in the database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No training sheets found")

        training_sheet_weeks_response = []
        for training_sheet_week in training_sheet_weeks:
            # Obtendo os dias de treino associados
            days_statement = select(TrainingSheetDay).where(TrainingSheetDay.training_sheet_week_id == training_sheet_week.id)
            training_sheet_days = session.exec(days_statement).all()

            training_sheet_days_response = []

            for day in training_sheet_days:
                # Obtendo os exercícios associados a cada dia
                links_statement = select(TrainingSheetDayExerciseLink.exercise_id).where(
                    TrainingSheetDayExerciseLink.training_sheet_day_id == day.id).order_by(TrainingSheetDayExerciseLink.order)
                
                exercise_ids = session.exec(links_statement).all()

                # Criando a resposta para o dia de treino
                training_sheet_day_response = TrainingSheetDayResponse(
                    focus_area=day.focus_area,
                    day_of_week=day.day_of_week,
                    exercises_ids=exercise_ids
                )
                training_sheet_days_response.append(training_sheet_day_response)

            training_sheet_week_response = TrainingSheetWeekResponse(
                id=training_sheet_week.id,
                name=training_sheet_week.name,
                description=training_sheet_week.description,
                level=training_sheet_week.level,
                training_sheet_days=training_sheet_days_response
            )

            training_sheet_weeks_response.append(training_sheet_week_response)

        total = session.exec(select(func.count(TrainingSheetWeek.id))).one()
        logger.info(f"Training sheet retrieved: {training_sheet_week.id} - {training_sheet_week.name}")
        return PaginatedResponse(
            items=training_sheet_weeks_response,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages= math.ceil((total) / pagination.per_page)
        )

@training_sheet_router.get("/training_sheet/filter/")
def filter(level: level_exercise = None, keywords: str = None, pagination: PaginationParams = Depends()):
    with Session(engine) as session:

        conditions = []

        if level:
            conditions.append(TrainingSheetWeek.level == level)

        if keywords:
            search_keywords_lower = keywords.lower() # Converte as palavras-chave para minúsculas uma vez
            conditions.append(
                (func.lower(TrainingSheetWeek.name).contains(search_keywords_lower)) |
                (func.lower(TrainingSheetWeek.description).contains(search_keywords_lower))
            )

        offset = (pagination.page-1) * pagination.per_page 
        statement = select(TrainingSheetWeek).offset(offset).limit(pagination.per_page)
        
        # Pegando o total de registros com tais condições
        count_stmt = select(func.count(TrainingSheetWeek.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = session.exec(count_stmt).one()

        # Aplicando condições de filtro
        if conditions:
            statement = statement.where(*conditions)
        training_sheet_weeks = session.exec(statement).all()

        if not training_sheet_weeks:
            logger.warning("No training sheets found in the database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No training sheets found")

        training_sheet_weeks_response = []
        for training_sheet_week in training_sheet_weeks:
            # Obtendo os dias de treino associados
            days_statement = select(TrainingSheetDay).where(TrainingSheetDay.training_sheet_week_id == training_sheet_week.id)
            training_sheet_days = session.exec(days_statement).all()

            training_sheet_days_response = []

            for day in training_sheet_days:
                # Obtendo os exercícios associados a cada dia
                links_statement = select(TrainingSheetDayExerciseLink.exercise_id).where(
                    TrainingSheetDayExerciseLink.training_sheet_day_id == day.id).order_by(TrainingSheetDayExerciseLink.order)
                
                exercise_ids = session.exec(links_statement).all()

                # Criando a resposta para o dia de treino
                training_sheet_day_response = TrainingSheetDayResponse(
                    focus_area=day.focus_area,
                    day_of_week=day.day_of_week,
                    exercises_ids=exercise_ids
                )
                training_sheet_days_response.append(training_sheet_day_response)

            training_sheet_week_response = TrainingSheetWeekResponse(
                id=training_sheet_week.id,
                name=training_sheet_week.name,
                description=training_sheet_week.description,
                level=training_sheet_week.level,
                training_sheet_days=training_sheet_days_response
            )

            training_sheet_weeks_response.append(training_sheet_week_response)

        logger.info(f"Training sheet retrieved: {training_sheet_week.id} - {training_sheet_week.name}")
        return PaginatedResponse(
            items=training_sheet_weeks_response,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages= math.ceil((total) / pagination.per_page)
        )  


@training_sheet_router.get("/training_sheet/get_quantity")
def get_quantity():
    with Session(engine) as session:
        quantity = session.exec(select(func.count(TrainingSheetWeek.id))).one()
    logger.info(f"Successfully fetched the total number of Training Sheet: {quantity}")
    return {"quantity": quantity}
    

@training_sheet_router.post("/training_sheet/create")
def create(training_sheet_week_request: TrainingSheetWeekRequest):
    with Session(engine) as session:

        # Verificando se todos os exercise_ids existem
        ids_exercises = []

        for day in training_sheet_week_request.training_sheet_days:
            for ex_id in day.exercises_ids:
                ids_exercises.append(ex_id)

        existing_ids = session.exec(select(Exercise.id).where(Exercise.id.in_(ids_exercises))).all()

        not_found = set(ids_exercises) - set(existing_ids)
        
        if not_found:
            raise HTTPException(
                status_code=400,
                detail=f"Exercises not found with IDs: {list(not_found)}"
            )
        
        # Recuperando os exercícios de todos os dias
        exercises = session.exec(select(Exercise).where(Exercise.id.in_(existing_ids))).all()
        
        # Criando o TrainingSheetWeek
        trainingSheetWeek = TrainingSheetWeek(
            name=training_sheet_week_request.name,
            description=training_sheet_week_request.description,
            level=training_sheet_week_request.level,
        )
        session.add(trainingSheetWeek)
        session.commit()
        session.refresh(trainingSheetWeek)

        # Criando os TrainingSheetDays
        for day_request in training_sheet_week_request.training_sheet_days:
            trainingSheetDay = TrainingSheetDay(
                focus_area=day_request.focus_area,
                day_of_week=day_request.day_of_week,
                training_sheet_week_id=trainingSheetWeek.id # Linka ao ID da semana
            )
            session.add(trainingSheetDay)
            session.commit()
            session.refresh(trainingSheetDay) # Garante que o ID do dia foi populado

            # Criar os links entre exercicos e TrainingSheetDay
            for i, ex_id in enumerate(day_request.exercises_ids):
                link = TrainingSheetDayExerciseLink (
                    training_sheet_day_id=trainingSheetDay.id,
                    exercise_id=ex_id,
                    order = i+1 
                )
                session.add(link)
            
            session.commit() # Commit para os links de cada dia
            session.refresh(trainingSheetDay)

        logger.info(f"Training sheet created: {trainingSheetWeek.id} - {trainingSheetWeek.name}")
        return {"message": "Training sheet created successfully", "id": trainingSheetWeek.id}

@training_sheet_router.put("/training_sheet/update/{training_sheet_id}", status_code=status.HTTP_200_OK) # Adicione o status_code
def update(training_sheet_id: int, training_sheet_week_request: TrainingSheetWeekRequest,):
    
    with Session(engine) as session:
        # 1. Verifica se o TrainingSheetWeek existe
        training_sheet_week = session.get(TrainingSheetWeek, training_sheet_id)
        if not training_sheet_week:
            logger.warning(f"Training sheet with ID {training_sheet_id} not found for update")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training sheet not found")

        # 2. Atualiza os campos principais do TrainingSheetWeek
        training_sheet_week.name = training_sheet_week_request.name
        training_sheet_week.description = training_sheet_week_request.description
        training_sheet_week.level = training_sheet_week_request.level

        # 3. Deleta os dias de treino associados (automaticamente remove os links devido à relação de cascata)
        existing_day = session.exec(select(TrainingSheetDay).where(TrainingSheetDay.training_sheet_week_id == training_sheet_id)).all()
        for day in existing_day:
            session.delete(day)

        session.commit()  # Commit para deletar os dias antigos
        
   
        # Criando os TrainingSheetDays
        for day_request in training_sheet_week_request.training_sheet_days:
            trainingSheetDay = TrainingSheetDay(
                focus_area=day_request.focus_area,
                day_of_week=day_request.day_of_week,
                training_sheet_week_id=training_sheet_week.id # Linka ao ID da semana
            )
            session.add(trainingSheetDay)
            session.commit()
            session.refresh(trainingSheetDay) # Garante que o ID do dia foi populado

            # Criar os links entre exercicos e TrainingSheetDay
            for i, ex_id in enumerate(day_request.exercises_ids):
                link = TrainingSheetDayExerciseLink (
                    training_sheet_day_id=trainingSheetDay.id,
                    exercise_id=ex_id,
                    order = i+1 
                )
                session.add(link)
            
            session.commit() # Commit para os links de cada dia
            session.refresh(trainingSheetDay)

        logger.info(f"Training sheet with ID {training_sheet_id} updated successfully")
        return {"message": "Training sheet updated successfully", "id": training_sheet_week.id}


@training_sheet_router.delete("/training_sheet/delete/{training_sheet_id}")
def delete(training_sheet_id: int):
    with Session(engine) as session:

        # Verifica se o TrainingSheetWeek existe e obtém o objeto
        statement = select(TrainingSheetWeek).where(TrainingSheetWeek.id == training_sheet_id)
        training_sheet_week = session.exec(statement).first()

        if not training_sheet_week:
            logger.warning(f"Training sheet with ID {training_sheet_id} not found for deletion")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training sheet not found")
        
        # Deleta os dias de treino associados (automaticamente remove os links devido à relação de cascata)
        session.delete(training_sheet_week)
        session.commit()

        logger.info(f"Training sheet with ID {training_sheet_id} deleted successfully")
        return {"message": "Training sheet deleted successfully"}