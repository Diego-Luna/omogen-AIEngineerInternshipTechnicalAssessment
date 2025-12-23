from fastapi import FastAPI, Depends, UploadFile, File, HTTPException # <--- AGREGADOS
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from database import init_db, get_session
from models import CV # Ya no necesitamos CVCreate si borramos el endpoint manual
from utils import extract_text_from_pdf

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando sistema y creando tablas...")
    await init_db()
    yield
    print("🛑 Apagando sistema...")

app = FastAPI(title="CV Filtering AI System", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "API is running", "tech": "FastAPI + AsyncPG"}

@app.get("/cvs/", response_model=list[CV])
async def read_cvs(session: AsyncSession = Depends(get_session)):
    """Retrieves a list of all CVs currently stored in the database."""
    result = await session.execute(select(CV))
    cvs = result.scalars().all()
    return cvs

@app.post("/upload/")
async def upload_cv(
    file: UploadFile = File(...), 
    session: AsyncSession = Depends(get_session)
):
    """
    Sube un PDF, extrae el texto y guarda el registro en la BD.
    """
    # 1. Validar que sea PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # 2. Leer el contenido del archivo
    content = await file.read()

    # 3. Extraer texto usando nuestra utilidad
    text = extract_text_from_pdf(content)

    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # 4. Crear el objeto CV en base de datos
    new_cv = CV(
        candidate_name=file.filename, 
        text_content=text,
        extracted_data={} 
    )

    session.add(new_cv)
    await session.commit()
    await session.refresh(new_cv)

    return {
        "id": new_cv.id,
        "filename": new_cv.candidate_name,
        "text_preview": new_cv.text_content[:200] + "..." 
    }