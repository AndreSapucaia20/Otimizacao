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

bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
