# bitfontmake
_Compile raster images to vectorized bitmap fonts_

## Developing

### Prerequisites

You'll need to install Python 3 (to run the font compiler) and `venv` (to fetch local dependencies).

From a terminal inside a clone of this project, first create a new virtual environment:

```
python3 -m venv env
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

- `python main.py` (to run the module)
- `python services.py` (to run the Flask web server)
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
