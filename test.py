from fontmake.font_project import FontProject
from objects import BitFont, BitInfo, BitGlyph
from transforms import convert_to_font
import codepoints

o = False
X = True

bit_font = BitFont(
    size=(4, 6),
    info=BitInfo(
        family_name='Bit Font Make Test',
        style_name='Regular',
        weight=400,
        designer='A Non',
        designer_url='http://example.org',
        copyright_year='2017',
        major_version=0,
        minor_version=1,
        is_ofl=True),
    glyphs=[
        BitGlyph(
            codepoint='A',
            bits=[
                o, X, X, o,
                o, X, X, o,
                X, o, o, X,
                X, X, X, X,
                X, o, o, X,
                X, o, o, X,
            ]),
        BitGlyph(
            codepoint=codepoints.replacement_character,
            bits=[
                X, o, X, o,
                o, X, o, X,
                X, o, X, o,
                o, X, o, X,
                X, o, X, o,
                o, X, o, X,
            ]),
    ])

print(bit_font)

font = convert_to_font(bit_font)

print(font)
font.save(
    path='test.ufo',
    formatVersion=3)
project = FontProject()
project.build_otfs(
    [ font ],
    remove_overlaps=True)
