"""Interface for Ethereum client and Trustery contract."""

import json
import os

from web3 import Web3
from trustery.utils_py3 import encode_hex
from trustery.utils_py3 import decode_hex
#For testing
#from trustery.testcontract import w3,myContract
import trustery
# Trustery contract constants.
#TRUSTERY_DEFAULT_ADDRESS = '0x9E84677B2874c1d8603Cde0A68225F5e86D7B200' 
TRUSTERY_DEFAULT_ADDRESS = '0xd6b7b79Fe0c787566f8d528fA4991a5fD15caE15'
TRUSTERY_ABI = json.load(open(os.path.join(os.path.dirname(trustery.__file__), 'trustery_abi.json')))
# Ethereum client interface.
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545')) #ethclient
w3.eth.defaultAccount=w3.eth.accounts[0]
w3.geth.personal.unlock_account(w3.eth.defaultAccount,'1', 15000)
myContract = w3.eth.contract(address=TRUSTERY_DEFAULT_ADDRESS, abi=TRUSTERY_ABI)
def encode_api_data(data):
    """
    Prepare arbitrary data to be send to the Ethereum client via the API.

    data: the data.
    """
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
    """
    elif type(data) == long:
        # Use native hex() to encode long.
        encoded = hex(data)
        if encoded[-1:] == 'L':
            # Remove the trailing 'L' if found.
            encoded = encoded[:-1]
        return encoded
    """