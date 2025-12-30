from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import matplotlib.pyplot as plt
import polars as pl
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

# Pro-Tip: Accuracy is misleading on imbalanced data (e.g., 99% healthy sensors); focus on precision/recall/F1. Logistic loss mirrors physics: it's the negative log-likelihood shaping the decision boundary.


@dataclass
class SensorDataset:
    features: list[str]
    target: str = "faulty"


def load_data(path: str, dataset: SensorDataset) -> Tuple[pl.DataFrame, pl.DataFrame]:
    df = pl.read_csv(path)
    if dataset.target not in df.columns:
        raise ValueError(f"missing target column: {dataset.target}")
    return df.select(dataset.features + [dataset.target]), df


def train_model(df: pl.DataFrame, dataset: SensorDataset) -> Tuple[LogisticRegression, list[int], list[int]]:
    X = df.select(dataset.features).to_numpy()
    y = df.select(dataset.target).to_series().to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return model, y_test.tolist(), y_pred.tolist()


def evaluate(y_true: list[int], y_pred: list[int]) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    print("Confusion matrix:\n", cm)
    print(f"Precision: {prec:.4f}, Recall: {rec:.4f}, F1: {f1:.4f}")
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["healthy", "faulty"])
    disp.plot()
    plt.title("Sensor Fault Classification")
    plt.tight_layout()
    plt.show()


def main() -> None:
    dataset = SensorDataset(features=["temperature", "pressure", "vibration_level"], target="target_churn")
    df_selected, _ = load_data("ml/sensor_data.csv", dataset)
    model, y_true, y_pred = train_model(df_selected, dataset)
    evaluate(y_true, y_pred)


if __name__ == "__main__":
    main()

