# Hito 5 - Problema de N cuerpos

## Selección del esquema temporal

El esquema de integración se configura **globalmente al inicio del archivo `hito_5.py`**.

### Cómo cambiar el esquema

Edita la línea 36 en `hito_5.py`:

```python
# Opciones disponibles: Euler, Inverse_Euler, Crank_Nicolson, RK4, Leap_Frog
ESQUEMA_TEMPORAL = RK4  # <-- CAMBIAR AQUÍ PARA TODOS LOS EJEMPLOS
```

El modo Leap-Frog se activa automáticamente cuando se selecciona ese esquema.

### Esquemas disponibles

- **`Euler`**: Euler explícito (orden 1)
- **`Inverse_Euler`**: Euler implícito (orden 1)
- **`Crank_Nicolson`**: Método de Crank-Nicolson (orden 2)
- **`RK4`**: Runge-Kutta de orden 4 (recomendado)
- **`Leap_Frog`**: Leap-Frog (simpléctico, se activa automáticamente)

### Ejemplo: Cambiar a Leap-Frog

```python
ESQUEMA_TEMPORAL = Leap_Frog
```

### Ejemplo: Cambiar a Euler

```python
ESQUEMA_TEMPORAL = Euler
```

## Características

- **Un solo esquema para todos los ejemplos**: Sistema solar, figura-8 y 3 cuerpos dummy
- **Marcadores visuales**:
  - Círculos huecos: posiciones iniciales
  - Círculos sólidos: posiciones finales
- **Conservación de energía y momento angular**: verificada automáticamente

## Ejecución

```bash
python hito_5.py
```

Las figuras se guardan en `Salidas Hito 5/`.
