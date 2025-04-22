import csv
from datetime import date
import os
import zipfile
from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from dtos.user_request_dto import user_request_dto
from entities.user import user
from utils.auxiliares import find_new_id_user

user_router = APIRouter()

@user_router.get("/users/get_by_id/{user_id}", tags=["users"])
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
                return returned_user

@user_router.get("/users/get_all", tags=["users"])
def ger_all():
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
    return users

@user_router.get("/users/get_quantity", tags=["users"])
def get_quantity():
    with open("data/users.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        users = list(reader)  
    return {"quantity": len(users)}

@user_router.get("/users/download_zip", tags=["users"])
def download_zip():
    with zipfile.ZipFile("data_zip/users.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("data/users.csv", os.path.basename("data/users.csv"))  
    
    return FileResponse("data_zip/users.zip", media_type='application/zip', filename='users.zip')

@user_router.post("/users/create", tags=["users"])
def create(userDto: user_request_dto):
    newUser = user(
        find_new_id_user(), 
        userDto.name, 
        userDto.objective, 
        userDto.height, 
        userDto.weight, 
        date.today()
    ) 
    with open('data/users.csv', mode='a', newline='', encoding='utf-8') as file:
        escritor = csv.writer(file)
        escritor.writerow([newUser.id, newUser.name, newUser.objective, newUser.height, newUser.weight, newUser.registration_date])

@user_router.delete("/users/delete/{user_id}", tags=["users"])
def delete(user_id: int):
    with open("data/users.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        users = list(reader)  

    updated_users = [row for row in users if (int(row[0]) != user_id)]

    with open("data/users.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_users)

    return {"message": "User deleted successfully"}

@user_router.put("/users/update/{user_id}", tags=["users"])
def update(user_id: int, userDto: user_request_dto):
    with open("data/users.csv", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        updated_users = list(reader)  

    for i, row in enumerate(updated_users):
        if int(row[0]) == user_id:
            updated_users[i] = [user_id, userDto.name, userDto.objective, userDto.height, userDto.weight, updated_users[i][5]]
            break

    with open("data/users.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_users)

    return {"message": "User updated successfully"}