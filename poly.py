# 2026-07-05 MC: Created file

# Import dependencies
from polygon import RESTClient
from datetime import datetime
from zoneinfo import ZoneInfo

class PolygonClient:
    def __init__(self, api_key:str) -> None:
        self.client = RESTClient(api_key)

    def get_option_chain(
            self
            , ticker:str
        ) -> list[dict]:
        """
        Retrieves all listed option contracts for a given underlying security.

        Parameters
        ----------
        ticker : str
            The underlying stock or ETF ticker symbol (e.g., "AAPL", "SPY").

        Returns
        -------
        list[dict]
            A list containing one dictionary per option contract with the
            following key-pairs:

            - poly_opt_id : Polygon option ticker symbol.
            - ticker : Underlying security ticker.
            - exp_dt : Contract expiration date.
            - strike : Strike price.
            - contract_type : Option type ("call" or "put").

        Raises
        ------
        polygon.exceptions.BadResponse
            If Polygon returns an unsuccessful response.

        requests.exceptions.RequestException
            If a network or connection error occurs.

        Notes
        -----
        - Retrieves up to 1,000 contracts per API request and automatically
        follows pagination until all contracts have been collected.
        - The returned DataFrame is intended for downstream ETL processing
        and database ingestion.
        - An empty DataFrame is returned if no option contracts are available
        for the specified ticker.
        """
        contracts = []

        for contract in self.client.list_options_contracts(
                underlying_ticker = ticker,
                limit = 1000
        ):

            contracts.append({
                "poly_opt_id": contract.ticker
                , "ticker": contract.underlying_ticker
                , "exp_dt": contract.expiration_date
                , "strike": contract.strike_price
                , "contract_type": contract.contract_type
            })

        return contracts
    
    def get_stock_data(
            self
            , ticker: str
            , aggregate: int
            , timespan: str
            , start_dt: datetime
            , end_dt: datetime
        ) -> list[dict]:
        """
        Retrieves aggregated market data for a given stock ticker from Polygon.io.

        Parameters
        ----------
        ticker : str
            Stock or ETF ticker symbol (e.g., "AAPL", "SPY").

        aggregate : int
            Size of the aggregation window (multiplier). For example:
            - 1 with timespan="minute" → 1-minute bars
            - 5 with timespan="minute" → 5-minute bars
            - 1 with timespan="day" → daily bars

        timespan : str
            The unit of aggregation (e.g., "minute", "hour", "day").

        start_dt : datetime
            Start datetime for the historical data query (inclusive).

        end_dt : datetime
            End datetime for the historical data query (inclusive).

        Returns
        -------
        list[dict]
            A list of dictionaries, where each dictionary represents one bar:

            - open : float
                Opening price of the interval.
            - close : float
                Closing price of the interval.
            - high : float
                Highest price during the interval.
            - low : float
                Lowest price during the interval.
            - volume : int
                Number of shares traded during the interval.
            - vwap : float
                Volume-weighted average price for the interval.
            - transactions : int
                Number of individual trades executed in the interval.
            - timestamp : str
                Human-readable timestamp converted from Polygon epoch (ms, UTC)
                into America/Denver local time

        Notes
        -----
        - This method automatically converts Polygon epoch timestamps (milliseconds)
        into timezone-aware Mountain Time (America/Denver).
        - Output is formatted for readability and downstream ETL consumption,
        not raw numerical time-series processing.

        Raises
        ------
        polygon.exceptions.BadResponse
            If the API request fails or returns an error.

        requests.exceptions.RequestException
            If there is a network or connectivity issue.
        """
        
        stock_data = []

        for bar in self.client.get_aggs(
            ticker = ticker
            , multiplier = aggregate
            , timespan = timespan
            , from_ = start_dt
            , to = end_dt
        ):
            
            stock_data.append({
                "open": bar.open
                , "close": bar.close
                , "high": bar.high
                , "low": bar.low
                , "volume": bar.volume
                , "vwap": bar.vwap
                , "transactions": bar.transactions
                , "timestamp": datetime.fromtimestamp(
                    # Converts Polygon epoch timestamp (milliseconds, UTC) 
                    # into America/Denver local time and formats it as a human-readable string
                    bar.timestamp / 1000,tz=ZoneInfo("UTC")
                    ).astimezone(ZoneInfo("America/Denver"))
            })

        return stock_data

    def get_option_data(
            self
            , poly_opt_id: str
            , aggregate: int
            , timespan: str
            , start_dt: datetime
            , end_dt: datetime
        ) -> list[dict]:
        """
        Retrieve historical aggregate data for a single option contract.

        Parameters
        ----------
        poly_opt_id : str
            Polygon option contract identifier (e.g., "O:AAPL240719C00200000").

        aggregate : int
            Size of the aggregation window. Examples:
            - 1 with timespan="minute" → 1-minute bars
            - 5 with timespan="minute" → 5-minute bars
            - 1 with timespan="day" → daily bars

        timespan : str
            The unit of aggregation (e.g., "minute", "hour", "day").

        start_dt : datetime
            Start datetime for historical data retrieval (inclusive).

        end_dt : datetime
            End datetime for historical data retrieval (inclusive).

        Returns
        -------
        list[dict]
            A list of dictionaries where each dictionary represents a single
            aggregate bar for the option contract:

            - open : float
                Opening price of the option during the interval.
            - high : float
                Highest traded price during the interval.
            - low : float
                Lowest traded price during the interval.
            - close : float
                Closing price of the interval.
            - volume : int
                Number of contracts traded during the interval.
            - vwap : float
                Volume-weighted average price for the interval.
            - transactions : int
                Number of individual trades executed during the interval.
            - timestamp : datetime
                Time of the aggregate bar converted from Polygon epoch
                (milliseconds, UTC) into America/Denver local time.

        Notes
        -----
        - This function automatically converts UTC epoch timestamps into
        Mountain Time (America/Denver), accounting for daylight saving time.

        Raises
        ------
        polygon.exceptions.BadResponse
            If the API request fails or returns invalid data.

        requests.exceptions.RequestException
            If a network or connectivity error occurs.
        """

        contract_data =[]

        for bar in self.client.get_aggs(
            ticker = poly_opt_id
            , multiplier = aggregate
            , timespan = timespan
            , from_ = start_dt
            , to = end_dt
        ):
            
            contract_data.append({
                "open": bar.open
                , "high": bar.high
                , "low": bar.low
                , "close": bar.close
                , "volume": bar.volume
                , "vwap": bar.vwap
                , "transactions": bar.transactions
                , "timestamp": datetime.fromtimestamp(
                    # Converts Polygon epoch timestamp (milliseconds, UTC) 
                    # into America/Denver local time and formats it as a human-readable string
                    bar.timestamp / 1000,tz=ZoneInfo("UTC")
                    ).astimezone(ZoneInfo("America/Denver"))
            })

            return contract_data
