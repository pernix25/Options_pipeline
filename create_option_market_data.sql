/*2026-07-12 MC: Created stocks.option_market_data



Terminalogy:
candle - aggregate period of time, most likely 1 minute of trading



urowid: unique row identifier
option_id: unique identifier for stocks 
open_price: opening price of the candle
high_price: highest price of the candle
low_price: lowest price of the candle
close_price: closing price of the candle
volume: total number of contracts bought during the candle timeframe
vwap: average price at which the option contract traded during the candle, weighted by the number of contracts traded
transactions: number of individual trades that occurred during the candle, not the number of option contracts traded
market_dts: time at which the trade data occured
load_dts: time the record was uploaded into the table
*/

create table stocks.option_market_data(
    urowid serial primary key 
    , option_id INT REFERENCES stocks.options(option_id)
    , open_price decimal(7, 3) -- xxxx.xxx
    , high_price decimal(7,3)
    , low_price decimal(7,3)
    , close_price decimal(7,3)
    , volume int
    , vwap decimal(8,4) -- xxxx.xxxx
    , transactions int
    , market_dts timestamptz
    , load_dts timestamptz default current_timestamp
);