from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from pathlib import Path
import sys 
sys.path.append('../')
base_dir = Path(__file__).resolve().parent.parent


templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory=base_dir / "data"), name="data")

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/Nodes")
def get_nodes():
    nodes = load_json(base_dir / 'data/nodes.json')
    return JSONResponse(content=nodes)

@app.get("/api/Lines")
def get_lines():
    lines = load_json(base_dir / 'data/conectivity.json')
    return JSONResponse(content=lines)

@app.get("/api/Mesh")
def get_lines():
    mesh = load_json(base_dir / 'data/mesh_shells.json')
    return JSONResponse(content=mesh)

@app.get("/api/Section_assign")
def get_sections_id():
    sections = load_json(base_dir / 'data/sections_assignation.json')
    return JSONResponse(content=sections)

@app.get("/api/Sections")
def get_sections_geometry():
    sections = load_json(base_dir / 'data/cross_section.json')
    return JSONResponse(content=sections)


@app.get("/api/all_modeshapes")
def get_all_modeshapes():
    modeshapes = load_json(base_dir / 'data/modeshapes.json')
    return JSONResponse(content=modeshapes)

@app.get("/api/modeshape/{mode_shape_num}")
def get_modeshape(mode_shape_num:int):
    modeshapes = load_json(base_dir / 'data/modeshapes.json')
    return JSONResponse(content=modeshapes[f'modeshape_{mode_shape_num}'])

@app.get("/api/magnitude/{mode_shape_num}")
def get_magnitude(mode_shape_num:int):
    modeshapes = load_json(base_dir / 'data/modeshapes.json')
    return JSONResponse(content=modeshapes[f'magnitud_{mode_shape_num}'])



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