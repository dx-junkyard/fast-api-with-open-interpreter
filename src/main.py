from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import health_router, interpreter_router, download_router, stable_chat_router, sge_router

origins = ["http://localhost:3000"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router.router)
app.include_router(interpreter_router.router)
app.include_router(download_router.router)
app.include_router(stable_chat_router.router)
app.include_router(sge_router.router)
