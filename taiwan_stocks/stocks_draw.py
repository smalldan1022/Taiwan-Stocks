import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Drawer:
    def __init__(self, stock_name: str, stock_num: str, df_stocks: pd.DataFrame, **kwargs) -> None:
        self.row = 1
        self.fig = None
        self.df_stocks = df_stocks
        self.title = f"{stock_name}-{stock_num}"

    def cal_investment_trust(self) -> None:
        df = self.df_stocks["投信買賣超股數"].str.replace(",", "")
        self.inv_num = pd.to_numeric(df).values
        self.inv_num = self.inv_num / 1000
        self.inv_num = np.ceil(self.inv_num)

    def cal_foreign_investor(self) -> None:
        df = self.df_stocks["外陸資買賣超股數(不含外資自營商)"].str.replace(",", "")
        self.foreign_num = pd.to_numeric(df).values
        self.foreign_num = self.foreign_num / 1000
        self.foreign_num = np.ceil(self.foreign_num)

    def cal_dealer(self) -> None:
        df = self.df_stocks["自營商買賣超股數"].str.replace(",", "")
        self.dealer_num = pd.to_numeric(df).values
        self.dealer_num = self.dealer_num / 1000
        self.dealer_num = np.ceil(self.dealer_num)

    def draw_plots(
        self,
        K_plot=True,
        volumn_plot=True,
        D_5MA=False,
        D_10MA=False,
        D_20MA=False,
        D_60MA=False,
        D_IT=False,
        D_FI=False,
        D_DL=False,
        save_fig=False,
        file_name="",
        save_path="",
    ):
        flags = [K_plot, volumn_plot, D_IT, D_FI, D_DL]
        title_candidates = ["K線圖", "成交量", "投信買超", "外資買超", "自營商買超"]

        subplot_titles = [
            title for flag, title in zip(flags, title_candidates, strict=False) if flag is True
        ]
        subplot_nums = sum(flags)

        self.fig = make_subplots(
            rows=subplot_nums,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.027,
            horizontal_spacing=0.009,
            subplot_titles=subplot_titles,
            row_heights=[0.45, 0.2, 0.25, 0.25, 0.25],
            specs=[
                [{"secondary_y": True}],
                [{"secondary_y": False}],
                [{"secondary_y": False}],
                [{"secondary_y": False}],
                [{"secondary_y": False}],
            ],
        )

        # adjust the layout of the figure
        font_family = "Noto Sans CJK TC"
        self.fig.update_layout(
            width=1650,
            height=3000,
            xaxis_rangeslider_visible=False,
            title={
                "text": self.title,
                "x": 0.0387,
                "y": 0.99,
                "font": {"family": font_family, "size": 36, "color": "#000000"},
            },
            font={"family": font_family, "size": 18},
        )

        # tune the font size of the titles
        self.fig.update_annotations(font_size=32)

        # create k plot figure
        figure_K_plot = go.Candlestick(
            x=self.df_stocks["Date"],
            open=self.df_stocks["開盤價"],
            high=self.df_stocks["最高價"],
            low=self.df_stocks["最低價"],
            close=self.df_stocks["收盤價"],
            increasing_line_color="red",
            decreasing_line_color="green",
            name="K線",
            showlegend=True,
        )

        # draw k plots
        self.fig.add_trace(figure_K_plot, self.row, 1, secondary_y=False)
        self.row += 1

        volumn = np.round(self.df_stocks["成交股數"] / 1000, decimals=0)
        volumn_color = ["#e53935"] + [
            "#e53935" if volumn[i] >= volumn[i - 1] else "#4caf50" for i in range(1, len(volumn))
        ]

        # create the volume plots figure
        figure_volume = go.Bar(
            x=self.df_stocks["Date"], y=volumn, marker_color=volumn_color, showlegend=False
        )

        # draw volume plots
        self.fig.add_trace(figure_volume, self.row, 1, secondary_y=False)
        self.row += 1

        if D_5MA:
            self.draw_MA(day_interval=5, marker={"color": "#FF9224"})
        if D_10MA:
            self.draw_MA(day_interval=10, marker={"color": "#E800E8"})
        if D_20MA:
            self.draw_MA(day_interval=20, marker={"color": "#7373B9"})
        if D_60MA:
            self.draw_MA(day_interval=60, marker={"color": "#00CACA"})
        print("Finish drawing the MA lines.")

        if D_IT:
            self.cal_investment_trust()
            self.draw_bar(buying_number=self.inv_num, marker={"color": "#FF9224"}, name="投信")
        if D_FI:
            self.cal_foreign_investor()
            self.draw_bar(buying_number=self.foreign_num, marker={"color": "#E800E8"}, name="外資")
        if D_DL:
            self.cal_dealer()
            self.draw_bar(buying_number=self.dealer_num, marker={"color": "#7373B9"}, name="自營商")
        print("Finish drawing the bars.")

        if save_fig and file_name != "" and save_path != "":
            filepath_base = os.path.join(save_path, file_name)
            self.fig.write_image(f"{filepath_base}.png", format="png")
            self.fig.write_html(f"{filepath_base}.html", include_plotlyjs="cdn")

        # self.fig.show()

    def draw_MA(self, day_interval: int, marker: dict) -> float:
        MA = self.df_stocks["收盤價"].rolling(day_interval).mean()

        figure_MA = go.Scatter(
            x=self.df_stocks["Date"],
            y=MA,
            mode="lines",
            name=f"{day_interval}MA",
            marker=marker,
            showlegend=True,
        )
        self.fig.add_trace(figure_MA, 1, 1, secondary_y=True)

    def draw_bar(self, buying_number: np.ndarray, marker: str, name: str = "") -> None:
        color = ["#e53935"] + [
            "#e53935" if buying_number[i] >= buying_number[i - 1] else "#4caf50"
            for i in range(1, len(buying_number))
        ]
        Bar = go.Bar(
            x=self.df_stocks["Date"].to_numpy(),
            y=buying_number,
            width=0.45,
            name=name,
            marker_color=color,
            showlegend=False,
        )
        go.Scatter(
            x=self.df_stocks["Date"].to_numpy(),
            y=buying_number,
            mode="lines",
            marker=marker,
            showlegend=False,
        )
        self.fig.add_trace(Bar, self.row, 1, secondary_y=False)
        self.row += 1
