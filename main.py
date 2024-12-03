import pygame
import pywavefront
from pywavefront import visualization
from OpenGL.raw.GLU import gluLookAt, gluPerspective
from pygame.locals import *
from OpenGL.GL import *

global time # time since beginning of program in ms

def draw_at(draw_func, posx, posy, posz):
    glPushMatrix()
    glTranslate(posx, posy, posz)
    draw_func()
    glPopMatrix()

def draw_human(human, human_body_model, human_arm_model):
    visualization.draw(human_body_model)
    visualization.draw(human_arm_model)

def draw_car(car_model):
    pass

class Car:
    time_to_finished = 5000
    start_time = 0
    pos = [0, 0, 0]
    dest = [0, 0, 0]
    def __init__(self, start_time, start_position, destination):
        self.pos = start_position
        self.dest = destination
        self.start_time = start_time

class Human:
    started_waving = 0
    is_waving = False
    def start_waving(self):
        global time
        self.is_waving = True
        self.started_waving = time
    def stop_waving(self):
        self.is_waving = False

def lerp(t, a, b):
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Array to store driving cars
    cars = []
    # Store human state
    human = Human()
    human.start_waving() # TODO: Decide when to wave

    # Import models
    car_model = pywavefront.Wavefront("Resources/car.obj", collect_faces=True) # collect faces will turn all non-triangle faces into triangles
    human_body_model = pywavefront.Wavefront("Resources/humanbody.obj", collect_faces=True)
    human_arm_model = pywavefront.Wavefront("Resources/humanarm.obj", collect_faces=True)

    global time; time = 0
    frame_len = 10 # Frame length in ms
    rot = 0
    while True:

        # Game Logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    rot += 15
                elif event.key == pygame.K_LEFT:
                    rot -= 15
                if event.key == pygame.K_k:
                    cars.append(Car(time, [-15, 0, 0], [15, 0, 0])) # TODO: Set start and dest

        # Render
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1, 0.1, 100) # fov, aspect ratio (width/height), near, far
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Render functions
        gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)
        for car in cars:
            t = (time - car.start_time) / car.time_to_finished
            if t >= car.time_to_finished:
                cars.remove(car)
            pos = lerp(t, car.pos, car.dest)
            draw_at(draw_car, *pos)
        glRotate(rot, 0, 1, 0)
        draw_at(lambda: draw_human(human, human_body_model, human_arm_model), 0, 0, 0) # TODO: Set human position
        pygame.display.flip()

        # Wait for next frame
        glFlush()
        pygame.time.wait(frame_len)
        time += frame_len

main()