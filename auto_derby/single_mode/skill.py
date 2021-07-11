from .. import imagetools, mathtools, ocr, template, templates
import os
import cv2
import numpy as np
import PIL.Image
import PIL.ImageOps
from .context import Context


def recognize_skills(img: PIL.Image.Image) -> int:
    rp = mathtools.ResizeProxy(img.width)
    t, b = 320, 360
    crop_img = img.crop(rp.vector4((18, t, 300, b), 466))
    cv_img = imagetools.cv_image(crop_img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)

    text = ocr.text(imagetools.pil_image(binary_img))
    print(text)
