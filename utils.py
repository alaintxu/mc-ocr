import os
from PIL import Image
from fuzzywuzzy import fuzz
import json
import pytesseract
from fastapi import WebSocket
from data import data, cards, clean_text


def json_message(message):
    return json.dumps({"type": "message", "message": message})


def json_result(input_image, result_code, result_score, text):
    return json.dumps({
        "type": "result",
        "input_image": input_image,
        "result_code": result_code,
        "result_score": result_score,
        "text": text,
        "already_exists": os.path.isfile(f"./images/accepted/{result_code}.webp")
    })


def json_uncut_images(images):
    return json.dumps({
        "type": "uncut_images",
        "images": images,
    })

def process_image_text(image):
    # Extract text from image
    text = pytesseract.image_to_string(image, lang="spa")

    # Clean and process the text
    processed_text = clean_text(text.lower())

    similarity_scores = {}

    # Match with card id
    for card_code, text_to_compare in data.items():
        similarity_score = fuzz.token_set_ratio(text_to_compare, processed_text)
        similarity_scores[card_code] = similarity_score

    return processed_text, similarity_scores


async def process_images(websocket: WebSocket):
    await websocket.send_text(json_message("Processing images..."))
    directory = "./images/not_processed"
    #image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    image_files = get_not_processed_images(directory)
    num_images = len(image_files)
    for image_file in image_files:
        action = await proces_image(image_file, websocket, directory)

        await websocket.send_text(json_message(f"Image processed {action['text']}. {num_images} images left."))
        num_images -= 1
    await websocket.send_text(json_message("Processing finished..."))


def get_not_processed_images(directory):
    image_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            image_files.append(os.path.join(root, file))
    return image_files


async def proces_image(image_file, websocket: WebSocket, directory):
    file_name = os.path.basename(image_file)
    #image = Image.open(os.path.join(directory, image_file))
    image = Image.open(image_file)
    processed_text, similarity_scores = process_image_text(image)

    sorted_similarity_scores = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

    best_match_code = sorted_similarity_scores[0][0]
    action = {
        "text": "starting",
        "degrees": 0
    }
    while action['text'] != 'yes' and action['text'] != 'skip' and len(
            sorted_similarity_scores) > 0:
        best_matching = sorted_similarity_scores.pop(0)
        best_match_code = best_matching[0]
        result_json = json_result(
            image_file,
            best_match_code,
            similarity_scores[best_match_code],
            processed_text
        )
        await websocket.send_text(result_json)

        action_str = await websocket.receive_text()
        action = json.loads(action_str)
        if action['text'] == 'find':
            card_name = action['card_name'].lower()
            for card in cards:
                if card['name'].lower() == card_name:
                    result_json = json_result(
                        image_file,
                        card['code'],
                        100,
                        processed_text
                    )
                    await websocket.send_text(result_json)
                    break

    if action['degrees'] != 0:
        image = image.rotate(action['degrees'], expand=True)
        '''Save rotated image'''
        image.save(image_file)
    if action['text'] == 'yes':
        image_is_card(image, image_file, best_match_code)

    return action


def image_is_card(image: Image, image_file, card_code: str):
    image.save(f"./images/accepted/{card_code}.webp", format="webp")

    '''Move image to processed folder'''
    '''replace /images/not_processed/ with /images/processed/'''
    moved_filename = image_file.replace("/images/not_processed/", "/images/processed/")
    '''Move and create folder if not exists'''
    os.makedirs(os.path.dirname(moved_filename), exist_ok=True)
    os.rename(image_file, moved_filename)


def delete_image(image_path):
    os.remove(image_path)
