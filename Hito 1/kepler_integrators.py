import numpy as np
import matplotlib.pyplot as plt
import os

# Aceleración Kepleriana
def accel(r, mu=1.0, eps=1e-12):
	n = np.linalg.norm(r)
	return -mu * r / max(n**3, eps)

# Integradores: Euler explícito
def euler_step(r, v, dt, mu=1.0):
	a = accel(r, mu)
	return r + dt * v, v + dt * a

# Crank-Nicolson aproximado: predictor (Euler) + trapezoidal corrector
def crank_nicolson_step(r, v, dt, mu=1.0):
	a = accel(r, mu)
	rp = r + dt * v
	vp = v + dt * a
	ap = accel(rp, mu)
	v_new = v + 0.5 * dt * (a + ap)
	r_new = r + 0.5 * dt * (v + v_new)
	return r_new, v_new

# RK4 para el sistema (r, v)
def rk4_step(r, v, dt, mu=1.0):
	def f(r_, v_):
		return v_, accel(r_, mu)
	k1r, k1v = f(r, v)
	k2r, k2v = f(r + 0.5*dt*k1r, v + 0.5*dt*k1v)
	k3r, k3v = f(r + 0.5*dt*k2r, v + 0.5*dt*k2v)
	k4r, k4v = f(r + dt*k3r, v + dt*k3v)
	r_new = r + dt*(k1r + 2*k2r + 2*k3r + k4r)/6.0
	v_new = v + dt*(k1v + 2*k2v + 2*k3v + k4v)/6.0
	return r_new, v_new

# Rutina de integración simple
def integrate(step, r0, v0, dt, T, mu=1.0):
	n = int(np.ceil(T / dt))
	rs = np.zeros((n+1, 2))
	vs = np.zeros((n+1, 2))
	ts = np.linspace(0, n*dt, n+1)
	rs[0], vs[0] = r0, v0
	E = np.zeros(n+1)
	E[0] = 0.5*np.dot(v0, v0) - mu/np.linalg.norm(r0)
	for i in range(n):
		rn, vn = step(rs[i], vs[i], dt, mu)
		rs[i+1], vs[i+1] = rn, vn
		E[i+1] = 0.5*np.dot(vn, vn) - mu/np.linalg.norm(rn)
	return ts, rs, vs, E

# Salida mínima: crear carpeta si no existe
def ensure_dir(d):
	if not os.path.exists(d):
		os.makedirs(d, exist_ok=True)

# Main: pruebas simples para varios dt
def main():
	out = "results"
	ensure_dir(out)
	mu = 1.0
	r0 = np.array([1.0, 0.0])
	v0 = np.array([0.0, 0.8])
	T = 50.0
	dts = [0.1, 0.02, 0.005]
	
	# Colores distintos para cada dt
	colors_dt = ['r', 'g', 'b']
	methods = [("Euler", euler_step), ("CrankNicolson", crank_nicolson_step), ("RK4", rk4_step)]

	# Órbitas
	plt.figure(figsize=(15,5))
	for i, (name, step) in enumerate(methods):
		plt.subplot(1,3,i+1)
		for dt, color in zip(dts, colors_dt):
			_, rs, _, _ = integrate(step, r0, v0, dt, T, mu)
			plt.plot(rs[:,0], rs[:,1], label=f"dt={dt}", color=color)
		plt.plot(0,0,'ko')
		plt.axis('equal')
		plt.title(f"{name}")
		plt.legend()
	plt.tight_layout()
	plt.savefig(os.path.join(out, "orbits_comparison.png"))
	plt.close()

	# Energía
	plt.figure(figsize=(15,5))
	for i, (name, step) in enumerate(methods):
		plt.subplot(1,3,i+1)
		for dt in dts:
			t, _, _, E = integrate(step, r0, v0, dt, T, mu)
			plt.plot(t, E - E[0], label=f"dt={dt}")
		plt.xlabel("t")
		plt.ylabel("ΔE")
		plt.title(f"{name}")
		plt.legend()
	plt.tight_layout()
	plt.savefig(os.path.join(out, "energy_comparison.png"))
	plt.close()

	# Tabla de errores
	print("\nMax |ΔE| por método y dt:")
	print("-" * 45)
	print(f"{'Método':15s} {'dt':8s} {'max|ΔE|':15s}")
	print("-" * 45)
	for name, step in methods:
		for dt in dts:
			_, _, _, E = integrate(step, r0, v0, dt, T, mu)
			print(f"{name:15s} {dt:8.3f} {np.max(np.abs(E-E[0])):15.3e}")

if __name__ == "__main__":
	main()