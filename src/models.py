import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split

def train_demand_model(df):
    """
    Train a simple LightGBM quantile regression model
    to forecast demand using lag and rolling window features.
    """

    # --- Feature Engineering ---
    df = df.copy()
    df["lag1"] = df["demand"].shift(1)
    df["roll7"] = df["demand"].shift(1).rolling(7).mean()
    df["roll14"] = df["demand"].shift(1).rolling(14).mean()

    # Drop missing rows from rolling/lag
    df = df.dropna()

    # Features (X) and target (y)
    X = df[["lag1", "roll7", "roll14"]]
    y = df["demand"]

    # --- Train-test split ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, shuffle=False, test_size=0.2
    )

    # --- LightGBM Quantile Regression ---
    model = lgb.LGBMRegressor(
        objective="quantile", 
        alpha=0.95,   # 95th percentile forecast
        n_estimators=50,
        num_leaves=7,
        min_data_in_leaf=5,
        learning_rate=0.1,
        verbosity=-1
    )
    model.fit(X_train, y_train)

    return model, X_test, y_test
