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
