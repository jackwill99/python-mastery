from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import polars as pl
from sklearn.preprocessing import StandardScaler

# Pro-Tip: Polars pipelines keep data vectorized and schema-aware—faster and safer than JavaScript Array.reduce or Dart list transforms, while still letting you drop into scikit-learn for scaling.


@dataclass
class DataPipeline:
    numeric_cols: Sequence[str]
    categorical_cols: Sequence[str]
    target_col: str | None = None
    scaler: StandardScaler = field(default_factory=StandardScaler)
    medians: dict[str, float] = field(default_factory=dict)
    dummy_columns: list[str] = field(default_factory=list)

    def _ensure_min_rows(self, df: pl.DataFrame, minimum: int = 1000) -> None:
        if df.height < minimum:
            raise ValueError(f"dataset too small: {df.height} rows (need >= {minimum})")

    def _impute(self, df: pl.DataFrame) -> pl.DataFrame:
        if not self.medians:
            median_row = df.select([pl.col(col).median().alias(col) for col in self.numeric_cols]).row(0)
            self.medians = {col: float(val) for col, val in zip(self.numeric_cols, median_row)}
        filled = df.with_columns(
            [pl.col(col).fill_null(self.medians[col]).alias(col) for col in self.numeric_cols]
            + [pl.col(col).fill_null("missing").alias(col) for col in self.categorical_cols]
        )
        return filled

    def _encode_categoricals(self, df: pl.DataFrame) -> pl.DataFrame:
        encoded = df.to_dummies(columns=list(self.categorical_cols), drop_first=False)
        if not self.dummy_columns:
            self.dummy_columns = [
                col for col in encoded.columns if col not in self.numeric_cols and col != self.target_col
            ]
        missing = set(self.dummy_columns) - set(encoded.columns)
        if missing:
            encoded = encoded.with_columns([pl.lit(0).alias(col) for col in missing])
        extra = set(encoded.columns) - set(self.dummy_columns) - set(self.numeric_cols) - ({self.target_col} if self.target_col else set())
        if extra:
            encoded = encoded.drop(list(extra))
        return encoded

    def _scale_numeric(self, df: pl.DataFrame) -> pl.DataFrame:
        numeric_np = df.select(self.numeric_cols).to_numpy()
        if not hasattr(self.scaler, "scale_"):
            scaled = self.scaler.fit_transform(numeric_np)
        else:
            scaled = self.scaler.transform(numeric_np)
        scaled_cols = [f"{col}_scaled" for col in self.numeric_cols]
        return pl.DataFrame(scaled, schema=scaled_cols)

    def fit_transform(self, df: pl.DataFrame) -> pl.DataFrame:
        self._ensure_min_rows(df)
        imputed = self._impute(df)
        encoded = self._encode_categoricals(imputed)
        scaled_df = self._scale_numeric(encoded)
        remaining_cols = [c for c in self.dummy_columns if c != self.target_col]
        parts = [scaled_df, encoded.select(remaining_cols)]
        if self.target_col and self.target_col in encoded.columns:
            parts.append(encoded.select(self.target_col))
        return pl.concat(parts, how="horizontal")

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        imputed = self._impute(df)
        encoded = self._encode_categoricals(imputed)
        scaled_df = self._scale_numeric(encoded)
        remaining_cols = [c for c in self.dummy_columns if c != self.target_col]
        parts = [scaled_df, encoded.select(remaining_cols)]
        if self.target_col and self.target_col in encoded.columns:
            parts.append(encoded.select(self.target_col))
        return pl.concat(parts, how="horizontal")


def load_sensor_data(path: str) -> pl.DataFrame:
    return pl.read_csv(path)


def demo() -> None:
    data_path = "ml/sensor_data.csv"
    df = load_sensor_data(data_path)
    pipeline = DataPipeline(
        numeric_cols=["temperature", "pressure", "vibration_level"],
        categorical_cols=["plan_type"],
        target_col="target_churn",
    )
    features = pipeline.fit_transform(df)
    print("Rows processed:", features.height)
    print("Columns:", features.columns)
    print(features.head(3))


if __name__ == "__main__":
    demo()


# In Machine Learning, if your Temperature is 25.0 and your Pressure is 1013.0, the math (Gradient Descent) will think the Pressure is "more important" just because the number is bigger.

# The Problem: The model gets "distorted" by the different scales.

# The Solution (Scaling): We subtract the mean and divide by the standard deviation. This turns everything into a "Z-score" (how many standard deviations away from the mean).

# Result: Both Temperature and Pressure now live in the same "unitless" range (usually -3 to 3), so the Optimizer treats them fairly.