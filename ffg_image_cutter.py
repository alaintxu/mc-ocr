from PIL import Image
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_jpg_to_png(input_folder, output_folder):
    logger.info(f"Removing transparency and cropping images from {input_folder} to {output_folder}")
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(input_folder, filename.replace(".jpg", ".png"))
            if not os.path.exists(output_file):
                try:
                    img = Image.open(input_file)
                    img.save(output_file, "PNG")
                    logger.info(f"Converted {filename} to PNG")
                except Exception as e:
                    logger.error(f"Error converting {filename}: {e}")
            

def remove_transparency_and_crop_from_folder(input_folder, output_folder):
    logger.info(f"Removing transparency and cropping images from {input_folder} to {output_folder}")
    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, f"cropped_{filename}")
            remove_transparency_and_crop(input_file, output_file)


def remove_transparency_and_crop(input_file, output_file):
    logger.info(f"Removing transparency and cropping {input_file} to {output_file}")
    img = Image.open(input_file)
    img = img.convert("RGBA")
    bbox = img.getbbox()  # Get bounding box of non-transparent pixels
    if bbox:
        cropped_img = img.crop(bbox)
        cropped_img.save(output_file)

def cut_in_nine_all(input_folder, output_folder):
    logger.info(f"Cutting all images in {input_folder} in nine parts")
    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):
            input_file = os.path.join(input_folder, filename)
            cut_in_nine_parts(input_file, output_folder)

def cut_in_nine_parts(input_file, output_folder):
    logger.info(f"Cutting {input_file} in nine parts")
    img = Image.open(input_file)
    width, height = img.size
    card_width = width // 3
    card_height = height // 3
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    for i in range(3):
        for j in range(3):
            x0 = max(i * card_width, 0)
            y0 = max(j * card_height, 0)
            x1 = min((i + 1) * card_width, width)
            y1 = min((j + 1) * card_height, height)
            cropped_img = img.crop((x0, y0, x1, y1))
            cropped_img.save(f"{output_folder}/{base_name}_{i}_{j}.png")


if __name__ == "__main__":
    input_folder = "images/uncut"
    output_folder = "images/not_processed"
    #convert_jpg_to_png(input_folder, output_folder)
    #cut_in_nine_all("images/uncut", "images/not_processed")
    remove_transparency_and_crop_from_folder(input_folder, output_folder)
