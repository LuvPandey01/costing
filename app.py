from flask import Flask, request, jsonify
from itertools import permutations

app = Flask(__name__)

# Distances from each center to others and to L1
distances = {
    'C1': {'C2': 4, 'C3': 3, 'L1': 3},
    'C2': {'C1': 4, 'C3': 5.5, 'L1': 2.5},
    'C3': {'C1': 3, 'C2': 5.5, 'L1': 2},
    'L1': {'C1': 3, 'C2': 2.5, 'C3': 2}
}

# Refined and validated product weights per center
product_weights = {
    'A': {'C1': 3, 'C2': 0, 'C3': 0},
    'B': {'C1': 2, 'C2': 0, 'C3': 0},
    'C': {'C1': 8, 'C2': 0, 'C3': 0},
    'D': {'C1': 0, 'C2': 12, 'C3': 0},
    'E': {'C1': 0, 'C2': 25, 'C3': 0},
    'F': {'C1': 0, 'C2': 15, 'C3': 0},
    'G': {'C1': 0, 'C2': 0, 'C3': 0.3},
    'H': {'C1': 0, 'C2': 0, 'C3': 0.7},
    'I': {'C1': 0, 'C2': 0, 'C3': 1.4}
}

def calculate_segment_cost(weight, distance):
    """Calculate delivery cost based on weight tiers"""
    if weight <= 5:
        return 10 * distance
    extra_blocks = (weight - 5) // 5 + (1 if (weight - 5) % 5 > 0 else 0)
    return (10 * distance) + (8 * distance * extra_blocks)

def calculate_minimum_cost(order):
    required_centers = set()
    weights = {'C1': 0, 'C2': 0, 'C3': 0}

    # Collect weight per center
    for product, quantity in order.items():
        for center, w in product_weights.get(product, {}).items():
            if w > 0:
                weights[center] += w * quantity
                required_centers.add(center)

    if not required_centers:
        return 0

    min_cost = float('inf')

    for start_center in required_centers:
        for perm in permutations(required_centers - {start_center}):
            total_cost = 0
            current_location = start_center

            # Initial delivery from start center
            if weights[start_center] > 0:
                total_cost += calculate_segment_cost(weights[start_center], distances[start_center]['L1'])
                current_location = 'L1'

            # Pickup and delivery from remaining centers
            for center in perm:
                total_cost += calculate_segment_cost(0, distances[current_location][center])
                total_cost += calculate_segment_cost(weights[center], distances[center]['L1'])
                current_location = 'L1'

            min_cost = min(min_cost, total_cost)

    return round(min_cost, 2)

@app.route('/calculate-delivery-cost', methods=['POST'])
def delivery_cost_api():
    try:
        order = request.get_json()
        if not isinstance(order, dict):
            return jsonify({"error": "Invalid input format"}), 400
        cost = calculate_minimum_cost(order)
        return jsonify({"min_cost": cost})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
