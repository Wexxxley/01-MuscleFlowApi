from datetime import date

class user:
    id: int
    name: str
    objective: str 
    height: float
    weight: float 
    registration_date: date

    def __init__(self, id, name, objective, height, weight, registration_date):
        self.id = id
        self.name = name
        self.objective = objective # Poderia ter um enum aqui.
        self.height = height
        self.weight = weight #PROVISOÓRIO. A ideia é ter um classe Registro Físico.
        self.registration_date = registration_date