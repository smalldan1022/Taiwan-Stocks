import pandas as pd
import traceback
import pymysql




class MySQL_Database:
    
    def __init__(self, db_settings, **kwargs):
        
        # Initialization

        self.db_settings = db_settings
        
        self.table_sql = """CREATE TABLE `{}` (
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
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""".format(self.table_name)
        self.db = None
        self.cursor = None

        print( "\n  {}".format("(4) Manipulating the data") )
        print("----------------------------------------\n")

        if self.db_settings != None:

            # Create db and cursor
            self.Connect()
            self.Cursor()
            
            # Create a table
            if self.Check():
                self.Create_table()


    def Connect(self):
        
        try:
            # 建立Connection物件
            self.db = pymysql.connect(**self.db_settings)
            print("MySQL Connected...")
        except Exception as err:
            print("Error:")
            print(err)
            
    def Cursor(self):
        
        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor()
    
    def Create_table(self):
        
        self.cursor.execute(self.table_sql)
        print("MySQL table created Successfully...")
        
        
    def Check(self):
        
        # Drop table if it already exist using execute() method.

        check_table_sql = "SHOW TABLES"

        self.cursor.execute(check_table_sql)
        results = self.cursor.fetchall()
        results_list = [item[0] for item in results]

        if self.table_name in results_list:
            print("This table already exists...")
            return False
        else:
            print("This table does not exist, creating table...")
            return True
    
    def Insert(self, insert_sql):
        
        try:
            self.cursor.execute(insert_sql)
            self.db.commit()
            print("Insert successfully.")

        except:
            self.db.rollback()
            traceback.print_exc()
            
    def Delete(self, delete_sql):
        
        try:
            # Execute the SQL command
            self.cursor.execute(delete_sql)
            # Commit your changes in the database
            self.db.commit()
            print("Delete successfully.")
            
        except:
            self.db.rollback()
            traceback.print_exc()

    
    def Fetch(self, fetch_sql):

        # 使用者有可能原本用完後關掉db connect，然後再次使用Fetch功能，因此要先連結
        self.Connect()
        self.Cursor()
        
        try:
            # Execute the SQL command
            self.cursor.execute(fetch_sql)
            # Fetch all the rows in a list of lists.
            results = self.cursor.fetchall()

            for row in results:
                fname = row[1]
                lname = row[2]
                age = row[3]
                sex = row[4]
                income = row[5]
                # Now print fetched result
                print("name = {} {}, age = {}, sex = {}, income = {}".format(fname, lname, age, sex, income ))
        except:
            traceback.print_exc()

    def Fetch_stock_statistics(self):

        print("Fetching stocks statistics...")
        # 使用者有可能原本用完後關掉db connect，然後再次使用Fetch功能，因此要先連結
        self.Connect()
        self.Cursor()

        #使用connect指定的Mysql獲取資料
        self.df_stocks = pd.read_sql('SELECT * FROM stocks.{}'.format(self.table_name), con = self.db)
        self.df_institutional_investors = pd.read_sql('SELECT * FROM stocks.{}'.format(self.table_name), con = self.db)

        # 先把Date的部分轉回str，不然後面畫圖會出錯
        self.df_stocks["Date"] = self.df_stocks["Date"].apply(lambda x: str(x))
        self.df_institutional_investors["Date"] = self.df_institutional_investors["Date"].apply(lambda x:str(x))

        # 要篩選出日期區間內的data
        assert not self.df_stocks.Date.empty, "This stock's data doesn't exist in this database!"
        assert int(self.dates[-1]) >= int(self.df_stocks.Date.min()) and int(self.dates[0]) <= int(self.df_stocks.Date.max()), "This stock's data doesn't exist in this database!!"

        if int(self.dates[0]) <= int(self.df_stocks.Date.min()) or int(self.dates[-1]) >= int(self.df_stocks.Date.max()):
            
            print("Fetching the maximum data...")

            Min_date = max(self.df_stocks.Date.min(), self.dates[0])
            Max_date = min(self.df_stocks.Date.max(), self.dates[-1])

            print("The maximum data in MySQL: {} - {}".format( Min_date, Max_date ))
            print("Fetching the data...")

            # print("資料庫資料不足，只取用最大限度資料...")
            # print("目前資料庫擁有資料: {} - {}".format( self.df_stocks.Date.min(), self.df_stocks.Date.max() ) )
            # print("取用中...")
            
            

        self.df_stocks = self.df_stocks[ (self.df_stocks.Date >= self.dates[0]) & (self.df_stocks.Date <= self.dates[-1]) ]
        self.df_institutional_investors = self.df_institutional_investors[ (self.df_institutional_investors.Date >= self.dates[0]) & 
                                            (self.df_institutional_investors.Date <= self.dates[-1]) ]

        # reset一下index值，不然後面的會有問題
        self.df_stocks.reset_index(drop=True, inplace=True)
        self.df_institutional_investors.reset_index(drop=True, inplace=True)

    def Close(self):
        
        self.db.close()