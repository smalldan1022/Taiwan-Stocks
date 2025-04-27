import numpy as np
import pandas as pd


class Analyzer:
    def __init__(self, df_stocks: pd.DataFrame) -> None:
        self.inv_num = []
        self.foreign_num = []
        self.dealer_num = []
        self.df_stocks = df_stocks
        self._ma5 = self.df_stocks["收盤價"].rolling(5).mean()
        self._ma10 = self.df_stocks["收盤價"].rolling(10).mean()
        self._ma20 = self.df_stocks["收盤價"].rolling(20).mean()
        self._ma60 = self.df_stocks["收盤價"].rolling(60).mean()
        self.cal_investment_trust()
        self.cal_foreign_investor()
        self.cal_dealer()

    @property
    def MA5(self) -> pd.Series:
        return self._ma5

    @property
    def MA10(self) -> pd.Series:
        return self._ma10

    @property
    def MA20(self) -> pd.Series:
        return self._ma20

    @property
    def MA60(self) -> pd.Series:
        return self._ma60

    def cal_investment_trust(self) -> None:
        df = self.df_stocks["投信買賣超股數"].apply(lambda x: x.replace(",", ""))
        self.inv_num = pd.to_numeric(df).values
        self.inv_num = self.inv_num / 1000
        self.inv_num = np.ceil(self.inv_num)

    def cal_foreign_investor(self) -> None:
        df = self.df_stocks["外陸資買賣超股數(不含外資自營商)"].apply(lambda x: x.replace(",", ""))
        self.foreign_num = pd.to_numeric(df).values
        self.foreign_num = self.foreign_num / 1000
        self.foreign_num = np.ceil(self.foreign_num)

    def cal_dealer(self) -> None:
        df = self.df_stocks["自營商買賣超股數"].apply(lambda x: x.replace(",", ""))
        self.dealer_num = pd.to_numeric(df).values
        self.dealer_num = self.dealer_num / 1000
        self.dealer_num = np.ceil(self.dealer_num)

    def get_close_price(self, stock_day: str) -> None:
        return self.df_stocks[self.df_stocks.Date == stock_day]["收盤價"]

    def dependency(self) -> None:
        print("dependency:")
        print("This feature is currently not available !!")

    def stand_up_on_MAs(self) -> None:
        print("\nStand_up_on_MAs (針對你Fetch data區間的最後一天做分析):")
        stock_price = self.df_stocks["收盤價"].astype(float).iloc[-1]
        MA5 = self.MA5.iloc[-1] if not self.MA5.isnull().values.all() else 0
        MA10 = self.MA10.iloc[-1] if not self.MA10.isnull().values.all() else 0
        MA20 = self.MA20.iloc[-1] if not self.MA20.isnull().values.all() else 0
        MA60 = self.MA60.iloc[-1] if not self.MA60.isnull().values.all() else 0

        three_MAs = MA5 and MA10 and MA20
        four_MAs = MA5 and MA10 and MA20 and MA60

        three_flag = (
            True if three_MAs and max(stock_price, MA5, MA10, MA20) == stock_price else False
        )
        four_flag = (
            True if four_MAs and max(stock_price, MA5, MA10, MA20, MA60) == stock_price else False
        )

        if four_flag:
            print("股價已站上5日、10日、20日、60日均線均線，為四海遊龍型股票!!")
        elif three_flag:
            print("股價已站上5日、10日、20日均線，為三陽開泰型股票!!")
        elif not four_MAs:
            print("目前的data數量不足以畫出四條均線，請補足後再用此演算法!!")
        elif not three_MAs:
            print("目前的data數量不足以畫出三條均線，請補足後再用此演算法!!")
        else:
            print("目前股價尚未成三陽開泰型、四海遊龍型股票!!")

    def save_csv(self, save_path, filename, stocks=False, institutional_investors=False) -> None:
        if stocks:
            self.df_stocks.to_csv(save_path + filename)
        if institutional_investors:
            self.df_stocks.to_csv(save_path + filename)
