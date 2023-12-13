from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from image_cutter import cut_image
from utils import process_images, json_message, json_uncut_images, delete_image
from data import data, cards, accepted_card_codes, get_uncut_image_list
import json

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")


@app.get("/")
async def index():
    """return HTMLResponse with index.html"""
    return FileResponse("index.html")


@app.get("/status")
async def status():
    """return the HTML for the app status"""
    return FileResponse("status.html")


def add_accepted_to_card(card):
    card['accepted'] = card["code"] in accepted_card_codes
    return card


@app.get("/status/data")
async def status_data():
    """Get all filenames of the images in /images/accepted"""
    my_cards = [cards[key] for key in cards.keys()]
    cards_are_accepted = list(map(add_accepted_to_card, my_cards))
    return { "data": cards_are_accepted }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await process_images(websocket)
    await websocket.send_text(json_message("WS finished"))


@app.get("/cut")
async def cut():
    """return the HTML for the cut functionality"""
    return FileResponse("cut.html")


@app.websocket("/cut-ws")
async def websocket_cut_endpoint(websocket: WebSocket):
    await websocket.accept()
    uncut_images = get_uncut_image_list()
    await websocket.send_text(json_uncut_images(uncut_images))
    
    action_str = await websocket.receive_text()
    print(f"ActionStr: {action_str}")
    while action_str != "finished":
        action = json.loads(action_str)
        if action["type"] == "cut":
            cut_image(action["image"]["path"], False)
            await websocket.send_text(json_message(f"Image {action['image']['path']} cut"))
        if action["type"] == "cut_and_turn":
            await websocket.send_text(json_message(f"Cutting and turning not implemented yet"))
            cut_image(action["image"]["path"], True)
            await websocket.send_text(json_message(f"Image {action['image']['path']} cut and turned"))
        if action["type"] == "delete":
            delete_image(action["image"]["path"])
            await websocket.send_text(json_uncut_images(uncut_images))
        action_str = await websocket.receive_text()
    await websocket.send_text(json_message("WS finished"))
    
