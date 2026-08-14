import csv
import numpy as np

data_file = "C:\\Users\\templ\\OneDrive\\Desktop\\shoe-foam-degradation-tester\\data\\dummy data\\dummy_output_1.csv" #input("Enter the path to the raw session .csv file: ")
shoes_file = "C:\\Users\\templ\\OneDrive\\Desktop\\shoe-foam-degradation-tester\\data\\results\\shoes.csv"
sessions_file = "C:\\Users\\templ\\OneDrive\\Desktop\\shoe-foam-degradation-tester\\data\\results\\sessions.csv"

def ensureTrailingNewline(filepath):
    with open(filepath, 'rb+') as f:
        f.seek(-1, 2)
        if f.read(1) != b'\n':
            f.write(b'\n')

def calculateEnergyReturn(file):
    displacement = []
    force = []
    with open(file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            displacement.append(float(row["displacement_mm"]))
            force.append(float(row["force_g"]))

    displacement_arr = np.array(displacement)
    force_arr = np.array(force)

    peak_index = np.argmax(displacement_arr)
    peak_displacement = displacement_arr[peak_index]
    peak_force = force_arr[peak_index]

    stiffness = peak_force / peak_displacement if peak_displacement > 0 else None

    loading_displacement = displacement_arr[:peak_index + 1]
    loading_force = force_arr[:peak_index + 1]
    release_displacement = displacement_arr[peak_index:]
    release_force = force_arr[peak_index:]

    energy_stored = np.trapezoid(loading_force, loading_displacement)
    energy_returned = abs(np.trapezoid(release_force, release_displacement))

    return stiffness, energy_stored, energy_returned, 100 * energy_returned / energy_stored

def createNewShoeEntry():
    owner = input("Owner name: ")
    brand = input("Brand: ")
    model = input("Shoe model: ")
    size = input("Enter shoe size: ")
    date_acquired = input("Enter date acquired (YYYY-MM-DD): ")
    notes = input("Enter any notes for this shoe (optional): ")

    with open(shoes_file) as f:
        reader = csv.DictReader(f)
        existing_ids = [int(row["shoe_id"]) for row in reader]
        new_shoe_id = max(existing_ids) + 1 if existing_ids else 1

    ensureTrailingNewline(shoes_file)

    with open(shoes_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([new_shoe_id, brand, model, size, owner, date_acquired, notes])

    print(f"New shoe entry created with ID: {new_shoe_id}")
    return new_shoe_id

def listShoesByOwner(owner):
    with open(shoes_file) as f:
        reader = csv.DictReader(f)
        shoes = [row for row in reader if row["owner"].strip().lower() == owner.strip().lower()]
    return shoes

def selectShoe():
    owner = input("Owner name: ")
    shoes = listShoesByOwner(owner)

    if len(shoes) == 0:
        print("No shoes on file for this owner.")
        return None, owner

    print("\nExisting shoes:")
    for i, s in enumerate(shoes):
        print(f"{i+1}: {s['brand']} {s['model']} (size {s['size']})")
    print(f"{len(shoes)+1}: None of these — enter a new shoe")
    print(f"{len(shoes)+2}: More details about a shoe (view notes, date acquired, etc.)")

    choice = int(input("Select a number: "))

    if 1 <= choice <= len(shoes):
        return shoes[choice - 1]
    elif choice == len(shoes) + 1:
        return None
    elif choice == len(shoes) + 2:
        shoe_index = int(input("Enter the number of the shoe to view details: ")) - 1
        if 0 <= shoe_index < len(shoes):
            selected_shoe = shoes[shoe_index]
            print("\nShoe details:")
            print(f"ID: {selected_shoe['shoe_id']}")
            print(f"Brand: {selected_shoe['brand']}")
            print(f"Model: {selected_shoe['model']}")
            print(f"Size: {selected_shoe['size']}")
            print(f"Owner: {selected_shoe['owner']}")
            print(f"Date Acquired: {selected_shoe['date_acquired']}")
            print(f"Notes: {selected_shoe['notes']}\n")
        else:
            print("Invalid selection.")
        return selectShoe()  # Allow the user to select again after viewing details
    else:
        print("Invalid selection, please try again.")
        return selectShoe()


# --- main flow ---

stiffness, energy_stored, energy_returned, energy_return_pct = calculateEnergyReturn(data_file)

selected_shoe = selectShoe()

if selected_shoe is None:
    found_shoe_id = createNewShoeEntry()
else:
    found_shoe_id = selected_shoe["shoe_id"]
    owner = selected_shoe["owner"]
    brand = selected_shoe["brand"]
    model = selected_shoe["model"]
    size = selected_shoe["size"]
    date_acquired = selected_shoe["date_acquired"]
    notes = selected_shoe["notes"]
    print("\nShoe details:\nID-", found_shoe_id, "\nBrand-", brand, "\nModel-", model,
          "\nOwner-", owner, "\nSize-", size, "\nDate Acquired-", date_acquired, "\nNotes-", notes)

mileage = input("\nEnter mileage (in miles) to date: ")
test_date = input("Enter test date (YYYY-MM-DD): ")
session_notes = input("Enter any notes for this session (optional): ")

with open(sessions_file) as f:
    reader = csv.DictReader(f)
    existing_ids = [int(row["session_id"]) for row in reader]
    new_session_id = max(existing_ids) + 1 if existing_ids else 1

ensureTrailingNewline(sessions_file)

with open(sessions_file, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([new_session_id, found_shoe_id, mileage, test_date, energy_stored,
                      energy_returned, energy_return_pct, stiffness, session_notes])

print(f"\nSession data saved with ID: {new_session_id}")