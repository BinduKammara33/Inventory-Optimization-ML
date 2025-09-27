def evaluate(results, demand_total):
    """
    Evaluate performance of inventory policy.
    """
    service_level = 1 - results['stockouts'] / demand_total
    return {
        "Total Cost": round(results['total'], 2),
        "Holding Cost": round(results['holding'], 2),
        "Ordering Cost": round(results['ordering'], 2),
        "Orders": results['orders'],
        "Service Level": round(service_level, 3)
    }
