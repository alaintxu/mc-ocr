from PIL import Image
import os

CARD_HEIGHT = 1039
CARD_WIDTH = 750


def cut_image(image_path: str, turn: bool = False):
    input_folder = os.path.dirname(image_path)
    output_folder = input_folder.replace("/uncut/", "/cut/")
    output2_folder = input_folder.replace("/uncut/", "/not_processed/")
    input_file_name = os.path.basename(image_path).split(".")[0]
    input_image = Image.open(image_path)
    image_width, image_height = input_image.size

    # Crop input image in multiple 744x1039 pixels images
    h = 0
    while h < image_height:
        w = 0
        while w < image_width:
            # Create output paths
            output_path = f"{output_folder}/{input_file_name}_{w//CARD_WIDTH+1}x{h//CARD_HEIGHT+1}.jpg"
            output2_path = f"{output2_folder}/{input_file_name}_{w//CARD_WIDTH+1}x{h//CARD_HEIGHT+1}.jpg"

            # Crop image
            output_image = input_image.crop((w, h, w + CARD_WIDTH, h + CARD_HEIGHT))

            # Rotate image if needed
            if turn:
                output_image = output_image.rotate(90, expand=True)

            # Create folder if not exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            os.makedirs(os.path.dirname(output2_path), exist_ok=True)

            # Save images
            output_image.save(output_path)
            output_image.save(output2_path)

            # Delete if they are all black (smaller than 50KB)
            if os.path.getsize(output_path) < 50000:
                os.remove(output_path)
                os.remove(output2_path)

            w += CARD_WIDTH
        h += CARD_HEIGHT
