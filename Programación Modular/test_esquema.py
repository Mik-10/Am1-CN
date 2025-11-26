"""
Test rápido de selección de esquema temporal
"""
from Temporal_Schemes import Euler, Inverse_Euler, Crank_Nicolson, RK4, Leap_Frog
from problems import setup_three_body_dummies, nbody_rhs
from hito_5 import ESQUEMA_TEMPORAL

print("="*70)
print("TEST: Verificación de configuración de esquema")
print("="*70)
print(f"\nEsquema seleccionado: {ESQUEMA_TEMPORAL.__name__}")
if ESQUEMA_TEMPORAL == Leap_Frog:
    print("Modo Leap-Frog: ACTIVADO (automático)")
print("\nEsquemas disponibles:")
print("  - Euler")
print("  - Inverse_Euler")
print("  - Crank_Nicolson")
print("  - RK4")
print("  - Leap_Frog (modo automático)")
print("="*70)
