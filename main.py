from dataclasses import dataclass
from typing import List, Sequence
import pygame
import math
import time
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

global timeVar  # Time since the beginning of the program

# Global variables for day/night cycle
is_day = True           # Indicates whether it's currently day
transition_in_progress = False  # Indicates if a transition is happening
transition_start_time = 0       # Time when the transition started
transition_duration = 5000      # Duration of the transition in milliseconds (5 seconds)

# Light position variables
day_light_position = [0.0, 100.0, 0.0, 1.0]   # High in the sky
night_light_position = [0.0, -200.0, 0.0, 1.0]  # Below the scene
current_light_position = day_light_position.copy()

# Background color
background_color = [0.53, 0.81, 0.92, 1.0]  # Initial sky color (day)

def lerp(start, end, t):
    """Linear interpolation between start and end by t."""
    return start + t * (end - start)

def update_day_night_cycle():
    """Updates the light position and sky color during the day/night transition."""
    global transition_in_progress, transition_start_time, current_light_position, background_color

    if transition_in_progress:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - transition_start_time
        t = min(elapsed / transition_duration, 1.0)  # Normalized time [0.0, 1.0]

        if is_day:
            # Transitioning from night to day
            current_light_position = [
                lerp(night_light_position[i], day_light_position[i], t)
                for i in range(4)
            ]
            background_color = [
                lerp(0.05, 0.53, t),  # Red component
                lerp(0.05, 0.81, t),  # Green component
                lerp(0.15, 0.92, t),  # Blue component
                1.0                    # Alpha
            ]
        else:
            # Transitioning from day to night
            current_light_position = [
                lerp(day_light_position[i], night_light_position[i], t)
                for i in range(4)
            ]
            background_color = [
                lerp(0.53, 0.05, t),  # Red component
                lerp(0.81, 0.05, t),  # Green component
                lerp(0.92, 0.15, t),  # Blue component
                1.0                    # Alpha
            ]

        # Update the background color
        glClearColor(*background_color)

        if t >= 1.0:
            # Transition complete
            transition_in_progress = False
    else:
        # No transition in progress; ensure light and background are set correctly
        if is_day:
            current_light_position = day_light_position.copy()
            background_color = [0.53, 0.81, 0.92, 1.0]  # Sky blue
        else:
            current_light_position = night_light_position.copy()
            background_color = [0.05, 0.05, 0.15, 1.0]  # Dark blue

        glClearColor(*background_color)
        

def load_texture(image_path):
    """Loads a texture from an image file and returns the texture ID."""
    # Generate a texture ID
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Load the image using PIL
    image = Image.open(image_path)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)  # Flip the image vertically
    img_data = image.convert("RGB").tobytes()

    # Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)  # Repeat texture horizontally
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)  # Repeat texture vertically
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)  # Linear filtering
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Upload the texture data
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height,
                 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

    return texture_id

def draw_at(draw_func, posx, posy, posz):
    glPushMatrix()
    glTranslate(posx, posy, posz)
    draw_func()
    glPopMatrix()

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

    def bind(self):
        glMaterial(GL_FRONT, GL_SPECULAR, self.specular_reflection)
        glMaterial(GL_FRONT, GL_AMBIENT, self.ambient_reflection)
        glMaterial(GL_FRONT, GL_DIFFUSE, self.diffused_reflection)
        glMaterial(GL_FRONT, GL_SHININESS, [self.specular_exponent])
        glMaterial(GL_FRONT, GL_EMISSION, self.emissive_material)

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
class Model:
    default_material = Material(1, [1, 1, 1], [1, 1, 1], [1, 1, 1], [0, 0, 0], 1, 1, 2)
    # From obj file
    vertices : List[List[float]] # Vertex Array
    normals : List[List[float]] # Normals Array
    uvs : List[List[float]] # Texture Vertex Array
    faces : List[List[List[int]]] # Faces Array. 1 index to vertices, 2 index to texture coordinates, 3 index to normals
    # From mtl file
    material : Material
    # From .png or similar file
    texture : Sequence[int] or None
    texture_id : int # The texture index of where the texture is stored at on the gpu. If not yet passed to gpu, -1.

    # Sends the texture to the GPU and stores the texture id into texture_id. Throws if texture_id is not -1.
    # When leaving this method, the currently bound texture is this texture
    def send_texture(self):
        if self.texture_id != -1: raise Exception("Texture is already in GPU.")
        if self.texture is None: raise Exception("Cannot send a texture if there is not one to send.")
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
    def load(obj_file, texture_file = None):
        vertices = []
        normals = []
        uvs = []
        faces = []
        material = Model.default_material
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
        texture = None
        if texture_file is not None:
            texture = Image.open(texture_file).transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert("RGB").tobytes()
        return Model(vertices, normals, uvs, faces, material, texture, -1)

def draw_model(model : Model):
    if model.texture is not None:
        model.bind_texture()
    model.material.bind()
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
            if model.texture is not None:
                glTexCoord2fv(model.uvs[indices[1]])
            glVertex3fv(model.vertices[indices[0]])
    if length != -1:
        glEnd()
    if model.texture is not None:
        model.unbind_texture()

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

def draw_prt():
        glPushMatrix()
        glScale(1.2, 1.2, 1.2)
        glRotatef(90, 0, 1, 0)
        glTranslatef(-40, 10, 10)
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
        glTranslatef(0, 0, -10)
        prtStraightTrack(False)
        glTranslatef(0, 0, -10)
        prtStraightTrack(False)
        glTranslatef(0, 0, -10)
        prtStraightTrack(True)
        prtStraightTrack(False)
        glTranslatef(0, 0, -10)
        prtStraightTrack(False)
        glTranslatef(0, 0, -10)
        prtStraightTrack(True)
        prtStraightTrack(False)
        glTranslatef(0, 0, -10)
        prtStraightTrack(False)
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
        prtStraightTrack(True)

        glTranslatef(0, 0, 5)
        for i in range(1,19):
            glScalef(1, 1, 0.333)
            prtStraightTrack(False)
            glScalef(1, 1, 3)
            glRotatef(-5, 0, 1, 0)
            glTranslatef(0, 0, 1)
        
        glTranslatef(0, 0, 5)
        prtStraightTrack(True)

        glTranslatef(0, 0, 10)
        prtStraightTrack(False)
        glTranslatef(0, 0, 10)
        prtStraightTrack(False)
        glTranslatef(0, 0, 10)
        prtStraightTrack(True)
        glTranslatef(0, 0, 10)
        prtStraightTrack(False)
        glTranslatef(0, 0, 10)
        prtStraightTrack(False)
        glTranslatef(0, 0, 10)
        prtStraightTrack(True)

        glPushMatrix()
        glScalef(2, 2, 2)
        glRotatef(90, 0, 1, 0)
        glTranslatef(0, 0.5, 1.25)
        glPushMatrix()

        glTranslatef(min(position, 33), 0, 0)
        turns = max(0, min((position - 33)/0.306, 36))
        for i in range(round(turns)):
            glRotatef(2.5, 0, 1, 0)
            glTranslatef(0.306, 0, -0.005)
        if position > 33 and position < 44:
            glTranslatef(position-33-round(turns)*0.306, 0, -0.016*(position-33-round(turns)*0.306))

        glTranslatef(max(0, min(position-44, 5.75)), 0, 0)
        
        turns = max(0, min((position - 49.75)/0.153, 36))
        for i in range(round(turns)):
            glRotatef(-2.5, 0, 1, 0)
            glTranslatef(0.153, 0, -0.01)
        if position > 49.75 and position < 55.25:
            glTranslatef(position-49.75-round(turns)*0.153, 0, 0.065*(position-49.75-round(turns)*0.153))
        
        glTranslatef(max(0, min(position-55.25, 12.25)), 0, 0)

        turns = max(0, min((position - 67.5)/0.306, 36))
        for i in range(round(turns)):
            glRotatef(2.5, 0, 1, 0)
            glTranslatef(0.306, 0, -0.005)
        if position > 67.5 and position < 78.5:
            glTranslatef(position-67.5-round(turns)*0.306, 0, -0.016*(position-67.5-round(turns)*0.306))
        
        glTranslatef(max(0, min(position-78.5, 34.5)), 0, 0)

        '''turns = max(0, min((position - 40)/0.153, 36))
        for i in range(round(turns)):
            glRotatef(-2.5, 0, 1, 0)
            glTranslatef(0.153, 0, -0.01)
        if position > 40 and position < 45.5:
            glTranslatef(position-40-round(turns)*0.153, 0, -0.065*(position-40-round(turns)*0.153))'''
        
        '''turns = max(0, min((position - 21)/0.306, 36))
        for i in range(round(turns)):
            glRotatef(2.5, 0, 1, 0)
            glTranslatef(0.306, 0, -0.005)
        if position > 21 and position < 32:
            glTranslatef(position-21-round(turns)*0.306, 0, -0.016*(position-21-round(turns)*0.306))
        
        glTranslatef(max(0, min(position-32, 4)), 0, 0)'''
 
        prtCar()
        glPopMatrix()

        glRotatef(270, 0, 1, 0)
        glTranslatef(-58, 0, -59.6)

        glTranslatef(min(position2, 35), 0, 0)
        turns = max(0, min((position2 - 35)/0.153, 36))
        for i in range(round(turns)):
            glRotatef(-2.5, 0, 1, 0)
            glTranslatef(0.153, 0, -0.01)
        if position2 > 35 and position2 < 40.5:
            glTranslatef(position2-35-round(turns)*0.153, 0, -0.065*(position2-35-round(turns)*0.153))

        glTranslatef(max(0, min(position2-40.5, 12)), 0, 0)

        turns = max(0, min((position2 - 52.5)/0.306, 36))
        for i in range(round(turns)):
            glRotatef(2.5, 0, 1, 0)
            glTranslatef(0.306, 0, -0.005)
        if position2 > 52.5 and position2 < 63.5:
            glTranslatef(position2-52.5-round(turns)*0.306, 0, -0.016*(position2-52.5-round(turns)*0.306))
        
        glTranslatef(max(0, min(position2-63.5, 5.75)), 0, 0)

        turns = max(0, min((position2 - 69.25)/0.153, 36))
        for i in range(round(turns)):
            glRotatef(-2.5, 0, 1, 0)
            glTranslatef(0.153, 0, -0.01)
        if position2 > 69.25 and position2 < 74.75:
            glTranslatef(position2-69.25-round(turns)*0.153, 0, -0.065*(position2-69.25-round(turns)*0.153))

        glTranslatef(max(0, min(position2-74.75, 37.25)), 0, 0)

        prtCar()
        glPopMatrix()

        #prtStraightTrack(True)
        glPopMatrix()
        glPopMatrix()

def draw_cylinder(radius, segments, height, offset=0):
    # Draw the bottom face
    glBegin(GL_TRIANGLE_FAN)
    glColor3f(0.96, 0.87, 0.70)  # Beige color
    glVertex3f(0, offset, 0)  # Center of the bottom face
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glVertex3f(x, offset, z)
    glEnd()

    # Draw the top face
    glBegin(GL_TRIANGLE_FAN)
    glColor3f(0.96, 0.87, 0.70)  # Beige color
    glVertex3f(0, offset + height, 0)  # Center of the top face
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glVertex3f(x, offset + height, z)
    glEnd()

    # Draw the sidewalls
    glBegin(GL_QUAD_STRIP)
    glColor3f(0.96, 0.87, 0.70)  # Beige color
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glVertex3f(x, offset, z)  # Bottom vertex
        glVertex3f(x, offset + height, z)  # Top vertex
    glEnd()

# Function to draw walls for the coliseum (upright)
def draw_coliseum_walls(radius, segments, height, protrusion=1):
    wall_radius = radius + protrusion  # Increase radius for protrusion

    for i in range(segments):
        angle1 = 2 * math.pi * i / segments
        angle2 = 2 * math.pi * (i + 1) / segments
        x1, z1 = wall_radius * math.cos(angle1), wall_radius * math.sin(angle1)
        x2, z2 = wall_radius * math.cos(angle2), wall_radius * math.sin(angle2)

        # Leave gaps for arches or windows
        if i % 4 == 0:  # Adjust this value to control the number of gaps
            continue

        glBegin(GL_QUADS)
        glColor3f(0.98, 0.92, 0.78)  # Slightly lighter beige
        glVertex3f(x1, 0, z1)           # Bottom-left corner
        glVertex3f(x2, 0, z2)           # Bottom-right corner
        glVertex3f(x2, height, z2)      # Top-right corner
        glVertex3f(x1, height, z1)      # Top-left corner
        glEnd()

def draw_dome(radius, segments, rings, offset, height_scale=0.5):

    glColor3f(0.5, 0.5, 0.5)  # Gray color for the dome

    for i in range(rings):
        theta1 = math.pi * i / (2 * rings)  # Latitude angle (bottom to top)
        theta2 = math.pi * (i + 1) / (2 * rings)

        glBegin(GL_TRIANGLE_STRIP)
        for j in range(segments + 1):
            phi = 2 * math.pi * j / segments  # Longitude angle (around)

            # First vertex of the strip
            x1 = radius * math.sin(theta1) * math.cos(phi)
            y1 = radius * math.cos(theta1) * height_scale  # Scaled height
            z1 = radius * math.sin(theta1) * math.sin(phi)
            glVertex3f(x1, y1 + offset, z1)

            # Second vertex of the strip
            x2 = radius * math.sin(theta2) * math.cos(phi)
            y2 = radius * math.cos(theta2) * height_scale  # Scaled height
            z2 = radius * math.sin(theta2) * math.sin(phi)
            glVertex3f(x2, y2 + offset, z2)
        glEnd()

def init_opengl():
    """Initializes OpenGL settings and projection matrix."""
    glEnable(GL_DEPTH_TEST)  # Enable depth testing for 3D rendering
    glEnable(GL_LIGHTING)    # Enable lighting
    glEnable(GL_LIGHT0)      # Enable a default light source
    glEnable(GL_COLOR_MATERIAL)  # Enable color material tracking
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glEnable(GL_NORMALIZE)  # Normalize normals for consistent lighting
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 800 / 600, 0.1, 1000)  # Set up perspective projection
    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0, -1, -20)  # Move scene slightly for better initial view
    glClearColor(0.53, 0.81, 0.92, 1.0)  # Set background color to light blue



def draw_ground():
    """Draws the ground plane with a texture."""
    glDisable(GL_LIGHTING)  # Disable lighting for the ground
    glEnable(GL_TEXTURE_2D)  # Enable texture mapping
    glBindTexture(GL_TEXTURE_2D, ground_texture_id)
    glColor3f(1.0, 1.0, 1.0)  # Set color to white to display texture colors accurately

    glBegin(GL_QUADS)
    # Repeat the texture 10 times across the ground
    glTexCoord2f(0.0, 0.0); glVertex3f(-150, -2, 150)
    glTexCoord2f(10.0, 0.0); glVertex3f(150, -2, 150)
    glTexCoord2f(10.0, 10.0); glVertex3f(150, -2, -150)
    glTexCoord2f(0.0, 10.0); glVertex3f(-150, -2, -150)
    glEnd()

    glDisable(GL_TEXTURE_2D)  # Disable textures for subsequent objects
    glEnable(GL_LIGHTING)     # Re-enable lighting if it was disabled

def draw_dotted_line_straight():
    """Draws a dotted yellow line down the straight road."""
    glEnable(GL_POLYGON_OFFSET_FILL)  # Prevents Z-fighting
    glColor3f(1.0, 1.0, 0.0)  # Yellow color for the line

    # Line parameters
    dash_length = 10
    gap_length = 5
    line_width = 1
    z_start = -150
    z_end = 150
    z = z_start
    x_center = 0

    glBegin(GL_QUADS)
    while z < z_end:
        x_left = x_center - line_width
        x_right = x_center + line_width
        z0 = z
        z1 = min(z + dash_length, z_end)  # Ensure the dash doesn't exceed road length

        # Draw one dash as a quad
        glVertex3f(x_left, 0.02, z0)
        glVertex3f(x_right, 0.02, z0)
        glVertex3f(x_right, 0.02, z1)
        glVertex3f(x_left, 0.02, z1)

        z += dash_length + gap_length  # Move to the position of the next dash
    glEnd()
    glDisable(GL_POLYGON_OFFSET_FILL)

def draw_dotted_line_diagonal():
    """Draws a dotted yellow line down the diagonal road."""
    glEnable(GL_POLYGON_OFFSET_FILL)  # Prevents Z-fighting
    glColor3f(1.0, 1.0, 0.0)  # Yellow color for the line

    # Line parameters
    dash_length = 10
    gap_length = 5
    line_width = 1
    diagonal_length = 150
    start_distance = 10  # Distance from intersection to start drawing dashes
    angle = math.radians(30)  # Angle of diagonal road

    # Calculate number of dashes
    t_initial = start_distance
    num_dashes = int((diagonal_length - start_distance) / (dash_length + gap_length)) + 1

    dx = math.cos(angle)
    dz = -math.sin(angle)

    dx_perp = math.sin(angle)
    dz_perp = math.cos(angle)

    x_start = 0  # Starting point at intersection
    z_start = 0

    glBegin(GL_QUADS)
    for i in range(num_dashes):
        t0 = t_initial + i * (dash_length + gap_length)
        t1 = t0 + dash_length

        # Adjust end of the last dash
        if t1 > diagonal_length:
            t1 = diagonal_length

        # Center positions of start and end of the dash
        x0_center = x_start + t0 * dx
        z0_center = z_start + t0 * dz
        x1_center = x_start + t1 * dx
        z1_center = z_start + t1 * dz

        # Offset for line width
        x_offset = line_width * dx_perp
        z_offset = line_width * dz_perp
        y_offset = 0.05  # Slightly above the road to avoid Z-fighting

        # Draw dash as a quad
        glVertex3f(x0_center - x_offset, y_offset, z0_center - z_offset)
        glVertex3f(x0_center + x_offset, y_offset, z0_center + z_offset)
        glVertex3f(x1_center + x_offset, y_offset, z1_center + z_offset)
        glVertex3f(x1_center - x_offset, y_offset, z1_center - z_offset)
    glEnd()
    glDisable(GL_POLYGON_OFFSET_FILL)

def draw_road():
    """Draws the straight and diagonal roads."""
    # Draw the straight road
    glColor3f(0.2, 0.2, 0.2)  # Dark gray color for the road
    glBegin(GL_QUADS)
    glVertex3f(-6, 0.01, -150)
    glVertex3f(6, 0.01, -150)
    glVertex3f(6, 0.01, 150)
    glVertex3f(-6, 0.01, 150)
    glEnd()
    draw_dotted_line_straight()

    # Draw the diagonal road
    diagonal_length = 150
    angle = math.radians(30)
    road_width = 12

    # Direction vector along diagonal road
    dx = math.cos(angle)
    dz = -math.sin(angle)

    # Perpendicular vector for road width
    dx_perp = math.sin(angle)
    dz_perp = math.cos(angle)

    # Width offsets
    x_offset_width = (road_width / 2) * dx_perp
    z_offset_width = (road_width / 2) * dz_perp

    # Start and end points of diagonal road
    x_start = 0
    z_start = 0
    x_end = x_start + diagonal_length * dx
    z_end = z_start + diagonal_length * dz

    # Define the edges of the diagonal road
    x_start_left = x_start + x_offset_width
    z_start_left = z_start + z_offset_width
    x_start_right = x_start - x_offset_width
    z_start_right = z_start - z_offset_width
    x_end_left = x_end + x_offset_width
    z_end_left = z_end + z_offset_width
    x_end_right = x_end - x_offset_width
    z_end_right = z_end - z_offset_width

    glColor3f(0.2, 0.2, 0.2)  # Dark gray color for the road
    glBegin(GL_QUADS)
    glVertex3f(x_start_left, 0.01, z_start_left)
    glVertex3f(x_start_right, 0.01, z_start_right)
    glVertex3f(x_end_right, 0.01, z_end_right)
    glVertex3f(x_end_left, 0.01, z_end_left)
    glEnd()
    draw_dotted_line_diagonal()

def draw_tunnel():
    """Draws a tunnel into the mountain."""
    tunnel_width = 12  # Match straight road width
    tunnel_height = 15
    tunnel_depth = 40

    # Position of the tunnel entrance
    x_center = 0
    y_base = 0
    z_entrance = -50

    # Define vertices of the tunnel (rectangular prism)

    # Front face (entrance)
    blf = (x_center - tunnel_width / 2, y_base, z_entrance)
    brf = (x_center + tunnel_width / 2, y_base, z_entrance)
    tlf = (x_center - tunnel_width / 2, y_base + tunnel_height, z_entrance)
    trf = (x_center + tunnel_width / 2, y_base + tunnel_height, z_entrance)

    # Back face
    blb = (x_center - tunnel_width / 2, y_base, z_entrance - tunnel_depth)
    brb = (x_center + tunnel_width / 2, y_base, z_entrance - tunnel_depth)
    tlb = (x_center - tunnel_width / 2, y_base + tunnel_height, z_entrance - tunnel_depth)
    trb = (x_center + tunnel_width / 2, y_base + tunnel_height, z_entrance - tunnel_depth)

    glColor3f(0.5, 0.2, 0.2)  # Brick red color
    glBegin(GL_QUADS)

    # Front face
    glVertex3f(*blf)
    glVertex3f(*brf)
    glVertex3f(*trf)
    glVertex3f(*tlf)

    # Back face
    glVertex3f(*blb)
    glVertex3f(*brb)
    glVertex3f(*trb)
    glVertex3f(*tlb)

    # Left face
    glVertex3f(*blf)
    glVertex3f(*blb)
    glVertex3f(*tlb)
    glVertex3f(*tlf)

    # Right face
    glVertex3f(*brf)
    glVertex3f(*brb)
    glVertex3f(*trb)
    glVertex3f(*trf)

    # Top face
    glVertex3f(*tlf)
    glVertex3f(*tlb)
    glVertex3f(*trb)
    glVertex3f(*trf)

    # Bottom face
    glVertex3f(*blf)
    glVertex3f(*blb)
    glVertex3f(*brb)
    glVertex3f(*brf)
    glEnd()

    # Black front face to give the illusion of a tunnel entrance
    glEnable(GL_POLYGON_OFFSET_FILL)  # Prevents Z-fighting
    glPolygonOffset(-1.0, -1.0)  # Bring the entrance forward so it's visible
    glColor3f(0.0, 0.0, 0.0)  # Black color

    # Define vertices for entrance rectangle
    entrance_width = tunnel_width
    entrance_height = tunnel_height
    be_left = x_center - entrance_width / 2
    be_right = x_center + entrance_width / 2
    be_bottom = y_base
    be_top = y_base + entrance_height
    be_z = z_entrance

    glBegin(GL_QUADS)
    glVertex3f(be_left, be_bottom, be_z)
    glVertex3f(be_right, be_bottom, be_z)
    glVertex3f(be_right, be_top, be_z)
    glVertex3f(be_left, be_top, be_z)
    glEnd()
    glDisable(GL_POLYGON_OFFSET_FILL)

def draw_water():
    """Draws a river."""
    glColor3f(0, 0.5, 1)  # Keep darker than skybox color
    glBegin(GL_QUADS)

    # Long skinny quad for river
    glVertex3f(-120, 0.01, -150)
    glVertex3f(-100, 0.01, -150)
    glVertex3f(-100, 0.01, 150)
    glVertex3f(-120, 0.01, 150)
    glEnd()

def draw_pyramid(base_size, height, position, color):
    """Helper function to draw a mountain/pyramid with a snowy peak."""
    x, y, z = position
    half_base = base_size / 2
    peak_color = (1.0, 1.0, 1.0)  # White color for snowy peak

    glBegin(GL_TRIANGLES)

    # Front face
    glColor3f(*color)  # Base color
    glVertex3f(x - half_base, y, z - half_base)  # Base bottom-left
    glVertex3f(x + half_base, y, z - half_base)  # Base bottom-right
    glColor3f(*peak_color)  # Gradient from base color to peak color
    glVertex3f(x, y + height, z)

    # Right face
    glColor3f(*color)
    glVertex3f(x + half_base, y, z - half_base)
    glVertex3f(x + half_base, y, z + half_base)
    glColor3f(*peak_color)
    glVertex3f(x, y + height, z)

    # Back face
    glColor3f(*color)
    glVertex3f(x + half_base, y, z + half_base)
    glVertex3f(x - half_base, y, z + half_base)
    glColor3f(*peak_color)
    glVertex3f(x, y + height, z)

    # Left face
    glColor3f(*color)
    glVertex3f(x - half_base, y, z + half_base)
    glVertex3f(x - half_base, y, z - half_base)
    glColor3f(*peak_color)
    glVertex3f(x, y + height, z)
    glEnd()

    # Base of pyramid
    glColor3f(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)  # Slightly darker color
    glBegin(GL_QUADS)
    glVertex3f(x - half_base, y, z - half_base)
    glVertex3f(x + half_base, y, z - half_base)
    glVertex3f(x + half_base, y, z + half_base)
    glVertex3f(x - half_base, y, z + half_base)
    glEnd()

def draw_background():
    """Draws many pyramids to create a mountain range."""
    pyramids = [
        # Main cluster
        (50, 30, (-20, 0, -100)),
        (60, 40, (0, 0, -120)),
        (70, 50, (20, 0, -110)),
        (40, 25, (-50, 0, -90)),
        (55, 35, (-10, 0, -130)),
        (65, 45, (30, 0, -140)),
        (45, 28, (10, 0, -80)),
        (50, 30, (50, 0, -100)),
        (35, 22, (-35, 0, -120)),

        # Left cluster
        (40, 26, (-70, 0, -100)),
        (50, 35, (-90, 0, -120)),
        (60, 40, (-110, 0, -110)),
        (45, 30, (-130, 0, -100)),
        (55, 38, (-150, 0, -130)),
        (50, 35, (-170, 0, -110)),

        # Right cluster
        (40, 26, (70, 0, -100)),
        (50, 35, (90, 0, -120)),
        (60, 40, (110, 0, -110)),
        (45, 30, (130, 0, -100)),
        (55, 38, (150, 0, -130)),
        (50, 35, (170, 0, -110)),
    ]

    mountain_color = (0.6, 0.4, 0.2)  # Earthy brown color

    # Draw the pyramids
    for base_size, height, position in pyramids:
        draw_pyramid(base_size, height, position, mountain_color)

# Initial camera position and rotation
camera_pos = [0, 10, -30]
camera_rotation = [20, 0]

def camera_controls():
    """Handles keyboard input for camera controls."""
    global camera_pos, camera_rotation
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: camera_pos[2] += 1  # Move forward along Z-axis
    if keys[pygame.K_s]: camera_pos[2] -= 1  # Move backward along Z-axis
    if keys[pygame.K_a]: camera_pos[0] -= 1  # Move left along X-axis
    if keys[pygame.K_d]: camera_pos[0] += 1  # Move right along X-axis
    if keys[pygame.K_UP]: camera_rotation[0] += 1  # Pitch up
    if keys[pygame.K_DOWN]: camera_rotation[0] -= 1  # Pitch down
    if keys[pygame.K_LEFT]: camera_rotation[1] -= 1  # Yaw left
    if keys[pygame.K_RIGHT]: camera_rotation[1] += 1  # Yaw right

def apply_camera():
    """Applies camera's position and rotation."""
    glLoadIdentity()
    glTranslatef(*camera_pos)
    glRotatef(camera_rotation[0], 1, 0, 0)
    glRotatef(camera_rotation[1], 0, 1, 0)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    init_opengl()

    global ground_texture_id
    ground_texture_id = load_texture('grass.jpg')  # Load the ground texture

    coliseum_position = [-55, 0, -15]  # [x, y, z] coordinates for the coliseum

    # PRT position variables
    previousTime = time.time()
    delta = 0
    global position
    position = 0
    speed = 0
    maxSpeed = 4.5
    minSpeed = 0
    acceleration = 1.5
    global position2
    position2 = 3
    speed2 = 0

    global is_day, transition_in_progress, transition_start_time, current_light_position
    global background_color

    while True:
        # PRT position updates
        delta = time.time() - previousTime
        previousTime = time.time()
        speed += acceleration * delta
        speed = max(min(speed, maxSpeed), minSpeed)  # Clamp speed between minSpeed and maxSpeed
        position += speed * delta

        speed2 += acceleration * delta
        speed2 = max(min(speed2, maxSpeed), minSpeed)
        position2 += speed2 * delta

        if position > 112:
            position = 0
            speed = 0
        if position2 > 112:
            position2 = 0
            speed2 = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_p:
                    acceleration = -acceleration  # Stop PRT cars
                elif event.key == K_n:
                    if not transition_in_progress:
                        transition_in_progress = True
                        transition_start_time = pygame.time.get_ticks()
                        is_day = not is_day  # Toggle between day and night

        camera_controls()  # Update camera based on user input
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear screen and depth buffer

        # Set the light position
        glLightfv(GL_LIGHT0, GL_POSITION, current_light_position)

        apply_camera()  # Apply camera transformations

        # Update the day/night transition
        update_day_night_cycle()

        # Draw scene
        draw_tunnel()
        draw_ground()
        draw_road()
        draw_water()
        draw_background()
        draw_prt()

        glPushMatrix()
        glTranslatef(*coliseum_position)  # Move the coliseum to its specified position
        # Draw the coliseum components
        draw_cylinder(30, 50, 25, offset=0)
        draw_coliseum_walls(30, 50, 25)
        draw_dome(30, 50, 20, offset=25)
        glPopMatrix()

        pygame.display.flip()  # Swap buffers
        pygame.time.wait(10)  # Small delay to control camera speed

main()