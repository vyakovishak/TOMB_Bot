import asyncio
import json
import calendar
from datetime import datetime, timedelta
import time

import mpf as mpf
from pandas import DataFrame
from pycoingecko import CoinGeckoAPI
import pandas as pd
from .tombQuerys import treasuryABI, masonryABI, tbondToken, tombABI, tshareRewardPoolABI, tshareABI, \
    TombGenesisRewardPool, tombOracle, TombRewardPool, tombFTM_LP_ABI, wftmABI, TOMB_WFTM_LP, TOMB, WFTM, \
    UniswapPairABI, erc20TokenABI, TombPriceInFTMchart
import aiohttp
from web3 import Web3
from web3.middleware import geth_poa_middleware

w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
cg = CoinGeckoAPI()

tombContract = w3.eth.contract(TOMB, abi=tombABI)

wftmContract = w3.eth.contract(WFTM, abi=wftmABI)

treasuryContract = w3.eth.contract("0xF50c6dAAAEC271B56FCddFBC38F0b56cA45E6f0d", abi=treasuryABI)

masonryContract = w3.eth.contract("0x8764DE60236C5843D9faEB1B638fbCE962773B67", abi=masonryABI)

tbondToken = w3.eth.contract("0x24248CD1747348bDC971a5395f4b3cd7feE94ea0", abi=tbondToken)

genesisRewardsPoolContract = w3.eth.contract("0x9A896d3c54D7e45B558BD5fFf26bF1E8C031F93b", abi=TombGenesisRewardPool)

oracleContract = w3.eth.contract("0x55530fA1B042582D5FA3C313a7e02d21Af6B82f4", abi=tombOracle)

tombRewardPool = w3.eth.contract("0xa7b9123f4b15fE0fF01F469ff5Eab2b41296dC0E", abi=TombRewardPool)

tombToken = w3.eth.contract("0x6c021Ae822BEa943b2E66552bDe1D2696a53fbB7", abi=tombABI)

tshareRewardsPool = w3.eth.contract("0xcc0a87F7e7c693042a9Cc703661F5060c80ACb43", abi=tshareRewardPoolABI)

tshareToken = w3.eth.contract("0x4cdF39285D7Ca8eB3f090fDA0C069ba5F4145B37", abi=tshareABI)

uniswapLP = w3.eth.contract("0x2A651563C9d3Af67aE0388a5c8F89b867038089e", abi=UniswapPairABI)

TOMB_FTM_LP = w3.eth.contract(TOMB_WFTM_LP, abi=tombFTM_LP_ABI)


async def requestCall(dateType=None):
    if dateType is None:
        rangeFrom = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        date = datetime.strptime(rangeFrom, "%Y-%m-%dT%H:%M:%S.%fZ")
        timestampFrom = int(datetime.timestamp(date) * 1000)
        rawFrom = "now-24h"
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
    QueryList = [TombPriceInFTMchart]
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
                response = await resp.json()
            if response["results"][str(QueryNames[1])]:

                queryName = response["results"][str(QueryNames[1])]["frames"][0]['schema']['fields'][1]['name']
                print(queryName)
                date = response["results"][str(QueryNames[1])]["frames"][0]['data']['values'][0]
                value = response["results"][str(QueryNames[1])]["frames"][0]['data']['values'][1]
                if (queryName) in statsData:
                    queryName = '_1'

                if str(QueryNames[1]) == '"A"':
                    date = date[-1]
                    value = value[-1]

            statsData.update({queryName: {"Value": value, "Date": date}})

    return statsData



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
    else:
        date = (datetime.now() - timedelta(hours=24))
    return dateType, date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


# ------------------------------------------------------------------------------------------------------------------------------------------------------

async def latestSnapshotIndex():
    return masonryContract.functions.latestSnapshotIndex().call()


# get rewardReceived
async def masonryHistory():
    return w3.fromWei(masonryContract.functions.masonryHistory(await latestSnapshotIndex()).call()[1], 'ether')


# get current TOMB price
async def getTombPrice():
    return w3.fromWei(masonryContract.functions.getTombPrice().call(), 'ether')


# get FTM price
async def getFTMprice():
    payload = r'{"query":"\n  query($tokenAddress: Bytes!) {\n    token(id: $tokenAddress) {\n      derivedETH\n      totalSupply\n      symbol\n    }\n    bundle(id: \"1\") {\n      ethPrice\n    }\n  }\n","variables":{"tokenAddress":""}}'
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.thegraph.com/subgraphs/name/eerieeight/spookyswap', data=payload) as resp:
            response = await resp.json()
            ftmPrice = float(response['data']['bundle']['ethPrice'])
            return ftmPrice


"""
Get Masonry Data
"""


# Get TWAP TOMB Price
async def getTombUpdatedPrice():
    return float(w3.fromWei(treasuryContract.functions.getTombUpdatedPrice().call(), 'ether'))


# Get previous TWAP TOMB Price
async def previousTombUpdatedPrice():
    return float(w3.fromWei(treasuryContract.functions.previousEpochTombPrice().call(), 'ether'))


# get current TOMB reward form TSHARE staking
async def tombEarned(wallet):
    return w3.fromWei(masonryContract.functions.earned(Web3.toChecksumAddress(wallet)).call(), 'ether')


# get current Staked TSHARE
async def stakedTSHARE():
    return float(w3.fromWei(masonryContract.functions.totalSupply().call(), 'ether'))


# get price of TSHARE/FTM in USD/FTM
async def getTSHAREprice():
    payload = r'{"query":"\n  query($tokenAddress: Bytes!) {\n    token(id: $tokenAddress) {\n      derivedETH\n      totalSupply\n      symbol\n    }\n    bundle(id: \"1\") {\n      ethPrice\n    }\n  }\n","variables":{"tokenAddress":"0x4cdf39285d7ca8eb3f090fda0c069ba5f4145b37"}}'
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.thegraph.com/subgraphs/name/eerieeight/spookyswap', data=payload) as resp:
            response = await resp.json()
            ftmPrice = response['data']['bundle']['ethPrice']
            ftmTSHAREprice = response['data']['token']['derivedETH']
            result = {'ftmTSHAREprice': float(ftmTSHAREprice),
                      'tshareUSD': float(ftmPrice) * float(ftmTSHAREprice)}

            return result


# Masonry TSHARE APR
async def getMasonryAPR():
    tsharePrice = await getTSHAREprice()  # Get price in USD/FTM
    ftmPrice = await getFTMprice()  # Get FTM price in USD
    usdTSHARE = tsharePrice['tshareUSD']  # Get TSHARE price in USD
    staked = await stakedTSHARE()  # Get total staked TSHARES IN Masonry
    stakedInUSD = float(usdTSHARE) * float(staked)
    tombFTM = await getTombUpdatedPrice()  # Get TOMB price in FTM
    reward = await masonryHistory()  # Get latest snapshot index
    APR = 100 * (float((float(reward)) * float(ftmPrice) * float(tombFTM) * 4) / stakedInUSD * 365)
    return APR


# get current Epoch on staking
async def currentEpoch():
    return masonryContract.functions.epoch().call()


# get next Epoch on staking
async def nextEpoch():
    return masonryContract.functions.nextEpochPoint().call()


# check user TSHARE balance
async def stakedTshareBalance(wallet):
    return w3.fromWei(masonryContract.functions.balanceOf(Web3.toChecksumAddress(wallet)).call(), 'ether')


# check if possible to clan TOMB reward from staking TSHARE
async def canClaimTombReward(wallet):
    return masonryContract.functions.canClaimReward(Web3.toChecksumAddress(wallet)).call()


# check if possible to withdraw TSHARE from staking
async def canWithdrawTshare(wallet):
    return masonryContract.functions.canWithdraw(Web3.toChecksumAddress(wallet)).call()


"""
End of Masonry Data
"""

"""
Get Cemetery Data
"""


# get current Staked TOMB-FTM
async def totalSupplyTOMB_FTM():
    return float(w3.fromWei(TOMB_FTM_LP.functions.totalSupply().call(), 'ether'))


# Get circulating supply of TOMB in TOMB-FTM
async def getValueOfTOMB_in_TOMB_WFTM_LP():
    return float(w3.fromWei(tombContract.functions.balanceOf(TOMB_WFTM_LP).call(), 'ether'))


# Get circulating supply of WFTM in TOMB-FTM
async def getValueOfWFTM_in_TOMB_WFTM_LP():
    return float(w3.fromWei(wftmContract.functions.balanceOf(TOMB_WFTM_LP).call(), 'ether'))


#
async def getBondReemableBonds():
    return float(w3.fromWei(treasuryContract.functions.getRedeemableBonds().call(), 'ether'))


# get price of TOMB/FTM in USD/FTM
async def getPriceOfTombUSD():
    payload = r'{"query":"\n  query($tokenAddress: Bytes!) {\n    token(id: $tokenAddress) {\n      derivedETH\n      totalSupply\n      symbol\n    }\n    bundle(id: \"1\") {\n      ethPrice\n    }\n  }\n","variables":{"tokenAddress":"0x6c021ae822bea943b2e66552bde1d2696a53fbb7"}}'
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.thegraph.com/subgraphs/name/eerieeight/spookyswap', data=payload) as resp:
            response = await resp.json()
            ftmPrice = response['data']['bundle']['ethPrice']
            ftmTOMBprice = response['data']['token']['derivedETH']
            result = {"ftmPrice": ftmPrice,
                      "TOMBprice": float(ftmPrice) * float(ftmTOMBprice)}
            return result


"""
End of Cemetery Data
"""

# ******************************************************

"""
Get Current Supply of TSHARE, TOMB
"""


# Get current supply of TSHARE
async def getTSHAREcurrentSupply():
    totalSupply = await getTSHAREtotalSupply()
    tshareRewardSpoolBalance = w3.fromWei(
        tshareToken.functions.balanceOf('0xcc0a87F7e7c693042a9Cc703661F5060c80ACb43').call(), 'ether')
    return float(totalSupply) - float(tshareRewardSpoolBalance)


# Current Supply of TOMB
async def getTOMBcurrentSupply():
    tombRewardSpoolBalance = w3.fromWei(
        tombToken.functions.balanceOf('0xcc0a87F7e7c693042a9Cc703661F5060c80ACb43').call(), 'ether')
    totalSupply = await getTOMBtotalSupply()
    print(totalSupply)
    print(tombRewardSpoolBalance)
    currentSupply = float(totalSupply) - float(tombRewardSpoolBalance)
    tombSupply = {"totalSupply": float(totalSupply),
                  "currentSupply": float(currentSupply)}
    return tombSupply


"""
End of Current Supply
"""

# ******************************************************

"""
Get Total Supply of TSHARE,TOMB, TBOND 
"""


# Total supply of TSHARE
async def getTSHAREtotalSupply():
    return w3.fromWei(tshareToken.functions.totalSupply().call(), 'ether')


# Total supply of TOMB
async def getTOMBtotalSupply():
    return w3.fromWei(tombToken.functions.totalSupply().call(), 'ether')


# Total supply of TBOND
async def getTBONDtotalSupply():
    return w3.fromWei(tbondToken.functions.totalSupply().call(), 'ether')


async def getTBONDpremiumRate():
    tond = w3.fromWei(tbondToken.functions.getBondpremiumRate().call(), 'ether')
    tonbAvalibale = 1 if tond == 0 else tond
    return tonbAvalibale


async def getTBONDPrice():
    tond = w3.fromWei(tbondToken.functions.tombPriceOne().call(), 'ether')
    ftmTBOND = tond * getFTMprice()
    data = {"TBOND": tond,
            "usdTBOND": ftmTBOND}
    return data


"""
End of Total Supply
"""

# ******************************************************

"""
Get Market Cap of TSHARE,TOMB, TBOND 

"""


# Mc of Tomb
async def tombMarketCap():
    currentSupply = await getTOMBcurrentSupply()
    ftmPrice = await getFTMprice()
    return ftmPrice * currentSupply["currentSupply"]


# MC of TSHARE
async def tshareMarketCap():
    currentSupply = await getTSHAREcurrentSupply()
    tshareUSD = await getTSHAREprice()
    return currentSupply * tshareUSD['tshareUSD']


# Mc of TBOND
async def tbondMarketCap():
    currentSupply = await getTBONDtotalSupply()
    ftmPrice = await getFTMprice()
    return ftmPrice * currentSupply


"""
End of Market Cap
"""

"""
Get Balance of TSHARE,TOMB, TBOND 

"""


async def tombBalanceOf(wallet):
    return w3.fromWei(tombContract.functions.balanceOf(Web3.toChecksumAddress(wallet)).call(), 'ether')


async def tshareBalanceOf(wallet):
    return w3.fromWei(tshareToken.functions.balanceOf(Web3.toChecksumAddress(wallet)).call(), 'ether')


async def tbondBalanceOf(wallet):
    return w3.fromWei(tbondToken.functions.balanceOf(Web3.toChecksumAddress(wallet)).call(), 'ether')


"""
End of Market Cap
"""


async def getHeart(heart, amount):
    x = int(float(amount) / 1000)
    heartStatus = f'{heart}'
    for y in range(x):
        heartStatus += heart
    return heartStatus


async def getDate(timestamp):
    return datetime.fromtimestamp(timestamp)


async def getChart(tokenName=None, tokenAddress=None, Day="12H", resolution="4H"):
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

    payload = f"?pair={tokenAddress}" \
              f"&position=1" \
              f"&resolution={str(resolution)}" \
              f"&window={str(window)}" \
              f"&from=0" \
              f"&to={str(int(time.mktime(datetime.today().timetuple()) - DayNum))}" \
              f"&limit=545" \
              f"&denomination=native"

    headers = {
        'Host': 'kekapi.keks.app',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36',
        'Sec-GPC': '1',
        'Origin': 'https://kek.tools',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://kek.tools/',
        'Accept-Language': 'en-US,en;q=0.9',
        'If-None-Match': 'W/"85-67Gju/qsfyC1/dCrpovgAHGvomI"',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('https://kekapi.keks.app/v1/m/ftm/candles' + payload, headers=headers) as resp:
            response = await resp.json()

        response = str(response['data']).replace('', '') \
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

    return await chartBuilber(jsonTradingData, tokenName, window, resolution, Day)


async def chartBuilber(chatData, tokenName, window, resolution, Day):
    df: DataFrame = pd.DataFrame.from_dict(chatData).fillna(method="backfill")
    df['Date'] = pd.to_datetime(df['Date'], unit='ns')
    df.index = pd.DatetimeIndex(df['Date'])

    # Creating Style
    market_colors = mpf.make_marketcolors(
        base_mpf_style="charles"
    )
    rc = {
        "axes.labelcolor": "none",
        "axes.spines.bottom": True,
        "axes.spines.left": False,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "font.size": 10,
    }
    styles = mpf.make_mpf_style(
        base_mpf_style="nightclouds",
        marketcolors=market_colors,
        gridstyle="",
        rc=rc
    )

    filledShape = {
        "y1": df['Close'].values,
        "facecolor": "#2279e4"
    }

    fg1, _ = mpf.plot(df, type='candle',
                      title=f'\n{tokenName}\n Date Range: {Day} days Resolution: {window} {resolution}',
                      ylabel='Price(FTM)',
                      ylabel_lower='Volume',
                      linecolor='white',
                      style=styles,
                      volume=True,
                      figsize=(12, 8),
                      figscale=1.5,
                      scale_padding={'left': 0.3, 'top': 0.5, 'right': 0.3, 'bottom': 0.5},
                      returnfig=True,
                      datetime_format='%b %d')

    fg1.savefig(f'chart{tokenName}.jpg', dpi=500)
    return True


def getTokenSymbol(address):
    contract = w3.eth.contract(address=address, abi=erc20TokenABI)
    return contract.functions.symbol().call()


"""
Transaction Handles
"""

"""
END of Transaction Handles
"""

"""
PEG Calculator
"""


async def PEG_Calculator(peg=1.0111):
    #txs = await getLastTrx()
    #marketScreener = await MarketScreener(txs)
    # txsSortedByDate = await sortByDate(txs)
    # past = datetime.now() - timedelta(minutes=30)
    # biggetTXin30m = []
    #
    # for tx in txsSortedByDate:
    #     if datetime(past) < tx['Date']:
    #         biggetTXin30m.append(tx)
    #
    # sortedTXin30m = await sortByDate(biggetTXin30m)

    token01 = TOMB_FTM_LP.functions.getReserves().call()
    previousTWAP = await previousTombUpdatedPrice()
    currentTWAP = await getTombUpdatedPrice()
    wtfmTotal = float(w3.fromWei(token01[0], 'ether'))
    tombTotal = float(w3.fromWei(token01[1], 'ether'))
    ftmToGetPeg = float(tombTotal * peg)
    ftmNeed = ftmToGetPeg - wtfmTotal
    ftmUSDprice = await getFTMprice()
    nextEpochB = await nextEpoch()
    nextEpochInHMS = datetime.fromtimestamp(nextEpochB) - datetime.fromtimestamp(int(calendar.timegm(time.gmtime())))

    x = ftmToGetPeg - wtfmTotal  # V1 - V2 #NEED IT - CURRENT
    y = ftmToGetPeg + wtfmTotal  # V1 + V2 #NEED IT + CURRENT
    e = y / 2  # (V1 + V2)/2
    z = x / e
    percentPush = z * 100

    guruScreener = await getScreener()
    print("HERE: "+ str("{:.3f}".format(guruScreener["casual"]-50)))
    pegData = {
        "Current Peg": wtfmTotal / tombTotal,
        "Target PEG": ftmToGetPeg / tombTotal,
        "Current TWAP": currentTWAP,
        "Previous": previousTWAP,
        "FTM Need": ftmNeed,
        "FTM in USD": ftmNeed * ftmUSDprice,
        "Percent": percentPush,
        "Next Epoch": nextEpochInHMS,
        "TOMB": tombTotal,
        "TOMB/FTM": wtfmTotal,
        "FISH": str("{:.3f}".format(guruScreener["casual"]-50)),
        "DOLPHINE": str("{:.3f}".format(guruScreener["medium"]-50)),
        "WHALES": str("{:.3f}".format(guruScreener["heavy"]-50)),
    }
    return pegData


"""
END of PEG Calculator
"""


async def sortByDate(txs):
    return sorted(txs, key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d %H:%M:%S'))


async def MarketScreener(txs):
    fishBUY = 0
    fishSELL = 0
    delphineBUY = 0
    delphineSELL = 0
    whalesBUY = 0
    whalesSELL = 0
    for tx in txs:
        if tx['Trade Status'] == 'BUY':

            if 10000.0 <= float(tx['Amount USD']) <= 49999.0:
                fishBUY = fishBUY + 1
            elif 50000.0 <= float(tx['Amount USD']) <= 99999.0:
                print('50000')
                delphineBUY = delphineBUY + 1
            elif float(tx['Amount USD']) >= 100000:
                whalesBUY = whalesBUY + 1
        else:
            if 5000.0 <= float(tx['Amount USD']) <= 10000.0:
                fishSELL = fishSELL + 1
            elif 50000.0 <= float(tx['Amount USD']) <= 99999.0:
                delphineSELL = delphineSELL + 1
            elif float(tx['Amount USD']) >= 100000:
                whalesSELL = whalesSELL + 1

    marketData = {"fish": {"BUY": fishBUY,
                           "SELL": fishSELL},
                  "delphine": {"BUY": delphineBUY,
                               "SELL": delphineSELL},
                  "whale": {"BUY": whalesBUY,
                            "SELL": whalesSELL},
                  }
    return marketData


async def getScreener():
    async with aiohttp.ClientSession() as session:
        async with session.get(
                'https://api.dex.guru/v2/tokens/0x6c021ae822bea943b2e66552bde1d2696a53fbb7-fantom/screener') as resp:
            response = await resp.json()

    return response


async def getLastTrx():
    _30Dats = str(int(datetime.timestamp(datetime.today() - timedelta(days=45))))
    print(_30Dats)
    payload = '{"query": "query ($allPairs: Bytes!, $toNot: [String]!) {\\n  swaps(\\n first: 1000\\n   orderBy: ' \
              'timestamp\\n    orderDirection: desc\\n    where:{pair: $allPairs, pair_not_in: $toNot, to_not_in: ' \
              '$toNot, sender_not_in: $toNot, from_not_in: $toNot, amountUSD_gte: 15000}\\n      ) {\\n    ' \
              'timestamp\\n    sender\\n    from\\n    amount0In\\n    amount1In\\n    amount0Out\\n    amount1Out\\n ' \
              '   amountUSD\\n    transaction {\\n      id\\n      blockNumber\\n    }\\n  }\\n}","variables": {' \
              '"allPairs": "0x2a651563c9d3af67ae0388a5c8f89b867038089e","toNot": [' \
              '"0x8e63054f7d04686f9922b5071f841bf8792ebc74", "0xa7d39ad541fec0407d2829c14d6fb02f749bbbcd", ' \
              '"0x7675c53e00a898f92f26b339fcdeea325d97aacf", "0x995e502ba378d855925a238606c6df63e471e419", ' \
              '"0x5364a521a6052842450b1ea60d981608cb6b0b88", "0xe841cd70e83ddee17f5432e06b12b77914fff4b8",' \
              '"0x256410f7b8951c879111dba3efa756ad1f2b402e", "0x68f598280a843a5ce07c1b9fb0d3af00cd085c31", ' \
              '"0x5364a521a6052842450b1ea60d981608cb6b0b88", "0xd0ad79e5acc51afdf4693d8304f40a1a221abe9e", ' \
              '"0xeb43cae19c8914b174c3680e6d5c1cf138ef04eb", "0xf491e7b69e4244ad4002bc14e878a34207e38c29", ' \
              '"0xc439220b52abf7641348896950d5a69511c18243","0x58a91472ae3d618c268db417faa391075ac8f969", ' \
              '"0x8afc0f9bdc5dca9f0408df03a03520bfa98a15af","0xc439220b52abf7641348896950d5a69511c18243"]}} '
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.thegraph.com/subgraphs/name/eerieeight/spookyswap', data=payload) as resp:
            response = await resp.json()
    tradeResult = []

    for trx in response["data"]["swaps"]:
        print(trx)
        if float(trx['amount0In']) > 0.0:
            tradeStatus = 'SELL'
            amountFTM = [trx['amount0In'], ' FTM']
            amountTOMB = [trx['amount1Out'], ' TOMB']

        else:
            tradeStatus = 'BUY'
            amountFTM = [trx['amount0Out'], ' FTM']
            amountTOMB = [trx['amount1In'], ' TOMB']

        usdAmount = trx['amountUSD']
        fromUser = trx['from']
        trxID = trx['transaction']['id']
        date = await getDate(int(trx['timestamp']))

        tradeResult.append({'Trade Status': f'{tradeStatus}',
                            'FTM': f'{"{:.3f}".format(float(amountFTM[0]))}',
                            'TOMB': f'{"{:.3f}".format(float(amountTOMB[0]))}',
                            'Amount USD': f'{"{:.3f}".format(float(usdAmount))}',
                            'From': f'{fromUser}',
                            'Date': f'{date}',
                            'Transaction ID': f'https://ftmscan.com/tx/{trxID}'
                            })

    return tradeResult
