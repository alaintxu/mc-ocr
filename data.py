import json
import re

def get_texts_to_compare(cards_json):
    texts_to_compare = {}
    for card in cards_json:
        texts_to_compare[card['code']] = add_card_data_to_compare(card)
        if "linked_card" in card.keys():
            linked_card = card["linked_card"]
            texts_to_compare[linked_card['code']] = add_card_data_to_compare(linked_card)
    return texts_to_compare


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


with open('jsons/cards.json') as f:
    json_data = json.load(f)
    data = get_texts_to_compare(json_data)
