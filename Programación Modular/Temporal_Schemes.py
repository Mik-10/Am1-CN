# ==============================================================================
# ESQUEMAS TEMPORALES VISTOS EN CLASE - INTEGRACIÓN DE EDOs
# ==============================================================================
from scipy.optimize import fsolve
import numpy as np

# ------------------------------------------------------------------------------
# 1. MÉTODO DE EULER
# ------------------------------------------------------------------------------
def Euler(U, t, dt, F):
    """
    Euler explícito (orden 1).
    Fórmula: U_{n+1} = U_n + dt * F(U_n, t_n)
    Retorna estado avanzado un paso.
    """
    return U + dt * F(U, t)


# ------------------------------------------------------------------------------
# 2. MÉTODO DE CRANK-NICOLSON
# ------------------------------------------------------------------------------
def Crank_Nicolson(U, t, dt, F):
    """
    Crank-Nicolson (implícito, orden 2).
    U_{n+1} = U_n + dt/2 [F(U_n,t_n)+F(U_{n+1},t_{n+1})]
    Se resuelve G(U_{n+1})=0 con fsolve.
    """
    def residual(U_next):
        return U_next - U - dt/2 * (F(U, t) + F(U_next, t + dt))
    U_next_guess = U + dt * F(U, t)
    U_next = fsolve(residual, U_next_guess)
    return U_next


# ------------------------------------------------------------------------------
# 3. MÉTODO RUNGE-KUTTA DE ORDEN 4 (RK4)
# ------------------------------------------------------------------------------
def RK4(U, t, dt, F):
    """
    Runge-Kutta clásico, orden 4.
    Combina 4 evaluaciones para error ~ O(dt^5).
    Retorna U_{n+1}.
    """
    k1 = F(U, t)
    k2 = F(U + dt/2 * k1, t + dt/2)
    k3 = F(U + dt/2 * k2, t + dt/2)
    k4 = F(U + dt * k3, t + dt)
    return U + dt/6 * (k1 + 2*k2 + 2*k3 + k4)


# ------------------------------------------------------------------------------
# 3a. MÉTODO RUNGE-KUTTA DE ORDEN 4(5) - DORMAND–PRINCE (RK45)
# ------------------------------------------------------------------------------
def RK45(U, t, dt, F):
    """
    Runge-Kutta Dormand-Prince 4(5) embebido.
    Retorna U_{n+1} usando la solución de orden 5 (más precisa).
    NOTA: k7 se usa para el cálculo del error (no implementado aquí).
    """
    k1 = F(U, t)
    k2 = F(U + dt * (1/5) * k1, t + dt * (1/5))
    k3 = F(U + dt * (3/40 * k1 + 9/40 * k2), t + dt * (3/10))
    k4 = F(U + dt * (44/45 * k1 - 56/15 * k2 + 32/9 * k3), t + dt * (4/5))
    k5 = F(U + dt * (19372/6561 * k1 - 25360/2187 * k2 + 64448/6561 * k3 - 212/729 * k4), t + dt * (8/9))
    k6 = F(U + dt * (9017/3168 * k1 - 355/33 * k2 + 46732/5247 * k3 + 49/176 * k4 - 5103/18656 * k5), t + dt * 1)
    k7 = F(U + dt * (35/384 * k1 + 500/1113 * k3 + 125/192 * k4 - 2187/6784 * k5 + 11/84 * k6), t + dt * 1)

    # Pesos de orden 5 (solución principal)
    U_next = U + dt * (35/384 * k1 + 500/1113 * k3 + 125/192 * k4 - 2187/6784 * k5 + 11/84 * k6)
    return U_next


# ------------------------------------------------------------------------------
# 3b. MÉTODO RUNGE-KUTTA DE ORDEN 8(9) - DORMAND-PRINCE
# ------------------------------------------------------------------------------
def RK89(U, t, dt, F):
    """
    Runge-Kutta Dormand-Prince 8(9) (orden 8, embebido con orden 9).
    Método de alta precisión con 17 etapas.
    Retorna U_{n+1} con error ~ O(dt^9).
    
    Basado en los coeficientes de Dormand-Prince 8(9).
    """
    # Coeficientes del método (Butcher tableau simplificado)
    # Nodos c
    c = np.array([0, 1/18, 1/12, 1/8, 5/16, 3/8, 59/400, 93/200, 
                  5490023248/9719169821, 13/20, 1201146811/1299019798, 1, 1])
    
    # Matriz A (coeficientes para las etapas intermedias)
    k1 = F(U, t)
    k2 = F(U + dt * k1/18, t + dt*c[1])
    k3 = F(U + dt * (k1/48 + k2/16), t + dt*c[2])
    k4 = F(U + dt * (k1/32 + 3*k2/32), t + dt*c[3])
    k5 = F(U + dt * (5*k1/16 + -75*k2/64 + 75*k3/64), t + dt*c[4])
    k6 = F(U + dt * (3*k1/80 + 3*k4/16 + 3*k5/20), t + dt*c[5])
    k7 = F(U + dt * (29443841*k1/614563906 + 77736538*k3/692538347 
                     - 28693883*k4/1125000000 + 23124283*k5/1800000000 
                     + 1518*k6/234375), t + dt*c[6])
    k8 = F(U + dt * (16016141*k1/946692911 + 61564180*k3/158732637 
                     + 22789713*k4/633445777 + 545815736*k5/2771057229 
                     - 180193667*k6/1043307555 + 39632708*k7/573591083), t + dt*c[7])
    k9 = F(U + dt * (39632708*k1/573591083 - 433636366*k3/683701615 
                     - 421739975*k4/2616292301 + 100302831*k5/723423059 
                     + 790204164*k6/839813087 + 800635310*k7/3783071287), t + dt*c[8])
    k10 = F(U + dt * (246121993*k1/1340847787 - 37695042795*k3/15268766246 
                      - 309121744*k4/1061227803 - 12992083*k5/490766935 
                      + 6005943493*k6/2108947869 + 393006217*k7/1396673457 
                      + 123872331*k8/1001029789), t + dt*c[9])
    k11 = F(U + dt * (-1028468189*k1/846180014 + 8478235783*k3/508512852 
                      + 1311729495*k4/1432422823 - 10304129995*k5/1701304382 
                      - 48777925059*k6/3047939560 + 15336726248*k7/1032824649 
                      - 45442868181*k8/3398467696 + 3065993473*k9/597172653), t + dt*c[10])
    k12 = F(U + dt * (185892177*k1/718116043 - 3185094517*k3/667107341 
                      - 477755414*k4/1098053517 - 703635378*k5/230739211 
                      + 5731566787*k6/1027545527 + 5232866602*k7/850066563 
                      - 4093664535*k8/808688257 + 3962137247*k9/1805957418 
                      + 65686358*k10/487910083), t + dt*c[11])
    k13 = F(U + dt * (403863854*k1/491063109 - 5068492393*k3/434740067 
                      - 411421997*k4/543043805 + 652783627*k5/914296604 
                      + 11173962825*k6/925320556 - 13158990841*k7/6184727034 
                      + 3936647629*k8/1978049680 - 160528059*k9/685178525 
                      + 248638103*k10/1413531060), t + dt*c[12])
    
    # Pesos para orden 8
    b8 = np.array([14005451/335480064, 0, 0, 0, 0, -59238493/1068277825,
                   181606767/758867731, 561292985/797845732, -1041891430/1371343529,
                   760417239/1151165299, 118820643/751138087, -528747749/2220607170, 1/4])
    
    # Calcular solución
    U_next = U + dt * (b8[0]*k1 + b8[5]*k6 + b8[6]*k7 + b8[7]*k8 
                       + b8[8]*k9 + b8[9]*k10 + b8[10]*k11 + b8[11]*k12 + b8[12]*k13)
    
    return U_next


# ------------------------------------------------------------------------------
# 4. MÉTODO DE EULER INVERSO (IMPLÍCITO)
# ------------------------------------------------------------------------------
def Inverse_Euler(U, t, dt, F):
    """
    Euler inverso (implícito, orden 1, amortigua).
    Ecuación: U_{n+1} - U_n - dt F(U_{n+1}, t_{n+1}) = 0
    Se resuelve con fsolve.
    """
    def residual(U_next):
        return U_next - U - dt * F(U_next, t + dt)
    U_next_guess = U + dt * F(U, t)
    U_next = fsolve(residual, U_next_guess)
    return U_next


# ------------------------------------------------------------------------------
# 5. MÉTODO LEAP-FROG (SALTO DE RANA)
# ------------------------------------------------------------------------------
def Leap_Frog(U, U_prev, t, dt, F):
    """
    Leap-Frog (explícito, orden 2, multi-paso).
    Fórmula: U_{n+1} = U_{n-1} + 2*dt*F(U_n, t_n)
    Requiere dos pasos previos: U_n y U_{n-1}.
    
    Parámetros:
    - U: estado actual U_n
    - U_prev: estado previo U_{n-1}
    - t: tiempo actual t_n
    - dt: paso de tiempo
    - F: función que define dU/dt = F(U,t)
    
    Retorna U_{n+1}.
    """
    return U_prev + 2*dt * F(U, t)


# ------------------------------------------------------------------------------
# 6. INTEGRADOR GENERAL DE PROBLEMAS DE CAUCHY
# ------------------------------------------------------------------------------
def integrate_cauchy(scheme, U0, t_span, dt, F, **kwargs):
    """
    Integrador genérico IVP: dU/dt = F(U,t), U(t0)=U0.
    
    Parámetros:
    - scheme: función del esquema temporal scheme(U,t,dt,F) o Leap_Frog
    - U0: condición inicial
    - t_span: (t_initial, t_final)
    - dt: paso de tiempo
    - F: función que define dU/dt = F(U,t)
    - **kwargs: argumentos adicionales (ej. is_leapfrog=True)
    
    Retorna:
    - t_array: array de tiempos
    - U_array: array de estados [n_steps, len(U0)]
    """
    t_initial, t_final = t_span
    n_steps = int((t_final - t_initial) / dt) + 1
    
    t_array = np.linspace(t_initial, t_final, n_steps)
    U_array = np.zeros((n_steps, len(U0)))
    U_array[0, :] = U0
    
    is_leapfrog = kwargs.get('is_leapfrog', False)
    
    if is_leapfrog:
        # Primer paso con Euler para inicializar
        U_array[1, :] = Euler(U_array[0, :], t_array[0], dt, F)
        
        # Pasos siguientes con Leap-Frog
        for i in range(1, n_steps - 1):
            U_array[i+1, :] = scheme(U_array[i, :], U_array[i-1, :], 
                                    t_array[i], dt, F)
    else:
        # Esquemas de un solo paso
        for i in range(n_steps - 1):
            U_array[i+1, :] = scheme(U_array[i, :], t_array[i], dt, F)
    
    return t_array, U_array
