"""Orquestra a geração, limpeza e carga dos dados."""
from src.config import CSV_PATH, DATABASE_PATH, DATA_PROCESSED_DIR
from src.generate_data import save_raw_data
from src.data_processing import load_and_clean_data
from src.database import save_orders


def run_pipeline(number_of_orders: int = 1500) -> dict:
    raw_df = save_raw_data(number_of_orders)
    clean_df = load_and_clean_data(CSV_PATH)

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(DATA_PROCESSED_DIR / "pedidos_tratados.csv",
                    index=False, encoding="utf-8")
    save_orders(clean_df, DATABASE_PATH)

    return {
        "orders_processed": len(clean_df),
        "restaurants": clean_df["id_restaurante"].nunique(),
        "customers": clean_df["id_cliente"].nunique(),
        "database_path": str(DATABASE_PATH),
        "raw_orders": len(raw_df),
    }
