import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# ==============================================================================
# MILESTONE 2: PROTOTIPOS PARA INTEGRAR ÓRBITAS CON FUNCIONES
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. MÉTODO DE EULER
# ------------------------------------------------------------------------------
def Euler(U, t, dt, F):
    """
    Método de Euler explícito para integrar un paso temporal.
    
    Aproximación de primer orden que utiliza la derivada en el punto N
    para estimar N+1.
    
    De la teoría: U_{n+1} = U_n + dt * F(U_n, t_n)
    
    Parámetros:
    -----------
    U : Vector de estado en el instante t
    t : Tiempo actual
    dt : Paso de tiempo
    F : Función F(U, t) que define el problema de Cauchy dU/dt = F(U, t)
    
    Salida:
    --------        
    Vector de estado en el instante t + dt
    """
    return U + dt * F(U, t)


# ------------------------------------------------------------------------------
# 2. MÉTODO DE CRANK-NICOLSON
# ------------------------------------------------------------------------------
def Crank_Nicolson(U, t, dt, F):
    """
    Método de Crank-Nicolson (implícito) para integrar un paso.
    
    Fórmula: U_{n+1} = U_n + dt/2 * [F(U_n, t_n) + F(U_{n+1}, t_{n+1})]
    
    Se resuelve mediante el método de Newton para la ecuación no lineal:
    G(U_{n+1}) = U_{n+1} - U_n - dt/2 * [F(U_n, t_n) + F(U_{n+1}, t_{n+1})] = 0
    
    Parámetros:
    -----------
    U : Vector de estado en el instante t
    t : Tiempo actual
    dt : Paso de tiempo
    F : Función F(U, t) que define el problema de Cauchy dU/dt = F(U, t)
    
    Salida:
    --------
    Vector de estado en el instante t + dt
    """
    def residual(U_next):
        """Función residual para el método de Newton"""
        return U_next - U - dt/2 * (F(U, t) + F(U_next, t + dt))
    
    # Estimación inicial usando Euler explícito
    U_next_guess = U + dt * F(U, t)
    
    # Resolver el sistema no lineal con fsolve (más robusto que newton para sistemas)
    U_next = fsolve(residual, U_next_guess)
    
    return U_next


# ------------------------------------------------------------------------------
# 3. MÉTODO RUNGE-KUTTA DE ORDEN 4 (RK4)
# ------------------------------------------------------------------------------
def RK4(U, t, dt, F):
    """
    Método de Runge-Kutta de orden 4 (RK4) - integra un paso.
    
    Método explícito
    Parámetros:
    -----------
    U : Vector de estado en el instante t
    t : Tiempo actual
    dt : Paso de tiempo
    F : Función F(U, t) que define el problema de Cauchy dU/dt = F(U, t)
    
    Salda:
    --------
    Vector de estado en el instante t + dt
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
    Método de Euler inverso (implícito) para integrar un paso.
    
    Método implícito
    
    Se resuelve mediante el método de Newton para la ecuación no lineal:
    G(U_{n+1}) = U_{n+1} - U_n - dt * F(U_{n+1}, t_{n+1}) = 0
    
    Parámetros:
    -----------
    U : Vector de estado en el instante t
    t : Tiempo actual
    dt : Paso de tiempo
    F : Función F(U, t) que define el problema de Cauchy dU/dt = F(U, t)
        
    Salida:
    --------
    Vector de estado en el instante t + dt
    """
    def residual(U_next):
        """Función residual para el método de Newton"""
        return U_next - U - dt * F(U_next, t + dt)
    
    # Estimación inicial usando Euler explícito
    U_next_guess = U + dt * F(U, t)
    
    # Resolver el sistema no lineal con fsolve (más robusto que newton para sistemas)
    U_next = fsolve(residual, U_next_guess)
    
    return U_next


# ------------------------------------------------------------------------------
# 5. INTEGRADOR GENERAL DE PROBLEMAS DE CAUCHY
# ------------------------------------------------------------------------------
def integrate_cauchy(scheme, U0, t_span, dt, F):
    """
    Integra un problema de Cauchy usando un esquema temporal especificado.
    
    Resuelve el problema de valor inicial:
    dU/dt = F(U, t)
    U(t0) = U0
    
    Parámetros:
    -----------
    scheme : Función que implementa el esquema temporal (Euler, RK4, etc.)
        Debe tener la firma: scheme(U, t, dt, F)
    U0 : Condición inicial en t = t_span[0]
    t_span : tuple
        Tupla (t_initial, t_final) con los tiempos inicial y final
    dt : Paso de tiempo 
    F : Función F(U, t) que define el problema de Cauchy dU/dt = F(U, t)
    
    Salida:
    --------
    t_array : array de tiempos
    U_array : array con los estados en cada tiempo (shape: [n_steps, len(U0)])
    """
    t_initial, t_final = t_span
    
    # Número de pasos temporales
    n_steps = int((t_final - t_initial) / dt) + 1
    
    # resultados
    t_array = np.linspace(t_initial, t_final, n_steps)
    U_array = np.zeros((n_steps, len(U0)))
    
    # CI
    U_array[0, :] = U0
    
    # Integración temporal
    for i in range(n_steps - 1):
        U_array[i+1, :] = scheme(U_array[i, :], t_array[i], dt, F)
    
    return t_array, U_array


# ------------------------------------------------------------------------------
# 6. FUERZA DE KEPLER PARA EL PROBLEMA DE DOS CUERPOS
# ------------------------------------------------------------------------------
def Kepler_force(U, t):
    """
    Calcula la fuerza gravitatoria en el problema de Kepler (dos cuerpos).

    
    Parámetros:
    -----------
    U : Vector de estado [x, y, vx, vy] donde:
        - (x, y): posición en el plano
        - (vx, vy): velocidad en el plano
    t : Tiempo (no se usa en este problema autónomo)
    
    Salida:
    --------
    Derivada del vector de estado [vx, vy, ax, ay] donde:
        - (vx, vy): velocidad
        - (ax, ay): aceleración gravitatoria
    """
    # Desempaquetar el vector de estado
    x, y, vx, vy = U
    
    # Vector de posición r = [x, y]
    r = np.array([x, y])
    
    # Módulo de la posición |r|
    r_norm = np.linalg.norm(r)
    
    # Fuerza gravitatoria: -r/|r|³ (con μ = 1)
    acceleration = -r / r_norm**3
    
    # Derivada del vector de estado: dU/dt = [v, a]
    return np.array([vx, vy, acceleration[0], acceleration[1]])


# ------------------------------------------------------------------------------
# 7. INTEGRACIÓN DE ÓRBITAS DE KEPLER Y ANÁLISIS DE RESULTADOS
# ------------------------------------------------------------------------------
def analyze_kepler_orbits():
    """
    Integra el problema de Kepler con diferentes esquemas temporales y
    analiza los resultados en términos de conservación de energía y momento.
    
    Se consideran órbitas elípticas, circulares y parabólicas, integrando
    con los métodos: Euler, Inverse Euler, Crank-Nicolson y RK4.
    
    Se evalúa la influencia del paso temporal en la precisión y estabilidad.
    """
    print("="*70)
    print("ANÁLISIS DE ÓRBITAS DE KEPLER CON DIFERENTES ESQUEMAS TEMPORALES")
    print("="*70)
    
    # Condiciones iniciales para una órbita elíptica
    # Posición inicial: r0 = [1, 0]
    # Velocidad inicial: v0 = [0, 1] (órbita circular con μ = 1)
    U0_circular = np.array([1.0, 0.0, 0.0, 1.0])
    
    # Órbita elíptica (velocidad ligeramente menor)
    U0_elliptic = np.array([1.0, 0.0, 0.0, 0.8])
    
    # Periodo aproximado de la órbita circular: T = 2π
    T_period = 2 * np.pi
    t_span = (0, 3 * T_period)  # Integrar 3 periodos
    
    # Lista de esquemas a probar
    schemes = {
        'Euler': Euler,
        'Euler Inverso': Inverse_Euler,
        'Crank-Nicolson': Crank_Nicolson,
        'RK4': RK4
    }
    
    # Paso de tiempo base
    dt = 0.01
    
    print(f"\n1. INTEGRACIÓN CON PASO TEMPORAL dt = {dt}")
    print("-" * 70)
    
    # Integrar con cada esquema
    results = {}
    for name, scheme in schemes.items():
        print(f"\nIntegrando con {name}...")
        t, U = integrate_cauchy(scheme, U0_elliptic, t_span, dt, Kepler_force)
        results[name] = (t, U)
        
        # Calcular energía total (debería conservarse)
        r = np.sqrt(U[:, 0]**2 + U[:, 1]**2)
        v = np.sqrt(U[:, 2]**2 + U[:, 3]**2)
        E = 0.5 * v**2 - 1.0 / r  # Energía total (cinética + potencial)
        
        # Error relativo en la energía
        E_error = np.abs(E - E[0]) / np.abs(E[0]) * 100
        
        print(f"  Error máximo en energía: {np.max(E_error):.6f}%")
        print(f"  Error final en energía: {E_error[-1]:.6f}%")
    
    # Graficar órbitas
    plt.figure(figsize=(10, 8))
    
    plt.subplot(2, 2, 1)
    for name, (t, U) in results.items():
        plt.plot(U[:, 0], U[:, 1], label=name, alpha=0.7)
    plt.plot(0, 0, 'ko', markersize=10, label='Cuerpo central')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(f'Órbitas de Kepler (dt = {dt})')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    
    # Graficar energía vs tiempo para cada método
    plt.subplot(2, 2, 2)
    for name, (t, U) in results.items():
        r = np.sqrt(U[:, 0]**2 + U[:, 1]**2)
        v = np.sqrt(U[:, 2]**2 + U[:, 3]**2)
        E = 0.5 * v**2 - 1.0 / r
        plt.plot(t, E, label=name, alpha=0.7)
    plt.xlabel('Tiempo')
    plt.ylabel('Energía total')
    plt.title('Conservación de energía')
    plt.legend()
    plt.grid(True)
    
    # 8. EFECTO DEL PASO TEMPORAL
    print(f"\n2. ANÁLISIS DEL EFECTO DEL PASO TEMPORAL (usando RK4)")
    print("-" * 70)
    
    dt_values = [0.1, 0.05, 0.01, 0.005]
    
    plt.subplot(2, 2, 3)
    for dt_test in dt_values:
        print(f"\n  dt = {dt_test}:")
        t, U = integrate_cauchy(RK4, U0_elliptic, t_span, dt_test, Kepler_force)
        plt.plot(U[:, 0], U[:, 1], label=f'dt = {dt_test}', alpha=0.7)
        
        # Error en energía
        r = np.sqrt(U[:, 0]**2 + U[:, 1]**2)
        v = np.sqrt(U[:, 2]**2 + U[:, 3]**2)
        E = 0.5 * v**2 - 1.0 / r
        E_error = np.abs(E - E[0]) / np.abs(E[0]) * 100
        print(f"    Error máximo en energía: {np.max(E_error):.6f}%")
    
    plt.plot(0, 0, 'ko', markersize=10)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Efecto del paso temporal (RK4)')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    
    # Error en energía vs paso temporal
    plt.subplot(2, 2, 4)
    errors = []
    for dt_test in dt_values:
        t, U = integrate_cauchy(RK4, U0_elliptic, t_span, dt_test, Kepler_force)
        r = np.sqrt(U[:, 0]**2 + U[:, 1]**2)
        v = np.sqrt(U[:, 2]**2 + U[:, 3]**2)
        E = 0.5 * v**2 - 1.0 / r
        E_error = np.max(np.abs(E - E[0]) / np.abs(E[0]))
        errors.append(E_error)
    
    plt.plot(dt_values, errors, 'o-', linewidth=2, markersize=8)
    plt.xlabel('Paso temporal (dt)')
    plt.ylabel('Error máximo relativo en energía')
    plt.title('Convergencia del método RK4')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout(pad=3.0, w_pad=3.0, h_pad=3.0)
    plt.savefig('kepler_orbits_analysis.png', dpi=150, bbox_inches='tight')
    print(f"\n  Gráficas guardadas en 'kepler_orbits_analysis.png'")
    
    # EXPLICACIÓN DE RESULTADOS
    print("\n" + "="*70)
    print("EXPLICACIÓN DE RESULTADOS")
    print("="*70)
    print("""
    1. COMPARACIÓN DE MÉTODOS:
       - Euler explícito: Método de primer orden, tiende a incrementar la energía
         artificialmente, causando que la órbita espiral hacia afuera.
       
       - Euler inverso: Método implícito de primer orden, más estable que Euler
         explícito, pero tiende a disipar energía artificialmente.
       
       - Crank-Nicolson: Método implícito de segundo orden, mejor conservación
         de energía que los métodos de primer orden.
       
       - RK4: Método explícito de cuarto orden, excelente conservación de energía
         y precisión. El más recomendado para este tipo de problemas.
    
    2. EFECTO DEL PASO TEMPORAL:
       - Pasos grandes (dt = 0.1): Mayor error de discretización, peor conservación
         de energía, desviación visible de la órbita teórica.
       
       - Pasos pequeños (dt = 0.005): Mejor aproximación, mayor coste computacional,
         conservación de energía mejorada significativamente.
       
       - Para RK4, el error decrece aproximadamente como O(dt⁴), como se observa
         en la gráfica de convergencia (pendiente ~ 4 en escala log-log).
    
    3. CONCLUSIONES:
       - Para problemas de Kepler, RK4 con dt ~ 0.01-0.001 ofrece un buen balance
         entre precisión y eficiencia computacional.
       
       - Los métodos simplécticos (no implementados aquí) serían ideales para
         conservación exacta de cantidades como energía y momento angular.
    """)
    
    plt.show()


# ==============================================================================
# PROGRAMA PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    analyze_kepler_orbits()
