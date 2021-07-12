# -*- coding=UTF-8 -*-
# pyright: strict

from .. import imagetools, mathtools, ocr, template, templates
import cv2
import numpy as np
import PIL.Image
import PIL.ImageOps
from typing import Dict
from .. import action, template, templates, imagetools, terminal
from typing import Dict, Text
import os
import json


class gv:
    skill_path: str = os.getenv("AUTO_DERBY_OCR_SKILL_PATH", "ocr_skills.json")
    labels: Dict[Text, Text] = {}


def reload() -> None:
    try:
        with open(gv.skill_path, "r", encoding="utf-8") as f:
            gv.labels = json.load(f)
    except OSError:
        pass


def _save() -> None:
    with open(gv.skill_path, "w", encoding="utf-8") as f:
        json.dump(gv.labels, f, indent=2, ensure_ascii=False)


hash_skills = {
    "貴顕の使命を果たすべく": True
}


def recognize_skills(img: PIL.Image.Image) -> bool:
    reload()
    rp = mathtools.ResizeProxy(img.width)
    r = template.match(
        img,
        template.Specification(
            templates.SKILL_ITEM, threshold=0.8
        ),
    )
    for _ in r:
        x, y = _[1]
        skill_name_img = img.crop((x - 400, y + 2, x - 130, y + 33))
        image_hash = imagetools.image_hash(skill_name_img)
        is_save_skill_label = False
        for skill_label in gv.labels:
            rate = imagetools.compare_hash(image_hash, skill_label)
            if rate > 0.99:
                is_save_skill_label = True
                print(gv.labels[skill_label])
                break
        if not is_save_skill_label:
            close_img = imagetools.show(skill_name_img)
            ans = terminal.prompt(
                "Corresponding text for current displaying image:")
            gv.labels[image_hash] = ans
            close_img()
            _save()
    return True

    skill_name_img = img.crop(rp.vector4((18, 301, 300, 340), 466))
    skill_point_img = img.crop(rp.vector4((360, 342, 400, 365), 466))
    skill_remain_point_img = img.crop(rp.vector4((350, 260, 400, 285), 466))

    cv_img = imagetools.cv_image(skill_remain_point_img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    text = ocr.text(imagetools.pil_image(binary_img))
    remain = int(text)

    if (remain < 150):
        return False

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

    if skills.setdefault(name):
        action.tap(rp.vector2((420, 355), 466))
    return True
