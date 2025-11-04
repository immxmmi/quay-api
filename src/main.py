from fastapi import FastAPI
from health.endpoints import router as health_router

app = FastAPI()

# Health routes registrieren
app.include_router(health_router, prefix="/health")

@app.get("/")
def root():
    return {"message": "Welcome to Quay API"}