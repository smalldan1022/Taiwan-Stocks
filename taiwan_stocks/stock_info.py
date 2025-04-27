TSE_URL = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=%s&type=ALLBUT0999"
TSE_PB_PE_URL = (
    "https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date=%s&selectType=ALL"
)
TSE_COLUMNS = [
    "Date",
    "證券代號",
    "證券名稱",
    "成交股數",
    "成交筆數",
    "成交金額",
    "開盤價",
    "最高價",
    "最低價",
    "收盤價",
    "漲跌(+/-)",
    "漲跌價差",
]
TSE_INSTITUTIONAL_INVESTORS_URL = (
    "https://www.twse.com.tw/rwd/zh/fund/T86?date=%s&selectType=ALLBUT0999&response=csv"
)
TSE_INSTITUTIONAL_INVESTORS_COLUMNS = [
    "Date",
    "證券代號",
    "證券名稱",
    "外陸資買進股數(不含外資自營商)",
    "外陸資賣出股數(不含外資自營商)",
    "外陸資買賣超股數(不含外資自營商)",
    "外資自營商買進股數",
    "外資自營商賣出股數",
    "外資自營商買賣超股數",
    "投信買進股數",
    "投信賣出股數",
    "投信買賣超股數",
    "自營商買賣超股數",
    "自營商買進股數(自行買賣)",
    "自營商賣出股數(自行買賣)",
    "自營商買賣超股數(自行買賣)",
    "自營商買進股數(避險)",
    "自營商賣出股數(避險)",
    "自營商買賣超股數(避險)",
    "三大法人買賣超股數",
]

OTC_URL = "https://www.tpex.org.tw/www/zh-tw/afterTrading/otc?date=%s&type=EW&id=&response=csv&order=0&sort=asc"
OTC_PB_PE_URL = (
    "https://www.tpex.org.tw/www/zh-tw/afterTrading/peQryStock?date=%s&code=%s&id=&response=csv"
)
OTC_INSTITUTIONAL_INVESTORS_URL = (
    "https://www.tpex.org.tw/www/zh-tw/insti/dailyTrade?type=Daily&sect=AL&date=%s&id=&response=csv"
)
OTC_STOCKS_RENAME_COLUMNS = {
    "代號": "證券代號",
    "名稱": "證券名稱",
    "收盤 ": "收盤價",
    "漲跌": "漲跌價差",
    "開盤 ": "開盤價",
    "最高 ": "最高價",
    "最低": "最低價",
    "成交股數  ": "成交股數",
    " 成交金額(元)": "成交金額",
    " 成交筆數 ": "成交筆數",
}
OTC_INSTI_INV_RENAME_COLUMNS = {
    "代號": "證券代號",
    "名稱": "證券名稱",
    "外資及陸資(不含外資自營商)-買進股數": "外陸資買進股數(不含外資自營商)",
    "外資及陸資(不含外資自營商)-賣出股數": "外陸資賣出股數(不含外資自營商)",
    "外資及陸資(不含外資自營商)-買賣超股數": "外陸資買賣超股數(不含外資自營商)",
    "外資自營商-買進股數": "外資自營商買進股數",
    "外資自營商-賣出股數": "外資自營商賣出股數",
    "外資自營商-買賣超股數": "外資自營商買賣超股數",
    "投信-買進股數": "投信買進股數",
    "投信-賣出股數": "投信賣出股數",
    "投信-買賣超股數": "投信買賣超股數",
    "自營商(自行買賣)-買進股數": "自營商買進股數(自行買賣)",
    "自營商(自行買賣)-賣出股數": "自營商賣出股數(自行買賣)",
    "自營商(自行買賣)-買賣超股數": "自營商買賣超股數(自行買賣)",
    "自營商(避險)-買進股數": "自營商買進股數(避險)",
    "自營商(避險)-賣出股數": "自營商賣出股數(避險)",
    "自營商(避險)-買賣超股數": "自營商買賣超股數(避險)",
    "自營商-買賣超股數": "自營商買賣超股數",
    "三大法人買賣超股數合計": "三大法人買賣超股數",
}
NUMERICAL_COLUMNS = [
    "成交股數",
    "成交筆數",
    "成交金額",
    "開盤價",
    "最高價",
    "最低價",
    "收盤價",
]
