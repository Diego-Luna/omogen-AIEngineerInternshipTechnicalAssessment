import os
import json
from litellm import acompletion

# Configuration
# For Docker on Mac, we must use 'host.docker.internal' to reach your machine's Ollama
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://host.docker.internal:11434")

# LiteLLM requires the prefix "ollama/" for local models
MODEL_NAME = os.getenv("AI_MODEL", "ollama/qwen2.5-coder:14b") 

async def get_llm_response(prompt: str, json_mode: bool = False) -> dict | str:
    try:
        messages = [{"role": "user", "content": prompt}]
        
        # Call LiteLLM asynchronously
        response = await acompletion(
            model=MODEL_NAME,
            messages=messages,
            api_base=OLLAMA_API_BASE,
            format="json" if json_mode else None, 
            temperature=0.1
        )

        content = response.choices[0].message.content

        if json_mode:
            # Parse the string content into a real Python dictionary
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                print(f"JSON Decode Error. Raw content: {content}")
                return {}
        
        return content

    except Exception as e:
        print(f"Error calling LiteLLM: {e}")
        return {} if json_mode else "Error generating response"

async def extract_cv_data_ai(text: str) -> dict:
    """ 
    Extract skills, experience, etc. in JSON format using Qwen.
    """
    prompt = f"""
    You are an expert HR AI. Extract information from the following CV text into JSON format.
    You MUST output ONLY valid JSON. Do not add markdown blocks like ```json.
    
    Keys required: 
    - "skills" (list of strings)
    - "years_experience" (number)
    - "location" (string)
    - "education" (string)
    - "certifications" (list of strings)
    
    CV TEXT:
    {text[:4000]} 
    """
    return await get_llm_response(prompt, json_mode=True)

async def match_cv_job(cv_data: dict, job_description: str) -> dict:
    """ 
    Compare the structured resume with the job offer and give it a score.
    """
    prompt = f"""
    Compare this Candidate Data with the Job Description.
    You MUST output ONLY valid JSON.
    
    CANDIDATE DATA: 
    {json.dumps(cv_data)}
    
    JOB DESCRIPTION: 
    {job_description[:3000]}
    
    Return a JSON with these exact keys:
    - "match_status": "Match" or "No Match"
    - "overall_score": number 0-100
    - "explanation": string reason (max 2 sentences)
    - "criteria_scores": {{ "skills": 0-100, "experience": 0-100, "location": 0-100 }}
    """
    return await get_llm_response(prompt, json_mode=True)