# bitfontmake PNG encoding spec
_How to write PNGs that compile to vectorized bitmap fonts_

# Table of contents

 * [Overview](#overview)
 * [Image and glyph dimensions](#image-and-glyph-dimensions)
 * [Info section](#info-section)
     * [Example info parameters](#example-info-parameters)
     * [Automatic info parameters](#automatic-info-parameters)
 * [Glyphs section](#glyphs-section)
     * [Example glyph](#example-glyph)
     * [Automatic glyphs](#automatic-glyphs)

# Overview

The PNG is separated into two sections:

 * the "info" section at the top, containing all metadata about the font
 * the "glyphs" section below, containing all glyphs in vertical sequence

All data in the PNG is encoded as greyscale + alpha.

All glyphs must be the same width and height. In other words, only
monospace (fixed pitch) fonts are supported.

The glyph width and height must both be greater than or equal to 2.

The last glyph must be `U+FFFD REPLACEMENT CHARACTER`:

```
�
```

# Image and glyph dimensions

The overall image width must be equal to the glyph width plus 2.

The overall image height must be equal to the height of the info section
plus the height of the glyphs section.

To calculate the glyph height from a PNG file, start at the bottom-left
pixel, and continue read up until the the following RGBA sequence is
found:

```
EFEFEF01
BFBFBF01
BDBDBD01
00000000 { repeated N times }
```

Based on the `N` times that the `00000000` pixel was read, the glyph
height is calculated to be `N + 1`.

# Info section

The info section occurs at the top of the PNG file.

The pixel data in the info section must be a UTF-8 encoding of an "info"
JSON object:

| JSON key | UFO 3 parameter           | Required | Example                 |
| -------- | --------------------------| -------- | ----------------------- |
| `f`      | `familyName`              | **Yes**  | `"My Example Font"`     |
| `s`      | `styleName`               | **Yes**  | `"Regular"`             |
| `w`      | `weight`                  | **Yes**  | `400`                   |
| `d`      | `openTypeNameDesigner`    | No       | `"Ay Non"`              |
| `du`     | `openTypeNameDesignerURL` | No       | `"http://example.org/"` |
| `c`      | *copyright year\**        | No       | `"2017"`                |
| `mj`     | `majorVersion`            | No       | `2`                     |
| `mn`     | `minorVersion`            | No       | `302`                   |
| `o`      | *Open Font Licence\*\**   | No       | `true`                  |

*\* the copyright year `c` is used to construct the UFO 3 `copyright`
parameter, together with the designer name `d`*

*\*\* the Open Font License `o` is used to set the UFO 3 parameters for
`openTypeNameLicense`, `openTypeNameLicenseURL`, and `openTypeOS2Type`*

(**bitfontmake** internally uses UFO to compile fonts, so all info
parameters correspond to [UFO 3 `fontinfo`
parameters](http://unifiedfontobject.org/versions/ufo3/fontinfo.plist/).)

After encoding the UTF-8 JSON object, the bytes must be set as greyscale
pixels in reading order with an alpha value of 128. Any remaining pixels
on the final row of the info section must be encoded as RGBA zero.

## Example info parameters

Here's an example info object:

```json
{
  "f": "Example",
  "s": "Regular",
  "w": 400
}
```

Which encodes to the UTF-8 byte sequence:

```
7B 22 66 22 3A
22 45 78 61 6D
70 6C 65 22 2C
22 73 22 3A 22
52 65 67 75 6C
61 72 22 2C 22
77 22 3A 34 30
30 7D
```

If the glyphs for this font have a width of 3, the overall image width is
5. The UTF-8 bytes will then be laid out in reading order:

```
┏━━━━━┓
┃01234┃
┃56789┃
┃.....┃
┃.....┃
┃.....┃
┃.....┃
┃.....┃
┃yz!!!┃
```

And these are the RGBA values that would be used for those pixels:

```
0: 7B7B7B80
1: 22222280
2: 66666680
3: 22222280
4: 3A3A3A80
5: 22222280
6: 45454580
7: 78787880
8: 61616180
9: 6D6D6D80
...
y: 30303080
z: 7D7D7D80
!: 00000000
!: 00000000
!: 00000000
```

## Automatic info parameters

The following UFO info parameters are set up automatically and cannot be
specified in the PNG info section:

 * `unitsPerEm`: set to 100 * the glyph height
 * `ascender`: set to `unitsPerEm` + 100
 * `descender`: set to -100
 * `postscriptUnderlinePosition`: set to -50
 * `postscriptUnderlineThickness`: set to 100
 * `capHeight`: set to `unitsPerEm`
 * `xHeight`: set to `unitsPerEm`

# Glyphs section

The glyphs section occurs immediately below the info section. It must
contain a vertical sequence of glyphs with no extra spacing.

Each glyph contains two pieces of information: the Unicode code point and
the bit data. Whenever the font is used to render text, each code point of
the text will be looked up in the font, and if a corresponding glyph is
found, then that code point will be rendered as a pixelized version of the
glyphs bit data.

The glyph's bit data is set into a rectangle of pixels matching the glyph
width and height of the font. It is surrounded by a 1-pixel border on all
sides.

The Unicode code point must be encoded in UTF-8, and embedded in the left
border of the glyph's bit data. Similar to the info parameters, each byte
is encoded as a greyscale pixel value. Unlike the info parameters, the
codepoint is written top-to-bottom (starting at the top-left pixel) and
the alpha value is set to 1.

The rest of the 1-pixel border surrounding the bit data (not containing
the Unicode code point) must be set to RGBA zero.

Inside the 1-pixel border is the bit data for the glyph. Each pixel must
be either RGBA zero or RGBA solid black (alpha 255). The layout of the bit
data matches exactly how the glyph will be rendered by the font.

## Example glyph

Here is an example of a 4 width by 5 height letter `P`:

```
┃P-----┃
┃-XXX--┃
┃-X--X-┃
┃-XXX--┃
┃-X----┃
┃-X----┃
┃------┃
```

The pixels in this example have the following RGBA values:

```
P: 50505001
-: 00000000
X: 000000FF
```

## Automatic glyphs

The following code points must be omitted from the glyph list because they
will be inferred as blank:

 * `U+0020 SPACE`
 * `U+00A0 NO-BREAK SPACE`
