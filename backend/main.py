import shutil
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from database import db_manager
from agent import data_agent

app = FastAPI(title="Autonomous Data Analyst API")

class AnalysisRequest(BaseModel):
    prompt: str

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Saves uploaded CSV file and creates a DuckDB table."""
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        table_name = db_manager.load_csv(temp_file_path)
        os.remove(temp_file_path)
        return {"status": "success", "message": f"Table '{table_name}' initialized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_data(request: AnalysisRequest):
    """Executes the LangGraph agent flow based on natural language input."""
    try:
        initial_state = {"user_query": request.prompt}
        result = data_agent.invoke(initial_state)
        return {
            "sql": result["generated_sql"],
            "results": result["query_results"],
            "summary": result["executive_summary"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))