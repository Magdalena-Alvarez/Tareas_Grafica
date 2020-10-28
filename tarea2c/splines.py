
import numpy as np
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

def catmulRom(P1,P2,P3,P4):

    G = np.concatenate((P1, P2, P3, P4), axis=1)

    Mcr=1/2 * np.array([
        [0,-1,2,-1],
        [2,0,-5,3],
        [0,1,4,-3],
        [0,0,-1,1]
    ])

    return np.matmul(G,Mcr)

# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
    return curve

def plotCurve(ax, curve, label, color=(0,0,1)):
    
    xs = curve[:, 0]
    ys = curve[:, 1]
    zs = curve[:, 2]
    
    ax.plot(xs, ys, zs, label=label, color=color)

if __name__ == "__main__":
    fig = mpl.figure()
    ax = fig.gca(projection='3d')

    P1=np.array([[-7,-5,2]]).T
    P2=np.array([[-8,-6,5]]).T
    P3=np.array([[8,-6,5]]).T
    P4=np.array([[-6,-5,1]]).T
    P5=np.array([[6,-5,1]]).T
    P6=np.array([[-4,-3,-2]]).T
    P7=np.array([[4,3,-2]]).T
    P8=np.array([[-3,-2,-6]]).T



    GMcr1= catmulRom(P1,P2,P3,P4)

    spline= evalCurve(GMcr1,100)
    plotCurve(ax, spline, "CatmulRom", (1,0,0))

    GMcr2= catmulRom(P2,P3,P4,P5)
    spline1= evalCurve(GMcr2,100)
    plotCurve(ax, spline1, "CatmulRom2", (0,1,0))

    GMcr3= catmulRom(P3,P4,P5,P6)
    spline2= evalCurve(GMcr3,100)
    plotCurve(ax, spline2, "CatmulRom3", (0,0,1))

    GMcr4= catmulRom(P4,P5,P6,P7)
    spline3= evalCurve(GMcr4,100)
    plotCurve(ax, spline3, "CatmulRom4", (1,1,0))

    GMcr5= catmulRom(P5,P6,P7,P8)
    spline4= evalCurve(GMcr5,100)
    plotCurve(ax, spline4, "CatmulRom5", (0,1,1))

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    mpl.show()