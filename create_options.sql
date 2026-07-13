/*2026-06-29 MC: Created stocks.options table



option_id: unique identifier for option contracts
stock_id: unique identifier for stocks 
strike_price: Price at which an option can be exercised.
exp_dt: Specified date when an options contract expires and ceases to be valid
call_flag: Boolean flag denoting call (true/1) versus put (false/0) option type
load_dts: time the record was uploaded into the table
*/

create table stocks.options(
    option_id serial primary key
    , stock_id INT REFERENCES stocks.stocks(stock_id)
    , strike_price decimal(6, 2)
    , exp_dt date
    , call_flag boolean
    , load_dts timestamptz default current_timestamp
);