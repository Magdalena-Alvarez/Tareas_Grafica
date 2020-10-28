import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import lighting_shaders as ls
import scene_graph as sg




# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.thetaEx = - np.pi/12
        self.thetaIn =  np.pi/12
        self.thetaCol = -np.pi/6
        self.mousePos = (0, 0)

# We will use the global controller as communication with the callback function
controller = Controller()

def cursor_pos_callback(window, x, y): # da la posición del mouse en pantalla con coordenadas de la ventana
    global controller
    controller.mousePos = (x,y)

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

#Función para crear un martín pescador:

def createMartinP():
    cuadosc=es.toGPUShape(bs.createColorNormalsCube(0.02,0.48,0.655))
    cuadclar=es.toGPUShape(bs.createColorNormalsCube(0.026,0.689,0.871))
    cuad= es.toGPUShape(bs.createColorNormalsCube(0.91,0.53,0.13))
    whitecuad = es.toGPUShape(bs.createColorNormalsCube(1,1,1))

    #Alas:
        
        #Ala izquiersa:

    wing1L= sg.SceneGraphNode("wing1L")
    wing1L.transform = tr.matmul([ tr.translate(0.75,0,0),tr.scale(1.5,1.2,0.2)])
    wing1L.childs += [cuadosc]

    wing2L = sg.SceneGraphNode("wing2L")
    wing2L.transform = tr.matmul([tr.translate(0.75,0,0),tr.scale(1.5,0.9,0.2)])
    wing2L.childs += [cuadclar]

    wing2LRot = sg.SceneGraphNode('wing2LRot')
    wing2LRot.transform = tr.rotationY(controller.thetaIn)
    wing2LRot.childs += [wing2L]

    wingLA = sg.SceneGraphNode("wingL2")
    wingLA.transform = tr.translate(1.52,0.15,0)
    wingLA.childs += [wing2LRot]

    wingLRot = sg.SceneGraphNode('wingLRot')
    wingLRot.transform = tr.rotationY(controller.thetaEx)
    wingLRot.childs += [wingLA,wing1L]

    wingL = sg.SceneGraphNode('wingL')
    wingL.transform =tr.translate(0.77,0,0.3)
    wingL.childs += [wingLRot]

        #Ala derecha:

    wing1R= sg.SceneGraphNode("wing1R")
    wing1R.transform = tr.matmul([ tr.translate(-0.75,0,0),tr.scale(1.5,1.2,0.2)])
    wing1R.childs += [cuadosc]

    wing2R = sg.SceneGraphNode("wing2R")
    wing2R.transform = tr.matmul([tr.translate(-0.75,0,0),tr.scale(1.5,0.9,0.2)])
    wing2R.childs += [cuadclar]

    wing2RRot = sg.SceneGraphNode('wing2RRot')
    wing2RRot.transform = tr.rotationY(-controller.thetaIn)
    wing2RRot.childs += [wing2R]

    wingRA = sg.SceneGraphNode("wingR2")
    wingRA.transform = tr.translate(-1.52,0.15,0)
    wingRA.childs += [wing2RRot]

    wingRRot = sg.SceneGraphNode('wingRRot')
    wingRRot.transform = tr.rotationY(-controller.thetaEx)
    wingRRot.childs += [wingRA,wing1R]

    wingR = sg.SceneGraphNode('wingR')
    wingR.transform =tr.translate(-0.77,0,0.3)
    wingR.childs += [wingRRot]

    #Superior:

        #Cabeza:

    head = sg.SceneGraphNode('head')
    head.transform = tr.matmul([tr.translate(0,0.25,1.5), tr.uniformScale(1.1)])
    head.childs += [cuadclar]

        #Cuello:

    neck = sg.SceneGraphNode('neck')
    neck.transform= tr.matmul([tr.translate(0,0,0.8), tr.scale(0.8,0.5,0.8)])
    neck.childs += [whitecuad]

        #Pico:

    pico = sg.SceneGraphNode('pico')
    pico.transform = tr.matmul([tr.translate(0,0.7,1.3), tr.scale(0.85,1.70,0.25)])
    pico.childs+=[cuadosc]

    sup = sg.SceneGraphNode('sup')
    sup.transform = tr.translate(0,1,0)
    sup.childs += [neck,pico,head]

    #Cola:

    colitaC = sg.SceneGraphNode('colitaC')
    colitaC.transform = tr.matmul([ tr.translate(0,-0.6,0), tr.scale(1,1.2,0.1)])
    colitaC.childs += [cuadosc]

    colitaRot = sg.SceneGraphNode('colitaRot')
    colitaRot.transform = tr.rotationX(controller.thetaCol)
    colitaRot.childs += [colitaC]

    colita = sg.SceneGraphNode('colita')
    colita.transform =tr.translate(0,-1.3,0.3)
    colita.childs += [colitaRot]

    #Cuerpo:

    body = sg.SceneGraphNode("body")
    body.transform = tr.scale(1.5,2.7,1)
    body.childs+=[cuad]

    bird = sg.SceneGraphNode("bird")
    bird.childs += [wingL,wingR,body,sup, colita]

    return bird

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Pajarito", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function cursor_pos_callback' to handle mouse events
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Different shader programs for different lighting strategies
    #lightingPipeline = ls.SimpleFlatShaderProgram()
    #lightingPipeline = ls.SimpleGouraudShaderProgram()
    lightingPipeline = ls.SimplePhongShaderProgram()

    # This shader program does not consider lighting
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = es.toGPUShape(bs.createAxis(5))
    gpuRainbowCube = es.toGPUShape(bs.createRainbowNormalsCube())
    bird = createMartinP()

    #Definimos varianles iniciales
    t0 = glfw.get_time()
    camera_theta = np.pi/4
    camara_Z = 4
    mousePosY0= 0
    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
        
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height
        dPos= mousePosY-mousePosY0
        mousePosY0 = mousePosY

        controller.thetaIn -= 0.5*dPos
        controller.thetaEx -=  dPos
        controller.thetaCol += dPos
    
    #Definimos el movimiento de las partes del ave:

        wing2LRot = sg.findNode(bird, 'wing2LRot')
        wing2LRot.transform = tr.rotationY(controller.thetaIn)

        wingLRot = sg.findNode(bird, 'wingLRot')
        wingLRot.transform = tr.rotationY(controller.thetaEx)

        wing2RRot = sg.findNode(bird, 'wing2RRot')
        wing2RRot.transform = tr.rotationY(-controller.thetaIn)

        wingRRot = sg.findNode(bird, 'wingRRot')
        wingRRot.transform = tr.rotationY(-controller.thetaEx)

        colitaRot = sg.findNode(bird, 'colitaRot')
        colitaRot.transform = tr.rotationX( controller.thetaCol)

        #projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

            #Definimos ángulos modificándolos para la posición de la cámara:
    
        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta += 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta -= 2* dt

        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            camara_Z+= 0.05

        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            camara_Z -= 0.05
    #Definimos las posición de la cámara:
        camX = 10 * np.sin(camera_theta)
        camY = 10 * np.cos(camera_theta)

        viewPos = np.array([camX,camY,camara_Z])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        rotation_theta = glfw.get_time()

        axis = np.array([1,-1,1])
        #axis = np.array([0,0,1])
        axis = axis / np.linalg.norm(axis)
        #model = tr.rotationA(rotation_theta, axis)
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

        # Selecting the shape to display

        glUseProgram(lightingPipeline.shaderProgram)

        # Setting all uniform shader variables

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), 0, 5, 7.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)
        
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, model)

        # Drawing:
        sg.drawSceneGraphNode(bird,lightingPipeline,'model')
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()