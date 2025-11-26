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
    Runge-Kutta clásico orden 4.
    Combina 4 evaluaciones para error O(dt^5).
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
# 5. INTEGRADOR GENERAL DE PROBLEMAS DE CAUCHY
# ------------------------------------------------------------------------------
def integrate_cauchy(scheme, U0, t_span, dt, F):
    """
    Integrador genérico IVP: dU/dt = F(U,t), U(t0)=U0.
    scheme(U,t,dt,F) avanza un paso.
    Devuelve arrays de tiempos y estados.
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
    RHS problema de dos cuerpos 2D (μ=1).
    Entrada U=[x,y,vx,vy]; salida dU/dt=[vx,vy,ax,ay].
    a = -r/|r|^3.
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
    Comparación de esquemas en órbita elíptica.
    Métricas: órbita y energía vs tiempo; efecto dt.
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
    Resumen métodos:
     Euler: energías crecientes (no conservativo).
     Euler inverso: disipación numérica.
     Crank-Nicolson: buena conservación (orden 2).
     RK4: alta precisión y muy baja deriva energética.
    Convergencia RK4 ~ O(dt^4).
    Recomendación: dt pequeño balanceando coste y precisión.
    Métodos simplécticos (no incluidos) mejorarían conservación larga.
    """)
    
    plt.show()


# ==============================================================================
# PROGRAMA PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    analyze_kepler_orbits()
