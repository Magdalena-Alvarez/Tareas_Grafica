import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import json
import matplotlib.pyplot as plt
import PIL as pl

import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es

class Controller:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.rotate = False
        self.fillPolygon = True
        self.mousePos = (0, 0)
        self.leftClickOn = False
        self.Save=False
        
        
    def reset(self):
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.rotate = False
        self.fillPolygon = True
        self.mousePos = (0, 0)

controller = Controller()

def cursor_pos_callback(window, x, y): # da la posición del mouse en pantalla con coordenadas de la ventana
    global controller
    controller.mousePos = (x,y)

  

#    glfw.MOUSE_BUTTON_1: left click
#    glfw.MOUSE_BUTTON_2: right click
#    glfw.MOUSE_BUTTON_3: scroll click

# definimos las acciones que ocurren al presionar el mouse

def mouse_button_callback(window, button, action, mods): 
    global controller
    if (action == glfw.PRESS or action == glfw.REPEAT):

        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = True

        if (button == glfw.MOUSE_BUTTON_2):
            controller.rightClickOn = True
        

    elif (action ==glfw.RELEASE):

        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = False

        if (button == glfw.MOUSE_BUTTON_2):
            controller.rightClickOn = False
#definimos lo que hacen las teclas
def on_key(window, key, scancode, action, mods):

    if action == glfw.PRESS:
        if key == glfw.KEY_G or key==glfw.KEY_S:
            controller.Save=True

        if key == glfw.KEY_ESCAPE:
            sys.exit()
    elif action == glfw.RELEASE:
        if key == glfw.KEY_G or key==glfw.KEY_S:
            controller.Save=False

#extrayendo información de inputs:

N= int(sys.argv[1])              #tamaño grilla
paleta= sys.argv[2]                #archivo con la paleta
fileName= sys.argv[3]               #Nombre con que se guardará el archivo

#extraer informacion de la paleta:

with open(paleta) as A:
    B=json.load(A)

tran=B["transparent"]           #Definimos el color que será el transparente
colors=[]                   #Lista en que guasdaremos los colores


#Guadamos los colores de la paleta, anañdiendo el elemento de transparencia

for color in B['pallete']:
    colors.append(color +[1.0])
pallete=[tran + [0.0]] + colors
colorActivo=pallete[0]                  #definimos nuestro color activo inicial

#Comenzaremos con la grilla:

grilla=np.zeros((N,N,4) , dtype= np.float32)
grilla[:][:] = pallete[0]                   #Dando a la grilla el color transparente inicual

#definimos la figura del cuadrado base:
#formado por uno del color indicado y el otro negro más grande para der el borde
def createQuadBorde(color):
    gpuBlackQuad=es.toGPUShape(bs.createColorQuad(0,0,0))
    gpuGrayQuad= es.toGPUShape(bs.createColorQuad(color[0],color[1],color[2]))

    #crear cuadrado:
    fondo=sg.SceneGraphNode("fondo")
    fondo.childs+=[gpuBlackQuad]

    quady=sg.SceneGraphNode("quady")
    quady.transform=tr.uniformScale(0.9)
    quady.childs+=[gpuGrayQuad]

    cuadradito=sg.SceneGraphNode("cuadradito")
    cuadradito.childs+=[fondo,quady]

    return cuadradito


#definimos la figura de la cuadrícula de NxN cuadraditos para pintar, 
def createGrilla(gril):
    n=gril.shape[0]

    grilla=sg.SceneGraphNode("grilla")
    baseName="cuadradito"
    a=0.5*1.5/n
    fil=np.array(range(0,n),dtype=int)
    col=np.array(range(0,n), dtype=int)
    for i in fil:
        for j in col:
            NewQuad= sg.SceneGraphNode(baseName + str(i)+' '+str(j))
            NewQuad.transform=tr.matmul([tr.translate((-0.8+a)+2*a*j,(0.55-a)-2*a*i,0),tr.uniformScale(1.5/n)])
            NewQuad.childs+=[createQuadBorde(gril[i][j])]
            grilla.childs+=[NewQuad]
    return grilla

#Creamos la fila de recuadros con los colores el la parte superior:

def createColoresQuad(paleta):
    columna=sg.SceneGraphNode("columnaColores")
    baseName="rectangulito"
    for i in range(0,len(paleta)):
        cuadEsc=sg.SceneGraphNode(baseName + str(i))
        cuadEsc.transform=  tr.matmul([tr.translate(-0.9+0.095*i,0.7,0), tr.scale(0.09,0.15,1)])
        cuadEsc.childs+= [createQuadBorde(paleta[i])]
        columna.childs+=[cuadEsc]
    return columna

#Juntamos la grilla con la fila de colores en la ventana:

def createVentana(grilla,paleta):
    
    ventana=sg.SceneGraphNode("ventana")
    ventana.childs+=[createGrilla(grilla),createColoresQuad(paleta)]

    return ventana

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Pixel Paint", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function ' mouse_button_callback' and 'cursor_pos_callback' to handle mouse events
    #
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    # Connecting the callback function ' on_key ' to handle keyboard events
    glfw.set_key_callback(window, on_key) 
    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTransformShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    #generamos la ventana 
    
    ventana=createVentana(grilla,pallete)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

          

        if controller.leftClickOn:

            # Getting the mouse location in opengl coordinates  
            mousePosX = 2 * (controller.mousePos[0] - width/2) / width
            mousePosY = 2 * (height/2 - controller.mousePos[1]) / height
           
            num=np.array(range(0,len(pallete)))

            #Con el click verificamos que si se clickea en algun color, lo identificamos y 
            # extraemos el color para declararlo como activo 
            for k in num:
                baseName='rectangulito'
                poscuad=sg.findPosition(ventana,baseName+str(k))
                if mousePosX >=poscuad[0]-0.035 and mousePosX<=poscuad[0]+0.035: 
                    if mousePosY >=poscuad[1]-0.07 and mousePosY<=poscuad[1]+0.07:
                        colorActivo=pallete[k]
                        print('Color activo: ', colorActivo[:3])

            num1=np.array(range(0,N))

            #Con el click verificamos que si se clickea sobre un cuadrado de la cuadrícula lo
            #identificamos y cambiamos su color por el color activo
            for h in num1:
                for g in num1:
                    baseName2="cuadradito"
                    poscuady=sg.findPosition(ventana,baseName2+str(h)+' '+str(g))
                    if mousePosX >=poscuady[0]-(0.5*1.5/N) and mousePosX<=poscuady[0]+(0.5*1.5/N) and mousePosY >=poscuady[1]-(0.5*1.5/N) and mousePosY<=poscuady[1]+(0.5*1.5/N):
                        cuady=sg.findNode(ventana, baseName2+str(h)+' '+str(g))
                        cuadyy=createQuadBorde(colorActivo)
                        cuady.childs+=[cuadyy]
                        grilla[h][g]=colorActivo

        #Cuando el usuario quiera guardar su imagen con G o S, guardamos la matriz numpy con
        #el nombre indicado al inicio
        
        if controller.Save:
            print('Guardando...')
            plt.imsave(fileName,grilla)
            print('Guardado')

        sg.drawSceneGraphNode(ventana, pipeline, "transform")

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)
    

    
    glfw.terminate()