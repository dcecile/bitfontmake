from flask import Flask, send_file, request
from fontmake.font_project import FontProject
from ufo2ft.fontInfoData import postscriptFontNameFallback
from utils import temporary_cwd
from input import open_bit_font
from transforms import convert_to_font

app = Flask(__name__)

@app.route('/compile-to-otf', methods=['POST'])
def compile_font_to_otf():
    return compile_font(
        'otf',
        lambda project: project.build_otfs)

@app.route('/compile-to-ttf', methods=['POST'])
def compile_font_to_ttf():
    return compile_font(
        'ttf',
        lambda project: project.build_ttfs)

def compile_font(extension, action):
    with temporary_cwd():
        bit_font = open_bit_font(request.stream)
        font = convert_to_font(bit_font)
        project = FontProject()
        action(project)(
            [font],
            remove_overlaps=True)
        font_filename = f'{get_font_name(font)}.{extension}'
        return send_file(
            open(f'master_{extension}/{font_filename}', 'rb'),
            as_attachment=True,
            attachment_filename=font_filename)

def get_font_name(font):
    return postscriptFontNameFallback(font.info)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
