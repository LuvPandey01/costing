from flask import Flask, request, jsonify
import math

app = Flask(__name__)

warehouse_data = {
    "C1": {"A": 3, "B": 2, "C": 8},
    "C2": {"D": 12, "E": 25, "F": 15},
    "C3": {"G": 0.5, "H": 1, "I": 2}
}

distances_to_L1 = {"C1": 3, "C2": 2.5, "C3": 3}

inter_center_distances = {
    ("C1", "C2"): 4, ("C2", "C1"): 4,
    ("C1", "C3"): 3, ("C3", "C1"): 3,
    ("C2", "C3"): 5.5, ("C3", "C2"): 5.5
}

def get_product_weight(product, quantity):
    for center, items in warehouse_data.items():
        if product in items:
            return items[product] * quantity, center
    return 0, None

def calculate_trip_cost(weight, distance):
    if weight <= 5:
        return 10 * distance
    else:
        cost = 10 * 5
        remaining_weight = weight - 5
        extra_blocks = math.ceil(remaining_weight / 5)
        cost += extra_blocks * 8 * distance
        return cost

def split_order_by_center(order):
    center_order = {"C1": [], "C2": [], "C3": []}
    for product, qty in order.items():
        weight, center = get_product_weight(product, qty)
        if center:
            center_order[center].append((product, weight))
    return {k: v for k, v in center_order.items() if v}

def simulate_from_center(start_center, order):
    order_by_center = split_order_by_center(order)
    total_cost = 0
    current_center = start_center

    while order_by_center:
        if current_center in order_by_center:
            weight = sum(w for _, w in order_by_center[current_center])
            total_cost += calculate_trip_cost(weight, distances_to_L1[current_center])
            del order_by_center[current_center]

        if order_by_center:
            next_center = min(order_by_center.keys(),
                              key=lambda c: inter_center_distances[(current_center, c)])
            total_cost += inter_center_distances[(current_center, next_center)]
            current_center = next_center

    return total_cost

@app.route('/calculate', methods=['POST'])
def calculate():
    order = request.json
    if not order:
        return jsonify({"error": "Invalid input"}), 400

    centers = ["C1", "C2", "C3"]
    min_cost = min(simulate_from_center(center, order) for center in centers)

    return jsonify({"min_cost": round(min_cost, 2)})
