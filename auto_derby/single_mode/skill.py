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
    "良バ場": True,
    "急ぎ足": True,
    "コーナー巧者": True,
    "逃げ直線": True,
    "直線回復": True,
    "垂れウマ回避": True,
    "非根幹距離": True,
    "道悪": True,
    "長距離コーナー": True,
    "先頭プライド": True,
    "ポジションセンス": True,
    "左回": True,
    "晴れの日": True,
    "外枠得意": True,
    "徹底マーク": True,
    "コーナー回復": True,
    "弧線のプロフェッサー": True,
    "注目の踊り子": True,
    "集中力": True,
    "東京レース場": True,
    "阪神レース場": True,
    "臨機応変": True
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


def recognize_skills(img: PIL.Image.Image) -> bool:
    reload()
    nr = template.match(
        img,
        template.Specification(
            templates.SKILL_ITEM, threshold=0.8
        ),
    )
    gr = template.match(
        img,
        template.Specification(
            templates.SKILL_ITEM_GOLD, threshold=0.8
        ),
    )
    r = (*nr, *gr)
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
        is_leaen = template.match(
            skill_point_img,
            template.Specification(
                templates.SINGLE_MODE_LEARNED_SKILL, threshold=0.8
            ),
        )
        for _ in is_leaen:
            continue
        if text == ' ':
            continue
        point = int(text)
        if not point or remain < point:
            continue
        skill_name_img = img.crop((x - 400, y + 2, x - 130, y + 92))
        image_hash = imagetools.image_hash(skill_name_img)
        is_save_skill_label = False
        for skill_label in gv.labels:
            rate = imagetools.compare_hash(image_hash, skill_label)
            if rate > 0.99:
                is_save_skill_label = True
                skill_name = gv.labels[skill_label]
                if skills.setdefault(skill_name) and remain > point:
                    action.tap((x - 20, y + 52))
                    print(skill_name, skill_label)
                    break
                print('not learn or not needed', skill_name)
        if not is_save_skill_label:
            close_img = imagetools.show(skill_name_img)
            ans = terminal.prompt(
                "Corresponding text for current displaying image:")
            if skills.setdefault(ans) and remain > point:
                action.tap((x - 20, y + 52))
            gv.labels[image_hash] = ans
            print('not learn or not needed', ans)
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
