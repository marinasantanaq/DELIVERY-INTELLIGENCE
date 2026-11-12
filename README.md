# Delivery Intelligence

Plataforma de análise de desempenho comercial e operacional para restaurantes que trabalham com delivery.

## Escopo do MVP

- Geração de dados fictícios e reproduzíveis.
- Leitura, validação e limpeza com Pandas.
- Persistência local em SQLite.
- Indicadores de faturamento, pedidos, ticket médio, cancelamentos, tempos e avaliações.
- Dashboard interativo com Streamlit e Plotly.
- Teste automatizado dos principais KPIs.

> Os dados são inteiramente simulados e não representam clientes ou restaurantes reais.

## Requisitos

- Python 3.10 ou superior
- pip

## Instalação

```bash
python -m venv .venv
```

Ative o ambiente virtual:

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## Executar o pipeline

Na raiz do projeto:

```bash
python main.py
```

O comando gera `data/raw/pedidos.csv`, trata os registros, salva
`data/processed/pedidos_tratados.csv` e carrega os dados em
`database/delivery_intelligence.db`.

## Executar a aplicação web (HTML, CSS, JavaScript + API Python)

Primeiro gere o banco e os arquivos de dados:

```bash
python main.py
```

Depois inicie a API e o servidor web:

```bash
uvicorn backend.api:app --reload
```

Abra http://127.0.0.1:8000 no navegador. A interface em HTML, CSS e JavaScript consome os endpoints FastAPI e lê os dados do SQLite.

O dashboard Streamlit anterior também permanece disponível, se desejar comparar:

```bash
streamlit run dashboard/app.py
```

## Executar os testes

```bash
pytest -q
```

## Estrutura

```text
delivery-intelligence/
├── data/
│   ├── raw/
│   └── processed/
├── database/
├── backend/
│   └── api.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── dashboard/
│   └── app.py
├── src/
│   ├── config.py
│   ├── database.py
│   ├── data_processing.py
│   ├── generate_data.py
│   ├── metrics.py
│   └── pipeline.py
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## Decisões e limitações do MVP

- SQLite foi escolhido para facilitar a execução local inicial. A camada de persistência
  está isolada para permitir uma migração posterior para PostgreSQL.
- O faturamento válido considera somente pedidos com status `entregue`.
- A taxa de cancelamento considera pedidos cancelados divididos pelo total de pedidos
  no recorte selecionado.
- Os tempos médios e a avaliação média consideram somente pedidos entregues.
- O dataset é sintético; resultados não devem ser interpretados como evidência de
  comportamento de um mercado real.

## Próximas evoluções

1. Modelagem dimensional e migração para PostgreSQL.
2. Testes de qualidade de dados mais abrangentes.
3. Pipeline incremental e logging.
4. Previsão de demanda e risco de atraso com Machine Learning.
5. Monitoramento e versionamento de modelos.
