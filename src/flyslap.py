import pygame
import random
import sys
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 700
FPS = 60
GAME_TIME = 60
INITIAL_FLIES = 3
MAX_FLIES = 15

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
YELLOW = (241, 196, 15)
GRAY = (149, 165, 166)
DARK_BLUE = (41, 128, 185)
LIGHT_GREEN = (144, 238, 144)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
icon = pygame.image.load("../assets/icons/flyslapicon.ico")
pygame.display.set_icon(icon)
pygame.display.set_caption("Fly Slap!")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 56)
small_font = pygame.font.Font(None, 32)
tiny_font = pygame.font.Font(None, 24)

def make_sound(frequency, duration=100):
    try:
        sample_rate = 22050
        n_samples = int(duration * sample_rate / 1000)
        buf = []
        for i in range(n_samples):
            value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
            buf.append([value, value])
        sound = pygame.sndarray.make_sound(pygame.array.array('h', [item for sublist in buf for item in sublist]))
        return sound
    except:
        return None

hit_sound = make_sound(800, 50)
miss_sound = make_sound(200, 100)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-8, -2)
        self.color = color
        self.life = 30
        self.size = random.randint(3, 6)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.life -= 1
        self.size = max(1, self.size - 0.1)
        
    def draw(self, screen):
        alpha = int(255 * (self.life / 30))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class Fly:
    def __init__(self, level=1):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(100, HEIGHT - 50)
        self.base_size = random.randint(12, 20)
        self.size = self.base_size
        self.speed = 2 + level * 0.3
        self.vx = random.choice([-1, 1]) * random.uniform(self.speed, self.speed + 1)
        self.vy = random.choice([-1, 1]) * random.uniform(self.speed, self.speed + 1)
        self.alive = True
        self.wing_angle = 0
        self.buzz_offset = 0
        self.color_variation = random.randint(0, 30)
        
    def update(self):
        if not self.alive:
            return
            
        self.x += self.vx
        self.y += self.vy
        
        self.wing_angle += 0.5
        self.buzz_offset = math.sin(self.wing_angle) * 2
        
        if self.x <= self.size:
            self.x = self.size
            self.vx = abs(self.vx)
        elif self.x >= WIDTH - self.size:
            self.x = WIDTH - self.size
            self.vx = -abs(self.vx)
            
        if self.y <= self.size + 80:
            self.y = self.size + 80
            self.vy = abs(self.vy)
        elif self.y >= HEIGHT - self.size:
            self.y = HEIGHT - self.size
            self.vy = -abs(self.vy)
            
        if random.random() < 0.015:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(self.speed, self.speed + 1)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
    
    def draw(self, screen):
        if self.alive:
            x, y = int(self.x), int(self.y + self.buzz_offset)
            
            shadow_surf = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50), 
                              (0, 0, self.size * 3, self.size // 2))
            screen.blit(shadow_surf, (x - self.size * 1.5, y + self.size))
            
            wing_color = (200, 200, 200, 150)
            wing_left = pygame.Surface((self.size * 1.2, self.size), pygame.SRCALPHA)
            wing_right = pygame.Surface((self.size * 1.2, self.size), pygame.SRCALPHA)
            
            wing_size = abs(math.sin(self.wing_angle)) * self.size * 0.8 + self.size * 0.4
            pygame.draw.ellipse(wing_left, wing_color, 
                              (0, 0, self.size * 1.2, wing_size))
            pygame.draw.ellipse(wing_right, wing_color, 
                              (0, 0, self.size * 1.2, wing_size))
            
            screen.blit(wing_left, (x - self.size * 1.5, y - wing_size // 2))
            screen.blit(wing_right, (x + self.size * 0.3, y - wing_size // 2))
            
            body_color = (30 + self.color_variation, 30 + self.color_variation, 30 + self.color_variation)
            pygame.draw.ellipse(screen, body_color, 
                              (x - self.size // 2, y - self.size // 3, 
                               self.size, self.size * 0.8))
            
            pygame.draw.circle(screen, (40, 40, 40), (x, y - self.size // 3), self.size // 3)
            
            eye_offset = self.size // 6
            pygame.draw.circle(screen, RED, (x - eye_offset, y - self.size // 3), self.size // 6)
            pygame.draw.circle(screen, RED, (x + eye_offset, y - self.size // 3), self.size // 6)
    
    def check_hit(self, pos, radius=35):
        if not self.alive:
            return False
        dist = math.hypot(self.x - pos[0], self.y - pos[1])
        return dist < (self.size + radius)

class Swatter:
    def __init__(self):
        self.pos = pygame.mouse.get_pos()
        self.hitting = False
        self.hit_timer = 0
        self.trail = []
        self.angle = 0
        
    def update(self):
        new_pos = pygame.mouse.get_pos()
        
        if new_pos != self.pos:
            dx = new_pos[0] - self.pos[0]
            dy = new_pos[1] - self.pos[1]
            self.angle = math.atan2(dy, dx)
        
        self.pos = new_pos
        
        self.trail.append(self.pos)
        if len(self.trail) > 8:
            self.trail.pop(0)
        
        if self.hit_timer > 0:
            self.hit_timer -= 1
        else:
            self.hitting = False
    
    def hit(self):
        self.hitting = True
        self.hit_timer = 8
    
    def draw(self, screen):
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                alpha = int(50 * (i / len(self.trail)))
                s = pygame.Surface((5, 5), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 255, alpha), (2, 2), 2)
                screen.blit(s, self.trail[i])
        
        handle_length = 70
        handle_end_x = self.pos[0] + math.cos(self.angle + math.pi/4) * handle_length
        handle_end_y = self.pos[1] + math.sin(self.angle + math.pi/4) * handle_length
        
        for i in range(3):
            offset = i - 1
            pygame.draw.line(screen, (101, 67, 33), 
                           (self.pos[0] + offset, self.pos[1] + offset),
                           (handle_end_x + offset, handle_end_y + offset), 6)
        
        size = 40 if self.hitting else 35
        color = RED if self.hitting else LIGHT_GREEN
        
        shadow_surf = pygame.Surface((size * 2 + 10, size * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 80), (size + 5, size + 5), size)
        screen.blit(shadow_surf, (self.pos[0] - size - 2, self.pos[1] - size - 2))
        
        pygame.draw.circle(screen, color, self.pos, size)
        pygame.draw.circle(screen, BLACK, self.pos, size, 4)
        
        for i in range(-1, 2):
            start_x = self.pos[0] + i * size // 1.5
            pygame.draw.line(screen, BLACK, 
                           (start_x, self.pos[1] - size),
                           (start_x, self.pos[1] + size), 2)
            start_y = self.pos[1] + i * size // 1.5
            pygame.draw.line(screen, BLACK, 
                           (self.pos[0] - size, start_y),
                           (self.pos[0] + size, start_y), 2)

class Game:
    def __init__(self):
        self.flies = [Fly(1) for _ in range(INITIAL_FLIES)]
        self.swatter = Swatter()
        self.particles = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.hits = 0
        self.misses = 0
        self.start_time = pygame.time.get_ticks()
        self.level = 1
        self.running = True
        self.game_over = False
        self.float_texts = []
        
    def add_float_text(self, text, pos, color):
        self.float_texts.append({
            'text': text,
            'pos': list(pos),
            'color': color,
            'life': 60,
            'vel': -2
        })
    
    def spawn_particles(self, pos, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(pos[0], pos[1], color))
    
    def update(self):
        if self.game_over:
            return
            
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        time_left = max(0, GAME_TIME - elapsed)
        
        if time_left <= 0:
            self.game_over = True
            return
        
        new_level = 1 + int(elapsed // 15)
        if new_level > self.level:
            self.level = new_level
            self.add_float_text(f"Level {self.level}!", (WIDTH // 2, HEIGHT // 2), YELLOW)
        
        alive_flies = sum(1 for f in self.flies if f.alive)
        if alive_flies < min(INITIAL_FLIES + self.level, MAX_FLIES):
            self.flies.append(Fly(self.level))
        
        for fly in self.flies:
            fly.update()
        
        self.swatter.update()
        
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
        
        for ft in self.float_texts:
            ft['pos'][1] += ft['vel']
            ft['life'] -= 1
        self.float_texts = [ft for ft in self.float_texts if ft['life'] > 0]
    
    def handle_click(self, pos):
        if self.game_over:
            return
            
        self.swatter.hit()
        hit_any = False
        
        for fly in self.flies:
            if fly.check_hit(pos):
                fly.alive = False
                hit_any = True
                self.hits += 1
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                
                base_points = 10
                combo_bonus = self.combo * 5
                total_points = base_points + combo_bonus
                self.score += total_points
                
                self.spawn_particles(pos, (255, 0, 0), 20)
                if hit_sound:
                    hit_sound.play()
                
                if self.combo > 1:
                    self.add_float_text(f"+{total_points} (x{self.combo} Combo!)", 
                                      pos, YELLOW)
                else:
                    self.add_float_text(f"+{total_points}", pos, GREEN)
                break
        
        if not hit_any:
            self.misses += 1
            self.combo = 0
            self.spawn_particles(pos, (100, 100, 100), 8)
            if miss_sound:
                miss_sound.play()
            self.add_float_text("Miss!", pos, RED)
    
    def draw(self):
        for y in range(HEIGHT):
            color_val = int(52 + (102 - 52) * y / HEIGHT)
            pygame.draw.line(screen, (color_val, color_val + 50, color_val + 100), 
                           (0, y), (WIDTH, y))
        
        pygame.draw.rect(screen, (44, 62, 80), (0, 0, WIDTH, 80))
        pygame.draw.rect(screen, YELLOW, (0, 77, WIDTH, 3))
        
        for particle in self.particles:
            particle.draw(screen)
        
        for fly in self.flies:
            fly.draw(screen)
        
        self.swatter.draw(screen)
        
        for ft in self.float_texts:
            alpha = int(255 * (ft['life'] / 60))
            text_surf = small_font.render(ft['text'], True, ft['color'])
            text_surf.set_alpha(alpha)
            screen.blit(text_surf, 
                       (ft['pos'][0] - text_surf.get_width() // 2, ft['pos'][1]))
        
        score_text = font.render(f"Score: {self.score}", True, YELLOW)
        screen.blit(score_text, (20, 15))
        
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        time_left = max(0, GAME_TIME - elapsed)
        time_color = RED if time_left < 10 else WHITE
        time_text = font.render(f"Time: {int(time_left)}s", True, time_color)
        screen.blit(time_text, (WIDTH - 180, 15))
        
        if self.combo > 1:
            combo_text = small_font.render(f"Combo x{self.combo}", True, YELLOW)
            screen.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 20))
        
        level_text = small_font.render(f"Level {self.level}", True, WHITE)
        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT - 40))
        
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            panel_width, panel_height = 600, 450
            panel_x = (WIDTH - panel_width) // 2
            panel_y = (HEIGHT - panel_height) // 2
            
            pygame.draw.rect(screen, (44, 62, 80), 
                           (panel_x, panel_y, panel_width, panel_height), 
                           border_radius=20)
            pygame.draw.rect(screen, YELLOW, 
                           (panel_x, panel_y, panel_width, panel_height), 
                           5, border_radius=20)
            
            y_offset = panel_y + 40
            
            game_over_text = font.render("Game Over!", True, YELLOW)
            screen.blit(game_over_text, 
                       (WIDTH // 2 - game_over_text.get_width() // 2, y_offset))
            y_offset += 80
            
            final_score = font.render(f"Score: {self.score}", True, GREEN)
            screen.blit(final_score, 
                       (WIDTH // 2 - final_score.get_width() // 2, y_offset))
            y_offset += 60
            
            stats = [
                f"Hits: {self.hits}",
                f"Misses: {self.misses}",
                f"Max Combo: x{self.max_combo}",
                f"Accuracy: {int(self.hits / max(1, self.hits + self.misses) * 100)}%"
            ]
            
            for stat in stats:
                stat_text = small_font.render(stat, True, WHITE)
                screen.blit(stat_text, 
                           (WIDTH // 2 - stat_text.get_width() // 2, y_offset))
                y_offset += 40
            
            y_offset += 20
            restart_text = tiny_font.render("Press ESC to exit or R to play again", 
                                           True, GRAY)
            screen.blit(restart_text, 
                       (WIDTH // 2 - restart_text.get_width() // 2, y_offset))

def main():
    game = Game()
    pygame.mouse.set_visible(False)
    
    while game.running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False
                elif event.key == pygame.K_r and game.game_over:
                    game = Game()
        
        game.update()
        game.draw()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()