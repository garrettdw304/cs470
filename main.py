import pygame
from pygame.locals import *
from OpenGL.GL import *

global time # time since beginning of program in ms

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    global time; time = 0
    frame_len = 10 # Frame length in ms
    while True:

        # Game Logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Render
        glClear(GL_COLOR_BUFFER_BIT)
        # Render functions
        pygame.display.flip()

        # Wait for next frame
        glFlush()
        pygame.time.wait(frame_len)
        time += frame_len

main()