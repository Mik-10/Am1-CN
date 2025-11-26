"""
Script de debug para verificar condiciones iniciales del sistema de 3 cuerpos dummy.
"""
import numpy as np
from problems import setup_three_body_dummies, nbody_energy, nbody_angular_momentum

# Obtener condiciones iniciales
masses, U0, t_span, names, G = setup_three_body_dummies()
N = len(masses)

print("="*70)
print("DEBUG: CONDICIONES INICIALES - SISTEMA 3 CUERPOS DUMMY")
print("="*70)

# Extraer posiciones y velocidades
pos = U0[:3*N].reshape((N, 3))
vel = U0[3*N:].reshape((N, 3))

print(f"\nMasas: {masses}")
print(f"G = {G}")
print(f"Tiempo: {t_span}")

print("\n" + "-"*70)
print("POSICIONES INICIALES:")
print("-"*70)
for i in range(N):
    r = pos[i]
    r_norm = np.linalg.norm(r)
    print(f"{names[i]:10s}: r = [{r[0]:7.4f}, {r[1]:7.4f}, {r[2]:7.4f}]  |r| = {r_norm:.4f}")

# Centro de masa
R_cm = np.sum(masses[:, None] * pos, axis=0) / np.sum(masses)
print(f"\nCentro de masa: R_cm = [{R_cm[0]:7.4f}, {R_cm[1]:7.4f}, {R_cm[2]:7.4f}]")

print("\n" + "-"*70)
print("VELOCIDADES INICIALES:")
print("-"*70)
for i in range(N):
    v = vel[i]
    v_norm = np.linalg.norm(v)
    print(f"{names[i]:10s}: v = [{v[0]:7.4f}, {v[1]:7.4f}, {v[2]:7.4f}]  |v| = {v_norm:.4f}")

# Momento lineal total
P_total = np.sum(masses[:, None] * vel, axis=0)
P_norm = np.linalg.norm(P_total)
print(f"\nMomento lineal total: P = [{P_total[0]:7.4e}, {P_total[1]:7.4e}, {P_total[2]:7.4e}]")
print(f"                      |P| = {P_norm:.4e}")

print("\n" + "-"*70)
print("ENERGÍAS:")
print("-"*70)

# Energía cinética
E_kin = 0.5 * np.sum(masses[:, None] * vel**2)
print(f"Energía cinética:  E_kin = {E_kin:.6f}")

# Energía potencial
E_pot = 0.0
print("\nContribuciones al potencial:")
for i in range(N):
    for j in range(i+1, N):
        r_ij = pos[i] - pos[j]
        dist = np.linalg.norm(r_ij)
        U_ij = -G * masses[i] * masses[j] / dist
        E_pot += U_ij
        print(f"  U_{i}{j} = -{G}*{masses[i]}*{masses[j]}/{dist:.4f} = {U_ij:.6f}")

print(f"\nEnergía potencial: E_pot = {E_pot:.6f}")

# Energía total
E_total = E_kin + E_pot
print(f"Energía total:     E_tot = {E_total:.6f}")

if E_total < 0:
    print("  → Sistema LIGADO (E < 0)")
else:
    print("  → Sistema NO LIGADO (E ≥ 0) - se dispersará")

print("\n" + "-"*70)
print("MOMENTO ANGULAR:")
print("-"*70)

L_total = np.zeros(3)
for i in range(N):
    L_i = masses[i] * np.cross(pos[i], vel[i])
    L_total += L_i
    print(f"{names[i]:10s}: L = [{L_i[0]:7.4f}, {L_i[1]:7.4f}, {L_i[2]:7.4f}]")

L_norm = np.linalg.norm(L_total)
print(f"\nMomento angular total: L = [{L_total[0]:7.4f}, {L_total[1]:7.4f}, {L_total[2]:7.4f}]")
print(f"                       |L| = {L_norm:.4f}")

print("\n" + "-"*70)
print("ANÁLISIS DE VELOCIDADES:")
print("-"*70)

for i in range(N):
    r = pos[i]
    v = vel[i]
    
    # Componente radial: v·r / |r|
    r_norm = np.linalg.norm(r)
    if r_norm > 1e-10:
        v_radial = np.dot(v, r) / r_norm
        # Componente tangencial
        v_perp = v - (np.dot(v, r) / r_norm**2) * r
        v_tang = np.linalg.norm(v_perp)
    else:
        v_radial = 0.0
        v_tang = 0.0
    
    print(f"{names[i]:10s}: v_radial = {v_radial:7.4f}, v_tangencial = {v_tang:.4f}")
    if v_radial > 0:
        print(f"              → alejándose del centro")
    elif v_radial < 0:
        print(f"              → acercándose al centro")

print("\n" + "="*70)
print("RECOMENDACIONES:")
print("="*70)

if E_total >= 0:
    print("⚠ El sistema tiene E_total ≥ 0:")
    print("  - Las masas se dispersarán eventualmente")
    print("  - Reducir velocidades (factores 0.35→0.25) o aumentar masas/reducir distancias")
else:
    energy_ratio = abs(E_kin / E_pot)
    print(f"✓ El sistema está ligado (E < 0)")
    print(f"  Ratio E_kin/|E_pot| = {energy_ratio:.3f}")
    if energy_ratio > 0.5:
        print("  - Ratio alto: órbitas amplias, posible dispersión tras interacciones")
    else:
        print("  - Ratio moderado: debería mantener ligadura")

if P_norm > 1e-6:
    print(f"\n⚠ Momento lineal no es exactamente cero (|P| = {P_norm:.2e})")
    print("  - El centro de masa se moverá")

print("="*70)
