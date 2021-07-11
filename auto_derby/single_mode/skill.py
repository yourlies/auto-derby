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
from .. import action, template, templates, imagetools


def recognize_skills(img: PIL.Image.Image, skills: dict) -> bool:
    rp = mathtools.ResizeProxy(img.width)
    skill_name_img = img.crop(rp.vector4((18, 301, 300, 340), 466))
    skill_point_img = img.crop(rp.vector4((360, 342, 400, 365), 466))
    skill_remain_point_img = img.crop(rp.vector4((350, 260, 400, 285), 466))

    cv_img = imagetools.cv_image(skill_name_img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    text = ocr.text(imagetools.pil_image(binary_img))
    name = text.strip()
    print(name)
    r = template.match(
        skill_point_img,
        template.Specification(
            templates.SINGLE_MODE_LEARNED_SKILL, threshold=0.8
        ),
    )
    for _ in r:
        return True
    cv_img = imagetools.cv_image(skill_point_img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    text = ocr.text(imagetools.pil_image(binary_img))
    point = int(text)

    cv_img = imagetools.cv_image(skill_remain_point_img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    text = ocr.text(imagetools.pil_image(binary_img))
    remain = int(text)

    if (remain < point):
        return False
    if skills.setdefault(name):
        action.tap(rp.vector2((420, 355), 466))
    return True
