"""
Main application module for Khmer Number Identifier
"""
import pygame
import sys


class KhmerNumApp:
    """Khmer Number Identifier Application"""
    
    def __init__(self, rows=50, cols=50):
        """
        Initialize the Khmer Number Identifier app
        
        Args:
            rows: Number of rows in the grid (default: 50)
            cols: Number of columns in the grid (default: 50)
        """
        self.rows = rows
        self.cols = cols
        self.box_size = 10
        self.gap = 0
        self.margin = 5
        
        # Colors
        self.background = (30, 30, 30)
        self.box_off = (230, 230, 230)
        self.box_on = (0, 200, 100)
        self.grid_line = (80, 80, 80)
        self.text_colour = (255, 255, 255)
        
        # Calculate screen dimensions
        self.screen_width = (
            self.cols * self.box_size +
            (self.cols - 1) * self.gap +
            self.margin * 2
        )
        self.screen_height = (
            self.rows * self.box_size +
            (self.rows - 1) * self.gap +
            self.margin * 2 + 60
        )
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption("Khmer Number Identifier")
        
        self.font = pygame.font.SysFont(None, 28)
        
        # Pixel states: False = OFF, True = ON
        self.pixels = [
            [False for _ in range(self.cols)] for _ in range(self.rows)
        ]
    
    def draw_panel(self):
        """Draw the pixel grid panel"""
        self.screen.fill(self.background)
        
        title = self.font.render(
            "Khmer Number Identifier",
            True,
            self.text_colour
        )
        self.screen.blit(title, (self.margin, 10))
        
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.margin + col * (self.box_size + self.gap)
                y = self.margin + 40 + row * (self.box_size + self.gap)
                
                colour = (
                    self.box_on if self.pixels[row][col]
                    else self.box_off
                )
                
                pygame.draw.rect(
                    self.screen, colour,
                    (x, y, self.box_size, self.box_size)
                )
                pygame.draw.rect(
                    self.screen, self.grid_line,
                    (x, y, self.box_size, self.box_size), 2
                )
        
        pygame.display.update()
    
    def get_clicked_box(self, mouse_pos):
        """
        Get which pixel box was clicked
        
        Args:
            mouse_pos: (x, y) tuple of mouse position
            
        Returns:
            (row, col) tuple or None if no box clicked
        """
        mx, my = mouse_pos
        
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.margin + col * (self.box_size + self.gap)
                y = self.margin + 40 + row * (self.box_size + self.gap)
                
                box_rect = pygame.Rect(
                    x, y, self.box_size, self.box_size
                )
                
                if box_rect.collidepoint(mx, my):
                    return row, col
        
        return None
    
    def print_pixel_data(self):
        """Print the current pixel pattern"""
        print("\nPixel Pattern:")
        for row in self.pixels:
            line = ""
            for pixel in row:
                line += "1 " if pixel else "0 "
            print(line)
    
    def clear_panel(self):
        """Clear all pixels"""
        self.pixels = [
            [False for _ in range(self.cols)] for _ in range(self.rows)
        ]
        print("\nPanel cleared.")
    
    def run(self):
        """Run the application main loop"""
        running = True
        
        while running:
            self.draw_panel()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    clicked_box = self.get_clicked_box(event.pos)
                    
                    if clicked_box is not None:
                        row, col = clicked_box
                        self.pixels[row][col] = not self.pixels[row][col]
                        self.print_pixel_data()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.clear_panel()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
        
        pygame.quit()
        sys.exit()


def main():
    """Main entry point"""
    app = KhmerNumApp()
    app.run()


if __name__ == "__main__":
    main()
