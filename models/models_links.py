from sqlmodel import Field, SQLModel

class TrainingSheetWeekUserLink(SQLModel, table=True):
    training_sheet_week_id: int = Field(default=None, foreign_key="trainingsheetweek.id", primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)

class TrainingSheetDayExerciseLink(SQLModel, table=True):
    training_sheet_day_id: int = Field(default=None, foreign_key="trainingsheetday.id", primary_key=True)
    exercise_id: int = Field(default=None, foreign_key="exercise.id", primary_key=True)
    order: int = Field(default=0)