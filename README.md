# otimizador

TCC (Universidade Presbiteriana Mackenzie, FCI): técnicas de otimização aplicadas à alocação de recursos financeiros em ações da B3.

O projeto compara três técnicas na construção de uma carteira de ações:

Programação Quadrática (PQ): método clássico, resolvido com scipy.optimize (SLSQP).
Algoritmo Genético (GA): heurística populacional (seleção por torneio, cruzamento e mutação).
Simulated Annealing (SA): metaheurística probabilística com resfriamento geométrico.

Os três métodos usam os mesmos dados, a mesma função objetivo e as mesmas restrições, e devolvem o resultado no mesmo formato (JSON), o que permite compará-los de forma justa.
## Problema de otimização

Modelo de média-variância de Markowitz:

max   μᵀw − λ · wᵀΣw
s.a.  Σ wᵢ = 1,   0 ≤ wᵢ ≤ w_max
μ: vetor de retornos esperados (média dos retornos logarítmicos diários)
Σ: matriz de covariância amostral dos retornos
λ: aversão ao risco (padrão 3,0)
w_max: peso máximo por ativo (padrão 0,6); não há venda a descoberto (wᵢ ≥ 0)

Retornos logarítmicos: rₜ = ln(Pₜ / Pₜ₋₁), calculados sobre preços ajustados de fechamento.

## Arquitetura

```text
src/otimizador/
  domain/          configuração, modelos e função objetivo
  data/            download dos dados (yfinance + cache) e cálculo de retornos
  algorithms/      os três algoritmos de otimização
  evaluation/      ranking/comparação, exportação CSV/JSON e relatório em PDF
  infrastructure/  API local (FastAPI)
  application.py   executa o experimento completo
  cli.py           execução por linha de comando
frontend/          interface web estática (HTML, CSS e JS)
scripts/           geração de gráficos e PDF, execução do experimento
tests/             testes automatizados (pytest)
cache/             séries históricas baixadas (CSV)
examples/          exemplos de saída JSON e exportações
docs/              figuras, relatórios gerados e documentos
```

Escolha de MVP: com apenas um ativo (`PETR4.SA`), os pesos são distribuídos entre horizontes de retorno (`ret_1d`, `ret_5d`, `ret_21d`) para permitir comparação real dos algoritmos sem overengineering.

## Instalação

Requer Python 3.10 ou superior.
```text
bash
python -m venv .venv
.venv\Scripts\activate         # Windows

pip install -r requirements.txt -r requirements-dev.txt
$env:PYTHONPATH='src'
```

## Como executar
Experimento completo (imprime o JSON com os três algoritmos e o ranking):
```text
python -m otimizador
```
Experimento com exportação para examples/exports/:
```text
python scripts/run_local_experiment.py
```
Gráficos(docs/figures/):
```text
python scripts/generate_tcc_charts.py --symbols PETR4.SA,VALE3.SA,ITUB4.SA --start-date 2015-01-01 --end-date 2025-12-31 --interval 1d
```

```text
01_precos_normalizados.png	preços normalizados dos ativos
02_distribuicao_retornos.png	distribuição dos retornos
03_volatilidade_movel.png	volatilidade móvel
04_heatmap_correlacao.png	matriz de correlação
05_pesos_algoritmos.png	pesos por algoritmo
06_metricas_algoritmos.png	métricas por algoritmo
07_fronteira_risco_retorno.png	fronteira risco-retorno
08_convergencia_algoritmos.png	convergência dos algoritmos
09_backtest_acumulado.png	backtest acumulado
10_drawdown_algoritmos.png	drawdown
```

Relatório em PDF:
```text
python scripts/generate_pdf_report.py --export-dir examples/exports --figures-dir docs/figures --output docs/reports/relatorio_otimizador.pdf
```

Testes:
```text
pytest -q
```

## Parâmetros (variáveis de ambiente)
```text
Variável	Descrição
OTIMIZADOR_SYMBOLS	ativos separados por vírgula (PETR4.SA,VALE3.SA,ITUB4.SA)
OTIMIZADOR_START_DATE / OTIMIZADOR_END_DATE	intervalo dos dados (2015-01-01 / 2025-12-31)
OTIMIZADOR_PERIOD	período relativo, usado só se não houver datas (2y)
OTIMIZADOR_INTERVAL	frequência dos preços (1d)
OTIMIZADOR_CACHE_DIR	pasta do cache (cache)
OTIMIZADOR_RISK_AVERSION	λ, aversão ao risco (3.0)
OTIMIZADOR_MAX_WEIGHT	peso máximo por ativo (0.6)
OTIMIZADOR_RANDOM_SEED	semente de GA e SA (42)
OTIMIZADOR_GA_POPULATION	tamanho da população do GA (32)
OTIMIZADOR_GA_GENERATIONS	gerações do GA (50)
OTIMIZADOR_SA_ITERATIONS	iterações do SA (250)
OTIMIZADOR_SA_INITIAL_TEMPERATURE	temperatura inicial do SA (1.0)
OTIMIZADOR_SA_COOLING_RATE	taxa de resfriamento do SA (0.98)
```

## API local e interface web
Interface auxiliar para executar os algoritmos e exportar resultados pelo navegador. Não é necessária para reproduzir o experimento.
Suba a API (porta 8000), a partir da raiz do projeto:
```text
python -m uvicorn otimizador.infrastructure.local_api:app --port 8000
```
Em outro terminal, sirva o front-end estático:
```text
python -m http.server 8080 --directory frontend
```
Abra http://localhost:8080.

Endpoints:
```text
Método	Rota	Função
GET	/status	verificação de saúde
POST	/optimize	executa um algoritmo ou todos
POST	/export	executa e exporta CSV/JSON
POST	/report/pdf	gera e devolve o relatório em PDF
```

Exemplo de corpo para /optimize (algorithm aceita quadratic_programming, genetic_algorithm, simulated_annealing ou all):
```text
{
  "algorithm": "all",
  "symbols": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
  "start_date": "2015-01-01",
  "end_date": "2025-12-31",
  "interval": "1d",
  "max_weight": 0.6
}
```

## Resultado de referência
execução com os parâmetros padrão (os tempos variam de uma execução para outra):
```text
Algoritmo	Objetivo	Retorno diário	Volatilidade	Sharpe
PQ	−0,00030763	0,00064487	0,01781861	0,036191
GA	−0,00030763	0,00064491	0,01781892	0,036192
SA	−0,00041316	0,00072172	0,01944978	0,037107
```
Pesos (PETR4 / VALE3 / ITUB4): PQ e GA ≈ 0,119 / 0,281 / 0,600; SA ≈ 0,358 / 0,219 / 0,423.

Mais detalhes (métricas, leitura dos resultados e como reproduzir) em docs/experiment.md.

## Limitações conhecidas
O backtest é in-sample (mesmo período usado na otimização).
O índice de Sharpe é calculado sobre retornos diários, sem taxa livre de risco e sem anualização.
Os parâmetros do GA e do SA são os padrões, sem calibração.
O resultado depende de λ: valores muito baixos levam a soluções de canto.

## Autoria
André Sapucaia de Araujo. Orientador: Rogério de Oliveira. Faculdade de Computação e Informática, Universidade Presbiteriana Mackenzie.
