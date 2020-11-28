from web3 import Web3
from solc import compile_standard
import json
# Solidity source code
compiled_sol = compile_standard({
     "language": "Solidity",
    "sources": {
        "Trustery.sol": {
            "content":
            """
//"SPDX-License-Identifier: UNLICENSED"
pragma solidity  ^0.7.2;
contract Trustery {
    struct Signature {
        address signer;
    }

    uint public attributes;
    Signature[1000] public signatures;
    uint public signcount;
    uint public revocations;
    event AttributeAdded(uint indexed attributeID, address indexed owner, string attributeType, bool has_proof, bytes32 indexed identifier, string data, string datahash);
    event AttributeSigned(uint indexed signatureID, address indexed signer, uint indexed attributeID, uint expiry);
    event SignatureRevoked(uint indexed revocationID, uint indexed signatureID);

    function addAttribute(string memory attributeType, bool has_proof, bytes32 identifier, string memory data, string memory datahash) public returns (uint attributeID) {
        attributeID = attributes++;
        emit AttributeAdded(attributeID, msg.sender, attributeType, has_proof, identifier, data, datahash);
    }

    function signAttribute(uint attributeID, uint expiry) public returns (uint signatureID) {
        signcount++;
        signatures[signcount].signer=msg.sender;
        signatureID=signcount;
        
        //signatureID = signatures.length+1;
        //Signature memory signature = signatures[signatureID];
        //signature.signer = msg.sender;
        emit  AttributeSigned(signatureID, msg.sender, attributeID, expiry);
    }

    function revokeSignature(uint signatureID) public returns (uint revocationID) {
        require(signatures[signatureID].signer == msg.sender);
        revocationID = revocations++;
        emit SignatureRevoked(revocationID, signatureID);
        
        
    }
}

            """

                        }
   },
     "settings":
       {
             "outputSelection": {
                 "*": {
                     "*": [
                         "metadata", "evm.bytecode"
                         , "evm.bytecode.sourceMap"
                     ]
                }
            }
        }
 })

# web3.py instance
w3 = Web3(Web3.EthereumTesterProvider())

# set pre-funded account as sender
w3.eth.defaultAccount = w3.eth.accounts[0]

# get bytecode
bytecode = compiled_sol['contracts']['Trustery.sol']['Trustery']['evm']['bytecode']['object']

# get abi
abi = json.loads(compiled_sol['contracts']['Trustery.sol']['Trustery']['metadata'])['output']['abi']

MyContract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Submit the transaction that deploys the contract
tx_hash = MyContract.constructor().transact()

# Wait for the transaction to be mined, and get the transaction receipt
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

myContract = w3.eth.contract(
     address=tx_receipt.contractAddress,
     abi=abi )