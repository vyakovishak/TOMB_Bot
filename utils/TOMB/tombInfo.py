import calendar

import aiohttp

from . import tombAPI
from datetime import datetime
import time


# Get Masonry Data
async def masonryData(wallet=None):
    epoch = await tombAPI.currentEpoch()
    nextEpoch = await tombAPI.nextEpoch()
    nextEpochInHMS = datetime.fromtimestamp(nextEpoch) - datetime.fromtimestamp(int(calendar.timegm(time.gmtime())))
    WTOMB = await tombAPI.getTombUpdatedPrice()
    totalTshareStaked = await tombAPI.stakedTSHARE()
    tshareAPR = await tombAPI.getMasonryAPR()

    if wallet is not None:
        tombEarned = await tombAPI.tombEarned(wallet)
        userStaked = await tombAPI.stakedTshareBalance(wallet)
        canWithdrawTshare = await tombAPI.canWithdrawTshare(wallet)
        canClaimTombReward = await tombAPI.canClaimTombReward(wallet)
        tsharePrice = await tombAPI.getTSHAREprice()
        tombPrice = await tombAPI.getFTMprice()
        data = {
            "Current Epoch": epoch,
            "Next Epoch": str(nextEpochInHMS),
            "WTOMB": "{:.3f}".format(float(WTOMB)),
            "APR": "{:.2f}".format(float(tshareAPR)),
            "Total Staked": str(totalTshareStaked),
            "Tomb Earned": "{:.2f}".format(float(tombEarned)) + " = $" + "{:.2f}".format(
                float((float(tombPrice) * float(tombEarned)))),
            "TSHARE Staked": "{:.2f}".format(float(userStaked)) + " = $" + "{:.2f}".format(
                float(tsharePrice['tshareUSD'] * float(userStaked))),
            "Can be withdraw?": canWithdrawTshare,
            "Can reward be claim?": canClaimTombReward
        }

    else:
        data = {
            "Current Epoch": epoch,
            "Next Epoch": str(nextEpochInHMS),
            "WTOMB": "{:.3f}".format(WTOMB),
            "APR": "{:.2f}".format(tshareAPR),
            "Total Staked": "{:.2f}".format(totalTshareStaked)}

    return data


async def cemeteryTomb_Wftm_Data():
    tombWFTMInUSD = await tombAPI.getPriceOfTombUSD()
    tombInLP = await tombAPI.getValueOfTOMB_in_TOMB_WFTM_LP()
    wftmInLP = await tombAPI.getValueOfWFTM_in_TOMB_WFTM_LP()
    totalLP = await tombAPI.totalSupplyTOMB_FTM()
    TOMBtotalSupply = await tombAPI.getTOMBtotalSupply()
    bondSupply = await tombAPI.getBondReemableBonds()
    tshareStaked = await tombAPI.stakedTSHARE()
    tombLPusd = float(tombInLP) * float(tombWFTMInUSD["TOMBprice"])
    ftmLPusd = float(wftmInLP) * float(tombWFTMInUSD["ftmPrice"])
    liqulidy = (tombLPusd + ftmLPusd) / totalLP
    data = {
        "APR": "{:.2f}".format(
            (((((float(TOMBtotalSupply) - float(bondSupply)) * 0.01 * 0.8) / float(tshareStaked)) / 100) * 365)),
        "Daily APR": "{:.2f}".format(
            ((((float(TOMBtotalSupply) - float(bondSupply)) * 0.01 * 0.8) / float(tshareStaked)) / 100)),
        "Liquidity": "{:.2f}".format((tombLPusd + ftmLPusd)),
        "Total supply": "{:.2f}".format(totalLP),
        "TOMB/WFTM": "{:.2f}".format(liqulidy)
    }
    return data


async def tombToken():
    tombWFTMInUSD = await tombAPI.getPriceOfTombUSD()

    currentSupply = await tombAPI.getTOMBcurrentSupply()
    tombMC = await tombAPI.tombMarketCap()
    tomb = await tombAPI.getTombUpdatedPrice()
    tombPrice = await tombAPI.getTombPrice()
    data = {"TOMB": "{:.4f}".format(tombPrice),
            "TOMB_USD": "{:.2f}".format(tombWFTMInUSD["TOMBprice"]),
            "MarketCap": "{:.2f}".format(tombMC),
            "CurrentSupply": "{:.2f}".format(currentSupply["currentSupply"]),
            "totalSupply": "{:.2f}".format(currentSupply["totalSupply"])}
    return data


async def tshareToken():
    tombWFTMInUSD = await tombAPI.getTSHAREprice()
    currentSupply = await tombAPI.getTSHAREcurrentSupply()
    tshareMC = await tombAPI.tshareMarketCap()
    ts = await tombAPI.getTSHAREtotalSupply()
    data = {"TSHARE": "{:.2f}".format(tombWFTMInUSD["ftmTSHAREprice"]),
            "TSHARE_USD": "{:.2f}".format(tombWFTMInUSD["tshareUSD"]),
            "MarketCap": "{:.2f}".format(tshareMC),
            "CurrentSupply": "{:.2f}".format(currentSupply),
            "totalSupply": "{:.2f}".format(ts)}
    return data


async def tbondToken():
    tbondL = await tombAPI.tbondMarketCap()
    tbondTS = await tombAPI.getTBONDtotalSupply()
    tbond = await tombAPI.getTBONDPrice()
    tbondAvalible = await tombAPI.getTBONDpremiumRate()
    tbondMC = tbondL * tbond["usdTBOND"]
    data = {"TBOND": "{:.4f}".format(tbond["TBOND"]),
            "TBOND_USD": "{:.2f}".format(tbond["usdTBOND"]),
            "TBOND_AVALIBLE": "{:.2f}".format(tbondAvalible),
            "MarketCap": "{:.2f}".format(tbondMC),
            "CurrentSupply": "{:.2f}".format(tbondL),
            "totalSupply": "{:.2f}".format(tbondTS)}
    return data


async def getMyTokens(wallet):
    tshareBalance = await tombAPI.tshareBalanceOf(wallet)
    tombBalance = await tombAPI.tombBalanceOf(wallet)
    tbondBalance = await tombAPI.tbondBalanceOf(wallet)
    tshareStaked = await tombAPI.stakedTshareBalance(wallet)
    tombLearned = await tombAPI.tombEarned(wallet)
    tsharePrice = await tombAPI.getTSHAREprice()
    tombPrice = await tombAPI.getPriceOfTombUSD()

    data = {"TSHARE_IN_WALLET": "{:.3f}".format(tshareBalance),
            "TSHARE_IN_WALLET_USD": "{:.3f}".format(float(tshareBalance) * float(tsharePrice["tshareUSD"])),
            "TSHARE_IN_STAKING": "{:.3f}".format(tshareStaked),
            "TSHARE_IN_STAKING_USD": "{:.3f}".format(float(tshareStaked) * tsharePrice["tshareUSD"]),
            "TOTAL_TSHARE": "{:.3f}".format(float(tshareBalance) + float(tshareStaked)),
            "TOTAL_TSHARE_OWN_USD": "{:.3f}".format((
                float(tshareBalance) + float(tshareStaked)) * float(tsharePrice["tshareUSD"])),

            "TOMB_IN_WALLET": "{:.3f}".format(float(tombBalance)),
            "TOMB_IN_WALLET_USD": "{:.3f}".format(float(tombBalance) * float(tombPrice["TOMBprice"])),
            "TOMB_EARNED": "{:.3f}".format(tombLearned),
            "TOMB_EARNED_USD": "{:.3f}".format(float(tombLearned) * float(tombPrice["TOMBprice"])),
            "TOTAL_TOMB": "{:.3f}".format(float(tombBalance) + float(tombLearned)),
            "TOTAL_TOMB_OWN_USD": "{:.3f}".format((float(tombBalance) + float(tombLearned)) * float(tombPrice["TOMBprice"])),

            "TBOND_IN_WALLET": "{:.3f}".format(tbondBalance)}

    return data

