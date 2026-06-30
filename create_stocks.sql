/*2026-06-28 MC: Created stocks.stocks table



stock_id: Unique identifier for stock information
ticker: stock ticker symbol used on robinhood
stock_nm: full name of the stock
load_dts: time the record was uploaded into the table
*/

create table stocks.stocks(
  stock_id serial primary key
  , ticker varchar(6)
  , stock_nm varchar(16)
  , load_dts timestampz
);
