"""
Test rápido solo del ejemplo de 3 cuerpos dummy
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

from Temporal_Schemes import RK4, integrate_cauchy
from problems import (
    nbody_rhs, nbody_energy, nbody_angular_momentum,
    setup_three_body_dummies
)
from hito_5 import simulate_nbody

print("="*70)
print("TEST RÁPIDO: SISTEMA 3 CUERPOS DUMMY CON dt=0.001")
print("="*70)

masses, U0, t_span, names, G = setup_three_body_dummies()
dt = 0.001

t, U = simulate_nbody(masses, U0, t_span, dt, names, G, RK4, img_prefix="test_dummies")

print("\n✓ Test completado. Revisa las gráficas en 'Salidas Hito 5/'")
