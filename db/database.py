from sqlmodel import SQLModel, create_engine

from models.physical_record import PhysicalRecord
from models.executed_daily_training import ExecutedDailyTraining
from models.user import User
from models.exercise import Exercise 
from models.executed_exercise import ExecutedExercise
from models.training_sheet_day import TrainingSheetDay
from models.models_links import TrainingSheetDayExerciseLink
from models.training_sheet_week import TrainingSheetWeek
from models.models_links import TrainingSheetWeekUserLink

DATABASE_URL = "postgresql://postgres:Wfrso2022@localhost:5432/MuscleFlow"

engine = create_engine(DATABASE_URL, echo=True)

target_metadata = SQLModel.metadata

def create_db_and_tables():
    target_metadata.create_all(engine)

