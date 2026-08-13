import csv
import numpy as np

data_file = input("Enter the path to the raw session .csv file: ")
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

    # find where loading ends and release begins
    peak_index = np.argmax(displacement_arr)

    peak_displacement = displacement_arr[peak_index]
    peak_force = force_arr[peak_index]

    stiffness = peak_force / peak_displacement if peak_displacement > 0 else None

    #print("Stiffness:", stiffness)

    # split into two halves at the peak
    loading_displacement = displacement_arr[:peak_index + 1]
    loading_force = force_arr[:peak_index + 1]

    release_displacement = displacement_arr[peak_index:]
    release_force = force_arr[peak_index:]

    energy_stored = np.trapezoid(loading_force, loading_displacement)
    energy_returned = abs(np.trapezoid(release_force, release_displacement))

    #print("Energy stored:", energy_stored)
    #print("Energy returned:", energy_returned)

    #print("Energy return percentage:", 100 * energy_returned / energy_stored, "%")

    return stiffness, energy_stored, energy_returned, 100 * energy_returned / energy_stored

def findShoe(brand, model, owner): #brand not used yet
    matches = []
    with open(shoes_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["model"].strip().lower() == model.strip().lower() and \
               row["owner"].strip().lower() == owner.strip().lower():
                matches.append(row)
    return matches

def createNewShoeEntry(brand, model, owner):
    size = input("Enter shoe size: ")
    date_acquired = input("Enter date acquired (YYYY-MM-DD): ")
    notes = input("Enter any notes for this shoe (optional): ")

    with open(shoes_file) as f:
        reader = csv.DictReader(f)
        existing_ids = [int(row["shoe_id"]) for row in reader]
        new_shoe_id = max(existing_ids) + 1 if existing_ids else 1

    # ensure the file ends with a newline before appending
    ensureTrailingNewline(shoes_file)

    with open(shoes_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([new_shoe_id, brand, model, size, owner, date_acquired, notes])

    print(f"New shoe entry created with ID: {new_shoe_id}")
    return new_shoe_id


stiffness, energy_stored, energy_returned, energy_return_pct = calculateEnergyReturn(data_file)

tested = input("Has the shoe been tested before on this machine? (y/n): ").strip().lower()
brand = input("Brand: ")
model = input("Shoe model: ")
owner = input("Owner: ")
found_shoe_id = None

if tested == "y":
    matches = findShoe(brand, model, owner)

    if len(matches) == 0:
        print("No existing shoe found — creating a new entry.")
        found_shoe_id = createNewShoeEntry(brand, model, owner)
    elif len(matches) == 1:
        shoe_id = matches[0]["shoe_id"]
        brand = matches[0]["brand"]
        model = matches[0]["model"]
        owner = matches[0]["owner"]
        size = matches[0]["size"]
        date_acquired = matches[0]["date_acquired"]
        notes = matches[0]["notes"]
        found_shoe_id = shoe_id
        print("Found shoe ID:", found_shoe_id)
    else:
        print("Multiple matches found:")
        for i, m in enumerate(matches):
            print(f"{i+1}: {m['shoe_id']} (size {m['size']}, acquired {m['date_acquired']})")
        choice = int(input("Select a number: "))
        shoe_id = matches[choice - 1]["shoe_id"]
        brand = matches[choice - 1]["brand"]
        model = matches[choice - 1]["model"]
        owner = matches[choice - 1]["owner"]
        size = matches[choice - 1]["size"]
        date_acquired = matches[choice - 1]["date_acquired"]
        notes = matches[choice - 1]["notes"]
        found_shoe_id = shoe_id

    print("\nShoe details:\nID-", found_shoe_id,"\nBrand-", brand, "\nModel-", model, "\nOwner-", owner, "\nSize-", size, "\nDate Acquired-", date_acquired, "\nNotes-", notes)
else:
    found_shoe_id = createNewShoeEntry(brand, model, owner)

mileage = input("\nEnter mileage (in miles) to date: ")
test_date = input("Enter test date (YYYY-MM-DD): ")
notes = input("Enter any notes for this session (optional): ")

with open(sessions_file)as f:
    reader = csv.DictReader(f)
    existing_ids = [int(row["session_id"]) for row in reader]
    new_session_id = max(existing_ids) + 1 if existing_ids else 1

# ensure the file ends with a newline before appending
ensureTrailingNewline(sessions_file)

with open(sessions_file, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([new_session_id, found_shoe_id, mileage, test_date, energy_stored, energy_returned, energy_return_pct, stiffness, notes])

print(f"\nSession data saved with ID: {new_session_id}")