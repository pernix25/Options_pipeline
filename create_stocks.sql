/*2026-06-28 MC: Created stocks.stocks table*/
create table stocks.stocks(
  stock_id serial primary key
  , ticker varchar(6)
  , stock_nm varchar(16)
  , load_dts timestampz
);
