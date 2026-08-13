import csv
import numpy as np
import matplotlib.pyplot as plt

displacement = []
force = []

file = r"C:\Users\templ\OneDrive\Desktop\shoe-foam-degradation-tester\data\dummy data\dummy_output_1.csv"

with open(file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        displacement.append(float(row["displacement_mm"]))
        force.append(float(row["force_g"]))

displacement_arr = np.array(displacement)
force_arr = np.array(force)

# find where loading ends and release begins
peak_index = np.argmax(displacement_arr)

peak_displacement = displacement_arr[peak_index]
peak_force = force_arr[peak_index]

stiffness = peak_force / peak_displacement if peak_displacement > 0 else None

print("Stiffness:", stiffness)

# split into two halves at the peak
loading_displacement = displacement_arr[:peak_index + 1]
loading_force = force_arr[:peak_index + 1]

release_displacement = displacement_arr[peak_index:]
release_force = force_arr[peak_index:]

energy_stored = np.trapezoid(loading_force, loading_displacement)
energy_returned = abs(np.trapezoid(release_force, release_displacement))

print("Energy stored:", energy_stored)
print("Energy returned:", energy_returned)

print("Energy return percentage:", 100* energy_returned / energy_stored,"%")


release_displacement_sorted = release_displacement[::-1]
release_force_sorted = release_force[::-1]

release_displacement_sorted = release_displacement[::-1]
release_force_sorted = release_force[::-1]

# resample release curve onto loading_displacement's x-values
release_force_interp = np.interp(loading_displacement, release_displacement_sorted, release_force_sorted)

plt.fill_between(loading_displacement, loading_force, release_force_interp,
                  alpha=0.2, label="Hysteresis loss", zorder=1)
plt.plot(loading_displacement, loading_force, label="Compression (loading)", zorder=2)
plt.plot(release_displacement, release_force, label="Release (unloading)", zorder=2)
plt.xlabel("Displacement (mm)")
plt.ylabel("Force (g)")
plt.title("Force vs. Displacement")
plt.legend()
plt.show()