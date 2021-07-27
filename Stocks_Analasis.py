import Stocks_Crawl as SC
import pandas as pd
import numpy as np



class Stocks_Analasis(SC.Stocks_Crawl):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.IT_num = []
        self.FI_num = []
        self.DL_num = []
        
        self.Cal_Investment_Trust()
        self.Cal_Foreign_Investor()
        self.Cal_Dealer()

        print( "\n  {}".format("(5) Analyzing the stocks") )
        print("----------------------------------------")
        
    
    # CALCULATING
    #############################################
    
    # 計算投信
    def Cal_Investment_Trust(self):

        # 把數字裡的逗點轉換掉
        df = self.df_institutional_investors["投信買賣超股數"].apply(lambda x: x.replace(',',''))

        self.IT_num = pd.to_numeric(df).values
                
        # 換成張數
        self.IT_num = self.IT_num / 1000

        # 取整數
        self.IT_num = np.ceil(self.IT_num)

        
    # 計算外資
    def Cal_Foreign_Investor(self):

        # 把數字裡的逗點轉換掉
        df = self.df_institutional_investors["外陸資買賣超股數(不含外資自營商)"].apply(lambda x: x.replace(',', ''))

        self.FI_num = pd.to_numeric(df).values

        # 換成張數
        self.FI_num = self.FI_num / 1000

        # 取整數
        self.FI_num = np.ceil(self.FI_num)


    # 計算自營商
    def Cal_Dealer(self):

        # 把數字裡的逗點轉換掉
        df = self.df_institutional_investors["自營商買賣超股數"].apply(lambda x: x.replace(',',''))

        self.DL_num = pd.to_numeric(df).values

        # 換成張數
        self.DL_num = self.DL_num / 1000

        # 取整數
        self.DL_num = np.ceil(self.DL_num)
    
    
    # ALGORITHM
    #############################################
    
    def Get_Close_Price(self, stock_day):
        
        """
        INPUT: 股票日期
        OUTPUT: 股票當天的收盤價
        
        """
        return self.df_stocks[self.df_stocks.Date==stock_day]["收盤價"]
        
    def Dependency(self, IT_flag = False, IT_stocks_number = 50, FI_flag = False, FI_stocks_number = 100, 
                         DL_flag = False, DL_stocks_number = 10, date_interval = 3, value_date_interval = 2):

        print("Dependency:")
        print("This feature is currently not available !!")
  
    
    def Stand_Up_On_MAs(self):
        
        print("\n{}".format("Stand_Up_On_MAs (針對你Fetch data區間的最後一天做分析):"))

        # 抓出所需data
        stock_price = self.df_stocks['收盤價'].astype(float).iloc[-1]
        MA5 = self.MA5.iloc[-1] if not self.MA5.isnull().values.all() else 0
        MA10 = self.MA10.iloc[-1] if not self.MA10.isnull().values.all() else 0
        MA20 = self.MA20.iloc[-1] if not self.MA20.isnull().values.all() else 0
        MA60 = self.MA60.iloc[-1] if not self.MA60.isnull().values.all() else 0

        four_MAs = MA5 and MA10 and MA20 and MA60
        three_MAs = MA5 and MA10 and MA20
        
        four_flag = True if four_MAs and max(stock_price, MA5, MA10, MA20, MA60) == stock_price else False
        three_flag = True if three_MAs and max(stock_price, MA5, MA10, MA20) == stock_price else False

        # 判斷data值
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

    # UTILITIES
    #############################################
    
    def save_csv(self, save_path, filename, stocks = False, institutional_investors = False):
        
        if stocks:
            self.df_stocks.to_csv(save_path+filename)
        if institutional_investors:
            self.df_institutional_investors.to_csv(save_path+filename)