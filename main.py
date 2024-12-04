import pygame
import math
import OpenGL
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image
import pywavefront

global time  # time since beginning of program in ms
"""
def draw_at(draw_func, posx, posy, posz):
    glPushMatrix()
    glTranslate(posx, posy, posz)
    draw_func()
    glPopMatrix()


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
        texture = Image.open(texture_file).transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert("RGB").tobytes()
        return Model(vertices, normals, uvs, faces, material, texture, -1)


def draw_model(model : Model):
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
            glTexCoord2fv(model.uvs[indices[1]])
            glVertex3fv(model.vertices[indices[0]])
    if length != -1:
        glEnd()
    model.unbind_texture()
"""
def draw_garage_house(size, position):
    x, y, z = position

def draw_house(sizeMod, position, rotate):
    scene = pywavefront.Wavefront("allTest.obj", collect_faces=True)
    glPushMatrix()
    glScalef(*sizeMod)
    if rotate:
        glRotatef(180, 0, 1, 0)
    glTranslatef(*position)
    for mesh in scene.mesh_list:
        glBegin(GL_TRIANGLES)
        for face in mesh.faces:
            for vertex_i in face:
                glVertex3f(*scene.vertices[vertex_i])
        glEnd()
    
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
    """Initializes OpenGL settings and projection matrix"""
    glEnable(GL_DEPTH_TEST)  # enable depth testing for 3D rendering
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 800 / 600, 0.1, 1000)  # set up perspective projection
    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0, -1, -20)  # move scene slightly for better initial view
    glClearColor(0.53, 0.81, 0.92, 1.0) # void color to light blue

# currently not working, save for Wednesday
def load_texture(image_path):
    """Loads texture from an image file"""
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    image = Image.open(image_path)
    img_data = image.tobytes("raw", "RGB", 0, -1)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)  # repeat texture horizontally
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)  # repeat texture vertically
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture

def draw_ground():
    """Draws grassy ground plane"""
    glColor3f(0.13, 0.55, 0.13)  # Grass green color
    glBindTexture(GL_TEXTURE_2D, ground_texture)
    glBegin(GL_QUADS)
    # define vertices with texture coordinates for the ground quad
    glTexCoord2f(0, 0); glVertex3f(-150, -2, 150)
    glTexCoord2f(1, 0); glVertex3f(150, -2, 150)
    glTexCoord2f(1, 1); glVertex3f(150, -2, -150)
    glTexCoord2f(0, 1); glVertex3f(-150, -2, -150)
    glEnd()

def draw_dotted_line_straight():
    """Draws a dotted yellow line down the straight road"""
    glEnable(GL_POLYGON_OFFSET_FILL) # prevents z-fighting
    glColor3f(1.0, 1.0, 0.0)

    # line parameters
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
        z1 = min(z + dash_length, z_end)  # ensure the dash doesn't exceed road length

        # draw one dash as a quad
        glVertex3f(x_left, 0.02, z0)
        glVertex3f(x_right, 0.02, z0)
        glVertex3f(x_right, 0.02, z1)
        glVertex3f(x_left, 0.02, z1)

        z += dash_length + gap_length  # move to the position of the next dash
    glEnd()
    glDisable(GL_POLYGON_OFFSET_FILL)

def draw_dotted_line_diagonal():
    """Draws a dotted yellow line down the diagonal road"""
    glEnable(GL_POLYGON_OFFSET_FILL) # prevents z-fighting

    glColor3f(1.0, 1.0, 0.0)
    # line parameters
    dash_length = 10
    gap_length = 5
    line_width = 1
    diagonal_length = 150
    start_distance = 10  # distance from intersection to start drawing dashes
    angle = math.radians(30)  # angle of diagonal road

    # calculate number of dashes
    t_initial = start_distance
    num_dashes = int((diagonal_length - start_distance) / (dash_length + gap_length)) + 1

    dx = math.cos(angle)
    dz = -math.sin(angle)

    dx_perp = math.sin(angle)
    dz_perp = math.cos(angle)

    x_start = 0  # starting point at intersection
    z_start = 0

    glBegin(GL_QUADS)
    for i in range(num_dashes):
        t0 = t_initial + i * (dash_length + gap_length)
        t1 = t0 + dash_length

        # adjust end of the last dash
        if t1 > diagonal_length:
            t1 = diagonal_length

        # center positions of start and end of the dash
        x0_center = x_start + t0 * dx
        z0_center = z_start + t0 * dz
        x1_center = x_start + t1 * dx
        z1_center = z_start + t1 * dz

        # offset for line width
        x_offset = line_width * dx_perp
        z_offset = line_width * dz_perp
        y_offset = 0.05  # Slightly above the road to avoid Z-fighting

        # draw dash as a quad
        glVertex3f(x0_center - x_offset, y_offset, z0_center - z_offset)
        glVertex3f(x0_center + x_offset, y_offset, z0_center + z_offset)
        glVertex3f(x1_center + x_offset, y_offset, z1_center + z_offset)
        glVertex3f(x1_center - x_offset, y_offset, z1_center - z_offset)
    glEnd()

    glDisable(GL_POLYGON_OFFSET_FILL)

def draw_road():
    """Draws the straight and diagonal roads."""
    # draw the straight road
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-6, 0.01, -150)
    glVertex3f(6, 0.01, -150)
    glVertex3f(6, 0.01, 150)
    glVertex3f(-6, 0.01, 150)
    glEnd()
    draw_dotted_line_straight()

    # draw the diagonal road
    diagonal_length = 150
    angle = math.radians(30)
    road_width = 12

    # direction vector along diag road
    dx = math.cos(angle)
    dz = -math.sin(angle)

    # perpendicular vector for diag road width
    dx_perp = math.sin(angle)
    dz_perp = math.cos(angle)

    # width offsets
    x_offset_width = (road_width / 2) * dx_perp
    z_offset_width = (road_width / 2) * dz_perp

    # start and end points of diag road
    x_start = 0
    z_start = 0
    x_end = x_start + diagonal_length * dx
    z_end = z_start + diagonal_length * dz

    # define the edges of diag road
    x_start_left = x_start + x_offset_width
    z_start_left = z_start + z_offset_width
    x_start_right = x_start - x_offset_width
    z_start_right = z_start - z_offset_width
    x_end_left = x_end + x_offset_width
    z_end_left = z_end + z_offset_width
    x_end_right = x_end - x_offset_width
    z_end_right = z_end - z_offset_width

    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(x_start_left, 0.01, z_start_left)
    glVertex3f(x_start_right, 0.01, z_start_right)
    glVertex3f(x_end_right, 0.01, z_end_right)
    glVertex3f(x_end_left, 0.01, z_end_left)
    glEnd()
    draw_dotted_line_diagonal()

def draw_tunnel():
    """Draws a tunnel into the mountain"""
    tunnel_width = 12  # match straight road width
    tunnel_height = 15
    tunnel_depth = 40  # length of tunnel into the mountain

    # position of the tunnel entrance
    x_center = 0
    y_base = 0
    z_entrance = -50

    # define vertices of the tunnel (just a simple rectangular prism)

    # front face (entrance)
    blf = (x_center - tunnel_width/2, y_base, z_entrance)
    brf = (x_center + tunnel_width/2, y_base, z_entrance)
    tlf = (x_center - tunnel_width/2, y_base + tunnel_height, z_entrance)
    trf = (x_center + tunnel_width/2, y_base + tunnel_height, z_entrance)

    # back face
    blb = (x_center - tunnel_width/2, y_base, z_entrance - tunnel_depth)
    brb = (x_center + tunnel_width/2, y_base, z_entrance - tunnel_depth)
    tlb = (x_center - tunnel_width/2, y_base + tunnel_height, z_entrance - tunnel_depth)
    trb = (x_center + tunnel_width/2, y_base + tunnel_height, z_entrance - tunnel_depth)

    glColor3f(0.6, 0.2, 0.2)
    glBegin(GL_QUADS)

    # front face
    glVertex3f(*blf)
    glVertex3f(*brf)
    glVertex3f(*trf)
    glVertex3f(*tlf)

    # back face
    glVertex3f(*blb)
    glVertex3f(*brb)
    glVertex3f(*trb)
    glVertex3f(*tlb)
    
    # left face
    glVertex3f(*blf)
    glVertex3f(*blb)
    glVertex3f(*tlb)
    glVertex3f(*tlf)
    
    # right face
    glVertex3f(*brf)
    glVertex3f(*brb)
    glVertex3f(*trb)
    glVertex3f(*trf)
    
    # top face
    glVertex3f(*tlf)
    glVertex3f(*tlb)
    glVertex3f(*trb)
    glVertex3f(*trf)
    
    # bottom face
    glVertex3f(*blf)
    glVertex3f(*blb)
    glVertex3f(*brb)
    glVertex3f(*brf)
    glEnd()

    # black front face to give the illusion of a tunnel entrance
    glEnable(GL_POLYGON_OFFSET_FILL) # prevents z-fighting
    glPolygonOffset(-1.0, -1.0)  # bring the entrance forward so its visible
    glColor3f(0.0, 0.0, 0.0)

    # define vertices for entrance rectangle
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
    """Draws a river"""
    glColor3f(0, 0.5, 1)  # keep darker than skybox color
    glBegin(GL_QUADS)

    # long skinny quad for river
    glVertex3f(-120, 0.01, -150)
    glVertex3f(-100, 0.01, -150)
    glVertex3f(-100, 0.01, 150)
    glVertex3f(-120, 0.01, 150)
    glEnd()

def draw_pyramid(base_size, height, position, color):
    """Helper function to draw a mountain/pyramid with snowy peak"""
    x, y, z = position
    half_base = base_size / 2
    peak_color = (1.0, 1.0, 1.0)  # white color for snowy peak

    glBegin(GL_TRIANGLES)

    # front face
    glColor3f(*color)  # base color
    glVertex3f(x - half_base, y, z - half_base)  # base bottom-left
    glVertex3f(x + half_base, y, z - half_base)  # base bottom-right
    glColor3f(*peak_color)  # gradient from base color to peak color
    glVertex3f(x, y + height, z)

    # right face
    glColor3f(*color)
    glVertex3f(x + half_base, y, z - half_base)
    glVertex3f(x + half_base, y, z + half_base)
    glColor3f(*peak_color)
    glVertex3f(x, y + height, z)

    # back face
    glColor3f(*color)
    glVertex3f(x + half_base, y, z + half_base)
    glVertex3f(x - half_base, y, z + half_base)
    glColor3f(*peak_color)
    glVertex3f(x, y + height, z)

    # left face
    glColor3f(*color)
    glVertex3f(x - half_base, y, z + half_base)
    glVertex3f(x - half_base, y, z - half_base)
    glColor3f(*peak_color)
    glVertex3f(x, y + height, z)
    glEnd()

    # base of pyramid
    glColor3f(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)  # slightly darker color
    glBegin(GL_QUADS)
    glVertex3f(x - half_base, y, z - half_base)
    glVertex3f(x + half_base, y, z - half_base)
    glVertex3f(x + half_base, y, z + half_base)
    glVertex3f(x - half_base, y, z + half_base)
    glEnd()

def draw_background():
    """Draws many pyramids to create a mountain range"""
    pyramids = [
        
        # main cluster
        (50, 30, (-20, 0, -100)),
        (60, 40, (0, 0, -120)),
        (70, 50, (20, 0, -110)),
        (40, 25, (-50, 0, -90)),
        (55, 35, (-10, 0, -130)),
        (65, 45, (30, 0, -140)),
        (45, 28, (10, 0, -80)),
        (50, 30, (50, 0, -100)),
        (35, 22, (-35, 0, -120)),

        # left cluster
        (40, 26, (-70, 0, -100)),
        (50, 35, (-90, 0, -120)),
        (60, 40, (-110, 0, -110)),
        (45, 30, (-130, 0, -100)),
        (55, 38, (-150, 0, -130)),
        (50, 35, (-170, 0, -110)),

        # right cluster
        (40, 26, (70, 0, -100)),
        (50, 35, (90, 0, -120)),
        (60, 40, (110, 0, -110)),
        (45, 30, (130, 0, -100)),
        (55, 38, (150, 0, -130)),
        (50, 35, (170, 0, -110)),
    ]

    mountain_color = (0.6, 0.4, 0.2)

    # draw the pyramids
    for base_size, height, position in pyramids:
        draw_pyramid(base_size, height, position, mountain_color)

# initial camera position and rotation
camera_pos = [0, 10, -30]
camera_rotation = [20, 0]

def camera_controls():
    """Handles keyboard input for camera controls"""
    global camera_pos, camera_rotation
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: camera_pos[2] += 1  # moves forward along Z-axis
    if keys[pygame.K_s]: camera_pos[2] -= 1  # moves backward along Z-axis
    if keys[pygame.K_a]: camera_pos[0] -= 1  # moves left along X-axis
    if keys[pygame.K_d]: camera_pos[0] += 1  # moves right along X-axis
    if keys[pygame.K_UP]: camera_rotation[0] += 1  # pitch up
    if keys[pygame.K_DOWN]: camera_rotation[0] -= 1  # pitch down
    if keys[pygame.K_LEFT]: camera_rotation[1] -= 1  # yaw left
    if keys[pygame.K_RIGHT]: camera_rotation[1] += 1  # yaw right

def apply_camera():
    """Applies camera's position and rotation"""
    glLoadIdentity()
    glTranslatef(*camera_pos)
    glRotatef(camera_rotation[0], 1, 0, 0)
    glRotatef(camera_rotation[1], 0, 1, 0)

def setMaterial(r, g, b):
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [r*0.25, g*0.25, b*0.25, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [r, g, b, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [r*0.5, g*0.5, b*0.5, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 30)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    init_opengl()
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glLight(GL_LIGHT0, GL_POSITION, [1.0, 100.0, 1.0, 1.0])
    coliseum_position = [75, 0, 75]  # [x, y, z] coordinates for the coliseum

    # not working currently
    global ground_texture
    ground_texture = load_texture('ground.jpg')  # load ground texture image

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        camera_controls()  # update camera based on user input
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear screen and depth buffer
        apply_camera()  # apply camera transformations
        
        # draw scene
        draw_tunnel()
        draw_ground()
        draw_road()
        draw_water()
        draw_background()
        
        
        glPushMatrix()  # Save the current transformation matrix
        glTranslatef(*coliseum_position)  # Move the coliseum to its specified position

        # Draw the coliseum components
        draw_cylinder(30, 50, 25, offset=0)
        draw_coliseum_walls(30, 50, 25)
        draw_dome(30, 50, 20, offset=25)
        
        glPopMatrix()  # Restore the previous transformation matrix
        
        # Draw houses
        draw_house((.5, .5, .5), (-20,0,0), False)
        draw_house((.5, .5, .5), (-20,0,40), True)

        pygame.display.flip()  # swap buffers
        pygame.time.wait(10)  # small delay to control camera speed

        
main()
