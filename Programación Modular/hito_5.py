import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# -----------------------------------------------------------------------------
# Importar esquemas del Hito 2
# (Se asume que el directorio madre está en sys.path; ajustar si fuese necesario)
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
#ENUNCIADO HITO 5: 
