from PIL import Image
from collections import defaultdict, namedtuple
from functools import partial
from jsonschema import Draft4Validator
from objects import BitFont, BitInfo, BitGlyph
from utils import count_while
import codepoints
import json

def open_bit_font(source):
    try:
        image_basics = read_image_basics(source)
        info = read_info(image_basics)
        glyphs = list(read_glyphs(image_basics))
        return BitFont(
            size=image_basics.glyph_size,
            info=info,
            glyphs=glyphs)
    except ImageInputError:
        raise
    except Exception as exception:
        raise ImageInputError('Unknown image error') from exception

class ImageInputError(Exception):
    pass

ImageInputBasics = namedtuple(
    'ImageInputBasics',
    [
        'size',
        'values',
        'glyph_size',
        'glyph_count',
    ])

def read_image_basics(path):
    image = convert_image_to_rgba(Image.open(path))
    image_values = get_image_values(image)
    image_left_column = get_image_left_column(image_values, image.width)
    image_left_column_reversed = list(reversed(image_left_column))
    glyph_width = calculate_glyph_width(image.width)
    glyph_height = find_glyph_height(image_left_column_reversed)
    glyph_count = count_glyphs(image_left_column_reversed, glyph_height)
    return ImageInputBasics(
        size=image.size,
        values=image_values,
        glyph_size=(glyph_width, glyph_height),
        glyph_count=glyph_count)

def convert_image_to_rgba(image):
    if image.mode == 'RGBA':
        return image
    else:
        return image.convert(mode='RGBA')

def get_image_values(image):
    def convert(color):
        red = color[0]
        alpha = color[3]
        if red < 0 or red > 255:
            raise ImageInputError(f'Red value {value} not in range')
        elif red != int(red):
            raise ImageInputError(f'Red value {value} not an integer')
        elif alpha == 0:
            return 255
        else:
            return int(red)
    return list(map(convert, image.getdata()))

def get_image_left_column(image_values, image_width):
    indices = range(
        0,
        len(image_values),
        image_width)
    return list(image_values[i] for i in indices)

def calculate_glyph_width(image_width):
    width = image_width - 2
    if width < 3:
        raise ImageInputError(f'Glyph width {width} too low')
    return width

def find_glyph_height(image_left_column_reversed):
    blanks = count_while(is_pixel_blank, image_left_column_reversed)
    last_begin = blanks + 0
    last_end = blanks + 3
    last_codepoint = image_left_column_reversed[last_begin : last_end]
    if last_codepoint != [0xBD, 0xBF, 0xEF]:
        raise ImageInputError(f'Could not find U+FFFD glyph ({last_codepoint} found instead)')
    height = blanks + 1
    if height < 3:
        raise ImageInputError(f'Glyph height {height} too low')
    return height

def is_pixel_blank(value):
    return value == 0xFF

def is_pixel_nonblank(value):
    return not is_pixel_blank(value)

def count_glyphs(image_left_column_reversed, glyph_height):
    indices = range(
        glyph_height + 2,
        len(image_left_column_reversed),
        glyph_height + 2)
    pixels = (image_left_column_reversed[i] for i in indices)
    return count_while(is_pixel_blank, pixels) + 1

def read_info(image_basics):
    image_values = image_basics.values
    (image_width, image_height) = image_basics.size
    (glyph_width, glyph_height) = image_basics.glyph_size
    glyph_count = image_basics.glyph_count
    info_height = calculate_info_height(image_height, glyph_height, glyph_count)
    info_values = get_info_values(image_values, image_width, info_height)
    info_string = extract_and_decode_utf8(info_values)
    info_json = decode_json(info_string)
    validate_info_json(info_json)
    return create_bit_info(info_json)

def calculate_info_height(image_height, glyph_height, glyph_count):
    return image_height - (glyph_height + 2) * glyph_count

def get_info_values(image_data, image_width, image_info_height):
    return image_data[0 : image_width * image_info_height]

def extract_and_decode_utf8(values):
    return decode_utf8(extract_utf8(values))

def extract_utf8(values):
    utf8_count = count_while(is_pixel_nonblank, values)
    blanks = values[utf8_count:]
    if blanks and not all(map(is_pixel_blank, blanks)):
        raise ImageInputError(f'Non-blank data after UTF-8 data (found {blanks})')
    return bytes(values[:utf8_count])

def decode_utf8(utf8):
    try:
        return utf8.decode('utf-8', errors='strict')
    except UnicodeDecodeError as unicode_error:
        raise ImageInputError(f'Invalid UTF-8 data (found {utf8})') from unicode_error

def decode_json(string):
    try:
        return json.loads(string)
    except json.JSONDecodeError as json_error:
        raise ImageInputError(f'Invalid JSON data (found {string})') from json_error

def validate_info_json(info_json):
    non_blank_string = {
        'type': 'string',
        'minLength': 1,
    }
    positive_integer = {
        'type': 'integer',
        'minimum': 1,
    }
    non_negative_integer = {
        'type': 'integer',
        'minimum': 0,
    }
    boolean = {
        'type': 'boolean',
    }
    schema = {
      'type': 'object',
      'properties': {
          'f': non_blank_string,
          's': non_blank_string,
          'w': positive_integer,
          'd': non_blank_string,
          'du': non_blank_string,
          'c': non_blank_string,
          'mj': non_negative_integer,
          'mn': non_negative_integer,
          'o': boolean,
      },
      'required': [
          'f',
          's',
          'w',
      ]
    }
    validator = Draft4Validator(schema)
    errors = list(validator.iter_errors(info_json))
    if errors:
        messages = ', '.join(map(format_json_validation_error, errors))
        raise ImageInputError(f'Invalid JSON data (found {info_json}, {messages})')

def format_json_validation_error(error):
    message = error.message
    if error.path:
        path = '/'.join(error.path)
        return f"{message} at '{path}'"
    else:
        return message

def create_bit_info(info_json):
    info_json = defaultdict(lambda: None, info_json)
    return BitInfo(
        family_name=info_json['f'],
        style_name=info_json['s'],
        weight=info_json['w'],
        designer=info_json['d'],
        designer_url=info_json['du'],
        copyright_year=info_json['c'],
        major_version=info_json['mj'],
        minor_version=info_json['mn'],
        is_ofl=info_json['o'])

def read_glyphs(image_basics):
    for i in range(0, image_basics.glyph_count):
        glyph_values = get_glyph_values(image_basics.values, image_basics.size, image_basics.glyph_size, i)
        yield read_glyph(image_basics.glyph_size, glyph_values)

def get_glyph_values(image_data, image_size, glyph_size, i):
    (image_width, image_height) = image_size
    padded_glyph_height = glyph_size[1] + 2
    start_row = image_height - (i + 1) * padded_glyph_height
    begin = start_row * image_width
    end = begin + padded_glyph_height * image_width
    return image_data[begin : end]

def read_glyph(glyph_size, glyph_values):
    codepoint = read_glyph_codepoint(glyph_size, glyph_values)
    validate_glyph_border(glyph_size, glyph_values)
    bits = read_glyph_bits(glyph_size, glyph_values)
    return BitGlyph(
        codepoint=codepoint,
        bits=bits)

def read_glyph_codepoint(glyph_size, glyph_values):
    left_border = get_glyph_column_values(glyph_size, glyph_values, 0)
    codepoint_string = extract_and_decode_utf8(left_border)
    if len(codepoint_string) > 1:
        raise ImageInputError(f'Glyph has multiple codepoints (found "{codepoint_string}")')
    return codepoint_string

def get_glyph_column_values(glyph_size, glyph_values, i):
    indices = range(
        i,
        (glyph_size[0] + 2) * (glyph_size[1] + 2),
        glyph_size[0] + 2)
    return list(glyph_values[j] for j in indices)

def validate_glyph_border(glyph_size, glyph_values):
    top = 0
    right = glyph_size[0] + 1
    bottom = glyph_size[1] + 1
    border = (get_glyph_row_values(glyph_size, glyph_values, top)
        + get_glyph_column_values(glyph_size, glyph_values, right)
        + get_glyph_row_values(glyph_size, glyph_values, bottom))
    if not all(map(is_pixel_blank, border)):
        raise ImageInputError(f'Glyph border not all blank (found {border})')

def get_glyph_row_values(glyph_size, glyph_values, i):
    begin = i * (glyph_size[0] + 2) + 1
    end = begin + glyph_size[0]
    return glyph_values[begin : end]

def read_glyph_bits(glyph_size, glyph_values):
    bit_values = get_glyph_bit_values(glyph_size, glyph_values)
    validate_glyph_bit_values(bit_values)
    return list(map(is_pixel_filled, bit_values))

def get_glyph_bit_values(glyph_size, glyph_values):
    rows = map(
        partial(get_glyph_row_values, glyph_size, glyph_values),
        range(1, glyph_size[1] + 1))
    return sum(rows, [])

def validate_glyph_bit_values(glyph_bit_values):
    def test(value):
        return is_pixel_filled(value) or is_pixel_blank(value)
    if not all(map(test, glyph_bit_values)):
        raise ImageInputError(f'Glyph bit data out of range (found {glyph_bit_values})')

def is_pixel_filled(value):
    return value == 0
