import pygame
import random
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (46, 204, 113)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
YELLOW = (241, 196, 15)
PURPLE = (155, 89, 182)
ORANGE = (230, 126, 34)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
icon = pygame.image.load("../assets/icons/mathematicalquizicon.ico")
pygame.display.set_icon(icon)
pygame.display.set_caption("Mathematical Quiz - Fuck You Edition")

try:
    font_big = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)
except:
    font_big = pygame.font.SysFont('arial', 72)
    font_medium = pygame.font.SysFont('arial', 48)
    font_small = pygame.font.SysFont('arial', 36)

def generate_sound(frequency, duration=0.1):
    sample_rate = 22050
    n_samples = int(round(duration * sample_rate))
    buf = []
    for i in range(n_samples):
        value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        buf.append([value, value])
    sound = pygame.sndarray.make_sound(buf)
    return sound

try:
    sound_correct = generate_sound(523, 0.15)
    sound_wrong = generate_sound(200, 10)
    sound_click = generate_sound(800, 0.05)
except:
    sound_correct = None
    sound_wrong = None
    sound_click = None

class ParticleEffect:
    def __init__(self, x, y, color, count=20):
        self.particles = []
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 60,
                'color': color
            })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 60))
            size = max(2, int(6 * (particle['life'] / 60)))
            pygame.draw.circle(surface, particle['color'], 
                             (int(particle['x']), int(particle['y'])), size)
    
    def is_finished(self):
        return len(self.particles) == 0

class MathQuiz:
    def __init__(self):
        self.score = 0
        self.total = 0
        self.current_question = None
        self.user_answer = ""
        self.feedback = ""
        self.feedback_timer = 0
        self.particle_effects = []
        self.shake_amount = 0
        self.generate_question()
    
    def generate_question(self):
        operations = ['+', '-', '*', '/']
        operation = random.choice(operations)
        
        if operation == '/':
            divisor = random.randint(2, 10)
            result = random.randint(1, 10)
            num1 = divisor * result
            num2 = divisor
        else:
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
        
        self.current_question = {
            'num1': num1,
            'num2': num2,
            'operation': operation,
            'answer': self.calculate_answer(num1, num2, operation)
        }
    
    def calculate_answer(self, num1, num2, operation):
        if operation == '+':
            return num1 + num2
        elif operation == '-':
            return num1 - num2
        elif operation == '*':
            return num1 * num2
        elif operation == '/':
            return num1 // num2
    
    def check_answer(self):
        try:
            user_ans = int(self.user_answer)
            self.total += 1
            
            if user_ans == self.current_question['answer']:
                self.score += 1
                self.feedback = "Congrats, you failure! "
                self.particle_effects.append(ParticleEffect(WIDTH // 2, HEIGHT // 2, GREEN))
                if sound_correct:
                    sound_correct.play()
            else:
                self.feedback = f"NO, FUCK YOU! \nAnswer: {self.current_question['answer']}"
                self.particle_effects.append(ParticleEffect(WIDTH // 2, HEIGHT // 2, RED))
                self.shake_amount = 20
                if sound_wrong:
                    sound_wrong.play()
            
            self.feedback_timer = 120
            self.user_answer = ""
            self.generate_question()
        except ValueError:
            pass
    
    def update(self):
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
        
        if self.shake_amount > 0:
            self.shake_amount -= 1
        
        for effect in self.particle_effects[:]:
            effect.update()
            if effect.is_finished():
                self.particle_effects.remove(effect)
    
    def draw(self, surface):
        offset_x = 0
        offset_y = 0
        if self.shake_amount > 0:
            offset_x = random.randint(-self.shake_amount // 2, self.shake_amount // 2)
            offset_y = random.randint(-self.shake_amount // 2, self.shake_amount // 2)
        
        surface.fill(PURPLE)
        
        for i in range(HEIGHT):
            alpha = i / HEIGHT
            color = (
                int(PURPLE[0] * (1 - alpha) + BLUE[0] * alpha),
                int(PURPLE[1] * (1 - alpha) + BLUE[1] * alpha),
                int(PURPLE[2] * (1 - alpha) + BLUE[2] * alpha)
            )
            pygame.draw.line(surface, color, (0, i), (WIDTH, i))
        
        score_text = font_small.render(f"Score: {self.score}/{self.total}", True, WHITE)
        surface.blit(score_text, (20 + offset_x, 20 + offset_y))
        
        question_str = f"{self.current_question['num1']} {self.current_question['operation']} {self.current_question['num2']} = ?"
        question_text = font_big.render(question_str, True, YELLOW)
        question_rect = question_text.get_rect(center=(WIDTH // 2 + offset_x, HEIGHT // 3 + offset_y))
        surface.blit(question_text, question_rect)
        
        answer_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 30, 300, 60)
        answer_box.x += offset_x
        answer_box.y += offset_y
        pygame.draw.rect(surface, WHITE, answer_box, 0, 10)
        pygame.draw.rect(surface, ORANGE, answer_box, 4, 10)
        
        answer_text = font_medium.render(self.user_answer or "_", True, BLACK)
        answer_rect = answer_text.get_rect(center=answer_box.center)
        surface.blit(answer_text, answer_rect)
        
        if self.feedback_timer > 0:
            lines = self.feedback.split('\n')
            y_offset = HEIGHT // 2 + 100
            for line in lines:
                if "FUCK YOU" in line:
                    feedback_text = font_medium.render(line, True, RED)
                else:
                    feedback_text = font_medium.render(line, True, GREEN)
                feedback_rect = feedback_text.get_rect(center=(WIDTH // 2 + offset_x, y_offset + offset_y))
                surface.blit(feedback_text, feedback_rect)
                y_offset += 50
        
        instruction = font_small.render("Type your answer and press ENTER | ESC - exit", True, WHITE)
        instruction_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        surface.blit(instruction, instruction_rect)
        
        for effect in self.particle_effects:
            effect.draw(surface)

def main():
    clock = pygame.time.Clock()
    quiz = MathQuiz()
    running = True
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_RETURN:
                    if quiz.user_answer:
                        quiz.check_answer()
                        if sound_click:
                            sound_click.play()
                
                elif event.key == pygame.K_BACKSPACE:
                    quiz.user_answer = quiz.user_answer[:-1]
                
                elif event.unicode.isdigit() or (event.unicode == '-' and not quiz.user_answer):
                    if len(quiz.user_answer) < 6:
                        quiz.user_answer += event.unicode
        
        quiz.update()
        quiz.draw(screen)
        pygame.display.flip()
    
    screen.fill(BLUE)
    
    summary_texts = [
        font_big.render("GAME OVER!", True, YELLOW),
        font_medium.render(f"Your score: {quiz.score}/{quiz.total}", True, WHITE),
    ]
    
    if quiz.total > 0:
        percentage = (quiz.score / quiz.total) * 100
        summary_texts.append(font_medium.render(f"Accuracy: {percentage:.1f}%", True, WHITE))
        
        if percentage == 100:
            summary_texts.append(font_small.render("You're still talentless", True, GREEN))
        elif percentage >= 80:
            summary_texts.append(font_small.render("Nice job, loser!", True, GREEN))
        elif percentage >= 50:
            summary_texts.append(font_small.render("Shitty result!", True, YELLOW))
        else:
            summary_texts.append(font_small.render("You need to practice more, you piece of shit!", True, ORANGE))
    
    y_offset = HEIGHT // 3
    for text in summary_texts:
        rect = text.get_rect(center=(WIDTH // 2, y_offset))
        screen.blit(text, rect)
        y_offset += 60
    
    pygame.display.flip()
    pygame.time.wait(3000)
    
    pygame.quit()

if __name__ == "__main__":
    main()