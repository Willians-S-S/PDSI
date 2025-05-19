from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from predpeso.routes.user_router import user_router
from predpeso.routes.farm_router import farm_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir requisições do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(farm_router)
