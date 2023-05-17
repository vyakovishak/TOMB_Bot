import aiogram
from aiogram import types
from loader import dp, bot
from utils.BSHARE.CHART_BUILDER import getChart
from utils.BSHARE.bshareAPI import bPEG_Calculator
from utils.TOMB import tombInfo
from utils.TOMB.TOMB_PEG_CHART import requestCall
from utils.TOMB.tombAPI import PEG_Calculator
from utils.SpookyTokens.chartBuilder import Chart


@dp.message_handler(commands=['cal', 'peg'])
async def pegCal(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action=aiogram.types.ChatActions.TYPING)
    arg = message.get_args()
    chartObj = Chart(tokenName='TOMB')
    await chartObj.chartBuilberV2()
    try:
        arg = float(arg)
    except:
        if len(arg) != 0:
            limitOrderData = await requestCall(arg.upper())
        else:
            limitOrderData = await requestCall(None)

    if type(arg) is float:
        data = await PEG_Calculator(arg)
    else:
        data = await PEG_Calculator()

    if data["Current TWAP"] >= 1.01:
        printStatus = "🟢"
    else:
        printStatus = "🔴"

        nicePrint = f"""<code>┌➽$TOMB PEG
├────────────
├➤<b>Print Status</b>: ({printStatus})
├────────────
├➤<b>Current PEG</b>: {"{:.3f}".format(data["Current Peg"])}
├➤<b>Target PEG</b>: {"{:.3f}".format(data["Target PEG"])}
├➤<b>Current TWAP</b>: {"{:.3f}".format(data["Current TWAP"])}
├➤<b>Previous TWAP</b>: {"{:.3f}".format(data["Previous"])}
├➤<b>FTM Need</b>: {"{:.3f}".format(data["FTM Need"])}
├➤<b>FTM (USD)</b>: ${"{:.3f}".format(data["FTM in USD"])}
├➤<b>Pump Need </b>: %{"{:.3f}".format(data["Percent"])}
├➤<b>Next Epoch</b>: {data["Next Epoch"]}
├──
├─➽FTM/TOMB
├➤<b>TOMB</b>: {"{:.3f}".format(data["TOMB"])}
├➤<b>FTM</b>: {"{:.3f}".format(data["TOMB/FTM"])}
├──
├─➽TOMB % BUY/SELL
├➤<b>Fish</b>: {(data["FISH"])}
├➤<b>Dolphin</b>: {(data["DOLPHINE"])}
├➤<b>Whales</b>: {(data["WHALES"])}
├──
├─➽Limit Orders
├➤<b>Buy Amount</b>: ${(limitOrderData["buy"])}
├➤<b>Sell Amount</b>: ${(limitOrderData["sell"])}
└────────────
    </code>"""
    img = open("tomb_chart_data.png", 'rb')
    await bot.send_photo(message.chat.id, photo=img, caption=nicePrint)


@dp.message_handler(commands=['bcal', 'bpeg'])
async def pegCal(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action=aiogram.types.ChatActions.TYPING)
    arg = message.get_args()
    chartObj = Chart(tokenName='BASED')
    await chartObj.chartBuilberV2()
    try:
        arg = float(arg)
    except:
        pass

    if type(arg) is float:
        data = await bPEG_Calculator(arg)
    else:
        data = await bPEG_Calculator()

    if data["Current TWAP"] >= 1.01:
        printStatus = "🟢"
    else:
        printStatus = "🔴"

    nicePrint = f"""<code>┌➽$TOMB PEG
├────────────
├➤<b>Print Status</b>: ({printStatus})
├➤<b>Current PEG</b>: {"{:.3f}".format(data["Current Peg"])}
├➤<b>Target PEG</b>: {"{:.3f}".format(data["Target PEG"])}
├➤<b>FTM Need</b>: {"{:.3f}".format(data["FTM Need"])}
├➤<b>FTM (USD)</b>: ${"{:.3f}".format(data["FTM in USD"])}
├➤<b>Pump Need </b>: %{"{:.3f}".format(data["Percent"])}
├➤<b>Next Epoch</b>: {data["Next Epoch"]}
└────────────
    </code>"""
    img = open("BASED_CHART.png", 'rb')
    await bot.send_photo(message.chat.id, photo=img, caption=nicePrint)


@dp.message_handler(commands="tip")
async def masonry(message: types.Message):
    await message.answer('Buy some  ☕️ for 👨‍💻\n<code>0x727a72c73434A5C42c706dA1659a116892Fd2994</code>')


@dp.message_handler(commands=["tshare", "ts"])
async def tshare(message: types.Message):
    tshare = await tombInfo.tshareToken()
    nicePrint = f"""<code>┌➽TSHARE
├────────────
├➤<b>TSHARE(FTM)</b>:{tshare["TSHARE"]} 
├➤<b>TSHARE(USD)</b>:${tshare["TSHARE_USD"]} 
├➤<b>Market Cap</b>:${tshare["MarketCap"]} 
├➤<b>Current Supply</b>:{tshare["CurrentSupply"]} 
├➤<b>Total Supply</b>:{tshare["totalSupply"]}
└────────────
    </code>"""

    await message.answer(nicePrint, disable_web_page_preview=True,
                         disable_notification=True)


@dp.message_handler(commands=["tokens", "my"])
async def mytokens(message: types.Message):
    arg = message.get_args()
    tokensData = await tombInfo.getMyTokens(str(arg))
    tombData = await tombInfo.masonryData(wallet=arg)
    nicePrint = f"""<code>┌➽Wallet
├─{arg}
│
│┌$TOMB
│├➤<b>In wallet</b>:{tokensData["TOMB_IN_WALLET"] + "= $" + tokensData["TOMB_IN_WALLET_USD"]} 
│├➤<b>Earned</b>:{tokensData["TOMB_EARNED"] + "= $" + tokensData["TOMB_EARNED_USD"]} 
│├➤<b>Total</b>:{tokensData["TOTAL_TOMB"] + "= $" + tokensData["TOTAL_TOMB_OWN_USD"]}
│└────────────
├────────────
│┌$TSHARE
│├➤<b>In wallet</b>:{tokensData["TSHARE_IN_WALLET"] + " = $" + tokensData["TSHARE_IN_WALLET_USD"]} 
│├➤<b>Staked in Masonry</b>:{tokensData["TSHARE_IN_STAKING"] + " = $" + tokensData["TSHARE_IN_STAKING_USD"]} 
│├➤<b>Total</b>:{tokensData["TOTAL_TSHARE"] + " = $" + tokensData["TOTAL_TSHARE_OWN_USD"]} 
│├➤<b>Can reward be claim?</b>: {"Yes" if tombData["Can be withdraw?"] == True else "No"}
│├➤<b>Can be withdraw?</b>: {"Yes" if tombData["Can be withdraw?"] == True else "No"}
│└────────────
├────────────
│┌$TBOND
│├➤<b>In wallet</b>:{tokensData["TBOND_IN_WALLET"]} 
│└────────────
└────────────
</code>"""
    await message.answer(nicePrint, disable_web_page_preview=True,
                         disable_notification=True)
