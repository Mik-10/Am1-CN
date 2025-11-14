import numpy as np
from numpy import array, zeros
import matplotlib.pyplot as plt

# Milestone 1 : Prototypes to integrate orbits without functions.
# 1. Write a script to integrate Kepler orbits with an Euler method.
# 2. Write a script to integrate Kepler orbits with a Crank-Nicolson method.
# 3. Write a script to integrate Kepler orbits with a Runge–Kutta fourth order.
# 4. Change time step and plot orbits. Discuss results.

# Dado el problema centrado en ejes M1, quedará la resolución de las ecuaciones en 2D
# El vector de estado será U = [r, r'], siendo d/dt(r, r') = (r', r'') = (r', -r/r^3)

# Puesto que se usarán 3 métodos distintos, vamos a hacer un selector
caso = 1

# Parámetros
N = 1000
dt = 10E-3

# Definimos funciones antes, porque python es bien raro
def Kepler(U):
    xp = U[2]; yp = U[3]
    x = U[0]; y = U[1]
    d = np.linalg.norm(U[0:2])
    return array([xp, yp, -x/d**3, -y/d**3])

def Euler(U, dt, F):
    return U + dt*F

# Inicializamos variables y CI
r0 = np.zeros(2)
rp0 = np.zeros(2)

r0[0:2] = [1, 0]
rp0[0:2] = [0, 1]

U = np.zeros((4, N))
U[:, 0] = np.concatenate((r0, rp0))
F = zeros(4)

x = zeros(N); x[0] = r0[0]
y = zeros(N); y[0] = r0[1]

match caso:
    case 1:
        print("Euler Method")
        for n in range(1, N):
            F = Kepler(U[:, n-1])
            U[:, n] = Euler(U[:, n-1], dt, F)
            x[n] = U[0, n]; y[n] = U[1, n]
    case 2:
        print("Crank-Nicolson Method")
    case 3:
        print("Runge-Kutta Method. 4th order")

plt.plot(x, y)
plt.axis('equal')
plt.show()

