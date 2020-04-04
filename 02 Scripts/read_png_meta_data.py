import dotenv # Get enironmental variables from .env file
import os # Use dotenv to load environmental variables

import piexif # Core module, read/write metadata
from PIL import Image # Open images

#import logging # Used to keep track of program progress

class load_env_variables():
    def __init__(self):
        self.test_image_path = os.getenv("TEST_IMAGE_PATH")

def return_all_exif(image_object):
    if type(image_object) == "":
        pass
    else # TODO change to logging
        raise TypeError(f"ERROR[return_all_exif]: Passed object is of type |{type(image_object)}| it should be of type ||")

if __name__ == "__main__":
    print("starting...")
    settings = load_env_variables()
    image_object = Image.open(settings.test_image_path)
    exif_dictionary = piexif.load(image_object)
    print(typ(image_object))
    print(exif_dictionary)

