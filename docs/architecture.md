# Arquitetura do Delivery Intelligence

```text
Dados sintéticos (Python)
          |
          v
     CSV bruto
          |
          v
 Python + Pandas
 validação e limpeza
          |
          +------> CSV tratado
          |
          v
       SQLite
          |
          v
     FastAPI (API REST)
          |
          v
 HTML + CSS + JavaScript
          |
          v
 Chart.js + interface web
```

## Responsabilidades

- `src/`: geração, transformação, métricas, persistência e orquestração do pipeline.
- `database/`: banco SQLite local gerado pelo pipeline.
- `backend/`: API REST que disponibiliza indicadores e séries para a interface.
- `frontend/`: interface web em HTML, CSS e JavaScript.
- `dashboard/`: protótipo Streamlit mantido como alternativa de visualização.

## Execução

1. `python main.py`
2. `uvicorn backend.api:app --reload`
3. Acesse `http://127.0.0.1:8000`.

## Próximas decisões

- Restringir CORS para o domínio correto antes de publicar.
- Adicionar autenticação e autorização se houver dados reais.
- Migrar SQLite para PostgreSQL quando a modelagem estiver estável.
- Criar testes automatizados para os endpoints da API.
- Implementar modelos de previsão somente após validar a qualidade dos dados.
