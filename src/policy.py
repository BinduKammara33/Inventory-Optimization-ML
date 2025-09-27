import numpy as np
from scipy.stats import norm

def safety_stock(mean_d, var_d, mean_L, var_L, csl):
    """
    Calculate safety stock given demand and lead time variability.
    """
    var_LTD = mean_L * var_d + (mean_d ** 2) * var_L
    sigma_LTD = np.sqrt(var_LTD)
    z = norm.ppf(csl)
    return z * sigma_LTD

def reorder_point(mean_d, mean_L, ss):
    """
    Reorder point = mean lead time demand + safety stock.
    """
    return mean_d * mean_L + ss

def eoq(K, D_annual, h):
    """
    Economic Order Quantity (EOQ).
    """
    return np.sqrt(2 * K * D_annual / h)
