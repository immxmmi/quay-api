from fastapi import FastAPI, Form, HTTPException
import uvicorn
from reader.reader import read_yaml_live
from fastapi.responses import HTMLResponse, JSONResponse
from services.organization_service import OrganizationService

app = FastAPI()

org_service = OrganizationService()

@app.get("/")
def read_root():
    return {"message": "Hello World"}


# New endpoint to return the entire YAML configuration
@app.get("/config")
def get_config():
    """Returns the entire YAML configuration content."""
    config = read_yaml_live("src/test.yaml")
    return config

@app.get("/organization")
def show_organization_form():
    html_content = """
    <html>
        <head><title>Create Organization</title></head>
        <body style='font-family: Arial; margin: 40px;'>
            <h2>Create a New Organization</h2>
            <form action="/organization" method="post">
                <label for="name">Organization Name:</label><br>
                <input type="text" id="name" name="name" required><br><br>
                <label for="email">Email Address:</label><br>
                <input type="email" id="email" name="email" required><br><br>
                <button type="submit">Submit</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/organization")
async def create_organization(name: str = Form(...), email: str = Form(...)):
    try:
        org_service.create_organization(name, email)
        return HTMLResponse(f"<h3>Organization '{name}' created successfully!</h3><br><a href='/organization'>Back</a>", status_code=200)
    except Exception as e:
        return HTMLResponse(f"<h3>Error creating organization: {str(e)}</h3>", status_code=500)

@app.get("/organization/file")
async def show_yaml_creation_form():
    html_content = """
    <html>
        <head><title>Bulk Create Organizations</title></head>
        <body style='font-family: Arial; margin: 40px;'>
            <h2>Create Organizations from YAML</h2>
            <form action="/organization/file" method="post">
                <label for="path">YAML File Path:</label><br>
                <input type="text" id="path" name="path" value="src/test.yaml" required><br><br>
                <button type="submit">Create from File</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/organization/file")
async def create_organizations_from_yaml(path: str = Form("src/test.yaml")):
    """Reads organizations from YAML and creates them all."""
    try:
        yaml_data = read_yaml_live(path)
        organizations = yaml_data.get("organizations", [])
        if not organizations:
            return HTMLResponse("<h3>No organizations found in YAML.</h3><br><a href='/organization/file'>Back</a>", status_code=400)
        
        results = org_service.create_organizations_from_list(organizations)
        result_html = "<h3>Bulk creation completed.</h3><ul>"
        for r in results:
            status = "✅" if r["status"] == "created" else "❌"
            result_html += f"<li>{status} {r['name']} - {r['status']}</li>"
        result_html += "</ul><br><a href='/organization/file'>Back</a>"
        return HTMLResponse(result_html, status_code=200)
    except Exception as e:
        return HTMLResponse(f"<h3>Error: {str(e)}</h3><br><a href='/organization/file'>Back</a>", status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)