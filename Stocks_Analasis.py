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

        print( "\n  {}".format("(5) Calculating the SPRR") )
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
        
        print("目前不開放此功能，如有需要歡迎來信")
        
        
    def Cal_dependency(self, buying_number, stocks_number, date_interval=3, value_date_interval = 2):

        print("目前不開放此功能，如有需要歡迎來信")
    
    
    # UTILITIES
    #############################################
    
    def save_csv(self, save_path, filename, stocks = False, institutional_investors = False):
        
        if stocks:
            self.df_stocks.to_csv(save_path+filename)
        if institutional_investors:
            self.df_institutional_investors.to_csv(save_path+filename)
