def simulate(demand_series, R, Q, L, K, h):
    """
    Simulate inventory system under (Q, R) policy
    and track inventory levels over time.
    """
    on_hand = 0
    pipeline = []  # list of (arrival_day, qty)
    cost_holding, cost_order, stockouts = 0, 0, 0
    orders = 0
    inventory_trace = []

    for day, demand in enumerate(demand_series):
        # Receive arrivals
        arrivals = [q for d, q in pipeline if d == day]
        on_hand += sum(arrivals)
        pipeline = [(d, q) for d, q in pipeline if d > day]

        # Demand
        sales = min(on_hand, demand)
        stockouts += max(0, demand - sales)
        on_hand -= sales

        # Holding cost
        cost_holding += h * on_hand

        # Reorder
        if on_hand <= R:
            pipeline.append((day + L, Q))
            cost_order += K
            orders += 1

        # Track inventory each day
        inventory_trace.append(on_hand)

    return dict(
        holding=cost_holding,
        ordering=cost_order,
        stockouts=stockouts,
        total=cost_holding + cost_order,
        orders=orders,
        inventory_trace=inventory_trace  # ✅ added
    )
