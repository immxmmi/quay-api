from fastapi import FastAPI, Request
import uvicorn
from fastapi.responses import JSONResponse, HTMLResponse
from check.check import check, render_check_html

app = FastAPI()

@app.get("/check")
def run_check(request: Request):
    result = check()
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return HTMLResponse(content=render_check_html(result))
    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)