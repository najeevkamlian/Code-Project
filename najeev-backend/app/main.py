from fastapi import FastAPI
from app.controllers import router

app = FastAPI(title='Najeev Notes API', version='1.0.0')
app.include_router(router)
