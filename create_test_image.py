from PIL import Image
from itertools import chain
import codepoints
import json
import click

@click.command()
@click.argument('extension')
@click.argument('glyphs')
def create(extension, glyphs):
    """Create a blank, test raster image for input into bitfontmake."""
    info_bytes = json.dumps({
        'f': f'Bit Font Make Test{extension.upper()}',
        's': 'Regular',
        'w': 400,
        'd': 'Ay Non',
        'du': 'http://example.org',
        'c': '2017',
        'mj': 0,
        'mn': 1,
        'o': True,
    }, separators=(',', ':')).encode('utf-8')
    print(info_bytes, len(info_bytes))

    glyph_width, glyph_height = (4, 6)
    glyph_codepoints = (list(glyphs)
        + [codepoints.replacement_character])

    image_width = glyph_width + 2
    image_info_height = (len(info_bytes) + image_width - 1) // image_width
    image_height = (image_info_height
        + (glyph_height + 2) * len(glyph_codepoints))
    print(glyph_width, glyph_height, image_width, image_height)

    def get_color(byte_value):
        if byte_value == 0:
            return (0, 0, 0, 255)
        elif byte_value == 255:
            return (255, 255, 255, 0)
        else:
            return (byte_value, 255, 255, 255)

    image = Image.new(
        'RGBA',
        (image_width, image_height),
        get_color(255))
    image_data = list(image.getdata())
    for i, info_byte in enumerate(info_bytes):
        image_data[i] = get_color(info_byte)
    for i, glyph_codepoint in enumerate(glyph_codepoints):
        glyph_y = image_info_height + i * (glyph_height + 2)
        for j, glyph_codepoint_byte in enumerate(glyph_codepoint.encode('utf-8')):
            k = (glyph_y + j) * image_width
            image_data[k] = get_color(glyph_codepoint_byte)
            print(k, glyph_codepoint_byte)

    image.putdata(image_data)
    image.save(f'test_{extension}.png')

if __name__ == '__main__':
    create()
