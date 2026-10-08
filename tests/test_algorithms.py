from __future__ import annotations

import numpy as np

from otimizador.algorithms.genetic import run_genetic_algorithm
from otimizador.algorithms.quadratic_programming import run_quadratic_programming
from otimizador.algorithms.simulated_annealing import run_simulated_annealing
from otimizador.domain.models import OptimizationRequest
from otimizador.domain.objective import MeanVarianceObjective


def _request() -> OptimizationRequest:
    return OptimizationRequest(
        symbol="PETR4.SA,VALE3.SA,ITUB4.SA",
        feature_names=["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
        expected_returns=np.array([0.0010, 0.0008, 0.0006]),
        volatility=np.array([0.012, 0.009, 0.007]),
        risk_aversion=0.3,
        max_weight=0.6,
        seed=7,
    )


def test_algorithms_return_normalized_weights():
    request = _request()
    objective = MeanVarianceObjective(risk_aversion=request.risk_aversion)

    results = [
        run_quadratic_programming(request, objective),
        run_genetic_algorithm(request, objective, population_size=16, generations=10),
        run_simulated_annealing(
            request,
            objective,
            iterations=50,
            initial_temperature=1.0,
            cooling_rate=0.95,
        ),
    ]

    for result in results:
        assert result.objective_value == result.objective_value
        assert result.elapsed_ms >= 0.0
        assert abs(sum(result.weights.values()) - 1.0) < 1e-6
        assert set(result.weights.keys()) == {"PETR4.SA", "VALE3.SA", "ITUB4.SA"}
        assert max(result.weights.values()) <= request.max_weight + 1e-6


def _request_with_covariance() -> OptimizationRequest:
    sd = np.array([0.029, 0.026, 0.019])
    corr = np.array([[1.0, 0.6, 0.4], [0.6, 1.0, 0.5], [0.4, 0.5, 1.0]])
    return OptimizationRequest(
        symbol="A,B,C",
        feature_names=["A", "B", "C"],
        expected_returns=np.array([0.00092, 0.00072, 0.00055]),
        volatility=sd,
        covariance_matrix=corr * np.outer(sd, sd),
        risk_aversion=3.0,
        max_weight=0.6,
        seed=7,
    )


def test_quadratic_programming_is_global_optimum_and_beats_heuristics():
    request = _request_with_covariance()
    objective = MeanVarianceObjective(risk_aversion=request.risk_aversion)

    qp = run_quadratic_programming(request, objective)
    ga = run_genetic_algorithm(request, objective, population_size=32, generations=50)
    sa = run_simulated_annealing(
        request, objective, iterations=250, initial_temperature=1.0, cooling_rate=0.98
    )

    # Busca exaustiva em grade sobre o simplex (passo 0,005) com w_i <= max_weight
    best_grid = -np.inf
    steps = np.arange(0.0, 0.6 + 1e-9, 0.005)
    for w1 in steps:
        for w2 in steps:
            w3 = 1.0 - w1 - w2
            if 0.0 <= w3 <= 0.6 + 1e-12:
                w = np.array([w1, w2, w3])
                value = objective.evaluate(
                    w,
                    request.expected_returns,
                    request.volatility,
                    request.covariance_matrix,
                )
                best_grid = max(best_grid, value)

    assert qp.metadata["converged"] is True
    assert qp.objective_value >= best_grid - 1e-9
    assert qp.objective_value >= ga.objective_value - 1e-9
    assert qp.objective_value >= sa.objective_value - 1e-9
    assert abs(sum(qp.weights.values()) - 1.0) < 1e-6
    assert min(qp.weights.values()) >= -1e-9
    assert max(qp.weights.values()) <= request.max_weight + 1e-6
