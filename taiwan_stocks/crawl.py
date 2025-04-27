import time
from abc import ABC, abstractmethod
from io import StringIO

import pandas as pd
import requests

from taiwan_stocks.stock_info import (
    NUMERICAL_COLUMNS,
    OTC_INSTI_INV_RENAME_COLUMNS,
    OTC_INSTITUTIONAL_INVESTORS_URL,
    OTC_PB_PE_URL,
    OTC_STOCKS_RENAME_COLUMNS,
    OTC_URL,
    TSE_INSTITUTIONAL_INVESTORS_URL,
    TSE_PB_PE_URL,
    TSE_URL,
)


class Builder(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.df_all_stocks_info = pd.DataFrame()
        self.df_stocks = pd.DataFrame()
        self.df_institutional_investors = pd.DataFrame()
        self.df_statistics = pd.DataFrame()
        self.numerical_columns = NUMERICAL_COLUMNS

    @property
    @abstractmethod
    def product(self) -> None:
        pass

    @abstractmethod
    def produce_minimal_viable_crawl(self) -> None:
        pass

    @abstractmethod
    def produce_full_featured_crawl(self) -> None:
        pass

    @abstractmethod
    def crawl_PB_PE(self) -> None:
        pass


class TPECrawler(Builder):
    def __init__(self, stock_name: str, stock_num: str, dates: list):
        super().__init__()
        self.tse_url = TSE_URL
        self.tse_insti_inv_url = TSE_INSTITUTIONAL_INVESTORS_URL
        self.tse_PB_PE_url = TSE_PB_PE_URL

        self.stock_name = stock_name
        self.stock_num = stock_num

        self.dates = dates
        self.timesleep = 1

        self.reset()

    def reset(self) -> None:
        self._product = StockProduct()

    @property
    def product(self) -> "StockProduct":
        product = self._product
        self.reset()
        return product

    def produce_minimal_viable_crawl(self) -> None:
        for date in self.dates:
            print(date + " starts crawling")
            try:
                self.crawl_stocks_info(date=date)

            except Exception as err:
                if type(err) == ValueError:
                    print(date + " is holiday")
                elif type(err) == KeyError:
                    print(date + " is holiday")
                else:
                    raise Exception("Error happens!! -> " + str(err))  # noqa: B904
            time.sleep(self.timesleep)

        self._product.data = self.df_stocks

    def produce_full_featured_crawl(self) -> None:
        for date in self.dates:
            print(date + " starts crawling")
            try:
                self.crawl_stocks_info(date=date)
                self.crawl_insti_inv(date=date)
                self.crawl_PB_PE(date=date)

            except Exception as err:
                if type(err) == ValueError:
                    print(date + " is holiday")
                elif type(err) == KeyError:
                    print(date + " is holiday")
                else:
                    raise Exception("Error happens!! -> " + str(err))  # noqa: B904

            time.sleep(self.timesleep)
        self.transform_stock_data()
        self._product.data = self.df_all_stocks_info

    def get_stock(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.stock_name:
            return df[df["證券名稱"].str.replace(" ", "") == self.stock_name]
        if self.stock_num:
            return df[
                df["證券代號"].str.replace("=", "").str.replace('"', "").str.replace(" ", "")
                == self.stock_num
            ]
        return df

    def assign_column_first(self, df: pd.DataFrame, col_name: str, value: str) -> pd.DataFrame:
        return df.assign(**{col_name: value}).loc[
            :, [col_name] + [col for col in df.columns if col != col_name]
        ]

    def crawl_stocks_info(self, date: str) -> None:
        response = requests.post(self.tse_url % date)
        df = (
            pd.read_csv(
                StringIO(response.text.replace("=", "")),
                header=["證券代號" in line for line in response.text.split("\n")].index(True) - 1,
            )
            .dropna(subset=["證券名稱"], axis=0, how="any")
            .pipe(self.assign_column_first, col_name="Date", value=date)
            .iloc[:, :12]
        )
        df = self.get_stock(df)
        self.df_stocks = (
            pd.concat([self.df_stocks, df], ignore_index=True) if not self.df_stocks.empty else df
        )

    def crawl_insti_inv(self, date: str) -> None:
        response = requests.post(self.tse_insti_inv_url % date)
        df = (
            pd.read_csv(StringIO(response.text.replace("=", "")), header=1)
            .dropna(how="all", axis=1)
            .dropna(how="any")
            .pipe(self.get_stock)
            .pipe(self.assign_column_first, col_name="Date", value=date)
        )
        self.df_institutional_investors = (
            pd.concat([self.df_institutional_investors, df], ignore_index=True)
            if not self.df_institutional_investors.empty
            else df
        )

    def crawl_PB_PE(self, date: str) -> None:
        response = requests.get(self.tse_PB_PE_url % date)
        response = response.text.split("\r\n")[:-13]

        df = (
            pd.read_csv(StringIO("\n".join(response)), header=1)
            .dropna(how="all", axis=1)
            .pipe(self.get_stock)
        )
        self.df_statistics = (
            pd.concat([self.df_statistics, df], ignore_index=True)
            if not self.df_statistics.empty
            else df
        )

    def transform_stock_data(self) -> None:
        self.df_stocks.reset_index(drop=True, inplace=True)
        self.df_institutional_investors.reset_index(drop=True, inplace=True)
        self.df_statistics.reset_index(drop=True, inplace=True)
        if (
            self.df_stocks.empty
            and self.df_institutional_investors.empty
            and self.df_statistics.empty
        ):
            return

        self.df_all_stocks_info = pd.concat(
            [
                self.df_stocks,
                self.df_institutional_investors.drop(columns=["Date", "證券代號", "證券名稱"]),
                self.df_statistics.drop(columns=["證券代號", "證券名稱", "收盤價"]),
            ],
            axis=1,
        )
        for num_col in self.numerical_columns:
            self.df_all_stocks_info[num_col] = pd.to_numeric(
                self.df_all_stocks_info[num_col].str.replace(",", "")
            )


class OTCCrawler(Builder):
    def __init__(self, stock_name: str, stock_num: str, dates: list):
        super().__init__()
        self.otc_url = OTC_URL
        self.otc_insti_inv_url = OTC_INSTITUTIONAL_INVESTORS_URL
        self.otc_PB_PE_url = OTC_PB_PE_URL

        self.otc_insti_inv_rename_cols = OTC_INSTI_INV_RENAME_COLUMNS
        self.otc_stocks_rename_cols = OTC_STOCKS_RENAME_COLUMNS

        self.stock_name = stock_name
        self.stock_num = stock_num

        self.dates = dates
        self.timesleep = 1

        self.reset()

    def reset(self) -> None:
        self._product = StockProduct()

    @property
    def product(self) -> "StockProduct":
        product = self._product
        self.reset()
        return product

    def produce_minimal_viable_crawl(self) -> None:
        for date in self.dates:
            print(date + " starts crawling")
            date = self.date_convert(date)
            try:
                self.crawl_stocks_info(date=date)

            except Exception as err:
                if type(err) == ValueError:
                    print(date + " is holiday")
                elif type(err) == KeyError:
                    print(date + " is holiday")
                else:
                    raise Exception("Error happens!! -> " + str(err))  # noqa: B904
            time.sleep(self.timesleep)

        self._product.data = self.df_stocks

    def produce_full_featured_crawl(self) -> None:
        for date in self.dates:
            print(date + " starts crawling")
            date = self.date_convert(date)
            try:
                self.crawl_stocks_info(date=date)
                self.crawl_insti_inv(date=date)
                self.crawl_PB_PE(date=date)

            except Exception as err:
                if type(err) == ValueError:
                    print(date.replace("/", "") + " is holiday")
                elif type(err) == KeyError:
                    print(date.replace("/", "") + " is holiday")
                else:
                    raise Exception("Error happens!! -> " + str(err))  # noqa: B904

            time.sleep(self.timesleep)
        self.transform_stock_data()
        self._product.data = self.df_all_stocks_info

    def get_stock(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.stock_name:
            return df[df["證券名稱"].str.replace(" ", "") == self.stock_name]

        if self.stock_num:
            return df[
                df["證券代號"].str.replace("=", "").str.replace('"', "").str.replace(" ", "")
                == self.stock_num
            ]

        return df

    def assign_column_first(self, df: pd.DataFrame, col_name: str, value: str) -> pd.DataFrame:
        return df.assign(**{col_name: value}).loc[
            :, [col_name] + [col for col in df.columns if col != col_name]
        ]

    def crawl_stocks_info(self, date: str) -> None:
        response = requests.post(self.otc_url % date)
        df = (
            pd.read_csv(StringIO(response.text), header=3, encoding="big5")
            .dropna(how="all", axis=1)
            .dropna(how="any")
            .pipe(self.assign_column_first, col_name="Date", value=date)
            .pipe(self.rename_stock_columns, rename_cols=self.otc_stocks_rename_cols)
            .pipe(self.get_stock)
            .iloc[:, :11]
        )
        df["漲跌(+/-)"] = df["漲跌價差"].values[0][0] if df["漲跌價差"].values[0][0] != "0" else "X"
        self.df_stocks = (
            pd.concat([self.df_stocks, df], ignore_index=True) if not self.df_stocks.empty else df
        )

    def crawl_insti_inv(self, date: str) -> None:
        response = requests.post(self.otc_insti_inv_url % date)
        df = (
            pd.read_csv(StringIO(response.text), header=1)
            .dropna(how="all", axis=1)
            .dropna(how="any")
            .pipe(self.assign_column_first, col_name="Date", value=date)
            .pipe(self.rename_stock_columns, rename_cols=self.otc_insti_inv_rename_cols)
            .pipe(self.get_stock)
            .drop(
                columns=[
                    "自營商-買進股數",
                    "自營商-賣出股數",
                    "外資及陸資-買進股數",
                    "外資及陸資-賣出股數",
                    "外資及陸資-買賣超股數",
                ],
            )
        )
        self.df_institutional_investors = (
            pd.concat([self.df_institutional_investors, df], ignore_index=True)
            if not self.df_institutional_investors.empty
            else df
        )

    def crawl_PB_PE(self, date: str) -> None:
        # mingua
        mingua_date = f"{int(date[:4])-1911}/{date[5:7]}/{date[8:]}"
        response = requests.post(self.otc_PB_PE_url % (date, self.stock_num))
        filtered_text = "\n".join(response.text.splitlines()[:-12])
        df = (
            pd.read_csv(StringIO(filtered_text), header=4)
            .fillna(0)
            .loc[lambda df: df["日期"] == mingua_date]
            .pipe(self.assign_column_first, col_name="證券名稱", value=self.stock_name)
            .pipe(self.assign_column_first, col_name="證券代號", value=self.stock_num)
            .drop(columns=["日期"])
        )
        self.df_statistics = (
            pd.concat([self.df_statistics, df], ignore_index=True)
            if not self.df_statistics.empty
            else df
        )

    def transform_stock_data(self) -> None:
        self.df_stocks.reset_index(drop=True, inplace=True)
        self.df_institutional_investors.reset_index(drop=True, inplace=True)
        self.df_statistics.reset_index(drop=True, inplace=True)
        if (
            self.df_stocks.empty
            and self.df_institutional_investors.empty
            and self.df_statistics.empty
        ):
            return

        self.df_all_stocks_info = pd.concat(
            [
                self.df_stocks,
                self.df_institutional_investors.drop(columns=["Date", "證券代號", "證券名稱"]),
                self.df_statistics.drop(columns=["證券代號", "證券名稱"]),
            ],
            axis=1,
        )
        for num_col in self.numerical_columns:
            self.df_all_stocks_info[num_col] = pd.to_numeric(
                self.df_all_stocks_info[num_col].str.replace(",", "")
            )

    def rename_stock_columns(self, df: pd.DataFrame, rename_cols: dict) -> pd.DataFrame:
        return df.rename(columns=rename_cols)

    def date_convert(self, date: str) -> str:
        return f"{date[:4]}/{date[4:6]}/{date[6:]}"


class StockProduct:
    def __init__(self) -> None:
        self.tradesketcher = None
        self.analyzer = None
        self._df = None

    @property
    def data(self) -> None:
        return self._df

    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        self._df = data


class CrawlerDirector:
    def __init__(self):
        self._builder = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:
        self._builder = builder

    def build_minimal_viable_product(self) -> None:
        self.builder.produce_minimal_viable_crawl()

    def build_full_featured_product(self) -> None:
        self.builder.produce_full_featured_crawl()
