from src.pipeline import run_pipeline

if __name__ == "__main__":
    summary = run_pipeline()
    print("=== DELIVERY INTELLIGENCE ===")
    print("Pipeline executado com sucesso!")
    print(f"Pedidos processados: {summary['orders_processed']}")
    print(f"Restaurantes: {summary['restaurants']}")
    print(f"Clientes: {summary['customers']}")
    print(f"Banco SQLite: {summary['database_path']}")
