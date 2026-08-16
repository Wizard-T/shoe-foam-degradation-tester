import csv
import numpy as np
from datetime import date

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

def createNewShoeEntry(owner=None):
    if owner is None:
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
    return {
        "shoe_id": new_shoe_id, "brand": brand, "model": model,
        "size": size, "owner": owner, "date_acquired": date_acquired, "notes": notes
    }

def listShoesByOwner(owner):
    with open(shoes_file) as f:
        reader = csv.DictReader(f)
        shoes = [row for row in reader if row["owner"].strip().lower() == owner.strip().lower()]
    return shoes

def listOwners():
    with open(shoes_file) as f:
        reader = csv.DictReader(f)
        seen = {}
        for row in reader:
            name = row["owner"].strip()
            if name and name.lower() not in seen:
                seen[name.lower()] = name  # keep first-seen casing
        return list(seen.values())

def findMatchingOwners(name_input, owners):
    input_words = set(name_input.strip().lower().split())
    exact_matches = []
    partial_matches = []

    for owner in owners:
        owner_words = set(owner.strip().lower().split())
        if name_input.strip().lower() == owner.strip().lower():
            exact_matches.append(owner)
        elif input_words & owner_words:  # any shared word (first name, last name, etc.)
            partial_matches.append(owner)

    return exact_matches, partial_matches

def selectOwner():
    owners = listOwners()
    name_input = input("Shoe owner name: ")

    exact_matches, partial_matches = findMatchingOwners(name_input, owners)

    if len(exact_matches) == 1:
        return exact_matches[0]

    if len(partial_matches) == 0:
        print(f"No matching owners found for '{name_input}'.")
        choice = input("Type 'n' to use this as a new owner name, or press Enter to try again: ").strip().lower()
        if choice == "n":
            return name_input
        else:
            return selectOwner()

    print("\nPossible matches:")
    for i, o in enumerate(partial_matches):
        print(f"{i+1}: {o}")
    print(f"{len(partial_matches)+1}: None of these — re-enter name")
    print(f"{len(partial_matches)+2}: Use '{name_input}' as a new owner")

    choice = int(input("Select a number: "))
    if 1 <= choice <= len(partial_matches):
        return partial_matches[choice - 1]
    elif choice == len(partial_matches) + 1:
        return selectOwner()
    elif choice == len(partial_matches) + 2:
        return name_input
    else:
        print("Invalid selection, please try again.")
        return selectOwner()

def selectShoe():
    owner = selectOwner()
    shoes = listShoesByOwner(owner)

    if len(shoes) == 0:
        print("No shoes on file for this owner.")
        return None, owner

    while True:
        print("\nExisting shoes:")
        for i, s in enumerate(shoes):
            print(f"{i+1}: {s['brand']} {s['model']} (size {s['size']})")
        print(f"{len(shoes)+1}: None of these — enter a new shoe")
        print(f"{len(shoes)+2}: More details about a shoe (view notes, date acquired, etc.)")

        choice = int(input("Select a number: "))

        if 1 <= choice <= len(shoes):
            return shoes[choice - 1], owner
        elif choice == len(shoes) + 1:
            return None, owner
        elif choice == len(shoes) + 2:
            shoe_index = int(input("Enter the number of the shoe to view details: ")) - 1
            if 0 <= shoe_index < len(shoes):
                s = shoes[shoe_index]
                print("\nShoe details:")
                print(f"ID: {s['shoe_id']}")
                print(f"Brand: {s['brand']}")
                print(f"Model: {s['model']}")
                print(f"Size: {s['size']}")
                print(f"Owner: {s['owner']}")
                print(f"Date Acquired: {s['date_acquired']}")
                print(f"Notes: {s['notes']}\n")
            else:
                print("Invalid selection.")
            # loop back to the menu — no re-prompt for owner
        else:
            print("Invalid selection, please try again.")
            # loop back to the menu


# --- main flow ---

stiffness, energy_stored, energy_returned, energy_return_pct = calculateEnergyReturn(data_file)

selected_shoe, owner = selectShoe()

if selected_shoe is None:
    selected_shoe = createNewShoeEntry(owner)

found_shoe_id = selected_shoe["shoe_id"]
brand = selected_shoe["brand"]
model = selected_shoe["model"]
size = selected_shoe["size"]
date_acquired = selected_shoe["date_acquired"]
notes = selected_shoe["notes"]
print("\nShoe details:\nID-", found_shoe_id, "\nBrand-", brand, "\nModel-", model,
      "\nOwner-", owner, "\nSize-", size, "\nDate Acquired-", date_acquired, "\nNotes-", notes)

mileage = input("\nEnter mileage (in miles) to date: ")
test_date = input("Enter test date (YYYY-MM-DD) or 'today': ").strip().lower()
if test_date == "today":
    test_date = date.today().isoformat()
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

print("\n" + "="*40)
print("SESSION REPORT")
print("="*40)
print(f"Session ID:       {new_session_id}")
print(f"Shoe ID:          {found_shoe_id}")
print(f"Shoe:             {brand} {model} (size {size})")
print(f"Mileage:          {mileage}")
print(f"Test date:        {test_date}")
print(f"Stiffness:        {stiffness:.2f}")
print(f"Energy stored:    {energy_stored:.2f}")
print(f"Energy returned:  {energy_returned:.2f}")
print(f"Energy return %:  {energy_return_pct:.2f}%")
print(f"Session notes:    {session_notes if session_notes else '(none)'}")
print("="*40)