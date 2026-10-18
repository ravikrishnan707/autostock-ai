
import random
from pathlib import Path

import pandas as pd

# Make the generated data reproducible
random.seed(42)

# Find the project and output folders
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Automobile spare parts catalog
part_names = [
    "Brake Pad", "Oil Filter", "Air Filter", "Fuel Filter",
    "Spark Plug", "Ignition Coil", "Wheel Bearing", "Clutch Plate",
    "Clutch Cable", "Radiator", "Radiator Fan", "Water Pump",
    "Engine Mount", "Shock Absorber", "Suspension Ball Joint",
    "Tie Rod End", "Steering Rack", "Control Arm", "Drive Belt",
    "Timing Belt", "Alternator", "Starter Motor", "Battery",
    "Headlight Assembly", "Tail Light", "Fog Lamp", "Windshield Wiper",
    "Wiper Motor", "Side Mirror", "Door Handle", "Power Window Motor",
    "Window Regulator", "Door Lock", "Bumper", "Grille",
    "Engine Gasket", "Cylinder Head", "Piston Ring", "Fuel Injector",
    "Throttle Body", "Oxygen Sensor", "Air Flow Sensor", "ABS Sensor",
    "Brake Disc", "Brake Caliper", "Brake Shoe", "Master Cylinder",
    "Wheel Cylinder", "Brake Hose", "Handbrake Cable",
    "Gearbox Mount", "Transmission Filter", "CV Joint",
    "Drive Shaft", "Axle Shaft", "Differential Gear", "Gear Lever",
    "Gear Cable", "Exhaust Pipe", "Catalytic Converter", "Muffler",
    "AC Compressor", "AC Condenser", "AC Filter", "Blower Motor",
    "Thermostat", "Coolant Hose", "Engine Oil Pump", "Oil Pan",
    "Oil Seal", "Valve Cover", "Intake Manifold", "Exhaust Manifold",
    "Turbocharger", "Intercooler", "Diesel Injector", "Glow Plug",
    "Power Steering Pump", "Steering Column", "Horn", "Relay",
    "Fuse Box", "Wiring Harness", "ECU Module", "Parking Sensor",
    "Reverse Camera", "Seat Belt", "Seat Adjuster", "Fuel Pump",
    "Fuel Tank", "Fuel Cap", "Engine Valve", "Camshaft",
    "Crankshaft", "Flywheel", "Piston", "Connecting Rod",
    "Engine Chain", "Suspension Spring", "Strut Mount",
    "Wheel Hub"
]

warehouses = [
    "Chennai", "Bengaluru", "Hyderabad", "Coimbatore", "Pune"
]

suppliers = [
    "Supplier_A", "Supplier_B", "Supplier_C", "Supplier_D",
    "Supplier_E", "Supplier_F", "Supplier_G", "Supplier_H",
    "Supplier_I", "Supplier_J"
]

# Generate one inventory record per spare part
records = []

for index, part_name in enumerate(part_names, start=1):
    daily_demand = random.randint(2, 25)
    stock = random.randint(10, 250)
    warehouse = random.choice(warehouses)
    supplier = random.choice(suppliers)
    lead_time_days = random.randint(2, 14)
    unit_cost = round(random.uniform(100, 15000), 2)

    days_remaining = round(stock / daily_demand, 2)

    if days_remaining <= 3:
        risk = "HIGH"
    elif days_remaining <= 7:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    records.append({
        "part_id": f"P{index:03d}",
        "part_name": part_name,
        "warehouse": warehouse,
        "supplier": supplier,
        "stock": stock,
        "daily_demand": daily_demand,
        "lead_time_days": lead_time_days,
        "unit_cost": unit_cost,
        "days_remaining": days_remaining,
        "stockout_risk": risk
    })

# Convert records to a table
df = pd.DataFrame(records)

# Save the inventory dataset
output_file = DATA_DIR / "automobile_spare_parts.csv"
df.to_csv(output_file, index=False)

# Print a summary
print("=" * 65)
print("AUTOSTOCK AI - AUTOMOBILE SPARE PARTS DATA GENERATOR")
print("=" * 65)
print(f"Total spare parts : {len(df)}")
print(f"Warehouses        : {df['warehouse'].nunique()}")
print(f"Suppliers         : {df['supplier'].nunique()}")
print(f"High-risk parts   : {(df['stockout_risk'] == 'HIGH').sum()}")
print(f"Medium-risk parts : {(df['stockout_risk'] == 'MEDIUM').sum()}")
print(f"Low-risk parts    : {(df['stockout_risk'] == 'LOW').sum()}")
print(f"\nSaved dataset to: {output_file}")
print("\nFirst 10 inventory records:")
print(df.head(10).to_string(index=False))
