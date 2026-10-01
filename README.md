# Meu Site

Site pessoal.

Stack: **frontend em JavaScript** + **backend em Python**.

```
.
├── frontend/            # JavaScript (HTML + CSS + ES modules)
│   ├── index.html
│   └── src/
│       ├── app.js
│       └── style.css
├── backend/             # Python (FastAPI)
│   ├── main.py
│   └── requirements.txt
└── run.sh
```

## Rodar

```bash
./run.sh
```

Abre em <http://localhost:8000>. O `run.sh` cria o virtualenv, instala as
dependências do `backend/requirements.txt` e sobe o uvicorn. O backend serve o
frontend e a API no mesmo endereço.

### Manualmente

```bash
cd backend
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/uvicorn main:app --reload --port 8000
```

## API

| Método | Rota | Descrição |
| ------ | ---- | --------- |
| `GET` | `/api/health` | Status do serviço |
| `GET` | `/api/items` | Lista os itens |
| `POST` | `/api/items` | Cria um item |
| `PUT` | `/api/items/{id}` | Atualiza um item |
| `DELETE` | `/api/items/{id}` | Remove um item |
| `GET` | `/api/stats` | Totais (total / concluídos / pendentes) |

Documentação interativa: <http://localhost:8000/docs>

## Banco

SQLite (`backend/app.db`), criado automaticamente na primeira execução.
