import json

from web3 import Web3
from web3.middleware import geth_poa_middleware

w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


def getTx(tx, telegramID):
    txData = w3.eth.get_transaction(tx)
    fromWallet = txData['from']
    toWallet = txData['to']
    profilesData = loadProfile()
    print(profilesData)

    for profile in profilesData['accounts']:
        if int(telegramID) == int(profile):
            walletAddress = profilesData['accounts'][profile]['walletAddress']
            verificationAddress = profilesData['accounts'][profile]['verificationWallet']
            print(fromWallet)
            print(walletAddress)
            print(toWallet)
            print(verificationAddress)
            if walletAddress == fromWallet and toWallet == verificationAddress:
                print(fromWallet)
                return fromWallet
        else:
            return 'This transaction does not match setup address that you was provided before'


def loadProfile():
    with open('UserProfiles.json', "r") as saveFile:
        return json.loads(saveFile.read())
