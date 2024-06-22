import taiwan_stocks as TS

# If you don't have the MySQL database, just simply set  <------ IMPORTANT MESSAGE
# db_settings = None                                     <------ IMPORTANT MESSAGE
# MySQL_flag = False                                     <------ IMPORTANT MESSAGE
# Fetch_stock_statistics_flag = False                    <------ IMPORTANT MESSAGE


db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "YOUR-PASSWORD-HERE!!",
    "db": "YOUR-DATABASE-SCHEMA-NAME-HERE!!",
    "charset": "utf8",
}

# Crawl stock data, save data into MySQL, fetch data from MySQL
stocks = TS.Taiwan_Stocks(
    db_settings=db_settings,
    Crawl_flag=True,
    MySQL_flag=True,
    Fetch_stock_statistics_flag=True,
    timesleep=5,
)

# Draw plots
stocks.draw_plots(
    D_5MA=True,
    D_10MA=True,
    D_20MA=True,
    D_60MA=True,
    D_IT=True,
    D_FI=True,
    D_DL=True,
    save_fig=False,
    fig_name="",
    save_path="",
)

# Calculate the stock's dependency
stocks.Dependency(
    IT_flag=True,
    IT_stocks_number=50,
    FI_flag=True,
    FI_stocks_number=100,
    DL_flag=True,
    DL_stocks_number=4,
    date_interval=3,
    value_date_interval=2,
)

stocks.Stand_Up_On_MAs()

print("\n  {}".format("(6) Closing the program"))
print("----------------------------------------")
print("\nProgram Finished...\n")
