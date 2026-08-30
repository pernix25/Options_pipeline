# 2026-07-28 MC: Created file

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
    cursor = pipeline.cursor # once new pipeliine funcitons are completed, this line needs to be deleted
    
    pipeline.get_option_contracts(tickers)
    
    pipeline.get_option_prices()

    # commit and close the database connection
    pipeline.db.commit()
    pipeline.db.close()

if __name__ == "__main__":
    main()