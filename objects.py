from collections import namedtuple

BitFont = namedtuple(
    'BitFont',
    [
        'size',
        'info',
        'glyphs',
    ])

BitInfo = namedtuple(
    'BitInfo',
    [
        'family_name',
        'style_name',
        'weight',
        'designer',
        'designer_url',
        'copyright_year',
        'major_version',
        'minor_version',
        'is_ofl',
    ])

BitGlyph = namedtuple(
    'BitGlyph',
    [
        'codepoint',
        'bits',
    ])

BitMetrics = namedtuple(
    'BitMetrics',
    [
        'width',
        'height',
        'units_per_pixel',
        'units_per_em',
        'ascender',
        'descender',
        'line_gap',
        'left_advance',
        'total_advance',
    ])
