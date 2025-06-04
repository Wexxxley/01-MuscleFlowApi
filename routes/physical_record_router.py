import math
from datetime import datetime
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from dtos.physical_record.physical_record_request import PhysicalRecordRequest
from models.physical_record import PhysicalRecord
from models.user import User
from log.logger_config import get_logger
from db.database import engine
from sqlmodel import Session, func, select
from utils.pagination import PaginationParams, PaginatedResponse

logger = get_logger("physical_record_logger", "log/physical_record.log")

physical_record_router = APIRouter(tags=["Physical Record"])

@physical_record_router.get("/physical_record/get_by_id/{record_id}")
def get_by_id(record_id: int):
    with Session(engine) as session:
        statement = select(PhysicalRecord).where(PhysicalRecord.id == record_id)
        result = session.exec(statement).first()
        if result is None:
            logger.warning(f"Physical record with ID {record_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical record not found")
        
        logger.info(f"Physical record with ID {record_id} retrieved successfully")
        return result
          
        
@physical_record_router.get("/physical_record/get_all/")
def get_all(pagination: PaginationParams = Depends()):
    with Session(engine) as session:

        offset = (pagination.page-1) * pagination.per_page 
        statement = select(PhysicalRecord).offset(offset).limit(pagination.per_page)
        result = session.exec(statement).all()
        
        if result is None:
            logger.warning("No physical records found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No physical records found")
           
        total = session.exec(select(func.count(PhysicalRecord.id))).one()
        logger.info(f"Retrieved {len(result)} physical records successfully")
        return PaginatedResponse(
            items=result,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages= math.ceil((total) / pagination.per_page)
        )
    
@physical_record_router.get("/physical_record/get_by_user_id/{user_id}")
def get_by_user_id(user_id: int):
    with Session(engine) as session:

        statement = select(PhysicalRecord).where(PhysicalRecord.user_id == user_id)
        result = session.exec(statement).all()
        if result is None:
            logger.warning(f"No physical records found for user ID {user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No physical records found for this user")
           
        logger.info(f"Physical records for user ID {user_id} retrieved successfully")
        return result
            
        
@physical_record_router.get("/physical_record/get_quantity")
def get_quantity():
    with Session(engine) as session:
        quantity = session.exec(select(func.count(PhysicalRecord.id))).one()
        logger.info(f"Total physical records in the database: {quantity}")
        return {"quantity": quantity}

@physical_record_router.post("/physical_record/create")
def create(physical_record: PhysicalRecordRequest):

    record = PhysicalRecord(
        user_id=physical_record.user_id,
        weight=physical_record.weight,
        height=physical_record.height,
        body_fat_percentage=physical_record.body_fat_percentage,
        muscle_mass_percentage=physical_record.muscle_mass_percentage,
        recorded_at=datetime.now()
    )

    with Session(engine) as session:
        # verificando se o usuário existe
        user_statement = select(User).where(User.id == record.user_id)
        user = session.exec(user_statement).first()
        if user is None:
            logger.warning(f"User with ID {record.user_id} not found for physical record creation")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        session.add(record)
        session.commit()
        session.refresh(record)
    
    logger.info(f"Physical record created successfully with ID {record.id}")
    return {"message": "Physical record created successfully", "id": record.id}

@physical_record_router.put("/physical_record/update/{record_id}")
def update(record_id: int, physical_record: PhysicalRecordRequest):
    with Session(engine) as session:
        # verificando se o registro físico existe
        statament = select(PhysicalRecord).where(PhysicalRecord.id == record_id)
        record = session.exec(statament).first()
        if record is None:
            logger.warning(f"Physical record with ID {record_id} not found for update")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical record not found")
        
        # verificando se o usuário existe
        user_statement = select(User).where(User.id == physical_record.user_id)
        user = session.exec(user_statement).first()
        if user is None:
            logger.warning(f"User with ID {physical_record.user_id} not found for physical record creation")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # atualizando os campos do registro físico
        record.user_id = physical_record.user_id
        record.weight = physical_record.weight
        record.height = physical_record.height
        record.body_fat_percentage = physical_record.body_fat_percentage
        record.muscle_mass_percentage = physical_record.muscle_mass_percentage
        record.recorded_at = datetime.now()

        session.commit()
        session.refresh(record)

    logger.info(f"Physical record with ID {record_id} updated successfully")
    return {"message": "Physical record updated successfully", "id": record.id}

@physical_record_router.delete("/physical_record/delete/{record_id}")
def delete(record_id: int):
    with Session(engine) as session:
        statement = select(PhysicalRecord).where(PhysicalRecord.id == record_id)
        record = session.exec(statement).first()

        if record is None:
            logger.warning(f"Physical record with ID {record_id} not found for deletion")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical record not found")

        session.delete(record)
        session.commit()
        logger.info(f"Physical record with ID {record_id} deleted successfully")
        return {"message": "Physical record deleted successfully", "id": record_id}
        