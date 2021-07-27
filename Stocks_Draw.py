import Stocks_Analasis as SA
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Stocks_Draw(SA.Stocks_Analasis):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        
        self.MA5 =  pd.Series(data=np.nan, index=["1"])
        self.MA10 = pd.Series(data=np.nan, index=["1"])
        self.MA20 = pd.Series(data=np.nan, index=["1"])
        self.MA60 = pd.Series(data=np.nan, index=["1"])

        self.row = 1
        self.fig = None

    # DRAWING
    #############################################
        
    def draw_plots(self, K_plot = True, Volumn_plot = True,  D_5MA=False, D_10MA = False, D_20MA = False, D_60MA = False, 
                   D_IT=False, D_FI=False, D_DL=False, save_fig=False, fig_name="", save_path=""):
        
        
        Flags = [K_plot, Volumn_plot, D_IT, D_FI, D_DL]
        
        Subplot_titles = [ "K線圖", "成交量", "投信買超", "外資買超", "自營商買超" ]
        
        subplot_titles = [ j for i, j in zip(Flags, Subplot_titles) if i == True ]
        
        subplot_nums = sum(Flags)
        
        # 創造subplots, 並且設定相關參數
        self.fig = make_subplots(rows = subplot_nums, cols = 1, shared_xaxes = True,
                                 vertical_spacing = 0.027, horizontal_spacing = 0.009, 
                                 subplot_titles = subplot_titles, row_heights  = [0.45, 0.2, 0.25, 0.25, 0.25 ],
                                 specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}],
                                        [{"secondary_y": False}], [{"secondary_y": False}]] )
        
        # 把figure的整理大小調大，並把Candlestick的下半部分拿掉，整體圖畫起來比較順
        self.fig.update_layout( width=1650, height=3000, xaxis_rangeslider_visible = False,
                                title=dict( text='<b>{}-{}</b>'.format(self.table_name, self.stock_num), x=0.0387, y=0.99,
                                            font=dict( family="Arial", size=36, color='#000000' ) ), 
                                font = dict(family="Arial", size=18) )

        # 把supplots的title字體調大
        self.fig.update_annotations(font_size=32)


        # 創造K線圖
        figure_K_plot = go.Candlestick( x=self.df_stocks['Date'],
                                        open=self.df_stocks['開盤價'],
                                        high=self.df_stocks['最高價'],
                                        low=self.df_stocks['最低價'],
                                        close=self.df_stocks['收盤價'], 
                                        increasing_line_color= 'red', 
                                        decreasing_line_color= 'green',
                                        name='K線',
                                        showlegend = True )
        
        # 畫K線圖
        self.fig.add_trace(figure_K_plot, self.row, 1, secondary_y = False)

        self.row += 1

        Volumn = pd.to_numeric(self.df_stocks['成交股數'].apply(lambda x: x.replace(',','')))

        Volumn = np.round( Volumn / 1000, decimals=0 )

        Volumn_color = ['#e53935']

        # Volumn_color = [ 'red' if Volumn[ii] >= Volumn[ii-1] else 'green' for ii in range(1, len(Volumn)) ]

        for ii in range(1, len(Volumn)):

            if Volumn[ii] >= Volumn[ii-1]:
                Volumn_color.append('#e53935')
            else:
                Volumn_color.append('#4caf50')
        
        # 創造成交量(Volume)
        figure_volume = go.Bar( x = self.df_stocks['Date'], 
                                y = Volumn,
                                marker_color = Volumn_color,
                                showlegend = False )

        # 畫volume
        self.fig.add_trace(figure_volume , self.row, 1, secondary_y = False )

        self.row += 1

        # Set y-axes titles
        # Max_Volume = pd.to_numeric(self.df_stocks['成交股數'].apply(lambda x: x.replace(',',''))).max()
        # Max_Stock_Price = self.df_stocks['最高價'].apply(lambda x:x.replace(",", "").replace("-","0")).astype(float).max()
        # Min_Stock_Price = self.df_stocks['最低價'].apply(lambda x:x.replace(",", "").replace("-","0")).astype(float).min()
                              
        # self.fig.update_layout(yaxis=dict(title="<b>成交量</b>", range=[0, Max_Volume*7]) )
        # self.fig.update_layout(yaxis2=dict(title="<b>股價</b>", range = [Min_Stock_Price//1.2, Max_Stock_Price*1.02]))

        
        if D_5MA:
            self.MA5 = self.draw_MA(day_interval=5, marker = dict(color = '#FF9224'))
        if D_10MA:
            self.MA10 = self.draw_MA(day_interval=10, marker = dict(color = '#E800E8'))
        if D_20MA:
            self.MA20 = self.draw_MA(day_interval=20, marker = dict(color = '#7373B9'))
        if D_60MA:
            self.MA60 = self.draw_MA(day_interval=60, marker = dict(color = '#00CACA'))
        
        if D_IT:    
            self.Draw_Bar(buying_number = self.IT_num, marker = dict(color = '#FF9224'), name = "投信")
        if D_FI:
            self.Draw_Bar(buying_number = self.FI_num,  marker = dict(color = '#E800E8'), name = "外資")
        if D_DL:
            self.Draw_Bar(buying_number = self.DL_num, marker = dict(color = '#7373B9'), name = "自營商")

        if save_fig and fig_name != "" and save_path != "":
            self.fig.write_image(save_path + fig_name + ".png", format='png')
            # self.fig.write_html(save_path + fig_name + ".html", include_plotlyjs="cdn")
        
        self.fig.show()
        
    def draw_MA(self, day_interval, marker):
    
        MA = self.df_stocks["收盤價"].rolling(day_interval).mean()

        figure_MA = go.Scatter( x = self.df_stocks["Date"], 
                                y = MA, 
                                mode = 'lines', 
                                name = "{}MA".format(day_interval),
                                marker = marker,
                                showlegend = True )
            
        self.fig.add_trace(figure_MA, 1, 1, secondary_y = True)

        return MA

    def Draw_Bar(self, buying_number, marker, name = ""):

        color = [ '#e53935' if ii >= 0 else '#4caf50' for ii in buying_number ]

        Bar = go.Bar(x = self.df_stocks["Date"].to_numpy(), 
                     y = buying_number,
                     width = 0.45, 
                     name = name,
                     marker_color = color, 
                     showlegend = False)

        Line = go.Scatter(x = self.df_stocks["Date"].to_numpy(),
                          y = buying_number,
                          mode = "lines", 
                          marker = marker,
                          showlegend = False)

        self.fig.add_trace(Bar, self.row, 1, secondary_y = False)
        # self.fig.add_trace(Line, self.row, 1, secondary_y = False)

        self.row += 1