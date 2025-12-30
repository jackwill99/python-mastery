from datetime import datetime, timedelta

import numpy as np
import polars as pl


def generate_ml_data(n_rows: int = 10000):
    # Generating synthetic Physics-based sensor data
    np.random.seed(42)
    
    data = {
        "timestamp": [datetime.now() - timedelta(minutes=i) for i in range(n_rows)],
        "sensor_id": np.random.choice(["A1", "B2", "C3", "D4"], n_rows),
        "temperature": np.random.normal(25, 5, n_rows), # Mean 25, StdDev 5
        "pressure": np.random.normal(1013, 20, n_rows),
        "vibration_level": np.random.uniform(0, 1, n_rows),
        "plan_type": np.random.choice(["Basic", "Premium", "Enterprise"], n_rows),
        "target_churn": np.random.choice([0, 1], n_rows, p=[0.8, 0.2]) # 20% churn rate
    }
    
    df = pl.DataFrame(data)
    df.write_csv("ml/sensor_data.csv")
    print(f"✅ Successfully generated {n_rows} rows at 'ml/sensor_data.csv'")

if __name__ == "__main__":
    generate_ml_data()