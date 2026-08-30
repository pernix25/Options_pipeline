# 2026-07-28 MC: Created file

# Ideas
# move caching, getting contract, and getting contract prices into pipeline methods

from database import PostgresDatabase
from transformer import DataTransformer
from poly import PolygonClient
from datetime import date, timedelta

class ETLPipeline:
    def __init__(
            self
            , database: PostgresDatabase
            , polygon_client: PolygonClient
        ) -> None:
        
        self.db = database
        self.polygon = polygon_client

    def start(self) -> None:
        """
        Starts the ETL pipeline by establishing a database connection.

        Creates a PostgreSQL cursor that will be used throughout the ETL
        process for executing SQL statements.
        """
        self.cursor = self.db.connect()
    
    def get_option_contracts(self, tickers) -> None:
        
        # cache the database's stock ids
        stocks_table_query = "SELECT stock_id, ticker FROM stocks.stocks"
        self.cursor.execute(stocks_table_query)
        self.stock_ids = {
            ticker : stock_id
            for stock_id, ticker in self.cursor.fetchall()
        }

        # cache the polygon option ids that already exist within the databse
        options_id_query = "SELECT poly_id FROM stocks.options"
        self.cursor.execute(options_id_query)
        self.option_ids = [row[0] for row in self.cursor.fetchall()]

        for ticker in tickers:
            # get all option contracts for a ticker 
            chain = DataTransformer(self.polygon.get_option_chain(ticker))

            # get the available option expiration dates, select the one that is roughly a week out
            exp_dts = chain.get_exp_dts()
            main_dt = exp_dts[2]

            # limit the option chain to contracts with the selected expiration date
            chain.trim(main_dt)

            # retrieve the stock's most recent closing price from Polygon
            # this price is used to identify options near the current stock price
            stock_price = self.polygon.yesterday_stock_price(ticker)

            # process both call and put options for the selected expiration date
            for option_type in ('call', 'put'):
                df = chain.get_opts_near_stock_price(stock_price, 10, option_type)

                for row in df.itertuples():
                    # skip the option if it has already been loaded into the database
                    if row.poly_opt_id in self.option_ids:
                        continue

                    # convert the option type into a boolean flag for the database
                    # True represents a call and False represents a put
                    if row.contract_type == "call":
                        call_flag = True
                    else:
                        call_flag = False

                    # insert the new option contract into the database.
                    self.cursor.execute(
                        """INSERT INTO stocks.options 
                        (stock_id, strike_price, exp_dt, call_flag, load_dts, poly_id) 
                        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s)"""
                        , (self.stock_ids[ticker], row.strike, row.exp_dt, call_flag, row.poly_opt_id)
                    )
        # commit inserts 
        self.db.commit()

    def get_option_prices(self) -> None:
        
        # refresh options cache
        poly_id_query = "SELECT poly_id, option_id FROM stocks.options"
        self.cursor.execute(poly_id_query)
        poly_cache = {row[0] : row[1] for row in self.cursor.fetchall()}

        # get new option contracts cache
        options_table_query = """
            SELECT 
                o.poly_id
                , s.ticker
                , o.strike_price
                , o.exp_dt
                , o.call_flag
            FROM stocks.options o
            JOIN stocks.stocks s
                ON o.stock_id = s.stock_id
            WHERE exp_dt >= %s"""
        self.cursor.execute(options_table_query, (date.today(), )) # execute requires a tuple or list of parameters
        self.options_table = [{"polygon id" : row[0]
                        , "ticker" : row[1]
                        , "strike price" : row[2]
                        , "expiration date" : row[3]
                        , "option type" : "call" if row[4] else "put"
                        } for row in self.cursor.fetchall()]

        for option in self.options_table:
            contract_data = self.polygon.get_option_data(option["polygon id"], 1, "minute", date.today() - timedelta(days=1), date.today() - timedelta(days=1))

            # if there are no orders for an opiton, the request will be None, therefore skip to next contract
            if contract_data == None:
                continue

            for row in contract_data:
                self.cursor.execute(
                    """
                    INSERT INTO stocks.option_market_data
                    (option_id, open_price, high_price, low_price, close_price, volume, vwap, transactions, market_dts, load_dts)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"""
                    , (poly_cache[option["polygon id"]], row['open'], row['high'], row['low'], row['close'], row['volume'], row['vwap'], row['transactions'], row['timestamp'])
                )
            
            # commit inserts
            self.db.commit()
