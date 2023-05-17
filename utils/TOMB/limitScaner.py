import aiohttp
from web3 import Web3
from web3.middleware import geth_poa_middleware
from hexbytes import HexBytes
from eth_abi import decode_abi

w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools'))
data = 'fc8af52a87d1930'
response = HexBytes(data)

print(decode_abi(['string'], response))

async def getLimits():
    async with aiohttp.ClientSession() as session:
        async with session.get(
                'https://api.thegraph.com/subgraphs/name/gelatodigital/limit-orders-fantom-ii/') as resp:
            response = await resp.json()