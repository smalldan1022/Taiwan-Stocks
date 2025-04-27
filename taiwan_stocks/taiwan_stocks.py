from datetime import date
from io import StringIO

import pandas as pd
import requests
from dateutil.rrule import DAILY, rrule

from taiwan_stocks.crawl import CrawlerDirector, OTCCrawler, TPECrawler
from taiwan_stocks.database import StockDatabase
from taiwan_stocks.stocks_analysis import Analyzer
from taiwan_stocks.stocks_draw import Drawer


class TaiwanStocks:
    def __init__(
        self,
        is_save: bool = False,
        is_draw: bool = False,
        is_analyze: bool = False,
        save_path: str = "",
        **kwargs,
    ) -> None:
        self.stock_name = ""
        self.stock_num = ""
        self.start_date = ""
        self.end_date = ""
        self.table_name = ""
        self.is_tse = False
        self.is_otc = False
        self.is_save = is_save
        self.is_draw = is_draw
        self.is_analyze = is_analyze
        self.save_path = save_path
        self.title_num = 1

    def run(self) -> None:
        if (self.stock_name or self.stock_num) and self.start_date and self.end_date:
            self._direct_mode()
        else:
            self._interactive_mode()

    def _interactive_mode(self) -> None:
        self.get_user_input()
        self._main_flow()

    def _direct_mode(self) -> None:
        print(f"\n({self.title_num}) Use direct parameters")
        print("----------------------------------------")
        if self.stock_name:
            print(f"The stock number is {self.stock_name}")
        if self.stock_num:
            print(f"The stock number is {self.stock_num}")
        print(f"Start date is {self.start_date}")
        print(f"End date is {self.end_date}")
        self.title_num += 1
        self._main_flow()

    def _main_flow(self) -> None:
        self.dates = self._calculate_date_range(self.start_date, self.end_date)
        self.check_stock_market()

        cld = CrawlerDirector()
        crawler = (
            TPECrawler(stock_name=self.stock_name, stock_num=self.stock_num, dates=self.dates)
            if self.is_tse
            else OTCCrawler(stock_name=self.stock_name, stock_num=self.stock_num, dates=self.dates)
        )
        cld.builder = crawler
        print(f"\n({self.title_num}) Start crawling")
        print("----------------------------------------")
        self.title_num += 1
        cld.build_full_featured_product()
        df_stocks = crawler.product.data
        if df_stocks.empty:
            print("The data is empty")
            return

        if self.is_save:
            print(f"\n({self.title_num}) Save data into database")
            print("----------------------------------------")
            self.title_num += 1
            self.stock_db = StockDatabase(table_name=self.stock_name)
            self.stock_db.insert_df(df_stocks)

        if self.is_draw:
            print(f"\n({self.title_num}) Draw the stock plots")
            print("----------------------------------------")
            self.title_num += 1
            self.drawer = Drawer(
                stock_name=self.stock_name, stock_num=self.stock_num, df_stocks=df_stocks
            )
            self.drawer.draw_plots(
                K_plot=True,
                volumn_plot=True,
                D_5MA=True,
                D_10MA=True,
                D_20MA=True,
                D_60MA=True,
                D_IT=True,
                D_FI=True,
                D_DL=True,
                save_fig=True,
                file_name=f"{self.stock_name}-{self.stock_num}",
                save_path=self.save_path,
            )

        if self.is_analyze:
            print(f"\n({self.title_num}) Analyze the stock")
            print("----------------------------------------")
            self.title_num += 1
            self.analyzer = Analyzer(df_stocks=df_stocks)

        print(f"\n({self.title_num}) Close the program")
        print("----------------------------------------")
        self.title_num += 1
        print("\nProgram Finished...\n")

    def get_user_input(self) -> None:
        print(f"\n({self.title_num}) Enter the stock name or number")
        print("----------------------------------------")
        self.title_num += 1
        self.stock_name = input("Stock name (can leave blank): ").strip()
        self.stock_num = input("Stock number (can leave blank): ").strip()

        assert (
            self.stock_name or self.stock_num
        ), "Please enter at least stock name or stock number."

        print(f"\n({self.title_num}) Enter date range (format: YYYYMMDD)")
        print("----------------------------------------")
        self.title_num += 1
        print("\n{:^39}".format("The Date Format"))
        print("########################################")
        print("#{:^38}#".format("start time -> 20210101"))
        print("#{:^38}#".format("End time   -> 20210228"))
        print("########################################")
        self.start_date = input("\nStart date: ").strip()
        self.end_date = input("End date:   ").strip()

    def _calculate_date_range(self, start_time: str, end_time: str) -> list[str]:
        """Calculate list of dates between start_date and end_date in YYYYMMDD format."""
        start_year = int(start_time[:4])
        start_month = int(start_time[4:6])
        start_day = int(start_time[6:])
        end_year = int(end_time[:4])
        end_month = int(end_time[4:6])
        end_day = int(end_time[6:])

        start_date = date(start_year, start_month, start_day)
        end_date = date(end_year, end_month, end_day)

        return [dt.strftime("%Y%m%d") for dt in rrule(DAILY, dtstart=start_date, until=end_date)]

    def check_stock_market(self) -> None:
        print(f"\n({self.title_num}) Check stock info")
        print("----------------------------------------")
        self.title_num += 1

        if self.check_tse():
            self.is_tse = True
            print("Found in TWSE (上市)")
        elif self.check_otc():
            self.is_otc = True
            print("Found in TPEx (上櫃)")
        else:
            raise ValueError("Stock not found in TWSE or TPEx")

        print("Stock verified:", self.stock_name, self.stock_num)

    def check_tse(self) -> bool:
        tse_test_date = "20210104"
        url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={tse_test_date}&type=ALL"
        response = requests.post(url)
        df = pd.read_csv(
            StringIO(response.text.replace("=", "")),
            header=["證券代號" in line for line in response.text.split("\n")].index(True) - 1,
        )
        return self.match_stock(df, name_col="證券名稱", num_col="證券代號")

    def check_otc(self) -> bool:
        otc_test_date = "2021/01/04"
        url = f"https://www.tpex.org.tw/www/zh-tw/afterTrading/otc?date={otc_test_date}&type=EW&id=&response=csv&order=0&sort=asc"

        try:
            response = requests.post(url)
            response.encoding = "big5"

            df = (
                pd.read_csv(StringIO(response.text), header=3)
                .dropna(how="all", axis=1)
                .dropna(how="any")
            )

            df.columns = df.columns.str.strip()

            return self.match_stock(df, name_col="名稱", num_col="代號")

        except Exception as e:
            print(f"讀取上櫃股票資料失敗：{e}")
            return False

    def match_stock(self, df: pd.DataFrame, name_col: str, num_col: str) -> bool:
        if self.stock_name:
            match_by_name = df[df[name_col] == self.stock_name]
            if not match_by_name.empty:
                self.stock_num = match_by_name[num_col].values[0]
                return True

        if self.stock_num:
            match_by_num = df[df[num_col] == self.stock_num]
            if not match_by_num.empty:
                self.stock_name = match_by_num[name_col].values[0]
                return True

        return False

    def get_info(self) -> dict:
        return {
            "stock_name": self.stock_name,
            "stock_num": self.stock_num,
            "is_tse": self.is_tse,
            "is_otc": self.is_otc,
            "dates": self.dates,
        }
