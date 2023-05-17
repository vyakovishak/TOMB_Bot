import json
import time
from datetime import datetime

import aiohttp


async def getChart(tokenAddress=None, Day="12H", resolution="1H"):
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

    payload = f"?pair={str(tokenAddress)}" \
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
