# 2026-07-05 MC: Created file

# Import dependencies
import pandas as pd
import numpy as np

class DataTransformer:
    def __init__(
            self
            , contracts: list[dict]
        ) -> None:

        self.contracts = pd.DataFrame(contracts)
        # Seperate the contracts into 2 seperate data frames: calls & puts
        self.calls = self.contracts[self.contracts["contract_type"] == "call"].copy()
        self.puts = self.contracts[self.contracts["contract_type"] == "put"].copy()

    def get_exp_dts(self) -> np.ndarray:
        """
        Retrieves the unique option expiration dates from the loaded contracts.

        Returns
        -------
        np.ndarray
            A NumPy array containing the unique expiration dates for all
            loaded option contracts.

        Notes
        -----
        - The order of the returned dates matches their first occurrence in
        the underlying DataFrame.
        - Returns an empty NumPy array if no contracts are loaded.
        """
        return self.contracts['expiration'].unique()
    
    def get_opts_near_stock_price(
            self
            , stock_price: float
            , num_contracts: int
            , option_type: str
        ) -> pd.DataFrame:
        """
        Returns option contracts surrounding the current stock price.
        
        This method finds the option contract with the strike price closest to the
        provided stock price (at-the-money) and returns a collection of contracts
        consisting of:

        - The closest strike price (ATM)
        - Up to ``num_contracts`` strikes above & below the ATM strike

        The resulting DataFrame is sorted by strike price in ascending order.

        Parameters
        ----------
        stock_price : float
            The current price of the underlying stock. The value is rounded to the
            nearest whole number before determining the closest strike.

        num_contracts : int
            The number of option contracts to include above and below the
            at-the-money strike.

        option_type : str
            The type of option contracts to retrieve. Accepted values are:
            ``"CALL"``, ``"CALLS"``, ``"PUT"``, or ``"PUTS"`` (case-insensitive).

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the selected option contracts sorted by strike
            price.

        Raises
        ------
        ValueError
            If ``option_type`` is not one of the supported values.

        ValueError
            If no option contracts exist for the requested option type.

        Notes
        -----
        The returned DataFrame may contain fewer than
        ``(2 * num_contracts + 1)`` rows if there are insufficient strikes above
        or below the at-the-money strike.

        Example
        -------
        >>> chain.get_opts_near_stock_price(
        ...     stock_price=184.72,
        ...     num_contracts=2,
        ...     option_type="calls"
        ... )

        Returns contracts with strikes similar to:

            180
            182.5
            185  <- closest (ATM)
            187.5
            190
        """
        # Round stock price
        stock_price = round(stock_price)


        option_type = option_type.upper()

        # If option type is not 'calls' or 'puts', throw value error 
        if option_type not in ('CALL', 'CALLS', 'PUT', 'PUTS'):
            raise ValueError("option_type needs to be either 'calls' or 'puts'")
        
        # Set up df as the appropiate option dataframe
        if option_type in ('CALL', 'CALLS'):
            df = self.calls
        else:
            df = self.puts

        # Raise error if dataframe is empty
        if df.empty:
            raise ValueError(f'No {option_type} options found.')

        # Calculate the closest strike based on the stocks price
        closest_strike = df.iloc[(df["strike"] - stock_price).abs().argmin()]

        # Grab the nth number of contracts below the closest strike price
        below = (
            df[df["strike"] < closest_strike]
            .nlargest(num_contracts, "strike")
        )

        # Grab the contract details for the closest strike price
        atm = df[df["strike"] == closest_strike]

         # Grab the nth number of contracts above the closest strike price
        above = (
            df[df["strike"] > closest_strike]
            .nsmallest(num_contracts, "strike")
        )

        # Combine all of the data frames into one single data frame
        result = (
            pd.concat([below, atm, above])
            .sort_values("strike")
            .reset_index(drop=True)
        )

        return result
