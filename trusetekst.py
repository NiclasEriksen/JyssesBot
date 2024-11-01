import os
from typing import Union
from venv import create

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_PATH: str = os.path.dirname(os.path.realpath(__file__))
FONT_PATH: str = os.path.join(BASE_PATH, "fonts")
TRUSE_PATH: str = os.path.join(BASE_PATH, "truse.png")
H_ALIGN_LEFT: int = 0
H_ALIGN_RIGHT: int = 1
H_ALIGN_CENTER: int = 2
V_ALIGN_TOP: int = 0
V_ALIGN_BOTTOM: int = 1
V_ALIGN_CENTER: int = 2
MARGIN: float = 3.0
COLORS: dict = dict(
    red     = "#ff2440",
    white   = "#FFFFFF",
    black   = "#000000",
    pink    = "#ff6b9b",
    blue    = "#0064f8",
    olive   = "#72ba37",
    orange  = "#ff6713",
    cyan    = "#00fff7",
)


class Fonts:
    Runescape: tuple = ("Runescape", os.path.join(FONT_PATH, "runescape_uf.ttf"))
    Truckin: tuple = ("Truckin", os.path.join(FONT_PATH, "truckin.ttf"))
    Roboto: tuple = ("Roboto", os.path.join(FONT_PATH, "Roboto-Medium.ttf"))
    Girly: tuple = ("Girly", os.path.join(FONT_PATH, "Loverine.otf"))
    Porky: tuple = ("Porky", os.path.join(FONT_PATH, "PORKYS_.TTF"))

    def __init__(self):
        self._fonts: dict = {k: v for (k, v) in [self.Runescape, self.Truckin, self.Roboto, self.Girly, self.Porky]}

    @property
    def font_list(self) -> list:
        return list(self._fonts.keys())

    def __getitem__(self, key: str) -> Union[str, None]:
        if key in self._fonts.keys():
            return self._fonts[key]
        return None


fonts: Fonts = Fonts()
FONT_DEFAULT: str = "Roboto"


def add_text(
        img: Image, text: str,
        h_align: int = H_ALIGN_CENTER, v_align: int = V_ALIGN_CENTER,
        size: int = 32, font: str = FONT_DEFAULT, color_h: str = COLORS["blue"]
) -> Image:
    font_fp = fonts[font] if fonts[font] else fonts[FONT_DEFAULT]
    font_obj = ImageFont.truetype(font_fp, size)
    fg_img = Image.new("RGBA", img.size)
    # bg_img = Image.new("RGBA", img.size)
    fg_img_draw = ImageDraw.Draw(fg_img)
    # bg_img_draw = ImageDraw.Draw(bg_img)

    _, _, w, h = fg_img_draw.textbbox((0, 0), text, font=font_obj, stroke_width=2)
    if img.size[0] < w:
        factor = img.size[0] / w
        split_pos = int(len(text) * factor)
        text = text[:split_pos] + "\n" + text[split_pos:]
        _, _, w, h = fg_img_draw.textbbox((0, 0), text, font=font_obj, stroke_width=2)

    v_center: float = img.size[1] / 2.0
    h_center: float = img.size[0] / 2.0
    t_align: str = "center"
    if h_align == H_ALIGN_CENTER and v_align == V_ALIGN_CENTER:
        pos: tuple = (h_center - (w / 2.0), v_center - (h / 2.0))
    elif h_align == H_ALIGN_CENTER:
        if v_align == V_ALIGN_TOP:
            pos = (h_center - (w / 2.0), MARGIN)
        else:
            pos = (h_center - (w / 2.0), img.size[1] - h - MARGIN)
    else:
        pos_x = MARGIN
        pos_y = MARGIN
        if h_align == H_ALIGN_RIGHT:
            t_align = "right"
            pos_x = img.size[0] - w - MARGIN
        else:
            t_align = "left"

        if v_align == V_ALIGN_BOTTOM:
            pos_y = img.size[1] - h - MARGIN
        elif v_align == V_ALIGN_CENTER:
            pos_y = v_center - (h / 2.0)
        pos = (pos_x, pos_y)


    fg_img_draw.text(pos, text, font=font_obj, fill=color_h, align=t_align, stroke_width=2, stroke_fill=(255, 255, 255) if color_h == COLORS["black"] else (0, 0, 0))
    img.paste(fg_img, (0, 0), fg_img)

    return img


def create_img() -> Image:
    return Image.open(TRUSE_PATH)


def get_trusetext(
        text: str, font: str, size: int, color: str,
        v_align: int, h_align: int
) -> Image:
    if len(text) == 0:
        return create_img()

    img = create_img()
    return add_text(
        img, text,
        font=font, size=size, color_h=color, v_align=v_align, h_align=h_align
    )

if __name__ == "__main__":
    img = create_img()
    img = add_text(img, "Test tekst her på bildet 123123 dasd ad 123123", v_align=V_ALIGN_BOTTOM, h_align=H_ALIGN_CENTER)
    img.show()
