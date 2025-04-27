import taiwan_stocks.taiwan_stocks as TS

# Crawl stock data, save data into MySQL, fetch data from MySQL
ts = TS.TaiwanStocks(
    is_save=True, is_draw=True, is_analyze=True, save_path="/mnt/c/Users/smalldan/Downloads"
)
ts.run()
stock_info = ts.get_info()
