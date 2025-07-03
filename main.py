from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes.routes import register_routes
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from app.db import get_db
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.features.subscription.api.routes import router as subscription_router
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #TESTING CASE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/templates/subscription/static"), name="static")
templates = Jinja2Templates(directory="app/templates/subscription")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

register_routes(app)

@app.get("/")
async def root():
    return {"message": "Asset Management Backend, Beta Version"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    return {"status": "healthy"}
