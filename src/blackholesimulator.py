import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
icon = pygame.image.load("../assets/icons/blackholesimulatoricon.ico")
pygame.display.set_icon(icon)
pygame.display.set_caption("Black Hole Simulator")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.alive = True
        self.color = random.choice([ORANGE, YELLOW, WHITE, BLUE])
        self.size = random.randint(2, 4)
        
    def update(self, bh_x, bh_y, bh_mass):
        if not self.alive:
            return
            
        dx = bh_x - self.x
        dy = bh_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 30:
            self.alive = False
            return
        
        force = (bh_mass * 100) / (dist * dist)
        
        if dist > 0:
            dx /= dist
            dy /= dist
        
        self.vx += dx * force * 0.01
        self.vy += dy * force * 0.01
        
        self.x += self.vx
        self.y += self.vy
        
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.alive = False
    
    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class BlackHole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.mass = 50
        self.event_horizon = 30
        
    def draw(self, screen):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), int(self.event_horizon))
        
        for i in range(5, 0, -1):
            radius = self.event_horizon + i * 8
            alpha = 255 - i * 40
            color = (255, int(140 - i * 20), 0)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(radius), 2)
        
        pygame.draw.circle(screen, (139, 69, 19), (int(self.x), int(self.y)), self.event_horizon + 2, 2)
    
    def update_position(self, x, y):
        self.x = x
        self.y = y

black_hole = BlackHole(WIDTH // 2, HEIGHT // 2)
particles = []
spawn_timer = 0

running = True
mouse_control = False

font = pygame.font.Font(None, 30)

while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_control = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_control = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                mx, my = pygame.mouse.get_pos()
                for _ in range(50):
                    particles.append(Particle(mx, my))
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                black_hole.mass = min(black_hole.mass + 10, 200)
                black_hole.event_horizon = min(black_hole.event_horizon + 3, 60)
            elif event.key == pygame.K_MINUS:
                black_hole.mass = max(black_hole.mass - 10, 20)
                black_hole.event_horizon = max(black_hole.event_horizon - 3, 15)
    
    if mouse_control:
        mx, my = pygame.mouse.get_pos()
        black_hole.update_position(mx, my)
    
    spawn_timer += 1
    if spawn_timer > 10:
        spawn_timer = 0
        side = random.randint(0, 3)
        if side == 0:
            particles.append(Particle(random.randint(0, WIDTH), 0))
        elif side == 1:
            particles.append(Particle(WIDTH, random.randint(0, HEIGHT)))
        elif side == 2:
            particles.append(Particle(random.randint(0, WIDTH), HEIGHT))
        else:
            particles.append(Particle(0, random.randint(0, HEIGHT)))
    
    for particle in particles:
        particle.update(black_hole.x, black_hole.y, black_hole.mass)
    
    particles = [p for p in particles if p.alive]
    
    screen.fill((10, 10, 30))
    
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.circle(screen, WHITE, (x, y), 1)
    
    for particle in particles:
        particle.draw(screen)
    
    black_hole.draw(screen)
    
    texts = [
        "Drag with the mouse - move the black hole",
        "SPACE - particle explosion",
        "-/+ - change mass",
        f"Mass: {black_hole.mass}"
    ]
    
    for i, text in enumerate(texts):
        label = font.render(text, True, WHITE)
        screen.blit(label, (10, 10 + i * 30))
    
    pygame.display.flip()

pygame.quit()