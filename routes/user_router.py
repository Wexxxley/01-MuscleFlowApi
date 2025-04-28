import csv
import xml.etree.ElementTree as ET
from datetime import date, datetime
import os
import zipfile
from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from dtos.user_request_dto import user_request_dto
from entities.user import user
from utils.auxiliares import find_new_id_user, indent
from log.user_logger import logger

user_router = APIRouter()

@user_router.get("/users/get_by_id/{user_id}", tags=["users"], status_code=status.HTTP_200_OK)
def get_by_id(user_id: int):
    with open("data/users.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if int(row[0]) == user_id:
                returned_user = user(
                    int(row[0]), 
                    row[1], 
                    row[2], 
                    float(row[3]), 
                    float(row[4]), 
                    date.fromisoformat(row[5])
                )
                logger.info(f"User with ID {user_id} found")
                return returned_user
        
        logger.warning(f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        

@user_router.get("/users/get_all", tags=["users"], status_code=status.HTTP_200_OK)
def ger_all():
    try:
        with open("data/users.csv", newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            users = []
            for row in reader:
                user_instance = user(
                    int(row[0]), 
                    row[1], 
                    row[2], 
                    float(row[3]), 
                    float(row[4]), 
                    date.fromisoformat(row[5])
                )
                users.append(user_instance)
        logger.info(f"Successfully fetched {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"An error occurred while fetching users: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching users")

@user_router.get("/users/filter", tags=["users"], status_code=status.HTTP_200_OK)
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

    def matches(row) -> bool:
        return (
            (not name or row[1].lower() == name.lower()) and
            (not objective or row[2].lower() == objective.lower()) and
            (not date_registration or row[5].lower() == date_registration.lower())
        )
     
    with open("data/users.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        users = list(reader)

        returned_users = [
            user(
                int(row[0]), 
                row[1], 
                row[2], 
                float(row[3]), 
                float(row[4]), 
                date.fromisoformat(row[5])
            ) for row in users if matches(row)
        ]

    if not returned_users:
        logger.warning("No users found with the given criteria")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found with the given criteria")
    
    logger.info(f"Successfully filtered {len(returned_users)} users")
    return returned_users

@user_router.get("/users/get_quantity", tags=["users"])
def get_quantity():
    try:
        logger.info("Fetching the total number of users from 'data/users.csv'")
        with open("data/users.csv", newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            users = list(reader)
        logger.info(f"Successfully fetched the total number of users: {len(users)}")
        return {"quantity": len(users)}
    except Exception as e:
        logger.error(f"An error occurred while fetching the total number of users: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching user quantity")

@user_router.get("/users/download_zip", tags=["users"])
def download_zip():
    try: 
        with zipfile.ZipFile("data_zip/users.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write("data/users.csv", os.path.basename("data/users.csv"))  
            logger.info("users.zip created successfully")
            return FileResponse("data_zip/users.zip", media_type='application/zip', filename='users.zip')
    except Exception as e:
        logger.error(f"An error occurred while creating the zip file: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating zip file: {e}")

@user_router.get("/users/download_xml", tags=["users"])
def download_xml():
    Headers = [
        "id", "name", "objective", "height", "weight", "registration_date"
    ]
    
    try:
        with open("data/users.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=Headers)
            root = ET.Element("users")
            for row in reader:
                item = ET.SubElement(root, "user")
                for key, value in row.items():
                    field = ET.SubElement(item, key)
                    field.text = value
            indent(root)  # Aplica indentação personalizada
            tree = ET.ElementTree(root)
            tree.write("data_xml/users.xml", encoding='utf-8', xml_declaration=True)
            logger.info("users.xml created successfully")

        return FileResponse("data_xml/users.xml", media_type='application/xml', filename='users.xml')
    except Exception as e:
        logger.error(f"An error occurred while creating the XML file: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating XML file: {e}")
    
@user_router.post("/users/create", tags=["users"])
def create(userDto: user_request_dto):
    new_id = find_new_id_user()
    newUser = user(
        id = new_id, 
        name = userDto.name, 
        objective = userDto.objective, 
        height = userDto.height, 
        weight = userDto.weight, 
        registration_date = date.today()
    ) 
    with open('data/users.csv', mode='a', newline='', encoding='utf-8') as file:
        escritor = csv.writer(file)
        escritor.writerow([newUser.id, newUser.name, newUser.objective, newUser.height, newUser.weight, newUser.registration_date])
    
    logger.info(f"User {newUser.name} created successfully with ID {new_id}")
    return {"message": "Exercise created successfully", "id": new_id}

@user_router.put("/users/update/{user_id}", tags=["users"])
def update(user_id: int, userDto: user_request_dto):
    with open("data/users.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        updated_users = list(reader)  

    user_found = False
    for i, row in enumerate(updated_users):
        if int(row[0]) == user_id:
            updated_users[i] = [user_id, userDto.name, userDto.objective, userDto.height, userDto.weight, updated_users[i][5]]
            user_found = True
            break

    if user_found == False:
        logger.warning(f"User with ID {user_id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    with open("data/users.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_users)

    logger.info(f"User with ID {user_id} updated successfully")
    return {"message": "User updated successfully"}

@user_router.delete("/users/delete/{user_id}", tags=["users"])
def delete(user_id: int):
    with open("data/users.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        users = list(reader)  

    user_found = False
    updated_users = []

    for row in users:
        if int(row[0]) == int(user_id):
            user_found = True
            continue 

        updated_users.append(row)
    
    if user_found == False:
        logger.warning(f"User with ID {user_id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    with open("data/users.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_users)

    logger.info(f"User with ID {user_id} deleted successfully")
    return {"message": "User deleted successfully"}