# bitfontmake
_Compile raster images to vectorized bitmap fonts_

## Usage

Follow the directions in [rasterspec.md](rasterspec.md) to construct
a raster image that `bitfontmake` can convert into a font.

Then upload your GIF, PNG, or BMP file to the `bitfontmake` web service.
Here's how to do that via cURL, using `[my-new-file]` as the file to
upload:

```
curl -v -O -J --data-binary @[my-new-file] \
  https://bitfontmake.herokuapp.com/compile-to-ttf
```

The web service will respond by sending the TTF file for your font.

## Developing

### Prerequisites

You'll need to install Python 3.6 (to run the font compiler) and `venv` (to fetch local dependencies).

From a terminal inside a clone of this project, first create a new virtual environment:

```
python3.6 -m venv env
```

Then activate that environment:

```
source env/bin/activate
```

And finally, download the dependencies:

```
pip install -r requirements.txt
```

### Workflow

Here are some ways to test changes:

- `python test.py` (to run the test compilation)
- `python service.py` (to run the Flask web server)
- `heroku local` (to run the Flask web server in a Heroku-like environment)

### Style

Try to follow the conventions in [PEP 8](https://www.python.org/dev/peps/pep-0008/).

### Updating dependencies

After adding dependencies with `pip install`, check the output of `pip freeze`:

```
pip freeze -r requirements.txt | grep -v pkg-resources
```

Manually copy any newly added packages to `requirements.txt`.

## License

This project is released under the MIT License (see [LICENSE.md](LICENSE.md) for details).
