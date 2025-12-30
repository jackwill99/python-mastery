from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Pro-Tip: Similar to NestJS/Dart service classes, wrapping feature prep in a reusable pipeline class keeps concerns separated and testable.

PlanType = Literal["free", "pro", "enterprise"]


@dataclass
class DataPipeline:
    numeric_cols: list[str]
    categorical_cols: list[str]

    def build(self) -> Pipeline:
        numeric_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse=False)),
            ]
        )
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_pipeline, self.numeric_cols),
                ("cat", categorical_pipeline, self.categorical_cols),
            ]
        )
        return Pipeline(steps=[("preprocess", preprocessor)])

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        pipeline = self.build()
        return pipeline.fit_transform(df)

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        pipeline = self.build()
        return pipeline.transform(df)


def demo() -> None:
    df = pd.DataFrame(
        [
            {"user_id": "u1", "plan": "free", "usage_hours": 3.5, "tickets": 1},
            {"user_id": "u2", "plan": "pro", "usage_hours": None, "tickets": 0},
            {"user_id": "u3", "plan": "enterprise", "usage_hours": 12.0, "tickets": 5},
        ]
    )
    pipeline = DataPipeline(numeric_cols=["usage_hours", "tickets"], categorical_cols=["plan"])
    features = pipeline.fit_transform(df)
    print("Transformed shape:", features.shape)


if __name__ == "__main__":
    demo()

