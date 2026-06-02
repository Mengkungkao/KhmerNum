import pygame
import json
import os

pygame.init()

GRID_SIZE = 50
CELL_SIZE = 12
GRID_LEFT = 30
GRID_TOP = 55
GRID_PIXEL_SIZE = GRID_SIZE * CELL_SIZE

WINDOW_W = 960
WINDOW_H = 720
PANEL_X = GRID_LEFT + GRID_PIXEL_SIZE + 35

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREY = (210, 210, 210)
LIGHT_GREY = (238, 238, 238)
DARK_GREY = (90, 90, 90)
BLUE = (40, 100, 210)
GREEN = (30, 150, 90)
YELLOW = (255, 245, 180)

KHMER_DIGITS = ["០", "១", "២", "៣", "៤", "៥", "៦", "៧", "៨", "៩"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, "khmer_digit_templates.json")

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
pygame.display.set_caption("50x50 Khmer Number Recognition")

clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 16)
big_font = pygame.font.SysFont("arial", 34)

grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

brush_size = 1
prediction_text = "Draw a Khmer number"
prediction_score = ""
training_mode = False


def clear_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            grid[y][x] = 0


def draw_brush(gx, gy, value):
    radius = brush_size

    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy <= radius * radius:
                nx = gx + dx
                ny = gy + dy

                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    grid[ny][nx] = value


def mouse_to_grid(pos):
    mx, my = pos

    gx = (mx - GRID_LEFT) // CELL_SIZE
    gy = (my - GRID_TOP) // CELL_SIZE

    if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
        return int(gx), int(gy)

    return None


def bitmap_has_pixels(bitmap):
    return any(any(row) for row in bitmap)


def normalize_bitmap(bitmap, out_size=50, max_fill=42):
    h = len(bitmap)
    w = len(bitmap[0]) if h else 0

    points = []

    for y in range(h):
        for x in range(w):
            if bitmap[y][x]:
                points.append((x, y))

    if not points:
        return [[0 for _ in range(out_size)] for _ in range(out_size)]

    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)

    crop = []

    for y in range(min_y, max_y + 1):
        crop.append(bitmap[y][min_x:max_x + 1])

    crop_h = len(crop)
    crop_w = len(crop[0])

    scale = max_fill / max(crop_w, crop_h)
    new_w = max(1, int(round(crop_w * scale)))
    new_h = max(1, int(round(crop_h * scale)))

    resized = [[0 for _ in range(new_w)] for _ in range(new_h)]

    for y in range(new_h):
        src_y = min(crop_h - 1, int(y * crop_h / new_h))

        for x in range(new_w):
            src_x = min(crop_w - 1, int(x * crop_w / new_w))
            resized[y][x] = crop[src_y][src_x]

    output = [[0 for _ in range(out_size)] for _ in range(out_size)]

    start_x = (out_size - new_w) // 2
    start_y = (out_size - new_h) // 2

    for y in range(new_h):
        for x in range(new_w):
            output[start_y + y][start_x + x] = resized[y][x]

    return output


def flatten(bitmap):
    return [pixel for row in bitmap for pixel in row]


def unflatten(data, size=50):
    return [data[i * size:(i + 1) * size] for i in range(size)]


def dilate_bitmap(bitmap, radius=1):
    h = len(bitmap)
    w = len(bitmap[0])

    output = [[0 for _ in range(w)] for _ in range(h)]

    for y in range(h):
        for x in range(w):
            if bitmap[y][x]:
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        if dx * dx + dy * dy <= radius * radius:
                            nx = x + dx
                            ny = y + dy

                            if 0 <= nx < w and 0 <= ny < h:
                                output[ny][nx] = 1

    return output


def soft_distance(a, b):
    a_d = dilate_bitmap(a, 1)
    b_d = dilate_bitmap(b, 1)

    a_count = sum(sum(row) for row in a)
    b_count = sum(sum(row) for row in b)

    if a_count == 0 or b_count == 0:
        return 1.0

    match_a = 0
    match_b = 0

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if a[y][x] and b_d[y][x]:
                match_a += 1

            if b[y][x] and a_d[y][x]:
                match_b += 1

    similarity = (match_a + match_b) / (a_count + b_count)

    return 1.0 - similarity


def load_user_templates():
    if not os.path.exists(TEMPLATE_FILE):
        return []

    try:
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        templates = []

        for item in data:
            label = str(item["label"])
            pixels = item["pixels"]

            if len(pixels) == GRID_SIZE * GRID_SIZE:
                templates.append({
                    "label": label,
                    "char": KHMER_DIGITS[int(label)],
                    "bitmap": unflatten(pixels),
                    "source": "user"
                })

        return templates

    except Exception:
        return []


def save_user_templates(user_templates):
    data = []

    for item in user_templates:
        data.append({
            "label": item["label"],
            "char": item["char"],
            "pixels": flatten(item["bitmap"])
        })

    with open(TEMPLATE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def create_font_templates():
    candidate_fonts = [
        "khmer ui",
        "daunpenh",
        "noto sans khmer",
        "khmer os",
        "arial unicode ms",
        "arial"
    ]

    render_font = None

    for name in candidate_fonts:
        try:
            render_font = pygame.font.SysFont(name, 80)

            if render_font:
                break

        except Exception:
            continue

    if render_font is None:
        render_font = pygame.font.SysFont(None, 80)

    templates = []

    for i, ch in enumerate(KHMER_DIGITS):
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        surf.fill((255, 255, 255, 0))

        text = render_font.render(ch, True, BLACK)
        rect = text.get_rect(center=(60, 60))
        surf.blit(text, rect)

        bitmap = [[0 for _ in range(120)] for _ in range(120)]

        for y in range(120):
            for x in range(120):
                r, g, b, a = surf.get_at((x, y))

                if a > 30 and (r + g + b) < 500:
                    bitmap[y][x] = 1

        normalised = normalize_bitmap(bitmap, GRID_SIZE, 42)

        templates.append({
            "label": str(i),
            "char": ch,
            "bitmap": normalised,
            "source": "font"
        })

    return templates


font_templates = create_font_templates()
user_templates = load_user_templates()


def all_templates():
    return font_templates + user_templates


def recognise_current_grid():
    if not bitmap_has_pixels(grid):
        return None, None, "Draw something first"

    templates = all_templates()

    if not templates:
        return None, None, "No templates found. Press T then 0-9 to train."

    current = normalize_bitmap(grid, GRID_SIZE, 42)

    scores = []

    for template in templates:
        score = soft_distance(current, template["bitmap"])
        scores.append((score, template))

    scores.sort(key=lambda item: item[0])

    best_score, best_template = scores[0]

    confidence = max(0, min(100, int((1.0 - best_score) * 100)))

    label = best_template["label"]
    char = best_template["char"]
    source = best_template["source"]

    return label, confidence, f"Recognised: {char}  ({label})   source: {source}"


def add_training_sample(label):
    normalised = normalize_bitmap(grid, GRID_SIZE, 42)

    user_templates.append({
        "label": str(label),
        "char": KHMER_DIGITS[int(label)],
        "bitmap": normalised,
        "source": "user"
    })

    save_user_templates(user_templates)


def draw_button(rect, text, mouse_pos):
    colour = (230, 230, 230)

    if rect.collidepoint(mouse_pos):
        colour = (210, 225, 255)

    pygame.draw.rect(screen, colour, rect, border_radius=8)
    pygame.draw.rect(screen, DARK_GREY, rect, 2, border_radius=8)

    label = font.render(text, True, BLACK)
    screen.blit(label, label.get_rect(center=rect.center))


def draw_grid():
    pygame.draw.rect(
        screen,
        WHITE,
        (GRID_LEFT, GRID_TOP, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
    )

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            px = GRID_LEFT + x * CELL_SIZE
            py = GRID_TOP + y * CELL_SIZE

            if grid[y][x]:
                pygame.draw.rect(
                    screen,
                    BLACK,
                    (px, py, CELL_SIZE, CELL_SIZE)
                )

    for i in range(GRID_SIZE + 1):
        line_colour = GREY if i % 5 == 0 else LIGHT_GREY
        width = 2 if i % 5 == 0 else 1

        x = GRID_LEFT + i * CELL_SIZE
        y = GRID_TOP + i * CELL_SIZE

        pygame.draw.line(
            screen,
            line_colour,
            (x, GRID_TOP),
            (x, GRID_TOP + GRID_PIXEL_SIZE),
            width
        )

        pygame.draw.line(
            screen,
            line_colour,
            (GRID_LEFT, y),
            (GRID_LEFT + GRID_PIXEL_SIZE, y),
            width
        )

    pygame.draw.rect(
        screen,
        DARK_GREY,
        (GRID_LEFT, GRID_TOP, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE),
        3
    )


def draw_preview():
    preview_size = 150
    preview_left = PANEL_X
    preview_top = 345
    pixel = preview_size // GRID_SIZE

    pygame.draw.rect(
        screen,
        WHITE,
        (preview_left, preview_top, preview_size, preview_size)
    )

    pygame.draw.rect(
        screen,
        DARK_GREY,
        (preview_left, preview_top, preview_size, preview_size),
        2
    )

    normalised = normalize_bitmap(grid, GRID_SIZE, 42)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if normalised[y][x]:
                pygame.draw.rect(
                    screen,
                    BLACK,
                    (
                        preview_left + x * pixel,
                        preview_top + y * pixel,
                        pixel,
                        pixel
                    )
                )

    title = small_font.render("Normalised 50x50 preview", True, DARK_GREY)
    screen.blit(title, (preview_left, preview_top - 24))


def draw_ui():
    screen.fill((248, 248, 248))

    title = big_font.render(
        "Khmer Number Recognition - 50 x 50 Pixel Grid",
        True,
        BLACK
    )

    screen.blit(title, (30, 12))

    draw_grid()

    mouse_pos = pygame.mouse.get_pos()

    recognise_btn = pygame.Rect(PANEL_X, 80, 210, 42)
    clear_btn = pygame.Rect(PANEL_X, 135, 210, 42)
    train_btn = pygame.Rect(PANEL_X, 190, 210, 42)

    draw_button(recognise_btn, "Recognise  (R)", mouse_pos)
    draw_button(clear_btn, "Clear  (C)", mouse_pos)
    draw_button(train_btn, "Train Sample  (T)", mouse_pos)

    y = 260

    screen.blit(font.render(prediction_text, True, BLUE), (PANEL_X, y))
    screen.blit(font.render(prediction_score, True, GREEN), (PANEL_X, y + 32))

    y += 78

    screen.blit(
        small_font.render(f"Brush size: {brush_size}   use [ and ]", True, DARK_GREY),
        (PANEL_X, y)
    )

    screen.blit(
        small_font.render(f"User templates saved: {len(user_templates)}", True, DARK_GREY),
        (PANEL_X, y + 24)
    )

    if training_mode:
        box = pygame.Rect(PANEL_X, y + 58, 250, 58)

        pygame.draw.rect(screen, YELLOW, box, border_radius=8)
        pygame.draw.rect(screen, DARK_GREY, box, 2, border_radius=8)

        screen.blit(
            small_font.render("Training mode:", True, BLACK),
            (PANEL_X + 10, y + 66)
        )

        screen.blit(
            small_font.render("Press keyboard 0-9 to save", True, BLACK),
            (PANEL_X + 10, y + 90)
        )

    draw_preview()

    help_y = 535

    help_lines = [
        "How to use:",
        "1. Draw one Khmer number: ០ ១ ២ ៣ ៤ ៥ ៦ ៧ ៨ ៩",
        "2. Press R to recognise it.",
        "3. For better accuracy: draw a digit, press T,",
        "   then press the matching key 0-9 to save it.",
        "4. Add 3-5 samples for each number if possible.",
        "Left click = draw | Right click = erase"
    ]

    for i, line in enumerate(help_lines):
        colour = BLACK if i == 0 else DARK_GREY

        screen.blit(
            small_font.render(line, True, colour),
            (PANEL_X, help_y + i * 22)
        )

    return recognise_btn, clear_btn, train_btn


running = True

while running:
    recognise_btn, clear_btn, train_btn = draw_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(
                (event.w, event.h),
                pygame.RESIZABLE
            )

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if recognise_btn.collidepoint(event.pos):
                label, confidence, text = recognise_current_grid()

                prediction_text = text
                prediction_score = "" if confidence is None else f"Confidence: {confidence}%"

            elif clear_btn.collidepoint(event.pos):
                clear_grid()

                prediction_text = "Grid cleared"
                prediction_score = ""

            elif train_btn.collidepoint(event.pos):
                if bitmap_has_pixels(grid):
                    training_mode = True

                    prediction_text = "Training mode"
                    prediction_score = "Press 0-9 to label this drawing"

                else:
                    prediction_text = "Draw a number before training"
                    prediction_score = ""

            else:
                gp = mouse_to_grid(event.pos)

                if gp:
                    gx, gy = gp

                    if event.button == 1:
                        draw_brush(gx, gy, 1)

                    elif event.button == 3:
                        draw_brush(gx, gy, 0)

        elif event.type == pygame.MOUSEMOTION:
            gp = mouse_to_grid(event.pos)

            if gp:
                gx, gy = gp
                buttons = pygame.mouse.get_pressed()

                if buttons[0]:
                    draw_brush(gx, gy, 1)

                elif buttons[2]:
                    draw_brush(gx, gy, 0)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_c:
                clear_grid()

                prediction_text = "Grid cleared"
                prediction_score = ""

            elif event.key == pygame.K_r:
                label, confidence, text = recognise_current_grid()

                prediction_text = text
                prediction_score = "" if confidence is None else f"Confidence: {confidence}%"

            elif event.key == pygame.K_t:
                if bitmap_has_pixels(grid):
                    training_mode = True

                    prediction_text = "Training mode"
                    prediction_score = "Press 0-9 to label this drawing"

                else:
                    prediction_text = "Draw a number before training"
                    prediction_score = ""

            elif event.key == pygame.K_LEFTBRACKET:
                brush_size = max(1, brush_size - 1)

            elif event.key == pygame.K_RIGHTBRACKET:
                brush_size = min(5, brush_size + 1)

            elif training_mode and event.unicode in "0123456789":
                add_training_sample(event.unicode)

                training_mode = False

                prediction_text = (
                    f"Saved as Khmer digit "
                    f"{KHMER_DIGITS[int(event.unicode)]} ({event.unicode})"
                )

                prediction_score = f"Total user templates: {len(user_templates)}"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()