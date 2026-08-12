# 2026-07-28 MC: Created file

from database import PostgresDatabase
from poly import PolygonClient
from pipeline import ETLPipeline
from transformer import DataTransformer
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
    cursor = pipeline.cursor

    # cache the database's stock ids
    stocks_table_query = "SELECT stock_id, ticker FROM stocks.stocks"
    cursor.execute(stocks_table_query)
    stock_cache = {
        ticker : stock_id
        for stock_id, ticker in cursor.fetchall()
    }

    options_table_query = "SELECT poly_id FROM stocks.options"
    cursor.execute(options_table_query)
    options_cache = [row[0] for row in cursor.fetchall()]

    for ticker in tickers:
        chain = DataTransformer(pipeline.polygon.get_option_chain(ticker))

        exp_dts = chain.get_exp_dts()
        main_dt = exp_dts[2]

        chain.trim(main_dt)

        stock_price = poly.yesterday_stock_price(ticker)

        for option_type in ('call', 'put'):
            df = chain.get_opts_near_stock_price(stock_price, 10, option_type)

            for row in df.itertuples():
                if row.poly_opt_id in options_cache:
                    continue

                if row.contract_type == "call":
                    call_flag = True
                else:
                    call_flag = False

                cursor.execute(
                    """INSERT INTO stocks.options 
                    (stock_id, strike_price, exp_dt, call_flag, load_dts, poly_id) 
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s)"""
                    , (stock_cache[ticker], row.strike, row.exp_dt, call_flag, row.poly_opt_id)
                )

    pipeline.db.commit()
    pipeline.db.close()

if __name__ == "__main__":
    main()