from PIL import Image
import os


def remove_transparency_and_crop_from_folder(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, f"cropped_{filename}")
            remove_transparency_and_crop(input_file, output_file)


def remove_transparency_and_crop(input_file, output_file):
    img = Image.open(input_file)
    img = img.convert("RGBA")
    bbox = img.getbbox()  # Get bounding box of non-transparent pixels
    if bbox:
        cropped_img = img.crop(bbox)
        cropped_img.save(output_file)


# Example usage:
input_folder = "images/uncut"
output_folder = "images/not_processed"
remove_transparency_and_crop_from_folder(input_folder, output_folder)
