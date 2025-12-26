import httpx
import os
import json
from litellm import completion

# To access in Mac, i use “host.docker.internal”.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")
MODEL_NAME = "qwen2.5-coder:14b"

async def get_ollama_response(prompt: str, json_mode: bool = False) -> dict:
    async with httpx.AsyncClient(timeout=60.0) as client: # High timeout in case the CPU is slow
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "format": "json" if json_mode else ""
        }
        try:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return json.loads(data["response"]) if json_mode else data["response"]
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return {}

async def extract_cv_data_ai(text: str) -> dict:
    """ Extract skills, experience, etc. in JSON format """
    prompt = f"""
    You are an expert HR AI. Extract information from the following CV text into JSON format.
    Keys required: "skills" (list), "years_experience" (number), "location" (string), "education" (string), "certifications" (list).
    
    CV TEXT:
    {text[:3000]} 
    """ # We cut to 3000 characters so as not to saturate small contexts.
    return await get_ollama_response(prompt, json_mode=True)

async def match_cv_job(cv_data: dict, job_description: str) -> dict:
    """ Compare the structured resume with the job offer and give it a score """
    prompt = f"""
    Compare this Candidate Data with the Job Description.
    
    CANDIDATE: {json.dumps(cv_data)}
    JOB DESCRIPTION: {job_description[:2000]}
    
    Return a JSON with:
    - "match_status": "Match" or "No Match"
    - "overall_score": number 0-100
    - "explanation": string reason
    - "criteria_scores": {{ "skills": 0-100, "experience": 0-100, "location": 0-100 }}
    """
    return await get_ollama_response(prompt, json_mode=True)