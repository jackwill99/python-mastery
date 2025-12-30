from __future__ import annotations

import polars as pl

# Pro-Tip: Polars lazy pipelines run closer to Rust speed with schema awareness—think of it as a typed, vectorized upgrade over JavaScript Array.reduce or Dart List transforms.


def load_sensor_data(path: str) -> pl.LazyFrame:
    return (
        pl.scan_csv(path, has_header=True, infer_schema_length=1000)
        .with_columns(
            pl.col("temperature").cast(pl.Float64),
            pl.col("device_id").cast(pl.Utf8),
            pl.col("timestamp").str.to_datetime(),
        )
    )


def build_pipeline(lf: pl.LazyFrame) -> pl.LazyFrame:
    return (
        lf.filter(pl.col("temperature").is_not_null())
        .filter(pl.col("temperature").is_between(-40, 120))
        .with_columns(
            pl.col("temperature")
            .rolling_mean(window_size=10, by="device_id", closed="both")
            .alias("temperature_roll_mean"),
        )
        .select("device_id", "timestamp", "temperature", "temperature_roll_mean")
    )


def main() -> None:
    # For demo, use a placeholder CSV path; replace with your 100k-row IoT file.
    path = "sensor_readings.csv"
    lf = load_sensor_data(path)
    result = build_pipeline(lf)
    print(result.collect().head(5))


if __name__ == "__main__":
    main()

