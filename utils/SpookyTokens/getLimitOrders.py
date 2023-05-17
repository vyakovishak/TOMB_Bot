import asyncio
import json
import numpy as np
import aiohttp
from web3.auto import w3

from utils.TOMB.tombAPI import getPriceOfTombUSD

with open("tokensList.json", 'r') as f:
    tokensData = json.load(f)


class LimitOrders:
    def __init__(self, tokenAddress):
        self.outputToken = None
        self.tokenAddress = tokenAddress
        self.inputAmount = None
        self.outputAmount = None
        self.inputDecimal = None
        self.outputDecimal = None
        self.inputToken = None

    def getTokenDecimal(self):
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
            if str(token["address"]) == str(self.tokenAddress).lower():
                token_decimals = token["decimals"]
                return units.get(str(token_decimals))

    async def getTokenUSDprice(self):
        payload = r'{"query":"\n  query($tokenAddress: Bytes!) {\n    token(id: $tokenAddress) {\n      derivedETH\n      totalSupply\n      symbol\n    }\n    bundle(id: \"1\") {\n      ethPrice\n    }\n  }\n","variables":{"tokenAddress":"' + self.tokenAddress + '"}}'
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.thegraph.com/subgraphs/name/eerieeight/spookyswap',
                                    data=payload) as resp:
                response = await resp.json()
                ftmPrice = response['data']['bundle']['ethPrice']
                ftmTOMBprice = response['data']['token']['derivedETH']
                result = {"ftmPrice": ftmPrice,
                          "tokenPrice": float(ftmPrice) * float(ftmTOMBprice)}
                return result

    async def getLimitOrdersQuery(self):
        payload = r'{"query":"\n  query getOpenOrdersByOwner {\n    orders(\n      first: 1000\n      orderBy: inputAmount\n      orderDirection: desc\n      where: { status: open, inputToken: \"'+str(self.tokenAddress)+r'\"}\n    ) {\n         inputToken\n      outputToken\n      minReturn\n      inputAmount\n        }\n  }\n"}'
        print(payload)
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.thegraph.com/subgraphs/name/gelatodigital/limit-orders-fantom-ii',
                                    data=payload) as resp:
                print(await resp.text())
                inputLimit = await resp.json()

        payload = r'{"query":"\n  query getOpenOrdersByOwner {\n    orders(\n      first: 1000\n      orderBy: inputAmount\n      orderDirection: desc\n      where: { status: open, outputToken: \"' + self.tokenAddress + r'\"}\n    ) {\n         inputToken\n      outputToken\n      minReturn\n      inputAmount\n        }\n  }\n"}'
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

    def getExecutePrice(self):
        inAmount = float(w3.fromWei(int(self.inputAmount), self.inputDecimal))
        outAmount = float(w3.fromWei(int(self.outputAmount), self.outputDecimal))
        inputLimitPrice = inAmount / outAmount
        outputLimitPrice = outAmount / inAmount
        if self.inputToken != str(self.tokenAddress).lower():
            return "BUY", float(inputLimitPrice) // 0.01 / 100
        else:
            return "SELL", float(outputLimitPrice) // 0.01 / 100

    async def limitOrdersHandler(self):
        limitOrders = {"BUY": {}, "SELL": {}}

        inputData = await self.getLimitOrdersQuery()
        tokenPrice = await self.getTokenUSDprice()
        print(tokenPrice)
        for order in inputData:
            self.inputToken = order['inputToken']
            self.outputToken = order['outputToken']
            self.inputAmount = order['inputAmount']
            self.outputAmount = order['minReturn']
            try:
                self.inputDecimal = self.getTokenDecimal()
                self.outputDecimal = self.getTokenDecimal()
                limitOrderStatus, LimitPrice = self.getExecutePrice()

                if 1.20 >= float(LimitPrice) >= 0.02:
                    LimitPrice = str(LimitPrice)
                    if limitOrderStatus == 'BUY':
                        if LimitPrice in limitOrders["BUY"]:
                            limitOrderVolume = limitOrders["BUY"][LimitPrice]
                            inputAmountValue = float(w3.fromWei(int(self.outputAmount), self.getTokenDecimal()))
                            newVolume = limitOrderVolume + inputAmountValue
                            newVolumeUSD = int(newVolume * tokenPrice["tokenPrice"])
                            if 100 < newVolumeUSD < 500000000:
                                limitOrders[limitOrderStatus][LimitPrice] = newVolumeUSD
                        else:
                            newVolume = float(w3.fromWei(int(self.outputAmount), self.getTokenDecimal()))
                            newVolumeUSD = int(newVolume * tokenPrice["tokenPrice"])
                            if 100 < newVolumeUSD < 500000000:
                                limitOrders[limitOrderStatus][LimitPrice] = newVolumeUSD
                    else:
                        if LimitPrice in limitOrders["SELL"]:
                            limitOrderVolume = limitOrders["SELL"][LimitPrice]
                            inputAmountValue = float(w3.fromWei(int(self.outputAmount), self.getTokenDecimal()))
                            newVolume = limitOrderVolume + inputAmountValue
                            newVolumeUSD = int(newVolume * tokenPrice["tokenPrice"])
                            if 100 < newVolumeUSD < 500000000:
                                limitOrders[limitOrderStatus][LimitPrice] = newVolumeUSD
                        else:
                            newVolume = float(w3.fromWei(int(self.outputAmount), self.getTokenDecimal()))
                            newVolumeUSD = int(newVolume * tokenPrice["tokenPrice"])
                            if 100 < newVolumeUSD < 500000000:
                                limitOrders[limitOrderStatus][LimitPrice] = newVolumeUSD

            except:
                print("Wrong decimals")

        return limitOrders
