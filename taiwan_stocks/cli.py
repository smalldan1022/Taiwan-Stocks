import argparse

from taiwan_stocks.taiwan_stocks import TaiwanStocks


def main():
    parser = argparse.ArgumentParser(description="Taiwan Stock Crawler CLI")
    parser.add_argument("--save", action="store_true", help="Save data into database")
    parser.add_argument("--draw", action="store_true", help="Draw stock plots")
    parser.add_argument("--analyze", action="store_true", help="Analyze stock data")
    parser.add_argument("--save-path", type=str, default="", help="Path to save plots")

    parser.add_argument("--stock-name", type=str, help="Stock name (中文名，可選)")
    parser.add_argument("--stock-num", type=str, help="Stock number (股票代號，可選)")
    parser.add_argument("--start-date", type=str, help="Start date (格式：YYYYMMDD)")
    parser.add_argument("--end-date", type=str, help="End date (格式：YYYYMMDD)")

    args = parser.parse_args()

    stock_crawler = TaiwanStocks(
        is_save=args.save,
        is_draw=args.draw,
        is_analyze=args.analyze,
        save_path=args.save_path,
    )

    if args.save_path:
        stock_crawler.save_path = args.save_path
    if args.stock_name:
        stock_crawler.stock_name = args.stock_name
    if args.stock_num:
        stock_crawler.stock_num = args.stock_num
    if args.start_date:
        stock_crawler.start_date = args.start_date
    if args.end_date:
        stock_crawler.end_date = args.end_date

    if not (args.stock_name or args.stock_num):
        raise ValueError("Please provide stock name or stock number!!")

    if not (args.start_date and args.end_date):
        raise ValueError("Please provide both start-date and end-date!!")

    stock_crawler.run()


if __name__ == "__main__":
    main()
