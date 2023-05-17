import asyncio
import json
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
import aiohttp
import pandas as pd
import pytz
from PIL import Image
from pandas import DataFrame
from plotly.graph_objs import Layout

from utils.BSHARE import getLimitOrdersBSHARE
from utils.TOMB.tombAPI import userParameterParser
from utils.TOMB.tombQuerys import TombPriceInFTMchart, TombPriceInFantomChart
import numpy as np


async def getChart(Day="12H", resolution="1H"):
    if Day == "12H":
        DayNum = 43200

    else:
        dateRange = {
            "1M": 60,
            "5M": 300,
            "15M": 900,
            "30M": 1800,
            "12H": 43200,
            "1D": 86400,
            "7D": 432000,
            "3M": 7884000,
        }
        DayNum = dateRange.get(Day)

    if resolution == "1H":
        resolution = {1: "hour"}
        window, resolution = list(resolution.items())[0]
    else:
        position = {
            "1M": {1: "minute"},
            "5M": {5: "minute"},
            "15M": {15: "minute"},
            "1H": {1: "hour"},
            "4H": {4: "hour"},
        }
        resolution = position.get(resolution)

        window, resolution = list(resolution.items())[0]

    payload = f"?pair=0xab2ddcbb346327bbdf97120b0dd5ee172a9c8f9e" \
              f"&chain=ftm" \
              f"&denomination=native" \
              f"&limit=100" \
              f"&from=0" \
              f"&to={str(int(time.mktime(datetime.today().timetuple())))}" \
              f"&resolution={str(resolution)}" \
              f"&window={str(window)}" \
              f"&position=1" \



    headers = {
        'Host': 'api.keks.app',
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
        'sec-gpc': '1',
        'origin': 'https://kek.tools',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://kek.tools/',
        'accept-language': 'en-US,en;q=0.9',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.keks.app/v2/candles' + payload, headers=headers) as resp:

            response = await resp.json()
        response = str(response).replace('', '') \
            .replace("'", '"') \
            .replace("{[{", '{{') \
            .replace("}]}", '}}') \
            .replace('"t"', '"Date"') \
            .replace('"o"', '"Open"') \
            .replace('"h"', '"High"') \
            .replace('"l"', '"Low"') \
            .replace('"c"', '"Close"') \
            .replace('"v"', '"Volume"')
        jsonTradingData = json.loads(response)
    return await chartBuilberV2(jsonTradingData)


async def chartBuilberV2(chatData):
    limits = [1, 1.01]
    eastern = pytz.timezone('US/Eastern')

    df: DataFrame = pd.DataFrame.from_dict(chatData).fillna(method="backfill")

    x = df['Date']
    y = df['Open']

    x_mod = x.copy()
    y_mod = y.copy()
    for l in limits:
        x_mod, y_mod = modify_coords(x_mod, y_mod, l)

    y1, y2, y3 = [y_mod.copy() for i in range(3)]
    y1[y1 < limits[1]] = np.nan
    y2[(y2 < limits[0]) | (y2 > limits[1])] = np.nan
    y3[y3 > limits[0]] = np.nan
    x = pd.to_datetime(df['Date'], unit='ms').dt.tz_localize('UTC').dt.tz_convert(eastern)

    layout = Layout(
        autosize=True,
        width=1980,
        height=1080,
        margin=dict(l=10, r=140, t=80, b=10),
        title="<b>BASED PEG</b>",

        paper_bgcolor='rgb(0.03,0.00,0.07)',
        plot_bgcolor='rgb(0.03,0.00,0.07)',
        yaxis_tickformat=".3f",
        title_x=0.5,
        font=dict(
            family="Helvetica Neue,sans-serif",
            size=25,
            color="White")
    )

    limitOrders = await getLimitOrdersBSHARE.limitOrdersHandler()

    fig = go.Figure([
        go.Scatter(x=x, y=limits[1] * np.ones_like(x), opacity=1, line_width=1, line=dict(color="#d6d011"),
                   showlegend=False),

        go.Scatter(x=x_mod, y=y1, fill="tonexty", fillcolor='rgba(0,150,0,0.5)',
                   mode='none', opacity=0.5, showlegend=False),

        go.Scatter(x=x, y=limits[0] * np.ones_like(x), opacity=1, line_width=1, line=dict(color="#d6d011"),
                   showlegend=False),

        go.Scatter(x=x_mod, y=y2, fill="tonexty", fillcolor='rgba(162,126,89,0.5)',
                   mode='none', opacity=0.5, showlegend=False),

        go.Scatter(x=x, y=limits[0] * np.ones_like(x), opacity=1, line_width=1,
                   showlegend=False),

        go.Scatter(x=x_mod, y=y3, fill="tonexty", fillcolor='rgba(67, 37, 22,0.8)',
                   mode='none', opacity=0.5, showlegend=False),

    ], layout=layout)

    img = Image.open('based.png')  # image path
    # defined to source
    fig.add_layout_image(
        dict(
            source=img,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=1.2, sizey=1.2,
            xanchor="center",
            yanchor="middle",
            layer="below",
            sizing="stretch",
            opacity=0.5
        )
    )
    max_limit_volume = 30000
    BUY = 0
    SELL = 0
    for limit_order_name, limit_order_info in limitOrders.items():
        if limit_order_name == "BUY":
            for y_value, volume in limit_order_info.items():
                if volume > 500:
                    BUY = BUY + volume
                    y_value = float(y_value)
                    fig.add_shape(type="line",
                                  x0=1, y0=y_value, x1=1 - 0.1 * volume / max_limit_volume, y1=y_value,
                                  line=dict(color="green", width=3)
                                  )
                    fig.add_annotation(
                        x=1.05, y=y_value, xshift=40,
                        yshift=0,
                        xref="paper",
                        text=f"{'$' + str(volume)} = {y_value}", font=dict(color="green", size=20),
                        showarrow=False
                    )
        if limit_order_name == "SELL":
            for y_value, volume in limit_order_info.items():
                if volume > 500:
                    SELL = SELL + volume
                    y_value = float(y_value)
                    fig.add_shape(type="line",
                                  x0=1, y0=y_value, x1=1 - 0.1 * volume / max_limit_volume, y1=y_value,
                                  line=dict(color="red", width=3)
                                  )
                    fig.add_annotation(
                        x=1.05, y=y_value, xshift=40,
                        yshift=0,
                        xref="paper",
                        text=f"{'$' + str(volume)} = {y_value}", font=dict(color="red", size=20),
                        showarrow=False
                    )
            fig.update_shapes(dict(xref='paper', yref='y'))

    data = {'buy': BUY, 'sell': SELL}

    fig.write_image("BASED_CHART.png")
    return data


def modify_coords(x, y, y_lim):
    """If a line segment defined by `(x1, y1) -> (x2, y2)` intercepts
        a limiting y-value, divide this segment by inserting a new point
        such that y_newpoint = y_lim.
        """
    xv, yv = [x[0]], [y[0]]
    for i in range(len(x) - 1):
        xc, xn = x[i:i + 2]
        yc, yn = y[i:i + 2]
        if ((yc < y_lim) and (yn > y_lim)) or ((yc > y_lim) and (yn < y_lim)):
            xv.append(((y_lim - yc) / ((yn - yc) / (xn - xc))) + xc)
            yv.append(y_lim)
        xv.append(xn)
        yv.append(yn)
    return np.array(xv), np.array(yv)


async def userParameterParser(dateType):
    if dateType == "5M":
        date = (datetime.now() - timedelta(minutes=5))
    elif dateType == "15M":
        date = (datetime.now() - timedelta(minutes=15))
    elif dateType == "30M":
        date = (datetime.now() - timedelta(minutes=30))
    elif dateType == "1H":
        date = (datetime.now() - timedelta(hours=1))
    elif dateType == "3H":
        date = (datetime.now() - timedelta(hours=3))
    elif dateType == "6H":
        date = (datetime.now() - timedelta(hours=6))
    elif dateType == "12H":
        date = (datetime.now() - timedelta(hours=12))
    elif dateType == "24H":
        date = (datetime.now() - timedelta(hours=24))
    elif dateType == "2D":
        date = (datetime.now() - timedelta(days=2))
    elif dateType == "7D":
        date = (datetime.now() - timedelta(days=7))
    elif dateType == "14D":
        date = (datetime.now() - timedelta(days=14))
    elif dateType == "30D":
        date = (datetime.now() - timedelta(days=30))
    else:
        date = (datetime.now() - timedelta(hours=24))
    return dateType, date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
