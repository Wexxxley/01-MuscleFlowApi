from datetime import date
from pydantic import BaseModel, Field

class user_request_dto(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    objective: str = Field(min_length=1, max_length=50)
    height: float = Field(ge=0.0, le=3.0)
    weight: float = Field(ge=0.0) #PROVISOÓRIO. A ideia é ter um classe Registro Físico.