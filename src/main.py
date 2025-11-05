from fastapi import FastAPI, Request
import uvicorn
from fastapi.responses import JSONResponse, HTMLResponse
from check.check import check, render_check_html
from reader.reader import read_yaml_live
from models.quay_config import QuayConfig
import os

app = FastAPI()

@app.get("/check")
def run_check(request: Request):
    result = check()
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return HTMLResponse(content=render_check_html(result))
    return JSONResponse(content=result)

@app.get("/yaml")
def get_yaml():
    try:
        file_path = os.path.join(os.path.dirname(__file__), "test.yaml")
        if not os.path.exists(file_path):
            return JSONResponse(content={"status": "error", "message": "File './test.yaml' does not exist"}, status_code=404)
        data = read_yaml_live(file_path)
        try:
            validated = QuayConfig(**data)
            return JSONResponse(content=validated.model_dump())
        except Exception as e:
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)