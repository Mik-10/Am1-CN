"""
========================
HITO 5 - VERSIÓN MODULAR
========================
Problema de N cuerpos gravitatorios.

Objetivos: integrar y analizar sistemas de N cuerpos bajo interacción gravitatoria mutua.

Física del problema:
- N masas interactuando gravitatoriamente
- Cada cuerpo tiene posición r_i y velocidad v_i
- Fuerza entre i y j: F_ij = -G*m_i*m_j*(r_i - r_j)/|r_i - r_j|^3
- Sistema hamiltoniano -> conserva energía y momento total

CONFIGURACIÓN:
- El esquema temporal se selecciona globalmente al inicio (variable ESQUEMA_TEMPORAL)
- Todos los ejemplos usan el mismo esquema
- Esquemas disponibles: Euler, Inverse_Euler, Crank_Nicolson, RK4, Leap_Frog
- Leap_Frog se detecta automáticamente y activa el modo correspondiente


PENDIENTES!!!
- Revisar Crank-Nicolson
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import os

from Temporal_Schemes import (
    Euler, Inverse_Euler, Crank_Nicolson, RK4, Leap_Frog, integrate_cauchy
)
from problems import (
    nbody_rhs, nbody_energy, nbody_angular_momentum,
    setup_solar_system_simple, setup_three_body_figure8, setup_three_body_dummies
)

# --------------------------------------------------------------------------
# CONFIGURACIÓN GLOBAL: Selección del esquema temporal
# --------------------------------------------------------------------------
# Opciones disponibles: Euler, Inverse_Euler, Crank_Nicolson, RK4, Leap_Frog
ESQUEMA_TEMPORAL = RK4  # <-- CAMBIAR AQUÍ PARA TODOS LOS EJEMPLOS

# Selector global de animación - sólo para el último ejemplo
ANIMAR = False          # <-- CAMBIAR AQUÍ para activar/desactivar animaciones
ANIM_FPS = 5           # Frames por segundo
ANIM_STRIDE = 2         # Submuestreo de frames (1 = todos)

print("="*70)
print(f"CONFIGURACIÓN: Esquema temporal seleccionado = {ESQUEMA_TEMPORAL.__name__}")
if ESQUEMA_TEMPORAL == Leap_Frog:
    print(f"              Modo Leap-Frog: ACTIVADO")
print(f"              Animación: {'ON' if ANIMAR else 'OFF'} (fps={ANIM_FPS}, stride={ANIM_STRIDE})")
if ANIMAR:
    print("              Aviso: generar animaciones puede tardar varios segundos/minutos.")
print("="*70)


# --------------------------------------------------------------------------
# Simulación y visualización
# --------------------------------------------------------------------------
def simulate_nbody(masses, U0, t_span, dt, names, G=1.0, scheme=None, img_prefix="sim", animate=False, anim_fps=30, anim_stride=1):
    """
    Simula el problema de N cuerpos y genera gráficos.
    
    Parámetros:
    - masses
    - U0: condición inicial - ojo con el orden [posicionES..., velocidadES...]
    - t_span: (t0, tf)
    - dt: paso
    - names: nombres de los cuerpos
    - G: cte gravitacional
    - scheme: esquema de integración (si None, usa ESQUEMA_TEMPORAL global)
    
    Retorna:
    - t: array de tiempos
    - U: array de estados
    """
    # Usar esquema global si no se especifica uno
    if scheme is None:
        scheme = ESQUEMA_TEMPORAL
    
    N = len(masses)
    # Crear carpeta de salida
    output_dir = 'Salidas Hito 5'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"SIMULACIÓN DE {N} CUERPOS")
    print(f"{'='*70}")
    print(f"Cuerpos: {', '.join(names)}")
    print(f"Masas: {masses}")
    print(f"Tiempo: {t_span[0]} -> {t_span[1]}")
    print(f"Paso dt = {dt}")
    print(f"Esquema: {scheme.__name__}")
    
    # Integración
    print("\n[1] Integrando ecuaciones de movimiento...")

    def F(U, t):
        return nbody_rhs(U, t, masses, G)

    # Determinar si usar modo Leap-Frog (automático según el esquema)
    isleapfrog = (scheme == Leap_Frog)
    
    t, U = integrate_cauchy(scheme, U0, t_span, dt, F, is_leapfrog=isleapfrog)
    print(f"    Completado: {len(t)} pasos temporales")
    
    # Análisis de conservación
    print("\n[2] Analizando conservación...")
    E = nbody_energy(U, masses, G)
    L = nbody_angular_momentum(U, masses)
    
    E0 = E[0]
    L0_norm = np.linalg.norm(L[0])
    
    dE_rel = (E - E0) / np.abs(E0) if E0 != 0 else E - E0
    dL_norm = np.linalg.norm(L - L[0], axis=1)
    
    print(f"    Energia inicial: E0 = {E0:.6e}")
    print(f"    |L| inicial: {L0_norm:.6e}")
    print(f"    max|dE/E0| = {np.max(np.abs(dE_rel)):.2e}") # Da pistas sobre si se tiene algun error numerico o conceptual
    print(f"    max|dL| = {np.max(dL_norm):.2e}")
    
    # Gráficos
    print("\n[3] Generando gráficos...")

    # Normalizar orientación: (n_steps, state_dim)
    if U.shape[0] != len(t) and U.shape[1] == len(t):
        U_plot = U.T
    else:
        U_plot = U

    # Extracción directa: [posicionES...][velocidadES...]
    N3 = 3 * N
    pos = U_plot[:, :N3].reshape((-1, N, 3))

    # Diagnóstico posiciones
    print("\n    Posiciones extraídas del array U_plot:")
    for i in range(N):
        r_init = pos[0, i]
        r_final = pos[-1, i]
        print(f"      {names[i]:10s}: inicial = [{r_init[0]:7.4f}, {r_init[1]:7.4f}, {r_init[2]:7.4f}]")
        print(f"                  final   = [{r_final[0]:7.4f}, {r_final[1]:7.4f}, {r_final[2]:7.4f}]")

    # Fig 1: trayectorias 3D
    fig1 = plt.figure(figsize=(12, 5))
    ax1 = fig1.add_subplot(121, projection='3d')
    colors = plt.cm.tab10(np.linspace(0, 1, N))
    for i in range(N):
        xi = pos[:, i, 0]; yi = pos[:, i, 1]; zi = pos[:, i, 2]
        ax1.plot(xi, yi, zi, label=names[i], color=colors[i], linewidth=1.5)
        # Posición inicial: círculo hueco
        ax1.scatter(xi[0], yi[0], zi[0], facecolors='none', edgecolors=colors[i], 
                   s=100, linewidths=2, marker='o')
        # Posición final: círculo sólido
        ax1.scatter(xi[-1], yi[-1], zi[-1], color=colors[i], s=50, marker='o')
    ax1.set_xlabel('x'); ax1.set_ylabel('y'); ax1.set_zlabel('z')
    t_total = t_span[1] - t_span[0]
    ax1.set_title(f'Trayectorias: {N} cuerpos | {scheme.__name__} | dt={dt:.0e}, T={t_total:.1f}', weight='bold')
    ax1.legend(); ax1.grid(True, alpha=0.3)

    # Proyección XY
    ax2 = fig1.add_subplot(122)
    for i in range(N):
        xi = pos[:, i, 0]; yi = pos[:, i, 1]
        ax2.plot(xi, yi, label=names[i], color=colors[i], linewidth=1.5)
        # Posición inicial: círculo hueco
        ax2.scatter(xi[0], yi[0], facecolors='none', edgecolors=colors[i], 
                   s=100, linewidths=2, marker='o', zorder=10)
        # Posición final: círculo sólido
        ax2.scatter(xi[-1], yi[-1], color=colors[i], s=50, edgecolor='k', zorder=11)
    ax2.set_xlabel('x'); ax2.set_ylabel('y')
    ax2.set_title(f'Proyección XY | {scheme.__name__} | dt={dt:.0e}, T={t_total:.1f}', weight='bold')
    ax2.legend(); ax2.grid(True, alpha=0.3); ax2.axis('equal')

    plt.tight_layout()
    filepath1 = os.path.join(output_dir, f'{img_prefix}_{scheme.__name__}_trayectorias.png')
    fig1.savefig(filepath1, dpi=150, bbox_inches='tight')
    print(f"    Figura guardada: {filepath1}")

    # Fig 2: conservación
    fig2, (ax3, ax4) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax3.plot(t, dE_rel, 'b-', linewidth=1.5)
    ax3.set_xlabel('Tiempo')
    ax3.set_ylabel('dE/E0')
    ax3.set_title(f'Conservacion de energia | {scheme.__name__} | dt={dt:.0e}, T={t_total:.1f}', weight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(0, color='k', linestyle='--', linewidth=0.8)
    
    ax4.plot(t, dL_norm, 'r-', linewidth=1.5)
    ax4.set_xlabel('Tiempo')
    ax4.set_ylabel('|dL|')
    ax4.set_title(f'Conservacion de momento angular | {scheme.__name__} | dt={dt:.0e}, T={t_total:.1f}', weight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.axhline(0, color='k', linestyle='--', linewidth=0.8)
    
    plt.tight_layout()
    filepath2 = os.path.join(output_dir, f'{img_prefix}_{scheme.__name__}_conservacion.png')
    fig2.savefig(filepath2, dpi=150, bbox_inches='tight')
    print(f"    Figura guardada: {filepath2}")
    
    # Animación opcional
    if animate:
        print("\n[4] Generando animación...")
        try:
            # Prepara datos subsampleados para la animación
            frames_idx = np.arange(0, pos.shape[0], max(1, anim_stride))
            pos_anim = pos[frames_idx]

            fig_anim = plt.figure(figsize=(6, 6))
            ax_anim = fig_anim.add_subplot(111)
            ax_anim.set_xlabel('x'); ax_anim.set_ylabel('y'); ax_anim.axis('equal')
            ax_anim.grid(True, alpha=0.3)
            ax_anim.set_title(f"Animación XY | {scheme.__name__} | dt={dt:.0e}")

            colors = plt.cm.tab10(np.linspace(0, 1, N))
            lines = []
            scatters = []
            for i in range(N):
                line, = ax_anim.plot([], [], color=colors[i], linewidth=1.5, label=names[i])
                scatter = ax_anim.scatter([], [], color=colors[i], s=40)
                lines.append(line)
                scatters.append(scatter)
            ax_anim.legend()

            # Ajustar límites para toda la animación
            x_all = pos_anim[:, :, 0].ravel()
            y_all = pos_anim[:, :, 1].ravel()
            pad = 0.1 * max(1e-8, max(np.ptp(x_all), np.ptp(y_all)))
            ax_anim.set_xlim(np.min(x_all) - pad, np.max(x_all) + pad)
            ax_anim.set_ylim(np.min(y_all) - pad, np.max(y_all) + pad)

            def init():
                for i in range(N):
                    lines[i].set_data([], [])
                return lines

            def update(frame_idx):
                # frame_idx es índice en frames_idx
                k = frame_idx
                for i in range(N):
                    xi = pos_anim[:k+1, i, 0]
                    yi = pos_anim[:k+1, i, 1]
                    lines[i].set_data(xi, yi)
                    scatters[i].set_offsets([pos_anim[k, i, 0], pos_anim[k, i, 1]])
                return lines + scatters

            anim = animation.FuncAnimation(
                fig_anim, update, init_func=init,
                frames=len(frames_idx), interval=1000/anim_fps, blit=True
            )

            output_dir = 'Salidas Hito 5'
            os.makedirs(output_dir, exist_ok=True)
            gif_path = os.path.join(output_dir, f"{img_prefix}_{scheme.__name__}_anim.gif")
            mp4_path = os.path.join(output_dir, f"{img_prefix}_{scheme.__name__}_anim.mp4")

            # Intentar guardar como GIF usando PillowWriter
            saved = False
            try:
                from matplotlib.animation import PillowWriter
                writer = PillowWriter(fps=anim_fps)
                anim.save(gif_path, writer=writer)
                print(f"    Animación GIF guardada: {gif_path}")
                saved = True
            except Exception as e:
                print(f"    Aviso: no se pudo guardar GIF con PillowWriter ({e}).")

            # Fallback a MP4 (requiere ffmpeg instalado)
            if not saved:
                try:
                    Writer = animation.writers['ffmpeg']
                    writer = Writer(fps=anim_fps, metadata=dict(artist='Hito5'), bitrate=1800)
                    anim.save(mp4_path, writer=writer)
                    print(f"    Animación MP4 guardada: {mp4_path}")
                    saved = True
                except Exception as e:
                    print(f"    Aviso: no se pudo guardar MP4 con ffmpeg ({e}).")

            plt.close(fig_anim)
        except Exception as e:
            print(f"    Error generando animación: {e}")

    plt.close('all')
    
    return t, U


# --------------------------------------------------------------------------
# Main - Ejecución del Hito 5
# --------------------------------------------------------------------------
def run_hito5():
    """
    Ejecuta simulaciones del problema de N cuerpos (Hito 5).
    """
    print("=" * 70)
    print("HITO 5: PROBLEMA DE N CUERPOS")
    print("=" * 70)
    
    # Ejemplo 1: Sistema solar simplificado (Sol + Tierra + Júpiter)
    print("\n" + "="*70)
    print("EJEMPLO 1: SISTEMA SOLAR SIMPLIFICADO")
    print("="*70)
    
    masses1, U0_1, t_span1, names1, G1 = setup_solar_system_simple()
    
    # Diagnóstico del vector de estado inicial
    N = len(masses1)
    N3 = 3 * N
    print(f"\nDIAGNÓSTICO U0:")
    print(f"Longitud de U0: {len(U0_1)}")
    print(f"Esperado: {6*N} (3 pos + 3 vel por {N} cuerpos)")
    print(f"\nPosiciones (primeros {N3} elementos):")
    for i in range(N):
        r = U0_1[3*i:3*i+3]
        print(f"  {names1[i]}: r = {r}")
    print(f"\nVelocidades (últimos {N3} elementos):")
    for i in range(N):
        v = U0_1[N3 + 3*i:N3 + 3*i+3]
        print(f"  {names1[i]}: v = {v}")
    print(f"\nConstante G = {G1}")
    
    dt1 = 0.01  # 0.01 años ~ 3.65 días
    
    t1, U1 = simulate_nbody(masses1, U0_1, t_span1, dt1, names1, G1, img_prefix="sistema_solar", animate=ANIMAR, anim_fps=ANIM_FPS, anim_stride=ANIM_STRIDE)
    
    # Ejemplo 2: Órbita en forma de 8 (problema de 3 cuerpos)
    print("\n" + "="*70)
    print("EJEMPLO 2: ÓRBITA EN FIGURA-8")
    print("="*70)
    
    masses2, U0_2, t_span2, names2, G2 = setup_three_body_figure8()
    dt2 = 0.001  # Paso pequeño para estabilidad
    
    t2, U2 = simulate_nbody(masses2, U0_2, t_span2, dt2, names2, G2, img_prefix="figura8", animate=ANIMAR, anim_fps=ANIM_FPS, anim_stride=ANIM_STRIDE)
    
    # Ejemplo 3: Sistema de 3 cuerpos dummy
    print("\n" + "="*70)
    print("EJEMPLO 3: SISTEMA DE 3 CUERPOS DUMMY")
    print("="*70)

    masses3, U0_3, t_span3, names3, G3 = setup_three_body_dummies()
    dt3 = 0.001  # paso pequeño para estabilidad numérica (distancias ~1, masas ~1, G=1)

    print("    Tres cuerpos con masas y velocidades distintas, interacción gravitatoria mutua.")
    print("    IMPORTANTE: dt reducido a 0.001 para evitar errores numéricos grandes.")
    t3, U3 = simulate_nbody(masses3, U0_3, t_span3, dt3, names3, G3, img_prefix="dummies_3cuerpos", animate=ANIMAR, anim_fps=ANIM_FPS, anim_stride=ANIM_STRIDE)

    # Discusión final
    print("\n" + "="*70)
    print("DISCUSIÓN Y CONCLUSIONES")
    print("="*70)
    print("""
1. IMPLEMENTACIÓN:
   - Función nbody_rhs(): calcula interacciones gravitatorias entre N cuerpos
   - Complejidad O(N²)
   - Evita singularidades cuando dist < 1e-10

2. CONSERVACIÓN DE CANTIDADES:
   - Energía: debería conservarse
   - Momento angular: también conservado
   - Errores numéricos
   - RK4 mantiene buena conservación

3. SISTEMA SOLAR SIMPLIFICADO:
   - Sol prácticamente estático (masa dominante)
   - Tierra: órbita circular, periodo ~ 1 año
   - Júpiter: órbita más amplia, periodo ~ 11.86 años
   - Conservación excelente debido a órbitas casi circulares

4. ÓRBITA EN FIGURA-8:
   - Solución periódica especial del problema de 3 cuerpos - curiosidad vista en orbital
   - Muy sensible a CI
   - Requiere dt pequeño para mantener estabilidad
   - Las 3 masas trazan la misma trayectoria desfasadas temporalmente

5. SISTEMA DE 3 CUERPOS DUMMY:
   - Ejemplo ilustrativo con 3 cuerpos y condiciones iniciales variadas
   - Muestra interacciones gravitatorias sin un patrón orbital estable
   - Comportamiento más errático y menos predecible
   - Útil para estudiar el efecto de condiciones iniciales en el sistema

6. CONSIDERACIONES NUMÉRICAS:
   - dt crítico: depende de la escala temporal más rápida del sistema
   - Para órbitas cercanas -> dt pequeño (fuerzas grandes)
   - RK4 es buen compromiso entre precisión y coste
   - Leap-Frog mejor para largo plazo (revisar)

    """)
    print("="*70)


# --------------------------------------------------------------------------
# Punto de entrada
# --------------------------------------------------------------------------
if __name__ == '__main__':
    run_hito5()
