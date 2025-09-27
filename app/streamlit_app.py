import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from src.policy import safety_stock, reorder_point, eoq
from src.simulate import simulate
from src.evaluate import evaluate

st.title(" Inventory Optimization with ML")

# ℹ️ Explanations
st.markdown("""
**Reorder Point (R):** When stock falls to this level, we reorder.  
**Order Quantity (Q):** How much to order each time.  
**Safety Stock (SS):** Buffer to protect against uncertainty in demand/lead time.  
**Cycle Service Level (CSL):** The probability of not stocking out in a cycle.  
""")

# --- User inputs ---
K = st.number_input("Order cost (K)", 50)
h = st.number_input("Holding cost (h)", 2.0)
csl = st.slider("Target CSL", 0.80, 0.99, 0.95)
L = st.number_input("Lead time (days)", 2)

# --- Load demand ---
df = pd.read_csv("data/demand.csv", parse_dates=["date"])
demand = df['demand'].values
mean_d, var_d = demand.mean(), demand.var()
mean_L, var_L = L, 0  # assume fixed lead time

# --- Policy calculations ---
ss = safety_stock(mean_d, var_d, mean_L, var_L, csl)
R = reorder_point(mean_d, mean_L, ss)
Q = eoq(K, mean_d * 365, h)

# --- Simulation ---
results = simulate(demand, R, Q, L, K, h)
metrics = evaluate(results, demand.sum())

# --- Show outputs ---
st.write("### Inventory Policy")
st.write(f"Reorder Point (R) = {R:.1f}")
st.write(f"Order Quantity (Q) = {Q:.1f}")

st.write("### Results")
st.json(metrics)

# --- Inventory simulation chart ---
st.write("### Inventory Simulation")
df_inv = pd.DataFrame({
    "date": df["date"],
    "Inventory": results["inventory_trace"],
    "Demand": df["demand"].values
})
st.line_chart(df_inv.set_index("date"))

st.markdown("""
📦 **Interpretation of the Inventory Simulation**  
- Inventory **drops as demand is consumed** and **rises when new orders arrive**.  
- If inventory hits zero, stockouts occur (bad service level).  
- This helps managers see whether the chosen (Q, R) policy is effective.  
""")

# --- Cost vs Service Level curve ---
st.write("### Cost vs Service Level Curve")
levels = [0.85, 0.90, 0.95, 0.98, 0.99]
curve = []
for lvl in levels:
    ss_lvl = safety_stock(mean_d, var_d, mean_L, var_L, lvl)
    R_lvl = reorder_point(mean_d, mean_L, ss_lvl)
    results_lvl = simulate(demand, R_lvl, Q, L, K, h)
    m = evaluate(results_lvl, demand.sum())
    curve.append((lvl, m["Total Cost"], m["Service Level"]))

df_curve = pd.DataFrame(curve, columns=["Target CSL", "Total Cost", "Service Level"])
st.line_chart(df_curve.set_index("Target CSL")[["Total Cost", "Service Level"]])

st.markdown("""
📊 **Interpretation of the Cost vs Service Level Curve**  
- As the **Cycle Service Level (CSL)** increases, the **safety stock** and thus the total cost also increase.  
- Managers can use this curve to **choose the right balance**:  
  - Higher CSL = fewer stockouts but more cost.  
  - Lower CSL = lower cost but higher risk of stockouts.  
- The goal is to pick a CSL that matches **business priorities** (e.g., 98% for critical spare parts, 90% for low-value items).  
""")

# --- Demand chart ---
st.write("### Historical Demand")
st.line_chart(df.set_index("date")["demand"])

# --- ML Forecast vs Actual (optional) ---
try:
    from src.models import train_demand_model
    model, X_test, y_test = train_demand_model(df.copy())
    forecast = model.predict(X_test)

    st.write("### Forecast vs Actual Demand")
    chart_data = pd.DataFrame({
        "Actual": y_test.values,
        "Forecast (95% quantile)": forecast
    })
    st.line_chart(chart_data)

     

except Exception as e:
    st.info(f"ML forecasting not available: {e}")
