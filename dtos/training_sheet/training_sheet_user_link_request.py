from sqlmodel import SQLModel, Field
from typing import Optional

class TrainingSheetUserLinkRequest(SQLModel):
    user_id: int 
    training_sheet_week_id: int 