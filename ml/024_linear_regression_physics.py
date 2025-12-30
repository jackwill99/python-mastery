from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression
from typing import Tuple

# Pro-Tip: Analytical normal equation mirrors physics derivations (closed-form k from F=kx); iterative gradient descent is the ML workhorse, trading exactness for scalability.


@dataclass
class SpringData:
    displacement: np.ndarray  # x
    force: np.ndarray  # F


def generate_noisy_data(n: int = 200, k_true: float = 3.5, noise_std: float = 0.5) -> SpringData:
    rng = np.random.default_rng(42)
    x = rng.uniform(low=0.0, high=2.0, size=n)
    noise = rng.normal(0.0, noise_std, size=n)
    F = k_true * x + noise
    return SpringData(displacement=x, force=F)


def analytical_solution(data: SpringData) -> float:
    # Normal equation for slope (k) in y = kx with zero intercept: k = (X^T X)^{-1} X^T y
    x = data.displacement
    y = data.force
    k_hat = (x @ y) / (x @ x)
    return float(k_hat)


def iterative_solution(data: SpringData, lr: float = 0.1, steps: int = 500) -> float:
    # Gradient descent minimizing MSE: loss = (1/n) * sum((k*x - y)^2); grad = (2/n) * sum(x*(k*x - y))
    x = data.displacement
    y = data.force
    k = 0.0
    n = len(x)
    for _ in range(steps):
        grad = (2.0 / n) * np.sum(x * (k * x - y))
        k -= lr * grad
    return k


def sklearn_solution(data: SpringData) -> Tuple[float, float]:
    model = LinearRegression(fit_intercept=False)
    model.fit(data.displacement.reshape(-1, 1), data.force)
    return float(model.coef_[0]), float(model.intercept_)


def visualize(data: SpringData, k_hat: float) -> None:
    plt.scatter(data.displacement, data.force, alpha=0.4, label="noisy data")
    x_line = np.linspace(data.displacement.min(), data.displacement.max(), 100)
    plt.plot(x_line, k_hat * x_line, color="red", label=f"best fit (k={k_hat:.2f})")
    plt.xlabel("displacement (x)")
    plt.ylabel("force (F)")
    plt.legend()
    plt.title("Hooke's Law: F = kx")
    plt.tight_layout()
    plt.show()


def main() -> None:
    data = generate_noisy_data()
    k_analytical = analytical_solution(data)
    k_iterative = iterative_solution(data)
    k_sklearn, _ = sklearn_solution(data)
    print(f"Analytical k: {k_analytical:.4f}")
    print(f"Iterative (GD) k: {k_iterative:.4f}")
    print(f"sklearn k: {k_sklearn:.4f}")
    visualize(data, k_sklearn)


if __name__ == "__main__":
    main()

