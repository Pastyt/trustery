"""Interface for IPFS."""
#TODO change IPFSAPI to ipfshttpclient
import ipfsApi


# Initialise IPFS interface.
ipfsclient = ipfsApi.Client('127.0.0.1', 5001)
