# -*- coding=UTF-8 -*-
# pyright: strict

from .. import imagetools, ocr, template, templates
import cv2
import numpy as np
import PIL.Image
import PIL.ImageOps
from typing import Dict, Tuple
from .. import action, template, templates, imagetools, terminal
from typing import Dict, Text
import os
import json
from typing import List

_TEMPLATES_PATH = './auto_derby/templates/'

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
    "新潟レース場": True,
    "汝、皇帝の神威を見よ": True,
    "臨機応変": True,
    "末脚": True,
    "直線巧者": True,
    "外枠得意": True,
    "曇りの日": True,
    "春ウマ娘": True,
    "直線加速": True,
    "冬ウマ娘": True,
    "秋ウマ娘": True,
    "夏ウマ娘": True,
    "根幹距離": True,
    "危険回避": True,
    "長距離直線": True,
    "対抗意識": True,
    "直線回復": True,
    "末脚": True,
    "右回": True,
    "円弧のマエストロ": True,
    "急ぎ足": True,
    "先駆け": True,
    "ハヤテ一文字": True,
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


def _save_skill_img(img: PIL.Image.Image, image_hash: str) -> None:
    close_img = imagetools.show(img)
    ans = terminal.prompt(
        "Corresponding text for current displaying image:")

    if not os.path.exists(
            _TEMPLATES_PATH + ans + '.png'):
        img.save(
            _TEMPLATES_PATH + ans + '.png')

    gv.labels[image_hash] = ans
    _save()
    close_img()


def _is_match_exist_skill_img(name: str, img: PIL.Image.Image) -> bool:
    r = template.match(img, template.Specification(
        name + '.png', threshold=0.8
    ))
    for _ in r:
        return True
    return False


def _is_learned_skill(img: PIL.Image.Image) -> bool:
    is_leaened = template.match(
        img,
        template.Specification(
            templates.SINGLE_MODE_LEARNED_SKILL, threshold=0.8
        ),
    )
    for _ in is_leaened:
        return True
    return False


def _recognize_skill_remain_point(img: PIL.Image.Image) -> int:
    skill_remain_point_img = img.crop((414, 301, 465, 330))
    cv_img = imagetools.cv_image(skill_remain_point_img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text)


def _recognize_skill_point(img: PIL.Image.Image):
    cv_img = imagetools.cv_image(img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    return ocr.text(imagetools.pil_image(binary_img))


def _find_similar_skills(image_hash: str) -> List[Tuple[float, str]]:
    similar_skills: List[Tuple[float, str]] = []
    for skill_hash in gv.labels:
        rate = imagetools.compare_hash(image_hash, skill_hash)
        if rate > 0.80:
            similar_skills.append((rate, gv.labels[skill_hash]))
    similar_skills.sort(
        key=lambda x: x[0],
        reverse=True
    )
    values = {i[1]: i for i in reversed(similar_skills)}.values()
    similar_skills = []
    for _ in values:
        similar_skills.append(_)
    similar_skills.sort(
        key=lambda x: x[0],
        reverse=True
    )
    return similar_skills


def _find_skill_item(img: PIL.Image.Image):
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
    return (*nr, *gr)


def _is_scroll_to_end(img: PIL.Image.Image) -> bool:
    is_end = template.match(
        img,
        template.Specification(
            templates.SKILL_SCROLL_TO_END, threshold=0.8
        ),
    )
    for _ in is_end:
        return False
    return True


def recognize_skills(img: PIL.Image.Image) -> bool:
    r = _find_skill_item(img)
    for match in r:
        x, y = match[1]
        remain = _recognize_skill_remain_point(img)
        if remain <= 100:
            return False

        skill_point_img = img.crop((x - 73, y + 50, x - 30, y + 69))
        point = _recognize_skill_point(skill_point_img)
        if point == ' ':
            continue
        point = int(point)
        if _is_learned_skill(skill_point_img):
            continue
        if not point or remain < point:
            continue

        skill_img = img.crop((x - 400, y + 2, x - 130, y + 92))
        image_hash = imagetools.image_hash(skill_img)
        is_recorded_skill = False

        similar_skills = _find_similar_skills(image_hash)

        for _, skill_name in similar_skills:
            if not skills.setdefault(skill_name) or remain < point:
                continue

            is_exist_skill_img = os.path.exists(
                _TEMPLATES_PATH + skill_name + '.png')

            if is_exist_skill_img and _is_match_exist_skill_img(
                    skill_name, skill_img):
                action.tap((x - 20, y + 52))
                is_recorded_skill = True
                break
        if not is_recorded_skill:
            _save_skill_img(
                img.crop((x - 390, y + 12, x - 135, y + 87)), image_hash)
    return _is_scroll_to_end(img)
