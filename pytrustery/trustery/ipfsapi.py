"""Interface for IPFS."""
import ipfshttpclient

# Initialise IPFS interface.
ipfsclient = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')