import base64
import cv2
import numpy as np
from PIL import Image
import io


def screenshot_to_webp(driver, target_width=350):
    png = driver.get_screenshot_as_png()
    img = Image.open(io.BytesIO(png))

    w, h = img.size
    ratio = target_width / float(w)
    new_size = (target_width, int(h * ratio))
    img = img.resize(new_size)

    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=70)
    return base64.b64encode(buffer.getvalue()).decode()
