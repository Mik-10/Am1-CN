"""
========================
HITO 6
========================
Lagrangianos y su estabilidad

Objetivos: integrar y analizar sistemas de 3 cuerpos restringidos

Física del problema:
- 3 masas interactuando gravitatoriamente
- Cada cuerpo tiene posición r_i y velocidad v_i
- Fuerza entre i y j: F_ij = -G*m_i*m_j*(r_i - r_j)/|r_i - r_j|^3
- Sistema hamiltoniano -> conserva energía y momento total

CONFIGURACIÓN:
- El esquema temporal se selecciona globalmente al inicio (variable ESQUEMA_TEMPORAL)
- Esquemas disponibles: Euler, Inverse_Euler, Crank_Nicolson, RK4, Leap_Frog, implementar RUNGE KUTTA EMBEBIDO DE ALTO ORDEN
- Leap_Frog se detecta automáticamente y activa el modo correspondiente


PENDIENTES!!!
- Mapas de estabilidad en el plano de fases cerca de Lagrangianos
"""

from problems import crtbp_lagrange_points, crtbp_rhs
from Stability import jacobian_numerical
from Temporal_Schemes import RK45, RK4, RK89
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import os

def classify_stability(evals, tol=1e-8):
    """
    Clasifica estabilidad:
    - 'estable (centro)' si todas las partes reales ~ 0
    - 'inestable (silla)' si alguna parte real > 0 o < 0 con pares de signo
    """
    re = np.real(evals)
    if np.all(np.abs(re) < tol):
        return "estable (centro)"
    else:
        return "inestable (silla)"

def run_hito6_lagrange_stability(mu=0.012277471):
    """
    Determina estabilidad lineal de L1-L5 en CRTBP (plano, marco rotante).
    Usa jacobiano numérico de F en cada punto.
    """
    print("="*60)
    print("HITO 6: Estabilidad de puntos de Lagrange (CRTBP)")
    print(f"mu = {mu}")
    print("-"*60)
    pts = crtbp_lagrange_points(mu=mu)

    def F(U, t):
        # Empaqueta RHS con parámetro mu
        return crtbp_rhs(U, t, mu=mu)

    for name in ["L1", "L2", "L3", "L4", "L5"]:
        xy = pts[name]
        # Estado en reposo en el marco rotante (vx=vy=0)
        U_eq = np.array([xy[0], xy[1], 0.0, 0.0])
        J = jacobian_numerical(F, U_eq, t=0.0, h=1e-8)
        evals = np.linalg.eigvals(J)
        cls = classify_stability(evals)
        print(f"{name}: x={xy[0]:.8f}, y={xy[1]:.8f}")
        print(f"  autovalores: {', '.join(f'{ev.real:+.3e}{ev.imag:+.3e}i' for ev in evals)}")
        print(f"  clasificación: {cls}")
    print("="*60)
    
    run_hito6_plot_lagrange()
    
def run_hito6_plot_lagrange(mu=0.012277471, save_path=None):
    """
    Grafica L1-L5 y las circunferencias grises translúcidas
    solo para L3, L4 y L5. Lagrangianos en rosa con etiquetas.
    """
    # Crear carpeta de salida si no existe
    output_dir = os.path.join(os.path.dirname(__file__), "Salidas Hito 6")
    os.makedirs(output_dir, exist_ok=True)
    if save_path is None:
        save_path = os.path.join(output_dir, 'lagrangianos.png')

    pts = crtbp_lagrange_points(mu=mu)
    x1, x2 = -mu, 1 - mu

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([x1, x2], [0, 0], 'ko', ms=6)

    # Dibujar circunferencias únicamente para L3, L4, L5
    for name in ["L3", "L4", "L5"]:
        x, y = pts[name]
        r1 = np.sqrt((x + mu)**2 + y**2)
        r2 = np.sqrt((x - 1 + mu)**2 + y**2)
        c1 = Circle((x1, 0), r1, facecolor=(0., 0., 0., 0.), edgecolor='gray', linewidth=1.0)
        c2 = Circle((x2, 0), r2, facecolor=(0., 0., 0., 0.), edgecolor='gray', linewidth=1.0)
        ax.add_patch(c1); ax.add_patch(c2)

    # Marcar todos los puntos L1-L5 en rosa con etiquetas
    for name in ["L1", "L2", "L3", "L4", "L5"]:
        x, y = pts[name]
        ax.plot(x, y, 'o', color='#ff4fa3', ms=7)
        ax.text(x + 0.02, y + 0.02, name, color='#ff4fa3', fontsize=10, weight='bold')

    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.set_title('Lagrangianos y circunferencias de intersección (solo L3–L5)')
    ax.grid(True, alpha=0.2)
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.2, 1.2)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Figura guardada en: {save_path}")

def run_hito6_propagate_near_lagrange(name='L1', mu=0.012277471, dt=0.01, t_span=(0.0, 10.0), perturb=np.array([1e-4, 0.0, 0.0, 0.0]), scheme=RK45, save_path=None):
    """
    Propaga el movimiento cercano a un punto lagrangiano (por defecto L1, inestable).
    - name: 'L1'|'L2'|'L3'|'L4'|'L5'
    - mu: parámetro de masa reducido
    - dt: paso temporal
    - t_span: intervalo temporal
    - perturb: perturbación inicial aplicada a [x,y,vx,vy]
    """
    # Crear carpeta de salida si no existe
    output_dir = os.path.join(os.path.dirname(__file__), "Salidas Hito 6")
    os.makedirs(output_dir, exist_ok=True)
    if save_path is None:
        save_path = os.path.join(output_dir, f'Trayectoria_prox_a_{name}_{scheme.__name__}.png')

    pts = crtbp_lagrange_points(mu=mu)
    if name not in pts:
        raise ValueError("Nombre de lagrangiano inválido")

    # Estado de equilibrio en el marco rotante + pequeña perturbación
    if name == 'L4' or name == 'L5':
        perturb = np.array([1e-2, 1e-2, 0.0, 0.0])  # Perturbación en x e y para L4 y L5
    x, y = pts[name]
    U0 = np.array([x, y, 0.0, 0.0]) + perturb

    def F(U, t):
        return crtbp_rhs(U, t, mu=mu)

    from Temporal_Schemes import integrate_cauchy
    t, U = integrate_cauchy(scheme, U0, t_span, dt, F)

    # Gráfico
    fig, ax = plt.subplots(figsize=(8, 6))
    x1, x2 = -mu, 1 - mu
    ax.plot([x1, x2], [0, 0], 'ko', ms=6, label='Primarios')
    ax.plot(U[:, 0], U[:, 1], '-', color='#1f77b4', lw=1.8, label='Trayectoria')

    # Marcar lagrangianos
    for nm in ["L1", "L2", "L3", "L4", "L5"]:
        xx, yy = pts[nm]
        ax.plot(xx, yy, 'o', color='#ff4fa3', ms=7)
        ax.text(xx + 0.02, yy + 0.02, nm, color='#ff4fa3', fontsize=10, weight='bold')

    # Ajustar marco al contenido (trayectoria + primarios + lagrangianos) con margen
    xs = np.concatenate([U[:, 0], np.array([x1, x2]), np.array([pts[n][0] for n in ["L1","L2","L3","L4","L5"]])])
    ys = np.concatenate([U[:, 1], np.array([0.0, 0.0]), np.array([pts[n][1] for n in ["L1","L2","L3","L4","L5"]])])
    xmin, xmax = np.min(xs), np.max(xs)
    ymin, ymax = np.min(ys), np.max(ys)
    # Margen proporcional al tamaño del contenido
    dx = xmax - xmin; dy = ymax - ymin
    pad_x = max(0.05, 0.08 * dx)
    pad_y = max(0.05, 0.08 * dy)
    ax.set_xlim(xmin - pad_x, xmax + pad_x)
    ax.set_ylim(ymin - pad_y, ymax + pad_y)

    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.set_title(f'Propagación cerca de {name} (CRTBP, mu={mu}, dt={dt}, t_span={t_span[1]})')
    ax.grid(True, alpha=0.2)
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Figura guardada en: {save_path}")

if __name__ == "__main__":
    run_hito6_lagrange_stability()
    # Ejemplo: propagar cerca de L1 (inestable)
    for name in ["L1", "L2", "L3", "L4", "L5"]:
        run_hito6_propagate_near_lagrange(name=name, dt=0.01, t_span=(0.0, 50.0), scheme=RK45)