import matplotlib.pyplot as plt
import numpy as np



CONST_G = 0.06  # 6.67 e-11

class Body:
    """Class representing a body"""

    def __init__(self, name, position, mass, radius):
        self.name = name
        self.position = position
        self.mass = mass
        self.radius = radius

    def get_mass(self):
        return self.mass
    
    def get_pos(self):
        return self.position

    def get_radius(self):
        return self.radius


# Generating bodies
earth = Body(name='earth', position=(-1., -1., -1.), 
                mass=100.0, radius=0.5)
moon = Body(name='moon', position=(1., 1., 1.), 
                mass=20.0, radius=0.2)


def V(X, Y, Z, body):
    """Given a point x, y, z, calculates gravitatonial potential."""
    m = body.get_mass()
    xb, yb, zb = body.get_pos()

    potential = np.zeros(shape=X.shape)
    
    # x = X[i] si es que se va al ciclo for.
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            for k in range(X.shape[2]):
                x, y, z = X[i, j, k], Y[i, j, k], Z[i, j, k]
                euc_distance = np.sqrt((x-xb)**2 + (y-yb)**2 + (z-zb)**2)

                if euc_distance <= body.radius*1.1:
                    potential[i, j, k] = 0
                else:
                    potential[i, j, k] = -1 * CONST_G * m / euc_distance

    return potential

# otra forma con linspace, con el Y se recorre el X, para calcular X se tiene X = X_i


X, Y, Z = np.mgrid[-2:2:20j, -2:2:20j, -2:2:20j]
# Considerar: utilizar linspace endpoint=True

# Compute potential for both bodies
V_earth = V(X, Y, Z, earth)
V_moon = V(X, Y, Z, moon)

# Sum it to have the total effect.
V_total = V_earth + V_moon

print( V_total.shape[0],V_total.shape[1],V_total.shape[2])
print( X.shape[0],Y.shape[1],Z.shape[2])
# Storing our results
#np.save('Potentials_earth', V_earth)
#np.save('Potentials_moon', V_moon)
#np.save('Potentials', V_total)

def fast_marching_cube(X, Y, Z, scal_field, isosurface_value):
    dims = X.shape[0]-1, X.shape[1]-1, X.shape[2]-1
    voxels = np.zeros(shape=dims, dtype=bool)
    for i in range(1, X.shape[0]-1):
        for j in range(1, X.shape[1]-1):
            for k in range(1, X.shape[2]-1):
                # Tomamos desde i-1 hasta i+1, porque así analiza hasta el punto i
                # El slicing NO incluye el final.
                v_min = scal_field[i-1:i+1, j-1:j+1, k-1:k+1].min()
                v_max = scal_field[i-1:i+1, j-1:j+1, k-1:k+1].max()

                if v_min < isosurface_value and isosurface_value < v_max:
                    voxels[i,j,k] = True
                else:
                    voxels[i,j,k] = False

    return voxels


voxels = fast_marching_cube(X, Y, Z, V_total, -3.9408383)

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import transformations as tr
import easy_shaders as es
import basic_shapes as bs


PROJECTION_ORTHOGRAPHIC = 0
PROJECTION_FRUSTUM = 1
PROJECTION_PERSPECTIVE = 2


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.projection = PROJECTION_ORTHOGRAPHIC


# We will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_1:
        print('Orthographic projection')
        controller.projection = PROJECTION_ORTHOGRAPHIC

    elif key == glfw.KEY_2:
        print('Frustum projection')
        controller.projection = PROJECTION_FRUSTUM

    elif key == glfw.KEY_3:
        print('Perspective projection')
        controller.projection = PROJECTION_PERSPECTIVE

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

def createColorCube(i, j, k, X, Y, Z):
    l_x = X[i, j, k]
    r_x = X[i+1, j, k]
    b_y = Y[i, j, k]
    f_y = Y[i, j+1, k]
    b_z = Z[i, j, k]
    t_z = Z[i, j, k+1]
    c = np.random.rand
    #   positions    colors
    vertices = [
    # Z+: number 1
        l_x, b_y,  t_z, c(),c(),c(),
         r_x, b_y,  t_z, c(),c(),c(),
         r_x,  f_y,  t_z, c(),c(),c(),
        l_x,  f_y,  t_z, c(),c(),c(),
    # Z-: number 6
        l_x, b_y, b_z, 0,0,0,
         r_x, b_y, b_z, 1,1,1,
         r_x,  f_y, b_z, 0,0,0,
        l_x,  f_y, b_z, 1,1,1,
    # X+: number 5
         r_x, b_y, b_z, 0,0,0,
         r_x,  f_y, b_z, 1,1,1,
         r_x,  f_y,  t_z, 0,0,0,
         r_x, b_y,  t_z, 1,1,1,
    # X-: number 2
        l_x, b_y, b_z, 0,0,0,
        l_x,  f_y, b_z, 1,1,1,
        l_x,  f_y,  t_z, 0,0,0,
        l_x, b_y,  t_z, 1,1,1,
    # Y+: number 4
        l_x,  f_y, b_z, 0,0,0,
        r_x,  f_y, b_z, 1,1,1,
        r_x,  f_y, t_z, 0,0,0,
        l_x,  f_y, t_z, 1,1,1,
    # Y-: number 3
        l_x, b_y, b_z, 0,0,0,
        r_x, b_y, b_z, 1,1,1,
        r_x, b_y, t_z, 0,0,0,
        l_x, b_y, t_z, 1,1,1,
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,
        4, 5, 6, 6, 7, 4,
        4, 5, 1, 1, 0, 4,
        6, 7, 3, 3, 2, 6,
        5, 6, 2, 2, 1, 5,
        7, 4, 0, 0, 3, 7]

    return bs.Shape(vertices, indices)

def merge(destinationShape, strideSize, sourceShape):

    # current vertices are an offset for indices refering to vertices of the new shape
    offset = len(destinationShape.vertices)
    destinationShape.vertices += sourceShape.vertices
    destinationShape.indices += [(offset/strideSize) + index for index in sourceShape.indices]

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Projections Demo", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program
    pipeline = es.SimpleModelViewProjectionShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = es.toGPUShape(bs.createAxis(7))
    
    # Load potentials and grid
    load_voxels = voxels#np.load('voxels.npy')
    X, Y, Z = np.mgrid[-2:2:20j, -2:2:20j, -2:2:20j]
    
    isosurface = bs.Shape([], [])
    # Now let's draw voxels!
    for i in range(X.shape[0]-1):
        for j in range(X.shape[1]-1):
            for k in range(X.shape[2]-1):
                # print(X[i,j,k])
                if load_voxels[i,j,k]:
                    temp_shape = createColorCube(i,j,k, X,Y, Z)
                    merge(destinationShape=isosurface, strideSize=6, sourceShape=temp_shape)

    gpu_surface = es.toGPUShape(isosurface)

    t0 = glfw.get_time()
    camera_theta = np.pi/4

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt

        # Setting up the view transform

        camX = 10 * np.sin(camera_theta)
        camY = 10 * np.cos(camera_theta)

        viewPos = np.array([camX, camY, 10])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Setting up the projection transform

        if controller.projection == PROJECTION_ORTHOGRAPHIC:
            projection = tr.ortho(-8, 8, -8, 8, 0.1, 100)

        elif controller.projection == PROJECTION_FRUSTUM:
            projection = tr.frustum(-5, 5, -5, 5, 9, 100)

        elif controller.projection == PROJECTION_PERSPECTIVE:
            projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
        
        else:
            raise Exception()

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)


        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Drawing shapes with different model transformations
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(5,0,0))

        
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(3))
        pipeline.drawShape(gpuAxis, GL_LINES)
        pipeline.drawShape(gpu_surface)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()