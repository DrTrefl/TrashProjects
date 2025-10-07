import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
import random

class Building:
    def __init__(self, x, z, width, depth, height):
        self.x = x
        self.z = z
        self.width = width
        self.depth = depth
        self.height = height

class FlightSimulator:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        icon = pygame.image.load("../assets/icons/flightsimulator3d.ico")
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Flight Simulator 3D")
        
        self.pos = [0.0, 20.0, 0.0]
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        
        self.velocity = [0.0, 0.0, -30.0]
        self.speed = 30.0
        self.throttle = 0.7
        self.gravity = -9.8
        
        self.buildings = []
        self.generate_city()
        
        glMatrixMode(GL_PROJECTION)
        gluPerspective(70, (self.width / self.height), 0.1, 500.0)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glLight(GL_LIGHT0, GL_POSITION, (10, 50, 10, 1))
        glLight(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1))
        glLight(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
        
        self.clock = pygame.time.Clock()
        
    def generate_city(self):
        for _ in range(60):
            x = random.uniform(-200, 200)
            z = random.uniform(-200, 200)
            if abs(x) < 20 and abs(z) < 60:
                continue
            width = random.uniform(5, 20)
            depth = random.uniform(5, 20)
            height = random.uniform(10, 70)
            self.buildings.append(Building(x, z, width, depth, height))
        
    def draw_terrain(self):
        glColor3f(0.2, 0.6, 0.2)
        glBegin(GL_QUADS)
        size = 200
        for x in range(-5, 5):
            for z in range(-5, 5):
                x1, z1 = x * size/5, z * size/5
                x2, z2 = (x+1) * size/5, (z+1) * size/5
                
                glVertex3f(x1, 0, z1)
                glVertex3f(x2, 0, z1)
                glVertex3f(x2, 0, z2)
                glVertex3f(x1, 0, z2)
        glEnd()
        
        glColor3f(0.1, 0.4, 0.1)
        glBegin(GL_LINES)
        for i in range(-5, 6):
            glVertex3f(i * size/5, 0.01, -size)
            glVertex3f(i * size/5, 0.01, size)
            glVertex3f(-size, 0.01, i * size/5)
            glVertex3f(size, 0.01, i * size/5)
        glEnd()
        
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-5, 0.1, -50)
        glVertex3f(5, 0.1, -50)
        glVertex3f(5, 0.1, 50)
        glVertex3f(-5, 0.1, 50)
        glEnd()
        
        glColor3f(1, 1, 1)
        for i in range(-5, 6):
            glBegin(GL_QUADS)
            z = i * 10
            glVertex3f(-0.5, 0.2, z)
            glVertex3f(0.5, 0.2, z)
            glVertex3f(0.5, 0.2, z + 3)
            glVertex3f(-0.5, 0.2, z + 3)
            glEnd()
        
    def draw_buildings(self):
        for bld in self.buildings:
            dist = math.sqrt((bld.x - self.pos[0])**2 + (bld.z - self.pos[2])**2)
            if dist > 300:
                continue
                
            glPushMatrix()
            glTranslatef(bld.x, bld.height/2, bld.z)
            
            gray = random.Random(bld.x * bld.z).uniform(0.4, 0.7)
            glColor3f(gray, gray, gray + 0.1)
            
            glBegin(GL_QUADS)
            
            glVertex3f(-bld.width/2, -bld.height/2, bld.depth/2)
            glVertex3f(bld.width/2, -bld.height/2, bld.depth/2)
            glVertex3f(bld.width/2, bld.height/2, bld.depth/2)
            glVertex3f(-bld.width/2, bld.height/2, bld.depth/2)
            
            glVertex3f(-bld.width/2, -bld.height/2, -bld.depth/2)
            glVertex3f(-bld.width/2, bld.height/2, -bld.depth/2)
            glVertex3f(bld.width/2, bld.height/2, -bld.depth/2)
            glVertex3f(bld.width/2, -bld.height/2, -bld.depth/2)
            
            glVertex3f(-bld.width/2, -bld.height/2, -bld.depth/2)
            glVertex3f(-bld.width/2, -bld.height/2, bld.depth/2)
            glVertex3f(-bld.width/2, bld.height/2, bld.depth/2)
            glVertex3f(-bld.width/2, bld.height/2, -bld.depth/2)
            
            glVertex3f(bld.width/2, -bld.height/2, -bld.depth/2)
            glVertex3f(bld.width/2, bld.height/2, -bld.depth/2)
            glVertex3f(bld.width/2, bld.height/2, bld.depth/2)
            glVertex3f(bld.width/2, -bld.height/2, bld.depth/2)
            
            glEnd()
            
            glColor3f(gray * 0.6, gray * 0.6, gray * 0.6)
            glBegin(GL_QUADS)
            glVertex3f(-bld.width/2, bld.height/2, -bld.depth/2)
            glVertex3f(-bld.width/2, bld.height/2, bld.depth/2)
            glVertex3f(bld.width/2, bld.height/2, bld.depth/2)
            glVertex3f(bld.width/2, bld.height/2, -bld.depth/2)
            glEnd()
            
            glPopMatrix()
        
    def draw_sky(self):
        glDisable(GL_LIGHTING)
        glBegin(GL_QUADS)
        glColor3f(0.5, 0.7, 1.0)
        glVertex3f(-500, 100, -500)
        glVertex3f(500, 100, -500)
        glColor3f(0.3, 0.5, 0.8)
        glVertex3f(500, 0, -500)
        glVertex3f(-500, 0, -500)
        glEnd()
        glEnable(GL_LIGHTING)
        
    def draw_aircraft(self):
        glPushMatrix()
        glDisable(GL_LIGHTING)
        
        glColor3f(0.8, 0.1, 0.1)
        glBegin(GL_TRIANGLES)

        glVertex3f(0, 0, 2)
        glVertex3f(-0.3, 0, 0)
        glVertex3f(0.3, 0, 0)
        glEnd()
        
        glBegin(GL_QUADS)

        glVertex3f(-0.3, 0, 0)
        glVertex3f(0.3, 0, 0)
        glVertex3f(0.3, 0, -2)
        glVertex3f(-0.3, 0, -2)
        glEnd()
        
        glColor3f(0.9, 0.9, 0.9)
        glBegin(GL_TRIANGLES)
        glVertex3f(-3, 0, -0.5)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, -1)
        
        glVertex3f(3, 0, -0.5)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, -1)
        glEnd()
        
        glColor3f(0.7, 0.7, 0.7)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0.8, -2)
        glVertex3f(-0.3, 0, -2)
        glVertex3f(0.3, 0, -2)
        glEnd()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
        
    def draw_hud(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        glColor3f(0, 1, 0)
        glBegin(GL_LINES)
        cx, cy = self.width/2, self.height/2
        glVertex2f(cx - 20, cy)
        glVertex2f(cx + 20, cy)
        glVertex2f(cx, cy - 20)
        glVertex2f(cx, cy + 20)
        glEnd()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
    def update_physics(self, dt):
        thrust = self.throttle * 80.0
        
        rad_pitch = math.radians(self.pitch)
        rad_yaw = math.radians(self.yaw)
        
        forward = [
            math.sin(rad_yaw) * math.cos(rad_pitch),
            math.sin(rad_pitch),
            -math.cos(rad_yaw) * math.cos(rad_pitch)
        ]
        
        for i in range(3):
            self.velocity[i] += forward[i] * thrust * dt
            
        self.velocity[1] += self.gravity * dt
        
        drag = 0.98
        for i in range(3):
            self.velocity[i] *= drag
            
        for i in range(3):
            self.pos[i] += self.velocity[i] * dt
            
        if self.pos[1] < 1.0:
            self.pos[1] = 1.0
            self.velocity[1] = 0
            if self.speed > 20:
                print("CRASH! Restart...")
                self.pos = [0.0, 20.0, 0.0]
                self.velocity = [0.0, 0.0, -30.0]
                self.pitch = 0.0
        
        for bld in self.buildings:
            if (abs(self.pos[0] - bld.x) < bld.width/2 and 
                abs(self.pos[2] - bld.z) < bld.depth/2 and
                self.pos[1] < bld.height):
                print("CRASH! Collision with a building!")
                self.pos = [0.0, 20.0, 0.0]
                self.velocity = [0.0, 0.0, -30.0]
                self.pitch = 0.0
                
        self.speed = math.sqrt(sum(v*v for v in self.velocity))
        
    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        
        turn_speed = 50 * dt
        pitch_speed = 30 * dt
        
        if keys[K_LEFT]:
            self.yaw -= turn_speed
            self.roll = max(-20, self.roll - 20 * dt)
        elif keys[K_RIGHT]:
            self.yaw += turn_speed
            self.roll = min(20, self.roll + 20 * dt)
        else:
            self.roll *= 0.9
            
        if keys[K_UP]:
            self.pitch += pitch_speed
        if keys[K_DOWN]:
            self.pitch -= pitch_speed
            
        if keys[K_w]:
            self.throttle = min(1.0, self.throttle + 0.5 * dt)
        if keys[K_s]:
            self.throttle = max(0.0, self.throttle - 0.5 * dt)
            
        self.pitch = max(-80, min(80, self.pitch))
        
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        cam_dist = 8
        cam_height = 3
        
        rad_pitch = math.radians(self.pitch)
        rad_yaw = math.radians(self.yaw)
        
        cam_x = self.pos[0] - math.sin(rad_yaw) * cam_dist * math.cos(rad_pitch)
        cam_y = self.pos[1] + cam_height - math.sin(rad_pitch) * cam_dist
        cam_z = self.pos[2] + math.cos(rad_yaw) * cam_dist * math.cos(rad_pitch)
        
        gluLookAt(cam_x, cam_y, cam_z,
                  self.pos[0], self.pos[1], self.pos[2],
                  0, 1, 0)
        
        self.draw_terrain()
        self.draw_buildings()
        
        glPushMatrix()
        glTranslatef(*self.pos)
        glRotatef(-self.yaw, 0, 1, 0)
        glRotatef(-self.pitch, 1, 0, 0)
        glRotatef(self.roll, 0, 0, 1)
        self.draw_aircraft()
        glPopMatrix()
        
        self.draw_hud()
        
        pygame.display.set_caption(
            f"Flight Simulator 3D | Speed: {self.speed:.1f} | "
            f"Altitude: {self.pos[1]:.1f} | Throttle: {self.throttle*100:.0f}%"
        )
        
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                        
            self.handle_input(dt)
            self.update_physics(dt)
            self.render()
            pygame.display.flip()
            
        pygame.quit()

if __name__ == "__main__":
    print("\nControls:")
    print("  Arrows - control the airplane")
    print("  W/S - throttle")
    print("  ESC - exit")
    
    sim = FlightSimulator()
    sim.run()