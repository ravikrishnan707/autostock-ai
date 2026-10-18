
# ==================================================
# AutoStock AI
# Automobile Spare Parts Stockout Monitoring System
# ==================================================

parts = [
    {"id": "AP001", "name": "Brake Pad", "stock": 25, "daily_demand": 8},
    {"id": "AP002", "name": "Oil Filter", "stock": 60, "daily_demand": 5},
    {"id": "AP003", "name": "Wheel Bearing", "stock": 12, "daily_demand": 4},
    {"id": "AP004", "name": "Spark Plug", "stock": 15, "daily_demand": 6},
    {"id": "AP005", "name": "Wheel Cylinder", "stock": 40, "daily_demand": 3},
    {"id": "AP006", "name": "Air Filter", "stock": 35, "daily_demand": 4},
    {"id": "AP007", "name": "Clutch Plate", "stock": 18, "daily_demand": 3},
    {"id": "AP008", "name": "Brake Disc", "stock": 22, "daily_demand": 5},
    {"id": "AP009", "name": "Fuel Pump", "stock": 10, "daily_demand": 2},
    {"id": "AP010", "name": "Radiator Hose", "stock": 45, "daily_demand": 4},
    {"id": "AP011", "name": "Alternator", "stock": 8, "daily_demand": 2},
    {"id": "AP012", "name": "Starter Motor", "stock": 14, "daily_demand": 3},
    {"id": "AP013", "name": "Timing Belt", "stock": 20, "daily_demand": 2},
    {"id": "AP014", "name": "Water Pump", "stock": 16, "daily_demand": 3},
    {"id": "AP015", "name": "Engine Mount", "stock": 30, "daily_demand": 2},
    {"id": "AP016", "name": "Shock Absorber", "stock": 24, "daily_demand": 4},
    {"id": "AP017", "name": "Suspension Ball Joint", "stock": 18, "daily_demand": 3},
    {"id": "AP018", "name": "Tie Rod End", "stock": 28, "daily_demand": 4},
    {"id": "AP019", "name": "Clutch Release Bearing", "stock": 12, "daily_demand": 2},
    {"id": "AP020", "name": "Transmission Filter", "stock": 32, "daily_demand": 3},
    {"id": "AP021", "name": "Fuel Injector", "stock": 15, "daily_demand": 4},
    {"id": "AP022", "name": "Engine Gasket", "stock": 50, "daily_demand": 5},
    {"id": "AP023", "name": "Headlight Assembly", "stock": 20, "daily_demand": 2},
    {"id": "AP024", "name": "Tail Light", "stock": 26, "daily_demand": 3},
    {"id": "AP025", "name": "Windshield Wiper", "stock": 40, "daily_demand": 5},
    {"id": "AP026", "name": "Radiator", "stock": 9, "daily_demand": 1},
    {"id": "AP027", "name": "AC Compressor", "stock": 11, "daily_demand": 2},
    {"id": "AP028", "name": "Battery", "stock": 18, "daily_demand": 3},
    {"id": "AP029", "name": "Door Handle", "stock": 55, "daily_demand": 4},
    {"id": "AP030", "name": "Power Window Motor", "stock": 13, "daily_demand": 2},
]


def calculate_stockout_risk(part):
    stock = part["stock"]
    demand = part["daily_demand"]

    if demand <= 0:
        return None, "NO DEMAND"

    days_left = stock / demand

    if days_left <= 3:
        risk = "HIGH"
    elif days_left <= 7:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return days_left, risk


def main():
    print("=" * 65)
    print("AUTOSTOCK AI")
    print("Automobile Spare Parts Stockout Monitoring System")
    print("=" * 65)

    high_risk = 0
    medium_risk = 0
    low_risk = 0

    for part in parts:
        days_left, risk = calculate_stockout_risk(part)

        print(f"\nPart ID       : {part['id']}")
        print(f"Part Name     : {part['name']}")
        print(f"Current Stock : {part['stock']} units")
        print(f"Daily Demand  : {part['daily_demand']} units")

        if days_left is not None:
            print(f"Stock Remaining: {days_left:.1f} days")

        print(f"Stockout Risk : {risk}")
        print("-" * 40)

        if risk == "HIGH":
            high_risk += 1
        elif risk == "MEDIUM":
            medium_risk += 1
        elif risk == "LOW":
            low_risk += 1

    print("\n" + "=" * 65)
    print("INVENTORY SUMMARY")
    print("=" * 65)
    print(f"Total spare parts : {len(parts)}")
    print(f"High-risk parts   : {high_risk}")
    print(f"Medium-risk parts : {medium_risk}")
    print(f"Low-risk parts    : {low_risk}")
    print("=" * 65)


if __name__ == "__main__":
    main()
