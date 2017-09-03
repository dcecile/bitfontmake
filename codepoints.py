import unicodedata

replacement_character = unicodedata.lookup('REPLACEMENT CHARACTER')

spaces = list(map(unicodedata.lookup, [
    'SPACE',
    'NO-BREAK SPACE',
    'THIN SPACE',
    'IDEOGRAPHIC SPACE',
]))

def is_uppercase(codepoint):
    return unicodedata.category(codepoint) == 'Lu'
