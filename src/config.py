from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DATABASE_DIR = ROOT_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "delivery_intelligence.db"
CSV_PATH = DATA_RAW_DIR / "pedidos.csv"

RANDOM_SEED = 42
