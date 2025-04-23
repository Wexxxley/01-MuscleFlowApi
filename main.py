from fastapi import FastAPI
from routes.exercise_router import exercise_router
from routes.user_router import user_router  # Importa o router

app = FastAPI()

# Registra o router na aplicação
app.include_router(user_router)
app.include_router(exercise_router)

