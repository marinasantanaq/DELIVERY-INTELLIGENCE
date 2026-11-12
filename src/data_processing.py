"""Leitura, validação e preparação da base de pedidos."""
import pandas as pd

REQUIRED_COLUMNS = {
    "id_pedido", "id_restaurante", "nome_restaurante", "cidade_restaurante",
    "categoria", "id_cliente", "data_pedido", "valor", "status",
    "tempo_preparo_min", "tempo_entrega_min", "avaliacao",
}
VALID_STATUSES = {"entregue", "cancelado", "em_preparo", "em_entrega"}


def load_and_clean_data(csv_path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["data_pedido"])

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Colunas obrigatórias ausentes: {sorted(missing_columns)}")

    df = df.drop_duplicates(subset=["id_pedido"]).copy()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["tempo_preparo_min"] = pd.to_numeric(df["tempo_preparo_min"], errors="coerce")
    df["tempo_entrega_min"] = pd.to_numeric(df["tempo_entrega_min"], errors="coerce")
    df["avaliacao"] = pd.to_numeric(df["avaliacao"], errors="coerce")
    df["status"] = df["status"].astype(str).str.strip().str.lower()

    df = df.dropna(subset=[
        "id_pedido", "id_restaurante", "id_cliente", "data_pedido", "valor", "status"
    ])
    df = df[df["valor"] >= 0]
    df = df[df["status"].isin(VALID_STATUSES)]
    df["data_pedido"] = pd.to_datetime(df["data_pedido"], errors="coerce")
    df = df.dropna(subset=["data_pedido"])
    df["hora_pedido"] = df["data_pedido"].dt.hour
    df["data"] = df["data_pedido"].dt.date.astype(str)
    return df.reset_index(drop=True)
