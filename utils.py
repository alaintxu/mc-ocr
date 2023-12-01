import os
from PIL import Image
from fuzzywuzzy import fuzz
import re
import json
import pytesseract
from fastapi import WebSocket
from data import data


def json_message(message):
    return json.dumps({"type": "message", "message": message})


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
        text = "starting"
        while text != 'yes' and text != 'skip' and len(sorted_similarity_scores) > 0:
            best_matching = sorted_similarity_scores.pop(0)
            best_match_code = best_matching[0]
            # ToDo: proccess card from the other side!
            # best_match_card = next(card for card in data if card['code'] == best_match_code)
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



def image_is_card(image: Image, card_code: str):
    # ToDo: Turn image if necessary
    file_name = os.path.basename(image.filename)
    extension = file_name.split(".")[-1]

    # ToDo: Convert to webp
    image.save(f"./images/accepted/{card_code}.{extension}")

    '''Move image to processed folder'''
    os.rename(f"./images/not_processed/{file_name}", f"./images/processed/{card_code}.{extension}")


def json_result(input_image, result_code, result_score, text):
    return json.dumps({
        "type": "result",
        "input_image": input_image,
        "result_code": result_code,
        "result_score": result_score,
        "text": text,
        "already_exists": os.path.isfile(f"./images/accepted/{result_code}.jpg")
    }
    )


def clean_text(text):
    # Remove HTML tags
    text = re.sub('<.*?>', ' ', text)

    # Remove non-ASCII characters
    #text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Remove line breaks and special characters, but keep á, é, í, ó, ú, ü, ñ
    text = re.sub(r'\n|\r|\t|[^A-Za-z0-9 áéíóúüñ]+', ' ', text)

    return text


def add_card_data_to_compare(input_card, input_text_to_compare=""):
    keys_to_check = ["name", "flavor", "traits", "text", "scheme_text", "attack_text", "card_set_name", "boost_text"]

    for key in keys_to_check:
        if key in input_card.keys() and input_card[key] is not None:
            input_text_to_compare += " " + clean_text(input_card[key].lower())
    return input_text_to_compare