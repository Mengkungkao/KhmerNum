import pygame, os, glob
pygame.init()

N = 50
W, H = 1180, 760
MIN_W, MIN_H = 1040, 720
M, TOP, BOT = 24, 66, 34
FPS, FILL, MAX_BRUSH = 60, 42, 5
MIN_PIXELS = 25
MIN_DRAW_W = 8
MIN_DRAW_H = 8
MIN_CONFIDENCE = 55
MIN_SCORE_GAP = 0.03
BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE, "fonts")
os.makedirs(FONT_DIR, exist_ok=True)
DIGITS = ["០", "១", "២", "៣", "៤", "៥", "៦", "៧", "៨", "៩"]
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BG = (248, 248, 248)
PANEL = (242, 244, 248)
BOX = (255, 255, 255)
GRID_L = (228, 228, 228)
GRID_D = (188, 188, 188)
BTN = (230, 230, 230)
BTN_H = (210, 225, 255)
BORDER = (80, 80, 80)
LIGHT = (215, 218, 224)
TEXT = (25, 25, 25)
MUTED = (90, 90, 90)
BLUE = (40, 100, 210)
GREEN = (30, 150, 90)
RED = (200, 50, 50)

screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Khmer Number Recognition - 50x50 Pixel Grid")
clock = pygame.time.Clock()

preferred = [
    "NotoSerifKhmer-Regular.ttf",
]
font_path = None
for f in preferred:
    p = os.path.join(FONT_DIR, f)
    if os.path.exists(p):
        font_path = p
        break
if not font_path:
    found = glob.glob(os.path.join(FONT_DIR, "*.ttf")) + glob.glob(os.path.join(FONT_DIR, "*.otf"))
    font_path = found[0] if found else None

def make_font(size):
    return pygame.font.Font(font_path, size) if font_path else pygame.font.SysFont("arial", size)

title_f = make_font(30)
head_f = make_font(22)
font = make_font(19)
small = make_font(16)
tiny = make_font(14)
template_f = make_font(80)
grid = [[0] * N for _ in range(N)]
brush = 1
message = "Draw any Khmer number"
score_text = ""
recognise_btn = None
clear_btn = None

def layout():
    sw, sh = screen.get_size()
    pw = max(360, min(430, int(sw * 0.33)))
    left_w = sw - pw - M * 3
    left_h = sh - TOP - BOT - M * 2
    cell = max(6, min(left_w // N, left_h // N))
    gp = cell * N
    gx = M + max(0, (left_w - gp) // 2)
    gy = TOP + M + max(0, (left_h - gp) // 2)
    px = sw - pw - M
    py = TOP + M
    ph = sh - py - BOT - M
    return sw, sh, px, py, pw, ph, gx, gy, gp, cell

def box(rect):
    pygame.draw.rect(screen, BOX, rect, border_radius=11)
    pygame.draw.rect(screen, LIGHT, rect, 2, border_radius=11)

def button(rect, label):
    colour = BTN_H if rect.collidepoint(pygame.mouse.get_pos()) else BTN
    pygame.draw.rect(screen, colour, rect, border_radius=9)
    pygame.draw.rect(screen, BORDER, rect, 2, border_radius=9)
    text = font.render(label, True, BLACK)
    screen.blit(text, text.get_rect(center=rect.center))

def wrap(text, fnt, colour, x, y, width, max_lines=99):
    words = text.split()
    line = ""
    lines = 0
    for word in words:
        test = word if not line else line + " " + word

        if fnt.size(test)[0] <= width:
            line = test
        else:
            if line and lines < max_lines:
                img = fnt.render(line, True, colour)
                screen.blit(img, (x, y))
                y += img.get_height() + 4
                lines += 1

            line = word

            if lines >= max_lines:
                return y
    if line and lines < max_lines:
        img = fnt.render(line, True, colour)
        screen.blit(img, (x, y))
    return y

def clear():
    for y in range(N):
        for x in range(N):
            grid[y][x] = 0

def has_pixel(bmp):
    return any(any(row) for row in bmp)

def mouse_grid(pos, lay):
    _, _, _, _, _, _, gx, gy, _, cell = lay

    mx, my = pos
    x = (mx - gx) // cell
    y = (my - gy) // cell

    return (int(x), int(y)) if 0 <= x < N and 0 <= y < N else None

def draw_brush(x, y, val):
    for dy in range(-brush, brush + 1):
        for dx in range(-brush, brush + 1):
            if dx * dx + dy * dy <= brush * brush:
                nx, ny = x + dx, y + dy

                if 0 <= nx < N and 0 <= ny < N:
                    grid[ny][nx] = val

def empty(w, h=None):
    h = w if h is None else h
    return [[0] * w for _ in range(h)]
def drawing_stats(bmp):
    pts = [(x, y) for y in range(N) for x in range(N) if bmp[y][x]]

    if not pts:
        return 0, 0, 0
    min_x = min(x for x, y in pts)
    max_x = max(x for x, y in pts)
    min_y = min(y for x, y in pts)
    max_y = max(y for x, y in pts)

    pixels = len(pts)
    width = max_x - min_x + 1
    height = max_y - min_y + 1

    return pixels, width, height

def normalise(bmp, out=N, fill=FILL):
    h = len(bmp)
    w = len(bmp[0])

    pts = [(x, y) for y in range(h) for x in range(w) if bmp[y][x]]

    if not pts:
        return empty(out)
    min_x = min(x for x, y in pts)
    max_x = max(x for x, y in pts)
    min_y = min(y for x, y in pts)
    max_y = max(y for x, y in pts)
    crop = [bmp[y][min_x:max_x + 1] for y in range(min_y, max_y + 1)]
    ch, cw = len(crop), len(crop[0])
    scale = fill / max(cw, ch)

    nw = max(1, round(cw * scale))
    nh = max(1, round(ch * scale))

    resized = empty(nw, nh)

    for y in range(nh):
        sy = min(ch - 1, int(y * ch / nh))
        for x in range(nw):
            sx = min(cw - 1, int(x * cw / nw))
            resized[y][x] = crop[sy][sx]

    out_bmp = empty(out)

    ox = (out - nw) // 2
    oy = (out - nh) // 2

    for y in range(nh):
        for x in range(nw):
            out_bmp[oy + y][ox + x] = resized[y][x]

    return out_bmp
def dilate(bmp):
    h, w = len(bmp), len(bmp[0])
    out = empty(w, h)

    for y in range(h):
        for x in range(w):
            if bmp[y][x]:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = x + dx, y + dy

                        if 0 <= nx < w and 0 <= ny < h:
                            out[ny][nx] = 1

    return out

def count(bmp):
    return sum(sum(row) for row in bmp)

def make_templates():
    templates = []

    for i, digit in enumerate(DIGITS):
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        surf.fill((255, 255, 255, 0))

        text = template_f.render(digit, True, BLACK)
        surf.blit(text, text.get_rect(center=(60, 60)))

        bmp = empty(120, 120)

        for y in range(120):
            for x in range(120):
                r, g, b, a = surf.get_at((x, y))

                if a > 30 and r + g + b < 500:
                    bmp[y][x] = 1

        templates.append({
            "label": str(i),
            "char": digit,
            "bmp": normalise(bmp)
        })

    return templates

templates = make_templates()
def distance(a, b):
    ad = dilate(a)
    bd = dilate(b)
    ac = count(a)
    bc = count(b)

    if ac == 0 or bc == 0:
        return 1.0

    ma = 0
    mb = 0

    for y in range(N):
        for x in range(N):
            if a[y][x] and bd[y][x]:
                ma += 1

            if b[y][x] and ad[y][x]:
                mb += 1

    return 1 - ((ma + mb) / (ac + bc))

def recognise():
    if not has_pixel(grid):
        return None, None, "Draw something first"

    pixels, draw_w, draw_h = drawing_stats(grid)

    if pixels < MIN_PIXELS or draw_w < MIN_DRAW_W or draw_h < MIN_DRAW_H:
        return None, None, "Unknown drawing"

    current = normalise(grid)
    results = []

    for t in templates:
        results.append((distance(current, t["bmp"]), t))

    results.sort(key=lambda v: v[0])

    best_score, best = results[0]
    second_score, _ = results[1]

    confidence = max(0, min(100, int((1 - best_score) * 100)))
    score_gap = second_score - best_score

    if confidence < MIN_CONFIDENCE or score_gap < MIN_SCORE_GAP:
        return None, None, "Unknown drawing"

    return best["label"], confidence, f"Recognised: {best['char']}  ({best['label']})"

def draw_grid(lay):
    _, _, _, _, _, _, gx, gy, gp, cell = lay

    pygame.draw.rect(screen, WHITE, (gx, gy, gp, gp))

    for y in range(N):
        for x in range(N):
            if grid[y][x]:
                pygame.draw.rect(
                    screen,
                    BLACK,
                    (gx + x * cell, gy + y * cell, cell, cell)
                )

    for i in range(N + 1):
        colour = GRID_D if i % 5 == 0 else GRID_L
        width = 2 if i % 5 == 0 else 1
        x = gx + i * cell
        y = gy + i * cell
        pygame.draw.line(screen, colour, (x, gy), (x, gy + gp), width)
        pygame.draw.line(screen, colour, (gx, y), (gx + gp, y), width)

    pygame.draw.rect(screen, BORDER, (gx, gy, gp, gp), 3)
    screen.blit(small.render("Drawing area: 50 x 50 pixel grid", True, MUTED), (gx, gy - 28))


def draw_preview(x, y, w, h):
    box(pygame.Rect(x, y, w, h))

    screen.blit(small.render("Normalised preview", True, TEXT), (x + 12, y + 8))

    size = max(90, min(h - 52, w - 24))
    pix = max(1, size // N)
    size = pix * N

    px = x + (w - size) // 2
    py = y + 42

    pygame.draw.rect(screen, WHITE, (px, py, size, size))
    pygame.draw.rect(screen, BORDER, (px, py, size, size), 2)

    bmp = normalise(grid)

    for row in range(N):
        for col in range(N):
            if bmp[row][col]:
                pygame.draw.rect(
                    screen,
                    BLACK,
                    (px + col * pix, py + row * pix, pix, pix)
                )

def draw_panel(lay):
    global recognise_btn, clear_btn

    sw, sh, px, py, pw, ph, *_ = lay

    pygame.draw.rect(screen, PANEL, (px, py, pw, ph), border_radius=14)
    pygame.draw.rect(screen, LIGHT, (px, py, pw, ph), 2, border_radius=14)

    x = px + 18
    y = py + 16
    w = pw - 36

    gap = 10
    title_h = 32
    digit_h = 58
    btn_h = 44
    result_h = 86
    control_h = 112

    screen.blit(head_f.render("Control Panel", True, TEXT), (x, y))
    y += title_h

    box(pygame.Rect(x, y, w, digit_h))

    screen.blit(small.render("Khmer digits", True, TEXT), (x + 12, y + 8))
    screen.blit(font.render(" ".join(DIGITS), True, BLACK), (x + 12, y + 31))

    y += digit_h + gap

    bw = (w - gap) // 2

    recognise_btn = pygame.Rect(x, y, bw, btn_h)
    clear_btn = pygame.Rect(x + bw + gap, y, bw, btn_h)

    button(recognise_btn, "Recognise")
    button(clear_btn, "Clear")

    y += btn_h + gap

    box(pygame.Rect(x, y, w, result_h))

    screen.blit(small.render("Result", True, TEXT), (x + 12, y + 8))
    wrap(message, font, BLUE, x + 12, y + 34, w - 24, 2)

    if score_text:
        screen.blit(small.render(score_text, True, GREEN), (x + 12, y + result_h - 28))

    y += result_h + gap
    control_y = py + ph - 16 - control_h
    preview_h = max(150, control_y - y - gap)
    draw_preview(x, y, w, preview_h)
    box(pygame.Rect(x, control_y, w, control_h))
    screen.blit(small.render("Controls", True, TEXT), (x + 12, control_y + 8))
    left = ["Left click: draw", "Right click: erase", "R: recognise", "C: clear"]
    right = ["[: smaller brush", "]: bigger brush", "ESC: close"]

    for i, item in enumerate(left):
        screen.blit(tiny.render(item, True, MUTED), (x + 12, control_y + 36 + i * 19))

    for i, item in enumerate(right):
        screen.blit(tiny.render(item, True, MUTED), (x + w // 2 + 10, control_y + 36 + i * 19))

def draw_ui():
    lay = layout()
    screen.fill(BG)
    screen.blit(
        title_f.render("Khmer Number Recognition - 50 x 50 Pixel Grid", True, TEXT),
        (M, 18)
    )
    draw_grid(lay)
    draw_panel(lay)

    colour = GREEN if font_path else RED
    status = f"Khmer font loaded: fonts/{os.path.basename(font_path)}" if font_path else "No Khmer font found in fonts folder."

    screen.blit(tiny.render(status, True, colour), (M, lay[1] - 27))

    return lay

def do_recognise():
    global message, score_text

    _, confidence, msg = recognise()

    message = msg
    score_text = "" if confidence is None else f"Confidence: {confidence}%"

def do_clear():
    global message, score_text
    clear()
    message = "Grid cleared. Draw again."
    score_text = ""
running = True

while running:
    lay = draw_ui()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        elif e.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(
                (max(e.w, MIN_W), max(e.h, MIN_H)),
                pygame.RESIZABLE
            )

        elif e.type == pygame.MOUSEBUTTONDOWN:
            if recognise_btn and recognise_btn.collidepoint(e.pos):
                do_recognise()

            elif clear_btn and clear_btn.collidepoint(e.pos):
                do_clear()

            else:
                p = mouse_grid(e.pos, lay)

                if p:
                    if e.button == 1:
                        draw_brush(*p, 1)

                    elif e.button == 3:
                        draw_brush(*p, 0)

        elif e.type == pygame.MOUSEMOTION:
            p = mouse_grid(e.pos, lay)

            if p:
                left, _, right = pygame.mouse.get_pressed()

                if left:
                    draw_brush(*p, 1)

                elif right:
                    draw_brush(*p, 0)

        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False

            elif e.key == pygame.K_r:
                do_recognise()

            elif e.key == pygame.K_c:
                do_clear()

            elif e.key == pygame.K_LEFTBRACKET:
                brush = max(1, brush - 1)

            elif e.key == pygame.K_RIGHTBRACKET:
                brush = min(MAX_BRUSH, brush + 1)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
