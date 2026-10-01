"""
Meu Site - backend (Python / FastAPI)

Serve a API e o frontend JavaScript (pasta ../frontend).
Rodar:  uvicorn main:app --reload --port 8000   (ou ./run.sh na raiz)
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
DB_PATH = BASE_DIR / "app.db"

app = FastAPI(title="Meu Site", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Banco (SQLite) - troque por Postgres/SQLAlchemy quando precisar escalar
# --------------------------------------------------------------------------
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_conn()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT    NOT NULL DEFAULT '',
                done        INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()


init_db()


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------
class ItemIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    done: bool = False


class Item(BaseModel):
    id: int
    title: str
    description: str
    done: bool
    created_at: str


# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------
@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "Meu Site"}


@app.get("/api/items", response_model=list[Item])
def list_items() -> list[dict]:
    with closing(get_conn()) as conn:
        rows = conn.execute(
            "SELECT * FROM items ORDER BY id DESC"
        ).fetchall()
    return [dict(r) | {"done": bool(r["done"])} for r in rows]


@app.post("/api/items", response_model=Item, status_code=201)
def create_item(payload: ItemIn) -> dict:
    with closing(get_conn()) as conn:
        cur = conn.execute(
            "INSERT INTO items (title, description, done) VALUES (?, ?, ?)",
            (payload.title, payload.description, int(payload.done)),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM items WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
    return dict(row) | {"done": bool(row["done"])}


@app.put("/api/items/{item_id}", response_model=Item)
def update_item(item_id: int, payload: ItemIn) -> dict:
    with closing(get_conn()) as conn:
        cur = conn.execute(
            "UPDATE items SET title = ?, description = ?, done = ? WHERE id = ?",
            (payload.title, payload.description, int(payload.done), item_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        row = conn.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ).fetchone()
    return dict(row) | {"done": bool(row["done"])}


@app.delete("/api/items/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    with closing(get_conn()) as conn:
        cur = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item não encontrado")


@app.get("/api/stats")
def stats() -> dict:
    with closing(get_conn()) as conn:
        total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        done = conn.execute(
            "SELECT COUNT(*) FROM items WHERE done = 1"
        ).fetchone()[0]
    return {"total": total, "done": done, "pending": total - done}


# --------------------------------------------------------------------------
# Frontend (JavaScript) servido pelo backend Python
# --------------------------------------------------------------------------
if FRONTEND_DIR.is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="static",
    )

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:  # pragma: no cover
    print(f"[aviso] pasta do frontend não encontrada em {FRONTEND_DIR}")
