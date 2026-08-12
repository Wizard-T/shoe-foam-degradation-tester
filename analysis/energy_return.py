import csv
import numpy as np
import matplotlib.pyplot as plt

displacement = []
force = []

with open(r"C:\Users\templ\OneDrive\Desktop\shoe-foam-degradation-tester\data\dummy data\test_session_known-values.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        displacement.append(float(row["displacement_mm"]))
        force.append(float(row["force_g"]))

displacement_arr = np.array(displacement)
force_arr = np.array(force)

# find where loading ends and release begins
peak_index = np.argmax(displacement_arr)

# split into two halves at the peak
loading_displacement = displacement_arr[:peak_index + 1]
loading_force = force_arr[:peak_index + 1]

release_displacement = displacement_arr[peak_index:]
release_force = force_arr[peak_index:]

energy_stored = np.trapezoid(loading_force, loading_displacement)
energy_returned = abs(np.trapezoid(release_force, release_displacement))

print("Energy stored:", energy_stored)
print("Energy returned:", energy_returned)

print("Energy return ratio:", 100* energy_returned / energy_stored,"%")