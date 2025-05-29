from sqlmodel import SQLModel, create_engine
from models import user, exercise, executed_daily_training

DATABASE_URL = "postgresql://postgres:Wfrso2022@localhost:5432/MuscleFlow"
engine = create_engine(DATABASE_URL, echo=True)

target_metadata = SQLModel.metadata

def create_db_and_tables():
    target_metadata.create_all(engine)

