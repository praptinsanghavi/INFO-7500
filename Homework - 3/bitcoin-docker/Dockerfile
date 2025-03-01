# Use the official Bitcoin Core image (No need to install Ubuntu)
FROM ruimarinho/bitcoin-core:latest

# Set environment variables
ENV BITCOIN_DATA=/data

# Create a volume for persistent blockchain data
VOLUME ["/data"]

# Copy the Bitcoin configuration file
COPY bitcoin.conf "$BITCOIN_DATA/"

# Expose ports for RPC and P2P connections
EXPOSE 8332 8333

# Start bitcoind with the specified data directory and configuration
ENTRYPOINT ["bitcoind", "-datadir=/data", "-conf=/data/bitcoin.conf"]

# In your Dockerfile:
VOLUME ["hw3-bitcoin-data"] 
