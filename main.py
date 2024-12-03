import math
from dataclasses import dataclass
from typing import List, Sequence

import pygame
from OpenGL.raw.GLU import gluLookAt, gluPerspective
from pygame.locals import *
from OpenGL.GL import *
from PIL import Image

global time # time since beginning of program in ms

def draw_at(draw_func, posx, posy, posz):
    glPushMatrix()
    glTranslate(posx, posy, posz)
    draw_func()
    glPopMatrix()

def draw_human(human, human_body_model, human_arm_model):
    global time
    if human.is_waving:
        glPushMatrix()
        glTranslate(-0.24308, 1.3941, 0)
        wave_speed = 2
        glRotate(math.fabs(math.sin((time - human.started_waving) / 1000 * wave_speed)) * -180, 0, 0, 1)
        draw_model(human_arm_model)
        glPopMatrix()
    else:
        draw_at(lambda: draw_model(human_arm_model), -0.24308, 1.3941, 0)
    draw_model(human_body_model)

@dataclass
class Material:
    specular_exponent : float # Ns
    ambient_reflection : List[float] # Ka
    diffused_reflection : List[float] # Kd
    specular_reflection : List[float] # Ks
    emissive_material : List[float] # Ke
    index_of_reflection : float # Ni
    dissolve_index : float # Dissolve Index (transparency)
    illum : int

    @staticmethod
    def load(mtl_file):
        specular_exponent = 1
        ambient_reflection = [0, 0, 0]
        diffused_reflection = [0, 0, 0]
        specular_reflection = [0, 0, 0]
        emissive_material = [0, 0, 0]
        index_of_reflection = 1
        dissolve_index = 1
        illum = 2
        with open(mtl_file, 'r') as mtl:
            for line in mtl:
                line = line.strip()
                if line.startswith("newmtl"): # Expects only one material
                    continue
                if line.startswith("#"):
                    continue
                if len(line) == 0:
                    continue

                if line.startswith("Ns"): specular_exponent = float(line.split()[1])
                elif line.startswith("Ka"): ambient_reflection = [float(line.split()[1]), float(line.split()[2]), float(line.split()[3])]
                elif line.startswith("Kd"): diffused_reflection = [float(line.split()[1]), float(line.split()[2]), float(line.split()[3])]
                elif line.startswith("Ks"): specular_reflection = [float(line.split()[1]), float(line.split()[2]), float(line.split()[3])]
                elif line.startswith("Ke"): emissive_material = [float(line.split()[1]), float(line.split()[2]), float(line.split()[3])]
                elif line.startswith("Ni"): index_of_reflection = float(line.split()[1])
                elif line.startswith("d"): dissolve_index = float(line.split()[1])
                elif line.startswith("illum"): illum = int(line.split()[1])
                else: print("Cannot parse line of material file: " + line)
        return Material(specular_exponent, ambient_reflection, diffused_reflection, specular_reflection, emissive_material, index_of_reflection, dissolve_index, illum)

@dataclass
class Mesh:
    default_material = Material(1, [1, 1, 1], [1, 1, 1], [1, 1, 1], [0, 0, 0], 1, 1, 2)
    # From obj file
    vertices : List[List[float]] # Vertex Array
    normals : List[List[float]] # Normals Array
    uvs : List[List[float]] # Texture Vertex Array
    faces : List[List[List[int]]] # Faces Array. 1 index to vertices, 2 index to texture coordinates, 3 index to normals
    # From mtl file
    material : Material
    # From .png or similar file
    texture : Sequence[int]
    texture_id : int # The texture index of where the texture is stored at on the gpu. If not yet passed to gpu, -1.

    # Sends the texture to the GPU and stores the texture id into texture_id. Throws if texture_id is not -1.
    # When leaving this method, the currently bound texture is this texture
    def send_texture(self):
        if self.texture_id != -1: raise Exception("Texture is already in GPU.")
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1024, 1024, 0, GL_RGB, GL_UNSIGNED_BYTE, self.texture) # TODO: 1024 magic number

    def clear_texture(self):
        if self.texture_id == -1: raise Exception("Texture is not loaded into GPU.")
        glDeleteTextures(self.texture_id)
        self.texture_id = -1

    def bind_texture(self):
        if self.texture_id == -1: raise Exception("Texture is not loaded into GPU.")
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

    def unbind_texture(self):
        if self.texture_id == -1: raise Exception("Texture cannot be bound if it is not loaded into GPU...")
        glBindTexture(GL_TEXTURE_2D, 0)

    @staticmethod
    def load(obj_file, texture_file):
        vertices = []
        normals = []
        uvs = []
        faces = []
        material = Mesh.default_material
        with open(obj_file, 'r') as mtl:
            for line in mtl:
                line = line.strip()
                if len(line) == 0:
                    continue
                if line.startswith("#"):
                    continue
                if line.startswith("o"): # Expects only one object
                    continue
                if line.startswith("s"): # Smooth shading
                    continue
                if line.startswith("usemtl"): # Expects only one material
                    continue

                split = line.split(' ')

                if line.startswith("mtllib"):
                    material = Material.load('/'.join(obj_file.split('/')[:-1]) + "/" + ' '.join(split[1:])) # Probably a terrible solution
                elif line.startswith("vn"):
                    normals.append([float(split[1]), float(split[2]), float(split[3])])
                elif line.startswith("vt"):
                    uvs.append([float(split[1]), float(split[2])])
                elif line.startswith("v"):
                    vertices.append([float(split[1]), float(split[2]), float(split[3])])
                elif line.startswith("f"):
                    face = []
                    for vert in line.split()[1:]:
                        indices = vert.split('/')
                        face.append([int(indices[0]) - 1, int(indices[1]) - 1, int(indices[2]) - 1]) # - 1 because indices start at 1 not 0
                    faces.append(face)
                else:
                    print("Cannot parse line of obj file: " + line)
        texture = Image.open(texture_file).transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert("RGB").tobytes()
        return Mesh(vertices, normals, uvs, faces, material, texture, -1)

def draw_model(model : Mesh):
    model.bind_texture()
    length = -1  # -1 -> glBegin has not been called, 0 -> drawing polygons, 3 -> drawing triangles, 4 -> drawing quads
    for face in model.faces:
        if len(face) != length:
            if length != -1:
                glEnd()
            length = len(face)
            if length != 3 or length != 4:
                length = 0
            if length == 3:
                glBegin(GL_TRIANGLES)
            elif length == 4:
                glBegin(GL_QUADS)
            else:
                glBegin(GL_POLYGON)
        elif length == 0:
            glEnd()
            glBegin(GL_POLYGON)

        for indices in face:  # Each 'indices' contains 3 vertex indices: 0 -> mesh vertex index, 1 -> texture vertex index, 2 -> normal vertex index
            glNormal3fv(model.normals[indices[2]])
            glTexCoord2fv(model.uvs[indices[1]])
            glVertex3fv(model.vertices[indices[0]])
    if length != -1:
        glEnd()
    model.unbind_texture()

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
    def start_waving(self, cur_time):
        self.is_waving = True
        self.started_waving = cur_time
    def stop_waving(self):
        self.is_waving = False

def lerp(t, a, b):
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]

def main():
    global time; time = 0
    frame_len = 10 # Frame length in ms
    rot = 0

    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_TEXTURE_2D) # Enable texture mapping
    glEnable(GL_DEPTH_TEST)

    # Array to store driving cars
    cars = []
    # Store human state
    human = Human()

    # Import models
    car_model = Mesh.load("Resources/car.obj", "Resources/Car.png"); car_model.send_texture(); car_model.unbind_texture()
    human_body_model = Mesh.load("Resources/humanbody.obj", "Resources/Human.png"); human_body_model.send_texture(); human_body_model.unbind_texture()
    human_arm_model = Mesh.load("Resources/humanarm.obj", "Resources/Human.png"); human_arm_model.send_texture(); human_arm_model.unbind_texture()

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
                if event.key == pygame.K_h:
                    if human.is_waving: human.stop_waving()
                    else: human.start_waving(time)

        # Render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
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
                continue
            pos = lerp(t, car.pos, car.dest)
            draw_at(lambda: draw_model(car_model), *pos)
        glRotate(rot, 0, 1, 0)
        draw_at(lambda: draw_human(human, human_body_model, human_arm_model), 0, 0, 0) # TODO: Set human position
        draw_at(lambda: draw_model(car_model), 0, 2, 0) # This can be removed, it is simply demoing the car model. We can add cars to the scene by adding them to the cars array.
        pygame.display.flip()

        # Wait for next frame
        glFlush()
        pygame.time.wait(frame_len)
        time += frame_len

main()