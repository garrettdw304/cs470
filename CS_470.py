import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time

def cube(xSize, ySize, zSize):
    glBegin(GL_POLYGON)
    glVertex3f(-xSize/2, -ySize/2, -zSize/2)
    glVertex3f(xSize/2, -ySize/2, -zSize/2)
    glVertex3f(xSize/2, -ySize/2, zSize/2)
    glVertex3f(-xSize/2, -ySize/2, zSize/2)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-xSize/2, ySize/2, -zSize/2)
    glVertex3f(xSize/2, ySize/2, -zSize/2)
    glVertex3f(xSize/2, ySize/2, zSize/2)
    glVertex3f(-xSize/2, ySize/2, zSize/2)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-xSize/2, ySize/2, -zSize/2)
    glVertex3f(-xSize/2, -ySize/2, -zSize/2)
    glVertex3f(-xSize/2, -ySize/2, zSize/2)
    glVertex3f(-xSize/2, ySize/2, zSize/2)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(xSize/2, ySize/2, -zSize/2)
    glVertex3f(xSize/2, -ySize/2, -zSize/2)
    glVertex3f(xSize/2, -ySize/2, zSize/2)
    glVertex3f(xSize/2, ySize/2, zSize/2)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-xSize/2, -ySize/2, -zSize/2)
    glVertex3f(xSize/2, -ySize/2, -zSize/2)
    glVertex3f(xSize/2, ySize/2, -zSize/2)
    glVertex3f(-xSize/2, ySize/2, -zSize/2)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-xSize/2, -ySize/2, zSize/2)
    glVertex3f(xSize/2, -ySize/2, zSize/2)
    glVertex3f(xSize/2, ySize/2, zSize/2)
    glVertex3f(-xSize/2, ySize/2, zSize/2)
    glEnd()

def prtCar():
    glTranslatef(0, 0, 0.5)

    glColor3f(1.0, 1.0, 0)
    #setMaterial(1.0, 1.0, 0)

    glBegin(GL_POLYGON)
    glVertex3f(-0.5, 0, 0)
    glVertex3f(-0.7, 0.2, 0)
    glVertex3f(0.7, 0.2, 0)
    glVertex3f(0.5, 0, 0)
    glEnd()

    glColor3f(0, 0, 1.0)
    #setMaterial(0, 0, 1.0)

    glBegin(GL_POLYGON)
    glVertex3f(-1, 0.2, 0)
    glVertex3f(-0.95, 0.8, 0)
    glVertex3f(0.95, 0.8, 0)
    glVertex3f(1, 0.2, 0)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.95, 0.8, 0)
    glVertex3f(-0.9, 1.4, 0)
    glVertex3f(-0.85, 1.4, 0)
    glVertex3f(-0.9, 0.8, 0)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(0.95, 0.8, 0)
    glVertex3f(0.9, 1.4, 0)
    glVertex3f(0.85, 1.4, 0)
    glVertex3f(0.9, 0.8, 0)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.85, 1.4, 0)
    glVertex3f(-0.855, 1.35, 0)
    glVertex3f(0.855, 1.35, 0)
    glVertex3f(0.85, 1.4, 0)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.4, 1.4, 0)
    glVertex3f(-0.5, 1.4, 0)
    glVertex3f(-0.5, 0.8, 0)
    glVertex3f(-0.4, 0.8, 0)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(0, 1.4, 0)
    glVertex3f(0.5, 1.4, 0)
    glVertex3f(0.5, 0.8, 0)
    glVertex3f(0, 0.8, 0)
    glEnd()

    glTranslatef(0, 0, -1)

    glColor3f(1.0, 1.0, 0)
    #setMaterial(1.0, 1.0, 0)
    
    glBegin(GL_POLYGON)
    glVertex3f(-0.5, 0, 0)
    glVertex3f(-0.7, 0.2, 0)
    glVertex3f(0.7, 0.2, 0)
    glVertex3f(0.5, 0, 0)
    glEnd()

    glColor3f(0, 0, 1.0)
    #setMaterial(0, 0, 1.0)

    glBegin(GL_POLYGON)
    glVertex3f(-1, 0.2, 0)
    glVertex3f(-0.95, 0.8, 0)
    glVertex3f(0.95, 0.8, 0)
    glVertex3f(1, 0.2, 0)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.95, 0.8, 0)
    glVertex3f(-0.9, 1.4, 0)
    glVertex3f(-0.85, 1.4, 0)
    glVertex3f(-0.9, 0.8, 0)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(0.95, 0.8, 0)
    glVertex3f(0.9, 1.4, 0)
    glVertex3f(0.85, 1.4, 0)
    glVertex3f(0.9, 0.8, 0)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.85, 1.4, 0)
    glVertex3f(-0.855, 1.35, 0)
    glVertex3f(0.855, 1.35, 0)
    glVertex3f(0.85, 1.4, 0)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.4, 1.4, 0)
    glVertex3f(-0.5, 1.4, 0)
    glVertex3f(-0.5, 0.8, 0)
    glVertex3f(-0.4, 0.8, 0)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(0, 1.4, 0)
    glVertex3f(0.5, 1.4, 0)
    glVertex3f(0.5, 0.8, 0)
    glVertex3f(0, 0.8, 0)
    glEnd()

    glColor3f(1, 1, 0)
    #setMaterial(1, 1, 0)
    glBegin(GL_POLYGON)
    glVertex3f(0.9, 1.4, 0)
    glVertex3f(0.91, 1.3, 0)
    glVertex3f(0.91, 1.3, 1)
    glVertex3f(0.9, 1.4, 1)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(0.91, 1.3, 0)
    glVertex3f(0.96, 0.7, 0)
    glVertex3f(0.96, 0.7, 0.05)
    glVertex3f(0.91, 1.3, 0.05)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(0.91, 1.3, 1)
    glVertex3f(0.96, 0.7, 1)
    glVertex3f(0.96, 0.7, 0.95)
    glVertex3f(0.91, 1.3, 0.95)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(0.96, 0.7, 0)
    glVertex3f(1, 0.2, 0)
    glVertex3f(1, 0.2, 1)
    glVertex3f(0.96, 0.7, 1)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.9, 1.4, 0)
    glVertex3f(-0.91, 1.3, 0)
    glVertex3f(-0.91, 1.3, 1)
    glVertex3f(-0.9, 1.4, 1)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.91, 1.3, 0)
    glVertex3f(-0.96, 0.7, 0)
    glVertex3f(-0.96, 0.7, 0.05)
    glVertex3f(-0.91, 1.3, 0.05)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.91, 1.3, 1)
    glVertex3f(-0.96, 0.7, 1)
    glVertex3f(-0.96, 0.7, 0.95)
    glVertex3f(-0.91, 1.3, 0.95)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.96, 0.7, 0)
    glVertex3f(-1, 0.2, 0)
    glVertex3f(-1, 0.2, 1)
    glVertex3f(-0.96, 0.7, 1)
    glEnd()

    glColor3f(0.3, 0.3, 0.3)
    #setMaterial(0.3, 0.3, 0.3)

    glBegin(GL_POLYGON)
    glVertex3f(-0.5, 0, 0)
    glVertex3f(0.5, 0, 0)
    glVertex3f(0.5, 0, 1)
    glVertex3f(-0.5, 0, 1)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.5, 0, 0)
    glVertex3f(-0.7, 0.2, 0)
    glVertex3f(-0.7, 0.2, 1)
    glVertex3f(-0.5, 0, 1)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-0.7, 0.2, 0)
    glVertex3f(-1, 0.2, 0)
    glVertex3f(-1, 0.2, 1)
    glVertex3f(-0.7, 0.2, 1)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(0.5, 0, 0)
    glVertex3f(0.7, 0.2, 0)
    glVertex3f(0.7, 0.2, 1)
    glVertex3f(0.5, 0, 1)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(0.7, 0.2, 0)
    glVertex3f(1, 0.2, 0)
    glVertex3f(1, 0.2, 1)
    glVertex3f(0.7, 0.2, 1)
    glEnd()

    glColor3f(1, 1, 0.8)
    #setMaterial(1.0, 1.0, 0.8)

    glBegin(GL_POLYGON)
    glVertex3f(1, 0.21, 0)
    glVertex3f(-1, 0.21, 0)
    glVertex3f(-1, 0.21, 1)
    glVertex3f(1, 0.21, 1)
    glEnd()

    glColor3f(1, 1, 0)
    #setMaterial(1.0, 1.0, 0)

    glBegin(GL_POLYGON)
    glVertex3f(0.9, 1.4, 0)
    glVertex3f(-0.9, 1.4, 0)
    glVertex3f(-0.9, 1.4, 1)
    glVertex3f(0.9, 1.4, 1)
    glEnd()

    glColor3f(0.6, 0.6, 0.6)
    #setMaterial(0.6, 0.6, 0.6)

    glPushMatrix()

    glRotatef(90, 1, 0, 0)
    glTranslatef(0.25, 0.75, -1.4)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.05, 0.05, 1.2, 20, 1)

    glTranslatef(0, -0.5, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.05, 0.05, 1.2, 20, 1)

    glTranslatef(-0.5, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.05, 0.05, 1.2, 20, 1)

    glTranslatef(0, 0.5, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.05, 0.05, 1.2, 20, 1)

    glPopMatrix()

    glPushMatrix()

    glColor3f(0.1, 0.1, 0.1)
    #setMaterial(0.1, 0.1, 0.1)

    glTranslatef(0.8, -0.02, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.2, 0.2, 0.2, 20, 1)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.075, 0.075, 0.2, 20, 1)
    quadric = gluNewQuadric()
    gluDisk(quadric, 0.075, 0.2, 20, 1)

    glTranslatef(-1.6, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.2, 0.2, 0.2, 20, 1)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.075, 0.075, 0.2, 20, 1)
    quadric = gluNewQuadric()
    gluDisk(quadric, 0.075, 0.2, 20, 1)

    glTranslatef(0, 0, 0.8)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.2, 0.2, 0.2, 20, 1)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.075, 0.075, 0.2, 20, 1)
    quadric = gluNewQuadric()
    gluDisk(quadric, 0.075, 0.2, 20, 1)

    glTranslatef(1.6, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.2, 0.2, 0.2, 20, 1)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.075, 0.075, 0.2, 20, 1)
    quadric = gluNewQuadric()
    gluDisk(quadric, 0.075, 0.2, 20, 1)

    glPopMatrix()

    glPushMatrix()

    glColor3f(0.2, 0.2, 0.2)
    #setMaterial(0.2, 0.2, 0.2)

    glTranslatef(-1.05, 0.1, 0.5)
    cube(0.1, 0.2, 1)

    glTranslatef(2.1, 0, 0)
    cube(0.1, 0.2, 1)

    glPopMatrix()

def prtStraightTrack(pillar):
    glPushMatrix()

    glColor3f(0.6, 0.3, 0)
    #setMaterial(0.6, 0.3, 0)

    cube(10, 1, 10)

    glColor3f(0.6, 0.4, 0)
    #setMaterial(0.6, 0.4, 0)

    glTranslatef(0, 0.6, 0)
    cube(1, 0.2, 10)

    glColor3f(0.5, 0.4, 0)
    #setMaterial(0.5, 0.4, 0)

    glTranslatef(0, 0.6, 0)
    cube(0.4, 1, 10)

    glColor3f(0.5, 0.5, 0)
    #setMaterial(0.5, 0.5, 0)

    glTranslatef(0, 0.6, 0)
    cube(1, 0.2, 10)

    glColor3f(0.7, 0.7, 0.7)
    #setMaterial(0.7, 0.7, 0.7)

    glTranslatef(0.35, -0.3, -5)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.1, 0.1, 10, 20, 1)

    glTranslatef(0, -0.3, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.1, 0.1, 10, 20, 1)

    glTranslatef(0, -0.3, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.1, 0.1, 10, 20, 1)

    glTranslatef(-0.7, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.1, 0.1, 10, 20, 1)

    glTranslatef(0, 0.3, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.1, 0.1, 10, 20, 1)

    glTranslatef(0, 0.3, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.1, 0.1, 10, 20, 1)

    glColor3f(0.4, 0.2, 0)
    #setMaterial(0.4, 0.2, 0)

    glTranslatef(5.25, -0.4, 5)
    cube(0.2, 1.2, 10)

    glColor3f(0.45, 0.4, 0)
    #setMaterial(0.45, 0.4, 0)

    glTranslatef(-0.25, 0, 0)
    cube(0.3, 0.1, 10)

    glColor3f(0.4, 0.35, 0.05)
    #setMaterial(0.4, 0.35, 0.05)

    glTranslatef(-0.2, 0, 0)
    cube(0.1, 0.6, 10)

    glColor3f(0.4, 0.2, 0)
    #setMaterial(0.4, 0.2, 0)

    glTranslatef(-9.35, 0, 0)
    cube(0.2, 1.2, 10)

    glColor3f(0.45, 0.4, 0)
    #setMaterial(0.45, 0.4, 0)

    glTranslatef(0.25, 0, 0)
    cube(0.3, 0.1, 10)

    glColor3f(0.4, 0.35, 0.05)
    #setMaterial(0.4, 0.35, 0.05)

    glTranslatef(0.2, 0, 0)
    cube(0.1, 0.6, 10)

    glColor3f(0.6, 0.4, 0)
    #setMaterial(0.6, 0.4, 0)

    glTranslatef(2, -0.6, 0)
    cube(3, 0.01, 10)

    glTranslatef(5, 0, 0)
    cube(3, 0.01, 10)

    glTranslatef(2.5, 0, 0)

    glColor3f(0.5, 0.5, 0.5)
    #setMaterial(0.5, 0.5, 0.5)
    if(pillar):
        glPushMatrix()
        glTranslatef(-5, -8, 0)
        cube(4, 8, 3)
        glPopMatrix()

    glBegin(GL_POLYGON)
    glVertex3f(0, 1.2, 5)
    glVertex3f(0, 1.2, -5)
    glVertex3f(0, -2, -5)
    glVertex3f(0, -2, 5)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(0, -2, -5)
    glVertex3f(0, -2, 5)
    glVertex3f(-3, -5, 5)
    glVertex3f(-3, -5, -5)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-3, -5, -5)
    glVertex3f(-3, -5, 5)
    glVertex3f(-7, -5, 5)
    glVertex3f(-7, -5, -5)
    glEnd()
    
    glBegin(GL_POLYGON)
    glVertex3f(-7, -5, -5)
    glVertex3f(-7, -5, 5)
    glVertex3f(-10.1, -2, 5)
    glVertex3f(-10.1, -2, -5)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex3f(-10.1, 1.2, 5)
    glVertex3f(-10.1, 1.2, -5)
    glVertex3f(-10.1, -2, -5)
    glVertex3f(-10.1, -2, 5)
    glEnd()

    glPopMatrix()

def prtLight():
    glPushMatrix()

    glColor3f(0.8, 0.8, 0.8)
    #setMaterial(0.8, 0.8, 0.8)

    glRotatef(90, 1, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.2, 0.2, 5, 20, 1)

    glColor3f(0.6, 0.6, 0.6)
    #setMaterial(0.6, 0.6, 0.6)

    glTranslatef(0.5, 0, 0)
    cube(2, 1, 0.2)

    glPopMatrix()

def setMaterial(r, g, b):
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [r*0.25, g*0.25, b*0.25, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [r, g, b, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [r*0.5, g*0.5, b*0.5, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 30)

def main():
    rotation = 0
    rotationDirection = 0
    cameraSpeed = 0
    cameraPosition = 0

    previousTime = time.time()
    delta = 0

    position = 0
    speed = 0
    maxSpeed = 4.5
    minSpeed = 0
    acceleration = 1.5

    position2 = 3
    speed2 = 0

    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    light_diffuse = [0.8, 0.8, 0.8, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_position = [1.0, 1.0, 1.0, 0.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    while True:
        delta = time.time() - previousTime
        previousTime = time.time()
        speed += acceleration*delta
        if speed > maxSpeed:
            speed = maxSpeed
        if speed < minSpeed:
            speed = minSpeed
        position += speed*delta

        speed2 += acceleration*delta
        if speed2 > maxSpeed:
            speed2 = maxSpeed
        if speed2 < minSpeed:
            speed2 = minSpeed
        position2 += speed2*delta

        if position > 36:
            position = 0
            speed = 0
        
        if position2 > 36:
            position2 = 0
            speed2 = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    rotationDirection = 1
                elif event.key == K_LEFT:
                    rotationDirection = -1
                
                if event.key == K_UP:
                    cameraSpeed = 1
                elif event.key == K_DOWN:
                    cameraSpeed = -1

                if event.key == K_p:
                    acceleration = -acceleration
            elif event.type == KEYUP:
                if event.key == K_RIGHT and rotationDirection == 1:
                    rotationDirection = 0
                elif event.key == K_LEFT and rotationDirection == -1:
                    rotationDirection = 0
                
                if event.key == K_UP and cameraSpeed == 1:
                    cameraSpeed = 0
                elif event.key == K_DOWN and cameraSpeed == -1:
                    cameraSpeed = 0
        if rotationDirection == -1:
            rotation += 6
        elif rotationDirection == 1:
            rotation += -6
        
        cameraPosition += cameraSpeed

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(0, 3, 15,  0, 0, 0,  0, 1, 0)
        glTranslatef(0, 0, cameraPosition)
        glRotatef(-rotation, 0, 1, 0)
        glScalef(0.5, 0.5, 0.5)

        prtStraightTrack(True)
        glTranslatef(0, 0, -10)
        prtStraightTrack(False)

        glPushMatrix()
        glTranslatef(0, 7, -5)
        prtLight()
        glTranslatef(0, 0, 13)
        glRotatef(180, 0, 1, 0)
        prtLight()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, 0, -6)
        for i in range(1,19):
            glScalef(1, 1, 0.333)
            prtStraightTrack(False)
            glScalef(1, 1, 3)
            glRotatef(5, 0, 1, 0)
            glTranslatef(0, 0, -1)
        glTranslatef(0, 0, -5)
        prtStraightTrack(True)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, 0, 16)
        for i in range(1,19):
            glScalef(1, 1, 0.333)
            prtStraightTrack(False)
            glScalef(1, 1, 3)
            glRotatef(5, 0, 1, 0)
            glTranslatef(0, 0, 1)
        glTranslatef(0, 0, 5)

        glPushMatrix()
        glScalef(2, 2, 2)
        glRotatef(90, 0, 1, 0)
        glTranslatef(0, 0.5, 1.25)
        glPushMatrix()

        glTranslatef(min(position, 3.5), 0, 0)

        turns = max(0, min((position - 3.5)/0.153, 36))
        for i in range(round(turns)):
            glRotatef(-2.5, 0, 1, 0)
            glTranslatef(0.153, 0, -0.01)
        if position > 3.5 and position < 9:
            glTranslatef(position-3.5-round(turns)*0.153, 0, -0.065*(position-3.5-round(turns)*0.153))

        glTranslatef(max(0, min(position-9, 12)), 0, 0)
        
        turns = max(0, min((position - 21)/0.306, 36))
        for i in range(round(turns)):
            glRotatef(2.5, 0, 1, 0)
            glTranslatef(0.306, 0, -0.005)
        if position > 21 and position < 32:
            glTranslatef(position-21-round(turns)*0.306, 0, -0.016*(position-21-round(turns)*0.306))
        
        glTranslatef(max(0, min(position-32, 4)), 0, 0)
 
        prtCar()
        glPopMatrix()

        glRotatef(180, 0, 1, 0)
        glTranslatef(-17, 0, -19.55)

        glTranslatef(min(position2, 3.5), 0, 0)

        turns = max(0, min((position2 - 3.5)/0.153, 36))
        for i in range(round(turns)):
            glRotatef(-2.5, 0, 1, 0)
            glTranslatef(0.153, 0, -0.01)
        if position2 > 3.5 and position2 < 9:
            glTranslatef(position2-3.5-round(turns)*0.153, 0, -0.065*(position2-3.5-round(turns)*0.153))

        glTranslatef(max(0, min(position2-9, 12)), 0, 0)
        
        turns = max(0, min((position2 - 21)/0.306, 36))
        for i in range(round(turns)):
            glRotatef(2.5, 0, 1, 0)
            glTranslatef(0.306, 0, -0.005)
        if position2 > 21 and position2 < 32:
            glTranslatef(position2-21-round(turns)*0.306, 0, -0.016*(position2-21-round(turns)*0.306))
        
        glTranslatef(max(0, min(position2-32, 4)), 0, 0)

        prtCar()
        glPopMatrix()

        prtStraightTrack(True)
        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

main()