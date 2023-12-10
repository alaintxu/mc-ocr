import json
import re
import os

def get_texts_to_compare(cards_json):
    texts_to_compare = {}
    cards_output = {}
    for card in cards_json:
        cards_output[card['code']] = card
        texts_to_compare[card['code']] = add_card_data_to_compare(card)
        if "linked_card" in card.keys():
            linked_card = card["linked_card"]
            cards_output[linked_card['code']] = linked_card
            texts_to_compare[linked_card['code']] = add_card_data_to_compare(linked_card)
    return texts_to_compare, cards_output


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


def get_all_accepted_image_file_names():
    directory = "./images/accepted"
    image_file_names = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.webp'):
                file = file.split(".")[0]
                image_file_names.append(file)
    return image_file_names


def get_all_card_codes_from_image_file_names(image_file_names):
    card_codes = []
    for image_file_name in image_file_names:
        card_codes.append(image_file_name.split(".")[0])
    return card_codes

def get_uncut_image_list():
    directory = "./images/uncut"
    images = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.jpg'):
                image = {
                    "path": os.path.join(root, file),
                    "name": file.split(".")[0],
                }
                images.append(image)
    return images


with open('jsons/cards.json') as f:
    json_data = json.load(f)
    data, cards = get_texts_to_compare(json_data)

accepted_card_codes = get_all_card_codes_from_image_file_names(get_all_accepted_image_file_names())
