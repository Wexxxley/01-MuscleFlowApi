import csv
import xml.etree.ElementTree as ET
from datetime import date, datetime
import os
import zipfile
from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from dtos.user_request import user_request
from models.user import User
from log.logger_config import get_logger
from db.database import engine
import hashlib
from sqlmodel import Session, func, select

logger = get_logger("user_logger", "log/user.log")

user_router = APIRouter(tags=["users"])

@user_router.get("/users/get_by_id/{user_id}")
def get_by_id(user_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        result = session.exec(statement).first()
        if result is not None:
            return result
        else:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@user_router.get("/users/get_all")
def ger_all():
    with Session(engine) as session:
        statement = select(User)
        results = session.exec(statement).all()
        if not results:
            logger.warning("No users found in the database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
        
    logger.info(f"Successfully fetched {len(results)} users")
    return results

@user_router.get("/users/filter")
def filter_users(name: str = None, objective: str = None, date_registration: str = None):
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
        conditions = []
        if name:
            conditions.append(func.lower(User.name) == name.lower())
        if objective:
            conditions.append(func.lower(User.objective) == objective.lower())
        if date_registration:
            conditions.append(User.registration_date == date.fromisoformat(date_registration))

        statement = select(User)
        if conditions:
            statement = statement.where(*conditions)

        users = session.exec(statement).all()

    if not users:
        logger.warning("No users found with the given criteria")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found with the given criteria")
    
    logger.info(f"Successfully filtered {len(users)} users")
    return users

@user_router.get("/users/get_quantity")
def get_quantity():
    with Session(engine) as session:
        quantity = session.exec(select(func.count(User.id))).one()
    logger.info(f"Successfully fetched the total number of users: {quantity}")
    return {"quantity": quantity}
    
@user_router.post("/users/create")
def create(userDto: user_request):
    newUser = User( 
        name = userDto.name, 
        objective = userDto.objective, 
        height = userDto.height, 
        weight = userDto.weight, 
        registration_date = date.today()
    ) 
    with Session(engine) as session:
        session.add(newUser)
        session.commit()
        session.refresh(newUser)
    
    logger.info(f"User {newUser.name} created successfully with ID {newUser.id}")
    return {"message": "User created successfully", "id": newUser.id}

@user_router.put("/users/update/{user_id}")
def update(user_id: int, userDto: user_request):
    with Session(engine) as session:
        statament = select(User).where(User.id == user_id)
        user = session.exec(statament).first()

        if user is None:
            logger.warning(f"User with ID {user_id} not found for update")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user.name = userDto.name
        user.objective = userDto.objective
        user.height = userDto.height
        user.weight = userDto.weight

        session.commit()
        session.refresh(user)

    logger.info(f"User with ID {user_id} updated successfully")
    return {"message": "User updated successfully"}

@user_router.delete("/users/delete/{user_id}", tags=["users"])
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

#==========================================================================================================

# @user_router.get("/users/download_zip")
# def download_zip():
#     with Session(engine) as session:
#         zipf.write("data/users.csv", os.path.basename("data/users.csv")) 
#         hash_sha256 = get_hash_csv()
#         logger.info("users.zip created successfully")
#         return FileResponse(
#             path="data_zip/users.zip",
#             media_type='application/zip',
#             filename='users.zip',
#             headers={"X-CSV-Hash": str(hash_sha256)}  # <-- header como dict de str:str
#         )


# @user_router.get("/users/download_xml", tags=["users"])
# def download_xml():
#     Headers = ["id", "name", "objective", "height", "weight", "registration_date"]
    
#     try:
#         with open("data/users.csv", newline='', encoding='utf-8') as csvfile:
#             reader = csv.DictReader(csvfile, fieldnames=Headers)
#             root = ET.Element("users")
#             for row in reader:
#                 item = ET.SubElement(root, "user")
#                 for key, value in row.items():
#                     field = ET.SubElement(item, key)
#                     field.text = value
#             indent(root)  # Aplica indentação personalizada
#             tree = ET.ElementTree(root)
#             tree.write("data_xml/users.xml", encoding='utf-8', xml_declaration=True)
#             logger.info("users.xml created successfully")

#         return FileResponse("data_xml/users.xml", media_type='application/xml', filename='users.xml')
    
#     except Exception as e:
#         logger.error(f"An error occurred while creating the XML file: {e}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating XML file: {e}")


# @user_router.get("/users/hash", tags=["users"])
# def get_hash_csv():
#     try: 
#         with open("data/users.csv", 'rb') as f:
#             file_data = f.read()
#             sha256_hash = hashlib.sha256(file_data).hexdigest()
#             logger.info("SHA256 hash of users.csv generated successfully")
#             return {"hash": str(sha256_hash)}
#     except Exception as e:
#         logger.error(f"An error occurred while generating the hash: {e}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating hash: {e}")
