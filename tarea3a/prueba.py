
import numpy as np

H = 4
W = 3
L = 6
F = 0.01
Ta = 10
Tb = 20
T = 5

h=0.25

nh = int(W / h) - 1
nv = int(H / h) - 1
nz = int(L / h) - 1

def getNI(i,j,k):
    return j * nh + i + nh*nv*k

def getIJK(Ni):
    k = Ni//(nh*nv)
    j=(Ni - nh*nv*k)//nh
    i=(Ni - nh*nv*k)%nh
    return (i,j,k)
print( getNI(0,1,0))
A= np.zeros((64,64))
b=np.zeros((64,))

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

            elif 1<=i and i<= nh-2 and j== nh-1 and 1<= k and k <= nz -2:
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_back] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -T
            
            
            elif j== 0:
                #calentador A:
                if k >= 3*heatL and k <= 4*heatL and i >= heatW and i <=2*heatW:
                    A[p, p_up] = 1
                    A[p, p_left] = 1
                    A[p, p_right] = 1
                    A[p, p_back] = 1
                    A[p, p_front] = 1
                    A[p, p] = -6
                    b[p] = -Ta
            
                #calentador B:
                elif k >= heatL and k <= 2*heatL and i >= heatW and i <=2*heatW:
                    A[p, p_up] = 1
                    A[p, p_left] = 1
                    A[p, p_right] = 1
                    A[p, p_back] = 1
                    A[p, p_front] = 1
                    A[p, p] = -6
                    b[p] = -Tb

                #suelo:

                elif 1 <= i and i <= nh - 2 and 1<= k and k <= nz -2:
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

            #esquina sup,izq,frontal :

            elif (i,j,k) == (0,nv-1,0):
                A[p, p_down] = 1
                A[p, p_right] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -4*h*F - T

            #esquina sup,der,frontal:

            elif (i,j,k) == (nh-1 ,nv-1 ,0):
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -4*h*F - T

            #esquina inf, der, frontal:

            elif (i,j,k) == (nh-1 ,0 ,0):
                A[p, p_up] = 1
                A[p, p_left] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -4*h*F

            #esquina inf, izq, frontal:

            elif (i,j,k) == (0,0,0):
                A[p, p_up] = 1
                A[p, p_right] = 1
                A[p, p_back] = 1
                A[p, p] = -6
                b[p] = -4*h*F

            #esquina sup,izq, back :

            elif (i,j,k) == (0,nv-1,nz-1):
                A[p, p_down] = 1
                A[p, p_right] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -4*h*F - T

            #esquina sup,der,backl:

            elif (i,j,k) == (nh-1 ,nv-1 ,nz-1):
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -4*h*F - T

            #esquina inf, der, back:

            elif (i,j,k) == (nh-1 ,0 ,nz-1):
                A[p, p_up] = 1
                A[p, p_left] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -4*h*F

            #esquina inf, izq, back:

            elif (i,j,k) == (0,0,nz-1):
                A[p, p_up] = 1
                A[p, p_right] = 1
                A[p, p_front] = 1
                A[p, p] = -6
                b[p] = -4*h*F
