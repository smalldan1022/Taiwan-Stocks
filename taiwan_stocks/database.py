import traceback

import pandas as pd
from sqlalchemy import CHAR, Column, MetaData, Table, and_, create_engine, delete, text
from sqlalchemy.exc import SQLAlchemyError

from taiwan_stocks.config import DBConfig


class StockDatabase:
    def __init__(self, **kwargs):
        self.config = DBConfig()
        self.engine = create_engine(self.config.url)
        self.metadata = MetaData()
        self.table_name = kwargs["table_name"]
        self.stock_table = Table(
            self.table_name,
            self.metadata,
            Column("Date", CHAR(20), primary_key=True),
            Column("證券代號", CHAR(20), nullable=False),
            Column("證券名稱", CHAR(20), nullable=False),
            Column("成交股數", CHAR(100)),
            Column("成交筆數", CHAR(100)),
            Column("成交金額", CHAR(100)),
            Column("開盤價", CHAR(100), nullable=False),
            Column("最高價", CHAR(100), nullable=False),
            Column("最低價", CHAR(100), nullable=False),
            Column("收盤價", CHAR(100), nullable=False),
            Column("漲跌(+/-)", CHAR(100), nullable=True),
            Column("漲跌價差", CHAR(100), nullable=True),
            Column("外陸資買進股數(不含外資自營商)", CHAR(100)),
            Column("外陸資賣出股數(不含外資自營商)", CHAR(100)),
            Column("外陸資買賣超股數(不含外資自營商)", CHAR(100)),
            Column("外資自營商買進股數", CHAR(100)),
            Column("外資自營商賣出股數", CHAR(100)),
            Column("外資自營商買賣超股數", CHAR(100)),
            Column("投信買進股數", CHAR(100)),
            Column("投信賣出股數", CHAR(100)),
            Column("投信買賣超股數", CHAR(100)),
            Column("自營商買賣超股數", CHAR(100)),
            Column("自營商買進股數(自行買賣)", CHAR(100)),
            Column("自營商賣出股數(自行買賣)", CHAR(100)),
            Column("自營商買賣超股數(自行買賣)", CHAR(100)),
            Column("自營商買進股數(避險)", CHAR(100)),
            Column("自營商賣出股數(避險)", CHAR(100)),
            Column("自營商買賣超股數(避險)", CHAR(100)),
            Column("三大法人買賣超股數", CHAR(100)),
            Column("本益比", CHAR(20)),
            Column("股價淨值比", CHAR(20)),
            Column("殖利率(%)", CHAR(20)),
            Column("股利年度", CHAR(20)),
            Column("財報年/季", CHAR(20)),
            mysql_charset="utf8",
            mysql_engine="InnoDB",
        )

        assert self.config is not None, "Error: the database settings is empty!!"
        # create a table
        self.metadata.create_all(self.engine)

    def fetch_df(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = pd.read_sql_table(self.table_name, con=self.engine)
            return df
        except SQLAlchemyError as e:
            print(f"Fetch failed: {e}")
            return pd.DataFrame()

    def insert_df(self, df: pd.DataFrame) -> None:
        # map column names to safe parameter names, col_0, col_1...
        # avoid the (+/-) and (%) sql syntax issue
        columns = df.columns.tolist()
        safe_columns = {col: f"col_{i}" for i, col in enumerate(columns)}

        col_str = ", ".join(f"`{col}`" for col in columns)
        val_str = ", ".join(f":{safe_columns[col]}" for col in columns)

        sql = text(f"REPLACE INTO `{self.table_name}` ({col_str}) VALUES ({val_str})")

        try:
            with self.engine.begin() as conn:
                for _, row in df.iterrows():
                    # map row keys to safe ones
                    row_dict = row.to_dict()
                    safe_row_dict = {safe_columns[k]: v for k, v in row_dict.items()}
                    conn.execute(sql, safe_row_dict)
            print("Data inserted successfully.")
        except SQLAlchemyError as e:
            print(f"Insert failed: {e}")

    def delete(self, stock_id: str, target_date: str) -> None:
        try:
            stmt = delete(self.stock_table).where(
                and_(
                    self.stock_table.c.Date == target_date,
                    self.stock_table.c["證券代號"] == stock_id,
                )
            )
            with self.engine.begin() as conn:
                conn.execute(stmt)
            print(f"Deleted records where 證券代號 = {stock_id} and Date = {target_date}")
        except SQLAlchemyError:
            print("Delete failed.")
            traceback.print_exc()

    def fetch_stock_statistics(self):
        print("Fetching stocks statistics...")

        # 使用connect指定的Mysql獲取資料
        self.df_stocks = pd.read_sql(
            f"SELECT * FROM stocks.{self.table_name}", con=self.engine.begin()
        )
        self.df_institutional_investors = pd.read_sql(
            f"SELECT * FROM stocks.{self.table_name}", con=self.engine.begin()
        )

        # 先把Date的部分轉回str，不然後面畫圖會出錯
        self.df_stocks["Date"] = self.df_stocks["Date"].str
        self.df_institutional_investors["Date"] = self.df_institutional_investors["Date"].str

        # 要篩選出日期區間內的data
        assert not self.df_stocks.Date.empty, "This stock's data doesn't exist in this database!"
        assert int(self.dates[-1]) >= int(self.df_stocks.Date.min()) and int(self.dates[0]) <= int(
            self.df_stocks.Date.max()
        ), "This stock's data doesn't exist in this database!!"

        if int(self.dates[0]) <= int(self.df_stocks.Date.min()) or int(self.dates[-1]) >= int(
            self.df_stocks.Date.max()
        ):
            print("Fetching the maximum data...")

            Min_date = max(self.df_stocks.Date.min(), self.dates[0])
            Max_date = min(self.df_stocks.Date.max(), self.dates[-1])

            print(f"The maximum data in MySQL: {Min_date} - {Max_date}")
            print("Fetching the data...")

        self.df_stocks = self.df_stocks[
            (self.df_stocks.Date >= self.dates[0]) & (self.df_stocks.Date <= self.dates[-1])
        ]
        self.df_institutional_investors = self.df_institutional_investors[
            (self.df_institutional_investors.Date >= self.dates[0])
            & (self.df_institutional_investors.Date <= self.dates[-1])
        ]

        # reset一下index值，不然後面的會有問題
        self.df_stocks.reset_index(drop=True, inplace=True)
        self.df_institutional_investors.reset_index(drop=True, inplace=True)

    def close(self):
        self.engine.dispose()
