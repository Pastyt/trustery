"""Interface for Ethereum client and Trustery contract."""

import json
import os

from web3 import Web3
#from trustery.utils_py3 import encode_hex
#from trustery.utils_py3 import decode_hex

#For tests
#from trustery.testcontract import w3,myContract
import trustery
# Trustery contract constants.
TRUSTERY_DEFAULT_ADDRESS = '0xEF0A66be3F6F2b5F7121d1BF8b84837D82cB660D'
TRUSTERY_ABI = json.load(open(os.path.join(os.path.dirname(trustery.__file__), 'trustery_abi.json')))
# Ethereum client interface.
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.eth.defaultAccount=w3.eth.coinbase
#Allow transactions from web3.
w3.geth.personal.unlock_account(w3.eth.defaultAccount,'1', 15000)
myContract = w3.eth.contract(address=TRUSTERY_DEFAULT_ADDRESS, abi=TRUSTERY_ABI)

def encode_web3_hex(data):
    if data!=None:
        #Best solution because toHex return 0x , need 0x0
        data = w3.toHex(data)
        data = '0x' + '0' * (66 - len(data)) + data[2:]
    else:
        data = None
    return data
"""
def encode_api_data(data):
    
    Prepare arbitrary data to be send to the Ethereum client via the API.

    data: the data.
    
    if data is None:
        return None
    elif type(data) == str and data.startswith('0x'):
        # Return data if it is already hex-encoded.
        return data
    elif type(data) in [bool, int]:
        # Use native hex() to encode non-string data has encode_hex() does not support it.
        return hex(data)
    else:
        # Encode data using encode_hex(), the recommended way to encode Ethereum data.
        return '0x' + encode_hex(data)
    
    elif type(data) == long:
        # Use native hex() to encode long.
        encoded = hex(data)
        if encoded[-1:] == 'L':
            # Remove the trailing 'L' if found.
            encoded = encoded[:-1]
        return encoded
"""