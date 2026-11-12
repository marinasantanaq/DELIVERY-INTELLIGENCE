"""Gera uma base fictícia e reproduzível de pedidos de delivery."""
import numpy as np
import pandas as pd

from src.config import CSV_PATH, RANDOM_SEED

RESTAURANTS = [
    (1, "Sabor da Vila", "São Paulo", "Brasileira"),
    (2, "Verde no Pote", "Guarulhos", "Saudável"),
    (3, "Forno & Massa", "São Paulo", "Italiana"),
    (4, "Burguer Lab", "Guarulhos", "Hambúrguer"),
    (5, "Temaki House", "São Paulo", "Japonesa"),
]
STATUSES = ["entregue", "cancelado", "em_preparo", "em_entrega"]
STATUS_PROBABILITIES = [0.78, 0.08, 0.07, 0.07]


def generate_orders(number_of_orders: int = 1500) -> pd.DataFrame:
    """Cria pedidos fictícios; os dados não representam clientes reais."""
    rng = np.random.default_rng(RANDOM_SEED)
    restaurant_ids = [item[0] for item in RESTAURANTS]
    start = pd.Timestamp("2025-01-01")
    timestamps = start + pd.to_timedelta(
        rng.integers(0, 365 * 24 * 60, size=number_of_orders), unit="m"
    )
    statuses = rng.choice(STATUSES, size=number_of_orders, p=STATUS_PROBABILITIES)
    prep = rng.integers(10, 51, size=number_of_orders)
    delivery = rng.integers(15, 76, size=number_of_orders)
    ratings = rng.integers(1, 6, size=number_of_orders).astype(float)

    # Avaliações e tempos concluídos só existem para pedidos entregues.
    for i, status in enumerate(statuses):
        if status != "entregue":
            ratings[i] = np.nan
            if status == "cancelado":
                delivery[i] = 0

    rows = []
    for i in range(number_of_orders):
        restaurant = RESTAURANTS[int(rng.integers(0, len(RESTAURANTS)))]
        rows.append({
            "id_pedido": i + 1,
            "id_restaurante": restaurant[0],
            "nome_restaurante": restaurant[1],
            "cidade_restaurante": restaurant[2],
            "categoria": restaurant[3],
            "id_cliente": int(rng.integers(1, 501)),
            "data_pedido": timestamps[i],
            "valor": round(float(rng.uniform(18, 180)), 2),
            "status": statuses[i],
            "tempo_preparo_min": int(prep[i]),
            "tempo_entrega_min": int(delivery[i]),
            "avaliacao": ratings[i],
        })

    df = pd.DataFrame(rows)
    df["data_pedido"] = pd.to_datetime(df["data_pedido"])
    return df.sort_values("data_pedido").reset_index(drop=True)


def save_raw_data(number_of_orders: int = 1500) -> pd.DataFrame:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_orders(number_of_orders)
    df.to_csv(CSV_PATH, index=False, encoding="utf-8")
    return df


if __name__ == "__main__":
    data = save_raw_data()
    print(f"Arquivo criado: {CSV_PATH}")
    print(f"Registros: {len(data)}")
