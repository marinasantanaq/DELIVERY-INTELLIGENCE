"""Persistência local em SQLite. PostgreSQL poderá substituir esta camada depois."""
import sqlite3
from pathlib import Path
import pandas as pd


def save_orders(df: pd.DataFrame, database_path) -> None:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        df.to_sql("pedidos", connection, if_exists="replace", index=False)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_pedidos_data
            ON pedidos (data_pedido)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_pedidos_restaurante
            ON pedidos (id_restaurante)
        """)


def read_orders(database_path) -> pd.DataFrame:
    path = Path(database_path)
    if not path.exists():
        raise FileNotFoundError(
            "Banco de dados não encontrado. Execute primeiro: python main.py"
        )
    with sqlite3.connect(path) as connection:
        return pd.read_sql_query("SELECT * FROM pedidos", connection,
                                 parse_dates=["data_pedido"])
