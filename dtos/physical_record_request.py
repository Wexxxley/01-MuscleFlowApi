from pydantic import BaseModel

class PhysicalRecordRequest(BaseModel):
    user_id: int
    weight: float
    height: float
    body_fat_percentage: float
    muscle_mass_percentage: float

        