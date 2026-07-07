import pygame
import random
import sys
import math
import os
from enum import Enum

pygame.init()

def load_chinese_font(size):
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
GRID_SIZE = 25
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = (WINDOW_HEIGHT - 100) // GRID_SIZE
FPS = 8

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BG = (15, 20, 35)
GRID_LINE = (25, 35, 55)
SNAKE_HEAD = (0, 230, 180)
SNAKE_BODY = (0, 180, 140)
SNAKE_TAIL = (0, 140, 110)
FOOD_COLOR = (255, 80, 80)
FOOD_GLOW = (255, 120, 120)
GOLD = (255, 215, 0)
DARK_GRAY = (40, 50, 70)
LIGHT_GRAY = (180, 195, 220)
MENU_BG = (20, 28, 50)
BUTTON_COLOR = (0, 200, 160)
BUTTON_HOVER = (0, 230, 180)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("贪吃蛇大作战")
        pygame.key.set_repeat(500, 100)
        self.clock = pygame.time.Clock()
        self.font_large = load_chinese_font(72)
        self.font_medium = load_chinese_font(42)
        self.font_small = load_chinese_font(28)
        self.font_score = load_chinese_font(36)
        self.reset_game()
        self.state = GameState.MENU
        self.shake_offset = [0, 0]

    def reset_game(self):
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.high_score = self.load_high_score()
        self.food = self.spawn_food()
        self.animation_frame = 0

    def spawn_food(self):
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake:
                return food

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0

    def save_high_score(self):
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif self.state == GameState.PLAYING:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.state = GameState.PAUSED
                    else:
                        self.change_direction(event.key)
                elif self.state == GameState.PAUSED:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.state = GameState.PLAYING
                elif self.state == GameState.GAME_OVER:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == GameState.MENU:
                    button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 400, 300, 60)
                    if button_rect.collidepoint(event.pos):
                        self.reset_game()
                        self.state = GameState.PLAYING
                elif self.state == GameState.GAME_OVER:
                    restart_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 80, 300, 50)
                    menu_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 150, 300, 50)
                    if restart_rect.collidepoint(event.pos):
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif menu_rect.collidepoint(event.pos):
                        self.state = GameState.MENU

    def change_direction(self, key):
        if key in (pygame.K_UP, pygame.K_w) and self.direction != Direction.DOWN:
            self.next_direction = Direction.UP
        elif key in (pygame.K_DOWN, pygame.K_s) and self.direction != Direction.UP:
            self.next_direction = Direction.DOWN
        elif key in (pygame.K_LEFT, pygame.K_a) and self.direction != Direction.RIGHT:
            self.next_direction = Direction.LEFT
        elif key in (pygame.K_RIGHT, pygame.K_d) and self.direction != Direction.LEFT:
            self.next_direction = Direction.RIGHT

    def update(self):
        if self.state != GameState.PLAYING:
            return
        self.direction = self.next_direction
        dx, dy = self.direction.value
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.state = GameState.GAME_OVER
            self.shake_offset = [random.randint(-5, 5), random.randint(-5, 5)]
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return
        if new_head in self.snake:
            self.state = GameState.GAME_OVER
            self.shake_offset = [random.randint(-5, 5), random.randint(-5, 5)]
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
        else:
            self.snake.pop()
        self.animation_frame += 1

    def draw_grid(self):
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(x * GRID_SIZE, 100 + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                color = GRID_LINE if (x + y) % 2 == 0 else DARK_BG
                pygame.draw.rect(self.screen, color, rect, 0)
                pygame.draw.rect(self.screen, GRID_LINE, rect, 1)

    def draw_snake(self):
        if not self.snake:
            return
        for i in range(len(self.snake) - 1, -1, -1):
            x, y = self.snake[i]
            center_x = x * GRID_SIZE + GRID_SIZE // 2 + self.shake_offset[0]
            center_y = 100 + y * GRID_SIZE + GRID_SIZE // 2 + self.shake_offset[1]
            radius = GRID_SIZE // 2 - 2
            progress = i / max(len(self.snake) - 1, 1)
            color = self.lerp_color(SNAKE_HEAD, SNAKE_TAIL, 1 - progress)
            pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
            pygame.draw.circle(self.screen, WHITE, (center_x, center_y), radius, 2)
            if i == 0:
                self.draw_snake_head(center_x, center_y, radius)

    def draw_snake_head(self, center_x, center_y, radius):
        dx, dy = self.direction.value
        eye_offset = radius // 3
        eye_size = radius // 4
        if dx == 1:
            eye1 = (center_x + eye_offset, center_y - eye_offset)
            eye2 = (center_x + eye_offset, center_y + eye_offset)
            pupil_offset = eye_size // 2
        elif dx == -1:
            eye1 = (center_x - eye_offset, center_y - eye_offset)
            eye2 = (center_x - eye_offset, center_y + eye_offset)
            pupil_offset = -eye_size // 2
        elif dy == -1:
            eye1 = (center_x - eye_offset, center_y - eye_offset)
            eye2 = (center_x + eye_offset, center_y - eye_offset)
            pupil_offset = -eye_size
        else:
            eye1 = (center_x - eye_offset, center_y + eye_offset)
            eye2 = (center_x + eye_offset, center_y + eye_offset)
            pupil_offset = eye_size
        for ex, ey in [eye1, eye2]:
            pygame.draw.circle(self.screen, WHITE, (ex, ey), eye_size)
            pygame.draw.circle(self.screen, BLACK, 
                (ex + pupil_offset if dx != 0 else ex, ey + pupil_offset if dy != 0 else ey), 
                eye_size // 2)

    def draw_food(self):
        x, y = self.food
        center_x = x * GRID_SIZE + GRID_SIZE // 2 + self.shake_offset[0]
        center_y = 100 + y * GRID_SIZE + GRID_SIZE // 2 + self.shake_offset[1]
        pulse = math.sin(self.animation_frame * 0.1) * 3
        radius = GRID_SIZE // 2 - 2 + pulse
        for glow_radius in range(int(radius) + 8, int(radius), -2):
            alpha = int(100 * (glow_radius - radius) / 8)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*FOOD_GLOW, alpha), (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))
        pygame.draw.circle(self.screen, FOOD_COLOR, (center_x, center_y), int(radius))
        pygame.draw.circle(self.screen, WHITE, (center_x, center_y), int(radius), 2)

    def draw_ui(self):
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game_ui()
        elif self.state == GameState.PAUSED:
            self.draw_pause_screen()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

    def draw_menu(self):
        self.screen.fill(DARK_BG)
        self.draw_grid()
        title_text = self.font_large.render("贪吃蛇大作战", True, GOLD)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
        self.screen.blit(title_text, title_rect)
        subtitle = self.font_medium.render("SNAKE GAME", True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 310))
        self.screen.blit(subtitle, subtitle_rect)
        button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 400, 300, 60)
        self.draw_button(button_rect, "开始游戏")
        instructions = [
            "方向键 / WASD：控制蛇的移动",
            "SPACE / ENTER：开始/重新开始",
            "ESC / P：暂停/继续",
            "",
            "最高分：{}".format(self.high_score)
        ]
        for i, text in enumerate(instructions):
            inst_text = self.font_small.render(text, True, LIGHT_GRAY)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 500 + i * 30))
            self.screen.blit(inst_text, inst_rect)

    def draw_button(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)
        color = BUTTON_HOVER if is_hover else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)
        text_surface = self.font_medium.render(text, True, BLACK if is_hover else DARK_BG)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_game_ui(self):
        ui_panel = pygame.Rect(0, 0, WINDOW_WIDTH, 100)
        pygame.draw.rect(self.screen, MENU_BG, ui_panel)
        pygame.draw.rect(self.screen, GRID_LINE, ui_panel, 2)
        score_text = self.font_score.render(f"得分: {self.score}", True, GOLD)
        self.screen.blit(score_text, (30, 35))
        high_score_text = self.font_score.render(f"最高分: {self.high_score}", True, LIGHT_GRAY)
        self.screen.blit(high_score_text, (250, 35))
        length_text = self.font_score.render(f"长度: {len(self.snake)}", True, SNAKE_HEAD)
        self.screen.blit(length_text, (500, 35))
        hint_text = self.font_small.render("ESC/P 暂停", True, DARK_GRAY)
        self.screen.blit(hint_text, (WINDOW_WIDTH - 150, 50))

    def draw_pause_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        pause_text = self.font_large.render("游戏暂停", True, GOLD)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        hint_text = self.font_medium.render("按 ESC 或 P 继续", True, WHITE)
        hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(hint_text, hint_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        game_over_text = self.font_large.render("游戏结束", True, (255, 80, 80))
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(game_over_text, game_over_rect)
        score_text = self.font_medium.render(f"得分: {self.score}", True, GOLD)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        if self.score >= self.high_score and self.score > 0:
            new_record = self.font_small.render("恭喜！新纪录！", True, FOOD_COLOR)
            record_rect = new_record.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
            self.screen.blit(new_record, record_rect)
        restart_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 80, 300, 50)
        self.draw_button(restart_rect, "重新开始")
        menu_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 150, 300, 50)
        self.draw_button(menu_rect, "返回菜单")

    def lerp_color(self, color1, color2, t):
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.shake_offset = [int(self.shake_offset[0] * 0.8), int(self.shake_offset[1] * 0.8)]
            self.screen.fill(DARK_BG)
            self.draw_grid()
            if self.state == GameState.PLAYING:
                self.draw_snake()
                self.draw_food()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()