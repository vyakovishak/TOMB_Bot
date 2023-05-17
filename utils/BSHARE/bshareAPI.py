import asyncio
import json
import calendar
from datetime import datetime, timedelta
import time
import aiohttp
from web3 import Web3
from web3.middleware import geth_poa_middleware

from utils.BSHARE.bshareQuerys import BSHARE, BSHARE_TOKEN_ABI, BSHARE_FTM_LP, BSHARE_FTM_LP_ABI, BSHARE_ACROPOLIS, \
    BSHARE_ACROPOLIS_ABI, BASED_TOKEN, BASED_TOKEN_ABI, BASED_FTM_LP, BASED_FTM_LP_ABI, BSHARE_TREASURY, \
    BSHARE_TREASURY_ABI

w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

Based_Contract = w3.eth.contract(BSHARE, abi=BSHARE_TOKEN_ABI)

BSHARE_FTM_Contract = w3.eth.contract(BSHARE_FTM_LP, abi=BSHARE_FTM_LP_ABI)

BSHARE_ACROPOLIS_Contract = w3.eth.contract(BSHARE_ACROPOLIS, abi=BSHARE_ACROPOLIS_ABI)

BASED_TOKEN_Contract = w3.eth.contract(BASED_TOKEN, abi=BASED_TOKEN_ABI)

BASED_FTM_LP_Contract = w3.eth.contract(BASED_FTM_LP, abi=BASED_FTM_LP_ABI)

BASED_FTM_LP_TREASURY = w3.eth.contract(BSHARE_TREASURY, abi=BSHARE_TREASURY_ABI)


# get current Epoch on staking
async def currentEpoch():
    return BSHARE_ACROPOLIS_Contract.functions.epoch().call()


# get next Epoch on staking
async def nextEpoch():
    return BSHARE_ACROPOLIS_Contract.functions.nextEpochPoint().call()


# get FTM price
async def getFTMprice():
    payload = r'{"query":"\n  query($tokenAddress: Bytes!) {\n    token(id: $tokenAddress) {\n      derivedETH\n      totalSupply\n      symbol\n    }\n    bundle(id: \"1\") {\n      ethPrice\n    }\n  }\n","variables":{"tokenAddress":""}}'
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.thegraph.com/subgraphs/name/eerieeight/spookyswap', data=payload) as resp:
            response = await resp.json()
            ftmPrice = float(response['data']['bundle']['ethPrice'])
            return ftmPrice


async def getScreener():
    async with aiohttp.ClientSession() as session:
        async with session.get(
                'https://api.dex.guru/v2/tokens/0x49C290Ff692149A4E16611c694fdED42C954ab7a-fantom/screener') as resp:
            response = await resp.json()

    return response


async def previousBasedUpdatedPrice():
    return BASED_FTM_LP_TREASURY.functions.previousEpochBasedPrice().call()


async def getBasedUpdatedPrice():
    return BASED_FTM_LP_TREASURY.functions.getBasedUpdatedPrice().call()


async def getPriceOfBasedUSD():
    payload = r'{"query":"\n  query($tokenAddress: Bytes!) {\n    token(id: $tokenAddress) {\n      derivedETH\n      totalSupply\n      symbol\n    }\n    bundle(id: \"1\") {\n      ethPrice\n    }\n  }\n","variables":{"tokenAddress":"0x49C290Ff692149A4E16611c694fdED42C954ab7a"}}'
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.thegraph.com/subgraphs/name/eerieeight/spookyswap', data=payload) as resp:
            response = await resp.json()
            print(response)
            ftmPrice = response['data']['bundle']['ethPrice']
            ftmTOMBprice = response['data']['token']['derivedETH']
            result = {"ftmPrice": ftmPrice,
                      "BASEDprice": float(ftmPrice) * float(ftmTOMBprice)}
            return result


async def bPEG_Calculator(peg=1.0111):
    token01 = BASED_FTM_LP_Contract.functions.getReserves().call()
    previousTWAP = float(w3.fromWei(await previousBasedUpdatedPrice(), 'ether'))
    currentTWAP = float(w3.fromWei(await getBasedUpdatedPrice(), 'ether'))
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
    percentPsuh = z * 100
    guruScreener = await getScreener()

    pegData = {
        "Current Peg": wtfmTotal / tombTotal,
        "Target PEG": ftmToGetPeg / tombTotal,
        "Current TWAP": currentTWAP,
        "Previous": previousTWAP,
        "FTM Need": ftmNeed,
        "FTM in USD": ftmNeed * ftmUSDprice,
        "Percent": percentPsuh,
        "Next Epoch": nextEpochInHMS,
        "TOMB": tombTotal,
        "TOMB/FTM": wtfmTotal,
        "FISH": str("{:.3f}".format(guruScreener["casual"] - 50)),
        "DOLPHINE": str("{:.3f}".format(guruScreener["medium"] - 50)),
        "WHALES": str("{:.3f}".format(guruScreener["heavy"] - 50)),
    }
    return pegData
