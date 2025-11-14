import numpy as np
from numpy import array, zeros
import matplotlib.pyplot as plt
# Milestone 1 : Prototypes to integrate orbits without functions.
# 1. Write a script to integrate Kepler orbits with an Euler method.
# 2. Write a script to integrate Kepler orbits with a Crank-Nicolson method.
# 3. Write a script to integrate Kepler orbits with a Runge–Kutta fourth order.
# 4. Change time step and plot orbits. Discuss results.

# --- Parámetros de simulación ---
T = 50      # Tiempo total (reducido para ver algunas órbitas)
N = 1000    # Número de pasos
dt = T/N    # Paso de tiempo

# --- Condiciones iniciales ---
# r0: posición inicial, rp0: velocidad inicial (rp0 = r_prime)
r0 = np.array([1.0, 0.0])
rp0 = np.array([0.0, 0.8]) # Velocidad para una órbita elíptica

# --- Arrays para almacenar resultados ---
# U es el vector de estado [x, y, vx, vy]
U = np.zeros((4, N + 1))
U[:, 0] = np.concatenate((r0, rp0))

# --- Definición de la dinámica (Ecuaciones de Movimiento) ---
# F(U) calcula la derivada del vector de estado U' = [vx, vy, ax, ay]
def F(U_state, mu=1.0):
    r_vec = U_state[0:2]
    v_vec = U_state[2:4]
    r_norm = np.linalg.norm(r_vec)
    # Evitar división por cero si r es muy pequeño
    if r_norm < 1e-9:
        accel = np.zeros(2)
    else:
        accel = -mu * r_vec / r_norm**3
    return np.concatenate((v_vec, accel))

# --- Comparación de métodos de integración ---
methods = ['euler', 'crank-nicolson', 'rk4']
results = {}

for method in methods:
    # Reiniciar el vector de estado para cada método
    U = np.zeros((4, N + 1))
    U[:, 0] = np.concatenate((r0, rp0))

    # Bucle de integración
    for n in range(N):
        if method == 'euler':
            # 1. Método de Euler
            U[:, n+1] = U[:, n] + dt * F(U[:, n])

        elif method == 'crank-nicolson':
            # 2. Método de Crank-Nicolson (predictor-corrector)
            U_pred = U[:, n] + dt * F(U[:, n])
            U[:, n+1] = U[:, n] + dt/2 * (F(U[:, n]) + F(U_pred))

        elif method == 'rk4':
            # 3. Método de Runge-Kutta 4
            k1 = F(U[:, n])
            k2 = F(U[:, n] + dt/2 * k1)
            k3 = F(U[:, n] + dt/2 * k2)
            k4 = F(U[:, n] + dt * k3)
            U[:, n+1] = U[:, n] + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
    
    results[method] = U

# --- Visualización Comparativa ---
fig, axs = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle(f'Comparación de Métodos de Integración (dt={dt})', fontsize=16)

for i, method in enumerate(methods):
    U_res = results[method]
    x = U_res[0, :]
    y = U_res[1, :]
    
    axs[i].plot(x, y)
    axs[i].plot(0, 0, 'yo', markersize=10) # Centro de atracción
    axs[i].set_title(method.capitalize())
    axs[i].set_xlabel('x')
    axs[i].set_ylabel('y')
    axs[i].axis('equal')
    axs[i].grid(True)

plt.show()