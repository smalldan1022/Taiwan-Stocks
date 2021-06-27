import MySQL_Database as MD
import requests
from io import StringIO
import pandas as pd
import time


class Stocks_Crawl(MD.MySQL_Database):
    
    def __init__(self, timesleep=5, Crawl_flag = True, MySQL_flag = True, 
                 Fetch_stock_statistics_flag = True, **kwargs):
        
        super().__init__(**kwargs)      

        self.Crawl_flag = Crawl_flag
        self.MySQL_flag = MySQL_flag
        self.Fetch_stock_statistics_flag = Fetch_stock_statistics_flag

        ################# 上櫃公司價格資料
        self.url_tpex_stock = "http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_download.php?l=zh-tw&d="
        # self.tpex_df_stocks = pd.DataFrame( data = [], 
        #                                     columns = ['Date', '證券代號', '證券名稱', 
        #                                                '成交股數', '成交筆數', 
        #                                                '成交金額', '開盤價', 
        #                                                '最高價', '最低價', 
        #                                                '收盤價', '漲跌(+/-)', 
        #                                                '漲跌價差' ])

        ################# 上櫃公司法人買賣資料
        self.url_tpex_df_institutional_investors = "https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?l=zh-tw&o=csv&se=EW&t=D&d="
        # self.tpex_df_institutional_investors = pd.DataFrame( data = [], 
        #                                                      columns = ['證券代號', '證券名稱', 
        #                                                                 '外陸資買進股數(不含外資自營商)', 
        #                                                                 '外陸資賣出股數(不含外資自營商)',
        #                                                                 '外陸資買賣超股數(不含外資自營商)', '外資自營商買進股數', 
        #                                                                 '外資自營商賣出股數', '外資自營商買賣超股數', 
        #                                                                 '投信買進股數','投信賣出股數', 
        #                                                                 '投信買賣超股數', '自營商買賣超股數', 
        #                                                                 '自營商買進股數(自行買賣)', '自營商賣出股數(自行買賣)',
        #                                                                 '自營商買賣超股數(自行買賣)', '自營商買進股數(避險)',
        #                                                                 '自營商賣出股數(避險)', '自營商買賣超股數(避險)',
        #                                                                 '三大法人買賣超股數' ])

        ################# 上市公司價格資料
        
        self.url_stock = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date='
        self.df_stocks = pd.DataFrame(data = [],
                                      columns = ['Date', '證券代號', '證券名稱', 
                                                 '成交股數', '成交筆數', 
                                                 '成交金額', '開盤價', 
                                                 '最高價', '最低價', 
                                                 '收盤價', '漲跌(+/-)', 
                                                 '漲跌價差' ])
        
        ################# 上市公司法人買賣資料
        
        self.url_institutional_investors = 'http://www.tse.com.tw/fund/T86?response=csv&date='
        self.df_institutional_investors = pd.DataFrame( data = [], 
                                                        columns = ['證券代號', '證券名稱', 
                                                                    '外陸資買進股數(不含外資自營商)', 
                                                                    '外陸資賣出股數(不含外資自營商)',
                                                                    '外陸資買賣超股數(不含外資自營商)', '外資自營商買進股數', 
                                                                    '外資自營商賣出股數', '外資自營商買賣超股數', 
                                                                    '投信買進股數','投信賣出股數', 
                                                                    '投信買賣超股數', '自營商買賣超股數', 
                                                                    '自營商買進股數(自行買賣)', '自營商賣出股數(自行買賣)',
                                                                    '自營商買賣超股數(自行買賣)', '自營商買進股數(避險)',
                                                                    '自營商賣出股數(避險)', '自營商買賣超股數(避險)',
                                                                    '三大法人買賣超股數'])

        ################# 上市櫃公司股票本益比, 股價淨值比, 殖利率, 股利年度

        self.df_statistics = pd.DataFrame( data = [], 
                                           columns = ["證券代號", "證券名稱", "本益比", "股價淨值比", "殖利率", "股利年度"])

        
        self.timesleep = timesleep
        
        if self.Crawl_flag:
            self.Crawl()
        elif self.Fetch_stock_statistics_flag:
            self.Fetch_stock_statistics()
        else:
            print("The program is useless...END")

        # 爬蟲完要不要存進MySQL資料庫
        if self.MySQL_flag:

            # 存進去Database
            self.SaveIntoDatabase()

            # 爬蟲完，也如果有將資料存進MySQL，將資料庫關起來
            self.Close()
            
    

    # Change the date
    #############################################

    def date_changer(self, date):

        year = date[:4]
        year = str(int(year)-1911)
        month = date[4:6]
        day = date[6:]

        return year+"/"+month+"/"+day

    # CRAWLING
    #############################################
        
    def Crawl(self):
        
        # Start crawling data
        for date in self.dates:

            print(date + " starts crawling")

            try:

                ################ 爬上櫃公司 ################
                
                if self.Flag_tpe_stocks:
                    
                    ROC_era_date = self.date_changer(date)

                    # 股價資訊
                    self.Crawl_method(url = self.url_tpex_stock, 
                                            date = ROC_era_date, 
                                            Date = date, 
                                            url_suffix='&s=0,asc,0', 
                                            Flag_tpex_stocks=True,
                                            Flag_tpex_insti_inv=False,
                                            Flag_stocks=False, 
                                            Flag_insti_inv=False)
                                            
                    # 三大法人資訊
                    self.Crawl_method(url = self.url_tpex_df_institutional_investors, 
                                            date = ROC_era_date, 
                                            Date = date, 
                                            url_suffix='&s=0,asc', 
                                            Flag_tpex_stocks=False,
                                            Flag_tpex_insti_inv=True,
                                            Flag_stocks=False, 
                                            Flag_insti_inv=False)

                    # 本益比, 股價淨值比, 殖利率(%), 股利年度

                    self.Crawl_PB_and_PE(ROC_era_date)

                ################ 爬上市公司 ################
                
                if self.Flag_tsw_stocks:

                    # 股價資訊
                    self.Crawl_method(url = self.url_stock, 
                                            date = date, 
                                            Date = date, 
                                            url_suffix='&type=ALL', 
                                            Flag_tpex_stocks=False,
                                            Flag_tpex_insti_inv=False,
                                            Flag_stocks=True, 
                                            Flag_insti_inv=False)
                                            
                    #爬上市公司三大法人資訊
                    self.Crawl_method(url = self.url_institutional_investors, 
                                            date = date, 
                                            Date = date, 
                                            url_suffix='&selectType=ALLBUT0999', 
                                            Flag_tpex_stocks=False,
                                            Flag_tpex_insti_inv=False,
                                            Flag_stocks=False, 
                                            Flag_insti_inv=True)

                    # 本益比, 股價淨值比, 殖利率(%), 股利年度

                    self.Crawl_PB_and_PE(date)

            except Exception as err:
                
                if type(err) == ValueError:
                    # print(err)
                    print(date +" is holiday")

                elif type(err) == KeyError:
                    # print(err)
                    print(date +" is holiday")
                else:
                    
                    print("Error happens!! -> " + str(err))
                    break

                                        
            time.sleep(self.timesleep)

        # 把所有資料concatenate起來

        self.ConcatData()
        

 
    # 抓取特定股票(使用者要抓的那支股票)
    #############################################

    def Get_specific_stock(self, df):

        if self.stock_name != '':
            
            df = df[df["證券名稱"].apply(lambda x:x.replace(" ", "") ) == self.stock_name]

        elif self.stock_num != '':

            df["證券代號"] = df["證券代號"].apply(lambda x:x.replace("=", "").replace('"', '').replace(" ", ""))
            df = df[df['證券代號'] == self.stock_num]

        return df
    
    # 重新命名col name, 確保一致
    #############################################

    def Rename_df_columns(self, df, Flag_tpex_stocks = False, Flag_tpex_insti_inv = False):

        tpex_stocks_rename_columns = {  "代號":"證券代號",
                                        "名稱":"證券名稱",
                                        "收盤 ":"收盤價",
                                        "漲跌":"漲跌價差",
                                        "開盤 ":"開盤價", 
                                        "最高 ":"最高價",
                                        "最低":"最低價",
                                        "成交股數  ":"成交股數",
                                        "成交金額(元)":"成交金額",
                                        "成交筆數 ":"成交筆數"}

        tpex_insti_inv_rename_columns = {   "代號":"證券代號", 
                                            "名稱":"證券名稱", 
                                            "外資及陸資(不含外資自營商)-買進股數":"外陸資買進股數(不含外資自營商)", 
                                            "外資及陸資(不含外資自營商)-賣出股數":"外陸資賣出股數(不含外資自營商)", 
                                            "外資及陸資(不含外資自營商)-買賣超股數":"外陸資買賣超股數(不含外資自營商)", 
                                            "外資自營商-買進股數":"外資自營商買進股數", 
                                            "外資自營商-賣出股數":"外資自營商賣出股數", 
                                            "外資自營商-買賣超股數":"外資自營商買賣超股數",
                                            "投信-買進股數":"投信買進股數",
                                            "投信-賣出股數":"投信賣出股數",
                                            "投信-買賣超股數":"投信買賣超股數",
                                            "自營商(自行買賣)-買進股數":"自營商買進股數(自行買賣)",
                                            "自營商(自行買賣)-賣出股數":"自營商賣出股數(自行買賣)",
                                            "自營商(自行買賣)-買賣超股數":"自營商買賣超股數(自行買賣)",
                                            "自營商(避險)-買進股數":"自營商買進股數(避險)",
                                            "自營商(避險)-賣出股數":"自營商賣出股數(避險)",
                                            "自營商(避險)-買賣超股數":"自營商買賣超股數(避險)",
                                            "自營商-買賣超股數":"自營商買賣超股數",
                                            "三大法人買賣超股數合計":"三大法人買賣超股數" }

        if Flag_tpex_stocks:  
            df.rename(columns=tpex_stocks_rename_columns, inplace = True)
        elif Flag_tpex_insti_inv:
            df.rename(columns=tpex_insti_inv_rename_columns, inplace = True)
        else:
            print("Error!!")

        return df

    # 開始爬蟲
    #############################################

    def Crawl_method(self, url, date, Date, url_suffix='', Flag_tpex_stocks=False, Flag_tpex_insti_inv=False,
                     Flag_stocks=False, Flag_insti_inv=False):
        
        # 下載股價
        r = requests.post( url + date + url_suffix)

        # 整理資料，變成表格
        
        if not Flag_tpex_stocks and not Flag_tpex_insti_inv and not Flag_stocks and not Flag_insti_inv:
            
            print("Error...Crawling nothing, please set the flags right")
            return 0


        ######### 爬上櫃公司 #########

        if Flag_tpex_stocks:
            
            df = pd.read_csv(StringIO(r.text), header=2).dropna(how='all', axis=1).dropna(how='any')

            df = df.iloc[:, :11]

            df = self.Rename_df_columns(df, Flag_tpex_stocks = True, Flag_tpex_insti_inv = False)

            df = self.Get_specific_stock(df)

            df.insert(0, "Date", Date)

            df.drop("均價 ", axis = "columns", inplace = True)
            
            df["漲跌(+/-)"] = df["漲跌價差"].values[0][0] if df["漲跌價差"].values[0][0] != "0" else "X"

            self.df_stocks = self.df_stocks.append(df, ignore_index=True)

        
        if Flag_tpex_insti_inv:

            df = pd.read_csv(StringIO(r.text.replace("=", "")), header = 1 ).dropna(how='all', axis=1).dropna(how='any')

            df.insert(0, "Date", Date)
            
            df.drop(columns=[ "自營商-買進股數", 
                              "自營商-賣出股數",
                              "外資及陸資-買進股數",
                              "外資及陸資-賣出股數",
                              "外資及陸資-買賣超股數"], inplace = True)

            df = self.Rename_df_columns(df, Flag_tpex_stocks = False, Flag_tpex_insti_inv = True)

            df = self.Get_specific_stock(df)
            
            self.df_institutional_investors = self.df_institutional_investors.append(df, ignore_index = True)


        ######### 爬上市公司 #########

        if Flag_stocks:

            df = pd.read_csv(StringIO(r.text.replace("=", "")), 
                             header = ["證券代號" in l for l in r.text.split("\n")].index(True)-1 )

            df.insert(0, "Date", date)

            df = df.iloc[:, :12]

            df = self.Get_specific_stock(df)

            self.df_stocks = self.df_stocks.append(df, ignore_index=True)

        
        if Flag_insti_inv:

            df = pd.read_csv(StringIO(r.text.replace("=", "")),
                             header = 1 ).dropna(how='all', axis=1).dropna(how='any')

            df.insert(0, "Date", date)

            df = self.Get_specific_stock(df)
            
            self.df_institutional_investors = self.df_institutional_investors.append(df, ignore_index = True)


    # 合併Date
    #############################################

    def ConcatData(self):

        # 將index reset 以免concat出現NaN值
        self.df_stocks.reset_index(drop=True, inplace=True)
        self.df_institutional_investors.reset_index(drop=True, inplace=True)
        self.df_statistics.reset_index(drop=True, inplace=True)

        self.df_stocks = pd.concat([self.df_stocks, self.df_institutional_investors.drop(columns=["Date", "證券代號", "證券名稱"]), 
                        self.df_statistics.drop(columns=["證券代號", "證券名稱"])], axis = 1)


    # 將Date存進資料庫
    #############################################

    def SaveIntoDatabase(self):


        # creating column list for insertion
        cols = "`,`".join([str(i) for i in self.df_stocks.columns.tolist()])

        # Insert DataFrame recrds one by one.
        for i, row in self.df_stocks.iterrows():

            try:
                sql = "INSERT INTO `{}` (`".format(self.table_name) +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
                
                self.cursor.execute(sql, tuple(row))

                # the connection is not autocommitted by default, so we must commit to save our changes
                self.db.commit()
                
            except Exception as err:
                
                # print(err)
                print("This data already exists in this table, jumping...")
                continue
    

    # 抓取PB, PE
    #############################################

    def Crawl_PB_and_PE(self, date):

        """
        This function is for crwaling the PB, PE and Dividend yield statistics.
        """


        # 上櫃公司

        if self.Flag_tpe_stocks:
            
            url = "https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_download.php?l=zh-tw&d="+date+"&s=0,asc,0"

            r = requests.get(url)

            r = r.text.split("\n")

            df = pd.read_csv(StringIO("\n".join(r[3:-1]))).fillna(0)

            columns_title = ["股票代號", "名稱", "本益比", "股價淨值比", "殖利率(%)", "股利年度" ]

            df = df[columns_title]

            df.rename(columns = {"殖利率(%)":"殖利率", "股票代號":"證券代號", "名稱":"證券名稱"}, inplace = True)

            df = self.Get_specific_stock(df)

            self.df_statistics = self.df_statistics.append(df, ignore_index=True)


        # 上市公司

        if self.Flag_tsw_stocks:

            url = "https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date="+date+"&selectType=ALL"

            r = requests.get(url)

            r = r.text.split("\r\n")[:-13]

            df = pd.read_csv(StringIO("\n".join(r)), header=1).dropna(how="all", axis=1).apply(lambda x:x.replace("-", 0))

            columns_title = ["證券代號", "證券名稱", "本益比", "股價淨值比", "殖利率(%)", "股利年度" ]

            df = df[columns_title]

            df.rename(columns = {"殖利率(%)":"殖利率"}, inplace = True)

            df = self.Get_specific_stock(df)

            self.df_statistics = self.df_statistics.append(df, ignore_index=True)

        