from .. import imagetools, mathtools, ocr, template, templates
import os
import cv2
import numpy as np
import PIL.Image
import PIL.ImageOps
from PIL.Image import Image
from .context import Context
from typing import Dict, Tuple, Type
from PIL.Image import fromarray as image_from_array


def recognize_skills(img: PIL.Image.Image) -> int:
    rp = mathtools.ResizeProxy(img.width)
    skill_name_img = img.crop(rp.vector4((18, 301, 300, 340), 466))
    skill_point_img = img.crop(rp.vector4((360, 344, 400, 365), 466))

    cv_img = skill_name_img
    cv_img = imagetools.cv_image(cv_img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)

    text = ocr.text(imagetools.pil_image(binary_img))
    print(text)
