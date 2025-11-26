# ==============================================================================
# ANÁLISIS DE ESTABILIDAD DE ESQUEMAS TEMPORALES
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# ------------------------------------------------------------------------------
# FACTORES DE AMPLIFICACIÓN G(z) PARA ECUACIÓN TEST y' = λy
# z = λ*dt (número complejo)
# ------------------------------------------------------------------------------

def G_euler(z):
    """Factor de amplificación Euler explícito: G(z) = 1 + z"""
    return 1 + z


def G_inverse_euler(z):
    """Factor de amplificación Euler inverso: G(z) = 1/(1-z)"""
    return 1 / (1 - z)


def G_crank_nicolson(z):
    """Factor de amplificación Crank-Nicolson: G(z) = (1+z/2)/(1-z/2)"""
    return (1 + z/2) / (1 - z/2)


def G_rk4(z):
    """Factor de amplificación RK4: polinomio de orden 4"""
    return 1 + z + z**2/2 + z**3/6 + z**4/24


def stable_leapfrog(z):
    """
    Estabilidad de Leap-Frog.
    Ecuación característica: r^2 - 2zr - 1 = 0
    Raíces: r = z ± sqrt(z^2 + 1)
    Estable si max(|r1|, |r2|) <= 1
    """
    root = np.sqrt(z**2 + 1)
    r1 = z + root
    r2 = z - root
    return (np.abs(r1) <= 1) & (np.abs(r2) <= 1)


# ------------------------------------------------------------------------------
# CÁLCULO DEL JACOBIANO
# ------------------------------------------------------------------------------

def jacobian_numerical(F, U, t, h=1e-6):
    """
    Calcula el jacobiano de F(U,t) mediante diferencias finitas.
    
    Parámetros:
    - F: función F(U,t)
    - U: punto donde evaluar
    - t: tiempo
    - h: paso para diferencias finitas
    
    Retorna:
    - J: matriz jacobiana [n x n]
    """
    n = len(U)
    J = np.zeros((n, n))
    F0 = F(U, t)
    
    for j in range(n):
        U_pert = U.copy()
        U_pert[j] += h
        F_pert = F(U_pert, t)
        J[:, j] = (F_pert - F0) / h
    
    return J


def spectral_radius(J):
    """
    Calcula el radio espectral (máximo autovalor en módulo).
    
    Parámetros:
    - J: matriz jacobiana
    
    Retorna:
    - rho: radio espectral
    - eigenvalues: autovalores
    """
    eigenvalues = np.linalg.eigvals(J)
    rho = np.max(np.abs(eigenvalues))
    return rho, eigenvalues


# ------------------------------------------------------------------------------
# REGIONES DE ESTABILIDAD
# ------------------------------------------------------------------------------

def plot_stability_regions(save_path='regiones_estabilidad.png'):
    """
    Genera gráficos de regiones de estabilidad |G(z)| <= 1.
    Región estable en cyan, inestable en magenta.
    """
    # Malla en plano complejo
    re = np.linspace(-4, 2, 600)
    im = np.linspace(-3, 3, 600)
    R, I = np.meshgrid(re, im)
    Z = R + 1j * I
    
    # Métodos a analizar
    methods = [
        ("Euler", lambda z: np.abs(G_euler(z)) <= 1),
        ("Euler Inverso", lambda z: np.abs(G_inverse_euler(z)) <= 1),
        ("Crank-Nicolson", lambda z: np.abs(G_crank_nicolson(z)) <= 1),
        ("RK4", lambda z: np.abs(G_rk4(z)) <= 1),
        ("Leap-Frog", stable_leapfrog)
    ]
    
    # Configurar subplots
    cols = 3
    rows = 2
    fig, axes = plt.subplots(rows, cols, figsize=(14, 9))
    axes = axes.ravel()
    
    # Colormap: magenta (inestable), cyan (estable)
    cmap = ListedColormap(["#fc77db", "#54e5f8"])
    cf_ref = None
    
    for ax, (name, criterion) in zip(axes, methods):
        mask = criterion(Z).astype(int)
        cf_ref = ax.pcolormesh(R, I, mask, cmap=cmap, vmin=0, vmax=1, 
                               shading='nearest')
        ax.set_title(f"Estabilidad: {name}")
        ax.set_xlabel("Re(z)")
        ax.set_ylabel("Im(z)")
        ax.axhline(0, color='k', linewidth=0.5)
        ax.axvline(0, color='k', linewidth=0.5)
        
        # Marcar puntos z = i*dt típicos (oscilador)
        for dt_val in [0.05, 0.1, 0.2, 0.5, 1.0]:
            ax.plot(0, dt_val, 'ro', ms=3)
            ax.plot(0, -dt_val, 'ro', ms=3)
    
    # Ocultar subplot sobrante
    for ax in axes[len(methods):]:
        ax.axis('off')
    
    # Colorbar horizontal
    if cf_ref is not None:
        fig.subplots_adjust(bottom=0.12, hspace=0.35, wspace=0.3)
        cbar_ax = fig.add_axes([0.15, 0.04, 0.7, 0.03])
        cbar = fig.colorbar(cf_ref, cax=cbar_ax, orientation='horizontal')
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(["Inestable", "Estable"])
        cbar_ax.set_xlabel("|G(z)| ≤ 1")
    
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Regiones de estabilidad guardadas en: {save_path}")
    return fig


# ------------------------------------------------------------------------------
# ANÁLISIS DE CONVERGENCIA
# ------------------------------------------------------------------------------

def convergence_rate(scheme, F, U0, t_span, dt_values, U_exact=None, **kwargs):
    """
    Calcula tasa de convergencia de un esquema temporal.
    
    Parámetros:
    - scheme: función del esquema temporal
    - F: función que define dU/dt = F(U,t)
    - U0: condición inicial
    - t_span: (t0, tf)
    - dt_values: lista de pasos temporales
    - U_exact: función solución exacta U_exact(t) (opcional)
    - **kwargs: argumentos para integrate_cauchy
    
    Retorna:
    - errors: array de errores
    - rates: array de tasas de convergencia
    """
    from Temporal_Schemes import integrate_cauchy
    
    errors = []
    
    for dt in dt_values:
        t, U = integrate_cauchy(scheme, U0, t_span, dt, F, **kwargs)
        
        if U_exact is not None:
            # Error con solución exacta
            error = np.linalg.norm(U[-1] - U_exact(t[-1]))
        else:
            # Error por Richardson (comparar con dt/2)
            dt_refined = dt / 2
            t_ref, U_ref = integrate_cauchy(scheme, U0, t_span, 
                                           dt_refined, F, **kwargs)
            error = np.linalg.norm(U[-1] - U_ref[-1])
        
        errors.append(error)
    
    errors = np.array(errors)
    rates = []
    
    # Calcular tasas: log(E_i/E_{i+1}) / log(dt_i/dt_{i+1})
    for i in range(len(errors) - 1):
        if errors[i+1] > 0:
            rate = np.log(errors[i] / errors[i+1]) / \
                   np.log(dt_values[i] / dt_values[i+1])
            rates.append(rate)
    
    return errors, np.array(rates)


# ------------------------------------------------------------------------------
# GRÁFICOS DE CONVERGENCIA
# ------------------------------------------------------------------------------

def plot_convergence(results_dict, dt_values, save_path='convergencia.png'):
    """
    Grafica convergencia para múltiples esquemas.
    
    Parámetros:
    - results_dict: {nombre: (errors, rates)}
    - dt_values: array de pasos temporales
    - save_path: ruta para guardar figura
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Errores vs dt (escala log-log)
    ax1.set_title('Convergencia de esquemas temporales')
    for name, (errors, rates) in results_dict.items():
        ax1.loglog(dt_values, errors, 'o-', label=name, linewidth=2, 
                   markersize=8)
    
    ax1.set_xlabel('Paso temporal (dt)')
    ax1.set_ylabel('Error')
    ax1.legend()
    ax1.grid(True, alpha=0.3, which='both')
    
    # Tasas de convergencia
    ax2.set_title('Tasas de convergencia')
    for name, (errors, rates) in results_dict.items():
        if len(rates) > 0:
            dt_mid = np.sqrt(dt_values[:-1] * dt_values[1:])
            ax2.semilogx(dt_mid, rates, 'o-', label=name, linewidth=2, 
                        markersize=8)
    
    ax2.set_xlabel('Paso temporal (dt)')
    ax2.set_ylabel('Orden de convergencia')
    ax2.axhline(1, color='k', linestyle='--', alpha=0.3, label='Orden 1')
    ax2.axhline(2, color='k', linestyle='--', alpha=0.3, label='Orden 2')
    ax2.axhline(4, color='k', linestyle='--', alpha=0.3, label='Orden 4')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Gráficos de convergencia guardados en: {save_path}")
    return fig
