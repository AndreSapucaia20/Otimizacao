# otimizador

Projeto de TCC (Mackenzie, FCI): comparação de técnicas de otimização aplicadas à alocação de carteiras de ações da B3.

Os algoritmos usam o mesmo conjunto de dados (preços do Yahoo Finance via yfinance), a mesma função objetivo e retornam o mesmo formato de resultado (JSON), o que permite compará-los de forma justa.

## Visão geral

O projeto compara:
1. Programação Quadrática
2. Algoritmo genético
3. Simulated annealing

Todos os algoritmos:
- usam o mesmo dataset,
- usam a mesma função objetivo,
- retornam o mesmo schema JSON.

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
docs/              figuras, relatórios gerados e documentos do TCC
```

Escolha de MVP: com apenas um ativo (`PETR4.SA`), os pesos são distribuídos entre horizontes de retorno (`ret_1d`, `ret_5d`, `ret_21d`) para permitir comparação real dos algoritmos sem overengineering.

## Função objetivo comum

`linear_risk_adjusted_return`:

`objective = dot(weights, expected_returns - risk_aversion * volatility)`

## Variáveis de ambiente

Copie `.env.example` e ajuste se necessário:

- `OTIMIZADOR_SYMBOL` (default: `PETR4.SA`)
- `OTIMIZADOR_PERIOD` (default: `2y`)
- `OTIMIZADOR_START_DATE` (opcional, ex: `2015-01-01`)
- `OTIMIZADOR_END_DATE` (opcional, ex: `2025-12-31`)
- `OTIMIZADOR_INTERVAL` (default: `1d`)
- `OTIMIZADOR_CACHE_DIR` (default: `cache`)
- `OTIMIZADOR_RISK_AVERSION` (default: `0.35`)
- `OTIMIZADOR_RANDOM_SEED` (default: `42`)
- `OTIMIZADOR_GA_POPULATION` (default: `32`)
- `OTIMIZADOR_GA_GENERATIONS` (default: `50`)
- `OTIMIZADOR_SA_ITERATIONS` (default: `250`)
- `OTIMIZADOR_SA_INITIAL_TEMPERATURE` (default: `1.0`)
- `OTIMIZADOR_SA_COOLING_RATE` (default: `0.98`)

## Como rodar localmente

1. Criar ambiente e instalar dependências:

```bash
python -m venv .venv
source .venv/bin/activate  # linux/mac
# .venv\\Scripts\\activate   # windows powershell
pip install -r requirements.txt -r requirements-dev.txt
```

2. Executar experimento ponta a ponta:

```bash
python -m otimizador
```

3. Gerar exemplos JSON:

```bash
python scripts/run_local_experiment.py
```

## Como testar

```bash
pytest -q
```

## Como executar cada algoritmo

Use `run_full_experiment()` em `src/otimizador/application.py`, ou chame:
- `run_linear_programming`
- `run_genetic_algorithm`
- `run_simulated_annealing`

Todos recebem `OptimizationRequest` + `ObjectiveFunction`.

## Empacotamento para deploy

Linux/macOS:

```bash
bash scripts/package_lambda.sh
```

Windows PowerShell:

```powershell
./scripts/package_lambda.ps1
```

Artefato gerado: `dist/otimizador-lambda.zip`

## Dados e cache

Na primeira execução o `yfinance` baixa os preços do Yahoo Finance (é preciso internet) e salva um CSV em `cache/`. Nas execuções seguintes, se o CSV do mesmo período e dos mesmos ativos existir, ele é reutilizado.

## Front-end com Docker

1. Suba a API local (porta 8000):

```bash
set PYTHONPATH=src
python -m uvicorn otimizador.infrastructure.local_api:app --host 0.0.0.0 --port 8000 --reload
```

2. Em outro terminal, suba o front com Docker:

```bash
docker compose up --build frontend
```

3. Abra no navegador:

- `http://localhost:8080`

O front ja vem apontando para `http://localhost:8000`.

### Multi-ativos via API local

No endpoint `POST /optimize`, envie:

```json
{
  "algorithm": "linear_programming",
  "symbols": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
  "start_date": "2015-01-01",
  "end_date": "2025-12-31",
  "interval": "1d",
  "max_weight": 0.6,
  "period": "2y"
}
```

### Exportacao de resultados

Endpoint `POST /export` cria artefatos em CSV/JSON para analise:
- `*_full_report.json`
- `*_comparison_summary.csv`
- `*_weights_by_algorithm.csv`

Exemplo de uso:

```json
{
  "algorithm": "all",
  "symbols": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
  "start_date": "2015-01-01",
  "end_date": "2025-12-31",
  "interval": "1d",
  "max_weight": 0.6,
  "export_dir": "examples/exports"
}
```

### Relatorio em PDF com graficos

Com os arquivos de `examples/exports` e `docs/figures` gerados:

```powershell
$env:PYTHONPATH='src'
python scripts/generate_pdf_report.py --export-dir examples/exports --figures-dir docs/figures --output docs/reports/relatorio_otimizador_2015_2025.pdf
```

Ou via API/Frontend:
- Endpoint `POST /report/pdf` gera o PDF e retorna o arquivo para download.
- No frontend, use o botao `Gerar PDF`.


## Graficos para TCC

Script unico para gerar 10 graficos em `docs/figures`:

```bash
PYTHONPATH=src python scripts/generate_tcc_charts.py --symbols PETR4.SA,VALE3.SA,ITUB4.SA --period 2y --interval 1d
```

Windows PowerShell:

```powershell
$env:PYTHONPATH='src'
python scripts/generate_tcc_charts.py --symbols PETR4.SA,VALE3.SA,ITUB4.SA --start-date 2015-01-01 --end-date 2025-12-31 --interval 1d
```

Saidas principais:
- `01_precos_normalizados.png`
- `02_distribuicao_retornos.png`
- `03_volatilidade_movel.png`
- `04_heatmap_correlacao.png`
- `05_pesos_algoritmos.png`
- `06_metricas_algoritmos.png`
- `07_fronteira_risco_retorno.png`
- `08_convergencia_algoritmos.png`
- `09_backtest_acumulado.png`
- `10_drawdown_algoritmos.png`
