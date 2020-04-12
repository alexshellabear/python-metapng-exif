import piexif # Core module, read/write metadata for jpeg # TODO check if this is needed delete later
#import pyexiv2 # Core module ^^ might replace the one above

from tiff_file_structure import read_tiff_image_file_header_ifh # Custom module to read/write TIFF meta data

import PIL
from PIL import Image, TiffImagePlugin, TiffTags # Open images
from PIL.TiffImagePlugin import ImageFileDirectory_v2
from io import BytesIO

import cv2 # OpenCV library
import numpy as np
import logging # Used to keep track of program progress

import time # TODO delete this later

import dotenv # Get enironmental variables from .env file
import os # Use dotenv to load environmental variables
dotenv.load_dotenv() # initialise .env environmental variables

import random # For random generation
import io # Save png compression to memory

'''
    Note 1: piexif doesn't appear to work for png files.
    Note 2: can't save exif using PIL.Image.save for .tif files. Only works for jpegs
    Note 3: Need lossless image format, can't use piexif for jpegs
    Note 4: py3exiv2 is compiled for linux environment and not for windows, can't use for this project
    Note 5: Pillow has inbuilt module for Exiftags https://hhsprings.bitbucket.io/docs/programming/examples/python/PIL/ExifTags.html
    Note 6: Exif IFD tag = 34665 or 0x8769
    Note 7: UserComment tag = 37510 or 0x9286
    Note 8: Little endians / big endian
        1001 = 4F 52 = 4F 00 (1000) + 52 (1)
        Little Endians: [counter-intuative] Least significant bits stored first. Stores as 52 4F
        Big-Endians: [intuative] Most significant bit stored first. Stores as 4F 52

    https://hhsprings.bitbucket.io/docs/programming/examples/python/PIL/ExifTags.html


    Reverse engineering hex structure for 64 bit system - source https://www.fileformat.info/format/tiff/egff.html
        Contain 3 sections
            1) IFH: Image File Header [required], fixed location first 8 bytes of every TIFF file. x1
            2) IFD: Image File Directory [required] xN
            3) Bitmap: Bitmap data [technically not required] xM such that M < N
        A TIFF file can have multiple IFD~Bitmaps

        IFH Data Structure
        - P

        IFD Tag Data structure


        TAG Structure
        - 70 pre-defined [public] tags given by latest TIFF specification standard
        - Other tags [private] can be changed by developers
        - Each tag has a maximum of 12 bytes otherwise it is too large and must be stored elsewhere
    TODO 1: Rename repo to tiff not png
'''



class load_env_variables():
    def __init__(self):
        self.test_image_path = os.getenv("TEST_IMAGE_PATH")
        self.log_path = os.getenv("LOG_PATH")
        self.temp_jpeg = os.getenv("TEMP_JPEG")
        self.new_test_image_path = os.getenv("TEST_IMAGE_NEW_PATH")
        self.output_cv2_path = os.getenv("TEST_OUTPUT_IMAGE_PATH")
        self.logger_settings()
        
    def logger_settings(self):
        self.logger = logging.getLogger("MetaPNG_Main")
        self.logger.setLevel(logging.DEBUG)
        #file_handler = logging.FileHandler()

def return_all_exif(file_path:str):
    if type(file_path) != str: # TODO make logging
        raise TypeError(f"ERROR[return_all_exif]: Passed object is of type |{type(file_path)}| it should be of type |str|")
    if not os.path.isfile(file_path):
        raise ValueError(f"ERROR[return_all_exif]: |{file_path}| does not exist or is not a file. It should be.")
    valid_file_types = [".tif",".jpeg",".jpg",'.tiff']
    file_extension = os.path.splitext(settings.test_image_path)[1]
    if file_extension not in valid_file_types:
        raise ValueError(f"ERROR[return_all_exif]: |{file_path}| should have a file extension of .tif or .jpeg. It currently doesn't, change this.")

    exif_dictionary = piexif.load(settings.test_image_path)
    return exif_dictionary

def read_exif_user_comments(file_path:str):
    if type(file_path) != str: # TODO make logging
        raise TypeError(f"ERROR[read_exif_user_comments]: Passed object is of type |{type(file_path)}| it should be of type |str|")
    if not os.path.isfile(file_path):
        raise ValueError(f"ERROR[read_exif_user_comments]: |{file_path}| does not exist or is not a file. It should be.")
    valid_file_types = [".tif",".jpeg",".jpeg"]
    file_extension = os.path.splitext(settings.test_image_path)[1]
    if file_extension not in valid_file_types:
        raise ValueError(f"ERROR[read_exif_user_comments]: |{file_path}| should have a file extension of .tif or .jpeg. It currently doesn't, change this.")

    exif_dictionary = piexif.load(settings.test_image_path)
    exif = exif_dictionary["Exif"]

    if len(exif) == 0:
        return None

    user_comments = exif.get(37510,'').decode("UTF-8")
    
    return user_comments

def add_user_comments_to_jpeg(jpeg_file_path:str,user_comments:str):
    # Note 1: Only works for jpeg
    if type(jpeg_file_path) != str: # TODO make logging
        raise TypeError(f"ERROR[add_user_comments_to_jpeg]: jpeg_file_path is of type |{type(jpeg_file_path)}| it should be of type |str|")
    if not os.path.isfile(jpeg_file_path):
        raise ValueError(f"ERROR[add_user_comments_to_jpeg]: |{jpeg_file_path}| does not exist or is not a file. It should be.")
    valid_file_types = [".jpeg",".jpg"]
    file_extension = os.path.splitext(jpeg_file_path)[1]
    if file_extension not in valid_file_types:
        raise ValueError(f"ERROR[add_user_comments_to_jpeg]: |{jpeg_file_path}| should have a file extension of .tif or .jpeg. It currently doesn't, change this.")

    if type(user_comments) != str:
        raise TypeError(f"ERROR[add_user_comments_to_jpeg]: user_comments is of type |{type(user_comments)}| it should be of type |str|")


    image_object = Image.open(jpeg_file_path)
    try:
        exif_dict = piexif.load(image_object.info["exif"])
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comments.encode()
    except:
        exif_ifd = {piexif.ExifIFD.UserComment: user_comments.encode()}
        exif_dict = {"Exif": exif_ifd}
    exif_bytes = piexif.dump(exif_dict)
    image_object.save(jpeg_file_path,exif=exif_bytes)

if __name__ == "__main__":
    print("starting...") #TODO put code in necessary functions
    settings = load_env_variables()
    
    # Read all exif data
    print(return_all_exif(settings.test_image_path))

    # PIL to OpenCV
    pil_im_object = Image.open(settings.test_image_path).convert('RGB')
    cv2_image = np.array(pil_im_object)
    cv2_image = cv2_image[:, :, ::-1].copy() # Convert RGB to BGR
    
    # OpenCV to PIL
    cv2_colour_image = np.zeros((100,100,3),np.uint8)
    # random colour function
    height, width, channels = cv2_colour_image.shape
    for row_index,row in enumerate(cv2_colour_image):
        for height_index,pixel in enumerate(row):
            for rgb_index,rgb in enumerate(pixel):
                cv2_colour_image[row_index][height_index][rgb_index] = random.randint(0,255)

    pil_colour_image = Image.fromarray(cv2_colour_image)

    # Save png
    png_compression_parms = [cv2.IMWRITE_PNG_COMPRESSION,3] # 0 -9  higher value means smaller size but longer pression time, default is 3
    cv2.imwrite(settings.output_cv2_path,cv2_colour_image,png_compression_parms)

    # save png to memory - https://stackoverflow.com/questions/52865771/write-opencv-image-in-memory-to-bytesio-or-tempfile - https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html
    compression_successful, buffer = cv2.imencode(".png",cv2_colour_image,png_compression_parms)
    if compression_successful:
        io_buf = io.BytesIO(buffer)
        byte_array_png = io_buf.read()
    else: 
        print("TODO raise error, compression_successful is False")
    # pil_im_object = Image.fromarray()
    print("finishing")
