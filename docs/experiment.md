# Experimento: Programação Quadrática, Algoritmo Genético e Simulated Annealing

## Objetivo

Comparar três técnicas de otimização na construção de uma carteira de ações da B3, usando os mesmos dados, a mesma função objetivo e as mesmas restrições:

- Programação Quadrática (PQ), método clássico
- Algoritmo Genético (GA)
- Simulated Annealing (SA)

## Dados

- Fonte: Yahoo Finance, via `yfinance`
- Ativos: `PETR4.SA`, `VALE3.SA`, `ITUB4.SA`
- Período: 01/01/2015 a 31/12/2025, frequência diária (2.736 retornos diários)
- Cache local em `cache/` (CSV). Se o download falhar, o programa usa o CSV já salvo.

## Pré-processamento

- Retornos logarítmicos diários: `r_t = ln(P_t / P_{t-1})`
- Vetor de retornos esperados `μ`: média dos retornos diários
- Matriz de covariância `Σ`: covariância amostral dos retornos
- Volatilidade individual: desvio padrão dos retornos diários

## Problema de otimização

```
max  μᵀw − λ · wᵀΣw
s.a. Σ wᵢ = 1,  0 ≤ wᵢ ≤ w_max
```

Parâmetros padrão: `λ = 3,0` (aversão ao risco) e `w_max = 0,6` (peso máximo por ativo). Sem venda a descoberto (`wᵢ ≥ 0`).

A função é côncava e as restrições são lineares, então o problema é uma Programação Quadrática convexa: qualquer ótimo local é global.

## Algoritmos

| Algoritmo | Implementação | Parâmetros |
|---|---|---|
| PQ | `scipy.optimize.minimize` (SLSQP), determinístico | tolerância 1e-12 |
| GA | população, seleção, cruzamento e mutação | população 32, 50 gerações, semente 42 |
| SA | perturbação dos pesos com resfriamento geométrico | 250 iterações, T0 = 1,0, resfriamento 0,98, semente 42 |

GA e SA usam a mesma função objetivo como aptidão/energia. Os pesos de todos os métodos são projetados para respeitar as restrições.

## Métricas

Valor da função objetivo, retorno esperado diário, volatilidade da carteira, índice de Sharpe, contribuição de risco por ativo e tempo de execução. Os gráficos adicionam backtest acumulado, drawdown e fronteira risco-retorno.

O Sharpe é calculado como retorno esperado dividido pela volatilidade, sobre retornos diários, sem taxa livre de risco e sem anualização.

## Resultado de referência (execução de 08/10/2026)

| Algoritmo | Objetivo | Retorno | Volatilidade | Sharpe | Tempo (ms) |
|---|---|---|---|---|---|
| PQ | −0,00030763 | 0,00064487 | 0,01781861 | 0,036191 | 0,64 |
| GA | −0,00030763 | 0,00064491 | 0,01781892 | 0,036192 | 161,38 |
| SA | −0,00041316 | 0,00072172 | 0,01944978 | 0,037107 | 14,70 |

Pesos (PETR4 / VALE3 / ITUB4): PQ e GA ≈ 0,119 / 0,281 / 0,600. SA ≈ 0,358 / 0,219 / 0,423.

Leitura dos resultados:

- A PQ encontra o ótimo global, e o GA chega praticamente ao mesmo ponto, com tempo muito maior.
- O SA, com 250 iterações, para num ponto de menor objetivo. Ele aceita mais risco para obter mais retorno, por isso aparece com Sharpe maior e também com drawdown mais fundo. Isso não contradiz o ranking: o objetivo otimizado é média-variância, não o Sharpe.
- Os tempos variam de uma execução para outra. Os valores acima são de uma execução específica.

## Limitações conhecidas

1. O backtest é in-sample (mesmo período da otimização). Falta a validação fora da amostra.
2. O Sharpe não usa taxa livre de risco nem é anualizado.
3. Apenas 3 ativos. Com poucos ativos e restrições simples, o problema é fácil e a PQ domina; um universo maior e restrições adicionais (por exemplo, número máximo de ativos) são necessários para testar a hipótese de que as heurísticas ganham flexibilidade.
4. O resultado depende de `λ`. Valores muito baixos levam a soluções de canto (todo o capital nos ativos de maior retorno); varie `λ` para traçar a fronteira eficiente.

## Como reproduzir

```
python -m otimizador
python scripts/run_local_experiment.py
python scripts/generate_tcc_charts.py --symbols PETR4.SA,VALE3.SA,ITUB4.SA --start-date 2015-01-01 --end-date 2025-12-31 --interval 1d
python scripts/generate_pdf_report.py --export-dir examples/exports --figures-dir docs/figures --output docs/reports/relatorio_otimizador.pdf
```

Veja o `README.md` na raiz para a instalação e para a interface web.
