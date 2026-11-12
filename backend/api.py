from pathlib import Path
import sqlite3
import sys
from typing import Optional

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "database" / "delivery_intelligence.db"
FRONTEND_DIR = ROOT_DIR / "frontend"

app = FastAPI(
    title="Delivery Intelligence API",
    description="API de indicadores operacionais e comerciais de delivery.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir ao domínio do frontend.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_orders() -> pd.DataFrame:
    if not DB_PATH.exists():
        raise FileNotFoundError("Banco não encontrado. Execute `python main.py` primeiro.")
    with sqlite3.connect(DB_PATH) as connection:
        df = pd.read_sql_query("SELECT * FROM pedidos", connection)
    df["data_pedido"] = pd.to_datetime(df["data_pedido"])
    return df


def filtered_orders(
    restaurant: Optional[str] = None,
    period: str = "30d",
) -> pd.DataFrame:
    df = load_orders()
    if restaurant and restaurant != "Todos":
        df = df[df["nome_restaurante"] == restaurant]
    if period != "Tudo":
        days = int(period.replace("d", ""))
        cutoff = df["data_pedido"].max() - pd.Timedelta(days=days)
        df = df[df["data_pedido"] >= cutoff]
    return df


@app.get("/api/health")
def health():
    return {"status": "ok", "database_exists": DB_PATH.exists()}


@app.get("/api/filters")
def filters():
    df = load_orders()
    return {
        "restaurants": ["Todos"] + sorted(df["nome_restaurante"].dropna().unique().tolist()),
        "periods": ["7d", "30d", "90d", "Tudo"],
    }


@app.get("/api/overview")
def overview(
    restaurant: Optional[str] = Query(default="Todos"),
    period: str = Query(default="30d"),
):
    df = filtered_orders(restaurant, period)
    total = len(df)
    delivered = df[df["status"] == "entregue"]
    cancelled = int((df["status"] == "cancelado").sum())
    revenue = float(delivered["valor"].sum())
    delivered_count = len(delivered)
    return {
        "revenue": round(revenue, 2),
        "orders": int(total),
        "ticket": round(revenue / delivered_count, 2) if delivered_count else 0,
        "cancellation_rate": round(cancelled / total * 100, 1) if total else 0,
        "prep_time": round(float(delivered["tempo_preparo_min"].mean()), 1) if delivered_count else 0,
        "delivery_time": round(float(delivered["tempo_entrega_min"].mean()), 1) if delivered_count else 0,
        "rating": round(float(delivered["avaliacao"].mean()), 2) if delivered["avaliacao"].notna().any() else 0,
        "delivered": int(delivered_count),
    }


@app.get("/api/revenue")
def revenue(
    restaurant: Optional[str] = Query(default="Todos"),
    period: str = Query(default="30d"),
):
    df = filtered_orders(restaurant, period)
    df = df[df["status"] == "entregue"].copy()
    df["day"] = df["data_pedido"].dt.strftime("%d/%m")
    grouped = df.groupby(df["data_pedido"].dt.date)["valor"].sum().reset_index()
    return {
        "labels": [pd.Timestamp(day).strftime("%d/%m") for day in grouped["data_pedido"]],
        "values": [round(float(value), 2) for value in grouped["valor"]],
    }


@app.get("/api/hourly")
def hourly(
    restaurant: Optional[str] = Query(default="Todos"),
    period: str = Query(default="30d"),
):
    df = filtered_orders(restaurant, period)
    grouped = df.groupby(df["data_pedido"].dt.hour).size()
    labels = [f"{hour:02d}h" for hour in range(24)]
    values = [int(grouped.get(hour, 0)) for hour in range(24)]
    return {"labels": labels, "values": values}


@app.get("/api/restaurants")
def restaurants(
    restaurant: Optional[str] = Query(default="Todos"),
    period: str = Query(default="30d"),
):
    df = filtered_orders(restaurant, period)
    rows = []
    for name, group in df.groupby("nome_restaurante"):
        delivered = group[group["status"] == "entregue"]
        cancelled = int((group["status"] == "cancelado").sum())
        rows.append({
            "name": name,
            "orders": int(len(group)),
            "revenue": round(float(delivered["valor"].sum()), 2),
            "cancellations": round(cancelled / len(group) * 100, 1) if len(group) else 0,
        })
    rows.sort(key=lambda row: row["revenue"], reverse=True)
    return rows


@app.get("/api/recent-orders")
def recent_orders(
    restaurant: Optional[str] = Query(default="Todos"),
    period: str = Query(default="30d"),
):
    df = filtered_orders(restaurant, period).sort_values("data_pedido", ascending=False).head(10)
    result = []
    for _, row in df.iterrows():
        result.append({
            "id": int(row["id_pedido"]),
            "restaurant": row["nome_restaurante"],
            "date": row["data_pedido"].strftime("%d/%m/%Y %H:%M"),
            "value": round(float(row["valor"]), 2),
            "status": row["status"],
        })
    return result


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
