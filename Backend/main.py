from fastapi import FastAPI, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from database import init_db, get_session
from models import CV, CVCreate

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting system and creating tables...")
    await init_db()
    yield
    print("Stopping system...")

app = FastAPI(title="CV Filtering AI System", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "API is running", "tech": "FastAPI + AsyncPG"}

@app.post("/cvs/", response_model=CV)
async def create_cv(cv: CVCreate, session: AsyncSession = Depends(get_session)):
    """Endpoint to manually create and store a CV. This simulates a CV submission process."""
    new_cv = CV.from_orm(cv)
    session.add(new_cv)
    await session.commit()
    await session.refresh(new_cv)
    return new_cv

@app.get("/cvs/", response_model=list[CV])
async def read_cvs(session: AsyncSession = Depends(get_session)):
    """Retrieves a list of all CVs currently stored in the database."""
    result = await session.execute(select(CV))
    cvs = result.scalars().all()
    return cvs