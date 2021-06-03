# 台灣上市上櫃公司盤後股票資料抓取分析

[![Website MyProfile](https://img.shields.io/website/http/huggingface.co/transformers/index.html.svg?down_color=red&down_message=offline&up_message=online)](https://github.com/smalldan1022)


從台灣證券交易所、證券櫃檯買賣中心，抓取台灣上市櫃公司的盤後資料，包括價格、以及法人的成交量資訊。目前提供的功能有將爬取的資料存進去 MySQL資料庫中，並且畫出 K線圖以及 5MA、10MA、20MA線圖，K線圖的下方有成交量，以及三大法人的成交量，很適合盤後拿來判斷股票進出場。

##### *Hint 1 : 證交所有 request limit, 目前測試 5秒爬一次比較安全，時間間隔太短的話會被 ban掉，如果有好的方法可以躲的話也歡迎提供 !!*
##### *Hint 2 : 櫃買中心在爬資料的時候會比證交所的還要慢，目前還不確定是甚麼原因，如果有人知道的話歡迎來信跟我討論 !!*



![image](https://github.com/smalldan1022/Taiwan-Stocks/blob/main/pictures/Stocks.png)

此為示意圖，雖然最下面的日期數字是直行，但用此程式會在 chrome端直接開一個 local page秀出這張圖表，滑鼠游標點上去會有相關的日期，非常方便。


資料來源:

* [台灣證券交易所](https://www.twse.com.tw/zh/)
* [證券櫃檯買賣中心](https://www.tpex.org.tw/web/index.php?l=zh-tw)


## Requirements

* pandas             -> 1.0.5  
* plotly             -> 4.14.3
* pymysql            -> 0.10.1
* python             -> 3.7.7
* python-dateutil    -> 2.8.1
* requests           -> 2.24.0 

## MySQL 安裝


* [官網安裝教學](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/)
  
這部分看個人需求，我目前都是將爬蟲完的資料存進 local MySQL database裡面，在之後想要分析的時候不用再重爬一次資料，分析速度會更快。


至於安裝流程，請看網路上各篇 google教學，都蠻詳盡的，由於百家爭鳴，這邊就不特定貼那個網站了，有遇到任何問題歡迎來信，我會幫你盡力解決!!



## Quick Start

### *皆使用 Stocks.py*

``` python
stocks = TS.Taiwan_Stocks( db_settings = db_settings, Crawl_flag = True, MySQL_flag = True, 
                           Fetch_stock_statistics_flag = True, timesleep = 5)

參數解釋:

- db_settings                 -> 設置你自己的database參數
- Crawl_flag                  -> 是否爬資料 
- MySQL_flag                  -> 是否存進 MySQL database 
- Fetch_stock_statistics_flag -> 是否直接拿取 Database資料作分析
- timesleep                   ->  爬蟲的時間間隔

```

### 1.  如果要存到 MySQL database

``` python
stocks = TS.Taiwan_Stocks( db_settings = db_settings, Crawl_flag = True, MySQL_flag = True, 
                           Fetch_stock_statistics_flag = True, timesleep = 5)
```

### 2. 如果沒有要存到MySQL database，純爬蟲下來分析

``` python
stocks = TS.Taiwan_Stocks( db_settings = None, Crawl_flag = True, MySQL_flag = False, 
                           Fetch_stock_statistics_flag = False, timesleep = 5)
```
### 3. 如果MySQL database已有資料，純分析

``` python
stocks = TS.Taiwan_Stocks( db_settings = db_settings, Crawl_flag = False, MySQL_flag = False, 
                           Fetch_stock_statistics_flag = True, timesleep = 5)
```

## Advance statistics or plots

### *皆使用 Stocks.py*
### *1. 畫出圖表 - 可繪製線圖、 繪製法人成交量、儲存成圖片*

```python
stocks = TS.Taiwan_Stocks( db_settings = db_settings, Crawl_flag = True, MySQL_flag = True, 
                           Fetch_stock_statistics_flag = True, timesleep = 5)

stocks.draw_plots( D_5MA=True, D_10MA = True, D_20MA = True, D_IT=True, D_FI=True, D_DL=True, save_fig=False, 
                   fig_name="", save_path="")

參數解釋:

- D_5MA     -> 是否繪製五日均線
- D_10MA    -> 是否繪製十日均線
- D_20MA    -> 是否繪製二十日均線 
- D_IT      -> 是否繪製投信成交量
- D_FI      -> 是否繪製外資成交量
- D_DL      -> 是否繪製自營商成交量
- save_fig  -> 是否存取圖
- fig_name  -> 圖的名稱
- save_path -> 存圖的路徑
```

* 繪製線圖
```python
stocks.draw_plots( D_5MA=True, D_10MA = True, D_20MA = True, D_IT=False, D_FI=False, D_DL=False, 
                   save_fig=False, fig_name="", save_path="")

```

* 繪製法人成交量
```python
stocks.draw_plots( D_5MA=True, D_10MA = True, D_20MA = True, D_IT=True, D_FI=True, D_DL=True, 
                   save_fig=False, fig_name="", save_path="")

```

* 儲存成圖片
```python
stocks.draw_plots( D_5MA=True, D_10MA = True, D_20MA = True, D_IT=True, D_FI=True, D_DL=True, 
                   save_fig=True, fig_name="XXX.png",save_path="C:/Users/GitHub_projects/Side_project_1.stocks")

```
### *2. 買賣策略 - ( Algorithm )*


 1. 短線 - 針對站上5MA、10MA、20MA的三陽開泰型股票進行買進
    * 最近由於盤勢復甦，這類型的股票有肉可吃，最近正在加緊開發

 2. 中長線 - 針對站上5MA、10MA、20MA、60MA的四海遊龍型股票進行買進
    * 開發中

 3. 針對法人現金流向而做的買賣策略 
    * 曾經以此選股方式在今年三月選到 IC設計飆股-天鈺


*Hint : 這邊的選股策略只是我個人的一些研究心得，請勿依據此心得而操作股票，這些策略也不是作為或被視為買入或出售該股票的邀請或意向* 


## Updates

### 2021-06-03: 
更新 [2. 買賣策略 - ( Algorithm )](#2-買賣策略----algorithm-)，目前暫不提供自行開發的 algorithm。


## 聯絡方式

有任何問題歡迎來信，會盡快回覆 !

*信箱 : asign1022@gmail.com*

## 免責聲明

本人旨在為廣大投資人提供正確可靠之資訊及最好之服務，作為投資研究的參考依據，若因任何資料之不正確或疏漏所衍生之損害或損失，本人將不負法律責任。是否經由本網站使用下載或取得任何資料，應由您自行考量且自負風險，因任何資料之下載而導致您電腦系統之任何損壞或資料流失，您應負完全責任。

所有分享純屬個人心得，所提供的投資策略未必適合所有投資者, 也非作為或被視為買入或出售該股票的邀請或意向。



