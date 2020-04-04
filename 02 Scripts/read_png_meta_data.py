import dotenv # Get enironmental variables from .env file
import subprocesses # Run exif tool
import piexif
from PIL import Image

class load_env_variables():
    def __init__(self):
        self.test_image_path = os.getenv("TEST_IMAGE_PATH")

if __name__ == "__main__":
    print("starting...")
    settings = load_env_variables()
    exif_data = exif