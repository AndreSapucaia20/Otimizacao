"""Programacao Quadratica (PQ): metodo classico da comparacao.

Resolve o problema de Markowitz

    max  mu'w - lambda * w'Sigma w
    s.a. sum(w) = 1,  0 <= w_i <= max_weight

Como Sigma e semidefinida positiva, o problema e uma PQ convexa e qualquer
otimo local e global. O solver usado e o SLSQP do SciPy (programacao
quadratica sequencial), que resolve esse tipo de problema de forma exata
e deterministica, sem depender de sementes aleatorias.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from otimizador.algorithms.common import build_result, normalize_weights, timed_run
from otimizador.domain.models import AlgorithmResult, OptimizationRequest
from otimizador.domain.objective import MeanVarianceObjective, ObjectiveFunction

# Retornos diarios sao ~1e-3: multiplicar a funcao por uma constante positiva
# nao muda o otimo, mas evita que o solver pare cedo por tolerancia absoluta.
_SCALE = 1e4


@timed_run
def _solve_qp(
    request: OptimizationRequest, objective: MeanVarianceObjective
) -> tuple[np.ndarray, dict]:
    n_assets = len(request.feature_names)
    if request.max_weight * n_assets < 1.0 - 1e-12:
        raise ValueError(
            "Configuracao invalida: max_weight * quantidade_de_ativos deve ser >= 1."
        )

    mu = np.asarray(request.expected_returns, dtype=float)
    covariance = request.covariance_matrix
    if covariance is None:
        covariance = np.diag(np.square(request.volatility))
    covariance = np.asarray(covariance, dtype=float)
    covariance = 0.5 * (covariance + covariance.T)
    lam = float(objective.risk_aversion)

    def negative_utility(w: np.ndarray) -> float:
        return -_SCALE * float(mu @ w - lam * (w @ covariance @ w))

    def gradient(w: np.ndarray) -> np.ndarray:
        return -_SCALE * (mu - 2.0 * lam * (covariance @ w))

    start = normalize_weights(np.ones(n_assets), max_weight=request.max_weight)
    result = minimize(
        negative_utility,
        start,
        jac=gradient,
        method="SLSQP",
        bounds=[(0.0, min(request.max_weight, 1.0))] * n_assets,
        constraints=[
            {
                "type": "eq",
                "fun": lambda w: float(np.sum(w) - 1.0),
                "jac": lambda w: np.ones(n_assets),
            }
        ],
        options={"ftol": 1e-12, "maxiter": 500},
    )

    weights = np.clip(result.x, 0.0, request.max_weight)
    if abs(float(np.sum(weights)) - 1.0) > 1e-6:
        raise RuntimeError(f"Solver de PQ nao convergiu: {result.message}")

    info = {
        "solver": "scipy_slsqp",
        "converged": bool(result.success),
        "iterations": int(result.nit),
    }
    return weights, info


def run_quadratic_programming(
    request: OptimizationRequest, objective: ObjectiveFunction
) -> AlgorithmResult:
    if not isinstance(objective, MeanVarianceObjective):
        raise TypeError(
            "A Programacao Quadratica exige a funcao objetivo media-variancia "
            "(MeanVarianceObjective)."
        )
    (weights, info), elapsed_ms = _solve_qp(request, objective)
    return build_result(
        algorithm="quadratic_programming",
        request=request,
        weights=weights,
        objective=objective,
        elapsed_ms=elapsed_ms,
        extra_metadata=info,
    )
