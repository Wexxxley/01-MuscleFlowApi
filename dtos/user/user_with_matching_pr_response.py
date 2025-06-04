from pydantic import ConfigDict
from sqlmodel import SQLModel
from models.physical_record import PhysicalRecord
from models.user import User



class UserWithMatchingPhysicalRecord(SQLModel):
    user: User 
    physical_record: PhysicalRecord 
    model_config = ConfigDict(from_attributes=True) 
