from fastapi import FastAPI, Request
import uvicorn
from fastapi.responses import JSONResponse, HTMLResponse
from check.check import check, render_check_html
from reader.yaml_reader import read_yaml_live
from reader.yaml_diff import check_yaml_change
from models.quay_config import QuayConfig
import os
import logging
from pathlib import Path

app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# YAML file path (must be a file)
YAML_FILE_PATH = Path(os.getenv("YAML_FILE_PATH", Path(__file__).parent / "test.yaml"))

# YAML storage path (must be a directory)
YAML_STORAGE_PATH = Path(os.getenv("YAML_STORAGE_PATH", "./storage"))
if not YAML_STORAGE_PATH.exists():
    YAML_STORAGE_PATH.mkdir(parents=True, exist_ok=True)

@app.get("/")
def run_check(request: Request):
    """Performs environment and API health checks."""
    result = check()
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return HTMLResponse(content=render_check_html(result))
    return JSONResponse(content=result)

@app.get("/yaml")
def get_yaml():
    """Reads and validates the configured YAML file."""
    if not YAML_FILE_PATH.exists():
        return JSONResponse(content={"status": "error", "message": f"File '{YAML_FILE_PATH}' does not exist"}, status_code=404)
    try:
        data = read_yaml_live(YAML_FILE_PATH)
        validated = QuayConfig(**data)
        return JSONResponse(content=validated.model_dump())
    except Exception as e:
        logging.error(f"YAML validation failed: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=400)





@app.get("/yaml/check")
def yaml_check():
    """Checks for YAML file changes and returns a diff if detected."""
    if not YAML_FILE_PATH.exists():
        return JSONResponse(content={"status": "error", "message": "YAML file not found"}, status_code=404)
    try:
        result = check_yaml_change(YAML_STORAGE_PATH, YAML_FILE_PATH)
        logging.info(f"YAML check result: {result}")
        return JSONResponse(content=result)
    except Exception as e:
        logging.error(f"YAML check failed: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)