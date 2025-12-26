from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from database import init_db, get_session
from models import CV, Job
from utils import extract_text_from_pdf, anonymize_text
from ai_service import extract_cv_data_ai, match_cv_job

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting system...")
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Endpoint 1: Markdown/Text 
# @app.post("/jobs/upload/")
# async def upload_job(
#     title: str = Form(...),
#     file: UploadFile = File(...),
#     session: AsyncSession = Depends(get_session)
# ):
#     content = await file.read()
#     # We assume it is text or markdown (decode bytes to string)
#     text_content = content.decode("utf-8")
    
#     new_job = Job(title=title, description_text=text_content)
#     session.add(new_job)
#     await session.commit()
#     return {"id": new_job.id, "title": new_job.title}

#  Endpoint 2: match
@app.post("/match")
async def match_cv_and_job(
    cv: UploadFile = File(...),
    job_description: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Receive a CV and an Offer. 
    1. Extract text.
    2. Anonymize text (Bias Prevention).
    3. AI Processing.
    4. Store ORIGINAL data.
    """

    cv_bytes = await cv.read()
    cv_text = extract_text_from_pdf(cv_bytes)
    
    # ! --- BIAS PREVENTION LAYER ---
    anonymized_cv_text = anonymize_text(cv_text)
    
    # Process Text/MD
    job_bytes = await job_description.read()
    job_text = job_bytes.decode("utf-8")
    
    # * AI: Extract CV data (USING ANONYMIZED TEXT)

    extracted_data = await extract_cv_data_ai(anonymized_cv_text)
    
    # * AI: Matching (USING ANONYMIZED DATA)
    match_result = await match_cv_job(extracted_data, job_text)
    
    # * Persistence (Save to database)
    new_cv = CV(
        candidate_name=cv.filename,
        text_content=cv_text,
        extracted_data=extracted_data,
        is_processed=True
    )
    session.add(new_cv)
    
    # We keep Job
    new_job = Job(title=job_description.filename, description_text=job_text)
    session.add(new_job)
    
    await session.commit()
    
    return match_result