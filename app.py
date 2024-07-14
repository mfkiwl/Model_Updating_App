from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/Nodes")
def get_nodes():
    nodes = load_json('data/nodes.json')
    return JSONResponse(content=nodes)

@app.get("/api/Lines")
def get_lines():
    lines = load_json('data/conectivity.json')
    return JSONResponse(content=lines)

origins = [
    "http://localhost",
    "http://localhost:8888"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8888)