import pygame
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

global time  # Time since the beginning of the program

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
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 800 / 600, 0.1, 1000)  # Set up perspective projection
    glMatrixMode(GL_MODELVIEW)
    glClearColor(0.50, 0.80, 0.90, 1.0)  # Set void color to sky blue

def draw_ground():
    """Draws a grassy ground plane as a solid color."""
    glColor3f(0.15, 0.55, 0.15)  # Grass green color
    glBegin(GL_QUADS)
    # Define vertices for the ground quad
    glVertex3f(-150, -2, 150)
    glVertex3f(150, -2, 150)
    glVertex3f(150, -2, -150)
    glVertex3f(-150, -2, -150)
    glEnd()

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
    coliseum_position = [75, 0, 75]  # [x, y, z] coordinates for the coliseum

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        camera_controls()  # Update camera based on user input
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear screen and depth buffer
        apply_camera()  # Apply camera transformations

        # Draw scene
        draw_tunnel()
        draw_ground()
        draw_road()
        draw_water()
        draw_background()

        
        glTranslatef(*coliseum_position)  # Move the coliseum to its specified position
        # Draw the coliseum components
        draw_cylinder(30, 50, 25, offset=0)
        draw_coliseum_walls(30, 50, 25)
        draw_dome(30, 50, 20, offset=25)

        pygame.display.flip()  # Swap buffers
        pygame.time.wait(10)  # Small delay to control camera speed

main()
