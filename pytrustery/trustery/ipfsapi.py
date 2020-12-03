"""Interface for IPFS."""
#TODO change IPFSAPI to ipfshttpclient
import ipfshttpclient

# Initialise IPFS interface.
ipfsclient = ipfshttpclient.connect()