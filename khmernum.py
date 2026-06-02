import pygame
import sys

# -----------------------------
# Basic settings
# -----------------------------
ROWS = 50
COLS = 50

BOX_SIZE = 10
GAP = 0
MARGIN = 5

SCREEN_WIDTH = COLS * BOX_SIZE + (COLS - 1) * GAP + MARGIN * 2
SCREEN_HEIGHT = ROWS * BOX_SIZE + (ROWS - 1) * GAP + MARGIN * 2 + 60

# Colours
BACKGROUND = (30, 30, 30)
BOX_OFF = (230, 230, 230)
BOX_ON = (0, 200, 100)
GRID_LINE = (80, 80, 80)
TEXT_COLOUR = (255, 255, 255)

# -----------------------------
# Initialise pygame
# -----------------------------
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("100 x100 Pixel Panel")

font = pygame.font.SysFont(None, 28)

# Store pixel states
# False = OFF, True = ON
pixels = [[False for _ in range(COLS)] for _ in range(ROWS)]


def draw_panel():
    screen.fill(BACKGROUND)

    title = font.render("Khmer Number Indentifier", True, TEXT_COLOUR)
    screen.blit(title, (MARGIN, 10))

    for row in range(ROWS):
        for col in range(COLS):
            x = MARGIN + col * (BOX_SIZE + GAP)
            y = MARGIN + 40 + row * (BOX_SIZE + GAP)

            colour = BOX_ON if pixels[row][col] else BOX_OFF

            pygame.draw.rect(screen, colour, (x, y, BOX_SIZE, BOX_SIZE))
            pygame.draw.rect(screen, GRID_LINE, (x, y, BOX_SIZE, BOX_SIZE), 2)

    pygame.display.update()


def get_clicked_box(mouse_pos):
    mx, my = mouse_pos

    for row in range(ROWS):
        for col in range(COLS):
            x = MARGIN + col * (BOX_SIZE + GAP)
            y = MARGIN + 40 + row * (BOX_SIZE + GAP)

            box_rect = pygame.Rect(x, y, BOX_SIZE, BOX_SIZE)

            if box_rect.collidepoint(mx, my):
                return row, col

    return None


def print_pixel_data():
    print("\nPixel Pattern:")
    for row in pixels:
        line = ""
        for pixel in row:
            line += "1 " if pixel else "0 "
        print(line)


# -----------------------------
# Main loop
# -----------------------------
running = True

while running:
    draw_panel()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked_box = get_clicked_box(event.pos)

            if clicked_box is not None:
                row, col = clicked_box

                # Toggle pixel ON/OFF
                pixels[row][col] = not pixels[row][col]

                print_pixel_data()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                # Clear all pixels
                pixels = [[False for _ in range(COLS)] for _ in range(ROWS)]
                print("\nPanel cleared.")

            elif event.key == pygame.K_ESCAPE:
                running = False

pygame.quit()
sys.exit()