from flask import Flask, send_file, request
from fontmake.font_project import FontProject
from ufo2ft.fontInfoData import postscriptFontNameFallback
from utils import TemporaryWorkingDirectory
from input import open_bit_font
from transforms import convert_to_font

app = Flask(__name__)

@app.route('/compile-to-otf', methods=['POST'])
def buildFont():
    with TemporaryWorkingDirectory():
        bit_font = open_bit_font(request.stream)
        print(bit_font)
        font = convert_to_font(bit_font)
        print(font)
        print(request)
        project = FontProject()
        project.build_otfs(
            [font],
            remove_overlaps=True)
        font_filename = f'{get_font_name(font)}.otf'
        return send_file(
            f'master_otf/{font_filename}',
            as_attachment=True,
            attachment_filename=font_filename)

def get_font_name(font):
    info = font.info
    return info.postscriptFontName or postscriptFontNameFallback(info)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
