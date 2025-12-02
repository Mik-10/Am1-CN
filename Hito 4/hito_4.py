import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# -----------------------------------------------------------------------------
# Importar esquemas del Hito 2
# Ajustar si fuese necesario
# -----------------------------------------------------------------------------
from pathlib import Path
import sys
# Ruta relativa: este archivo -> ../ (Hitos_CN) -> "Hito 2"
hito2_dir = Path(__file__).resolve().parent.parent / "Hito 2"
if str(hito2_dir) not in sys.path:
    sys.path.append(str(hito2_dir))
# Importar esquemas del Hito 2
from Hito_2 import Euler, Inverse_Euler, Crank_Nicolson, RK4, integrate_cauchy

# -----------------------------------------------------------------------------
# Fuerza oscilador: U=[x,v], dU/dt=[v,-x]
# -----------------------------------------------------------------------------
def oscillator_rhs(U, t):
    x, v = U
    return np.array([v, -x])

# Leap-Frog clásico (velocidad en semipasos):
# v_{n+1/2} = v_{n-1/2} + dt * a(x_n), a=-x
# x_{n+1}   = x_n + dt * v_{n+1/2}
# Reconstrucción v_n: v_n = v_{n+1/2} - (dt/2) a(x_{n+1})
# Orden 2, energía casi constante, estable si dt<2.
# -----------------------------------------------------------------------------
def integrate_leapfrog(U0, t_span, dt):
    t0, tf = t_span
    n = int((tf - t0)/dt) + 1
    t = np.linspace(t0, tf, n)
    U = np.zeros((n, 2))
    x0, v0 = U0
    U[0] = U0
    a0 = -x0
    # Inicialización velocidad en semipaso
    v_half = v0 + 0.5 * dt * a0
    x = x0
    for k in range(n-1):
        a_k = -x
        v_half = v_half + dt * a_k          # v_{k+1/2}
        x_next = x + dt * v_half            # x_{k+1}
        a_next = -x_next
        v_next = v_half - 0.5 * dt * a_next # reconstrucción v_{k+1}
        U[k+1] = [x_next, v_next]
        x = x_next
    return t, U

# POLINOMIOS DE ESTABILIDAD - programar genérico para cada esquema, sin usar los poliniomios directamente 
# def Stability_Region(Scheme, N, x0, xf, y0, yf):    
#     x, y = linspace(x0, xf, N), linspace(y0, yf, N)
#     rho = zeros((N, N), dtype=float64)
#     for i in range(N):
#         for j in range(N)
#             w = complex(x[i], y[j])
#             r = Scheme(U = 1., dt = 1., t = 0., F = lambda U, t: w*U)
#             rho[i, j] = abs(r)
#     return x, y, rho
# -----------------------------------------------------------------------------
# Euler: 1+z; Inverso: 1/(1-z); CN: (1+z/2)/(1-z/2); RK4: polinomio orden 4.
# Leap-Frog: raíces r del polinomio r^2 - 2 z r - 1; estable si |r_i|≤1.
# -----------------------------------------------------------------------------
def G_euler(z): return 1 + z
def G_inverse_euler(z): return 1/(1 - z)
def G_crank_nicolson(z): return (1 + z/2)/(1 - z/2)
def G_rk4(z): return 1 + z + z**2/2 + z**3/6 + z**4/24 

# Leap-Frog dos pasos: r^2 - 2 z r - 1 = 0 -> r = z ± sqrt(z**2 + 1)
# Estable si max(|r1|,|r2|) ≤ 1
def stable_leapfrog(z):
    root = np.sqrt(z**2 + 1)
    r1 = z + root
    r2 = z - root
    return (np.abs(r1) <= 1) & (np.abs(r2) <= 1)

# -----------------------------------------------------------------------------
# Construcción y plot de regiones de estabilidad
# -----------------------------------------------------------------------------
def plot_stability_regions():
    # Región |G(z)|≤1 (máscara 0/1); colorbar horizontal.
    # Malla compleja
    re = np.linspace(-4, 2, 600)
    im = np.linspace(-3, 3, 600)
    R, I = np.meshgrid(re, im)
    Z = R + 1j*I

    methods = [
        ("Euler", lambda z: np.abs(G_euler(z)) <= 1),
        ("Euler Inverso", lambda z: np.abs(G_inverse_euler(z)) <= 1),
        ("Crank-Nicolson", lambda z: np.abs(G_crank_nicolson(z)) <= 1),
        ("RK4", lambda z: np.abs(G_rk4(z)) <= 1),
        ("Leap-Frog", stable_leapfrog)
    ]
    cols = 3
    rows = int(np.ceil(len(methods)/cols))
    fig, axes = plt.subplots(rows, cols, figsize=(12, 7))
    axes = axes.ravel()
    cf_ref = None
    cmap = ListedColormap(["#ff69da", "#54e5f8"])  # 0 inestable (magenta pastel), 1 estable (cyan pastel)
    for ax, (name, crit) in zip(axes, methods):
        mask = crit(Z).astype(int)
        cf_ref = ax.pcolormesh(R, I, mask, cmap=cmap, vmin=0, vmax=1, shading='nearest')
        ax.set_title(f"Estabilidad: {name}")
        ax.set_xlabel("Re(z)")
        ax.set_ylabel("Im(z)")
        ax.axhline(0, color='k', linewidth=0.5)
        ax.axvline(0, color='k', linewidth=0.5)
        # Punto z = i dt típico λ= i con dt=0.1,... se muestran como vimos en las clases del martes
        for dt in [0.05,0.1,0.2,0.5,1.0]:
            ax.plot(0, dt, 'ro', ms=3)
            ax.plot(0, -dt, 'ro', ms=3)
    # Borrar gráficos sobrantes
    for ax in axes[len(methods):]:
        ax.axis('off')
    # Colorbar horizontal debajo (no toca primera fila)
    if cf_ref is not None:
        fig.subplots_adjust(bottom=0.16, hspace=0.35, wspace=0.3)
        cbar_ax = fig.add_axes([0.15, 0.08, 0.7, 0.04])  # [left, bottom, width, height]
        cbar = fig.colorbar(cf_ref, cax=cbar_ax, orientation='horizontal')
        cbar.set_ticks([0,1])
        cbar.set_ticklabels(["Inestable (magenta)","Estable (cyan)"])
        cbar_ax.set_xlabel("|G(z)| ≤ 1")
    fig.savefig("regiones_estabilidad.png", dpi=140)

# -----------------------------------------------------------------------------
# Integración comparativa y análisis energía
# -----------------------------------------------------------------------------
def run_oscilador():
    print("="*70)
    print("HITO 4: Oscilador lineal, estabilidad absoluta")
    print("="*70)

    # CI estándar: x(0)=1, v(0)=0 -> energía exacta E=0.5
    U0 = np.array([1.0, 0.0])
    # Periodo exacto T = 2π
    T = 2*np.pi
    t_span = (0.0, 20*T)  # muchos periodos para ver deriva
    dt = 0.05  # paso moderado para evidenciar diferencias
    print("Periodo T={T}, integración hasta {t_span[1]}, dt={dt}")

    # Integraciones con esquemas 1‑paso del Hito 2
    schemes = {
        "Euler": Euler,
        "Euler Inverso": Inverse_Euler,
        "Crank-Nicolson": Crank_Nicolson,
        "RK4": RK4
    }

    resultados = {}
    for nombre, f in schemes.items():
        t, U = integrate_cauchy(f, U0, t_span, dt, oscillator_rhs)
        resultados[nombre] = (t, U)

    # Leap-Frog separado
    t_LF, U_LF = integrate_leapfrog(U0, t_span, dt)
    resultados["Leap-Frog"] = (t_LF, U_LF)

    z_imag = 1j*dt  # λ=i
    print("\nResumen métodos (z = i*dt para test y'=λ y):")
    for nombre in resultados:
        if nombre == "Euler":
            G = G_euler(z_imag)
        elif nombre == "Euler Inverso":
            G = G_inverse_euler(z_imag)
        elif nombre == "Crank-Nicolson":
            G = G_crank_nicolson(z_imag)
        elif nombre == "RK4":
            G = G_rk4(z_imag)
        elif nombre == "Leap-Frog":
            # Para oscilador la condición dt<2, ponemos valor criterio:
            G = np.exp(1j*dt)  # representación ideal (|G|=1)
        amp = abs(G)
        print(f"  {nombre} |G|≈{amp}")

    # Cálculo energía y errores
    fig1, (ax1, ax2) = plt.subplots(2,1, figsize=(10,8))
    for nombre,(t,U) in resultados.items():
        x = U[:,0]; v = U[:,1]
        E = 0.5*(v**2 + x**2)
        err_rel = (E - E[0])/E[0]
        ax1.plot(t, x, label=nombre, alpha=0.8)
        ax2.plot(t, err_rel, label=nombre, alpha=0.8)

        print(f"{nombre:15s}  max|ΔE/E0|={np.max(np.abs(err_rel)):.2e}  final={err_rel[-1]:.2e}")

    ax1.set_title("x(t) oscilador lineal")
    ax1.set_xlabel("t")
    ax1.set_ylabel("x")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.set_title("Error relativo energía")
    ax2.set_xlabel("t")
    ax2.set_ylabel("ΔE/E0")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    fig1.tight_layout()
    fig1.savefig("oscilador_metodos.png", dpi=140)

    # Frecuencia numérica aproximada usando cero-cruces de x(t)
    print("\nFrecuencia numérica estimada (cero-cruces sucesivos):")
    for nombre,(t,U) in resultados.items():
        x = U[:,0]
        # localizar índices donde x cambia de signo (cruces ascendentes)
        s = np.sign(x)
        idx = np.where((s[1:]-s[:-1])>0)[0]
        if len(idx) > 5:
            tiempos = t[idx]
            periodos = np.diff(tiempos)
            omega_num = 2*np.pi/np.mean(periodos)
            print(f"  {nombre:15s} ω_num≈{omega_num:.6f}  error ω≈{omega_num-1:.2e}")
        else:
            print(f"  {nombre:15s} insuficiente para estimar")

    # Regiones de estabilidad
    plot_stability_regions()

    # Explicación final
    print("\n--- Interpretación rápida ---")
    print("Euler: amplificación |G|>1 → energía crece.")
    print("Euler Inverso: |G|<1 → energía decae.")
    print("Crank-Nicolson: |G|=1 → amplitud casi neutra.")
    print("RK4: aproximación e^{i dt} → muy estable en amplitud.")
    print("Leap-Frog: conserva energía (oscilación pequeña), requiere dt<2.")
    print("Conclusión: elegir esquema según equilibrio estabilidad/fase.")

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    run_oscilador()
