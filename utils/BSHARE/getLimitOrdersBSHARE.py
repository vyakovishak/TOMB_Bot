import asyncio
import json
import numpy as np
import aiohttp
from web3.auto import w3

from utils.BSHARE.bshareAPI import getPriceOfBasedUSD
from utils.TOMB.tombAPI import getPriceOfTombUSD

with open("tokensList.json", 'r') as f:
    tokensData = json.load(f)


def getTokenDecimal(tokenAddress):
    units = {
        "1": "wei",
        "2": "wei2",
        "3": "kwei",
        "6": "mwei",
        "8": "gwei8",
        "9": "gwei",
        "12": "szabo",
        "15": "finney",
        "18": "ether",
        "21": "kether",
        "24": "mether",
        "27": "gether",
        "30": "tether",
    }
    for token in tokensData["tokens"]:
        if str(token["address"]) == str(tokenAddress).lower():
            token_decimals = token["decimals"]
            return units.get(str(token_decimals))


async def getLimitOrders():
    payload = r'{"query":"\n  query getOpenOrdersByOwner {\n    orders(\n      first: 1000\n      orderBy: inputAmount\n      orderDirection: desc\n      where: { status: open, inputToken: \"0x49C290Ff692149A4E16611c694fdED42C954ab7a\"}\n    ) {\n         inputToken\n      outputToken\n      minReturn\n      inputAmount\n        }\n  }\n"}'
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.thegraph.com/subgraphs/name/gelatodigital/limit-orders-fantom-ii',
                                data=payload) as resp:
            inputLimit = await resp.json()

    payload = r'{"query":"\n  query getOpenOrdersByOwner {\n    orders(\n      first: 1000\n      orderBy: inputAmount\n      orderDirection: desc\n      where: { status: open, outputToken: \"0x49C290Ff692149A4E16611c694fdED42C954ab7a\"}\n    ) {\n         inputToken\n      outputToken\n      minReturn\n      inputAmount\n        }\n  }\n"}'
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.thegraph.com/subgraphs/name/gelatodigital/limit-orders-fantom-ii',
                                data=payload) as resp:
            outputLimit = await resp.json()
    inputLimit = inputLimit["data"]
    outputLimit = outputLimit["data"]
    ds = [inputLimit, outputLimit]
    d = {}
    for k in inputLimit.keys():
        d[k] = np.concatenate(list(d[k] for d in ds))
    return d["orders"]


def getExecutePrice(inputAmount, inputDecimals, outputAmount, outputDecimals, inputToken):
    inAmount = float(w3.fromWei(int(inputAmount), inputDecimals))
    outAmount = float(w3.fromWei(int(outputAmount), outputDecimals))
    inputLimitPrice = inAmount / outAmount
    outputLimitPrice = outAmount / inAmount
    if inputToken != '0x49C290Ff692149A4E16611c694fdED42C954ab7a'.lower():
        return "BUY", float(inputLimitPrice) // 0.01 / 100
    else:
        return "SELL", float(outputLimitPrice) // 0.01 / 100


async def limitOrdersHandler():
    limitOrders = {"BUY": {}, "SELL": {}}
    limitOrdersData = await getLimitOrders()
    basedPrice = await getPriceOfBasedUSD()
    for order in limitOrdersData:
        inputToken = order['inputToken']
        outputToken = order['outputToken']
        inputAmount = order['inputAmount']
        minReturn = order['minReturn']
        try:
            inputTokenDecimal = getTokenDecimal(inputToken)
            outputTokenDecimal = getTokenDecimal(outputToken)
            limitOrderStatus, LimitPrice = getExecutePrice(inputAmount,
                                                           inputTokenDecimal,
                                                           minReturn,
                                                           outputTokenDecimal,
                                                           inputToken)

            if 1.20 >= float(LimitPrice) >= 0.02:
                LimitPrice = str(LimitPrice)
                if limitOrderStatus == 'BUY':
                    if LimitPrice in limitOrders["BUY"]:
                        limitOrderVolume = limitOrders["BUY"][LimitPrice]
                        inputAmountValue = float(w3.fromWei(int(minReturn), getTokenDecimal(inputToken)))
                        newVolume = limitOrderVolume + inputAmountValue
                        newVolumeUSD = int(newVolume * basedPrice["BASEDprice"])
                        if 100 < newVolumeUSD < 500000000:
                            limitOrders[limitOrderStatus][LimitPrice] = newVolumeUSD
                    else:
                        newVolume = float(w3.fromWei(int(minReturn), getTokenDecimal(inputToken)))
                        newVolumeUSD = int(newVolume * basedPrice["BASEDprice"])
                        if 100 < newVolumeUSD < 500000000:
                            limitOrders[limitOrderStatus][LimitPrice] = newVolumeUSD
                else:
                    if LimitPrice in limitOrders["SELL"]:
                        limitOrderVolume = limitOrders["SELL"][LimitPrice]
                        inputAmountValue = float(w3.fromWei(int(inputAmount), getTokenDecimal(inputToken)))
                        newVolume = limitOrderVolume + inputAmountValue
                        newVolumeUSD = int(newVolume * basedPrice["BASEDprice"])
                        if 100 < newVolumeUSD < 500000000:
                            limitOrders[limitOrderStatus][LimitPrice] = newVolumeUSD
                    else:
                        newVolume = float(w3.fromWei(int(inputAmount), getTokenDecimal(inputToken)))
                        newVolumeUSD = int(newVolume * basedPrice["BASEDprice"])
                        if 100 < newVolumeUSD < 500000000:
                            limitOrders[limitOrderStatus][LimitPrice] = newVolumeUSD

        except:
            print("Wrong decimals")

    return limitOrders
