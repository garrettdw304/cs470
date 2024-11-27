import pygame
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

global time  # time since beginning of program in ms

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

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    init_opengl()

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

        pygame.display.flip()  # swap buffers
        pygame.time.wait(10)  # small delay to control camera speed

main()
