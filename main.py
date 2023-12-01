import json
import os
from functools import reduce
# import pandas as pd

import pytesseract
from PIL import Image
from fuzzywuzzy import fuzz
import re
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse, HTMLResponse

with open('jsons/cards_all_2023-11-28.json') as f:
    data = json.load(f)

app = FastAPI()


@app.get("/")
async def index():
    """return HTMLResponse with index.html"""
    return FileResponse("index.html")


@app.get("/images/not_processed/{image_name}")
async def get_image(image_name):
    """return image"""
    return FileResponse(f"./images/not_processed/{image_name}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await process_images(websocket)
    await websocket.send_text(json_message("WS finished"))
    # while True:
    #     data = await websocket.receive_text()
    #     print(data)
    #     await websocket.send_text(f"Message text was: {data}")


async def process_images(websocket: WebSocket):
    await websocket.send_text(json_message("Processing images..."))
    directory = "./images/not_processed"
    image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    num_images = len(image_files)
    for image_file in image_files:
        file_name = os.path.basename(image_file)
        image = Image.open(os.path.join(directory, image_file))
        processed_text, similarity_scores, text_to_compare_list = process_image_file(image)

        sorted_similarity_scores = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

        best_match_code = sorted_similarity_scores[0][0]
        #best_match_card = next(card for card in data if card['code'] == best_match_code)
        text = "starting"
        while text != 'yes' and text != 'skip' and len(sorted_similarity_scores) > 0:
            best_matching = sorted_similarity_scores.pop(0)
            best_match_code = best_matching[0]
            result_json = json_result(
                file_name,
                best_match_code,
                similarity_scores[best_match_code],
                processed_text
            )
            await websocket.send_text(result_json)

            text = await websocket.receive_text()

        if text == 'yes':
            image_is_card(image, best_match_code)

        await websocket.send_text(json_message(f"Image processed {text}. {num_images} images left."))
        num_images -= 1
    await websocket.send_text(json_message("Processing finished..."))


def json_message(message):
    return json.dumps({"type": "message", "message": message})


def image_is_card(image, card_code):
    '''Copy image to processed folder and name it as card code'''
    extension = image.format.lower()
    image.save(f"./images/processed/{card_code}.{extension}")


def json_result(input_image, result_code, result_score, text):
    return json.dumps({
        "type": "result",
        "input_image": input_image,
        "result_code": result_code,
        "result_score": result_score,
        "text": text}
    )


def clean_text(text):
    # Remove HTML tags
    text = re.sub('<.*?>', ' ', text)

    # Remove non-ASCII characters
    #text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Remove line breaks and special characters, but keep á, é, í, ó, ú, ü, ñ
    text = re.sub(r'\n|\r|\t|[^A-Za-z0-9 áéíóúüñ]+', ' ', text)

    return text


def process_image_file(image):
    # Extract text from image
    text = pytesseract.image_to_string(image, lang="spa")

    # Clean and process the text
    processed_text = clean_text(text.lower())

    similarity_scores = {}
    text_to_compare_list = {}

    # Match with card id
    for card in data:
        text_to_compare = add_card_data_to_compare(card)
        if "linked_card" in card.keys():
            text_to_compare = add_card_data_to_compare(card["linked_card"], text_to_compare)

        similarity_score = fuzz.token_set_ratio(text_to_compare, processed_text)
        text_to_compare_list[card['code']] = text_to_compare
        similarity_scores[card['code']] = similarity_score

    return processed_text, similarity_scores, text_to_compare_list


def add_card_data_to_compare(input_card, input_text_to_compare=""):
    keys_to_check = ["name", "flavor", "traits", "text", "scheme_text", "attack_text", "card_set_name", "boost_text"]

    for key in keys_to_check:
        if key in input_card.keys() and input_card[key] is not None:
            input_text_to_compare += " " + clean_text(input_card[key].lower())
    return input_text_to_compare
