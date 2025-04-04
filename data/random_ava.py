from io import BytesIO
from random import choice

from PIL import Image, ImageDraw


def generate_image():
    # 7x7
    coords = [(x, y) for x in range(4) for y in range(7)]
    colors = [
        (212, 255, 133),
        (237, 255, 174),
        (255, 185, 124),
        (255, 254, 153),
        (169, 174, 255),
        (255, 117, 170),
    ]
    ava = Image.new(size=(700, 700), mode="RGB", color=(255, 255, 255))
    drawer = ImageDraw.Draw(ava)
    colors = [choice(colors), (255, 255, 255)]
    for i in range(28):
        col = choice(colors)
        x, y = choice(coords)
        coords.pop(coords.index((x, y)))
        drawer.rectangle(
            ((x * 100, y * 100), (x * 100 + 99, y * 100 + 99)), col
        )
        if x != 3:
            drawer.rectangle(
                ((600 - x * 100, y * 100), (600 - x * 100 + 99, y * 100 + 99)),
                col,
            )
    ava_io = BytesIO()
    ava.save(ava_io, "PNG")
    ava_io.seek(0)
    return ava_io
