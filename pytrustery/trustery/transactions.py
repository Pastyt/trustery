"""API for making Trustery tranactions."""

import io

from ethereum import abi
from trustery.ethapi import w3,myContract
from trustery.ipfsapi import ipfsclient
from trustery.gpgapi import generate_pgp_attribute_data
from trustery.ethapi import TRUSTERY_ABI
from trustery.ethapi import TRUSTERY_DEFAULT_ADDRESS

from trustery.ethapi import encode_api_data

class Transactions(object):
    """API for making Trustery tranactions."""
    def __init__(self, from_address=None, to_address=TRUSTERY_DEFAULT_ADDRESS):
        """
        Initialise transactions.

        from_address: the Ethereum address transactions should be sent from.
        to_address: the Ethereum Trustery contract address.
        """
        if from_address is None:
            # Use the first Ethereum account address if no from address is specified.
            self.from_address = w3.eth.coinbase

        else:
            self.from_address = from_address
        self.to_address = to_address

        # Initialise contract ABI.
        self._contracttranslator = abi.ContractTranslator(TRUSTERY_ABI)
    """
    def _send_transaction(self, data):
        
        Send a transaction.

        data: the transactions data.
    
        return myContract({
            #_from=self.from_address,
            'to': self.to_address,
            'data': encode_api_data(data),
            'gas':2000000, # TODO deal with gas limit more sensibly
        }
        )
    """

    def add_attribute(self, attributetype, has_proof, identifier, data, datahash):
        """
        Send a transaction to add an identity attribute.

        attributetype: the type of address.
        has_proof: True if the attribute has a cryptographic proof, otherwise False.
        identifier: the indexable identifier of the attribute.
        data: the data of the attribute.
        datahash: the Keccak hash of the data of the attribute if it is stored off-blockchain.
        identifier has type str so need to change to bytes32
        """
        tx=myContract.functions.addAttribute( attributetype , has_proof , bytes( identifier, 'utf-8' ) , data , datahash ).transact()
        tx_receipt = w3.eth.waitForTransactionReceipt(tx)
        print(myContract.events.AttributeAdded().processReceipt(tx_receipt))
    
    def add_attribute_with_hash(self, attributetype, has_proof, identifier, data):
        """
        Send a transaction to add an identity attribute, automatically calculating its datahash if the data is stored remotely.

        attributetype: the type of address.
        has_proof: True if the attribute has a cryptographic proof, otherwise False.
        identifier: the indexable identifier of the attribute.
        data: the data of the attribute.
        """
        datahash = '' # TODO calculate hash for remotely stored data
        return self.add_attribute(attributetype, has_proof, identifier, data, datahash)

    def add_attribute_over_ipfs(self, attributetype, has_proof, identifier, data):
        """
        Send a transaction to add an identity attribute, storing the data on IPFS first.

        attributetype: the type of address.
        has_proof: True if the attribute has a cryptographic proof, otherwise False.
        identifier: the indexable identifier of the attribute.
        data: the data of the attribute.
        """
        #  Store the data as an IPFS block and get its key.
        ipfs_key = ipfsclient.block_put(io.StringIO(data))['Key']

        # Generate Trustery-specific URI for the IPFS block.
        ipfs_uri = 'ipfs-block://' + ipfs_key

        # Add the attribute.
        self.add_attribute(attributetype, has_proof, identifier, ipfs_uri, datahash='')

    def add_pgp_attribute_over_ipfs(self, keyid):
        """
        Send a transaction to add an identity PGP attribute, storing the attribute data on IPFS.

        keyid: the ID of the PGP key.
        """
        # Generate PGP attribute data and get identifier (fingerprint).
        (fingerprint, data) = generate_pgp_attribute_data(keyid, self.from_address)

        # Express identifier as fingerprint in binary format.
        identifier = fingerprint.decode('hex')

        self.add_attribute_over_ipfs(
            attributetype='pgp-key',
            has_proof=True,
            identifier=identifier,
            data=data,
        )

    def sign_attribute(self, attributeID, expiry):

        """
        Send a transaction to sign an identity attriute.

        attributeID: the ID of the attribute.
        expiry: the expiry time of the attriute.
        """
        tx=myContract.functions.signAttribute( attributeID , expiry ).transact()
        tx_receipt = w3.eth.waitForTransactionReceipt(tx)
        print(myContract.events.AttributeSigned().processReceipt(tx_receipt))
        

    def revoke_signature(self, signatureID):
        """
        Send a transaction to revoke a signature.

        signatureID: the ID of the signature.
        """
        tx=myContract.functions.revokeSignature( signatureID ).transact()
        tx_receipt = w3.eth.waitForTransactionReceipt(tx)
        print(myContract.events.SignatureRevoked().processReceipt(tx_receipt))
        