import traceback

import pandas as pd
import pymysql


class MySQL:
    def __init__(self, db_settings, **kwargs):
        # Initialization
        self.db_settings = db_settings
        self.table_sql = f"""CREATE TABLE `{self.table_name}` (
                            `Date` int(10) NOT NULL AUTO_INCREMENT,
                            `證券代號` char(20) NOT NULL,
                            `證券名稱` char(20) NOT NULL,
                            `成交股數` char(100) DEFAULT NULL,
                            `成交筆數` char(100) DEFAULT NULL,
                            `成交金額` char(100) DEFAULT NULL,
                            `開盤價` char(100) NOT NULL,
                            `最高價` char(100) NOT NULL,
                            `最低價` char(100) NOT NULL,
                            `收盤價` char(100) NOT NULL,
                            `漲跌(+/-)` char(100) DEFAULT NULL,
                            `漲跌價差` char(100) NOT NULL,
                            `外陸資買進股數(不含外資自營商)` char(100) DEFAULT NULL ,
                            `外陸資賣出股數(不含外資自營商)` char(100) DEFAULT NULL ,
                            `外陸資買賣超股數(不含外資自營商)` char(100) DEFAULT NULL ,
                            `外資自營商買進股數` char(100) DEFAULT NULL ,
                            `外資自營商賣出股數` char(100) DEFAULT NULL ,
                            `外資自營商買賣超股數` char(100) DEFAULT NULL ,
                            `投信買進股數` char(100) DEFAULT NULL ,
                            `投信賣出股數` char(100) DEFAULT NULL ,
                            `投信買賣超股數` char(100) DEFAULT NULL ,
                            `自營商買賣超股數` char(100) DEFAULT NULL ,
                            `自營商買進股數(自行買賣)` char(100) DEFAULT NULL ,
                            `自營商賣出股數(自行買賣)` char(100) DEFAULT NULL ,
                            `自營商買賣超股數(自行買賣)` char(100) DEFAULT NULL ,
                            `自營商買進股數(避險)` char(100) DEFAULT NULL ,
                            `自營商賣出股數(避險)` char(100) DEFAULT NULL ,
                            `自營商買賣超股數(避險)` char(100) DEFAULT NULL ,
                            `三大法人買賣超股數` char(100) DEFAULT NULL ,
                            `本益比` char(20) DEFAULT NULL,
                            `股價淨值比` char(20) DEFAULT NULL,
                            `殖利率` char(20) DEFAULT NULL,
                            `股利年度` char(20) DEFAULT NULL,
                        PRIMARY KEY (`Date`)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        self.db = None
        self.cursor = None

        print("\n  {}".format("(4) Manipulating the data"))
        print("----------------------------------------\n")

        assert self.db_settings is not None, "Error: the database settings is empty!!"
        self.open_connection()
        self.create_cursor()

        # Create a table
        if self.check_if_table_exist():
            self.create_table()

    def open_connection(self):
        try:
            self.db = pymysql.connect(**self.db_settings)
            self.cursor = self.db.cursor()
            print("MySQL Connected...")
        except Exception as err:
            print("Error connecting to MySQL:", err)

    def create_cursor(self):
        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor()

    def create_table(self):
        self.cursor.execute(self.table_sql)
        print("MySQL table created Successfully...")

    def check_if_table_exist(self):
        # Drop table if it already exist, using execute() method.
        check_table_sql = "SHOW TABLES"

        self.cursor.execute(check_table_sql)
        results = self.cursor.fetchall()
        tables = [item[0] for item in results]

        if self.table_name in tables:
            print("This table already exists...")
            return False
        else:
            print("This table does not exist, creating table...")
            return True

    def insert(self, insert_sql):
        try:
            self.cursor.execute(insert_sql)
            self.db.commit()
            print("Insert successfully.")
        except:  # noqa: E722
            self.db.rollback()
            traceback.print_exc()

    def delete(self, delete_sql):
        try:
            # Execute the SQL command
            self.cursor.execute(delete_sql)
            # Commit your changes in the database
            self.db.commit()
            print("Delete successfully.")
        except:  # noqa: E722
            self.db.rollback()
            traceback.print_exc()

    def fetch(self, fetch_sql):
        # 使用者有可能原本用完後關掉db connect，然後再次使用fetch功能，因此要先連結
        self.open_connection()
        self.create_cursor()
        try:
            # Execute the SQL command
            self.cursor.execute(fetch_sql)
            # Fetch all the rows in a list of lists.
            results = self.cursor.fetchall()

            for idx, row in enumerate(results):
                print(f"row-{idx} data: {row}")
        except:  # noqa: E722
            traceback.print_exc()

    def fetch_stock_statistics(self):
        print("Fetching stocks statistics...")
        # 使用者有可能原本用完後關掉db connect，然後再次使用Fetch功能，因此要先連結
        self.open_connection()
        self.create_cursor()

        # 使用connect指定的Mysql獲取資料
        self.df_stocks = pd.read_sql(f"SELECT * FROM stocks.{self.table_name}", con=self.db)
        self.df_institutional_investors = pd.read_sql(
            f"SELECT * FROM stocks.{self.table_name}", con=self.db
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

    def close_db(self):
        self.db.close()
