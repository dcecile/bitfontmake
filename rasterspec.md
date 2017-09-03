# bitfontmake raster image input specification
_How to write raster images that compile to vectorized bitmap fonts_

# Table of contents

 * [Encoding overview](#encoding-overview)
     * [Example RGBA encoding](#example-rgba-encoding)
 * [Image and glyph dimensions](#image-and-glyph-dimensions)
 * [Info section](#info-section)
     * [Example info parameters](#example-info-parameters)
     * [Automatic info parameters](#automatic-info-parameters)
 * [Glyphs section](#glyphs-section)
     * [Example glyph](#example-glyph)
     * [Automatic glyphs](#automatic-glyphs)

# Encoding overview

The raster image is separated into two sections:

 * the "info" section at the top, containing all metadata about the font
 * the "glyphs" section below, containing all glyphs in vertical sequence

The only significant color channels in the raster image are the **red**
channel and the **alpha** channel. All other channels (blue and green) are
ignored. *All 8-bit binary values are encoded directly into the 8-bit red
channel value of each pixel, with the exception of value 255, which may
either be encoded as red 255 or alpha 0.*

The following raster image formats are supported: GIF, PNG, and BMP.

## Example RGBA encoding

One recommended RGBA encoding is to set the background colour of the
raster image to `#??????00` (fully transparent), which is used for the
binary value 255, while using `#000000FF` (solid black) for binary value
0, and `#??FFFFFF` (light cyan) for all other binary values from 1 to
254. When used together with the GIF file format, this RGBA encoding can
be edited by many pixel graphics editors and transmitted losslessly
over Twitter.

Here are some other ideas for encoding:

 * Use RGB instead of RGBA, for editing in non-alpha software
 * Use a low alpha value for binary values from 1 to 254 (e.g. using
   a separate layer), to reduce the visual appearance of the metadata
 * Use grayscale, for monochrome display of the raster font file
 * Use green and blue values that are completely independent of the red
   values, to effectively overlay a different image on top of the font

# Image and glyph dimensions

All glyphs must be the same width and height. Only monospace (fixed pitch)
fonts are supported.

The glyph width and height must both be greater than or equal to 3.

The overall image width must be equal to the glyph width plus 2.

The overall image height must be equal to the height of the info section
plus the height of the glyphs section.

To calculate the glyph height from a raster image file, start at the
bottom-left pixel, and continue read up until the the following red/alpha
value sequence is found:

```
#EF******
#BF******
#BD******
#FF****** or #******00 { repeated N times }
```

Based on the `N` times that the 255-value pixel was read, the glyph height
is calculated to be `N + 1`.

To calculate the total number of glyphs, and thus the height of the info
section, start from one pixel above the `#EF******` pixel that was just
found. If this is a 255-value pixel, then there is at least one more
glyph: repeat the test with the pixel that's the glyph height plus two
pixels above this one. If this is not a 255-value pixel, then the info
section has been found: this row plus all preceding rows are part of the
info section.

# Info section

The info section occurs at the top of the raster image file.

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

(Because **bitfontmake** uses UFO to compile fonts, all info parameters
correspond to [UFO 3 `fontinfo`
parameters](http://unifiedfontobject.org/versions/ufo3/fontinfo.plist/).)

All required JSON keys must be specified.

After encoding the UTF-8 JSON object, the binary values must encoded as
red values of the raster image's pixels. (Byte value 255 is invalid for
UTF-8.) The order of the data must be left-to-right, top-to-bottom. Any
remaining pixels on the final row of the info section must be encoded
with red value 255 or alpha value 0.

## Example info parameters

Here's an example info object:

```json
{
  "f": "Example",
  "s": "Regular",
  "w": 400
}
```

Which encodes to the UTF-8 binary value sequence:

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
5. The UTF-8 binary values will then be laid out in left-to-right rows
from top to bottom:

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

And these are the red/alpha values that would be used for those pixels:

```
0: #7B******
1: #22******
2: #66******
3: #22******
4: #3A******
5: #22******
6: #45******
7: #78******
8: #61******
9: #6D******
............
y: #30******
z: #7D******
!: #FF****** or #******00
!: #FF****** or #******00
!: #FF****** or #******00
```

## Automatic info parameters

The following UFO info parameters are set up automatically and cannot be
specified in the raster image info section:

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

The last glyph in the sequence must be `U+FFFD REPLACEMENT CHARACTER`:

> �

Each glyph contains two pieces of information: the Unicode code point and
the bit data. Whenever the font is used to render text, each code point of
the text will be looked up in the font, and if a corresponding glyph is
found, then that code point will be rendered as a pixelized version of the
glyphs bit data.

The glyph's bit data is set into a rectangle of pixels matching the glyph
width and height of the font. It is surrounded by a 1-pixel border on all
sides.

The Unicode code point must be encoded in UTF-8, and embedded in the left
border of the glyph's bit data. Similar to the info parameters, the binary
values are encoded into pixel red values. Unlike the info parameters, the
codepoint is written top-to-bottom (starting at the top-left pixel) and
the alpha value is set to 1.

(One UTF-8 code point uses at most 4 bytes, so only the left border of the
glyph is used.)

The rest of the 1-pixel border surrounding the bit data (not containing
the Unicode code point) must be set to red value 255 or alpha value 0.

Inside the 1-pixel border is the bit data for the glyph. Each pixel must
be either red value zero or red value 255 / alpha value 0. The layout of
red-value zero pixels matches the exact location of where the glyph will
be filled when rendered by the font.

## Example glyph

Here is an example glyph for a 4-width-by-5-height letter `P`:

```
┃P-----┃
┃-XXX--┃
┃-X--X-┃
┃-XXX--┃
┃-X----┃
┃-X----┃
┃------┃
```

The pixels in this example have the following red values:

```
P: #50******
-: #FF****** or #******00
X: #00******
```

## Automatic glyphs

The following code points must be omitted from the glyph sequence because
they will be inferred as blank:

 * `U+0020 SPACE`
 * `U+00A0 NO-BREAK SPACE`
