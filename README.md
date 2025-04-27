# 台灣上市上櫃公司盤後股票資料抓取分析

[![Website MyProfile](https://img.shields.io/website/http/huggingface.co/transformers/index.html.svg?down_color=red&down_message=offline&up_message=online)](https://github.com/smalldan1022)

從台灣證券交易所、證券櫃檯買賣中心，抓取台灣上市櫃公司的盤後資料，包括價格、以及法人的成交量資訊。目前提供的功能有將爬取的資料存進去 MySQL 資料庫中，並且畫出 K 線圖以及 5MA、10MA、20MA 線圖，K 線圖的下方有成交量，以及三大法人的成交量，很適合盤後拿來判斷股票進出場。

### 這邊有實際的[圖表 Demo](https://nbviewer.jupyter.org/github/smalldan1022/Taiwan-Stocks/blob/main/pictures/index.html) !!

##### _Hint 1 : 證交所有 request limit, 目前測試 1 秒爬一次比較安全，時間間隔太短的話會被 ban 掉，如果有好的方法可以躲的話也歡迎提供 !!_

&emsp;

![image](https://github.com/smalldan1022/Taiwan-Stocks/blob/main/pictures/Stocks.png)

- 此為示意圖，雖然最下面的日期數字是直行，但用此程式會在 chrome 端直接開一個 local page 秀出這張圖表，滑鼠游標點上去會有相關的日期，非常方便。

### 資料來源:

- [台灣證券交易所](https://www.twse.com.tw/zh/)
- [證券櫃檯買賣中心](https://www.tpex.org.tw/web/index.php?l=zh-tw)


## MySQL 安裝

- [官網安裝教學](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/)

這部分看個人需求，我目前都是將爬蟲完的資料存進 local MySQL database 裡面，在之後想要分析的時候不用再重爬一次資料，分析速度會更快。

至於安裝流程，請看網路上各篇 google 教學，都蠻詳盡的，由於百家爭鳴，這邊就不特定貼那個網站了，有遇到任何問題歡迎來信，我會幫你盡力解決!!

## Quick Start

__In run.py__

```python
import taiwan_stocks.taiwan_stocks as TS

# cawl stock data, save data into MySQL, fetch data from MySQL
ts = TS.TaiwanStocks(is_save=True, is_draw=True, is_analyze=True, save_path="YOUR/FILE/PATH")
ts.run()
stock_info = ts.get_info()

```

__In command line__

```bash
# in your terminal
# 1. install the taiwan-stock package first
poetry install
# 2. use it on bash
taiwan-stocks --stock-num 2330 --start-date 20240101 --end-date 20240110 --save --draw --save-path YOUR/PATH/HERE

```

### 1. 如果要存到 MySQL database

_在 run.py 修改 is_save 參數_
```python
import taiwan_stocks.taiwan_stocks as TS

# cawl stock data, save data into MySQL, fetch data from MySQL
ts = TS.TaiwanStocks(is_save=True, is_draw=True, is_analyze=True, save_path="YOUR/FILE/PATH")
ts.run()

# set is_save=True
```

_在 taiwan_stocks folder 底下建立自己的 .env 檔案_
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_PASSWORD
DB_NAME=YOUR_DB_NAME

```

### 2. 如果沒有要存到 MySQL database，純爬蟲下來分析

```python
import taiwan_stocks.taiwan_stocks as TS

# cawl stock data, save data into MySQL, fetch data from MySQL
ts = TS.TaiwanStocks(is_save=False)
ts.run()

# set is_save=False
```

## Advanced statistics or plots

### _使用 taiwan_stocks.py_

### _1. 畫出圖表 - 可繪製線圖、 繪製法人成交量、儲存成圖片_

```python
if self.is_draw:
    ...
    self.drawer.draw_plots(
        K_plot=True,
        volumn_plot=True,
        D_5MA=True,
        D_10MA=True,
        D_20MA=True,
        D_60MA=True,
        D_IT=True,
        D_FI=True,
        D_DL=True,
        save_fig=True,
        file_name=f"{self.stock_name}-{self.stock_num}",
        save_path=self.save_path,
    )


參數解釋:
- K_plot      -> 是否繪製 k 線圖
- volumn_plot -> 是否繪製成交量
- D_5MA       -> 是否繪製五日均線
- D_10MA      -> 是否繪製十日均線
- D_20MA      -> 是否繪製二十日均線
- D_IT        -> 是否繪製投信成交量
- D_FI        -> 是否繪製外資成交量
- D_DL        -> 是否繪製自營商成交量
- save_fig    -> 是否存取圖
- fig_name    -> 圖的名稱
- save_path   -> 存圖的路徑
```

- 儲存成圖片: 在 _run.py 調整參數_

```python
import taiwan_stocks.taiwan_stocks as TS

# cawl stock data, save data into MySQL, fetch data from MySQL
ts = TS.TaiwanStocks(is_save=True, 
save_path="YOUR/FILE/PATH")

# set is_save = True
# set save_path = "YOUR/FILE/PATH/HERE"

```

### _2. 買賣策略 - ( Algorithm )_

_Hint : 皆在 run.py 裡操作_

1.  短線 - 針對站上 5MA、10MA、20MA 的三陽開泰型股票進行買進

```python
import taiwan_stocks.taiwan_stocks as TS

# cawl stock data, save data into MySQL, fetch data from MySQL
ts = TS.TaiwanStocks(is_save=True, is_draw=True, is_analyze=True, save_path="YOUR/FILE/PATH")
ts.run()
ts.stand_up_on_MAs()
```

2.  中長線 - 針對站上 5MA、10MA、20MA、60MA 的四海遊龍型股票進行買進

```python
import taiwan_stocks.taiwan_stocks as TS

# cawl stock data, save data into MySQL, fetch data from MySQL
ts = TS.TaiwanStocks(is_save=True, is_draw=True, is_analyze=True, save_path="YOUR/FILE/PATH")
ts.run()
ts.stand_up_on_MAs()
```

3.  針對法人現金流向而做的買賣策略
    - 曾經以此選股方式在今年三月選到 IC 設計飆股-天鈺

_Hint : 這邊的選股策略只是我個人的一些研究心得，請勿依據此心得而操作股票，這些策略也不是作為或被視為買入或出售該股票的邀請或意向_

## Updates

### 2025-04-27:

- 大幅度修正 code structure, logic 讓專案變得 readable and structural
- 大量修正原本的 class names, function names, parameter names
- 修正原本的專案結構, 讓多個 componebt decouple
- 新增 poetry manage project
- 新增 ruff to make the code style consistent
- 新增 cli, 讓大家能直接安裝完無腦使用 taiwan-stocks package

### 2021-07-27:

- 修正交易量的數值 (先前是以交易市值計算)
- 修正 MySQL_Database.py 裡面的 bug
- 更新程式過後的圖以及 Demo 同步修改

### 2021-06-27:

- 調整了 Stock_Draw 的 Plot 圖表大小
- 調整 Stocks_Crawl 的爬蟲方法、數據的合併方法以及存入 Database 的方法
- 爬蟲股票殖利率、本益比、淨值比功能 - 完成

### 2021-06-23:

- 爬蟲股票殖利率、本益比、淨值比功能 (ongoing)

### 2021-06-14:

- 更新 [2. 買賣策略 - ( Algorithm ) 1. 2. ](#2-買賣策略----algorithm-) : 功能已完成

### 2021-06-13:

- 更新 [Demo](#這邊有實際的圖表demo-) : 讓大家能直接看圖表結果並操作看看 ( 互動式圖表 )

- 更新 [Quick Start](#quick-start) : 新增參數細節說明，讓大家在使用上更方便

### 2021-06-03:

- 更新 [2. 買賣策略 - ( Algorithm )](#2-買賣策略----algorithm-) : 目前仍在調整自行開發的 algorithm，如有興趣或想要一起討論，歡迎來信。

## 聯絡方式

有任何問題歡迎來信，會盡快回覆 !

_信箱 : asign1022@gmail.com_

## 免責聲明

本人旨在為廣大投資人提供正確可靠之資訊及最好之服務，作為投資研究的參考依據，若因任何資料之不正確或疏漏所衍生之損害或損失，本人將不負法律責任。是否經由本網站使用下載或取得任何資料，應由您自行考量且自負風險，因任何資料之下載而導致您電腦系統之任何損壞或資料流失，您應負完全責任。

所有分享純屬個人心得，所提供的投資策略未必適合所有投資者, 也非作為或被視為買入或出售該股票的邀請或意向。
