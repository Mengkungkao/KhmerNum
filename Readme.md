# KhmerNum - Khmer Number Identifier

A pygame-based interactive application for drawing and identifying Khmer numerals on a pixel grid.

## Features

- Interactive 50x50 pixel grid for drawing numerals
- Real-time visual feedback with color-coded pixels
- Simple keyboard controls for clearing and exiting
- Pixel pattern printing for analysis

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




### Controls

- **Left Mouse Click**: Toggle pixel ON/OFF
- **C Key**: Clear all pixels
- **ESC Key**: Exit application

## Development

### Setup Development Environment

```bash
git clone "link"
cd KhmerNum
pip install -r requirements.txt
```


### Project Structure

```
Proj/
├── khmernum/
│   ├── fonts/                # font
│   │    └── NotoSerifKhmer-Regular.ttf
│   └── khmernum.py                # Main application code
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

#### Methods

- `draw_panel()`: Render the current pixel grid
- `get_clicked_box(mouse_pos)`: Get grid position of mouse click
- `print_pixel_data()`: Print current pixel pattern to console
- `clear_panel()`: Reset all pixels to OFF
- `run()`: Start the application main loop


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
