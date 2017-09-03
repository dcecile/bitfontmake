from defcon import Font, Glyph, Contour, Point
from functools import partial
from objects import BitFont, BitInfo, BitGlyph, BitMetrics
import codepoints
import re
import unicodedata
from utils import flatten

def convert_to_font(bit_font):
    bit_metrics = calculate_bit_metrics(bit_font.size)
    all_bit_glyphs = bit_font.glyphs + create_extra_bit_glyphs(bit_metrics)
    return create_font(
        info_params=convert_to_info_params(bit_metrics, bit_font.info),
        glyphs=convert_to_glyphs(bit_metrics, all_bit_glyphs))

def calculate_bit_metrics(bit_size):
    (width, height) = bit_size
    units_per_pixel = 100
    units_per_em = units_per_pixel * height
    x_height = find_x_height() or units_per_em
    stems = list(
        units_per_pixel * (i + 1)
        for i in range(0, 4))
    values = flatten(set([
        (0, -25),
        (x_height, 25),
        (units_per_em, 25)
    ]))
    print('blue values', values)
    return BitMetrics(
        width=width,
        height=height,
        units_per_pixel=units_per_pixel,
        units_per_em=units_per_em,
        ascender=units_per_pixel * (height + 1),
        descender=units_per_pixel * (-1),
        x_height=x_height,
        line_gap=units_per_pixel * 2,
        left_advance=0,
        total_advance=units_per_pixel * (width + 1),
        stems=stems,
        values=values)

def create_extra_bit_glyphs(bit_metrics):
    space_bits = ([False]
        * bit_metrics.width
        * bit_metrics.height)
    return [
        BitGlyph(
            codepoint=' ',
            bits=space_bits),
        BitGlyph(
            codepoint=codepoints.no_break_space,
            bits=space_bits),
    ]

def convert_to_info_params(bit_metrics, bit_info):
    return [
        ('familyName', bit_info.family_name),
        ('styleName', bit_info.style_name),
        ('unitsPerEm', bit_metrics.units_per_em),
        ('postscriptForceBold', False),
        ('postscriptIsFixedPitch', True),
        ('postscriptUnderlinePosition', -bit_metrics.units_per_pixel / 2),
        ('postscriptUnderlineThickness', bit_metrics.units_per_pixel),
        ('postscriptBlueValues', bit_metrics.values),
        ('postscriptStemSnapH', bit_metrics.stems),
        ('postscriptStemSnapV', bit_metrics.stems),
        ('versionMajor', bit_info.major_version),
        ('versionMinor', bit_info.minor_version),
        ('ascender', bit_metrics.ascender),
        ('descender', bit_metrics.descender),
        ('capHeight', bit_metrics.units_per_em),
        ('xHeight', bit_metrics.x_height),
        ('openTypeOS2TypoLineGap', 0),
        ('openTypeHheaLineGap', 0),
        ('openTypeOS2WeightClass', bit_info.weight),
        ('openTypeNameDesigner', bit_info.designer),
        ('openTypeNameDesignerURL', bit_info.designer_url),
        ('copyright', f'Copyright {bit_info.copyright_year} {bit_info.designer}'),
        ('openTypeNameLicense', 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL. This Font Software is distributed on an \u2018AS IS\u2019 BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the SIL Open Font License for the specific language, permissions and limitations governing your use of this Font Software.' if bit_info.is_ofl else None),
        ('openTypeNameLicenseURL', 'http://scripts.sil.org/OFL' if bit_info.is_ofl else None),
        ('openTypeOS2Type', [] if bit_info.is_ofl else None),
    ]

def find_x_height():
    return None

def convert_to_glyphs(bit_metrics, bit_glyphs):
    return map(
        partial(convert_to_glyph, bit_metrics),
        bit_glyphs)

def convert_to_glyph(bit_metrics, bit_glyph):
    return create_glyph(
        codepoint=bit_glyph.codepoint,
        width=bit_metrics.total_advance,
        contours=convert_to_contours(bit_metrics, bit_glyph.bits))

def convert_to_contours(bit_metrics, bits):
    for y in range(0, bit_metrics.height):
        for x in range(0, bit_metrics.width):
            if bits[y * bit_metrics.width + x]:
                points = [
                    (x + 0, y + 0),
                    (x + 1, y + 0),
                    (x + 1, y + 1),
                    (x + 0, y + 1),
                ]
                yield create_contour(
                    map(
                        partial(transform_pixels_to_units, bit_metrics),
                        points))

def transform_pixels_to_units(bit_metrics, point):
    offset_x = bit_metrics.left_advance
    scale = bit_metrics.units_per_pixel
    (x, y) = point
    flipped_y = bit_metrics.height - y
    return (offset_x + x * scale, flipped_y * scale)

def create_point(coordinates):
    return Point(coordinates, "line")

def create_contour(contour_path):
    contour = Contour()
    for point in map(create_point, contour_path):
        contour.appendPoint(point)
    return contour

def create_glyph(codepoint, width, contours):
    glyph = Glyph()
    glyph.name = get_glyph_name(codepoint)
    glyph.unicode = ord(codepoint)
    glyph.width = width
    for contour in contours:
        glyph.appendContour(contour)
    return glyph

english_alphabet = re.compile('^[A-Za-z]$')

def get_glyph_name(codepoint):
    if codepoint == codepoints.replacement_character:
        return '.notdef'
    elif english_alphabet.match(codepoint):
        return codepoint
    else:
        return unicodedata.name(codepoint).lower()

def create_font(info_params, glyphs):
    font = Font()
    for info_key, info_value in info_params:
        setattr(font.info, info_key, info_value)
    for glyph in glyphs:
        font.insertGlyph(glyph)
    return font
