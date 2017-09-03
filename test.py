from fontmake.font_project import FontProject
from objects import BitFont, BitInfo, BitGlyph
from transforms import convert_to_font
import codepoints
from input import open_bit_font

def create_py_bit_font():
    o = False
    X = True

    return BitFont(
        size=(4, 6),
        info=BitInfo(
            family_name='Bit Font Make TestPy',
            style_name='Regular',
            weight=400,
            designer='Ay Non',
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
                codepoint=' ',
                bits=[
                    o, o, o, o,
                    o, o, o, o,
                    o, X, X, o,
                    o, X, X, o,
                    o, o, o, o,
                    o, o, o, o,
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

def test_bit_font(bit_font):
    print(bit_font)
    font = convert_to_font(bit_font)
    font.save(
        path=f'master_ufo/{bit_font.info.family_name}.ufo',
        formatVersion=3)
    project = FontProject()
    project.build_otfs(
        [font],
        remove_overlaps=True)

bit_fonts = [
    create_py_bit_font(),
    open_bit_font('test.png'),
    open_bit_font('test.gif'),
]
for bit_font in bit_fonts:
    test_bit_font(bit_font)
