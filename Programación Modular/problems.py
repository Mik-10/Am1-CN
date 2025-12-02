# ==============================================================================
# DEFINICIÓN DE PROBLEMAS DE PRUEBA PARA INTEGRACIÓN NUMÉRICA
# ==============================================================================
import numpy as np

# ------------------------------------------------------------------------------
# 1. OSCILADOR ARMÓNICO LINEAL
# ------------------------------------------------------------------------------

def oscillator_rhs(U, t, omega=1.0):
    """
    Oscilador armónico: x'' + omega^2 * x = 0
    
    Vector de estado: U = [x, v]
    Derivada: dU/dt = [v, -omega^2 * x]
    
    Parámetros:
    - U: [x, v]
    - t: tiempo
    - omega: frecuencia angular (default=1.0)
    
    Retorna:
    - dU/dt: [v, -omega^2 * x]
    """
    x, v = U
    return np.array([v, -omega**2 * x])


def oscillator_exact(t, x0=1.0, v0=0.0, omega=1.0):
    """
    Solución exacta del oscilador armónico.
    
    x(t) = x0*cos(omega*t) + (v0/omega)*sin(omega*t)
    v(t) = -x0*omega*sin(omega*t) + v0*cos(omega*t)
    
    Parámetros:
    - t: tiempo
    - x0, v0: condiciones iniciales
    - omega: frecuencia angular
    
    Retorna:
    - U: [x(t), v(t)]
    """
    x = x0 * np.cos(omega * t) + (v0 / omega) * np.sin(omega * t)
    v = -x0 * omega * np.sin(omega * t) + v0 * np.cos(omega * t)
    return np.array([x, v])


def oscillator_energy(U, omega=1.0):
    """
    Calcula energía total del oscilador: E = (1/2)(v^2 + omega^2*x^2)
    
    Parámetros:
    - U: [x, v] o array [N, 2]
    - omega: frecuencia angular
    
    Retorna:
    - E: energía total
    """
    if U.ndim == 1:
        x, v = U
        return 0.5 * (v**2 + omega**2 * x**2)
    else:
        x = U[:, 0]
        v = U[:, 1]
        return 0.5 * (v**2 + omega**2 * x**2)


# ------------------------------------------------------------------------------
# 2. PROBLEMA DE KEPLER (DOS CUERPOS)
# ------------------------------------------------------------------------------

def kepler_rhs(U, t, mu=1.0):
    """
    Problema de Kepler 2D: movimiento orbital.
    
    Vector de estado: U = [x, y, vx, vy]
    Derivada: dU/dt = [vx, vy, -mu*x/r^3, -mu*y/r^3]
    donde r = sqrt(x^2 + y^2)
    
    Parámetros:
    - U: [x, y, vx, vy]
    - t: tiempo
    - mu: parámetro gravitacional (default=1.0)
    
    Retorna:
    - dU/dt: [vx, vy, ax, ay]
    """
    x, y, vx, vy = U
    r = np.sqrt(x**2 + y**2)
    
    # Evitar singularidad en r=0
    if r < 1e-10:
        ax, ay = 0.0, 0.0
    else:
        ax = -mu * x / r**3
        ay = -mu * y / r**3
    
    return np.array([vx, vy, ax, ay])


def kepler_energy(U, mu=1.0):
    """
    Calcula energía total de Kepler: E = (1/2)v^2 - mu/r
    
    Parámetros:
    - U: [x, y, vx, vy] o array [N, 4]
    - mu: parámetro gravitacional
    
    Retorna:
    - E: energía total
    """
    if U.ndim == 1:
        x, y, vx, vy = U
        r = np.sqrt(x**2 + y**2)
        v2 = vx**2 + vy**2
        return 0.5 * v2 - mu / r
    else:
        x = U[:, 0]
        y = U[:, 1]
        vx = U[:, 2]
        vy = U[:, 3]
        r = np.sqrt(x**2 + y**2)
        v2 = vx**2 + vy**2
        return 0.5 * v2 - mu / r


def kepler_angular_momentum(U):
    """
    Calcula momento angular de Kepler: L = r x v (componente z)
    
    Parámetros:
    - U: [x, y, vx, vy] o array [N, 4]
    
    Retorna:
    - L: momento angular (escalar, componente z)
    """
    if U.ndim == 1:
        x, y, vx, vy = U
        return x * vy - y * vx
    else:
        x = U[:, 0]
        y = U[:, 1]
        vx = U[:, 2]
        vy = U[:, 3]
        return x * vy - y * vx


# ------------------------------------------------------------------------------
# 3. ECUACIÓN DE ARENSTORF (PROBLEMA DE TRES CUERPOS RESTRINGIDO)
# ------------------------------------------------------------------------------

def arenstorf_rhs(U, t, mu=0.012277471):
    """
    Ecuación de Arenstorf (problema restringido de tres cuerpos).
    
    Parámetros:
    - U: [x, y, vx, vy]
    - t: tiempo
    - mu: parámetro de masa (default para sistema Tierra-Luna)
    
    Retorna:
    - dU/dt
    """
    x, y, vx, vy = U
    
    # Distancias a los cuerpos primarios
    D1 = ((x + mu)**2 + y**2)**(3/2)
    D2 = ((x - 1 + mu)**2 + y**2)**(3/2)
    
    # Aceleraciones
    ax = x + 2*vy - (1 - mu)*(x + mu)/D1 - mu*(x - 1 + mu)/D2
    ay = y - 2*vx - (1 - mu)*y/D1 - mu*y/D2
    
    return np.array([vx, vy, ax, ay])


# ------------------------------------------------------------------------------
# 4. ECUACIÓN DE VAN DER POL (SISTEMA RÍGIDO)
# ------------------------------------------------------------------------------

def vanderpol_rhs(U, t, mu=1.0):
    """
    Ecuación de Van der Pol: x'' - mu*(1-x^2)*x' + x = 0
    
    Vector de estado: U = [x, x']
    
    Parámetros:
    - U: [x, v]
    - t: tiempo
    - mu: parámetro de no linealidad
    
    Retorna:
    - dU/dt
    """
    x, v = U
    return np.array([v, mu * (1 - x**2) * v - x])


# ------------------------------------------------------------------------------
# 5. PÉNDULO NO LINEAL
# ------------------------------------------------------------------------------

def pendulum_rhs(U, t, g=9.81, L=1.0):
    """
    Péndulo no lineal: theta'' + (g/L)*sin(theta) = 0
    
    Vector de estado: U = [theta, omega]
    
    Parámetros:
    - U: [theta, omega]
    - t: tiempo
    - g: aceleración de la gravedad
    - L: longitud del péndulo
    
    Retorna:
    - dU/dt
    """
    theta, omega = U
    return np.array([omega, -(g / L) * np.sin(theta)])


def pendulum_energy(U, m=1.0, g=9.81, L=1.0):
    """
    Energía del péndulo: E = (1/2)*m*L^2*omega^2 + m*g*L*(1-cos(theta))
    
    Parámetros:
    - U: [theta, omega]
    - m: masa
    - g: gravedad
    - L: longitud
    
    Retorna:
    - E: energía total
    """
    if U.ndim == 1:
        theta, omega = U
        return 0.5 * m * L**2 * omega**2 + m * g * L * (1 - np.cos(theta))
    else:
        theta = U[:, 0]
        omega = U[:, 1]
        return 0.5 * m * L**2 * omega**2 + m * g * L * (1 - np.cos(theta))


# ------------------------------------------------------------------------------
# 6. SISTEMA DE LORENZ (CAÓTICO)
# ------------------------------------------------------------------------------

def lorenz_rhs(U, t, sigma=10.0, rho=28.0, beta=8.0/3.0):
    """
    Sistema de Lorenz (caótico).
    
    dx/dt = sigma*(y - x)
    dy/dt = x*(rho - z) - y
    dz/dt = x*y - beta*z
    
    Parámetros:
    - U: [x, y, z]
    - t: tiempo
    - sigma, rho, beta: parámetros del sistema
    
    Retorna:
    - dU/dt
    """
    x, y, z = U
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return np.array([dx, dy, dz])


# ------------------------------------------------------------------------------
# CRTBP: Problema restringido de tres cuerpos (marco rotante) para estudio de Lagrangianos
# ------------------------------------------------------------------------------
def crtbp_rhs(U, t, mu=0.012277471):
    """
    Problema restringido de 3 cuerpos en marco rotante (x,y,vx,vy).
    Primarios en posiciones fijas: (-mu,0) y (1-mu,0). Unidades normalizadas.

    Ecuaciones:
      r1 = sqrt((x+mu)^2 + y^2), r2 = sqrt((x-1+mu)^2 + y^2)
      ax = 2*vy + x - (1-mu)*(x+mu)/r1^3 - mu*(x-1+mu)/r2^3
      ay = -2*vx + y - (1-mu)*y/r1^3    - mu*y/r2^3
    """
    x, y, vx, vy = U
    r1 = np.sqrt((x + mu)**2 + y**2)
    r2 = np.sqrt((x - 1 + mu)**2 + y**2)

    ax = 2*vy + x - (1 - mu)*(x + mu)/r1**3 - mu*(x - 1 + mu)/r2**3
    ay = -2*vx + y - (1 - mu)*y/r1**3 - mu*y/r2**3
    return np.array([vx, vy, ax, ay])


def crtbp_jacobi(U, mu=0.012277471):
    """
    Constante de Jacobi C = 2*Omega(x,y) - v^2, donde
    Omega = 0.5*(x^2 + y^2) + (1-mu)/r1 + mu/r2
    """
    x, y, vx, vy = U
    r1 = np.sqrt((x + mu)**2 + y**2)
    r2 = np.sqrt((x - 1 + mu)**2 + y**2)
    Omega = 0.5*(x**2 + y**2) + (1 - mu)/r1 + mu/r2
    v2 = vx**2 + vy**2
    return 2*Omega - v2


def crtbp_lagrange_points(mu=0.012277471):
    """
    Posiciones de L1–L5 en el marco rotante.
    L4/L5: triangulares, exactos en normalización.
    L1–L3: aproximaciones de tercer orden (series clásicas).
    Retorna dict con arrays [x,y] para cada Li.
    """
    # Primarios
    x1 = -mu
    x2 = 1 - mu

    # L4 y L5 (triangulares, forming equilátero)
    xL4 = 0.5 - mu
    yL4 =  np.sqrt(3)/2
    xL5 = xL4
    yL5 = -np.sqrt(3)/2

    # Aprox para L1, L2, L3 (Murray & Dermott-style)
    # q = (mu/(1-mu))**(1/3)
    q = (mu/(1 - mu))**(1/3)

    # L1 cerca de x2
    xL1 = x2 - (q - q**2/3 - q**3/9)
    # L2 más allá de x2
    xL2 = x2 + (q + q**2/3 + q**3/9)
    # L3 cerca de x1, al otro lado
    xL3 = -1 - (5*mu/12) + (mu**2)/3  # aproximación sencilla
    yL1 = yL2 = yL3 = 0.0

    return {
        'L1': np.array([xL1, yL1]),
        'L2': np.array([xL2, yL2]),
        'L3': np.array([xL3, yL3]),
        'L4': np.array([xL4, yL4]),
        'L5': np.array([xL5, yL5]),
    }


# ------------------------------------------------------------------------------
# DICCIONARIO DE PROBLEMAS - WIP
# ------------------------------------------------------------------------------

PROBLEMS = {
    'oscillator': {
        'rhs': oscillator_rhs,
        'exact': oscillator_exact,
        'energy': oscillator_energy,
        'U0': np.array([1.0, 0.0]),
        't_span': (0, 2*np.pi),
        'description': 'Oscilador armónico lineal'
    },
    'kepler': {
        'rhs': kepler_rhs,
        'energy': kepler_energy,
        'angular_momentum': kepler_angular_momentum,
        'U0': np.array([1.0, 0.0, 0.0, 1.0]),
        't_span': (0, 6*np.pi),
        'description': 'Problema de Kepler (órbita circular)'
    },
    'kepler_elliptic': {
        'rhs': kepler_rhs,
        'energy': kepler_energy,
        'angular_momentum': kepler_angular_momentum,
        'U0': np.array([1.0, 0.0, 0.0, 0.8]),
        't_span': (0, 10*np.pi),
        'description': 'Problema de Kepler (órbita elíptica)'
    },
    'arenstorf': {
        'rhs': arenstorf_rhs,
        'U0': np.array([0.994, 0.0, 0.0, -2.00158510637908]),
        't_span': (0, 17.0652165601579625588917206249),
        'description': 'Órbita de Arenstorf'
    },
    'vanderpol': {
        'rhs': vanderpol_rhs,
        'U0': np.array([2.0, 0.0]),
        't_span': (0, 20.0),
        'description': 'Ecuación de Van der Pol'
    },
    'pendulum': {
        'rhs': pendulum_rhs,
        'energy': pendulum_energy,
        'U0': np.array([np.pi/4, 0.0]),
        't_span': (0, 10.0),
        'description': 'Péndulo no lineal'
    },
    'lorenz': {
        'rhs': lorenz_rhs,
        'U0': np.array([1.0, 1.0, 1.0]),
        't_span': (0, 50.0),
        'description': 'Sistema de Lorenz (caótico)'
    },
    'crtbp': {
        'rhs': crtbp_rhs,
        'U0': np.array([0.5 - 0.012277471, np.sqrt(3)/2, 0.0, 0.0]),  # en L4 con v=0
        't_span': (0.0, 20.0),
        'description': 'CRTBP en marco rotante, estudio de puntos de Lagrange'
    },
}


def get_problem(name):
    """
    Obtiene un problema predefinido.
    
    Parámetros:
    - name: nombre del problema (clave en PROBLEMS)
    
    Retorna:
    - dict con información del problema
    """
    if name not in PROBLEMS:
        available = ', '.join(PROBLEMS.keys())
        raise ValueError(f"Problema '{name}' no encontrado. "
                        f"Disponibles: {available}")
    return PROBLEMS[name]


# ------------------------------------------------------------------------------
# 7. PROBLEMA DE N CUERPOS
# ------------------------------------------------------------------------------

def nbody_rhs(U, t, masses, G=1.0):
    """
    Sistema de N cuerpos gravitatorios.
    
    Parámetros:
    - U: vector de estado [x1,y1,z1, vx1,vy1,vz1, x2,y2,z2, vx2,vy2,vz2, ...]
         Tamaño: 6*N (3 pos + 3 vel por cuerpo)
    - t: tiempo (no usado, pero necesario para interfaz)
    - masses: array con masas [m1, m2, ..., mN]
    - G: constante gravitacional (default=1.0)
    
    Retorna:
    - dU/dt: derivadas [vx1,vy1,vz1, ax1,ay1,az1, vx2,vy2,vz2, ax2,ay2,az2, ...]
    """
    N = len(masses)
    dU = np.zeros_like(U)
    
    # Extraer posiciones y velocidades
    pos = U[:3*N].reshape((N, 3))  # [N, 3]
    vel = U[3*N:].reshape((N, 3))  # [N, 3]
    
    # dU/dt: velocidades van primero
    dU[:3*N] = U[3*N:]  # dr/dt = v
    
    # Calcular aceleraciones por interacción gravitatoria
    acc = np.zeros((N, 3))
    
    for i in range(N):
        for j in range(N):
            if i != j:
                r_ij = pos[i] - pos[j]  # vector de i a j
                dist = np.linalg.norm(r_ij)
                
                # Evitar singularidad
                if dist < 1e-10:
                    continue
                
                # F_ij = -G*m_j*(r_i - r_j)/|r_ij|^3
                # a_i = F_i/m_i = sum_j(-G*m_j*(r_i - r_j)/|r_ij|^3)
                acc[i] += -G * masses[j] * r_ij / dist**3
    
    # Guardar aceleraciones
    dU[3*N:] = acc.flatten()
    
    return dU


def nbody_energy(U, masses, G=1.0):
    """
    Calcula energía total del sistema de N cuerpos.
    E = E_cin + E_pot
    E_cin = sum(0.5 * m_i * v_i^2)
    E_pot = -sum_{i<j}(G * m_i * m_j / |r_i - r_j|)
    
    Parámetros:
    - U: vector de estado (puede ser 1D o 2D [n_steps, 6*N])
    - masses: array de masas
    - G: constante gravitacional
    
    Retorna:
    - E: energía total (escalar o array según U)
    """
    N = len(masses)
    
    if U.ndim == 1:
        # Caso 1D: un solo instante
        pos = U[:3*N].reshape((N, 3))
        vel = U[3*N:].reshape((N, 3))
        
        # Energía cinética
        E_kin = 0.5 * np.sum(masses[:, None] * vel**2)
        
        # Energía potencial
        E_pot = 0.0
        for i in range(N):
            for j in range(i+1, N):
                r_ij = pos[i] - pos[j]
                dist = np.linalg.norm(r_ij)
                if dist > 1e-10:
                    E_pot -= G * masses[i] * masses[j] / dist
        
        return E_kin + E_pot
    
    else:
        # Caso 2D: múltiples instantes
        n_steps = U.shape[0]
        E = np.zeros(n_steps)
        for k in range(n_steps):
            E[k] = nbody_energy(U[k], masses, G)
        return E


def nbody_angular_momentum(U, masses):
    """
    Calcula momento angular total del sistema.
    L = sum(m_i * r_i x v_i)
    
    Parámetros:
    - U: vector de estado (1D o 2D)
    - masses: array de masas
    
    Retorna:
    - L: vector momento angular [Lx, Ly, Lz] (o array [n_steps, 3])
    """
    N = len(masses)
    
    if U.ndim == 1:
        pos = U[:3*N].reshape((N, 3))
        vel = U[3*N:].reshape((N, 3))
        
        L = np.zeros(3)
        for i in range(N):
            L += masses[i] * np.cross(pos[i], vel[i])
        return L
    
    else:
        n_steps = U.shape[0]
        L = np.zeros((n_steps, 3))
        for k in range(n_steps):
            L[k] = nbody_angular_momentum(U[k], masses)
        return L


def setup_solar_system_simple():
    """
    Sistema solar simplificado: Sol + Tierra + Júpiter (2D).
    Unidades: UA, años, masas solares.
    
    Retorna:
    - masses: array de masas
    - U0: condición inicial [pos_sol, pos_tierra, pos_jupiter, vel_sol, vel_tierra, vel_jupiter]
    - t_span: intervalo temporal
    - names: nombres de los cuerpos
    - G: constante gravitacional
    """
    # Masas en unidades de masa solar
    M_sol = 1.0
    M_tierra = 3.0e-6  # aprox 1/333000
    M_jupiter = 9.5e-4  # aprox 1/1050
    
    masses = np.array([M_sol, M_tierra, M_jupiter])
    names = ["Sol", "Tierra", "Júpiter"]
    
    # Posiciones iniciales (z=0, todo en plano xy)
    r_sol = np.array([0.0, 0.0, 0.0])
    r_tierra = np.array([1.0, 0.0, 0.0])
    r_jupiter = np.array([5.2, 0.0, 0.0])
    
    # Velocidades orbitales circulares (v = sqrt(G*M/r))
    # G=4*pi^2 en unidades de UA^3 / (M_sol * año^2)
    G = 4 * np.pi**2
    
    v_sol = np.array([0.0, 0.0, 0.0])
    v_tierra = np.array([0.0, np.sqrt(G * M_sol / 1.0), 0.0])
    v_jupiter = np.array([0.0, np.sqrt(G * M_sol / 5.2), 0.0])
    
    # Vector de estado: [TODAS LAS POSICIONES][TODAS LAS VELOCIDADES]
    U0 = np.hstack([r_sol, r_tierra, r_jupiter, v_sol, v_tierra, v_jupiter])
    
    t_span = (0.0, 20.0)  # 20 años
    
    return masses, U0, t_span, names, G


def setup_three_body_figure8():
    """
    Órbita en forma de 8: solución periódica del problema de 3 cuerpos.
    Masas iguales, configuración simétrica especial.
    
    Retorna:
    - masses: array de masas
    - U0: condición inicial [posiciones...][velocidades...]
    - t_span: intervalo temporal
    - names: nombres de los cuerpos
    - G: constante gravitacional
    """
    # Tres masas iguales
    masses = np.array([1.0, 1.0, 1.0])
    names = ["Cuerpo 1", "Cuerpo 2", "Cuerpo 3"]
    
    # Condiciones iniciales para órbita en 8
    r1 = np.array([-0.97000436, 0.24308753, 0.0])
    r2 = np.array([0.0, 0.0, 0.0])
    r3 = np.array([0.97000436, -0.24308753, 0.0])
    
    v1 = np.array([0.4662036850, 0.4323657300, 0.0])
    v2 = np.array([-0.93240737, -0.86473146, 0.0])
    v3 = np.array([0.4662036850, 0.4323657300, 0.0])
    
    # Vector de estado: [TODAS LAS POSICIONES][TODAS LAS VELOCIDADES]
    U0 = np.hstack([r1, r2, r3, v1, v2, v3])
    
    t_span = (0.0, 6.5)  # Periodo aprox 6.3
    G = 1.0
    
    return masses, U0, t_span, names, G


def setup_three_body_dummies():
    """
    Tres cuerpos 'dummy' con masas distintas en configuración quasi-circular.
    
    Estrategia mejorada:
    - Masas colocadas formando triángulo casi equilátero
    - Velocidades tangenciales calibradas para equilibrio aproximado entre E_cin y E_pot
    - Sistema diseñado para minimizar encuentros cercanos y mantener ligadura
    - Momento lineal total = 0
    
    Configuración inspirada en órbitas de Lagrange pero adaptada para masas desiguales.
    Formato: [posiciones...][velocidades...], G=1
    """
    masses = np.array([1.0, 0.8, 1.2])
    names = ["Dummy A", "Dummy B", "Dummy C"]
    G = 1.0
    
    # Posiciones en triángulo equilátero con lado a = 2.0 (más separadas para evitar colisiones)
    a = 2.0
    r1 = np.array([-a/2, -a/(2*np.sqrt(3)), 0.0])
    r2 = np.array([ a/2, -a/(2*np.sqrt(3)), 0.0])
    r3 = np.array([ 0.0,  a/np.sqrt(3),     0.0])
    
    # Recentrar al centro de masa
    R_cm = (masses[0]*r1 + masses[1]*r2 + masses[2]*r3) / np.sum(masses)
    r1 -= R_cm; r2 -= R_cm; r3 -= R_cm
    
    # Para un sistema aproximadamente circular:
    # v_circ ~ sqrt(G*M_total/r_medio)
    # Con a=2.0, r_medio ~ a/sqrt(3) ~ 1.15
    M_tot = np.sum(masses)
    r_medio = a / np.sqrt(3)
    v_circ_base = np.sqrt(G * M_tot / r_medio)
    
    # Factor de reducción para tener E_total negativo pero no demasiado (órbitas estables)
    factor = 0.45  # ajustado empíricamente
    
    def tangencial_unitario(r):
        """Vector tangencial unitario (perpendicular a r en plano xy)"""
        norm_xy = np.sqrt(r[0]**2 + r[1]**2)
        if norm_xy < 1e-10:
            return np.array([0.0, 0.0, 0.0])
        return np.array([-r[1]/norm_xy, r[0]/norm_xy, 0.0])
    
    # Velocidades tangenciales
    v1 = factor * v_circ_base * tangencial_unitario(r1)
    v2 = factor * v_circ_base * tangencial_unitario(r2)
    v3 = factor * v_circ_base * tangencial_unitario(r3)
    
    # Forzar momento lineal total = 0
    P = masses[0]*v1 + masses[1]*v2 + masses[2]*v3
    v_corr = P / M_tot
    v1 -= v_corr; v2 -= v_corr; v3 -= v_corr
    
    # Ensamblar estado
    U0 = np.hstack([r1, r2, r3, v1, v2, v3])
    
    # Intervalo temporal: ajustado para observar ~2-3 órbitas aproximadas
    # Periodo estimado T ~ 2*pi*sqrt(r^3/(G*M)) ~ 2*pi*sqrt(1.15^3/3) ~ 4.4
    t_span = (0.0, 15.0)
    
    return masses, U0, t_span, names, G