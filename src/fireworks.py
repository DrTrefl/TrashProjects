import pygame
import random
import math
import numpy as np

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
icon = pygame.image.load("../assets/icons/fireworksicon.ico")
pygame.display.set_icon(icon)
pygame.display.set_caption("Fireworks")
clock = pygame.time.Clock()

BLACK = (5, 5, 15)
WHITE = (255, 255, 255)
GLOW_COLORS = [
    (255, 100, 100), (100, 255, 100), (100, 100, 255),
    (255, 255, 100), (255, 100, 255), (100, 255, 255),
    (255, 150, 50), (150, 50, 255), (50, 255, 150)
]

CIRCLE_CENTER = (WIDTH // 2, HEIGHT // 2)
CIRCLE_RADIUS = 380

class Particle:

    def __init__(self, x, y, vx, vy, color, size=3, is_spark=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.alpha = 255
        self.lifetime = 150 if not is_spark else 80
        self.max_lifetime = self.lifetime
        self.is_spark = is_spark
        self.gravity = 0.05 if not is_spark else 0.02
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.98
        self.vy *= 0.98
        self.lifetime -= 1
        self.alpha = max(0, int(255 * (self.lifetime / self.max_lifetime)))
        
    def draw(self, surface):
        if self.alpha > 0:
            color_with_alpha = (*self.color, self.alpha)
            s = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            
            glow_radius = self.size * 2
            pygame.draw.circle(s, (*self.color, self.alpha // 4), (self.size * 2, self.size * 2), glow_radius)
            
            pygame.draw.circle(s, color_with_alpha, (self.size * 2, self.size * 2), self.size)
            
            surface.blit(s, (int(self.x - self.size * 2), int(self.y - self.size * 2)))

class CollectingBall:

    def __init__(self, generation=1):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(100, CIRCLE_RADIUS - 80)
        self.x = CIRCLE_CENTER[0] + distance * math.cos(angle)
        self.y = CIRCLE_CENTER[1] + distance * math.sin(angle)
        
        target_angle = random.uniform(0, 2 * math.pi)
        target_x = CIRCLE_CENTER[0] + CIRCLE_RADIUS * 0.95 * math.cos(target_angle)
        target_y = CIRCLE_CENTER[1] + CIRCLE_RADIUS * 0.95 * math.sin(target_angle)
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        speed = random.uniform(2, 4)
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed
        
        self.color = random.choice(GLOW_COLORS)
        self.size = max(3, 10 - generation)
        self.trail = []
        self.generation = generation
        self.pulse = random.uniform(0, 2 * math.pi)
        
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 20:
            self.trail.pop(0)
            
        self.x += self.vx
        self.y += self.vy
        self.pulse += 0.1
        
    def check_collision(self):
        dx = self.x - CIRCLE_CENTER[0]
        dy = self.y - CIRCLE_CENTER[1]
        dist = math.sqrt(dx**2 + dy**2)
        return dist >= CIRCLE_RADIUS - self.size
    
    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int(180 * (i / len(self.trail)))
            size = int(self.size * (i / len(self.trail)))
            if size > 0:
                s = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                color_with_alpha = (*self.color, alpha // 2)
                pygame.draw.circle(s, color_with_alpha, (size * 1.5, size * 1.5), size)
                surface.blit(s, (int(pos[0] - size * 1.5), int(pos[1] - size * 1.5)))
        
        pulse_size = int(self.size * (1 + 0.3 * math.sin(self.pulse)))
        
        glow_size = self.size * 3
        s = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, 60), (glow_size, glow_size), glow_size)
        screen.blit(s, (int(self.x - glow_size), int(self.y - glow_size)))
        
        mid_glow = self.size * 2
        s = pygame.Surface((mid_glow * 2, mid_glow * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, 120), (mid_glow, mid_glow), mid_glow)
        screen.blit(s, (int(self.x - mid_glow), int(self.y - mid_glow)))
        
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), pulse_size)
        
        core_size = max(1, pulse_size // 2)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), core_size)

def create_explosion(x, y, color, num_particles, generation):
    particles = []
    explosion_power = min(5, 1 + generation * 0.5)
    
    for _ in range(num_particles):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 12 * explosion_power)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        size = random.randint(2, 6)
        
        r = min(255, color[0] + random.randint(-30, 30))
        g = min(255, color[1] + random.randint(-30, 30))
        b = min(255, color[2] + random.randint(-30, 30))
        varied_color = (max(0, r), max(0, g), max(0, b))
        
        particles.append(Particle(x, y, vx, vy, varied_color, size))
    
    for _ in range(num_particles // 2):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(15, 25 * explosion_power)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        particles.append(Particle(x, y, vx, vy, WHITE, 1, is_spark=True))
    
    return particles

def generate_explosion_sound(intensity=1.0):

    sample_rate = 22050
    duration = 2.5
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    bass_freq = 30 + 20 * intensity
    bass = np.sin(2 * np.pi * bass_freq * t) * np.exp(-t * 1.5)
    bass += np.sin(2 * np.pi * bass_freq * 1.5 * t) * np.exp(-t * 2)
    
    noise = np.random.uniform(-1, 1, len(t)) * np.exp(-t * 2.5)
    
    crackle_freq = 1200 * intensity
    crackle = np.sin(2 * np.pi * crackle_freq * t) * np.exp(-t * 6)
    crackle += np.random.uniform(-0.3, 0.3, len(t)) * np.exp(-t * 4)
    
    modulation = 1 + 0.5 * np.sin(2 * np.pi * 2 * t) * np.exp(-t * 3)
    
    sound = (bass * 0.4 + noise * 0.4 + crackle * 0.2) * modulation * intensity
    
    sound = sound * 32767 / (np.max(np.abs(sound)) + 0.01)
    sound = sound.astype(np.int16)
    
    delay = int(sample_rate * 0.01)
    left = np.pad(sound, (0, delay), 'constant')[:-delay]
    right = np.pad(sound, (delay, 0), 'constant')[delay:]
    stereo_sound = np.column_stack((left, right))
    
    return pygame.sndarray.make_sound(stereo_sound)

explosion_sounds = [generate_explosion_sound(i) for i in [0.8, 1.0, 1.3, 1.6, 2.0]]

class ShockWave:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 0
        self.max_radius = 100
        self.alpha = 255
        self.thickness = 3
        
    def update(self):
        self.radius += 8
        self.alpha = max(0, int(255 * (1 - self.radius / self.max_radius)))
        
    def draw(self, surface):
        if self.alpha > 0 and self.radius < self.max_radius:
            s = pygame.Surface((self.radius * 2 + 10, self.radius * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.alpha), (self.radius + 5, self.radius + 5), 
                             int(self.radius), self.thickness)
            surface.blit(s, (int(self.x - self.radius - 5), int(self.y - self.radius - 5)))

def main():
    running = True
    balls = []
    particles = []
    shockwaves = []
    explosion_flash = 0
    spawn_timer = 0
    score = 0
    max_generation = 1
    
    for _ in range(3):
        balls.append(CollectingBall(1))
    
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), 
              random.randint(1, 3)) for _ in range(200)]
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    balls.append(CollectingBall(1))
                elif event.key == pygame.K_r:
                    balls.clear()
                    particles.clear()
                    shockwaves.clear()
                    score = 0
                    max_generation = 1
                    for _ in range(3):
                        balls.append(CollectingBall(1))
        
        spawn_timer += 1
        if spawn_timer > 60 and len(balls) < 30:
            balls.append(CollectingBall(1))
            spawn_timer = 0
        
        balls_to_remove = []
        for ball in balls:
            ball.update()
            if ball.check_collision():
                generation = ball.generation
                max_generation = max(max_generation, generation)
                
                num_particles = min(300, 40 + generation * 20)
                particles.extend(create_explosion(ball.x, ball.y, ball.color, num_particles, generation))
                
                shockwaves.append(ShockWave(ball.x, ball.y, ball.color))
                
                num_new_balls = min(3, 1 + generation // 3)
                for _ in range(num_new_balls):
                    balls.append(CollectingBall(generation + 1))
                
                balls_to_remove.append(ball)
                explosion_flash = min(60, 20 + generation * 5)
                score += generation * 10
                
                sound_idx = min(len(explosion_sounds) - 1, generation - 1)
                explosion_sounds[sound_idx].play()
        
        for ball in balls_to_remove:
            balls.remove(ball)
        
        particles = [p for p in particles if p.lifetime > 0]
        for particle in particles:
            particle.update()
        
        shockwaves = [sw for sw in shockwaves if sw.alpha > 0]
        for shockwave in shockwaves:
            shockwave.update()
        
        screen.fill(BLACK)
        
        for star in stars:
            brightness = 150 + int(100 * math.sin(pygame.time.get_ticks() / 1000 + star[0]))
            pygame.draw.circle(screen, (brightness, brightness, brightness), 
                             (star[0], star[1]), star[2])
        
        if explosion_flash > 0:
            flash_intensity = int(200 * (explosion_flash / 60))
            flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, flash_intensity // 4))
            screen.blit(flash_surface, (0, 0))
            explosion_flash -= 1
        
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (100, 150, 255, 30), CIRCLE_CENTER, CIRCLE_RADIUS + 10)
        screen.blit(glow_surface, (0, 0))
        pygame.draw.circle(screen, (100, 200, 255), CIRCLE_CENTER, CIRCLE_RADIUS, 3)
        
        for shockwave in shockwaves:
            shockwave.draw(screen)
        
        for particle in particles:
            particle.draw(screen)
        
        for ball in balls:
            ball.draw(screen)
        
        info_bg = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        info_bg.fill((0, 0, 0, 180))
        screen.blit(info_bg, (0, 0))
        
        font_large = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)
        
        score_text = font_large.render(f'Score: {score}', True, (255, 255, 100))
        screen.blit(score_text, (20, 15))
        
        balls_text = font_small.render(f'Balls: {len(balls)} | Generation: {max_generation}', True, WHITE)
        screen.blit(balls_text, (20, 60))
        
        particles_text = font_small.render(f'Particles: {len(particles)}', True, (150, 220, 255))
        screen.blit(particles_text, (WIDTH - 250, 60))
        
        help_text = font_small.render('SPACE - add a ball | R - reset', True, (200, 200, 200))
        screen.blit(help_text, (WIDTH // 2 - 200, HEIGHT - 40))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()