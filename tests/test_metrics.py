import pandas as pd
from src.metrics import calculate_kpis


def test_kpis_ignore_cancelled_revenue():
    df = pd.DataFrame({
        "id_pedido": [1, 2, 3],
        "status": ["entregue", "cancelado", "entregue"],
        "valor": [50.0, 100.0, 30.0],
        "tempo_preparo_min": [20, 30, 40],
        "tempo_entrega_min": [25, 0, 35],
        "avaliacao": [5.0, float("nan"), 3.0],
    })
    result = calculate_kpis(df)
    assert result["revenue"] == 80.0
    assert result["total_orders"] == 3
    assert result["delivered_orders"] == 2
    assert result["average_ticket"] == 40.0
    assert abs(result["cancellation_rate"] - 100 / 3) < 0.001
