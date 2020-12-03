"""API for retrieving Trustery events."""

import time
from ethereum import abi
from ethereum import block
from ethereum.utils import big_endian_to_int
from trustery.utils_py3 import decode_hex
from trustery.ipfsapi import ipfsclient
from trustery.gpgapi import process_proof
from trustery.ethapi import TRUSTERY_ABI
from trustery.ethapi import TRUSTERY_DEFAULT_ADDRESS
from trustery.ethapi import w3, myContract, encode_web3_hex
from trustery.ethapi import encode_api_data

class Events(object):
    """API for retrieving Trustery events."""
    def __init__(self, address=TRUSTERY_DEFAULT_ADDRESS):
        """
        Initialise events retriever.

        address: the Ethereum Trustery contract address.
        """
        self.address = address

        # Initialise contract ABI.
        self._contracttranslator = abi.ContractTranslator(TRUSTERY_ABI)
    """
    def _get_event_id_by_name(self, event_name):

        Get the ID of an event given its name.

        event_name: the name of the event.

        for event_id, event in self._contracttranslator.event_data.items():
            if event['name'] == event_name:
                return event_id
    """
    def _get_all_events(self):
        events = {}
        for event_id, event in self._contracttranslator.event_data.items():
            events[event['name']] = encode_web3_hex(event_id)
        return events

    def _get_logs(self, topics, event_name=None):
        """
        Get logs (events).

        topics: a list of topics to search for.
        event_name: the name of the event.
        """
        # Set the event topic to the event ID if the event name is specified.
        events = self._get_all_events()

        if event_name is None:
            event_topic = None
        else:
            event_topic = events[event_name]
        # Prepent the event type to the topics.
        topics = [event_topic] + [encode_web3_hex(topic) for topic in topics]
        # Encode topics to be sent to the Ethereum client.
        #Setting up filter to get transaction through topics
        filter = w3.eth.filter({
            'address': myContract.address,
            'topics': topics, 
            'fromBlock': 5000} #only for tests, need to be 0
            )
        # Get logs from Ethereum client.
        getlogs = w3.eth.getFilterLogs(filter.filter_id)
        logs = []
        #Choose how to decode event by event name
        #TODO change in pythonic way
        if event_name == 'AttributeAdded':
            for log in getlogs:
                logs.append(myContract.events.AttributeAdded().processLog(log))
        elif event_name == 'AttributeSigned':
            for log in getlogs:
                logs.append(myContract.events.AttributeSigned().processLog(log))
        else:
            for log in getlogs:
                logs.append(myContract.events.SignatureRevoked().processLog(log))

        # Decode logs using the contract ABI.
        
        decoded_logs = []
        """
        for log in logs:
            logobj = processblock.Log(
                log['address'][2:],
                [big_endian_to_int(decode_hex(topic[2:])) for topic in log['topics']],
                decode_hex(log['data'][2:])
            )
            decoded_log = self._contracttranslator.listen(logobj, noprint=True)
            decoded_logs.append(decoded_log)
        """
        for log in logs:
            temp = {}
            temp['address']= log['address']
            temp.update(log['args'])
            decoded_logs.append(temp)
        return decoded_logs

    def filter_attributes(self, attributeID=None, owner=None, identifier=None):
        """
        Filter and retrieve attributes.

        attributeID: the ID of the attribute.
        owner: the Ethereum address that owns the attributes.
        identifier: the identifier of the attribute.
        """
        return self._get_logs([attributeID, owner, identifier], event_name='AttributeAdded')

    def filter_signatures(self, signatureID=None, signer=None, attributeID=None):
        """
        Filter and retrieve signatures.

        signatureID: the ID of the signature.
        signer: the Ethereum address that owns the signature.
        attributeID: the ID of the attribute.
        """
        return self._get_logs([signatureID, signer, attributeID], event_name='AttributeSigned')

    def filter_revocations(self, revocationID=None, signatureID=None):
        """
        Filter and retrieve revocations.

        revocationID: the ID of the revocation.
        attributeID: the ID of the attribute.
        """
        return self._get_logs([revocationID, signatureID], event_name='SignatureRevoked')

    def get_attribute_signatures_status(self, attributeID):
        """
        Get all the signatures of an attribute and check whether they have been revoked or expired.

        attributeID: the ID of the attribute.

        Returns a dictionaries representing the signatures status of the attribute:
            dict['status']['valid']: number of valid signatures.
            dict['status']['invalid']: number of invalid signatures.
            dict['signatures']: a list of signatures.

            For a signature index s:
                dict['signatures'][s]: dictionary representing the signature, plus the additional status keys below.
                dict['signatures'][s]['expired']: True if the signature is expired.
                dict['signatures'][s]['revocation']: dictionary representing the signature's revocation if it was revoked, otherwise False.
                dict['signatures'][s]['valid']: True if the signature is valid.
        """
        # Prepare return dictionary
        signatures = []
        status = {
            'valid': 0,
            'invalid': 0
        }
        signatures_status = {
            'status': status,
            'signatures': signatures
        }

        # Filter signatures for the specified attribute
        rawsignatures = self.filter_signatures(attributeID=attributeID)       
        # Process signatures
        for rawsignature in rawsignatures:
            signature = {}

            # Add signature properties to the dictionary
            signature.update(rawsignature)

            #dentifie Check if expired
            signature['expired'] = time.time() > signature['expiry']

            # Check if revoked
            rawrevocations = self.filter_revocations(signatureID=signature['signatureID'])
            if len(rawrevocations) > 0:
                signature['revocation'] = rawrevocations
            else:
                signature['revocation'] = False
            # Check if valid
            if not signature['expired'] and not signature['revocation']:
                signature['valid'] = True
                status['valid'] += 1
            else:
                signature['valid'] = False
                status['invalid'] += 1

            signatures.append(signature)

        return signatures_status

    def retrieve_attribute(self, attributeID):
        """Get an attribute, its status and signatures status, downloading off-blockchain data if necessary.

        attributeID: the ID of the attribute.

        Returns a dictionary representing all of the attribute's properties:
            dict: dictionary representing the attribute itself, plus the additional status keys below.
            dict['signatures_status']: the signatures status of the attribute.
        """
        rawattributes = self.filter_attributes(attributeID=attributeID)

        if not rawattributes:
            return None

        attribute = rawattributes[0]
        attribute['signatures_status'] = self.get_attribute_signatures_status(attributeID)

        # Download IPFS data if necessary.
        if attribute['data'].startswith('ipfs-block://'):
            ipfs_key = attribute['data'][len('ipfs-block://'):]
            attribute['data'] = ipfsclient.block_get(ipfs_key)

        # Verify PGP proof.
        if attribute['attributeType'] == 'pgp-key':
            attribute['proof_valid'] = self.verify_attribute_pgp_proof(attribute)

        # Set proof validity to unknown if the attribute has a proof but we did not know how to process it.
        if attribute['has_proof'] and 'proof_valid' not in attribute:
            attribute['proof_valid'] = None

        return attribute

    def verify_attribute_pgp_proof(self, attribute):
        """
        Verify the PGP proof of an attribute.

        Return True if valid, False if invalid, or None is unknown because a proof is unspecified.

        attribute: the attribute dictionary.
        """
        # Don't check proof if one was not specified.
        if not attribute['has_proof']:
            return None # Unknown validity.

        # Process the proof.
        proof = process_proof(attribute['data'])

        if not proof:
            return False

        (proof_address, proof_fingerprint) = proof
        if (
            # Check that the fingerprints match.
            proof_fingerprint.decode('hex') == attribute['identifier'].rstrip('\x00')
            # Check that the Ethereum addresses match.
            and proof_address == '0x' + attribute['owner']
            ):
            return True

        return False
