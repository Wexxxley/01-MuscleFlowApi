from fastapi import FastAPI
from routes.training_sheet_router import training_sheet_router
from routes.executed_daily_training_router import daily_training_router
from routes.exercise_router import exercise_router
from routes.user_router import user_router 
from routes.physical_record_router import physical_record_router
from db.database import create_db_and_tables

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

#Registra o router na aplicação
app.include_router(user_router)
app.include_router(exercise_router)
app.include_router(daily_training_router)
app.include_router(training_sheet_router)
app.include_router(physical_record_router)

