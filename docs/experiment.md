# Experimento MVP - PETR4.SA

## Objetivo

Comparar três abordagens de otimização com o mesmo conjunto de dados e a mesma função objetivo:
- Programação linear
- Algoritmo genético
- Simulated annealing

## Dataset

- Fonte: Yahoo Finance via `yfinance`
- Ativo inicial: `PETR4.SA`
- Configuração por ambiente: símbolo, período, intervalo
- Fallback: cache local CSV em `cache/`

## Feature engineering

Para manter simplicidade no MVP e ainda produzir um vetor de pesos comparável, criamos três features derivadas do mesmo ativo:
- `ret_1d`
- `ret_5d`
- `ret_21d`

Cada otimização aloca pesos nesses três horizontes.

## Função objetivo

Modelo linear de retorno ajustado por risco:

`objective = dot(weights, expected_returns - risk_aversion * volatility)`

Por ser linear, permite usar programação linear e manter o mesmo contrato para GA e SA.

## Decisões de design (MVP)

1. Contrato único de saída JSON para facilitar comparação, API e persistência.
3. Sem dependência de AWS para execução local.
4. Testes rápidos com mocks para rede e handlers.
