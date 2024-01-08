
def get_images_with_characters(character):
    """
    Returns a list of all the images that contain the character in the filename
    """
    import os
    images = []
    for root, dirs, files in os.walk("./images/accepted"):
        for file in files:
            if character in file:
                images.append(os.path.join(root, file))
    return images


def copy_images_with_characters(characters="a.webp", new_characters=".webp"):
    """
    Get the image, and saves it with a different name
    """
    import shutil
    images = get_images_with_characters(characters)
    for image in images:
        shutil.copy(image, image.replace(characters, new_characters))


if __name__ == "__main__":
    copy_images_with_characters("a.webp", ".webp")

