import sys
from PIL import Image
import base64
import io

def image_to_base64(image_filename):
    image = Image.open(image_filename)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
