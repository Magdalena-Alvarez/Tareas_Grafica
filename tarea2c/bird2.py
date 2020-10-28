import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import basic_shapes as bs
import easy_shaders as es
import scene_graph as sg
import transformations as tr
import lighting_shaders as ls

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.theta = 0
        self.theta1 = 0
        self.mousePos = (0,0)

# we will use the global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_LEFT_CONTROL:
        controller.showAxis = not controller.showAxis

    elif key == glfw.KEY_ESCAPE:
        sys.exit()

# función que permite obtener coordenadas de la ventana
def cursor_pos_callback(window, x, y): 
    global controller 
    controller.mousePos = (x,y)

# función para crear el pájaro
def bird():
    gpuGreen = es.toGPUShape(bs.createColorNormalsCube(0.1765,0.4,0.1725))
    gpuBody = es.toGPUShape(bs.createColorNormalsCube(0.502,0.251,0))
    gpuWing = es.toGPUShape(bs.createColorNormalsCube(0.3,0.3,0.3))
    gpuBack = es.toGPUShape(bs.createColorNormalsCube(0.3,0.3,0.3))
    gpueye1 = es.toGPUShape(bs.createColorNormalsCube(1,1,1))
    gpueye2 = es.toGPUShape(bs.createColorNormalsCube(0,0,0))
    gpuMouth = es.toGPUShape(bs.createColorNormalsCube(1,1,0))

    # ojos
    L_eye = sg.SceneGraphNode("l_eye1")
    L_eye.transform = tr.matmul([tr.translate(2.1,0.3,1.15), tr.scale(0.1,0.3,0.4)])
    L_eye.childs = [gpueye1]

    L_eye2 = sg.SceneGraphNode("l_eye2")
    L_eye2.transform = tr.matmul([tr.translate(2.12,0.3,1.1), tr.scale(0.1,0.3,0.2)])
    L_eye2.childs = [gpueye2]

    L_eyef = sg.SceneGraphNode("l_eyef")
    L_eyef.childs = [L_eye, L_eye2]

    R_eye = sg.SceneGraphNode("r_eye1")
    R_eye.transform = tr.matmul([tr.translate(2.1,-0.3,1.15), tr.scale(0.1,0.3,0.4)])
    R_eye.childs = [gpueye1]

    R_eye2 = sg.SceneGraphNode("r_eye2")
    R_eye2.transform = tr.matmul([tr.translate(2.12,-0.3,1.1), tr.scale(0.1,0.3,0.2)])
    R_eye2.childs = [gpueye2]

    R_eyef = sg.SceneGraphNode("r_eyef")
    R_eyef.childs = [R_eye, R_eye2]

    eyes = sg.SceneGraphNode("eyes")
    eyes.childs = [L_eyef, R_eyef]

    # cabeza
    head1 = sg.SceneGraphNode("head1")
    head1.transform = tr.matmul([tr.translate(1.5,0,1), tr.uniformScale(1.2)])
    head1.childs = [gpuGreen]

    # boca
    mouth1 = sg.SceneGraphNode("mouht1")
    mouth1.transform = tr.matmul([tr.translate(2,0,0.75), tr.scale(1,0.7,0.1)])
    mouth1.childs = [gpuMouth]

    # unión de cabeza, boca y ojos
    head_f = sg.SceneGraphNode("head")
    head_f.childs = [head1,eyes,mouth1]

    # cuello
    neck = sg.SceneGraphNode("neck")
    neck.transform = tr.matmul([tr.rotationY(-np.pi/5), tr.translate(1,0,0), tr.scale(0.7,0.5,0.5)])
    neck.childs = [gpuGreen]

    # alas
    #izq

    wing1_1 = sg.SceneGraphNode("wing1.1")
    wing1_1.transform = tr.matmul([tr.translate(0,0.75,0.2), tr.scale(1,1.5,0.2)])
    wing1_1.childs = [gpuWing]

    wing1_2 = sg.SceneGraphNode("wing1.2")
    wing1_2.transform = tr.matmul([tr.translate(0,0.75,0), tr.scale(1,1.5,0.2)])
    wing1_2.childs = [gpuWing]

    rotWing1_2 = sg.SceneGraphNode("rot wing1.2")
    rotWing1_2.childs = [wing1_2]

    transWing1_2 = sg.SceneGraphNode("trans wing1.2")
    transWing1_2.transform = tr.translate(0,1.5,0.2)
    transWing1_2.childs = [rotWing1_2]
    
    l_wing = sg.SceneGraphNode("left wing")
    l_wing.childs = [wing1_1, transWing1_2]

    lw=sg.SceneGraphNode("l wing")
    lw.transform=tr.translate(0,0.,0)
    lw.childs+=[l_wing]

    #der

    wing2_1 = sg.SceneGraphNode("wing2.1")
    wing2_1.transform = tr.matmul([tr.translate(0,-1.5,0.2), tr.scale(1,1.5,0.2)])
    wing2_1.childs = [gpuWing]

    wing2_2 = sg.SceneGraphNode("wing2.2")
    wing2_2.transform = tr.matmul([tr.translate(0,-0.75,0), tr.scale(1,1.5,0.2)])
    wing2_2.childs = [gpuWing]

    rotWing2_2 = sg.SceneGraphNode("rot wing2.2")
    rotWing2_2.childs = [wing2_2]

    transWing2_2 = sg.SceneGraphNode("trans wing2.2")
    transWing2_2.transform = tr.translate(0,-2.25,0.2)
    transWing2_2.childs+=[rotWing2_2]
 
    r_wing = sg.SceneGraphNode("right wing")
    r_wing.transform=tr.rotationX(-controller.theta)
    r_wing.childs = [wing2_1, transWing2_2]

    rw=sg.SceneGraphNode("r wing")
    rw.transform=tr.translate(0,-0.1,0)
    rw.childs+=[r_wing]

    # cuerpo
    body = sg.SceneGraphNode("body")
    body.transform = tr.scale(2.2,1.5,0.9)
    body.childs = [gpuBody]

    # cola
    back = sg.SceneGraphNode("back")
    back.transform = tr.matmul([tr.translate(-0.1,0,0.5), tr.scale(0.2,1.5,1)])
    back.childs = [gpuBack]

    rotBack = sg.SceneGraphNode("rot back")
    rotBack.childs = [back]

    transBack = sg.SceneGraphNode("trans back")
    transBack.transform = tr.translate(-1.1,0,0.1)
    transBack.childs = [rotBack]

    # cabeza y cuello final
    headNneck = sg.SceneGraphNode("headNneck")
    headNneck.transform = tr.translate(0.25,0,-0.2)
    headNneck.childs = [head_f, neck]

    

    # unión de todas las partes
    all_body = sg.SceneGraphNode("all_body")
    all_body.childs = [lw, rw,body, transBack]

    # estructuras finales
    bird = sg.SceneGraphNode("bird")
    bird.childs = [headNneck, all_body]

    final = sg.SceneGraphNode("final")
    final.childs = [bird]

    return final

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Quack!", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    
    # Assembling the shader program (pipeline) with both shaders
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    lightingPipeline = ls.SimpleGouraudShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(mvpPipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = es.toGPUShape(bs.createAxis(7))
    bird = bird()

    # Using the same view and projection matrices in the whole application

    t0 = glfw.get_time()
    camera_theta = np.pi/4
    mousePosY1 = 0
    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
        
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height
        deltapos = mousePosY - mousePosY1
        mousePosY1 = mousePosY

        # rotación de la cámara
        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2 * dt

        controller.theta += 0.5 * deltapos
        controller.theta1 -= 0.8 * deltapos

        # ubicación de la cámara
        projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        camX = 10 * np.sin(camera_theta)
        camY = 10 * np.cos(camera_theta)

        viewPos = np.array([camX,camY,2])
        viewPos2 = np.array([0,0,15])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        rotation_theta = glfw.get_time()

        axis = np.array([1,-1,1])
        axis = axis / np.linalg.norm(axis)
        model = tr.rotationA(rotation_theta, axis)
        model = tr.identity()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # The axis is drawn without lighting effects
        if controller.showAxis:
            glUseProgram(mvpPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            mvpPipeline.drawShape(gpuAxis, GL_LINES)
        
        glUseProgram(lightingPipeline.shaderProgram)

        # Setting all uniform shader variables

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.8, 0.8, 0.8)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), -5, -5, 5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)
        
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, model)

        # rotación de las alas
        rotBack = sg.findNode(bird, "rot back")
        rotBack.transform = tr.rotationY(-0.25 * np.pi + controller.theta)
        
        l_wing = sg.findNode(bird, "left wing")
        l_wing.transform = tr.rotationX(controller.theta)

        r_wing = sg.findNode(bird, "right wing")
        r_wing.transform = tr.rotationX(-controller.theta)

        rotWing1_2 = sg.findNode(bird, "rot wing1.2")
        rotWing1_2.transform = tr.rotationX(controller.theta1)

        rotWing2_2 = sg.findNode(bird, "rot wing2.2")
        rotWing2_2.transform = tr.rotationX(-controller.theta1)

        sg.drawSceneGraphNode(bird, lightingPipeline, "model")
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()