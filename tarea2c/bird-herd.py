import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import csv
import numpy as np

import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import lighting_shaders as ls
import scene_graph as sg
import splines as sp

from bird import createMartinP


class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
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

#Extraemos información del archivo para las trayectoria:
path = sys.argv[1]
points=[]
trayect=[]
pts=0
with open(path) as A:
    B= csv.reader(A)
    for l in B:
        c1=float(l[0])
        c2 = float(l[1])
        c3 = float(l[2])
        points+=[[c1,c2,c3]]
        pts+=1

#Interpolamos los puntos extraidos con Catmull-Rom:

for i in range(3,len(points)):
    GMcri=sp.catmulRom(np.array([points[i-3]]).T,np.array([points[i-2]]).T,np.array([points[i-1]]).T,np.array([points[i]]).T)
    spline=sp.evalCurve(GMcri,100*pts)
    #Vamos generando la trayectoria
    for p in spline:
        trayect.append(p)

#Función para crear un cubo con terxturas para el fondo con ciertas coordenadas dadas
# :
def createFondo(image_filename,lc):

    # Defining locations,texture coordinates for each vertex of the shape  
    vertices = [
    #   positions               tex coords             
    # Z+
        -0.5, -0.5,  0.5,    lc[0][0], lc[0][1],        
         0.5, -0.5,  0.5,    lc[1][0], lc[1][1],        
         0.5,  0.5,  0.5,    lc[2][0], lc[2][1],        
        -0.5,  0.5,  0.5,    lc[3][0], lc[3][1],           
    # Z-          
        -0.5, -0.5, -0.5,    lc[4][0], lc[4][1],       
         0.5, -0.5, -0.5,    lc[5][0], lc[5][1],       
         0.5,  0.5, -0.5,    lc[6][0], lc[6][1],       
        -0.5,  0.5, -0.5,    lc[7][0], lc[7][1],       
       
    # X+          
         0.5, -0.5, -0.5,    lc[8][0], lc[8][1],       
         0.5,  0.5, -0.5,    lc[9][0], lc[9][1],       
         0.5,  0.5,  0.5,    lc[10][0], lc[10][1],     
         0.5, -0.5,  0.5,    lc[11][0], lc[11][1],        
    # X-          
        -0.5, -0.5, -0.5,    lc[12][0], lc[12][1],     
        -0.5,  0.5, -0.5,    lc[13][0], lc[13][1],        
        -0.5,  0.5,  0.5,    lc[14][0], lc[14][1],        
        -0.5, -0.5,  0.5,    lc[15][0], lc[15][1],           
    # Y+          
        -0.5,  0.5, -0.5,    lc[16][0], lc[16][1],        
         0.5,  0.5, -0.5,    lc[17][0], lc[17][1],        
         0.5,  0.5,  0.5,    lc[18][0], lc[18][1],        
        -0.5,  0.5,  0.5,    lc[19][0], lc[19][1],           
    # Y-          
        -0.5, -0.5, -0.5,    lc[20][0], lc[20][1],        
         0.5, -0.5, -0.5,    lc[21][0], lc[21][1],        
         0.5, -0.5,  0.5,    lc[22][0], lc[22][1],        
        -0.5, -0.5,  0.5,    lc[23][0], lc[23][1],        
        ]   

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    return bs.Shape(vertices, indices, image_filename)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Little bird", None, None)

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
    texturePipeline = es.SimpleTextureModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = es.toGPUShape(bs.createAxis(5))
    bird1 = createMartinP()
    bird2 = createMartinP()
    bird3 = createMartinP()
    bird4 = createMartinP()
    bird5 = createMartinP()
    birds = np.array([bird1,bird2,bird3,bird4,bird5])

    #Coordenadas para el cubo con el fondo del bosque:
    coords3=np.array([[0,0],[0,0],[0,0],[0,0],
                        [0,0],[0,0],[0,0],[0,0],
                        [1/2,1],[1/4,1],[1/4,0],[1/2,0],
                        [3/4,1],[1,1],[1,0],[3/4,0],
                        [0,1],[1/4,1],[1/4,0],[0,0],
                        [3/4,1],[1/2,1],[1/2,0],[3/4,0]
                        ]) 

    fondo3 = es.toGPUShape(createFondo("bosque2.jpg",coords3),GL_REPEAT,GL_LINEAR)
    sky = es.toGPUShape(bs.createTextureQuad("cielo1.jpg"),GL_REPEAT,GL_LINEAR)
    floor = es.toGPUShape(bs.createTextureQuad("bosque3.jpg"),GL_REPEAT,GL_LINEAR)

    #Definimos variables iniciales
    t0 = glfw.get_time()
    mousePosY0 = 0
    mousePosX0 = 0
    p=0
    tray0 = trayect[0]
    dx0=1
    while not glfw.window_should_close(window):
        if p==len(trayect):
            p=0

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration


    #Definimos la posición del mouse en coordenadas de ventana
        mousePosX = 2 * (controller.mousePos[0] - width/2) / width
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height

        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)
    #Definimos la posición de la cámara
        viewPos = np.array([-10,5,5])

        view = tr.lookAt(
            viewPos,
            np.array([-mousePosX*10,-mousePosX*10,mousePosY*10]),
            np.array([0,0,1])
        )

        axis = np.array([1,-1,1])
        #axis = np.array([0,0,1])
        axis = axis / np.linalg.norm(axis)
    #Vemos el delta posición para determinar la rotación del ave ( hacia donde mira)
        x1 = trayect[p][0]
        x0 = tray0[0]
        dx = x1-x0

        tray0=trayect[p]

        rotx = tr.identity()

    #definimos la rotación correspondiente
        if dx<0:
            rotx=tr.rotationZ(np.pi/2)
        elif dx>0:
            rotx=tr.rotationZ(-np.pi/2)
    #Definimos las transformaciones correspondientes a cada ave en cada iteración
        model1 =  tr.matmul([tr.translate(trayect[p][0],trayect[p][1],trayect[p][2]),rotx,tr.uniformScale(0.4)])
        model2 =  tr.matmul([tr.translate(trayect[p][0]+2,trayect[p][1]-2,trayect[p][2]),rotx,tr.uniformScale(0.4)])
        model3 =  tr.matmul([tr.translate(trayect[p][0]-2,trayect[p][1]-2,trayect[p][2]),rotx,tr.uniformScale(0.4)])
        model4 =  tr.matmul([tr.translate(trayect[p][0]+4,trayect[p][1]-4,trayect[p][2]),rotx,tr.uniformScale(0.4)])
        model5 =  tr.matmul([tr.translate(trayect[p][0]-4,trayect[p][1]-4,trayect[p][2]),rotx,tr.uniformScale(0.4)])
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

        #usamos el shader de texturas para los fondos

        glUseProgram(texturePipeline.shaderProgram)


        

        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([tr.translate(0,0,-26),tr.uniformScale(55)]))
        texturePipeline.drawShape(floor)

        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([tr.translate(0,0,26),tr.uniformScale(55)]))
        texturePipeline.drawShape(sky)

        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.scale(54,54,60))
        texturePipeline.drawShape(fondo3)
    
    #cambiamos el shader para iluminación

        glUseProgram(lightingPipeline.shaderProgram)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Bright white for diffuse and specular components.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.4, 0.4, 0.4)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.8, 0.9)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!
        
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), 0, 0, 15)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    #definimos las tranformaciones y las aplicamos para las alas y la cola
        m=0
        t1 = glfw.get_time()

        for pajaro in birds:
            
            theta=np.cos(t1*6+m)*0.8
            theta2=  np.cos(t1*6+m)
            theta3= np.cos(t1*5+m)

            wing2LRot = sg.findNode(pajaro, 'wing2LRot')
            wing2LRot.transform = tr.rotationY(theta)

            wingLRot = sg.findNode(pajaro, 'wingLRot')
            wingLRot.transform = tr.rotationY(theta2)

            wing2RRot = sg.findNode(pajaro, 'wing2RRot')
            wing2RRot.transform = tr.rotationY(-theta)

            wingRRot = sg.findNode(pajaro, 'wingRRot')
            wingRRot.transform = tr.rotationY(-theta2)

            colitaRot = sg.findNode(pajaro, 'colitaRot')
            colitaRot.transform = tr.rotationX( theta3)
            
            m+=1

    #Aplicamos las transformaciones definidas antes a cada pájaro    
        bird1.transform=model1
        bird2.transform=model2
        bird3.transform=model3
        bird4.transform=model4
        bird5.transform=model5
    #Dibujamos 
        sg.drawSceneGraphNode(bird1,lightingPipeline,'model')
        sg.drawSceneGraphNode(bird2,lightingPipeline,'model')
        sg.drawSceneGraphNode(bird3,lightingPipeline,'model')
        sg.drawSceneGraphNode(bird4,lightingPipeline,'model')
        sg.drawSceneGraphNode(bird5,lightingPipeline,'model')

    #Sumamos al contador para recorrer la trayectoria
        p+=1
        
        
        glfw.swap_buffers(window)
        

    glfw.terminate()
