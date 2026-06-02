import pygame
import json
import os
import glob
pygame.init()
GRID_SIZE = 100
DEFAULT_W, DEFAULT_H = 1100, 760
MIN_W, MIN_H = 980, 720
PANEL_W = 360
MARGIN = 24
TOP_H = 60
BOTTOM_H = 34
MAX_BRUSH = 5
FPS = 60
FILL_SIZE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")
TEMPLATE_FILE = os.path.join(BASE_DIR, "khmer_digit_templates.json")
KHMER_DIGITS = ["០", "១", "២", "៣", "៤", "៥", "៦", "៧", "៨", "៩"]
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BG = (248, 248, 248)
PANEL_BG = (242, 244, 248)
GRID_LIGHT = (225, 225, 225)
GRID_DARK = (190, 190, 190)
BTN = (230, 230, 230)
BTN_HOVER = (210, 225, 255)
BORDER = (90, 90, 90)
TEXT = (25, 25, 25)
MUTED = (90, 90, 90)
BLUE = (40, 100, 210)
GREEN = (30, 150, 90)
RED = (200, 50, 50)
YELLOW = (255, 245, 180)
screen = pygame.display.set_mode((DEFAULT_W, DEFAULT_H), pygame.RESIZABLE)
pygame.display.set_caption("50x50 Khmer Number Recognition")
clock = pygame.time.Clock()
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
brush_size = 1
training_mode = False
prediction_text = "Draw a Khmer number"
prediction_score = ""
recognise_btn = None
clear_btn = None
train_btn = None
def ensure_font_folder():
    if not os.path.exists(FONT_DIR):
        os.makedirs(FONT_DIR)
def find_khmer_font():
    ensure_font_folder()
    preferred = ["NotoSerifKhmer-Regular.ttf"]
    for filename in preferred:
        path = os.path.join(FONT_DIR, filename)
        if os.path.exists(path):
            return path
    fonts = glob.glob(os.path.join(FONT_DIR, "*.ttf")) + glob.glob(os.path.join(FONT_DIR, "*.otf"))
    return fonts[0] if fonts else None
KHMER_FONT_PATH = find_khmer_font()
def load_font(size):
    if KHMER_FONT_PATH and os.path.exists(KHMER_FONT_PATH):
        return pygame.font.Font(KHMER_FONT_PATH, size)
    return pygame.font.SysFont("arial", size)
title_font = load_font(32)
font = load_font(20)
small_font = load_font(16)
tiny_font = load_font(14)
template_font = load_font(80)
def get_layout():
    win_w, win_h = screen.get_size()
    left_w = win_w - PANEL_W - MARGIN * 3
    left_h = win_h - TOP_H - BOTTOM_H - MARGIN * 2
    cell = max(6, min(left_w // GRID_SIZE, left_h // GRID_SIZE))
    grid_px = cell * GRID_SIZE
    grid_left = MARGIN + max(0, (left_w - grid_px) // 2)
    grid_top = TOP_H + MARGIN + max(0, (left_h - grid_px) // 2)
    panel_x = win_w - PANEL_W - MARGIN
    panel_y = TOP_H + MARGIN
    panel_h = win_h - panel_y - BOTTOM_H - MARGIN
    return {
        "win_w": win_w, "win_h": win_h, "cell": cell,
        "grid_px": grid_px, "grid_left": grid_left, "grid_top": grid_top,
        "panel_x": panel_x, "panel_y": panel_y, "panel_w": PANEL_W, "panel_h": panel_h,
    }
def draw_text(text, fnt, colour, x, y):
    image = fnt.render(text, True, colour)
    screen.blit(image, (x, y))
    return y + image.get_height()
def draw_wrapped(text, fnt, colour, x, y, max_w, gap=5):
    if not text:
        return y
    words = text.split(" ")
    line = ""
    for word in words:
        test = word if line == "" else line + " " + word
        if fnt.size(test)[0] <= max_w:
            line = test
        else:
            if line:
                img = fnt.render(line, True, colour)
                screen.blit(img, (x, y))
                y += img.get_height() + gap
            line = word
    if line:
        img = fnt.render(line, True, colour)
        screen.blit(img, (x, y))
        y += img.get_height() + gap
    return y
def draw_button(rect, text, mouse_pos):
    colour = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN
    pygame.draw.rect(screen, colour, rect, border_radius=8)
    pygame.draw.rect(screen, BORDER, rect, 2, border_radius=8)
    label = font.render(text, True, BLACK)
    screen.blit(label, label.get_rect(center=rect.center))
def clear_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            grid[y][x] = 0
def grid_has_pixels(bitmap):
    for row in bitmap:
        for value in row:
            if value:
                return True
    return False
def mouse_to_grid(pos, layout):
    mx, my = pos
    gx = (mx - layout["grid_left"]) // layout["cell"]
    gy = (my - layout["grid_top"]) // layout["cell"]
    return (int(gx), int(gy)) if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE else None
def draw_brush(gx, gy, value):
    for dy in range(-brush_size, brush_size + 1):
        for dx in range(-brush_size, brush_size + 1):
            if dx * dx + dy * dy <= brush_size * brush_size:
                nx, ny = gx + dx, gy + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    grid[ny][nx] = value
def empty_bitmap(size):
    return [[0 for _ in range(size)] for _ in range(size)]
def empty_bitmap_wh(width, height):
    return [[0 for _ in range(width)] for _ in range(height)]
def flatten_bitmap(bitmap):
    return [value for row in bitmap for value in row]
def unflatten_bitmap(data, size=50):
    return [data[row * size:(row + 1) * size] for row in range(size)]
def normalize_bitmap(bitmap, out_size=50, max_fill=42):
    h = len(bitmap)
    if h == 0:
        return empty_bitmap(out_size)
    w = len(bitmap[0])
    points = [(x, y) for y in range(h) for x in range(w) if bitmap[y][x]]
    if not points:
        return empty_bitmap(out_size)
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    crop = [bitmap[y][min_x:max_x + 1] for y in range(min_y, max_y + 1)]
    crop_h, crop_w = len(crop), len(crop[0])
    scale = max_fill / max(crop_w, crop_h)
    new_w = max(1, int(round(crop_w * scale)))
    new_h = max(1, int(round(crop_h * scale)))
    resized = empty_bitmap_wh(new_w, new_h)
    for y in range(new_h):
        sy = min(crop_h - 1, int(y * crop_h / new_h))
        for x in range(new_w):
            sx = min(crop_w - 1, int(x * crop_w / new_w))
            resized[y][x] = crop[sy][sx]
    output = empty_bitmap(out_size)
    start_x = (out_size - new_w) // 2
    start_y = (out_size - new_h) // 2
    for y in range(new_h):
        for x in range(new_w):
            output[start_y + y][start_x + x] = resized[y][x]
    return output
def dilate_bitmap(bitmap, radius=1):
    h, w = len(bitmap), len(bitmap[0])
    output = empty_bitmap_wh(w, h)
    for y in range(h):
        for x in range(w):
            if bitmap[y][x]:
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        if dx * dx + dy * dy <= radius * radius:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                output[ny][nx] = 1
    return output
def count_pixels(bitmap):
    return sum(1 for row in bitmap for value in row if value)
def soft_distance(a, b):
    a_d = dilate_bitmap(a, 1)
    b_d = dilate_bitmap(b, 1)
    a_count = count_pixels(a)
    b_count = count_pixels(b)
    if a_count == 0 or b_count == 0:
        return 1.0
    match_a, match_b = 0, 0
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if a[y][x] and b_d[y][x]:
                match_a += 1
            if b[y][x] and a_d[y][x]:
                match_b += 1
    similarity = (match_a + match_b) / (a_count + b_count)
    return 1.0 - similarity
def create_font_templates():
    templates = []
    for index, khmer_digit in enumerate(KHMER_DIGITS):
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        surf.fill((255, 255, 255, 0))
        text = template_font.render(khmer_digit, True, BLACK)
        surf.blit(text, text.get_rect(center=(60, 60)))
        bitmap = empty_bitmap_wh(120, 120)
        for y in range(120):
            for x in range(120):
                r, g, b, a = surf.get_at((x, y))
                if a > 30 and (r + g + b) < 500:
                    bitmap[y][x] = 1
        templates.append({
            "label": str(index), "char": khmer_digit,
            "bitmap": normalize_bitmap(bitmap, GRID_SIZE, FILL_SIZE),
            "source": "font",
        })
    return templates
def load_user_templates():
    if not os.path.exists(TEMPLATE_FILE):
        return []
    try:
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        templates = []
        for item in data:
            label, pixels = str(item["label"]), item["pixels"]
            if len(pixels) == GRID_SIZE * GRID_SIZE:
                templates.append({
                    "label": label, "char": KHMER_DIGITS[int(label)],
                    "bitmap": unflatten_bitmap(pixels, GRID_SIZE),
                    "source": "user",
                })
        return templates
    except Exception:
        return []
def save_user_templates():
    data = []
    for item in user_templates:
        data.append({
            "label": item["label"],
            "char": item["char"],
            "pixels": flatten_bitmap(item["bitmap"]),
        })
    with open(TEMPLATE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
font_templates = create_font_templates()
user_templates = load_user_templates()
def recognise_current_grid():
    if not grid_has_pixels(grid):
        return None, None, "Draw something first"
    templates = font_templates + user_templates
    if not templates:
        return None, None, "No templates found. Add Khmer font or train samples."
    current = normalize_bitmap(grid, GRID_SIZE, FILL_SIZE)
    scores = [(soft_distance(current, template["bitmap"]), template) for template in templates]
    scores.sort(key=lambda item: item[0])
    best_score, best_template = scores[0]
    confidence = max(0, min(100, int((1.0 - best_score) * 100)))
    label = best_template["label"]
    char = best_template["char"]
    source = best_template["source"]
    return label, confidence, f"Recognised: {char}  ({label})  source: {source}"
def add_training_sample(label):
    user_templates.append({
        "label": str(label), "char": KHMER_DIGITS[int(label)],
        "bitmap": normalize_bitmap(grid, GRID_SIZE, FILL_SIZE),
        "source": "user",
    })
    save_user_templates()
def draw_grid(layout):
    left, top = layout["grid_left"], layout["grid_top"]
    cell, grid_px = layout["cell"], layout["grid_px"]
    pygame.draw.rect(screen, WHITE, (left, top, grid_px, grid_px))
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x]:
                pygame.draw.rect(screen, BLACK, (left + x * cell, top + y * cell, cell, cell))
    for i in range(GRID_SIZE + 1):
        colour = GRID_DARK if i % 5 == 0 else GRID_LIGHT
        width = 2 if i % 5 == 0 else 1
        x = left + i * cell
        y = top + i * cell
        pygame.draw.line(screen, colour, (x, top), (x, top + grid_px), width)
        pygame.draw.line(screen, colour, (left, y), (left + grid_px, y), width)
    pygame.draw.rect(screen, BORDER, (left, top, grid_px, grid_px), 3)
    label = small_font.render("Draw here: 50 x 50 pixel grid", True, MUTED)
    screen.blit(label, (left, top - 26))
def draw_preview(x, y, max_w):
    preview_size = min(150, max_w)
    pixel = max(1, preview_size // GRID_SIZE)
    preview_size = pixel * GRID_SIZE
    y = draw_text("Normalised preview", small_font, MUTED, x, y)
    y += 8
    pygame.draw.rect(screen, WHITE, (x, y, preview_size, preview_size))
    pygame.draw.rect(screen, BORDER, (x, y, preview_size, preview_size), 2)
    normalised = normalize_bitmap(grid, GRID_SIZE, FILL_SIZE)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if normalised[row][col]:
                pygame.draw.rect(screen, BLACK, (x + col * pixel, y + row * pixel, pixel, pixel))
    return y + preview_size + 18
def draw_training_box(x, y, width):
    if not training_mode:
        return y
    box = pygame.Rect(x, y, width, 64)
    pygame.draw.rect(screen, YELLOW, box, border_radius=8)
    pygame.draw.rect(screen, BORDER, box, 2, border_radius=8)
    screen.blit(small_font.render("Training mode", True, TEXT), (x + 10, y + 8))
    screen.blit(small_font.render("Press 0-9 to save this drawing", True, TEXT), (x + 10, y + 34))
    return y + 80
def draw_help(x, y, width):
    y = draw_text("How to use", small_font, TEXT, x, y)
    y += 8
    help_lines = [
        "Left click = draw", "Right click = erase", "R = recognise",
        "C = clear", "T = train sample",
        "After pressing T, press 0-9 to save the correct Khmer digit.",
        "Add 3 to 5 samples for each digit to improve accuracy.",
    ]
    for line in help_lines:
        y = draw_wrapped(line, tiny_font, MUTED, x, y, width, gap=4)
def draw_status(layout):
    y = layout["win_h"] - 26
    if KHMER_FONT_PATH:
        text = f"Khmer font loaded: fonts/{os.path.basename(KHMER_FONT_PATH)}"
        colour = GREEN
    else:
        text = "No Khmer font found. Put a .ttf or .otf Khmer font inside the fonts folder."
        colour = RED
    screen.blit(tiny_font.render(text, True, colour), (MARGIN, y))
def draw_panel(layout):
    global recognise_btn, clear_btn, train_btn
    panel_rect = pygame.Rect(layout["panel_x"], layout["panel_y"], layout["panel_w"], layout["panel_h"])
    pygame.draw.rect(screen, PANEL_BG, panel_rect, border_radius=14)
    pygame.draw.rect(screen, (220, 224, 230), panel_rect, 2, border_radius=14)
    x, y = layout["panel_x"] + 18, layout["panel_y"] + 18
    width = layout["panel_w"] - 36
    mouse_pos = pygame.mouse.get_pos()
    y = draw_text("Control Panel", font, TEXT, x, y)
    y += 12
    y = draw_wrapped("Digits: " + " ".join(KHMER_DIGITS), font, TEXT, x, y, width)
    y += 14
    recognise_btn = pygame.Rect(x, y, width, 42)
    draw_button(recognise_btn, "Recognise  (R)", mouse_pos)
    y += 52
    clear_btn = pygame.Rect(x, y, width, 42)
    draw_button(clear_btn, "Clear  (C)", mouse_pos)
    y += 52
    train_btn = pygame.Rect(x, y, width, 42)
    draw_button(train_btn, "Train Sample  (T)", mouse_pos)
    y += 60
    y = draw_wrapped(prediction_text, font, BLUE, x, y, width)
    y = draw_wrapped(prediction_score, small_font, GREEN, x, y, width)
    y += 8
    y = draw_wrapped(f"Brush size: {brush_size}    [ smaller   ] bigger", small_font, MUTED, x, y, width)
    y = draw_text(f"Saved user templates: {len(user_templates)}", small_font, MUTED, x, y + 4)
    y += 14
    y = draw_training_box(x, y, width)
    y = draw_preview(x, y, width)
    draw_help(x, y, width)
def draw_ui():
    layout = get_layout()
    screen.fill(BG)
    title = title_font.render("Khmer Number Recognition - 50 x 50 Pixel Grid", True, TEXT)
    screen.blit(title, (MARGIN, 16))
    draw_grid(layout)
    draw_panel(layout)
    draw_status(layout)
    return layout
def do_recognition():
    global prediction_text, prediction_score
    label, confidence, message = recognise_current_grid()
    prediction_text = message
    prediction_score = "" if confidence is None else f"Confidence: {confidence}%"
def do_clear():
    global prediction_text, prediction_score, training_mode
    clear_grid()
    training_mode = False
    prediction_text = "Grid cleared"
    prediction_score = ""
def start_training():
    global prediction_text, prediction_score, training_mode
    if not grid_has_pixels(grid):
        prediction_text = "Draw a number before training"
        prediction_score = ""
        return
    training_mode = True
    prediction_text = "Training mode"
    prediction_score = "Press keyboard 0-9 to label this drawing"
def save_training_digit(digit):
    global prediction_text, prediction_score, training_mode
    add_training_sample(digit)
    training_mode = False
    prediction_text = f"Saved as Khmer digit {KHMER_DIGITS[int(digit)]} ({digit})"
    prediction_score = f"Total user templates: {len(user_templates)}"
def handle_mouse_down(event, layout):
    if recognise_btn and recognise_btn.collidepoint(event.pos):
        do_recognition()
        return
    if clear_btn and clear_btn.collidepoint(event.pos):
        do_clear()
        return
    if train_btn and train_btn.collidepoint(event.pos):
        start_training()
        return
    gp = mouse_to_grid(event.pos, layout)
    if gp:
        gx, gy = gp
        if event.button == 1:
            draw_brush(gx, gy, 1)
        elif event.button == 3:
            draw_brush(gx, gy, 0)
def handle_mouse_motion(event, layout):
    gp = mouse_to_grid(event.pos, layout)
    if not gp:
        return
    gx, gy = gp
    left, middle, right = pygame.mouse.get_pressed()
    if left:
        draw_brush(gx, gy, 1)
    elif right:
        draw_brush(gx, gy, 0)
def handle_key_down(event):
    global running, brush_size
    if event.key == pygame.K_ESCAPE:
        running = False
    elif event.key == pygame.K_r:
        do_recognition()
    elif event.key == pygame.K_c:
        do_clear()
    elif event.key == pygame.K_t:
        start_training()
    elif event.key == pygame.K_LEFTBRACKET:
        brush_size = max(1, brush_size - 1)
    elif event.key == pygame.K_RIGHTBRACKET:
        brush_size = min(MAX_BRUSH, brush_size + 1)
    elif training_mode and event.unicode in "0123456789":
        save_training_digit(event.unicode)
running = True
while running:
    layout = draw_ui()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            new_w = max(event.w, MIN_W)
            new_h = max(event.h, MIN_H)
            screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_down(event, layout)
        elif event.type == pygame.MOUSEMOTION:
            handle_mouse_motion(event, layout)
        elif event.type == pygame.KEYDOWN:
            handle_key_down(event)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()