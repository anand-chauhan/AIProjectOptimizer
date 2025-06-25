# Entry pointfrom fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import audit, auth, mood, dashboard, role_routes, tasks

load_dotenv()
app = FastAPI()

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# Middleware for sessions
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# Routers
app.include_router(auth.router)
app.include_router(mood.router)
app.include_router(dashboard.router)
app.include_router(role_routes.router)
app.include_router(audit.router)
app.include_router(tasks.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
 