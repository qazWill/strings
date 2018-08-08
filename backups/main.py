import math, random, sys, time

# openggl
from OpenGL.GL import *
from OpenGL.GLU import *

# pygame
import pygame
from pygame.locals import *

# matrix
from gameobjects.matrix44 import *

def abs(a):
    if a < 0:
        a = -a
    return a

def add(a, b):
    result = []
    for i in [0, 1, 2]:
        result.append(a[i] + b[i])
    return result

def multiply(a, b):
    result = []
    for i in [0, 1, 2]:
        result.append(a[i] * b[i])
    return result

def cmultiply(a, b):
    result = []
    for i in [0, 1, 2]:
        result.append(a[i] * b)
    return result

def cdivide(a, b):
    result = []
    for i in [0, 1, 2]:
        result.append(a[i] / b)
    return result

def negate(a):
    result = []
    for i in [0, 1, 2]:
        result.append(-a[i])
    return result

def mag(a):
    return math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2])

class SpringAnchored:
    def __init__():
        self.k = k
        self.pos = pos
        self.mass

class Spring:
    
    def __init__(k, length, pos1, pos2, mass1, mass2):
        self.k = k
        self.length = length
        self.pos1 = pos1
        self.pos2 = pos2
        self.mass1 = mass1
        self.mass2 = mass2
    
    def getForce():
        r = add(pos2, negate(pos1))
        r_mag = mag(r)
        r_dir = cdivide(r, r_mag)
        force1 = cmultiply(r_dir, (r_mag - length) * k)
        return [force1, -force1]

class Web:
    
    def __init__(self, k, length, n, pos, mass, object):
        self.k = k
        self.length = length
        self.n = n
        self.anchor = pos
        self.mass = mass
        self.object = object
        self.pos = []
        self.vel = []
        for i in range(0, n):
            self.pos.append(add(pos, cmultiply([0, -1.8 * length, 0], n - i)))
            self.vel.append([0, 0, 0])
        self.object.pos = add(pos, cmultiply([0, -1.8 * length, 0], n + 1))

        size = 0.1
        self.size = size

        self.vertices = [ [0.0, 0.0, size],
                 [size, 0.0, size],
                 [size, size, size],
                 [0.0, size, size],
                 [0.0, 0.0, 0.0],
                 [size, 0.0, 0.0],
                 [size, size, 0.0],
                 [0.0, size, 0.0] ]
                 
        self.normals = [ (0.0, 0.0, +1.0),  # front
                                 (0.0, 0.0, -1.0),  # back
                                 (+1.0, 0.0, 0.0),  # right
                                 (-1.0, 0.0, 0.0),  # left
                                 (0.0, +1.0, 0.0),  # top
                                 (0.0, -1.0, 0.0) ] # bottom
                                 
        self.faces = [ (0, 1, 2, 3),  # front
                                               (4, 5, 6, 7),  # back
                                               (1, 5, 6, 2),  # right
                                               (0, 4, 7, 3),  # left
                                               (3, 2, 6, 7),  # top
                                               (0, 1, 5, 4) ] # bottom
                                               
        self.colors = [ (1.0, 0, 0),
                                                              (0.0, 1.0, 0),
                                                              (0.0, 0.0, 1.0),
                                                              (1.0, 1.0, 0.0),
                                                              (1.0, 0.0, 1.0),
                                                              (0.0, 1.0, 1.0) ]
    
    def getForce(self, pos1, pos2, vel, delta_t):
        r = add(pos2, negate(pos1))
        r_mag = mag(r)
        
        if r_mag <= self.length:
            return [0, 0, 0]
        r_dir = [0.0, 0.0, 0.0]
        if r_mag == 0:
            print "0"
        else:
            r_dir = cdivide(r, float(r_mag))
        force1 = cmultiply(r_dir, abs(r_mag - self.length) * self.k)
        
        # checks if object is moving away or towards
        new_pos = add(pos1, vel)
        new_dist = mag(add(negate(pos2), new_pos))
        resist = 1.0
        if (new_dist > r_mag): # moving outward
           resist = 1.2
        force1 = cmultiply(force1, resist)
        
        return force1

    def getForceAvg(self, pos1, pos2, vel, delta_t):
        force_initial = self.getForce(pos1, pos2, vel, delta_t)
            
        accel = cdivide(force_initial, self.mass)
        delta_v = cmultiply(accel, delta_t)
        v_avg = cdivide(add(cmultiply(vel, 2), delta_v), 2.0)
        vel = add(vel, delta_v)
        delta_x = cmultiply(v_avg, delta_t)
        final_pos = add(pos1, delta_x)
        
        force_final = self.getForce(final_pos, pos2, vel, delta_t)
        return cmultiply(add(force_final, force_initial), 0.5)
    
    def move(self, delta_t):
        self.object.addForce(self.getForceAvg(self.object.pos, self.pos[0], self.object.vel, delta_t))
        delta_x = []
        for i in range(0, self.n - 1):
            delta_x.append([0, 0, 0])
        for i in range(0, self.n - 1):
            i = self.n - 2 - i
            print i
            accel = cdivide(self.getForceAvg(self.pos[i], self.pos[i + 1], self.vel[i], delta_t), self.mass)
            if i != 0:
                accel = add(accel, cdivide(self.getForceAvg(self.pos[i], self.pos[i - 1], self.vel[i], delta_t), self.mass))
            else:
                accel = add(accel, cdivide(self.getForceAvg(self.pos[i], self.object.pos, self.vel[i], delta_t), self.mass))
            accel = add(accel, [0, -9.8, 0])
            accel = add(accel, cmultiply(cmultiply(multiply(self.vel[i], self.vel[i]), -0.5), self.mass))

            delta_v = cmultiply(accel, delta_t)
            v_avg = cdivide(add(cmultiply(self.vel[i], 2), delta_v), 2.0)
            self.vel[i] = add(self.vel[i], delta_v)
            delta_x[i] = cmultiply(v_avg, delta_t)
            change = cmultiply(multiply(self.vel[i], self.vel[i]), 1 * delta_t)
            if mag(change) > self.vel[i]:
                self.vel[i] = 0
            else:
                self.vel[i] = add(self.vel[i], change)
            self.pos[i] = add(self.pos[i], delta_x[i])
        '''for i in range(0, self.n - 1):
            self.pos[i] = add(self.pos[i], delta_x[i])'''
        self.object.move(delta_t)

    def render(self):

        for i1 in range(0, self.n):


            vertices = []
            for vertex in self.vertices:
                new_one = []
                for i2 in [0, 1, 2]:
                    new_one.append(vertex[i2] + self.pos[i1][i2] - self.size / 2.0)
                vertices.append(new_one)

            # begin drawing
            glBegin(GL_QUADS)

            for face in self.faces:
    
                glColor(self.colors[self.faces.index(face)])
    
                glVertex(vertices[face[0]])
    
                glVertex(vertices[face[1]])
    
                glVertex(vertices[face[2]])
    
                glVertex(vertices[face[3]])

            # stop drawing
            glEnd()

        self.object.render()

class Player:
    
    def __init__(self, mass, pos, vel, size):
        self.mass = mass
        self.pos = pos
        self.vel = vel
        self.net_force = [0, 0, 0]
        
        self.size = size
        
        self.vertices = [ [0.0, 0.0, size],
                         [size, 0.0, size],
                         [size, size, size],
                         [0.0, size, size],
                         [0.0, 0.0, 0.0],
                         [size, 0.0, 0.0],
                         [size, size, 0.0],
                         [0.0, size, 0.0] ]
                         
        self.normals = [ (0.0, 0.0, +1.0),  # front
                        (0.0, 0.0, -1.0),  # back
                        (+1.0, 0.0, 0.0),  # right
                        (-1.0, 0.0, 0.0),  # left
                        (0.0, +1.0, 0.0),  # top
                        (0.0, -1.0, 0.0) ] # bottom
                                         
        self.faces = [ (0, 1, 2, 3),  # front
                        (4, 5, 6, 7),  # back
                        (1, 5, 6, 2),  # right
                        (0, 4, 7, 3),  # left
                        (3, 2, 6, 7),  # top
                        (0, 1, 5, 4) ] # bottom
    
        self.colors = [ (1.0, 0, 0),
                        (0.0, 1.0, 0),
                        (0.0, 0.0, 1.0),
                        (1.0, 1.0, 0.0),
                        (1.0, 0.0, 1.0),
                        (0.0, 1.0, 1.0) ]
    
    def render(self):
        vertices = []
        for vertex in self.vertices:
            new_one = []
            for i in [0, 1, 2]:
                new_one.append(vertex[i] + self.pos[i] - self.size / 2.0)
            vertices.append(new_one)
        
        
        glColor((0.30, 0.30, 0.45))
        
        # begin drawing
        glBegin(GL_QUADS)
        
        for face in self.faces:
        
            glColor(self.colors[self.faces.index(face)])
            
            glVertex(vertices[face[0]])
            
            glVertex(vertices[face[1]])
            
            glVertex(vertices[face[2]])
            
            glVertex(vertices[face[3]])
        
        # stop drawing
        glEnd()
    
    def addForce(self, force):
        self.net_force = add(self.net_force, force)
    
    def move(self, delta_t):
        accel = cdivide(self.net_force, self.mass)
        delta_v = cmultiply(accel, delta_t)
        v_avg = cdivide(add(cmultiply(self.vel, 2), delta_v), 2.0)
        self.vel = add(self.vel, delta_v)
        delta_x = cmultiply(v_avg, delta_t)
        self.pos = add(self.pos, delta_x)
        self.net_force = [0, 0, 0]
        self.vel = add(self.vel, cmultiply(self.vel, -0.1 * delta_t))


def resize(width, height):
    
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(width)/height, .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init():
    
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_FLAT)
    
    glClearColor(0.8, 0.8, 0.8, 0)
    glEnable(GL_COLOR_MATERIAL)
    
    '''glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLight(GL_LIGHT0, GL_POSITION,  (0, 0.8, -1, 1))
    glLight(GL_LIGHT0, GL_AMBIENT,  (0.02, 0.02, 0.02, 1))
    glLight(GL_LIGHT0, GL_DIFFUSE,  (0.7, 0.7, 0.7, 1))'''
    
    # Enables Fog
    '''glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (1, 1, 1))
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 0)
    glFogf(GL_FOG_END, 50)'''



pygame.init()
#screen = pygame.display.set_mode((800, 600), HWSURFACE|OPENGL|DOUBLEBUF|FULLSCREEN) # (1366, 768) is Full Screen
screen = pygame.display.set_mode((800, 600), HWSURFACE|OPENGL|DOUBLEBUF)
pygame.display.set_caption("String test")
resize(screen.get_width(), screen.get_height())
init()

player = Player(1.5, [0, 0, 0], [0, 0, 0], 0.2)
web = Web(80, 0.1, 7, [0, 0 ,0], 0.1, player)
rotation = [0.0, 45.0, 0]
translate = [5, 0, 5]
display_list = None
speed = 8

# makes mouse invisible
pygame.mouse.set_visible(False)

clock = pygame.time.Clock()

# Camera transform matrix
camera_matrix = Matrix44()
camera_matrix.translate = (5, 6, 5)
rotation_matrix = Matrix44.xyz_rotation(0, 180, 0)
camera_matrix *= rotation_matrix

# Upload the inverse camera matrix to OpenGL
glLoadMatrixd(camera_matrix.get_inverse().to_opengl())


done = False
while not done:
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYUP and event.key == K_ESCAPE:
            sys.exit()
            done = True
        if event.type == KEYUP:
            if event.key == K_u:
                web.object.vel = add(web.object.vel, [0, 2, 0])
            if event.key == K_o:
                web.object.vel = add(web.object.vel, [0, -2, 0])
            if event.key == K_l:
                web.object.vel = add(web.object.vel, [2, 0, 0])
            if event.key == K_j:
                web.object.vel = add(web.object.vel, [-2, 0, 0])
            if event.key == K_i:
                web.object.vel = add(web.object.vel, [0, 0, 2])
            if event.key == K_k:
                web.object.vel = add(web.object.vel, [0, 0, -2])

    # Clear the screen, and z-buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    time_passed = clock.tick(30)
    time_passed_seconds =  1 * time_passed / 1000.0
    
    # gets rotation based on mouse movement
    mouse_rel_x, mouse_rel_y = pygame.mouse.get_rel()
    rotation[1] -= float(mouse_rel_x) / 4
    rotation[0] -= float(mouse_rel_y) / 4
    
    # gets list of pressed keys
    pressed = pygame.key.get_pressed()
    
    # adjusts translate based on the keys pressed
    old_x, old_y, old_z = translate
    if pressed[K_w]:
        x = math.sin(math.radians(rotation[1]))
        z = math.cos(math.radians(rotation[1]))
        translate[0] += x * -speed * time_passed_seconds
        translate[2] += z * -speed * time_passed_seconds
    elif pressed[K_s]:
        x = math.sin(math.radians(rotation[1]))
        z = math.cos(math.radians(rotation[1]))
        translate[0] += x * speed * time_passed_seconds
        translate[2] += z * speed * time_passed_seconds
    if pressed[K_a]:
        x = math.sin(math.radians(rotation[1] + 90))
        z = math.cos(math.radians(rotation[1] + 90))
        translate[0] += x * -speed * time_passed_seconds
        translate[2] += z * -speed * time_passed_seconds
    elif pressed[K_d]:
        x = math.sin(math.radians(rotation[1] + 90))
        z = math.cos(math.radians(rotation[1] + 90))
        translate[0] += x * speed * time_passed_seconds
        translate[2] += z * speed * time_passed_seconds
    if pressed[K_q]:
        translate[1] += speed * time_passed_seconds
    elif pressed[K_e]:
        translate[1] -= speed * time_passed_seconds

    web.object.addForce([0, -9.8 * web.object.mass, 0])
    #web.object.addForce(cmultiply(multiply(web.object.vel, web.object.vel), -0.05))
    web.move(time_passed_seconds)
    #web.object.addForce([0, -9.8, 0])

    # resets camera matrix
    camera_matrix = Matrix44()
    camera_matrix.translate = translate
    rotation_matrix = Matrix44.xyz_rotation(0, 0, 0)
    camera_matrix *= rotation_matrix
    
    # calculate rotation matrix and multiply by camera matrix
    rotation_matrix = Matrix44.xyz_rotation(0, math.radians(rotation[1]), 0)
    camera_matrix *= rotation_matrix
    rotation_matrix = Matrix44.xyz_rotation(math.radians(rotation[0]), 0, 0)
    camera_matrix *= rotation_matrix
    
    # Upload the inverse camera matrix to OpenGL
    glLoadMatrixd(camera_matrix.get_inverse().to_opengl())
    
        
    web.render()
    
    # Show the screen
    pygame.display.flip()