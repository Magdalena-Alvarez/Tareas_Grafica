
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from matplotlib import cm
import json
import sys
import scipy.sparse as sci
import scipy.sparse.linalg as ssl

setups= sys.argv[1]

#extraemos los datos del problema:
with open(setups) as A:
    B=json.load(A)


H = B["height"]
W = B["width"]
L = B["lenght"]
F = B["window_loss"]
Ta = B["heater_a"]
Tb = B["heater_b"]
T = B["ambient_temperature"]
filename = B["filename"]

#más setups:

h=0.2
heatL= int(L/(5*h))
heatW = int(W/(3*h))
#número de incógnitas:
nh = int(W / h) - 1
nv = int(H / h) - 1
nz = int(L / h) - 1
print(nh,' ',nv,' ',nz )

#vemos el dominio:

N = nh * nz * nv

def getNI(i,j,k):
    return j * nh + i + nh*nv*k

def getIJK(Ni):
    k = Ni//(nh*nv)
    j=(Ni - nh*nv*k)//nh
    i=(Ni - nh*nv*k)%nh
    return (i,j,k)
#print(getNI(2,2,1))
#print(getNI(15))

"""
# This code is useful to debug the indexation functions above
print("="*10)
print(getK(0,0), getIJ(0))
print(getK(1,0), getIJ(1))
print(getK(0,1), getIJ(2))
print(getK(1,1), getIJ(3))
print("="*10)

import sys
sys.exit(0)
"""

# In this matrix we will write all the coefficients of the unknowns
#A = np.zeros((N,N))

# In this vector we will write all the right side of the equations
b = np.zeros((N,))
A = sci.csc_matrix((N, N))  # We use a sparse matrix in order to spare memory, since it has many 0's


for k in range(0,nz):
    for i in range(0,nh):
        for j in range(0,nv):
            #print('hola')
            p = getNI(i,j,k)

        # We obtain indices of the other coefficients
            p_up = getNI(i, j+1,k)
            p_down = getNI(i, j-1,k)
            p_left = getNI(i-1, j,k)
            p_right = getNI(i+1, j,k)
            p_front = getNI(i,j,k-1)
            p_back = getNI(i,j,k+1)
            #interior:

            if 1 <= i and i <= nh - 2 and 1 <= j and j <= nv - 2 and 1<= k and k <= nz -2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_back] = 1
                A[p,p_front] = 1
                A[p, p] = -6
                b[p] = 0
                #print(A[p,p])

            # tapa:

            elif 1<=i and i<= nh-2 and j== nv-1 and 1<= k and k <= nz -2:
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -T
            
            #calentador A:
            elif j== 0 and  k >= 3*heatL and k <= 4*heatL and i >= heatW and i <=2*heatW:
                A[p, p_up] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -Ta
            
            #calentador B:
            elif j==0 and k >= heatL and k <= 2*heatL and i >= heatW and i <=2*heatW:
                A[p, p_up] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -Tb

            #suelo:

            elif j==0 and 1 <= i and i <= nh - 2 and 1<= k and k <= nz -2:
                A[p, p_up] = 2
                A[p, p_right] = 1
                A[p, p_left] = 1
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = 0

            #lado derecho:

            elif i == nh - 1 and 1 <= j and j <= nv - 2 and k >=1 and k <=nz-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -2 * h * F

            #lado izquierdo:

            elif i == 0 and 1 <= j and j <= nv - 2 and k >=1 and k <=nz-2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] =- 2 * h * F

            #lado frontal:

            elif i >= 1 and i<=nh -2 and 1 <= j and j <= nv - 2 and k ==0:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -2 * h * F

            #lado tracero:

            elif i >= 1 and i<=nh -2 and 1 <= j and j <= nv - 2 and k == nz-1:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = - 2 * h * F

            #lado izq,frontal:
            elif (i,k)==(0,0) and 1<=j and j<=nv -2:
                A[p, p_down] = 1
                A[p, p_up] = 1
                A[p, p_right] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4*h*F

            #lado izq, back:
            elif (i,k)==(0,nz-1) and 1<=j and j<=nv -2:
                A[p, p_down] = 1
                A[p, p_up] = 1
                A[p, p_right] = 2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4*h*F

            #lado der, back:
            elif (i,k)==(nh -1,nz-1) and 1<=j and j<=nv -2:
                A[p, p_down] = 1
                A[p, p_up] = 1
                A[p, p_left] = 2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4*h*F

            #lado der, front:
            elif (i,k)==(nh -1,0) and 1<=j and j<=nv -2:
                A[p, p_down] = 1
                A[p, p_up] = 1
                A[p, p_left] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4*h*F

            #lado sup, front:
            elif j==nv-1 and k == 0 and 1<=i and i<=nh -2:
                A[p, p_down] = 1
                A[p, p_right] = 1
                A[p, p_left] = 1
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = (-2*h*F) - T

            #lado inf, front:
            elif (j,k)==(0,0) and 1<=i and i<=nh -2:
                A[p, p_up] = 2
                A[p, p_right] = 1
                A[p, p_left] = 1
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -2*h*F

            #lado sup, back:
            elif (j,k)==(nv -1,nz-1) and 1<=i and i<=nh -2:
                A[p, p_down] = 1
                A[p, p_right] = 1
                A[p, p_left] = 1
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = (-2*h*F) -T

            #lado inf, back:
            elif (j,k)==(0,nz-1) and 1<=i and i<=nh -2:
                A[p, p_up] = 2
                A[p, p_right] = 1
                A[p, p_left] = 1
                A[p, p_front] =2
                A[p, p] = -6
                b[p] = -2*h*F
            
            #lado sup, izq:
            elif (i,j)==(0,nv -1) and 1<=k and k<=nz -2:
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = (-2*h*F)-T

            #lado sup, der:
            elif (i,j)==(nh-1,nv -1) and 1<=k and k<=nz -2:
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = (-2*h*F) -T

            #lado inf, der:
            elif (i,j)==(nh-1,0) and 1<=k and k<=nz -2:
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -2*h*F

            #lado inf, izq:
            elif (i,j)==(0,0) and 1<=k and k<=nz -2:
                A[p, p_up] = 2
                A[p, p_right] = 2
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -2*h*F

            #esquina sup,izq,frontal :

            elif (i,j,k) == (0,nv-1,0):
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4*h*F - T

            #esquina sup,der,frontal:

            elif (i,j,k) == (nh-1 ,nv-1 ,0):
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4*h*F - T

            #esquina inf, der, frontal:

            elif (i,j,k) == (nh-1 ,0 ,0):
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4*h*F

            #esquina inf, izq, frontal:

            elif (i,j,k) == (0,0,0):
                A[p, p_up] = 2
                A[p, p_right] = 2
                A[p, p_back] = 2
                A[p, p] = -6
                b[p] = -4*h*F

            #esquina sup,izq, back :

            elif (i,j,k) == (0,nv-1,nz-1):
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4*h*F - T

            #esquina sup,der,backl:

            elif (i,j,k) == (nh-1 ,nv-1 ,nz-1):
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_front] =2
                A[p, p] = -6
                b[p] = -4*h*F - T

            #esquina inf, der, back:

            elif (i,j,k) == (nh-1 ,0 ,nz-1):
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4*h*F

            #esquina inf, izq, back:

            elif (i,j,k) == (0,0,nz-1):
                A[p, p_up] = 2
                A[p, p_right] =2
                A[p, p_front] = 2
                A[p, p] = -6
                b[p] = -4*h*F
            else:
                print("Point (" + str(i) + ", " + str(j) + "," + str(k)+") missed!")
                print("Associated point index is " + str(p))
                raise Exception()

#print(A)
#x = np.linalg.solve(A, b)
x = ssl.spsolve(A, b)
print(x)

ux=[]
uy=[]
uz=[]
#u = np.zeros((nh, nz, nv))
matrix=np.zeros((nh,nz,nv))
for l in range(0, N):
        i, j, k = getIJK(l)
        ux+=[i]
        uy+=[k]
        uz+=[j]
        matrix[i,k,j]=x[l]
fig = plt.figure()
ax = plt.axes(projection ='3d')
ax.scatter(ux,uy,uz,c=x,alpha=0.15, s=100, marker='s')
plt.show()
ub = np.zeros((nh + 2, nz + 2, nv + 2))
ub[1:nh + 1, 1:nz + 1, 1:nv + 1] = matrix[:, :, :]

# top 
ub[0:nh + 2,0: nz + 2, nv +1] = T
# botom:
#asumiremos mientras que es 0 la neumann nula:
ub[0:nh+2,0:nz +2,0]=0
#ahora re-rellenamos los calentadores:
ub[heatW:2*heatW+1,heatL:heatL*2+1,0] = Tb
ub[heatW:2*heatW+1,3*heatL:heatL*4+1,0] = Ta
# left
ub[0, 1:nz + 1, 1:nv+1] = 2*h*F
# right
ub[nh + 1, 1:nz + 1,1:nv+1 ] = 2*h*F
#front 
ub[1:nh + 1, 0,1:nv+1 ] = 2*h*F
#back 
ub[1:nh + 1, nz + 1,1:nv+1 ] = 2*h*F
np.save(filename, ub)
