import math
from datetime import date, datetime
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from dtos.user_request import user_request
from models.user import User
from log.logger_config import get_logger
from db.database import engine
from sqlmodel import Session, func, select
from utils.pagination import PaginationParams, PaginatedResponse

logger = get_logger("user_logger", "log/user.log")

user_router = APIRouter(tags=["Users"])

@user_router.get("/user/get_by_id/{user_id}")
def get_by_id(user_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        result = session.exec(statement).first()
        if result is not None:
            logger.info(f"User with ID {user_id} retrieved successfully")
            return result
        else:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@user_router.get("/user/get_all")
def get_all(pagination: PaginationParams = Depends()):
    
    with Session(engine) as session:
        # desvio para a página atual
        offset = (pagination.page-1) * pagination.per_page 
        
        # Consulta paginada
        statement = select(User).offset(offset).limit(pagination.per_page)
        results = session.exec(statement).all()
        
        if not results:
            logger.warning("No users found in the database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found"
            )
        
        # Contagem do total de usuários
        total = session.exec(select(func.count(User.id))).one()
        logger.info(f"Successfully fetched {len(results)} users (page {pagination.page})")
        
        return PaginatedResponse(
            items=results,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages= math.ceil((total) / pagination.per_page)
        )

@user_router.get("/user/filter")
def filter_users(name: str = None, objective: str = None, date_registration: str = None, pagination: PaginationParams = Depends()):
    # validando data
    if date_registration:
        try:
            datetime.strptime(date_registration, '%Y-%m-%d').date()
        except ValueError:
            logger.error(f"Invalid date format: {date_registration}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data inválido. Use YYYY-MM-DD"
            )
     
    with Session(engine) as session:
        # Construindo condições de filtro
        conditions = []
        if name:
            conditions.append(func.lower(User.name) == name.lower())
        if objective:
            conditions.append(func.lower(User.objective) == objective.lower())
        if date_registration:
            conditions.append(User.registration_date == date.fromisoformat(date_registration))

        offset = (pagination.page-1) * pagination.per_page 
        statement = select(User).offset(offset).limit(pagination.per_page)
        
        # Pegando o total de registros com tais condições
        count_stmt = select(func.count(User.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = session.exec(count_stmt).one()

        # Aplicando condições de filtro
        if conditions:
            statement = statement.where(*conditions)
        users = session.exec(statement).all()

        if not users:
            logger.warning("No users found with the given criteria")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found with the given criteria")
        
        # Retornando com paginação
        logger.info(f"Successfully filtered {len(users)} users")
        return PaginatedResponse(
            items=users,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages= math.ceil((total) / pagination.per_page)
        )

@user_router.get("/user/get_quantity")
def get_quantity():
    with Session(engine) as session:
        quantity = session.exec(select(func.count(User.id))).one()
    logger.info(f"Successfully fetched the total number of users: {quantity}")
    return {"quantity": quantity}
    
@user_router.post("/user/create")
def create(userDto: user_request):
    newUser = User( 
        name = userDto.name, 
        objective = userDto.objective, 
        registration_date = date.today()
    ) 
    with Session(engine) as session:
        session.add(newUser)
        session.commit()
        session.refresh(newUser)
    
    logger.info(f"User {newUser.name} created successfully with ID {newUser.id}")
    return {"message": "User created successfully", "id": newUser.id}

@user_router.put("/user/update/{user_id}")
def update(user_id: int, userDto: user_request):
    with Session(engine) as session:
        statament = select(User).where(User.id == user_id)
        user = session.exec(statament).first()

        if user is None:
            logger.warning(f"User with ID {user_id} not found for update")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user.name = userDto.name
        user.objective = userDto.objective

        session.commit()
        session.refresh(user)

    logger.info(f"User with ID {user_id} updated successfully")
    return {"message": "User updated successfully"}

@user_router.delete("/user/delete/{user_id}")
def delete(user_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()

        if user is None:
            logger.warning(f"User with ID {user_id} not found for deletion")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        session.delete(user)
        session.commit()

    logger.info(f"User with ID {user_id} deleted successfully")
    return {"message": "User deleted successfully"}