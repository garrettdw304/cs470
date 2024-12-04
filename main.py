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
import numpy as np

global timeVar; timeVar = 0  # Time since the beginning of the program

def draw_house_at(position, rotate, scale):
    for object in houseObjects:
        glPushMatrix()
        glTranslate(*position)
        glScale(*scale)
        if rotate:
            glRotate(180, 0, 0)
        draw_model(object)
        glPopMatrix()

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

    def unbind(self):
        glMaterial(GL_FRONT, GL_SPECULAR, Model.default_material.specular_reflection)
        glMaterial(GL_FRONT, GL_AMBIENT, Model.default_material.ambient_reflection)
        glMaterial(GL_FRONT, GL_DIFFUSE, Model.default_material.diffused_reflection)
        glMaterial(GL_FRONT, GL_SHININESS, [Model.default_material.specular_exponent])
        glMaterial(GL_FRONT, GL_EMISSION, Model.default_material.emissive_material)

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
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

    def unbind_texture(self):
        if self.texture_id == -1: raise Exception("Texture cannot be bound if it is not loaded into GPU...")
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)


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

def draw_model(model: Model):
    if model.texture is not None:
        model.bind_texture()
    model.material.bind()

    # Prepare arrays for vertex positions, normals, and texture coordinates
    vertices = []
    normals = []
    tex_coords = []

    for face in model.faces:
        for indices in face:
            vertices.extend(model.vertices[indices[0]])
            normals.extend(model.normals[indices[2]])
            if model.texture is not None:
                tex_coords.extend(model.uvs[indices[1]])

    # Convert lists to NumPy arrays
    vertices_array = np.array(vertices, dtype=np.float32)
    normals_array = np.array(normals, dtype=np.float32)
    if model.texture is not None:
        tex_coords_array = np.array(tex_coords, dtype=np.float32)

    # Enable client states
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    if model.texture is not None:
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    # Set pointers
    glVertexPointer(3, GL_FLOAT, 0, vertices_array)
    glNormalPointer(GL_FLOAT, 0, normals_array)
    if model.texture is not None:
        glTexCoordPointer(2, GL_FLOAT, 0, tex_coords_array)

    # Draw arrays
    glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 3)

    # Disable client states
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)
    if model.texture is not None:
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    if model.texture is not None:
        model.unbind_texture()
    model.material.unbind()

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

    glBegin(GL_POLYGON)
    glVertex3f(-0.5, 0, 0)
    glVertex3f(-0.7, 0.2, 0)
    glVertex3f(0.7, 0.2, 0)
    glVertex3f(0.5, 0, 0)
    glEnd()

    glColor3f(0, 0, 1.0)

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
    
    glBegin(GL_POLYGON)
    glVertex3f(-0.5, 0, 0)
    glVertex3f(-0.7, 0.2, 0)
    glVertex3f(0.7, 0.2, 0)
    glVertex3f(0.5, 0, 0)
    glEnd()

    glColor3f(0, 0, 1.0)

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

    glBegin(GL_POLYGON)
    glVertex3f(1, 0.21, 0)
    glVertex3f(-1, 0.21, 0)
    glVertex3f(-1, 0.21, 1)
    glVertex3f(1, 0.21, 1)
    glEnd()

    glColor3f(1, 1, 0)

    glBegin(GL_POLYGON)
    glVertex3f(0.9, 1.4, 0)
    glVertex3f(-0.9, 1.4, 0)
    glVertex3f(-0.9, 1.4, 1)
    glVertex3f(0.9, 1.4, 1)
    glEnd()

    glColor3f(0.6, 0.6, 0.6)

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

    glTranslatef(-1.05, 0.1, 0.5)
    cube(0.1, 0.2, 1)

    glTranslatef(2.1, 0, 0)
    cube(0.1, 0.2, 1)

    glPopMatrix()

def prtStraightTrack(pillar):
    glPushMatrix()

    glColor3f(0.6, 0.3, 0)

    cube(10, 1, 10)

    glColor3f(0.6, 0.4, 0)

    glTranslatef(0, 0.6, 0)
    cube(1, 0.2, 10)

    glColor3f(0.5, 0.4, 0)

    glTranslatef(0, 0.6, 0)
    cube(0.4, 1, 10)

    glColor3f(0.5, 0.5, 0)

    glTranslatef(0, 0.6, 0)
    cube(1, 0.2, 10)

    glColor3f(0.7, 0.7, 0.7)

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

    glTranslatef(5.25, -0.4, 5)
    cube(0.2, 1.2, 10)

    glColor3f(0.45, 0.4, 0)

    glTranslatef(-0.25, 0, 0)
    cube(0.3, 0.1, 10)

    glColor3f(0.4, 0.35, 0.05)

    glTranslatef(-0.2, 0, 0)
    cube(0.1, 0.6, 10)

    glColor3f(0.4, 0.2, 0)

    glTranslatef(-9.35, 0, 0)
    cube(0.2, 1.2, 10)

    glColor3f(0.45, 0.4, 0)

    glTranslatef(0.25, 0, 0)
    cube(0.3, 0.1, 10)

    glColor3f(0.4, 0.35, 0.05)

    glTranslatef(0.2, 0, 0)
    cube(0.1, 0.6, 10)

    glColor3f(0.6, 0.4, 0)

    glTranslatef(2, -0.6, 0)
    cube(3, 0.01, 10)

    glTranslatef(5, 0, 0)
    cube(3, 0.01, 10)

    glTranslatef(2.5, 0, 0)

    glColor3f(0.5, 0.5, 0.5)
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

    glRotatef(90, 1, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.2, 0.2, 5, 20, 1)

    glColor3f(0.6, 0.6, 0.6)

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

def draw_trees():
    positionsX = [
-53,
-27,
-50,
-51,
-35,
-75,
-61,
-86,
-73,
-63,
-55,
-48,
-43,
-45,
-37,
-20,
-68,
-49,
-80,
-77,
-64,
-25,
-76,
-56,
-21,
-57,
-72,
-88,
-58,
-81,
-94,
-92,
-30,
-44,
-60,
-84,
-87,
-78,
-67,
-85,
-32,
-38,
-98,
-99,
-23,
-79,
-91,
-97,
-47,
-22,
71,
34,
68,
31,
94,
61,
97,
87,
65,
43,
21,
79,
96,
27,
48,
64,
54,
75,
47,
36,
66,
82,
22,
55,
33,
57,
72,
44,
83,
78,
91,
42,
20,
40,
37,
69,
74,
52,
88,
56,
81,
32,
53,
93,
23,
35,
50,
45,
70,
49
    ]
    positionsY = [
-26,
-105,
-53,
-122,
-112,
-128,
-107,
-129,
-64,
-124,
-101,
-62,
-46,
-125,
-60,
-109,
-20,
-88,
-77,
-65,
-31,
-83,
-32,
-120,
-51,
-76,
-114,
-63,
-81,
-70,
-127,
-44,
-102,
-85,
-68,
-33,
-91,
-106,
-38,
-58,
-45,
-61,
-54,
-49,
-22,
-94,
-40,
-72,
-75,
-71,
-55,
-74,
-30,
-79,
-118,
-97,
-100,
-66,
-93,
-126,
-108,
-98,
-43,
-28,
-110,
-89,
-67,
-113,
-82,
-48,
-130,
-84,
-87,
-59,
-103,
-104,
-39,
-24,
-50,
-25,
-92,
-99,
-111,
-115,
-41,
-52,
-21,
-36,
-29,
-47,
-119,
-35,
-27,
-86,
-90,
-23,
-69,
-78,
-95,
-73]
    greens = [
        0.6288, 0.6232, 0.7784, 0.7038, 0.7922, 0.7818, 0.7809, 0.7402, 0.7935, 0.6935, 0.7118, 0.6322, 0.6171, 0.6641, 0.6065, 0.6665, 0.707, 0.6596, 0.6631, 0.7858, 0.666, 0.7807, 0.6109, 0.7763, 0.6847, 0.7916, 0.7235, 0.6516, 0.6955, 0.6014, 0.6, 0.7085, 0.787, 0.748, 0.7103, 0.6664, 0.7721, 0.7233, 0.7858, 0.7343, 0.746, 0.6137, 0.7417, 0.6776, 0.6675, 0.631, 0.7975, 0.6932, 0.7772, 0.6468, 0.6758, 0.6657, 0.6913, 0.7668, 0.7346, 0.6441, 0.715, 0.7385, 0.6775, 0.6037, 0.7618, 0.6587, 0.6385, 0.6607, 0.6182, 0.6584, 0.6169, 0.7854, 0.7797, 0.6013, 0.7296, 0.6396, 0.6499, 0.6793, 0.7937, 0.703, 0.6793, 0.7361, 0.7066, 0.7633, 0.7552, 0.7879, 0.7848, 0.6808, 0.672, 0.6053, 0.6068, 0.6386, 0.727, 0.7323, 0.6367, 0.745, 0.7304, 0.6732, 0.7706, 0.7459, 0.7548, 0.7097, 0.6402, 0.7634
    ]
    trunks = [
        0.2547, 0.3544, 0.276, 0.502, 0.2385, 0.3021, 0.2868, 0.4916, 0.4319, 0.3809, 0.5721, 0.5966, 0.5011, 0.3927, 0.4665, 0.2886, 0.3685, 0.5782, 0.3238, 0.5478, 0.5269, 0.586, 0.5733, 0.2728, 0.3786, 0.4769, 0.3222, 0.4413, 0.5303, 0.3714, 0.2271, 0.2497, 0.3017, 0.2931, 0.5135, 0.5524, 0.4881, 0.421, 0.2458, 0.578, 0.4666, 0.4202, 0.3953, 0.503, 0.5267, 0.2678, 0.4927, 0.4254, 0.43, 0.464, 0.3155, 0.5407, 0.2831, 0.5788, 0.4408, 0.2651, 0.207, 0.3673, 0.4399, 0.3363, 0.4413, 0.2328, 0.5657, 0.5174, 0.5742, 0.303, 0.2214, 0.3322, 0.4915, 0.5872, 0.3729, 0.534, 0.302, 0.4608, 0.3782, 0.5692, 0.3543, 0.5745, 0.2288, 0.4576, 0.3112, 0.2624, 0.4845, 0.4004, 0.2037, 0.3675, 0.5938, 0.5303, 0.2844, 0.5689, 0.3644, 0.2933, 0.4392, 0.4891, 0.3409, 0.512, 0.4941, 0.3943, 0.2368, 0.2758
    ]
    widths = [
        1.9891, 1.3488, 2.1147, 1.3697, 1.2419, 1.6457, 2.3897, 2.0031, 1.4682, 2.8847, 1.2741, 2.6916, 1.3642, 2.1348, 2.261, 1.0361, 2.2734, 1.8312, 1.5199, 1.2973, 2.4516, 1.2584, 2.4907, 2.0425, 2.9217, 2.1392, 2.2842, 2.8505, 2.8994, 2.4906, 2.7219, 2.5333, 2.8981, 2.2621, 1.6825, 1.03, 2.6026, 2.0429, 2.1425, 1.3364, 2.1748, 2.273, 2.2498, 2.7394, 1.4921, 2.7213, 1.9248, 2.4806, 2.4288, 1.1902, 2.0032, 2.0762, 2.3173, 2.8992, 1.3325, 1.617, 1.8698, 1.9849, 2.7794, 2.3283, 1.5949, 1.0415, 2.7668, 2.5422, 2.8227, 2.9594, 1.2154, 2.2046, 2.3792, 1.059, 2.7216, 1.9585, 2.9857, 1.6533, 1.6539, 1.8015, 2.5788, 2.1265, 2.9703, 2.1948, 1.0069, 2.1693, 2.268, 2.834, 2.6399, 1.703, 1.4684, 1.2666, 2.7072, 2.3955, 2.0649, 1.6169, 1.7616, 2.4623, 1.1419, 1.886, 1.0806, 2.1522, 1.9039, 2.6044
    ]
    heights = [
        6.2659, 6.3036, 6.3481, 4.3313, 4.1753, 3.0561, 6.6123, 4.0224, 4.5811, 4.5975, 3.1208, 4.4046, 3.5354, 4.0431, 4.7386, 5.0944, 6.163, 3.463, 3.2967, 4.8988, 5.0663, 4.708, 4.639, 6.8063, 5.9601, 5.143, 3.7997, 5.7029, 3.413, 6.0307, 3.496, 3.8878, 3.7186, 3.9521, 4.5175, 6.2592, 6.7384, 3.6114, 3.839, 4.5583, 6.8676, 6.3397, 4.6526, 4.8305, 5.1816, 3.1288, 6.0267, 3.6738, 4.3365, 6.044, 6.8462, 3.5802, 6.1543, 4.2312, 5.8795, 6.0729, 5.8318, 3.1886, 6.1382, 6.4638, 5.4616, 5.6234, 4.0931, 6.8213, 6.6032, 5.3229, 4.8614, 5.0598, 6.4951, 3.1684, 3.6898, 6.6193, 3.6253, 3.957, 5.922, 4.6214, 3.8991, 5.6486, 4.226, 3.7339, 3.0256, 5.4456, 6.5385, 5.5673, 6.8313, 5.7355, 6.4646, 5.5248, 3.4053, 3.1692, 6.7875, 3.0783, 6.6489, 3.7603, 3.4659, 3.1114, 5.0647, 6.5091, 4.9005, 5.92]
    heightOffs = [
        2.6227, 2.2296, 3.1824, 3.854, 3.473, 2.1252, 3.825, 3.8578, 2.9844, 3.3008, 2.8587, 3.0345, 2.862, 2.8008, 2.9165, 2.8226, 3.9926, 2.3404, 2.8017, 2.5277, 3.6926, 2.9002, 3.6295, 3.7614, 3.8201, 2.7946, 3.5615, 3.1171, 2.1724, 3.578, 3.0054, 3.9159, 2.4113, 3.0343, 2.8536, 3.6162, 2.3425, 2.8684, 3.6846, 3.5548, 3.1618, 2.7397, 2.2654, 3.1135, 2.5208, 3.1068, 2.2282, 3.8556, 3.8085, 2.8059, 3.2935, 2.9386, 3.9659, 3.2135, 2.9232, 3.6583, 2.1916, 2.6217, 3.6022, 2.9316, 2.7195, 3.9453, 3.7837, 2.2206, 3.3416, 3.6073, 2.572, 2.8307, 2.9367, 3.6212, 3.1896, 2.3914, 2.9865, 3.6828, 2.3181, 3.3232, 2.97, 2.6381, 2.317, 2.0614, 3.0902, 2.3088, 3.7334, 2.1661, 3.6971, 3.669, 3.402, 3.49, 2.8597, 2.3312, 2.0631, 2.0245, 2.4132, 2.8019, 2.5189, 2.355, 2.854, 2.1607, 2.9309, 3.4644
    ]
    def draw_tree(heightOffGround, height, trunkWidth, width, positionX, positionY, green):
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glTranslatef(positionX, positionY, heightOffGround-2)
        glColor3f(0, green, 0)
        quadric = gluNewQuadric()
        gluCylinder(quadric, width, 0.1, height, 15, 1)

        glTranslatef(0, 0, -heightOffGround)
        glColor3f(0.6, 0.3, 0)
        quadric = gluNewQuadric()
        gluCylinder(quadric, trunkWidth, trunkWidth, heightOffGround, 5, 1)
        glPopMatrix()
    for i in range(100):
        draw_tree(heightOffs[i], heights[i], trunks[i], widths[i], positionsX[i], positionsY[i], greens[i])

def draw_cylinder(radius, segments, height, offset=0):
    
    glDisable(GL_LIGHTING)  # Disable lighting for the coliseum

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

    glEnable(GL_LIGHTING)  
    
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
        glNormal3f(0, 1, 0)  # Normal pointing up
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
        glNormal3f(0, 1, 0)  # Normal pointing up
    
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
    glEnable(GL_TEXTURE_2D)  # Enable texture mapping
    glBindTexture(GL_TEXTURE_2D, ground_texture_id)
    glColor3f(1.0, 1.0, 1.0)  # Set color to white to display texture colors accurately

    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)  # Normal pointing up
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
    glNormal3f(0, 1, 0)  # Normal pointing up
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
    glNormal3f(0, 1, 0)  # Normal pointing up
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
    glNormal3f(0, 0, 1)  # Normal facing forward
    glVertex3f(*blf)
    glVertex3f(*brf)
    glVertex3f(*trf)
    glVertex3f(*tlf)

    # Back face
    glNormal3f(0, 0, -1)  # Normal facing backward
    glVertex3f(*blb)
    glVertex3f(*brb)
    glVertex3f(*trb)
    glVertex3f(*tlb)

    # Left face
    glNormal3f(-1, 0, 0)  # Normal facing left
    glVertex3f(*blf)
    glVertex3f(*blb)
    glVertex3f(*tlb)
    glVertex3f(*tlf)

    # Right face
    glNormal3f(1, 0, 0)  # Normal facing right
    glVertex3f(*brf)
    glVertex3f(*brb)
    glVertex3f(*trb)
    glVertex3f(*trf)

    # Top face
    glNormal3f(0, 1, 0)  # Normal facing up
    glVertex3f(*tlf)
    glVertex3f(*tlb)
    glVertex3f(*trb)
    glVertex3f(*trf)

    # Bottom face
    glNormal3f(0, -1, 0)  # Normal facing down
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

def draw_human(human, human_body_model, human_arm_model):
    global timeVar
    if human.is_waving:
        glPushMatrix()
        glTranslate(-0.24308, 1.3941, 0)
        wave_speed = 2
        glRotate(math.fabs(math.sin((timeVar - human.started_waving) / 1000 * wave_speed)) * -180, 0, 0, 1)
        draw_model(human_arm_model)
        glPopMatrix()
    else:
        draw_at(lambda: draw_model(human_arm_model), -0.24308, 1.3941, 0)
    draw_model(human_body_model)

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

# Initialize global variables for the day/night cycle
is_day = True           # Indicates whether it's currently day
transition_in_progress = False  # Indicates if a transition is happening
transition_start_time = 0       # Time when the transition started
transition_duration = 5000      # Duration of the transition in milliseconds (5 seconds)

# Light position variables
day_light_position = [0.0, 100.0, 0.0, 1.0]   # High in the sky
night_light_position = [0.0, -100.0, 0.0, 1.0]  # Below the scene
current_light_position = day_light_position.copy()

# Background color
background_color = [0.53, 0.81, 0.92, 1.0]  # Initial sky color (day)

# Initialize time variable for human animation
timeVar = 0

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


def main():
    global timeVar
    global is_day, transition_in_progress, transition_start_time, current_light_position, background_color
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    init_opengl()
    glEnable(GL_LIGHT0)
    # We will set the light position in the main loop after applying camera transformations

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

    # Initialize default material properties
    Model.default_material.specular_reflection = glGetMaterialfv(GL_FRONT, GL_SPECULAR)
    Model.default_material.ambient_reflection = glGetMaterialfv(GL_FRONT, GL_AMBIENT)
    Model.default_material.diffused_reflection = glGetMaterialfv(GL_FRONT, GL_DIFFUSE)
    Model.default_material.specular_exponent = glGetMaterialfv(GL_FRONT, GL_SHININESS)
    Model.default_material.emissive_material = glGetMaterialfv(GL_FRONT, GL_EMISSION)

    # Human and car state
    human = Human()
    cars = []

    # Load Models
    car_model = Model.load("Resources/car.obj", "Resources/Car.png")
    car_model.send_texture()
    car_model.unbind_texture()
    human_body_model = Model.load("Resources/humanbody.obj", "Resources/Human.png")
    human_body_model.send_texture()
    human_body_model.unbind_texture()
    human_arm_model = Model.load("Resources/humanarm.obj", "Resources/Human.png")
    human_arm_model.send_texture()
    human_arm_model.unbind_texture()

    global houseObjects
    houseObjects = [Model.load("Resources/furniture.obj"), Model.load("Resources/doors.obj"), Model.load("Resources/walls.obj"), Model.load("Resources/roof.obj")]

    while True:
        # PRT position updates
        delta = time.time() - previousTime
        previousTime = time.time()
        speed += acceleration * delta
        if speed > maxSpeed:
            speed = maxSpeed
        if speed < minSpeed:
            speed = minSpeed
        position += speed * delta
        speed2 += acceleration * delta
        if speed2 > maxSpeed:
            speed2 = maxSpeed
        if speed2 < minSpeed:
            speed2 = minSpeed
        position2 += speed2 * delta
        if position > 112:
            position = 0
            speed = 0
        if position2 > 110:
            position2 = 0
            speed2 = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_p:
                    acceleration = -acceleration  # Stop PRT cars
                elif event.key == K_h:
                    if human.is_waving:
                        human.stop_waving()
                    else:
                        human.start_waving(timeVar)
                elif event.key == K_n:
                    if not transition_in_progress:
                        transition_in_progress = True
                        transition_start_time = pygame.time.get_ticks()
                        is_day = not is_day  # Toggle between day and night

        camera_controls()  # Update camera based on user input

        # Update the day/night transition before clearing the screen
        update_day_night_cycle()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear screen and depth buffer

        apply_camera()  # Apply camera transformations

        # Set the light position after applying camera transformations
        glLightfv(GL_LIGHT0, GL_POSITION, current_light_position)

        # Draw scene
        draw_tunnel()
        draw_ground()
        draw_road()
        draw_water()
        draw_background()
        draw_prt()
        draw_trees()
        draw_human(human, human_body_model, human_arm_model)

        glPushMatrix()
        glTranslatef(*coliseum_position)  # Move the coliseum to its specified position
        # Draw the coliseum components
        draw_cylinder(30, 50, 25, offset=0)
        draw_coliseum_walls(30, 50, 25)
        draw_dome(30, 50, 20, offset=25)
        glPopMatrix()

        draw_house_at((30,0,0), False, (.5,.5,.5))

        pygame.display.flip()  # Swap buffers
        pygame.time.wait(10)  # Small delay to control camera speed
        timeVar += 10

main()