import os
import hashlib
from PIL import Image
import shutil


uncut_directory = './images/uncut'
tts_directory = "/home/aperez/.local/share/Tabletop Simulator/Mods/Images"


def get_directory_hashed_files(directory):
    hashes = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.jpg'):
                file_path = os.path.join(root, file)
                image_md5 = hashlib.md5(open(file_path,'rb').read()).hexdigest()
                hashes[image_md5] = file_path
    return hashes


def copy_from_tts_to_uncut(hashes, tts_hashes):
    hashes_keys = hashes.keys()
    for tts_hash, tts_file in tts_hashes.items():
        if tts_hash not in hashes_keys:
            copy_if_wider_than(tts_file, uncut_directory)


def copy_if_wider_than(input_file, output_directory):
    image = Image.open(input_file)
    width, height = image.size
    if width > 3000:
        print(f'copy {input_file} to {output_directory}')
        shutil.copy(input_file, output_directory)


if __name__ == '__main__':
    '''calculate hash for all files in a folder and its sub folders'''

    hashes = get_directory_hashed_files(uncut_directory)
    tts_hashes = get_directory_hashed_files(tts_directory)
    copy_from_tts_to_uncut(hashes, tts_hashes)
