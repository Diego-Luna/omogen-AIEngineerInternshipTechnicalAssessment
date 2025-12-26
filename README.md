CV Filtering System - Technical Interview Challenge

## Overview

Build an automated CV filtering system that extracts information from resumes and matches them with job offers using Large Language Models (LLMs).

## Project Structure

- Backend/: API and core logic
	- [Backend/ai_service.py](Backend/ai_service.py) : LLM integration and JSON extraction/matching helpers
	- [Backend/main.py](Backend/main.py) : FastAPI app and endpoints (`/jobs/upload/` and `/match`)
	- [Backend/models.py](Backend/models.py) : SQLModel DB models
	- [Backend/database.py](Backend/database.py) : DB init and session helpers
	- [Backend/utils.py](Backend/utils.py) : PDF/text extraction utilities
- docker-compose.yml : Docker services (db + api)
- requirements.txt : Python dependencies

## Objective

Create a system that can:
- Extract key information from CVs (skills, experience, location, education, certifications)
- Match candidates with job positions based on defined criteria
- Provide scoring and explanations for each match

## How to run locally

Start services with:

```bash
docker-compose up --build
```

This starts Postgres and the API service on port 8000.

API documentation and interactive testing is available at:

http://localhost:8000/docs

Environment variables
- See .env.example for variables: `DATABASE_URL`, `OLLAMA_API_BASE`, `AI_MODEL`.

## API Endpoints

- POST /jobs/upload/ - Upload a job description (form fields: `title`, `file`)
- POST /match - Multipart form: `cv` (PDF) and `job_description` (MD/TXT). Returns matching JSON with `match_status`, `overall_score`, `criteria_scores` and `explanation`.

Example `curl` for `/match`:

## Notes & Recommendations

- The project implements the core pipeline: PDF text extraction → LLM-based extraction → LLM matching → persistence (Postgres).
- Configure `OLLAMA_API_BASE` and `AI_MODEL` in `.env` when using local models (the code defaults to `http://host.docker.internal:11434` and a `ollama/` model prefix).
