from random import choice
from PIL import Image, ImageDraw

# 7x7
coords = [(x, y) for x in range(4) for y in range(7)]

def generate_image(colors:list):
    ava = Image.new(size=(700, 700), mode='RGB', color=choice(colors))
    drawer = ImageDraw.Draw(ava)
    for i in range(28):
        x, y = choice(coords)
        coords.pop(coords.index((x, y)))
        color = choice(colors)
        drawer.rectangle(((x * 100, y * 100), (x * 100 + 99, y * 100 + 99)), color)
        if x != 3:
            drawer.rectangle(((600 - x * 100, y * 100), (600 - x * 100 + 99, y * 100 + 99)), color)
    ava.save('file.jpeg')
    