"""Cálculo dos indicadores de desempenho do delivery."""
import pandas as pd


def calculate_kpis(df: pd.DataFrame) -> dict:
    total_orders = int(len(df))
    cancelled = int((df["status"] == "cancelado").sum())
    delivered = df[df["status"] == "entregue"].copy()
    valid_revenue = float(delivered["valor"].sum())
    delivered_count = int(len(delivered))

    return {
        "revenue": valid_revenue,
        "total_orders": total_orders,
        "delivered_orders": delivered_count,
        "average_ticket": valid_revenue / delivered_count if delivered_count else 0.0,
        "cancellation_rate": cancelled / total_orders * 100 if total_orders else 0.0,
        "average_prep_time": float(delivered["tempo_preparo_min"].mean()) if delivered_count else 0.0,
        "average_delivery_time": float(delivered["tempo_entrega_min"].mean()) if delivered_count else 0.0,
        "average_rating": float(delivered["avaliacao"].mean()) if delivered["avaliacao"].notna().any() else 0.0,
    }


def revenue_over_time(df: pd.DataFrame) -> pd.DataFrame:
    delivered = df[df["status"] == "entregue"]
    if delivered.empty:
        return pd.DataFrame(columns=["data", "faturamento"])
    return (delivered.assign(data=pd.to_datetime(delivered["data_pedido"]).dt.date)
            .groupby("data", as_index=False)["valor"].sum()
            .rename(columns={"valor": "faturamento"}))


def orders_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("hora_pedido", as_index=False)
            .size().rename(columns={"size": "pedidos"}))


def cancellations_by_restaurant(df: pd.DataFrame) -> pd.DataFrame:
    result = df.assign(cancelado=(df["status"] == "cancelado"))
    return (result.groupby("nome_restaurante", as_index=False)
            .agg(pedidos=("id_pedido", "count"), cancelamentos=("cancelado", "sum")))
