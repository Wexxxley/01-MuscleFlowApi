import math
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlmodel import Session, func, select
from dtos.exercise.top_executed_exercise_response import TopExecutedExerciseResponse
from log.logger_config import get_logger
from models.executed_exercise import ExecutedExercise
from models.exercise import Exercise
from dtos.exercise.exercise_request import exercise_request
from utils.level_exercise import level_exercise
from db.database import engine
from utils.pagination import PaginatedResponse, PaginationParams

logger = get_logger("exercise_logger", "log/exercise.log")

exercise_router = APIRouter(tags=["Exercise"])

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
def get_all(pagination: PaginationParams = Depends()):
    with Session(engine) as session:

        offset = (pagination.page-1) * pagination.per_page 
        statement = select(Exercise).offset(offset).limit(pagination.per_page)
        exercises = session.exec(statement).all()

        if not exercises:
            logger.warning("No exercises found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No exercises found")

        total = session.exec(select(func.count(Exercise.id))).one()
        logger.info(f"Successfully fetched {len(exercises)} exercises")
        return PaginatedResponse(
            items=exercises,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages= math.ceil((total) / pagination.per_page)
        )

   
@exercise_router.get("/exercise/filter")
def filter_exercises(pagination: PaginationParams = Depends(), target_muscle_group: str=None, equipment: str = None, level: level_exercise = None):      

    with Session(engine) as session:
        # Verificando condições
        conditions = []
        if target_muscle_group:
            conditions.append(func.lower(Exercise.target_muscle_group) == target_muscle_group.lower())
        if equipment:
            conditions.append(func.lower(Exercise.equipment) == equipment.lower())
        if level:
            conditions.append(Exercise.level == level)
        
        offset = (pagination.page-1) * pagination.per_page 
        statement = select(Exercise).offset(offset).limit(pagination.per_page)

        # Pegando o total de registros com tais condições
        count_stmt = select(func.count(Exercise.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = session.exec(count_stmt).one()

        # Aplicando condições de filtro e executando
        if conditions:
            statement = statement.where(*conditions)
        exercises = session.exec(statement).all()

        if not exercises:
            logger.warning("No exercises found matching the criteria")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No exercises found matching the criteria")

        # Retornando com paginação
        logger.info(f"Successfully fetched {len(exercises)} exercises")        
        return PaginatedResponse(
            items=exercises,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages= math.ceil((total) / pagination.per_page)
        )
  
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

@exercise_router.get("/exercise/get_top_executed_exercises")
def get_top_executed_exercises(limit: int = 5):
    with Session(engine) as session:
        statement = (
            select(Exercise, func.count(ExecutedExercise.id).label("execution_count"))
            .join(ExecutedExercise, Exercise.id == ExecutedExercise.id_exercise) 
            .group_by(Exercise.id, Exercise.name) # Agrupa pelo ID e nome do exercício para contar
            .order_by(func.count(ExecutedExercise.id).desc()) # Ordena pela contagem em ordem decrescente
            .limit(limit) # Limita ao número de top exercícios desejado
        )

        results: list[tuple[Exercise, int]] = session.exec(statement).all()
        if not results:
            logger.warning(f"Not found executed exercises")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found executed exercises")


        response_list: list[TopExecutedExerciseResponse] = []
        
        for ex, count in results:
            response_list.append(TopExecutedExerciseResponse(exercise=ex, execution_count=count))

        return response_list
