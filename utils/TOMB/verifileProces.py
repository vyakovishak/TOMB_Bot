import json
from os import path
from eth_account import Account


class Profile:
    def __init__(self, telegramID, telegramName, telegramUsername, walletAddress):
        self.telegramID = telegramID
        self.walletAddress = walletAddress
        self.telegramName = telegramName
        self.telegramUsername = telegramUsername
        self.verificationWallet = None
        self.verificationPrivetKey = None
        self.verificationPrivetHex = None
        self.verificationStatus = False
        self.userTxHash = None
        self.setupWallet()

    def setupWallet(self):
        Account.enable_unaudited_hdwallet_features()
        acct, mnemonic = Account.create_with_mnemonic()
        self.verificationWallet = acct.address
        self.verificationPrivetKey = mnemonic
        self.verificationPrivetHex = acct.key.hex()
        doesExist = self.saveProfile()
        if "0x" in str(doesExist):
            self.verificationWallet = doesExist

    def saveProfile(self):
        objectData = self.__dict__

        if not path.exists('UserProfiles.json'):
            defaultData = {"accounts": {}}
            defaultData['accounts'][str(self.telegramID)] = objectData
            with open('UserProfiles.json', "w") as saveFile:
                saveFile.write(json.dumps(defaultData, indent=4))
        else:
            fileData = self.load()
            if not fileData['accounts'][str(self.telegramID)]:
                fileData['accounts'][str(self.telegramID)] = objectData
                with open('UserProfiles.json', "w") as file:
                    file.write(json.dumps(fileData, indent=4))
            else:
                return fileData['accounts'][str(self.telegramID)]['verificationWallet']

    def getAddress(self, address):
        data = self.load()
        for profile in data['accounts']:
            if address == data['accounts'][str(profile)]['walletAddress']:
                if data['accounts'][str(profile)]['verificationStatus']:
                    return True
                else:
                    return False
            else:
                return False
        return False

    def getStatus(self, telegramId):
        data = self.load()
        for profile in data['accounts']:
            if int(telegramId) == int(profile):
                status = data['accounts'][str(telegramId)]['verificationStatus']
                return status

    @staticmethod
    def load():
        accountFile = "UserProfiles.json"
        if not path.exists('UserProfiles.json'):
            defaultData = {"accounts": {}}
            with open('UserProfiles.json', "w") as file:
                file.write(json.dumps(defaultData, indent=4))
            return defaultData
        else:
            with open(accountFile, "r") as f:
                return json.loads(f.read())
