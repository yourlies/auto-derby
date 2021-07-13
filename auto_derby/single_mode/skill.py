# -*- coding=UTF-8 -*-
# pyright: strict

from .. import imagetools, ocr, template, templates
import cv2
import numpy as np
import PIL.Image
import PIL.ImageOps
from typing import Dict
from .. import action, template, templates, imagetools, terminal
from typing import Dict, Text
import os
import json

skills = {
    "貴顕の使命を果たすべく": True,
    "直線回復": True
}


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
    r = template.match(
        img,
        template.Specification(
            templates.SKILL_ITEM, threshold=0.8
        ),
    )
    for match in r:
        x, y = match[1]

        skill_remain_point_img = img.crop((414, 301, 465, 330))
        cv_img = imagetools.cv_image(skill_remain_point_img.convert("L"))
        cv_img = imagetools.level(
            cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
        )
        _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
        text = ocr.text(imagetools.pil_image(binary_img))
        remain = int(text)
        if remain <= 100:
            return False
        skill_point_img = img.crop((x - 73, y + 50, x - 30, y + 69))
        cv_img = imagetools.cv_image(skill_point_img.convert("L"))
        cv_img = imagetools.level(
            cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
        )
        _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
        text = ocr.text(imagetools.pil_image(binary_img))
        point = int(text)
        skill_name_img = img.crop((x - 400, y + 2, x - 130, y + 33))
        image_hash = imagetools.image_hash(skill_name_img)
        is_save_skill_label = False
        for skill_label in gv.labels:
            rate = imagetools.compare_hash(image_hash, skill_label)
            if rate > 0.99:
                is_save_skill_label = True
                skill_name = gv.labels[skill_label]
                if skills.setdefault(skill_name) and remain > point:
                    action.tap((x - 20, y + 52))
                break
        if not is_save_skill_label:
            close_img = imagetools.show(skill_name_img)
            ans = terminal.prompt(
                "Corresponding text for current displaying image:")
            gv.labels[image_hash] = ans
            close_img()
            _save()

    is_end = template.match(
        img,
        template.Specification(
            templates.SKILL_SCROLL_TO_END, threshold=0.8
        ),
    )
    for _ in is_end:
        return False
    return True
