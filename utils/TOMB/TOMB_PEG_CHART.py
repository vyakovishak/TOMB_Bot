from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
import aiohttp
import pandas as pd
import pytz
from PIL import Image
from pandas import DataFrame
from plotly.graph_objs import Layout
from utils.TOMB.tombAPI import userParameterParser
from utils.TOMB.tombQuerys import TombPriceInFantomChart
import numpy as np
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools'))


async def requestCall(dateType):
    if dateType is None:
        rangeFrom = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        date = datetime.strptime(rangeFrom, "%Y-%m-%dT%H:%M:%S.%fZ")
        timestampFrom = int(datetime.timestamp(date) * 1000)
        rawFrom = "now-24H"
    else:
        rawFrom, rangeFrom = await userParameterParser(dateType)
        date = datetime.strptime(rangeFrom, "%Y-%m-%dT%H:%M:%S.%fZ")
        timestampFrom = int(datetime.timestamp(date) * 1000)
        rawFrom = f"now-{rawFrom}"

    headers = {
        'Host': 'stats.tomb.finance',
        'accept': 'application/json, text/plain, */*',
        'x-grafana-org-id': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36',
        'content-type': 'application/json',
        'sec-gpc': '1',
        'origin': 'https://stats.tomb.finance',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en-US,en;q=0.9',
    }
    statsData = {}
    QueryList = [TombPriceInFantomChart]
    for QueryNames in QueryList:
        params = {
            "queries": [{
                "query": str(QueryNames[0]),
                "refId": str(QueryNames[1]),
                "datasource": "InfluxDB",
                "datasourceId": 1,
                "intervalMs": 300000,
                "maxDataPoints": 500
            }],
            "range": {
                "from": rangeFrom,
                "to": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "raw": {
                    "from": rawFrom,
                    "to": "now"
                }
            },
            "from": str(timestampFrom),
            "to": str((int(round(time.time() * 1000))))
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://stats.tomb.finance/api/ds/query',
                                    json=params, headers=headers) as resp:
                print(await  resp.text())
                response = await resp.json()
            if response["results"][str(QueryNames[1])]:
                queryName = response["results"][str(QueryNames[1])]["frames"][0]['schema']['fields'][1]['name']
                date = response["results"][str(QueryNames[1])]["frames"][0]['data']['values'][0]
                value = response["results"][str(QueryNames[1])]["frames"][0]['data']['values'][1]
                if queryName in statsData:
                    queryName = '_1'
                if str(QueryNames[1]) == '"A"':
                    date = date[-1]
                    value = value[-1]

            statsData.update({queryName: {"Price": value, "Date": date}})
    return await chartBuilberV2(statsData[queryName])


async def getLimitOrders():
    payload = r'{"query":"\n  query getOpenOrdersByOwner($owner: String) {\n    orders(\n      first: 1000\n      orderBy: updatedAtBlock\n      orderDirection: desc\n      where: { owner: $owner, status: open }\n    ) {\n      id\n      owner\n      inputToken\n      outputToken\n      minReturn\n      module\n      witness\n      secret\n      inputAmount\n      vault\n      bought\n      auxData\n      status\n      createdTxHash\n      executedTxHash\n      cancelledTxHash\n      blockNumber\n      createdAt\n      updatedAt\n      updatedAtBlock\n      updatedAtBlockHash\n      data\n      inputData\n    }\n  }\n","variables":{"owner":"0x92680a05add17217927d96d9eb59701a19feb898"}}'
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.thegraph.com/subgraphs/name/gelatodigital/limit-orders-fantom-ii',
                                data=payload) as resp:
            response = await resp.json()

            return response['data']['orders']


async def fetchLimitOrders():
    sortedLimitOrders = {"BUY": {}, "SELL": {}}
    limitOrders = await getLimitOrders()
    for order in limitOrders:
        if order['inputToken'] == '0x6c021ae822bea943b2e66552bde1d2696a53fbb7':
            inputAmount = w3.fromWei(order['inputAmount'], 'ether')
            minReturn = w3.fromWei(order['minReturn'], 'ether')
            limitPrice = inputAmount / minReturn


async def chartBuilberV1(chatData):
    eastern = pytz.timezone('US/Eastern')
    df: DataFrame = pd.DataFrame.from_dict(chatData).fillna(method="backfill")
    df['Date'] = pd.to_datetime(df['Date'], unit='ms').dt.tz_localize('UTC').dt.tz_convert(eastern)
    x = df['Date']
    y = df['Price']
    layout = Layout(
        autosize=True,
        width=1980,
        height=1080,
        margin=dict(l=10, r=10, t=80, b=10),
        title="<b>TOMB PEG</b>",
        paper_bgcolor='rgb(0.03,0.00,0.07)',
        plot_bgcolor='rgb(0.03,0.00,0.07)',
        yaxis_tickformat=".3f",
        title_x=0.5,
        font=dict(
            family="Amarante,cursive",
            size=25,
            color="White")
    )

    fig = go.Figure([
        go.Scatter(x=x, y=1.01 * np.ones_like(y), opacity=0.5, line_width=0, showlegend=False),
        go.Scatter(x=x, y=y, fill='tonexty', fillcolor="#240050", line=dict(color="#940099"), line_shape='spline',
                   opacity=0, showlegend=False)
    ], layout=layout)
    fig.show()


async def chartBuilberV2(chatData):
    limits = [1, 1.01]
    eastern = pytz.timezone('US/Eastern')

    df: DataFrame = pd.DataFrame.from_dict(chatData).fillna(method="backfill")

    x = df['Date']
    y = df['Price']

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
        margin=dict(l=20, r=140, t=80, b=10),
        title="<b>TOMB PEG</b>",
        paper_bgcolor='rgb(0.03,0.00,0.07)',
        plot_bgcolor='rgb(0.03,0.00,0.07)',
        yaxis_tickformat=".3f",
        title_x=0.5,
        font=dict(
            family="Amarante,cursive",
            size=25,
            color="White")
    )
    limitOrders = await getLimitOrders()

    fig = go.Figure([
        go.Scatter(x=x, y=limits[1] * np.ones_like(x), opacity=1, line_width=1, line=dict(color="#d6d011"),
                   showlegend=False),

        go.Scatter(x=x_mod, y=y1, fill="tonexty", fillcolor='rgba(0,150,0,0.5)',
                   mode='none', opacity=0.5, showlegend=False),

        go.Scatter(x=x, y=limits[0] * np.ones_like(x), opacity=1, line_width=1, line=dict(color="#d6d011"),
                   showlegend=False),

        go.Scatter(x=x_mod, y=y2, fill="tonexty", fillcolor='rgba(106,64,153,0.5)',
                   mode='none', opacity=0.5, showlegend=False),

        go.Scatter(x=x, y=limits[0] * np.ones_like(x), opacity=1, line_width=1,
                   showlegend=False),

        go.Scatter(x=x_mod, y=y3, fill="tonexty", fillcolor='rgba(47, 32, 54,0.8)',
                   mode='none', opacity=0.5, showlegend=False),

    ], layout=layout)

    img = Image.open('../background images/TOMB.jpg')  # image path
    # defined to source
    fig.add_layout_image(
        dict(
            source=img,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=1.3, sizey=1.2,
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
    fig.write_image("tomb_chart_data.png")
    data = {'buy': BUY, 'sell': SELL}
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
