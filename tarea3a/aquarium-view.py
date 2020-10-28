###################
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import json
import sys
import numpy as np
import random

import transformations as tr
import easy_shaders as es
import basic_shapes as bs
import scene_graph as sg



class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.a = True
        self.b = True
        self.c = True

controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon
    
    elif key == glfw.KEY_A:
        controller.a= not controller.a

    elif key == glfw.KEY_B:
        controller.b= not controller.b

    elif key == glfw.KEY_C:
        controller.c= not controller.c

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

setups= sys.argv[1]

#extraemos los datos del problema:
with open(setups) as A:
    B=json.load(A)

Ta = B["t_a"]
Tb = B["t_b"]
Tc = B["t_c"]
na = B["n_a"] #cantidad de peces a
nb = B["n_b"] #cantidad de peces b
nc = B["n_c"] #cantidad de peces c

filename = B["filename"]
M=np.load(filename)
#print(M)
x=M.shape[0]
y=M.shape[1]
z=M.shape[2]

X, Y, Z = np.mgrid[-2:2:complex(x), -2:2:complex(y), -2:2:complex(z)]

#print(x,y,z)
#print( X.shape[0],Y.shape[1],Z.shape[2])


def fast_marching_cube(X, Y, Z, M, isosurface_value):
    dims = X.shape[0]-1, X.shape[1]-1, X.shape[2]-1
    voxels = np.zeros(shape=dims, dtype=bool)
    for i in range(1, X.shape[0]-1):
        for j in range(1, X.shape[1]-1):
            for k in range(1, X.shape[2]-1):
                # Tomamos desde i-1 hasta i+1, porque así analiza hasta el punto i
                # El slicing NO incluye el final.
                v_min = M[i-1:i+1, j-1:j+1, k-1:k+1].min()
                v_max = M[i-1:i+1, j-1:j+1, k-1:k+1].max()
                if v_min >= isosurface_value-2 and isosurface_value+2 >= v_max:
                    voxels[i,j,k] = True
                else:
                    voxels[i,j,k] = False
    
    return voxels

def createColorCube(i, j, k, X, Y, Z,c):
    l_x = X[i, j, k]
    r_x = X[i+1, j, k]
    b_y = Y[i, j, k]
    f_y = Y[i, j+1, k]
    b_z = Z[i, j, k]
    t_z = Z[i, j, k+1]
    #   positions    colors
    vertices = [
    # Z+: number 1
        l_x, b_y,  t_z, c[0],c[1],c[2],
         r_x, b_y,  t_z, c[0],c[1],c[2],
         r_x,  f_y,  t_z, c[0],c[1],c[2],
        l_x,  f_y,  t_z, c[0],c[1],c[2],
    # Z-: number 6
        l_x, b_y, b_z, c[0],c[1],c[2],
         r_x, b_y, b_z, c[0],c[1],c[2],
         r_x,  f_y, b_z, c[0],c[1],c[2],
        l_x,  f_y, b_z, c[0],c[1],c[2],
    # X+: number 5
         r_x, b_y, b_z, c[0],c[1],c[2],
         r_x,  f_y, b_z, c[0],c[1],c[2],
         r_x,  f_y,  t_z, c[0],c[1],c[2],
         r_x, b_y,  t_z, c[0],c[1],c[2],
    # X-: number 2
        l_x, b_y, b_z, c[0],c[1],c[2],
        l_x,  f_y, b_z, c[0],c[1],c[2],
        l_x,  f_y,  t_z, c[0],c[1],c[2],
        l_x, b_y,  t_z, c[0],c[1],c[2],
    # Y+: number 4
        l_x,  f_y, b_z, c[0],c[1],c[2],
        r_x,  f_y, b_z, c[0],c[1],c[2],
        r_x,  f_y, t_z, c[0],c[1],c[2],
        l_x,  f_y, t_z, c[0],c[1],c[2],
    # Y-: number 3
        l_x, b_y, b_z, c[0],c[1],c[2],
        r_x, b_y, b_z, c[0],c[1],c[2],
        r_x, b_y, t_z, c[0],c[1],c[2],
        l_x, b_y, t_z, c[0],c[1],c[2],
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


def pez(texfile,n,l,vertex):
    frame= es.toGPUShape(bs.createTextureQuad(texfile),GL_REPEAT,GL_LINEAR)
    pez=sg.SceneGraphNode('pez'+l)
    pez.transform=  tr.matmul([tr.rotationZ(np.pi/2),tr.rotationX(np.pi/2),tr.uniformScale(0.3)])
    pez.childs+=[frame]
    peces=sg.SceneGraphNode('peces'+l)
    for i in range(n):
        p=vertex[i]
        x= p[0]#random.uniform(xmin,xmax)
        y =p[1]# random.uniform(ymin,ymax)
        z= p[2]#random.uniform(zmin,zmax)
        peztras=sg.SceneGraphNode('pez tras'+l+str(i))
        peztras.transform=tr.translate(x,y,z)
        peztras.childs+=[pez]
        peces.childs+=[peztras]

    return peces

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Aquarium", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program
    pipelinevox = es.SimpleModelViewProjectionShaderProgram2()
    pipeline = es.SimpleTextureModelViewProjectionShaderProgram()
    # Telling OpenGL to use our shader program
    

    # Setting up the clear screen color
    glClearColor(0.1, 0.1, 0.1, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    #glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory

    voxa=fast_marching_cube(X,Y,Z,M,Ta)
    voxb=fast_marching_cube(X,Y,Z,M,Tb)
    voxc=fast_marching_cube(X,Y,z,M,Tc)

    isosurface2 = bs.Shape([], [])
    isosurface0 = bs.Shape([], [])
    isosurface1 = bs.Shape([], [])
    
    #listas de puntos donde pueden estar los peces:
    puntosa=[]
    puntosb=[]
    puntosc=[]

    # Now let's draw voxels!

    for i in range(X.shape[0]-1):
        for j in range(X.shape[1]-1):
            for k in range(X.shape[2]-1):
                #print(voxa[i,j,k])
                # print(X[i,j,k])
                if voxa[i,j,k]:
                    temp_shape0 = createColorCube(i,j,k, X,Y, Z,[1,1,0])
                    merge(destinationShape=isosurface0, strideSize=6, sourceShape=temp_shape0)
                    vertexa=temp_shape0.vertices
                    for v in range(1,len(vertexa),6):
                        puntosa.append([vertexa[v-1],vertexa[v],vertexa[v+1]])


                if voxb[i,j,k]:
                    temp_shape1 = createColorCube(i,j,k, X,Y, Z,[1,0,0])
                    merge(destinationShape=isosurface1, strideSize=6, sourceShape=temp_shape1)
                    vertexb=temp_shape1.vertices
                    for r in range(1,len(vertexb),6):
                        puntosb.append([vertexb[r-1],vertexb[r],vertexb[r+1]])


                if voxc[i,j,k]:
                    temp_shape2 = createColorCube(i,j,k, X,Y,Z,[0,1,1])
                    merge(destinationShape=isosurface2, strideSize=6, sourceShape=temp_shape2)
                    vertexc=temp_shape2.vertices
                    for p in range(1,len(vertexc),6):
                        puntosc.append([vertexc[p-1],vertexc[p],vertexc[p+1]])

    #print('x:',cminx,cmaxx)   
    #print('y:',cminy,cmaxy)
    #print('z:',cminz,cmaxz) 
    gpu_surface0 = es.toGPUShape(isosurface0)
    gpu_surface1 = es.toGPUShape(isosurface1)
    gpu_surface2 = es.toGPUShape(isosurface2)

    pa=[]
    for va in range(na):
        pa.append(random.choice(puntosa))
    pb=[]
    for vb in range(nb):
        pb.append(random.choice(puntosb))
    pc=[]
    for vc in range(nc):
        pc.append(random.choice(puntosc))


    pecesaf1= pez('peza12.png',na,'a',pa)
    pecesaf2= pez('peza22.png',na,'a',pa)
    pecesaf3= pez('peza32.png',na,'a',pa)

    pecesbf1= pez('pezb12.png',nb,'b',pb)
    pecesbf2= pez('pezb22.png',nb,'b',pb)
    pecesbf3= pez('pezb32.png',nb,'b',pb)

    pecescf1= pez('pezc12.png',nc,'c',pc)
    pecescf2= pez('pezc22.png',nc,'c',pc)
    pecescf3= pez('pezc32.png',nc,'c',pc)

    t0 = glfw.get_time()
    camera_theta = np.pi/4
    n=2.5
    camZ=5
    a=0
    b=0
    c=0
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta += 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta -= 2* dt

        if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
            n +=3* dt

        if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
            n -=3*dt

        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            camZ += 10 * dt

        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            camZ -= 10* dt

        # Setting up the view transform

        camX = 20 * np.sin(camera_theta)
        camY = 20 * np.cos(camera_theta)

        viewPos = np.array([camX, camY, camZ])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        

        # Setting up the projection transform
        projection = tr.perspectiveZoom(30, float(width)/float(height), 0.1,100,n)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Drawing shapes with different model transformations

        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)      
        #glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(3))

        
        if controller.a:
            
            
            #glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([tr.translate(-2,-3,0),tr.rotationZ(np.pi/2),tr.rotationX(np.pi/2),tr.uniformScale(0.5)]))
            l=a%400
            #peza= sg.findNode(pecesa,'peza')
            if l>=0 and l<100:
                sg.drawSceneGraphNode(pecesaf1,pipeline,'model')
            elif l>=100 and l<200:
                sg.drawSceneGraphNode(pecesaf2,pipeline,'model')
            elif l>=200 and l<300:
                sg.drawSceneGraphNode(pecesaf1,pipeline,'model')
            elif l>=300 and l<400:
                sg.drawSceneGraphNode(pecesaf3,pipeline,'model')
            a+=2
            
        
        if controller.b:

            #glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([tr.translate(-3,-2,0),tr.rotationZ(np.pi/2),tr.rotationX(np.pi/2),tr.uniformScale(0.5)]))
            l=b%400
            if l>=0 and l<100:
                sg.drawSceneGraphNode(pecesbf1,pipeline,'model')
            elif l>=100 and l<200:
                sg.drawSceneGraphNode(pecesbf2,pipeline,'model')
            elif l>=200 and l<300:
                sg.drawSceneGraphNode(pecesbf1,pipeline,'model')
            elif l>=300 and l<400:
                sg.drawSceneGraphNode(pecesbf3,pipeline,'model')
            b+=1
        
        if controller.c:
            #sg.drawSceneGraphNode(pecesc,pipeline,'model')
            #glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([tr.translate(-5,-5,0),tr.rotationZ(np.pi/2),tr.rotationX(np.pi/2),tr.uniformScale(0.5)]))
            l=c%400
            if l>=0 and l<100:
                sg.drawSceneGraphNode(pecescf1,pipeline,'model')
            elif l>=100 and l<200:
                sg.drawSceneGraphNode(pecescf2,pipeline,'model')
            elif l>=200 and l<300:
                sg.drawSceneGraphNode(pecescf1,pipeline,'model')
            elif l>=300 and l<400:
                sg.drawSceneGraphNode(pecescf3,pipeline,'model')
            c+=1.5
        
        glUseProgram(pipelinevox.shaderProgram)
        
        glUniformMatrix4fv(glGetUniformLocation(pipelinevox.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipelinevox.shaderProgram, "projection"), 1, GL_TRUE, projection)
        #glUniformMatrix4fv(glGetUniformLocation(pipelinevox.shaderProgram, "model"), 1, GL_TRUE, tr.translate(5,0,0))
        glUniformMatrix4fv(glGetUniformLocation(pipelinevox.shaderProgram, "model"), 1, GL_TRUE,tr.identity()) #tr.uniformScale(3))
        if controller.a:
            pipelinevox.drawShape(gpu_surface0)
        if controller.b:
            pipelinevox.drawShape(gpu_surface1)
        if controller.c:
            pipelinevox.drawShape(gpu_surface2)
        
        

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
