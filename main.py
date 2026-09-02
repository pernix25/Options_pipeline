# 2026-09-02 MC: this file is deprecated as this project is now run using Airflow

from database import PostgresDatabase
from poly import PolygonClient
from pipeline import ETLPipeline
import json
from pathlib import Path

def main():
    db = PostgresDatabase()
    poly = PolygonClient()
    pipeline = ETLPipeline(db, poly)

    # Path to the directory containing this Python file
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "config.json"

    # Load configuration
    with config_path.open("r") as file:
        config = json.load(file)

    tickers = config["tickers"]

    pipeline.start()
    
    pipeline.get_option_contracts(tickers)
    
    pipeline.get_option_prices()

    # commit and close the database connection
    pipeline.end()

if __name__ == "__main__":
    main()