# KhmerNum - Khmer Number Identifier

A pygame-based interactive application for drawing and identifying Khmer numerals on a pixel grid.

## Features

- Interactive 50x50 pixel grid for drawing numerals
- Real-time visual feedback with color-coded pixels
- Simple keyboard controls for clearing and exiting
- Pixel pattern printing for analysis
- Fully packaged as a Python library

## Requirements

- Python 3.8 or higher
- pygame >= 2.0.0

**Note:** Python 3.13 is recommended for the best compatibility with pygame wheels.

## Installation

### From GitHub

```bash
git clone https://github.com/mengkungkao/KhmerNum.git
cd KhmerNum
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On macOS/Linux
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### From PyPI (once published)

```bash
pip install khmernum
```

## Usage

### Run the Application

```bash
python -m khmernum.app
```

Or after installing:

```bash
khmernum
```

### Controls

- **Left Mouse Click**: Toggle pixel ON/OFF
- **C Key**: Clear all pixels
- **ESC Key**: Exit application

## Development

### Setup Development Environment

```bash
git clone https://github.com/mengkungkao/KhmerNum.git
cd KhmerNum
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install -e .
```

### Run Tests

```bash
python -m pytest tests/
```

Or use unittest:

```bash
python -m unittest discover -s tests
```

### Project Structure

```
KhmerNum/
├── khmernum/
│   ├── __init__.py           # Package initialization
│   └── app.py                # Main application code
├── tests/
│   ├── __init__.py
│   └── test_khmernum.py      # Unit tests
├── requirements.txt          # Python dependencies
├── setup.py                  # Setup configuration
├── pyproject.toml            # Modern Python packaging
└── README.md                 # This file
```

## API Reference

### KhmerNumApp

```python
from khmernum import KhmerNumApp

app = KhmerNumApp(rows=50, cols=50)
app.run()
```

#### Methods

- `draw_panel()`: Render the current pixel grid
- `get_clicked_box(mouse_pos)`: Get grid position of mouse click
- `print_pixel_data()`: Print current pixel pattern to console
- `clear_panel()`: Reset all pixels to OFF
- `run()`: Start the application main loop

## License

MIT License - see LICENSE file for details

## Author

Mengkungkao - mengkungkao@gmail.com

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### pygame installation issues

If you encounter issues installing pygame:

1. Ensure you're using Python 3.13 or lower (pygame has better wheel support):
   ```bash
   py -3.13 -m venv .venv
   ```

2. Install with pre-built wheels:
   ```bash
   pip install pygame --only-binary=:all:
   ```

3. Update pip and setuptools:
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

### Module not found errors

Make sure you've installed the package in editable mode:

```bash
pip install -e .
```
