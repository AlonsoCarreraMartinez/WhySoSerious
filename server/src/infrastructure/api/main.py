from fastapi import FastAPI
from app.routers import users, teams, auth, burnout, channels 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# python -m venv .venv
# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs

app = FastAPI(title="WhySoSerious Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(teams.router)
app.include_router(auth.router)
app.include_router(burnout.router)
app.include_router(channels.router)


frontend_path = os.path.join(os.getcwd(), "..", "frontend", "dist")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f" Frontend mounted from {frontend_path}")
else:
    print("The folder doesn't found, maybe you don't execute 'npm run build'")
