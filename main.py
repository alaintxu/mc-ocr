import json
import os
from functools import reduce
import pandas as pd

import pytesseract
from PIL import Image
from fuzzywuzzy import fuzz
import re


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


def process_images_and_save_to_excel(image_files, data):
    similarity_scores = {}
    text_to_compare_list = {}
    # Create an empty list to store the data for each image
    data_list = []

    for file_path in image_files:
        file_name = os.path.basename(file_path)
        image = Image.open(os.path.join(directory, file_name))

        # Get the top 10 matches for the image
        top_match_codes, top_match_cards, similarity_scores, text_to_compare_list = get_top_matches(image, data, num_matches=10)

        # For each match, create a dictionary and append it to the list
        for match_code, match_card in zip(top_match_codes, top_match_cards):
            data_dict = {
                'Image Name': file_name,
                'Card Code': match_code,
                'Similarity Score': similarity_scores[match_code],
                'Text to Compare': text_to_compare_list[match_code]
            }
            data_list.append(data_dict)

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data_list)

    # Write the DataFrame to an Excel file
    df.to_excel('image_matches.xlsx', index=False)


def get_top_matches(image, data, num_matches=10):
    similarity_scores, text_to_compare_list = process_image_file(image)

    # Sort the similarity scores in descending order and get the top num_matches
    top_match_codes = sorted(similarity_scores, key=similarity_scores.get, reverse=True)[:num_matches]

    # Find the cards corresponding to the top num_matches match codes
    top_match_cards = [next(card for card in data if card['code'] == match_code) for match_code in top_match_codes]

    return top_match_codes, top_match_cards, similarity_scores, text_to_compare_list


if __name__ == "__main__":
    # Load JSON data
    with open('jsons/cards_all_2023-11-28.json') as f:
        data = json.load(f)


    def add_card_data_to_compare(input_card, input_text_to_compare=""):
        keys_to_check = ["name", "flavor", "traits", "text", "scheme_text", "attack_text", "card_set_name", "boost_text"]

        for key in keys_to_check:
            if key in input_card.keys() and input_card[key] is not None:
                input_text_to_compare += " " + clean_text(input_card[key].lower())
        return input_text_to_compare


    directory = "./images"
    image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    #process_images_and_save_to_excel(image_files, data)
    for file_path in image_files:
        file_name = os.path.basename(file_path)
        image = Image.open(os.path.join(directory, file_name))

        processed_text, similarity_scores, text_to_compare_list = process_image_file(image)

        # top_match_codes, top_match_cards = get_top_matches(image, data, num_matches=3)
        best_match_code = max(similarity_scores, key=similarity_scores.get)
        best_match_card = next(card for card in data if card['code'] == best_match_code)

        print(f"\n---------------------------------------------\n{file_name}\n")
        print(f"Best match: {best_match_code}\nScore: {similarity_scores[best_match_code]}\n")
        print(f"Text from image:\n{processed_text}\n")
        print(f"Compared with:\n{text_to_compare_list[best_match_card['code']]}")
        # if "name" in best_match_card.keys():
        #     print(f"Name: {best_match_card['name']}")
        # if "text" in best_match_card.keys():
        #     print(f"Text: {best_match_card['text']}")
        # if "flavor" in best_match_card.keys():
        #     print(f"Flavor: {best_match_card['flavor']}")
