import Stocks_Draw as SD
import requests
from io import StringIO
from datetime import date
from dateutil.rrule import rrule, DAILY
import pandas as pd


class Taiwan_Stocks(SD.Stocks_Draw):

    def __init__(self, **kwargs):

        
        # Get all the settings done 
        self.stock_name = ""
        self.stock_num = ""
        self.table_name = ""
        self.dates = []
        self.Stocks_settings()

        # Check whether it is a tpe or tsw stock
        self.Flag_tpe_stocks = False
        self.Flag_tsw_stocks = False
        self.Control_Check_stocks()
        
        super().__init__(**kwargs)

    def time_calculate(self, start_time, end_time):
        
        start_year = int( start_time[:4] )
        end_year = int( end_time[:4] )
        start_month = int( start_time[4:6] )
        end_month = int( end_time[4:6] )
        start_day = int( start_time[6:] )
        end_day = int( end_time[6:] )
        
        #時間抓取設定
        start_date = date(start_year, start_month, start_day)
        end_date = date(end_year, end_month, end_day)

        for dt in rrule(DAILY, dtstart=start_date, until=end_date):
            self.dates.append(dt.strftime("%Y%m%d"))

    
    def Stocks_settings(self):

        # 股票類型設定

        # print("----請輸入想要抓取的股票名稱或股票代碼，擇一即可----")
        # print("\n----Enter the stock name or the stock number----")
        print("\n  {}".format("(1) Enter the stock name or number"))
        print("----------------------------------------")


        # stock_name = input("請輸入股票名稱:")
        self.stock_name = input("\nEnter the stock name: ")

        if self.stock_name == '':
            # stock_num = input("請輸入股票代碼:")
            self.stock_num = input("Enter the stock number: ")
            if self.stock_num == '':
                # print("沒有輸入任何股票名稱或代碼!\n")
                assert self.stock_name != "" or self.stock_num != '' , "Please enter the stock name or number!!"


        # 時間抓取設定
        
        # print("""請輸入想要抓取的時間區間，輸入格式為\n20210102 -> 起始時間\n20210228 -> 結束時間""")
        # start_time = input("請輸入起始時間:")
        # end_time = input("請輸入結束時間:")
        # print("\n----Please enter the date interval----\nThe format is...\nstart time -> 20210102\nend time -> 20210228")
        print("\n  {}".format("(2) Please enter the date interval"))
        print("----------------------------------------")
        print("\n{:^39}".format("The Date Format"))
        print("########################################")
        print("#{:^38}#".format("start time -> 20210101"))
        print("#{:^38}#".format("End time   -> 20210228"))
        print("########################################")
        start_time = input("\nEnter the start time: ")
        end_time = input("Enter the end time:   ")


        # Get the date, format -> 20210104
        self.time_calculate(start_time, end_time)


    ##############################################
    
    def Check_stocks(self, df, check_name, check_num):

    
        if df[df[check_name]==self.stock_name].empty and df[df[check_num]==self.stock_num].empty:

            return False

        else:

            if self.stock_name != "" and self.stock_num != '':
                # assert df[df[check_name] == self.stock_name][check_num].values[0] == self.stock_num, "股票名稱與股票代號不符!! 請重新輸入!!"
                assert df[df[check_name] == self.stock_name][check_num].values[0] == self.stock_num, "The stock name is inconsistent with the stock number!! Please enter again!!"
                
            if not self.stock_name:
                self.stock_name = df[df[check_num] == self.stock_num][check_name].values[0]
            if not self.stock_num:
                self.stock_num = df[df[check_name] == self.stock_name][check_num].values[0]
            
            print("Pass checking... Starts analyzing stocks..")

            return True


    def Control_Check_stocks(self):


        print("\n  {}".format("(3) Starts checking"))
        print("----------------------------------------")
        print("\nChecking the stock name and number...")


        ##### 上市公司

        datestr = '20210104'
        r = requests.post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
        # 整理資料，變成表格
        df = pd.read_csv(StringIO(r.text.replace("=", "")), header=["證券代號" in l for l in r.text.split("\n")].index(True)-1)

        self.Flag_tsw_stocks = self.Check_stocks(df, check_name="證券名稱", check_num="證券代號")

        ##### 上櫃公司

        if not self.Flag_tsw_stocks:

            datestr = '110/01/04'
            r = requests.post('http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_download.php?l=zh-tw&d=' + datestr + '&s=0,asc,0')
            # 整理資料，變成表格
            df = pd.read_csv(StringIO(r.text), header=2).dropna(how='all', axis=1).dropna(how='any')
            self.Flag_tpe_stocks = self.Check_stocks(df, check_name="名稱", check_num="代號")
        
        # Set the table_name
        self.table_name = self.stock_name 
        
        # assert Flag_tpe_stocks or Flag_tsw_stocks, "非上市上櫃公司!"
        assert self.Flag_tpe_stocks or self.Flag_tsw_stocks, "Not Listed company!"
        

