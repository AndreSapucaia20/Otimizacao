"""Função objetivo comum para todos os algoritmos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class ObjectiveFunction(Protocol):
    def evaluate(
        self,
        weights: np.ndarray,
        expected_returns: np.ndarray,
        volatility: np.ndarray,
        covariance_matrix: np.ndarray | None = None,
    ) -> float:
        ...


@dataclass(frozen=True)
class MeanVarianceObjective:
    """Utilidade media-variancia de Markowitz: mu'w - lambda * w'Sigma w.

    E a mesma funcao descrita no relatorio. Como e quadratica e concava
    (Sigma e semidefinida positiva), a Programacao Quadratica encontra o
    otimo global; GA e SA usam a mesma funcao como aptidao/energia.
    """

    risk_aversion: float

    def evaluate(
        self,
        weights: np.ndarray,
        expected_returns: np.ndarray,
        volatility: np.ndarray,
        covariance_matrix: np.ndarray | None = None,
    ) -> float:
        covariance = covariance_matrix
        if covariance is None:
            covariance = np.diag(np.square(volatility))
        covariance = np.asarray(covariance, dtype=float)
        portfolio_variance = max(float(weights @ covariance @ weights), 0.0)
        expected_portfolio_return = float(np.dot(weights, expected_returns))
        return expected_portfolio_return - (self.risk_aversion * portfolio_variance)
