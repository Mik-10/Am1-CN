"""
HITO 4 - VERSIÓN MODULAR
"""

import numpy as np
import matplotlib.pyplot as plt

from Temporal_Schemes import (
    Euler, Inverse_Euler, Crank_Nicolson, RK4, Leap_Frog, integrate_cauchy
)
from Stability import (
    plot_stability_regions, G_euler, G_inverse_euler, 
    G_crank_nicolson, G_rk4, stable_leapfrog
)
from problems import PROBLEMS, oscillator_energy


# --------------------------------------------------------------------------
# Integración con Leap-Frog (adaptación para integrador genérico)
# --------------------------------------------------------------------------
def integrate_leapfrog_standalone(U0, t_span, dt, F):
    """
    Integración directa con Leap-Frog para el oscilador.
    Usa integrate_cauchy con is_leapfrog=True.
    
    Parámetros:
    - U0: condición inicial [x0, v0]
    - t_span: (t_inicial, t_final)
    - dt: paso temporal
    - F: función F(U, t) que define dU/dt
    
    Retorna:
    - t: array de tiempos
    - U: array de estados [N, 2]
    """
    return integrate_cauchy(Leap_Frog, U0, t_span, dt, F, is_leapfrog=True)


# --------------------------------------------------------------------------
# Análisis de factores de amplificación
# --------------------------------------------------------------------------
def analyze_amplification_factors(dt):
    """
    Calcula y muestra factores de amplificación |G(z)| para z = i*dt.
    
    Parámetros:
    - dt: paso temporal
    """
    z_imag = 1j * dt
    
    print("\nFactores de amplificación |G(z)| para z = i*dt (λ = i):")
    print(f"  dt = {dt}")
    print("-" * 50)
    
    methods = {
        "Euler": G_euler(z_imag),
        "Euler Inverso": G_inverse_euler(z_imag),
        "Crank-Nicolson": G_crank_nicolson(z_imag),
        "RK4": G_rk4(z_imag),
    }
    
    for nombre, G in methods.items():
        amp = abs(G)
        phase = np.angle(G)
        print(f"  {nombre:20s} |G| = {amp:.6f}  ∠G = {phase:.6f}")
    
    # Leap-Frog: análisis especial
    root = np.sqrt(z_imag**2 + 1)
    r1 = z_imag + root
    r2 = z_imag - root
    max_r = max(abs(r1), abs(r2))
    stable = (abs(r1) <= 1) and (abs(r2) <= 1)
    print(f"  {'Leap-Frog':20s} max|r| = {max_r:.6f}  estable = {stable}")
    print("-" * 50)


# --------------------------------------------------------------------------
# Estimación de frecuencia numérica
# --------------------------------------------------------------------------
def estimate_frequency(t, x, nombre_metodo):
    """
    Estima frecuencia numérica mediante cruces por cero ascendentes.
    
    Parámetros:
    - t: array de tiempos
    - x: array de posiciones
    - nombre_metodo: nombre del método (para print)
    
    Retorna:
    - omega_num: frecuencia angular numérica estimada
    """
    s = np.sign(x)
    idx = np.where((s[1:] - s[:-1]) > 0)[0]
    
    if len(idx) > 5:
        tiempos = t[idx]
        periodos = np.diff(tiempos)
        T_mean = np.mean(periodos)
        omega_num = 2 * np.pi / T_mean
        error_omega = omega_num - 1.0
        print(f"  {nombre_metodo:20s} ω_num = {omega_num:.6f}  error = {error_omega:+.2e}")
        return omega_num
    else:
        print(f"  {nombre_metodo:20s} insuficientes cruces para estimar")
        return None


# --------------------------------------------------------------------------
# Ejecución principal del Hito 4
# --------------------------------------------------------------------------
def run_hito4():
    print("=" * 70)
    print("HITO 4: OSCILADOR ARMÓNICO - ESTABILIDAD ABSOLUTA")
    print("=" * 70)
    
    # Configuración del problema
    prob = PROBLEMS['oscillator']
    F = prob['rhs']
    U0 = prob['U0']
    
    # Periodo exacto T = 2π, integración larga para ver deriva
    T = 2 * np.pi
    t_span = (0.0, 20 * T)  # 20 periodos
    dt = 0.05
    
    print(f"\nConfiguración:")
    print(f"  Condición inicial: x(0) = {U0[0]}, v(0) = {U0[1]}")
    print(f"  Periodo teórico: T = {T:.4f}")
    print(f"  Tiempo final: t_f = {t_span[1]:.2f} ({t_span[1]/T:.1f} periodos)")
    print(f"  Paso temporal: dt = {dt}")
    print(f"  Energía teórica: E_0 = 0.5")
    
    # 1) Generar regiones de estabilidad
    print("\n[1] Generando regiones de estabilidad...")
    fig_stability = plot_stability_regions(save_path='regiones_estabilidad.png')
    plt.close(fig_stability)
    
    # 2) Análisis de factores de amplificación
    print("\n[2] Análisis de factores de amplificación")
    analyze_amplification_factors(dt)
    
    # 3) Integración con esquemas de un paso
    print("\n[3] Integrando con esquemas de un paso...")
    schemes = {
        "Euler": Euler,
        "Euler Inverso": Inverse_Euler,
        "Crank-Nicolson": Crank_Nicolson,
        "RK4": RK4
    }
    
    resultados = {}
    for nombre, func in schemes.items():
        t, U = integrate_cauchy(func, U0, t_span, dt, F)
        resultados[nombre] = (t, U)
        print(f"  {nombre}: completado ({len(t)} puntos)")
    
    # 4) Integración con Leap-Frog
    print("\n[4] Integrando con Leap-Frog...")
    t_LF, U_LF = integrate_leapfrog_standalone(U0, t_span, dt, F)
    resultados["Leap-Frog"] = (t_LF, U_LF)
    print(f"  Leap-Frog: completado ({len(t_LF)} puntos)")
    
    # 5) Análisis de energía
    print("\n[5] Análisis de conservación de energía")
    print("-" * 70)
    print(f"  {'Método':20s} {'max|ΔE/E₀|':>15s} {'ΔE/E₀ final':>15s}")
    print("-" * 70)
    
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    for nombre, (t, U) in resultados.items():
        x = U[:, 0]
        v = U[:, 1]
        E = oscillator_energy(U, omega=1.0)
        E0 = E[0]
        err_rel = (E - E0) / E0
        
        # Gráficos
        ax1.plot(t, x, label=nombre, alpha=0.8)
        ax2.plot(t, err_rel, label=nombre, alpha=0.8)
        
        # Estadísticas
        max_err = np.max(np.abs(err_rel))
        final_err = err_rel[-1]
        print(f"  {nombre:20s} {max_err:15.2e} {final_err:15.2e}")
    
    print("-" * 70)
    
    # Configurar gráficos
    ax1.set_title("Posición x(t) - Oscilador armónico lineal", fontsize=12)
    ax1.set_xlabel("Tiempo (t)")
    ax1.set_ylabel("Posición x")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')
    
    ax2.set_title("Error relativo de energía ΔE/E₀", fontsize=12)
    ax2.set_xlabel("Tiempo (t)")
    ax2.set_ylabel("ΔE/E₀")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best')
    
    fig1.tight_layout()
    fig1.savefig("oscilador_metodos.png", dpi=150, bbox_inches='tight')
    plt.close(fig1)
    print("\n[6] Figura guardada: oscilador_metodos.png")
    
    # 6) Estimación de frecuencia numérica
    print("\n[7] Estimación de frecuencia numérica (ω teórico = 1.0)")
    print("-" * 70)
    for nombre, (t, U) in resultados.items():
        x = U[:, 0]
        estimate_frequency(t, x, nombre)
    print("-" * 70)
    
    # 7) Conclusiones
    print("\n" + "=" * 70)
    print("CONCLUSIONES - HITO 4")
    print("=" * 70)
    print("""
1. ESTABILIDAD ABSOLUTA:
   - Euler: |G| > 1 → energía crece (inestable para oscilador).
   - Euler Inverso: |G| < 1 → energía decae (amortiguamiento numérico).
   - Crank-Nicolson: |G| = 1 → amplitud neutra (conserva norma).
   - RK4: aproxima e^(i*dt) → muy estable en amplitud y fase.
   - Leap-Frog: dt < 2 → estable, conserva energía casi perfectamente.

2. CONSERVACIÓN DE ENERGÍA:
   - Leap-Frog: mejor conservación (método simpléctico).
   - RK4: buena conservación por alta precisión.
   - Crank-Nicolson: conservación aceptable (implícito).
   - Euler: divergencia energética (crece exponencialmente).
   - Euler Inverso: decaimiento energético (disipativo).

3. PRECISIÓN EN FRECUENCIA:
   - RK4: mejor aproximación a ω = 1.
   - Crank-Nicolson y Leap-Frog: errores de fase pequeños.
   - Euler y Euler Inverso: errores de fase significativos.

4. RECOMENDACIONES:
   - Sistemas conservativos (Hamiltoniano): Leap-Frog, RK4.
   - Sistemas rígidos (stiff): Euler Inverso, Crank-Nicolson.
   - Balance precisión/coste: RK4 (versátil).
   - Integración larga conservativa: Leap-Frog (simpléctico).
    """)
    print("=" * 70)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
if __name__ == '__main__':
    run_hito4()
