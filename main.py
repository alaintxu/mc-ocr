from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from utils import process_images, json_message
from data import data

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")


@app.get("/")
async def index():
    """return HTMLResponse with index.html"""
    return FileResponse("index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await process_images(websocket)
    await websocket.send_text(json_message("WS finished"))
